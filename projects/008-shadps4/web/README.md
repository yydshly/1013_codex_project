# shadPS4 中文理解网页

十一章详细导读：概念、能力、机制、交互教学、原生实测、基础知识价值、对当前研究目标的意义、扩展方向、实践和源码词典。

## 功能与范围

完整一图总览提供可放大 SVG 与 1800×3290 PNG，汇总概念、资源控制边界、能力、原理、价值、扩展、个人意义和验证范围；另保留简化流程图。三类请求 × 正常/接口缺失/着色器失败；七步文字、阶段高亮、轨迹与浏览器角色示意；缓存教学；三题理解核对；二十二列 UTF-8 BOM CSV 下载。读取本机 JSON，展示官方 v0.19.0 真实运行日志、OpenOrbis 分形窗口、来源与复现说明。

Canvas 是浏览器教学图，不执行 PS4 内容。实际分形像素由 guest CPU 生成，经 VideoOut/Vulkan 呈现，未覆盖 GCN 重编译和商业游戏 3D 性能。源码研究 23c4133 与运行包 c7e065d 分别记录。

## 本地访问与部署

Python 3.10+，网页无需第三方依赖。仓库根目录运行：

```powershell
python -m http.server 8772 --bind 127.0.0.1 --directory projects/008-shadps4/web
```

访问 http://127.0.0.1:8772/。通过 HTTP 读取 JSON，未验证直接双击文件的方式。上述服务根目录是本项目，返回总索引需整站预演：

```powershell
python scripts/build_site.py --project 008-shadps4 --output site-shadps4-preview
python -m http.server 8773 --bind 127.0.0.1 --directory site-shadps4-preview
```

访问 http://127.0.0.1:8773/008-shadps4/，返回索引为 ../。正式汇集收集全部已跟踪项目，遵循 [部署约定](../../../docs/deployment.md)。公网尚未部署，demo_url 为空。

页面无后端、模型、外部字体和脚本。全部资源为相对路径，统一子路径为 /1013_codex_project/008-shadps4/。原生程序、系统模块、配置和缓存完全不在 web/ 内。

## 验证与截图

[网页验证](../experiments/results/web-verification.md) / [JSON](../experiments/results/web-verification.json) 记录实际浏览器功能、下载、资源、桌面/手机与日志检查。开发检查使用宿主提供的 Playwright，不是网页运行依赖。[原生实测](../experiments/results/runtime-verification.md) 单独记录。
