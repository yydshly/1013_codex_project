# 网页运行与展示范围

本网页完整汇总 Claude Managed Agents 的多 Agent 编排与运行管理理解。采用原生 HTML、CSS 和 JavaScript，无安装步骤、无外部前端依赖、无模型请求。

## 主要功能

- 十七章中文导读与阅读导航，首段明确能力、原理、价值和扩展方向；首页完整展示 18 项摘要。
- 八种扩展场景，逐项说明工作流程、输入输出、实现前提和验收指标。
- 累计启动上限、任务拆分和模型 / 框架分工。
- 动态工作流 / 普通子 Agent 机制切换。
- 正常、任务失败、证据不足三种固定数据的分步教学流程。
- 海底世界六个阶段、六份任务接口和集成失败 / 定向修复的教学交互。
- 六项任务契约、内部黑盒边界及十二个讨论问题。
- 可下载完整 SVG / PNG 总览图和自建任务格式 JSON。
- 响应式布局、键盘焦点与减少动画偏好支持。

教学流程不读取实际项目，不启动 Agent，不产生模型费，也不是官方事件回放。JSON 模板没有执行器。

可直接用浏览器打开本目录的 `index.html` 阅读和操作。跨项目链接与“全部项目”入口需要按下面方式构建整个预览。

## 构建与访问

从仓库根目录运行：

```powershell
python scripts/build_site.py --project 013-claude-managed-agents --project 001-infinite-bookshelf --project 002-production-agentic-rag-course --project 007-hermes-jev-skills --output site-claude-agents-preview
python -m http.server 8793 --bind 127.0.0.1 --directory site-claude-agents-preview
```

打开 `http://127.0.0.1:8793/013-claude-managed-agents/`。选择已有 001、002、007 是为了验证组合方向中的站内链接。临时构建目录已被仓库 `site-*` 规则忽略。

资源均使用相对路径，导航使用锚点，部署前缀为 `/1013_codex_project/013-claude-managed-agents/`。无需后端、凭据或第三方 CDN。正式部署按 [部署约定](../../../docs/deployment.md) 收集已提交静态文件；[公开网址](https://yydshly.github.io/1013_codex_project/013-claude-managed-agents/) 已发布并实际验证，`demo_url` 已登记。完整 18 项摘要及原 PNG 引导图同时保留在站点首页。

## 验证

具体资源、布局和交互结果见 [本地验证记录](../experiments/results/verification.md) 与 [公网发布记录](../experiments/results/publication-2026-10-14.md)。本地网页验证与产品实测分别记录，不将教学模拟视为真实多 Agent 成果。
