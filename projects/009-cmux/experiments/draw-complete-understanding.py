"""Render the original, text-exact cmux understanding poster as PNG and SVG.

This creates a new diagram from shapes and text; it does not edit an image.
Requires Pillow and Windows Microsoft YaHei fonts. No model calls.
"""
from pathlib import Path
from html import escape
from math import atan2, cos, sin, pi
import shutil
import re

from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 2400, 3700
BG, INK, MUTED = "#f5f7fa", "#182b43", "#53667e"
BLUE, GREEN, ORANGE, LINE = "#285cb0", "#14785d", "#ad5b27", "#cdd8e6"
PALE_BLUE, PALE_GREEN = "#edf3ff", "#ecf6f1"
image = Image.new("RGB", (WIDTH, HEIGHT), BG)
draw = ImageDraw.Draw(image)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">',
       '<title id="title">cmux 完整理解总图</title>',
       '<desc id="desc">承接现有 Agent 工具，统一展示和交互，定向控制多个会话。说明上下层分工、原生宿主、PTY、Hooks、Socket、消息、能力、效果、接入方式、场景、个人价值、扩展与边界。根据固定版本研究原创绘制，非上游运行截图。</desc>',
       f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{BG}"/>']
fonts = {}
visible_text = []


def font(size, bold=False):
    key = (size, bold)
    if key not in fonts:
        fonts[key] = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc", size)
    return fonts[key]


def rectangle(x, y, w, h, fill="#ffffff", stroke=LINE, radius=18, thickness=2):
    draw.rounded_rectangle((x, y, x+w, y+h), radius=radius, fill=fill, outline=stroke, width=thickness)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{thickness}"/>')


def text(x, y, value, size=32, color=INK, bold=False):
    f = font(size, bold)
    assert x + draw.textlength(value, font=f) <= WIDTH - 45, f"text exceeds canvas: {value}"
    cursor = x
    for run in re.split("(↔)", value):
        if not run:
            continue
        run_font = ImageFont.truetype("C:/Windows/Fonts/seguisym.ttf", size) if run == "↔" else f
        draw.text((cursor, y), run, font=run_font, fill=color, anchor="lt")
        cursor += draw.textlength(run, font=run_font)
    svg.append(f'<text x="{x}" y="{y + size*.91:.1f}" font-family="Microsoft YaHei, PingFang SC, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{escape(value)}</text>')
    visible_text.append(value)


def wrapped(x, y, value, max_width, size=32, color=MUTED, bold=False, line_height=None):
    f = font(size, bold)
    line_height = line_height or round(size*1.55)
    line = ""
    lines = []
    for char in value:
        if char == "\n" or (line and draw.textlength(line + char, font=f) > max_width):
            lines.append(line)
            line = "" if char == "\n" else char
        else:
            line += char
    if line:
        lines.append(line)
    for line in lines:
        text(x, y, line, size, color, bold)
        y += line_height
    return y


def bullets(x, y, items, max_width, size=31, gap=15, color=MUTED):
    for item in items:
        draw.ellipse((x, y+11, x+9, y+20), fill=BLUE)
        svg.append(f'<circle cx="{x+4.5}" cy="{y+15.5}" r="4.5" fill="{BLUE}"/>')
        y = wrapped(x+25, y, item, max_width-25, size, color) + gap
    return y


def arrow(x1, y1, x2, y2, color=BLUE, bidirectional=False):
    draw.line((x1,y1,x2,y2), fill=color, width=4)
    svg.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="4"/>')
    angle = atan2(y2-y1, x2-x1)
    ends = [(x2, y2, angle)] + ([(x1,y1,angle+pi)] if bidirectional else [])
    for x, y, a in ends:
        points = [(x,y), (x-16*cos(a-.48),y-16*sin(a-.48)),(x-16*cos(a+.48),y-16*sin(a+.48))]
        draw.polygon(points, fill=color)
        svg.append('<polygon points="'+" ".join(f"{px:.1f},{py:.1f}" for px,py in points)+f'" fill="{color}"/>')


def panel_title(x, y, number, title, color=BLUE):
    rectangle(x, y, 58, 58, color, color, 14)
    text(x+10, y+11, number, 31, "#ffffff", True)
    text(x+80, y+7, title, 42, INK, True)


# Header: a single clear thesis, with the three responsibilities stated.
rectangle(0, 0, WIDTH, 308, INK, INK, 0)
text(76, 36, "我们的完整理解 / CMUX RESEARCH", 28, "#b3c6df")
text(76, 88, "cmux · 一个人控制多个 Agent", 82, "#ffffff", True)
text(76, 195, "多个现有会话放进工作台：分屏、独立交互、定向控制、并行工作", 48, "#c9ddf9", True)
text(76, 267, "能力 · 原理 · 架构 · 操作效果 · 接入方式 · 使用场景 · 对我的意义", 27, "#a7bfdf")

# Central diagram: control above; app-owned surfaces; separate executor processes.
rectangle(64, 342, 2272, 988)
panel_title(94, 373, "01", "承接与操作：统一工作环境，执行逻辑仍由 Agent 负责")
rectangle(96, 458, 2208, 116, PALE_BLUE, "#b8cdef", 15)
text(124, 479, "人 / 协调 Agent / 工作流", 36, BLUE, True)
text(124, 529, "决定目标、拆分任务、选择执行者、安排依赖与权限，检查成果是否通过", 32)
arrow(1200, 579, 1200, 618)
text(1240, 584, "提示、问题回应、CLI / Socket 操作", 27, BLUE)

rectangle(96, 635, 2208, 391, "#172a42", "#172a42", 15)
text(124, 656, "cmux 原生 UI / Swift + AppKit + SwiftUI", 34, "#f2f6ff", True)
text(124, 710, "Window → Workspace → Pane → Surface  |  稳定会话身份定位目标", 27, "#b2c6e1")
text(1950, 669, "教学示意，非截图", 25, "#a8bdd8")

panes = [(124, "A / Claude Code", "源码研究", "运行中", "#72c6aa"),
         (848, "B / Codex", "网页实现", "需要输入", "#edb476"),
         (1572, "C / OpenCode", "检查结果", "空闲", "#a4b8d3")]
for x, name, task, state, state_color in panes:
    rectangle(x, 763, 700, 177, "#243b59", "#516f94", 12)
    text(x+20, 782, name, 32, "#dfebfb", True)
    text(x+20, 830, task, 30, "#b3c8e4")
    text(x+495, 831, state, 28, state_color, True)
    text(x+20, 881, "查看输出 ↔ 发送输入 / 回应问题", 27, "#b3c8e4")
rectangle(124, 963, 2148, 42, "#e4edf8", "#e4edf8", 8)
text(144, 971, "浏览器 / WebKit：导航、快照、点击、填表、JS、截图；与终端并列检查成果", 26, INK)

for x, name, _, _, _ in panes:
    arrow(x+350, 1030, x+350, 1081, BLUE, True)
    rectangle(x, 1095, 700, 115, PALE_BLUE, "#b8cdef", 12)
    text(x+23, 1112, "独立 Shell / Agent CLI 进程", 30, BLUE, True)
    text(x+23, 1162, "自己的模型 + 账号 + 上下文 + 工具", 27)
text(94, 1243, "终端核心 libghostty + PTY 承载双向输入输出；Agent 调用模型、操作文件与命令，产出实际成果。", 30, MUTED)
text(94, 1290, "效果：多个会话可同时运行；按目标操作、找回待输入项、查看进展，减少窗口切换与重复搬运。", 28, MUTED)

# Four channels, keeping terminal entry separate from structured messages.
panel_title(64, 1371, "02", "底层原理：四条通道，共用 Surface / 生命周期 / 原生 session ID")
paths = [
    (64, 1463, "输入 / 输出", "UI ↔ PTY ↔ Shell / Agent CLI", "ANSI 解析与渲染；OSC 可承载通知。模型调用在 Agent 侧。", BLUE, PALE_BLUE),
    (1224, 1463, "状态 / 提醒", "Hooks / OSC / CLI → 状态 / 通知存储", "侧栏、通知环、未读与会话状态；丰富程度依赖具体适配。", GREEN, PALE_GREEN),
    (64, 1655, "程序化控制", "人 / 脚本 / Agent → CLI / Unix Socket", "显式定位 Workspace / Surface，创建、选择、输入、读取和操作浏览器。", BLUE, PALE_BLUE),
    (1224, 1655, "协作消息", "发送者 → queued → 接收方 Hook → delivered", "消息加入上下文；投递轮结束或手动标记为 read，不修改人的草稿。", GREEN, PALE_GREEN),
]
for x, y, title, chain, explanation, color, fill in paths:
    rectangle(x, y, 1112, 166, fill, LINE, 15)
    text(x+23, y+16, title, 34, color, True)
    text(x+23, y+62, chain, 28, INK, True)
    bottom = wrapped(x+23, y+105, explanation, 1066, 26, MUTED, line_height=37)
    assert bottom <= y+174, title

# Capabilities and integration path.
rectangle(64, 1867, 1112, 630)
rectangle(1224, 1867, 1112, 630)
panel_title(88, 1894, "03", "能力清单")
capabilities = [
    "终端与分屏：真实 CLI，多窗口 / 工作区 / 页签",
    "状态与通知：运行、空闲、需输入，集中提醒",
    "控制接口：创建、选择、文本、按键与屏幕读取",
    "浏览器自动化：导航、快照、点击、填表、截图",
    "Agent 消息：定向发送、收件箱、回复与投递状态",
    "团队适配：Claude teams 的 tmux 操作映射为原生分屏",
    "事件与规则：订阅、留痕、通知 / rpc / run / webhook",
    "恢复与远程：布局、支持的会话恢复、SSH / tmux",
]
bottom = bullets(94, 1986, capabilities, 1054, 30, 12)
assert bottom <= 2470, "capabilities overflow"

panel_title(1248, 1894, "04", "接入方式：由基础到增强", GREEN)
integration = [
    "1 终端接入：在 cmux 中启动已安装的 Agent CLI。\nAgent 自己登录、配置模型、使用自己的工具。",
    "2 状态接入：支持的 Agent 配 Hooks。\n也可用 OSC 或 cmux CLI 发通知、上报状态。",
    "3 控制接入：CLI / Socket 显式选择目标。\n环境带有 Workspace / Surface 标识，定向操作。",
    "4 协作接入：启用消息适配或支持的团队集成。\n按目标发送 / 回复，交付时机取决于接收方适配。",
]
bottom = bullets(1254, 1986, integration, 1054, 28, 8)
text(1254, 2373, "CLI 能运行，不代表所有增强能力都已支持。", 28, ORANGE, True)
wrapped(1254, 2420, "Claude 可空闲唤醒；Codex 空闲消息等下一次提示；等待人回答时暂缓交付。", 1050, 26, MUTED, line_height=36)
assert bottom <= 2371, f"integration overflow: {bottom}"

# Situations and personalized judgment.
rectangle(64, 2537, 1112, 452)
rectangle(1224, 2537, 1112, 452)
panel_title(88, 2564, "05", "使用场景")
bottom = bullets(94, 2658, [
    "多库研究：分开组织研究、实验、页面与检查，少找窗口、少漏提醒。",
    "开发与验证：终端实现、浏览器检查和结果反馈在同一工作台衔接。",
    "远程长任务：在线远程宿主持有进程，本地观察、输入和重连。",
    "个人工作流：借鉴身份、事件、消息和控制，按真实痛点扩展。",
], 1054, 29, 12)
assert bottom <= 2966, "scenarios overflow"

panel_title(1248, 2564, "06", "对我的意义", GREEN)
bottom = bullets(1254, 2658, [
    "人的价值：一个人组织更多独立任务，少找会话、少漏提醒、少搬运。",
    "研究价值：模型无关承载、稳定身份、状态 / 控制 / 消息分层。",
    "我现在用 Windows：即时价值偏架构参考；原生桌面端需要 Mac。",
    "是否采用：比较并行负担、返工、通过率、端到端耗时与总费用。",
], 1054, 29, 12)
assert bottom <= 2966, "value overflow"

# Extension and boundaries; keep complete-workflow strategy above the primitive.
rectangle(64, 3029, 2272, 223, PALE_BLUE)
panel_title(88, 3053, "07", "可扩展：在已有基础上补齐任务闭环")
text(94, 3141, "任务契约与依赖 · 模型路由 · 通用适配 · 材料与产物 · worktree / 合并 · 交付检查 · 费用与 Windows 宿主", 29)
text(94, 3195, "已有事件、规则与消息可作基础；通用 fan-out 聚合在研究版本中仍是提案。原型容易，可靠交付与恢复仍需工程。", 28, MUTED)

rectangle(64, 3292, 2272, 258, "#f9f0e6", "#e0c7ab")
panel_title(88, 3315, "08", "关键边界：可控的环境，需要明确策略与独立验收", ORANGE)
for x, y, value in [
    (94, 3402, "能操作多个 Agent，不等于自动决定谁做什么。"),
    (1254, 3402, "read / idle 不等于任务完成，更不等于成果合格。"),
    (94, 3450, "Workspace 不等于文件隔离，修改代码另需合并策略。"),
    (1254, 3450, "恢复布局不保留任意进程内存；保活需另有宿主。"),
    (94, 3498, "屏幕输出与状态上报，不等于完整模型内部推理。"),
    (1254, 3498, "更多 Agent 不保证更快、更便宜；收益须实际测量。"),
]:
    text(x, y, value, 27, "#79522e")

text(76, 3580, "来源：github.com/manaflow-ai/cmux  |  基准 cdbe99596fe1  |  2026-10-14", 27, BLUE)
text(76, 3624, "本仓库按研究内容原创绘制，非上游运行截图；未运行 macOS 客户端、真实 Agent / 模型、恢复或云移动链路。", 26, MUTED)
text(76, 3664, "许可：主体 GPL-3.0-or-later；指定 server 目录另用 BUSL-1.1，复用按文件核对。具体依据见项目 README 和网页来源。", 25, MUTED)

svg.append("</svg>")
assets = PROJECT / "assets"
web_assets = PROJECT / "web" / "assets"
assets.mkdir(exist_ok=True)
web_assets.mkdir(exist_ok=True)
png = assets / "07-complete-understanding.png"
vector = assets / "07-complete-understanding.svg"
image.save(png, optimize=True)
vector.write_text("\n".join(svg)+"\n", encoding="utf-8")
(assets / "07-understanding-content.txt").write_text("\n".join(visible_text)+"\n", encoding="utf-8")
shutil.copyfile(png, web_assets / "complete-understanding.png")
shutil.copyfile(vector, web_assets / "complete-understanding.svg")
print(f"Rendered {WIDTH}x{HEIGHT} PNG and SVG; exact-text source retained; copied to web/assets")
