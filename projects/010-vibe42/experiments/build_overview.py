"""Original overview and diagram teaching data; no product calls or installation."""
from pathlib import Path
from html import escape
import json
import unicodedata
import re

PROJECT = Path(__file__).resolve().parents[1]

ESSENCE = "为电脑上已有的 Agent 提供跨设备远程交互入口；理解、模型调用和工具执行由 Agent 自身负责。"
CAPABILITIES = [
    ("终端交互", "发送文字、按键和确认操作", "查看输出、光标、颜色与图片"),
    ("会话接续", "手机离开，会话可继续运行", "前提是电脑和相应进程仍运行"),
    ("文件与成果", "浏览、预览、编辑与传输文件", "冲突、大小和权限细节待实测"),
    ("桌面与通知", "Mac桌面控制、状态提醒", "多设备/团队访问；权限粒度待验"),
]
SCENARIOS = [
    ("外出接手开发", "查看电脑里的编程任务，处理等待回答或审批的请求。", "主机在线；选对会话；对具体操作作确认。"),
    ("长任务观察", "测试、构建或研究继续运行，手机查看进度与结果。", "断网、休眠、重启要分别测试；通知不代替验收。"),
    ("多电脑入口", "从一个设备切换已有工作电脑和开发环境。", "授权、会话身份、路径与目录必须明确。"),
    ("成果核查与协作", "阅读日志、浏览文件，按权限共享访问或通过Mac桌面接手。", "真实编辑冲突、团队权限和桌面体验尚未验证。"),
]
EXTENSIONS = [
    ("结构化 Agent 适配", "增加任务/历史/审批ID、事件和精确中断；借鉴Agenvo。"),
    ("恢复与故障对账", "稳定会话ID、输出补齐、重连后先查状态，避免重复写操作。"),
    ("授权与可观察性", "设备撤销、访问范围、脱敏日志和诊断；明确内容与元数据边界。"),
    ("任务与产物验收", "连接测试报告、代码改动、研究文件与人的验收记录。"),
    ("研究工作流衔接", "探索接入RAG、cmux工作区与统一模型入口，各层独立验收。"),
    ("平台与部署扩展", "探索自建主机与中继，更多平台、权限和移动体验。"),
]
VALUES = [
    ("直接价值", "人在外面也能接手电脑任务，减少回到电脑前的等待。"),
    ("工程参考", "学习身份、连接、会话、渲染、通知与执行的职责划分。"),
    ("对我们的意义", "让GitHub研究与长任务有移动入口，并保留可追溯成果。"),
    ("实际收益条件", "依赖在线主机、连接质量与正确会话；效率、费用与可靠性须测量。"),
]

def digest_items():
    metadata = json.loads((PROJECT/'project.json').read_text(encoding='utf-8'))
    sections = {item['label']:item['text'] for item in metadata['summary_sections']}
    labels = ['能力','本质','原理','价值','使用场景','可扩展场景']
    return [(label,sections[label]) for label in labels]

PRINCIPLES = [
    {"id":"client", "title":"手机 / 浏览器", "term":"人的控制入口", "body":"人选择已授权电脑与正确会话，输入任务、按键或对当前请求作确认。控制端显示收到的终端内容或桌面画面。", "mechanism":"文字与按键变成输入事件；输出需要终端渲染或画面显示。控制客户端与电脑上的活进程具有不同生命周期。", "example":"你在手机输入“运行测试并说明失败原因”，这一步只提交输入。", "boundary":"输入不等于执行成功。通用终端确认依赖程序当前状态；结构化审批ID需要专门集成。", "source":"install"},
    {"id":"control", "title":"设备配对与授权", "term":"谁可以访问哪台电脑", "body":"账号与设备服务协调身份、配对、在线状态和连接路由，确定允许访问的目标。", "mechanism":"将授权关系与工作内容传输分开：平台需要部分账号、设备和连接记录，内容仍可在端点之间加密。", "example":"先确认手机被授权访问电脑A，再选择A上的研究会话。", "boundary":"逻辑控制面来自公开职责归纳，内部服务划分和撤销传播时机未知；加密不能替代访问授权。", "source":"privacy"},
    {"id":"transport", "title":"加密连接", "term":"直连 / 必要时密文中继", "body":"官方描述设备间直连，必要时中继转发密文；Noise握手，内容密钥保存在设备端。", "mechanism":"工作输入输出通过端点之间的加密通道传递。中继为网络可达性提供另一条路径；官方称中继没有工作内容解密密钥。", "example":"切换“直连 / 中继”，观察同一份输入在不同逻辑路径上送达。", "boundary":"这是路径机制示意，不做NAT测试或握手。Noise具体模式、穿透和浏览器回退未公开。", "source":"home"},
    {"id":"companion", "title":"Companion", "term":"电脑上的接入服务", "body":"Mac/Linux主机运行Companion，将授权连接接入本机终端、文件和支持的桌面资源。", "mechanism":"Linux安装资料列出用户级systemd或supervisor；服务持续接入本机资源，运行身份决定能访问的范围。", "example":"手机里的请求到达你的开发电脑，随后被送入选中的终端。", "boundary":"手机App可以关闭，主机仍要运行。Windows当前可作浏览器控制端，不能据此视为Companion主机。", "source":"install"},
    {"id":"session", "title":"PTY / 会话", "term":"把远程输入送进交互式程序", "body":"PTY承载shell或Agent的双向输入输出；Linux安装说明要求tmux，给会话接续机制提供依据。", "mechanism":"控制端文字/按键写入终端，程序输出返回。持续会话将观察界面与活进程分离；显示状态和Agent历史还需各自恢复。", "example":"手机断线后，电脑会话可能仍在运行；重连先查看状态，再决定是否补发任务。", "boundary":"Mac会话实现、断线输出缓冲未知。手机离开、主机休眠、服务退出和进程结束不能混为一种恢复。", "source":"tmux"},
    {"id":"agent", "title":"Agent 与工具", "term":"实际理解与执行所在层", "body":"Agent收到输入后决定动作，按自己的项目目录、模型配置和权限调用工具，修改文件或运行测试。", "mechanism":"远程入口送达操作，原生Agent产生决策与实际产物。外部模型调用由Agent配置，需独立评价其数据流。", "example":"Agent选择测试工具，电脑执行测试并产生报告；手机随后阅读报告。", "boundary":"远控链路的E2EE不能自动覆盖模型请求；它也不自动提供任务编排、工具权限控制或结果正确性。", "source":"pty"},
    {"id":"notify", "title":"状态与系统推送", "term":"让人及时回来处理和验收", "body":"官网列OSC7501状态报告；APNs/FCM等系统推送可将提醒交付到关闭了App的手机。", "mechanism":"程序报告working/done/blocked/error等状态，必要事件进入通知交付。协议与推送有公开依据，完整内部管道为推导。", "example":"程序报告blocked，用户回到正确会话阅读请求；报告done后仍需核对代码或研究产物。", "boundary":"不是每种终端程序都会准确报告状态。完整适配、去重、通知延迟和敏感内容尚未实测。", "source":"osc"},
]

TRACES = {
    "input": {"label":"输入到执行", "direction":"input", "steps":[
        {"node":"control","title":"01 选对授权设备","text":"先确认访问关系和目标电脑，再选正确终端；尚未执行业务。"},
        {"node":"client","title":"02 人提交输入","text":"手机输入任务或按键；文本由控制端编码为交互事件。"},
        {"node":"transport","title":"03 加密送达","text":"端点通道传递输入；可行时直连，必要时经中继转发密文。"},
        {"node":"companion","title":"04 电脑接入","text":"Companion接收授权连接，将操作路由到本机目标资源。"},
        {"node":"session","title":"05 写入终端","text":"输入到PTY中的交互式程序；程序当前状态决定如何解释按键和确认。"},
        {"node":"agent","title":"06 Agent执行","text":"Agent自行决定工具调用，电脑产生真实成果。此页面只有教学数据。"}]},
    "output": {"label":"结果返回", "direction":"output", "steps":[
        {"node":"agent","title":"01 产物与输出","text":"Agent与工具产生代码、报告、文件和程序输出；任务是否成功仍要验收。"},
        {"node":"session","title":"02 终端承载输出","text":"文字、颜色和光标等控制序列来自终端；文件与桌面另有资源通路。"},
        {"node":"companion","title":"03 目标端桥接","text":"主机接入服务将相应资源数据交付到控制端连接。"},
        {"node":"transport","title":"04 加密回传","text":"直连或中继都应保持端点间工作内容加密；具体实现未独立审计。"},
        {"node":"client","title":"05 显示并核查","text":"控制端渲染输出；用户检查报告、代码与产物，不能只看退出码。"}]},
    "notice": {"label":"状态提醒与接手", "direction":"notice", "steps":[
        {"node":"agent","title":"01 程序报告状态","text":"状态由主动报告或适配产生；done、blocked与error表达不同语义。"},
        {"node":"notify","title":"02 通知交付","text":"必要事件可经系统推送到达手机；完整事件管道是依据公开资料作出的推导。"},
        {"node":"client","title":"03 人回来阅读","text":"手机App可以关闭后再回来；选择正确会话并阅读具体问题。"},
        {"node":"control","title":"04 确认访问与目标","text":"重新连接仍需确认授权和会话身份；提醒本身不授予新的操作权限。"},
        {"node":"agent","title":"05 处理与验收","text":"需要确认时通过交互入口处理；看到done后核对业务目标和实际产物。"}]},
}

def units(text):
    return sum(1 if unicodedata.east_asian_width(c) in "WF" else .56 for c in text)

def wrapped(text, width, font=18):
    lines, line = [], ""
    for token in re.findall(r'[A-Za-z0-9_./+-]+|\s+|.',text):
        if line and units(line+token)*font > width and token not in '，。；：、）】':
            lines.append(line.rstrip()); line = token.lstrip()
        else: line += token
    if line: lines.append(line)
    return lines

def text(x, y, value, cls="ov-text", width=1000, font=18, leading=28):
    return f'<text x="{x}" y="{y}" class="{cls}">' + ''.join(f'<tspan x="{x}" dy="{0 if i==0 else leading}">{escape(line)}</tspan>' for i,line in enumerate(wrapped(value,width,font))) + '</text>'

def box(x,y,w,h,fill="#fffefa",stroke="#cbd6c8",radius=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'

def heading(y,no,title,note):
    return text(56,y,f'{no}  {title}',"ov-heading",font=24)+text(56,y+31,note,"ov-note",font=16)

def make_svg():
    parts = ['''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="2250" viewBox="0 0 1400 2250" role="img" aria-labelledby="overview-title overview-desc">
<title id="overview-title">Vibe42理解总览：远程控制Agent的能力、本质、原理、场景、扩展和意义</title>
<desc id="overview-desc">人从手机或浏览器输入，经授权与加密连接到电脑Companion，再到PTY会话和原生Agent；Agent自行执行工具，输出返回并由人验收。图含七个原理模块、使用条件、建议扩展、产品分工与证据边界。网页原理视图支持点击节点；下载图为静态原创解释。</desc>
<defs><marker id="ov-green-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#356954"/></marker><marker id="ov-gold-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#9b8153"/></marker></defs>
<style>.ov-heading{font-size:24px;font-weight:700}.ov-title{font-size:40px;font-weight:750}.ov-text{font-size:18px}.ov-small{font-size:17px}.ov-note{font-size:16px;fill:#697a6e}.ov-label{font-size:21px;font-weight:650}.ov-white{font-size:20px;fill:#f3f5e8;font-weight:550}.ov-flow{fill:none;stroke:#356954;stroke-width:2.7;marker-end:url(#ov-green-arrow)}.ov-state{fill:none;stroke:#9b8153;stroke-width:2;marker-end:url(#ov-gold-arrow)}.ov-control{fill:none;stroke:#91a396;stroke-width:1.8;stroke-dasharray:6 6}.ov-principle-node rect{transition:stroke .15s}.ov-number{font-size:13px;fill:#708578;letter-spacing:1px}</style>
<rect width="1400" height="2250" fill="#f6f6ee"/><g font-family="Microsoft YaHei,PingFang SC,system-ui,sans-serif" fill="#23473c">''']
    parts += [text(56,55,'010 / VIBE42 · 我们的理解总览 · 2026.10.14','ov-note'),text(56,121,'远程控制 Agent：从手机接手电脑上的工作','ov-title',font=40),text(56,165,'人发出操作，连接送达输入，Agent在原有环境中理解并执行，结果回到人手里。','ov-text')]
    parts += [box(56,196,1288,76,'#254f40','#254f40'),text(80,229,'本质：已有开发环境的远程交互入口','ov-white',font=20),text(80,255,'远控提供操作与观察能力；模型能力、工具执行和业务成功分别属于其他层。','ov-white',font=20)]
    parts += [heading(306,'01','能力：能远程做什么','官方产品说明的能力；完整支持范围与实际行为尚未运行验收。')]
    for i,(title,a,b) in enumerate(CAPABILITIES):
        x=56+i*330
        parts += [box(x,356,298,145),text(x+20,392,title,'ov-label',width=260,font=21),text(x+20,427,a,width=258),text(x+20,466,b,'ov-note',width=258,font=16,leading=24)]
    parts += [text(56,540,'兼容终端程序 ≠ 原生任务接口。多设备 / 团队授权与Mac桌面有公开说明，权限和体验需另验。','ov-note',font=16)]

    parts += [box(28,570,1344,565,'#edf1e5','#cbd6c8'),heading(610,'02','原理：远程交互如何接入真实执行','下面是逻辑职责图。点击网页中的节点可放大、查看机制和逐步追踪；内部组件划分未公开。')]
    parts += ['<g class="ov-principle-node" data-principle="control">',box(319,662,750,58,'#fffefa'),text(340,699,'设备配对 / 授权 / 在线与路由 · 必要元数据','ov-label',width=705,font=21),'</g>']
    parts += ['<path d="M319 690H168V743M946 722V743" class="ov-control"/>']
    nodes = [('client','手机 / 浏览器','人输入与查看','控制端'),('transport','加密连接','直连 / 密文中继','连接路径'),('companion','Companion','持续接入本机资源','电脑服务'),('session','PTY / 会话','程序双向输入输出','Linux要求tmux'),('agent','Agent / 工具','决定动作并实际执行','已有开发环境')]
    for i,(key,title,body,note) in enumerate(nodes):
        x=56+i*263
        parts += [f'<g class="ov-principle-node" data-principle="{key}">',box(x,746,236,150,'#fffefa' if key!='agent' else '#dce8d6'),text(x+17,774,f'{i+1:02} / {note}','ov-number',width=204,font=13),text(x+17,816,title,'ov-label',width=204,font=21),text(x+17,857,body,width=204,font=18),'</g>']
        if i<4: parts += [f'<path data-edge="{key}" d="M{x+239} 825H{x+258}" class="ov-flow"/>']
    parts += ['<path d="M82 919H1320" class="ov-flow" data-trace="input"/>',text(376,907,'输入送达 → Agent依自身配置调用模型与工具','ov-note',font=16),'<path d="M1316 959H82" class="ov-flow" data-trace="output"/>',text(340,947,'← 终端输出 / 文件 / 画面返回；人检查实际成果','ov-note',font=16)]
    parts += ['<g class="ov-principle-node" data-principle="notify">',box(581,994,763,91,'#f4efe1','#d7c9a8'),text(603,1028,'状态报告 → 通知交付 → 手机系统推送','ov-label',width=720,font=21),text(603,1060,'OSC7501、APNs/FCM有依据；完整管道为推导。done仍须验收。','ov-note',width=720,font=16),'</g>','<path d="M1226 899V989" class="ov-state" data-trace="notice"/>']
    parts += [text(56,1021,'手机App关闭可收到提醒；电脑需持续运行。','ov-small',width=494,font=17),text(56,1074,'终端显示、活进程与Agent历史分开恢复。','ov-note',width=494,font=16),text(56,1115,'信任边界：官方称工作内容设备间加密；账号与连接元数据仍存在。Agent模型调用的数据流另看自身配置。','ov-note',width=1280,font=16)]

    parts += [heading(1184,'03','场景：在哪些时候有用','目标是让人及时观察和接手；这些场景需要真实主机、授权、网络与会话条件。')]
    for i,(title,body,boundary) in enumerate(SCENARIOS):
        x=56+(i%2)*658; y=1240+(i//2)*144
        parts += [box(x,y,630,126),text(x+20,y+33,title,'ov-label',width=590,font=21),text(x+20,y+65,body,width=586,font=18,leading=26),text(x+20,y+98,boundary,'ov-note',width=586,font=16,leading=23)]
    parts += [heading(1583,'04','扩展：我们可以在此基础上探索什么','以下为本研究提出的方向；不是Vibe42已发布功能或已完成的复刻。')]
    for i,(title,body) in enumerate(EXTENSIONS):
        x=56+(i%3)*439; y=1638+(i//3)*128
        parts += [box(x,y,410,111,'#f0eee8','#d8d2c7'),text(x+18,y+31,title,'ov-label',width=375,font=21),text(x+18,y+63,body,'ov-small',width=375,font=17,leading=25)]
    parts += [heading(1928,'05','意义：选择合适层次，形成自己的工作流','Vibe42是人的跨设备入口；Agenvo是原生接口桥接；cmux是工作台；WireGuard是网络通道。')]
    for i,(title,body) in enumerate(VALUES):
        x=56+(i%2)*658; y=2000+(i//2)*80
        parts += [text(x,y,title,'ov-label',width=610,font=21),text(x,y+31,body,'ov-small',width=610,font=17,leading=24)]
    parts += ['<path d="M56 2150H1344" stroke="#cbd6c8"/>',text(56,2181,'来源：Vibe42官网、安装与隐私资料；PTY、tmux、Noise、OSC7501；已有Agenvo、cmux和WireGuard研究。','ov-note',width=1288,font=16),text(56,2221,'证据边界：原创解释图，非产品截图；未取得核心源码，未安装配对、抓包或测性能。0.11.0仅为下载版本观察。','ov-note',width=1288,font=16),'</g></svg>']
    return '\n'.join(parts)

def build():
    svg=make_svg()
    for folder in [PROJECT/'assets',PROJECT/'web'/'assets']:
        folder.mkdir(parents=True,exist_ok=True)
        (folder/'understanding-overview.svg').write_text(svg,encoding='utf-8',newline='\n')
    return svg

def inline_svg():
    svg=build().replace('role="img"','role="group"',1).replace('<svg xmlns=', '<svg id="understanding-map" class="understanding-svg" xmlns=',1)
    for item in PRINCIPLES:
        before=f'<g class="ov-principle-node" data-principle="{item["id"]}">'
        after=before[:-1]+f' role="button" tabindex="0" aria-pressed="false" aria-label="查看{escape(item["title"])}的原理说明">'
        svg=svg.replace(before,after)
    return svg

def render_section():
    first=PRINCIPLES[0]
    digest=''.join(f'<div><dt>{escape(label)}</dt><dd>{escape(body)}</dd></div>' for label,body in digest_items())
    return f'''<section id="understanding" class="research-section understanding-section"><div class="section-heading"><span class="section-no">00</span><div><h2>一张图，理解远程控制 Agent</h2><p class="section-intro">从能力与本质，看到输入怎样送达电脑、谁负责执行，以及场景、扩展和实际意义。</p></div></div>
<dl class="understanding-thesis" aria-label="能力、原理、价值与扩展场景摘要">{digest}</dl>
<div class="map-toolbar"><div class="map-view-buttons" aria-label="选择理解图视图"><button type="button" data-map-view="full" aria-pressed="true">完整理解图</button><button type="button" data-map-view="principle" aria-pressed="false">原理放大 · 可点击</button></div><a href="./assets/understanding-overview.svg" download="vibe42-understanding-overview.svg">下载SVG ↓</a><a href="./assets/understanding-overview.png" download="vibe42-understanding-overview.png">下载PNG ↓</a></div>
<figure class="understanding-figure" data-view="full"><div class="understanding-canvas">{inline_svg()}</div><img class="overview-print-image" src="./assets/understanding-overview.svg" alt="完整理解总览：能力、本质、原理、场景、扩展和意义"><figcaption id="map-caption">原创理解总览，2026-10-14。点击原理节点或选择“原理放大”，进入同一底图的交互讲解。下载图为静态版本。</figcaption></figure>
<div id="principle-explorer" class="principle-explorer" hidden><div class="principle-controls"><div class="trace-buttons" aria-label="选择教学数据路径"><button type="button" data-principle-trace="input" aria-pressed="true">输入到执行</button><button type="button" data-principle-trace="output" aria-pressed="false">结果返回</button><button type="button" data-principle-trace="notice" aria-pressed="false">状态提醒与接手</button></div><div class="map-route-buttons" aria-label="选择教学连接路径"><button type="button" data-map-route="direct" aria-pressed="true">直连</button><button type="button" data-map-route="relay" aria-pressed="false">密文中继</button></div></div>
<div class="trace-stage" aria-live="polite"><div><span id="principle-step-count" class="overline">输入到执行 · 01 / 06</span><h3 id="principle-step-title">01 选对授权设备</h3><p id="principle-step-text">先确认访问关系和目标电脑，再选正确终端；尚未执行业务。</p></div><div class="trace-arrows"><button type="button" id="principle-prev" disabled>← 上一步</button><button type="button" id="principle-next">下一步 →</button></div></div>
<article id="principle-detail" class="principle-detail" aria-live="polite"><div><span id="principle-term" class="overline">{escape(first['term'])}</span><h3 id="principle-title">{escape(first['title'])}</h3><p id="principle-body">{escape(first['body'])}</p></div><dl><div><dt>怎么工作</dt><dd id="principle-mechanism">{escape(first['mechanism'])}</dd></div><div><dt>具体例子</dt><dd id="principle-example">{escape(first['example'])}</dd></div><div><dt>证据与边界</dt><dd id="principle-boundary">{escape(first['boundary'])}</dd></div></dl></article>
<p id="map-route-note" class="small-note" aria-live="polite">当前示意为直连。实际路径由网络条件与产品实现决定；没有发起真实连接。</p><p class="small-note">构造的教学路径，不执行命令或连接Agent。手机视图可横向滑动原理图；点击节点后文字说明在下方。</p></div>
<noscript><p class="small-note">完整总览和正文可阅读。启用JavaScript后可放大原理、点击节点与逐步追踪。</p></noscript>
<div class="citations"><span>依据</span><a href="https://vibe42.ai/" target="_blank" rel="noopener">Vibe42官网 ↗</a> · <a href="https://vibe42.ai/install.md" target="_blank" rel="noopener">安装说明 ↗</a> · <a href="https://vibe42.ai/privacy" target="_blank" rel="noopener">隐私说明 ↗</a> · <a href="#implementation">扩展与实现路线 ↓</a> · <a href="#comparison">完整产品对比 ↓</a></div></section>'''

def markdown():
    lines=['## 0. 一张图总结我们的理解','',
        '![Vibe42原创理解总览：远程控制Agent的能力、本质、原理、场景、扩展、意义和证据边界](./assets/understanding-overview.svg)','',
        '图片说明：本研究原创，2026-10-14，非产品截图。网页使用同一SVG底图，可放大原理、点击7个节点、追踪3条路径和切换直连/中继；下载图为静态解释图。','',
        *[line for label,body in digest_items() for line in ['**'+label+'：** '+body,'']],
        '[下载PNG](./assets/understanding-overview.png) · [原理交互网页](./web/index.html#understanding) · [详细三端架构图](./assets/architecture.svg)','']
    for title,items in [('使用场景',SCENARIOS),('可扩展方向（本研究建议）',EXTENSIONS),('意义与成立条件',VALUES)]:
        lines += ['### '+title,'']
        lines += ['- **'+item[0]+'：** '+' '.join(item[1:]) for item in items]
        lines += ['']
    lines += ['这些内容来自既有公开资料研究与明确标注的工程建议。图中的逻辑组件不代表内部源码目录；原产品安装、连接、恢复、安全、通知和性能尚未独立验证。','']
    return '\n'.join(lines)

def data():
    return {'principles':PRINCIPLES,'traces':TRACES,'essence':ESSENCE,'scenarios':SCENARIOS,'extensions':EXTENSIONS,'values':VALUES}

if __name__=='__main__':
    build()
    print('Built original 1400x2250 overview SVG; 7 principle nodes, 3 teaching paths.')
