# 研究生成、页面验收与后续复现

本目录不包含 Vibe42 安装副本或可运行远控后端。本次只读核对官方资料，用原创文字、解释图和静态教学交互整理机制；没有在 Windows 研究机安装 Companion。

## 研究基线

- 日期：2026-10-14，Asia/Shanghai。
- Vibe42：官网下载元数据标注 0.11.0；未安装，无可确认的公开源码 commit 或源码许可证。
- 部分公开响应的 UTF-8 文本 SHA-256、查阅方法和以前研究的固定版本见 [source_records.json](./source_records.json)。没有保存完整第三方安装说明或脚本。
- [results/verification.md](./results/verification.md) 记录实际页面与工具检查；真实产品安装、网络、安全、通知和性能另列待验。

## 生成材料

从仓库根目录运行：

```powershell
python projects/010-vibe42/experiments/build_research.py
```

`build_research.py` 仅使用 Python 标准库，是 14 个专题、12 个对比维度、18 项证据和 21 项来源的内容源。它生成子项目 README、完整静态 HTML、研究 TXT、证据 JSON 和交互配置。修改正文优先改这个文件再生成，以免网页与 README 漂移。原创 SVG、样式、交互逻辑和验收记录独立维护。不会连接账号或执行产品安装。

新增的`build_overview.py`由主生成工具调用，维护“00理解总览”与7个原理节点、3条教学路径、4个场景、6个扩展方向和4项价值判断；使用同一SVG底图生成完整总览及网页中的原理放大视图。静态导出为1400×2250，节点只有在网页加载本地JavaScript时可交互。

初次导出PNG的顺序为：生成内容 → 构建预览 → 启动本地HTTP服务 → 运行`render_overview.cjs` → 再构建预览，将PNG加入公开静态目录。导出脚本从HTTP读取原创SVG，检查文字未出画布，写入`assets/`与`web/assets/`两份相同PNG；无需安装Vibe42或调用模型。

## 页面验收

```powershell
python scripts/build_site.py --project 010-vibe42 --output site-preview-vibe42
python -m http.server 8775 --bind 127.0.0.1 --directory site-preview-vibe42
```

在另一个终端使用已经安装的 Node.js 和 Playwright：

```powershell
node projects/010-vibe42/experiments/verify_web.cjs http://127.0.0.1:8775/010-vibe42/
# 章节导航改动后的定向复验：
node projects/010-vibe42/experiments/verify_navigation.cjs http://127.0.0.1:8775/010-vibe42/
node projects/010-vibe42/experiments/render_overview.cjs http://127.0.0.1:8775/010-vibe42/assets/understanding-overview.svg
node projects/010-vibe42/experiments/verify_overview.cjs http://127.0.0.1:8775/010-vibe42/
```

验收脚本检查正文、子路径与资源、架构模块、六步示意、故障条件、直连/中继、证据筛选、键盘、下载、手机宽度、关闭 JavaScript 和本地文件打开。它不点击外部来源、运行 Agent 或连接产品服务。Playwright 需在本机可用；本次使用 Codex 附带运行时，具体版本与截图见验收记录。

库工具检查：

```powershell
python scripts/update_index.py
python scripts/update_index.py --check
python -m unittest discover -s tests -v
```

## 公网发布验证

正式发布使用仓库GitHub Pages工作流，保留其他已跟踪静态演示。工作流成功后，用`verify_publication.py --commit <发布commit> --run-url <Actions链接>`访问公开资源，并与Git提交中的实际字节比对。这样区分本地Windows换行和部署端Git文件，避免将本地HTTP当作公网证据。结果写入`results/publication-http.json`。

用`verify_publication.cjs <HTTP或HTTPS入口> publication-browser.json`检查6项页面摘要、17项统一索引摘要、原理节点与路径、中继说明、PNG实际下载、手机布局和关闭JavaScript的正文。它不操作真实产品，且只接受HTTP/HTTPS。执行依赖与现有浏览器脚本一致。

## 后续真实产品实验（未执行）

| 范围 | 操作 | 需要记录 |
| --- | --- | --- |
| 安装与身份 | 单台 Mac/Linux 主机、一个授权控制端 | 系统/应用/Agent版本、服务与安装变更、设备身份 |
| PTY | 中文输入、粘贴、Ctrl+C、尺寸变化、交互程序 | 输出是否准确、输入是否重复、进程退出行为 |
| 持续会话 | 手机断网、切后台、主机锁屏与休眠、服务退出、重启分别测试 | 活进程、输出、会话身份与 Agent 历史分别是否恢复 |
| 网络 | 同局域网、蜂窝、受限网络与中继路径 | 路径证据、失败原因、重连时间、是否重复业务操作 |
| 授权与隐私 | 撤销设备、错误身份、查看传输和必要日志 | 撤销时机、泄露范围、密钥与元数据边界 |
| 状态通知 | working、done、blocked、error 与关闭 App 推送 | 状态来源、误报/漏报、敏感内容、限频与去重 |
| 文件与桌面 | 权限、编辑冲突、大文件与中断、Mac画面及输入 | 完整性、冲突策略、权限、延迟与资源消耗 |

在执行这些实验前，不把官方声明改写为已复现结果。实验产物不得含密钥、配对码、私人终端输出或推送令牌。
