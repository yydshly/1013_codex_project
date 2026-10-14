/* Original teaching models. No subprocesses, model APIs, or upstream cmux connection. */
"use strict";

function createMessageModel(kind = "claude", recipientState = "idle") {
  return { kind, recipientState, phase: "draft", receiving: true };
}

function transitionMessage(model, action) {
  const next = { ...model };
  if (action === "send" && next.phase === "draft" && next.receiving) next.phase = "queued";
  if (action === "disable") {
    next.receiving = false;
    if (next.phase === "queued") next.phase = "failed";
  }
  if (action === "step" && next.phase === "queued") {
    if (next.recipientState === "human") next.recipientState = "idle";
    else next.phase = "delivered";
  } else if (action === "step" && next.phase === "delivered") next.phase = "read";
  return next;
}

function messagePresentation(model) {
  if (model.phase === "draft") return { label: "等待发送", feedback: "选择适配与状态，然后发送。这个模拟只解释投递时机，不模拟模型思考。", canAdvance: false };
  if (model.phase === "failed") return { label: "已停止投递", feedback: "failed：排队期间关闭接收，消息不再交付。重新打开接收也不会自动重送这条失败消息。", canAdvance: false };
  if (model.phase === "read") return { label: "投递轮已结束", feedback: "read：该投递轮已结束（或可手动标记已读）。这只说明消息处理状态，不表示实现任务完成、测试通过或成果已验收。", canAdvance: false };
  if (model.phase === "delivered") return { label: "模拟本轮执行结束", feedback: "delivered：消息已由接收方 Hook 加入上下文；人的草稿保持原样。下一步只模拟该投递轮结束。", canAdvance: true };
  if (model.recipientState === "human") return { label: "模拟人回答当前问题", feedback: "queued：接收方正在等待人的问题 / 权限 / 计划回应，交付暂缓。先模拟人回答，再到支持的交付点接收。", canAdvance: true };
  if (model.recipientState === "busy") return {
    label: model.kind === "claude" ? "模拟下一适配交付点" : "模拟即将停止的 Hook",
    feedback: model.kind === "claude" ? "queued：Claude Code 正在执行，消息等待下一个支持的交付点。模拟点击代表到达该点，不代表立即打断所有工具调用。" : "queued：Codex 正在执行。这里模拟它到达即将停止的 Hook，再接收消息并继续当前轮；不是任意时刻直接唤醒。",
    canAdvance: true
  };
  return model.kind === "claude"
    ? { label: "模拟后台 Hook 唤醒", feedback: "queued：Claude Code 空闲，后台 asyncRewake Hook 可轮询并唤醒。点击模拟消息作为系统提醒进入上下文；不修改输入框。", canAdvance: true }
    : { label: "模拟人提交下一次提示", feedback: "queued：Codex 空闲，Hook 不能主动唤醒。必须等人提交下一次提示，消息随该提示附加为上下文。", canAdvance: true };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { createMessageModel, transitionMessage, messagePresentation };
}

if (typeof document !== "undefined") {
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const initialSessions = () => ({
    research: { name: "A / 源码研究", id: "A", status: "running", lines: ["› 正在核对固定版本的 Hooks 和消息接口…", "[source] docs/agent-messages.md", "[note] 状态与任务验收需要分开理解。"] },
    build: { name: "B / 网页实现", id: "B", status: "waiting", lines: ["› 已制作页面结构，等待补充内容范围。", "[needs input] 需要把历史研究对照也加入页面吗？", "提示：在这里输入会进入当前模拟终端。"] },
    check: { name: "C / 检查结果", id: "C", status: "idle", lines: ["› 检查清单已准备。", "[idle] 等待网页产物和明确的验收标准。", "检查交互、移动布局、来源链接与模拟标签。"] }
  });
  let sessions = initialSessions();
  let focus = "research";
  const statuses = { running: "运行中", waiting: "需要输入", idle: "空闲" };
  function renderWorkbench(feedback) {
    const current = sessions[focus];
    $("#demo-title").textContent = current.name;
    $("#demo-state").textContent = statuses[current.status];
    $("#demo-state").style.color = current.status === "waiting" ? "#efb56f" : "#8cddc2";
    const output = $("#demo-output");
    output.replaceChildren(...current.lines.map((line) => {
      const item = document.createElement("div");
      item.className = "terminal-line" + (line.startsWith("[input]") ? " user" : "");
      item.textContent = line;
      return item;
    }));
    output.scrollTop = output.scrollHeight;
    $$(".agent-choice").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.agent === focus));
      const dot = button.querySelector(".status-dot");
      dot.className = "status-dot " + sessions[button.dataset.agent].status;
      dot.title = statuses[sessions[button.dataset.agent].status];
    });
    $("#demo-feedback").textContent = feedback || `当前焦点：surface:${current.id}。输入仅送到这个模拟会话。`;
  }
  $$(".agent-choice").forEach((button) => button.addEventListener("click", () => {
    focus = button.dataset.agent;
    renderWorkbench();
  }));
  $("#terminal-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const input = $("#terminal-input");
    const text = input.value.trim();
    if (!text) { $("#demo-feedback").textContent = "请先输入一条模拟文本。"; return; }
    const current = sessions[focus];
    current.lines.push("[input] " + text, "[simulation] 当前 Agent 接到输入，转为执行中。没有调用真实模型。");
    current.status = "running";
    input.value = "";
    renderWorkbench(`模拟输入已定向送到 surface:${current.id}。其他会话保持各自上下文。`);
  });
  $("#jump-attention").addEventListener("click", () => {
    const pending = Object.keys(sessions).find((key) => sessions[key].status === "waiting");
    if (pending) { focus = pending; renderWorkbench(`已定位 ${sessions[pending].name}：它需要人的输入。`); }
    else $("#demo-feedback").textContent = "当前没有需要输入的会话，可模拟 A 发出通知。";
  });
  $("#simulate-notification").addEventListener("click", () => {
    sessions.research.status = "waiting";
    sessions.research.lines.push("[notification] 源码材料已整理，请确认研究范围。");
    renderWorkbench("A 发出模拟通知；侧栏标记需要输入，当前焦点保持。点击定位按钮可跳过去。");
  });
  $("#reset-workbench").addEventListener("click", () => { sessions = initialSessions(); focus = "research"; renderWorkbench("工作台模拟已重置。"); });
  renderWorkbench();

  $$("[data-filter]").forEach((button) => button.addEventListener("click", () => {
    const filter = button.dataset.filter;
    $$("[data-filter]").forEach((item) => { item.classList.toggle("active", item === button); item.setAttribute("aria-pressed", String(item === button)); });
    let count = 0;
    $$(".capability-table tbody tr").forEach((row) => {
      row.hidden = filter !== "all" && row.dataset.category !== filter;
      if (!row.hidden) count += 1;
    });
    $("#filter-count").textContent = `显示 ${count} 项能力 / 共 10 项`;
  }));

  const paths = {
    terminal: { title: "① 双向终端：承载真实运行环境", steps: ["人的输入", "终端 Surface / PTY", "Shell / Agent CLI", "输出字节 / ANSI", "libghostty 渲染"], text: "输入和输出双向流动。模型请求、文件操作与工具调用由 Agent 执行；cmux 负责承载进程交互和显示结果。终端输出不是对模型内部状态的完整探测。" },
    status: { title: "② 状态与通知：把注意力送到正确会话", steps: ["Agent Hook / OSC / CLI", "会话身份关联", "状态 / 通知存储", "侧栏与通知环", "人定位并回应"], text: "Hooks 带来原生运行状态与 session ID，OSC 或 CLI 可触发通知。终端能运行任意 CLI，并不意味着每个 CLI 都有同样丰富的状态、唤醒和恢复适配。" },
    control: { title: "③ 控制平面：让人、脚本与 Agent 操作工作台", steps: ["CLI / 调用者", "本地 Unix Socket", "控制协调器", "目标 Workspace / Surface", "终端 / WebKit 操作"], text: "请求显式指定目标或使用当前会话环境，通过统一控制接口创建分屏、发送输入、读取终端和操作浏览器。控制环境的能力可作为更高层工作流的执行工具。" },
    message: { title: "④ 协作消息：存储后在适配点交付", steps: ["发送者 + 接收目标", "消息存储 / queued", "接收方 Hook", "delivered / 上下文", "投递轮结束 / read"], text: "消息通道不会键入接收方的输入草稿。Claude 与 Codex 的空闲唤醒能力不同；read 也不提供任务验收结论。跨 Agent 的协作需要双方有支持的启动方式与适配。" }
  };
  function renderPath(key) {
    const data = paths[key];
    const detail = $("#path-detail");
    const heading = document.createElement("h3"); heading.textContent = data.title;
    const chain = document.createElement("div"); chain.className = "path-chain";
    data.steps.forEach((step, i) => {
      if (i) { const arrow = document.createElement("i"); arrow.textContent = "→"; arrow.setAttribute("aria-hidden", "true"); chain.append(arrow); }
      const node = document.createElement("span"); node.textContent = step; chain.append(node);
    });
    const description = document.createElement("p"); description.textContent = data.text;
    detail.replaceChildren(heading, chain, description);
    $$("[data-path]").forEach((button) => { const active = button.dataset.path === key; button.classList.toggle("active", active); button.setAttribute("aria-pressed", String(active)); });
  }
  $$("[data-path]").forEach((button) => button.addEventListener("click", () => renderPath(button.dataset.path)));
  renderPath("terminal");

  let message = createMessageModel();
  function renderMessage() {
    const presentation = messagePresentation(message);
    $("#message-feedback").textContent = presentation.feedback;
    $("#message-advance").textContent = presentation.label;
    $("#message-advance").disabled = !presentation.canAdvance;
    $("#message-send").disabled = message.phase !== "draft";
    $("#message-disable").disabled = message.phase !== "queued" || !message.receiving;
    $("#recipient-kind").disabled = message.phase !== "draft";
    $("#recipient-state").disabled = message.phase !== "draft";
    const order = ["queued", "delivered", "read"];
    $$("[data-message-state]").forEach((node) => {
      const i = order.indexOf(node.dataset.messageState);
      const current = order.indexOf(message.phase);
      node.classList.toggle("active", i === current);
      node.classList.toggle("done", current > i);
    });
  }
  $("#message-send").addEventListener("click", () => {
    message = transitionMessage(createMessageModel($("#recipient-kind").value, $("#recipient-state").value), "send"); renderMessage();
  });
  $("#message-advance").addEventListener("click", () => { message = transitionMessage(message, "step"); renderMessage(); });
  $("#message-disable").addEventListener("click", () => { message = transitionMessage(message, "disable"); renderMessage(); });
  $("#message-reset").addEventListener("click", () => { message = createMessageModel($("#recipient-kind").value, $("#recipient-state").value); renderMessage(); });
  renderMessage();

  $$("input[name='pain']").forEach((box) => box.addEventListener("change", () => {
    const picked = $$("input[name='pain']:checked").map((item) => item.value);
    const recommendations = [];
    if (picked.includes("parallel")) recommendations.push("用工作区与稳定会话身份组织并行任务");
    if (picked.includes("attention")) recommendations.push("先改善待输入提醒与定位");
    if (picked.includes("context")) recommendations.push("尝试共享材料链接与定向消息，减少搬运");
    if (picked.includes("automation")) recommendations.push("在已有事件规则上建立任务与验收闭环");
    $("#value-feedback").textContent = recommendations.length
      ? "对应方向：" + recommendations.join("；") + "。你当前是 Windows，优先借鉴这些机制；直接使用原生 cmux 需要 Mac。"
      : "先观察当前工具是否已有这些能力。没有明显痛点时，保留架构参考即可。";
  }));
  let printSnapshot;
  window.addEventListener("beforeprint", () => {
    if (printSnapshot) return;
    printSnapshot = { details: $$("details").map((node) => [node, node.open]), rows: $$(".capability-table tbody tr").map((node) => [node, node.hidden]) };
    printSnapshot.details.forEach(([node]) => { node.open = true; });
    printSnapshot.rows.forEach(([node]) => { node.hidden = false; });
  });
  window.addEventListener("afterprint", () => {
    if (!printSnapshot) return;
    printSnapshot.details.forEach(([node, open]) => { node.open = open; });
    printSnapshot.rows.forEach(([node, hidden]) => { node.hidden = hidden; });
    printSnapshot = undefined;
  });
  $("#print-page").addEventListener("click", () => window.print());
  const navItems = $$(".contents nav a");
  if ("IntersectionObserver" in window) {
    const visible = new Map();
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => visible.set(entry.target.id, entry.isIntersecting));
      const first = $$(".chapter").find((chapter) => visible.get(chapter.id));
      if (first) navItems.forEach((item) => { const current = item.hash === "#" + first.id; item.classList.toggle("current", current); if (current) item.setAttribute("aria-current", "location"); else item.removeAttribute("aria-current"); });
    }, { rootMargin: "-100px 0px -55% 0px", threshold: 0 });
    $$(".chapter").forEach((chapter) => observer.observe(chapter));
  }
}
