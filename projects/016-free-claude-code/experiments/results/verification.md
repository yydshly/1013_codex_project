# 验证记录 · 2026-10-14

## 范围与环境

目标：读者浏览中文导读，切换 Agent 与模型教学示例，查看六步请求往返、备用条件和问答，下载原创总览图与空白评测表。

- 操作系统：Windows，本仓库研究工作区。
- 网页：无第三方运行与构建依赖的 HTML / CSS / JavaScript。
- 静态构建：仓库 `scripts/build_site.py`，显式选择 `016-free-claude-code`，输出到被忽略的 `site-fcc-preview/`。
- 本地服务：Python 3.10.11 标准库 HTTP 服务，限定 `127.0.0.1`；首次测试使用 8875，提交前在独立发布工作区复核地址 `http://127.0.0.1:8876/016-free-claude-code/`。
- 浏览器检查：工作区自带 Playwright / Chromium；桌面 1440×1050、手机 390×844、完整总览 SVG 1600×2460、底层 SVG 1600×1320，启用减少动画设置。
- 上游要求另行记录：固定版本 pyproject.toml 要求 Python 3.14.7，本次没有安装该上游环境、运行 FCC、Agent 或模型。

## 实际验证

| 项目 | 结果与证据 |
| --- | --- |
| 子项目静态构建 | 成功收集本项目，未将其他未跟踪项目加入本次预览 |
| HTML 与资源 | 页面、CSS、JS、两张 SVG / PNG 和评测表下载资源 HTTP 200 |
| 完整正文 | 单一 h1、十五个有锚点的章节，章节导航和固定版本来源及既有项目对比可用 |
| 六步请求流程 | 发请求、选目标、适配调用、响应转换、工具执行和结果回传可切换，重置正常 |
| Agent 切换 | Claude Code 显示 Messages；Codex 显示 Responses 和对应教学字段 |
| 模型切换 | 云端、本地和自定义示例改变目标；没有实际模型调用 |
| 备用条件 | 显示主模型不可用前提、教学备用目标及恢复边界说明 |
| 问答与下载 | 问答展开；两图 PNG / SVG 与空白 CSV 下载成功，保存文件名正确 |
| 手机布局 | 390px 下无全页横向溢出；流程可用，大图可放大并双向滚动；表格在自身容器横向滚动 |
| 无 JavaScript | 正文、源码链接和完整原理说明仍可直接阅读 |
| 本地 HTML | 保存的 HTML 可以直接打开，静态正文不依赖预览服务 |
| 浏览器错误与外部请求 | 无浏览器脚本错误；检查期间仅访问本地静态资源，没有模型或其他外部请求 |
| 总索引 | 已运行 update_index.py；最终 --check 通过 |
| 仓库工具测试 | 35 项测试完成，34 项通过、1 项跳过；跳过原因是当前 Windows 用户不能创建符号链接 |

机器检查结果见 [browser-checks.json](./browser-checks.json)，检查脚本为 [verify_web.cjs](../verify_web.cjs)。下载评测表的静态承载文件是 TXT 扩展名的 CSV 内容，浏览器按下载属性保存为 `fcc-evaluation-template.csv`；这样遵循现有构建白名单，无需修改构建工具。

## 补充理解与图示验证

本次把“统一地址 → 协议适配 → 接入解耦 → 模型服务可替换”的理解写入首屏、正文、元信息和总索引；保留三方职责及能力差异。新增 FreeLLMAPI、Agenvo、Hermes Jev、cmux / Vibe42 的固定版本对比。

发布前补充能力、原理、价值和可扩展场景四问摘要；详细列出多模型编程、写作与报告、资料问答、网页审查、任务选模和团队入口六类组合的网关职责、建设前提与验收标准。元信息保留十五项分段摘要，索引生成后完整展示，未压缩成仅有项目名称的介绍。

- 完整总览图：1600 × 2460，PNG / SVG 同源，覆盖能力、原理、价值、意义、场景、扩展与边界。
- 底层模块图：1600 × 1320，说明代理入口、配置路由、适配、供应商调用、响应返回与 Agent 工具循环。
- SVG 浏览器文字边界检查通过，PNG 与 SVG 的导出排版已目视检查。
- 两张大图都能打开阅读器、放大、缩小、适应宽度、滚动与关闭；桌面键盘 Escape 退出通过。
- 图片下载、390px 手机阅读、原有请求流程、禁用脚本后的正文与图片链接均通过。
- 图示可复现源码：[draw_understanding.py](../draw_understanding.py)、[render_diagrams.cjs](../render_diagrams.cjs)。

## 图片与来源

- [01-web-overview.png](../../assets/01-web-overview.png)：本研究网页桌面首屏实拍。
- [02-request-flow.png](../../assets/02-request-flow.png)：Codex、本地模型与教学备用条件的流程实拍；为完整展示章节，捕获时隐藏导航与跳转链接。
- [03-mobile-overview.png](../../assets/03-mobile-overview.png)：390×844 手机视口首屏实拍。
- [04-overview-render.png](../../assets/04-overview-render.png)：原创理解 SVG 的浏览器渲染。
- [understanding-overview.svg](../../assets/understanding-overview.svg) / [PNG](../../assets/understanding-overview.png)：原创完整理解图，非上游运行截图。
- [gateway-internals.svg](../../assets/gateway-internals.svg) / [PNG](../../assets/gateway-internals.png)：原创底层概念模块图。
- [05-gateway-internals-page.png](../../assets/05-gateway-internals-page.png)：网页底层章节实拍。
- [06-mobile-diagram-reader.png](../../assets/06-mobile-diagram-reader.png)：手机放大阅读与滚动状态实拍。
- [07-public-extensions.png](../../assets/07-public-extensions.png)：公开网页六类应用扩展表实拍，深色文字与浅色背景的对比度约 11.81:1；390px 表格滚动和整页布局均通过。

图片最初来自本地研究页面或原创图示；发布时以同一检查脚本在实际公开网页重新捕获 01—06，图示内容保持一致。图为原创解释，页面截图不代表真实 FCC 或模型运行。

## 未验证事项

上游安装与启动、真实客户端集成、各供应商资格与免费额度、长上下文和图像、工具调用质量、断流及备用效果、真实账单、RTK / Headroom、消息与语音，以及任务完成质量和降本收益都未实测。

网页已完成公网发布与资源一致性、桌面和手机交互验证，`demo_url` 在实际访问通过后登记。网页可用、仓库校验通过，与上游运行或实际模型收益通过验证，是不同结论。

## 公网发布

公开网址为 https://yydshly.github.io/1013_codex_project/016-free-claude-code/ 。内容提交、Pages 工作流、公开资源和浏览器验证见 [发布记录](./publication-2026-10-14.md)、[资源一致性 JSON](./publication-content.json)及[公网浏览器 JSON](./publication-browser.json)。
