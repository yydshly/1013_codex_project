"""Verify a deployed static snapshot against the locally built release."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
TEXT = {".html", ".css", ".js", ".json", ".txt", ".svg"}
ROUTES = [
    "index.html", "site-build.json", "009-cmux/index.html", "009-cmux/styles.css",
    "009-cmux/app.js", "009-cmux/assets/complete-understanding.png",
    "009-cmux/assets/complete-understanding.svg", "009-cmux/assets/overview.svg",
    "009-cmux/assets/architecture.svg", "009-cmux/research-summary.txt",
    "previews/009-cmux.png", "001-infinite-bookshelf/index.html",
    "002-production-agentic-rag-course/index.html", "005-wireguard-install/index.html",
    "006-jev-seo/index.html", "007-hermes-jev-skills/index.html", "008-shadps4/index.html",
]


def normalized(data, route):
    return data.replace(b"\r\n", b"\n") if Path(route).suffix in TEXT else data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--base-url", default="https://yydshly.github.io/1013_codex_project/")
    args = parser.parse_args()
    checks = []
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for route in ROUTES:
        expected = normalized((ROOT / "site-dist" / route).read_bytes(), route)
        public_url = args.base_url.rstrip("/") + "/" + route
        request = urllib.request.Request(public_url + "?release=" + args.commit[:12], headers={"User-Agent": "cmux-research-publication-check", "Cache-Control": "no-cache"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    actual = normalized(response.read(), route)
                    status = response.status
                break
            except (urllib.error.URLError, OSError) as error:
                if attempt == 2:
                    checks.append({"url": public_url, "status": None, "matches_build": False, "error": str(error)})
                    args.output.write_text(json.dumps({"commit": args.commit, "base_url": args.base_url, "checks": checks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    raise
                print(f"RETRY network {route}", flush=True)
                time.sleep(2)
        same = actual == expected
        check = {"url": public_url, "status": status, "matches_build": same,
                 "sha256": hashlib.sha256(actual).hexdigest(), "bytes": len(actual),
                 "text_line_endings_normalized": Path(route).suffix in TEXT}
        checks.append(check)
        print(f"{'PASS' if same else 'FAIL'} {status} {route}", flush=True)
        args.output.write_text(json.dumps({"commit": args.commit, "base_url": args.base_url, "checks": checks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = {"commit": args.commit, "base_url": args.base_url, "checks": checks}
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not all(row["status"] == 200 and row["matches_build"] for row in checks):
        raise SystemExit("Public resources do not yet match the release snapshot")
    print(f"Verified {len(checks)} public resources against release build; binary files exact, text normalizes platform line endings.")


if __name__ == "__main__":
    main()
