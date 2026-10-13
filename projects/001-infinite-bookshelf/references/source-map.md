# 源码与资料证据表

上游源码固定到 commit `400b272175945d35eaefa68aefe9106fa9d7e467`，于 2026-10-13 读取。行号按 raw 源码计数。源码推断、历史样本与本地运行验证分别记录，避免把“存在代码”当作“已经复现”。

| 结论 | 一手证据 | 说明 |
| --- | --- | --- |
| 基础模式先生成目录、再生成书名、再扩写正文 | [main.py L97](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/main.py#L97) | 顺序执行 |
| 目录是嵌套 JSON 对象 | [structure_writer.py L24](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/infinite_bookshelf/agents/structure_writer.py#L24) | `response_format` 为 `json_object` |
| 高级模式“300 页”只是提示词要求 | [structure_writer.py L19](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/infinite_bookshelf/agents/structure_writer.py#L19) | 无页数校验；不能当实际输出指标 |
| 正文逐节生成，不共享前文 | [main.py L129](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/main.py#L129) | 每个叶子节点提供标题、描述与附加要求 |
| 正文流式生成，单次最多 8,000 tokens | [section_writer.py L8](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/infinite_bookshelf/agents/section_writer.py#L8) | 不是整本书的上限或目标字数 |
| 文风、难度、TXT 与已有笔记输入 | [advanced_form.py L69](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/infinite_bookshelf/ui/components/advanced_form.py#L69) | TXT 上传，不是通用文档解析 |
| 参考材料直接加入提示词 | [advanced.py L89](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/pages/advanced.py#L89) | 正文再次拼入材料见 L158；无检索组件 |
| 高级模型列表与默认值 | [advanced_form.py L3](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/infinite_bookshelf/ui/components/advanced_form.py#L3) | 默认目录 Maverick、正文 Scout |
| 书名模型参数被忽略，固定使用 Maverick | [title_writer.py L8](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/infinite_bookshelf/agents/title_writer.py#L8) | L13 是硬编码 ID |
| 书稿存储、页面更新与 Markdown 汇总 | [book.py L8](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/infinite_bookshelf/ui/book.py#L8) | `Book` 保存目录与正文；无数据库持久化 |
| TXT 与 PDF 下载 | [download.py L9](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/infinite_bookshelf/ui/components/download.py#L9) | 文本后缀 `.txt`，内容由 Markdown 生成 |
| PDF 用 Markdown → HTML → WeasyPrint | [pdf.py L10](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/infinite_bookshelf/tools/pdf.py#L10) | 未运行原应用 PDF 导出 |
| 推理统计依赖 Groq 字段 | [section_writer.py L34](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/infinite_bookshelf/agents/section_writer.py#L34) | `x_groq` 等字段不能假定其他服务也有 |
| README 仍描述大小模型搭配 | [README.md L34](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/README.md#L34) | 基础流程实际用同一模型，按源码核对 |
| 上游声明内容可能错误或有占位内容 | [README.md L120](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/README.md#L120) | 作者定位为娱乐用途 |
| MIT 许可证与版权 | [LICENSE.md](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/LICENSE.md) | 原文保留在 `assets/upstream-LICENSE.md` |

## 效果证据

- [Example_1.md](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/Example_1.md)：原作者提供的大语言模型基础书稿，读取后 75,136 字符、16 个 Markdown 标题行。
- [Example_2.md](https://github.com/Bklieger/infinite-bookshelf/blob/400b272175945d35eaefa68aefe9106fa9d7e467/Example_2.md)：原作者提供的 Java 数据结构与算法书稿，读取后 175,125 字符、53 个 Markdown 标题行。
- 统计对 UTF-8 解码文本计算 `len(text)`，标题用 `^#{1,6} ` 多行匹配；未重新生成原作者样本，未据此推导页数或速度。
- 本次中文样稿由当前对话 GPT 生成，页面回放保存结果。接口合约测试使用测试数据，不能作为模型质量的证据。记录见 [实验说明](../experiments/README.md) 和 [演示说明](../web/README.md)。

## 当前模型可用性

2026-10-13 查阅 [Groq 官方停用公告](https://console.groq.com/docs/deprecations)：

| 上游 ID | 官方停用日期 | 范围 / 说明 |
| --- | --- | --- |
| `meta-llama/llama-4-maverick-17b-128e-instruct` | 2026-03-09 | 基础入口、书名函数固定使用 |
| `meta-llama/llama-4-scout-17b-16e-instruct` | 2026-07-17 | 免费与开发者账户；部分企业合同账户例外 |
| `deepseek-r1-distill-llama-70b` | 2025-10-02 | 高级模型列表选项 |
| `moonshotai/kimi-k2-instruct` | 2025-10-10 | 高级模型列表中的旧 ID |

“原样运行预计失败”由硬编码 ID 与官方停用记录得出，本次没有向停用模型发请求。可用替代模型按所接入服务的实际清单核对。
