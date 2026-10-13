# 多个 Web 演示的部署约定

## 站点结构

多个子项目的静态 Web 演示统一发布到仓库的 GitHub Pages 项目站点，每个项目使用独立路径。首页完整展示元信息中的摘要，介绍能力、原理、价值与输入输出；不对摘要做字数截断。依据：[GitHub Pages 官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)。

```text
https://yydshly.github.io/1013_codex_project/
├── index.html
├── 001-infinite-bookshelf/
├── 002-another-project/
└── ...
```

这是地址约定。某个项目是否实际发布，以它的 `project.json` 中经过验证的 `demo_url` 和发布记录为准；部署脚本或工作流的存在不等于发布成功。

## 当前已验证发布

2026-10-13，已启用仓库 GitHub Pages 的 Actions 发布方式，首次部署提交为 `8d12bcc46c753c9ddc30c8b95f32fa92ecd29013`，[构建与部署运行](https://github.com/yydshly/1013_codex_project/actions/runs/38393707526)以及索引检查均成功。

- [站点总览](https://yydshly.github.io/1013_codex_project/)：完整展示已提交项目的能力、原理、输入输出、价值、意义与局限摘要。
- [001 Infinite Bookshelf](https://yydshly.github.io/1013_codex_project/001-infinite-bookshelf/)：详细研究、一图总览、摄影与电商样稿、回放和文件下载。
- [摄影入口](https://yydshly.github.io/1013_codex_project/001-infinite-bookshelf/?sample=photography#workbench)：摄影样稿参数可用于直接阅读。

首页、项目页、摄影入口、CSS、JavaScript、总览 PNG、两份 JSON 和首页预览图已实际请求，均返回 HTTP 200；项目静态文件 SHA-256 与远端提交 blob 一致。页面新版浏览器交互尚未重测，当前发布不包含自动生成新主题所需的模型服务。完整范围见 [发布验证](../projects/001-infinite-bookshelf/experiments/results/verification.md#公网静态发布验证)。

子项目静态源文件保存在 `projects/编号-slug/web/`。`scripts/build_site.py` 使用 Python 标准库，将可发布的原生静态项目汇集为一个完整站点：

```text
site-dist/                   # 临时构建目录，不提交到 Git
├── index.html               # 导航、完整摘要、截图与研究链接
├── .nojekyll
├── site-build.json          # 生成标记及本次包含的项目目录
├── previews/               # 每个项目明确指定的预览图
├── 001-infinite-bookshelf/  # 该项目 web/ 的公开静态文件
└── ...
```

## 构建与发布范围

默认构建只读取 Git 已跟踪的 `projects/*/project.json`，只复制其中已跟踪的 `web/` 静态文件和元信息明确指定的预览图片。工作区中新建但尚未提交的其他研究项目不会被意外收录。Git 暂存区中的新增文件也属于本地已跟踪文件；GitHub Actions 运行时只有实际提交并检出的文件。

```powershell
# 正式发布使用此默认方式：收集全部已跟踪的静态演示
python scripts/build_site.py

# 新项目尚未提交时，显式选择本地预演；可重复 --project
python scripts/build_site.py --project 001-infinite-bookshelf

# 可另建一个仓库内的 site-* 临时产物目录
python scripts/build_site.py --project 001-infinite-bookshelf --output site-preview

# 本地查看构建产物；静态服务不提供模型 API
python -m http.server 8767 --bind 127.0.0.1 --directory site-dist
```

`--project` 用于本地验证，正式 Pages 工作流不使用该筛选参数。每次发布都重新收集全部已跟踪静态演示，保持其他项目入口；已有 `demo_url` 的项目缺少可发布的 `web/index.html` 时，构建会失败，避免悄悄丢失入口。未部署且没有静态页面的研究项目保留在仓库索引中，不加入网页演示列表。归档项目若仍保留静态文件，也继续发布。

构建只允许替换仓库内直接命名为 `site-*` 的生成目录。已有非空目录必须带有 `site-build.json` 生成标记，脚本才会替换；构建成功前不会删除上次产物。

## 公开文件与资源路径

- 仅复制 `web/` 内的 HTML、CSS、JavaScript、JSON、公开 TXT、常用图像、字体、音视频和 PDF。Markdown 研究文档与 Python 等源码不作为网页产物复制；导航链接指向 GitHub 研究文档。
- 隐藏文件、`.env`、密钥文件、依赖目录、后端与私有目录、源码映射、已知凭据文件被排除。`experiments/`、`references/` 和其他项目文件完全不进入网页产物。
- `web/` 是公开前端目录；不得把任何私密内容放在其中。静态白名单不是对任意文件内容的自动密钥审计。
- 预览图只从项目元信息的 `preview` 取一张明确图片，不将整个项目 `assets/` 目录发布。网页自身需要的图片应放在 `web/assets/`。
- 资源和项目链接使用相对路径，例如 `./app.js`、`./data/book.json`、`./assets/image.png`，适配 `/1013_codex_project/001-infinite-bookshelf/` 的仓库名前缀。
- 项目跳回站点总览使用 `../`；客户端路由使用 hash 或查询参数，避免静态托管刷新深层路径返回 404。
- 当前构建器直接汇集原生静态文件，不运行框架安装或打包。需要 React、Vite 等构建时，应先在明确的构建步骤产出经过审核的公开文件，再扩展汇集约定，不能把依赖和源码一并上传。

在 `web/README.md` 中记录依赖、运行方式、静态部署前缀、已验证功能和服务端限制。GitHub Pages 不运行 Python 后端、不存放模型密钥；真实模型请求需使用另外部署的后端。Infinite Bookshelf 的静态网页可展示研究说明、两份保存的 GPT 样稿、步骤回放和前端导出；回放不等于现场模型生成。

## GitHub Actions 工作流

`.github/workflows/pages.yml` 在 `main` 推送或手动触发时：

1. 检出已提交的仓库文件，使用 Python 3.12。
2. 校验 `project.json` 与根 README 自动索引，运行项目工具和静态发布隔离测试。
3. 构建任务使用 `contents: read` 与 `pages: read`，运行 `actions/configure-pages@v5` 读取已启用的 Pages 配置。
4. 默认收集全部已跟踪静态演示到 `site-dist/`。
5. 使用 `actions/upload-pages-artifact@v4` 上传站点产物。
6. 在依赖构建任务的 `deploy` 任务中，使用 `actions/deploy-pages@v4` 发布。该任务拥有 `pages: write`、`id-token: write` 权限，并使用 `github-pages` 环境。

首次发布前需在仓库 `Settings → Pages → Build and deployment` 将发布来源设为 `GitHub Actions`。Pages 专用上传动作 v4 不接受 `include-hidden-files`，会排除隐藏文件；本地产物中的 `.nojekyll` 不进入上传包也不影响本流程，因为 Actions 直接部署已经生成的静态产物，不再运行 Jekyll。动作定义依据：[upload-pages-artifact v4](https://github.com/actions/upload-pages-artifact/blob/v4/action.yml)。

本流程不在构建任务中自动创建 Pages 站点。`configure-pages` 默认 `enablement: false`，只读取站点配置；首次创建需仓库管理员事先完成。读取权限依据：[Pages REST API](https://docs.github.com/en/rest/pages/pages#get-a-github-pages-site)；动作默认参数依据：[configure-pages v5](https://github.com/actions/configure-pages/blob/v5/action.yml)。

工作流完成后，还应实际访问导航首页、项目页、样稿 JSON 和图片资源，确认子路径、资源和刷新可用，再填写 `demo_url` 并执行：

```powershell
python scripts/update_index.py
python scripts/update_index.py --check
python -m unittest discover -s tests -v
```

摘要与公开入口更新需要提交后重新发布，不能在尚未验证成功时预填“已部署”。GitHub 官方工作流说明和版本依据：[使用自定义工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。
