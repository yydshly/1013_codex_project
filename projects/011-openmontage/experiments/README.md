# 研究整理与本地网页验证

本目录只包含原创资料整理和静态网页验证，不安装或运行上游视频制作系统。

## 目录生成

```powershell
python projects/011-openmontage/experiments/build_research_catalog.py
```

生成器使用 Python 标准库，将 `web/research.json` 的 34 项能力、12 条流程和 27 项来源写入 HTML；读取 `web/comparison.json`，把包含 OpenMontage 基准的 11 行项目对比写入 HTML 与 README。能力表和来源同步到 README，并导出含完整比较和依据链接的文字导读。手写论述在标记块外保留。可重复执行，不需要网络或密钥。

## 浏览器验证

完整总览图可以按下列顺序重建：

```powershell
python projects/011-openmontage/experiments/build_ability_map.py
# 使用上文相同的已有 Playwright 运行时；参数为本机 Chromium 浏览器路径。
node projects/011-openmontage/experiments/render_ability_map.cjs "<浏览器可执行文件路径>"
```

SVG 使用原创说明与能力目录；渲染器检查 34 项能力、12 条流程是否全部在图中，测量实际字体宽度并导出 PNG，保留分段截图用于布局检查。结果见 `results/ability-map-verification.json`。这是原创矢量图渲染，不调用素材生成模型。

`verify_web.cjs` 使用已有 Playwright 运行时检查真实本地页面。需要指定可用 Chromium 浏览器或已安装的 Edge；依赖仅用于验证，不进入公开网页。

```powershell
# 启动网页服务器后，在另一个终端执行；将模块和浏览器路径替换成实际环境。
$env:NODE_PATH = "<playwright 所在 node_modules 目录>"
node projects/011-openmontage/experiments/verify_web.cjs http://127.0.0.1:8791/011-openmontage/ "<浏览器可执行文件路径>"
```

验证包括：子路径与资源、所有本地锚点、34 项能力及类别、搜索清空与空结果、三条路径、八阶段前置条件与确认门、重置、关闭 JavaScript 阅读、桌面与手机溢出、图片加载和脚本错误。截图保存到项目 `assets/`；记录保存到 `results/`。不访问或测试上游服务。

## 结果范围

- `results/source-review.json`：固定版本、阅读范围、证据位置和未验证事项。
- `results/verification.md`：实际执行的本地检查与环境。
- `results/web-verification.json`：浏览器检查的机器可读结果。

本地网页通过不等于上游可安装、工具可用或真实成片质量通过。

## 公网发布验证

`verify_publication.py` 用公开地址检查项目文件、完整图、首页、构建清单和旧项目入口；项目文件按已提交 Git blob 逐字节核对，避免 Windows 换行差异。`verify_web.cjs` 加 `--public` 可验证公网交互并保存独立的结果和截图。入口实际验证后才写入 `demo_url`。本次发布范围与证据见 `results/publication-2026-10-14.md`，不涉及上游真实视频或模型服务部署。
