"""Generate static guide fragments from authored research data, without REA."""
from pathlib import Path
import html
import json
import re

PROJECT = Path(__file__).resolve().parents[1]


def replace_region(text, name, body):
    pattern = rf"(<!-- {name}_START -->).*?(<!-- {name}_END -->)"
    updated, count = re.subn(pattern, lambda m: m[1] + "\n" + body + "\n" + m[2], text, flags=re.S)
    if count != 1:
        raise ValueError(f"Expected one {name} region; found {count}")
    return updated


def render_comparisons(data):
    """Render the same reviewed comparison content for the page and README."""
    esc = lambda value: html.escape(value, quote=True)
    markdown = lambda value: value.replace("|", "\\|").replace("\n", " ")
    baseline = data["baseline"]
    table_rows = [
        '<tr class="comparison-baseline"><th scope="row">REA<br><small>软件调查 · 本页基准</small></th>'
        f'<td>{esc(baseline["goal"])}<br>{esc(baseline["input"])}</td>'
        f'<td>{esc(" → ".join(baseline["flow"]))}</td>'
        f'<td>{esc(baseline["output"])}</td><td>围绕问题取得证据，再解释与验证。</td></tr>'
    ]
    options, details, md_rows, md_details = [], [], [], []
    for item in data["projects"]:
        selected = ' selected' if item["slug"] == data["default_project"] else ''
        options.append(f'<option value="{esc(item["slug"])}"{selected}>{esc(item["name"])} · {esc(item["similarity"])}</option>')
        source_links = " · ".join(
            f'<a href="{esc(source["url"])}" target="_blank" rel="noopener">{esc(source["title"])}</a>'
            for source in item["sources"]
        )
        version = item["source_ref"][:12] or '官方资料 · ' + item["record_date"]
        table_rows.append(
            f'<tr><th scope="row">{esc(item["name"])}<br><small>{esc(item["role"])}</small>'
            f'<br><a href="{esc(item["web_href"])}">已有导读 ↗</a></th>'
            f'<td>{esc(item["goal"])}<br>{esc(item["input"])}</td>'
            f'<td>{esc(" → ".join(item["flow"]))}</td><td>{esc(item["output"])}</td>'
            f'<td>{esc(item["difference"])}</td></tr>'
        )
        details.append(
            f'<article class="comparison-detail" data-comparison="{esc(item["slug"])}" aria-labelledby="compare-title-{esc(item["project_id"])}">'
            f'<div class="mini-label">{esc(item["similarity"])} / {esc(item["role"])}</div>'
            f'<h3 id="compare-title-{esc(item["project_id"])}">REA 与 {esc(item["name"])}：分工在哪里？</h3>'
            '<div class="comparison-paths"><div><h4>REA 的路径</h4>'
            f'<p>{esc(" → ".join(baseline["flow"]))}</p><p class="compare-result">产物：{esc(baseline["output"])}</p></div>'
            f'<div><h4>{esc(item["name"])} 的路径</h4><p>{esc(" → ".join(item["flow"]))}</p>'
            f'<p class="compare-result">产物：{esc(item["output"])}</p></div></div>'
            '<dl class="comparison-facts">'
            + "".join(f'<div><dt>{label}</dt><dd>{esc(item[key])}</dd></div>' for label, key in [
                ("实现原理", "principle"), ("共同设计", "shared"), ("关键差异", "difference"),
                ("选择依据", "use_when"), ("证据边界", "boundary"), ("实际验证", "validation")
            ])
            + f'</dl><p class="comparison-source">研究基线 {esc(version)} · {source_links}</p></article>'
        )
        readme_link = f'../{item["slug"]}/README.md'
        md_rows.append('| ' + ' | '.join([
            f'[{item["name"]}]({readme_link}) · {markdown(item["role"])}',
            markdown(item["goal"]), markdown(" → ".join(item["flow"])),
            markdown(item["output"]), markdown(item["difference"])
        ]) + ' |')
        md_details.append(
            f'### REA 与 {item["name"]}\n\n'
            + "\n\n".join(f'**{label}：** {item[key]}' for label, key in [
                ("实现原理", "principle"), ("共同设计", "shared"), ("关键差异", "difference"),
                ("选择依据", "use_when"), ("证据边界", "boundary"), ("实际验证", "validation")
            ])
            + f'\n\n基线：{version}；[本仓库研究]({readme_link})；'
            + '、'.join(f'[{source["title"]}]({source["url"]})' for source in item["sources"]) + '。'
        )
    table = '<div class="table-scroll comparison-table"><table><caption>按职责与机制对照：REA 与十个已有研究项目</caption><thead><tr>' \
        '<th scope="col">项目与位置</th><th scope="col">问题与输入</th><th scope="col">工作路径</th>' \
        '<th scope="col">主要输出</th><th scope="col">与 REA 的差异</th></tr></thead><tbody>' + ''.join(table_rows) + '</tbody></table></div>'
    controls = '<div class="comparison-controls"><div><label for="compare-project">选择对比项目</label>' \
        '<select id="compare-project">' + ''.join(options) + '</select></div>' \
        '<button class="button secondary small" id="compare-expand" type="button" aria-pressed="false">展开全部原理</button></div>'
    body = controls + '<div id="comparison-details">' + ''.join(details) + '</div>' + table
    md_table = '| 项目与位置 | 回答的问题 | 工作路径 | 主要输出 | 与 REA 的差异 |\n| --- | --- | --- | --- | --- |\n' + '\n'.join(md_rows)
    return body, md_table + '\n\n' + '\n\n'.join(md_details)


def render_toolchain(data):
    source_root = f'https://github.com/morluto/rea/blob/{data["source_ref"]}/'
    rows, markdown_rows = [], []
    for item in data["modules"]:
        sources = " · ".join(f'<a href="{source_root}{html.escape(doc)}">{html.escape(doc.removeprefix("docs/"))}</a>' for doc in item["docs"])
        values = [item["tools"], item["principle"], item["output"], item["handoff"], item["limit"]]
        rows.append(f'<tr><th scope="row">{item["no"]} · {html.escape(item["name"])}<br><small>{html.escape(item["kind"])}</small></th>'
                    + ''.join(f'<td>{html.escape(value)}</td>' for value in values)
                    + f'<td>{sources}</td></tr>')
        cells = [item["no"]+' · '+item["name"], *values]
        links = '、'.join(f'[{doc.removeprefix("docs/")}]({source_root}{doc})' for doc in item["docs"])
        markdown_rows.append('| '+' | '.join(value.replace('|', '\\|') for value in cells)+f' | {links} |')
    heads = ['模块', '工具', '原理', '返回材料', '串接', '范围', '固定依据']
    table_html = '<div class="table-scroll toolchain-table"><table><thead><tr>'+''.join(f'<th scope="col">{head}</th>' for head in heads)+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'
    table_md = '| '+' | '.join(heads)+' |\n| '+' | '.join('---' for _ in heads)+' |\n'+'\n'.join(markdown_rows)
    return table_html, table_md


def render_understanding(metadata):
    cards, paragraphs = [], []
    for index, item in enumerate(metadata["summary_sections"]):
        label, text = html.escape(item["label"]), html.escape(item["text"])
        core = " brief-card-core" if index < 5 else ""
        cards.append(f'<article class="brief-card{core}"><div class="mini-label">{index+1:02d} / REA RESEARCH</div><h3>{label}</h3><p>{text}</p></article>')
        paragraphs.append(f'### {item["label"]}\n\n{item["text"]}')
    return '<div class="brief-grid">'+''.join(cards)+'</div>', '\n\n'.join(paragraphs)


def render_extensions(data):
    keys = ["name", "materials", "modules", "implementation", "output", "acceptance"]
    heads = ["扩展场景", "输入材料", "模块交接", "实施方式", "输出成果", "如何验收"]
    rows, paragraphs = [], []
    for item in data["scenarios"]:
        rows.append('<tr><th scope="row">'+html.escape(item["name"])+'</th>'
                    + ''.join('<td>'+html.escape(item[key])+'</td>' for key in keys[1:])+'</tr>')
        paragraphs.append('#### '+item["name"]+'\n\n'+'\n\n'.join(
            '**'+head+'：** '+item[key] for head, key in zip(heads[1:], keys[1:])))
    table = '<div class="table-scroll extension-scenarios"><table><caption>本仓库的八种扩展建议，尚未实现</caption><thead><tr>' \
        + ''.join('<th scope="col">'+head+'</th>' for head in heads)+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'
    return table, '\n\n'.join(paragraphs)


def main():
    catalog = json.loads((PROJECT / "web/data/capabilities.json").read_text(encoding="utf-8"))
    source_root = f'https://github.com/morluto/rea/blob/{catalog["source_ref"]}/'
    cards, rows = [], []
    for item in catalog["capabilities"]:
        e = {key: html.escape(value, quote=True) for key, value in item.items()}
        cards.append(
            f'<article class="cap-card" id="cap-{e["id"]}" data-group="{e["group"]}" data-mode="{e["mode"]}">'
            f'<div class="cap-meta"><span>{e["group"]}</span><span>{e["mode"]}</span></div><h3>{e["name"]}</h3>'
            f'<dl><dt>输入</dt><dd>{e["input"]}</dd><dt>输出</dt><dd>{e["output"]}</dd>'
            f'<dt>条件</dt><dd>{e["requirements"]}</dd></dl><p class="cap-boundary"><strong>边界：</strong>{e["boundary"]}</p>'
            f'<a class="source-link" href="{source_root}{e["doc"]}" target="_blank" rel="noopener">固定版本专题依据 ↗</a></article>'
        )
        values = [item[k].replace("|", "\\|").replace("\n", " ") for k in ["name", "input", "output", "requirements", "boundary"]]
        rows.append("| " + " | ".join(values) + f' | [来源]({source_root}{item["doc"]}) |')
    index_path = PROJECT / "web/index.html"
    page = replace_region(index_path.read_text(encoding="utf-8"), "CAPABILITIES", "\n".join(cards))
    page = re.sub(r'(<a\b[^>]*data-doc="([^"]+)"[^>]*href=")[^"]*(")',
                  lambda m: m[1] + source_root + m[2] + m[3], page)
    script = (PROJECT / "web/app.js").read_text(encoding="utf-8")
    scenarios = re.findall(r'name: "([^"\n]+)",\s*steps: \[(.*?)\n    \]', script, re.S)
    if len(scenarios) != 3:
        raise ValueError("Expected three teaching scenarios")
    references = []
    for name, raw in scenarios:
        steps = json.loads("[" + raw + "]")
        if len(steps) != 6:
            raise ValueError("Expected six steps per scenario")
        items = "".join(f'<li><strong>{html.escape(s[1])}</strong><p>{html.escape(s[2])}</p></li>' for s in steps)
        references.append(f'<article><h3>{html.escape(name)}</h3><ol>{items}</ol></article>')
    page = replace_region(page, "SCENARIOS", "\n".join(references))
    comparisons = json.loads((PROJECT / "web/data/comparisons.json").read_text(encoding="utf-8"))
    comparison_html, comparison_readme = render_comparisons(comparisons)
    page = replace_region(page, "COMPARISON", comparison_html)
    toolchain = json.loads((PROJECT / "web/data/toolchain-overview.json").read_text(encoding="utf-8"))
    toolchain_html, toolchain_readme = render_toolchain(toolchain)
    page = replace_region(page, "TOOLCHAIN", toolchain_html)
    metadata = json.loads((PROJECT / "project.json").read_text(encoding="utf-8"))
    brief_html, brief_readme = render_understanding(metadata)
    page = replace_region(page, "UNDERSTANDING", brief_html)
    extensions = json.loads((PROJECT / "web/data/research-extensions.json").read_text(encoding="utf-8"))
    extensions_html, extensions_readme = render_extensions(extensions)
    page = replace_region(page, "EXTENSION_SCENARIOS", extensions_html)
    brief_data = {key: metadata[key] for key in ["name", "summary", "source_url", "source_ref", "summary_sections"]}
    (PROJECT / "web/data/understanding.json").write_text(json.dumps(brief_data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8", newline="\n")
    page = "\n".join(line.rstrip() for line in page.splitlines())+"\n"
    index_path.write_text(page, encoding="utf-8", newline="\n")
    readme_path = PROJECT / "README.md"
    table = "| 能力 | 输入 | 输出 | 条件 | 边界 | 固定来源 |\n| --- | --- | --- | --- | --- | --- |\n" + "\n".join(rows)
    readme = replace_region(readme_path.read_text(encoding="utf-8"), "CAPABILITY_TABLE", table)
    readme = replace_region(readme, "COMPARISON", comparison_readme)
    readme = replace_region(readme, "TOOLCHAIN", toolchain_readme)
    readme = replace_region(readme, "UNDERSTANDING", brief_readme)
    readme = replace_region(readme, "EXTENSION_SCENARIOS", extensions_readme)
    readme_path.write_text(readme, encoding="utf-8", newline="\n")
    sources = (PROJECT / "references/source-map.md").read_text(encoding="utf-8")
    verification = (PROJECT / "experiments/results/verification.md").read_text(encoding="utf-8")
    (PROJECT / "web/guide.txt").write_text(readme + "\n\n---\n\n" + sources + "\n\n---\n\n" + verification, encoding="utf-8", newline="\n")
    print(f"Generated {len(metadata['summary_sections'])} summary sections, {len(extensions['scenarios'])} extension scenarios, {len(cards)} capabilities, {len(scenarios)} teaching scenarios, {len(comparisons['projects'])} comparisons and study download.")


if __name__ == "__main__":
    main()
