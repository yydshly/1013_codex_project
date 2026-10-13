# 多个 Web 演示的部署约定

## 站点结构

GitHub Pages 为每个仓库提供一个项目站点。多个子项目的静态 Web 演示统一汇集到这个站点下，使用各自的路径。依据：[GitHub Pages 官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)。

本仓库预期的发布路径如下，**当前尚未部署**：

```text
https://yydshly.github.io/1013_codex_project/
├── 001-example-project/
├── 002-another-project/
└── ...
```

子项目的源代码保存在 `projects/编号-slug/web/`。各项目可独立选择框架和构建方式；未来发布时，将构建结果汇集成一个完整的静态站点：

```text
site-dist/                   # 临时构建目录，不提交到 Git
├── index.html               # 演示导航首页
├── .nojekyll
├── 001-example-project/
│   └── index.html
└── 002-another-project/
    └── index.html
```

## 子项目需要记录什么

在每个 `web/README.md` 中说明依赖、安装命令、启动命令、构建命令、输出目录、访问前缀和已验证的功能。选定技术栈后再添加对应依赖和构建配置。

- 静态资源的访问前缀应包含仓库名和子项目名，例如 `/1013_codex_project/001-example-project/`。
- 子项目内部的跳转和图片路径应适配该前缀；跨项目跳转回到站点总览。
- 客户端路由需适配静态托管，例如使用 hash 路由，避免刷新深层路径后返回 404。
- 需要服务端、数据库或私密凭据的功能，需使用外部后端；GitHub Pages 用于静态前端。
- 每次发布应汇集所有已部署子项目，保持其入口可访问。
- 首页 `demo_url` 只填写部署并验证后的实际地址。

## 有首个可部署项目后

1. 为子项目配置适当的构建命令和资源前缀，并在本地验证导航、资源加载与刷新。
2. 添加 GitHub Actions 工作流，将各子项目产物汇集到 `site-dist/` 并生成导航页。
3. 在仓库 `Settings → Pages → Build and deployment` 中选择 `GitHub Actions`。
4. 按官方工作流使用 `configure-pages`、`upload-pages-artifact` 和 `deploy-pages`；部署任务配置 `pages: write`、`id-token: write` 及 `github-pages` 环境。
5. 访问发布地址确认演示可用，再更新子项目 `demo_url` 和总索引。

当前初始化包含索引校验工作流；发布工作流将在选定具体演示与技术栈后添加。参考：[GitHub Pages 自定义工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。
