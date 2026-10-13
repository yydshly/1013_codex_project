const $ = (id) => document.getElementById(id);
const sourceCommit = "400b272175945d35eaefa68aefe9106fa9d7e467";
const samples = {
  commerce: { path: "data/gpt-demo-book.json", label: "电商运营入门" },
  photography: { path: "data/gpt-photography-book.json", label: "手机摄影入门" },
};
const state = { mode: "conversation", sample: null, sampleKey: "commerce", sampleCache: {}, loadingSample: false, book: null, config: null, busy: false, done: false, controller: null, run: 0, stats: null };
const explanation = {
  capability: ["把“写一份长材料”变成一次操作。", "接收主题和写作要求，自动规划章节、逐节扩写、合并正文，并提供文件下载。", ["培训手册", "入门教程", "知识指南", "可编辑初稿"]],
  contents: ["仓库提供的是一套写作应用代码。", "主要内容包括 Streamlit 界面、目录/书名/正文生成模块、Groq 接口封装和导出工具。这里的书稿是模型输出，并不是仓库自带的知识库。", ["Python 应用", "提示词与接口", "生成流程", "文件导出"]],
  principle: ["代码组织多次模型请求，顺序生成长稿。", "提示词提出内容要求，代码安排调用和数据传递，模型写出目录与正文。没有新增模型能力，也没有全书质量自动验收。", ["固定流程", "多次调用", "逐节组装", "人工审核"]],
  effect: ["得到一份有结构、可下载的完整初稿。", "下面可以直接阅读本次对话 GPT 写出的 3 节样稿。页面回放已保存内容；模型 API 模式才是程序的真实调用。原流程缺少全书审稿与事实核查。", ["可读样稿", "来源可见", "仍需审核", "非出版成稿"]],
};

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = String(text);
  return node;
}

function setExplanation(key) {
  const [lead, body, tags] = explanation[key];
  document.querySelectorAll("[data-explain]").forEach((button) => {
    const active = button.dataset.explain === key;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
    button.tabIndex = active ? 0 : -1;
  });
  const panel = $("understanding-panel");
  panel.setAttribute("aria-labelledby", `tab-${key}`);
  const paragraph = el("p");
  paragraph.append(el("strong", "", lead), document.createTextNode(` ${body}`));
  const tagList = el("div", "output-tags");
  tags.forEach((tag) => tagList.append(el("span", "", tag)));
  panel.replaceChildren(paragraph, tagList);
}

document.querySelectorAll("[data-explain]").forEach((button, index, buttons) => {
  button.addEventListener("click", () => setExplanation(button.dataset.explain));
  button.addEventListener("keydown", (event) => {
    let next;
    if (event.key === "ArrowRight") next = (index + 1) % buttons.length;
    if (event.key === "ArrowLeft") next = (index + buttons.length - 1) % buttons.length;
    if (event.key === "Home") next = 0;
    if (event.key === "End") next = buttons.length - 1;
    if (next === undefined) return;
    event.preventDefault();
    setExplanation(buttons[next].dataset.explain);
    buttons[next].focus();
  });
});

// A small text-only Markdown renderer. Model text never enters innerHTML.
function appendInline(parent, text) {
  const pattern = /\*\*([^*\n]+)\*\*|`([^`\n]+)`/g;
  let cursor = 0;
  for (const match of text.matchAll(pattern)) {
    parent.append(document.createTextNode(text.slice(cursor, match.index)));
    parent.append(el(match[1] !== undefined ? "strong" : "code", "", match[1] ?? match[2]));
    cursor = match.index + match[0].length;
  }
  parent.append(document.createTextNode(text.slice(cursor)));
}

function renderMarkdown(content) {
  const fragment = document.createDocumentFragment();
  const lines = String(content).replace(/\r\n?/g, "\n").split("\n");
  const isTableDivider = (line) => /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line);
  const cells = (line) => line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
  let index = 0;
  while (index < lines.length) {
    const line = lines[index];
    if (!line.trim()) { index++; continue; }
    if (line.trimStart().startsWith("```")) {
      const codeLines = [];
      index++;
      while (index < lines.length && !lines[index].trimStart().startsWith("```")) codeLines.push(lines[index++]);
      index++;
      const pre = el("pre");
      pre.append(el("code", "", codeLines.join("\n")));
      fragment.append(pre);
      continue;
    }
    if (index + 1 < lines.length && line.includes("|") && isTableDivider(lines[index + 1])) {
      const table = el("table");
      const header = el("thead");
      const headerRow = el("tr");
      cells(line).forEach((cell) => { const node = el("th"); node.scope = "col"; appendInline(node, cell); headerRow.append(node); });
      header.append(headerRow);
      const body = el("tbody");
      index += 2;
      while (index < lines.length && lines[index].includes("|") && lines[index].trim()) {
        const row = el("tr");
        cells(lines[index++]).forEach((cell) => { const node = el("td"); appendInline(node, cell); row.append(node); });
        body.append(row);
      }
      table.append(header, body);
      fragment.append(table);
      continue;
    }
    const heading = line.match(/^#{1,6}\s+(.+)$/);
    if (heading) {
      const node = el(line.startsWith("###") ? "h5" : "h4");
      appendInline(node, heading[1]);
      fragment.append(node); index++; continue;
    }
    if (/^\s*([-*+]\s+|\d+[.)]\s+)/.test(line)) {
      const ordered = /^\s*\d+[.)]\s+/.test(line);
      const list = el(ordered ? "ol" : "ul");
      const pattern = ordered ? /^\s*\d+[.)]\s+(.*)$/ : /^\s*[-*+]\s+(.*)$/;
      while (index < lines.length && pattern.test(lines[index])) {
        const item = el("li"); appendInline(item, lines[index++].match(pattern)[1]); list.append(item);
      }
      fragment.append(list); continue;
    }
    if (/^>\s?/.test(line)) {
      const quote = el("blockquote"); appendInline(quote, line.replace(/^>\s?/, "")); fragment.append(quote); index++; continue;
    }
    const paragraphLines = [line];
    index++;
    while (index < lines.length && lines[index].trim() && !/^(#{1,6}\s|\s*[-*+]\s|\s*\d+[.)]\s|\s*```|>)/.test(lines[index]) && !(index + 1 < lines.length && lines[index].includes("|") && isTableDivider(lines[index + 1]))) paragraphLines.push(lines[index++]);
    const paragraph = el("p"); appendInline(paragraph, paragraphLines.join("\n")); fragment.append(paragraph);
  }
  return fragment;
}

function normalizeBook(book) {
  if (!book || !Array.isArray(book.outline) || !Array.isArray(book.sections)) throw new Error("书稿数据格式不完整。");
  return {
    title: String(book.title || "未命名长文初稿"), topic: String(book.topic || ""), instructions: String(book.instructions || ""),
    outline: book.outline.map((part) => ({ title: String(part.title || "未命名章节"), description: String(part.description || "") })),
    sections: book.sections.map((part) => ({ title: String(part.title || "未命名章节"), content: String(part.content || ""), truncated: part.truncated === true })),
    provenance: book.provenance || {},
  };
}

function characterCount(book) { return book.sections.reduce((sum, section) => sum + Array.from(section.content).length, 0); }
function isConversation(book = state.book) { return book?.provenance?.mode === "conversation"; }
function hasTruncatedSections(book = state.book) { return book?.sections?.some((section) => section.truncated) || state.stats?.truncated_sections?.length > 0; }
function recordTime(book = state.book) {
  const timestamp = book?.provenance?.generated_at;
  if (timestamp) {
    const date = new Date(timestamp);
    if (!Number.isNaN(date.getTime())) return `${new Intl.DateTimeFormat("zh-CN", { timeZone: "Asia/Shanghai", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false }).format(date)}（北京时间）`;
    return String(timestamp);
  }
  return book?.provenance?.created_at || "未记录";
}
function provenanceText(book = state.book) {
  return isConversation(book) ? "本次对话 GPT 生成样稿 · 流程回放 · 未通过项目 API 调用" : `通过本地模型 API 生成 · ${book?.provenance?.model || state.config?.model || "模型待确认"}`;
}

function setProgress(message, detail = "") {
  $("progress-status").textContent = message;
  $("progress-detail").textContent = detail;
}

function setStep(current, finished = false) {
  const order = ["outline", "title", "sections", "done"];
  const currentIndex = order.indexOf(current);
  document.querySelectorAll("[data-step]").forEach((node) => {
    const index = order.indexOf(node.dataset.step);
    node.classList.toggle("active", !finished && index === currentIndex);
    node.classList.toggle("complete", finished || index < currentIndex);
  });
}

function updateControls() {
  $("generate-button").disabled = state.busy || state.loadingSample || !state.sample || (state.mode === "live" && !state.config?.configured);
  $("sample-mode").disabled = state.busy || state.loadingSample;
  $("live-mode").disabled = state.busy || state.loadingSample;
  $("sample-select").disabled = state.busy || state.loadingSample;
  $("restore-button").disabled = state.loadingSample;
  $("cancel-button").classList.toggle("hidden", !state.busy);
  $("progress-indicator").classList.toggle("running", state.busy);
  ["export-md", "export-txt", "print-book"].forEach((id) => { $(id).disabled = state.busy || state.loadingSample || !state.done; });
  $("export-note").textContent = state.done ? (hasTruncatedSections() ? "正文有截断 · 下载后需续写" : isConversation() ? "完整 GPT 样稿可下载" : "模型初稿可下载") : "完成后可下载初稿";
}

function clearError() { $("error-panel").textContent = ""; $("error-panel").classList.add("hidden"); }
function showError(message) { $("error-panel").textContent = message; $("error-panel").classList.remove("hidden"); }

function setMode(mode) {
  if (state.busy) return;
  state.mode = mode;
  const conversation = mode === "conversation";
  $("sample-picker").classList.toggle("hidden", !conversation);
  $("sample-mode").classList.toggle("selected", conversation);
  $("live-mode").classList.toggle("selected", !conversation);
  $("sample-mode").setAttribute("aria-pressed", String(conversation));
  $("live-mode").setAttribute("aria-pressed", String(!conversation));
  $("topic").readOnly = conversation;
  $("instructions").readOnly = conversation;
  $("input-label-note").textContent = conversation ? "样稿固定" : "可自定义";
  $("mode-description").textContent = conversation ? "阅读本次对话 GPT 已写好的样稿，回放从目录到正文的过程。" : "通过本地服务调用配置的模型，为你的主题生成新初稿。";
  $("generate-button").replaceChildren(el("span", "", conversation ? "▶" : "↗"), document.createTextNode(conversation ? " 回放写作流程" : " 生成新的初稿"));
  $("generate-button").firstChild.setAttribute("aria-hidden", "true");
  $("cancel-button").textContent = conversation ? "停止回放" : "停止等待";
  $("sample-disclosure").replaceChildren();
  if (conversation) {
    $("sample-disclosure").append(el("strong", "", "本次对话 GPT 生成样稿"), el("br"), document.createTextNode("流程回放 · 未通过项目 API 调用。"), el("br"), document.createTextNode("回放延时只为展示顺序，不代表模型速度。"));
    if (state.sample) {
      $("topic").value = state.sample.topic;
      $("instructions").value = state.sample.instructions;
    }
  } else {
    $("sample-disclosure").append(el("strong", "", "新主题需要独立的 API 配置"), el("br"), document.createTextNode("当前对话 GPT 可以提供已写好的样稿；网页自动写新主题需另接模型 API。请求会发送到你配置的模型服务。"));
  }
  clearError();
  updateControls();
}

function renderRecord() {
  const container = $("experiment-record-content");
  container.replaceChildren();
  container.append(el("p", "", `来源：${provenanceText()}`));
  if (state.book?.provenance?.method) container.append(el("p", "", state.book.provenance.method));
  if (state.book?.provenance?.scope) container.append(el("p", "", state.book.provenance.scope));
  container.append(el("p", "", `生成 / 记录时间：${recordTime()}`));
  if (state.book?.provenance?.data_note) container.append(el("p", "", state.book.provenance.data_note));
  if (state.stats && !isConversation()) {
    const stats = el("div", "record-grid");
    [[state.stats.requests, "实际请求次数"], [state.stats.usage_reported === false ? undefined : state.stats.input_tokens, "输入 tokens（服务报告）"], [state.stats.usage_reported === false ? undefined : state.stats.output_tokens, "输出 tokens（服务报告）"], [state.stats.elapsed_seconds, "总耗时 / 秒"]].forEach(([value, label]) => {
      const cell = el("div"); cell.append(el("strong", "", value ?? "未报告"), el("span", "", label)); stats.append(cell);
    });
    container.append(stats);
    container.append(el("p", "", "仅反映本次生成；不能用来推断其他模型或原项目的性能。"));
  } else if (isConversation()) container.append(el("p", "", "未获得本次对话的推理 token、耗时及 API 调用统计。回放不产生模型请求，不展示推理性能。"));
  if (hasTruncatedSections()) container.append(el("p", "truncation-notice", "服务报告部分正文因输出限制被截断。请求已返回，但书稿需要继续补写；请勿当作完整成稿。"));
  const source = el("p");
  source.append(document.createTextNode("参考流程："));
  const link = el("a", "", `上游 ${sourceCommit.slice(0, 7)} · main.py`);
  link.href = `https://github.com/Bklieger/infinite-bookshelf/blob/${sourceCommit}/main.py`;
  link.target = "_blank"; link.rel = "noopener noreferrer";
  source.append(link, document.createTextNode("。这是为理解原理编写的研究演示，界面与接口适配不是上游原样运行。"));
  container.append(source);
}

function renderBook() {
  const book = state.book;
  if (!book) return;
  $("book-title").textContent = book.title;
  $("book-provenance").textContent = provenanceText(book);
  $("book-meta").textContent = `${book.sections.length} / ${book.outline.length || 3} 节正文 · ${characterCount(book).toLocaleString("zh-CN")} 字符（含标点与格式）`;
  const badge = $("mode-badge");
  badge.replaceChildren(el("span"), document.createTextNode(isConversation(book) ? " 对话 GPT 样稿" : " 模型 API 实测"));
  const content = $("book-sections"); content.replaceChildren();
  book.sections.forEach((section, index) => {
    const sectionElement = el("section", "book-section");
    sectionElement.id = `chapter-${index}`;
    const heading = el("h3", "", `${String(index + 1).padStart(2, "0")} / ${section.title}`);
    heading.tabIndex = -1;
    sectionElement.append(heading);
    if (section.truncated) sectionElement.append(el("p", "truncation-notice", "本节达到模型输出限制，正文被截断，需要继续补写。"));
    const description = book.outline[index]?.description;
    if (description) sectionElement.append(el("p", "section-description", description));
    sectionElement.append(renderMarkdown(section.content));
    content.append(sectionElement);
  });
  $("empty-preview").classList.toggle("hidden", book.sections.length > 0);
  const navigation = $("chapter-links"); navigation.replaceChildren();
  book.outline.forEach((chapter, index) => {
    const button = el("button"); button.type = "button";
    button.disabled = !book.sections[index];
    button.append(el("span", "chapter-index", String(index + 1).padStart(2, "0")), el("span", "", chapter.title));
    button.classList.toggle("active", index === 0);
    button.addEventListener("click", () => {
      const section = $(`chapter-${index}`);
      if (!section) return;
      const reader = $("book-reader");
      reader.scrollTo({ top: section.offsetTop - reader.offsetTop - 20, behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth" });
      navigation.querySelectorAll("button").forEach((node) => node.classList.toggle("active", node === button));
      section.querySelector("h3").focus({ preventScroll: true });
    });
    navigation.append(button);
  });
  $("chapter-nav-note").textContent = book.outline.length ? "点击章节，阅读对应正文。" : "目录会首先出现在这里。";
  renderRecord();
  updateControls();
}

function stopCurrentRun() {
  state.run++;
  state.controller?.abort();
  state.controller = null;
  state.busy = false;
}

function restoreSample() {
  if (!state.sample) return;
  stopCurrentRun();
  state.book = normalizeBook(state.sample);
  state.stats = null;
  state.done = true;
  setMode("conversation");
  setStep("done", true);
  renderBook();
  $("book-reader").scrollTop = 0;
  setProgress(`${samples[state.sampleKey].label} · 本次对话 GPT 样稿已载入`, `${state.sample.sections.length} 节完整正文`);
}

async function chooseSample(key, updateUrl = true) {
  if (state.busy || state.loadingSample || !Object.hasOwn(samples, key)) return;
  state.loadingSample = true;
  updateControls();
  setProgress(`正在载入${samples[key].label}样稿…`);
  try {
    let sample = state.sampleCache[key];
    if (!sample) {
      const response = await fetch(new URL(samples[key].path, document.baseURI));
      if (!response.ok) throw new Error("样稿文件未找到。");
      sample = normalizeBook(await response.json());
      state.sampleCache[key] = sample;
    }
    state.sampleKey = key;
    state.sample = sample;
    $("sample-select").value = key;
    restoreSample();
    if (updateUrl) {
      const url = new URL(window.location.href);
      if (key === "commerce") url.searchParams.delete("sample");
      else url.searchParams.set("sample", key);
      window.history.replaceState(null, "", url);
    }
  } catch {
    $("sample-select").value = state.sampleKey;
    showError(`无法载入${samples[key].label}样稿。请通过 HTTP 服务打开本页，并确认 ${samples[key].path} 文件存在。`);
    setProgress(state.sample ? "样稿切换未完成 · 保留原样稿" : "未载入样稿");
  } finally {
    state.loadingSample = false;
    updateControls();
  }
}

function delay(milliseconds, signal) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => { signal.removeEventListener("abort", abort); resolve(); }, milliseconds);
    const abort = () => { clearTimeout(timer); reject(new DOMException("已停止", "AbortError")); };
    if (signal.aborted) abort();
    else signal.addEventListener("abort", abort, { once: true });
  });
}

function handleEvent(event) {
  if (event.type === "error") throw new Error(String(event.message || "模型服务返回错误。"));
  if (event.type === "outline") {
    if (!Array.isArray(event.outline)) throw new Error("模型未返回可用的目录。");
    state.book.outline = event.outline.map((part) => ({ title: String(part.title || "未命名章节"), description: String(part.description || "") }));
    setStep("outline");
    setProgress(state.mode === "conversation" ? "流程回放：目录已准备好" : "已生成目录", `${event.outline.length} 节`);
  } else if (event.type === "title") {
    state.book.title = String(event.title || "未命名初稿");
    setStep("title");
    setProgress(state.mode === "conversation" ? "流程回放：为初稿命名" : "已生成书名");
  } else if (event.type === "section") {
    const index = Number(event.index);
    if (!Number.isInteger(index) || index !== state.book.sections.length) throw new Error("正文返回顺序不完整，请重新生成。");
    state.book.sections.push({ title: String(event.title || state.book.outline[index]?.title || "未命名章节"), content: String(event.content || ""), truncated: event.truncated === true });
    setStep("sections");
    setProgress(state.mode === "conversation" ? `流程回放：第 ${index + 1} 节正文已展开` : `已生成第 ${index + 1} 节正文`, `${index + 1} / ${state.book.outline.length} 节`);
  } else if (event.type === "done") {
    state.book = normalizeBook(event.book);
    state.stats = event.stats || null;
    state.done = true;
    setStep("done", true);
    setProgress(state.mode === "conversation" ? "流程回放完成 · 内容为本次对话 GPT 已保存样稿" : hasTruncatedSections() ? "模型请求完成 · 部分正文被截断，需要续写" : "模型生成完成 · 可下载初稿", `${state.book.sections.length} 节正文`);
  } else return;
  renderBook();
}

async function replay(signal) {
  await delay(500, signal);
  handleEvent({ type: "outline", outline: state.sample.outline });
  await delay(650, signal);
  handleEvent({ type: "title", title: state.sample.title });
  for (const [index, section] of state.sample.sections.entries()) {
    await delay(1000, signal);
    handleEvent({ type: "section", index, ...section });
  }
  await delay(600, signal);
  handleEvent({ type: "done", book: state.sample });
}

async function generateLive(signal) {
  const response = await fetch(new URL("api/generate", document.baseURI), {
    method: "POST", headers: { "Content-Type": "application/json" }, signal,
    body: JSON.stringify({ topic: $("topic").value.trim(), instructions: $("instructions").value.trim(), chapter_count: 3 }),
  });
  if (!response.ok) {
    let message = `服务返回 HTTP ${response.status}。`;
    try { const payload = await response.json(); message = payload.message || payload.error || message; } catch { /* Preserve HTTP status on a non-JSON response. */ }
    throw new Error(String(message));
  }
  if (!response.body) throw new Error("浏览器未收到生成数据，请使用支持流式读取的浏览器。");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let end;
      while ((end = buffer.indexOf("\n")) !== -1) {
        const line = buffer.slice(0, end).trim();
        buffer = buffer.slice(end + 1);
        if (line) handleEvent(JSON.parse(line));
      }
    }
    buffer += decoder.decode();
    if (buffer.trim()) handleEvent(JSON.parse(buffer));
    if (!state.done) throw new Error("连接在书稿完成前结束，可重新生成。");
  } finally { reader.releaseLock(); }
}

async function startGeneration(event) {
  event.preventDefault();
  if (state.busy || !state.sample) return;
  if (state.mode === "live" && !state.config?.configured) return;
  if (!$("generation-form").reportValidity()) return;
  const run = ++state.run;
  const controller = new AbortController();
  state.controller = controller;
  state.busy = true;
  state.done = false;
  state.stats = null;
  state.book = { title: "正在准备长文初稿…", topic: $("topic").value, instructions: $("instructions").value, outline: [], sections: [], provenance: state.mode === "conversation" ? { ...state.sample.provenance } : { mode: "live", model: state.config.model } };
  clearError();
  setStep("outline");
  setProgress(state.mode === "conversation" ? "流程回放开始 · 不会发起模型调用" : "正在请求模型规划目录…");
  renderBook();
  $("book-reader").scrollTop = 0;
  try {
    if (state.mode === "conversation") await replay(controller.signal);
    else await generateLive(controller.signal);
  } catch (error) {
    if (run !== state.run) return;
    if (error.name === "AbortError") {
      setProgress(state.mode === "conversation" ? "回放已停止 · 可以重新开始或恢复 GPT 样稿" : "已停止接收 · 可以恢复 GPT 样稿");
      if (state.mode === "live") showError("页面已停止等待。已发出的模型请求可能仍在服务端执行，稍后可以重新生成。");
    }
    else {
      const message = error.message === "Failed to fetch" ? "无法连接本地服务，请确认服务仍在运行。" : error.message;
      showError(`本次生成未完成：${message} 可以重新生成，或恢复 GPT 样稿继续阅读。`);
      setProgress("生成未完成 · 已保留当前预览");
    }
  } finally {
    if (run === state.run) {
      state.busy = false;
      state.controller = null;
      updateControls();
    }
  }
}

function exportBook(format) {
  if (!state.done || !state.book) return;
  const book = state.book;
  const note = provenanceText(book);
  const lines = [`# ${book.title}`, "", `> ${note}`, "", `生成 / 记录时间：${recordTime(book)}`, "", `主题：${book.topic}`, "", `写作要求：${book.instructions}`, "", "## 目录", "", ...book.outline.map((chapter, index) => `${index + 1}. ${chapter.title}`), ""];
  if (book.provenance.data_note) lines.push(`数据说明：${book.provenance.data_note}`, "");
  book.sections.forEach((section, index) => {
    lines.push(`# ${index + 1}. ${section.title}`, "");
    if (section.truncated) lines.push("> 本节达到模型输出限制，正文被截断，需要继续补写。", "");
    lines.push(section.content, "");
  });
  let content = lines.join("\n");
  if (format === "txt") content = content.replace(/^#{1,6}\s+/gm, "").replace(/^>\s?/gm, "").replace(/\*\*([^*]+)\*\*/g, "$1");
  const blob = new Blob(["\uFEFF", content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${book.title.replace(/[<>:"/\\|?*\u0000-\u001f]/g, "-").slice(0, 100)}.${format === "md" ? "md" : "txt"}`;
  document.body.append(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

$("sample-mode").addEventListener("click", restoreSample);
$("sample-select").addEventListener("change", (event) => chooseSample(event.target.value));
$("live-mode").addEventListener("click", () => setMode("live"));
$("restore-button").addEventListener("click", restoreSample);
$("generation-form").addEventListener("submit", startGeneration);
$("cancel-button").addEventListener("click", () => state.controller?.abort());
$("export-md").addEventListener("click", () => exportBook("md"));
$("export-txt").addEventListener("click", () => exportBook("txt"));
$("print-book").addEventListener("click", () => { if (state.done) window.print(); });

async function initialize() {
  const requestedSample = new URL(window.location.href).searchParams.get("sample");
  const initialSample = Object.hasOwn(samples, requestedSample) ? requestedSample : "commerce";
  $("sample-select").value = initialSample;
  const results = await Promise.allSettled([
    chooseSample(initialSample, false),
    fetch(new URL("api/config", document.baseURI), { signal: AbortSignal.timeout(5000) }).then(async (response) => { if (!response.ok) throw new Error("无配套服务"); return response.json(); }),
  ]);
  if (results[1].status === "fulfilled") state.config = results[1].value;
  else state.config = { configured: false, reason: "当前是静态演示。接入模型 API 需启动本地配套服务。" };
  const configured = state.config?.configured === true;
  $("model-status").classList.toggle("ready", configured);
  $("model-status").replaceChildren(el("span", "status-dot"), el("span", "", configured ? `模型 API 已配置：${state.config.model || "兼容模型"}` : `模型 API 未配置。${state.config.reason || "请在服务端配置后刷新页面。"}`));
  updateControls();
}

initialize();
