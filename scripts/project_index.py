"""Read project metadata and render the README index using only the standard library."""

import html
import json
import re
from pathlib import Path
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- PROJECT_INDEX:START -->"
END = "<!-- PROJECT_INDEX:END -->"
SLUG_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DIRECTORY_PATTERN = re.compile(r"([0-9]{3})-([a-z0-9]+(?:-[a-z0-9]+)*)")
STATUSES = {
    "planned": "待研究",
    "researching": "研究中",
    "reproduced": "已复现",
    "completed": "已完成",
    "archived": "已归档",
}
TEXT_FIELDS = (
    "id", "slug", "name", "summary", "source_url", "source_ref",
    "source_license", "status", "preview", "preview_caption", "demo_url",
)
OPTIONAL_TEXT_FIELDS = {"source_ref", "source_license", "demo_url"}


def validate_url(value: str, *, github: bool = False) -> None:
    """Accept public HTTP(S) links, optionally requiring a GitHub repository URL."""
    url = urlsplit(value)
    if url.scheme not in {"http", "https"} or not url.hostname or re.search(r"\s", value):
        raise ValueError(f"Invalid HTTP(S) URL: {value!r}")
    if url.username or url.password:
        raise ValueError("URLs must not contain credentials")
    if github and (
        url.scheme != "https" or url.netloc != "github.com"
        or len(url.path.strip("/").split("/")) != 2 or url.query or url.fragment
    ):
        raise ValueError("source_url must be https://github.com/owner/repository")


def validate_summary_sections(metadata: dict, directory: str) -> list[dict]:
    """Validate optional labeled summary lines without changing legacy metadata."""
    if "summary_sections" not in metadata:
        return []
    sections = metadata["summary_sections"]
    if not isinstance(sections, list) or not sections:
        raise ValueError(f"{directory}: summary_sections must be a nonempty list")
    seen_labels = set()
    for section in sections:
        if not isinstance(section, dict):
            raise ValueError(f"{directory}: each summary section must be an object")
        for field in ("label", "text"):
            value = section.get(field)
            if (
                not isinstance(value, str) or not value.strip()
                or "\n" in value or "\r" in value
            ):
                raise ValueError(
                    f"{directory}: summary section {field} must be a nonempty single-line string"
                )
        label = section["label"].strip()
        if label in seen_labels:
            raise ValueError(f"{directory}: duplicate summary section label: {label}")
        seen_labels.add(label)
    return sections


def source_repository_name(source_url: str) -> str:
    """Return the repository name from an already validated source URL."""
    return urlsplit(source_url).path.rstrip("/").rsplit("/", 1)[-1]


def load_projects(root: Path = ROOT) -> list[dict]:
    """Validate real project folders; templates and directory documentation are excluded."""
    projects = []
    seen_slugs = set()
    seen_ids = set()
    directory_root = root / "projects"
    if not directory_root.is_dir():
        raise ValueError("Missing projects directory")
    for directory in sorted(directory_root.iterdir()):
        if not directory.is_dir():
            continue
        match = DIRECTORY_PATTERN.fullmatch(directory.name)
        if not match or match[1] == "000":
            raise ValueError(f"Invalid project directory: {directory.name}")
        metadata_path = directory / "project.json"
        if not metadata_path.is_file():
            raise ValueError(f"Missing project.json: {directory.name}")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if not isinstance(metadata, dict):
            raise ValueError(f"project.json must be an object: {directory.name}")
        for field in TEXT_FIELDS:
            value = metadata.get(field)
            if not isinstance(value, str) or "\n" in value or "\r" in value:
                raise ValueError(f"{directory.name}: {field} must be a single-line string")
            if field not in OPTIONAL_TEXT_FIELDS and not value.strip():
                raise ValueError(f"{directory.name}: {field} must not be empty")
        if (metadata["id"], metadata["slug"]) != (match[1], match[2]):
            raise ValueError(f"Metadata id/slug does not match {directory.name}")
        if metadata["id"] in seen_ids or metadata["slug"] in seen_slugs:
            raise ValueError(f"Duplicate id or slug: {directory.name}")
        if metadata["status"] not in STATUSES:
            raise ValueError(f"Unknown project status: {metadata['status']}")
        tags = metadata.get("tags")
        if not isinstance(tags, list) or any(
            not isinstance(tag, str) or not tag.strip() or "\n" in tag or "\r" in tag
            for tag in tags
        ):
            raise ValueError(f"{directory.name}: tags must be a list of nonempty strings")
        validate_summary_sections(metadata, directory.name)
        validate_url(metadata["source_url"], github=True)
        if metadata["demo_url"]:
            validate_url(metadata["demo_url"])
        preview = metadata["preview"]
        if "\\" in preview or not preview.startswith("assets/"):
            raise ValueError(f"{directory.name}: preview must be a path inside assets/")
        image_path = (directory / preview).resolve()
        assets_root = (directory / "assets").resolve()
        if assets_root not in image_path.parents or not image_path.is_file():
            raise ValueError(f"{directory.name}: missing preview or path outside assets/")
        if image_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
            raise ValueError(f"{directory.name}: unsupported preview image format")
        if not (directory / "README.md").is_file():
            raise ValueError(f"Missing project README: {directory.name}")
        seen_ids.add(metadata["id"])
        seen_slugs.add(metadata["slug"])
        projects.append({**metadata, "directory": directory.name})
    return sorted(projects, key=lambda project: int(project["id"]))


def markdown_text(value: str) -> str:
    value = html.escape(value, quote=False)
    return re.sub(r"([\\`*_|\[\]])", r"\\\1", value)


def link_url(value: str) -> str:
    return quote(value, safe="/:?=&%#@+;,$!~.-_")


def has_guide_image(project: dict) -> bool:
    """Display validated previews outside the table, excluding labeled placeholders."""
    preview = project.get("preview", "")
    caption = project.get("preview_caption", "")
    return (
        isinstance(preview, str) and bool(preview.strip())
        and isinstance(caption, str) and bool(caption.strip())
        and not any(marker in caption for marker in ("占位", "待添加"))
    )


def render_index(projects: list[dict]) -> str:
    lines = [f"当前收录 **{len(projects)}** 个项目，按三位编号升序排列。", ""]
    if not projects:
        lines.append(
            "暂无研究项目。首个项目将从 **001** 开始；添加后，这里会展示项目摘要、目标源库、研究状态和相关入口。"
        )
        return "\n".join(lines)
    lines.extend([
        "| 编号 | 项目 / 研究摘要 | 目标源库 | 研究状态 | 相关入口 |",
        "| --- | --- | --- | --- | --- |",
    ])
    for project in projects:
        path = f"./projects/{project['directory']}"
        name = markdown_text(project["name"])
        sections = validate_summary_sections(project, project["directory"])
        summary = "<br>".join(
            f"**{markdown_text(section['label'])}：** {markdown_text(section['text'])}"
            for section in sections
        ) if sections else markdown_text(project["summary"])
        tags = " · ".join(markdown_text(tag) for tag in project["tags"])
        intro = f"**[{name}]({path}/README.md)**<br><br>{summary}"
        if tags:
            intro += f"<br><br>{tags}"
        source_url = project["source_url"]
        source_name = markdown_text(source_repository_name(source_url))
        source_owner = markdown_text(urlsplit(source_url).path.strip("/").split("/")[0])
        source = f"[{source_name}]({link_url(source_url)})<br>{source_owner}"
        entries = f"[研究文档]({path}/README.md)"
        if project["demo_url"]:
            entries += f"<br>[在线演示]({link_url(project['demo_url'])})"
        else:
            entries += "<br>演示未部署"
        lines.append(
            f"| **{project['id']}** | {intro} | {source} | {STATUSES[project['status']]} | {entries} |"
        )
    guides = [project for project in projects if has_guide_image(project)]
    if guides:
        lines.extend([
            "", "## 项目引导图", "",
            "引导图独立展示在索引表外。点击图片进入研究文档，图片说明保留其内容与来源。", "",
        ])
        for project in guides:
            path = f"./projects/{project['directory']}"
            image_url = link_url(f"{path}/{project['preview']}")
            readme_url = link_url(f"{path}/README.md")
            caption = markdown_text(project["preview_caption"])
            entries = f"[查看原图]({image_url}) · [研究文档]({readme_url})"
            if project["demo_url"]:
                entries += f" · [在线演示]({link_url(project['demo_url'])})"
            lines.extend([
                f"### {project['id']} · {markdown_text(project['name'])}", "",
                f"[![{caption}]({image_url})]({readme_url})", "",
                f"图片说明与来源：{caption}", "", entries, "",
            ])
    return "\n".join(lines)


def replace_index(readme: str, index: str) -> str:
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("README must contain exactly one pair of PROJECT_INDEX markers")
    start = readme.index(START) + len(START)
    end = readme.index(END)
    if start > end:
        raise ValueError("PROJECT_INDEX markers are in the wrong order")
    return readme[:start] + "\n" + index + "\n" + readme[end:]


def update_readme(root: Path = ROOT, *, check: bool = False) -> bool:
    projects = load_projects(root)
    path = root / "README.md"
    original = path.read_text(encoding="utf-8")
    updated = replace_index(original, render_index(projects))
    if original == updated:
        return True
    if check:
        return False
    path.write_text(updated, encoding="utf-8", newline="\n")
    return True
