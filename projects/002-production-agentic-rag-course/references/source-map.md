# 固定版本源码证据表

研究日期：2026-10-13（Asia/Shanghai）。固定 commit：`424a0eb99edf841994f2a9a053912b489d2a94ff`。下面均为静态阅读结果，不能当作运行验收记录。

[返回研究说明](../README.md) · [复现与验收清单](../experiments/README.md)

| 结论 / 核对事项 | 固定版本源码 | 阅读结果与边界 |
| --- | --- | --- |
| Python 运行时严格限定为 3.12 | [pyproject.toml](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/pyproject.toml#L5) | 版本约束为 >=3.12,<3.13，不能只按 README 的“3.12+”准备。 |
| 离线任务依赖与工作日调度 | [airflow/dags/arxiv_paper_ingestion.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/airflow/dags/arxiv_paper_ingestion.py#L30) | 采集、存储、切块向量化、索引、报告依次执行；运行结果未验证。 |
| Airflow 构建版本 | [airflow/Dockerfile](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/airflow/Dockerfile#L5) | 固定 Dockerfile 使用 2.10.3，与上游 README 的 3.0 描述不同。 |
| Langfuse 主机端口 | [compose.yml](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/compose.yml#L261) | 容器内部为 3000，宿主机映射为 3001。 |
| Langfuse 环境变量前缀 | [src/config.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/config.py) | LangfuseSettings 使用 LANGFUSE__ 前缀；关闭追踪应核对 LANGFUSE__ENABLED=false 的实际生效值。 |
| PDF 页数与大小限制 | [src/config.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/config.py#L64) | 配置默认最多 30 页、20 MB；.env 可覆盖。Docling 注释中的 20 页不能作为有效配置。 |
| 解析参数来自配置 | [src/services/pdf_parser/factory.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/services/pdf_parser/factory.py#L13) | PDF parser 的工厂将有效配置传入解析服务。 |
| 章节切块与回退 | [src/services/indexing/text_chunker.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/services/indexing/text_chunker.py#L54) | 优先按章节处理；无有效章节则回退到词数与重叠切块。 |
| Jina 文本会发送到外部 API | [src/services/embeddings/jina_client.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/services/embeddings/jina_client.py#L32) | 使用 jina-embeddings-v3、1024 维；本地 Ollama 不代表整条链路离线。 |
| BM25、向量、RRF 混合搜索 | [src/services/opensearch/client.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/services/opensearch/client.py#L181) | 存在三个搜索方法，实际召回质量需标注语料评估。 |
| 普通问答与来源构造 | [src/routers/ask.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/routers/ask.py#L19) | 从命中结果组装论文 PDF URL，/ask 与 /stream 使用该辅助函数。 |
| 普通 RAG 的缓存路径 | [src/routers/ask.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/routers/ask.py#L99) | 普通问答与流式路径使用缓存；Agentic 路由没有这条缓存调用。 |
| 缓存为精确匹配 | [src/services/cache/client.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/services/cache/client.py#L24) | 键包含问题、模型、top_k、检索方式和分类；不含语料版本。 |
| LangGraph 控制流 | [src/services/agents/agentic_rag.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/services/agents/agentic_rag.py#L86) | 校验、检索工具、整批资料相关性判断、改写、生成由有向图编排。 |
| Agent 默认配置 | [src/services/agents/config.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/services/agents/config.py#L14) | 最多检索 2 次、领域阈值 60、top_k=3，默认 llama3.2:1b。 |
| 重试次数到达上限后的终止 | [src/services/agents/nodes/retrieve_node.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/services/agents/nodes/retrieve_node.py#L66) | 返回找不到相关论文的消息；不是无限重试或转为全网搜索。 |
| 领域判断与故障降级 | [src/services/agents/nodes/guardrail_node.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/services/agents/nodes/guardrail_node.py#L119) | 模型失败时分数降为 50，默认阈值 60 会使请求进入范围外分支。 |
| Agentic 模型客户端适配 | [guardrail_node.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/services/agents/nodes/guardrail_node.py)、[ollama/client.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/services/ollama/client.py)、[agents/factory.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/services/agents/factory.py) | 节点调用 get_langchain_model，但注入的 OllamaClient 类未定义该方法；工厂直接传入客户端。可能进入模型异常降级分支，实际影响待复现。 |
| 相关性判断并非逐文档重排 | [src/services/agents/nodes/grade_documents_node.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/services/agents/nodes/grade_documents_node.py#L35) | 对拼接上下文给一次 yes/no；异常降级只判断文本长度是否 >50。 |
| Agentic 参数传递缺口 | [src/routers/agentic_ask.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/routers/agentic_ask.py#L40) | 路由只传 query；model、top_k、use_hybrid、categories 没有按请求配置执行。 |
| 来源提取辅助函数占位 | [src/services/agents/nodes/utils.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/services/agents/nodes/utils.py#L24) | 该函数尚未解析来源。工作流初始化 relevant_sources=[]，已读节点中未见填充。 |
| Agentic 来源与 trace 返回 | [src/services/agents/agentic_rag.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/services/agents/agentic_rag.py#L293) | 来源读取 relevant_sources；服务返回字典没有 trace_id，需验证客户端引用与反馈闭环。 |
| 响应字段类型与范围 | [src/schemas/api/ask.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/schemas/api/ask.py#L48) | sources 继承 List[str]；未声明 rewritten_query 字段，接口不会按 schema 暴露该字段。 |
| Telegram 当前路径 | [src/services/telegram/bot.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/services/telegram/bot.py#L129) | 直接执行检索和 Ollama 调用，没有进入 AgenticRAGService；生成模型写死为 llama3.2:1b。 |
| Gradio 当前路径 | [src/gradio_app.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/gradio_app.py#L31) | 调用普通 /stream，端口 7861；不是 Agentic 工作流的可视化界面。 |
| 请求状态与持久记忆 | [src/services/agents/agentic_rag.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/src/services/agents/agentic_rag.py#L237) | 每次请求初始化图状态；图 compile 未配置 checkpointer，不能据此宣称跨请求持久记忆。 |
| 上游 API 测试使用模拟依赖 | [tests/api/routers/test_agentic_ask.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/tests/api/routers/test_agentic_ask.py#L14) | 来源与回答由 mock 返回，不能证明真实检索、引用或模型效果。 |
| 上游自定义模型测试 | [tests/api/routers/test_agentic_ask.py](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/tests/api/routers/test_agentic_ask.py#L204) | 该断言要求模型被传给服务，与当前路由只传 query 的代码存在静态矛盾；测试尚未运行。 |
| MIT 许可证 | [LICENSE](https://github.com/jamwithai/production-agentic-rag-course/blob/424a0eb99edf841994f2a9a053912b489d2a94ff/LICENSE#L3) | Copyright (c) 2025 Jam With AI；原文保留在 assets/upstream-LICENSE.md。 |

这些链接固定在研究 commit；后续升级上游版本时，先更新证据与复现记录，再同步 project.json 的 source_ref。
