# 验证与后续实验

本次验证静态网页与教学模型，不启动上游应用、Agent 或模型。

- `check-message-model.cjs`：消息等待、交付、关闭接收和 read 语义。
- `check-static.py`：章节、来源锚点、本地资源、版本、图示副本与元信息。
- `draw-complete-understanding.py`：根据研究文字和形状原创绘制完整理解图，同时输出 PNG、SVG 和文字记录，复制至网页；不是图像编辑或模型调用。
- `results/verification.md`：实际命令、浏览器结果与未验证范围。

后续真实实验需要 macOS 和支持的 Agent CLI；依次验证会话绑定、Hooks、定向消息与草稿保护、权限等待、重启与恢复，再比较耗时、费用和最终通过率。当前未执行。
