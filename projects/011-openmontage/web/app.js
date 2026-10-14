"use strict";
// Original teaching interaction. Does not invoke upstream tools or any model.
const STAGES = [
  {key:"research",name:"研究",purpose:"助手研究主题，整理来源与讲解角度。",input:"主题、受众、目标与可选参考视频分析",output:"research_brief",tools:"助手自身的搜索与写作能力；此阶段 tools_available 为空",check:"研究简报需有来源、具体资料与不同角度。",gate:false,example:{research_brief:{topic:"GitHub 项目解读",audience:"希望理解用途的读者",source_notes:"此处为教学材料，非真实研究成果"}}},
  {key:"proposal",name:"方案",purpose:"把研究转成可行的内容方案、制作路径与费用估算。",input:"research_brief 与当前工具可用性",output:"proposal_packet、decision_log",tools:"助手做方案；参考驱动制作可增加 10–15 秒样片子阶段",check:"流程要求确认方案；选择运行时与交付方向，记录成本取舍。",gate:true,example:{proposal_packet:{selected_concept:"原理讲解",duration_seconds:60,render_runtime:"remotion",approval:"教学中等待确认"}}},
  {key:"script",name:"脚本",purpose:"按方案写旁白，安排内容、时长和声音表演方向。",input:"proposal_packet，可选 research_brief",output:"script",tools:"助手自身写作能力",check:"脚本格式、时长与内容来源需复核；默认要求确认。",gate:true,example:{script:{sections:[{id:"intro",text:"先说明这个项目解决的问题。",visual_intent:"标题与实际界面"}]}}},
  {key:"scene_plan",name:"分镜",purpose:"把脚本分配给镜头，明确时间、画面形式与所需素材。",input:"script，可选 proposal_packet",output:"scene_plan",tools:"助手设计镜头与表达方式",check:"镜头覆盖脚本，所需素材应有可行制作路径；默认要求确认。",gate:true,example:{scene_plan:{scenes:[{id:"s01",start_seconds:0,end_seconds:6,type:"hero_title",required_assets:["界面截图"]}]}}},
  {key:"assets",name:"素材",purpose:"根据分镜生成、检索或制作画面、配音与音乐。",input:"scene_plan、script，可选 proposal_packet",output:"asset_manifest 与实际素材文件",tools:"tts_selector、image_selector；可选视频、图解、代码、数学动画和音乐工具",check:"检查文件、旁白覆盖、费用和风格；默认要求确认。",gate:true,example:{asset_manifest:{assets:[{id:"screen01",scene_id:"s01",path:"示意/界面截图.png",source:"教学占位路径，文件不存在"}]}}},
  {key:"edit",name:"剪辑",purpose:"决定镜头顺序、素材截取、字幕、音乐与完整时间线。",input:"scene_plan、asset_manifest，可选 script",output:"edit_decisions",tools:"助手制定剪辑决策；本阶段 tools_available 为空",check:"引用素材、时间线、字幕与音乐配置需要核对；默认无人工确认门。",gate:false,example:{edit_decisions:{cuts:[{scene_id:"s01",asset_id:"screen01",in:0,out:6}],render_runtime:"remotion",subtitles:"教学示意"}}},
  {key:"compose",name:"合成",purpose:"将时间线、画面与音轨交给合成运行时，检查输出。",input:"edit_decisions、asset_manifest，可选 scene_plan",output:"render_report、final_review 和视频",tools:"video_compose、audio_mixer、hyperframes_compose 等流程允许的工具",check:"渲染前检查与成片检查；只有真实执行后才能判断制作成功。",gate:false,example:{render_report:{output_path:"示意/renders/final.mp4",verification:"教学未渲染，文件不存在"}}},
  {key:"publish",name:"导出",purpose:"整理成片、传播元信息与导出包。",input:"render_report、final_review，可选 proposal_packet",output:"publish_log 与导出目录",tools:"export_bundle；不表示已上传到任何社交平台",check:"默认要求确认；确认与导出记录需要对应实际操作。",gate:true,example:{publish_log:{status:"教学示意，未导出或发布",artifacts:["成片","元信息","封面概念"]}}}
];
const PATHS = {
  generated:{title:"模型生成素材 → 再组织成片",steps:["脚本与分镜","选择图片 / 视频 / 语音工具","生成与检查素材","剪辑决策","合成与渲染"],description:"助手负责内容和制作判断，专门模型生成图像、运动镜头或声音。多个素材再通过时间线形成视频，可以混入已有素材和代码画面。",boundary:"生成质量、人物/产品一致性、时长与费用取决于所接模型和实际重试；仍需试听与观看。",source:"selector"},
  footage:{title:"检索真实镜头 → 再组织成片",steps:["主题与镜头描述","搜索 / 建立候选库","CLIP 相似度与标签检索","选择并剪辑片段","调色、音乐与合成"],description:"真实素材路线从 Archive.org、NASA、Wikimedia 等来源与可选素材站收集候选镜头。标准路径建立可检索素材库；快速路径也可以直接搜索和检查缩略图。",boundary:"documentary-montage 标记为 beta。画面相似不证明事实；需要核对原始来源、许可与实际内容。",source:"documentary"},
  code:{title:"代码描述画面 → 渲染为视频帧",steps:["内容与数据","画面布局与动画设计","React / HTML / GSAP 代码","参数与资源校验","渲染并观看检查"],description:"通过 Remotion 或 HyperFrames，组织动态文字、图表、图解、分屏和角色动作。生成的代码和参数可以保存、修改与重复使用，适合清晰可控的技术讲解。",boundary:"代码来自助手的编程能力。需安装渲染依赖，处理时间线、字体、资源与音轨；特殊布局可能要自定义实现。",source:"remotion"}
};
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));
let filter = "all";
function filterCapabilities(){
  const query = $("#capability-search").value.trim().toLocaleLowerCase();
  const rows = $$("#capability-rows tr");
  let count = 0;
  rows.forEach((row)=>{
    const match = (filter === "all" || row.dataset.category === filter) && row.textContent.toLocaleLowerCase().includes(query);
    row.hidden = !match;
    if(match) count++;
  });
  $("#capability-count").textContent = "显示 " + count + " 项 / 共 " + rows.length + " 项能力";
  $("#empty-results").hidden = count !== 0;
}
$$("[data-filter]").forEach((button)=>button.addEventListener("click",()=>{
  filter = button.dataset.filter;
  $$("[data-filter]").forEach((item)=>{item.classList.toggle("active",item===button);item.setAttribute("aria-pressed",String(item===button));});
  filterCapabilities();
}));
$("#capability-search").addEventListener("input",filterCapabilities);
filterCapabilities();

let selected = 0;
const completed = new Set();
const waiting = new Set();
function node(tag, text, className){
  const item = document.createElement(tag);
  if(text !== undefined) item.textContent = text;
  if(className) item.className = className;
  return item;
}
function renderStage(message){
  const stage = STAGES[selected];
  const heading = node("h3",stage.name + " / " + stage.key);
  const purpose = node("p",stage.purpose);
  const fields = node("div",undefined,"stage-meta");
  [["输入",stage.input],["交付成果",stage.output],["执行者与工具",stage.tools],["阶段要求",stage.check]].forEach(([label,value])=>{
    const item = node("div");
    item.append(node("strong",label),node("p",value));
    fields.append(item);
  });
  const details = node("details");
  const sample = node("pre");
  sample.append(node("code",JSON.stringify(stage.example,null,2)));
  details.append(node("summary","查看交接材料的教学片段（非完整合法 schema）"),sample);
  const source = node("p",undefined,"source-note");
  const link = node("a","流程定义与状态检查依据"); link.href = "#source-checkpoint";
  source.append(link);
  $("#stage-detail").replaceChildren(heading,purpose,fields,details,source);
  $$("[data-stage]").forEach((button)=>{
    const index = Number(button.dataset.stage);
    button.setAttribute("aria-pressed",String(index === selected));
    button.classList.toggle("done",completed.has(index));
  });
  $("#finish-stage").disabled = completed.has(selected);
  $("#approve-stage").disabled = !waiting.has(selected);
  let status = "未完成";
  if(completed.has(selected)) status = "已完成（教学状态）";
  else if(waiting.has(selected)) status = "等待模拟确认";
  $("#gate-status").textContent = message || (stage.name + "：" + status + "。已完成 " + completed.size + " / 8 个教学阶段。");
}
function missingPredecessors(){return STAGES.slice(0,selected).filter((_,index)=>!completed.has(index)).map((item)=>item.name);}
$$("[data-stage]").forEach((button)=>button.addEventListener("click",()=>{selected=Number(button.dataset.stage);renderStage();}));
$("#finish-stage").addEventListener("click",()=>{
  const missing = missingPredecessors();
  if(missing.length){renderStage("无法推进：前置阶段尚未完成（" + missing.join("、") + "）。真实检查点代码会检查前置状态。");return;}
  const stage = STAGES[selected];
  if(stage.gate){waiting.add(selected);renderStage(stage.name + "：等待模拟确认。格式或生成结束不能替代必要确认。");return;}
  completed.add(selected);
  renderStage(stage.name + "：已模拟完成。可以查看下一阶段；没有执行任何真实制作工具。");
});
$("#approve-stage").addEventListener("click",()=>{
  if(!waiting.has(selected)) return;
  const missing = missingPredecessors();
  if(missing.length){renderStage("前置阶段未完成，无法确认推进。");return;}
  waiting.delete(selected);completed.add(selected);
  renderStage(STAGES[selected].name + "：已记录教学中的假设确认。可以选择下一阶段。");
});
$("#reset-flow").addEventListener("click",()=>{completed.clear();waiting.clear();selected=0;renderStage("教学状态已重置，从研究阶段开始。");});
renderStage();

function renderPath(key){
  const data = PATHS[key];
  const chain = node("div",undefined,"path-chain");
  data.steps.forEach((step,index)=>{if(index) chain.append(node("i","→"));chain.append(node("span",step));});
  const boundary = node("p",data.boundary,"small");
  const source = node("p",undefined,"source-note");
  const link = node("a","查看该路径的依据");link.href="#source-"+data.source;source.append(link);
  $("#path-detail").replaceChildren(node("h3",data.title),chain,node("p",data.description),boundary,source);
  $$("[data-path]").forEach((button)=>{const active=button.dataset.path===key;button.setAttribute("aria-pressed",String(active));button.classList.toggle("active",active);});
}
$$("[data-path]").forEach((button)=>button.addEventListener("click",()=>renderPath(button.dataset.path)));
renderPath("generated");
$("#print-page").addEventListener("click",()=>window.print());
if("IntersectionObserver" in window){
  const visible = new Map();
  const sections = $$(".chapter");
  const observer = new IntersectionObserver((entries)=>{
    entries.forEach((entry)=>visible.set(entry.target.id,entry.isIntersecting));
    const section = sections.find((item)=>visible.get(item.id));
    if(!section) return;
    $$(".contents nav a").forEach((link)=>{
      const active=link.hash==="#"+section.id;link.classList.toggle("current",active);
      if(active)link.setAttribute("aria-current","location");else link.removeAttribute("aria-current");
    });
  },{rootMargin:"-120px 0px -55% 0px",threshold:0});
  sections.forEach((section)=>observer.observe(section));
}
