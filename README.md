# GitHub 项目研究索引

> 研究 GitHub 项目的能力、实现原理、输入输出、应用价值与实践意义，记录源码证据、复现实验和使用边界，并集中提供研究文档与网页演示入口。

这里是研究总仓库。每个子项目拥有独立编号、研究文档、图片与实践代码；本页提供按编号排列的索引和简要介绍。

[项目目录](./projects/) · [新增项目指南](./CONTRIBUTING.md) · [研究模板](./templates/project/) · [Web 部署约定](./docs/deployment.md)

## 项目索引

<!-- PROJECT_INDEX:START -->
当前收录 **7** 个项目，按三位编号升序排列。

| 编号 | 项目 / 研究摘要 | 目标源库 | 研究状态 | 相关入口 |
| --- | --- | --- | --- | --- |
| **001** | **[Infinite Bookshelf：写书流程、能力与价值研究](./projects/001-infinite-bookshelf/README.md)**<br><br>**能力：** 把主题展开为目录、书名和分节长文初稿，顺序生成并汇总展示。<br>**原理：** 代码组织多次模型请求，先目录、再书名、逐节正文；写作方法与手动让模型先出大纲再写细节相同。<br>**输入：** 主题；可补充读者、目标、范围和风格要求，高级模式可加入笔记或 TXT 资料。<br>**输出：** 书名、目录、各节正文，以及可导出的 TXT/PDF 初稿，供人工编辑和审核。<br>**价值：** 减少重复请求与整理，复用写作流程，并可修改接口接入自有模型；没有提高模型本身能力。<br>**意义与场景：** 适合重复起草较独立的教程和培训材料；偶尔写作额外价值有限，复杂小说需补前文与人工审核。<br>**边界与验证：** 不能自动保证质量。本研究提供源码证据、总览图与摄影等可读样稿；样稿是保存内容，未验证真实模型 API 的质量、速度和费用优势。<br><br>AI 写作 · 长文生成 · 模型可替换 · 源码研究 | [infinite-bookshelf](https://github.com/Bklieger/infinite-bookshelf)<br>Bklieger | 已完成 | [研究文档](./projects/001-infinite-bookshelf/README.md)<br>[在线演示](https://yydshly.github.io/1013_codex_project/001-infinite-bookshelf/) |
| **002** | **[Production Agentic RAG Course：论文助手与工程架构研究](./projects/002-production-agentic-rag-course/README.md)**<br><br>**定位：** 以 arXiv AI 论文为默认资料的课程与参考工程，展示从资料采集到检索问答、运行维护的完整 RAG 链路；论文是示例领域。<br>**能力：** 源码包含定时采集论文、PDF 解析、章节或词数切块、关键词与向量混合检索、普通流式问答和论文来源链接，以及普通问答缓存、追踪和多个入口；Agentic 增加领域判断、相关性检查、改写与重试。<br>**原理：** 先获取并整理文件，解析正文、切分片段、生成语义向量并建立搜索索引；提问时融合关键词与向量检索，把相关片段与问题一起交给模型，再回看原文核对。RAG 为本次请求补充资料，无需为这条链路重新训练模型。<br>**架构：** PostgreSQL 保存正文与元信息，OpenSearch 保存片段、向量和检索字段；Docling 解析 PDF，Jina API 生成向量，Ollama 生成回答。Airflow 调度采集，Redis 缓存普通问答，Langfuse 追踪；FastAPI、Gradio、Telegram 提供入口。<br>**输入：** 默认采集 arXiv 的 cs.AI 论文和 PDF，问答输入为问题与检索参数。自有农业资料、手册或研究笔记需要新增来源或导入入口，保留题名、作者、年份、来源、版本、原文位置和领域字段。<br>**输出：** 建库得到可检索的片段、向量与元信息；搜索返回相关资料，普通问答返回模型回答和论文来源链接，供人工核查。本研究另提供中文导读、完整理解图、可下载使用路线、源码证据与复现清单。<br>**价值：** 主要参考价值是完整 RAG 的搭建方法、组件分工、数据衔接和评测思路，可为自己的知识系统提供实现基础；减少重复找资料与整理的效果，需要通过检索质量、核查时间、耗时和成本验证。<br>**对你的意义：** 把你收集的论文、种植资料、试验记录与 GitHub 项目研究逐步积累为能查找、能回答、能追溯依据的知识系统；同时形成判断 AI 项目质量的方法，并为后续研究对比、专题报告和写作提供资料基础。<br>**可扩展场景：** 上游默认用于 AI 论文研究；适配后可用于农业论文与种植手册问答、产品手册与技术规范查询、固定版本的 GitHub 项目研究对比，再探索资料助手、专题报告和与项目 001 长文写作的衔接。<br>**扩展方向：** 新资料入口、去重与定期更新，中文、扫描件、表格和实验条件提取，本地向量模型与私有部署，权限、版本和领域筛选，以及普通 RAG 与 Agentic 的对比评测。以上均为后续实现与验证方向。<br>**使用路线：** 先选明确主题，准备一批可靠文档和 10 个真实问题；获取资源、保留来源、整理文档、解析切块、建索引、检索问答并核对引用。先跑通普通 RAG、保存运行基线和验证记录，再扩展 Agentic 或其他应用。<br>**边界与验证：** 已完成核心源码研究和导读页验证，尚未运行上游。知识覆盖由已入库资料决定，来源链接需核对是否支持结论；默认领域规则需调整，Jina 向量化调用外部 API。Agentic 参数、模型接入、来源与追踪闭环，以及解析、检索、回答、更新、缓存和故障恢复仍待复现。<br><br>RAG · LangGraph · 混合检索 · AI 工程 | [production-agentic-rag-course](https://github.com/jamwithai/production-agentic-rag-course)<br>jamwithai | 研究中 | [研究文档](./projects/002-production-agentic-rag-course/README.md)<br>[在线演示](https://yydshly.github.io/1013_codex_project/002-production-agentic-rag-course/) |
| **004** | **[Leak Check：个人信息泄漏查询与关联原理研究](./projects/004-leak-check/README.md)**<br><br>**搜索能力：** 支持输入手机号、邮箱、身份证号或 QQ 号，查询匹配记录并通过共同标识关联其他记录；姓名、地址和公司等是返回字段，不能作为当前搜索入口。<br>**原理：** 识别输入格式，在本地 SQLite 既有数据库的对应字段中精确匹配；默认直接查询后再关联一轮，汇总、去重并脱敏返回。本质是数据库查询与数据处理的封装。<br>**输出：** 返回脱敏的姓名、联系方式、账号、地址、公司等字段列表及来源标签；字段与来源分别聚合，未保留逐条对应关系。<br>**数据前提：** 只能查到数据库已收录的内容，不自动发现或采集泄漏数据。仓库附示例库，未附作者线上完整数据库；空库无匹配结果，查不到也不能证明未泄漏。<br>**对我们的价值：** 价值不大，主要可参考常规数据库操作、有限关联与脱敏接口的实现；缺少核心数据，不能仅凭源码复现作者线上服务的查询效果。<br>**研究结论：** 基础源码理解与文档整理已完成，沿用本次生成的引导图，保留参考即可，不继续深入研究；尚未运行上游或验证真实数据与性能。<br><br>数据库查询 · 信息泄漏 · SQLite · 关联查询 · 脱敏 | [leak-check](https://github.com/garinasset/leak-check)<br>garinasset | 已完成 | [研究文档](./projects/004-leak-check/README.md)<br>演示未部署 |
| **005** | **[WireGuard Install：自建 VPN、原理与应用研究](./projects/005-wireguard-install/README.md)**<br><br>**库的能力：** 帮助你在自己的 Linux 服务器上搭建 WireGuard VPN：自动安装、生成密钥与接入配置、设置转发和 NAT、启动服务，并添加或撤销设备。客户端使用现成的 WireGuard 应用。<br>**底层原理：** 客户端把整个原始 IP 包认证加密，封装到外层 IP / UDP / WireGuard 消息中；服务端验证、解密和解封装，再由 Linux 路由与 NAT 转发。内部可以承载 TCP 或 UDP，HTTPS 的 TLS 加密继续存在。<br>**两端职责：** 两端都是密钥认证的 peer。客户端按系统路由选取流量、加密发送和解密返回；本项目的 Linux 服务端登记客户端公钥与内部 IP，处理隧道并作为集中出口网关。<br>**部署方法：** 准备受支持的 Linux、root 权限和可达 UDP 端口，运行安装器并设置服务器地址、端口与 DNS；将生成的配置或二维码导入设备，检查握手和实际业务。云安全组、上游端口映射和内网返回路径按环境配置。<br>**输入与输出：** 输入是服务器环境、可达地址、端口、DNS 和设备名称；输出是服务端接口与网络规则、每台设备的密钥和配置文件 / 二维码。导出材料含客户端私钥，属于接入凭据。<br>**个人价值：** 减少重复手配，掌握自己的出口和设备授权，方便多台手机电脑接入，并学习虚拟接口、加密隧道、路由和 NAT。需要承担服务器、流量费用、系统更新、凭据管理和排错。<br>**使用场景：** 适合个人自建集中出口、在不可信网络保护到网关的路径、实验室与小团队密钥接入；访问家庭或办公室内网、指定网段分流还需补充路由、返回路径、DNS 与防火墙策略。<br>**可扩展方向：** 可进一步设计分流与内网接入、逐设备访问策略、配置分发与密钥生命周期、Web 管理 / API、监控审计、部署自动化和多网关冗余；这些是后续设计，安装器未提供完整实现。<br>**边界与验证：** 源码、配置字段与官方协议已核对，中文网页已部署，线上资源与交互已验证；真实 VPN 连接、抓包、DNS / IPv6 与容量未实测。安装器无 TCP 回退或自动穿透中继平台，不保证速度、匿名性或平台断线阻断。<br><br>WireGuard · VPN · UDP · 加密隧道 · Linux | [wireguard-install](https://github.com/hwdsl2/wireguard-install)<br>hwdsl2 | 研究中 | [研究文档](./projects/005-wireguard-install/README.md)<br>[在线演示](https://yydshly.github.io/1013_codex_project/005-wireguard-install/) |
| **006** | **[Jev SEO：网页质量检查规则与自有模型审查框架](./projects/006-jev-seo/README.md)**<br><br>**核心定位：** 核心是针对公开网页前端可见质量的检查规则与内容评估标准，侧重 SEO、页面结构、抓取设置、链接与内容。适合作为网页质量检查的基础框架；采集提供事实，模型处理语义，报告提供整改依据。<br>**必须补充：** 还需要另外补充实际交互、手机布局、无障碍、业务功能和后端检查。viewport 存在不等于手机布局正常，响应正常不等于表单、权限或后端业务正确；本库不提供完整的应用质量认证。<br>**能力：** 采集部署网址，提取 HTML、标题、正文与链接，执行 52 条固定规则，按 19 个评估维度使用自有模型判断内容并生成带证据的报告。<br>**原理：** 采集页面快照 → 解析事实 → 固定规则与模型评估 → 指纹、格式及原文校验 → 整改排序与人工复核。规则未触发和模型未知都不能证明整站通过。<br>**参考与提取：** 固定上游 commit，保留采集、解析、规则和问题标准；新增项目路径范围、中文正文保留、兼容接口、聊天材料导入、证据与任务校验；未移植 DataForSEO 和专用概率体系。<br>**规则与定制：** 完整列出 52 条规则的触发、修复、上下文与来源，以及 19 个模型维度的选项和档位。固定规则需扩展执行代码，语义规则需扩展问题与报告映射；网页 JSON 是手册，不是扫描配置，经验阈值不能机械当作合格线。<br>**输入与输出：** 输入部署后公开可访问的网址与范围，内容判断另需聊天会话或模型接口。输出页面事实、规则问题、模型引文、审查覆盖、整改清单和 JSON/Markdown/本地 HTML。<br>**模型替换：** 当前聊天模型通过导出材料、审查、导入完成；自有模型通过 OpenAI 兼容 Chat Completions 自动评估。两种路径均校验输出与引文，允许未知，判断需要人工复核。<br>**使用场景：** 自己的 GitHub Pages、上线自查、文章与知识库、产品服务介绍、改版迁移、模型比较、便于检索引用的内容研究，以及记录网页症状后转入独立后端根因排查。<br>**价值：** 把检查目标、证据、判断标准和修复建议组织成可复用清单，将审查经验与模型供应商分开；减少重复核查并把建议定位到网址与原文，按影响和工作量安排整改。实际质量、效率和成本要通过真实样本验证。<br>**对我们的意义：** 将规则作为自己网页的基础检查标准，按作品集、产品页、文章或文档用途调整；用相同材料比较模型，再逐步补齐交互、移动端、无障碍、业务与后端测试，形成自己的质量检查流程。<br>**边界与验证：** 27 项离线实验测试通过，聊天样例 3 任务/28 判断跑通；导读网页已发布，资源与提交一致，公网规则检索与回跳验证，手机展示本地验证。真实网站审查、自有接口、PageSpeed 与采集器动态渲染未实测；不检查后端源码或真实排名，规则未触发和模型未知不代表整站通过。<br><br>网页质量 · SEO · 规则检查 · 模型替换 · 证据校验 | [jev-seo](https://github.com/AgriciDaniel/jev-seo)<br>AgriciDaniel | 研究中 | [研究文档](./projects/006-jev-seo/README.md)<br>[在线演示](https://yydshly.github.io/1013_codex_project/006-jev-seo/) |
| **007** | **[Hermes Jev Skills：多模型路由与判断标准研究](./projects/007-hermes-jev-skills/README.md)**<br><br>**库的能力：** 提供 Python 工具、CLI、技能、Hermes 插件和路由面板，把模型路由、技能选择、检索与证据判断、消息分类和候选动作选择接入 Agent。<br>**Jev 的作用：** Jev 是 TypeSafe 的云端决策模型，按输入状态、问题和标准返回有限选择、评分或是否概率；生成正文、修改代码和执行动作由主模型与工具完成。<br>**所在位置：** 位于工作流的判断环节：宿主组织状态与候选 → Jev 判断 → 本地策略校验、约束与回退 → 执行模型或工具；库不包含 Jev 权重和训练实现。<br>**路由原理：** 默认询问难度、工作类型和出错代价，本地代码结合阈值、模型池、上下文、图像能力和用户固定模型选择具体模型；Hermes 换模型不自动换供应商连接。<br>**输入与输出：** 输入是必要背景、明确问题与有限选项；输出是结构化判断。默认路由只看到脱敏且截断的当前请求及粗略特征，不能据此理解未提供的完整项目。<br>**我们的理解：** 值得借鉴的是按能力拆分任务，分开判断、选择、执行与验收。图中的个人架构和 A/B 策略是扩展设计，不是上游默认实现的逐项复刻。<br>**标准怎么设：** 先定义成果如何通过，再拆出背景是否足够、是否只改表达、是否需综合推理、是否存在行为依赖和错误代价；用真实 A/B 任务验证模型映射与阈值。<br>**何时使用：** 固定阶段、硬字段和可穷举分支优先规则；反复出现且会改变后续动作的语义判断，再比较 Jev 与便宜小模型；替代需要适配、合法值校验和回退。<br>**可扩展基础：** 可观察的状态、有限合法选项、明确判断标准、确定的执行方式、失败回退和结果验收齐备时，可扩展到证据充分性、技能选择、重试升级和交付检查。<br>**对我的意义：** 书籍写作按阶段配置模型；导览播放与同步保留代码，新联动需求再判断；RAG 判断证据覆盖；Leak Check 精确流程保留规则。先验证已有材料整理能否稳定交给便宜执行模型。<br>**价值怎么证实：** 比较固定模型、规则、规则 + Jev、规则 + 小模型四条完整流程，查看最终通过率、误降级、判断与重试升级总费用、耗时、返工和维护；路由标签准确不等于成果合格。<br>**边界与验证：** 源码职责与默认策略已核对，中文网页、完整理解图与评测表已部署，线上资源及交互已验证；未调用真实 Jev 或执行模型，未证明个人任务中的准确率与费用优势。<br><br>多模型路由 · 有限决策 · 判断标准 · 模型替换 · 评测 | [hermes-jev-skills](https://github.com/kerpopule/hermes-jev-skills)<br>kerpopule | 研究中 | [研究文档](./projects/007-hermes-jev-skills/README.md)<br>[在线演示](https://yydshly.github.io/1013_codex_project/007-hermes-jev-skills/#understanding) |
| **008** | **[shadPS4：PS4 模拟原理、系统知识与实践价值研究](./projects/008-shadps4/README.md)**<br><br>**定位：** 运行在电脑操作系统上的 C++ PS4 模拟器核心；PS4 是含硬件与系统的设备，手柄是输入设备，常用图形启动器由独立 QtLauncher 提供。<br>**能力：** 加载兼容 PS4 游戏或公开自制程序，安排游戏内存与执行入口，提供不同程度的系统库、图形转换、输入音视频和调试支持；借助主机系统与驱动使用实际 CPU / GPU，完整性依内容与版本。<br>**原理：** 加载与链接 → x86-64 主机大量原生执行及差异修补；系统兼容层处理 PS4 请求，PM4 命令解析与 GCN → IR → SPIR-V 着色器重编译组织 Vulkan 绘图，同时管理数据同步、资源与缓存。<br>**输入输出：** 输入游戏转储或自制可执行程序、所需模块、配置和玩家操作；输出运行画面、声音及调试日志。网页教学动画由浏览器绘制，不执行 PS4 游戏。<br>**研究展示：** 提供十一章中文导读，完整 SVG / PNG 一图总览与简化流程、三个请求流程与两类失败示例、缓存教学、理解核对、官方案例链接及二十二列实测记录表。<br>**实际验证：** 官方 v0.19.0 Windows 包摘要核对与 CLI 帮助通过；OpenOrbis v0.5.3 Hello World 真实执行，graphics 显示 CPU 生成的 Mandelbrot 分形，保存目标窗口截图、日志和可复现脚本。<br>**验证边界：** 已验证公开 homebrew 的 CPU / 部分 HLE、帧缓冲和 Vulkan 呈现，未证明 GCN 着色器重编译、商业游戏、3D 性能、音频或长时间稳定性；没有实体 PS4 主机对照。<br>**价值：** 使用价值是为部分 PS4 内容提供电脑运行路径；知识价值是把体系结构、操作系统、编译器、图形与并发联系起来；工程价值是理解跨平台行为兼容、证据诊断和回归验证。<br>**对你的意义：** 补充研究库的系统工程样本，建立概念 → 调用链 → 源码 → 最小实测 → 局限的研究方法，提升项目能力判断与问题定位；可探索源码和日志助手，对日常 AI / 资料自动化的直接收益较少。<br>**扩展方向：** 按难度从中文知识索引、兼容性回归工作台、日志分析助手，到着色器调试、系统库与同步修复、图形兼容和缓存优化；均明确验收条件，属于后续提议。<br>**复现环境：** Windows 11、i9-13980HX、16GB 内存、RTX 4070 Laptop、NVIDIA 576.28 / Vulkan 1.4.303；本次使用进程级 NVIDIA 驱动筛选，未使用 Sony 系统模块。源码研究提交与运行包提交分别记录。<br>**网页状态：** 本地中文网页已制作；统一静态子路径为 008-shadps4。公网尚未部署，在线地址保持为空，验证结果记录在子项目中。<br><br>PS4 模拟器 · 系统兼容 · 原生执行 · GPU · 编译器 · 公开示例实测 | [shadPS4](https://github.com/shadps4-emu/shadPS4)<br>shadps4-emu | 研究中 | [研究文档](./projects/008-shadps4/README.md)<br>演示未部署 |

## 项目引导图

引导图独立展示在索引表外。点击图片进入研究文档，图片说明保留其内容与来源。

### 001 · Infinite Bookshelf：写书流程、能力与价值研究

[![本次研究解释图：输入、流程、输出、能力、价值与局限；非原版运行截图](./projects/001-infinite-bookshelf/assets/03-understanding-overview.png)](./projects/001-infinite-bookshelf/README.md)

图片说明与来源：本次研究解释图：输入、流程、输出、能力、价值与局限；非原版运行截图

[查看原图](./projects/001-infinite-bookshelf/assets/03-understanding-overview.png) · [研究文档](./projects/001-infinite-bookshelf/README.md) · [在线演示](https://yydshly.github.io/1013_codex_project/001-infinite-bookshelf/)

### 002 · Production Agentic RAG Course：论文助手与工程架构研究

[![本仓库理解总览图：定位、价值、能力、原理与架构、场景、使用路线、扩展与验证；直接绘制，非上游运行截图](./projects/002-production-agentic-rag-course/assets/04-rag-understanding.png)](./projects/002-production-agentic-rag-course/README.md)

图片说明与来源：本仓库理解总览图：定位、价值、能力、原理与架构、场景、使用路线、扩展与验证；直接绘制，非上游运行截图

[查看原图](./projects/002-production-agentic-rag-course/assets/04-rag-understanding.png) · [研究文档](./projects/002-production-agentic-rag-course/README.md) · [在线演示](https://yydshly.github.io/1013_codex_project/002-production-agentic-rag-course/)

### 004 · Leak Check：个人信息泄漏查询与关联原理研究

[![本次生成的能力、数据库查询原理与个人价值汇总图；AI 信息图，非运行截图，源码依据见项目 README](./projects/004-leak-check/assets/research-summary.png)](./projects/004-leak-check/README.md)

图片说明与来源：本次生成的能力、数据库查询原理与个人价值汇总图；AI 信息图，非运行截图，源码依据见项目 README

[查看原图](./projects/004-leak-check/assets/research-summary.png) · [研究文档](./projects/004-leak-check/README.md)

### 005 · WireGuard Install：自建 VPN、原理与应用研究

[![本次研究原创理解总览图：自建 VPN 的部署、两端 IP 隧道与 UDP 加密封装、网关转发、使用场景及个人价值；依据固定源码与官方协议绘制，非运行实测](./projects/005-wireguard-install/assets/understanding-map.svg)](./projects/005-wireguard-install/README.md)

图片说明与来源：本次研究原创理解总览图：自建 VPN 的部署、两端 IP 隧道与 UDP 加密封装、网关转发、使用场景及个人价值；依据固定源码与官方协议绘制，非运行实测

[查看原图](./projects/005-wireguard-install/assets/understanding-map.svg) · [研究文档](./projects/005-wireguard-install/README.md) · [在线演示](https://yydshly.github.io/1013_codex_project/005-wireguard-install/)

### 006 · Jev SEO：网页质量检查规则与自有模型审查框架

[![本仓库基于固定源码研究、使用 imagegen 生成的理解总览图：能力、原理、52 条规则与 19 个模型维度、定制排查、模型替换、场景、价值与边界；2026-10-14，非上游或真实网站实测截图](./projects/006-jev-seo/assets/04-jev-seo-understanding.png)](./projects/006-jev-seo/README.md)

图片说明与来源：本仓库基于固定源码研究、使用 imagegen 生成的理解总览图：能力、原理、52 条规则与 19 个模型维度、定制排查、模型替换、场景、价值与边界；2026-10-14，非上游或真实网站实测截图

[查看原图](./projects/006-jev-seo/assets/04-jev-seo-understanding.png) · [研究文档](./projects/006-jev-seo/README.md) · [在线演示](https://yydshly.github.io/1013_codex_project/006-jev-seo/)

### 007 · Hermes Jev Skills：多模型路由与判断标准研究

[![本次讨论的 Jev 与多模型路由总览图：能力、原理、场景、标准与扩展；AI 生成研究说明，非上游截图，个人方案待验证](./projects/007-hermes-jev-skills/assets/04-understanding-overview.png)](./projects/007-hermes-jev-skills/README.md)

图片说明与来源：本次讨论的 Jev 与多模型路由总览图：能力、原理、场景、标准与扩展；AI 生成研究说明，非上游截图，个人方案待验证

[查看原图](./projects/007-hermes-jev-skills/assets/04-understanding-overview.png) · [研究文档](./projects/007-hermes-jev-skills/README.md) · [在线演示](https://yydshly.github.io/1013_codex_project/007-hermes-jev-skills/#understanding)

### 008 · shadPS4：PS4 模拟原理、系统知识与实践价值研究

[![本仓库整理的 shadPS4 全面理解图：资源控制边界、能力、加载与执行原理、价值、扩展方向、个人意义及公开样例实测范围；非上游截图。](./projects/008-shadps4/assets/comprehensive-map.svg)](./projects/008-shadps4/README.md)

图片说明与来源：本仓库整理的 shadPS4 全面理解图：资源控制边界、能力、加载与执行原理、价值、扩展方向、个人意义及公开样例实测范围；非上游截图。

[查看原图](./projects/008-shadps4/assets/comprehensive-map.svg) · [研究文档](./projects/008-shadps4/README.md)

<!-- PROJECT_INDEX:END -->

## 收录与阅读方式

- **先看索引**：了解项目用途、研究进度与演示入口。
- **再读子项目**：查看选择理由、环境配置、源码分析、截图说明与研究结论。
- **保留来源**：记录原仓库、研究时的版本或 commit，以及上游许可证。
- **积累实践**：将实验代码放在对应子项目中，区分上游功能与本仓库的改动。

研究状态：`待研究` → `研究中` → `已复现` → `已完成`，停止维护的项目标记为 `已归档`。状态可按实际进度调整。

## 目录结构

```text
1013_codex_project/
├── README.md                 # 对外总览：索引、分项摘要、源库和导航
├── AGENTS.md                 # 后续研究与维护的工作约定
├── projects/                 # 001-xxx、002-xxx…，每个目录一个研究项目
├── templates/project/        # 子项目文档、元信息和图片占位模板
├── docs/deployment.md        # 多个 Web 演示的路径与部署约定
├── scripts/                  # 创建子项目、生成并校验索引
├── tests/                    # 索引与创建工具的行为检查
└── .github/workflows/        # 自动检查项目结构与索引同步
```

## 添加第一个项目

需要 Python 3.10 或更高版本，无需安装第三方依赖。将下面的示例名称和原仓库地址替换为实际项目：

```bash
python scripts/new_project.py example-project --name "项目名称" --source "https://github.com/owner/repository" --summary "这个项目解决什么问题，以及本次研究的重点。"
```

工具会分配下一个编号，创建 `projects/001-example-project/`，复制研究模板，并更新本页索引。

后续修改子项目的 `project.json` 后，执行：

```bash
python scripts/update_index.py
python scripts/update_index.py --check
```

编号从 `001` 开始，保持稳定，不随研究状态变化而重排。图片放在各子项目的 `assets/` 中，Web 演示代码放在各子项目的 `web/` 中。详细规则见 [新增项目指南](./CONTRIBUTING.md)。

## Web 演示

预留同一站点下的独立路径，例如 `/1013_codex_project/001-example-project/`。每个子项目可选择适合自己的技术栈；有可访问的演示后，将实际地址写入 `project.json` 的 `demo_url`，索引便会显示入口。

静态演示通过 GitHub Actions 汇集到 [GitHub Pages 站点](https://yydshly.github.io/1013_codex_project/)，各子项目使用独立路径。线上页面展示研究说明与可公开的样稿；需要模型接口或私密凭据的功能使用单独后端。发布步骤和验证范围见 [Web 部署约定](./docs/deployment.md)。

## 来源与使用

各子项目应注明原作者、原仓库、研究版本和许可证。引用的源码、图片及其他素材遵循各自的上游许可；本仓库目前未设置统一开源许可证。
