# OpenMontage 中文研究网页：2026-10-14 发布验证

[在线导读](https://yydshly.github.io/1013_codex_project/011-openmontage/#brief) · [完整能力图](https://yydshly.github.io/1013_codex_project/011-openmontage/#understanding) · [产品对比](https://yydshly.github.io/1013_codex_project/011-openmontage/#comparison)

## 版本与范围

- 上游研究版本：`e45f5b12bd46440b04f3675af9a77d0718e6a254`，AGPL-3.0。
- 首次内容提交：[`ba8980a123bd00fed7d3fd98dbeafd1ee986555a`](https://github.com/yydshly/1013_codex_project/commit/ba8980a123bd00fed7d3fd98dbeafd1ee986555a)。
- 首次构建与部署：[Actions 38497224736](https://github.com/yydshly/1013_codex_project/actions/runs/38497224736)，build 与 deploy 均成功。
- 发布到现有 GitHub Pages 项目站点的独立路径，包含原创静态网页与公开下载，不部署真实视频工具、模型或后端。
- 从远端最新版本建立独立发布副本，只提交 OpenMontage 项目与所需自动索引；工作区其他未发布项目和无关改动未上传。

## 能力、原理、价值与扩展的完整说明

首页保留18项摘要：本质、能力、原理、模型与工具、输入、输出、制作流程、制作路径、真实素材检索、程序化与媒体处理、工具与预算、核心价值、对你的意义、适用场景、可扩展场景、产品对比、边界与验证、版本与网页。

网页开头以四项导读直接说明：

- **能力：** 研究、脚本分镜、素材生成与检索、既有视频处理、程序化画面、合成、制作管理及导出。
- **原理：** 外部助手按 YAML 和技能工作，以结构化成果交接，并调用素材模型、本地处理工具与渲染器；检查点校验部分格式、前置条件与确认。
- **价值：** 阶段职责和成果契约让制作可检查、可修改、可复用；模型与执行工具可以按能力适配替换，效率和质量优势仍待实测。
- **扩展：** 项目解说、课程科普、软件演示、产品短片、语言版本和既有内容复用，并探索 RAG 资料、自有素材、栏目模板、中文规范、工具接入、恢复和可编辑协作。

完整内容含 34 项能力、12 条制作流程、27 项固定来源、一幅 2200×4753 完整图、阶段教学交互，以及包含基准在内的11项产品对比和七维 BaoCut 对照。图、JSON 和文字导读可以下载。

## 首轮公网验证

`publication-http-first.json` 实际请求21个公开地址，全部 HTTP 200：

- 项目 HTML、CSS、JavaScript、四项图像资源、研究 JSON、比较 JSON 与文字导读。
- 首页、构建清单、首页完整图。
- 已有八个演示入口：001、002、005、006、007、008、009、010。

项目公开文件与上述内容提交的 Git blob 逐字节一致；首页、完整图和清单与对应构建快照一致。首页18项摘要完整保留，无截断或折叠。Windows 工作区可能使用 CRLF，项目文件以 Git blob 为准，避免把换行转换误判为发布差异。

`public-web-verification.json` 的公网浏览器检查已通过20组，涵盖：

- 四项导读与元信息对应，首页18项完整摘要和完整图入口。
- 34项能力、12条流程、27项来源、本地锚点和唯一 ID。
- PNG/SVG 实际下载、原尺寸查看、JSON/文字导读下载。
- 11项比较、七维 BaoCut 表格与来源对应。
- 分类、搜索、三条制作路径、八阶段与确认门、重置。
- 1440 / 1024 / 768 / 390 / 320 px 视口、关闭 JavaScript 阅读和本地文件阅读。
- 无脚本错误和页面自动外部请求。

本地发布副本同样通过20组检查；仓库工具测试35项，34通过、1项因 Windows 符号链接条件跳过。GitHub Actions 的校验、构建与部署另已成功。

## 正式入口与最终证据

首轮公网检查通过后才填写 `project.json.demo_url`，同步首页、研究文档、网页说明与部署记录。正式入口登记后的资源验证保存在 `publication-http-final.json`；公网交互结果使用独立的 `public-*.png` 截图。验证记录注明对应提交与实际时间，不把初次发布、正式入口登记和上游运行验证混为同一件事。

## 能力边界

这次发布的是中文研究导读和浏览器内教学状态。没有安装上游完整系统、配置付费密钥、运行 GPU 模型或生成真实成片。中文效果、人物连续性、真实费用、性能、恢复和跨产品导入仍待实验；RAG → 制作 → BaoCut 的组合尚未集成。外部来源链接按既有固定版本研究引用，没有把网页 QA 当作逐条实时外链审查。

## 复查

```powershell
python scripts/update_index.py --check
python -m unittest discover -s tests -v
python scripts/build_site.py --output site-openmontage-release
python projects/011-openmontage/experiments/verify_publication.py https://yydshly.github.io/1013_codex_project/ site-openmontage-release projects/011-openmontage/experiments/results/publication-http-final.json
```

公网浏览器命令为 `verify_web.cjs` 加 `--public`，使用已有 Playwright 与本机 Chromium 浏览器；依赖不随静态网页发布。
