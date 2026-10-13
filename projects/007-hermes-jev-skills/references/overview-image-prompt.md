# 理解总览图 · 生成记录

日期：2026-10-13。使用内置 imagegen，非 CLI / 自有 API。图片为本次讨论的理解图，不是上游截图或真实路由结果。

最终图片：[理解总览图](../assets/04-understanding-overview.png)。PNG 尺寸与检查记录在项目 README。个人标准、模型映射和收益仍待实测。

## 最终提示词

```text
Use case: infographic-diagram
Asset type: one comprehensive Chinese knowledge poster for a GitHub research project.
Primary request: Make ONE polished, information-rich infographic that comprehensively summarizes our understanding of Hermes Jev Skills, capability-based multi-model routing, author-defined criteria, how to set and validate them, conditions for use, and foundations for extending finite decisions. The intended reader is the Chinese-speaking project owner. Accuracy and readable Chinese are more important than decoration.
Composition: a single high-resolution vertical poster, preferably 2160×3840 or similarly large, with a generous title, a prominent architecture flow, then a carefully aligned two-column information grid, and a compact footer. Use all available space sensibly, no giant blank areas. Off-white paper, dark charcoal text, teal for decision logic, restrained burnt-orange for unknown/risk/validation boundaries. Chinese sans-serif typography; section titles distinctly larger than body. Crisp clean editorial diagram style. Thin connectors, small functional line icons only. No people, mascot, stock photo, screenshots, 3D decoration, nonsense text, fake data, or invented benchmark claims.
All displayed text must be Chinese unless API names and project names require English. Render supplied Chinese verbatim and legibly; do not replace paragraphs with gibberish. You may reflow text into short lines. Preserve every section's meaning and coverage. Use the text below as the complete content, with each numbered section separately labeled; keep the architecture as a real arrow diagram and routing/validation comparisons as compact structured tables.

TITLE:
"Jev 与多模型路由：我们的理解总览"
SUBTITLE:
"按能力拆分工作，把判断做成可验证的决策"
CORE THESIS, prominent:
"你制定标准，判断器识别需求，代码选择，模型与工具执行，结果检验标准。"

SECTION 01 — "核心能力与原理"
"有限选择 Choice｜按定义评分 Score｜是否判断 Noul"
"输入：任务状态 + 明确问题 + 选项或评分标准"
"输出：结构化判断 → 本地代码决定后续动作"
"默认路由判断：难度、工作类型、出错代价"
"Jev 是 TypeSafe 云端决策模型；此库提供接入工具、技能与策略，未公开模型权重和训练实现。"
"判断任务需求与验证执行模型能力，需要分别完成。"

SECTION 02 — "完整分工与反馈闭环", a dominant horizontal or wrapped flow:
"你：目标与验收" → "输入：任务与必要背景" → "判断器：规则 / Jev / 小模型" → "本地策略：约束、阈值、模型池、回退" → "执行：模型 + 工具" → "验收：质量、成本、耗时"
Arrow returning from acceptance to goals/criteria with label "记录失败，修订标准和模型映射".
Under policy: "图像支持、上下文、可用连接、用户指定等硬约束由代码检查。"
Under flow: "Jev 不承担最终写作、代码修改或应用运行。"

SECTION 03 — "什么场景值得用？"
"适合：重复的语义判断；有限候选；信息足够；选择改变行动；结果可验收。"
"先用规则：任务标签明确、流程固定、格式或数值条件可直接检查。"
"先补背景：只有“继续完善”，缺少目标、材料、当前状态与验收要求。"
"少量偶发任务、固定配置已足够、判断开销超过收益时，继续用简单流程。"

SECTION 04 — "规则、Jev、小模型怎么选？", three comparison rows:
"本地规则｜按字段与流程分支｜验证覆盖、边界和维护成本"
"Jev｜按状态和有限问题判断｜验证语义判断、概率表现与整体收益"
"便宜小模型｜提示词 + 结构化输出｜验证格式、误判、延迟与回退"
"可替换判断器；接口适配、合法输出校验和本地回退不可省。"
"模型自报的高置信度，不能直接当成可靠概率。"

SECTION 05 — "自己的判断标准是什么？", five short numbered definitions:
"① 背景足够：任务、材料、阶段和验收要求已提供。"
"② 仅改表达：事实与结论已给定，只改措辞、长度或格式。"
"③ 综合推理：跨材料关联、处理冲突或形成新结论。"
"④ 相互依赖：改变部件间的行为、约束或共享状态。"
"⑤ 错误代价：返工是否昂贵，是否触及不能随意降级的要求。"
"三处按钮改字 ≠ 联动；音频与地图共同暂停恢复 = 行为依赖。"

SECTION 06 — "如何设置标准？"
"1. 从真实任务收集样本，明确什么算通过。"
"2. 选 A 便宜候选、B 较强候选；能力先当作假设。"
"3. 把“复杂”拆成独立、可复查的问题，允许未知。"
"4. 规定状态字段、硬约束、合法选项与回退方式。"
"5. 先设质量容限和延迟预算，再测阈值。"
"6. 用开发集修订，保留独立测试集。"
"7. 影子模式只记录建议，再小范围启用。"

SECTION 07 — "多模型路由：初始假设", compact table:
"已有事实的字幕压缩 → 尝试 A → 验收字数、专名、数字与事实"
"新讲解与跨材料分析 → 暂用 B → 验收推理、覆盖与来源"
"地图、音频、镜头联动 → 暂用 B → 实测暂停、探索与返回"
"背景不足 → 补信息；判断未知 → 保持约定的默认模型"
"这是待验证方案；不是上游默认策略的精确复刻。"

SECTION 08 — "如何验证能力与实际价值？"
"相同输入、材料、工具和验收，A / B 配对执行；关键案例重复，隐藏模型名称评阅。"
Four rows:
"A、B 都通过 → 比较完整成本与延迟"
"A 失败、B 通过 → 重点防止误降级"
"A 通过、B 失败 → 修订能力映射"
"A、B 都失败 → 检查信息、工具与流程"
"比较基线：固定模型、规则、规则 + Jev、规则 + 小模型。"
"指标：最终通过率、误降级率、每个通过任务的总成本、延迟、返工与维护工时。"
"总成本包含判断、全部执行调用、重试升级与缓存变化。"
"判断符合标准但结果失败：改标准或模型映射；漏掉标准条件：查输入、提问或判断器。"

SECTION 09 — "可扩展场景的共同基础"
"状态可观察：判断器能看到决策所需的信息。"
"问题可定义：条件明确，可拆成独立问题。"
"候选可枚举：模型、技能、证据或合法动作。"
"行动可执行：每个选项对应真实、受约束的步骤。"
"未知可回退：补信息、保持默认或交给人工。"
"结果可反馈：有日志、验收与代表性案例。"
"先由已有工作流提供候选与信息，再让判断器选择；它不会自动创造缺失证据或业务规则。"

SECTION 10 — "可以扩展到哪些场景？", mappings:
"技能选择 → 哪个技能匹配，或都不需要"
"RAG / 搜索 → 证据是否覆盖问题，是否继续检索"
"候选排序 → 哪段材料或哪个查询值得优先处理"
"浏览器 / 游戏动作 → 从当前合法动作中选择"
"工作流监督 → 继续、重试、升级或交给人工"
"消息分流 → 紧急程度、类型、是否需要人工"
"这些共享有限决策结构；每种场景都要单独定义标准并验证。"

BOTTOM PRACTICAL STRIP — "你的实践起点"
"写书：固定阶段先配模型；核实材料的表达整理试 A。"
"新疆 / 海底：固定导演顺序用规则；新联动需求再做语义判断。"
"RAG：证据充分性可判断；缺证据先检索。"
"Leak Check：格式、精确匹配与关联优先规则。"
"第一条实验：已有材料的表达整理，便宜模型能否稳定通过？"

FOOTER:
"任务标签 ≠ 执行能力｜置信度 ≠ 最终成功率｜路由回放 ≠ 质量验证"
"机制依据：hermes-jev-skills / 31f476c；TypeSafe 官方文档。个人标准与路由收益仍待实测。"
"研究整理 · 2026-10-13"
Ensure final artifact is ONE cohesive comprehensive infographic, not several images.
```
