# Vibe42 中文研究网页

这是详细研究与教学页面，涵盖能力、本质、三端架构、操作链路、会话、网络、加密、通知、桌面、产品对比、实现路线、证据和复现清单。没有远控后端，不需要登录、密钥或外部 CDN。

## 已验证的公开入口

[打开Vibe42理解网页](https://yydshly.github.io/1013_codex_project/010-vibe42/#understanding)。2026-10-14经GitHub Pages发布并实际访问；资源与提交比对、统一索引摘要和浏览器交互已检查，见[公网发布记录](../experiments/results/publication.md)。

## 打开方式

可以直接在浏览器打开 [index.html](./index.html)，本地文字和交互配置无需请求后端。返回项目索引的相对入口按统一站点路径设计，推荐通过下述构建预览阅读完整导航。

在仓库根目录运行：

```powershell
python scripts/build_site.py --project 010-vibe42 --output site-preview-vibe42
python -m http.server 8775 --bind 127.0.0.1 --directory site-preview-vibe42
```

访问 [本地预览](http://127.0.0.1:8775/010-vibe42/)。端口占用时选择其他空闲端口。停止预览服务后，本地 HTTP 地址不再可用；源 HTML 仍可直接打开。

## 阅读与交互

- 新增“00 理解总览与原理图”：同一底图汇总能力、本质、原理、使用场景、建议扩展、意义与证据边界，支持SVG/PNG下载。
- 选择“原理放大 · 可点击”，点击7个节点阅读机制、例子和边界；3条路径分别追踪输入到执行、结果返回、状态提醒与接手，共6/5/5步，支持直连/密文中继示意。
- 手机上原理图可在图内横向滑动，解释文字纵向排列；键盘Enter/Space可操作节点。切回完整图恢复总览，打印始终使用完整静态图。
- 14 个专题和独立资料来源，完整正文预先生成；不执行 JavaScript 也能阅读。
- 三端原创 SVG 可下载和放大；七个模块可切换查看职责与证据边界。
- 六步操作演示使用构造数据；故障条件面板解释不同生命周期。
- 直连/密文中继切换是机制示意；没有建立真实网络通道。
- 12 个维度比较 Agenvo、cmux 和 WireGuard Install，来源有固定 commit 与研究状态。
- 18 项证据按公开依据、实现推导、我们的建议、尚未验证筛选。
- 可下载完整文字、架构图和证据 JSON；“打印 / PDF”调用浏览器打印。

本地交互不会安装产品、执行命令、写入主机文件、访问真实 Agent、设置 Cookie 或将数据发送到平台。点击外部来源才会打开原文网站。

## 文件与维护

`index.html`、`data/` 由 [研究生成工具](../experiments/build_research.py) 产生；`styles.css` 与 `app.js` 使用原生 CSS/JavaScript。架构图是本研究原创解释，不是产品运行截图；网页截图在子项目 `assets/`，来源与实际检查见 [验证记录](../experiments/results/verification.md)。

[build_overview.py](../experiments/build_overview.py)维护总览内容、原理讲解与SVG。运行主生成工具会同步生成静态图、HTML和交互数据；再使用[render_overview.cjs](../experiments/render_overview.cjs)通过本地HTTP预览导出PNG。详细顺序见实验目录说明。

标准静态子路径为 `010-vibe42/`，资源均为相对路径。正式发布遵循 [仓库部署约定](../../../docs/deployment.md)：默认构建汇集全部已跟踪项目，显式 `--project` 仅供本地预演。首次部署成功并实际访问后，`project.json`的`demo_url`已填写正式入口。研究页面发布不证明原产品安装、配对、连接或Agent执行已经复现。
