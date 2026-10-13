'use strict';

// All examples are authored teaching cases. This page never calls a model API.
const scenarios = {
  subtitle: {
    task: '把已经审核的导览字幕压缩到每条 30 字以内，保留地名和数字，不增加新知识。',
    background: '背景：原字幕与事实已提供。A / B 是待实测的执行模型候选。',
    judgment: '任务性质：仅改表达；无新推理；无联动修改。',
    route: '尝试 A', routeNote: 'A 能否合格，需要与 B 配对实测。',
    execution: '执行模型压缩字幕 → 检查字数、专名、数字与事实 → 不合格时记录失败，再按既定策略返工或升级。',
    methods: {
      rules: ['明确的任务标签，直接走固定规则。', '如果入口已经标明“已审核字幕压缩”，且有原文与长度要求，代码可直接选择 A；无需再让模型判断。'],
      jev: ['按标准判断：是否只改变表达？', '给 Jev 任务、必要背景，以及“事实和结论已给定，只改长度与措辞”的定义。预期判断是仅改表达；本地策略据此尝试 A。这个答案是教学预设。'],
      small: ['用有限字段返回任务性质。', '让小模型按相同标准返回“仅改表达=true，综合推理=false，联动=false”。代码验证字段后尝试 A。需要实测输出稳定性；不能预设其判断优于规则。']
    }
  },
  synthesis: {
    task: '设计一段新讲解：为什么新疆的山脉和盆地会影响绿洲分布与历史交通？把三份材料关联起来，列出证据。',
    background: '背景：三份材料已提供，尚无最终结论；需要核对材料、因果关系和来源。',
    judgment: '任务性质：需要跨材料综合推理；结论尚未给定。',
    route: '暂用 B', routeNote: '这是一条初始假设，A 也应参加配对测试。',
    execution: '执行模型组织材料与讲解 → 核对每个因果结论和来源 → 验收覆盖与准确性。判断器不撰写最终讲解。',
    methods: {
      rules: ['有明确任务类型时可以直接选 B。', '若入口已标记“新讲解设计 / 跨材料综合”，规则可选 B。仅按“为什么”等关键词判断容易漏掉改写或复杂表达，需要边界测试。'],
      jev: ['按定义识别“需要形成新结论”。', '把三份材料的必要摘要、任务和综合推理标准交给 Jev，询问是否需要关联不同来源。预设答案为“需要”，本地代码暂路由 B。真实判断表现待验证。'],
      small: ['按相同定义判断综合推理需求。', '提供材料摘要与标准，让小模型输出有限标签，必要时附简短依据。代码校验后选 B；不能因为它给出了理由，就认定标签或来源一定正确。']
    }
  },
  sync: {
    task: '修复暂停：音频停止时地图与镜头也停止；进入自由探索后，返回导览要从同一进度继续。',
    background: '背景：涉及共享进度、播放状态、自由控制和恢复逻辑；需要提供相关实现与复现步骤。',
    judgment: '任务性质：存在部件行为与共享状态的相互依赖。',
    route: '暂用 B', routeNote: '验收重点是联动是否正确，而非代码改动数量。',
    execution: '执行模型检查并修改代码 → 实际播放、暂停、自由探索、返回 → 验证音频、地图、镜头进度一致。',
    methods: {
      rules: ['固定联动任务可以按标签处理。', '若任务已经归类为“共享进度 / 暂停恢复”，规则直接选择 B；对于自由表述，只数文件、按钮或字数无法可靠判断相互依赖。'],
      jev: ['识别暂停、恢复与进度一致的依赖。', '提供当前状态、任务和联动定义，询问是否影响部件间行为或共享状态。预设判断为“有依赖”；代码暂选 B。相关上下文缺失时应先补充。'],
      small: ['结构化提取共享状态与依赖。', '小模型按标准标记“相互依赖=true”，可指出暂停、恢复和进度一致性。代码再路由 B，最终正确性仍需实际运行检查。']
    }
  },
  missing: {
    task: '继续完善一下，做得更好。',
    background: '背景：没有提供具体目标、当前阶段、相关材料和验收标准；无法判断需要什么能力。',
    judgment: '任务性质：信息不足，不能可靠应用路由标准。',
    route: '先补背景', routeNote: '执行模型能力更强，也不能自动补出真实意图。',
    execution: '补齐目标、当前状态、相关代码或材料与验收要求 → 再判断需求 → 路由并执行。',
    methods: {
      rules: ['检查必要字段是否齐全。', '自有流程可以先检查任务、材料与验收字段；不足就进入补信息流程。无需让模型猜测“完善”的含义。'],
      jev: ['判断器也需要知道真实任务。', '只发这句话，Jev 无法看到真正要修改的内容。自有方案应先补背景；上游默认路由通常只看当前请求，而不是完整项目与历史。'],
      small: ['允许输出“未知”，避免强制猜选。', '让小模型识别缺少目标与验收要求，返回“未知 / 背景不足”；不要强迫它一定输出 A 或 B。缺信息应由任务输入流程解决。']
    }
  }
};

let selectedScenario = 'subtitle';
let selectedMethod = 'rules';
const methodNames = { rules: '本地规则', jev: 'Jev', small: '便宜小模型' };
const write = (id, text) => { document.getElementById(id).textContent = text; };

function renderExample() {
  const item = scenarios[selectedScenario];
  const [title, description] = item.methods[selectedMethod];
  write('task-text', item.task);
  write('task-background', item.background);
  write('method-label', `如何判断 / ${methodNames[selectedMethod]}`);
  write('judge-title', title);
  write('judge-description', description);
  write('judge-output', item.judgment);
  write('route-result', item.route);
  write('route-note', item.routeNote);
  write('execution-text', item.execution);
  document.querySelectorAll('[data-scenario]').forEach(button => {
    const active = button.dataset.scenario === selectedScenario;
    button.classList.toggle('selected', active);
    button.setAttribute('aria-pressed', String(active));
  });
  document.querySelectorAll('[data-method]').forEach(button => {
    const active = button.dataset.method === selectedMethod;
    button.classList.toggle('selected', active);
    button.setAttribute('aria-pressed', String(active));
  });
}

document.querySelectorAll('[data-scenario]').forEach(button => {
  button.addEventListener('click', () => {
    selectedScenario = button.dataset.scenario;
    renderExample();
  });
});
document.querySelectorAll('[data-method]').forEach(button => {
  button.addEventListener('click', () => {
    selectedMethod = button.dataset.method;
    renderExample();
  });
});

function renderRubric() {
  const checked = name => document.getElementById(`criterion-${name}`).checked;
  let route, reason;
  if (!checked('context')) {
    route = '先补背景';
    reason = '缺少真实任务、材料或验收要求。先补信息，不能依靠判断器猜测。';
  } else if (checked('synthesis') || checked('dependency') || checked('risk')) {
    route = '暂用 B';
    const causes = [];
    if (checked('synthesis')) causes.push('综合推理');
    if (checked('dependency')) causes.push('相互依赖');
    if (checked('risk')) causes.push('较高错误代价');
    reason = `已识别${causes.join('、')}，初始策略暂用 B。若仍不确定，也不据此降级；模型映射需要配对实测。`;
  } else if (checked('uncertain')) {
    route = '保持默认模型';
    reason = '没有可靠证据支持降级。保留事先约定的默认模型，并记录未知原因。';
  } else if (checked('expression')) {
    route = '尝试 A';
    reason = '背景完整，明确只改表达，且没有综合推理、联动或高代价条件。';
  } else {
    route = '保持默认模型';
    reason = '没有落入已验证的便宜分支。先保持默认模型，补案例并修订标准。';
  }
  write('rubric-route', route);
  write('rubric-reason', reason);
}
document.querySelectorAll('.rubric-controls input').forEach(input => input.addEventListener('change', renderRubric));
document.getElementById('rubric-reset').addEventListener('click', () => {
  document.querySelectorAll('.rubric-controls input').forEach(input => {
    input.checked = ['criterion-context', 'criterion-expression'].includes(input.id);
  });
  renderRubric();
});

document.getElementById('download-evaluation').addEventListener('click', () => {
  const columns = [
    '任务ID', '数据集(开发/测试)', '任务类别', '输入与材料引用', '输入版本', '工具环境',
    '验收标准', '风险与延迟预算', 'A模型版本', 'B模型版本', '重复轮次',
    'A是否通过', 'B是否通过', 'A失败原因', 'B失败原因',
    '判断器版本', '标准版本', '策略版本', '标准期望标签', '判断器实际标签',
    '标准是否正确应用', '路由选择', '是否误降级', '最终是否通过',
    '判断费用', '全部执行费用', '重试升级费用', '缓存影响费用(勿重复计入)',
    '总费用', '总耗时秒', '人工返工分钟', '维护工时', '备注'
  ];
  const content = '\uFEFF' + columns.join(',') + '\r\n' + columns.map(() => '').join(',') + '\r\n';
  const url = URL.createObjectURL(new Blob([content], { type: 'text/csv;charset=utf-8' }));
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = '多模型路由验证记录表.csv';
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});

const navigation = [...document.querySelectorAll('.sidebar nav a')];
const sections = navigation.map(link => document.querySelector(link.getAttribute('href')));
function updateNavigation() {
  const threshold = window.innerWidth <= 820 ? 160 : 150;
  let active = sections[0];
  for (const section of sections) {
    if (section.getBoundingClientRect().top <= threshold) active = section;
  }
  navigation.forEach(link => {
    const selected = link.getAttribute('href') === `#${active.id}`;
    link.classList.toggle('active', selected);
    if (selected) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
}
let navigationQueued = false;
window.addEventListener('scroll', () => {
  if (navigationQueued) return;
  navigationQueued = true;
  requestAnimationFrame(() => { updateNavigation(); navigationQueued = false; });
}, { passive: true });
window.addEventListener('resize', updateNavigation);
renderExample();
renderRubric();
updateNavigation();
