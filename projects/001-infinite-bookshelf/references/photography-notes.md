# 手机摄影样稿：资料与核验记录

核验日期：2026-10-13（Asia/Shanghai）。本文件记录中文摄影样稿中少量基础事实的来源，不是对 Infinite Bookshelf 的模型性能测试。资料使用 Apple、Adobe 与 Nikon 的官方文档与教学内容，以下是自行概括，没有复制原文图片或长段正文。

## 基础事实核对

| 核验项 | 可采用的准确表述 | 一手资料 |
| --- | --- | --- |
| 点按对焦与曝光 | 以 iPhone 照片模式为例，点按画面可选择对焦区域，在旁边拖动曝光控制调亮或调暗；长按可锁定对焦与曝光。其他品牌、机型、模式和系统版本可能不同。 | [Apple：Use iPhone camera tools to set up your shot](https://support.apple.com/guide/iphone/use-camera-tools-iph3dc593597/ios) |
| 三分法 | 把画面想成九宫格，用线条和交点安排主体，是可尝试的构图方法。中心、对称等构图也可以成立；不应声称好照片必须遵守三分法。 | [Adobe：How to use, and break, the rule of thirds](https://www.adobe.com/creativecloud/photography/discover/rule-of-thirds.html) |
| 主体与背景 | 靠近、后退或改变拍摄位置，会改变主体与背景的关系和取景内容。是否更好需比较照片；不能把“越近越好”当通用规则。 | [Adobe Lightroom Academy：Fill The Frame](https://lightroom.adobe.com/academy/principles/composition/fill-the-frame) |
| 稳定与运动模糊 | 低光拍摄时稳住手机，或使用可靠支撑，能减少相机移动造成的模糊。但即使相机稳定，慢曝光仍可能使运动主体模糊；拍摄运动不能只依赖防抖。 | [Apple：Use Night mode on your iPhone](https://support.apple.com/en-gb/102519)、[Nikon：Capturing or Freezing Motion in Photos](https://www.nikonusa.com/learn-and-explore/c/tips-and-techniques/capturing-or-freezing-motion-in-photos) |
| 自然光光向与软硬 | 窗边光不一定柔和：没有直射阳光时可以得到较柔和的照明，直射窗光也可能产生明显阴影。可以转动主体或改变位置，观察光向与阴影，按想表达的效果选择。 | [Nikon：The beginner’s guide to light](https://www.nikon.co.uk/en_GB/learn-and-explore/magazine/tips-and-tricks/the-beginners-guide-to-light) |
| 混光与白平衡 | 混合不同色温的光源可能造成画面不同区域偏色，整体白平衡难以同时校正。初学练习可以尽量用一致光源；这不是混光禁令，混光也可用于创作。 | [Nikon：The beginner’s guide to White Balance](https://www.nikon.co.uk/en_GB/learn-and-explore/magazine/tips-and-tricks/the-beginners-guide-to-white-balance)、[Nikon：The beginner’s guide to light](https://www.nikon.co.uk/en_GB/learn-and-explore/magazine/tips-and-tricks/the-beginners-guide-to-light) |

## 核验范围

这里只核对拍摄主体、构图参考、背景整理、点按对焦与亮度、自然光和模糊原因等基础表述。通用建议是面向零基础读者设计的练习，不保证每款手机拥有同样按钮或自动处理能力。

当前对话 GPT 生成的书稿与网页回放，是内容与流程演示的参考结果。没有进行手机实拍、机型对比、学员学习效果评估，也没有记录项目调用模型 API 的性能。官方资料核对属于本次研究的人工审读步骤，上游项目本身没有自动执行这些核查。

## 样稿审读结果

审读对象：[《手机摄影入门小手册》](../experiments/results/gpt-photography-book.md)，由当前对话 GPT 于 2026-10-13 生成并保存。三节正文累计 3,280 个字符，统计来自保存的 JSON `sections[].content` 字符串长度之和，包含标题、空格和 Markdown 格式。

| 章节 | 事实审读 | 可执行性审读 |
| --- | --- | --- |
| 先确定主体 再整理画面 | 对靠近、换角度、对焦距离与三分法的表述保留条件；没有把居中或倾斜排除为错误构图 | 用同一杯子比较居中、网格位置与拍摄站位，观察主体、背景和边缘，并要求具体选片理由 |
| 用自然光拍清楚主体 | 明确窗光可能硬或柔，限定 iPhone 操作示例，并区分亮度、对焦、相机移动和主体移动 | 亮度比较与光向比较分成两轮，问题排查表提供首个可尝试动作；不要求购买器材或专业模式 |
| 完成一次拍摄并复盘 | 把十分钟写成练习安排，假设复盘例子明确标注为教学记录，没有声称已拍出真实结果 | 有拍摄顺序、选片证据、保留前后照片、一次只改一个问题及明确的交付物 |

审读未发现需修正的上述基础事实。三节沿用杯子案例，步骤从构图到光线，再到拍摄复盘，范围与面向初学者的写作要求相符。它提供可尝试的练习设计；没有真实样片，不能评价练习是否已经产生摄影改善，也不能推断上游逐节生成流程会取得同样质量。

网页入口：[摄影样稿与流程回放](http://127.0.0.1:8765/?sample=photography)，需要先启动本子项目本地服务。实际页面验证记录由演示说明单独维护。
