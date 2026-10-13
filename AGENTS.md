# 仓库工作约定

本仓库用于研究多个优秀 GitHub 项目。根 README 是对外索引；各子项目独立记录源码分析、复现、实验和可选 Web 演示。

## 子项目与顺序

- 新增项目优先使用 `python scripts/new_project.py <slug> --name "名称" --source "https://github.com/owner/repo" --summary "摘要"`。
- 子项目目录使用 `projects/001-slug/`、`projects/002-slug/` 等三位编号，按收录顺序递增。
- 保留已有编号与目录名。归档时保留项目并将 `status` 改为 `archived`。
- `templates/project/` 是模板，不是实际研究项目。

## 研究与展示

- 先读取对应子项目 README、元信息和已有代码，再开展工作。
- 在 `project.json` 中维护摘要、状态、预览图片和演示入口；详细研究过程写入子项目 README。
- 记录原仓库、实际研究版本或 commit、上游许可证和复现环境。验证结果与未验证事项分开写。
- 截图保存在子项目 `assets/`；添加替代文本和来源说明，模板占位图不得当作真实截图。
- 实验代码放在 `experiments/`，Web 演示代码放在 `web/`。按子项目选择依赖与技术栈。
- 引用上游源码或素材时保留所需的版权和许可证；密钥、依赖目录、缓存和构建产物不入库。

## 索引与部署

- 修改元信息后运行 `python scripts/update_index.py`，不要手动编辑根 README 的自动索引区段。
- 检查 `python scripts/update_index.py --check`；修改索引或创建工具时运行 `python -m unittest discover -s tests -v`。
- 多个静态演示统一使用仓库站点下的独立子路径，具体约定见 `docs/deployment.md`。
- `demo_url` 填写已发布并验证可访问的地址；尚未部署时保持空字符串。
