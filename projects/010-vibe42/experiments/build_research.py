"""Build original research prose and a static reading page; no Vibe42 connection."""
from pathlib import Path
import html
import json
import build_overview as overview

PROJECT = Path(__file__).resolve().parents[1]
WEB = PROJECT / "web"
DATE = "2026-10-14"
METADATA = json.loads((PROJECT/"project.json").read_text(encoding="utf-8"))
DEMO_URL = METADATA.get("demo_url", "")
SOURCES = [
    ("home", "Vibe42 官网", "https://vibe42.ai/", "产品定位、Ghostty、直连/中继、Noise 与状态协议；属于官方说明。"),
    ("install", "官方安装与故障排查说明", "https://vibe42.ai/install.md", "Companion、Mac/Linux 条件、tmux、systemd/supervisor、设备配对、权限与网络排查。"),
    ("bootstrap", "官方安装入口脚本", "https://get.vibe42.app/install.sh", "只读检查下载、安装入口、用户 shell 文件和 PATH；未执行安装。"),
    ("privacy", "Vibe42 隐私政策", "https://vibe42.ai/privacy", "工作内容、设备密钥、账号与连接元数据、授权和推送令牌的边界。"),
    ("meta", "官方客户端下载元数据", "https://vibe42.ai/downloads/api/meta", "本次响应标注 macOS/iOS/Android 0.11.0；没有安装或验证其发布包。"),
    ("github", "Vibe42 官方 GitHub 组织", "https://github.com/vibe42-ai", "本次查看没有公开仓库；不能据此确认内部源码、全部依赖或开源许可证。"),
    ("store", "Google Play 开发者应用说明", "https://play.google.com/store/apps/details?id=ai.vibecafe.x", "完整 PTY、文件浏览/编辑、会话接续与设备授权的产品声明。"),
    ("pty", "Linux PTY 手册", "https://man7.org/linux/man-pages/man7/pty.7.html", "伪终端两端、双向输入输出、控制字符与前台进程组。"),
    ("tmux", "tmux 官方仓库", "https://github.com/tmux/tmux", "终端复用、分离后持续运行与重新附着；是机制说明，不是 Vibe42 内部源码。"),
    ("noise", "Noise Protocol Framework", "https://noiseprotocol.org/noise.html", "握手、公钥协商与加密传输；具体模式和算法组合需另行确认。"),
    ("osc", "OSC 7501 Program Status Protocol", "https://www.superlogical.com/rex/docs/build/program-status", "idle/working/done/blocked/error、用户介入类型与上报语义。"),
    ("kitty", "Kitty 图片协议", "https://sw.kovidgoyal.net/kitty/graphics-protocol/", "终端图片传送与显示的协议机制。"),
    ("agenvo", "Agenvo 固定版本架构", "https://github.com/Xuanwo/agenvo/blob/68e046a5d8691054f8c134d85ae051988bae3dff/design/architecture.zh-CN.md", "对应以前研究的 68e046a：Relay、Connector、Adapter 与原生运行时。"),
    ("agenvo-security", "Agenvo 固定版本安全说明", "https://github.com/Xuanwo/agenvo/blob/68e046a5d8691054f8c134d85ae051988bae3dff/SECURITY.zh-CN.md", "自托管边界、Relay 的内容可见性与原生权限。"),
    ("cmux", "cmux 固定版本 README", "https://github.com/manaflow-ai/cmux/blob/cdbe99596fe13784ec5ea24d2e1c720a8f67f5cb/README.md", "工作区、终端、浏览器与 Agent 控制；本次补充对比。"),
    ("cmux-mobile", "cmux 官方移动入口", "https://cmux.com/", "本次官网提供 iOS/iPadOS companion beta，不能把 cmux 简化成纯本地工具。"),
    ("cmux-tmux", "cmux local-tmux 说明", "https://github.com/manaflow-ai/cmux/blob/cdbe99596fe13784ec5ea24d2e1c720a8f67f5cb/docs/local-tmux.md", "UI 恢复、tmux 活进程与原生 Agent session 的不同生命周期。"),
    ("cmux-transport", "cmux 移动传输架构文档", "https://github.com/manaflow-ai/cmux/blob/cdbe99596fe13784ec5ea24d2e1c720a8f67f5cb/docs/iroh-app-transport-architecture.md", "文档说明 Iroh/QUIC、端点身份与账户配对；未进行运行验证。"),
    ("cmux-license", "cmux 根许可证", "https://github.com/manaflow-ai/cmux/blob/cdbe99596fe13784ec5ea24d2e1c720a8f67f5cb/LICENSE", "主体 GPL-3.0-or-later；列出的服务器目录另受 BUSL-1.1 条件约束。"),
    ("wireguard", "WireGuard 官方协议", "https://www.wireguard.com/protocol/", "IP 包的认证、握手、UDP 加密封装；不提供 Agent 业务界面。"),
    ("wg-install", "WireGuard Install 固定脚本", "https://github.com/hwdsl2/wireguard-install/blob/3f428774e61c95bca60d1e7b80f0c768ca2c6137/wireguard-install.sh", "以前研究的部署、peer 配置、转发、NAT 和防火墙。"),
]
SOURCE_MAP = {s[0]: s for s in SOURCES}

CHAPTERS = [
 {"id":"essence", "title":"本质：执行留在电脑，操作跨越设备", "intro":"Vibe42 提供的是已有开发环境的远程入口。理解它，先把人、连接服务、终端和 Agent 的职责分开。", "paragraphs":[
 "人通过控制端表达意图或输入操作；电脑里的 Agent 按自己的能力处理请求、修改文件、调用开发工具。Vibe42 将两端的交互送达并显示回来。编程能力来自被连接的 Agent，远程接入能力来自 Vibe42。",
 "你前面说的“在运行 Agent 的电脑装一个客户端，再由手机通过适配器交互”，整体连接关系成立。精确术语是：手机/浏览器是控制客户端，电脑上的 Companion 是接入服务。这里的桥接主要围绕通用终端和桌面，不需要先假定存在针对每一种 Agent 的原生 API Adapter。",
 "从工程角度，本产品把远程终端、设备身份、连接协调、会话接续、移动端输入与渲染、状态通知、文件和桌面能力组织成一个跨设备工作流。每个环节可用成熟机制实现，产品价值来自这些环节在真实网络和设备上能否稳定配合。",
 "本次官网 GitHub 组织未列出公开仓库。因此这里收录的是产品公开资料研究：能确认安装与使用机制，能解释标准协议的工作方式；对内部模块划分、穿透算法、视频编码和恢复实现，只给出带依据的推导或待查问题。"], "table":(["对象","主要职责","工作在哪里发生"],[
 ["你与控制端","文字、按键、审批操作、阅读输出","手机、平板或浏览器"],["Companion","接入电脑资源并保持可连接","目标 Mac / Linux"],["终端与会话","承载 shell、程序输入输出和存活进程","目标电脑；Linux 文档要求 tmux"],["编程 Agent","理解任务、决定动作、执行工具","已有 Agent 环境；模型调用取决于其配置"],["平台控制与中继","设备授权、连接路由、必要时转发密文","Vibe42 基础设施"]]), "refs":["home","install","github"]},
 {"id":"capabilities", "title":"能力地图：输入、输出与适用范围", "intro":"把“能连接任何 Agent”拆成可观察的能力，避免把终端兼容、任务语义和自动化能力混在一起。", "table":(["能力","你提供什么","得到什么","公开边界"],[
 ["远程终端","文字、快捷键、终端操作","程序输出与交互界面","开发者说明完整 PTY；内部协议未公开"],
 ["接着原有工作","选择电脑与终端会话","继续查看或操作正在运行的程序","断开手机与退出电脑进程要分别考虑"],
 ["文件与产物","浏览、预览、编辑、传输操作","电脑上的文件与工作结果","没有核对所有文件类型、大小上限和冲突策略"],
 ["Mac 远程桌面","触摸、鼠标、键盘操作","桌面画面与远端输入反馈","安装说明要求屏幕录制/辅助功能权限；Linux桌面未确认"],
 ["多设备与多电脑","设备配对、工作机选择","跨设备工作入口","配额、套餐和正式可用范围以控制台为准"],
 ["任务状态与通知","程序报告状态或相应适配","工作完成/需要介入的提醒","官网列 OSC 7501、APNs/FCM；完整适配矩阵未公开"],
 ["移动端终端体验","触屏输入、中日韩文本、图片内容","字体、光标、控制序列与图片显示","官网列 Ghostty、GPU 和 Kitty；性能指标未实测"],
 ["团队共享","成员身份、角色与电脑授权","团队访问和共享入口","产品列角色能力；真实权限粒度未测试"]]), "paragraphs":[
 "通用终端首先解决“这个程序能够被显示和操作”。结构化创建任务、读取原生历史、按 turn 精确中断、自动回答审批等能力，还取决于 Agent 自身接口及上层集成。产品的广泛终端兼容性不能单独证明这些语义能力。",
 "平台分工要看方向：Mac 和 Linux 可以作为被控制的电脑；iOS、Android 和浏览器是操作入口。官方安装说明明确 Windows 当前不能运行 Companion，但 Windows 浏览器可以控制已有的其他电脑。本研究机就是 Windows，尚未具备真实主机端复现条件。"], "refs":["store","home","install"]},
 {"id":"architecture", "title":"架构：控制端、平台、执行端各管什么", "intro":"这是根据公开材料绘制的逻辑架构。模块名称用于解释职责，不代表已经看到了内部仓库的目录或类。", "paragraphs":[
 "控制端将人的输入编码成可传输事件，并把收到的终端数据或桌面画面呈现出来。平台控制面负责账号、设备、授权、在线状态和连接路由。执行端 Companion 接入本机终端与资源，Agent 则继续使用本机工具链和文件。",
 "将控制面与数据面分开，有助于理解隐私：登录、配对、授权、在线状态属于控制信息；终端内容、文件和桌面画面属于工作数据。官方称工作数据在设备之间端到端加密；控制平台仍然需要一些账号和连接元数据。",
 "将会话管理与渲染分开，有助于理解连续性：手机屏幕上显示的内容可以被关闭；电脑上的会话进程可以仍然运行。之后重新连接，需要重新附着或恢复观察，是否补齐断线期间的输出以及怎样处理屏幕尺寸变化，属于需要进一步验证的实现细节。"], "table":(["逻辑模块","公开依据","内部仍未确认"],[
 ["移动/Web控制端","官方客户端和应用说明","平台代码语言、框架、跨端共享比例"],["账号/设备控制面","隐私政策中的配对、角色、presence和连接记录","数据库结构、API、授权撤销传播时机"],["连接与中继层","直连优先、加密中继、排查出站HTTPS/QUIC","打洞策略、路径选择、流复用、浏览器回退"],["电脑Companion","安装文档与入口脚本","核心源码、资源隔离、事件和会话持久化"],["PTY/会话层","应用列PTY；Linux要求tmux","Mac实现、tmux调用方式、断线输出缓冲"],["终端渲染层","官网列Ghostty和Kitty","确切集成API、协议覆盖、移动性能"],["文件/桌面桥接","产品说明与Mac权限要求","传输冲突策略、画面采集和编解码实现"]]), "refs":["install","privacy","home"]},
 {"id":"lifecycle", "title":"一次操作的完整路径", "intro":"以“从手机让电脑里的 Agent 运行测试”为例，逐层看输入、执行和结果属于谁。页面中的步骤和终端输出均为教学构造。", "paragraphs":[
 "先安装与授权目标电脑，让控制端确认它是允许访问的设备；再选择正确会话。连接建立后，输入经过认证和加密到达目标端，写入终端。终端中的 Agent 读到请求后，才决定怎样运行测试。结果经终端输出返回，手机负责显示。",
 "需要确认时，你从手机输入同意或其他内容，通常与在本机终端操作相似。若底层是通用终端，传入的按键、文字和程序当前界面共同决定实际效果；结构化审批ID、请求关联和幂等执行需要专门协议支持。",
 "连接恢复时应先查看当前状态，再决定要不要再次发送操作。例如第一次测试已经开始，只是结果尚未传回，盲目重发可能创建第二次运行。相同问题也存在于发布、提交、删除或支付等写操作，因此可靠恢复不仅是让网络重新连上。"], "refs":["pty","install"]},
 {"id":"terminals", "title":"终端与会话：输入输出、存活与恢复", "intro":"PTY、tmux、终端渲染和 Agent 历史是不同层次，分别解决不同问题。", "paragraphs":[
 "PTY 提供一对双向通道。一端由接入程序读写，另一端表现为真实终端，供 shell 与交互式程序使用。输入可包含普通文字和控制字符；输出可包含文字、颜色、光标移动、清屏和其他控制序列。控制端需要解析并呈现这些序列，而不只是显示一串文本。",
 "因此，终端通道可以承载测试程序、git、shell 脚本和多种编程 Agent。图像还可以通过终端图片协议传输。通道的通用性是广泛兼容的基础，但对终端控制序列的覆盖、中文输入法、粘贴、组合键、窗口尺寸同步仍需逐项测试。",
 "Linux 安装说明要求 tmux。tmux 能让会话在观察界面分离后继续运行，再由新观察者附着。这为接续机制提供直接依据，但尚不能据此断言 Vibe42 的全部终端都用相同方式管理，或 Mac 的会话实现与 Linux 一样。",
 "持久化至少有三种含义：活进程继续存在，关闭界面后能继续运行；显示状态恢复，重开应用后能恢复标签、目录和滚动记录；Agent 原生历史续接，用其会话ID恢复任务上下文。它们需要不同的数据和生命周期管理，电脑重启尤其不能由“断线会话存活”直接覆盖。"], "table":(["事件","执行端通常会怎样","重新连接后要确认什么"],[
 ["手机App关闭/手机短暂断网","电脑仍运行时，会话可持续；这是产品声明","是否恢复到同一会话、输出是否完整"],["切换Wi-Fi与蜂窝网络","需要恢复认证通道或切换路径","输入是否重复、丢失，终端尺寸是否改变"],["电脑屏幕锁定","与机器休眠不同；官网展示Mac远程解锁","权限、画面与系统策略；未实测"],["电脑进入休眠","计算和网络连接可能暂停，属于系统机制推导","唤醒后服务、会话和连接能否恢复"],["Companion退出","远程入口中断；独立会话能否存活依实现","服务重启后的会话重新发现"],["Agent退出/机器重启","活进程已经结束或消失","原生历史续接、检查点或重新启动策略"]]), "refs":["pty","tmux","kitty","store"]},
 {"id":"network", "title":"网络：连接建立、直连和中继", "intro":"“免配置”是用户体验目标；背后仍需要身份、授权、路由和可用传输路径。", "paragraphs":[
 "公开材料确认存在设备配对、连接路由、直接设备通信与中继路径。安装排查要求关注目标机的出站 HTTPS/QUIC 访问。这些足以说明平台封装了连接基础设施，但尚不足以确认其完整 NAT 穿透算法、端口策略或每个平台的具体传输栈。",
 "从可实现的系统设计推导，控制平台通常保存设备身份和可连接状态，协调两端尝试建立连接。直连可减少中转；在网络不允许直连时，让两端分别到达可用中继，由中继转发消息。这里的“通常”是方案解释，不是 Vibe42 核心源码结论。",
 "无论通过哪条路径，都需要处理重连、超时、流量控制和网络变化。快速恢复终端输出、避免无意重放输入、保护桌面交互延迟，是产品工程的实际难点。全球节点、120Hz 或毫秒重连等宣称不能代替在真实网络上测量的延迟、吞吐和耗电。"], "table":(["路径","数据经过哪里","可观察优势与代价"],[
 ["直连","控制端 ↔ 目标电脑","减少中转；可行性取决于两端网络"],["中继","控制端 ↔ relay ↔ 目标电脑","增加网络可达性；带宽、延迟和运营资源受中继影响"],["控制面","设备 ↔ 账号/授权/连接平台","管理在线与授权；需要元数据，不能视为完全离线系统"]]), "refs":["home","install","privacy"]},
 {"id":"security", "title":"安全边界：内容密文与连接元数据", "intro":"把登录认证、设备授权、工作内容加密和执行权限分开理解，才能准确评价“端到端加密”。", "paragraphs":[
 "官网明确使用 Noise 握手，并称密钥留在设备端。Noise 是可实例化为不同模式与算法组合的密码协议框架：握手通过公钥相关运算建立秘密，再使用派生密钥保护传输内容。这个框架说明如何建立加密通道；具体模式、算法组合和密钥轮换仍需产品源码或技术说明确认。",
 "按官方隐私声明，终端、文件和屏幕内容不在其服务器留存，中继不能解密工作数据。与此同时，平台记录账号、设备、授权、在线状态和连接元数据，以及通知/计费所需记录。工作内容不留存与运营数据留存可以同时成立。",
 "设备配对建立“谁可以访问谁”的关系；加密建立“路径上的中转方能否读取内容”的边界；电脑上的进程权限决定“已经连接的人或程序可以做什么”。三者不能互相替代。端点上已经可见的明文、执行环境的权限和 Agent 调用的工具，仍应按本机运行时检查。",
 "Agent 若调用外部模型，代码或上下文可能按 Agent 自身配置发送到模型服务商。本产品远程链路的保护范围应单独评价，不能据此推出整个开发流程没有外部模型请求。",
 "本次没有实施网络抓包、密钥验证、撤销测试或安全审计，所以能记录官方设计声明及其合理含义，尚不能给出“已经独立证明”的安全结论。"], "refs":["noise","privacy","home"]},
 {"id":"notifications", "title":"通知：状态来自哪里，手机为什么可以关闭", "intro":"状态报告与消息推送是两段不同的流程。状态由程序或适配产生，推送由系统通知通道交付。", "paragraphs":[
 "官网列出 OSC 7501。这个协议让终端程序报告 idle、working、done、blocked、error 等状态；blocked 可以携带 permission、question 或 auth 等介入类型。协议表达状态，并不规定产品必须怎样弹出通知。",
 "由此可以设计：电脑端观察状态变化，将必要事件交给通知服务；服务通过 APNs 或 FCM 通知手机。平台隐私政策确认保存推送令牌及必要通知记录。因为通知通过操作系统的渠道交付，手机客户端无需一直维持自己的前台网络连接。完整内部事件管道仍未公开。",
 "通用终端中的任意程序都可以显示，但准确报告“需要审批”“正在执行某个阶段”，需要程序主动上报或可靠适配。还要分别处理重复事件、通知限频、已在当前会话中阅读的结果，以及状态恢复。官网没有公开所有 Agent 的适配与通知准确率。",
 "done 表示程序报告了一项工作完成，error 表示程序报告失败。无论来自 OSC 还是原生接口，任务状态都应配合产物和验证结果判断：进程退出成功、Agent停止输出与用户目标真正达成都属于不同证据。"], "table":(["状态","含义","用户通常需要做什么"],[
 ["working","程序正在运行","等待或查看进度"],["blocked","需要用户审批、回答或登录","回到正确会话处理具体请求"],["done","某项结果已准备好","阅读输出、核对产物与验收"],["error","程序报告失败并停止","查看错误并决定修复或重试"],["idle","等待下一条指令","发送新任务或结束会话"]]), "refs":["osc","privacy","home"]},
 {"id":"desktop", "title":"文件与桌面：另两类数据通道", "intro":"终端、文件和桌面可以共用身份与网络基础，但负载、控制语义和验收方式各有差异。", "paragraphs":[
 "文件浏览、预览、编辑和传输在产品资料中有说明。一个可实现的文件桥接会把操作送到目标端执行，再返回目录、文件内容或数据块；路径处理、大小限制、权限、编辑冲突和中断续传都需要设计。这里描述的是实现问题清单，尚未确认 Vibe42 的具体策略。",
 "Mac 远程桌面的安装说明要求屏幕录制与辅助功能权限。据此和官网演示，可以推导出画面采集 → 编码传输 → 客户端显示，以及输入事件 → 目标端操作的两条通路。所用屏幕捕获接口、视频编码、码率控制与权限处理细节仍未公开。",
 "桌面画面与终端数据有不同代价：桌面持续传送图像，更依赖带宽和视频解码；终端主要传文字和控制序列，但对交互延迟、字形和输入法更敏感。CPU/GPU用量、温度、输入延迟与手机耗电需要以实际任务、网络和设备测试。",
 "本次只确认官方展示 Mac 桌面控制，没有把 Linux 远程桌面或 Windows 被控主机能力补写成已支持。"], "refs":["install","store","home"]},
 {"id":"comparison", "title":"与以前研究的产品比较", "intro":"四个产品的主要控制层次不同，也存在重叠和可组合部分。比较具体通路，比只贴“远控”“Agent工具”标签更有帮助。", "paragraphs":[
 "Agenvo 在以前的研究中已有固定源码快照，重点是让通用助手经 MCP 调用不同原生运行时。Connector 内的 Adapter 将方法与参数转成运行时 API/CLI，并保留原生会话身份。它支持自托管 Relay，但 Relay 可看到请求和结果。",
 "cmux 此前已有009子项目研究；本次对照固定官方快照补充比较。它管理工作区、终端、浏览器和 Agent 事件，同时存在 SSH 与 iOS companion beta。因此它的用途与 Vibe42 在移动接续上有交集，不能简单写成仅本地工具。移动传输架构文档是文档证据，本研究未验证发布实现。",
 "WireGuard Install 以前研究的是配置部署脚本。WireGuard 保护 IP 传输，安装器配置 peer、路由、转发和NAT；远程终端、Agent方法、任务通知仍由上层应用提供。这个集中网关方案在服务器处解密VPN内的IP包，内层HTTPS等可以继续保护应用内容。",
 "三者可与远程工作系统组合，但不能由共享某个机制推出产品完全相同。Noise 同属密码协议背景，并不能证明 Vibe42 采用了 WireGuard 的握手模式或完整VPN数据协议。"], "refs":["agenvo","agenvo-security","cmux","cmux-mobile","cmux-tmux","cmux-transport","wireguard","wg-install"]},
 {"id":"meaning", "title":"对我们有什么用：选入口，也学习分工", "intro":"选择取决于想从手机继续操作、让助手自动调用，还是给多个任务建立可观察的工作环境。", "table":(["你的目标","优先借鉴什么","成立条件"],[
 ["离开电脑后查看/继续开发","Vibe42的跨设备终端与交互入口","目标机在线、平台支持、已配对，真实移动体验达标"],["自建助手统一调用多种Agent","Agenvo的能力发现、Adapter和原生身份","原生接口可用，权限和业务验收明确"],["一处组织多个Agent与网页实验","cmux的工作区、对象ID、Hooks和控制API","macOS等条件满足；远程/移动能力另行验证"],["访问自己的服务器或内网服务","WireGuard的设备密钥与网络路由","服务器可达，路由/返回路径/防火墙配置正确"],["持续整理GitHub研究证据","独立任务状态、来源与产物验收","需要自己补上研究版本、日志、截图和文档归档流程"]]), "paragraphs":[
 "对当前Windows研究机，Vibe42主机端尚不是立即可复现的选择。若已有Mac/Linux实验机，Windows浏览器可以作为入口；若只是研究工程设计，这次材料足以拆分连接、会话、渲染和通知职责。",
 "可以设想自己的研究流程：RAG索引在Linux机运行，手机读取进度并处理请求；网页实验在另一会话中构建，你回到电脑再核对截图和文档。减少等待和检查状态的收益是合理目标，实际节省时间、遗漏确认次数、恢复失败率仍要记录才能证明。",
 "更值得复用的是层次划分：远程连接解决能到达，终端解决能操作，原生接口解决结构化调用，工作区解决能管理，产物验收解决结果是否成立。把这几层组合，才能形成自己的研究与自动化工作流。"], "refs":["install","agenvo","cmux","wireguard"]},
 {"id":"implementation", "title":"自己实现：分阶段建立可验收的系统", "intro":"以下是本研究提出的实现路线，不是 Vibe42 的真实源代码或已完成复刻。先解决一个确定场景，再扩充协议和平台。", "table":(["阶段","实现范围","关键验收"],[
 ["01 本机终端闭环","接入服务创建PTY，网页终端发送输入、呈现输出与尺寸变化","交互式程序、Ctrl+C、中文输入、粘贴、退出与权限正确"],["02 持续会话","加入tmux或独立会话管理，控制端可离开再接续","手机断网不杀进程；恢复到正确会话；输出与输入不混线"],["03 授权与远程路由","设备身份、一次性配对、撤销、账号/授权服务与中继","陌生设备不能操作；授权撤销生效；连接目标身份可验证"],["04 内容端到端加密","采用有审阅依据的密码库/协议，定义密钥、握手和加密消息格式","中继不持有内容密钥；篡改被拒绝；计数/重连/密钥生命周期正确"],["05 连接可靠性","路径选择、网络切换、心跳、重连、缓冲与流量控制","多种NAT和蜂窝环境；无重复写操作；恢复时间可测"],["06 状态和通知","程序主动状态报告、适配、系统推送、去重与限频","等待审批/完成/失败可区分；关闭App可达；通知不泄露多余内容"],["07 文件与桌面","路径权限、编辑冲突/断点；画面捕获、编码和远程输入","越权/冲突/中断处理；真实交互延迟与资源消耗"],["08 多平台与运营","跨端输入体验、系统权限、升级、团队访问和观测","不同平台行为一致；升级不丢身份；故障诊断可用"]]), "paragraphs":[
 "最小版本可以只做一个Linux主机和一个浏览器入口；原生手机、直接穿透和桌面视频可后续加入。开发中可以使用普通的受控远程通道验证业务链路，但“完成远程访问”与“达到端到端加密、免配置和全球连接的产品能力”需要分别验收。",
 "通用终端路线提供广泛兼容。如果目标是助手自动创建任务、读原生历史、响应某项审批并精确中断，应增加类似Agenvo的运行时Adapter与结构化事件。两种入口可以共存，统一设备身份、原生会话ID和任务验收记录。",
 "实现前先定义威胁模型、会话生命周期、允许操作和恢复语义。特别说明中继是否可信、浏览器端密钥怎样持有、设备丢失怎样撤销、主机服务按谁的权限执行，以及重连后哪些操作允许重试。生产方案应使用成熟组件并进行独立审核，本研究没有提供可部署远控后端。"], "refs":["pty","tmux","noise","agenvo"]},
 {"id":"boundaries", "title":"已知、推导与待验证：避免把概念当实测", "intro":"每项结论都有证据层次。官方声明确认“产品怎样描述自己”；标准协议说明“这种机制怎样工作”；运行验证才能确认具体实现的行为。", "table":(["容易混淆的说法","本研究的准确表述"],[
 ["没有后台，所以电脑也不必运行服务","手机客户端可以关闭；目标电脑的Companion承担持续接入"],["官网说不会改shell，所以安装完全没有变动","当前安装说明和脚本涉及PATH/shell文件；与官网笼统说法存在范围差异，实际安装变更需检查"],["零留存等于平台不保存任何数据","官方区分工作内容与账号、设备、连接、通知和计费数据"],["支持所有Agent等于全都有原生任务接口","通用终端兼容与原生任务语义应分别验证"],["手机断线、电脑休眠、进程退出都是会话不断","分别测试观察通道、系统运行、接入服务和原生历史恢复"],["下载版本就是研究过对应源码commit","0.11.0来自下载元数据；未安装、无公开源码commit"],["有Noise，所以底层就是WireGuard","Noise是协议框架，不能推出具体产品的VPN/传输实现"],["cmux纯本地；Agenvo每任务装适配器","cmux已有远程/移动交集；Agenvo Adapter属于Connector实现，部署不按任务重复"],["状态done或进程退出0等于用户目标完成","需要阅读产物、检查结果并按业务验收"],["设计文档存在等于功能已发布","对cmux移动运输设计和未来方案分别标明证据状态"]]), "paragraphs":[
 "价格、额度和免费政策不在这里固定为购买结论：官网首页与安装说明对免费/计划要求的表达存在差异，应由使用时的账号控制台确认。研究重点是架构与可验证能力，不以抓取的一次价格展示作长期承诺。",
 "未确认项包括：主机/客户端语言与框架、源码许可证、Noise具体模式、NAT打洞策略、浏览器传输回退、Mac会话管理、文件冲突/续传、视频编解码、通知适配矩阵、性能和撤销行为。没有证据时不补全为某个熟悉技术栈。"], "refs":["install","bootstrap","privacy","github","meta","cmux-transport"]},
 {"id":"verification", "title":"验证范围与下一次复现清单", "intro":"本次完成的是公开资料核对与研究网页制作。所有交互面板是本地教学示意，未连接真实Agent、账号或主机。", "table":(["事项","本次状态","独立验证需要什么"],[
 ["官网、安装说明、脚本、隐私与元数据","已只读核对，记录日期和部分响应哈希","复查文档变更与发布说明"],["以前研究记录与固定源码来源","Agenvo/WireGuard已对照；cmux本次补充官方文档","运行条件和当前版本需另验"],["原产品安装与配对","未运行","Mac/Linux主机、账号、授权与可用计划"],["PTY交互与会话恢复","只解释机制；未测Vibe42","中文、快捷键、粘贴、断网、休眠、重启"],["直连、中继、加密和撤销","官方说明；未抓包/审计","受控网络、多种路径、授权撤销与协议验证"],["推送、文件和远程桌面","产品资料；未运行","真机通知、权限、文件冲突和桌面延迟"],["研究页面与静态子路径","Chromium桌面/手机浏览器验收通过；见本地验证记录","其他浏览器、真机和辅助技术需另验"],["公网发布","未部署，demo_url为空","发布成功并实际访问之后再填写入口"]]), "paragraphs":[
 "复现实验应按最小权限、单台主机与单个终端开始。先记录主机系统、产品版本、Agent版本、会话名称、测试动作与观察结果，再扩展网络故障、设备切换和多会话。不要在研究材料中保存密钥、配对码、推送令牌或私人终端内容。",
 "对连续性分别记录：手机关闭后程序是否运行；恢复是否仍为同一会话；断线输出是否补齐；已发送操作是否重复；休眠/重启后如何恢复。对安全分别记录：未配对设备拒绝、撤销后现有/新连接行为、内容加密范围和元数据可见范围。",
 "对通知记录到达时间、重复/漏发、所携带内容，以及人工处理后状态是否更新。对桌面和终端记录输入延迟、网络条件、CPU/GPU与耗电。把记录与用户目标验收并列，才能从“功能存在”推进到“对我们有用”。"], "refs":["install","privacy"]},
]

COMPARISON = [
 ["主要控制层次","PTY输入输出、桌面事件；状态协议补充语义","原生Agent方法、参数与会话身份，经MCP/Adapter调用","工作区/pane/surface、终端与浏览器API、Agent Hooks","IP包、peer、系统路由和防火墙"],
 ["执行在哪里","目标电脑的现有开发环境","原生运行时所在环境；Connector不必等于最终执行机","本地Mac或SSH等远程环境","自身不执行Agent；承载上层连接"],
 ["会话归谁","电脑终端与程序；Linux要求tmux；内部细节未知","原生Agent历史与thread/session等身份","布局/scrollback、原生Agent历史、tmux进程分别管理","没有Agent会话概念"],
 ["断线后怎样","产品称手机离开后会话持续；电脑仍需运行","连接断开不取消独立原生任务；不自动重放输入","UI恢复与活进程恢复分开；可选local-tmux等","网络恢复不保证业务连接或任务恢复"],
 ["连接路径","设备直连或密文中继；具体穿透未知","目标侧主动WSS连接自托管Relay","SSH；iOS beta文档描述Iroh直连/managed relay","本安装器采用集中Linux网关与可达UDP"],
 ["中转信任","官方称设备端Noise加密；Relay只转密文","TLS保护传输；Relay可见请求与结果","移动架构文档分开端点TLS身份与账户授权；未实测","VPN网关解密内部IP包；内层TLS可以继续保护业务"],
 ["自托管与源码","本次未发现完整公开源码或自托管说明","Apache-2.0；支持Cloudflare/单Linux VPS Relay","客户端主体GPL；列出的server目录有BUSL条件","安装器MIT；自有Linux主机与官方VPN客户端"],
 ["移动/远程交集","iOS、Android、Web控制Mac/Linux","可接自建客户端/助手，重点是运行时接口","iOS/iPadOS companion beta与SSH已有交集","各平台VPN客户端；上层交互另行提供"],
 ["部署单位","目标电脑运行Companion，控制设备配对","按backend配置Connector；Adapter随实现；无需每任务重装","工作台/远程连接/移动配对按用途组合","网关加peer配置与各设备客户端"],
 ["通知与验收","OSC7501与推送；准确适配与业务验收另验","原生状态与事件；accepted/idle不等于业务成功","Agent Hooks与工作台通知；产物仍需验收","不提供Agent任务通知或业务成功判定"],
 ["更适合的目标","人在外面继续操作开发环境","通用助手/自动化统一调用多种运行时","组织多个Agent、终端和浏览器并及时接手","建立设备间受控网络可达性"],
 ["我们可复用什么","跨设备交互、会话接续、配对、通知与数据边界","能力发现、地址层级、原生身份、请求关联与故障对账","工作区ID、可编程界面、可见状态与人工接手","每设备密钥、配置撤销、路由与网络层分工"],
]

EVIDENCE = [
 ["official","电脑运行Companion","安装说明明确电脑端服务及systemd/supervisor管理。","install"],
 ["official","Linux要求tmux 3.0+","这是安装前提；Mac实现不能由此直接推定。","install"],
 ["official","完整PTY与会话接续","开发者应用说明；尚未实际运行。","store"],
 ["official","直连或加密中继","官网公开产品路径；穿透细节未公开。","home"],
 ["official","Noise与设备端密钥","官网说明握手框架；具体模式未知。","home"],
 ["official","内容不留存、运营元数据存在","隐私政策分别列出内容与账号/连接记录。","privacy"],
 ["official","Mac/Linux主机、Windows浏览器控制","官方安装说明区分Computer与Device。","install"],
 ["official","OSC7501状态协议","状态语义有官网及协议文档依据；完整通知管道未知。","osc"],
 ["official","下载元数据标注0.11.0","只读元数据响应，不代表源码commit或安装验证。","meta"],
 ["inference","控制面与数据面逻辑拆分","依据公开职责整理；不是内部服务目录。","privacy"],
 ["inference","桌面采集、编码与逆向输入","依据Mac权限和展示推导；具体接口/编码未知。","install"],
 ["inference","恢复时应先查看再重发","通用网络与任务执行语义分析；不是产品默认策略证明。","pty"],
 ["proposal","自己的最小远程工作系统","本研究提出的阶段路线，尚未实现后端。","tmux"],
 ["proposal","原生Adapter与通用终端共存","借鉴Agenvo形成的集成建议。","agenvo"],
 ["unverified","NAT穿透、路径选择和浏览器回退","无公开核心源码或完整协议细节；未测。","github"],
 ["unverified","每种Agent的状态适配","通用兼容不自动说明原生状态准确性。","home"],
 ["unverified","运行、安全与性能效果","未安装配对、抓包、测量延迟或耗电。","install"],
 ["unverified","完整源码许可证与自托管方案","官方GitHub本次无公开仓库；未知保持未知。","github"],
]

MODULES = [
 ["client","控制客户端","手机、平板、浏览器","把人的文字/按键/触摸变成输入事件；解析终端数据或显示桌面画面。手机App关闭后的系统推送属于另一通道。","公开功能说明；内部框架未公开。"],
 ["control","账号与设备控制面","平台基础设施","管理身份、一次性配对、授权、角色、在线状态和连接路由。隐私声明列出必要的账号、设备与连接记录。","根据官方职责整理的逻辑模块。"],
 ["relay","连接与中继","直连 / 密文中继","两端可直接通信时使用直连；需要时中继转发。按官方说明，中继不持有工作内容的解密密钥。","官方路径声明；打洞/选择算法未公开。"],
 ["companion","电脑接入服务","Mac / Linux","持续接入目标电脑。Linux以用户级systemd或supervisor管理；Mac应用内含Companion。安装权限与执行身份影响本机可访问范围。","官方安装说明；核心源码未公开。"],
 ["session","终端与会话","PTY / Linux tmux","为交互程序提供终端输入输出；电脑保持运行时，让观察界面与会话生命周期分离。活进程、显示状态和Agent历史各自管理。","PTY有产品说明；Linux要求tmux；内部使用方式未知。"],
 ["agent","原生Agent与工具","已有开发环境","收到请求后决定动作、读写代码、运行测试；按自身配置调用模型和工具。业务完成仍需核对产物。","机制解释；本页没有运行真实Agent。"],
 ["notify","状态与通知","事件 / 系统推送","程序报告状态，相关事件可交付到通知服务，再通过APNs/FCM到手机。报告完整性、去重和通知限频属于实现与验证事项。","协议和推送有公开依据；完整内部管道为推导。"],
]
STEPS = [
 ["配对并选机","确认授权设备与正确会话","目标机安装Companion并获授权；手机或浏览器选择允许访问的电脑。","还没有向Agent发送业务任务。"],
 ["建立通道","验证端点，形成可用路径","平台完成连接协调；设备间建立加密通道。能直连时直连，需要时走中继。","具体握手模式与路由算法尚未公开。"],
 ["送入终端","文本/按键到达PTY","控制端提交构造示例：请运行测试并说明结果。输入送入电脑终端。","通用终端事件本身不等同原生task/turn方法。"],
 ["Agent执行","电脑运行命令并产生结果","Agent读取请求，决定运行测试，使用自己的项目目录、工具和模型配置。","模拟输出并非真实测试结果。"],
 ["显示结果","输出返回并在控制端渲染","文字、颜色和光标控制序列返回；控制端绘制终端。若为桌面模式，则显示画面。","回到同一会话与补齐输出需要实际验证。"],
 ["状态与验收","通知后，用户核对产物","状态报告可触发提醒；用户阅读结果并核对代码与测试。","done/退出成功均不能单独证明用户目标完成。"],
]

def esc(value):
    return html.escape(str(value), quote=True)

def source_links(refs):
    return '<div class="citations"><span>依据</span> ' + ' · '.join(f'<a href="{esc(SOURCE_MAP[r][2])}" target="_blank" rel="noopener">{esc(SOURCE_MAP[r][1])} ↗</a>' for r in refs) + '</div>'

def render_table(headers, rows, caption):
    body = []
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            tag = 'th' if i == 0 else 'td'
            scope = ' scope="row"' if i == 0 else ''
            cells.append(f'<{tag}{scope} data-label="{esc(headers[i])}">{esc(cell)}</{tag}>')
        body.append('<tr>'+''.join(cells)+'</tr>')
    return '<div class="table-wrap"><table><caption>' + esc(caption) + '</caption><thead><tr>' + ''.join('<th scope="col">'+esc(h)+'</th>' for h in headers) + '</tr></thead><tbody>' + ''.join(body) + '</tbody></table></div>'

def section_intro(chapter, number):
    return f'<div class="section-heading"><span class="section-no">{number:02}</span><div><h2>{esc(chapter["title"])}</h2><p class="section-intro">{esc(chapter["intro"])}</p></div></div>'

def custom_content(section):
    if section == 'architecture':
        buttons = ''.join(f'<button type="button" data-module="{m[0]}" aria-pressed="{"true" if i == 0 else "false"}"><span>{i+1:02}</span>{esc(m[1])}</button>' for i,m in enumerate(MODULES))
        return f'''<figure class="architecture-figure"><a href="./assets/architecture.svg" target="_blank" aria-label="打开完整架构图"><img src="./assets/architecture.svg" alt="原创Vibe42逻辑架构：控制客户端、平台控制与中继、电脑Companion、终端会话、原生Agent及系统推送；公开依据与推导分开" loading="lazy"></a><figcaption>本研究绘制的逻辑架构，2026-10-14。属于解释图；内部模块边界与路由细节尚未公开。</figcaption></figure><div class="module-inspector"><div class="module-buttons" aria-label="选择架构模块">{buttons}</div><article id="module-detail" class="module-detail" aria-live="polite"><span class="overline">{esc(MODULES[0][2])}</span><h3>{esc(MODULES[0][1])}</h3><p>{esc(MODULES[0][3])}</p><small>{esc(MODULES[0][4])}</small></article></div><div class="inline-actions"><a href="./assets/architecture.svg" download="vibe42-architecture.svg">下载架构图 SVG ↓</a><a href="./data/research-notes.txt" download>下载完整研究文字 ↓</a></div>'''
    if section == 'lifecycle':
        buttons = ''.join(f'<button type="button" data-step="{i}" aria-pressed="{"true" if i==0 else "false"}"><span>{i+1}</span>{esc(s[0])}</button>' for i,s in enumerate(STEPS))
        timeline = ''.join(f'<li><strong>{esc(s[0])}</strong><p>{esc(s[2])}</p><small>{esc(s[3])}</small></li>' for s in STEPS)
        return f'''<div class="walkthrough"><div class="walk-controls" aria-label="选择操作步骤">{buttons}</div><div class="walk-stage"><div><span id="step-count" class="overline">步骤 01 / 06</span><h3 id="step-title">{esc(STEPS[0][1])}</h3><p id="step-body">{esc(STEPS[0][2])}</p><p id="step-note" class="small-note">{esc(STEPS[0][3])}</p><div class="walk-arrows"><button type="button" id="step-prev" disabled>← 上一步</button><button type="button" id="step-next">下一步 →</button></div></div><div class="terminal-window"><div class="terminal-head"><span class="terminal-dot"></span>终端交互示意 · 构造数据</div><pre id="terminal-output" aria-live="polite">等待选择已授权电脑…\n本页没有真实远程连接。</pre></div></div></div><ol class="timeline">{timeline}</ol>'''
    if section == 'terminals':
        return '''<div class="failure-panel"><label for="failure-select">改变一个条件，观察会话边界</label><select id="failure-select"><option value="phone">手机断网 / 关闭App</option><option value="sleep">电脑进入休眠</option><option value="service">Companion退出</option><option value="restart">电脑重启 / Agent退出</option></select><p id="failure-result" aria-live="polite">产品说明：电脑持续运行时，手机离开后终端会话可以继续；重新连接是否完整补齐输出仍待实测。</p><small>这是机制解释面板，结果来自研究材料，没有执行故障实验。</small></div>'''
    if section == 'network':
        return '''<div class="network-panel"><div class="network-top"><span class="overline">同一份工作内容，两种传输路径</span><div class="segmented" aria-label="选择连接路径"><button type="button" data-route="direct" aria-pressed="true">直连</button><button type="button" data-route="relay" aria-pressed="false">经过中继</button></div></div><div id="route-path" class="route-path"><span>控制端</span><b>⇄ 加密内容 ⇄</b><span>目标电脑</span></div><p id="route-explanation" aria-live="polite">官方路径：设备之间直接通信。可行性取决于网络条件；具体建立算法未公开。</p><div class="network-footer"><span>工作数据：终端 / 文件 / 画面</span><span>控制数据：身份 / 授权 / 在线状态</span></div></div>'''
    if section == 'verification':
        published = ('<p><strong>公开网页已验证：</strong>GitHub Pages发布成功，公开资源与提交逐项比对、索引摘要和浏览器交互均已检查。<a href="https://github.com/yydshly/1013_codex_project/blob/main/projects/010-vibe42/experiments/results/publication.md" target="_blank" rel="noopener">查看独立发布记录 ↗</a></p>' if DEMO_URL else '')
        return '<div class="comparison-notes"><p><strong>本地页面验收：</strong>Chromium桌面/手机交互通过，五种视口无页面横向溢出；完整研究的章节跳转和理解图教学交互已验收。原产品的安装、连接、安全和性能仍待独立验证。</p>'+published+'<p><a href="./data/verification.json" download="vibe42-page-verification.json">下载页面验收记录 JSON ↓</a></p></div>'
    if section == 'comparison':
        return render_table(['比较维度','Vibe42','Agenvo','cmux','WireGuard Install'], COMPARISON, '主要控制层次与完整工作流对比') + '''<div class="comparison-notes"><p><strong>版本依据：</strong>Agenvo 源码68e046a（发行参考v0.2.0）；WireGuard Install 3f42877；cmux cdbe995。本次Vibe42依据2026-10-14公开资料，下载元数据标注0.11.0。</p><p><strong>许可范围：</strong>cmux主体GPL-3.0-or-later，根LICENSE列出的服务器目录另有BUSL-1.1生产使用条件，不能按客户端许可概括整个仓库；Vibe42未发现公开源码许可证。</p><p><a href="https://yydshly.github.io/1009_codex_project/016-agenvo/" target="_blank" rel="noopener">以前的Agenvo研究 ↗</a> · <a href="https://github.com/hwdsl2/wireguard-install" target="_blank" rel="noopener">WireGuard Install源库 ↗</a> · <a href="https://github.com/manaflow-ai/cmux" target="_blank" rel="noopener">cmux源库 ↗</a></p></div>'''
    if section == 'boundaries':
        labels={'official':'公开依据','inference':'实现推导','proposal':'我们的建议','unverified':'尚未验证'}
        filters='<button type="button" data-evidence-filter="all" aria-pressed="true">全部</button>'+''.join(f'<button type="button" data-evidence-filter="{k}" aria-pressed="false">{v}</button>' for k,v in labels.items())
        cards=''.join(f'<article class="evidence-row" data-evidence-kind="{r[0]}"><span class="evidence-tag {r[0]}">{labels[r[0]]}</span><div><h3>{esc(r[1])}</h3><p>{esc(r[2])}</p></div><a href="{esc(SOURCE_MAP[r[3]][2])}" target="_blank" rel="noopener" aria-label="查看{esc(r[1])}的依据">依据 ↗</a></article>' for r in EVIDENCE)
        return f'<div class="evidence-controls" aria-label="筛选证据层次">{filters}</div><p id="evidence-count" class="small-note" aria-live="polite">显示 {len(EVIDENCE)} 项研究记录</p><div class="evidence-list">{cards}</div>'
    return ''

def sync_publication_status():
    if not DEMO_URL: return
    for chapter in CHAPTERS:
        if chapter["id"] == "verification":
            for row in chapter["table"][1]:
                if row[0] == "公网发布":
                    row[1] = "静态研究网页已发布并实际访问验证"
                    row[2] = "见独立发布记录；真实产品验证仍需另行执行"


def make_readme():
    lines=['# 010 · '+METADATA['name'],'',
    '> '+METADATA['summary'],'',
    '[返回总索引](../../README.md#项目索引) · [官方产品网站](https://vibe42.ai/) · [研究网页源码](./web/index.html) · [网页运行说明](./web/README.md) · [验证记录](./experiments/results/verification.md)','',
    ('[已验证的公开网页]('+DEMO_URL+'#understanding) · [公网发布记录](./experiments/results/publication.md)' if DEMO_URL else '公开入口待实际发布验证。'),'',
    '## 研究基线与来源','',
    '| 信息 | 本次记录 |','| --- | --- |',
    '| 研究日期 | 2026-10-14，Asia/Shanghai |',
    '| 研究对象 | Vibe42 产品；以前称 Vibe X。不是已取得公开源码的开源库 |',
    '| 最初入口 | https://vibe42.ai/zh-HANS#features；以可读取官网和官方资料核对 |',
    '| 研究版本 | 官网/安装/隐私等公开资料的当日查阅；下载元数据标注 0.11.0，未安装 |',
    '| 原仓库与源码 commit | 官方 GitHub 组织 https://github.com/vibe42-ai 本次无公开仓库；没有可填写的源码 commit |',
    '| 上游源码许可证 | 未发现公开源码许可证；project.json 对应字段留空，不默认视为 MIT 或其他开源许可 |',
    '| 本地环境 | Windows / PowerShell；Python 标准库生成静态研究材料；浏览器验收环境见验证记录 |',
    '| 状态 | researching：公开资料与研究网页；未安装、配对或复现真实产品 |',
    ('| 演示入口 | [公开理解网页]('+DEMO_URL+')；静态研究页，真实产品尚未复现 |' if DEMO_URL else '| 演示入口 | 静态研究网页待部署验证；demo_url保持为空 |'),
    '| 素材与许可 | 原创文字、HTML/CSS/JS和架构SVG；没有复制产品截图、二进制或上游源码 |','',
    overview.markdown(),'']
    for i,c in enumerate(CHAPTERS,1):
        lines += [f'## {i}. {c["title"]}','',c['intro'],'']
        for p in c.get('paragraphs',[]): lines += [p,'']
        if 'table' in c:
            heads, rows=c['table']; lines += ['| '+' | '.join(heads)+' |','| '+' | '.join('---' for _ in heads)+' |']
            lines += ['| '+' | '.join(row)+' |' for row in rows]; lines += ['']
        if c['id']=='lifecycle':
            lines += [f'{j+1}. **{s[0]}：** {s[2]} {s[3]}' for j,s in enumerate(STEPS)]; lines+=['']
        if c['id']=='comparison':
            lines += ['| 比较维度 | Vibe42 | Agenvo | cmux | WireGuard Install |','| --- | --- | --- | --- | --- |']
            lines += ['| '+' | '.join(row)+' |' for row in COMPARISON]; lines+=['',
            '固定对比基线：Agenvo `68e046a5d8691054f8c134d85ae051988bae3dff`（源码快照；v0.2.0仅发行参考）；WireGuard Install `3f428774e61c95bca60d1e7b80f0c768ca2c6137`；cmux `cdbe99596fe13784ec5ea24d2e1c720a8f67f5cb`。cmux对应已有009研究；本次比较对照固定官方快照和官网，移动传输设计与实际发布行为仍分别标明证据范围。','',
            'cmux许可：根LICENSE默认为GPL-3.0-or-later，但列出的server目录采用BUSL-1.1，并有生产使用、包括自托管的商业授权条件。复制或部署前须按具体目录核对。Vibe42未发现公开源码许可证。','',
            '以前记录：[Agenvo既有研究网页](https://yydshly.github.io/1009_codex_project/016-agenvo/)、[WireGuard README](../005-wireguard-install/README.md)、[cmux既有研究](../009-cmux/README.md)。','']
        lines += ['依据：'+'、'.join(f'[{SOURCE_MAP[r][1]}]({SOURCE_MAP[r][2]})' for r in c['refs'])+'。','']
    lines += ['## 15. 证据登记与资料版本','',
    '当前公开网页不是固定源码版本。部分响应哈希与版本观察保存在 [source_records.json](./experiments/source_records.json)。哈希针对本次收到的UTF-8文本，用于对照文档变更，不是应用签名验证，也不代表后端版本。没有把完整第三方网页或安装文档复制入库。','',
    '| 层次 | 结论 | 说明 |','| --- | --- | --- |']
    levels={'official':'公开依据','inference':'实现推导','proposal':'我们的建议','unverified':'尚未验证'}
    lines += ['| '+levels[r[0]]+' | '+r[1]+' | '+r[2]+' |' for r in EVIDENCE]
    lines += ['', '## 16. 网页与可维护文件','',
    '- `web/index.html`：预渲染完整研究内容，不依赖外部CDN。',
    '- `web/styles.css`、`web/app.js`：响应式阅读、模块说明、六步示意、故障条件、路由切换和证据筛选。',
    '- `web/assets/understanding-overview.svg`与同名PNG：完整理解图；研究目录assets内的同图用于索引与下载。',
    '- `web/assets/architecture.svg`：保留详细三端架构图。',
    '- `experiments/build_overview.py`：总览、节点机制和路径讲解内容；网页与静态图共用底图。',
    '- `web/data/research-notes.txt`、`web/data/evidence.json`：完整研究文字与结构化证据；下载不包含凭据。',
    '- `experiments/build_research.py`：研究材料的单一内容源与生成工具；不会连接产品。',
    '- `experiments/results/verification.md`：本次页面验收与尚未验证事项。','',
    '### 网页截图（本次本地研究页）','',
    '这些截图来自本研究原创静态页面的Chromium验收，非Vibe42运行界面。原生架构SVG另有下载入口。','',
    '![研究网页桌面首屏：执行位置与阅读入口](./assets/01-web-desktop.png)','',
    '![研究网页架构章节：三端、会话和数据边界](./assets/02-web-architecture.png)','',
    '![研究网页产品对比：12个维度与证据说明](./assets/03-web-comparison.png)','',
    '![研究网页手机首屏：390px响应式阅读](./assets/04-web-mobile.png)','',
    '![桌面原理互动：同图放大、节点、三路径与直连/中继](./assets/05-overview-interaction-desktop.png)','',
    '![手机原理讲解：节点机制、例子与证据边界](./assets/06-overview-interaction-mobile.png)','',
    '## 17. 来源与致谢','']
    lines += [f'- **{name}**：[原文]({url})。{note}' for _,name,url,note in SOURCES]
    lines += ['', '本仓库研究解释图与网页为原创整理。标准协议用于说明机制，产品资料用于记录官方声明。没有取得公开源代码时，语言、框架、算法、数据结构与具体性能保持未知。','']
    return '\n'.join(lines)

def make_page():
    nav_labels = {"verification":"验证与复现清单", "boundaries":"证据与待验证", "comparison":"产品对比", "lifecycle":"完整操作路径", "meaning":"意义与应用"}
    nav='<a href="#understanding"><span>00</span>理解总览与原理图</a>'+''.join(f'<a href="#{c["id"]}"><span>{i:02}</span>{esc(nav_labels.get(c["id"], c["title"].split("：")[0]))}</a>' for i,c in enumerate(CHAPTERS,1))
    sections=[overview.render_section()]
    for i,c in enumerate(CHAPTERS,1):
        body=custom_content(c['id'])
        body+=''.join('<p>'+esc(p)+'</p>' for p in c.get('paragraphs',[]))
        if 'table' in c: body+=render_table(*c['table'],c['title'].split('：')[0]+'说明')
        body+=source_links(c['refs'])
        sections.append(f'<section id="{c["id"]}" class="research-section">{section_intro(c,i)}{body}</section>')
    source_list=''.join(f'<li><a href="{esc(url)}" target="_blank" rel="noopener">{esc(name)} ↗</a><p>{esc(note)}</p></li>' for _,name,url,note in SOURCES)
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="Vibe42公开资料研究：能力与本质、Companion三端架构、终端会话、直连与加密中继、通知和桌面，与Agenvo、cmux、WireGuard对比，附来源和验证边界。"><meta name="color-scheme" content="light"><title>Vibe42 · Agent远程控制、原理与价值研究 | 010</title><link rel="icon" href="./assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="./styles.css"><script defer src="./data/interaction.js"></script><script defer src="./app.js"></script></head>
<body><a class="skip-link" href="#essence">跳到研究正文</a><header class="topbar"><a class="brand" href="#top"><span class="brand-mark">42</span><span>Vibe42 <small>研究档案 / 010</small></span></a><div class="top-actions"><a href="../">项目索引 ↗</a><a href="#sources">资料来源</a><button type="button" id="print-button">打印 / PDF</button></div></header>
<main id="top"><section class="hero"><div class="hero-copy"><div class="eyebrow"><span class="live-dot"></span>公开资料研究 <span>2026.10.14</span></div><h1>电脑上的开发环境，<br><em>从手机继续。</em></h1><p class="hero-lead">远程操作电脑里的 Agent、终端和文件，查看进度、处理确认、接手已有工作。<br>理解跨设备交互怎样送达真实执行，以及它的价值和可扩展场景。</p><div class="hero-tags"><span>理解总览</span><span>原理互动</span><span>产品对比</span><span>验证边界</span></div><div class="hero-actions"><a class="button-primary" href="#understanding">先看理解总览 <span>↘</span></a><a href="#comparison">与以前的研究对照 →</a></div><p class="hero-note">本次未发现Vibe42公开核心源库。本文依据官方材料和标准协议整理；所有示意与推导均有标注。</p></div><div class="hero-diagram" aria-label="人、远程入口与电脑的执行关系"><div class="diagram-label">执行在哪里？</div><div class="mini-device"><span class="mini-icon">↗</span><div><strong>你的手机 / 浏览器</strong><span>输入、查看、处理需要确认的操作</span></div></div><div class="mini-connection"><i></i><span>设备配对 · 加密连接</span><i></i></div><div class="mini-host"><div class="mini-host-head"><span class="terminal-dot"></span>你的 Mac / Linux</div><div class="mini-host-body"><span>Companion 接入服务</span><b>↓</b><span>终端 / 会话 → 编程 Agent</span><b>↓</b><strong>代码 · 工具 · 实际执行</strong></div></div><div class="diagram-caption">原创逻辑示意 · 未连接真实主机</div></div></section>
<div class="scope-banner"><strong>这次研究做到了哪里</strong><p>公开说明、安装入口与以前的研究已核对；尚未安装或配对产品。下载元数据标注 <b>0.11.0</b>，它是版本观察，源码 commit 未知。</p><a href="#verification">查看完整验证范围 →</a></div>
<div class="reading-layout"><aside class="reading-nav"><span class="overline">阅读路线</span><nav aria-label="研究章节">{nav}<a href="#sources"><span>15</span>资料来源</a></nav><a class="nav-download" href="./data/research-notes.txt" download>下载完整文字 ↓</a></aside><div class="reading-content">{''.join(sections)}<section id="sources" class="research-section sources-section"><div class="section-heading"><span class="section-no">15</span><div><h2>资料来源与研究版本</h2><p class="section-intro">优先使用产品官方、标准协议与固定代码快照。来源链接指向原文，本文内容是原创整理。</p></div></div><ol class="source-list">{source_list}</ol><div class="download-panel"><div><strong>把这份研究带走</strong><p>完整文字、原创架构图与证据登记均可下载。</p></div><div><a href="./assets/understanding-overview.svg" download="vibe42-understanding-overview.svg">理解总览 SVG ↓</a><a href="./assets/understanding-overview.png" download="vibe42-understanding-overview.png">理解总览 PNG ↓</a><a href="./data/research-notes.txt" download>完整文字 TXT ↓</a><a href="./assets/architecture.svg" download="vibe42-architecture.svg">架构图 SVG ↓</a><a href="./data/evidence.json" download="vibe42-evidence.json">证据登记 JSON ↓</a></div></div></section></div></div></main><footer><span>010 / Vibe42 · 中文研究档案</span><p>原创解释图与教学交互，2026-10-14。主机执行、网络传输、任务状态和业务验收分别评价。</p><a href="#top">回到顶部 ↑</a></footer><noscript><div class="noscript-note">已显示完整研究正文。启用JavaScript后可使用模块、步骤、故障、路由和证据筛选面板。</div></noscript></body></html>'''

def main():
    (WEB/'data').mkdir(parents=True, exist_ok=True)
    sync_publication_status()
    readme=make_readme()
    (PROJECT/'README.md').write_text(readme, encoding='utf-8')
    (WEB/'index.html').write_text(make_page(), encoding='utf-8')
    (WEB/'data'/'research-notes.txt').write_text(readme, encoding='utf-8')
    evidence={'date':DATE,'scope':'公开资料研究与原创教学网页；未连接真实产品','version_observation':'下载元数据0.11.0；无源码commit','records':[{'level':r[0],'claim':r[1],'note':r[2],'source':SOURCE_MAP[r[3]][2]} for r in EVIDENCE],'sources':[{'id':s[0],'title':s[1],'url':s[2],'note':s[3]} for s in SOURCES]}
    (WEB/'data'/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    interaction={'modules':MODULES,'steps':STEPS,'overview':overview.data()}
    (WEB/'data'/'interaction.json').write_text(json.dumps(interaction,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (WEB/'data'/'interaction.js').write_text('window.VIBE42_RESEARCH = '+json.dumps(interaction,ensure_ascii=False)+';\n',encoding='utf-8')
    results = PROJECT/'experiments'/'results'
    verification = {'date':DATE,'scope':('静态研究网页的本地与公网验收；不验证真实Vibe42产品' if DEMO_URL else '本地静态研究页；不验证真实Vibe42，不代表公网部署'),'demo_url':DEMO_URL,'interaction_report':None,'final_navigation_report':None}
    for field, filename in [('interaction_report','browser-check.json'),('final_navigation_report','navigation-check.json'),('overview_report','overview-check.json'),('publication_http_report','publication-http.json'),('publication_browser_report','publication-browser.json')]:
        record = results/filename
        if record.is_file(): verification[field] = json.loads(record.read_text(encoding='utf-8'))
    (WEB/'data'/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Generated {len(CHAPTERS)} chapters, {len(COMPARISON)} comparison dimensions, {len(SOURCES)} primary sources.')

if __name__=='__main__': main()
