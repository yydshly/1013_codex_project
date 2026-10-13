# 2026-10-14 · Jev 理解网页发布验证

本记录验证静态研究网页的发布与交互，不是 Jev、普通小模型或执行模型的能力评测。

## 发布身份

- 研究仓库：`yydshly/1013_codex_project`，分支 `main`。
- 内容提交：`cc171f4bf3b096b4c4d45930b856af049d9ba5a0`。
- 上游研究版本：`kerpopule/hermes-jev-skills@31f476cac49713b6bf88c00d42382542e1c36965`，MIT。
- [GitHub Actions 构建与部署](https://github.com/yydshly/1013_codex_project/actions/runs/38428497187)：build 与 deploy 成功。
- [项目网页](https://yydshly.github.io/1013_codex_project/007-hermes-jev-skills/#understanding) · [导航首页](https://yydshly.github.io/1013_codex_project/)。
- HTTP 核对时间：2026-10-14 00:13:50，Asia/Shanghai；原始记录使用 UTC。

验证后才填写 `project.json` 的 `demo_url`。该记录对应首次内容部署；在线地址、文档和索引的更新随后单独提交发布，保持首次验证的依据可追溯。

## 发布内容

十个章节说明库的能力、Jev 的实际作用和位置、上游架构与个人扩展、默认机制、具体任务、标准设置、价值验证、判断器选择、个人意义、扩展基础与证据边界。提供完整理解 PNG、四类任务 × 三种判断方式、六项条件调整与空白评测表。

首页完整展示十二项摘要：库的能力、Jev 的作用、所在位置、路由原理、输入与输出、我们的理解、标准怎么设、何时使用、可扩展基础、对我的意义、价值怎么证实、边界与验证。引导图在索引表外展示。

正式构建只包含已提交的 001、002、007 静态项目。其他尚未提交的本地研究目录未进入本次提交和发布。保留原有项目入口，不提交临时构建目录、依赖、密钥或模型后端。

## HTTP 与内容一致性

以下均使用正式 URL 实际请求，返回 HTTP 200。首页内容与按该提交元信息生成的导航 HTML 一致；项目 HTML、CSS、JavaScript、两处 PNG 及原有项目页的 SHA-256 与该提交 blob 一致。构建清单准确列出三个项目。

| 资源 | 结果 |
| --- | --- |
| 站点首页 `/1013_codex_project/` | 200；生成内容一致，摘要完整 |
| 项目页 `007-hermes-jev-skills/` | 200；内容一致 |
| `007-hermes-jev-skills/styles.css` | 200；内容一致 |
| `007-hermes-jev-skills/app.js` | 200；内容一致 |
| `007-hermes-jev-skills/assets/understanding-overview.png` | 200；2,249,534 字节，内容一致 |
| `previews/007-hermes-jev-skills.png` | 200；内容一致 |
| `001-infinite-bookshelf/` | 200；已有页面保留，内容一致 |
| `002-production-agentic-rag-course/` | 200；已有页面保留，内容一致 |
| `site-build.json` | 200；只列出已提交的三个静态项目 |

逐项 URL、字节数、实际和预期 SHA-256 保存在 [原始 HTTP 验证记录](./publication-2026-10-14.json)。总览 PNG SHA-256 为 `6ea71ab4edaf4ab727c4fa260e35ea56d18246800c0d9b00afe349096b89db0b`。

## 浏览器与本地检查

- 新版本地：十二个任务 / 方式组合正确更新；七个标准分支正确；十个目录锚点有效。
- 响应式：1280px 桌面、390px 与 320px 窄屏，无页面横向溢出；宽表格在自身区域滚动。
- 下载：本地和公网实际下载 UTF-8 BOM CSV，均为 33 列，包含任务与模型版本、验收、标准、策略、结果、费用与工时。
- 公网浏览器：`修复联动 × Jev` 显示依赖判断与“暂用 B”；首页显示十二项摘要和总览引导图；返回项目正常；PNG 实际加载，原图宽 941 像素。
- 浏览器日志：检查时无 JavaScript 错误或警告。
- 元信息与索引：工作区和只含实际提交文件的独立快照均通过校验。
- 现有仓库测试：32 项完成，Windows 本地 31 通过、1 因符号链接权限跳过；远端 Ubuntu 的检查步骤成功。
- JavaScript：Node.js 22.15.0 语法检查通过。网页无构建依赖与环境变量。

![公网架构区实拍：Jev 所在位置与我们的扩展分工](../../assets/06-published-web.jpg)

来源：2026-10-14，公开项目 URL 的真实浏览器截图。其他新版截图见 [网页运行与检查说明](../../web/README.md)。

## 未验证事项

没有真实模型 API 调用、A / B 执行、概率校准或费用优势实验。个人路由与扩展方案仍为待验证设计；网页预设判断不代表 Jev 或小模型的真实回答。后续按 [研究文档](../../README.md#如何验证标准与价值) 比较四条完整流程。
