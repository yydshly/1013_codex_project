"use strict";

const flowSteps = [
  {
    title: "系统路由把流量交给客户端",
    description: "应用生成 IP 包，操作系统按路由把需要经过 VPN 的流量交给 WireGuard 虚拟接口。",
    note: "默认全流量配置：AllowedIPs = 0.0.0.0/0, ::/0",
    nodes: ["client"], edges: [], reverse: []
  },
  {
    title: "双方握手，认证并协商会话密钥",
    description: "没有有效会话时，客户端发送 UDP 握手请求。服务器验证已登记的密钥身份，返回握手响应，双方派生收发会话密钥。",
    note: "信任关系由配置预先建立；已有有效会话时不重复此步骤。",
    nodes: ["client", "server"], edges: ["tunnel"], reverse: []
  },
  {
    title: "客户端加密，服务器验证与解密",
    description: "客户端把整个内部 IP 包认证加密，封装在外部 IP / UDP / WireGuard 消息中。服务器验证、防重放、解密，并检查内部源 IP 是否属于这个客户端。",
    note: "外层目标是 VPN 服务器，内层目标仍是网站；公钥绑定内部源 IP，例如 10.7.0.2/32。",
    nodes: ["client", "server"], edges: ["tunnel"], reverse: []
  },
  {
    title: "服务器转发，通过 NAT 访问网站",
    description: "Linux 网络栈处理解密后的 IP 包，通过路由、转发和 NAT 将请求送到目标网站。",
    note: "网关解开 WG 层；HTTPS 的 TLS 仍加密，通常不终止内部 TCP / TLS 连接。",
    nodes: ["server", "website"], edges: ["internet"], reverse: []
  },
  {
    title: "网站响应回到服务器",
    description: "网站将响应发回服务器。Linux 通过反向 NAT 恢复客户端内部目的地址，把返回包交给 WireGuard 接口。",
    note: "返回路径依赖服务器路由、防火墙和 NAT 配置正确。",
    nodes: ["server", "website"], edges: ["internet"], reverse: ["internet"]
  },
  {
    title: "服务器加密返回，客户端解密",
    description: "服务器按内部目的 IP 找到对应客户端 peer，用会话密钥加密后通过 UDP 返回。客户端验证并解密，将内部包交还本机网络栈。",
    note: "应用继续处理自己的业务协议；隧道负责安全传输内部 IP 包。",
    nodes: ["client", "server"], edges: ["tunnel"], reverse: ["tunnel"]
  }
];

let currentStep = 0;
const stepButtons = Array.from(document.querySelectorAll(".flow-step"));
const previousButton = document.getElementById("flow-prev");
const nextButton = document.getElementById("flow-next");

function renderStep(index) {
  currentStep = Math.max(0, Math.min(flowSteps.length - 1, index));
  const step = flowSteps[currentStep];
  document.getElementById("flow-count").textContent = `${String(currentStep + 1).padStart(2, "0")} / 06`;
  document.getElementById("flow-title").textContent = step.title;
  document.getElementById("flow-description").textContent = step.description;
  document.getElementById("flow-note").textContent = step.note;
  stepButtons.forEach((button, position) => {
    const selected = position === currentStep;
    button.classList.toggle("selected", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
  document.querySelectorAll("[data-node]").forEach(node => {
    node.classList.toggle("active", step.nodes.includes(node.dataset.node));
  });
  document.querySelectorAll("[data-edge]").forEach(edge => {
    edge.classList.toggle("active", step.edges.includes(edge.dataset.edge));
    edge.classList.toggle("reverse", step.reverse.includes(edge.dataset.edge));
  });
  previousButton.disabled = currentStep === 0;
  nextButton.disabled = currentStep === flowSteps.length - 1;
}

stepButtons.forEach(button => button.addEventListener("click", () => renderStep(Number(button.dataset.step))));
previousButton.addEventListener("click", () => renderStep(currentStep - 1));
nextButton.addEventListener("click", () => renderStep(currentStep + 1));
renderStep(0);

const packetExamples = {
  tcp: {
    protocol: "TCP", content: "TLS / HTTPS 数据",
    description: "以使用 TCP 的 HTTPS 请求为例：内部 TCP 负责自身的排序与重传，外层 WireGuard 始终通过 UDP 发送。"
  },
  udp: {
    protocol: "UDP", content: "普通 DNS 查询",
    description: "以普通 UDP DNS 查询为例：内部 UDP 包被封装进 WG 加密隧道，内外两层端口与用途不同。到 VPN 服务器解封装后，普通 DNS 仍是明文；后续保护取决于 DNS 自身采用的协议。"
  }
};
document.querySelectorAll("[data-packet]").forEach(button => {
  button.addEventListener("click", () => {
    const example = packetExamples[button.dataset.packet];
    document.getElementById("inner-protocol").textContent = example.protocol;
    document.getElementById("inner-content").textContent = example.content;
    document.getElementById("packet-description").textContent = example.description;
    document.querySelectorAll("[data-packet]").forEach(other => {
      const selected = other === button;
      other.classList.toggle("selected", selected);
      other.setAttribute("aria-pressed", String(selected));
    });
  });
});

const sections = Array.from(document.querySelectorAll("main > .section"));
const navigation = Array.from(document.querySelectorAll(".nav-link, .mobile-nav a"));
let scrollScheduled = false;
function updateNavigation() {
  const offset = Math.min(200, window.innerHeight * 0.3);
  let current = sections[0].id;
  sections.forEach(section => {
    if (section.getBoundingClientRect().top <= offset) current = section.id;
  });
  navigation.forEach(link => {
    const selected = link.hash === `#${current}`;
    link.classList.toggle("active", selected);
    if (selected) link.setAttribute("aria-current", "location");
    else link.removeAttribute("aria-current");
  });
  scrollScheduled = false;
}
window.addEventListener("scroll", () => {
  if (!scrollScheduled) {
    scrollScheduled = true;
    window.requestAnimationFrame(updateNavigation);
  }
}, { passive: true });
window.addEventListener("resize", updateNavigation);
updateNavigation();
