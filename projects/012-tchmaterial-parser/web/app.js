"use strict";

const scenarios = {
  single: {
    label: "官网通常足够",
    title: "偶尔获取一两本，直接使用官网",
    description: "先确认学校用书，在官网阅读或按其提供的方式获取。少量需求时，安装工具和设置凭据未必更省事。",
    caution: "核对年级、学科、上下册、出版社和修订版次。工具也不会替你确认学校采用的版本。"
  },
  semester: {
    label: "批量整理更有价值",
    title: "准备小学整学期，集中获取与归档",
    description: "选好多个学科的教材和对应版本，一次集中选择或输入链接。程序统一排队，按标题命名、按学段 / 学科 / 版本分类。",
    caution: "先用少量资源试下载并抽查。自动目录不保证包含年级、学期等所有维度，长期保存时补上来源与版本登记。"
  },
  compare: {
    label: "资料获取入口",
    title: "比较同学科教材，先把不同版本找齐",
    description: "获取同年级、同学科、相应册次的不同版本，保留来源与版次后，人工比较目录、章节和教学安排。",
    caution: "工具不会自动比较知识点或判断质量；不同教材的册次、修订年份和编写体系也要核对。"
  },
  teaching: {
    label: "关联文件获取",
    title: "备课与听力学习，把相关资料放在一起",
    description: "教材解析会尝试获取配套音频；受支持的课程或备课页面可以通过链接解析关联的课件、导学案和教学设计等文件。",
    caution: "默认浏览列表主要显示教材。解析范围取决于已适配页面、实际关联文件和授权；课程进度以学校与教师安排为准。"
  }
};

const steps = [
  ["选择教材，或粘贴多个页面链接", "程序中的教材列表可以批量勾选，与链接输入框同步。其他受支持的资源，可以每行粘贴一个页面链接。", "待处理的资源页面链接列表"],
  ["识别页面类型，提取资源编号", "读取链接里的 contentId、resourceId、activityId 或 courseId，判断教材、课程、专题或备课类型，决定使用哪个平台接口。", "资源类型与对应编号"],
  ["向平台请求 JSON 资源信息", "用编号请求平台详情，获得资源标题、分类标签、关联文件，以及 ti_items 中的格式、存储位置等字段。", "资源元信息与候选文件"],
  ["选择文档源文件和音频播放文件", "文档优先使用源文件；音频按平台播放器的规则选择播放地址。课程包展开关联资源，批量解析按文件地址去重。", "标题、格式、实际文件地址与分类"],
  ["携带认证信息，分块下载", "部分资源需要有效凭据；源码针对地址生成签名、有限并发下载，并处理部分错误。先写临时文件，按条件检查传输大小。", "尚未成为正式成品的临时文件"],
  ["命名、分类、写入书签并保存", "按标题命名，批量时依据学段 / 学科 / 版本标签建立目录；有有效目录映射且开启选项时写入 PDF 书签，再替换为正式文件。", "你选择的本地文件与目录"]
];

const scenarioButtons = Array.from(document.querySelectorAll("[data-scenario]"));
scenarioButtons.forEach(function (button) {
  button.addEventListener("click", function () {
    const data = scenarios[button.dataset.scenario];
    scenarioButtons.forEach(function (item) {
      const selected = item === button;
      item.classList.toggle("selected", selected);
      item.setAttribute("aria-pressed", String(selected));
    });
    document.getElementById("scenario-label").textContent = data.label;
    document.getElementById("scenario-title").textContent = data.title;
    document.getElementById("scenario-description").textContent = data.description;
    document.getElementById("scenario-caution").textContent = data.caution;
  });
});

const stepButtons = Array.from(document.querySelectorAll("[data-step]"));
stepButtons.forEach(function (button) {
  button.addEventListener("click", function () {
    const index = Number(button.dataset.step);
    const data = steps[index];
    stepButtons.forEach(function (item) {
      const selected = item === button;
      item.classList.toggle("selected", selected);
      item.setAttribute("aria-pressed", String(selected));
    });
    document.getElementById("step-number").textContent = String(index + 1).padStart(2, "0");
    document.getElementById("step-title").textContent = data[0];
    document.getElementById("step-description").textContent = data[1];
    document.getElementById("step-output").textContent = data[2];
  });
});

const versionForm = document.getElementById("version-form");
const versionChecks = Array.from(versionForm.querySelectorAll('input[type="checkbox"]'));
function updateVersionChecklist() {
  const count = versionChecks.filter(function (input) { return input.checked; }).length;
  document.getElementById("version-count").textContent = "已自行确认 " + count + " / 6 项";
  document.getElementById("version-message").textContent = count === 6
    ? "6 项已自行确认。请按学校要求和实物教材做最后核对；本页未自动验证一致性。"
    : "这是一份人工核对提醒。勾选只记录你的确认，不会自动识别或验证教材一致性。";
}
versionForm.addEventListener("change", updateVersionChecklist);
versionForm.addEventListener("reset", function () { setTimeout(updateVersionChecklist, 0); });

const registryColumns = [
  "学段", "年级", "学科", "册次", "出版社", "版别", "修订年份与版次", "印次",
  "ISBN（辅助核对）", "来源页面", "资源编号", "获取日期", "本地文件路径",
  "原始文件校验值（可选）", "书签加工文件校验值（可选）", "版本与文件抽查结果", "备注"
];
document.getElementById("download-registry").addEventListener("click", function () {
  const csv = "\uFEFF" + registryColumns.join(",") + "\r\n" + registryColumns.map(function () { return ""; }).join(",") + "\r\n";
  const blob = new Blob([csv], {type: "text/csv;charset=utf-8"});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "小学教材资料登记表.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(function () { URL.revokeObjectURL(url); }, 3000);
  document.getElementById("download-status").textContent = "已生成空白 CSV（17 列），请自行填写；不要记录登录凭据。";
});

const chapterLinks = Array.from(document.querySelectorAll(".chapter-nav a"));
if ("IntersectionObserver" in window) {
  const sections = chapterLinks.map(function (link) {
    return document.querySelector(link.getAttribute("href"));
  });
  const visibleSections = new Set();
  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) visibleSections.add(entry.target);
      else visibleSections.delete(entry.target);
    });
    const current = sections.find(function (section) { return visibleSections.has(section); });
    if (current) {
      chapterLinks.forEach(function (link) {
        const active = link.getAttribute("href") === "#" + current.id;
        link.classList.toggle("active", active);
        if (active) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
    }
  }, {rootMargin: "-8% 0px -65% 0px", threshold: 0});
  sections.forEach(function (section) { observer.observe(section); });
}
