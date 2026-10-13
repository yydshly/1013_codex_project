# 2026-10-13 · 研究摘要与静态导读发布验证

日期按 Asia/Shanghai 记录。**这份记录仅验证本仓库研究材料、索引和静态导读，不验证上游采集、解析、检索、模型问答或 Agentic 运行效果。** 上游研究版本仍为 424a0eb99edf841994f2a9a053912b489d2a94ff，研究状态仍为 researching。

## 提交与发布

- 研究内容提交：[81f224c7ff5c606eebd0ce6162adc6798f2a3b0c](https://github.com/yydshly/1013_codex_project/commit/81f224c7ff5c606eebd0ce6162adc6798f2a3b0c)，已推送到 origin/main。
- 发布任务：[38418966428](https://github.com/yydshly/1013_codex_project/actions/runs/38418966428)，build 与 deploy 均成功。
- [站点索引](https://yydshly.github.io/1013_codex_project/) · [项目导读](https://yydshly.github.io/1013_codex_project/002-production-agentic-rag-course/) · [共识与理解图](https://yydshly.github.io/1013_codex_project/002-production-agentic-rag-course/#understanding)。
- [高清 PNG](https://yydshly.github.io/1013_codex_project/002-production-agentic-rag-course/assets/rag-understanding.png) · [矢量 SVG](https://yydshly.github.io/1013_codex_project/002-production-agentic-rag-course/assets/rag-understanding.svg)。

## 内容与来源

摘要完整展示定位、能力、原理、架构、输入、输出、价值、对你的意义、可扩展场景、扩展方向、使用路线与边界验证，共 12 个独立维度。原仓库来源、固定版本、MIT 许可证、29 项源码证据和 16 项后续复现任务随研究说明一并提交。

引导图使用我们已制作的 2400 × 3500 理解总览图：project.json 的 preview 指向 assets/04-rag-understanding.png，网页使用 web/assets/rag-understanding.png。两份 PNG SHA-256 相同。图保留源码实现、拟议适配及未验证运行状态，来源与编辑方式见 [认知图说明](../../references/understanding-overview.md)。

## 已通过的检查

| 检查 | 结果与范围 |
| --- | --- |
| 索引同步 | project.json、根 README 与站点摘要一致；首页逐项检查 12 个标签及完整正文，没有截断 |
| 本地测试 | 32 项仓库测试中 31 项通过，1 项因当前 Windows 用户不能创建符号链接跳过；远端发布工作流中的检查成功 |
| 本地页面交互 | 本次发布的网页与之前完成桌面、手机、文字版展开、PNG / SVG 下载和路线导出的前端一致，详见 web/README.md |
| 链接与公开范围 | Markdown 本地文件引用、网页图片和脚本路径有效；站点产物只汇集已跟踪静态项目，不收录未提交项目或制作代码 |
| 项目页、CSS、JavaScript | 公网 HTTP 200；响应字节 SHA-256 与提交对应 Git blob 一致 |
| PNG、SVG 与首页引导 PNG | 公网 HTTP 200；响应字节 SHA-256 与提交对应 Git blob 一致 |
| 首页 | HTTP 200，包含项目 001、002 入口及项目 002 的完整摘要与指定总览图 |
| 原有项目 | 项目 001 网页 HTTP 200，并与其未修改的提交 blob 一致 |

以上资源完整验证后，才填写 project.json 的 demo_url。后续文档提交登记正式地址和本记录，不改变上游研究版本或“尚未复现”的状态。

## 待验证

上游独立环境、数据采集、文档解析、索引、检索质量、回答引用、Agentic 分支、缓存失效、故障恢复、耗时与成本仍按 [复现清单](../README.md)推进。农业等新领域、权限、本地向量化、专题报告和与长文写作的整合仍是适配或扩展方向。浏览器打印 / PDF 输出尚未验收。
