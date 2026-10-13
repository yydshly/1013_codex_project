"""Draw the research overview as editable SVG and a matching readable PNG.

This only creates an explanatory figure; it never runs the upstream RAG app.
Requires Pillow and Microsoft YaHei fonts. Run from any working directory.
"""

from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 2400, 3500
INK, TEXT, MUTED = "#243d34", "#43534c", "#69756d"
GREEN, PALE, LIME, LINE, BG = "#264d3d", "#e9eee5", "#d7e9b7", "#d4deca", "#f5f6f0"
REGULAR = Path("C:/Windows/Fonts/msyh.ttc")
BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")
ET.register_namespace("", "http://www.w3.org/2000/svg")


class Figure:
    def __init__(self):
        self.image = Image.new("RGB", (WIDTH, HEIGHT), BG)
        self.draw = ImageDraw.Draw(self.image)
        self.svg = ET.Element("{http://www.w3.org/2000/svg}svg", {
            "viewBox": f"0 0 {WIDTH} {HEIGHT}", "width": str(WIDTH), "height": str(HEIGHT),
            "role": "img", "aria-labelledby": "figure-title figure-desc",
        })
        ET.SubElement(self.svg, "title", {"id": "figure-title"}).text = "论文 RAG 与我们的知识库：理解总览"
        ET.SubElement(self.svg, "desc", {"id": "figure-desc"}).text = (
            "项目定位、能力、价值、建库与问答原理、组件职责、适用场景、使用路线、扩展和验收。"
            "依据上游 commit 424a0eb；所有上游运行效果尚未复现，新领域和扩展方向待实现验证。"
        )
        self.rect(0, 0, WIDTH, HEIGHT, BG, radius=0)
        self.fonts = {}

    def rect(self, x, y, w, h, fill=PALE, stroke=None, radius=16):
        self.draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=fill, outline=stroke, width=2)
        attrs = {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "rx": str(radius), "fill": fill}
        if stroke:
            attrs.update(stroke=stroke, **{"stroke-width": "2"})
        ET.SubElement(self.svg, "rect", attrs)

    def text(self, x, y, value, size=32, fill=TEXT, bold=False, width=None, line_height=None):
        key = (size, bold)
        if key not in self.fonts:
            self.fonts[key] = ImageFont.truetype(str(BOLD if bold else REGULAR), size)
        font = self.fonts[key]
        lines = []
        for paragraph in value.split("\n"):
            line = ""
            for character in paragraph:
                candidate = line + character
                if width and line and font.getlength(candidate) > width:
                    lines.append(line)
                    line = character
                else:
                    line = candidate
            lines.append(line)
        spacing = line_height or round(size * 1.45)
        for index, line in enumerate(lines):
            top = y + index * spacing
            length = font.getlength(line)
            assert x >= 0 and x + length <= WIDTH - 40, (line, x + length)
            assert top + size < HEIGHT - 24, (line, top)
            self.draw.text((x, top), line, font=font, fill=fill, anchor="lt")
            ET.SubElement(self.svg, "text", {
                "x": str(x), "y": str(top), "fill": fill, "font-size": str(size),
                "font-family": "Microsoft YaHei, PingFang SC, Noto Sans CJK SC, sans-serif",
                "font-weight": "700" if bold else "400", "dominant-baseline": "text-before-edge",
            }).text = line
        return y + len(lines) * spacing

    def line(self, x1, y1, x2, y2, fill=LINE, thickness=3):
        self.draw.line((x1, y1, x2, y2), fill=fill, width=thickness)
        ET.SubElement(self.svg, "line", {"x1": str(x1), "y1": str(y1), "x2": str(x2), "y2": str(y2), "stroke": fill, "stroke-width": str(thickness)})

    def arrow(self, x1, y, x2):
        self.line(x1, y, x2, y, GREEN, 4)
        points = [(x2 - 12, y - 11), (x2, y), (x2 - 12, y + 11)]
        self.draw.line(points, fill=GREEN, width=4)
        ET.SubElement(self.svg, "polyline", {"points": " ".join(f"{x},{top}" for x, top in points), "stroke": GREEN, "stroke-width": "4", "fill": "none"})

    def heading(self, number, y, title, note=None):
        self.rect(96, y - 1, 68, 58, GREEN, radius=12)
        self.text(108, y + 8, number, size=34, fill=LIME, bold=True)
        self.text(186, y + 2, title, size=44, fill=INK, bold=True)
        if note:
            self.text(1280, y + 13, note, size=27, fill=MUTED)


def create():
    figure = Figure()
    f = figure
    f.text(96, 60, "研究项目 002  /  PRODUCTION AGENTIC RAG COURSE", 29, MUTED)
    f.text(96, 125, "一图看懂：论文 RAG 与我们的知识库", 76, INK, True)
    f.text(96, 231, "论文是案例  ·  RAG 工程是参考  ·  自有资料是基础", 39, GREEN)
    f.line(96, 310, 2304, 310)

    f.heading("01", 343, "定位、能力与价值")
    cards = [
        ("项目定位", "以 arXiv AI 论文为默认资料\n课程＋应用参考工程\n串起资料处理、检索与问答\n学习完整 RAG 的搭建方法"),
        ("实现能力｜源码存在", "采集论文、解析切块、建索引\n关键词＋语义混合检索\n模型问答与论文来源链接\n追踪、普通问答缓存、多入口"),
        ("我们的价值｜待实测", "理解数据、检索与模型的衔接\n把自己的资料变成知识库\n为研究对比与资料助手打基础\n用质量、时间和成本衡量收益"),
    ]
    for i, (title, body) in enumerate(cards):
        x = 96 + i * 746
        f.rect(x, 425, 716, 275, "#ffffff", LINE)
        f.text(x + 27, 449, title, 36, INK, True)
        end = f.text(x + 27, 512, body, 31, TEXT, width=662, line_height=43)
        assert end <= 695

    f.heading("02", 748, "核心原理与架构")
    f.text(96, 822, "先建库｜把获取到的资料变成可检索的知识", 31, GREEN, True)
    offline = [
        ("收集与整理", "arXiv 或适配新来源\n保留原文、来源与版本"),
        ("解析与保存", "Docling 提取内容\nPostgreSQL 存正文与元信息"),
        ("切块与向量化", "保留片段及原文位置\nJina API 生成语义向量"),
        ("建立搜索索引", "OpenSearch\n片段＋向量＋来源"),
    ]
    for i, (title, body) in enumerate(offline):
        x = 96 + i * 566
        f.rect(x, 877, 510, 184, PALE, LINE)
        f.text(x + 22, 900, title, 36, INK, True)
        end = f.text(x + 22, 957, body, 29, TEXT, width=466, line_height=42)
        assert end <= 1058
        if i < 3:
            f.arrow(x + 522, 969, x + 554)
    f.text(96, 1101, "再使用｜每次问题都先检索，再让模型依据资料回答", 31, GREEN, True)
    online = [
        ("用户问题", "只检索已入库的资料"),
        ("检索相关片段", "BM25＋向量检索\nRRF 合并两路排名"),
        ("模型生成回答", "问题＋相关片段\n一起交给 Ollama"),
        ("回答＋来源", "阅读结论并回看原文\n核对依据是否支持回答"),
    ]
    for i, (title, body) in enumerate(online):
        x = 96 + i * 566
        f.rect(x, 1155, 510, 160, GREEN if i == 1 else "#ffffff", None if i == 1 else LINE)
        f.text(x + 22, 1177, title, 36, LIME if i == 1 else INK, True)
        f.text(x + 22, 1233, body, 29, "#ffffff" if i == 1 else TEXT, width=466, line_height=41)
        if i < 3:
            f.arrow(x + 522, 1235, x + 554)
    f.rect(96, 1353, 2208, 108, "#e2eadb")
    f.text(121, 1369, "RAG 的核心", 33, INK, True)
    f.text(121, 1415, "把检索片段放进本次模型输入；无需重新训练模型，知识覆盖范围由已入库资料决定。", 31, TEXT)
    f.rect(96, 1490, 2208, 149, "#ffffff", LINE)
    f.text(121, 1507, "Agentic｜增加检索过程的判断与重试", 33, INK, True)
    f.text(121, 1555, "领域判断 → 检索 → 检查相关性 → 回答；不相关则改写并重新检索。", 32, TEXT)
    f.text(121, 1602, "默认最多检索两次；参数、模型接入、来源与追踪闭环仍需复现核对。", 29, MUTED)
    f.text(96, 1674, "Airflow：采集调度   Redis：普通问答缓存   Langfuse：追踪   FastAPI / Gradio / Telegram：入口", 27, MUTED)

    f.heading("03", 1737, "适用场景与必要适配")
    scenarios = [
        ("上游默认", "AI 论文研究", "查找方法、比较研究，回到论文核对依据"),
        ("适配方向", "农业与种植", "论文、手册、试验记录；保留作物、地区、土壤、气候与实验条件"),
        ("适配方向", "产品与技术资料", "产品手册、规范、操作文档；区分型号、版本与使用者权限"),
        ("适配方向", "GitHub 项目研究", "README、源码分析、复现记录；保留仓库、commit 与验证状态"),
    ]
    for i, (label, title, body) in enumerate(scenarios):
        y = 1818 + i * 89
        f.rect(96, y, 2208, 78, "#ffffff", LINE, 10)
        f.rect(111, y + 14, 156, 48, GREEN if i == 0 else PALE, radius=8)
        f.text(124, y + 23, label, 28, "#ffffff" if i == 0 else GREEN, True)
        f.text(291, y + 22, title, 32, INK, True)
        f.text(645, y + 24, body, 29, TEXT, width=1625)

    f.heading("04", 2240, "我们如何开始")
    steps = [
        ("1  确定问题并准备资料", "一个明确主题＋一批可靠文档\n＋10 个真实问题\n保留来源与期待找到的依据"),
        ("2  跑通最小普通 RAG", "整理 → 解析 → 索引\n搜索 → 问答 → 核对引用\n保存运行基线和验证记录"),
        ("3  验证后再扩展应用", "先确认检索与回答有用\n再加 Agentic、交互入口\n或专题报告与写作流程"),
    ]
    for i, (title, body) in enumerate(steps):
        x = 96 + i * 746
        f.rect(x, 2320, 716, 211, PALE, LINE)
        f.text(x + 24, 2345, title, 34, INK, True)
        f.text(x + 24, 2403, body, 30, TEXT, width=668, line_height=41)
    f.text(96, 2563, "最终积累：资料集合＋可检索知识库＋问答接口＋验证记录，作为后续应用基础。", 31, GREEN, True)

    f.heading("05", 2640, "可扩展方向", "均需后续实现与验证")
    extensions = [
        ("新资料入口与定期更新", "增加导入、去重和更新流程"),
        ("中文、扫描件与表格", "验证 OCR 与实验条件提取"),
        ("本地向量模型与私有部署", "同时考虑向量化、生成与追踪"),
        ("权限、版本与领域筛选", "回答使用正确且可访问的资料"),
        ("Agentic 与质量评测", "比较重试的收益、耗时与成本"),
        ("资料助手、报告与长文写作", "探索知识检索与项目 001 的衔接"),
    ]
    for i, (title, body) in enumerate(extensions):
        x, y = 96 + (i % 3) * 746, 2720 + (i // 3) * 123
        f.rect(x, y, 716, 107, "#ffffff", LINE, 10)
        f.text(x + 23, y + 16, title, 32, INK, True)
        f.text(x + 23, y + 61, body, 28, MUTED)

    f.heading("06", 3020, "怎样判断是否真的有用")
    checks = [
        ("解析", "原文、表格与实验条件是否完整？"),
        ("检索", "相关资料是否找到，版本是否正确？"),
        ("回答", "结论有引用支持，缺资料时能说明？"),
        ("工程", "更新、缓存、耗时、成本与故障恢复？"),
    ]
    for i, (label, body) in enumerate(checks):
        x, y = 96 + (i % 2) * 1120, 3105 + (i // 2) * 97
        f.rect(x, y, 1088, 76, PALE, radius=10)
        f.text(x + 20, y + 22, label, 31, INK, True)
        f.text(x + 115, y + 22, body, 29, TEXT)
    f.line(96, 3310, 2304, 3310)
    f.text(96, 3339, "当前：已读源码并完成导读，尚未运行上游；农业等领域需适配，网页未连接真实论文库或模型。", 29, GREEN, True)
    f.text(96, 3405, "依据：jamwithai/production-agentic-rag-course · commit 424a0eb · 2026-10-13", 27, MUTED)

    web_assets = PROJECT / "web" / "assets"
    web_assets.mkdir(exist_ok=True)
    f.image.save(web_assets / "rag-understanding.png", optimize=True)
    ET.indent(f.svg)
    ET.ElementTree(f.svg).write(web_assets / "rag-understanding.svg", encoding="utf-8", xml_declaration=True)
    f.image.save(PROJECT / "assets" / "04-rag-understanding.png", optimize=True)
    print(f"Overview exported: {WIDTH} x {HEIGHT}; PNG and SVG")


if __name__ == "__main__":
    create()
