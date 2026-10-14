"""Draw the original BaoCut research infographic as matching PNG and SVG files.

All text is a research summary of fixed upstream commit 7aa049e8, not an
upstream screenshot or an execution result. Pillow lays out the Chinese text;
the same drawing commands are also emitted as editable vector markup.
"""

from html import escape
from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 2400, 3740
FONT_DIR = Path("C:/Windows/Fonts")
PALETTE = {
    "paper": "#F6F5EF", "ink": "#173C37", "muted": "#5A6D62",
    "line": "#CCD6C7", "white": "#FFFEF9", "soft": "#E7EDDF",
    "lime": "#D9EAB7", "coral": "#C66A4E", "light": "#CEDCC8",
}


class Canvas:
    def __init__(self):
        self.image = Image.new("RGB", (WIDTH, HEIGHT), PALETTE["paper"])
        self.draw = ImageDraw.Draw(self.image)
        self.svg = []
        self.fonts = {}
        self.text_records = []

    def font(self, size, bold=False):
        key = (size, bold)
        if key not in self.fonts:
            name = "msyhbd.ttc" if bold else "msyh.ttc"
            self.fonts[key] = ImageFont.truetype(str(FONT_DIR / name), size)
        return self.fonts[key]

    def rect(self, x, y, w, h, fill, border=None, radius=20):
        self.draw.rounded_rectangle((x, y, x+w, y+h), radius=radius,
                                    fill=fill, outline=border, width=2)
        stroke = f' stroke="{border}" stroke-width="2"' if border else ""
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                        f'rx="{radius}" fill="{fill}"{stroke}/>')

    def line(self, points, color=None, width=3, arrow=False):
        color = color or PALETTE["muted"]
        self.draw.line(points, fill=color, width=width, joint="curve")
        coords = " ".join(f"{x},{y}" for x, y in points)
        self.svg.append(f'<polyline points="{coords}" fill="none" stroke="{color}" '
                        f'stroke-width="{width}" stroke-linejoin="round"/>')
        if arrow:
            (x0, y0), (x1, y1) = points[-2:]
            dx, dy = x1-x0, y1-y0
            magnitude = (dx*dx+dy*dy)**0.5
            ux, uy = dx/magnitude, dy/magnitude
            left = (x1-14*ux+7*uy, y1-14*uy-7*ux)
            right = (x1-14*ux-7*uy, y1-14*uy+7*ux)
            polygon = [left, (x1, y1), right]
            self.draw.polygon(polygon, fill=color)
            coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in polygon)
            self.svg.append(f'<polygon points="{coords}" fill="{color}"/>')

    def wrap(self, text, size, width, bold=False):
        font = self.font(size, bold)
        result = []
        for paragraph in text.split("\n"):
            line = ""
            for char in paragraph:
                candidate = line + char
                if line and self.draw.textlength(candidate, font=font) > width:
                    result.append(line)
                    line = char
                else:
                    line = candidate
            result.append(line)
        return result

    def text(self, x, y, text, size=30, color=None, bold=False, max_width=None,
             line_height=None, max_height=None):
        color = color or PALETTE["ink"]
        lines = self.wrap(text, size, max_width, bold) if max_width else text.split("\n")
        line_height = line_height or int(size*1.48)
        height = (len(lines)-1)*line_height+size
        if max_height is not None and height > max_height:
            raise ValueError(f"Text exceeds its panel: {text!r} needs {height}, has {max_height}")
        font = self.font(size, bold)
        ascent, _ = font.getmetrics()
        for index, line in enumerate(lines):
            top = y+index*line_height
            self.draw.text((x, top), line, fill=color, font=font, anchor="lt")
            bbox = font.getbbox(line or " ")
            baseline = top+ascent-bbox[1]
            weight = "700" if bold else "400"
            self.svg.append(f'<text x="{x}" y="{baseline}" font-size="{size}" '
                            f'font-weight="{weight}" fill="{color}">{escape(line)}</text>')
            self.text_records.append({"text":line, "x":x, "y":top,
                                      "width":self.draw.textlength(line,font=font),
                                      "font_size":size})
        return y+height

    def section(self, number, title, y, note=""):
        self.text(68, y, number, 29, PALETTE["coral"], True)
        self.text(133, y-3, title, 42, bold=True)
        if note:
            self.text(133, y+57, note, 26, PALETTE["muted"], max_width=2195)

    def save(self):
        for record in self.text_records:
            if record["x"]+record["width"] > WIDTH-50:
                raise ValueError(f'Text extends beyond the right margin: {record["text"]}')
            if record["y"] < 0 or record["y"]+record["font_size"] > HEIGHT-30:
                raise ValueError(f'Text extends beyond the canvas: {record["text"]}')
        svg = '\n'.join([
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
            f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">',
            '<title id="title">BaoCut 完整理解总览：能力、功能、人机协作、场景与价值</title>',
            '<desc id="desc">八部分中文研究图：人通过界面、AI 通过工具共同修改当前视频；'
            '原有视频功能、输入输出、模型入口、新增设计画布与设计系统、适用场景、'
            '个人研究价值以及未验证事项。</desc>',
            '<style>text{font-family:"Microsoft YaHei","PingFang SC",sans-serif}</style>',
            f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{PALETTE["paper"]}"/>',
            *self.svg,
            '</svg>',
        ]) + '\n'
        paths = []
        for folder in (PROJECT/"assets", PROJECT/"web"/"assets"):
            folder.mkdir(exist_ok=True)
            png = folder/"understanding-comprehensive.png"
            self.image.save(png, optimize=True)
            vector = folder/"understanding-comprehensive.svg"
            vector.write_text(svg, encoding="utf-8", newline="\n")
            paths.extend([str(png), str(vector)])
        results = PROJECT/"experiments"/"results"
        results.mkdir(exist_ok=True)
        (results/"overview-layout.json").write_text(json.dumps({
            "size": [WIDTH, HEIGHT], "minimum_body_font": 28,
            "text_lines": len(self.text_records), "bounds_check": "passed",
            "source_ref": "7aa049e82e1367da013b7aba80f0b79033fa04ad",
            "outputs": [Path(p).relative_to(PROJECT).as_posix() for p in paths],
        }, ensure_ascii=False, indent=2)+'\n', encoding="utf-8")
        print(json.dumps({"size":[WIDTH,HEIGHT],"text_lines":len(self.text_records),
                          "outputs":paths},ensure_ascii=False))


def panel(canvas, x, y, width, height, title, lines, dark=False, title_size=34):
    fill = PALETTE["ink"] if dark else PALETTE["white"]
    ink = PALETTE["white"] if dark else PALETTE["ink"]
    body = PALETTE["light"] if dark else PALETTE["muted"]
    canvas.rect(x,y,width,height,fill,None if dark else PALETTE["line"])
    canvas.text(x+27,y+25,title,title_size,ink,True,max_width=width-54)
    canvas.text(x+27,y+82,lines,29,body,max_width=width-54,
                line_height=44,max_height=height-90)


def build():
    c=Canvas()
    c.text(68,42,"014 / BAOCUT · 完整理解总览 · 固定版本 7aa049e8 · 2026.10.14",27,PALETTE["muted"])
    c.text(68,96,"BaoCut：人和 AI，接着改同一份作品。",68,bold=True)
    c.text(68,192,"底层视频能力 + 可视化 UI + 模型对话 → 可编辑、可接手、可持续优化的创作流程",35,PALETTE["coral"],True)

    # 01 / Identity and shared video editing structure.
    c.section("01","它是什么？怎样让人和 AI 配合？",285,
              "以可编辑视频为中心的 AI 创作工作台。人决定要求与接受程度，模型组织工作，底层负责执行和保存。")
    panel(c,68,396,392,122,"人 → 可视化 UI","预览 / 编辑 / 撤销",title_size=31)
    panel(c,68,544,392,122,"AI → 工具调用","理解 / 执行 / 回执",title_size=31)
    c.line([(472,456),(510,456),(510,531),(548,531)],arrow=True)
    c.line([(472,604),(510,604),(510,531)])
    panel(c,560,459,460,155,"共同视频编辑入口","命令 · 事务 · 撤销机制",title_size=32)
    c.line([(1033,531),(1080,531)],arrow=True)
    panel(c,1093,425,650,212,"同一份可编辑视频项目","时间线 · 文稿 · 字幕 · 音轨\n底层执行操作，保留当前工作稿",True,35)
    c.line([(1757,531),(1800,531)],arrow=True)
    panel(c,1813,459,519,155,"人检查，再继续优化","通过 UI 调整，或提出下一轮要求",title_size=32)
    c.line([(2070,650),(2070,686),(960,686),(960,650)],color=PALETTE["coral"],arrow=True)
    c.text(1200,654,"查看 → 反馈 → 修改 → 再检查",26,PALETTE["coral"])
    c.text(68,715,"视频编辑的 UI 与 AI 修改共同进入当前项目；AI 主要调用工具接口，无需模拟鼠标点击。",29,PALETTE["muted"])

    # 02 / Eight capability families, without claiming tested execution.
    c.section("02","源库原有视频能力与功能",800,
              "下列为固定版本文档描述的能力；具体精度、效果和可用性取决于模型、素材、配置与硬件。")
    capabilities=[
        ("① 转写与说话人","本地或在线语音转写\n带时间信息，按模型区分说话人\n可以核对与修订转写"),
        ("② 字幕与翻译","原文、译文或双语字幕\n修改具体句子与字幕样式\n字幕结果保存在视频项目中"),
        ("③ 声音与配音","人声与背景分离\n预设或克隆音色，逐句合成\n跨语言配音与重新铺设音轨"),
        ("④ 口播与时间线剪辑","删除口头语、长停顿和重录\n调整镜头、剪辑点与顺序\n保留原始媒体文件"),
        ("⑤ 从简报制作视频","组织脚本、合成旁白\n按旁白编排画面与节奏\n复用内置创作模板"),
        ("⑥ 图片与动态图形","生成静态图片\nHTML 代码动效烘焙后入时间线\n字卡、数字、标注与品牌短动画"),
        ("⑦ 内容衍生与整理","按带时间文稿组织章节\n摘要、标题、文章与短视频\n可用时间戳核对资料来源"),
        ("⑧ 导出与继续编辑","MP4、SRT / WebVTT、文稿、音频\n便携 .baocut 项目包\n导出成片后仍可继续编辑项目"),
    ]
    for i,(title,lines) in enumerate(capabilities):
        x=68+(i%4)*574
        y=910+(i//4)*236
        panel(c,x,y,542,212,title,lines,title_size=31)

    # 03 / Input/output and access surfaces.
    c.section("03","输入什么、得到什么、从哪里操作？",1390)
    panel(c,68,1474,714,213,"输入","视频、音频、图片、文稿或创作简报\n自然语言目标、素材、样式与范围要求\n人的 UI 修改；设计模块的位置标注")
    panel(c,811,1474,749,213,"四种入口，共用本地 Runtime","桌面 UI：对话、查看和可视化编辑\nCLI / MCP：脚本或外部智能体操作\nWeb：在浏览器查看与编辑项目")
    panel(c,1589,1474,743,213,"输出","可编辑视频及 MP4 / 字幕 / 音频等\n新增设计稿、设计系统及 HTML / PDF\n回执与修改记录，供人检查与续改")
    c.text(68,1717,"智能体引擎可选；本地 / 在线模型按支持接入。智能体需安装登录；媒体处理依赖 FFmpeg / ffprobe。",29,PALETTE["muted"])

    # 04 / The incremental value of commit 7aa049e8.
    c.section("04","本次新增设计模块：把协作扩展到视觉设计",1804,
              "视频时间线与对话协作原本已有。本次增加设计类作品、相应工具与指导，以及编辑器和会话的连接。")
    panel(c,68,1913,1117,300,"设计画布 / Design Canvas",
          "界面、网页原型、海报、信息图：画板保留可编辑结构\n可视化修改文字、样式、画板位置；元素 / 区域标注\n标注随消息交给 AI，针对具体位置继续修改\n整份设计稿可导出 HTML / PDF",True,36)
    panel(c,1214,1913,1118,300,"设计系统 / Design System",
          "集中管理颜色、字体、间距、圆角、阴影、组件与素材\n按真实品牌或代码资料整理规范，预览组件与文档\n针对具体条目标注，让 AI 继续修改\n供后续设计稿引用，使视觉规则与素材可以复用",True,36)
    c.text(68,2241,"模块价值：可编辑结构 + 可视化反馈 + 规范复用。设计模块使用自己的文件与宿主桥接机制。",29,PALETTE["muted"])

    # 05 and 06 / Applications and personal learning value are research judgments.
    c.text(68,2327,"05",29,PALETTE["coral"],True)
    c.text(133,2324,"适用场景",42,bold=True)
    c.text(1214,2327,"06",29,PALETTE["coral"],True)
    c.text(1279,2324,"对我们的价值",42,bold=True)
    c.rect(68,2412,1117,439,PALETTE["white"],PALETTE["line"])
    c.rect(1214,2412,1118,439,PALETTE["white"],PALETTE["line"])
    scenarios=[
        ("口播、教程与知识讲解","去停顿、校字幕、调镜头，人逐轮检查表达与节奏。"),
        ("跨语言内容发布","翻译字幕、重做配音，并由人试听与核对。"),
        ("产品或项目传播","制作解说视频、动态图形，以及配套视觉设计稿。"),
        ("个人创作与品牌整理","保存可编辑成果，维护设计规范与常用素材。"),
    ]
    values=[
        ("把学习与项目研究做成作品","探索视频化笔记、项目解说和可持续修改的展示。"),
        ("借鉴人机协作的方法","学习 UI 接手、当前状态共享、范围控制与反馈定位。"),
        ("学习工程组织方式","研究执行工具、任务调度、事务撤销及多模型入口。"),
        ("积累可复用的创作资产","保留时间线、结构化设计稿、规范和素材。"),
    ]
    for x,items in [(96,scenarios),(1242,values)]:
        for i,(title,body) in enumerate(items):
            y=2440+i*100
            c.text(x,y,title,32,bold=True)
            c.text(x,y+47,body,28,PALETTE["muted"],max_width=1060,max_height=48)
    c.text(68,2880,"场景与个人价值为我们的适配判断。是否减少返工、提高质量或节约成本，需要真实任务对照验证。",29,PALETTE["coral"])

    # 07 / One complete iteration with a clear narrow-change example.
    c.section("07","实际怎么用：一轮协作，再接下一轮",2969)
    steps=["明确目标","AI 出初稿","UI 查看试听","人直接调整","限定修改范围","AI 局部修订","人验收导出"]
    for i,title in enumerate(steps):
        x=68+i*327
        c.rect(x,3050,300,76,PALETTE["ink"] if i in (1,5) else PALETTE["soft"],radius=10)
        c.text(x+16,3070,f"{i+1}  {title}",29,PALETTE["white"] if i in (1,5) else PALETTE["ink"],True)
        if i<6:
            c.line([(x+305,3088),(x+320,3088)],arrow=True,width=2)
    c.text(68,3152,"例子：AI 将口播剪成一分钟 → 你改镜头和第二句 → 要求 AI 只改第三句、保留人工调整 → 再检查。",29,PALETTE["muted"])

    # 08 / Scope, provenance, legal reference, and verification.
    c.section("08","理解与验证边界",3238)
    limits=[
        ("验证范围","已核对固定版本资料\n网页教学流程已本地检查\n未运行真实上游视频或模型\n质量、费用、速度尚未实测"),
        ("能力边界","人工改动保留可靠性待实测\n未证明设计稿自动入时间线\n网页原型需另做业务工程\n便携包不含完整撤销历史"),
        ("新增贡献与来源","核心价值在工作流集成\n编辑器来自前端重建移植\n模型能力取决于所选模型\n原有视频协作与新增要分清"),
        ("上游许可","BaoCut Community License 1.0\n附条件的源码可用许可\n使用与再分发以条款为准\n图标字体分发许可待确认"),
    ]
    for i,(title,lines) in enumerate(limits):
        panel(c,68+i*574,3319,542,269,title,lines,title_size=32)
    c.text(68,3615,"来源：JimLiu/baocut · commit 7aa049e8 · 中文 README、产品设计、设计运行时与设计指导、LICENSE。",26,PALETTE["muted"])
    c.text(68,3660,"本仓库原创研究图，非 BaoCut 产品截图或运行证明。主线：底层执行 + 人直接编辑 + 模型对话，共同优化当前作品。",26,PALETTE["muted"])
    c.save()


if __name__ == "__main__":
    build()
