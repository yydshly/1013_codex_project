# cmux 公网发布与验证

2026-10-14，将“一个人同时控制多个现有 Agent 会话”的理解整理为网页，提交到远端 `main`，通过既有 GitHub Pages 工作流发布。

## 公开入口与版本

- [理解网页与完整总图](https://yydshly.github.io/1013_codex_project/009-cmux/#understanding)
- [项目首页](https://yydshly.github.io/1013_codex_project/009-cmux/)
- [站点索引](https://yydshly.github.io/1013_codex_project/)
- [高清 PNG](https://yydshly.github.io/1013_codex_project/009-cmux/assets/complete-understanding.png)、[可编辑 SVG](https://yydshly.github.io/1013_codex_project/009-cmux/assets/complete-understanding.svg)
- 首发提交：[`4a7ec58c8f3e8b3c2d59833a656842973f1b6821`](https://github.com/yydshly/1013_codex_project/commit/4a7ec58c8f3e8b3c2d59833a656842973f1b6821)
- [首发构建与部署运行 38490130025](https://github.com/yydshly/1013_codex_project/actions/runs/38490130025)：build / deploy 均 success。

首次公网访问与内容验证成功之后，再登记 `demo_url` 并更新发布记录和自动索引。

## 摘要与研究内容

索引完整保留十二项描述：本质、能力、架构、原理、多 Agent 协作、接入方式、输入输出、场景、个人价值、可扩展方向、实现思路和边界与验证。

本质是把多个现有 Agent 会话放进一个工作台，分屏展示、独立交互、定向控制，让它们并行工作，使一个人能够同时管理和控制多个 Agent。价值是将人的注意力用于分派、回应和验收，减少找窗口、等待、漏看和材料搬运；扩展按“复用现有 CLI / 模型 → 进程与会话承接 → 状态 / 控制 / 消息 → 上层任务与验收”逐步推进。

## 公网资源验证

[首发机器可读检查记录](./publication-first-check.json)记录 17 个地址，均 HTTP 200，内容与正式构建快照一致：

- 首页、构建清单、009 项目页、CSS、JS。
- 完整 PNG / SVG、简版 SVG、架构 SVG、文字摘要与首页引导图。
- 已有 001、002、005、006、007、008 的六个网页入口，发布未丢失这些入口。

PNG 按字节和 SHA-256 核对；文字资源仅归一化 Windows / Linux 换行符，其余内容完全比较。检查请求使用提交标识避免读取旧缓存，并保留 TLS 验证；网络临时错误采用有限重试。核验脚本为 `experiments/verify-publication.py`。

## 浏览器与本地检查

- 公网首屏标题、核心摘要正常显示；[公网桌面截图](../../assets/10-public-desktop.jpg)来自本仓库网页，非上游应用。
- 公网定位待输入会话到 B、定向输入后 B 转为运行。
- Codex 空闲消息保持 queued，提示等待人提交下一次提示。
- PNG 下载实际触发并取得文件。
- 返回公开索引成功，cmux 行展示全部十二项摘要，核心“一人控制多个 Agent”描述可见。
- 本地 390px 首屏与完整图正常加载，无页面横向溢出；见 [发布前检查](./release-validation-2026-10-14.md)。
- 索引检查、静态检查、9 项消息教学检查通过；远端基线的仓库测试 32 项中 31 通过、1 因 Windows 符号链接不可用跳过，Pages 构建与部署均成功。

## 范围

这次部署是研究网页与浏览器内教学模拟，不启动上游 macOS 客户端或真实 Agent，不调用模型，也不证明时间、质量和费用优势。上游恢复、Hooks、团队与云移动链路仍待真实环境复现。先前共享工作区索引阻塞属于历史制作记录，本次从远端最新版本独立发布，索引与正式工作流已通过。
