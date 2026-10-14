# BaoCut 理解网页发布记录

日期：2026-10-14（Asia/Shanghai）。原项目研究版本：`7aa049e82e1367da013b7aba80f0b79033fa04ad`。

## 已验证内容发布

- 公开网页：https://yydshly.github.io/1013_codex_project/014-baocut/
- 内容提交：`f8682c7a7d3010cb368bcaa8920b33db8acc1233`。
- GitHub Pages 工作流：[38517467344](https://github.com/yydshly/1013_codex_project/actions/runs/38517467344)，结果 success。
- 首页完整保留 18 项摘要，说明定位、能力、原理、人机协作、输入输出、新增模块、价值、个人意义、场景、扩展前提、评估与验证边界。
- 网页新增四步执行原理、八种扩展场景及实现前提，保留固定协作教学示例。
- 沿用本次讨论的完整图；高清 PNG SHA-256 为 `34752eae7afd4e8a4255e8694088a4871441cb03ce37f5c9b96480a259f11de3`；SVG SHA-256 为 `0df78093f1cbb7df4cb63cab68f098bd6b6ec01b3201aad34d160c43e910bba7`，内容未改。

## 公开资源与交互

[内容发布检查 JSON](./publication-content.json)记录 22 个公开地址：11 项新网页、资源、首页、清单和引导图与快照逐字节相同；11 个原有演示入口均 HTTP 200。一次临时请求失败已单独重试并通过，保留在报告中。

[浏览器验证 JSON](./publication-browser.json)记录实际公开网页上的检查：8 行视频能力、8 项扩展场景、人工第二句保留、第三句局部更新、撤销、重置、PNG/SVG/TXT 下载，以及 390×844 手机布局；整页无横向溢出，扩展卡片为单列，无页面 error 日志。

正式静态构建包含 12 个已跟踪演示：001、002、005、006、007、008、009、010、011、012、013、014；未将工作区其他尚未提交的项目混入部署。14 的元信息与索引生成通过，仓库测试 35 项中 34 通过，Windows 符号链接检查跳过；GitHub 发布工作流的验证步骤成功。

## 后续入口登记

在内容发布与实际访问通过后，将真实公开地址写入 `project.json`，自动更新索引，并提交研究文档、验证记录与公开入口。登记后的工作流及最终资源复核随后补充。

## 验证边界

这是原创研究网页与固定教学交互，不执行上游 BaoCut 视频引擎或真实模型。未证明上游任务质量、费用、速度、长期稳定性或人工改动保留的可靠性；八种扩展场景是适配建议，未作为新系统实现。图片是原创理解图或本网页截图，非 BaoCut 产品运行截图。

## 复核方式

```powershell
python projects/014-baocut/experiments/verify_publication.py --site-dir site-baocut-release --output projects/014-baocut/experiments/results/publication-final.json
```

先按仓库部署约定生成包含全部已跟踪演示的静态快照；此脚本检查公开文件与该快照，以及原有演示入口。
