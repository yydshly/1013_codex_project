"""Verify own published bytes and preservation of previous static guide entries.

Uses canonical public URLs. Expected project bytes come from committed Git
blobs, avoiding Windows checkout line-ending differences with Linux Pages.
"""
import argparse
import hashlib
import html
import json
import subprocess
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url")
    parser.add_argument("build_directory")
    parser.add_argument("output")
    parser.add_argument("--ref", default="HEAD")
    args = parser.parse_args()
    project = Path(__file__).resolve().parents[1]
    root = project.parents[1]
    build = Path(args.build_directory).resolve()
    metadata = json.loads((project / "project.json").read_text(encoding="utf-8"))
    manifest = json.loads((build / "site-build.json").read_text(encoding="utf-8"))
    slug = project.name
    tasks = []
    for file in sorted((build / slug).rglob("*")):
        if not file.is_file():
            continue
        relative = file.relative_to(build / slug).as_posix()
        blob = subprocess.run(["git", "show", args.ref + ":projects/" + slug + "/web/" + relative], cwd=root, check=True, capture_output=True).stdout
        tasks.append({"path":slug + "/" + ("" if relative == "index.html" else relative), "expected":blob, "type":"project"})
    preview_path = "previews/" + slug + Path(metadata["preview"]).suffix
    tasks.append({"path":preview_path,"expected":(build / preview_path).read_bytes(),"type":"preview"})
    tasks.extend([{"path":"","expected":(build / "index.html").read_bytes(),"type":"home"},
                  {"path":"site-build.json","expected":(build / "site-build.json").read_bytes(),"type":"manifest"}])
    for prior in manifest["projects"]:
        if prior != slug:
            tasks.append({"path":prior + "/", "expected":None, "type":"preserved-entry"})

    def check(task):
        url = args.base_url.rstrip("/") + "/" + task["path"]
        result = {"path":task["path"], "url":url, "type":task["type"]}
        try:
            request = urllib.request.Request(url, headers={"User-Agent":"tchMaterial-research-publication-check", "Cache-Control":"no-cache"})
            with urllib.request.urlopen(request, timeout=35) as response:
                content = response.read()
                result.update(http_status=response.status, bytes=len(content), sha256=hashlib.sha256(content).hexdigest())
            expected = task["expected"]
            result["matches_expected"] = expected is None or content == expected
            if expected is not None:
                result["expected_sha256"] = hashlib.sha256(expected).hexdigest()
            if task["type"] == "home":
                markup = content.decode("utf-8")
                result["all_summary_sections"] = all(html.escape(section["text"]) in markup for section in metadata["summary_sections"])
                result["summary_sections"] = len(metadata["summary_sections"])
            result["passed"] = result["http_status"] == 200 and result["matches_expected"] and result.get("all_summary_sections", True)
        except (urllib.error.URLError, OSError, UnicodeError) as error:
            result.update(passed=False, error=str(error))
        return result

    with ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(check, tasks))
    commit = subprocess.run(["git","rev-parse",args.ref], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
    report = {"date":datetime.now(timezone(timedelta(hours=8))).isoformat(), "base_url":args.base_url, "source_commit":commit,
              "status":"passed" if all(item["passed"] for item in results) else "failed",
              "scope":"公网静态发布与已有入口；不验证上游登录、真实教材下载、音频书签或 RAG", "results":results}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":report["status"],"urls":len(results),"failures":[item for item in results if not item["passed"]]},ensure_ascii=False))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
