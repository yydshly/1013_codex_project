# 源码来源与改动记录

上游：[AgriciDaniel/jev-seo](https://github.com/AgriciDaniel/jev-seo)，commit `55a184a3b0d09565a4c84268f725a47784e62528`，v0.1.1，MIT，Copyright (c) 2026 Agrici Daniel。保留 [LICENSE.upstream](LICENSE.upstream)；提取文件保留版权头；原始文件 SHA-256 见 [source_manifest.json](source_manifest.json)。

| 本地文件 | 原始文件 | 改动 |
| --- | --- | --- |
| `site_audit/upstream/crawl.py` | `jevseo/crawl.py` | 调整导入；新增路径边界，筛选站点地图、发现队列与重定向内容 |
| `site_audit/upstream/parse.py` | `jevseo/parse.py` | 调整导入；噪声过滤限定 ASCII 长串，保留连续中文 |
| `site_audit/upstream/checks.py` | `jevseo/checks.py` | 调整导入，保留 52 条规则定义与来源 |
| `site_audit/upstream/psi.py` | `jevseo/psi.py` | 调整导入与配置读取 |
| `site_audit/upstream/questions.py` | `jevseo/jev.py` 中 `def choice` 至关键词部分前 | 提取问题、选项、标准、状态构造与页面对筛选；不提取 Jev 客户端或概率阈值 |

上游注释的 A/B 结果是原作者对原模型的记录，不是本实验或自有模型的验证结果。

`upstream/__init__.py`、`upstream/env.py` 是本地适配文件。其余 `site_audit/` 模块、入口、测试与文档是本次实现。报告排序参考严重程度、涉及范围和业务重要性；明确区分模型建议与经验规则。

## 替换模型层

原 Jev/TypeSafe 的类型化判断和概率门槛，改为普通模型输出结构化 JSON，附理由、原文引文、缺证据 `null` 和材料指纹。不转换或伪造概率，不声称等同于 TypeSafe 的可靠性或原作者评估结果。

保留问题不等于保留模型能力；实际效果取决于模型、材料与复核。接口采用兼容 Chat Completions 的 JSON Schema、JSON 对象或文本输出。聊天路径通过导出材料与导入结果工作。

未移植 DataForSEO 关键词/竞争数据、PDF/XLSX 导出；未复制密钥、上游 `.env`、报告或依赖目录。

## 重做基础提取

`extract_upstream.py` 校验 checkout 的 HEAD 与固定 commit 一致，将基础提取写入独立目录 `runs/upstream-base/`。基础提取不包含后续路径和中文修正，不能覆盖当前适配实现。

```powershell
python extract_upstream.py C:/path/to/jev-seo-checkout
```

清单哈希针对原始完整文件；`questions.py` 只取片段，记录的是完整 `jev.py` 的哈希。

2026-10-13，Windows + Python 3.10.11；requests 2.33.1、beautifulsoup4 4.14.3、lxml 6.1.1。27 项离线测试通过；当前聊天模型审查虚构页面的 3 个任务、28 项判断，导入通过。真实网站、真实模型接口、浏览器渲染和 PageSpeed 未验证。
