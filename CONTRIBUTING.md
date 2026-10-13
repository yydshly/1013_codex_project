# 新增与维护研究项目

## 1. 创建项目

在仓库根目录运行（Python 3.10+）：

```bash
python scripts/new_project.py example-project --name "项目名称" --source "https://github.com/owner/repository" --summary "项目用途与研究重点。"
```

- 自动分配 `001` 到 `999` 的下一个编号，目录名为 `编号-slug`。
- `slug` 使用小写英文字母、数字和单个连字符，如 `agent-workbench`。
- 编号表示收录顺序，首页按编号升序展示；归档时保留目录与编号。
- 同一 `slug` 不重复收录。相关研究优先补充到已有子项目。
- 模板仅用于创建项目，不计入研究索引。

创建后形成：

```text
projects/001-example-project/
├── project.json              # 首页索引的唯一数据来源
├── README.md                 # 子项目导读与研究记录
├── assets/
│   └── cover.svg             # 图片占位，研究时替换为实际截图
├── experiments/
│   └── README.md             # 复现、实验与改动代码说明
└── web/
    └── README.md             # Web 演示的运行与部署说明
```

## 2. 填写元信息

编辑子项目的 `project.json`：

| 字段 | 用途 |
| --- | --- |
| `id` / `slug` | 三位编号和英文短名，必须与目录名一致 |
| `name` | 对外展示名称 |
| `summary` | 完整单行摘要，介绍项目能力、原理、输入输出、价值与本次研究重点；作为兼容字段保留 |
| `summary_sections` | 可选的分项摘要数组，格式为 `[{"label": "能力", "text": "具体说明"}, ...]`；标签加粗并逐项换行显示，旧项目未填写时仍展示 `summary` |
| `source_url` | 原 GitHub 仓库地址 |
| `source_ref` | 实际研究的 tag 或 commit；暂未选定时留空 |
| `source_license` | 查证后的上游许可证；未知时留空 |
| `status` | `planned`、`researching`、`reproduced`、`completed` 或 `archived` |
| `tags` | 分类关键词，如 `AI`、`可视化` |
| `preview` | 相对子项目目录的图片路径，如 `assets/cover.png` |
| `preview_caption` | 图片展示内容的简短说明；占位图须明确标注 |
| `demo_url` | 已部署、可访问的完整地址；未部署时留空 |

`project.json` 管理首页展示，子项目 README 记录详细研究。更改名称、来源或截图时，同时检查 README 中的对应内容。单行字段不要写多行 Markdown。`summary_sections` 若填写，必须是非空数组，每项 `label` 和 `text` 为非空单行字符串，标签不重复；无需手写 HTML 换行。建议按能力、原理、输入、输出、价值、场景、边界与验证分别描述，内容完整保留，避免以长段文字挤在一起。

总索引使用独立“目标源库”栏，链接名称自动取自 `source_url` 的仓库名，并标明作者。索引不展示引导图，图片留在子项目导读与演示页中。

## 3. 记录研究

按 README 模板补充：选择理由、原项目用途、研究版本、运行环境、复现步骤、关键实现、图片说明、实践结论与后续事项。执行过的验证与尚未验证的内容分别说明。

引用上游代码时保留来源与许可证；大体积原仓库优先记录地址和固定版本，按需引入研究需要的部分。

## 4. 添加图片

- 图片放在子项目 `assets/` 中，推荐 `cover.png`、`01-overview.png`、`02-workflow.png` 等名称。
- 为图片写清楚替代文本和说明：画面展示什么、来自上游还是本地复现、对应哪个研究版本。
- `preview` 和 `preview_caption` 保留图片来源与说明；总索引不展示图片，子项目 README 和演示页放截图与解释。
- 模板的 `cover.svg` 是明确标注的占位图，替换时同步更新元信息和 README 路径。
- 图片优先压缩后提交；运行缓存、依赖目录、密钥和构建产物不入库。

## 5. 更新索引并检查

```bash
python scripts/update_index.py
python scripts/update_index.py --check
python -m unittest discover -s tests -v
```

索引工具只更新根 README 中两个 `PROJECT_INDEX` 标记之间的内容；标记之外的说明可直接编辑。它会检查编号、目录、元信息、图片和入口，并对所有真实项目按编号排序。GitHub Actions 会在提交和 PR 中执行相同检查。

部署多个 Web 演示前，请阅读 [部署约定](./docs/deployment.md)。
