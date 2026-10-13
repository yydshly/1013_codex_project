"use strict";

const sourceRef = "23c41333822fe8eca4c609b43119180af63ae4ac";
const sourceBase = `https://github.com/shadps4-emu/shadPS4/blob/${sourceRef}/`;
const sourceRows = [
  ["库的定位与普通用户入口", "README.md", "核心、QtLauncher、平台、启动方式与官方案例"],
  ["怎样加载与启动程序", "src/emulator.cpp", "读取参数、初始化运行环境、LoadModule 与 Execute"],
  ["怎样安排代码与数据", "src/core/module.cpp", "程序段映射、模块信息、符号和 CPU 修补"],
  ["怎样执行和连接函数", "src/core/linker.cpp", "系统模块、导入重定位、主线程及游戏入口"],
  ["为什么 CPU 仍需适配", "src/core/cpu_patches.cpp", "线程局部访问和部分指令行为的修补"],
  ["系统请求去了哪里", "src/core/libraries/kernel/file_system.cpp", "sceKernelOpen / Read / Write 的兼容实现"],
  ["怎样解析 GPU 命令", "src/video_core/amdgpu/liverpool.cpp", "PM4 命令解码、绘制与计算任务处理"],
  ["怎样翻译着色器", "src/shader_recompiler/recompiler.cpp", "GCN 解码、控制流、IR 和优化处理"],
  ["怎样建立主机绘图工作", "src/video_core/renderer_vulkan/vk_pipeline_cache.cpp", "TranslateProgram → EmitSPIRV → 主机着色器及管线缓存"],
  ["怎样处理共享数据", "src/video_core/buffer_cache/buffer_cache.cpp", "缓存、上传、下载与失效处理"],
  ["为什么接口存在仍不完整", "src/core/libraries/np/np_auth.cpp", "部分请求仍标记 STUBBED，需要查看实际实现"],
  ["上游许可证", "LICENSE", "GPL v2 文本；源码 SPDX 标注 GPL-2.0-or-later"]
];
const sourceTable = document.getElementById("source-table");
sourceRows.forEach(([question, path, meaning]) => {
  const tr = document.createElement("tr");
  const th = document.createElement("th"); th.scope = "row"; th.textContent = question;
  const td = document.createElement("td");
  const a = document.createElement("a"); a.href = sourceBase + path; a.target = "_blank"; a.rel = "noreferrer"; a.textContent = path; td.append(a);
  const detail = document.createElement("td"); detail.textContent = meaning;
  tr.append(th, td, detail); sourceTable.append(tr);
});
const officialCases = [["Bloodborne", "5sZgWyVflFM"], ["Dark Souls Remastered", "-3PA-Xwszts"], ["Red Dead Redemption", "Al7yz_5nLag"]];
officialCases.forEach(([title, video]) => {
  const a = document.createElement("a"); a.href = `https://www.youtube.com/watch?v=${video}`; a.target = "_blank"; a.rel = "noreferrer";
  a.append(document.createTextNode(title + " ↗")); const tag = document.createElement("span"); tag.textContent = "上游 README 引用的视频"; a.append(tag); document.getElementById("official-links").append(a);
});

const stages = [
  {owner:"加载器 / 链接器", title:"准备好程序，找到入口", text:"先将游戏代码、数据和模块安排进内存，连接它依赖的函数，再启动游戏主线程。", detail:"这里只展示加载概念。浏览器没有读取真实 ELF 文件。"},
  {owner:"电脑 CPU", title:"游戏代码开始执行", text:"CPU 执行游戏的主循环。在 x86-64 主机上，可以利用同一指令集的基础；模拟器还需处理平台差异。", detail:"游戏规则已经存在于程序中，模拟器提供它所需的运行条件。"},
  {owner:"系统兼容层 + 电脑操作系统", title:"接住一项系统请求", text:"游戏请求输入或文件等服务。shadPS4 使用兼容实现处理请求，再返回游戏期待的结果。", detail:"真正的实现还涉及路径、数据格式、错误码、句柄和调用约定。"},
  {owner:"游戏代码 + 图形命令处理", title:"形成要画的场景，提交图形任务", text:"CPU 计算动作和场景，把绘图命令与资源交给图形路径。shadPS4 解析 PS4 的 GPU 命令。", detail:"游戏决定画什么；模拟器解释这些任务应怎样在主机上执行。"},
  {owner:"着色器编译器 / 管线缓存", title:"为显卡准备可执行的小程序", text:"遇到新着色器时，将 GCN 指令转换为内部表示、处理和优化，输出 SPIR-V，建立主机绘图管线；符合条件的旧结果可复用。", detail:"着色器与图形命令是不同的对象，都会影响最终渲染。"},
  {owner:"Vulkan 渲染器 + 主机驱动 / GPU", title:"显卡执行转换后的工作", text:"主机 GPU 接收绘图工作。数据上传与等待顺序也必须正确，显卡才能读取最新模型和纹理并生成画面。", detail:"快与正确是不同问题，数据一致性也属于模拟器要解决的工作。"},
  {owner:"显示输出", title:"看到结果，再进入下一轮", text:"画面呈现到屏幕，游戏继续处理输入、计算和提交任务。实际的 CPU 与 GPU 工作可重叠执行。", detail:"教学过程把工作拆成顺序步骤，以便理解；真实运行通常有并发。"}
];
const scenarioDetails = {
  attack:{
    2:{title:"收到攻击键，并返回给游戏", text:"主机接收按键，输入实现把它转成游戏期待的手柄状态；游戏随后读到“攻击键按下”。"},
    3:{title:"计算挥剑、命中和伤害", text:"游戏代码计算角色动作与命中结果，随后提交绘制人物、剑和场景的命令。"},
    6:{title:"角色挥剑的画面显示出来", text:"示意人物完成挥剑。真实游戏还会继续播放动作、声音并处理下一次输入。"}
  },
  file:{
    2:{title:"把 PS4 文件请求接到主机文件", text:"游戏调用类似 sceKernelOpen / sceKernelRead 的接口；模拟器解释路径、标志和句柄，从电脑读取模型数据，并返回预期结果。"},
    3:{title:"游戏使用模型，提交绘制任务", text:"文件内容成为模型资源。游戏安排几何数据与纹理，并提交 GPU 所需的命令和资源。"},
    6:{title:"读到的模型出现在画面里", text:"从“文件中的字节”到“屏幕中的角色”，中间经过游戏解释数据和 GPU 绘制。"}
  },
  shader:{
    2:{title:"取得绘图所需的资源", text:"游戏通过系统服务准备数据。这里把内存和资源准备简化为一个系统阶段。"},
    3:{title:"提交带新光照效果的图形任务", text:"游戏第一次使用一种新的着色器或状态组合，图形路径需要准备对应的主机绘图工作。"},
    4:{title:"第一次使用：按需转换并保存结果", text:"着色器重编译器转换 GPU 指令，建立主机着色器和管线。满足缓存条件的后续任务可以复用已有结果。"},
    6:{title:"新的光照效果出现在画面里", text:"画面中出现示意光照。实际效果取决于指令、资源、格式和管线转换是否准确。"}
  }
};
let currentStep = 0;
let effectCount = 0;
let hasCachedShader = false;
let sceneFrame = 0;
const scenario = document.getElementById("scenario");
const fault = document.getElementById("fault");
const nextButton = document.getElementById("next-step");
const previousButton = document.getElementById("previous-step");
const traceList = document.getElementById("trace-list");
const canvas = document.getElementById("scene");
const ctx = canvas.getContext("2d");
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

function failurePoint() { return fault.value === "api" ? 2 : fault.value === "shader" ? 4 : 99; }
function describeStep(index) {
  const base = {...stages[index], ...(scenarioDetails[scenario.value][index] || {})};
  if (index === failurePoint()) {
    if (fault.value === "api") return {owner:"系统兼容层",title:"停在系统接口：请求无法正确完成",text:"本教学条件假设所需接口尚未实现。游戏无法得到正确数据或返回值，因此这条请求没有继续完成。",detail:"真实失败可能导致报错、等待或崩溃，须结合程序与日志判断。"};
    return {owner:"着色器编译器",title:"停在着色器：转换没有成功",text:"本教学条件假设遇到了无法正确转换的 GPU 指令或行为。主机着色器无法准备完成，当前画面任务不能按预期继续。",detail:"真实问题可能表现为编译失败、画面错误或跳过任务，须用日志和抓帧定位。"};
  }
  return base;
}

function drawScene(progress = 1) {
  if (!ctx) return;
  const complete = currentStep === 6 && failurePoint() > currentStep;
  const failed = currentStep === failurePoint();
  const w = canvas.width, h = canvas.height;
  ctx.clearRect(0,0,w,h);
  const sky = ctx.createLinearGradient(0,0,0,h); sky.addColorStop(0,"#dae4d4"); sky.addColorStop(1,"#eef1e3"); ctx.fillStyle=sky;ctx.fillRect(0,0,w,h);
  ctx.fillStyle="#c6d3bf";ctx.beginPath();ctx.moveTo(0,220);ctx.lineTo(130,118);ctx.lineTo(270,220);ctx.lineTo(430,150);ctx.lineTo(620,235);ctx.lineTo(w,175);ctx.lineTo(w,h);ctx.lineTo(0,h);ctx.fill();
  ctx.fillStyle="#a9bda1";ctx.fillRect(0,300,w,100);ctx.fillStyle="#bdd0b0";ctx.fillRect(0,300,w,8);
  for(let x=0;x<w;x+=70){ctx.strokeStyle="#9fb496";ctx.beginPath();ctx.moveTo(x,310);ctx.lineTo(x-70,400);ctx.stroke();}
  ctx.fillStyle="#a0b095";ctx.fillRect(84,174,36,126);ctx.fillStyle="#b7c6a9";ctx.fillRect(73,157,58,19);
  ctx.fillStyle="#83987b";ctx.fillRect(662,205,30,95);ctx.fillStyle="#afc49f";ctx.fillRect(652,189,50,18);
  const actorX=305, actorY=270;
  ctx.fillStyle="rgba(46,75,53,.14)";ctx.beginPath();ctx.ellipse(actorX,309,45,9,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#345641";ctx.fillRect(actorX-15,actorY-37,30,48);ctx.fillRect(actorX-14,actorY+8,10,29);ctx.fillRect(actorX+4,actorY+8,10,29);
  ctx.fillStyle="#dfc7a4";ctx.beginPath();ctx.arc(actorX,actorY-57,16,0,Math.PI*2);ctx.fill();ctx.fillStyle="#2e4634";ctx.fillRect(actorX-16,actorY-76,32,11);
  const theta = complete ? -1.0 + progress*1.3 : -.9;
  ctx.save();ctx.translate(actorX+12,actorY-24);ctx.rotate(theta);ctx.fillStyle="#dfc7a4";ctx.fillRect(0,-5,31,10);ctx.fillStyle="#527359";ctx.fillRect(29,-12,6,24);ctx.fillStyle="#f8faf1";ctx.fillRect(35,-4,72,8);ctx.restore();
  ctx.fillStyle="#687c59";ctx.beginPath();ctx.moveTo(470,300);ctx.lineTo(470,257);ctx.lineTo(498,238);ctx.lineTo(526,257);ctx.lineTo(526,300);ctx.closePath();ctx.fill();ctx.fillStyle="#dfe9c1";ctx.fillRect(479,263,9,7);ctx.fillRect(508,263,9,7);
  if(complete && scenario.value==="attack") {ctx.strokeStyle="#f4edb7";ctx.lineWidth=8;ctx.beginPath();ctx.arc(actorX+12,actorY-24,112,-1.0,-1.0+1.3*progress);ctx.stroke();ctx.fillStyle="#f4edb7";ctx.beginPath();ctx.arc(465,266,4+7*progress,0,Math.PI*2);ctx.fill();}
  if(complete && scenario.value==="shader") {const glow=ctx.createRadialGradient(actorX,245,5,actorX,245,130);glow.addColorStop(0,"rgba(248,232,155,.7)");glow.addColorStop(1,"rgba(248,232,155,0)");ctx.fillStyle=glow;ctx.fillRect(170,110,280,260);}
  ctx.font='17px "Microsoft YaHei", sans-serif';ctx.fillStyle="#45644d";ctx.textAlign="left";ctx.fillText("教学场景 · 不执行 PS4 程序",24,32);
  if(failed){ctx.fillStyle="rgba(240,237,224,.9)";ctx.fillRect(0,105,w,92);ctx.fillStyle="#9c473e";ctx.textAlign="center";ctx.fillText(fault.value==="api"?"请求停在系统兼容阶段":"请求停在着色器转换阶段",w/2,143);ctx.font='14px "Microsoft YaHei", sans-serif';ctx.fillText("更强的硬件不会自动补齐缺失实现",w/2,174);}
}
function animateScene() {
  cancelAnimationFrame(sceneFrame);
  if(prefersReducedMotion.matches || currentStep!==6 || failurePoint()<=currentStep){drawScene();return;}
  const start=performance.now();
  const frame=(now)=>{const fraction=Math.min(1,(now-start)/550);drawScene(fraction);if(fraction<1)sceneFrame=requestAnimationFrame(frame);};
  sceneFrame=requestAnimationFrame(frame);
}
function renderStep(animate=true) {
  const description=describeStep(currentStep);
  document.getElementById("step-owner").textContent=description.owner;
  document.getElementById("step-title").textContent=description.title;
  document.getElementById("step-description").textContent=description.text;
  document.getElementById("step-detail").textContent=description.detail;
  document.getElementById("step-count").textContent=`${currentStep+1} / 7`;
  nextButton.disabled=currentStep===6 || currentStep>=failurePoint();
  previousButton.disabled=currentStep===0;
  document.querySelectorAll(".flow-node").forEach(node=>{const stage=Number(node.dataset.stage);node.classList.toggle("done",stage<currentStep);node.classList.toggle("current",stage===Math.min(currentStep,5));node.classList.toggle("failed",stage===currentStep && currentStep===failurePoint());});
  document.getElementById("scene-state").textContent=currentStep===failurePoint()?"请求未完成":currentStep===6?"画面已呈现":`当前：${description.owner}`;
  traceList.replaceChildren();for(let i=0;i<=currentStep;i++){const li=document.createElement("li");li.textContent=`${describeStep(i).owner}：${describeStep(i).title}`;traceList.append(li);}
  if(animate)animateScene();else drawScene();
}
nextButton.addEventListener("click",()=>{if(currentStep<6 && currentStep<failurePoint()){currentStep++;renderStep();}});
previousButton.addEventListener("click",()=>{if(currentStep>0){currentStep--;renderStep();}});
function resetSteps(){currentStep=0;renderStep();}
scenario.addEventListener("change",resetSteps);fault.addEventListener("change",resetSteps);document.getElementById("replay").addEventListener("click",resetSteps);
renderStep(false);

document.getElementById("draw-effect").addEventListener("click",()=>{
  effectCount++;
  document.getElementById("cache-result").textContent=hasCachedShader?`第 ${effectCount} 次绘制：复用教学缓存中的着色器与管线 → 提交绘图。这个示例没有再次编译。`:`第 ${effectCount} 次绘制：缓存为空 → 转换着色器 → 建立管线 → 保存结果 → 提交绘图。`;
  hasCachedShader=true;
});
document.getElementById("clear-cache").addEventListener("click",()=>{hasCachedShader=false;effectCount=0;document.getElementById("cache-result").textContent="教学缓存已清空；下一次绘制会重新展示编译过程。";});
document.getElementById("quiz-form").addEventListener("submit",event=>{
  event.preventDefault();const data=new FormData(event.currentTarget);const result=document.getElementById("quiz-result");
  if(!["q1","q2","q3"].every(key=>data.has(key))){result.textContent="请先回答三个问题，再核对理解。";return;}
  const feedback=[];if(data.get("q1")!=="b")feedback.push("第 1 题：PS4 是设备，操作系统是其中的软件。");if(data.get("q2")!=="b")feedback.push("第 2 题：相同指令集还不够，还要兼容系统和图形行为。");if(data.get("q3")!=="a")feedback.push("第 3 题：游戏制作时的编译，与运行时的着色器重编译通常发生在不同阶段。");
  result.textContent=feedback.length?feedback.join(" "):"三个理解都正确：设备、运行环境和代码翻译是不同层次。";
});

document.getElementById("download-record").addEventListener("click",()=>{
  const columns=["记录日期","内容名称","内容来源与许可证","游戏编号或样例版本","游戏更新版本","模拟器版本","模拟器提交","操作系统","CPU","GPU","驱动版本","系统模块来源与版本","配置与环境变量","是否修改内容","启动到达阶段","图像结果","声音结果","运行时长","帧时间与测试方法","问题与最小复现","证据位置","未验证事项"];
  const blob=new Blob(["\ufeff"+columns.join(",")+"\r\n"],{type:"text/csv;charset=utf-8"});const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download="shadps4-runtime-record.csv";document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
});

function makeFact(text){const span=document.createElement("span");span.textContent=text;document.getElementById("runtime-facts").append(span);}
async function loadRuntime(){
  try{
    const response=await fetch("./assets/runtime-verification.json");if(!response.ok)throw new Error("运行记录未加载");const record=await response.json();
    const resultLabels={"verified-public-homebrew":"公开示例已实际跑通",pass:"通过",unsupported:"此版本不支持","failed-initial-attempt":"初次失败，后续组合成功"};
    document.getElementById("runtime-status").textContent=resultLabels[record.status]||record.status;
    document.getElementById("runtime-title").textContent=record.title;
    document.getElementById("runtime-summary").textContent=record.summary;
    const versions=record.versions||{},env=record.environment||{};
    makeFact(`运行版本：${versions.runtime_version||"见记录"} · ${(versions.runtime_commit||"").slice(0,7)}`);makeFact(`样例：${versions.sample||"见记录"}`);makeFact(`设备：${env.cpu||"见记录"}`);makeFact(`显卡：${env.gpu||"见记录"}`);
    (record.checks||[]).forEach(check=>{const tr=document.createElement("tr");[check.name,resultLabels[check.result]||check.result,check.evidence].forEach((value,i)=>{const cell=document.createElement(i===0?"th":"td");if(i===0)cell.scope="row";cell.textContent=value;tr.append(cell);});document.getElementById("runtime-checks").append(tr);});
    document.getElementById("runtime-limit").textContent=record.limit;
    document.getElementById("runtime-output").textContent=typeof record.output==="string"?record.output:JSON.stringify(record.output,null,2);
    (record.media||[]).forEach(media=>{
      const figure=document.createElement("figure");
      if(media.kind==="video"){const video=document.createElement("video");video.src=media.path;video.controls=true;video.preload="metadata";video.style.width="100%";figure.append(video);}else{const a=document.createElement("a");a.href=media.path;a.target="_blank";const img=document.createElement("img");img.src=media.path;img.alt=media.caption;img.loading="lazy";a.append(img);figure.append(a);}
      const caption=document.createElement("figcaption");caption.textContent=media.caption;figure.append(caption);document.getElementById("runtime-media").append(figure);
    });
  }catch(error){document.getElementById("runtime-status").textContent="记录未能加载";document.getElementById("runtime-summary").textContent="请通过本地 HTTP 预览或已发布站点访问，并检查运行记录文件。此状态不表示原生模拟器运行失败。";document.getElementById("runtime-output").textContent=String(error.message);}
}
loadRuntime();
const chapterLinks=[...document.querySelectorAll("#chapters a")];
if("IntersectionObserver" in window){const observer=new IntersectionObserver(entries=>{entries.filter(entry=>entry.isIntersecting).forEach(entry=>{chapterLinks.forEach(link=>{const active=link.hash===`#${entry.target.id}`;link.classList.toggle("active",active);if(active)link.setAttribute("aria-current","location");else link.removeAttribute("aria-current");});});},{rootMargin:"-15% 0px -65% 0px",threshold:0});chapterLinks.forEach(link=>{const section=document.querySelector(link.hash);if(section)observer.observe(section);});}
