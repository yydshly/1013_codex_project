"""Render the shared capability guide and its original SVG relationship diagram."""

import html
import json
from pathlib import Path
import re
import unicodedata

DATA_PATH = Path("docs/research-workflow.json")
DIAGRAM_PATH = Path("docs/assets/research-workflow.svg")
DIAGRAM_ALT = "15 个项目的整体关系：获取资料、分析验证、知识检索与内容输出为主线，任务、模型和网络为可选支撑，shadPS4 与 Leak Check 为专项或参考支线"


def _text(value, label):
    if not isinstance(value, str) or not value.strip() or "\n" in value or "\r" in value:
        raise ValueError(f"Research workflow {label} must be a nonempty single-line string")
    return value


def load_workflow(root: Path, projects: list[dict], *, allow_partial=False):
    path = root / DATA_PATH
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Research workflow must be an object")
    for field in ("title", "intro", "note", "start", "handoff"):
        _text(data.get(field), field)
    for field in ("groups", "combinations"):
        if not isinstance(data.get(field), list) or not data[field]:
            raise ValueError(f"Research workflow {field} must be a nonempty list")
    grouped_ids = set()
    keys = set()
    for group in data["groups"]:
        if not isinstance(group, dict):
            raise ValueError("Research workflow groups must be objects")
        for field in ("key", "name", "purpose"):
            _text(group.get(field), field)
        if not re.fullmatch(r"[a-z][a-z0-9-]*", group["key"]) or group["key"] in keys:
            raise ValueError("Research workflow group keys must be unique slugs")
        keys.add(group["key"])
        if not isinstance(group.get("members"), list) or not group["members"]:
            raise ValueError("Research workflow group members must be a nonempty list")
        for member in group["members"]:
            if not isinstance(member, dict):
                raise ValueError("Research workflow members must be objects")
            for field in ("id", "role", "diagram_name", "diagram_role"):
                _text(member.get(field), field)
            if not re.fullmatch(r"[0-9]{3}", member["id"]) or member["id"] in grouped_ids:
                raise ValueError("Research workflow project IDs must be unique three-digit IDs")
            grouped_ids.add(member["id"])
    for case in data["combinations"]:
        if not isinstance(case, dict):
            raise ValueError("Research workflow combinations must be objects")
        for field in ("key", "title", "handoff", "needs"):
            _text(case.get(field), field)
        if not isinstance(case.get("roles"), list) or not case["roles"]:
            raise ValueError("Research workflow combination roles must be a nonempty list")
        for role in case["roles"]:
            if not isinstance(role, dict) or role.get("id") not in grouped_ids:
                raise ValueError("Research workflow combination references an unknown project")
            _text(role.get("role"), "combination role")
    project_ids = {project["id"] for project in projects}
    if unknown := grouped_ids - project_ids:
        if allow_partial:
            return None
        raise ValueError("Research workflow references missing projects: " + ", ".join(sorted(unknown)))
    extra = project_ids - grouped_ids
    if extra:
        data["groups"].append({
            "key": "pending", "name": "待整理分工", "purpose": "新收录项目，待补充能力与交接方案。",
            "members": [{"id": item, "role": "能力分工待整理。", "diagram_name": item,
                         "diagram_role": "待整理"} for item in sorted(extra)],
        })
    return data


def _short_name(project):
    return project["name"].partition("：")[0]


def render_markdown(data, projects, escape):
    if not data:
        return ""
    catalog = {project["id"]: project for project in projects}
    def link(project_id):
        project = catalog[project_id]
        return f"[{project_id} {escape(_short_name(project))}](./projects/{project['directory']}/README.md)"
    lines = ["### " + escape(data["title"]), "", escape(data["intro"]), "", escape(data["note"]), "",
             f"![{DIAGRAM_ALT}](./{DIAGRAM_PATH.as_posix()})", "",
             "图示与来源：本仓库依据各项目固定研究记录原创绘制；实线表示主线交接方案，虚线表示可选支撑。", "",
             f"[打开可缩放关系图](./{DIAGRAM_PATH.as_posix()})", "",
             "#### 按能力分组", "", "| 能力组 | 项目与职责 |", "| --- | --- |"]
    for group in data["groups"]:
        members = "<br>".join(link(member["id"]) + "：" + escape(member["role"]) for member in group["members"])
        lines.append(f"| **{escape(group['name'])}**<br>{escape(group['purpose'])} | {members} |")
    lines.extend(["", "#### 可以怎样组合", ""])
    for case in data["combinations"]:
        lines.extend(["**" + escape(case["title"]) + "**", ""])
        for role in case["roles"]:
            lines.append(f"- {link(role['id'])}：{escape(role['role'])}")
        lines.extend(["", "交接：" + escape(case["handoff"]), "", "需要补齐：" + escape(case["needs"]), ""])
    lines.extend(["#### 从一个最小流程开始", "", escape(data["start"]), "", escape(data["handoff"]), ""])
    return "\n".join(lines)


def render_html(data, projects, demo_directories, repository):
    if not data:
        return ""
    esc = html.escape
    catalog = {project["id"]: project for project in projects}
    def link(project_id):
        project = catalog[project_id]
        directory = project["directory"]
        url = f"./{directory}/" if directory in demo_directories else f"https://github.com/{repository}/blob/main/projects/{directory}/README.md"
        return f'<a href="{url}">{project_id} {esc(_short_name(project))}</a>'
    groups = []
    for group in data["groups"]:
        members = "".join(f'<li data-project-id="{member["id"]}">{link(member["id"])}<span>{esc(member["role"])}</span></li>' for member in group["members"])
        groups.append(f'<article class="workflow-group" data-workflow-group="{group["key"]}"><h3>{esc(group["name"])}</h3><p>{esc(group["purpose"])}</p><ul>{members}</ul></article>')
    cases = []
    for index, case in enumerate(data["combinations"]):
        roles = "".join(f'<li>{link(role["id"])}：{esc(role["role"])}</li>' for role in case["roles"])
        opened = " open" if index == 0 else ""
        cases.append(f'<details class="workflow-case"{opened}><summary>{esc(case["title"])}</summary><ul>{roles}</ul><p><strong>交接：</strong>{esc(case["handoff"])}</p><p><strong>需要补齐：</strong>{esc(case["needs"])}</p></details>')
    return f'''<section class="research-workflow" id="research-workflow" aria-labelledby="workflow-heading">
<h2 id="workflow-heading">{esc(data['title'])}</h2><p>{esc(data['intro'])}</p><p class="workflow-note">{esc(data['note'])}</p>
<figure class="workflow-figure"><div class="workflow-diagram-scroll" tabindex="0" aria-label="整体关系图，可横向滚动"><img src="./assets/research-workflow.svg" width="1600" height="1090" alt="{DIAGRAM_ALT}" loading="lazy"></div>
<figcaption>本仓库依据固定研究记录原创绘制；实线为主线交接方案，虚线为可选支撑。小屏可横向滚动，完整文字分工见下方。<a href="./assets/research-workflow.svg">打开／下载可缩放原图 ↗</a></figcaption></figure>
<h3>按能力分组</h3><div class="workflow-groups">{''.join(groups)}</div>
<h3>可以怎样组合</h3><p>展开一个场景，查看各自负责什么、交接什么、还需要补什么。</p><div class="workflow-cases">{''.join(cases)}</div>
<div class="workflow-start"><h3>从一个最小流程开始</h3><p>{esc(data['start'])}</p><p>{esc(data['handoff'])}</p></div></section>'''


def _wrap(text, width, size):
    lines, current, used = [], "", 0
    for char in text:
        advance = size if unicodedata.east_asian_width(char) in "WF" else size * 0.57
        if current and used + advance > width:
            lines.append(current)
            current, used = "", 0
        current += char
        used += advance
    if current:
        lines.append(current)
    return lines


def render_svg(data):
    members = {member["id"]: member for group in data["groups"] for member in group["members"]}
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1090" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(data['title'])}</title><desc id="desc">{html.escape(DIAGRAM_ALT + '。' + data['note'])}</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10Z" fill="#466452"/></marker><marker id="optional-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10Z" fill="#6c7888"/></marker></defs>
<style>text{{font-family:"Microsoft YaHei","Noto Sans CJK SC",system-ui,sans-serif;fill:#223329}}.title{{font-weight:700}}.role{{fill:#46584b}}.main-arrow{{fill:none;stroke:#466452;stroke-width:3;marker-end:url(#arrow)}}.optional{{fill:none;stroke:#6c7888;stroke-width:2;stroke-dasharray:7 6;marker-end:url(#optional-arrow)}}</style>
<rect width="1600" height="1090" fill="#f6f7f2"/>''']
    def text(x, y, value, size=19, bold=False, width=None, color=None, project_id=None):
        wrapped = _wrap(value, width, size) if width else [value]
        attr = ' class="title"' if bold else ' class="role"'
        if color:
            attr += f' style="fill:{color}"'
        if project_id:
            attr += f' data-project-id="{project_id}"'
        for index, line in enumerate(wrapped):
            parts.append(f'<text x="{x}" y="{y + index * (size + 8)}" font-size="{size}"{attr}>{html.escape(line)}</text>')
        return len(wrapped)
    def panel(x, y, width, height, title, fill):
        parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="16" fill="{fill}" stroke="#cdd8cf"/>')
        text(x + 22, y + 39, title, 22, True)
    def member(project_id, x, y, width):
        value = members[project_id]
        text(x, y, project_id + " · " + value["diagram_name"], 20, True, width, project_id=project_id)
        text(x, y + 30, value["diagram_role"], 17, width=width)
    text(80, 60, "15 个项目，按职责接成研究工作流", 32, True)
    text(80, 105, "材料 → 可核查证据 → 知识沉淀 → 可验收成果", 23)
    panel(80, 145, 680, 205, "任务编排与会话操作 · 按需选用", "#e9eff9")
    for project_id, y in (("013", 221), ("009", 278), ("010", 335)):
        value = members[project_id]
        text(102, y, project_id + " · " + value["diagram_name"], 20, True, project_id=project_id)
        text(365, y, value["diagram_role"], 17, width=370)
    panel(840, 145, 680, 205, "任务判断与模型接入 · 按需选用", "#fff1d9")
    member("007", 865, 225, 625)
    member("016", 865, 300, 625)
    parts.append('<path class="optional" d="M520 350 V375"/><path class="optional" d="M1050 350 V375"/>')
    parts.append('<rect x="440" y="375" width="720" height="40" rx="12" fill="#fff" stroke="#cdd8cf"/>')
    text(460, 402, "模型理解与生成；Agent／程序调用工具；人验收", 19)
    text(80, 401, "研究主线 · 交接方案", 19, True)
    panel(80, 430, 330, 355, "① 获取与固定资料", "#e9f2e5")
    member("012", 103, 527, 284)
    text(103, 635, "原仓库 / 论文 / 笔记", 19, True)
    text(103, 674, "保留来源、版本与原文位置", 17, width=284)
    text(103, 729, "002 也有论文采集入口", 17, width=284)
    panel(450, 430, 330, 355, "② 分析与验证", "#e8f0f7")
    member("015", 474, 527, 282)
    member("006", 474, 639, 282)
    text(474, 756, "人＋实验核对依据与未知", 17, width=282)
    panel(820, 430, 330, 355, "③ 沉淀与检索", "#e9f2e5")
    member("002", 845, 527, 280)
    text(845, 643, "文档、证据与引用登记", 19, True)
    text(845, 685, "先核对，再入库；", 17)
    text(845, 718, "来源链接仍需检查结论支持", 17, width=280)
    panel(1190, 430, 330, 355, "④ 表达与交付", "#f9ece7")
    for project_id, y in (("001", 522), ("011", 624), ("014", 726)):
        member(project_id, 1214, y, 280)
    for x, label in ((410, "文件"), (780, "证据"), (1150, "引用")):
        parts.append(f'<path class="main-arrow" d="M{x} 604 H{x + 38}"/>')
        text(x + 2, 581, label, 16)
    parts.append('<path class="main-arrow" d="M1355 785 V803"/><rect x="1210" y="807" width="310" height="32" rx="9" fill="#e2eddf"/>')
    text(1235, 830, "人核对成品、修订并归档", 17, True)
    panel(80, 872, 440, 148, "网络连接 · 按需", "#e9eef1")
    member("005", 103, 948, 390)
    panel(560, 872, 440, 148, "专项程序实测", "#e8f0f7")
    member("008", 584, 948, 390)
    panel(1040, 872, 480, 148, "查询机制参考", "#eeeeea")
    member("004", 1064, 948, 430)
    parts.append('<path class="optional" d="M80 955 H40 V250 H78"/><path class="optional" d="M780 870 V828 H615 V787"/>')
    text(610, 857, "实测记录补入证据", 16)
    text(80, 1062, "实线＝主线交接方案　虚线＝可选支撑；职责互补不表示现成连接，接口、格式与验收需适配。", 19)
    parts.append("</svg>\n")
    return "\n".join(parts)


def update_diagram(root, data, *, check=False):
    if not data:
        return True
    target = root / DIAGRAM_PATH
    expected = render_svg(data)
    if target.is_file() and target.read_text(encoding="utf-8") == expected:
        return True
    if check:
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(expected, encoding="utf-8", newline="\n")
    return True
