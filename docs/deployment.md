# 多个 Web 演示的部署约定

## 站点结构

多个子项目的静态 Web 演示统一发布到仓库的 GitHub Pages 项目站点，每个项目使用独立路径。首页索引表单列“目标源库”，以源库名称链接到研究目标；引导图在表格下方的独立图片区展示，每图附名称、说明、来源与原图入口。元信息含 `summary_sections` 时，按能力、原理、输入、输出、价值、意义与场景、边界与验证分项展示；旧项目仍完整展示 `summary`，不截断、不折叠摘要。手机按项目纵向排列，详情页也保留总览图和样稿。依据：[GitHub Pages 官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)。

```text
https://yydshly.github.io/1013_codex_project/
├── index.html
├── 001-infinite-bookshelf/
├── 002-another-project/
└── ...
```

这是地址约定。某个项目是否实际发布，以它的 `project.json` 中经过验证的 `demo_url` 和发布记录为准；部署脚本或工作流的存在不等于发布成功。

没有公开源码的产品可显式登记 `source_type: "website"` 与真实官网。混合索引的来源栏使用“研究来源”，网站项目标记为公开资料研究，首页也不把整个列表概括为开源产品。此来源类型不会改变发布范围、独立子路径或 `demo_url` 的验证要求。

## 当前已验证发布

2026-10-13，已启用仓库 GitHub Pages 的 Actions 发布方式，首次部署提交为 `8d12bcc46c753c9ddc30c8b95f32fa92ecd29013`，[构建与部署运行](https://github.com/yydshly/1013_codex_project/actions/runs/38393707526)以及索引检查均成功。

- [站点总览](https://yydshly.github.io/1013_codex_project/)：完整展示已提交项目的能力、原理、输入输出、价值、意义与局限摘要。
- [001 Infinite Bookshelf](https://yydshly.github.io/1013_codex_project/001-infinite-bookshelf/)：详细研究、一图总览、摄影与电商样稿、回放和文件下载。
- [002 Production Agentic RAG Course](https://yydshly.github.io/1013_codex_project/002-production-agentic-rag-course/#understanding)：完整理解摘要、一图总览、原理架构、适配场景、使用路线、PNG / SVG 下载与后续验证；静态导读未连接真实 RAG 后端。
- [摄影入口](https://yydshly.github.io/1013_codex_project/001-infinite-bookshelf/?sample=photography#workbench)：摄影样稿参数可用于直接阅读。

首页、项目页、摄影入口、CSS、JavaScript、总览 PNG、两份 JSON 和首页预览图已实际请求，均返回 HTTP 200；项目静态文件 SHA-256 与远端提交 blob 一致。页面新版浏览器交互尚未重测，当前发布不包含自动生成新主题所需的模型服务。完整范围见 [发布验证](../projects/001-infinite-bookshelf/experiments/results/verification.md#公网静态发布验证)。

项目 002 于 2026-10-13 随提交 81f224c 发布，[构建与部署运行](https://github.com/yydshly/1013_codex_project/actions/runs/38418966428)成功。首页完整保留 12 项摘要并使用本次生成的理解总览图；项目页、CSS、JavaScript、PNG、SVG、首页引导图和项目 001 入口均 HTTP 200，资源与对应提交 blob 一致。验证详情见 [项目 002 公网发布记录](../projects/002-production-agentic-rag-course/experiments/results/publication-2026-10-13.md)。

项目 007 于 2026-10-14 随提交 `cc171f4bf3b096b4c4d45930b856af049d9ba5a0` 发布，[构建与部署运行](https://github.com/yydshly/1013_codex_project/actions/runs/38428497187)成功。[Hermes Jev Skills 理解网页](https://yydshly.github.io/1013_codex_project/007-hermes-jev-skills/#understanding)说明库的能力、Jev 的判断作用与位置、默认路由机制、个人扩展、判断标准、规则与小模型选择、使用价值及扩展基础。首页保留十二项完整摘要与表外引导图。项目页、CSS、JS、PNG、首页、已有 001 / 002 入口和构建清单均 HTTP 200，内容与提交一致；公网示例、CSV 下载与返回入口已实际验证。教学网页未接入真实 Jev 或执行模型。详见 [项目 007 发布记录](../projects/007-hermes-jev-skills/experiments/results/publication-2026-10-14.md)。

项目 005 于 2026-10-14 随提交 `393ea14b713595e994fe5a3ed46bcfab08d91e34` 发布，[构建与部署运行](https://github.com/yydshly/1013_codex_project/actions/runs/38433870276)成功。[WireGuard Install 理解网页](https://yydshly.github.io/1013_codex_project/005-wireguard-install/)明确说明自建 VPN 的能力、UDP 加密 IP 隧道与网关转发原理、两端职责、部署方法、个人价值、使用场景及扩展方向。首页保留九项完整摘要并使用本次研究生成的完整原理图；10 项公开资源均 HTTP 200，内容与提交或构建快照一致，公网交互已验证。静态网页发布不等于真实 VPN 服务部署，详细范围见 [项目 005 发布记录](../projects/005-wireguard-install/experiments/results/publication-2026-10-14.md)。

项目 006 于 2026-10-14 随提交 `8edf844d3830a0994805c5d57db461bdf8f8f492` 发布，[构建与部署运行](https://github.com/yydshly/1013_codex_project/actions/runs/38436528319)成功。[Jev SEO 规则与模型审查导读](https://yydshly.github.io/1013_codex_project/006-jev-seo/)明确定位为网页质量检查的基础框架，并说明还需补充实际交互、手机布局、无障碍、业务功能和后端检查。完整展示 52 条规则、19 个模型维度、参考提取、定制方法、8 类场景、能力与价值；首页与详情页沿用本次生成的理解总览图。15 个公开地址均 HTTP 200，9 个项目资源与提交 blob 一致，公网规则检索、清除、回跳及图片加载已验证，全部已有演示入口保留。静态网页发布不证明真实审查或模型效果；详见 [项目 006 发布记录](../projects/006-jev-seo/experiments/results/publication-2026-10-14.md)。

项目 008 于 2026-10-14 随提交 `1cda73485ccfe63e7862403387ae5b5d3363c478` 发布，[构建与部署运行](https://github.com/yydshly/1013_codex_project/actions/runs/38443817551)成功。[shadPS4 理解网页](https://yydshly.github.io/1013_codex_project/008-shadps4/)完整说明能力、加载与执行原理、资源控制边界、学习与工程价值、个人意义及可扩展方向。首页完整保留十二项摘要，并沿用本次讨论整理的完整总览图；19 个公网地址均 HTTP 200，项目资源与对应提交一致，11 项公网浏览器检查通过，已有五个演示入口保留。公开样例的本机原生执行与网页教学分别记录，商业游戏与完整 3D 渲染尚未验证；详见 [项目 008 发布记录](../projects/008-shadps4/experiments/results/publication-2026-10-14.md)。

项目 009 于 2026-10-14 随提交 `4a7ec58c8f3e8b3c2d59833a656842973f1b6821` 发布，[构建与部署运行](https://github.com/yydshly/1013_codex_project/actions/runs/38490130025)成功。[cmux 理解网页](https://yydshly.github.io/1013_codex_project/009-cmux/#understanding)明确说明多个现有 Agent 会话进入一个工作台，分屏展示、独立交互、定向控制、并行工作，使一个人能控制多个 Agent；完整整理能力、价值、扩展方向和实现思路，保留高清总图与教学交互。首页保留十二项完整摘要。17 个公网资源及已有六个网页入口均 HTTP 200，内容与构建快照一致；公网定向输入、消息教学、PNG 下载与索引摘要已实际检查。网页未连接真实 Agent，详见 [项目 009 发布记录](../projects/009-cmux/experiments/results/publication-2026-10-14.md)。

项目 014 于 2026-10-14 随内容提交 `f8682c7a7d3010cb368bcaa8920b33db8acc1233` 发布，[构建与部署运行](https://github.com/yydshly/1013_codex_project/actions/runs/38517467344)成功。[BaoCut 理解网页](https://yydshly.github.io/1013_codex_project/014-baocut/)完整说明视频能力、Node Runtime 与 Rust 视频引擎的执行分工、人通过 UI 与 AI 工具调用共同修改当前项目的原理，以及新增设计模块、实际价值、个人意义和八种可扩展场景。首页完整保留 18 项摘要，沿用本次讨论的完整高清引导图；22 个公开地址通过，11 项内容与静态快照一致，11 个已有演示入口保持可用，公开协作教学、撤销、重置、下载和手机布局已验证。网页不执行真实视频引擎或模型，登记后的最终证据见 [项目 014 发布记录](../projects/014-baocut/experiments/results/publication-2026-10-14.md)。

项目 014 正式入口登记提交为 `4512d8fa160bdef3bab8722c455bb9df5a5af257`，[登记后的工作流](https://github.com/yydshly/1013_codex_project/actions/runs/38518228836)成功。最终 22 个公开地址、内容一致性和 18 项完整摘要再次通过，原理解图与 11 个已有演示入口保持可用，详见项目 014 发布记录。

子项目静态源文件保存在 `projects/编号-slug/web/`。`scripts/build_site.py` 使用 Python 标准库，将可发布的原生静态项目汇集为一个完整站点：

```text
site-dist/                   # 临时构建目录，不提交到 Git
├── index.html               # 索引表、源库栏、分项摘要与表格外的引导图区
├── .nojekyll
├── site-build.json          # 生成标记及本次包含的项目目录
├── previews/               # 首页表格外展示的各项目引导图
├── 001-infinite-bookshelf/  # 该项目 web/ 的公开静态文件
└── ...
```

项目 010 于 2026-10-14 随提交 `3249f63e953cc1c8b1c5090eacfd291a8f404306` 发布，[构建与部署运行](https://github.com/yydshly/1013_codex_project/actions/runs/38495097071)成功。[Vibe42理解网页](https://yydshly.github.io/1013_codex_project/010-vibe42/#understanding)完整说明远程操作Agent的能力、Companion/配对/加密连接/PTY与原生Agent执行原理、观察确认接手的价值及研究/RAG、原生接口、恢复、团队和产物验收的建议扩展。首页保留17项完整摘要，页面同步6项关键说明，沿用完整理解图和原理交互。12项项目资源、引导图及首页/清单已实际访问并核对；7个已有演示入口保持HTTP 200，6组公网浏览器检查通过。真实Vibe42产品尚未安装或配对，详见[项目010发布记录](../projects/010-vibe42/experiments/results/publication.md)。

## 构建与发布范围

项目 013 于 2026-10-14 随内容提交 `42f8398f0db99b0f8870ff42ccbc9bc7ddcde1b1` 发布，[构建与部署运行](https://github.com/yydshly/1013_codex_project/actions/runs/38514399743)成功。[Claude Managed Agents 理解网页](https://yydshly.github.io/1013_codex_project/013-claude-managed-agents/)明确说明多 Agent 编排与运行管理的能力、模型规划与程序执行原理、核心价值、个人意义及八种扩展场景，包含拆分、下发、黑盒接口和海底世界案例。首页完整保留 18 项摘要，沿用本次讨论的完整高清总览图。19 个公开地址 HTTP 200 且内容一致，13 组公网浏览器检查通过，已有 10 个演示入口保留；网页不执行真实 Agent 或 3D 场景。正式入口登记与后续检查见 [项目 013 发布记录](../projects/013-claude-managed-agents/experiments/results/publication-2026-10-14.md)。

项目 013 正式入口登记提交为 `31df444e218b51d64b85faf137f6a5adf62c7b41`，[登记后的工作流](https://github.com/yydshly/1013_codex_project/actions/runs/38515132055)成功。19 个公开资源的实际访问和内容一致性再次通过；完整摘要、原高清引导图和全部已有演示入口保持可用，详见项目 013 发布记录。

项目 012 于 2026-10-14 随内容提交 `4d40a06c72d223dd60140e531f69a044744bcaca` 发布，[构建与部署运行](https://github.com/yydshly/1013_codex_project/actions/runs/38512370698)成功。[tchMaterial Parser 理解网页](https://yydshly.github.io/1013_codex_project/012-tchmaterial-parser/)完整说明不同版本小学教材下载与整理能力、官方来源与节点、认证下载原理、操作便利、价值与场景、六项扩展场景及实现前提。首页完整保留 16 项摘要并沿用本次讨论的完整理解图；首次 18 个公网地址与 25 项浏览器检查通过，已有九个网页入口保留。网页不执行教材下载或模型请求；正式入口登记与最终证据见[项目 012 发布记录](../projects/012-tchmaterial-parser/experiments/results/publication-2026-10-14.md)。

项目 012 正式入口登记提交为 `dd312b54a573d4d7b68a3ccd4b2d64c05b005a8a`，[登记后的工作流](https://github.com/yydshly/1013_codex_project/actions/runs/38512835233)成功。最终 18 个公开地址与内容一致性再次通过，完整 16 项摘要及原理解图保留，详见项目 012 发布记录。

项目011正式入口登记提交为 `06ed87fd610618df067a9d90f612470d6577ad15`，[对应运行](https://github.com/yydshly/1013_codex_project/actions/runs/38498026649)成功；登记后21个公开地址和20组公网浏览器检查再次通过，18项最终摘要完整存在，证据见项目011发布记录。

项目 011 于 2026-10-14 随内容提交 `ba8980a123bd00fed7d3fd98dbeafd1ee986555a` 发布，[构建与部署运行](https://github.com/yydshly/1013_codex_project/actions/runs/38497224736)成功。[OpenMontage 理解网页](https://yydshly.github.io/1013_codex_project/011-openmontage/#brief)明确说明视频制作能力、助手/模型/检索/代码/规则分工、阶段成果交接、核心价值、适用与扩展场景，保留完整图、34项能力、12条流程、11项项目对比和教学交互。首页完整展示18项摘要；首轮21个公网地址及20组公网交互通过，已有八个演示入口保留。网页不执行上游制作或请求模型，正式入口登记和最终证据见[项目011发布记录](../projects/011-openmontage/experiments/results/publication-2026-10-14.md)。

默认构建只读取 Git 已跟踪的 `projects/*/project.json`，只复制其中已跟踪的 `web/` 静态文件和元信息明确指定的预览图片。工作区中新建但尚未提交的其他研究项目不会被意外收录。Git 暂存区中的新增文件也属于本地已跟踪文件；GitHub Actions 运行时只有实际提交并检出的文件。

```powershell
# 正式发布使用此默认方式：收集全部已跟踪的静态演示
python scripts/build_site.py

# 新项目尚未提交时，显式选择本地预演；可重复 --project
python scripts/build_site.py --project 001-infinite-bookshelf

# 可另建一个仓库内的 site-* 临时产物目录
python scripts/build_site.py --project 001-infinite-bookshelf --output site-preview

# 本地查看构建产物；静态服务不提供模型 API
python -m http.server 8767 --bind 127.0.0.1 --directory site-dist
```

`--project` 用于本地验证，正式 Pages 工作流不使用该筛选参数。每次发布都重新收集全部已跟踪静态演示，保持其他项目入口；已有 `demo_url` 的项目缺少可发布的 `web/index.html` 时，构建会失败，避免悄悄丢失入口。未部署且没有静态页面的研究项目保留在仓库索引中，不加入网页演示列表。归档项目若仍保留静态文件，也继续发布。

构建只允许替换仓库内直接命名为 `site-*` 的生成目录。已有非空目录必须带有 `site-build.json` 生成标记，脚本才会替换；构建成功前不会删除上次产物。

## 公开文件与资源路径

- 仅复制 `web/` 内的 HTML、CSS、JavaScript、JSON、公开 TXT、常用图像、字体、音视频和 PDF。Markdown 研究文档与 Python 等源码不作为网页产物复制；导航链接指向 GitHub 研究文档。
- 隐藏文件、`.env`、密钥文件、依赖目录、后端与私有目录、源码映射、已知凭据文件被排除。`experiments/`、`references/` 和其他项目文件完全不进入网页产物。
- `web/` 是公开前端目录；不得把任何私密内容放在其中。静态白名单不是对任意文件内容的自动密钥审计。
- 引导图资源只从项目元信息的 `preview` 取一张明确图片，不将整个项目 `assets/` 目录发布；在首页索引表外独立展示，并保留 `preview_caption` 作为替代文本和来源说明。说明包含“占位”或“待添加”的图片不作为实际引导图展示。详情页自身所需总览图与截图资源应放在 `web/assets/`。
- 资源和项目链接使用相对路径，例如 `./app.js`、`./data/book.json`、`./assets/image.png`，适配 `/1013_codex_project/001-infinite-bookshelf/` 的仓库名前缀。
- 项目跳回站点总览使用 `../`；客户端路由使用 hash 或查询参数，避免静态托管刷新深层路径返回 404。
- 当前构建器直接汇集原生静态文件，不运行框架安装或打包。需要 React、Vite 等构建时，应先在明确的构建步骤产出经过审核的公开文件，再扩展汇集约定，不能把依赖和源码一并上传。

在 `web/README.md` 中记录依赖、运行方式、静态部署前缀、已验证功能和服务端限制。GitHub Pages 不运行 Python 后端、不存放模型密钥；真实模型请求需使用另外部署的后端。Infinite Bookshelf 的静态网页可展示研究说明、两份保存的 GPT 样稿、步骤回放和前端导出；回放不等于现场模型生成。

## GitHub Actions 工作流

`.github/workflows/pages.yml` 在 `main` 推送或手动触发时：

1. 检出已提交的仓库文件，使用 Python 3.12。
2. 校验 `project.json` 与根 README 自动索引，运行项目工具和静态发布隔离测试。
3. 构建任务使用 `contents: read` 与 `pages: read`，运行 `actions/configure-pages@v5` 读取已启用的 Pages 配置。
4. 默认收集全部已跟踪静态演示到 `site-dist/`。
5. 使用 `actions/upload-pages-artifact@v4` 上传站点产物。
6. 在依赖构建任务的 `deploy` 任务中，使用 `actions/deploy-pages@v4` 发布。该任务拥有 `pages: write`、`id-token: write` 权限，并使用 `github-pages` 环境。

首次发布前需在仓库 `Settings → Pages → Build and deployment` 将发布来源设为 `GitHub Actions`。Pages 专用上传动作 v4 不接受 `include-hidden-files`，会排除隐藏文件；本地产物中的 `.nojekyll` 不进入上传包也不影响本流程，因为 Actions 直接部署已经生成的静态产物，不再运行 Jekyll。动作定义依据：[upload-pages-artifact v4](https://github.com/actions/upload-pages-artifact/blob/v4/action.yml)。

本流程不在构建任务中自动创建 Pages 站点。`configure-pages` 默认 `enablement: false`，只读取站点配置；首次创建需仓库管理员事先完成。读取权限依据：[Pages REST API](https://docs.github.com/en/rest/pages/pages#get-a-github-pages-site)；动作默认参数依据：[configure-pages v5](https://github.com/actions/configure-pages/blob/v5/action.yml)。

工作流完成后，还应实际访问导航首页、项目页、样稿 JSON 和图片资源，确认子路径、资源和刷新可用，再填写 `demo_url` 并执行：

```powershell
python scripts/update_index.py
python scripts/update_index.py --check
python -m unittest discover -s tests -v
```

摘要与公开入口更新需要提交后重新发布，不能在尚未验证成功时预填“已部署”。GitHub 官方工作流说明和版本依据：[使用自定义工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。
