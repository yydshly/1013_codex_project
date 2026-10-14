"""Draw original vector explanations; PNGs are rendered from these SVGs."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INK, MUTED, GREEN, LIME, CORAL = '#173d38', '#607465', '#173d38', '#dcebbb', '#bf5337'


class Drawing:
    def __init__(self, height, title, description):
        self.height = height
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="{height}" viewBox="0 0 1600 {height}" role="img" aria-labelledby="title desc">',
                      f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
                      '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="none" stroke="context-stroke" stroke-width="1.5"/></marker></defs>',
                      f'<rect width="1600" height="{height}" fill="#f7f6f0"/>']

    def text(self, x, y, value, size=22, color=INK, weight=400):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="Microsoft YaHei,Segoe UI,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(value)}</text>')

    def rect(self, x, y, width, height, fill='#fffef9', stroke='#d5ddd5', radius=12):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>')

    def arrow(self, x1, y1, x2, y2, color='#82967a'):
        self.parts.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="2.5" marker-end="url(#arrow)"/>')

    def lines(self, x, y, values, size=22, gap=35, color=MUTED):
        for i, value in enumerate(values):
            self.text(x, y + i * gap, value, size, color)

    def card(self, x, y, width, height, kicker, title, lines, fill='#fffef9', dark=False):
        self.rect(x, y, width, height, fill, fill if dark else '#cbd5c5')
        color = '#eff5e4' if dark else INK
        self.text(x + 25, y + 35, kicker, 16, '#bdd0b5' if dark else MUTED)
        self.text(x + 25, y + 81, title, 28, color, 600)
        self.lines(x + 25, y + 125, lines, 22, 35, '#d0dfc7' if dark else MUTED)

    def save(self, name):
        content = '\n'.join(self.parts + ['</svg>']) + '\n'
        for folder in (ROOT / 'assets', ROOT / 'web/assets'):
            folder.mkdir(parents=True, exist_ok=True)
            (folder / name).write_text(content, encoding='utf-8', newline='\n')


def overview():
    d = Drawing(2460, 'Free Claude Code：适配解耦完整理解总览', '在 Agent 和真实模型之间增加模型网关，用统一接口、协议适配和配置路由降低接入耦合。包含三方职责、底层模块、工具闭环、能力、场景、价值、意义、扩展、同类定位与验证边界。')
    d.text(70, 68, '016 / FREE CLAUDE CODE / 我们的完整理解', 19, MUTED)
    d.text(70, 146, 'Agent 与真实模型之间，加一个网关。', 56, INK, 650)
    d.text(70, 207, '接口适配实现解耦，工作方式与模型服务分别选择。', 34, CORAL, 550)
    d.lines(70, 259, ['统一代理地址是入口；消息、工具和响应适配是机制；模型可替换是核心价值。'], 23)
    d.rect(70, 300, 1460, 78, '#e5ecd9')
    for x, title, detail in [(95, '能力', '统一接入与调用'), (462, '原理', '适配与转发'), (825, '价值', '降低接口依赖'), (1178, '边界', '质量仍需验收')]:
        d.text(x, 330, title, 17, MUTED)
        d.text(x, 359, detail, 23, INK, 550)

    d.card(70, 425, 430, 235, '01 / AGENT 执行框架', '组织任务，执行工具', ['上下文 · 工具定义 · 执行权限', '读写文件 · 命令 · 结果验收'], '#edf0e4')
    d.card(585, 425, 430, 235, '02 / FCC 模型网关', '统一入口，适配与路由', ['模型配置 · 协议与事件转换', '真实调用 · 重试与有序备用'], GREEN, True)
    d.card(1100, 425, 430, 235, '03 / 真实模型服务', '理解、生成与调用决策', ['供应商云端 / 本地推理服务', '能力、上下文与输出行为各异'], '#f0e4d3')
    for a, b in [(512, 571), (1027, 1087)]:
        d.arrow(a, 510, b, 510, CORAL)
        d.arrow(b, 586, a, 586)
    d.text(515, 487, '请求', 16, CORAL)
    d.text(1030, 487, '调用', 16, CORAL)
    d.text(515, 620, '响应', 16, MUTED)
    d.text(1030, 620, '输出', 16, MUTED)
    d.text(70, 706, '解耦的是客户端与具体服务的接口依赖；模型能力差异仍然存在。', 25, INK, 550)

    d.rect(70, 750, 1460, 402, '#e9eee2')
    d.text(100, 792, '把网关展开：一条模型请求经过哪些模块？', 28, INK, 600)
    stages = [('01 / 入口', '接收与校验', ['Messages / Responses', '任务、上下文与工具定义']),
              ('02 / 路由', '按配置确定目标', ['直接模型 / 档位映射', '主模型与有序备用列表']),
              ('03 / 适配', '转换双方格式', ['消息、工具、图像与推理', '兼容协议可走原生路径']),
              ('04 / 出口', '调用真实服务', ['服务 URL、凭据与模型 ID', '请求、流式事件与错误'])]
    for i, (kicker, title, lines) in enumerate(stages):
        x = 100 + 365 * i
        d.card(x, 835, 335, 190, kicker, title, lines)
        if i < 3:
            d.arrow(x + 343, 920, x + 357, 920, CORAL)
    d.arrow(1490, 1067, 113, 1067)
    d.text(310, 1107, '返回方向：真实模型输出 → 转为客户端格式 → Agent 继续工作', 22)

    d.rect(70, 1200, 1460, 153, GREEN, GREEN)
    d.text(100, 1241, '工具闭环：模型给指令，Agent 负责实际操作', 28, '#eff5e4', 600)
    d.lines(100, 1288, ['模型提出工具调用 → FCC 转换事件 → Agent 按权限执行 → 结果再经网关交给模型',
                         '例如 Claude Code → FCC → DeepSeek：保留工具框架，由 DeepSeek 提供生成能力。'], 22, 35, '#caddc3')

    d.text(70, 1430, '能力、场景、价值与意义：为什么值得研究？', 32, INK, 600)
    d.card(70, 1470, 710, 280, '已有支持 / 效果需实测', '能力', ['统一模型配置与目录 · 自定义服务', '消息、工具、响应和流式事件适配', '档位映射 · 重试与备用 · 辅助请求优化', '浏览器、IDE、消息入口各有运行条件'])
    d.card(820, 1470, 710, 280, '使用场景 / 接口需兼容', '场景', ['保持 Agent 工作方式，经常切换模型', '同任务模型比较 · 本地推理 · 故障备选', '写作、SEO、RAG 的生成环节接入', '浏览器或手机入口需执行环境持续运行'])
    d.card(70, 1790, 710, 280, '对我们的价值 / 用真实任务验收', '价值与意义', ['降低重复接入、迁移和配置的工作', 'Agent 工作方式与模型服务分别选择', '理解执行、接口与模型的职责分工', '积累完成率、返工、耗时和真实费用'])
    d.card(820, 1790, 710, 280, '已有自定义接口 / 其他方向需建设', '可扩展方向', ['先配置自己的 API 或本地模型服务', '任务语义路由 · 能力与预算约束', '知识库工具 · 用量和评测记录', '团队权限 · 兼容回归 · 产物验收'])

    d.rect(70, 2110, 1460, 138, '#e5ecd9')
    d.text(97, 2148, '与以前项目的关系', 25, INK, 600)
    d.lines(97, 2186, ['FCC / FreeLLMAPI：模型网关；Jev：任务判断与选择策略。',
                       'Agenvo：原生 Agent 接入；cmux / Vibe42：会话工作台与远程操作。'], 23)
    d.lines(70, 2305, ['适配不会训练模型；免费来自供应商额度或本地方案；单模型直连已够用时，新增层收益可能有限。',
                       '真实调用、工具质量、恢复效果和任务总成本待实测。图为原创研究解释，非运行截图。'], 20, 34)
    d.text(70, 2410, '固定源码 74d4ccf · AGPL-3.0-only · 2026-10-14 · 来源：Alishahryar1/free-claude-code 与既有固定版本研究', 17, MUTED)
    d.save('understanding-overview.svg')


def internals():
    d = Drawing(1320, 'FCC 模型网关底层：请求适配与工具闭环', 'Agent 使用稳定入口；FCC 入口校验、配置路由、协议适配和供应商调用连接真实模型，返回响应并继续本机工具循环。')
    d.text(70, 66, '016 / 底层模块解释 / 概念数据流', 18, MUTED)
    d.text(70, 143, '适配解耦，究竟发生在哪一层？', 52, INK, 650)
    d.text(70, 198, 'Agent 发模型请求；FCC 加载连接配置和适配逻辑；真实服务运行模型。', 24, MUTED)
    d.card(70, 246, 400, 210, '客户端侧 / 稳定入口', 'Agent 执行框架', ['任务、上下文与工具说明', '按自己的权限执行工具'], '#edf0e4')
    d.card(600, 246, 400, 210, '中间层 / 可配置目标', 'FCC 模型网关', ['代理 URL 与协议适配', '工作方式与模型服务解耦'], GREEN, True)
    d.card(1130, 246, 400, 210, '服务侧 / 真实生成', '云端或本地模型', ['模型 ID 与推理服务', '生成文本和工具调用'], '#f0e4d3')
    d.arrow(482, 325, 585, 325, CORAL)
    d.arrow(1012, 325, 1115, 325, CORAL)
    d.arrow(1115, 397, 1012, 397)
    d.arrow(585, 397, 482, 397)
    d.text(493, 304, '请求', 18, CORAL)
    d.text(1022, 304, '真实 API', 18, CORAL)
    d.text(493, 435, '响应', 18, MUTED)
    d.text(1022, 435, '输出', 18, MUTED)
    d.text(70, 520, '网关内部的概念模块', 30, INK, 600)
    modules = [('① 接收与校验', ['Messages / Responses', '参数、请求与鉴权', '客户端入口和目录']),
               ('② 模型路由', ['指定模型或档位映射', '真实服务、模型与密钥', '按配置形成备用顺序']),
               ('③ 协议适配', ['消息与工具结构转换', '图像、推理与流式字段', '原生路径 / 不支持项']),
               ('④ 供应商调用', ['实际 Base URL 与凭据', 'HTTP 请求 / SSE 响应', '错误、重试及恢复条件'])]
    for i, (title, lines) in enumerate(modules):
        x = 70 + 375 * i
        d.rect(x, 557, 335, 214, '#fffef9')
        d.text(x + 20, 603, title, 25, INK, 600)
        d.lines(x + 20, 651, lines, 21, 35)
        if i < 3:
            d.arrow(x + 344, 665, x + 365, 665, CORAL)
    d.rect(70, 816, 710, 165, '#e9eee2')
    d.rect(820, 816, 710, 165, '#e9eee2')
    d.text(95, 857, '工具结构示例：连接两种表达方式', 25, INK, 600)
    d.lines(95, 901, ['Messages：tool_use / tool_result', 'Chat：tool_calls / tool 消息'], 22, 37)
    d.text(845, 857, '响应与历史：保持调用关系', 25, INK, 600)
    d.lines(845, 901, ['调用标识、参数和结果要相互对应', '流式事件映射；无法表达的内容有限制'], 22, 37)
    d.rect(70, 1020, 1460, 144, GREEN, GREEN)
    d.text(100, 1060, '回到 Agent 的实际工具环境', 28, '#eff5e4', 600)
    d.lines(100, 1106, ['真实模型提出调用 → FCC 转回客户端事件 → Agent 执行 → 工具结果再次进入模型请求',
                         '代理转发与模型推理是两层；文件、命令与业务操作仍由 Agent 的工具环境负责。'], 22, 35, '#caddc3')
    d.lines(70, 1222, ['此图按职责解释机制，不是逐函数调用图；原生透传、优化与错误路径可能绕过部分转换。',
                       '依据：harnesses/claude.py · api/routes.py · application/routing.py · conversion.py · provider 层'], 19, 33)
    d.text(70, 1295, '源码版本 74d4ccf · 2026-10-14 · 原创解释图，非真实模型日志或上游运行截图', 17, MUTED)
    d.save('gateway-internals.svg')


if __name__ == '__main__':
    overview()
    internals()
    print('Created complete understanding and gateway internals SVGs in assets/ and web/assets/.')
