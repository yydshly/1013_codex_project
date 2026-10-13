# 可替换模型的本地生成实验

本目录独立重写 [Infinite Bookshelf](https://github.com/Bklieger/infinite-bookshelf) 展示的「目录 → 书名 → 逐章正文」工作流程，用标准库提供本机服务，不需要安装原项目的 Groq、Streamlit 或 PDF 依赖。本实验没有复制上游应用代码；上游版本、许可证和源码分析见 [项目研究说明](../README.md)。

**已验证的是接口行为，尚未通过我们的模型 API 生成书稿。** 当前网页中的 GPT 样稿由本次对话生成并回放，不能作为这个 API 适配器的真实运行记录。这里的自动化测试使用本机伪服务，也不能证明模型质量、速度或准确性。

## 运行

环境：Python 3.10 或更新版本，已在 Windows / Python 3.10.11 上运行合同测试。

从仓库根目录启动：

```powershell
python projects/001-infinite-bookshelf/experiments/server.py
```

打开 <http://127.0.0.1:8765>。服务只监听本机地址，静态文件范围只包括相邻的 `web/`；`.env` 和实验源码不会由静态目录提供。启动和请求日志均不输出密钥，网页不会收到密钥或模型服务地址。退出使用 Ctrl+C，修改 `.env` 后需要重新启动。

可选端口：

```powershell
python projects/001-infinite-bookshelf/experiments/server.py --port 8766
```

## 换成我们的模型

复制本目录的 `.env.example` 为 `.env`，填写自己的配置。`.env` 已被根 `.gitignore` 排除，不要将实际密钥写入网页或提交到仓库。

```dotenv
BOOKSHELF_BASE_URL=https://your-model-service.example/v1
BOOKSHELF_MODEL=your-model-id
BOOKSHELF_API_KEY=
BOOKSHELF_SECTION_MAX_TOKENS=800
BOOKSHELF_TIMEOUT_SECONDS=90
```

| 变量 | 含义 |
| --- | --- |
| `BOOKSHELF_BASE_URL` | OpenAI 兼容的接口基础地址，通常以 `/v1` 结尾；程序追加 `/chat/completions`，也接受完整的该接口路径 |
| `BOOKSHELF_MODEL` | 服务端提供的模型标识；目录、书名、正文均使用它 |
| `BOOKSHELF_API_KEY` | 可选密钥；留空则不发送 `Authorization`，支持无需认证的本地模型 |
| `BOOKSHELF_API_KEY_ENV` | 可选，指向已有本机密钥变量的名称；设置后从该变量读取密钥，优先于 `BOOKSHELF_API_KEY` |
| `BOOKSHELF_SECTION_MAX_TOKENS` | 单章输出 token 上限，默认 800，可设 100–4000；它不等于中文字数 |
| `BOOKSHELF_TIMEOUT_SECONDS` | 每次模型请求的超时，默认 90 秒，可设 1–120 秒 |

操作系统环境变量优先于 `.env`。这里的 `.env` 解析器只处理简单 `KEY=value` 和成对引号，不执行命令、变量展开或脚本。替换模型不需要改生成流程；接口必须提供 Chat Completions 格式的 `choices[0].message.content`。只支持 Responses API 或自定义请求格式的服务，需要另写适配器。

## 生成过程与效果边界

1. 用主题、写作要求和章节数请求目录 JSON。支持 `{"outline":[{"title":"…","description":"…"}]}` 或等价数组，接受完整的 JSON 代码块，严格校验标题、说明和章节数量。
2. 用完整目录生成书名。
3. 按顺序请求各章正文，每次带完整目录及之前每章开头 600 字符的摘录，以帮助沿用术语和减少重复。
4. 前端收到书名、目录、各章正文和最终 `book` 对象；书稿留在浏览器中，由前端提供 TXT 下载。

通常生成 N 章需要 N+2 次真实模型请求。目录首先传 `response_format: {"type":"json_object"}`；遇到 HTTP 400 时，保留 JSON 格式提示并去掉该可选参数，只重试一次，因此请求数可能增加 1。目录返回非法 JSON 时停止，不继续生成书名和正文。

每次模型调用都是**非流式**请求；网页通过 NDJSON 接收各阶段结果，单章完成后才显示这章，不能逐 token 显示。前文摘录是确定性的截取，不是模型总结，也不能保证全书一致性。本实现没有检索资料、来源核验、事实审核、审稿循环或正式出版排版。

若服务报告 `finish_reason: "length"`，正文标记 `truncated: true`，最终统计列出相应章节索引。目录或书名截断则中止。若服务未返回用量数据，`usage_reported` 为 `false`；此时统计中的 0 是未报告的占位值，不能解读为免费或没有 token 消耗。

## API 合同

| 接口 | 结果 |
| --- | --- |
| `GET /api/health` | `{"ok":true}` |
| `GET /api/config` | `configured`、`model`、`reason`；不返回接口地址、密钥或密钥变量名称 |
| `POST /api/generate` | 输入 `topic`、可选 `instructions`、`chapter_count`（默认 3，范围 1–6）；响应 `application/x-ndjson` |

请求必须使用 `Content-Type: application/json`，正文最大 64 KB，主题最大 2000 字符，写作要求最大 8000 字符。同一时间只接受一个生成任务。来自其他浏览器来源的请求被拒绝；允许本机命令行请求。密钥只用于服务端调用，HTTP 重定向不被跟随，服务商原始错误正文不转发到浏览器。

事件顺序：

```text
{"type":"outline","outline":[{"title":"…","description":"…"}]}
{"type":"title","title":"…"}
{"type":"section","index":0,"title":"…","content":"…","truncated":false}
…
{"type":"done","book":{…},"stats":{…}}
```

阶段中失败会产生 `{"type":"error","message":"安全的中文错误说明"}` 并结束。输入错误、未配置或已有任务运行时，在开始 NDJSON 前返回常规 JSON `{"error":"…"}`，状态分别为 400/503/409 等。章节索引从 0 开始。

`book.provenance` 包含 `mode: "live"`、模型标识、UTC 生成时间、工作流程及上下文策略；最终统计包含请求次数、输入/输出 tokens（若服务报告）、耗时及截断章节。HTTP 服务不保存书稿，也没有续写或断点恢复；刷新页面可能丢失结果。

## 验证

```powershell
python -m unittest discover -s projects/001-infinite-bookshelf/experiments/tests -v
```

2026-10-13 执行结果：**16 个测试全部通过**。

覆盖 `.env`/环境变量优先级、引用已有密钥变量、无密钥本地配置、目录校验、章节事件顺序、上下文传递、JSON 参数降级、用量统计、截断标记、服务错误脱敏、拒绝带认证头的重定向、同源限制、非法输入、并发生成限制和静态目录边界。

测试使用本机伪模型服务，测试字符串只是接口合同数据。待提供我们的模型地址与标识后，才可另行记录真实 API 的成稿、用量、耗时和质量结果。
