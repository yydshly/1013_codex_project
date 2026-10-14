# 中文研究网页

本目录为 Free Claude Code 的静态研究导读，强调共用代理 API、协议适配与真实模型的分工，并汇总能力、原理、免费额度、场景、个人价值、扩展、使用路线和源码证据。

## 内容与交互

- 能力、原理、价值与可扩展场景四问摘要；六类应用组合的网关职责、建设前提和验收标准。
- 六步请求往返，Claude Code / Codex 两种客户端协议示意。
- 云端、本地和自定义模型示例，主模型不可用时的教学备用条件。
- 工具调用与结果回传、问答展开、章节导航。
- 完整的适配解耦理解图与独立底层模块图，可放大、缩小、适应宽度、滚动阅读与关闭。
- 两张图均提供 PNG / SVG 下载，另有空白 CSV；没有模型请求或计费。
- FreeLLMAPI、Agenvo、Hermes Jev、cmux / Vibe42 的固定版本对比。
- 完整正文与源码链接不依赖 JavaScript；流程切换需要 JavaScript。

## 运行与构建

无需安装前端依赖或运行打包器。可直接打开 index.html 阅读；使用仓库站点的相对路径，以兼容实际发布前缀。

```powershell
python scripts/build_site.py --project 016-free-claude-code --output site-fcc-preview
python -m http.server 8875 --bind 127.0.0.1 --directory site-fcc-preview
```

查看 `http://127.0.0.1:8875/016-free-claude-code/`。上级 `../` 指向生成的总览页。本地服务只提供静态文件，不提供模型 API。

正式发布约定见 [deployment.md](../../../docs/deployment.md)。默认发布只收集已跟踪文件；本项目当前未发布，demo_url 为空，不将本地验证写成公网验证。

## 文件与依赖

- index.html：全面正文、源代码链接和交互结构。
- styles.css：桌面、手机、键盘焦点、减少动画与打印样式。
- app.js：本地固定数据的教学流程，没有 fetch 或模型请求。
- assets/understanding-overview.svg / .png：1600 × 2460 原创完整理解图。
- assets/gateway-internals.svg / .png：1600 × 1320 原创底层模块图。
- data/evaluation-template.csv：研究用原始空白表；TXT 同内容副本用于静态发布，下载保存为 CSV。现有构建白名单不收集 .csv，因此不更改公共构建工具。

## 已验证与限制

桌面和手机阅读、六步切换、模型和 Agent 示例、备用提示、问答、两种下载、资源、无 JavaScript 阅读、本地 HTML 以及仓库校验已检查。详情及截图见 [verification.md](../experiments/results/verification.md)，机器结果见 [browser-checks.json](../experiments/results/browser-checks.json)。

上游服务、真实模型、免费额度、生成质量、恢复与费用均未实测；本网页不输入或保存凭据，也不启动 Agent。

## 图示制作

`experiments/draw_understanding.py` 生成原创 SVG；`experiments/render_diagrams.cjs` 使用浏览器渲染 PNG并检查文字边界。两种格式分别保存于项目 assets/ 与公开 web/assets/，保持内容一致。图片基于固定源码和既有研究，不是上游运行截图。
