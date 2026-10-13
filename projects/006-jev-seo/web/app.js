"use strict";
(() => {
  const catalogue = window.AUDIT_CATALOG;
  if (!catalogue) return;
  const $ = (id) => document.getElementById(id);
  const escape = (value) => String(value).replace(/[&<>"']/g, (s) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[s]));
  const categories = {crawl:"抓取与收录设置",onpage:"页面标题与结构",content:"内容量与重复",links:"链接与架构",structured:"结构化与分享",ai:"AI 爬虫政策",performance:"性能观测",security:"响应与安全配置"};
  const severity = {critical:"严重",high:"高",medium:"中",low:"低",info:"提示"};
  const effort = {1:"数小时",2:"约一天",3:"数天",4:"独立项目"};
  const scopeNames = {page:"单个页面",site:"网站入口",pair:"页面对"};
  const typeNames = {choice:"选项分类",score:"0–3 档评分",noul:"是 / 否"};

  const steps = {
    collect:{title:"从公开入口发现页面",description:"访问入口，读取 robots 和站点地图；沿站内链接发现页面，并保留响应、失败与重定向记录。",input:"公开网站地址、范围、页数与深度限制",method:"请求采集、内部链接发现、地图种子；动态渲染为可选",output:"本次实际抓取的页面与访问记录"},
    parse:{title:"把网页变成统一事实",description:"从 HTML 提取标题、描述、H1、正文、图片、链接、结构化信息和响应头，后续步骤不再各自猜网页状态。",input:"抓取到的 HTML 与响应记录",method:"解析文档，区分正文与导航，规范化网址",output:"标题、文本、链接、图片及其他页面字段"},
    rule:{title:"代码执行可确定的条件",description:"固定规则比较状态、存在性、数量、内容哈希和经验阈值，生成带网址、证据、修复建议与来源的问题。",input:"页面事实与站点探测信息",method:"例如 title 为空、链接目标 404、出现 noindex",output:"规则问题；经验和信息提示单独标记"},
    model:{title:"用我们的模型解释内容",description:"按网站、页面和页面对提出有明确标准的问题。返回分类、评分或是/否，附理由和原文；证据不足允许未知。",input:"页面正文摘录、网站背景、问题与标准",method:"当前聊天模型读材料，或兼容接口逐任务请求",output:"模型判断、理由、引文和任务状态"},
    report:{title:"校验材料后，生成可复核报告",description:"核实任务与快照一致、返回格式正确、引文原样存在，再结合规则问题整理整改先后，同时显示覆盖与遗漏。",input:"固定规则结果与模型判断",method:"指纹 / 格式 / 原文校验；严重程度与相对影响排序",output:"整改清单、来源、工作量、覆盖和限制"},
  };
  function stepMarkup(step){return `<span class="panel-label">当前步骤 / 可复用方法</span><h3>${step.title}</h3><p>${step.description}</p><dl class="step-facts"><div><dt>输入</dt><dd>${step.input}</dd></div><div><dt>做法</dt><dd>${step.method}</dd></div><div><dt>输出</dt><dd>${step.output}</dd></div></dl>`;}
  function setStep(key){
    document.querySelectorAll("[data-step]").forEach((button)=>{const active=button.dataset.step===key;button.setAttribute("aria-selected",String(active));button.tabIndex=active?0:-1;});
    $("step-panel").innerHTML=stepMarkup(steps[key]);$("step-panel").setAttribute("aria-labelledby",`step-${key}`);
  }
  document.querySelectorAll("[data-step]").forEach((button)=>button.addEventListener("click",()=>setStep(button.dataset.step)));
  setStep("collect");

  Object.entries(categories).forEach(([value,label])=>{const option=document.createElement("option");option.value=value;option.textContent=label;$("rule-category").append(option);});
  function ruleMarkup(rule,index){return `<details class="rule" data-rule="${escape(rule.id)}"><summary><span class="rule-number">${String(index+1).padStart(2,"0")}</span><span class="rule-heading"><strong>${escape(rule.title)}</strong><span class="rule-meta"><span>${categories[rule.category]}</span><span class="badge ${rule.severity}">${severity[rule.severity]}</span>${rule.heuristic?'<span class="badge heuristic">经验规则</span>':""}<code>${escape(rule.id)}</code></span></span></summary><div class="rule-body"><dl><dt>触发条件</dt><dd>${escape(rule.condition)}</dd><dt>处理思路</dt><dd>${escape(rule.fix)}</dd><dt>如何理解</dt><dd>${escape(rule.limit)}</dd><dt>参考工作量</dt><dd>${effort[rule.effort]}，来自上游建议；以实际网站为准。</dd></dl><div class="rule-links"><a href="${escape(rule.reference)}" target="_blank" rel="noopener noreferrer">参考依据 ↗</a><a href="${escape(rule.source)}" target="_blank" rel="noopener noreferrer">上游代码 ↗</a></div></div></details>`;}
  function renderRules(all=false){
    const query=$("rule-search").value.trim().toLocaleLowerCase();const category=$("rule-category").value;const kind=$("rule-kind").value;
    const rules=catalogue.rules.filter((rule)=>all||((category==="all"||category===rule.category)&&(kind==="all"||kind==="heuristic"&&rule.heuristic||kind==="info"&&rule.severity==="info"||kind==="fact"&&!rule.heuristic&&rule.severity!=="info")&&[rule.id,rule.title,rule.condition,rule.fix,rule.limit,categories[rule.category]].join(" ").toLocaleLowerCase().includes(query)));
    $("rule-list").innerHTML=rules.length?rules.map((rule)=>ruleMarkup(rule,catalogue.rules.indexOf(rule))).join(""):'<p class="empty-results">没有匹配的规则。可以清除筛选，或使用其他关键词。</p>';
    $("rule-count").textContent=`显示 ${rules.length} / ${catalogue.rules.length} 条规则 · 条件以固定版本源码为准`;
  }
  $("rule-search").addEventListener("input",()=>renderRules());$("rule-category").addEventListener("change",()=>renderRules());$("rule-kind").addEventListener("change",()=>renderRules());
  $("expand-rules").addEventListener("click",()=>document.querySelectorAll(".rule").forEach((detail)=>detail.open=true));
  $("collapse-rules").addEventListener("click",()=>document.querySelectorAll(".rule").forEach((detail)=>detail.open=false));
  $("reset-rules").addEventListener("click",()=>{$("rule-search").value="";$("rule-category").value="all";$("rule-kind").value="all";renderRules();});
  renderRules();

  let currentScope="page",currentQuestion="page_type";
  function questionMarkup(question){return `<span class="panel-label">${scopeNames[question.scope]} / ${typeNames[question.type]}</span><h3>${escape(question.title)}</h3><p>${escape(question.purpose)}</p><code class="qid">${escape(question.id)}</code><ul class="criteria">${question.criteria.map((criterion)=>`<li><span class="criterion-value">${escape(question.type==="noul"?(criterion.value==="true"?"是":"否"):criterion.value)}</span><span>${escape(criterion.label)}</span></li>`).join("")}</ul><div class="question-null"><b>证据不足 → 未知（null）</b><br>每个非空判断需要理由与原文引文，仍待人工复核。</div><p style="margin-top:18px;margin-bottom:0"><a class="text-link" href="${question.source}" target="_blank" rel="noopener noreferrer">查看原问题与标准 ↗</a></p>`;}
  function renderQuestions(scope,id){
    currentScope=scope;const questions=catalogue.questions.filter((question)=>question.scope===scope);currentQuestion=id||questions[0].id;
    document.querySelectorAll("[data-scope]").forEach((button)=>button.setAttribute("aria-pressed",String(button.dataset.scope===scope)));
    $("question-list").innerHTML=questions.map((question)=>`<button class="question-item" data-question="${question.id}" aria-pressed="${question.id===currentQuestion}">${escape(question.title)}</button>`).join("");
    $("question-detail").innerHTML=questionMarkup(questions.find((question)=>question.id===currentQuestion));
  }
  document.querySelectorAll("[data-scope]").forEach((button)=>button.addEventListener("click",()=>renderQuestions(button.dataset.scope)));
  $("question-list").addEventListener("click",(event)=>{const button=event.target.closest("[data-question]");if(button){renderQuestions(currentScope,button.dataset.question);document.querySelector(`[data-question="${currentQuestion}"]`).focus({preventScroll:true});}});
  renderQuestions("page");

  const evidenceCases={
    grounded:{title:"引文存在，保存为待复核判断",badge:"通过格式与原文校验",value:"具体性 0 / 3",reason:"文本主要是通用宣传，没有具体服务项目、数字或案例。",quote:"我们提供专业优质的服务",result:"引文确实来自样例正文，但评分是否合理仍需人工检查。"},
    fabricated:{title:"引文不存在，拒绝保存结果",badge:"未通过原文校验",value:"具体性 3 / 3",reason:"模型声称页面有详细交付案例。",quote:"十年经验，交付了 200 个网站",result:"样例材料中没有这句话。即使 JSON 合法，也不能作为有效审查结果。"},
    unknown:{title:"保留未知，不冒充低分",badge:"证据不足",value:"未知（null）",reason:"如果没有采集到正文，无法判断内容是否具体。",quote:"无引文",result:"这个例子演示缺少材料的情况。它不表示页面通过，也不应直接评为 0 分。"},
  };
  function setEvidence(key){const item=evidenceCases[key];document.querySelectorAll("[data-evidence]").forEach((button)=>button.setAttribute("aria-pressed",String(button.dataset.evidence===key)));$("evidence-result").innerHTML=`<span class="badge ${key==="fabricated"?"high":"info"}">${item.badge}</span><h3>${item.title}</h3><dl><dt>判断</dt><dd>${item.value}</dd><dt>理由</dt><dd>${item.reason}</dd><dt>引文</dt><dd>“${item.quote}”</dd></dl><p>${item.result}</p>`;}
  document.querySelectorAll("[data-evidence]").forEach((button)=>button.addEventListener("click",()=>setEvidence(button.dataset.evidence)));setEvidence("grounded");

  const scenarios=[
    {id:"pages",title:"自己的 GitHub Pages",subtitle:"作品集 / 项目介绍",heading:"检查一个项目，避免混入同域名其他站点",intro:"适合已经部署的作品集、研究演示和小型项目页面。",input:"部署网址，例如 https://name.github.io/project/，默认路径范围。",checks:"标题、描述、链接、图片说明、手机视口、canonical 和入口价值表达。",output:"定位缺失元信息和失效入口，判断访客能否理解项目与下一步。",steps:["核实输入的是部署地址，不是源码仓库","先采集重要页面，复核路径和覆盖","按问题修复后，新建目录重新采集"],limit:"不读取 GitHub 源码，也不验证 GitHub Actions 是否正确发布；根站点探测还需单独理解。"},
    {id:"launch",title:"上线前后自查",subtitle:"宣传页 / 服务页",heading:"发布前后，先排除明显可见问题",intro:"适合企业介绍、服务落地页和活动宣传页的发布复核。",input:"可公开访问的预发布或正式网址，以及希望被收录的页面。",checks:"HTTP 错误、意外 noindex、死链、标题与正文匹配、服务范围和联系方式。",output:"一份有来源与先后顺序的整改清单，供发布负责人复核。",steps:["区分预发布屏蔽策略与正式收录目标","检查规则事实和核心内容，不自动改动发布策略","复核联系方式与转化入口是否实际可用"],limit:"页面能打开不代表表单提交、支付或其他业务流程成功；需额外端到端测试。"},
    {id:"content",title:"文章与知识内容",subtitle:"博客 / 帮助中心",heading:"判断内容有没有真正回答问题",intro:"适合教程、文章、知识库和产品帮助文档。",input:"公开文章或文档入口，优先选择重要主题页面。",checks:"有用性、具体信息、来源与可信依据、开头重点、标题与摘要。",output:"指出泛泛表达、遗漏读者问题和缺乏具体例子的地方。",steps:["先明确目标读者与页面要解决的问题","把建议和原文逐项核对","由作者补充真实细节与来源，而非机械增加字数"],limit:"长文章可能截断；词数阈值不等于质量标准；代码示例的正确性需另测。"},
    {id:"product",title:"产品与服务介绍",subtitle:"SaaS / B2B / 电商",heading:"让访客看清产品、适用对象和下一步",intro:"适合软件功能页、服务说明、产品介绍与定价导读。",input:"核心产品页与入口页，保留网站业务背景。",checks:"价值说明、具体功能、交付或价格信息、信任依据、相关行动入口。",output:"发现宣传口号过多、说明模糊、标题失配和自然下一步缺失。",steps:["让内容判断符合产品页用途","复核案例和数字是否真实","结合用户任务决定是否需要定价、试用或联系"],limit:"不验证库存、订单、付款或后台价格逻辑，也不能保证转化率提升。"},
    {id:"migration",title:"网站改版或迁移",subtitle:"路径 / 域名 / 内容重组",heading:"比较可见结构变化，检查链接与跳转",intro:"适合域名迁移、页面重命名和内容结构调整。",input:"改版前后分别采集的公开网址与独立目录。",checks:"重定向链、链接目标、canonical、地图条目、404 与重复文本。",output:"人工对照新旧报告，确认关键入口是否仍能到达。",steps:["为前后版本保留不同快照","复核旧网址到新网址的合理对应","将变化和真实搜索表现分开观察"],limit:"当前没有自动跨报告 diff、长期监控或流量追踪；迁移成功还需搜索与运营数据。"},
    {id:"models",title:"比较自有模型",subtitle:"规则提取 / 模型实验",heading:"固定材料，比较判断的稳定性和成本",intro:"适合研究不同模型能否承担相同的网页语义审查。",input:"同一采集快照、问题和标准；每个模型保留独立结果目录。",checks:"选项一致性、原文引文、未知比例、误报漏报、输出失败和 token 用量。",output:"对模型的可用性形成证据，而不是只看一段漂亮建议。",steps:["准备人工标注的问题样本","使用相同材料，不把模型差异与采集差异混在一起","复核判断质量、遗漏和真实费用"],limit:"本次接口只做模拟测试；不继承原 Jev 的准确率或概率性质，也未实现自动评测排名。"},
    {id:"ai",title:"内容便于检索与引用",subtitle:"AI 搜索相关研究",heading:"检查表达与抓取政策，保持结果边界",intro:"适合探索内容是否便于人和机器理解。",input:"公开内容、结构化标记和站点抓取政策。",checks:"开头直达重点、可独立理解的陈述、主体信息、AI crawler 与可选 llms.txt。",output:"整理表达和可访问性改进点，明确哪些只属于政策提示。",steps:["用真实事实与来源补充内容","按业务政策选择允许的爬虫","用实际引用或搜索数据验证影响"],limit:"不是 AI 收录认证；Google AI 搜索没有额外专用文件要求，不能承诺被引用。"},
    {id:"backend",title:"寻找后端根因",subtitle:"能力边界 / 需要其他输入",heading:"公开网页只提供症状，根因需要另查",intro:"适合先记录异常发生在哪个网址，再进入独立代码或运行排查。",input:"这套工具只接收公开网址；深入排查另需源码、日志、接口与业务信息。",checks:"可记录 500、网络异常、跳转和页面不可达。",output:"可供后续定位的问题入口与时间点，不是后端代码审查结论。",steps:["复现并确认异常是否持续","提供对应代码与运行日志给其他审查流程","围绕鉴权、数据库与业务行为单独验证"],limit:"不发现未暴露的 SQL、权限或业务逻辑漏洞；响应正常也不能证明后端正确。"},
  ];
  function scenarioMarkup(scene){return `<span class="panel-label">${scene.subtitle}</span><h3>${scene.heading}</h3><p>${scene.intro}</p><dl><dt>需要输入</dt><dd>${scene.input}</dd><dt>检查重点</dt><dd>${scene.checks}</dd><dt>得到什么</dt><dd>${scene.output}</dd></dl><h4 style="font-size:12px;margin:0 0 10px;color:#648159">建议使用路线</h4><ul>${scene.steps.map((step)=>`<li>${step}</li>`).join("")}</ul><p class="scene-limit"><b>场景边界：</b>${scene.limit}</p>`;}
  $("scenario-list").innerHTML=scenarios.map((scene,index)=>`<button class="scenario-button" data-scenario="${scene.id}" aria-pressed="${index===0}"><strong>${scene.title}</strong><small>${scene.subtitle}</small></button>`).join("");
  function setScenario(id){document.querySelectorAll("[data-scenario]").forEach((button)=>button.setAttribute("aria-pressed",String(button.dataset.scenario===id)));$("scenario-detail").innerHTML=scenarioMarkup(scenarios.find((scene)=>scene.id===id));}
  $("scenario-list").addEventListener("click",(event)=>{const button=event.target.closest("[data-scenario]");if(button)setScenario(button.dataset.scenario);});setScenario("pages");

  function setModel(mode){document.querySelectorAll("[data-model]").forEach((button)=>{const active=button.dataset.model===mode;button.setAttribute("aria-selected",String(active));button.tabIndex=active?0:-1;});$("model-chat").hidden=mode!=="chat";$("model-api").hidden=mode!=="api";}
  document.querySelectorAll("[data-model]").forEach((button)=>button.addEventListener("click",()=>setModel(button.dataset.model)));
  document.querySelectorAll('[role="tablist"]').forEach((tablist)=>tablist.addEventListener("keydown",(event)=>{if(!["ArrowLeft","ArrowRight","Home","End"].includes(event.key))return;const tabs=[...tablist.querySelectorAll('[role="tab"]')];const index=tabs.indexOf(document.activeElement);if(index<0)return;event.preventDefault();const next=event.key==="Home"?0:event.key==="End"?tabs.length-1:(index+(event.key==="ArrowRight"?1:-1)+tabs.length)%tabs.length;tabs[next].click();tabs[next].focus({preventScroll:true});}));

  // Full standards and scenarios remain printable, even when selectors show one item.
  function addPrint(section,html){const node=document.createElement("div");node.className="print-only";node.innerHTML=html;$(section).append(node);}
  addPrint("principles",Object.values(steps).map((step)=>`<article class="print-step">${stepMarkup(step)}</article>`).join(""));
  addPrint("judgments",catalogue.questions.map((question)=>`<article class="print-question">${questionMarkup(question)}</article>`).join(""));
  addPrint("scenarios",scenarios.map((scene)=>`<article class="print-scenario">${scenarioMarkup(scene)}</article>`).join(""));
  let printState=null;
  window.addEventListener("beforeprint",()=>{printState={open:[...document.querySelectorAll("details[open]")],ruleIds:[...document.querySelectorAll(".rule[open]")].map((node)=>node.dataset.rule)};renderRules(true);document.querySelectorAll("details").forEach((detail)=>detail.open=true);});
  window.addEventListener("afterprint",()=>{if(!printState)return;renderRules();document.querySelectorAll("details").forEach((detail)=>detail.open=printState.open.includes(detail)||printState.ruleIds.includes(detail.dataset.rule));printState=null;});
  $("print-page").addEventListener("click",()=>window.print());
  const links=[...document.querySelectorAll(".nav-link")];
  if("IntersectionObserver" in window){const observer=new IntersectionObserver((entries)=>{for(const entry of entries){if(entry.isIntersecting){links.forEach((link)=>{const active=link.hash===`#${entry.target.id}`;link.classList.toggle("active",active);if(active)link.setAttribute("aria-current","location");else link.removeAttribute("aria-current");});}}},{rootMargin:"-18% 0px -68% 0px"});document.querySelectorAll("main>.section").forEach((section)=>observer.observe(section));}
})();
