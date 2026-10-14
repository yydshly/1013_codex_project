"use strict";

// These snapshots are teaching examples, not model calls or vendor API events.
const modes = {
  workflow: {
    label: "由程序组织后续",
    title: "主 Agent 写程序，服务端后台执行。",
    flow: "目标 → 编排程序 → 分阶段执行 Agent → 汇总",
    description: "程序收集各 Agent 的结果，再选择分支、循环和下一阶段；主线程可以继续与用户沟通。",
    limit: "流程中的 Agent 线程由程序管理，主 Agent 不能像普通子 Agent 那样逐个发送后续消息。"
  },
  subagents: {
    label: "由主 Agent 持续组织",
    title: "主 Agent 分派任务，读取报告，再继续跟进。",
    flow: "目标 → 主 Agent 分派 → 子 Agent 报告 → 主 Agent 跟进与汇总",
    description: "主 Agent 决定后续任务，能够向已有子 Agent 发送跟进消息；子 Agent 保留自身的对话上下文。",
    limit: "官方普通子 Agent 委派是一层；会话最多保持 25 个子线程，空闲线程也计入。动态工作流线程不计入这项限制。"
  }
};
document.querySelectorAll("[data-mode]").forEach((button) => {
  button.addEventListener("click", () => {
    const mode = modes[button.dataset.mode];
    document.querySelectorAll("[data-mode]").forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
    for (const key of ["label", "title", "flow", "description", "limit"]) {
      document.getElementById(`mode-${key}`).textContent = mode[key];
    }
  });
});

const row = (state, kind, evidence) => ({ state, kind, evidence });
const waiting = () => row("待分派", "", "先约定来源、版本和输出格式");
const running = () => row("研究中", "running", "分析与实验在同一独立任务中进行");
const returned = () => row("待复核", "", "示例：结论＋源码位置＋实验记录＋未验证项");
const accepted = () => row("已验收", "done", "示例证据已检查，结论范围与依据对应");
const stage = (title, description, observation, rows) => ({ title, description, observation, rows });
const define = () => stage("先定义研究任务", "研究三个候选项目。每个任务同时负责分析与实验，提交结论、依据和未验证事项。", "先约定输出和验收条件，防止最后只收到三段无法比较的摘要。", [waiting(), waiting(), waiting()]);
const execute = () => stage("分派三个独立任务", "各 Agent 处理自己的项目和结果目录；这些独立任务可以并行。", "观察任务状态与写入范围。对话上下文独立，仍应防止共享文件冲突。", [running(), running(), running()]);
const collect = () => stage("收集结构化成果", "三个执行任务返回研究结果，尚未将成果标为最终完成。", "拿到结果不等于通过验收。记录覆盖了哪些问题，缺少哪些证据。", [returned(), returned(), returned()]);
const verify = () => stage("按相同标准核对证据", "逐项检查来源、研究版本、源码依据和实验记录。", "验收依赖资料和实验，不能只让 Agent 相互认可。未验证内容保持明确标记。", [accepted(), accepted(), accepted()]);
const finish = () => stage("由一个步骤统一汇总", "所有任务验收后，组织比较报告、研究文档与索引。教学流程结束。", "这个演示展示组织工作的方法。真实质量、耗时和费用，需要运行单 Agent 与多 Agent 对比实验。", [accepted(), accepted(), accepted()]);
const scenarios = {
  normal: [define(), execute(), collect(), verify(), finish()],
  retry: [
    define(), execute(),
    stage("项目 B 的首次任务失败", "A 与 C 返回结果，B 未产出有效成果。失败被记录，汇总步骤等待。", "不能将失败任务静默跳过。由明确的重试规则决定是否继续；超过限制要披露缺失。", [returned(), row("首次失败", "failed", "示例：资料读取失败，尚无有效结果"), returned()]),
    stage("只重试失败的任务", "保留 A 与 C 的已有成果，重新执行 B；本例假定这次成功。", "重试不应反复执行已完成任务。实际工具还需避免重复写入和重复外部操作。", [returned(), row("重试中", "running", "只补项目 B，保留其他成果"), returned()]),
    collect(), verify(), finish()
  ],
  evidence: [
    define(), execute(),
    stage("项目 B 的结论证据不足", "三个任务都有输出，但 B 的一项能力结论缺少对应实验。", "输出流畅不等于结论可信。把问题定位到具体结论和证据，不直接判定整份报告合格。", [returned(), row("待补证据", "failed", "示例：宣称已复现，但未提供实验记录"), returned()]),
    stage("退回补证据或收窄结论", "B 需要补实验记录，或把相关能力标为未验证；A 与 C 不重做。", "补证据也是任务。重做轮数应受控，不能用无限循环承诺所有结论最终都能证明。", [returned(), row("补证据中", "running", "补原文位置、实验记录或未验证说明"), returned()]),
    stage("重新提交可核查成果", "B 返回补充后的示例材料，结果进入复核。", "这次假定补齐成功。真实任务可能仍无法验证，应保留失败与未覆盖事项。", [returned(), row("再次待复核", "", "示例：已附记录，并收窄未验证的结论"), returned()]),
    verify(), finish()
  ]
};
let step = 0;
const scenarioSelect = document.getElementById("demo-scenario");
const nextButton = document.getElementById("demo-next");
function renderDemo() {
  const steps = scenarios[scenarioSelect.value];
  const current = steps[step];
  document.getElementById("demo-stage-number").textContent = `步骤 ${step + 1} / ${steps.length}`;
  document.getElementById("demo-title").textContent = current.title;
  document.getElementById("demo-description").textContent = current.description;
  document.getElementById("demo-observation").textContent = current.observation;
  const rows = current.rows.map((task, index) => {
    const tr = document.createElement("tr");
    const th = document.createElement("th");
    th.scope = "row";
    th.textContent = `项目 ${String.fromCharCode(65 + index)}`;
    const stateCell = document.createElement("td");
    const state = document.createElement("span");
    state.className = `task-state ${task.kind}`;
    state.textContent = task.state;
    stateCell.append(state);
    const evidence = document.createElement("td");
    evidence.textContent = task.evidence;
    tr.append(th, stateCell, evidence);
    return tr;
  });
  document.getElementById("demo-tasks").replaceChildren(...rows);
  const markers = steps.map((item, index) => {
    const li = document.createElement("li");
    li.className = index < step ? "done" : index === step ? "current" : "";
    li.setAttribute("aria-label", `步骤 ${index + 1}：${item.title}`);
    if (index === step) li.setAttribute("aria-current", "step");
    return li;
  });
  document.getElementById("demo-progress").replaceChildren(...markers);
  nextButton.disabled = step === steps.length - 1;
  nextButton.textContent = nextButton.disabled ? "教学流程结束" : "下一步 →";
}
nextButton.addEventListener("click", () => {
  if (step < scenarios[scenarioSelect.value].length - 1) step += 1;
  renderDemo();
});
function resetDemo() { step = 0; renderDemo(); }
document.getElementById("demo-reset").addEventListener("click", resetDemo);
scenarioSelect.addEventListener("change", resetDemo);
renderDemo();

// The undersea example illustrates dependencies; it does not build a 3D world.
const oceanTasks = {
  foundation: { id: "T1", title: "场景基座", fields: [
    ["能力", "提供场景加载、对象管理与共享基础接口。"],
    ["输入", "第一版目标、米制坐标、资源与对象接口约定。"],
    ["输出", "可启动的基础场景、接口说明与检查记录。"],
    ["依赖与约束", "依赖整体设计；维护共享基础，接口变动记录版本并通知依赖任务。"],
    ["验收", "场景能加载，测试对象可创建与移除，坐标和资源格式符合规格。"],
    ["失败处理", "记录加载错误或接口缺失，修复基础后再安排受影响任务。"]
  ]},
  environment: { id: "T2", title: "海床、珊瑚与水体", fields: [
    ["能力", "构建小型珊瑚礁环境，提供区域与障碍物查询。"],
    ["输入", "场景基座、资源规范、米制坐标与环境查询约定。"],
    ["输出", "环境模块、区域与障碍物数据、接口和检查记录。"],
    ["依赖与约束", "依赖场景基座；维护环境范围，共享坐标与查询格式保持一致。"],
    ["验收", "环境可加载，查询结果与场景位置一致，玩家与鱼群能使用这些数据。"],
    ["失败处理", "定位资源或查询问题；接口改变时检查鱼群、玩家和互动的影响。"]
  ]},
  player: { id: "T3", title: "移动与视角", fields: [
    ["能力", "实现玩家移动、观察视角与位置状态。"],
    ["输入", "场景基座、坐标约定、输入方式与玩家状态接口。"],
    ["输出", "玩家控制模块、状态接口、操作与检查记录。"],
    ["依赖与约束", "依赖场景基座；环境检查需要真实区域数据，避免直接修改生物或任务逻辑。"],
    ["验收", "可以移动和观察，位置状态可被读取，接入环境后检查边界与联动。"],
    ["失败处理", "区分输入、坐标与环境依赖问题，修复后重测受影响操作。"]
  ]},
  fish: { id: "T4", title: "鱼群游动与避障", fields: [
    ["能力", "实现鱼群游动、活动范围与避障。"],
    ["输入", "米制坐标、环境查询接口、鱼模型与更新时步。"],
    ["输出", "可集成的鱼群模块、接口说明、改动与检查记录。"],
    ["依赖与约束", "依赖场景基座和环境数据；维护鱼群范围，共享接口有问题先报告。"],
    ["验收", "在指定检查场景中保持活动范围、避开珊瑚，并与玩家观察功能组合。"],
    ["失败处理", "缺接口报告阻塞；检查失败修复对应问题，重测受影响联动。"]
  ]},
  interaction: { id: "T5", title: "观察与地标互动", fields: [
    ["能力", "识别可观察对象和地标，产生约定的互动事件。"],
    ["输入", "玩家位置与视角、环境地标、生物对象及事件格式。"],
    ["输出", "互动模块、对象与事件说明、联动检查记录。"],
    ["依赖与约束", "依赖环境、玩家和生物接口；保持对象标识与事件格式一致。"],
    ["验收", "观察能对应正确对象，找到地标时事件内容正确，能被任务模块接收。"],
    ["失败处理", "记录无法识别或事件不一致的原因，修复接口消费者或生产者后重测。"]
  ]},
  objectives: { id: "T6", title: "探索任务与界面", fields: [
    ["能力", "显示探索提示、记录三个地标并给出完成反馈。"],
    ["输入", "互动事件、地标标识、玩家状态和第一版完成条件。"],
    ["输出", "探索任务与界面模块、状态说明、完整体验检查记录。"],
    ["依赖与约束", "依赖互动事件；可先用模拟事件开发，最终必须接入真实联动。"],
    ["验收", "同一地标不重复计数，找到三个不同地标后反馈正确，场景整体可体验。"],
    ["失败处理", "区分事件缺失、标识错误和界面问题，保留已完成部分并修复受影响链路。"]
  ]}
};
const oceanState = (text, kind = "waiting") => ({ text, kind });
const oceanStages = [
  { title: "先明确玩法、接口与完成标准", description: "主 Agent 应用工程方法形成计划，先固定第一版范围和共享规格。各模块等待输入。", observation: "先明确任务边界、输入输出与依赖，再决定并行范围。框架没有内置海底世界的最优拆分模板。", states: [oceanState("等待规格"), oceanState("等待基座"), oceanState("等待基座"), oceanState("等待接口"), oceanState("等待模块"), oceanState("等待事件")] },
  { title: "先做好共享的场景基座", description: "基础任务实现对象加载和共享接口。后续任务可以准备材料，正式接入仍需要基础成果。", observation: "共同接口由一个明确任务维护，检查基础是否可用再接入模块。避免多个执行任务各自改变坐标或入口。", states: [oceanState("开发与检查中", "running"), oceanState("等待基座"), oceanState("等待基座"), oceanState("等待基座"), oceanState("等待模块"), oceanState("等待事件")] },
  { title: "环境、玩家与鱼群按接口开发", description: "基座的示例检查通过后，环境与玩家开始实现；鱼群先使用临时环境数据开发接口，避障仍需等待真实环境检查。", observation: "可并行的工作与必须等待的依赖分别记录。临时数据可以帮助提前开发，不能替代真实联动验收。", states: [oceanState("局部检查通过", "done"), oceanState("开发与检查中", "running"), oceanState("开发与检查中", "running"), oceanState("临时数据开发", "running"), oceanState("等待模块"), oceanState("等待事件")] },
  { title: "接入互动，再组织探索任务", description: "环境、玩家和鱼群提交局部检查成果。互动模块接入这些接口；任务界面可先用模拟事件开发，最终接入真实事件。", observation: "三个局部通过的模块还不能证明整个世界完成。检查对象标识、事件内容与任务状态是否贯通。", states: [oceanState("局部检查通过", "done"), oceanState("局部检查通过", "done"), oceanState("局部检查通过", "done"), oceanState("局部检查通过", "done"), oceanState("联动开发中", "running"), oceanState("模拟事件开发", "running")] },
  { title: "集成时发现鱼群穿过珊瑚", description: "教学案例假设鱼群错误转换环境坐标单位。把问题定位到鱼群逻辑，保留其他成果，暂停受影响的联动验收。", observation: "报告具体失败、原因与影响范围。任务已经返回不代表整体验收通过；局部问题应定向修复，接口改变时再评估所有依赖。", states: [oceanState("局部检查通过", "done"), oceanState("局部检查通过", "done"), oceanState("局部检查通过", "done"), oceanState("集成检查失败", "failed"), oceanState("等待修复联动"), oceanState("等待整体验收")] },
  { title: "修复后重测完整的小区域", description: "本例假定修复成功，再检查游动、避障、观察、地标计数与完成反馈。第一版验收后，才规划扩大海域和增加玩法。", observation: "这只是固定教学数据的状态变化。真正交付需要可运行的世界与检查记录；下一轮可以产生新的开发、检查和修复任务。", states: Object.keys(oceanTasks).map(() => oceanState("示例验收通过", "done")) }
];
let oceanPhase = 0;
let selectedOceanTask = "fish";
function renderOcean() {
  const current = oceanStages[oceanPhase];
  document.getElementById("ocean-stage-label").textContent = `阶段 ${oceanPhase + 1} / ${oceanStages.length}`;
  document.getElementById("ocean-stage-title").textContent = current.title;
  document.getElementById("ocean-stage-description").textContent = current.description;
  document.getElementById("ocean-observation").textContent = current.observation;
  document.querySelectorAll("[data-ocean-phase]").forEach(button => button.setAttribute("aria-pressed", String(Number(button.dataset.oceanPhase) === oceanPhase)));
  const keys = Object.keys(oceanTasks);
  document.querySelectorAll("[data-ocean-task]").forEach(button => {
    const key = button.dataset.oceanTask;
    const state = current.states[keys.indexOf(key)];
    button.setAttribute("aria-pressed", String(key === selectedOceanTask));
    const badge = button.querySelector(".ocean-status");
    badge.textContent = state.text;
    badge.className = `ocean-status ${state.kind}`;
  });
  const task = oceanTasks[selectedOceanTask];
  document.getElementById("ocean-task-label").textContent = `${task.id} / 任务单与验收接口`;
  document.getElementById("ocean-task-title").textContent = task.title;
  const fields = task.fields.map(([label, content]) => {
    const field = document.createElement("div");
    const term = document.createElement("dt");
    const description = document.createElement("dd");
    term.textContent = label;
    description.textContent = content;
    field.append(term, description);
    return field;
  });
  document.getElementById("ocean-task-contract").replaceChildren(...fields);
}
document.querySelectorAll("[data-ocean-phase]").forEach(button => button.addEventListener("click", () => { oceanPhase = Number(button.dataset.oceanPhase); renderOcean(); }));
document.querySelectorAll("[data-ocean-task]").forEach(button => button.addEventListener("click", () => { selectedOceanTask = button.dataset.oceanTask; renderOcean(); }));
renderOcean();

const sectionLinks = [...document.querySelectorAll(".sidebar nav a")];
const sections = sectionLinks.map((link) => document.querySelector(link.getAttribute("href")));
let scrollScheduled = false;
function updateReadingPosition() {
  let active = sections[0];
  for (const section of sections) {
    if (section.getBoundingClientRect().top <= 180) active = section;
  }
  sectionLinks.forEach((link) => {
    if (link.getAttribute("href") === `#${active.id}`) link.setAttribute("aria-current", "location");
    else link.removeAttribute("aria-current");
  });
  scrollScheduled = false;
}
window.addEventListener("scroll", () => {
  if (!scrollScheduled) { scrollScheduled = true; requestAnimationFrame(updateReadingPosition); }
}, { passive: true });
updateReadingPosition();
