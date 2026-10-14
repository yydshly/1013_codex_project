"use strict";

// All states are authored teaching examples. No model or media service is called.
const initialState = () => ({
  stage: 0,
  revision: 0,
  duration: 90,
  clips: ["开场口播", "产品镜头", "结尾说明"],
  subtitles: ["呃，今天介绍我们的产品。", "它用起来比较方便。", "联系我们了解更多。"],
  humanEdited: false,
});
let state = initialState();
const history = [];
const stages = [
  { title: "产品介绍原始素材", description: "等待第一轮剪辑", action: "让 AI 生成初稿 →", message: "把这段产品口播剪成一分钟，去掉停顿，保留清楚的字幕。", reply: "提出整体目标后，AI 可以组织剪辑与字幕工作。点击下一步查看示例初稿。", receipt: "当前素材 90 秒；示例只展示三个镜头与三句字幕。", takeaway: "先提出整体目标，再查看初稿；每一轮继续修改当前项目。" },
  { title: "一分钟产品介绍", description: "第一轮剪辑完成，等待你检查", action: "通过 UI 调整作品 →", message: "把这段产品口播剪成一分钟，去掉停顿，保留清楚的字幕。", reply: "示例初稿已完成：删去停顿与口头语，把片长调整到 60 秒，保留产品镜头。", receipt: "修改片长、剪辑点和第一句字幕；仍保留同一份可编辑项目。", takeaway: "AI 完成批量处理，人可以直接在可视化界面查看和接手。" },
  { title: "产品画面先出现", description: "你把产品镜头移到开头，并改了第二句", action: "让 AI 只修改第三句 →", message: "我先把产品镜头放到开头，再把第二句改得简短一些。", reply: "这是人的直接编辑：画面顺序和第二句字幕已更新。你还可以在右侧输入自己的第二句，再继续下一步。", receipt: "人的修改保存在当前工作稿；下一轮从这个状态出发。", takeaway: "试着修改第二句。随后 AI 只改第三句，你的第二句和镜头顺序会保留。" },
  { title: "保留手动调整，修改第三句", description: "AI 本轮只更新了第三句字幕", action: "检查当前版本 →", message: "只把第三句改成“欢迎联系我们，获取完整方案。”，保留我刚才改的镜头和第二句。", reply: "第三句已更新。产品镜头仍在开头，第二句保持你当前保存的内容。", receipt: "本轮范围：第三句字幕。片长、镜头顺序、第二句保持当前值。", takeaway: "对话给出明确范围，AI 继续当前作品。可以撤销这一步，回到人的修改版本。" },
  { title: "当前版本，交给人确认", description: "确认字幕、画面与声音后，再导出", action: "流程已看完", message: "我会检查字幕、镜头和声音，再确认是否导出。", reply: "教学流程结束。真实使用中仍需预览、试听和验收，再由实际视频引擎导出。", receipt: "本网页没有生成或导出真实视频；可以下载本页的研究摘要与总览图。", takeaway: "最终效果由人检查。可编辑项目保留下来，后续仍能继续调整。" },
];
const $ = (selector) => document.querySelector(selector);

function message(role, text) {
  const item = document.createElement("div");
  item.className = `chat-message ${role === "智能体示例" ? "agent" : "human"}`;
  const label = document.createElement("span");
  label.className = "chat-role";
  label.textContent = role;
  const body = document.createElement("p");
  body.textContent = text;
  item.append(label, body);
  return item;
}

function render() {
  const current = stages[state.stage];
  const chat = $("#demo-chat");
  chat.replaceChildren(message("人的目标与操作", current.message), message("智能体示例", current.reply));
  const receipt = document.createElement("div");
  receipt.className = "change-receipt";
  const receiptTitle = document.createElement("strong");
  receiptTitle.textContent = "这一轮改变了什么";
  const receiptText = document.createElement("span");
  receiptText.textContent = current.receipt;
  receipt.append(receiptTitle, receiptText);
  chat.append(receipt);

  $("#preview-title").textContent = current.title;
  $("#preview-description").textContent = current.description;
  $("#project-revision").textContent = `工作稿 v${state.revision}`;
  $("#duration-chip").textContent = `${state.duration} 秒`;
  $("#timeline-note").textContent = state.stage >= 2 ? "保留人的镜头调整" : "原始顺序";
  const timeline = $("#demo-timeline");
  timeline.replaceChildren();
  state.clips.forEach((name, index) => {
    const clip = document.createElement("div");
    clip.className = "demo-clip";
    const number = document.createElement("span");
    number.textContent = `镜头 ${index + 1}`;
    const title = document.createElement("strong");
    title.textContent = name;
    clip.append(number, title);
    timeline.append(clip);
  });
  const subtitles = $("#demo-subtitles");
  subtitles.replaceChildren();
  state.subtitles.forEach((text, index) => {
    const line = document.createElement("li");
    const human = index === 1 && state.humanEdited;
    const ai = index === 2 && state.stage >= 3;
    if (human) line.className = "human-edit";
    if (ai) line.className = "changed";
    const number = document.createElement("b");
    number.textContent = String(index + 1).padStart(2, "0");
    const content = document.createElement("div");
    const words = document.createElement("span");
    words.textContent = text;
    content.append(words);
    if (human || ai) {
      const label = document.createElement("small");
      label.textContent = human ? "人的手动修改 · 当前值保留" : "AI 本轮修改 · 只改这一句";
      content.append(label);
    }
    line.append(number, content);
    subtitles.append(line);
  });
  $("#manual-edit").hidden = state.stage < 2 || state.stage === 4;
  if (state.stage >= 2) $("#manual-subtitle").value = state.subtitles[1];
  $("#manual-status").textContent = "这是你通过界面修改的当前字幕。";
  $("#next-step").textContent = current.action;
  $("#next-step").disabled = state.stage === 4;
  $("#undo-step").disabled = history.length === 0;
  $("#demo-takeaway").textContent = current.takeaway;
  document.querySelectorAll("[data-stage]").forEach((element) => {
    const number = Number(element.dataset.stage);
    element.classList.toggle("done", number < state.stage);
    if (number === state.stage) element.setAttribute("aria-current", "step");
    else element.removeAttribute("aria-current");
  });
}

function remember() {
  history.push(structuredClone(state));
}

$("#next-step").addEventListener("click", () => {
  if (state.stage === 4) return;
  remember();
  state.stage += 1;
  if (state.stage === 1) {
    state.duration = 60;
    state.subtitles[0] = "今天介绍我们的产品。";
    state.revision += 1;
  } else if (state.stage === 2) {
    state.clips = ["产品镜头", "开场口播", "结尾说明"];
    state.subtitles[1] = "操作简单，上手更快。";
    state.humanEdited = true;
    state.revision += 1;
  } else if (state.stage === 3) {
    state.subtitles[2] = "欢迎联系我们，获取完整方案。";
    state.revision += 1;
  }
  render();
});

$("#undo-step").addEventListener("click", () => {
  if (history.length === 0) return;
  state = history.pop();
  render();
});

$("#reset-demo").addEventListener("click", () => {
  state = initialState();
  history.length = 0;
  render();
});

$("#manual-edit").addEventListener("submit", (event) => {
  event.preventDefault();
  const value = $("#manual-subtitle").value.trim();
  if (!value) {
    $("#manual-status").textContent = "请填写第二句字幕。";
    return;
  }
  if (value === state.subtitles[1]) {
    $("#manual-status").textContent = "内容与当前字幕相同，无需再保存。";
    return;
  }
  remember();
  state.subtitles[1] = value;
  state.humanEdited = true;
  state.revision += 1;
  render();
  $("#manual-status").textContent = "已保存你的修改；下一轮 AI 示例会保留这一句。";
});

render();
