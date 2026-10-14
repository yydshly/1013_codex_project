# Free Claude Code 理解网页发布记录

日期：2026-10-14。研究版本：`74d4ccfde724f7416fa2a728d594d704dddc7c94`，上游许可证 `AGPL-3.0-only`。

## 内容与公开入口

- [在线研究网页](https://yydshly.github.io/1013_codex_project/016-free-claude-code/)。
- [内容提交 11260be](https://github.com/yydshly/1013_codex_project/commit/11260beec078ae0a45cfb535908d0eacb2e6b538)。
- [GitHub Pages 工作流 38520473250](https://github.com/yydshly/1013_codex_project/actions/runs/38520473250)，build 与 deploy 均 success；元信息、索引、仓库测试及静态构建步骤通过。

摘要与正文清楚解释四个问题：能力是统一模型接入、消息和工具适配、流式转换及配置路由；原理是在 Agent 与真实模型之间增加网关，适配并转发请求和响应；价值是接口适配带来的接入解耦，让工作方式与模型服务分别选择；可扩展到多模型编程、写作与报告、资料问答、网页审查、任务选模及团队入口，分别注明需要补齐的上层能力和验收标准。

保留十五项完整分段摘要、原有六步请求教学、角色和协议差异、成本来源、既有项目的底层比较、使用路线与固定源码证据。配置式选模与备用不等于自动判断最优模型，接口可替换不等于不同模型能力等价。

## 沿用我们的引导图

完整总览图和底层模块图继续使用本次原创 PNG / SVG，没有重新生成或替换。它们位于项目 assets/、公开 web/assets/；首页预览也使用完整理解图。

- 完整理解 PNG：1600 × 2460；SHA-256 `34fa4a77cca03af798dc341abd2a054738cc2df08c26ede28638233f0966340d`。
- 同源 SVG：SHA-256 `3cce6e72362b11e263f52ae162e85a387b4d33bc02c0766ad3cfb0a10c21209c`。
- 图中包含 Agent → 网关 → 真实模型、网关内部、工具闭环、能力、场景、价值、意义、扩展、同类定位和边界；均为解释图，非上游运行截图。

## 实际公开验证

[资源检查 JSON](./publication-content.json)记录 23 个公开地址全部通过：11 项首页、构建清单、完整图预览和项目页面资源逐字节一致，其他 12 个已有演示入口均 HTTP 200。项目文件以内容 commit 的 Git blob 作为基线，首页与清单以同版本生成站点为基线；正确处理 Git 的文本换行转换，没有将本地 CRLF 与 Linux 发布的 LF 差异误记为内容变化。

[公网浏览器 JSON](./publication-browser.json)记录十组检查：十五个章节、正文和来源、六步请求与重置、Claude Code / Codex 示例、云端 / 本地 / 自定义模型示例、教学备用、问答、PNG / SVG / CSV 下载、两图放大及键盘退出、390px 手机阅读与滚动、无 JavaScript 正文，以及保存的 HTML。公开页无脚本错误；加载过程仅访问本站静态资源，没有发送模型请求。01—06 截图已在实际公开网页复核时重新捕获。

独立发布工作区以远端最新 main 为基线，只提交本项目与自动生成的索引；正式构建保留 13 个静态演示：001、002、005、006、007、008、009、010、011、012、013、014、016。没有将当前共享工作区其他未提交项目混入发布。仓库本地测试 35 项，34 通过、1 项因当前 Windows 用户无法创建符号链接而跳过；Linux 发布工作流的测试步骤通过。

在实际访问和内容一致性通过后，登记 `demo_url`，更新项目说明、总索引与部署记录。后续入口登记与最终验证会补充在本文件末尾。

## 验证边界

这是静态研究导读与固定教学交互，没有运行 FCC、真实 Agent 或模型。上游安装、模型接入、免费资格、工具调用质量、长上下文、真实中断恢复、费用和任务收益仍待实测；六类应用组合是可扩展方向，尚未实现为新的业务系统。

## 复核方式

从仓库根目录先生成全部已跟踪演示，再比较指定提交的项目资源和同版本首页：

```powershell
python scripts/build_site.py
python projects/016-free-claude-code/experiments/verify_publication.py --site-dir site-dist --commit HEAD --output projects/016-free-claude-code/experiments/results/publication-final.json
```
