"""Reproduce the selected MIT source extraction from the recorded upstream commit."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

COMMIT = "55a184a3b0d09565a4c84268f725a47784e62528"
ROOT = Path(__file__).resolve().parent
HEADER = (
    "# Derived from AgriciDaniel/jev-seo, commit " + COMMIT + ".\n"
    "# Copyright (c) 2026 Agrici Daniel. MIT; see ../../LICENSE.upstream.\n"
    "# Adaptations: package imports; see SOURCE.md and source_manifest.json.\n"
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    parser.add_argument("--out", type=Path, default=ROOT / "runs" / "upstream-base",
                        help="Output directory for the base extraction; does not overwrite the adapted implementation")
    args = parser.parse_args()
    if args.out.resolve() == ROOT.resolve():
        raise SystemExit("Choose a separate output directory to preserve local adaptations")
    actual = subprocess.check_output(
        ["git", "-C", str(args.checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual != COMMIT:
        raise SystemExit(f"Expected upstream {COMMIT}; got {actual}")
    target = args.out / "site_audit" / "upstream"
    target.mkdir(parents=True, exist_ok=True)
    manifest = {"repository": "https://github.com/AgriciDaniel/jev-seo", "commit": COMMIT, "files": {}}
    for name in ("crawl.py", "parse.py", "checks.py", "psi.py"):
        source = args.checkout / "jevseo" / name
        original = source.read_text(encoding="utf-8")
        derived = HEADER + original.replace("from jevseo", "from site_audit.upstream")
        (target / name).write_text(derived, encoding="utf-8", newline="\n")
        manifest["files"][name] = {"source": f"jevseo/{name}", "sha256_original": hashlib.sha256(source.read_bytes()).hexdigest()}
    original = (args.checkout / "jevseo" / "jev.py").read_text(encoding="utf-8")
    question_code = original[original.index("def choice("):original.index("# ---------------------------------------------------------------- keywords")]
    (target / "questions.py").write_text(
        HEADER + '"""Extracted rubrics and state builders; no Jev client or probability thresholds."""\n'
        + "from __future__ import annotations\nimport re\n\nPAGE_TEXT_CHARS = 6000\n\n" + question_code,
        encoding="utf-8", newline="\n",
    )
    manifest["files"]["questions.py"] = {"source": "jevseo/jev.py (question definitions and state builders only)", "sha256_original": hashlib.sha256((args.checkout / "jevseo" / "jev.py").read_bytes()).hexdigest()}
    (args.out / "LICENSE.upstream").write_bytes((args.checkout / "LICENSE").read_bytes())
    (args.out / "source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Extracted {len(manifest['files'])} modules from {COMMIT}")


if __name__ == "__main__":
    main()
