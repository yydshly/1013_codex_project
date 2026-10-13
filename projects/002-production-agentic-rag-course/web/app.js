'use strict';

(function () {
  var stages = [
    {kicker: '第一步 / 获取资料', title: '先确定要研究什么，再收集资料。', description: '围绕明确主题收集论文、研究笔记或技术文档。上游自带 arXiv AI 论文采集，其他领域需要适配来源或增加文件导入入口。', input: '研究主题、资源入口、资料范围与文件。', output: '一批有来源、可读取的资料文件', check: '文件是否完整？资料是否覆盖想问的问题？来源能否回溯？', status: '上游有默认采集 · 新来源需适配'},
    {kicker: '第二步 / 整理文档', title: '让每份资料都能追溯来源与版本。', description: '先保留原文件与资料清单，再为后续处理整理标题、作者、日期和来源。自己的研究笔记要标注为笔记；模型生成的整理内容也要保留原文依据。', input: '原始文件、来源链接、版本或日期；农业场景还可补充作物与地区。', output: '资料清单 + 统一的文档信息结构', check: '来源能否访问？不同版本是否混在一起？缺失信息是否明确标注？', status: '上游保存论文元信息 · 新领域字段需适配'},
    {kicker: '第三步 / 解析切块', title: '把整份文件变成模型可用的片段。', description: 'Docling 提取 PDF 的文字与章节。切块优先保留章节，长章节拆分，短章节合并；没有有效章节时按词数与重叠切分。需要抽查内容完整性。', input: '资料文件与解析配置、切块规则。', output: '带文档来源、章节和位置的文本片段', check: '表格、公式和扫描页是否解析正确？片段是否丢失上下文？中文资料是否适配？', status: '源码存在 · 实际解析质量待验证'},
    {kicker: '第四步 / 建立知识库', title: '存好内容，再建立搜索结构。', description: 'PostgreSQL 保存论文内容与元信息。Jina 将片段转成向量，OpenSearch 保存片段原文、向量与来源，建立关键词和语义检索索引。', input: '解析片段、向量模型、索引配置与数据库连接。', output: '能够按问题检索的知识库', check: '片段数与向量数是否一致？维度是否匹配？每个片段能否找到原文？', status: '模型与索引维度匹配 · 更换后重新向量化'},
    {kicker: '第五步 / 检索与回答', title: '先找相关内容，再依据资料回答。', description: '问题通过关键词与向量检索寻找片段，RRF 合并两路排名。普通 RAG 把片段、问题和回答要求交给 Ollama；Agentic 额外检查相关性并尝试改写重试。', input: '真实问题、检索数量、检索方式与回答模型。', output: '相关资料；或带来源、可以核对的回答', check: '找到的内容是否相关？引用能否支持回答？资料不足时是否说明？请求参数是否生效？', status: '普通问答先验收 · Agentic 仍有链路缺口'},
    {kicker: '第六步 / 持续验证', title: '更新资料，也持续检查使用效果。', description: '新增资料重新处理并进入索引。用真实问题比较检索、引用与回答质量，再观察缓存、耗时和故障恢复。保存原始基线与改动后的结果。', input: '问题清单、原文标注、实际运行结果与新资料。', output: '可重复的验证记录 + 持续更新的知识库', check: '新资料是否可搜？缓存是否失效？重试增加了什么收益？核查后是否节省时间？', status: '当前未运行上游 · 后续已有 16 项验证任务'}
  ];

  var scenarios = {
    agriculture: {label: '农业与种植研究', shortLabel: '农业研究', kicker: '农业场景 / 适配方案', title: '建立一个农业论文资料助手。', description: '围绕作物、地区和研究主题收集论文，保留实验条件。用检索辅助理解已有研究，再回到原文核对。', adapt: '接入农业资料或增加本地 PDF 导入；调整领域校验；验证中文、表格与实验条件提取。', resources: '已获取的农业论文 PDF、研究笔记、可靠的技术资料。', metadata: '题名、作者、年份、来源、作物、地区与原文位置；缺失信息明确标注。', validation: '回答能否找到原文支持？不同地区与实验条件是否被混淆？表格数据是否完整？', question: '这些论文分别比较了哪些灌溉方式，实验条件有什么差异？', search: '找到灌溉试验相关内容，展示资料标题、章节和来源位置，由我们阅读与比较。', rag: '以检索到的片段为依据，整理实验条件、比较方法与观测结果，并附上来源供核对。这里仅说明输出结构，不给出实际种植建议。'},
    documents: {label: '产品与技术资料', shortLabel: '技术资料', kicker: '技术资料 / 适配方案', title: '建立一个产品与技术文档助手。', description: '把产品手册、技术规范和内部操作文档按产品与版本整理，围绕具体问题找到对应说明。', adapt: '增加文件或文档来源入口；适配章节和版本字段；调整领域规则与资料访问权限。', resources: '产品手册 PDF、技术规范、操作文档与已确认的维护记录。', metadata: '产品名称、文档版本、发布日期、适用型号、来源与章节；历史版本分别保留。', validation: '是否引用正确型号和版本？步骤能否在原文找到？资料访问是否符合使用者权限？', question: '这个版本的产品如何完成初始化，相关说明在哪一节？', search: '定位匹配产品与版本的文档，返回初始化相关章节与原文位置。', rag: '依据选中的版本资料整理初始化步骤，并附章节来源；资料缺失或版本不明确时，应说明。这里未连接真实产品文档。'},
    research: {label: 'GitHub 项目研究', shortLabel: '项目研究', kicker: '项目研究 / 适配方案', title: '让我们的项目研究资料可以被查询。', description: '把已收录项目的 README、研究笔记与技术说明统一整理，按实际问题查询实现与结论。', adapt: '接入仓库研究文档；保留项目与 commit；设置代码和技术文本的切块规则；调整领域范围。', resources: '项目 README、固定版本技术文档、我们的源码分析与复现记录。', metadata: '项目名、仓库链接、commit、文件位置、研究日期与验证状态。', validation: '是否把上游描述和实测结论混为一谈？来源是否对应固定版本？跨项目比较是否有资料依据？', question: '已收录项目各自解决什么问题，哪些流程可以衔接？', search: '返回相关项目的研究段落、固定版本和文档来源，由我们阅读、比较。', rag: '依据已有研究资料整理项目能力和衔接思路，分别标注已验证内容与待适配方案。与项目 001 的整合仍是后续探索。'}
  };

  var currentScenario = 'agriculture';
  var currentMode = 'search';
  var stageButtons = Array.from(document.querySelectorAll('[data-stage]'));
  var scenarioButtons = Array.from(document.querySelectorAll('[data-scenario]'));
  var modeButtons = Array.from(document.querySelectorAll('[data-mode]'));
  var planInputs = Array.from(document.querySelectorAll('[data-plan]'));
  var storageKey = 'rag-guide-002-plan-v1';
  var canStore = true;

  function put(id, value) {
    var element = document.getElementById(id);
    if (element) element.textContent = value;
  }

  function renderStage(index) {
    var stage = stages[index];
    if (!stage) return;
    stageButtons.forEach(function (button) {
      var selected = Number(button.dataset.stage) === index;
      button.classList.toggle('selected', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    put('stage-kicker', stage.kicker);
    put('stage-title', stage.title);
    put('stage-description', stage.description);
    put('stage-input', stage.input);
    put('stage-output', stage.output);
    put('stage-check', stage.check);
    put('stage-status', stage.status);
  }

  function renderExample() {
    var scenario = scenarios[currentScenario];
    modeButtons.forEach(function (button) {
      var selected = button.dataset.mode === currentMode;
      button.classList.toggle('selected', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    put('example-question', scenario.question);
    put('example-output-title', currentMode === 'search' ? '返回相关论文或文档与原文片段' : '依据检索资料整理回答，并附来源');
    put('example-output-copy', scenario[currentMode]);
  }

  function renderScenario(key) {
    if (!Object.prototype.hasOwnProperty.call(scenarios, key)) return;
    currentScenario = key;
    var scenario = scenarios[key];
    scenarioButtons.forEach(function (button) {
      var selected = button.dataset.scenario === key;
      button.classList.toggle('selected', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    put('scenario-eyebrow', scenario.kicker);
    put('scenario-title', scenario.title);
    put('scenario-description', scenario.description);
    put('scenario-adapt', scenario.adapt);
    put('scenario-resources', scenario.resources);
    put('scenario-metadata', scenario.metadata);
    put('scenario-validation', scenario.validation);
    renderExample();
  }

  function renderProgress(save) {
    var count = planInputs.filter(function (input) { return input.checked; }).length;
    put('plan-count', count + ' / ' + planInputs.length + ' 项已准备');
    document.getElementById('plan-progress-fill').style.width = (count / planInputs.length * 100) + '%';
    if (save && canStore) {
      var state = {};
      planInputs.forEach(function (input) { state[input.dataset.plan] = input.checked; });
      try { window.localStorage.setItem(storageKey, JSON.stringify(state)); }
      catch (error) { canStore = false; }
    }
    if (!canStore) {
      put('plan-storage-note', '当前浏览器未启用进度保存；本次勾选仍可下载成文档。');
    }
  }

  try {
    var saved = JSON.parse(window.localStorage.getItem(storageKey) || '{}');
    if (saved && typeof saved === 'object' && !Array.isArray(saved)) {
      planInputs.forEach(function (input) { input.checked = saved[input.dataset.plan] === true; });
    }
  } catch (error) {
    canStore = false;
  }

  stageButtons.forEach(function (button) {
    button.addEventListener('click', function () { renderStage(Number(button.dataset.stage)); });
  });
  scenarioButtons.forEach(function (button) {
    button.addEventListener('click', function () { renderScenario(button.dataset.scenario); });
  });
  modeButtons.forEach(function (button) {
    button.addEventListener('click', function () { currentMode = button.dataset.mode; renderExample(); });
  });
  planInputs.forEach(function (input) { input.addEventListener('change', function () { renderProgress(true); }); });

  document.getElementById('download-plan').addEventListener('click', function () {
    var scenario = scenarios[currentScenario];
    var lines = [
      '# RAG 项目使用路线：' + scenario.label,
      '',
      '研究项目：002 · Production Agentic RAG Course',
      '固定上游 commit：424a0eb99edf841994f2a9a053912b489d2a94ff',
      '当前状态：源码研究与使用计划；上游系统尚未复现。',
      '',
      '## 我们的共同理解',
      '',
      '论文是上游默认应用场景，完整 RAG 的方法和工程架构是我们的主要参考价值。',
      'RAG 先检索资料，再把相关片段放进本次模型输入；知识覆盖范围由已入库资料决定。',
      '从自己的问题与资料开始，依次获取、整理、解析、建库、问答和核对；新领域需要适配来源与规则。',
      '先验证普通 RAG，再探索 Agentic、专题报告、资料更新、本地向量化、权限与长文写作。',
      '扩展均为后续方向，实际收益用解析完整性、检索质量、引用支持、时间和成本衡量。',
      '',
      '## 选择的使用场景',
      '',
      scenario.description,
      '',
      '- 资料来源：' + scenario.resources,
      '- 文档信息：' + scenario.metadata,
      '- 适配工作：' + scenario.adapt,
      '- 验证重点：' + scenario.validation,
      '- 示例问题：' + scenario.question,
      '',
      '## 准备清单',
      '',
      '下面的勾选仅代表准备状态，不代表运行验证通过。',
      ''
    ];
    planInputs.forEach(function (input) {
      lines.push('- [' + (input.checked ? 'x' : ' ') + '] ' + input.parentElement.querySelector('span').textContent);
    });
    lines.push('', '## 六步流程', '');
    stages.forEach(function (stage, index) {
      lines.push((index + 1) + '. ' + stage.title, '   输入：' + stage.input, '   产物：' + stage.output, '   核对：' + stage.check, '');
    });
    lines.push('## 使用原则', '', '- 先验证真实资料的解析、检索和来源，再扩展 Agentic 与应用功能。', '- 比较回答质量与耗时，区分缓存命中、未命中和模型预热。', '- 农业等新领域需要适配资料入口与领域规则。', '- 保存原始基线、补丁和验证结果，区分方案与已验证能力。', '', '上游： https://github.com/jamwithai/production-agentic-rag-course/tree/424a0eb99edf841994f2a9a053912b489d2a94ff', '');
    var blob = new Blob([lines.join('\n')], {type: 'text/markdown;charset=utf-8'});
    var url = URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = 'RAG-使用路线-' + scenario.shortLabel + '.md';
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  });

  document.getElementById('print-guide').addEventListener('click', function () {
    var details = Array.from(document.querySelectorAll('details'));
    var initialStates = details.map(function (detail) { return detail.open; });
    var restore = function () {
      details.forEach(function (detail, index) { detail.open = initialStates[index]; });
      window.removeEventListener('afterprint', restore);
    };
    details.forEach(function (detail) { detail.open = true; });
    window.addEventListener('afterprint', restore);
    window.print();
  });

  var navLinks = Array.from(document.querySelectorAll('.nav-link'));
  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          navLinks.forEach(function (link) {
            var active = link.getAttribute('href') === '#' + entry.target.id;
            link.classList.toggle('active', active);
            if (active) link.setAttribute('aria-current', 'location');
            else link.removeAttribute('aria-current');
          });
        }
      });
    }, {rootMargin: '-15% 0px -65% 0px'});
    document.querySelectorAll('.page-section').forEach(function (section) { observer.observe(section); });
  }
  renderStage(0);
  renderScenario('agriculture');
  renderProgress(false);
})();
