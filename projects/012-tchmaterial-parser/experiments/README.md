# 研究实验与验证

本子项目分别记录源码分析、公开元信息探测与本仓库导读网页验证。当前没有运行上游桌面程序，没有输入账号凭据或下载教材文件。

## 公开元信息探测

probe_metadata.py 使用 Python 标准库读取平台公开 JSON：

1. 教材版本索引。
2. 最多前三个目录分片，寻找一个带“小学”分类的记录。
3. 对应教材详情，保存资源标题、标签、文件格式和是否存在存储地址。

仅允许 s-file-1 / s-file-2 元数据域名；不跟随返回的 PDF、音频或其他文件地址，不获取登录凭据。记录保存在 results/metadata-probe.json。

复查：

    python projects/012-tchmaterial-parser/experiments/probe_metadata.py

该命令会覆盖本实验的上次记录，应按需要先保留旧结果。本次成功样本为“道德与法治一年级上册”，请求返回 HTTP 200；单个样本不代表全平台覆盖、文件可下载或与学校用书一致。

## 网页验证记录

- results/static-check.json：构建页面本地资源、锚点、SVG XML 与七个 HTTP 地址。
- results/blank-registry.csv：通过网页下载按钮实际生成并下载的空白登记表，17 列，不含真实资料或登录凭据。
- results/verification.md：完整验证范围、网页操作、环境、结果与未验证项。
- ../assets/：本地浏览器截图、原版 SVG 简图及全面理解 PNG。
- infographic-prompt.md：2026-10-14 全面理解图的内置 imagegen 提示词、固定源码依据与生成方式；图像为解释资料，不是下载实测截图。
- verify_publication.py：按指定提交的 Git 文件内容核对公网项目资源，检查完整首页摘要、引导图、构建清单和已有网页入口；借鉴本仓库项目 011 的发布核对实现。

本地构建目录 site-tchmaterial-preview 是临时产物，已被仓库忽略，不入库。

发布后复查（需要先完成静态构建，第三项参数指定结果文件）：

    python projects/012-tchmaterial-parser/experiments/verify_publication.py https://yydshly.github.io/1013_codex_project/ site-tchmaterial-release projects/012-tchmaterial-parser/experiments/results/publication-http-final.json --ref HEAD

工具只请求公开静态站点；不执行教材下载或使用平台账号凭据。HTTP 200 与文件一致只验证研究网页发布。
