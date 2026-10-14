(() => {
  "use strict";
  const data = window.VIBE42_RESEARCH;
  if (!data) return;
  const q = (selector) => document.querySelector(selector);
  const all = (selector) => [...document.querySelectorAll(selector)];
  const pressed = (selector, selected) => all(selector).forEach((button) => button.setAttribute("aria-pressed", String(button === selected)));

  const map = q("#understanding-map");
  if (map && data.overview) {
    const overview = data.overview;
    const figure = q(".understanding-figure");
    let path = "input", position = 0, guided = true;
    function showView(mode) {
      const focus = mode === "principle";
      figure.dataset.view = mode;
      map.setAttribute("viewBox", focus ? "0 570 1400 565" : "0 0 1400 2250");
      map.setAttribute("height", focus ? "565" : "2250");
      q("#principle-explorer").hidden = !focus;
      const relay = q('[data-map-route="relay"]').getAttribute("aria-pressed") === "true";
      map.querySelector('[data-principle="transport"] .ov-text tspan').textContent = focus ? (relay ? "中继转发密文" : "可行时直连") : "直连 / 密文中继";
      if (!focus) {
        all("[data-principle]").forEach((node) => {node.classList.remove("is-selected");node.setAttribute("aria-pressed","false");});
        all("[data-trace]").forEach((edge) => edge.classList.remove("is-tracing"));
      }
      pressed("[data-map-view]", q(`[data-map-view="${mode}"]`));
      q("#map-caption").textContent = focus
        ? "同一张总览图的原理区域。点击7个节点查看解释，也可以选择路径逐步追踪；手机可在图内横向滑动。"
        : "原创理解总览，2026-10-14。点击原理节点或选择“原理放大”，进入同一底图的交互讲解。下载图为静态版本。";
    }
    function explain(key) {
      const item = overview.principles.find((entry) => entry.id === key);
      if (!item) return;
      ["term", "title", "body", "mechanism", "example", "boundary"].forEach((field) => {q(`#principle-${field}`).textContent = item[field];});
      all("[data-principle]").forEach((node) => {
        const selected = node.dataset.principle === key;
        node.classList.toggle("is-selected", selected);
        node.setAttribute("aria-pressed", String(selected));
      });
    }
    function showTrace(index) {
      guided = true;
      const trace = overview.traces[path];
      position = Math.max(0, Math.min(trace.steps.length - 1, index));
      const step = trace.steps[position];
      q("#principle-step-count").textContent = `${trace.label} · ${String(position+1).padStart(2,"0")} / ${String(trace.steps.length).padStart(2,"0")}`;
      q("#principle-step-title").textContent = step.title;
      q("#principle-step-text").textContent = step.text;
      q("#principle-prev").disabled = position === 0;
      q("#principle-next").disabled = position === trace.steps.length - 1;
      q("#principle-next").textContent = "下一步 →";
      all("[data-trace]").forEach((edge) => edge.classList.toggle("is-tracing", edge.dataset.trace === trace.direction));
      explain(step.node);
    }
    function inspect(key) {
      const item = overview.principles.find((entry) => entry.id === key);
      if (!item) return;
      showView("principle");
      guided = false;
      explain(key);
      q("#principle-step-count").textContent = "自由查看 · 点击节点阅读机制与边界";
      q("#principle-step-title").textContent = `你正在查看：${item.title}`;
      q("#principle-step-text").textContent = "下方说明是职责和机制解释；选择一条教学路径，可按顺序追踪输入、输出或通知。";
      q("#principle-prev").disabled = true;
      q("#principle-next").disabled = false;
      q("#principle-next").textContent = "开始逐步追踪 →";
      all("[data-trace]").forEach((edge) => edge.classList.remove("is-tracing"));
      const detail = q("#principle-explorer");
      const y = detail.getBoundingClientRect().top;
      if (y < 0 || y > innerHeight - 100) detail.scrollIntoView({block:"start",behavior:"auto"});
    }
    all("[data-map-view]").forEach((button) => button.addEventListener("click", () => {
      showView(button.dataset.mapView);
      if (button.dataset.mapView === "principle") showTrace(0);
    }));
    all("[data-principle]").forEach((node) => {
      node.addEventListener("click", () => inspect(node.dataset.principle));
      node.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {event.preventDefault();inspect(node.dataset.principle);}
      });
    });
    all("[data-principle-trace]").forEach((button) => button.addEventListener("click", () => {
      path = button.dataset.principleTrace;
      pressed("[data-principle-trace]", button);
      showTrace(0);
    }));
    q("#principle-prev").addEventListener("click", () => showTrace(position-1));
    q("#principle-next").addEventListener("click", () => showTrace(guided ? position+1 : 0));
    all("[data-map-route]").forEach((button) => button.addEventListener("click", () => {
      const relay = button.dataset.mapRoute === "relay";
      pressed("[data-map-route]", button);
      map.querySelector('[data-principle="transport"] .ov-text tspan').textContent = relay ? "中继转发密文" : "可行时直连";
      q("#map-route-note").textContent = relay
        ? "当前示意为密文中继。官方称中继无工作内容解密密钥；账号与连接元数据仍存在。没有抓包或建立真实连接。"
        : "当前示意为可行时直连。实际路径由网络条件与产品实现决定；没有发起真实连接。";
    }));
  }

  all("[data-module]").forEach((button) => button.addEventListener("click", () => {
    const module = data.modules.find((item) => item[0] === button.dataset.module);
    if (!module) return;
    pressed("[data-module]", button);
    const detail = q("#module-detail");
    detail.querySelector(".overline").textContent = module[2];
    detail.querySelector("h3").textContent = module[1];
    detail.querySelector("p").textContent = module[3];
    detail.querySelector("small").textContent = module[4];
  }));

  const outputs = [
    "等待选择已授权电脑…\n本页没有真实远程连接。",
    "[教学示意] 身份与连接确认\n路径：直连 / 必要时中继\n内容通道：设备间加密",
    "> 请运行测试并说明结果。\n输入送往电脑上的终端。\n这是构造示例，没有执行命令。",
    "[模拟] Agent读取任务\n[模拟] 调用测试工具\n[模拟] 输出运行结果…\n实际执行位置：目标电脑",
    "[模拟输出] 测试结果已返回\n文字 / 颜色 / 光标 → 控制端渲染\n请查阅真实日志与产物。",
    "[模拟状态] done / blocked\n[模拟] 系统推送 → 手机\n用户阅读结果并独立验收。"
  ];
  let step = 0;
  function showStep(index) {
    step = Math.max(0, Math.min(data.steps.length - 1, index));
    const item = data.steps[step];
    q("#step-count").textContent = `步骤 ${String(step + 1).padStart(2, "0")} / 06`;
    q("#step-title").textContent = item[1];
    q("#step-body").textContent = item[2];
    q("#step-note").textContent = item[3];
    q("#terminal-output").textContent = outputs[step];
    pressed("[data-step]", q(`[data-step="${step}"]`));
    q("#step-prev").disabled = step === 0;
    q("#step-next").disabled = step === data.steps.length - 1;
  }
  all("[data-step]").forEach((button) => button.addEventListener("click", () => showStep(Number(button.dataset.step))));
  q("#step-prev").addEventListener("click", () => showStep(step - 1));
  q("#step-next").addEventListener("click", () => showStep(step + 1));

  const failures = {
    phone: "产品说明：电脑持续运行时，手机离开后终端会话可以继续；重新连接是否完整补齐输出仍待实测。",
    sleep: "系统机制推导：电脑休眠时，执行与网络可能暂停。唤醒后的服务、连接与会话恢复需要逐项测试；锁屏与休眠是不同事件。",
    service: "实现依赖：Companion退出后远程入口中断。独立tmux会话可能继续，但产品怎样重新发现并附着这些会话尚未确认。",
    restart: "系统机制：机器重启或Agent退出会结束相应活进程。继续任务需要原生历史续接、检查点或重新启动；手机重连无法自动恢复已结束进程。"
  };
  q("#failure-select").addEventListener("change", (event) => {q("#failure-result").textContent = failures[event.target.value];});

  all("[data-route]").forEach((button) => button.addEventListener("click", () => {
    pressed("[data-route]", button);
    const relay = button.dataset.route === "relay";
    const path = q("#route-path");
    path.replaceChildren();
    const parts = relay ? ["控制端", "⇄ 密文 ⇄", "中继", "⇄ 密文 ⇄", "目标电脑"] : ["控制端", "⇄ 加密内容 ⇄", "目标电脑"];
    parts.forEach((text, index) => {
      const element = document.createElement(index % 2 ? "b" : "span");
      element.textContent = text;
      if (relay && index === 2) element.className = "relay-node";
      path.append(element);
    });
    q("#route-explanation").textContent = relay ? "官方路径：中继转发设备间密文。官方称它没有工作内容解密密钥；平台仍需要身份、在线与连接元数据。尚未独立抓包验证。" : "官方路径：设备之间直接通信。可行性取决于网络条件；具体建立算法未公开。";
  }));

  all("[data-evidence-filter]").forEach((button) => button.addEventListener("click", () => {
    pressed("[data-evidence-filter]", button);
    const kind = button.dataset.evidenceFilter;
    let count = 0;
    all("[data-evidence-kind]").forEach((row) => {
      const shown = kind === "all" || row.dataset.evidenceKind === kind;
      row.hidden = !shown;
      if (shown) count += 1;
    });
    q("#evidence-count").textContent = `显示 ${count} 项研究记录`;
  }));
  q("#print-button").addEventListener("click", () => window.print());
  const links = all(".reading-nav nav a");
  const sections = all(".research-section");
  let scheduled = false;
  function markReadingPosition() {
    scheduled = false;
    const threshold = innerWidth <= 860 ? 110 : 90;
    let current = sections[0];
    for (const section of sections) {
      if (section.getBoundingClientRect().top <= threshold) current = section;
      else break;
    }
    links.forEach((link) => {
      const active = link.getAttribute("href") === `#${current.id}`;
      link.classList.toggle("active", active);
      if (active) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  }
  function scheduleReadingPosition() {
    if (!scheduled) {
      scheduled = true;
      requestAnimationFrame(markReadingPosition);
    }
  }
  window.addEventListener("scroll", scheduleReadingPosition, { passive: true });
  window.addEventListener("resize", scheduleReadingPosition);
  markReadingPosition();
})();
