# cmux 中文研究网页

原生 HTML、CSS、JavaScript 静态页面，无安装依赖、CDN、后端或模型调用；所有操作是浏览器内教学模拟。基准 commit `cdbe99596fe13784ec5ea24d2e1c720a8f67f5cb`，官网查阅于 2026-10-14。

## 内容与交互

十章涵盖本质、操作效果、能力、架构、多 Agent 消息、分派、场景与价值、扩展、历史、证据。

- 模拟工作台：切换独立会话、定位待输入、定向输入、通知与重置。
- 能力筛选与四条架构路径解释。
- Claude / Codex × 空闲 / 执行中 / 等人：显式模拟交付时机、read 与 failed；不修改人的草稿。
- 按真实痛点给出价值判断；选择不上传、不持久化。
- 完整理解总图（2400 × 3700 PNG / SVG）、简版与架构 SVG、文字摘要下载、打印入口与二十项来源。

不实现实际进程、租约、Hook 轮询、模型或 Socket，不是上游应用的浏览器移植。

## 本地运行

在仓库根目录：

```powershell
python scripts/build_site.py --project 009-cmux --output site-cmux-preview
python -m http.server 8779 --bind 127.0.0.1 --directory site-cmux-preview
```

访问 `http://127.0.0.1:8779/009-cmux/`。预演首页只收录显式选择项目。也可直接服务 `web/`，但返回首页需完整站点结构。

## 验证

```powershell
node --check projects/009-cmux/web/app.js
node projects/009-cmux/experiments/check-message-model.cjs
python projects/009-cmux/experiments/check-static.py
python scripts/update_index.py
python scripts/update_index.py --check
python -m unittest discover -s tests -v
```

验证状态机等待、不同空闲条件、关闭接收与 read 语义；检查锚点、资源、版本与元信息。浏览器实查工作台、筛选、消息、下载与手机布局，见 [验证记录](../experiments/results/verification.md)。

## 部署与资源

相对资源路径、hash 章节适配 `/1013_codex_project/009-cmux/`。沿用仓库原生静态汇集和 Pages 约定，无框架打包。2026-10-14 已提交远端并发布，在线入口为 [cmux 理解网页](https://yydshly.github.io/1013_codex_project/009-cmux/#understanding)，详见 [公网验证](../experiments/results/publication-2026-10-14.md)。

顶部文字摘要可直接打开，站点索引的研究文档链接指向已提交的 GitHub README。SVG 为本仓库原创，项目 `assets/` 留有对应副本供索引；截图是本仓库教学页，非上游应用。

完整理解图入口是 `#understanding`，点击 PNG 可打开原图放大，PNG / SVG 均可下载。图像由本仓库根据研究内容直接绘制，界面为示意。可用 `python projects/009-cmux/experiments/draw-complete-understanding.py` 重新生成；绘制环境需要 Pillow、Microsoft YaHei 与 Segoe UI Symbol 字体，静态网页本身不需要 Python。
