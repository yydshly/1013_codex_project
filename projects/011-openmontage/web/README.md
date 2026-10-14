# OpenMontage 中文导读网页

原创静态研究页面，固定研究版本 `e45f5b12bd46440b04f3675af9a77d0718e6a254`。覆盖模型分工、核心价值、34 项能力、12 条制作流程、结构化交接、三种制作路径、代码处理、个人用途、产品对比、扩展与验证边界。

## 文件与依赖

- `index.html`、`styles.css`、`app.js`：静态页面与教学交互。
- `research.json`：能力、流程与固定来源目录。
- `comparison.json`：OpenMontage 基准与 10 个既有项目的职责、输入输出、差异、研究路径、版本、来源和许可证。
- `assets/overview.svg`：原创原理图，非上游截图。
- `assets/ability-map.svg` / `ability-map.png`：原创完整能力图，2200×4753；覆盖输入、组织、34 项能力、模型/算法/代码/规则、12 种效果、输出与扩展，可从 `#understanding` 查看及下载。
- `research-summary.txt`：可下载文字导读，由目录生成器生成。

页面无第三方前端依赖、外部字体或远程资源请求。完整正文、能力表与流程卡片预先写入 HTML，关闭 JavaScript 仍可阅读。JavaScript 提供类别与全文检索、制作路径切换、阶段交接模拟、重置与打印。

完整能力图使用 SVG 渲染，提供原尺寸 PNG 查看和两种格式下载；两张公开文件是同一幅图。源码与边界说明保留在图内，模型质量和扩展效果没有冒充运行实测。

新增 `#comparison` 产品与项目对比：11 行表格包含 OpenMontage 基准、BaoCut、写作、RAG、审查、决策、任务运行、软件调查、模型接入、会话工作台和远程入口。重点用七个维度比较 BaoCut，保留同目标案例、三类易混淆环节与未来组合设计。表格按手机宽度显示为逐项目内容，关闭脚本仍完整显示；对比清单可下载。依据各项目已有固定版本研究，不代表最新功能或同任务实测排名。

发布整理后，网页开头的 `#brief` 四项导读直接读取元信息的能力、原理、核心价值和可扩展场景；首页完整展示18项分项摘要，另有输入、输出、制作路径、检索、代码、工具费用、个人意义、场景、对比与验证。生成器同步 README 与文字导读，避免不同入口的摘要漂移。

## 本地预览

从仓库根目录执行：

```powershell
python projects/011-openmontage/experiments/build_research_catalog.py
python scripts/build_site.py --project 011-openmontage --output site-openmontage-preview
python -m http.server 8791 --bind 127.0.0.1 --directory site-openmontage-preview
```

打开 `http://127.0.0.1:8791/011-openmontage/`。直接打开本目录的 `index.html` 也能阅读与交互；返回首页功能在汇总站点中使用。

## 部署约定与范围

所有资源使用相对路径，兼容仓库 Pages 前缀 `/1013_codex_project/011-openmontage/`。返回索引用 `../`，章节使用 hash。公开 TXT、JSON 与 SVG 包含研究资料，不含凭据。Markdown 研究文档导航指向仓库。

按 [仓库部署约定](../../../docs/deployment.md) 处理：已发布至 [OpenMontage 理解网页](https://yydshly.github.io/1013_codex_project/011-openmontage/#brief)，实际核对资源与交互后登记 `demo_url`。正式构建收集全部已跟踪静态项目，已有八个演示入口保留；工作区其他未发布研究未随此次提交上传。发布记录见 `../experiments/results/publication-2026-10-14.md`。

## 验证与限制

本地浏览器验证范围见 [验证记录](../experiments/results/verification.md)，公网验证见 [发布记录](../experiments/results/publication-2026-10-14.md)。网页演示自己的教学状态，不执行 OpenMontage、模型调用、素材检索或视频渲染；示例 JSON 是非完整 schema 的教学片段。上游 API、真实中文效果、费用和制作效率仍未验证。
