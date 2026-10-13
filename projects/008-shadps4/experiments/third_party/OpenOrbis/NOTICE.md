# OpenOrbis 源码归属

本目录只保留用于解释公开示例实测的上游源文件，不含游戏、Sony SDK 或 Sony 系统模块。

- 上游：[OpenOrbis/OpenOrbis-PS4-Toolchain](https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain)
- 版本：v0.5.3，commit `6929bafac0b565692ed61e66032a79185ee9cf65`
- 作者与权利人：OpenOrbis 项目及上游文件所注明的贡献者。
- 许可证：GPL-3.0，完整许可证保存在同目录 `LICENSE`。
- 保留文件：`samples/hello_world/hello_world/main.cpp`、`samples/graphics/graphics/main.cpp`、`samples/_common/graphics.cpp`、`samples/_common/graphics.h`、`samples/_common/log.h`。
- 上述源码从固定 commit 读取，未修改。可运行二进制由脚本从官方公开发布包下载并转换，留在被 Git 忽略的 `experiments/runtime/`。

实机图像来自上述 graphics 的算法输出；它不是商业游戏截图。该样例在 CPU 上绘制 Mandelbrot，再调用 VideoOut 提交帧缓冲。
