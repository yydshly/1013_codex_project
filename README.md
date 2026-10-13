# GitHub 项目研究索引

> 收集值得研究的 GitHub 项目，记录源码分析、运行复现和实践结论，并集中导航到各子项目与 Web 演示。

这里是研究总仓库。每个子项目拥有独立编号、研究文档、图片与实践代码；本页提供按编号排列的索引和简要介绍。

[项目目录](./projects/) · [新增项目指南](./CONTRIBUTING.md) · [研究模板](./templates/project/) · [Web 部署约定](./docs/deployment.md)

## 项目索引

<!-- PROJECT_INDEX:START -->
当前收录 **0** 个项目，按三位编号升序排列。

暂无研究项目。首个项目将从 **001** 开始；添加后，这里会展示项目摘要、预览图片、研究状态和相关入口。
<!-- PROJECT_INDEX:END -->

## 收录与阅读方式

- **先看索引**：了解项目用途、研究进度与演示入口。
- **再读子项目**：查看选择理由、环境配置、源码分析、截图说明与研究结论。
- **保留来源**：记录原仓库、研究时的版本或 commit，以及上游许可证。
- **积累实践**：将实验代码放在对应子项目中，区分上游功能与本仓库的改动。

研究状态：`待研究` → `研究中` → `已复现` → `已完成`，停止维护的项目标记为 `已归档`。状态可按实际进度调整。

## 目录结构

```text
1013_codex_project/
├── README.md                 # 对外总览：索引、摘要、预览和导航
├── AGENTS.md                 # 后续研究与维护的工作约定
├── projects/                 # 001-xxx、002-xxx…，每个目录一个研究项目
├── templates/project/        # 子项目文档、元信息和图片占位模板
├── docs/deployment.md        # 多个 Web 演示的路径与部署约定
├── scripts/                  # 创建子项目、生成并校验索引
├── tests/                    # 索引与创建工具的行为检查
└── .github/workflows/        # 自动检查项目结构与索引同步
```

## 添加第一个项目

需要 Python 3.10 或更高版本，无需安装第三方依赖。将下面的示例名称和原仓库地址替换为实际项目：

```bash
python scripts/new_project.py example-project --name "项目名称" --source "https://github.com/owner/repository" --summary "这个项目解决什么问题，以及本次研究的重点。"
```

工具会分配下一个编号，创建 `projects/001-example-project/`，复制研究模板，并更新本页索引。

后续修改子项目的 `project.json` 后，执行：

```bash
python scripts/update_index.py
python scripts/update_index.py --check
```

编号从 `001` 开始，保持稳定，不随研究状态变化而重排。图片放在各子项目的 `assets/` 中，Web 演示代码放在各子项目的 `web/` 中。详细规则见 [新增项目指南](./CONTRIBUTING.md)。

## Web 演示

预留同一站点下的独立路径，例如 `/1013_codex_project/001-example-project/`。每个子项目可选择适合自己的技术栈；有可访问的演示后，将实际地址写入 `project.json` 的 `demo_url`，索引便会显示入口。

目前尚未部署演示站点。部署方案见 [Web 部署约定](./docs/deployment.md)。

## 来源与使用

各子项目应注明原作者、原仓库、研究版本和许可证。引用的源码、图片及其他素材遵循各自的上游许可；本仓库目前未设置统一开源许可证。
