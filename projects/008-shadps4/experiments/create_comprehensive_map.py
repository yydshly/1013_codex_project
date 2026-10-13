"""Author the editable Chinese summary diagram from the fixed research record."""
from html import escape
import json
from pathlib import Path
import shutil
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1800, 3290
PAPER, INK, MUTED = "#f8f7f2", "#233b33", "#63746a"
GREEN, LIME, SOFT, LINE = "#163c31", "#dcf294", "#edf1e7", "#d5dfd1"
REF = "23c41333822fe8eca4c609b43119180af63ae4ac"
SOURCE = f"https://github.com/shadps4-emu/shadPS4/blob/{REF}/"
parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
<title id="title">shadPS4 全面理解总览：定位、资源控制、能力、原理、价值与扩展</title>
<desc id="desc">PS4 是设备，操作系统是其中的软件，手柄是输入设备。shadPS4 是运行在电脑操作系统上的模拟器核心：管理游戏的内存布局和执行环境，利用主机 CPU，兼容系统接口，转换 GPU 命令和着色器，经 Vulkan 与驱动使用实际显卡。图中包含完整运行流程、控制权限边界、能力与使用场景、基础知识价值、六个扩展方向、对研究者的意义，以及公开样例实测与未验证范围。</desc>
<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto-start-reverse"><path d="M1 1L8 5L1 9" fill="none" stroke="#698271" stroke-width="1.8"/></marker></defs>
<rect width="{WIDTH}" height="{HEIGHT}" fill="{PAPER}"/>
<g font-family="Microsoft YaHei, Noto Sans CJK SC, Segoe UI, sans-serif" fill="{INK}">''']

def rect(x, y, w, h, fill=SOFT, border=None, radius=12):
    stroke = f' stroke="{border}" stroke-width="1.5"' if border else ""
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"{stroke}/>')

def text(x, y, value, size=24, color=INK, weight=400, anchor="start"):
    parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>')

def wrapped(value, width, size):
    result, line, used = [], "", 0
    for char in value:
        step = size * (1 if unicodedata.east_asian_width(char) in "WF" else .60)
        if char == "\n" or (line and used+step > width):
            result.append(line)
            line, used = "", 0
            if char == "\n":
                continue
        line += char
        used += step
    if line:
        result.append(line)
    return result

def para(x, y, value, width, size=24, line_height=34, color=INK):
    for line in wrapped(value, width, size):
        text(x, y, line, size, color)
        y += line_height
    return y

def bounded(x, y, w, h, label):
    parts.append(f'<g data-bounds="{x},{y},{w},{h}" data-label="{escape(label)}">')

def end():
    parts.append('</g>')

def arrow(d, both=False):
    start = ' marker-start="url(#arrow)"' if both else ""
    parts.append(f'<path d="{d}" fill="none" stroke="#698271" stroke-width="2.5" marker-end="url(#arrow)"{start}/>')

def heading(y, number, title, note=None):
    text(64, y, number, 22, MUTED)
    text(112, y, title, 36, GREEN, 600)
    if note:
        text(1736, y, note, 20, MUTED, anchor="end")

# The central statement deliberately separates application control from hardware privilege.
text(64, 69, "008 / shadPS4 / 一张图整理我们的理解", 22, MUTED)
text(64, 135, "把 PS4 游戏的运行条件，搬到电脑上。", 58, GREEN, 600)
rect(64, 168, 1672, 90, GREEN)
text(96, 205, "核心价值：管理游戏的内存布局与执行环境，接通 CPU、GPU 和系统服务，", 30, PAPER, 500)
text(96, 242, "让部分 PS4 程序在另一台电脑上，获得它所期待的运行行为。", 30, LIME, 500)

heading(304, "01", "先分清四个对象")
concepts = [
    ("PS4 = 一台游戏机", "CPU、GPU、内存、存储和操作系统组成的设备，可理解为主要用于游戏的电脑。"),
    ("PS4 操作系统 = 系统软件", "管理资源、线程、文件和设备，并通过系统接口为游戏提供服务。"),
    ("shadPS4 = 模拟器核心", "运行在电脑操作系统上的软件，加载 PS4 程序、兼容系统行为、转换图形工作。"),
    ("手柄 = 输入设备", "角色类似键盘和鼠标；使用手柄不会把一个软件变成操作系统。"),
]
for i, (title, body) in enumerate(concepts):
    x = 64+i*426
    rect(x, 331, 394, 166)
    bounded(x+22, 343, 350, 141, title)
    text(x+22, 369, title, 25, GREEN, 600)
    para(x+22, 407, body, 336, 22, 30)
    end()

heading(550, "02", "“自己控制资源”，具体控制到哪一层？")
rect(64, 575, 1672, 316, "#ffffff", LINE)
rect(64, 575, 1672, 56, SOFT, radius=0)
text(91, 612, "资源", 23, GREEN, 600)
text(277, 612, "shadPS4 自己安排的工作", 23, GREEN, 600)
text(1023, 612, "主机操作系统、驱动与硬件承担的工作", 23, GREEN, 600)
rows = [
    ("内存", "安排游戏地址空间、映射代码和数据，管理缓冲与同步。", "操作系统提供内存分配与映射；硬件完成实际读写。"),
    ("CPU", "建立游戏线程与入口，连接函数，修补平台行为差异。", "操作系统调度线程；合适的 x86-64 CPU 执行大量游戏代码。"),
    ("GPU", "解析 PS4 命令，转换着色器、绘图状态和图形资源。", "经 Vulkan 和主机驱动提交任务，由真实显卡执行。"),
    ("系统功能", "重新实现文件、线程、输入等接口；部分可用原始模块。", "主机系统完成文件与设备操作，提供实际运行资源。"),
]
for i, (name, own, host) in enumerate(rows):
    y = 637+i*62
    text(91, y+29, name, 24, GREEN, 600)
    bounded(277, y+2, 705, 57, name+" / 模拟器")
    para(277, y+24, own, 700, 22, 27)
    end()
    bounded(1023, y+2, 685, 57, name+" / 主机")
    para(1023, y+24, host, 679, 22, 27)
    end()
text(64, 929, "准确说法：它能加载并组织游戏运行；“直接执行 CPU 代码”不等于“绕过操作系统、独占硬件”。", 24, GREEN, 500)

heading(984, "03", "从游戏文件到一帧画面", "简化工作关系，真实任务可以并发")
rect(64, 1008, 1672, 64, SOFT)
text(91, 1049, "制作游戏时：源代码 → 编译器 → PS4 CPU 机器码；图形程序包含 GPU 着色器。", 25)
arrow("M900 1077V1112")
rect(64, 1125, 1672, 72, "#e3ecd8")
text(900, 1170, "输入：PS4 游戏转储 / 公开自制程序 + 资源与所需模块 + 配置 + 玩家输入", 27, GREEN, 500, "middle")
arrow("M900 1200V1233")

rect(64, 1246, 1672, 484, "#ffffff", "#abc09e")
text(92, 1281, "shadPS4 运行引擎", 24, GREEN, 600)
text(1706, 1281, "核心仓库：C++ · 常用图形启动器另在 QtLauncher", 20, MUTED, anchor="end")
rect(100, 1306, 578, 111, GREEN)
bounded(122, 1317, 534, 87, "加载与链接")
text(122, 1348, "① 加载与链接", 29, LIME, 600)
text(122, 1386, "解析可执行文件 → 映射代码 / 数据 → 连接函数", 23, PAPER)
end()
arrow("M684 1361H759")
rect(772, 1306, 928, 111, GREEN)
bounded(797, 1317, 878, 87, "CPU 执行")
text(797, 1348, "② 进入游戏代码，CPU 执行规则和主循环", 29, LIME, 600)
text(797, 1386, "x86-64 主机大量原生执行 + 差异修补；Apple Silicon 路线借助 Rosetta 2", 23, PAPER)
end()
arrow("M1210 1420V1444H442V1464")
arrow("M1210 1444H1283V1464")
rect(100, 1478, 690, 150, SOFT)
bounded(124, 1489, 642, 129, "系统兼容")
text(124, 1520, "③ 系统兼容：接住游戏请求，再返回预期结果", 27, GREEN, 600)
text(124, 1555, "HLE = 用自己的代码实现系统功能；部分原始模块可参与（LLE）。", 21)
text(124, 1584, "例如文件、内存、线程、输入、声音；须匹配数据、句柄与错误码。", 21)
text(124, 1612, "函数有名字或固定返回成功，仍可能只是占位实现。", 21, MUTED)
end()
rect(864, 1478, 836, 150, SOFT)
bounded(888, 1489, 788, 129, "图形与着色器")
text(888, 1520, "④ GPU 命令与着色器转换", 27, GREEN, 600)
text(888, 1555, "解析 PM4 命令 → 整理状态 / 资源 → 组织主机绘图任务", 23)
text(888, 1584, "GCN 指令 → 内部表示 IR → 处理 / 优化 → SPIR-V", 23)
text(888, 1612, "建立 Vulkan 着色器与管线；符合条件时复用缓存。", 23, MUTED)
end()
rect(100, 1650, 1600, 54, "#e3ecd8")
text(900, 1686, "贯穿全程：内存与纹理管理 · CPU / GPU 数据一致性 · 上传 / 下载 / 等待 · 缓存失效与复用", 24, GREEN, 500, "middle")

arrow("M445 1734V1770")
arrow("M1283 1734V1770")
rect(64, 1784, 808, 82, GREEN)
text(94, 1819, "电脑操作系统与资源服务", 28, LIME, 500)
text(94, 1851, "提供内存、线程调度、文件、窗口、声音和输入等实际服务", 23, PAPER)
rect(906, 1784, 830, 82, GREEN)
text(936, 1819, "Vulkan 渲染器 → 主机显卡驱动", 28, LIME, 500)
text(936, 1851, "建立绘图工作、同步资源并提交给主机 GPU", 23, PAPER)
arrow("M445 1870V1903")
arrow("M1283 1870V1903")
rect(64, 1916, 1672, 75, "#e3ecd8")
text(900, 1963, "实际硬件：CPU 执行指令  |  内存保存代码与数据  |  GPU 完成图形 / 计算  |  显示与音频设备输出", 26, GREEN, 500, "middle")
arrow("M900 1995V2028")
rect(64, 2041, 1672, 75, GREEN)
text(900, 2088, "输出：画面、声音、运行状态与调试日志 → 游戏继续处理下一轮输入", 29, LIME, 500, "middle")
text(64, 2155, "两种“编译”：游戏 CPU 代码通常在制作时编译；模拟器运行中按需重编译 GPU 程序。性能与兼容性要分别验证。", 23, GREEN)

heading(2210, "04", "能力、使用场景与价值")
rect(64, 2237, 808, 239, "#ffffff", LINE)
bounded(90, 2250, 756, 213, "能力与用途")
text(90, 2284, "它能提供什么？", 29, GREEN, 600)
text(90, 2321, "加载兼容内容；适配 CPU 执行、系统请求、图形与数据同步。", 24)
text(90, 2356, "系统库、输入音视频、存档与调试功能的完整程度依游戏而异。", 24)
text(90, 2391, "可用场景：兼容游戏体验、公开 homebrew、回归测试、源码学习。", 24)
text(90, 2426, "输入内容不由模拟器自带；系统模块需按具体游戏与版本准备。", 24)
text(90, 2457, "能启动、能到菜单、能进玩法、能稳定玩，是不同层次。", 22, MUTED)
end()
rect(906, 2237, 830, 239, "#ffffff", LINE)
bounded(932, 2250, 778, 213, "项目价值")
text(932, 2284, "它为什么值得研究？", 29, GREEN, 600)
text(932, 2321, "使用价值：为部分 PS4 内容提供在电脑上运行的路径。", 24)
text(932, 2356, "知识价值：体系结构、操作系统、编译原理、图形、并发与缓存。", 24)
text(932, 2391, "工程价值：把软件依赖的行为，映射到另一套系统和硬件。", 24)
text(932, 2426, "研究价值：源码、日志、最小程序与回归结果可以互相核对。", 24)
text(932, 2457, "更强硬件无法自动补齐缺失接口、图形错误或同步问题。", 22, MUTED)
end()

heading(2530, "05", "可以怎样扩展？", "以下是研究提议，难度为相对判断")
extensions = [
    ("中文导读 / 知识索引 · 较低", "解释固定版本、接口与调用链。", "验收：关键结论可追溯，初学者能分清对象。"),
    ("兼容性 / 回归工作台 · 中等", "记录内容、版本、设备、场景与结果。", "验收：条件一致、能够重复并发现退化。"),
    ("日志与源码助手 · 中等", "分阶段整理日志，辅助定位与提出假设。", "验收：人工核实问题集，评估误诊。"),
    ("着色器调试与补丁 · 较高", "导出、抓帧、修改并重新编译图形程序。", "验收：同一帧效果正确，其他场景无回归。"),
    ("系统库 / 同步修复 · 很高", "补接口契约、内存行为、等待与数据一致性。", "验收：最小程序通过，再做游戏回归。"),
    ("图形兼容 / 性能优化 · 很高", "改进指令转换、管线缓存、纹理与传输。", "验收：保持正确，分别测耗时和资源占用。"),
]
for i, (title, body, acceptance) in enumerate(extensions):
    x, y = 64+(i%3)*568, 2559+(i//3)*152
    rect(x, y, 536, 133, SOFT)
    bounded(x+20, y+8, 496, 115, title)
    text(x+20, y+36, title, 25, GREEN, 600)
    para(x+20, y+72, body, 490, 22, 29)
    para(x+20, y+105, acceptance, 490, 21, 27, MUTED)
    end()
text(64, 2874, "新 CPU 架构、手机或浏览器运行属于重大工程，涉及执行方式、内存、线程与图形后端；教学网页只承担解释与证据展示。", 23, GREEN)

heading(2925, "06", "对你的意义：从“看功能”走向“看系统关系”")
rect(64, 2946, 1672, 109, GREEN)
text(95, 2984, "学会识别项目解决哪一层；把“概念 → 调用链 → 源码 → 最小实测 → 局限”变成研究方法。", 27, LIME, 500)
text(95, 3027, "适合补系统基础、做中文知识整理和研究工具；对日常 AI / 资料自动化的直接收益较少，深入程度按你的目标选择。", 23, PAPER)

rect(64, 3080, 1672, 119, SOFT)
text(90, 3115, "本机已验证", 25, GREEN, 600)
text(294, 3115, "shadPS4 v0.19.0：Hello World 真实执行；graphics 显示 CPU 算出的蓝色分形，经 VideoOut / Vulkan 呈现。", 22)
text(90, 3150, "仍未验证", 25, "#966627", 600)
text(294, 3150, "商业游戏、完整 GCN 重编译 / 3D 性能、声音、手柄、存档、联网、跨设备与长期稳定性；无实体 PS4 对照。", 22)
text(90, 3181, "这次样例成功，证明的是一条有限的执行与显示路径；具体游戏兼容性必须单独实测。", 22, MUTED)

text(64, 3237, "本仓库整理的概念图 · 2026-10-14 · 研究源码 23c4133 · 运行包 c7e065d · shadPS4 GPL-2.0-or-later / 公开样例 GPL-3.0", 19, MUTED)
text(64, 3269, "来源：", 19, MUTED)
for x, label, path in [(132,"内存与映射", "src/core/memory.cpp"),(328,"加载与执行", "src/core/linker.cpp"),(524,"图形与着色器", "src/video_core/renderer_vulkan/vk_pipeline_cache.cpp")]:
    parts.append(f'<a href="{SOURCE+path}" target="_blank">')
    text(x, 3269, label, 19, GREEN)
    end_link = '</a>'
    parts.append(end_link)
text(760, 3269, "详细依据与公开样例实测见子项目 README 和 experiments/results/。箭头为简化依赖关系。", 19, MUTED)
parts.append('</g></svg>')

destination = ROOT/'assets/comprehensive-map.svg'
destination.write_text('\n'.join(parts)+'\n', encoding='utf-8')
shutil.copyfile(destination, ROOT/'web/assets/comprehensive-map.svg')
metadata = {
    "date":"2026-10-14", "kind":"authored-vector-explainer", "source":"本仓库根据固定源码、已有研究文档及公开样例实测整理；不是上游截图或实际执行轨迹",
    "research_commit":REF, "runtime_commit":"c7e065d1b415be16c23e260a21f1dd8bbfc4cb57",
    "content":["设备与软件区别", "资源控制层次", "游戏加载与执行", "系统兼容", "图形转换", "内存同步", "能力与用途", "工程和知识价值", "扩展方向与验收", "个人意义", "验证边界"],
    "sources":[SOURCE+"src/core/memory.cpp", SOURCE+"src/core/linker.cpp", SOURCE+"src/video_core/renderer_vulkan/vk_pipeline_cache.cpp", "../README.md", "../experiments/results/runtime-verification.json"],
    "editable":"comprehensive-map.svg", "rendered":"comprehensive-map.png", "dimensions":[WIDTH,HEIGHT],
}
origin = ROOT/'assets/comprehensive-map.source.json'
origin.write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copyfile(origin, ROOT/'web/assets/comprehensive-map.source.json')
print(f'Created {destination.name}: {WIDTH} x {HEIGHT}')
