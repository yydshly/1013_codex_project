# 中文研究网页与规则手册

原生 HTML/CSS/JavaScript，无前端依赖、外部字体、模型密钥或后台服务。12 个章节汇总 Jev SEO 的能力、采集原理、参考与提取、全部规则与内容标准、证据校验、8 类使用场景、聊天/接口两种路径、边界和来源。

## 本地阅读

在仓库根目录运行：

```powershell
python -m http.server 8876 --bind 127.0.0.1 --directory projects/006-jev-seo/web
```

浏览器打开 `http://127.0.0.1:8876/`。该独立目录下“研究索引”只能回到当前服务器根；完整仓库索引需下面的汇集预览。

没有运行中的服务时，可在普通浏览器中尝试直接打开本目录 `index.html`。规则数据使用 `catalog.js`，无需联网请求 JSON。Codex 内置浏览器禁止 `file:` 协议，本次未验证直接文件打开；本地 HTTP 预览已验证。

## 仓库路径预览与部署

```powershell
python scripts/build_site.py --project 006-jev-seo --output site-preview-jev-seo
python -m http.server 8876 --bind 127.0.0.1 --directory site-preview-jev-seo
```

打开 `http://127.0.0.1:8876/006-jev-seo/`。相对资源与 hash 章节导航适配仓库前缀 `/1013_codex_project/006-jev-seo/`。遵循 [统一部署约定](../../../docs/deployment.md)。本项目尚未提交发布，`demo_url` 保持空字符串。

## 规则数据维护

```powershell
python projects/006-jev-seo/experiments/build_web_catalog.py
```

生成器从实际实验规则和问题定义读取 ID、严重程度、经验标记、类型、选项、源码依据，再补充中文研究说明。断言规则 ID 集合与翻译档位数量一致。公开的 `catalog.json` / `catalog.js` 是网页数据源，保留上游 MIT 版权、完整许可证与固定版本。修改执行逻辑后需重新生成并核对说明；数据不是独立扫描器。

## 展示功能与验证

- 全部 52 条规则；搜索、领域/性质筛选、清除、展开/收起详情。
- 首页可展开一张理解总览图，提供原图放大与 PNG 下载；基于源码研究使用 imagegen 生成，不是实际审查截图。
- 19 个内容标准，按 13 个单页、5 个网站入口、1 个页面对切换。
- 5 个流程步骤、3 种证据示例、8 类场景与 2 种模型接入路径。
- 提供 JSON/提示词下载；打印样式纳入全部规则、维度、步骤与场景。
- 2026-10-14 在本地 HTTP 预览中验证主要交互；桌面 1280 × 800 与手机 390 × 844 均无整页横向溢出。浏览器未记录错误或警告。

真实截图保存在子项目 `assets/`；来源、尺寸与检查结果见 [验证记录](../experiments/results/web-verification.md)。下载资源 HTTP 可达已检查；打印样式及完整打印内容准备已检查，未实际导出 PDF。

## 服务边界

本网页不抓取真实网站、不在线调用模型、不上传密钥或自动修改网站。证据示例是明确标注的虚构材料，场景是使用建议。真实采集与评估由本地 Python 实验完成；GitHub Pages 不执行它的后台逻辑。网页展示验证不能证明 SEO、模型准确率或搜索效果。
