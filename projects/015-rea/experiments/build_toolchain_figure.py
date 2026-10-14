"""Draw the reviewed REA overview as matching SVG and PNG artifacts."""
from pathlib import Path
import html
import json
import math
import re
from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(__file__).resolve().parents[1]
WIDTH = 2400
MARGIN = 76
GAP = 24
INK = "#142e3b"
GREEN = "#36726a"
MUTED = "#52696d"
LINE = "#cedbd3"
PAPER = "#f5f4ef"
FONT = Path("C:/Windows/Fonts/msyh.ttc")
BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")


class Figure:
    def __init__(self):
        self.image = Image.new("RGB", (WIDTH, 10000), PAPER)
        self.draw = ImageDraw.Draw(self.image)
        self.elements = []
        self.fonts = {}
        self.max_text_right = 0

    def font(self, size, bold=False):
        key = (size, bold)
        if key not in self.fonts:
            self.fonts[key] = ImageFont.truetype(str(BOLD if bold else FONT), size)
        return self.fonts[key]

    def rect(self, x, y, w, h, fill="white", stroke=LINE, radius=18):
        self.draw.rounded_rectangle((x, y, x+w, y+h), radius, fill=fill, outline=stroke, width=2)
        self.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')

    def line(self, x1, y1, x2, y2, color=GREEN, width=4):
        self.draw.line((x1, y1, x2, y2), fill=color, width=width)
        self.elements.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}"/>')

    def arrow(self, x1, y1, x2, y2, color=GREEN):
        self.line(x1, y1, x2, y2, color)
        a = math.atan2(y2-y1, x2-x1)
        points = [(x2, y2), (x2-16*math.cos(a-.46), y2-16*math.sin(a-.46)), (x2-16*math.cos(a+.46), y2-16*math.sin(a+.46))]
        self.draw.polygon(points, fill=color)
        self.elements.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="{color}"/>')

    def routed_arrow(self, points, color=GREEN):
        for first, second in zip(points[:-2], points[1:-1]):
            self.line(*first, *second, color, 3)
        self.arrow(*points[-2], *points[-1], color)

    def wrap(self, text, width, size, bold=False):
        font = self.font(size, bold)
        result, line = [], ""
        for token in re.findall(r"[A-Za-z0-9_.@/+\-]+|[^\x00-\x7f]|\s|.", text):
            if token == "\n":
                result.append(line.strip()); line = ""; continue
            if font.getlength(line+token) > width and line:
                if token in "，。、：；！？）》】,.!?;:)]":
                    match = re.search(r"[A-Za-z0-9_.@/+\-]+$|.$", line.rstrip())
                    tail = match.group(0)
                    previous = line[:match.start()].rstrip()
                    if previous:
                        result.append(previous)
                    line = tail + token
                    continue
                result.append(line.strip()); line = ""
            if font.getlength(token) > width:
                for char in token:
                    if font.getlength(line+char) > width:
                        result.append(line.strip()); line = ""
                    line += char
            else:
                line += token
        if line.strip(): result.append(line.strip())
        return result

    def text(self, text, x, y, width, size=28, color=INK, bold=False, leading=None):
        lines = self.wrap(text, width, size, bold)
        leading = leading or round(size*1.5)
        font = self.font(size, bold)
        ascent = font.getmetrics()[0]
        for index, line in enumerate(lines):
            baseline = y + index*leading + ascent
            right = x+font.getlength(line)
            assert right <= x+width+1, (line, right, x+width)
            assert right <= WIDTH-MARGIN+1, (line, right)
            self.max_text_right = max(self.max_text_right, right)
            self.draw.text((x, baseline), line, font=font, fill=color, anchor="ls")
            self.elements.append(f'<text x="{x}" y="{baseline}" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{html.escape(line)}</text>')
        return y + len(lines)*leading

    def text_height(self, text, width, size=28, bold=False, leading=None):
        return len(self.wrap(text, width, size, bold))*(leading or round(size*1.5))

    def section(self, no, title, subtitle, y):
        self.rect(MARGIN, y+5, 60, 56, GREEN, GREEN, 10)
        self.text(no, MARGIN+12, y+7, 45, 28, "white", True)
        self.text(title, MARGIN+85, y, WIDTH-2*MARGIN-90, 40, INK, True)
        bottom = self.text(subtitle, MARGIN, y+73, WIDTH-2*MARGIN, 27, MUTED)
        return bottom+22

    def save(self, height):
        assert height < self.image.height
        desc = "REA 本质、18 类模块的工具原理与交接、六步调查、证据、价值和运行边界；固定版本文档与源码研究，未运行上游。"
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-labelledby="title description"><title id="title">REA 工具、能力、原理与完整流程总览</title><desc id="description">{desc}</desc><rect width="100%" height="100%" fill="{PAPER}"/><g font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif">'+"".join(self.elements)+"</g></svg>\n"
        for directory in (PROJECT/"assets", PROJECT/"web/assets"):
            (directory/"toolchain-overview.svg").write_text(svg, encoding="utf-8")
            self.image.crop((0,0,WIDTH,height)).save(directory/"toolchain-overview.png", optimize=True)
        return {"width":WIDTH,"height":height,"modules":18,"max_text_right":round(self.max_text_right,2)}


def main():
    data = json.loads((PROJECT/"web/data/toolchain-overview.json").read_text(encoding="utf-8"))
    catalog = json.loads((PROJECT/"web/data/capabilities.json").read_text(encoding="utf-8"))
    ids = [value for module in data["modules"] for value in module["capabilities"]]
    assert len(ids) == len(set(ids)) == 37
    assert set(ids) == {item["id"] for item in catalog["capabilities"]}
    f = Figure()
    f.text("015 / REA / REVERSE ENGINEER ANYTHING", MARGIN, 46, 1800, 26, GREEN, True)
    y = f.text("REA 逆向工具与调查流程总览", MARGIN, 104, WIDTH-2*MARGIN, 64, INK, True)
    y = f.text("本质："+data["subtitle"], MARGIN, y+15, WIDTH-2*MARGIN, 38, GREEN, True)+20
    y = f.text("把底层工具的结果，变成 AI 可继续查询、可追踪来源、可对照验证的软件证据。", MARGIN, y, WIDTH-2*MARGIN, 30, MUTED)+42

    y = f.section("01", "先分清谁提供能力，谁决定下一步", "底层引擎提供分析能力；REA 管理接入和证据；模型与助手进行调查；人和实验判断成果。", y)
    roles = [
        ("人 / 研究目标", "提出具体功能问题，提供对应版本材料与许可范围，检查成果。"),
        ("AI / Agent", "选择查询，解释材料，追加调查，写出自己的局部实现。"),
        ("REA / 中间层", "统一 CLI / MCP，适配提供者，解析与追踪，保留 Evidence。"),
        ("分析工具 / 目标", "读机器码、脚本、资源，或记录所选条件下的实际行为。")
    ]
    w = (WIDTH-2*MARGIN-3*GAP)//4
    height = 230
    for i,(title,body) in enumerate(roles):
        x = MARGIN+i*(w+GAP)
        f.rect(x,y,w,height,INK if i==2 else "white",INK if i==2 else LINE)
        f.text(title,x+24,y+22,w-48,31,"white" if i==2 else GREEN,True)
        f.text(body,x+24,y+78,w-48,27,"#d7ebe1" if i==2 else MUTED)
        if i<3:f.arrow(x+w+2,y+115,x+w+GAP-2,y+115)
    y += height+19
    y = f.text("请求向工具侧送达；代码、观察与未知返回 REA 和助手。AI 的解释与工具读取是不同环节。",MARGIN,y,WIDTH-2*MARGIN,27,MUTED)+43

    y = f.section("02", "REA 内部如何把不同工具接成统一调查", "先限定目标身份与分析范围，再在可用的模块之间选择和交接；每次只做问题需要的动作。", y)
    w = (WIDTH-2*MARGIN-2*GAP)//3
    stages = [
        ("入口与契约", "CLI 给人 / 脚本使用；MCP 给助手使用。参数、结果和错误按契约校验。"),
        ("目标与提供者管理", "识别格式、架构、版本和摘要；检查引擎可用性，管理启动、会话与清理。"),
        ("适配与自有分析", "桥接外部引擎；内置格式解析、AST / 应用图、追踪、比较与证据记录。")
    ]
    for i,(title,body) in enumerate(stages):
        x=MARGIN+i*(w+GAP);f.rect(x,y,w,230,"#e5eee4")
        f.text(title,x+25,y+22,w-50,32,GREEN,True)
        f.text(body,x+25,y+77,w-50,28,MUTED)
        if i<2:f.arrow(x+w+2,y+105,x+w+GAP-2,y+105)
    y += 251
    f.arrow(WIDTH//2,y-10,WIDTH//2,y+27)
    y = f.text("按目标选择 ↓   下列模块可交接材料，也可独立查询；并非每次把所有工具都运行一遍。",MARGIN,y+35,WIDTH-2*MARGIN,29,GREEN,True)+37

    y = f.section("03", "18 个模块：工具 → 原理 → 返回材料 → 如何串接", "外部引擎需要相应环境；“REA 内置”表示库本身有解析逻辑。模块编号供下面的完整流程引用。", y)
    colors={"静态":"#36726a","观察 / 执行":"#365f88","执行":"#97702c"}
    for start in range(0,len(data["modules"]),3):
        modules=data["modules"][start:start+3]
        heights=[]
        for module in modules:
            h=88+f.text_height(module["name"],w-55,32,True)
            for label,key in [("工具","tools"),("原理","principle"),("返回","output"),("串接","handoff"),("范围","limit")]:
                h+=f.text_height(label+"  "+module[key],w-52,26,key=="tools")+13
            heights.append(h+16)
        row_h=max(heights)
        for i,module in enumerate(modules):
            x=MARGIN+i*(w+GAP);color=colors[module["kind"]]
            f.rect(x,y,w,row_h,"white")
            f.text(module["no"]+" / "+module["kind"],x+26,y+20,w-52,24,color,True)
            cy=f.text(module["name"],x+26,y+63,w-52,32,INK,True)+18
            f.line(x+26,cy-5,x+w-26,cy-5,LINE,2)
            for label,key in [("工具","tools"),("原理","principle"),("返回","output"),("串接","handoff"),("范围","limit")]:
                cy=f.text(label+"  "+module[key],x+26,cy+8,w-52,26,color if key=="tools" else MUTED,key=="tools")+5
            assert cy<=y+row_h-6,(module["no"],cy,y+row_h)
        y += row_h+GAP
    y += 15
    f.arrow(WIDTH//2,y-10,WIDTH//2,y+20)
    y += 34
    f.rect(MARGIN,y,WIDTH-2*MARGIN,127,INK,INK)
    f.text("各模块返回 → REA 统一证据 → AI 决定继续查什么 → 必要时再次选择模块",MARGIN+28,y+19,WIDTH-2*MARGIN-56,35,"white",True)
    f.text("交接要保留文件 / 组件身份、地址或源码位置、解析范围与关系依据，不能只凭同名函数或同时出现来关联。",MARGIN+28,y+76,WIDTH-2*MARGIN-56,26,"#c7dfd3")
    y += 163

    y = f.section("04", "一条完整链路：调查“导出按钮怎样保存文件”", "下图是方法示例；具体入口、IPC 链与写入行为需要真实目标证据。发现未知或对照失败时返回前面的查询。", y)
    workflow_rows=[]
    for start in (0,3):
        max_h=0
        for i,step in enumerate(data["workflow"][start:start+3]):
            h=110+f.text_height(step["text"],w-55,28)+f.text_height(step["modules"],w-55,25)+43
            max_h=max(max_h,h)
        workflow_rows.append((y,max_h))
        for i,step in enumerate(data["workflow"][start:start+3]):
            x=MARGIN+i*(w+GAP)
            f.rect(x,y,w,max_h,"#eaf1e7")
            f.text(step["no"]+"  "+step["title"],x+25,y+22,w-50,32,GREEN,True)
            cy=f.text(step["text"],x+25,y+85,w-50,28,MUTED)+13
            f.text(step["modules"],x+25,cy,w-50,25,GREEN,True)
            if i<2:f.arrow(x+w+2,y+max_h//2,x+w+GAP-2,y+max_h//2)
        y += max_h+GAP
    row1, height1 = workflow_rows[0]
    row2, height2 = workflow_rows[1]
    right = MARGIN+2*(w+GAP)+w
    f.routed_arrow([(right,row1+height1//2),(WIDTH-47,row1+height1//2),
                    (WIDTH-47,row1+height1+GAP//2),(49,row1+height1+GAP//2),
                    (49,row2+height2//2),(MARGIN,row2+height2//2)],GREEN)
    y = f.text("这条流程由助手按发现推进；六种 MCP 调查指引提供起点，流程定义本身不会自动调用所有工具。",MARGIN,y+1,WIDTH-2*MARGIN,27,MUTED)+42

    y = f.section("05", "Evidence：软件材料怎样变成可复核的依据", "归一化让结果可保留、可查询、可比较；具体字段与覆盖取决于操作，统一记录不表示所有结果都已正确。", y)
    evidence = [
        ("材料身份与来源", "目标 / SHA-256、提供者与版本、操作与参数、地址 / 文件位置、关联 Evidence。"),
        ("事实、推导与假设", "observed / derived / inferred 是依据类别，不是正确率。保留 raw / normalized 结果及 authority。"),
        ("范围与剩余未知", "limitations、关系覆盖、缺失材料与未完成验证。静态可达 ≠ 已执行；观察关联 ≠ 因果证明。")
    ]
    h=max(110+f.text_height(body,w-50,27) for _,body in evidence)
    for i,(title,body) in enumerate(evidence):
        x=MARGIN+i*(w+GAP);f.rect(x,y,w,h,INK,INK)
        f.text(title,x+25,y+21,w-50,32,"#b3dbc7",True)
        f.text(body,x+25,y+80,w-50,27,"#d4e4df")
    y += h+44

    y = f.section("06", "价值：减少接入负担，让调查与复现有依据", "价值来自工具可用、材料可追踪与实验可对照；实际效率、质量和总费用仍需用同任务比较。", y)
    values=[
        ("统一工具入口", "复用 CLI / MCP 与适配器，减少反复切换工具、协议和结果格式。"),
        ("追踪跨层功能", "从资源 / 脚本 / IPC 到原生函数，再以运行材料核对关系。"),
        ("保留研究依据", "每条结论关联版本、位置、工具、覆盖和未知，便于回查与比较。"),
        ("辅助兼容与复现", "为功能学习、迁移、软件保存和授权研究提供材料；用有限测试报告范围。")
    ]
    for i,(title,body) in enumerate(values):
        x=MARGIN+i*( (WIDTH-2*MARGIN-3*GAP)//4 +GAP);vw=(WIDTH-2*MARGIN-3*GAP)//4
        f.rect(x,y,vw,230,"#e8eee0")
        f.text(title,x+22,y+21,vw-44,30,GREEN,True)
        f.text(body,x+22,y+78,vw-44,26,MUTED)
    y += 264

    y = f.section("07", "成立条件与边界", "工具需要与材料、平台、版本和权限相匹配；有限功能验证不能推出整款软件等价。", y)
    notes=[
        "运行时：REA 要求 Node.js 22.19+（22.x）、24.11+（24.x）或 26+；SQLite 单独要求 24.15+ / 26+。",
        "平台：Windows Ghidra 是实验性只读范围，主要准入 x86 / x64 PE 与 raw 6502；Linux 专用适配不能直接推广到 Windows。",
        "环境：各外部工具按需自备；JADX 需要完整 JDK，商业引擎按其许可使用。进程、设备、浏览器与插桩操作有实际效果。",
        "解释：不保证原始变量名、注释、完整源码或后端内部实现；REA 没有替代模型理解、领域判断和最终行为验证。"
    ]
    for note in notes:y=f.text("• "+note,MARGIN,y,WIDTH-2*MARGIN,28,MUTED)+9
    y += 14
    f.line(MARGIN,y,WIDTH-MARGIN,y,LINE,2);y+=24
    y=f.text("本仓库原创整理 · 2026-10-14 · 固定研究提交 ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4",MARGIN,y,WIDTH-2*MARGIN,24,GREEN,True)
    y=f.text(data["scope"]+"  外部工具各保留许可；本图不是软件分析实测截图。",MARGIN,y+9,WIDTH-2*MARGIN,24,MUTED)
    result=f.save(y+MARGIN)
    result["covered_capabilities"]=len(ids)
    (PROJECT/"experiments/results/toolchain-figure-layout.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
