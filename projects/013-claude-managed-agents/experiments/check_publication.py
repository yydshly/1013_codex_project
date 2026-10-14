"""Verify public static resources against committed Git blobs and the built index.

Uses only Python's standard library. Does not call models or control a browser.
Run after the Pages workflow succeeds and after building the same checkout.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import subprocess
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[3]
PROJECT = "013-claude-managed-agents"
BASE = "https://yydshly.github.io/1013_codex_project/"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    commit = git("rev-parse", "HEAD").decode().strip()
    prefix = f"projects/{PROJECT}"
    metadata = json.loads(git("show", f"{commit}:{prefix}/project.json"))
    manifest = json.loads((ROOT / "site-dist/site-build.json").read_text(encoding="utf-8"))
    assert PROJECT in manifest["projects"]
    entries = [
        ("", (ROOT / "site-dist/index.html").read_bytes(), "build"),
        ("site-build.json", (ROOT / "site-dist/site-build.json").read_bytes(), "build"),
    ]
    public_files = git("ls-tree", "-r", "--name-only", commit, f"{prefix}/web").decode().splitlines()
    for path in public_files:
        relative = path.split("/web/", 1)[1]
        if (ROOT / "site-dist" / PROJECT / relative).is_file():
            entries.append((f"{PROJECT}/{relative}", git("show", f"{commit}:{path}"), "git-blob"))
    preview = metadata["preview"]
    entries.append((f"previews/{PROJECT}{Path(preview).suffix}", git("show", f"{commit}:{prefix}/{preview}"), "git-blob"))
    for directory in manifest["projects"]:
        if directory != PROJECT:
            path = f"projects/{directory}/web/index.html"
            entries.append((f"{directory}/", git("show", f"{commit}:{path}"), "git-blob"))

    def check(entry):
        path, expected, basis = entry
        request = Request(BASE + path, headers={"User-Agent": "Repository publication verification", "Cache-Control": "no-cache"})
        with urlopen(request, timeout=25) as response:
            status, final_url, body = response.status, response.geturl(), response.read()
        assert status == 200, (path, status)
        assert digest(body) == digest(expected), f"Published content differs from {basis}: {path}"
        return {
            "path": path, "url": final_url, "status": status,
            "bytes": len(body), "sha256": digest(body), "expected_basis": basis,
            "matches": True,
        }, body

    with ThreadPoolExecutor(max_workers=5) as pool:
        checked = list(pool.map(check, entries))
    home = checked[0][1].decode("utf-8")
    for section in metadata["summary_sections"]:
        assert html.escape(section["text"]) in home, section["label"]
    assert f"./previews/{PROJECT}.png" in home
    project_html = next(body.decode("utf-8") for result, body in checked if result["path"] == f"{PROJECT}/index.html")
    assert 'id="extension-scenarios"' in project_html
    assert project_html.count('<tr><th scope="row">0') == 8
    png = next(result for result, _ in checked if result["path"] == f"previews/{PROJECT}.png")
    assert png["sha256"] == "136537eb21199cb206756c9f8ac7928debf1dbc60afc95fb788900d815c494e4"
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(), "phase": args.phase,
        "source_commit": commit, "workflow_run_id": args.run_id,
        "workflow_url": f"https://github.com/yydshly/1013_codex_project/actions/runs/{args.run_id}",
        "base_url": BASE, "project_url": BASE + PROJECT + "/",
        "summary_sections": len(metadata["summary_sections"]), "extension_scenarios": 8,
        "guide_original_png_preserved": True,
        "all_built_projects": manifest["projects"],
        "previous_project_pages_preserved": len(manifest["projects"]) - 1,
        "checks": [result for result, _ in checked],
        "scope": "Public static resources only; does not validate the Managed Agents service or model outcomes.",
    }
    report_path = args.report.resolve()
    if (ROOT / "projects" / PROJECT / "experiments/results").resolve() not in report_path.parents:
        raise ValueError("Save the report in this project's experiments/results directory")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(checked)} public resources match; 18 summary sections; original guide preserved; {len(manifest['projects']) - 1} previous demos retained.")


if __name__ == "__main__":
    main()
