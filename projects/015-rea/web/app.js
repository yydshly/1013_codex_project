"use strict";

// Fixed teaching content: no model, engine, process, or target application calls.
const teachingScenarios = {
  electron: {
    name: "Electron 应用：导出文件",
    steps: [
      ["你 / 定义范围", "“导出按钮怎样把内容保存为文件？”", "先限定应用版本、目标功能和要回答的问题。一次只研究一条功能链路，便于判断找到的证据是否足够。", "问题 + 对应版本的应用包", "明确的调查目标", "调用了哪些函数；是否使用 IPC；文件实际怎样写入"],
      ["REA / 材料身份", "确认这次分析的是哪一份应用。", "记录目录或 ASAR 的身份和摘要，检查入口、所选脚本和相关清单。缺失材料与解析范围应单独记录。", "指定的本地目录或 ASAR", "产物身份、文件清单、结构和覆盖信息", "缺少的原生模块或运行依赖；不在材料中的服务端逻辑"],
      ["REA / 静态分析", "从按钮相关的路由、字符串或模块定位。", "静态分析取得应用图，再用相关种子查询功能。关键是找到来源位置和关系，而不是仅凭名称认定业务行为。", "应用 Evidence + 导出相关种子", "候选入口、模块及支持它们的位置", "候选是否在当前条件下执行；动态注册是否覆盖"],
      ["AI + REA / 继续追踪", "检查是否经过 preload、IPC 和主进程。", "沿图中已支持的关系继续追踪。若找到文件写入或原生导出边界，保留其材料身份，并按需要追加调查。", "入口与已有关系", "可达链路、边界和未解析关系", "静态链路是否真实执行；权限、文件路径与失败分支"],
      ["AI / 解释与实现", "说明保存流程，写一个自己的最小实现。", "将观察、推导与假设分开：哪些是文件里的事实，哪些是关系推断，哪些仍需运行检查。复现只实现已明确的范围。", "证据、限制与目标功能要求", "带依据的解释 + 待验证实现", "异常输入、环境差异、完整应用等价性"],
      ["人 + 实验 / 对照", "使用同样输入，比较导出结果。", "检查内容、格式、路径、取消和错误处理。记录通过的样本、失败差异和剩余未知；有限样本只能支持相应范围。", "原应用 + 复现实现 + 同一组测试输入", "范围明确的对照记录", "未测试输入、背景操作和未覆盖依赖"]
    ]
  },
  native: {
    name: "原生程序：坐标计算",
    steps: [
      ["你 / 定义范围", "“输入一个坐标后，这个数值怎样算出来？”", "选择一个局部计算，明确目标版本、输入、输出和可获得的原程序样本。", "程序版本 + 一个计算问题", "可对照的局部目标", "函数位置、输入意义、精度和边界条件"],
      ["REA + 引擎 / 确认材料", "识别二进制与适用的分析引擎。", "确认目标格式、架构和摘要，再选择当前主机可用的 Ghidra、Hopper 或 IDA。设置成功不代表引擎已完成真实分析。", "二进制文件 + 提供者环境", "目标身份、可用性和分析状态", "不支持的格式、架构或引擎能力"],
      ["引擎 + REA / 定位函数", "从字符串、符号或调用者找相关函数。", "读取函数伪代码和指令；发现伪代码与指令不一致时，继续检查输入和调用关系。", "候选函数或引用", "函数材料、指令与位置", "错误类型推断、间接调用、缺失符号"],
      ["AI + REA / 读取关系与常量", "确认参数来源、运算和数据常量。", "检查调用者传入的内容、字节中的常量与返回转换。每个结论都应关联来源位置。", "函数、调用者、引用的数据", "局部计算的证据链", "全局状态、浮点转换及未解析路径"],
      ["AI / 重建局部计算", "依据指令写自己的函数。", "将输入意义、运算顺序、类型和状态整理为实现。原始变量名和注释不必能恢复；新实现的行为仍需验证。", "已核查的计算材料", "局部实现与假设清单", "边界精度、溢出、编译器差异"],
      ["人 + 实验 / 原程序对照", "将相同输入送给两种实现。", "比较正常、异常和边界输入。适用时可以检查编译结果，但字节匹配和测试通过都要说明目标、工具链与范围。", "原函数 + 重建函数 + 明确样本", "对应范围的行为或编译对照", "未测输入和整款应用的完整行为"]
    ]
  },
  web: {
    name: "网站：搜索请求",
    steps: [
      ["你 / 定义范围", "“输入关键词后，页面怎样请求并显示结果？”", "明确页面、输入和要观察的过程。问题覆盖前端交互与可见请求，服务端内部实现还需要别的材料。", "页面 + 搜索输入 + 问题", "明确的观察范围", "前端链路、请求构造和后端内部算法"],
      ["REA / 选择观察方式", "决定观察已有页面，还是启动受控场景。", "被动 CDP 观察附加已有页面；主动场景可以导航和操作。两种方式的效果、生命周期与捕获范围不同。", "浏览器目标 + 捕获或动作选择", "明确的目标、方式和实验条件", "附加前活动；未选择的截图、事件或载荷"],
      ["浏览器 + REA / 获取材料", "读取页面与脚本，记录可见请求。", "以合法可获得的脚本和观察窗口内记录为依据。source map 存在与否、网络字段是否暴露，都要按实际结果判断。", "所选页面、脚本和网络观察", "来源位置、页面结构及可见网络信息", "未捕获请求、加密或未暴露数据、后端源码"],
      ["AI + REA / 关联前端路径", "从搜索事件追到请求构造与结果消费者。", "可继续分析捕获脚本，追踪模块与语义关系；静态候选和运行观察分别保留，不能直接把同时出现当作因果证明。", "脚本 Evidence + 运行观察", "前端候选路径及可核查联系", "动态关系、未映射代码和因果关系"],
      ["AI / 解释与最小实现", "解释可见流程，设计自己的搜索交互。", "实现输入、请求、响应处理与展示；若没有服务器实现材料，只能说明观察到的接口与交互，保留内部未知。", "前端证据 + 接口观察", "范围明确的解释与实现方案", "服务端排序、索引、权限及所有输入表现"],
      ["人 + 实验 / 场景比较", "使用相同查询，检查行为和错误处理。", "保存加载、空结果、错误、响应变化和展示结果。比较选择和环境应一致，缺失或不匹配的捕获保持未知。", "可重复场景 + 比较条件", "可比的页面和网络记录", "窗口之外的活动与未覆盖的服务端行为"]
    ]
  }
};

const scenarioSelect = document.querySelector("#scenario");
const stepButtons = [...document.querySelectorAll(".step-button")];
const previousButton = document.querySelector("#demo-prev");
const nextButton = document.querySelector("#demo-next");
let activeStep = 0;

function renderStep() {
  const scenario = teachingScenarios[scenarioSelect.value];
  const step = scenario.steps[activeStep];
  ["actor", "title", "description", "input", "result", "unknown"].forEach((key, index) => {
    document.querySelector(`#demo-${key}`).textContent = step[index];
  });
  stepButtons.forEach((button, index) => {
    if (index === activeStep) button.setAttribute("aria-current", "step");
    else button.removeAttribute("aria-current");
  });
  previousButton.disabled = activeStep === 0;
  nextButton.disabled = activeStep === scenario.steps.length - 1;
  nextButton.textContent = nextButton.disabled ? "已到对照验证" : "下一步 →";
  document.querySelector("#demo-counter").textContent = `${String(activeStep + 1).padStart(2, "0")} / 06`;
}

scenarioSelect.addEventListener("change", () => { activeStep = 0; renderStep(); });
stepButtons.forEach(button => button.addEventListener("click", () => { activeStep = Number(button.dataset.step); renderStep(); }));
previousButton.addEventListener("click", () => { if (activeStep > 0) { activeStep--; renderStep(); } });
nextButton.addEventListener("click", () => { if (activeStep < 5) { activeStep++; renderStep(); } });

const searchField = document.querySelector("#cap-search");
const modeField = document.querySelector("#cap-mode");
const groupButtons = [...document.querySelectorAll(".filter")];
const capabilityCards = [...document.querySelectorAll(".cap-card")];
let activeGroup = "all";
function applyFilters() {
  const query = searchField.value.trim().toLocaleLowerCase();
  let visible = 0;
  for (const card of capabilityCards) {
    const matches = (activeGroup === "all" || card.dataset.group === activeGroup)
      && (modeField.value === "all" || card.dataset.mode === modeField.value)
      && card.textContent.toLocaleLowerCase().includes(query);
    card.hidden = !matches;
    if (matches) visible++;
  }
  document.querySelector("#cap-count").textContent = `显示 ${visible} / ${capabilityCards.length} 项。条目是本页研究分类，不是上游工具数量。`;
  document.querySelector("#cap-empty").hidden = visible !== 0;
  groupButtons.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.group === activeGroup)));
}
searchField.addEventListener("input", applyFilters);
modeField.addEventListener("change", applyFilters);
groupButtons.forEach(button => button.addEventListener("click", () => { activeGroup = button.dataset.group; applyFilters(); }));
document.querySelector("#clear-filters").addEventListener("click", () => {
  activeGroup = "all"; searchField.value = ""; modeField.value = "all"; applyFilters();
});
const compareSelect = document.querySelector("#compare-project");
const compareExpand = document.querySelector("#compare-expand");
const compareDetails = [...document.querySelectorAll(".comparison-detail")];
let showAllComparisons = false;
function applyComparison() {
  compareDetails.forEach(detail => {
    detail.hidden = !showAllComparisons && detail.dataset.comparison !== compareSelect.value;
  });
  compareSelect.disabled = showAllComparisons;
  compareExpand.setAttribute("aria-pressed", String(showAllComparisons));
  compareExpand.textContent = showAllComparisons ? "恢复单项对比" : "展开全部原理";
}
compareSelect.addEventListener("change", applyComparison);
compareExpand.addEventListener("click", () => {
  showAllComparisons = !showAllComparisons;
  applyComparison();
});
const progress = document.querySelector(".reading-progress");
function updateProgress() {
  const total = document.documentElement.scrollHeight - window.innerHeight;
  progress.style.width = `${total > 0 ? Math.min(100, window.scrollY / total * 100) : 0}%`;
}
window.addEventListener("scroll", updateProgress, { passive: true });
window.addEventListener("resize", updateProgress);
window.addEventListener("beforeprint", () => {
  capabilityCards.forEach(card => { card.hidden = false; });
  compareDetails.forEach(detail => { detail.hidden = false; });
  document.querySelector(".static-scenarios").open = true;
});
window.addEventListener("afterprint", applyFilters);
window.addEventListener("afterprint", applyComparison);
renderStep();
applyFilters();
applyComparison();
updateProgress();
