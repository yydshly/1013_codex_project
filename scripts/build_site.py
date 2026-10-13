"""Collect public static demos and render a complete GitHub Pages navigation page."""

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

from project_index import DIRECTORY_PATTERN, ROOT, STATUSES, validate_url

STATIC_EXTENSIONS = {
    ".html", ".css", ".js", ".mjs", ".json", ".txt", ".svg", ".png",
    ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".ico", ".woff", ".woff2",
    ".ttf", ".otf", ".mp3", ".mp4", ".webm", ".pdf",
}
EXCLUDED_PARTS = {
    "node_modules", "__pycache__", "experiments", "references", "coverage",
    "private", "secrets", "server", "backend",
}
MARKER = "site-build.json"
DEFAULT_REPOSITORY = "yydshly/1013_codex_project"


def tracked_paths(root: Path) -> set[str]:
    """Read the Git index; local untracked projects are never selected implicitly."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError("Cannot read Git tracked files; use --project for a local preview") from error
    return set(result.stdout.decode("utf-8").rstrip("\0").split("\0")) - {""}


def read_metadata(root: Path, directory: str) -> dict:
    match = DIRECTORY_PATTERN.fullmatch(directory)
    if not match or match[1] == "000":
        raise ValueError(f"Invalid project directory: {directory}")
    project_root = root / "projects" / directory
    if project_root.is_symlink() or not project_root.is_dir():
        raise ValueError(f"Project must be a regular directory: {directory}")
    path = project_root / "project.json"
    if path.is_symlink():
        raise ValueError(f"Metadata must not be a symbolic link: {directory}")
    metadata = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(metadata, dict):
        raise ValueError(f"Metadata must be an object: {directory}")
    for field in ("id", "slug", "name", "summary", "source_url", "status", "preview", "preview_caption"):
        value = metadata.get(field)
        if not isinstance(value, str) or not value.strip() or "\n" in value or "\r" in value:
            raise ValueError(f"{directory}: {field} must be a nonempty single-line string")
    if (metadata["id"], metadata["slug"]) != (match[1], match[2]):
        raise ValueError(f"Metadata id/slug does not match {directory}")
    if metadata["status"] not in STATUSES:
        raise ValueError(f"Unknown project status: {directory}")
    tags = metadata.get("tags")
    if not isinstance(tags, list) or any(not isinstance(tag, str) or not tag.strip() for tag in tags):
        raise ValueError(f"{directory}: tags must be a list of nonempty strings")
    validate_url(metadata["source_url"], github=True)
    for field in ("source_ref", "source_license", "demo_url"):
        value = metadata.get(field, "")
        if not isinstance(value, str) or "\n" in value or "\r" in value:
            raise ValueError(f"{directory}: {field} must be a single-line string")
        metadata[field] = value
    if metadata["demo_url"]:
        validate_url(metadata["demo_url"])
    preview = Path(metadata["preview"])
    assets_path = project_root / "assets"
    assets = assets_path.resolve()
    preview_path = project_root / preview
    if (
        "\\" in metadata["preview"] or not metadata["preview"].startswith("assets/")
        or assets_path.is_symlink() or project_root.resolve() not in assets.parents
        or preview_path.is_symlink() or assets not in preview_path.resolve().parents
        or not preview_path.is_file()
        or preview_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
    ):
        raise ValueError(f"{directory}: invalid public preview image")
    return {**metadata, "directory": directory}


def is_public_static(relative: Path) -> bool:
    """Only web assets are public; hidden/configuration/executable files are excluded."""
    parts = [part.lower() for part in relative.parts]
    if any(part.startswith(".") or part in EXCLUDED_PARTS for part in parts):
        return False
    if relative.name.lower() in {
        "readme.txt", "requirements.txt", "package.json", "package-lock.json",
        "credentials.json", "secrets.json", "config.local.json",
    }:
        return False
    return relative.suffix.lower() in STATIC_EXTENSIONS


def demo_files(root: Path, project: dict, tracked: set[str] | None) -> list[Path]:
    project_root = root / "projects" / project["directory"]
    web = project_root / "web"
    if web.is_symlink():
        raise ValueError(f"Web root must not be a symbolic link: {project['directory']}")
    files = []
    for path in sorted(web.rglob("*")) if web.is_dir() else []:
        relative = path.relative_to(web)
        if tracked is not None and path.relative_to(root).as_posix() not in tracked:
            continue
        if path.is_symlink() or web.resolve() not in path.resolve().parents:
            raise ValueError(f"Static assets must not be symbolic links: {path.relative_to(root)}")
        if not is_public_static(relative):
            continue
        if path.is_file():
            files.append(path)
    return files


def render_home(projects: list[dict], repository: str) -> str:
    cards = []
    for project in projects:
        directory = quote(project["directory"], safe="-_")
        research_url = f"https://github.com/{repository}/blob/main/projects/{directory}/README.md"
        preview = f"./previews/{directory}{Path(project['preview']).suffix.lower()}"
        name, summary = html.escape(project["name"]), html.escape(project["summary"])
        caption = html.escape(project["preview_caption"], quote=True)
        tags = "".join(f"<span>{html.escape(tag)}</span>" for tag in project["tags"])
        source = html.escape(project["source_url"], quote=True)
        cards.append(f'''<article class="project-card">
  <a class="preview" href="./{directory}/"><img src="{preview}" alt="{caption}" loading="lazy"></a>
  <div class="project-content"><div class="project-meta">项目 {project['id']} · {STATUSES[project['status']]}</div>
    <h2><a href="./{directory}/">{name}</a></h2><p class="summary">{summary}</p>
    <div class="tags">{tags}</div><p class="preview-caption">{html.escape(project['preview_caption'])}</p>
    <div class="links"><a class="primary" href="./{directory}/">查看理解与演示 →</a>
      <a href="{research_url}">研究文档 ↗</a><a href="{source}">原仓库 ↗</a></div>
  </div>
</article>''')
    content = "\n".join(cards) or '<p class="empty">暂无已提交的静态演示。</p>'
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="开源项目研究：能力、实现原理、输入输出、实际效果、价值与局限，附源码证据和可交互演示。">
<title>开源项目研究 · 能力、原理与价值</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;color:#202a32;background:#f5f6f2;font-family:system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;line-height:1.75}}
.wrap{{max-width:1120px;margin:auto;padding:42px 24px}}header{{border-bottom:1px solid #dce2da;margin-bottom:32px;padding-bottom:26px}}
.eyebrow,.project-meta{{color:#50765d;font-size:13px;letter-spacing:.05em}}h1{{font-size:clamp(26px,4vw,40px);line-height:1.3;margin:12px 0}}header p{{color:#53636a;max-width:850px}}
a{{color:#2b6343;text-underline-offset:4px}}.project-card{{display:grid;grid-template-columns:285px 1fr;background:#fff;border:1px solid #dce2da;border-radius:16px;overflow:hidden;margin:0 0 24px}}
.preview{{display:flex;align-items:center;padding:18px;background:#edf0ea}}.preview img{{width:100%;height:auto;border-radius:9px}}.project-content{{padding:26px}}h2{{font-size:22px;line-height:1.45;margin:8px 0 12px}}h2 a{{text-decoration:none}}
.summary{{margin:0 0 16px;overflow-wrap:anywhere}}.tags{{display:flex;flex-wrap:wrap;gap:7px}}.tags span{{font-size:12px;background:#eef4ed;border-radius:20px;padding:3px 10px}}
.preview-caption{{font-size:12px;color:#748078}}.links{{display:flex;flex-wrap:wrap;gap:16px;font-size:14px}}.primary{{font-weight:650}}footer{{color:#748078;font-size:13px;margin-top:32px}}.empty{{padding:28px;background:white;border-radius:12px}}
@media(max-width:700px){{.wrap{{padding:28px 16px}}.project-card{{grid-template-columns:1fr}}.preview img{{max-height:230px;object-fit:contain}}.project-content{{padding:21px}}}}
</style></head><body><main class="wrap"><header><div class="eyebrow">GITHUB 开源项目研究</div><h1>理解能力、原理与实际价值。</h1>
<p>从源码和演示出发，说明项目能做什么、如何执行、接受什么输入、产生什么输出，以及它对我们有什么用。区分验证结果、研究判断与尚未验证的事项。</p>
<p>当前有 {len(projects)} 个静态研究演示。摘要完整保留，进入项目可查看详细说明与示例。</p></header>
{content}<footer><a href="https://github.com/{repository}">查看研究仓库 ↗</a> · 静态页面公开展示；模型密钥和本地实验后端不随站点发布。</footer></main></body></html>
'''


def build_site(
    root: Path = ROOT, *, projects: list[str] | None = None,
    output: str = "site-dist", repository: str = DEFAULT_REPOSITORY,
) -> list[dict]:
    root = root.resolve()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Repository must be owner/repository")
    if not re.fullmatch(r"site-[a-z0-9-]+", output):
        raise ValueError("Output must be a direct generated site-* directory inside the repository")
    destination = root / output
    if destination.is_symlink() or destination.resolve().parent != root:
        raise ValueError("Output must remain inside the repository and must not be a symbolic link")
    if destination.exists() and (
        not destination.is_dir() or (any(destination.iterdir()) and not (destination / MARKER).is_file())
    ):
        raise ValueError("Refusing to replace an output directory without a site-build.json marker")
    tracked = None if projects else tracked_paths(root)
    directories = list(dict.fromkeys(projects or sorted({
        parts[1] for path in tracked or set()
        if len(parts := path.split("/")) == 3 and parts[0] == "projects" and parts[2] == "project.json"
    })))
    selected = []
    for directory in directories:
        metadata = read_metadata(root, directory)
        files = demo_files(root, metadata, tracked)
        entry = root / "projects" / directory / "web" / "index.html"
        if entry not in files:
            if projects or metadata["demo_url"]:
                raise ValueError(f"Missing publishable web/index.html for {directory}; cannot drop a deployed entry")
            continue
        preview = root / "projects" / directory / metadata["preview"]
        if tracked is not None and preview.relative_to(root).as_posix() not in tracked:
            raise ValueError(f"Preview image must be tracked before publishing: {directory}")
        selected.append((metadata, files, preview))
    selected.sort(key=lambda item: int(item[0]["id"]))
    # Build completely before replacing any previous output; no input directories are deleted.
    with tempfile.TemporaryDirectory(prefix=".site-build-", dir=root) as temporary:
        staging = Path(temporary)
        for metadata, files, preview in selected:
            target = staging / metadata["directory"]
            web = root / "projects" / metadata["directory"] / "web"
            for path in files:
                copied = target / path.relative_to(web)
                copied.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, copied)
            previews = staging / "previews"
            previews.mkdir(exist_ok=True)
            shutil.copyfile(preview, previews / f"{metadata['directory']}{preview.suffix.lower()}")
        published = [item[0] for item in selected]
        (staging / "index.html").write_text(render_home(published, repository), encoding="utf-8", newline="\n")
        (staging / ".nojekyll").write_text("", encoding="utf-8")
        (staging / MARKER).write_text(json.dumps({
            "generator": "scripts/build_site.py", "repository": repository,
            "projects": [project["directory"] for project in published],
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(staging, destination)
    return published


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", action="append", dest="projects", help="Explicit local preview project; repeat to select several")
    parser.add_argument("--output", default="site-dist", help="Generated site-* directory, default: site-dist")
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPOSITORY))
    args = parser.parse_args()
    try:
        projects = build_site(projects=args.projects, output=args.output, repository=args.repository)
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"Site build failed: {error}", file=sys.stderr)
        return 1
    print(f"Built {args.output}/ with {len(projects)} static project(s): " + ", ".join(project["directory"] for project in projects))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
