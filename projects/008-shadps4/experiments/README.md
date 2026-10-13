# 公开样例与网页复现

研究日期：2026-10-14。本目录包含真实原生程序复现和网页端到端验证。两类实验分别记录，不用浏览器动画代替原生结果。

## 本机运行公开 PS4 程序

目标：不使用商业游戏或 Sony 系统模块，观察 shadPS4 是否实际执行 PS4 自制程序，并显示其帧缓冲。

依赖：Windows x86-64、Python 3.10+、联网下载和可工作的 Vulkan 驱动；首次准备约 200 MB 官方开源发布包。脚本使用固定版本、官方发布地址和 SHA-256 校验，无需安装完整编译环境。

在仓库根目录执行：

```powershell
python projects/008-shadps4/experiments/run_public_example.py --prepare-only
python projects/008-shadps4/experiments/run_public_example.py --sample hello_world --seconds 5 --driver-select "*nv*"
python projects/008-shadps4/experiments/run_public_example.py --sample graphics --driver-select "*nv*"
```

本机 NVIDIA 实测使用进程级 `VK_LOADER_DRIVERS_SELECT=*nv*`，其他设备应调整或省略 `--driver-select`。这没有修改全局驱动设置。graphics 默认持续运行，关闭窗口或 Ctrl+C 停止；加 `--seconds 10` 可定时停止。Hello World 关闭图形后端，预期先输出 `Hello world! Waiting 2 seconds!`，两秒后输出 `Done. Infinitely looping...`。graphics 预期打开蓝色 Mandelbrot 分形窗口。两个样例按原源码持续循环，观察后停止属于正常实验操作。

脚本下载官方 shadPS4 v0.19.0 和 OpenOrbis v0.5.3 的预编译 ELF / Windows 转换工具，将 ELF 转换成模拟器可加载的 OELF / SELF 文件，配置隔离的 portable user 目录后启动模拟器。此复现未重新编译 shadPS4 或样例，不能据此宣称源码构建通过。

已实测：Hello World 输出、graphics 日志及窗口画面；完整设备、驱动、实际运行提交、下载摘要和初次失败见 [原生运行记录](results/runtime-verification.md) / [JSON](results/runtime-verification.json)。原始输出见 results/。本次 graphics 的像素由 CPU 算出，经 VideoOut 和 Vulkan 呈现，未验证 GCN 着色器重编译、商业游戏、声音、手柄、存档、联网或长期稳定性。

下载包、转换产物、可执行程序、配置和新日志全部放在被忽略的 `runtime/`；它们不属于入库研究素材。上游样例的准确源码、版权和完整 GPL-3.0 文本保留在 [third_party/OpenOrbis/](third_party/OpenOrbis/)，来源详见 NOTICE.md。运行包许可与研究源码版本在各结果记录中分别说明。

## 验证本地中文网页

目标：在实际静态子路径检查完整交互、实测证据展示、CSV 下载与手机布局。

在仓库根目录构建并启动服务：

```powershell
python scripts/build_site.py --project 008-shadps4 --output site-shadps4-preview
python -m http.server 8773 --bind 127.0.0.1 --directory site-shadps4-preview
```

打开 `http://127.0.0.1:8773/008-shadps4/`。在另一个终端执行：

```powershell
node projects/008-shadps4/experiments/verify_web.cjs
```

浏览器验证需要 Node.js、Playwright 和对应 Chromium。脚本默认从现有依赖查找 `playwright`；也可用 `SHAD_PLAYWRIGHT_MODULE` 指定已有 Playwright 的绝对路径，用 `SHAD_WEB_URL` 指定包含末尾 `/` 的预览地址。依赖与浏览器不入库。

脚本检查 9 条请求 / 条件路径、失败停止、后退与重播、缓存复用、答题反馈、22 列 UTF-8 BOM CSV、实测 JSON 和截图、11 个目录目标、静态资源、返回索引及 320–1440 像素布局。实际截图保存在项目 assets/，结果见 [网页运行记录](results/web-verification.md) / [JSON](results/web-verification.json)。静态文件不提供原生模拟器启动服务，公网未部署。

## 文件用途

完整总览图的可编辑内容由 `create_comprehensive_map.py` 生成，`render_comprehensive_map.cjs` 使用现有 Playwright 将 SVG 渲染为 1800×3290 PNG，并检查所有文字是否越过画布或所属区域。结果见 [diagram-verification.json](results/diagram-verification.json)。图是固定研究结论的讲解整理，原生程序实测另行记录。

| 文件 / 目录 | 内容 |
| --- | --- |
| run_public_example.py | 下载校验、准备并运行公开 PS4 样例 |
| verify_web.cjs | 实际浏览器完整流程验证与截图 |
| create_comprehensive_map.py / render_comprehensive_map.cjs | 完整总览图生成、高清输出与实际文字边界检查 |
| results/ | 可入库的版本、环境、日志和结果，记录验证边界 |
| third_party/OpenOrbis/ | 引用的原始样例源码、来源和许可证 |
| runtime/ | 不入库的本地下载、二进制、配置和缓存 |
