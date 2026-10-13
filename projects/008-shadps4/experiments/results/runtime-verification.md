# shadPS4 公开示例实机验证

验证日期：2026 年 10 月 14 日。本记录描述在本机 Windows 上实际运行模拟器的结果；没有运行实体 PS4 主机。

## 结果

- 官方 shadPS4 v0.19.0 Windows SDL 包 SHA-256 与发布资产摘要一致，`--help` 退出码为 0。
- OpenOrbis v0.5.3 `hello_world` 经官方 `create-fself.exe` 转换后，在 shadPS4 内实际执行，输出 `Hello world! Waiting 2 seconds!` 与 `Done. Infinitely looping...`。
- 同版本 `graphics` 样例成功注册 1920×1080 帧缓冲，进入绘图循环，窗口真实显示蓝色 Mandelbrot 分形。
- 保存了目标模拟器窗口截图 [openorbis-graphics-live.jpg](../../assets/openorbis-graphics-live.jpg)。截图 1282×752，图像随窗口缩放；没有拼接、重绘或包含用户桌面。
- 本仓库的复现脚本实际运行了两种样例：hello_world 观察 5 秒，graphics 观察 6 秒，随后停止测试进程。

## 实验说明

这条链路是真实的：**公开 PS4 homebrew 可执行文件 → shadPS4 加载/链接 → guest CPU 代码 → HLE 内存与 VideoOut 服务 → Vulkan → 电脑窗口**。

`graphics/main.cpp` 的 `drawMandelbrot` 在 guest CPU 上计算每个像素，再通过 `Scene2D` 提交帧缓冲。它证明公开 PS4 程序、部分系统兼容层与显示链路能够配合工作；它没有覆盖 PS4 GCN 着色器到 SPIR-V 的重编译，也没有覆盖商业游戏的 3D 绘制。

样例官方源码中的 `main` 都是无限循环。Hello world 在完成 2 秒休眠后进入无限循环，graphics 持续计算并提交画面；本次观察完成后主动结束测试进程，这不是样例自行正常退出。

## 版本与环境

| 项目 | 实际值 |
|---|---|
| 静态源码研究 ref | `23c41333822fe8eca4c609b43119180af63ae4ac` |
| 运行包 | `shadps4-win64-sdl-0.19.0.zip` |
| 运行包内日志 commit | `c7e065d1b415be16c23e260a21f1dd8bbfc4cb57` |
| 公开样例 | OpenOrbis v0.5.3 / `samples-elf-llvm-18.zip` |
| 样例源码 commit | `6929bafac0b565692ed61e66032a79185ee9cf65` |
| 官方转换工具 | v0.5.3 / `toolchain-llvm-18.2.zip` / `create-fself.exe` |
| 系统 | Windows 11 家庭版 中文版，64 位 |
| CPU / 内存 | Intel Core i9-13980HX，16 GB RAM |
| GPU / 驱动 | RTX 4070 Laptop GPU / NVIDIA 576.28 |
| Vulkan | 1.4.303 |
| 本次进程环境 | `VK_LOADER_DRIVERS_SELECT=*nv*` |
| Sony 系统模块 | 未提供；独立 portable `user/sys_modules` 目录为空 |

源码研究 ref 与实际正式包的 commit 不同，不能把两者混称为同一个版本。

## 如何复现

从仓库根目录运行（Python 3.10+，Windows）：

```powershell
python projects/008-shadps4/experiments/run_public_example.py --prepare-only
python projects/008-shadps4/experiments/run_public_example.py --sample hello_world --seconds 5 --driver-select "*nv*"
python projects/008-shadps4/experiments/run_public_example.py --sample graphics --driver-select "*nv*"
```

首次准备会下载 3 个官方开源发布包：模拟器约 31 MB、样例约 7 MB、工具链约 158 MB，解压后还需要额外磁盘空间。下载、生成的 `eboot.bin`、工具链、portable 配置和新运行日志全部放在被忽略的 `experiments/runtime/`，不会进入 Git。

`--driver-select "*nv*"` 是这台 NVIDIA 电脑验证过的进程级筛选；其他品牌电脑可以省略此参数，或使用适合自己驱动名称的筛选。它不会安装、更新或更改系统驱动。

graphics 不加 `--seconds` 时持续运行，关闭模拟器窗口或按终端 Ctrl+C 可停止。可加 `--seconds 10` 做短时间观察。

官方样例包内 `.elf` 是普通链接器输出，不能只把文件改名当成 PS4 可执行文件。脚本使用 OpenOrbis 的官方转换工具生成 PS4 OELF/SELF 格式，再交给模拟器运行。脚本不使用 Sony SDK，也不获取 Sony 系统模块。

## 日志与初次失败

- [CLI 帮助](shadps4-help.txt)
- [Hello world 真实 guest 输出](hello-converted-stdout.txt)
- [分形图形样例启动日志](graphics-stdout.txt)
- [初次 Vulkan 失败 stdout](diagnostic-vulkan-failure-stdout.txt)
- [初次 Vulkan 失败 stderr](diagnostic-vulkan-failure-stderr.txt)
- [机器可读结果](runtime-verification.json)

发布日志已将本地工作区绝对路径替换为 `<runtime>`；它们保留了原始错误和 guest 输出。

初次不筛选驱动的启动在 Vulkan 设备创建阶段返回 `ErrorOutOfHostMemory`，stderr 同时有 Mesa D3D12 创建错误。后续以 NVIDIA 驱动筛选重试成功；期间重新启动了进程，也调整了样例格式和配置，因此这里只记录这个可复现的成功组合，没有证明失败完全由某个单一驱动造成。启动日志还保留未实现 stub、缺失 OpenOrbis 可选模块和系统字体警告；这些警告没有阻止本次公开样例，但不能据此推断其他程序也能正常运行。

v0.19.0 的 CLI 没有 `--version` 选项，版本与 commit 来自样例真实启动日志。

## 未验证

商业 PS4 游戏、GCN 着色器重编译、音频、游戏手柄、存档、联网、长时间稳定性、跨显卡兼容性、实体 PS4 输出对照、游戏帧率，均不在本次验证范围内。网页内的教学交互如有绘图动画，也应与这里的原生实测分开标注。

## 来源与许可证

- [shadPS4 官方 v0.19.0](https://github.com/shadps4-emu/shadPS4/releases/tag/v.0.19.0)：GPL-2.0-or-later。
- [OpenOrbis 官方 v0.5.3](https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/releases/tag/v0.5.3)：GPL-3.0。
- [graphics 原始源码](https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain/blob/6929bafac0b565692ed61e66032a79185ee9cf65/samples/graphics/graphics/main.cpp)。
- 样例入口、相关 `graphics.cpp` / `graphics.h` / `log.h` 与上游完整 LICENSE 保存在 `experiments/third_party/OpenOrbis/`，用于解释、归属与许可证保留，没有修改上游源码。

shadPS4 发布包摘要：`b9600602a809b7cb4aaf29cbeb0917d32caecf27bc5a9232df76200fbf80c017`。OpenOrbis 两个下载包的摘要是本次下载后计算并固定的复现基线，见 JSON；它们不是额外独立的第三方签名证明。
