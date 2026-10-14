# cmux 研究网页验证记录

日期：2026-10-14。研究基准 `cdbe99596fe13784ec5ea24d2e1c720a8f67f5cb`。这是本仓库教学页验证，不是上游应用的运行验证。

## 命令验证

| 检查 | 结果 |
| --- | --- |
| `node --check projects/009-cmux/web/app.js` | 通过 |
| `node projects/009-cmux/experiments/check-message-model.cjs` | 9 项教学模型检查通过 |
| `python projects/009-cmux/experiments/check-static.py` | 10 章、20 来源锚点、本地资源、SVG 副本、版本与元信息通过 |
| `python scripts/update_index.py --check` | 项目元信息与自动索引一致 |
| `python -m unittest discover -s tests -v` | 35 项：34 通过、1 跳过；当前 Windows 用户无法使用符号链接 |
| `python scripts/build_site.py --project 009-cmux --output site-cmux-preview` | 成功，显式只收录 009 项目 |

上述索引检查在当次运行中通过。后续收尾复查时，共享工作区新增的 `012-tchmaterial-parser` 元信息引用了尚未生成的预览图，导致全仓库 `update_index.py` / `--check` 暂时失败。009 的独立资源与元信息检查通过；没有改动 012 的文件，也不能把此前通过的索引检查当作共享工作区最终状态全部通过。根 README 已包含本项目完整摘要与原创引导图，待该项目资源完成后应再统一生成检查。

Python 3.10.11、Node.js 22.15.0、Windows；预览通过 Python 标准库 HTTP 服务及 Codex 内置浏览器进行。预演目录 `site-cmux-preview/` 是被忽略的构建产物，不入库。

## 浏览器行为

| 行为 | 实际观察 |
| --- | --- |
| 载入 | 正文 10 章、样式、JS 与两张 SVG 正常显示 |
| 定位待输入 | 从 A 跳到 B / 网页实现，显示需要输入 |
| 定向输入 | 输入文字只加入 B 的输出，B 变为运行；C 保留原始独立内容 |
| 通知 | A 可模拟通知；当前焦点保持，定位按钮可跳到 A |
| 能力筛选 | 组织协作显示 3 项，计数一致 |
| 架构路径 | 消息路径切换后显示 queued、接收方 Hook、delivered 与 read 解释 |
| 空闲 Codex | 发送后保持 queued，按钮明确要求模拟人提交下一次提示 |
| 投递与已读 | 下一次提示后 delivered，再结束该轮到 read；提示明确不等于任务验收 |
| 等人回答 | 发送后暂缓；模拟人回答后仍 queued，再经过适配点才 delivered |
| 忙碌 Codex | 下一步明确模拟即将停止的 Hook |
| 关闭接收 | queued 变 failed，继续按钮禁用，不自动重送 |
| 草稿保护 | 状态变化后草稿文字保持原样 |
| 价值选择 | 选择漏看提醒时，提示先改善提醒与定位，并说明当前 Windows 条件 |
| 移动布局 | 390 × 844 与 320 × 740 无页面横向溢出；工作台输入、消息选择与按钮可操作 |
| 控制台 | 检查时未捕获 error / warn |
| 下载 | 真实触发总览 SVG 和文字摘要下载，两份下载文件的 SHA-256 均与源资源一致 |
| 本地资源 | 首页、项目页、CSS、JS、两张 SVG、文字摘要和索引预览共 8 个地址返回 HTTP 200 |

表格在手机上允许自身横向滚动，页面整体无横向滚动。架构 SVG 缩小后可保存或打开原图；正文、四条路径和折叠说明提供文字解释。打印入口调用浏览器打印；打印前展开全部解释和能力行，打印后恢复界面选择。本次未实际生成浏览器 PDF 文件。

## 图片与来源

- [03 桌面页面](../../assets/03-web-desktop.jpg)：本仓库网页的浏览器截图，非上游运行截图。
- [04 操作工作台](../../assets/04-web-workbench.jpg)：本仓库模拟会话、提醒与输入效果。
- [05 手机页面](../../assets/05-web-mobile.jpg)：390px 视口的实际网页截图。
- [06 手机消息实验](../../assets/06-web-mobile-message.jpg)：等待人回答时 queued 的教学提示。
- [01 总览 SVG](../../assets/01-understanding-overview.svg)、[02 架构 SVG](../../assets/02-architecture.svg)：本仓库依据固定源码原创绘制；`web/assets/` 保留对应副本。

## 未验证事项

上游 macOS 客户端、真实 CLI 登录、模型调用与费用、真实 Hook 时延、消息 lease / ack 实现、Claude teams 执行、恢复成功率、远程断线、Cloud 与移动全流程均未运行。

9 项消息检查只校验教学模型，不能证明上游消息队列可靠性。状态 read、idle 或程序退出不会成为本项目的任务验收信号。Windows 下不能据此声称已复现原生应用。

本次未提交、推送或部署公网；`demo_url` 为空。研究网页按仓库既有子路径约定准备，实际公网入口需发布和访问验证之后再登记。

后续新增完整理解图的制作、检查、索引阻塞与浏览器验证限制见 [完整理解图验证](./complete-understanding-2026-10-14.md)。此前 012 缺图已不再是本次观察到的阻塞；当前索引受到其他两个子项目重复使用 015 编号影响。
