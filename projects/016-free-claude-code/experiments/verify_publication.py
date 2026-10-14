"""Compare the public FCC guide with committed assets and a generated site snapshot."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import ssl
import subprocess
from urllib.request import Request, urlopen

PROJECT = "016-free-claude-code"
REPOSITORY = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", required=True, type=Path)
    parser.add_argument("--base-url", default="https://yydshly.github.io/1013_codex_project/")
    parser.add_argument("--commit", default="HEAD", help="Committed FCC asset baseline")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.site_dir.resolve()
    commit = subprocess.check_output(["git", "rev-parse", args.commit], cwd=REPOSITORY, text=True).strip()
    manifest = json.loads((root / "site-build.json").read_text(encoding="utf-8"))
    compared = [root / "index.html", root / "site-build.json", root / "previews" / f"{PROJECT}.png"]
    compared.extend(sorted(path for path in (root / PROJECT).rglob("*") if path.is_file()))
    checks = []
    for path in compared:
        relative = path.relative_to(root).as_posix()
        source = None
        if relative.startswith(PROJECT + "/"):
            source = f"projects/{PROJECT}/web/{relative[len(PROJECT)+1:]}"
        elif relative == f"previews/{PROJECT}.png":
            source = f"projects/{PROJECT}/assets/understanding-overview.png"
        expected = subprocess.check_output(["git", "show", f"{commit}:{source}"], cwd=REPOSITORY) if source else path.read_bytes()
        checks.append((relative, expected, source))
    checks.extend((directory + "/", None, None) for directory in manifest["projects"] if directory != PROJECT)
    # Create the system trust context before starting concurrent HTTPS requests.
    context = ssl.create_default_context()

    def inspect(item):
        relative, expected, source = item
        url = args.base_url.rstrip("/") + "/" + relative
        record = {"path": relative, "url": url, "kind": "byte-comparison" if expected is not None else "existing-entry"}
        try:
            request = Request(url, headers={"User-Agent": "FCC-research-publication-check", "Cache-Control": "no-cache"})
            with urlopen(request, timeout=35, context=context) as response:
                body = response.read()
                record.update(status=response.status, bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
            if expected is not None:
                record.update(expected_sha256=hashlib.sha256(expected).hexdigest(), matches_snapshot=body == expected,
                              baseline=f"{commit}:{source}" if source else "generated-site-snapshot")
            record["passed"] = record["status"] == 200 and record.get("matches_snapshot", True)
        except Exception as error:
            record.update(passed=False, error=f"{type(error).__name__}: {error}")
        return record

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(inspect, checks))
    report = {"verified_at": datetime.now(timezone.utc).isoformat(), "base_url": args.base_url,
              "asset_commit": commit, "projects": manifest["projects"], "checked": len(results),
              "byte_comparisons": len(compared), "existing_entries": len(manifest["projects"])-1,
              "all_passed": all(item["passed"] for item in results), "results": results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps({key: report[key] for key in ("asset_commit", "all_passed", "checked", "byte_comparisons", "existing_entries")}, ensure_ascii=False))
    for item in results:
        if not item["passed"]:
            print(json.dumps(item, ensure_ascii=False))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
