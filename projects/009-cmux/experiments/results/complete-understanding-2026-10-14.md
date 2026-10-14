# 完整理解总图制作与验证

用户要求一张图全面汇总“承接已有 Agent 工具，UI 展示与交互，同时控制多个”，以及能力、原理、效果、接入方式与个人意义。

## 最终成果

- 项目图：`assets/07-complete-understanding.png`，2400 × 3700，RGB。
- 同内容矢量图：`assets/07-complete-understanding.svg`。
- 网页副本：`web/assets/complete-understanding.png` 与 `.svg`。
- 绘制脚本：`experiments/draw-complete-understanding.py`，Pillow + 原创形状 / 文本，同步生成 SVG。
- 可查阅文字：`assets/07-understanding-content.txt`。

内容覆盖分工与架构、独立 Agent 进程、四条通道、操作效果、八项能力、四级接入、场景、个人价值、扩展与关键边界。根据同一研究基准 `cdbe99596fe13784ec5ea24d2e1c720a8f67f5cb`，不增加已实现功能的承诺。

## 制作方式与核对

先尝试内置图像生成工具，两次均返回网络发送错误，未产生可用图片。没有切换到需要用户密钥的 CLI API 路径。随后直接绘制研究图，最终成果不是 AI 图片；保留 `assets/07-image-prompt.txt` 记录尝试时的内容与约束。

已按原图检查整体内容，并放大检查四条通道与接入步骤。修正 Microsoft YaHei 对双向箭头的缺字，PNG 用 Segoe UI Symbol 绘制箭头。绘制脚本检查文字横向边界与模块纵向范围；关键措辞区分 Agent 执行、工作台控制和上层验收。

图中 UI 为教学示意，非上游运行截图。未运行 macOS 客户端或真实 Agent。项目元信息、README 与网页均记录图片出处；元信息的首页引导图已指向完整 PNG，原简版 SVG 与架构详图保留。

## 本次验证结果与限制

- 完整 PNG / SVG 与网页副本逐字节一致；原图 2400 × 3700，已实际查看并检查放大区域。
- 静态检查通过：10 章、20 来源锚点、98 个资源 / 引用，包含完整图与原图下载。
- 网页 JavaScript 语法检查通过，交互逻辑未改动。
- 仓库测试 35 项，34 通过、1 因当前 Windows 符号链接不可用跳过。
- 显式 `--project 009-cmux` 静态构建通过，完整 PNG / SVG HTTP 请求成功；这不是公网部署。
- 索引生成与 `--check` 当前失败：共享工作区同时存在 `015-free-claude-code` 与 `015-rea`，编号重复。未改动这两个项目；根 README 仍保留上次生成内容，新完整图的自动索引更新待编号问题解决后运行。
- 本次调用内置浏览器工具查看更新页面时被其 URL 策略拒绝，未重测新图片在浏览器中的实际布局；使用原图视觉检查、静态资源检查和本地 HTTP 请求验证。本次未通过其他浏览器方式绕过该拒绝。
