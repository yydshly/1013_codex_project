"""Check live static resources against committed Git blobs, preserving other demos."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
RESULTS = Path(__file__).parent / "results"
WEB = "projects/010-vibe42/web/"
PREVIOUS = ["001-infinite-bookshelf", "002-production-agentic-rag-course",
            "005-wireguard-install", "006-jev-seo", "007-hermes-jev-skills",
            "008-shadps4", "009-cmux"]

def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True).stdout

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="https://yydshly.github.io/1013_codex_project/010-vibe42/")
    parser.add_argument("--commit", default="HEAD")
    parser.add_argument("--run-url", default="")
    parser.add_argument("--report", default="publication-http.json")
    args = parser.parse_args()
    if urllib.parse.urlsplit(args.url).scheme not in ("http", "https"):
        parser.error("Only HTTP(S) publications can be checked")
    if Path(args.report).name != args.report:
        parser.error("Report must be a filename within experiments/results")
    commit = git("rev-parse", args.commit).decode().strip()
    site = urllib.parse.urljoin(args.url, "../")
    paths = git("ls-tree", "-r", "--name-only", commit, "--", WEB).decode().splitlines()
    assets = [p for p in paths if not p.endswith("/README.md")]

    def fetch(url):
        request = urllib.request.Request(url + "?revision=" + commit[:12],
                                         headers={"User-Agent": "Vibe42-static-publication-check/1"})
        with urllib.request.urlopen(request, timeout=40) as response:
            payload = response.read()
            return {"url": url, "status": response.status, "bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest()}, payload

    def verify_file(source):
        url = urllib.parse.urljoin(args.url, source[len(WEB):])
        result, _ = fetch(url)
        expected = hashlib.sha256(git("show", commit + ":" + source)).hexdigest()
        result.update(source=source, expected_git_sha256=expected,
                      matches_commit=result["sha256"] == expected)
        return result

    with ThreadPoolExecutor(max_workers=4) as pool:
        resources = list(pool.map(verify_file, assets))
    preview, _ = fetch(urllib.parse.urljoin(site, "previews/010-vibe42.svg"))
    preview_expected = hashlib.sha256(git("show", commit + ":projects/010-vibe42/assets/understanding-overview.svg")).hexdigest()
    preview.update(expected_git_sha256=preview_expected, matches_commit=preview["sha256"] == preview_expected)
    index, _ = fetch(site)
    manifest, content = fetch(urllib.parse.urljoin(site, "site-build.json"))
    projects = json.loads(content)["projects"]
    required = PREVIOUS + ["010-vibe42"]
    preserved = all(project in projects for project in required)
    with ThreadPoolExecutor(max_workers=4) as pool:
        previous = list(pool.map(lambda project: fetch(urllib.parse.urljoin(site, project + "/"))[0], PREVIOUS))
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "url": args.url,
              "commit": commit, "workflow_run": args.run_url,
              "scope": "Actual static publication; no Vibe42 installation, pairing or Agent execution",
              "resources": resources, "index": index, "manifest": manifest, "guide_preview": preview,
              "published_projects": projects, "previous_demos": previous,
              "preserved_previous_demos": preserved,
              "passed": preserved and preview["matches_commit"] and all(r["status"] == 200 and r["matches_commit"] for r in resources)}
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"commit": commit, "resources": len(resources),
                      "previous_demos": len(previous), "passed": report["passed"],
                      "report": args.report}, ensure_ascii=False))
    if not report["passed"]:
        raise SystemExit("Live resources do not match the expected commit or prior demos are missing")

if __name__ == "__main__":
    main()
