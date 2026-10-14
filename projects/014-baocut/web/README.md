# BaoCut 理解网页

本网页整理底层视频能力、可视化 UI、人和模型对话如何继续修改同一份作品，并说明提交 `7aa049e8` 新增设计画布与设计系统的价值、来源和边界。

## 内容与互动

- 核心理解与三类职责；原有视频能力表。
- 五步固定教学示例；可以修改第二句、查看下一轮只改第三句、撤销和重置。
- 设计画布与设计系统的新增价值，区分视频编辑与设计模块的实现。
- 执行原理：当前状态、模型规划、任务计算与事务应用、UI 接手验收。
- 八种可扩展场景，逐项说明目标、能力组合与实现前提；`extensions.json` 为研究建议数据。
- 固定版本来源、上游许可、已核对与未验证范围。
- 2400×3740 的八部分完整理解总览，覆盖能力、场景与价值；PNG / SVG 与研究摘要下载。

这是本仓库原创研究展示，无真实视频剪辑、模型调用或上游编辑器移植。示例台词、时长、画面和状态均为教学数据。

## 运行

纯静态 HTML / CSS / JavaScript，无需依赖安装或构建框架。兼容现代浏览器，交互使用 `structuredClone`。Python 3.10.11 或其他 Python 3 可提供本地服务。

在仓库根目录构建符合独立子路径的预演：

```powershell
python scripts/build_site.py --project 014-baocut --output site-baocut-preview
python -m http.server 8774 --bind 127.0.0.1 --directory site-baocut-preview
```

访问 `http://127.0.0.1:8774/014-baocut/`。返回总览使用 `../`，资源使用相对路径，页面导航使用 hash。

公开入口：[BaoCut 理解网页](https://yydshly.github.io/1013_codex_project/014-baocut/)，使用仓库站点下 `/1013_codex_project/014-baocut/`。2026-10-14 已发布并验证，`project.json` 已登记真实地址。发布沿用 [统一部署约定](../../../docs/deployment.md)，不创建独立托管站点。

## 验证

JavaScript 语法、本地资源、网页流程与手机布局的实际检查见 [验证记录](../experiments/verification.md)。无模型凭据、服务器功能或用户数据上传。

公开部署、资源一致性与实际浏览器交互结果见 [发布记录](../experiments/results/publication-2026-10-14.md)。
