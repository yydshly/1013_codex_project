# 实验与验证

本次完成公开资料研究、网页制作及公网发布。真实 Managed Agents、自建调度器和模型接入尚未运行。

[本地网页验证](./results/verification.md) 记录资源、桌面与手机布局、模式切换、并行教学流程、海底世界阶段与任务单、图像导出、下载和索引检查。教学数据不是模型输出。

`check_web.cjs` 检查完整网页交互；`export_overview.cjs` 将本仓库 SVG 导出为高清 PNG，并检查文字是否越出画布或面板。两者需要本机已有 Playwright 和 Chromium，没有模型请求。可用位置参数传入现有 Playwright 包目录。

## 公网发布检查

[发布记录](./results/publication-2026-10-14.md)保留内容提交、入口登记、成功工作流、公开资源哈希及 13 组实际浏览器验证。[初次](./results/publication-http-initial.json)与[最终](./results/publication-http-final.json)资源报告区分两次部署。

`check_publication.py` 使用 Python 标准库访问公开资源，与当前 Git 提交及同次静态构建比较，并确认 18 项摘要、八种扩展场景、原高清图及全部已有入口。需在对应提交的 Pages 工作流成功、同一工作副本构建成功后运行：

```powershell
python scripts/build_site.py
python projects/013-claude-managed-agents/experiments/check_publication.py --phase maintenance --run-id <实际成功运行编号> --report projects/013-claude-managed-agents/experiments/results/publication-http-maintenance.json
```

命令只验证静态文件，没有模型请求或浏览器交互。网页交互验证独立记录在 [publication-browser.json](./results/publication-browser.json)；没有将固定教学结果视为真实 Agent 成果。

## 后续真实实验方案

选择三个同类 GitHub 项目，固定 commit、研究问题、来源条件、完成标准与资源范围。分别运行单 Agent 和多 Agent，保留完整成果、用量、耗时与失败，不只展示成功样本。

比较证据准确性、覆盖与遗漏、人工核查时间、总体耗时及总费用。记录模型、工具、重试、搜索范围和汇总步骤差异，避免把多做的工作直接当成效率提升。

自建系统还应验证：资料读取失败；证据不充分；重复运行；停止后在途请求；共享文件修改；恢复是否跳过有效的既有成果。所有失败与未验证事项进入最终报告。

`web/data/research-plan.example.json` 仅为自建格式建议。没有实际执行器，不是官方 API 配置；并发、重试、预算和权限需要程序实现。
