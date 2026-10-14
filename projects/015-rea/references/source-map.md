# 来源与结论映射

研究日期：2026-10-14。固定源码：ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4。读取方式：GitHub 连接器固定 ref 读取；公开案例说明另由网络浏览核对。未复制整个原仓库或其截图素材。

| 内容 | 固定来源 | 核对范围 |
| --- | --- | --- |
| 项目定位、目标表与案例 | [README.md](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/README.md) | 公开说明；不是运行验证 |
| 版本号与 Node 要求 | [package.json](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/package.json) | 源码版本 6.4.0；不代表 npm 字节相同 |
| CLI / MCP、共享应用层与提供者 | [docs/architecture.mermaid](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/docs/architecture.mermaid) | 分层架构 |
| JavaScript 校验、重建与证据创建 | [src/application/javascript/JavaScriptApplicationService.ts](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/src/application/javascript/JavaScriptApplicationService.ts) | 核心流程源码 |
| 参数、摘要、来源和限制绑定 | [src/application/javascript/JavaScriptApplicationEvidence.ts](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/src/application/javascript/JavaScriptApplicationEvidence.ts) | 核心证据源码 |
| Evidence 字段与标记 | [src/domain/evidence.ts](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/src/domain/evidence.ts) | 核心数据契约 |
| 图追踪、比较与静态运行区分 | [docs/javascript-application-workflows.md](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/docs/javascript-application-workflows.md) | 专题文档 |
| 被动网页观察及附加前缺口 | [docs/browser-observation.md](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/docs/browser-observation.md) | 专题文档 |
| 主动浏览器场景 | [docs/browser-scenario-contract.md](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/docs/browser-scenario-contract.md) | 权限、生命周期与捕获边界 |
| Electron 被动与主动场景 | [docs/electron-observation.md](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/docs/electron-observation.md) | 专题文档 |
| 历史网络记录 | [docs/web-network-captures.md](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/docs/web-network-captures.md) | HAR / SAZ / mitmproxy / qlog 范围 |
| .NET 与 NativeAOT 边界 | [docs/managed-code-analysis.md](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/docs/managed-code-analysis.md) | 静态元数据与 CIL |
| JavaScript 恢复 | [docs/javascript-recovery.md](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/docs/javascript-recovery.md) | Linux x64 与 Wakaru |
| Frida 插桩 | [docs/frida-instrumentation.md](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/docs/frida-instrumentation.md) | 可选依赖、效果和验证限制 |
| Apple 应用清单投影 | [docs/apple-application-analysis.md](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/docs/apple-application-analysis.md) | 结构不证明运行 |
| 六种调查指引 | [docs/mcp-prompts.md](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/docs/mcp-prompts.md) | 指引不自动执行工具 |
| 会话、目录、结果、效果与限制 | [docs/mcp-contracts.md](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/docs/mcp-contracts.md) | 文档契约，不是全工具实测 |
| 工具设计原则 | [docs/tool-design.md](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/docs/tool-design.md) | 观察、推导、推断和未知 |
| 重建验证义务 | [docs/reconstruction-obligation-ledgers.md](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/docs/reconstruction-obligation-ledgers.md) | 候选与关闭义务 |
| 安装、Skill 与发布边界 | [docs/installation.md](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/docs/installation.md) | 引用作者 2026-10-11 发布核对；未独立检查最新 npm |
| Windows Ghidra P0 | [docs/windows-ghidra-p0.md](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/docs/windows-ghidra-p0.md) | 实验性主机、目标与操作范围 |
| 官方路线 | [docs/roadmap.md](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/docs/roadmap.md) | 与我们的建议分开 |
| 许可证 | [LICENSE](https://github.com/morluto/rea/blob/ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4/LICENSE) | 保留原文，第三方各有许可 |

能力清单的每项专题来源保存在 [capabilities.json](../web/data/capabilities.json) 的 doc 字段，并在网页和 README 展开为固定链接。目标范围以固定 README 表格为基础，专题延伸的输入输出和限制由文档辅助核对。

公开案例：[Notion](https://rea.tools/showcase/notion/)、[DX-Ball](https://rea.tools/showcase/dx-ball/)、[TH04](https://rea.tools/showcase/th04/)。案例结论归于作者，未独立复现；网站不是固定 commit 内容。

本研究原创整理：中文宏观分工、三个教学流程、个人价值判断、评测与扩展建议、网页和总览图。与 RAG 的衔接尚未实现，未证明质量、时间或成本优势。商业工具许可证不由 REA 的 MIT 许可授予。

## 细分范围补查

本页能力地图以 README 的目标表为起点，并补查固定版本的专题文档。38 个专题文件均已按固定 ref 成功读取，读取记录保存在 source_manifest.json 的 topic_sources；这项记录只证明本研究取得文档并核对说明，不代表真实工具调用成功。

新增范围包括 Node / Electron Inspector、静态运行关联、Dart AOT、HarmonyOS 包清单、DOS、raw、MIPS、PSP、RISC-V 和 NativeAOT。每项在 capabilities.json 保留专题路径，并在网页与 README 展开固定链接。

## 2026-10-14 补充共同理解与比较

新增十个已有研究项目的职责、输入、原理、输出和验收对照。采用各自研究基线，不作同任务效果横评；重点源码与官方资料有本次复查记录。参见 [比较依据](./comparison-map.md)、[读取记录](./comparison-sources.json) 和 [对比数据](../web/data/comparisons.json)。组合结构为建议，尚未实施跨项目集成。

## 2026-10-14 完整工具与流程总图

新增同一张完整图的 PNG / SVG、18 个模块的原理与交接，以及 37 项分类覆盖映射。制作与来源见 [总图依据](./toolchain-figure.md)，全部图文数据见 [toolchain-overview.json](../web/data/toolchain-overview.json)。图中链路为方法示例，未运行 REA。
