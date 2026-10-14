# 共同理解与既有项目比较依据

日期：2026-10-14（Asia/Shanghai）。REA 基线保持 ebaaa79ca02bde4a73013a2a9a781d0b07a57ee4，不混入未经研究的新版本。

## 方法与范围

先读取十个相关子项目的 README、元信息和已有来源说明；重点比较问题、输入、机制、产物、验收和能力边界。Jev SEO、shadPS4、FCC 的部分核心源码本次按既有固定 ref 重新读取，托管编排与远程产品的官方网页另有当日核对。

本次没有进行速度、质量、费用横评。已有局部实验按其原记录说明，不能据其推出其他产品更好或更差；官方网页与文档不等于底层源码审计。

## 对照基线

| 项目 | 本仓库记录 | 固定版本或核对日 |
| --- | --- | --- |
| Jev SEO | [研究文档](../../projects/006-jev-seo/README.md) | 55a184a3b0d09565a4c84268f725a47784e62528 |
| shadPS4 | [研究文档](../../projects/008-shadps4/README.md) | 23c41333822fe8eca4c609b43119180af63ae4ac |
| Free Claude Code | [研究文档](../../projects/016-free-claude-code/README.md) | 74d4ccfde724f7416fa2a728d594d704dddc7c94 |
| Production Agentic RAG Course | [研究文档](../../projects/002-production-agentic-rag-course/README.md) | 424a0eb99edf841994f2a9a053912b489d2a94ff |
| Hermes Jev Skills | [研究文档](../../projects/007-hermes-jev-skills/README.md) | 31f476cac49713b6bf88c00d42382542e1c36965 |
| Claude Managed Agents | [研究文档](../../projects/013-claude-managed-agents/README.md) | 公开资料 2026-10-14 |
| cmux | [研究文档](../../projects/009-cmux/README.md) | cdbe99596fe13784ec5ea24d2e1c720a8f67f5cb |
| Vibe42 | [研究文档](../../projects/010-vibe42/README.md) | 公开资料 2026-10-14 |
| OpenMontage | [研究文档](../../projects/011-openmontage/README.md) | e45f5b12bd46440b04f3675af9a77d0718e6a254 |
| BaoCut | [研究文档](../../projects/014-baocut/README.md) | 7aa049e82e1367da013b7aba80f0b79033fa04ad |

## 本次核心复查

- [jevseo/checks.py](https://github.com/AgriciDaniel/jev-seo/blob/55a184a3b0d09565a4c84268f725a47784e62528/jevseo/checks.py)：固定 ref 成功读取，支持接口、规则、语义判断、加载或着色器转换的职责分析。
- [jevseo/jev.py](https://github.com/AgriciDaniel/jev-seo/blob/55a184a3b0d09565a4c84268f725a47784e62528/jevseo/jev.py)：固定 ref 成功读取，支持接口、规则、语义判断、加载或着色器转换的职责分析。
- [src/free_claude_code/api/routes.py](https://github.com/Alishahryar1/free-claude-code/blob/74d4ccfde724f7416fa2a728d594d704dddc7c94/src/free_claude_code/api/routes.py)：固定 ref 成功读取，支持接口、规则、语义判断、加载或着色器转换的职责分析。
- [src/emulator.cpp](https://github.com/shadps4-emu/shadPS4/blob/23c41333822fe8eca4c609b43119180af63ae4ac/src/emulator.cpp)：固定 ref 成功读取，支持接口、规则、语义判断、加载或着色器转换的职责分析。
- [src/shader_recompiler/recompiler.cpp](https://github.com/shadps4-emu/shadPS4/blob/23c41333822fe8eca4c609b43119180af63ae4ac/src/shader_recompiler/recompiler.cpp)：固定 ref 成功读取，支持接口、规则、语义判断、加载或着色器转换的职责分析。

## 官方资料复查

- [官方资料](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration)：2026-10-14 读取；只作为产品职责与公开机制说明。
- [官方资料](https://platform.claude.com/docs/en/managed-agents/workflow-runs)：2026-10-14 读取；只作为产品职责与公开机制说明。
- [官方资料](https://vibe42.ai/)：2026-10-14 读取；只作为产品职责与公开机制说明。

## 理解与新增设计

REA 的四点补充是动作可调用、材料有结构、调查可继续、结论可复核，依据其既有共享流程和 Evidence 契约整理。与其他项目的共同模式、个人选择建议和组合草图是本仓库的分析；不是各产品默认承诺的集成。

006 的格式、任务、材料指纹和原文引文校验属于本仓库提取实验；不将普通模型的自报置信度等同上游 Jev 概率。REA 的 observed / derived / inferred 表示依据类别，也不是概率。008 公开 homebrew 执行与源码研究使用的版本分别记录。

若做真实组合，仍须验证主机、模型和工具接口、材料访问、权限、来源字段与成果验收。RAG 不能不经转换就假定读取 REA Evidence，云端 Agent 不能不经连接就读取本地软件路径。

全部原创对比内容见 [comparisons.json](../web/data/comparisons.json)，读取范围见 [comparison-sources.json](./comparison-sources.json)。没有复制其他产品源码、截图、模型或品牌素材。
