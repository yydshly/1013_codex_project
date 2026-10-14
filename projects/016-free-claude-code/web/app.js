(() => {
  "use strict";
  const sourceRoot = "https://github.com/Alishahryar1/free-claude-code/blob/74d4ccfde724f7416fa2a728d594d704dddc7c94/";
  document.querySelectorAll("[data-source]").forEach(link => {
    link.href = sourceRoot + (link.hasAttribute("data-root-file") ? "" : "src/free_claude_code/") + link.dataset.source;
  });

  const clients = {
    claude: {label: "Claude Code", endpoint: "/v1/messages", model: "claude-sonnet-demo"},
    codex: {label: "Codex", endpoint: "/v1/responses", model: "fcc-demo"}
  };
  const models = {
    deepseek: {label: "DeepSeek 示例", ref: "deepseek/demo-model", location: "供应商云端 API（示意）"},
    ollama: {label: "Ollama 示例", ref: "ollama/demo-model", location: "本机 Ollama 推理服务（示意）"},
    custom: {label: "自定义 API 示例", ref: "custom_demo/demo-model", location: "https://api.example.com/v1（示意）"}
  };
  const readTool = {name: "read_file", input_schema: {type: "object", properties: {path: {type: "string"}}, required: ["path"]}};
  const toolInput = {path: "README.md"};
  const prompt = "读取项目说明，并整理一份能力摘要。";
  const state = {agent: "claude", model: "deepseek", step: 0, fallback: false};
  const byId = id => document.getElementById(id);
  const messageRequest = client => client === "claude" ? {
    model: clients.claude.model,
    messages: [{role: "user", content: prompt}],
    tools: [readTool]
  } : {
    model: clients.codex.model,
    input: [{role: "user", content: prompt}],
    tools: [{type: "function", name: "read_file", parameters: readTool.input_schema}]
  };

  function steps() {
    const client = clients[state.agent];
    const model = models[state.model];
    const target = state.fallback ? "备用模型服务（教学示意）" : model.label;
    const targetRef = state.fallback ? "backup/demo-model" : model.ref;
    const convertedCall = state.agent === "claude" ? {
      type: "tool_use", id: "call_demo_01", name: "read_file", input: toolInput
    } : {
      type: "function_call", call_id: "call_demo_01", name: "read_file", arguments: JSON.stringify(toolInput)
    };
    return [
      {
        title: "Agent 把任务发到 FCC。",
        description: `${client.label} 发送问题、上下文和可用工具定义，使用 FCC 的代理 API 地址。这个步骤改变请求去向；客户端的任务组织与执行框架继续工作。`,
        takeaway: "代理 URL 是模型请求的入口，不是库文件夹或模型权重路径。",
        label: `客户端 → FCC ${client.endpoint}`,
        payload: messageRequest(state.agent),
        note: "客户端请求示意。真实请求通常含更多上下文与参数；示例模型 ID 不可直接调用。"
      },
      {
        title: state.fallback ? "FCC 根据配置选择备用目标。" : "FCC 解析你配置的真实目标。",
        description: state.fallback ? "这里假设主模型在任何内容交付前不可用，代理按预先配置的有序备用列表尝试下一目标。真实恢复还需要检查响应和工具状态，不能保证所有故障都可继续。" : `FCC 解析直接模型选择，或根据客户端档位映射到 ${model.label}。路由主要依据配置，并没有在这里自动判断任务的最佳模型。`,
        takeaway: state.fallback ? "备用顺序由你配置，故障切换与智能任务路由是两种不同功能。" : "统一入口固定，真实供应商与模型由代理配置决定。",
        label: "FCC 内部 → 实际路由目标",
        payload: {requested_model: client.model, primary: model.ref, selected: targetRef, model_service: state.fallback ? "备用服务地址（示意）" : model.location, fallback_before_output: state.fallback},
        note: "路由记录为教学示意，不是 FCC 的正式日志格式。未读取或保存任何真实凭据。"
      },
      {
        title: "适配格式，调用真实模型。",
        description: `此处演示把客户端请求转换成 Chat Completions 格式，再交给 ${target}。真实协议取决于提供商；兼容的 Messages 或 Responses 服务也可走原生适配路径。`,
        takeaway: "FCC 调用模型服务；生成发生在你选择的真实模型一端。",
        label: "FCC → 真实服务（Chat 格式示意）",
        payload: {model: targetRef.split("/").slice(1).join("/"), messages: [{role: "user", content: prompt}], tools: [{type: "function", function: {name: "read_file", parameters: readTool.input_schema}}]},
        note: "示例展示核心字段关系，不是完整 API 请求，也没有实际联网调用模型。"
      },
      {
        title: "把模型的工具调用转回客户端。",
        description: `${target} 生成“读取 README.md”的工具调用。FCC 适配为 ${client.label} 能识别的输出或流式事件；此时文件还未由模型直接读取。`,
        takeaway: "模型提出工具指令；实际工具操作交给 Agent 的执行环境。",
        label: `真实模型 → FCC → ${client.label}`,
        payload: convertedCall,
        note: "简化后的客户端工具调用示意。真实流式输出还包含事件、标识、状态和用量等字段。"
      },
      {
        title: "Agent 按权限执行文件读取。",
        description: `${client.label} 在自己的工具环境中处理 read_file，根据权限与目录范围读取文件，并把结果加入会话。网页这里仅展示固定样例，没有读取你电脑的文件。`,
        takeaway: "文件、命令和其他工具的执行权限属于客户端及其执行环境。",
        label: "Agent → 本机工具 → 工具结果",
        payload: {executor: client.label, tool: "read_file", input: toolInput, result: "固定样例：本项目提供统一代理入口与模型协议适配。", permission: "由客户端执行环境决定"},
        note: "read_file 是教学工具名。此网页没有 Agent 进程、文件权限或命令执行能力。"
      },
      {
        title: "工具结果再次交给模型。",
        description: "Agent 把工具结果和已有上下文再次发到 FCC，代理适配并调用模型。模型可以继续调用工具，或基于结果生成摘要；任务可能经历多轮往返。",
        takeaway: "完整闭环是：模型决策 → Agent 执行 → 结果回传 → 模型继续。",
        label: "工具结果 → FCC → 真实模型",
        payload: state.agent === "claude" ? {model: client.model, messages: [{role: "user", content: [{type: "tool_result", tool_use_id: "call_demo_01", content: "固定样例文件内容……"}]}], expected_next: "模型继续生成项目能力摘要"} : {model: client.model, input: [{type: "function_call_output", call_id: "call_demo_01", output: "固定样例文件内容……"}], expected_next: "模型继续生成项目能力摘要"},
        note: "为便于理解，仅展示工具结果片段；真实请求需要完整且一致的工具调用历史。"
      }
    ];
  }

  function render() {
    const client = clients[state.agent];
    const model = models[state.model];
    const current = steps()[state.step];
    byId("agent-label").textContent = client.label;
    byId("ingress-label").textContent = client.endpoint;
    byId("model-label").textContent = state.fallback && state.step > 0 ? "备用模型示例" : model.label;
    byId("target-label").textContent = state.fallback && state.step > 0 ? "backup/demo-model" : model.ref;
    byId("step-eyebrow").textContent = `步骤 ${String(state.step + 1).padStart(2, "0")} / 06`;
    byId("step-title").textContent = current.title;
    byId("step-description").textContent = current.description;
    byId("step-takeaway").textContent = current.takeaway;
    byId("payload-label").textContent = current.label;
    byId("request-payload").textContent = JSON.stringify(current.payload, null, 2);
    byId("payload-note").textContent = current.note;
    byId("next-step").textContent = state.step === 5 ? "重新开始 ↻" : "下一步 →";
    byId("fallback-note").hidden = !state.fallback;
    document.querySelectorAll("[data-agent]").forEach(button => button.setAttribute("aria-pressed", String(button.dataset.agent === state.agent)));
    document.querySelectorAll("[data-step]").forEach(button => {
      if (Number(button.dataset.step) === state.step) button.setAttribute("aria-current", "step");
      else button.removeAttribute("aria-current");
    });
    const focus = state.step === 0 || state.step === 4 ? "route-agent" : state.step === 3 ? "route-model" : "route-proxy";
    ["route-agent", "route-model"].forEach(id => byId(id).classList.toggle("is-current", id === focus));
    document.querySelector(".route-proxy").classList.toggle("is-current", focus === "route-proxy");
  }
  document.querySelectorAll("[data-agent]").forEach(button => button.addEventListener("click", () => {state.agent = button.dataset.agent; render();}));
  document.querySelectorAll("[data-step]").forEach(button => button.addEventListener("click", () => {state.step = Number(button.dataset.step); render();}));
  byId("model-select").addEventListener("change", event => {state.model = event.target.value; render();});
  byId("fallback-toggle").addEventListener("change", event => {state.fallback = event.target.checked; render();});
  byId("next-step").addEventListener("click", () => {state.step = (state.step + 1) % 6; render();});
  byId("reset-lab").addEventListener("click", () => {state.step = 0; render();});
  render();

  const diagramDialog = byId("diagram-dialog");
  const diagramViewport = byId("diagram-viewport");
  const diagramImage = byId("diagram-full-image");
  let diagramScale = 1;
  let diagramWidth = 1600;
  function scaleDiagram(value) {
    diagramScale = Math.max(0.1, Math.min(2, value));
    diagramImage.style.width = `${Math.round(diagramWidth * diagramScale)}px`;
    byId("diagram-scale").textContent = `${Math.round(diagramScale * 100)}%`;
    byId("diagram-zoom-out").disabled = diagramScale <= 0.1;
    byId("diagram-zoom-in").disabled = diagramScale >= 2;
  }
  function fitDiagram() {
    scaleDiagram(Math.min(1, (diagramViewport.clientWidth - 20) / diagramWidth));
  }
  document.querySelectorAll("[data-diagram]").forEach(link => link.addEventListener("click", event => {
    if (typeof diagramDialog.showModal !== "function") return;
    event.preventDefault();
    diagramWidth = Number(link.dataset.width) || 1600;
    diagramImage.src = link.dataset.diagram;
    diagramImage.alt = link.querySelector("img").alt;
    byId("diagram-dialog-title").textContent = link.dataset.title;
    diagramDialog.showModal();
    fitDiagram();
    diagramViewport.scrollTop = 0;
    diagramViewport.scrollLeft = 0;
  }));
  byId("diagram-zoom-in").addEventListener("click", () => scaleDiagram(diagramScale + 0.15));
  byId("diagram-zoom-out").addEventListener("click", () => scaleDiagram(diagramScale - 0.15));
  byId("diagram-fit").addEventListener("click", fitDiagram);
  byId("diagram-close").addEventListener("click", () => diagramDialog.close());
  diagramViewport.tabIndex = 0;
  diagramDialog.addEventListener("click", event => { if (event.target === diagramDialog) diagramDialog.close(); });
  window.addEventListener("resize", () => { if (diagramDialog.open) fitDiagram(); });

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        document.querySelectorAll(".site-header nav a").forEach(link => link.classList.toggle("active", link.hash === `#${entry.target.id}`));
      });
    }, {rootMargin: "-110px 0px -60% 0px", threshold: 0});
    ["top", "essence", "understanding", "request-lab", "gateway-internals", "comparison", "value", "evidence"].forEach(id => observer.observe(byId(id)));
  }
})();
