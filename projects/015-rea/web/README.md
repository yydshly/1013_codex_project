# REA 中文理解网页

原生 HTML / CSS / JavaScript，无第三方前端依赖。十三章完整导读、能力筛选、三组逐步教学、十个已有项目的原理对比、固定来源、FAQ、下载与打印样式。无 REA、模型、上传或真实软件分析调用。

## 文件

- index.html：完整静态内容，无 JavaScript 也可读能力和全部教学流程。
- app.js：领域 / 方式 / 关键词筛选、教学步骤、阅读进度。
- styles.css：桌面、窄屏、键盘焦点、减少动效与打印。
- data/capabilities.json：能力清单与研究版本。
- data/comparisons.json：十个既有项目的对比、固定基线、机制与验证边界。
- assets/toolchain-overview.png / .svg：同一张完整工具与流程总图，2400 × 6858；原简图保留为历史材料。
- data/toolchain-overview.json：18 个工具原理模块、交接和 37 项分类的覆盖映射。
- guide.txt：完整研究、来源映射和实际验证记录的 UTF-8 下载。

## 生成和预览

从仓库根目录运行：

~~~powershell
python projects/015-rea/experiments/build_toolchain_figure.py
python projects/015-rea/experiments/build_guide.py
python scripts/build_site.py --project 015-rea --project 006-jev-seo --project 008-shadps4 --project 016-free-claude-code --project 002-production-agentic-rag-course --project 007-hermes-jev-skills --project 013-claude-managed-agents --project 009-cmux --project 010-vibe42 --project 011-openmontage --project 014-baocut --output site-rea-preview
python -m http.server 8769 --bind 127.0.0.1 --directory site-rea-preview
~~~

入口 http://127.0.0.1:8769/015-rea/。端口被占用时可换空闲端口。构建产物不入库。

资源用相对路径，适配 /1013_codex_project/015-rea/；返回总览用 ../，章节用 hash。公开发布按根 docs/deployment.md；本项目尚未发布，demo_url 为空。

也可在浏览器打开本地 index.html；交互不依赖 fetch。总览返回链接用于构建后的站点。

## 验证

实际检查见 [verification.md](../experiments/results/verification.md)。固定教学内容不伪装真实引擎输出；源库链接固定 commit，案例网站可能变化。

对比入口为 /015-rea/#comparison。选定一个项目可并排看机制，展开全部可阅读十项完整分析；比较依据与原研究分别保留。跨项目导读链接需要上面的多项目构建。

完整图入口为 /015-rea/#toolchain-overview；点击图打开 SVG 原图，可下载 PNG / SVG / 图文 JSON，并展开带固定来源的等价文字版。图片已生成时，阅读静态网页无需 Pillow；重新绘图需要 Pillow 和程序中记录的本机字体。
## 完整理解与扩展方案

页面新增 `#brief`，完整展示与项目元信息、根索引和站点首页一致的十四项理解摘要，先说明能力、原理、价值与可扩展场景。`#extensions` 包含八种拟议扩展方案的材料、模块、实施、产物与验收表。表格在自己的容器内横向滚动，摘要在手机上单列显示。

下载 `data/understanding.json` 与 `data/research-extensions.json` 可得到对应文字。前者由 `experiments/build_guide.py` 从元信息生成；后者是本仓库撰写的扩展方案来源。同一脚本更新 HTML、README 和完整 `guide.txt`。主图继续使用本次讨论的 `assets/toolchain-overview.png` / `.svg`，没有替换成新的图或运行截图。

公开发布采用仓库既有 GitHub Pages 工作流，登记前先验证页面、完整摘要、总图、静态资源、下载及已有项目入口。实际部署范围和证据见项目的发布记录。
