# 全面理解总览图：生成提示词

日期：2026-10-14。工具：内置 imagegen。新生成一张 PNG，不修改或覆盖原 SVG。

依据：本子项目 README 及固定源码 244170e17bf8bc97401f65e04d261533d252572a。图中文字是我们的研究整理，不是上游运行截图或完整下载实测。

```text
Use case: infographic-diagram.
Asset: one comprehensive Chinese educational infographic for an existing repository research page. Brand-new image, no reference image. It must be a finished, readable, polished infographic, not a webpage screenshot.
Create ONE portrait poster, ideally 2400 × 3200 pixels, sharp simplified Chinese text, warm off-white background, dark forest green headings, muted sage card fills, restrained ochre accents. Clean editorial typesetting, generous margins, strong typographic hierarchy, thin arrows, small line icons (books, download, folder, school, headphones). No ornamental clutter, no fake textbook covers, no official logos. All text must be exact and legible; domains and commit hash must be spelled correctly. Use a structured grid with full-width header, clear numbered modules, some paired cards, a full-width pipeline and a compact footer. Include every module below. Make the central statement and download source especially prominent. This image summarizes verified SOURCE CODE behavior, not a claim that we performed actual textbook downloads.

TEXT AND LAYOUT:
HEADER:
Small label: "012 · GitHub 项目理解总览"
Main title: "不同版本的小学课本下载器"
Secondary title: "tchMaterial Parser"
Description: "从国家中小学智慧教育平台获取教材与配套资料，批量下载、自动命名、分类保存。"
Scope note: "本图聚焦小学；上游也覆盖初中、高中。资源与版本以平台实际提供为准。"

01 / THREE ROLE DIAGRAM:
Heading: "资源、工具、本地资料库：三个角色"
Three horizontally linked boxes:
"官方平台" / "提供教材和教学资源"
→ "下载工具" / "解析链接、管理任务、下载整理"
→ "你的电脑" / "保存 PDF、音频及关联文件"
Small note: "GitHub 存放程序代码；项目声明不存储、托管或分发教材。"

02 / SOURCES AND CONTENT (large module):
Heading: "从哪些源下载？"
Callout: "当前适配国家中小学智慧教育平台，不是任意网站下载器。"
Clearly show three levels in the SAME platform infrastructure, not three independent content libraries:
"官网入口" / "basic.smartedu.cn" / "查找教材、课程和页面链接"
"目录与详情" / "s-file-1.ykt.cbern.com.cn" / "s-file-2.ykt.cbern.com.cn" / "读取资源编号、标题、分类与文件地址"
"文件下载节点" / "r1-ndr-private.ykt.cbern.com.cn" / "r2-ndr-private.ykt.cbern.com.cn" / "r3-ndr-private.ykt.cbern.com.cn" / "常见文件节点，也使用元信息中的其他完整地址"
A separate small box:
"可获取的内容"
"教材 PDF · 配套音频"
"部分课程或备课页面的课件、教学设计、导学案、PPT、Word"
"默认浏览目录主要是教材；其他受支持资源可通过页面链接解析。"

03 / FEATURE CARDS:
Heading: "优点：把重复操作集中完成"
Six compact feature cards with title and short text:
"批量选择" / "搜索教材、勾选一批，或每行输入一个链接"
"自动整理" / "按标题命名，批量按学段 / 学科 / 版本分类"
"任务管理" / "集中查看进度、速度、错误；停止与失败重试"
"补齐资料" / "跳过目标位置已有同名文件，减少重复下载"
"章节书签" / "平台提供有效目录与页码时，可写入 PDF 书签"
"本地使用" / "文件保存在自选目录，便于离线阅读和归档"
Small note: "三平台桌面界面：Windows / Linux / macOS。"

04 / PIPELINE:
Heading: "原理：解析资源信息，再取得文件"
A numbered left-to-right pipeline in six boxes:
"选择链接" → "提取资源编号" → "读取 JSON 信息" → "选择文件地址" → "按需认证下载" → "命名与分类保存"
Note: "部分文件需要自己的登录凭据；源码按请求生成签名。先写临时文件，适用时写书签，再保存成品。"
Clarification: "这里的“解析”是找文件，不是理解教材正文。"

05 / VALUE AND WHEN (two columns):
LEFT heading: "意义与对你的价值"
"少做逐本下载、命名、建目录和失败补齐"
"方便准备整学期、多学科和不同版本资料"
"为人工教材比较、本地资料库提供文件入口"
"可学习认证、任务调度、文件保存和错误处理"
Highlight: "核心收益来自获取与整理流程的便利。"
RIGHT heading: "适合哪些场景？"
"家长：按学校用书准备小学整学期资料"
"学生：离线阅读、复习与配套听力"
"教师：获取备课文件，人工比较教材版本"
"研究者：积累本地资料，并保留来源记录"
Bottom spanning note: "只要一两本，直接用官网通常足够；批量需求越频繁，工具越有价值。安装、凭据配置和接口维护也有成本。"

06 / BOUNDARIES (highly readable, non-alarmist):
Heading: "使用前要知道的边界"
"学校教材要核对：年级、学科、册次、出版社与版别、修订版次、封面版权页和目录。"
"不保证所有资源可下载；接口、权限和资源可能变化。"
"失败重试从头开始，不是断点续传；同名跳过不等于内容校验或自动更新。"
"没有内置正文提取、OCR、向量索引或 RAG 问答。"
"MIT 是代码许可，教材版权另属权利人；上游要求个人学习、教学参考，不商业使用或二次分发。"

07 / EXTENSION PATH:
Heading: "以后可以怎样扩展？"
A clear pipeline:
"下载与整理" → "来源 / 版本 / 校验登记" → "正文提取与 OCR" → "切块与检索索引" → "带版本和页码引用的 RAG"
Separate note: "优先完善来源追溯、更新识别、持久任务与断点续传。后续内容处理和 RAG 都是扩展建议，尚未实现。"

FOOTER:
"研究依据：happycola233/tchMaterial-parser"
"固定源码：244170e17bf8bc97401f65e04d261533d252572a · 2026-10-14"
"本仓库理解图，非上游界面；源码已核对，登录后完整下载尚未实测。"

Accuracy constraints: do not invent publishers, claim all versions covered, imply multiple unrelated sources, show any token, say RAG exists, guarantee school textbook consistency, promise speed/cost percentages, or imply the GitHub repository hosts textbooks. Every title and sentence must have a clear reading order. Text must not be truncated or overlap.
```
