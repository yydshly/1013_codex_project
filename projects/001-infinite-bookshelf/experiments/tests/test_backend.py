"""Contract tests with a local fake provider; these are not real model evidence."""

import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib import error, request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from llm_client import GenerationError, LLMClient, ModelConfig, generate_book, parse_outline, read_dotenv
from server import create_server, validate_generation, RequestError


@contextlib.contextmanager
def running(server):
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


class FakeProvider(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, replies):
        super().__init__(("127.0.0.1", 0), FakeProviderHandler)
        self.replies = list(replies)
        self.calls = []

    @property
    def base_url(self):
        return f"http://127.0.0.1:{self.server_address[1]}/v1"


class FakeProviderHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_POST(self):
        payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.server.calls.append({"path": self.path, "payload": payload, "authorization": self.headers.get("Authorization")})
        reply = self.server.replies.pop(0)
        if isinstance(reply, tuple):
            status, body = reply
        else:
            status, body = 200, {"choices": [{"message": {"content": reply}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 10, "completion_tokens": 20}}
        raw = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        if status == 307:
            self.send_header("Location", self.server.base_url + "/redirected")
        self.end_headers()
        self.wfile.write(raw)


def outline_text(count=2):
    return json.dumps({"outline": [{"title": f"章节 {i + 1}", "description": f"范围 {i + 1}"} for i in range(count)]}, ensure_ascii=False)


class ConfigTests(unittest.TestCase):
    def test_dotenv_environment_priority_and_named_key(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            path.write_text('BOOKSHELF_BASE_URL="https://example.test/v1"\nBOOKSHELF_MODEL=old\nBOOKSHELF_API_KEY_ENV=PRIVATE_MODEL_KEY\nPRIVATE_MODEL_KEY=secret-for-test\n', encoding="utf-8")
            config = ModelConfig.from_environment({"BOOKSHELF_MODEL": "our-model"}, path)
            self.assertTrue(config.configured)
            self.assertEqual(config.model, "our-model")
            self.assertEqual(config.api_key, "secret-for-test")
            self.assertNotIn("secret-for-test", repr(config))

    def test_local_model_needs_no_fake_key(self):
        config = ModelConfig.from_environment({"BOOKSHELF_BASE_URL": "http://localhost:11434/v1", "BOOKSHELF_MODEL": "local-model"}, Path("missing-for-tests.env"))
        self.assertTrue(config.configured)
        self.assertEqual(config.api_key, "")

    def test_invalid_configuration(self):
        for overrides in ({}, {"BOOKSHELF_BASE_URL": "https://user:password@example.test/v1"}, {"BOOKSHELF_BASE_URL": "https://example.test:bad/v1"}, {"BOOKSHELF_TIMEOUT_SECONDS": "121"}, {"BOOKSHELF_SECTION_MAX_TOKENS": "0"}):
            env = {"BOOKSHELF_BASE_URL": "https://example.test/v1", "BOOKSHELF_MODEL": "model", **overrides} if overrides else {}
            self.assertFalse(ModelConfig.from_environment(env, Path("missing-for-tests.env")).configured)

    def test_no_shell_expansion(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            path.write_text('KEY=$(do-not-execute)\nexport OTHER="$KEY"\n', encoding="utf-8")
            self.assertEqual(read_dotenv(path), {"KEY": "$(do-not-execute)", "OTHER": "$KEY"})


class WorkflowTests(unittest.TestCase):
    def test_outline_fences_and_validation(self):
        self.assertEqual(len(parse_outline("```json\n" + outline_text() + "\n```", 2)), 2)
        for invalid in ("not json", "{}", "[]", '[{"title": 2, "description": "x"}]', '[{"title":"", "description":"x"}]'):
            with self.assertRaises(GenerationError):
                parse_outline(invalid, 1)

    def test_generation_order_usage_and_coherence_context(self):
        with running(FakeProvider([outline_text(), "测试书名", "前章正文，术语甲。", "后章正文。 "])) as provider:
            config = ModelConfig(provider.base_url, "test-model", "test-secret")
            events = list(generate_book(config, "学习测试", "面向初学者", 2))
            self.assertEqual([event["type"] for event in events], ["outline", "title", "section", "section", "done"])
            self.assertEqual([event["index"] for event in events if event["type"] == "section"], [0, 1])
            self.assertEqual(events[-1]["stats"]["requests"], 4)
            self.assertEqual(events[-1]["stats"]["input_tokens"], 40)
            self.assertEqual(events[-1]["stats"]["output_tokens"], 80)
            self.assertEqual(events[-1]["book"]["provenance"]["mode"], "live")
            self.assertTrue(all(call["authorization"] == "Bearer test-secret" for call in provider.calls))
            section_prompt = provider.calls[-1]["payload"]["messages"][-1]["content"]
            self.assertIn("前章正文，术语甲。", section_prompt)
            self.assertIn("完整目录", section_prompt)
            self.assertIn("章节 2", section_prompt)
            self.assertNotIn("test-secret", json.dumps(events))

    def test_json_mode_fallback_is_one_retry(self):
        with running(FakeProvider([(400, {"error": "response_format unsupported"}), outline_text(1), "书名", "内容"])) as provider:
            events = list(generate_book(ModelConfig(provider.base_url, "local-model"), "主题", "", 1))
            self.assertIn("response_format", provider.calls[0]["payload"])
            self.assertNotIn("response_format", provider.calls[1]["payload"])
            self.assertIsNone(provider.calls[0]["authorization"])
            self.assertEqual(events[-1]["stats"]["requests"], 4)

    def test_provider_error_body_never_exposed(self):
        with running(FakeProvider([(401, {"error": "sensitive-secret-in-error"})])) as provider:
            with self.assertRaises(GenerationError) as caught:
                LLMClient(ModelConfig(provider.base_url, "test-model", "sensitive-secret-in-error")).complete([], 100)
            self.assertNotIn("sensitive-secret", str(caught.exception))
            self.assertIn("认证", str(caught.exception))

    def test_redirect_not_followed_with_credentials(self):
        with running(FakeProvider([(307, {"error": "redirect"})])) as provider:
            with self.assertRaises(GenerationError):
                LLMClient(ModelConfig(provider.base_url, "model", "secret")).complete([], 100)
            self.assertEqual(len(provider.calls), 1)

    def test_invalid_provider_result_and_truncation(self):
        with running(FakeProvider([(200, {"choices": []})])) as provider:
            with self.assertRaises(GenerationError):
                LLMClient(ModelConfig(provider.base_url, "model")).complete([], 100)
        truncated = (200, {"choices": [{"message": {"content": "部分正文"}, "finish_reason": "length"}]})
        with running(FakeProvider([outline_text(1), "书名", truncated])) as provider:
            events = list(generate_book(ModelConfig(provider.base_url, "model"), "主题", "", 1))
            self.assertTrue(events[-2]["truncated"])
            self.assertEqual(events[-1]["stats"]["truncated_sections"], [0])

    def test_request_validation(self):
        self.assertEqual(validate_generation({"topic": " 主题 "}), ("主题", "", 3))
        for data in ([], {"topic": ""}, {"topic": "x", "chapter_count": True}, {"topic": "x", "chapter_count": 7}, {"topic": "x", "instructions": []}):
            with self.assertRaises(RequestError):
                validate_generation(data)


class ServerTests(unittest.TestCase):
    def fetch(self, server, path, data=None, headers=None):
        url = f"http://127.0.0.1:{server.server_address[1]}{path}"
        req = request.Request(url, data=json.dumps(data).encode("utf-8") if data is not None else None, headers=headers or ({"Content-Type": "application/json"} if data is not None else {}))
        return request.urlopen(req, timeout=3)

    def test_config_health_and_secrets_not_served(self):
        with tempfile.TemporaryDirectory() as directory, running(create_server(port=0, config=ModelConfig("https://example.test/v1", "model", "private-secret"), web_dir=Path(directory))) as server:
            with self.fetch(server, "/api/config") as response:
                body = response.read().decode()
                self.assertEqual(json.loads(body), {"configured": True, "model": "model", "reason": ""})
                self.assertNotIn("private-secret", body)
                self.assertNotIn("example.test", body)
            with self.fetch(server, "/api/health") as response:
                self.assertTrue(json.load(response)["ok"])
            with self.assertRaises(error.HTTPError) as caught:
                self.fetch(server, "/../experiments/.env")
            self.assertEqual(caught.exception.code, 404)

    def test_unconfigured_and_cross_origin_rejection(self):
        with running(create_server(port=0, config=ModelConfig.from_environment({}, Path("missing.env")))) as server:
            with self.assertRaises(error.HTTPError) as caught:
                self.fetch(server, "/api/generate", {"topic": "主题"})
            self.assertEqual(caught.exception.code, 503)
            with self.assertRaises(error.HTTPError) as caught:
                self.fetch(server, "/api/generate", {"topic": "主题"}, {"Content-Type": "application/json", "Origin": "https://external.test"})
            self.assertEqual(caught.exception.code, 403)

    def test_http_ndjson_contract(self):
        with running(FakeProvider([outline_text(1), "书名", "中文正文"])) as provider, running(create_server(port=0, config=ModelConfig(provider.base_url, "model"))) as server:
            with self.fetch(server, "/api/generate", {"topic": "主题", "chapter_count": 1}) as response:
                self.assertIn("application/x-ndjson", response.headers["Content-Type"])
                events = [json.loads(line) for line in response]
            self.assertEqual([item["type"] for item in events], ["outline", "title", "section", "done"])
            self.assertEqual(events[2]["content"], "中文正文")

    def test_failed_outline_stops_further_calls(self):
        with running(FakeProvider(["invalid-json"])) as provider, running(create_server(port=0, config=ModelConfig(provider.base_url, "model"))) as server:
            with self.fetch(server, "/api/generate", {"topic": "主题", "chapter_count": 1}) as response:
                events = [json.loads(line) for line in response]
            self.assertEqual([item["type"] for item in events], ["error"])
            self.assertEqual(len(provider.calls), 1)

    def test_parallel_generation_rejected_and_json_required(self):
        with running(create_server(port=0, config=ModelConfig("https://example.test/v1", "model"))) as server:
            server.generation_lock.acquire()
            try:
                with self.assertRaises(error.HTTPError) as caught:
                    self.fetch(server, "/api/generate", {"topic": "主题"})
                self.assertEqual(caught.exception.code, 409)
            finally:
                server.generation_lock.release()
            with self.assertRaises(error.HTTPError) as caught:
                self.fetch(server, "/api/generate", {"topic": "主题"}, {"Content-Type": "text/plain"})
            self.assertEqual(caught.exception.code, 415)


if __name__ == "__main__":
    unittest.main()
