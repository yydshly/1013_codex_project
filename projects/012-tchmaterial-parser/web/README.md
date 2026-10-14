# 小学教材批量下载与整理 · 中文理解网页

本页以“下载不同版本的小学资料，方便批量下载和自动整理”为主线，全面汇总本次讨论。页面也准确说明上游覆盖初中、高中，实际资源以平台提供为准。

## 内容与交互

- 十二项章节导航，另有平台、工具、本地资料库的角色说明。
- 当前能力、直接用官网与工具的便利对照、适用场景与对你的价值。
- 四种场景选择：少量教材、小学整学期、教材版本比较、备课与配套资料。
- 六项人工教材版本核对与重置；全部勾选也不代表自动验证教材一致性。
- 下载源与地址分工，六步可选择的下载原理解释。
- 使用路线、自动分类目录示意与空白资料登记表下载。
- 四阶段扩展建议，RAG 衔接思路、当前能力边界、常见问题与固定源码依据。
- 六项未来扩展场景及实现前提：资料台账、版本更新、章节对照、备课材料库、音频检索与带引用问答，明确区分现有与未来能力。
- 全面理解总览 PNG、保留原版 SVG 简图、桌面与手机响应式、键盘操作和打印样式。

这是理解导读，不是教材下载应用。网页不请求教材平台、不使用登录凭据、不执行下载或 RAG。场景建议与步骤内容是解释文本；下载按钮生成的是 17 列空白 CSV，供自行登记资料来源与版本。

## 技术与运行

原生 HTML / CSS / JavaScript，无安装依赖、无外部字体、无后端或模型密钥。可直接打开 index.html 阅读；本次实际验证使用 HTTP 服务，未将文件直开方式作为测试结论。

在仓库根目录运行：

    python scripts/build_site.py --project 012-tchmaterial-parser --output site-tchmaterial-preview
    python -m http.server 8812 --bind 127.0.0.1 --directory site-tchmaterial-preview

访问：

    http://127.0.0.1:8812/012-tchmaterial-parser/

首页返回链接指向构建预览的根索引。Ctrl+C 停止服务器；本次预览服务在验证结束后停止，后续访问需重新启动。

也可单独预览 web 目录，但此时“返回项目索引”不指向完整研究站点，推荐使用上面的汇集预览。

## 部署约定

资源采用相对路径，章节采用 hash，适配仓库站点独立子路径：

    /1013_codex_project/012-tchmaterial-parser/

遵循[仓库部署约定](../../../docs/deployment.md)。正式构建默认只包含 Git 已跟踪文件，本地 --project 预览允许当前新建未提交的文件；实际提交、发布并验证后才能填写 demo_url。本项目于 2026-10-14 发布，[正式网页入口](https://yydshly.github.io/1013_codex_project/012-tchmaterial-parser/)已通过公网访问、文件一致与交互检查；入口已登记。

## 图像与来源

- assets/understanding-summary.png 与 ../assets/understanding-summary.png 内容相同，1086 × 1448；本仓库根据固定源码使用内置 imagegen 生成，包含来源、优点、原理、价值、场景、边界及扩展。提示词与依据保存在[生成说明](../experiments/infographic-prompt.md)，非上游截图。
- assets/understanding-overview.svg 与 ../assets/understanding-overview.svg 内容相同，为保留的原版 SVG 简图，非上游截图。
- 首页教材封面、分类文件树均为示意，不代表真实教材封面或已下载资源。
- ../assets/01-web-desktop.png：本地桌面首页实拍。
- ../assets/02-web-mobile.png：390px 宽度的手机首页实拍。
- ../assets/03-web-mechanism.png：六步下载原理区实拍。
- ../assets/04-public-desktop.png：首次发布后的公网桌面首页实拍。
- ../assets/05-public-mobile.png：公网 390px 手机能力区实拍。
- ../assets/06-public-guide.png：公网完整理解图显示实拍。

截图来源：2026-10-14，本地构建预览的浏览器截图。页面研究依据为上游固定 commit 244170e17bf8bc97401f65e04d261533d252572a；本地网页实拍不证明上游下载功能已经运行。

## 本次验证

页面、CSS、JavaScript、图像、站点索引预览及首页引导图请求成功。四场景、六步流程、版本核对与重置、空白 CSV 实际下载、键盘选择与折叠说明经过检查；桌面、390px / 320px 无页面横向溢出，浏览器检查未发现错误或警告。

详细记录与范围见[验证记录](../experiments/results/verification.md)与[公网发布记录](../experiments/results/publication-2026-10-14.md)。首次公网 18 个地址、25 项浏览器检查通过，正式入口登记后再次核对 18 个最终地址与内容，全部通过。教材端到端下载、音频和书签、学校版本对应、平台全部库存与后续 RAG 效果尚未实测。
