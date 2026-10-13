# shadPS4 理解网页公网发布验证

2026-10-14，中文理解网页已发布至 [GitHub Pages](https://yydshly.github.io/1013_codex_project/008-shadps4/)。网页内容提交为 [`1cda73485ccfe63e7862403387ae5b5d3363c478`](https://github.com/yydshly/1013_codex_project/commit/1cda73485ccfe63e7862403387ae5b5d3363c478)，[构建与部署运行](https://github.com/yydshly/1013_codex_project/actions/runs/38443817551)成功。验证通过后才填写 project.json 的 demo_url，并另行提交正式地址与本记录。

## 内容与引导图

首页完整展示十二项摘要：定位、能力、原理、输入输出、研究展示、实际验证、验证边界、价值、对你的意义、扩展方向、复现环境和网页状态。摘要说明 shadPS4 如何加载 PS4 程序、安排游戏内存和执行环境、兼容系统行为、转换图形任务，以及如何用于系统学习、兼容性研究与回归测试。

首页和详情页均使用本次讨论整理的 1800×3290 完整总览图。首页 previews/008-shadps4.svg 与项目 assets/comprehensive-map.svg 的提交内容完全一致；详情页提供 SVG / PNG 下载。图与正文明确说明：模拟器通过主机操作系统与驱动使用 CPU、GPU 和内存，资源组织并不等于裸机操作系统或独占硬件。

## 实际验证

| 检查 | 结果与证据 |
| --- | --- |
| 公开地址 | 19 个地址均 HTTP 200，包括首页、构建清单、项目页面与资源、首页引导图以及已有五个项目入口 |
| 项目资源 | 11 个静态资源 SHA-256 与网页内容提交的 Git blob 完全一致；首页引导图另行核验一致 |
| 首页摘要 | 十二项摘要的完整文本均存在，没有截断或折叠；指定预览路径与来源说明存在 |
| 保留已有网页 | 构建清单含 001、002、005、006、007 和 008 六个静态项目，前五个入口实际可访问 |
| 公网浏览器 | Chromium 151.0.7922.34 的 11 项检查通过，包括资源、教学流程、键盘、缓存、答题、CSV 下载、手机布局、返回索引与无页面错误 |
| 仓库校验 | 索引检查与整站构建通过；32 项测试中 31 项通过、1 项因 Windows 符号链接不可用跳过 |

逐项地址、摘要与 SHA-256 见 [publication-2026-10-14.json](./publication-2026-10-14.json)。公网浏览器结果与实际截图见 [web-verification.md](./web-verification.md) / [JSON](./web-verification.json)。验证脚本为 [verify_publication.py](../verify_publication.py) 和 [verify_web.cjs](../verify_web.cjs)。

## 验证范围

本记录验证静态网页发布、内容完整性与浏览器教学交互。网页未执行 PS4 游戏。原生模拟器的 Hello World 和 CPU 生成 Mandelbrot 分形窗口已在本机单独实测，详见 [runtime-verification.md](./runtime-verification.md)。这些结果未证明 GCN 着色器重编译、商业游戏、3D 性能、音频或长时间稳定性。

发布包只包含已跟踪的静态网页和指定引导图；原生程序、游戏文件、系统模块、下载包、配置、依赖和缓存没有进入网页产物。本次使用独立发布工作区，保留已有网页，未收录其他尚未完成的本地研究。
