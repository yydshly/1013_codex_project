# 实验、证据与评测

当前完成固定版本源码研究与静态网页，尚未运行上游或接入真实模型。

- [固定版本证据](../references/source-evidence.json)：源文件、blob SHA、行数、符号与原始链接。
- [网页与仓库验证](./results/verification.md)：实际检查范围与局限。
- [公网发布记录](./results/publication-2026-10-14.md)：内容提交、Pages 工作流、资源一致性与公开网页交互。
- [空白评测表](../web/data/evaluation-template.csv)：五类任务，无预填结果。

真实实验选择一个 Agent、两个允许使用的模型与五类任务，固定资料、版本、协议、配置和验收标准。记录完成率、工具失败、重试与备用调用、返工、耗时和实际费用。各模型使用独立副本，不把一次演示或本地 usage 估算当作成本结论。

先在测试目录跑通工具闭环，再验证断流、已交付内容与备用条件。避免重复有副作用的工具操作。密钥、私密上下文、依赖、缓存和构建产物不入库。

## 两张图与网页检查

`draw_understanding.py` 绘制完整理解和底层模块 SVG，`render_diagrams.cjs` 将它们原样渲染为 PNG 并检查文字边界。`verify_web.cjs` 检查正文、原流程、旧项目对比、图示阅读器、下载及手机布局。图示、源码结论和教学模拟分别标注；没有调用真实模型。

`verify_publication.py` 对比公开资源、指定 commit 的本项目文件与生成站点快照，并检查其他已发布入口。先按仓库部署约定生成全部已跟踪演示，再从仓库根目录运行：

```powershell
python projects/016-free-claude-code/experiments/verify_publication.py --site-dir site-dist --output projects/016-free-claude-code/experiments/results/publication-content.json
```

`verify_index.cjs` 使用已有 Playwright 环境核对公开索引的十五项摘要、原引导图、正式路径、四问与六类扩展、表格对比度和手机滚动。最终结果见 [publication-index-final.json](./results/publication-index-final.json)，最终资源一致性见 [publication-final.json](./results/publication-final.json)。
