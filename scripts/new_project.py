"""Create the next numbered research project and update the root README."""

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

from project_index import (
    ROOT, SLUG_PATTERN, load_projects, markdown_text, render_index,
    replace_index, update_readme, validate_source,
)


def create_project(
    slug: str, name: str, source: str, summary: str, *, root: Path = ROOT,
    source_type: str = "repository",
) -> Path:
    if not SLUG_PATTERN.fullmatch(slug):
        raise ValueError("Slug must use lowercase letters, numbers and single hyphens")
    for field, value in (("name", name), ("summary", summary)):
        if not value.strip() or "\n" in value or "\r" in value:
            raise ValueError(f"{field} must be a nonempty single-line string")
    validate_source({"source_url": source, "source_type": source_type})
    projects = load_projects(root)
    # Validate README markers before creating any project files.
    replace_index((root / "README.md").read_text(encoding="utf-8"), render_index(projects))
    if any(project["slug"] == slug for project in projects):
        raise ValueError(f"Project slug already exists: {slug}")
    next_id = max((int(project["id"]) for project in projects), default=0) + 1
    if next_id > 999:
        raise ValueError("All three-digit project IDs have been allocated")
    project_id = f"{next_id:03d}"
    target = root / "projects" / f"{project_id}-{slug}"
    template = root / "templates" / "project"
    replacements = {
        "ID": project_id, "SLUG": slug, "NAME": markdown_text(name),
        "SOURCE_URL": source, "SUMMARY": markdown_text(summary),
    }
    # Prepare and validate a complete copy before adding it to the real registry.
    with tempfile.TemporaryDirectory(prefix="github-research-") as temporary:
        staging_root = Path(temporary)
        staging = staging_root / "projects" / target.name
        shutil.copytree(template, staging)
        metadata_path = staging / "project.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata.update({
            "id": project_id, "slug": slug, "name": name, "summary": summary,
            "source_url": source,
        })
        if source_type != "repository":
            metadata["source_type"] = source_type
        metadata_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8", newline="\n",
        )
        readme_path = staging / "README.md"
        readme = re.sub(
                r"\{\{(\w+)\}\}", lambda match: replacements[match[1]],
                readme_path.read_text(encoding="utf-8"),
            )
        if source_type == "website":
            readme = readme.replace("原 GitHub 仓库", "官方产品网站").replace("原仓库", "官方来源")
        readme_path.write_text(
            readme,
            encoding="utf-8", newline="\n",
        )
        load_projects(staging_root)
        shutil.copytree(staging, target)
    update_readme(root)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="Short name, e.g. agent-workbench")
    parser.add_argument("--name", required=True, help="Display name")
    parser.add_argument("--source", required=True, help="Original GitHub repository or official product website URL")
    parser.add_argument("--source-type", choices=("repository", "website"), default="repository",
                        help="Use website for public product research without a source repository")
    parser.add_argument("--summary", default="待补充项目用途与研究重点。", help="One-line research summary")
    args = parser.parse_args()
    try:
        target = create_project(args.slug, args.name, args.source, args.summary, source_type=args.source_type)
    except (ValueError, OSError) as error:
        print(f"Project creation failed: {error}", file=sys.stderr)
        return 1
    print(f"Created projects/{target.name}; README index updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
