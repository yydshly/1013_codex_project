# 完整工具与流程总图的制作依据

日期：2026-10-14（Asia/Shanghai）；固定 REA 源码：ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4。图为本仓库原创技术图示，未运行上游。

## 本质与结构

标题采用“工具管理与适配 + 自身解析与关系分析 + 统一证据接口”。“管理工具”包括提供者选择、可用性、请求适配、目标身份、会话和生命周期，并不等于一个安装所有引擎的包管理器。

图分为角色、内部管理与适配、18 模块、六步方法示例、Evidence、价值和成立条件。18 模块将已有 37 项阅读分类完整分组，每项恰好覆盖一次；它们不是上游工具数或 18 个 Agent。静态 / 观察 / 执行标签用于解释主要路径，具体操作的效果仍以运行契约为准。

## 工具和原理的依据

- 37 项能力及专题路径沿用 web/data/capabilities.json 与 references/source_manifest.json。
- [package.json](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/package.json) 本次重新读取，确认 Babel、ASAR、MCP SDK、Playwright、PTY、ZIP、plist 与 EVMole 等依赖；存在依赖不单独证明每项能力。
- 本次重新读取 Ghidra / IDA、JavaScript 产物与恢复、ELF / core、浏览器与 Electron、托管代码 / NativeAOT、Flutter、HarmonyOS、历史网络、信号和固件专题，用于核对图中工具分工与平台范围。
- 固定专题链接逐项保存在 web/data/toolchain-overview.json 的 docs，并在网页文字版和 README 展开为链接。
- 各模块的原理是对材料如何处理、返回什么、如何交接的中文概述；不是逐行反编译引擎算法说明，也不是所有主机与引擎等价能力承诺。

## 完整链路

“导出按钮”是方法示例：问题与材料 → 盘点和 AST 入口 → 按需原生查询 → 按需运行补证 → 解释与局部实现 → 同条件对照。模块交接须保留材料与位置依据；运行关联不自动证明因果，有限样本不证明完整应用等价。

图中通过编号、箭头与“串接”字段说明各模块如何衔接，助手仍按问题决定后续动作。工具可以独立使用，不要求每次运行所有模块。

## 文件与复现

- assets/toolchain-overview.png：2400 × 6858，高清展示。
- assets/toolchain-overview.svg：同一构图与文本的可缩放版本。
- web/assets/：与 assets 中两种格式字节相同，供静态网页使用。
- web/data/toolchain-overview.json：全部文字、模块编号、交接与能力映射。
- experiments/build_toolchain_figure.py：本仓库绘图程序，使用 Pillow 和本机 Microsoft YaHei 字体；未分发字体文件。
- experiments/results/toolchain-figure-layout.json：尺寸、模块数、覆盖数和文字水平范围的实际记录。

在本次 Windows / Python 环境运行：

~~~powershell
python projects/015-rea/experiments/build_toolchain_figure.py
python projects/015-rea/experiments/build_guide.py
~~~

程序检测分类完整性、重复映射、文字宽度与模块卡片高度。已实际检查顶部、模块细节和流程 / 证据 / 价值区域；PNG 和 SVG 都有来源说明，网页保留完整文字版。

原始简图 understanding-overview.svg 保留为历史解释图，元信息和网页主图已切换到完整总图。没有使用相关商业工具的品牌图标、截图或源码素材。
