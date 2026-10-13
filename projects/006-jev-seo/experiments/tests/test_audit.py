"""Offline behavior tests. All HTTP/model responses are mocked."""
import copy
from datetime import timedelta
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import requests

from site_audit.config import ModelConfig
from site_audit.demo import HOME, HOME_HTML, SERVICE_HTML, example_response, fixture_site, make_demo
from site_audit.evaluation import job_fingerprint, parse_json, response_schema, validate_answers
from site_audit.model import ModelClient
from site_audit import pipeline, report
from site_audit.upstream import checks, crawl
from site_audit.upstream.parse import parse_page


def small_job():
    job = {"id": "review-001", "kind": "page", "urls": [HOME], "metadata": {},
           "state": {"page": {"text": "页面提供设计服务。", "outline": ["h1: 设计"]}},
           "questions": {"kind": {"type": "choice", "criteria": {"service": "服务", "other": "其他"}},
                         "quality": {"type": "score", "criteria": ["差", "一般", "好"]},
                         "clear": {"type": "noul", "criteria": {"true": "明确", "false": "模糊"}}}}
    job["fingerprint"] = job_fingerprint(job)
    return job


def good_payload(job=None):
    return {"answers": {key: {"value": value, "reason": "引用说明页面提供设计服务。",
                              "evidence": [{"field": "page.text", "quote": "提供设计服务"}]}
                        for key, value in (("kind", "service"), ("quality", 2), ("clear", True))}}


def model_response(payload=None, finish="stop", usage=True):
    data = {"model": "test-model-returned", "choices": [{"finish_reason": finish,
            "message": {"content": json.dumps(payload or good_payload(), ensure_ascii=False)}}]}
    if usage:
        data["usage"] = {"prompt_tokens": 120, "completion_tokens": 80}
    return Mock(status_code=200, json=Mock(return_value=data))


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.job = small_job()

    def test_valid_answers_require_review_and_no_probability(self):
        answers = validate_answers(self.job, good_payload())
        self.assertTrue(all(answer["needs_review"] for answer in answers.values()))
        self.assertTrue(all(answer["calibrated_probability"] is None for answer in answers.values()))

    def test_null_is_allowed_without_evidence(self):
        payload = good_payload()
        payload["answers"]["quality"] = {"value": None, "reason": "证据不足", "evidence": []}
        self.assertIsNone(validate_answers(self.job, payload)["quality"]["value"])

    def test_rejects_bad_values_and_extra_questions(self):
        for key, value in (("kind", "fabricated"), ("quality", 3), ("quality", True),
                           ("quality", float("inf")), ("clear", "true")):
            with self.subTest(key=key, value=value):
                payload = good_payload()
                payload["answers"][key]["value"] = value
                with self.assertRaises(ValueError):
                    validate_answers(self.job, payload)
        payload = good_payload()
        payload["answers"]["invented"] = payload["answers"]["clear"]
        with self.assertRaises(ValueError):
            validate_answers(self.job, payload)

    def test_rejects_missing_fabricated_and_wrong_field_quotes(self):
        for evidence in ([], [{"field": "page.text", "quote": "根本不存在"}],
                         [{"field": "page.missing", "quote": "提供设计服务"}],
                         [{"field": "page.outline", "quote": "h1: 设计"}]):
            with self.subTest(evidence=evidence):
                payload = good_payload()
                payload["answers"]["quality"]["evidence"] = evidence
                with self.assertRaises(ValueError):
                    validate_answers(self.job, payload)

    def test_list_item_field_can_be_quoted(self):
        payload = good_payload()
        payload["answers"]["quality"]["evidence"] = [{"field": "page.outline.0", "quote": "设计"}]
        validate_answers(self.job, payload)

    def test_json_rejects_duplicates_and_nonfinite_values(self):
        for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):
                parse_json(text)
        self.assertEqual(parse_json('```json\n{"x":1}\n```'), {"x": 1})

    def test_schema_covers_types_and_all_questions(self):
        schema = response_schema(self.job["questions"])
        props = schema["properties"]["answers"]
        self.assertEqual(set(props["required"]), set(self.job["questions"]))
        self.assertFalse(props["additionalProperties"])
        self.assertIn(None, props["properties"]["kind"]["properties"]["value"]["enum"])

    def test_fingerprint_binds_metadata_and_snapshot(self):
        changed = copy.deepcopy(self.job)
        changed["metadata"]["word_count"] = 800
        self.assertNotEqual(job_fingerprint(changed), self.job["fingerprint"])


class ModelTests(unittest.TestCase):
    def cfg(self, **kwargs):
        return ModelConfig("https://llm.example/v1", "test-model", api_key="test-secret", **kwargs)

    @patch("site_audit.model.requests.post")
    def test_success_contract_usage_and_no_secret_in_result(self, post):
        post.return_value = model_response()
        client = ModelClient(self.cfg())
        result = client.ask(small_job())
        self.assertEqual(result["status"], "ok")
        self.assertEqual(client.ledger["input_tokens"], 120)
        args, kwargs = post.call_args
        self.assertEqual(args[0], "https://llm.example/v1/chat/completions")
        self.assertEqual(kwargs["json"]["response_format"]["type"], "json_schema")
        self.assertEqual(kwargs["json"]["max_completion_tokens"], 3000)
        self.assertFalse(kwargs["allow_redirects"])
        self.assertNotIn("test-secret", json.dumps(result) + repr(client.config))

    @patch("site_audit.model.requests.post")
    def test_non_schema_modes_and_legacy_token_parameter(self, post):
        post.return_value = model_response(usage=False)
        for mode in ("json_object", "text"):
            client = ModelClient(self.cfg(response_mode=mode, token_parameter="max_tokens"))
            self.assertEqual(client.ask(small_job())["status"], "ok")
            body = post.call_args.kwargs["json"]
            self.assertIn("max_tokens", body)
            self.assertIn("JSON schema", body["messages"][1]["content"])
            self.assertEqual("response_format" in body, mode == "json_object")
            self.assertEqual(client.ledger["usage_missing"], 1)

    @patch("site_audit.model.requests.post")
    def test_failures_count_and_no_retry(self, post):
        failures = [model_response(finish="length"), Mock(status_code=302),
                    Mock(status_code=200, json=Mock(return_value=[])),
                    Mock(status_code=200, json=Mock(return_value={"choices": []})),
                    requests.Timeout("test-secret")]
        for failure in failures:
            post.reset_mock()
            post.side_effect = failure if isinstance(failure, Exception) else None
            post.return_value = failure
            client = ModelClient(self.cfg())
            result = client.ask(small_job())
            self.assertEqual(result["status"], "failed")
            self.assertEqual(client.ledger["failed"], 1)
            self.assertEqual(post.call_count, 1)
            self.assertNotIn("test-secret", json.dumps(result))

    @patch("site_audit.model.requests.post")
    def test_fabricated_evidence_response_rejected(self, post):
        payload = good_payload()
        payload["answers"]["clear"]["evidence"][0]["quote"] = "不在网页中的话"
        post.return_value = model_response(payload)
        self.assertEqual(ModelClient(self.cfg()).ask(small_job())["status"], "failed")

    @patch("site_audit.model.requests.post")
    def test_request_limit_prevents_extra_call(self, post):
        post.return_value = model_response()
        client = ModelClient(self.cfg(max_requests=1))
        self.assertEqual(client.ask(small_job())["status"], "ok")
        self.assertEqual(client.ask(small_job())["status"], "skipped")
        self.assertEqual(post.call_count, 1)

    def test_config_rejects_invalid_url_and_limits(self):
        for url in ("file:///tmp/secret", "https://key@llm.example", "https://llm.example?key=x"):
            with self.assertRaises(ValueError):
                ModelConfig(url, "test")
        with self.assertRaises(ValueError):
            self.cfg(max_requests=0)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.pack = make_demo(self.folder)

    def tearDown(self):
        self.temp.cleanup()

    def import_document(self, document):
        path = self.folder / "answers.json"
        pipeline.write_json(path, document)
        return pipeline.import_answers(self.folder, path)

    def test_rules_and_partial_chat_import_generate_report(self):
        findings = pipeline.read_json(self.folder / "audit.json")["rule_findings"]
        ids = {finding["id"] for finding in findings}
        self.assertIn("title_missing", ids)
        self.assertIn("broken_internal_links", ids)
        self.assertEqual(self.import_document(example_response(self.pack)), 1)
        data = report.render(self.folder)
        self.assertEqual(data["model_jobs_assessed"], 1)
        self.assertEqual(data["model_jobs_total"], 3)
        self.assertGreater(data["unknown_answers"], 0)
        self.assertTrue(all(item["needs_review"] for item in data["model_findings"]))
        self.assertIn("人工构造示例", (self.folder / "report.md").read_text(encoding="utf-8"))

    @patch("site_audit.pipeline.crawl.crawl")
    def test_recollect_preserves_snapshot_before_network(self, crawl_call):
        original = (self.folder / "audit.json").read_bytes()
        with self.assertRaises(ValueError):
            pipeline.collect(HOME, self.folder)
        crawl_call.assert_not_called()
        self.assertEqual((self.folder / "audit.json").read_bytes(), original)

    def test_repeat_demo_keeps_snapshot_and_valid_judgments(self):
        self.import_document(example_response(self.pack))
        original = (self.folder / "audit.json").read_bytes()
        pack = make_demo(self.folder)
        self.assertEqual(pack["audit_id"], self.pack["audit_id"])
        self.assertEqual((self.folder / "audit.json").read_bytes(), original)
        self.assertEqual(report.render(self.folder)["model_jobs_assessed"], 1)

    def test_bad_snapshot_fingerprint_duplicate_and_unknown_rejected(self):
        base = example_response(self.pack)
        for mutation in ("audit", "fingerprint", "duplicate", "unknown"):
            doc = copy.deepcopy(base)
            if mutation == "audit":
                doc["audit_id"] = "wrong"
            elif mutation == "fingerprint":
                doc["results"][0]["fingerprint"] = "wrong"
            elif mutation == "duplicate":
                doc["results"] *= 2
            else:
                doc["results"][0]["job_id"] = "unknown"
            with self.assertRaises(ValueError):
                self.import_document(doc)
            self.assertFalse((self.folder / "judgments.json").exists())

    def test_bad_import_keeps_prior_valid_results(self):
        base = example_response(self.pack)
        self.import_document(base)
        original = (self.folder / "judgments.json").read_bytes()
        invalid = copy.deepcopy(base)
        invalid["results"][0]["answers"]["specificity"]["evidence"][0]["quote"] = "假引文"
        with self.assertRaises(ValueError):
            self.import_document(invalid)
        self.assertEqual((self.folder / "judgments.json").read_bytes(), original)

    def test_stale_result_is_not_counted(self):
        self.import_document(example_response(self.pack))
        saved = pipeline.read_json(self.folder / "judgments.json")
        next(iter(saved["results"].values()))["fingerprint"] = "stale"
        pipeline.write_json(self.folder / "judgments.json", saved)
        data = report.render(self.folder)
        self.assertEqual(data["model_jobs_assessed"], 0)
        self.assertEqual(data["unknown_answers"], 0)
        self.assertFalse(data["model_findings"])

    def test_html_report_escapes_model_content(self):
        doc = example_response(self.pack)
        doc["results"][0]["answers"]["specificity"]["reason"] = '<script>alert("x")</script>'
        self.import_document(doc)
        report.render(self.folder)
        html = (self.folder / "report.html").read_text(encoding="utf-8")
        self.assertNotIn('<script>alert("x")</script>', html)
        self.assertIn("&lt;script&gt;", html)

    @patch("site_audit.model.requests.post")
    def test_api_evaluation_resumes_without_repeating_success(self, post):
        def respond(*args, **kwargs):
            request = json.loads(kwargs["json"]["messages"][1]["content"])
            nulls = {key: {"value": None, "reason": "离线响应，无足够证据", "evidence": []}
                     for key in request["questions"]}
            return model_response({"answers": nulls})
        post.side_effect = respond
        cfg = ModelConfig("http://localhost:9999/v1", "offline-test", max_requests=10)
        pipeline.evaluate_api(self.folder, cfg)
        self.assertEqual(post.call_count, 3)
        pipeline.evaluate_api(self.folder, cfg)
        self.assertEqual(post.call_count, 3)
        data = report.render(self.folder)
        self.assertEqual(data["model_jobs_assessed"], 3)
        self.assertEqual(data["ledgers"][-1]["attempts"], 0)


def http_response(url, body="", status=200, content_type="text/html; charset=utf-8", history=None):
    response = requests.Response()
    response.status_code = status
    response.url = url
    response._content = body.encode("utf-8")
    response.encoding = "utf-8"
    response.headers["content-type"] = content_type
    response.elapsed = timedelta(milliseconds=12)
    response.history = history or []
    return response


class FixtureFetcher:
    def __init__(self):
        self.delay = 0
        self.requests = 0
        self.got = []

    def get(self, url):
        self.requests += 1
        self.got.append(url)
        if url == HOME:
            html = HOME_HTML.replace("</main>", '<a href="/project/redirect">跳转</a></main>')
            return http_response(url, html)
        if url == HOME + "/service":
            return http_response(url, SERVICE_HTML)
        if url == HOME + "/redirect":
            return http_response("https://demo.example/other-project", SERVICE_HTML,
                                 history=[http_response(url, status=301)])
        if url.endswith("/robots.txt"):
            return http_response(url, "User-agent: *\nDisallow:\nSitemap: https://demo.example/sitemap.xml", content_type="text/plain")
        if url.endswith("/sitemap.xml"):
            body = f'<urlset><url><loc>{HOME}</loc></url><url><loc>{HOME}/service</loc></url><url><loc>https://demo.example/other-project</loc></url></urlset>'
            return http_response(url, body, content_type="application/xml")
        return http_response(url, status=404)

    def head(self, url):
        self.requests += 1
        return 404 if url.endswith("/missing") else 200


class CrawlTests(unittest.TestCase):
    def test_path_scope_has_boundary_and_host(self):
        self.assertTrue(crawl.within_scope(HOME + "/service", "demo.example", "/project"))
        self.assertFalse(crawl.within_scope("https://demo.example/project-other", "demo.example", "/project"))
        self.assertFalse(crawl.within_scope("https://outside.example/project", "demo.example", "/project"))
        self.assertEqual(pipeline.selected_scope("https://u.github.io/project/index.html", "path"), "/project")
        self.assertEqual(pipeline.selected_scope(HOME, "site"), "/")

    def test_long_chinese_text_survives_parsing(self):
        text = "这是一段连续中文正文用于说明网页检查能力与使用流程" * 6
        facts = parse_page(HOME, f"<main><p>{text}</p></main>", "demo.example")
        self.assertIn(text, facts["text_excerpt"])

    @patch("site_audit.upstream.crawl.public_host", return_value=True)
    @patch("site_audit.upstream.crawl.Fetcher", side_effect=FixtureFetcher)
    def test_crawl_scopes_sitemaps_discovery_and_redirect_content(self, fetcher, public):
        site = crawl.crawl(HOME, max_pages=10, workers=1, render_mode="never", scope_path="/project", log=lambda _: None)
        urls = {page["url"] for page in site["pages"]}
        self.assertIn(HOME + "/service", urls)
        self.assertNotIn("https://demo.example/other-project", urls)
        self.assertEqual(site["sitemaps"]["total_urls"], 2)
        self.assertEqual(site["sitemaps"]["domain_total_urls"], 3)
        redirected = next(page for page in site["pages"] if page["url"].endswith("/redirect"))
        self.assertEqual(redirected["kind"], "redirect")
        self.assertNotIn("text_excerpt", redirected)
        findings = checks.run_checks(site)
        self.assertIn("broken_internal_links", {item["id"] for item in findings})

    @patch("site_audit.upstream.crawl.socket.getaddrinfo")
    def test_private_address_is_refused(self, dns):
        dns.return_value = [(2, 1, 6, "", ("127.0.0.1", 0))]
        self.assertFalse(crawl.public_host("example.org"))

    @patch("site_audit.upstream.crawl.public_host")
    def test_redirect_hop_rechecks_private_guard(self, public):
        public.side_effect = [True, False]
        fetcher = crawl.Fetcher()
        response = http_response("https://public.example/", status=302)
        response.headers["location"] = "http://127.0.0.1/private"
        response.close = Mock()
        fetcher.session.request = Mock(return_value=response)
        self.assertIsNone(fetcher.get("https://public.example/"))
        self.assertEqual(fetcher.session.request.call_count, 1)


if __name__ == "__main__":
    unittest.main()
