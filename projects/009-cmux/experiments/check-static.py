"""Check the local research artifact's references, assets and provenance."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

PROJECT = Path(__file__).resolve().parents[1]
WEB = PROJECT / "web"
COMMIT = "cdbe99596fe13784ec5ea24d2e1c720a8f67f5cb"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.chapters = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if data.get("id"):
            self.ids.append(data["id"])
        for attribute in ("href", "src"):
            if data.get(attribute):
                self.links.append(data[attribute])
        if tag == "section" and "chapter" in data.get("class", "").split():
            self.chapters.append(data["id"])
        if tag == "img":
            self.images.append(data)


def main():
    page = Page()
    html = (WEB / "index.html").read_text(encoding="utf-8")
    page.feed(html)
    assert len(page.ids) == len(set(page.ids)), "duplicate DOM IDs"
    assert len(page.chapters) == 10, "missing research chapters"
    assert len([item for item in page.ids if item.startswith("s-")]) == 20
    for link in page.links:
        if link.startswith("#"):
            assert link[1:] in page.ids, f"missing fragment: {link}"
        elif link.startswith("./"):
            asset = (WEB / link.split("#", 1)[0]).resolve()
            assert WEB.resolve() in asset.parents, f"asset outside web root: {link}"
            assert asset.is_file(), f"missing asset: {link}"
    assert all(image.get("alt", "").strip() for image in page.images)
    for name, copy in [("overview.svg", "01-understanding-overview.svg"), ("architecture.svg", "02-architecture.svg")]:
        asset = WEB / "assets" / name
        root = ET.parse(asset).getroot()
        assert root.find("{http://www.w3.org/2000/svg}title") is not None
        assert root.find("{http://www.w3.org/2000/svg}desc") is not None
        assert asset.read_bytes() == (PROJECT / "assets" / copy).read_bytes()
    for suffix in ("png", "svg"):
        assert (WEB / "assets" / f"complete-understanding.{suffix}").read_bytes() == (PROJECT / "assets" / f"07-complete-understanding.{suffix}").read_bytes()
    metadata = json.loads((PROJECT / "project.json").read_text(encoding="utf-8"))
    assert metadata["source_ref"] == COMMIT and COMMIT in html
    assert metadata["demo_url"] in {"", "https://yydshly.github.io/1013_codex_project/009-cmux/#understanding"}
    if metadata["demo_url"]:
        assert (PROJECT / "experiments" / "results" / "publication-2026-10-14.md").is_file(), "published entry needs a verification record"
    assert (PROJECT / metadata["preview"]).is_file()
    assert "非上游运行截图" in metadata["preview_caption"]
    assert len(metadata["summary_sections"]) == 12
    assert not re.search(r"\{\{(?:ID|SLUG|NAME|SUMMARY)\}\}", html)
    print(f"PASS 10 chapters, 20 source anchors, {len(page.links)} references, assets, SVG copies and provenance")


if __name__ == "__main__":
    main()
