"""Check published BaoCut assets against a local static publication snapshot."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import ssl
from urllib.request import Request, urlopen

PROJECT = "014-baocut"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", required=True, type=Path)
    parser.add_argument("--base-url", default="https://yydshly.github.io/1013_codex_project/")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.site_dir.resolve()
    manifest = json.loads((root / "site-build.json").read_text(encoding="utf-8"))
    compared = [root/"index.html", root/"site-build.json", root/"previews"/f"{PROJECT}.png"]
    compared.extend(sorted(path for path in (root/PROJECT).rglob("*") if path.is_file()))
    checks = [(path.relative_to(root).as_posix(), path) for path in compared]
    checks.extend((directory+"/", None) for directory in manifest["projects"] if directory != PROJECT)
    # Load the platform trust store once before concurrent HTTPS requests.
    context = ssl.create_default_context()

    def inspect(item):
        relative, path = item
        url = args.base_url.rstrip("/")+"/"+relative
        record = {"path":relative, "url":url, "kind":"byte-comparison" if path else "existing-entry"}
        try:
            request = Request(url, headers={"User-Agent":"BaoCut-research-publication-check", "Cache-Control":"no-cache"})
            with urlopen(request, timeout=35, context=context) as response:
                body = response.read()
                record.update(status=response.status, bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
            if path:
                expected = path.read_bytes()
                record["expected_sha256"] = hashlib.sha256(expected).hexdigest()
                record["matches_snapshot"] = body == expected
            record["passed"] = record["status"] == 200 and record.get("matches_snapshot", True)
        except Exception as error:
            record.update(passed=False, error=f"{type(error).__name__}: {error}")
        return record

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(inspect, checks))
    report = {
        "verified_at":datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "base_url":args.base_url, "projects":manifest["projects"],
        "all_passed":all(item["passed"] for item in results),
        "checked":len(results), "byte_comparisons":len(compared),
        "existing_entries":len(manifest["projects"])-1, "results":results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"all_passed":report["all_passed"],"checked":len(results),
                      "byte_comparisons":len(compared),"existing_entries":report["existing_entries"],
                      "failures":[item for item in results if not item["passed"]]},ensure_ascii=False))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
