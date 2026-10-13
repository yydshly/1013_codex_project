"""Verify the published static guide against Git blobs and complete summaries."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
PROJECT = "008-shadps4"
RESULTS = ROOT / "projects" / PROJECT / "experiments/results"


class TextCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        self.text.append(data)


def blob(commit, relative):
    return subprocess.run(["git", "show", f"{commit}:{relative}"], cwd=ROOT,
                          check=True, stdout=subprocess.PIPE).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--site-url", default="https://yydshly.github.io/1013_codex_project/")
    parser.add_argument("--run-url", default="")
    args = parser.parse_args()
    base = args.site_url.rstrip("/") + "/"
    record = {
        "date": "2026-10-14", "commit": args.commit, "site_url": base,
        "project_url": base + PROJECT + "/", "workflow_url": args.run_url,
        "status": "in-progress", "resources": [], "checks": [],
        "scope": "公网静态网页、完整摘要、指定引导图、文件内容与已有入口。网页交互另见 web-verification；原生程序另见 runtime-verification。未验证商业游戏或浏览器原生 PS4 执行。",
    }

    def fetch(relative, source=None):
        url = base + relative
        request = urllib.request.Request(url + ("&" if "?" in url else "?") + "verify=" + args.commit[:12],
                                         headers={"User-Agent": "shadps4-research-publication-check", "Cache-Control": "no-cache"})
        with urllib.request.urlopen(request, timeout=30) as response:
            data, status = response.read(), response.status
        assert status == 200, url
        item = {"url": url, "status": status, "sha256": hashlib.sha256(data).hexdigest()}
        if source:
            expected = hashlib.sha256(blob(args.commit, source)).hexdigest()
            item.update({"source": source, "expected_sha256": expected, "matches_commit": item["sha256"] == expected})
            record["resources"].append(item)
            assert item["matches_commit"], f"Published content differs from commit: {relative}"
        else:
            record["resources"].append(item)
        return data

    try:
        web = f"projects/{PROJECT}/web/"
        for relative in ["index.html", "styles.css", "app.js", "assets/comprehensive-map.svg", "assets/comprehensive-map.png",
                         "assets/comprehensive-map.source.json", "assets/understanding-map.svg", "assets/favicon.svg",
                         "assets/runtime-verification.json", "assets/openorbis-graphics-live.jpg", "assets/openorbis-graphics-live.source.json"]:
            fetch(f"{PROJECT}/{relative}", web + relative)
        record["checks"].append({"name": "项目公开资源", "result": "pass", "evidence": "11 项静态资源 HTTP 200，SHA-256 与对应提交 Git blob 完全一致。"})
        fetch(f"previews/{PROJECT}.svg", f"projects/{PROJECT}/assets/comprehensive-map.svg")
        record["checks"].append({"name": "指定完整引导图", "result": "pass", "evidence": "首页引导图与本次 1800×3290 总览 SVG 的提交内容一致。"})
        metadata = json.loads(blob(args.commit, f"projects/{PROJECT}/project.json"))
        html = fetch("").decode("utf-8")
        collector = TextCollector()
        collector.feed(html)
        visible = " ".join(" ".join(collector.text).split())
        for item in metadata["summary_sections"]:
            assert " ".join(item["text"].split()) in visible, "Incomplete summary: " + item["label"]
        assert f'./previews/{PROJECT}.svg' in html
        assert metadata["preview_caption"] in html
        record["checks"].append({"name": "能力、原理、价值与意义摘要", "result": "pass", "evidence": f"首页完整保留 {len(metadata['summary_sections'])} 项摘要，未截断或折叠，并在表格外展示完整总览图。"})
        manifest = json.loads(fetch("site-build.json"))
        required = ["001-infinite-bookshelf", "002-production-agentic-rag-course", "005-wireguard-install", "006-jev-seo", "007-hermes-jev-skills", PROJECT]
        assert set(required).issubset(manifest["projects"])
        record["published_projects"] = manifest["projects"]
        for project in required[:-1]:
            fetch(project + "/")
        record["checks"].append({"name": "保留现有网页", "result": "pass", "evidence": "构建清单包含本项目与已有五个静态项目；五个原有入口均返回 HTTP 200。"})
        record["status"] = "passed"
        print(json.dumps({"status":record["status"],"resources":len(record["resources"]),"checks":len(record["checks"]),"url":record["project_url"]},ensure_ascii=False))
    except Exception as error:
        record["status"] = "failed"
        record["failure"] = str(error)
        raise
    finally:
        RESULTS.mkdir(parents=True,exist_ok=True)
        (RESULTS/"publication-2026-10-14.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


if __name__ == "__main__":
    main()
