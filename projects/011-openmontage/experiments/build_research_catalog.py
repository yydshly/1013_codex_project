"""Render the original research catalog into the static page and README.

Uses only the Python standard library. Does not install or invoke OpenMontage.
"""
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
WEB = PROJECT / "web"
CATEGORIES = {
    "prepare": "研究与检索", "generate": "素材生成", "process": "已有视频处理",
    "compose": "画面与合成", "govern": "制作管理", "deliver": "交付与复用",
}


def source_url(data, source):
    mode = "tree" if source["path"] == "tools/graphics" else "blob"
    return ("https://github.com/calesthio/OpenMontage/" + mode + "/" +
            data["source_ref"] + "/" + source["path"])


def replace_block(text, name, content):
    pattern = r"(<!-- " + name + r":START -->).*?(<!-- " + name + r":END -->)"
    if len(re.findall(pattern, text, re.S)) != 1:
        raise ValueError("Expected exactly one block: " + name)
    return re.sub(pattern, lambda m: m[1] + "\n" + content + "\n" + m[2],
                  text, flags=re.S)


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "nav", "aside", "header", "footer"}:
            self.skip += 1
        if not self.skip and tag in {"h1", "h2", "h3", "p", "li", "tr", "article", "summary"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "nav", "aside", "header", "footer"}:
            self.skip = max(0, self.skip - 1)
        if not self.skip and tag in {"h1", "h2", "h3", "p", "li", "tr", "article", "summary"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.parts.append(data.strip() + " ")


def main():
    data = json.loads((WEB / "research.json").read_text(encoding="utf-8"))
    metadata = json.loads((PROJECT / "project.json").read_text(encoding="utf-8"))
    summaries = {section["label"]: section["text"] for section in metadata["summary_sections"]}
    brief_specs = [("能力", "能力是什么？", "capabilities"), ("原理", "如何组织与执行？", "workflow"),
                   ("核心价值", "最有价值的是什么？", "value"), ("可扩展场景", "可以扩展到哪些工作？", "extensions")]
    sources = {source["id"]: source for source in data["sources"]}
    comparison = json.loads((WEB / "comparison.json").read_text(encoding="utf-8"))
    comparison_rows = []
    comparison_markdown = ["| 项目 / 研究依据 | 输入 → 输出 | 与 OpenMontage 的区别 | 可借鉴设计 |", "| --- | --- | --- | --- |"]
    escape = html.escape
    brief_cards = []
    brief_markdown = []
    for number, (label, heading, target) in enumerate(brief_specs, 1):
        brief_cards.append('<article><span class="brief-index">0' + str(number) + ' / ' + label +
                           '</span><h3>' + heading + '</h3><p>' + escape(summaries[label]) +
                           '</p><a href="#' + target + '">展开' + label + '说明 ↓</a></article>')
        brief_markdown.append("**" + label + "：** " + summaries[label])
    for item in comparison["projects"]:
        version = ("固定版本 " + item["source_ref"][:12] if item["source_ref"]
                   else "公开资料核对 " + comparison["date"])
        baseline = ' class="current-product"' if item["id"] == "011-openmontage" else ""
        comparison_rows.append(
            '<tr data-project="' + escape(item["id"], quote=True) + '"' + baseline + '>'
            '<td data-label="项目 / 依据"><span class="project-role">' + escape(item["role"]) +
            '</span><a href="' + escape(item["evidence_url"], quote=True) +
            '" target="_blank" rel="noopener noreferrer">' + escape(item["name"]) +
            ' ↗</a><small class="project-version">' + escape(version) + '</small></td>'
            '<td data-label="输入 → 输出"><p><span class="io-label">输入：</span>' +
            escape(item["input"]) + '</p><p><span class="io-label">输出：</span>' +
            escape(item["output"]) + '</p></td>'
            '<td data-label="定位与差异">' + escape(item["difference"]) + '</td>'
            '<td data-label="可借鉴设计">' + escape(item["value"]) + '</td></tr>'
        )
        comparison_markdown.append(
            '| **' + item["name"] + '**<br>' + item["role"] +
            '<br>[研究](../' + item["id"] + '/README.md) · [依据](' + item["evidence_url"] +
            ')<br>' + version + ' | ' + item["input"] + ' → ' + item["output"] +
            ' | ' + item["difference"] + ' | ' + item["value"] + ' |'
        )
    rows = []
    for cap in data["capabilities"]:
        if cap["source"] not in sources or cap["category"] not in CATEGORIES:
            raise ValueError("Invalid catalog reference")
        rows.append(
            '<tr data-category="' + cap["category"] + '">'
            '<td data-label="能力"><small>' + escape(CATEGORIES[cap["category"]]) +
            '</small>' + escape(cap["name"]) + '</td>'
            '<td data-label="输入 / 输出"><p><span class="io-label">输入：</span>' +
            escape(cap["input"]) + '</p><p><span class="io-label">输出：</span>' +
            escape(cap["output"]) + '</p></td>'
            '<td data-label="实现方法">' + escape(cap["basis"]) + '</td>'
            '<td data-label="使用边界">' + escape(cap["boundary"]) + '</td>'
            '<td data-label="证据"><a href="#source-' + cap["source"] +
            '" aria-label="' + escape(cap["name"] + "的来源") + '">↗</a></td></tr>'
        )
    cards = []
    for i, pipeline in enumerate(data["pipelines"], 1):
        url = ("https://github.com/calesthio/OpenMontage/blob/" + data["source_ref"] +
               "/pipeline_defs/" + pipeline["id"] + ".yaml")
        cards.append(
            '<article class="pipeline-card"><header><span>' + f"{i:02d}" +
            '</span><div><h3>' + escape(pipeline["name"]) + '</h3><code>' +
            escape(pipeline["id"]) + '</code></div></header><p><strong>输入：</strong>' +
            escape(pipeline["input"]) + '</p><p><strong>输出：</strong>' +
            escape(pipeline["output"]) + '</p><p>' + escape(pipeline["note"]) +
            ' <a href="' + url + '" target="_blank" rel="noopener noreferrer">流程定义 ↗</a></p></article>'
        )
    links = [
        '<li id="source-' + source["id"] + '"><a href="' +
        source_url(data, source) + '" target="_blank" rel="noopener noreferrer">' +
        escape(source["title"]) + '</a><span>' + escape(source["kind"]) +
        ' · ' + escape(source["path"]) + '</span></li>'
        for source in data["sources"]
    ]
    page = (WEB / "index.html").read_text(encoding="utf-8")
    for name, content in [("CAPABILITIES", "\n".join(rows)),
                          ("PIPELINES", "\n".join(cards)), ("SOURCES", "\n".join(links)),
                          ("COMPARISON", "\n".join(comparison_rows)), ("BRIEF", "\n".join(brief_cards))]:
        page = replace_block(page, name, content)
    (WEB / "index.html").write_text(page, encoding="utf-8", newline="\n")

    readme_path = PROJECT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    catalog = ["| 类别 | 能力 | 输入 → 输出 | 实现与边界 |", "| --- | --- | --- | --- |"]
    for cap in data["capabilities"]:
        catalog.append("| " + CATEGORIES[cap["category"]] + " | " + cap["name"] + " | " +
                       cap["input"] + " → " + cap["output"] + " | " + cap["basis"] +
                       "；" + cap["boundary"] + " |")
    readme = replace_block(readme, "CAPABILITIES", "\n".join(catalog))
    readme = replace_block(readme, "BRIEF", "\n\n".join(brief_markdown))
    readme = replace_block(readme, "COMPARISON", "\n".join(comparison_markdown))
    readme = replace_block(readme, "SOURCES", "\n".join(
        "- [" + source["title"] + "](" + source_url(data, source) + ")：" + source["kind"]
        for source in data["sources"]
    ))
    readme_path.write_text(readme, encoding="utf-8", newline="\n")
    parser = PlainText()
    parser.feed(page)
    text = re.sub(r"\n\s*\n+", "\n\n", "".join(parser.parts)).strip()
    text = "\n".join(line.rstrip() for line in text.splitlines())
    text += "\n\n固定来源链接\n" + "\n".join(
        source["title"] + "\n" + source_url(data, source) for source in data["sources"]
    )
    text += "\n\n既有项目对比依据\n" + comparison["basis"] + "\n" + "\n".join(
        item["name"] + "\n" + item["evidence_url"] for item in comparison["projects"]
    )
    (WEB / "research-summary.txt").write_text(text + "\n", encoding="utf-8", newline="\n")
    print("Rendered", len(rows), "capabilities,", len(cards), "pipelines and", len(links), "sources.")
    print("Compared", len(comparison_rows), "projects including the OpenMontage baseline.")


if __name__ == "__main__":
    main()
