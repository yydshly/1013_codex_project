# REA 研究支持与验证

此目录没有 REA 软件分析实验。build_guide.py 仅从本仓库编写的能力数据与教学内容生成静态网页重复区段、README 能力表和完整下载文本，不安装工具、不调用模型、不执行目标应用。

运行：python projects/015-rea/experiments/build_guide.py。实际研究和网页检查见 [results/verification.md](./results/verification.md)。

后续实验建议：在合适主机选择有源码可对照的小应用，固定版本，只调查一个功能；记录定位时间、错误推断、遗漏与复核成本，再做局部复现对照。该实验尚未运行。

## 本次新增比较

build_guide.py 同时读取 web/data/comparisons.json，生成十个已有项目的网页原理面板、完整对照表和 README 详细分析，再更新完整研究 TXT。数据保留原研究基线、来源与未验证事项；不调用模型或产品。实际网页检查见 results/verification.md 的补充对比记录。

## 完整工具与流程总图

运行 `python projects/015-rea/experiments/build_toolchain_figure.py`，从 `web/data/toolchain-overview.json` 生成同一构图的高清 PNG 和 SVG，同时更新 `assets/` 与 `web/assets/`。绘图依赖 Pillow 和本机 Microsoft YaHei 字体，字体文件不随项目分发。

程序检查 18 个阅读模块对 37 项分类的完整、无重复映射，检测文字宽度和模块卡片高度，并将实际尺寸记录至 `results/toolchain-figure-layout.json`。随后运行 `build_guide.py` 同步网页文字表、README 表格和完整研究 TXT。总图依据、交接解释及未验证范围见 [toolchain-figure.md](../references/toolchain-figure.md)。

## 完整理解与扩展场景

`build_guide.py` 还从 `project.json` 的十四项 `summary_sections` 生成网页完整摘要、README 摘要和 `web/data/understanding.json`，使项目页与首页的定位、能力、原理、价值和范围保持一致。从 `web/data/research-extensions.json` 生成八种拟议扩展场景，完整写入网页、README 和下载文本。它们是建设与验收方案，尚未执行真实集成。
