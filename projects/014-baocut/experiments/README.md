# 研究与验证

本次完成固定版本资料研究与原创静态网页，没有运行 BaoCut 上游或调用真实模型。

- [验证记录](./verification.md)：网页、构建与测试结果，以及上游未验证事项。
- 真实复现建议：用固定口播素材，对照检查转写/剪辑、人工调整、局部对话修改、撤销与最终导出。
- 网页的协作教学示例位于 `../web/app.js`；它操作自己的示例状态，不执行媒体处理。

## 完整理解图

`build_comprehensive_overview.py` 从同一套文字与绘图指令生成高清 PNG 和可缩放 SVG，保存在项目 `assets/` 与 `web/assets/`，不是修改或复制上游截图。

```powershell
python projects/014-baocut/experiments/build_comprehensive_overview.py
```

需要 Pillow 与 Windows 的 Microsoft YaHei 字体。本次环境已具备；不属于网页运行依赖。布局尺寸与边界校验记录在 `results/overview-layout.json`。
