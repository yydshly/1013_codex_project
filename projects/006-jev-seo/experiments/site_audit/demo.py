"""Clearly labelled fixtures: no live network or real model judgment."""
from pathlib import Path

from site_audit.pipeline import save_audit, export_pack, write_json, import_answers, read_json
from site_audit.upstream.parse import parse_page

HOME = "https://demo.example/project"
HOME_HTML = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<title>星河网页服务</title><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="星河网页服务为小型企业制作网站，提供设计、上线和维护。">
<link rel="canonical" href="https://demo.example/project"></head><body>
<main><h1>星河网页服务</h1><p>我们为小型企业提供网页设计、网站上线和每月维护服务。需求确认后，十个工作日交付首页、服务介绍与联系页面。</p>
<p>此页面是本仓库构造的测试资料，星河网页服务不是已验证的真实企业。</p>
<a href="/project/service">了解服务</a><a href="/project/missing">案例</a>
<a href="/other-project">同域名其他项目</a><img src="/project/team.jpg"></main></body></html>'''
SERVICE_HTML = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"></head><body>
<main><h1>网页设计服务</h1><p>我们提供专业优质的服务，致力于持续创新和满意体验。我们重视客户需求，希望共同创造更美好的未来。</p>
<a href="/project">返回首页</a></main></body></html>'''


def fixture_site():
    pages = []
    for url, html, depth in ((HOME, HOME_HTML, 0), (HOME + "/service", SERVICE_HTML, 1)):
        pages.append({**parse_page(url, html, "demo.example"), "url": url, "final_url": url,
                      "kind": "page", "status": 200, "depth": depth, "inlinks": 1,
                      "in_sitemap": True, "ttfb_ms": 25, "bytes": len(html.encode()),
                      "headers": {}, "rendered": False, "js_dependent": False})
    pages.append({"url": HOME + "/missing", "kind": "error", "status": 404, "depth": 1})
    return {
        "fixture": True, "input_url": HOME, "start_url": HOME, "final_url": HOME,
        "origin": "https://demo.example", "domain": "demo.example", "https": True,
        "scope_path": "/project", "pages": pages,
        "robots": {"url": "https://demo.example/robots.txt", "present": True, "status": 200,
                   "disallow_all": False, "search_bots": {"Googlebot": True}, "ai_bots": {"GPTBot": True}},
        "sitemaps": {"files": [{"url": "https://demo.example/sitemap.xml", "error": None}],
                     "urls": [HOME, HOME + "/service"], "total_urls": 2, "domain_total_urls": 3},
        "probes": {"not_found_status": 404, "http_to_https": True, "http_redirect_status": 301,
                   "host_variant": {"host": "www.demo.example", "status": 200, "redirect_status": 301,
                                    "redirects_to_canonical_host": True}, "llms_txt": False},
        "link_status": {HOME: 200, HOME + "/service": 200, HOME + "/missing": 404,
                        "https://demo.example/other-project": 200},
        "external_status": {}, "external_total": 0, "blocked_by_robots": [], "requests": 0,
        "render": {"mode": "never", "browser_available": None, "homepage_rendered": False},
        "limits": {"max_pages": 30, "max_depth": 5, "hit_page_cap": False, "hit_time_budget": False},
    }


def example_response(pack):
    job = next(job for job in pack["jobs"] if job["kind"] == "page" and not job["metadata"]["homepage"])
    answers = {key: {"value": None, "reason": "人工构造测试响应：这一项不作判断。", "evidence": []}
               for key in job["questions"]}
    for key, value in (("importance", 3), ("specificity", 0), ("helpfulness", 0), ("intent", "commercial")):
        answers[key] = {"value": value, "reason": "人工构造测试响应：演示通用措辞如何进入报告，并非真实模型结论。",
                        "evidence": [{"field": "page.text", "quote": "我们提供专业优质的服务"}]}
    return {"schema_version": "1.0", "audit_id": pack["audit_id"], "model": "人工构造示例（非实际模型）",
            "results": [{"job_id": job["id"], "fingerprint": job["fingerprint"], "answers": answers}]}


def make_demo(folder: Path, with_judgments=False):
    site = fixture_site()
    if (folder / "audit.json").exists():
        if read_json(folder / "audit.json").get("site") != site:
            raise ValueError("样例目录已有其他采集材料，请使用新的 --out。")
    else:
        save_audit(folder, site)
    pack = export_pack(folder)
    if with_judgments:
        path = folder / "example-answers.json"
        write_json(path, example_response(pack))
        import_answers(folder, path)
    return pack
