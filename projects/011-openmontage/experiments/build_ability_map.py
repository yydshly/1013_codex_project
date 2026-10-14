"""Draw an original, exportable capability poster from the research catalog.

Standard-library SVG authoring. Does not invoke OpenMontage or a model.
"""
import html
import json
import unicodedata
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
DATA = json.loads((PROJECT / "web/research.json").read_text(encoding="utf-8"))
W, PAD, GAP = 2200, 80, 24
INNER = W - PAD * 2
INK, MUTED, PAPER = "#172426", "#556566", "#f6f5ef"
ACCENT, LINE, MINT, GOLD = "#b84c26", "#d4ddd6", "#e0ece5", "#f6e5bd"
parts = []


def rect(x, y, w, h, fill="#fffefa", radius=16, stroke=LINE):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>')


def text(x, y, value, size=26, color=INK, weight=400, width=None, anchor=None):
    extra = (f' data-max-width="{width}"' if width else "")
    extra += (f' text-anchor="{anchor}"' if anchor else "")
    parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}"{extra}>{html.escape(str(value))}</text>')


def measured(value, size):
    return sum(size * (1 if unicodedata.east_asian_width(c) in "WF" else .61) for c in value)


def wrap(value, width, size):
    result, line = [], ""
    for char in value:
        if char == "\n":
            result.append(line)
            line = ""
        elif measured(line + char, size) > width and line:
            if char in "、。，；：！？）》】" and len(line) > 1:
                result.append(line[:-1])
                line = line[-1] + char
            else:
                result.append(line)
                line = char
        else:
            line += char
    if line:
        result.append(line)
    return result


def paragraph(x, y, value, width, size=25, color=MUTED, leading=None, weight=400):
    leading = leading or size * 1.45
    for line in wrap(value, width - 20, size):
        text(x, y, line, size, color, weight, width)
        y += leading
    return y


def section(y, number, title, note):
    text(PAD, y, number, 28, ACCENT, 700)
    text(PAD + 60, y, title, 38, INK, 700)
    text(PAD + 60, y + 43, note, 23, MUTED, width=INNER - 60)
    return y + 68


def arrow(x, y, length=20):
    parts.append(f'<path d="M{x} {y}h{length}m-7 -6 7 6-7 6" fill="none" stroke="{ACCENT}" stroke-width="2.5"/>')


# Main positioning is a single reading order: input, organization, capabilities,
# implementation, effects, output, extension, value and limitations.
rect(0, 0, W, 230, INK, 0, INK)
text(PAD, 50, "OPENMONTAGE / 011 / 能力理解总览", 25, "#f1c88e", 600)
text(PAD, 123, "从主题、资料与素材，到可检查的视频制作。", 54, "#fffefa", 700)
text(PAD, 179, "AI 助手做决策 · OpenMontage 组织流程与交接 · 模型、检索和代码工具执行", 30, "#e4ece6", width=INNER)
text(PAD, 211, "34 项能力归纳 / 12 条制作流程 / 固定版本源码研究 / 2026-10-14", 21, "#bdd0c4")

y = section(296, "01", "输入：可以给它什么？", "可以从一个主题开始；明确受众、时长、素材与交付要求，有助于确定制作路线。 [1]")
col4 = (INNER - GAP * 3) / 4
inputs = [
    ("主题与资料", "一句主题、文档、项目研究、脚本\n先研究，再提出制作方案"),
    ("已有素材", "图片、长视频、录屏、口播、播客\n提取、加工和重新组织内容"),
    ("参考与风格", "参考视频、镜头、角色或品牌方向\n分析节奏与表达，形成镜头要求"),
    ("目标与执行条件", "受众、时长、比例、语言、预算\n助手、依赖、素材与 API 可用性"),
]
for i, (title, body) in enumerate(inputs):
    x = PAD + i * (col4 + GAP)
    rect(x, y, col4, 168)
    text(x + 25, y + 44, title, 30, INK, 700)
    paragraph(x + 25, y + 88, body, col4 - 50, 23, leading=32)
y += 236

y = section(y, "02", "组织：如何把各项工作连接起来？", "外部 AI 编程助手实际调度；YAML、技能与成果文件给它工作方法、阶段边界和继续制作的依据。 [1][2][3]")
col3 = (INNER - GAP * 2) / 3
control = [
    ("助手 / 理解与决策", "理解需求、研究、写脚本、设计镜头\n选工具、编写代码、观看并判断结果"),
    ("流程 + 技能 / 规定与指导", "YAML：阶段、工具、输入输出、确认\nMarkdown：研究、选材、剪辑的工作方法"),
    ("成果 + 检查点 / 交接与状态", "JSON：脚本、分镜、素材和剪辑决策\nschema、前置条件、确认字段与历史记录"),
]
for i, (title, body) in enumerate(control):
    x = PAD + i * (col3 + GAP)
    rect(x, y, col3, 163, MINT if i == 1 else "#fffefa")
    text(x + 25, y + 44, title, 30, INK, 700)
    paragraph(x + 25, y + 86, body, col3 - 50, 24, leading=33)
y += 187
stages = [
    ("研究", "research_brief", False), ("方案", "proposal_packet", True),
    ("脚本", "script", True), ("分镜", "scene_plan", True),
    ("素材", "asset_manifest", True), ("剪辑", "edit_decisions", False),
    ("合成", "render_report", False), ("导出", "publish_log", True),
]
step_gap = 27
step_w = (INNER - step_gap * 7) / 8
for i, (title, artifact, gate) in enumerate(stages):
    x = PAD + i * (step_w + step_gap)
    rect(x, y, step_w, 135, GOLD if gate else "#fffefa", 12)
    text(x + 16, y + 39, title, 29, INK, 700)
    text(x + 16, y + 75, artifact, 19, MUTED, width=step_w - 32)
    text(x + 16, y + 112, "默认需确认" if gate else "默认无确认门", 20, ACCENT if gate else MUTED)
    if i < 7:
        arrow(x + step_w + 3, y + 65, 21)
y += 170
text(PAD, y, "讲解流程示例：参考制作可先做 10–15 秒样片；合成还产出 final_review；导出不会自动上传社交平台。", 23, MUTED, width=INNER)
y += 70

y = section(y, "03", "能力：六类工作，共 34 项", "编号是本研究的能力归纳；右侧标明实现线索。能力可以单独使用，也可以沿阶段组合。 [1–5]")
categories = [
    ("prepare", "研究与检索", "主题、资料、参考 → 简报、脚本、镜头计划、候选素材", ["助手判断", "助手+技能", "代码+转录", "代码+索引", "CLIP+筛选"]),
    ("generate", "素材生成", "脚本、提示、参考 → 图片、运动镜头、声音与角色素材", ["生成模型", "生成模型", "TTS 模型", "模型/素材", "模型接入", "代码+资产", "工具入口"]),
    ("process", "已有视频处理", "既有视频/音频 → 加工后的片段、音轨、字幕和文件", ["FFmpeg", "代码+混音", "转录+叠加", "过滤/增强", "采样+探测", "转码/配置", "助手写代码"]),
    ("compose", "画面与合成", "内容、数据、素材与时间线 → 图形、动画和最终视频", ["代码逐帧", "HTML 渲染", "专用工具", "助手+渲染", "确定性执行"]),
    ("govern", "制作管理", "阶段成果、约束和运行记录 → 检查、状态、费用和看板", ["注册/检查", "规则+评分", "schema+状态", "字段+人工", "费用规则", "规则检查", "抽检+复核", "文件+SSE"]),
    ("deliver", "交付与复用", "成片与中间成果 → 导出包、元信息及后续制作基础", ["打包工具", "文件/模板"]),
]
counter = 0
card_h = 410
for ci, (key, title, io, methods) in enumerate(categories):
    x = PAD + (ci % 3) * (col3 + GAP)
    cy = y + (ci // 3) * (card_h + GAP)
    entries = [item for item in DATA["capabilities"] if item["category"] == key]
    assert len(entries) == len(methods)
    rect(x, cy, col3, card_h)
    text(x + 25, cy + 45, title, 31, INK, 700)
    text(x + col3 - 25, cy + 43, f"{len(entries)} 项", 24, ACCENT, 600, anchor="end")
    text(x + col3 - 25, cy + 78, "实现线索", 19, MUTED, anchor="end")
    for j, (item, method) in enumerate(zip(entries, methods)):
        counter += 1
        ry = cy + 108 + j * 30
        text(x + 25, ry, f"{counter:02d}", 18, ACCENT)
        text(x + 62, ry, item["name"], 23, INK, width=col3 - 218)
        text(x + col3 - 25, ry, method, 20, MUTED, anchor="end", width=134)
    if key == "deliver":
        paragraph(x + 25, cy + 206, "成片 / 元信息 / 封面概念 / 章节\n脚本 / 分镜 / 素材清单 / 剪辑决策\n可观察、可修改、可复用的制作记录", col3 - 50, 23, leading=34)
    paragraph(x + 25, cy + 367, io, col3 - 50, 21, leading=29)
assert counter == 34
y += card_h * 2 + GAP + 75

y = section(y, "04", "底层：模型、算法、规则和代码，各负责什么？", "生成有两种：素材模型生成画面/声音；助手写画面代码，再由渲染器逐帧执行。 [2–5]")
implementation = [
    ("A · 助手模型：理解与编排", "理解需求、研究与创作；选择素材和工具，编写处理/动画代码。实际调度依赖当前助手。"),
    ("B · 素材模型：图片、视频、声音", "专用图片、视频和 TTS 模型生成素材；可接云端服务或本地路径。模型能力、费用和效果各异。"),
    ("C · 检索算法：寻找真实镜头", "CLIP 图文 512 维向量，多帧均值；融合画面/标签相似度，再筛选与增加多样性。相似不证明事实。"),
    ("D · 程序化画面：代码渲染", "Remotion / HyperFrames 执行布局、图表、文字、动画与时间线。助手写代码，渲染器确定性生成视频帧。"),
    ("E · 媒体处理：工具加工", "FFmpeg / ffprobe 等执行剪切、拼接、变速、抽帧、字幕、混音、调色和转码；听感与画面仍需验收。"),
    ("F · 规则与人工：检查和放行", "YAML、已知成果 schema、检查点、预算和抽检提供约束。确认字段由调用者记录；创作质量需实际复核。"),
]
impl_h = 202
for i, (title, body) in enumerate(implementation):
    x, cy = PAD + (i % 3) * (col3 + GAP), y + (i // 3) * (impl_h + GAP)
    rect(x, cy, col3, impl_h, MINT if i in (0, 3) else "#fffefa")
    text(x + 25, cy + 43, title, 27, INK, 700, width=col3 - 50)
    paragraph(x + 25, cy + 86, body, col3 - 50, 23, leading=32)
y += impl_h * 2 + GAP + 76

y = section(y, "05", "效果：十二条制作流程，可以做什么？", "这是固定版本的制作路径；流程名称不承诺实际成片质量。另有 framework-smoke 测试流程。 [1]")
effect_h = 190
for i, pipeline in enumerate(DATA["pipelines"]):
    x = PAD + (i % 4) * (col4 + GAP)
    cy = y + (i // 4) * (effect_h + GAP)
    rect(x, cy, col4, effect_h)
    title = pipeline["name"]
    if pipeline["id"] in {"character-animation", "documentary-montage"}:
        title += " · beta"
    text(x + 23, cy + 41, title, 28, INK, 700, width=col4 - 46)
    iy = paragraph(x + 23, cy + 81, "输入：" + pipeline["input"], col4 - 46, 22, leading=29)
    paragraph(x + 23, iy + 9, "效果：" + pipeline["output"], col4 - 46, 23, INK, leading=31)
y += effect_h * 3 + GAP * 2 + 72

y = section(y, "06", "输出：成片之外，还留下什么？", "最终媒体与中间成果共同构成可复用的制作记录；结构合法不代表事实与表达已经正确。 [1][3][5]")
rect(PAD, y, INNER, 144, MINT)
text(PAD + 30, y + 47, "最终交付", 28, INK, 700)
text(PAD + 212, y + 47, "视频 + 旁白/音轨 + 字幕相关材料 + 元信息 + 封面/章节等导出材料", 27, INK, width=INNER - 255)
text(PAD + 30, y + 97, "过程成果", 28, INK, 700)
text(PAD + 212, y + 97, "研究 → 方案 → 脚本 → 分镜 → 素材清单 → 剪辑决策 → 渲染/检查 → 状态与费用", 25, MUTED, width=INNER - 255)
y += 215

y = section(y, "07", "扩展：可以把它用到哪些工作中？", "以下是适配方向；与本仓库其他系统的连接尚未实现。新增工具、业务模板与真实上传都需要接入和验证。 [6]")
extensions = [
    ("项目研究 → 短讲解", "README、截图、原理图与录屏 → 项目解说、对比片和功能演示。可探索与 001 写作、002 RAG 衔接。"),
    ("课程 / 科普 / 数据解释", "概念、公式、数据 → 可控动态图形、系统原理动画和讲解。适合 RAG、网络、终端及 Agent 流程。"),
    ("产品 / 品牌 / 栏目模板", "产品与品牌素材 → 功能介绍、氛围片、虚拟讲解员；通过模板统一视觉、声音与输出规格。"),
    ("既有内容 → 多版本复用", "录屏、播客、访谈与口播 → 短片、字幕、语言版本与不同平台比例；跨平台画面要重新检查。"),
    ("自有素材 / 新模型工具", "接入原创图库、录屏索引、中文发音与字幕规则、新提供商；适配参数、输出、错误、费用和依赖。"),
    ("更可靠的制作系统", "加入实测质量/费用评分、材料失效传播、重试、外部任务恢复和平台发布；逐项定义真实验收条件。"),
]
ext_h = 202
for i, (title, body) in enumerate(extensions):
    x, cy = PAD + (i % 3) * (col3 + GAP), y + (i // 3) * (ext_h + GAP)
    rect(x, cy, col3, ext_h, "#f0efe8", 16, LINE)
    text(x + 25, cy + 43, title, 28, INK, 700, width=col3 - 50)
    paragraph(x + 25, cy + 84, body, col3 - 50, 23, leading=31)
y += ext_h * 2 + GAP + 55

rect(PAD, y, INNER, 116, INK, 16, INK)
text(PAD + 30, y + 46, "最有价值：阶段职责 + 结构化成果交接", 37, "#f1c88e", 700)
text(PAD + 30, y + 89, "把开放的创作工作变成可检查、可修改、可复用的过程；再按能力替换模型、素材和代码工具。", 27, "#e6eee8", width=INNER - 60)
y += 155
text(PAD, y, "使用边界", 27, ACCENT, 700)
paragraph(PAD + 154, y, "本研究核对源码与文档，未安装上游或制作真实视频。人物连续性、中文配音、翻译、真实费用和效率待实测；3D 仅确认入口。", INNER - 154, 23, leading=32)
y += 78
paragraph(PAD, y, "预算默认 warn，cap 才阻断超预算预留；评分含经验默认值；抽帧和格式检查覆盖有限。依赖、硬件、API 与素材许可影响实际可用性。", INNER, 22, leading=31)
y += 80
parts.append(f'<path d="M{PAD} {y}H{W-PAD}" stroke="{LINE}"/>')
y += 39
text(PAD, y, "依据与阅读方式", 25, INK, 700)
y += 36
refs = [
    ("[1] README、架构与制作流程", "pipeline_defs/animated-explainer.yaml"),
    ("[2] 注册、选择与七维评分", "lib/scoring.py"),
    ("[3] 检查点、预算与配置", "lib/checkpoint.py"),
    ("[4] CLIP 编码与素材检索", "lib/clip_embedder.py"),
    ("[5] 合成、Remotion 与 FFmpeg", "tools/video/video_compose.py"),
]
rx = PAD
for label, source in refs:
    url = "https://github.com/calesthio/OpenMontage/blob/" + DATA["source_ref"] + "/" + source
    parts.append('<a href="' + html.escape(url, quote=True) + '">')
    text(rx, y, label, 20, ACCENT)
    parts.append("</a>")
    rx += measured(label, 20) + 38
y += 34
text(PAD, y, "[6] 核心价值与扩展为研究判断；完整 34 项输入输出和 27 项来源见配套网页。此图为本仓库原创，非上游运行截图。", 21, MUTED, width=INNER)
y += 34
text(PAD, y, "calesthio/OpenMontage @ " + DATA["source_ref"] + " · AGPL-3.0 · 研究日期 2026-10-14", 21, MUTED, width=INNER)
height = int(y + 51)

description = ("OpenMontage 完整能力理解图。输入主题、资料、参考和既有媒体；外部助手经八阶段交接组织制作。"
               "六类34项能力，模型、检索、代码与规则分工，12条制作流程，最终和过程输出，六类扩展场景，核心价值与未验证边界。")
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-labelledby="title desc">\n'
       '<title id="title">OpenMontage：能力、效果、输入输出、底层实现与扩展总览</title>\n'
       '<desc id="desc">' + description + '</desc>\n'
       '<style>text{font-family:"Microsoft YaHei","Noto Sans CJK SC","Segoe UI",sans-serif}a:hover text{text-decoration:underline}</style>\n'
       f'<rect width="{W}" height="{height}" fill="{PAPER}"/>\n' + "\n".join(parts) + '\n</svg>\n')
for target in [PROJECT / "assets/ability-map.svg", PROJECT / "web/assets/ability-map.svg"]:
    target.write_text(svg, encoding="utf-8", newline="\n")
print(json.dumps({"capabilities":counter, "pipelines":len(DATA["pipelines"]), "width":W, "height":height, "outputs":["assets/ability-map.svg", "web/assets/ability-map.svg"]}))
