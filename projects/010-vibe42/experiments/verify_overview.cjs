"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const {chromium} = require("playwright");
const project = path.resolve(__dirname,"..");
const url = process.argv[2] || "http://127.0.0.1:8775/010-vibe42/";
const checks=[];
async function exercise(page, viewport) {
  await page.goto(url,{waitUntil:"networkidle"});
  assert.equal(await page.locator("[data-principle]").count(),7);
  assert.equal(await page.locator("#principle-explorer").isVisible(),false);
  assert.equal(await page.locator("#understanding-map").getAttribute("viewBox"),"0 0 1400 2250");
  await page.locator('[data-map-view="principle"]').click();
  assert.equal(await page.locator("#principle-explorer").isVisible(),true);
  assert.equal(await page.locator("#understanding-map").getAttribute("viewBox"),"0 570 1400 565");
  for (const [key,title] of [["client","手机 / 浏览器"],["control","设备配对与授权"],["transport","加密连接"],["companion","Companion"],["session","PTY / 会话"],["agent","Agent 与工具"],["notify","状态与系统推送"]]) {
    await page.locator(`[data-principle="${key}"]`).click();
    assert.equal(await page.locator("#principle-title").innerText(),title);
    assert.match(await page.locator("#principle-step-count").innerText(),/自由查看/);
    assert.equal(await page.locator("#principle-prev").isDisabled(),true);
    assert.ok((await page.locator("#principle-boundary").innerText()).length>25);
  }
  checks.push({viewport,name:"完整图/原理区域切换、7节点与证据边界",status:"passed"});
  for (const [key,count,endNode] of [["input",6,"agent"],["output",5,"client"],["notice",5,"agent"]]) {
    await page.locator(`[data-principle-trace="${key}"]`).click();
    assert.equal(await page.locator("#principle-prev").isDisabled(),true);
    for(let i=1;i<count;i++) await page.locator("#principle-next").click();
    assert.match(await page.locator("#principle-step-count").innerText(),new RegExp(`0${count} / 0${count}`));
    assert.equal(await page.locator("#principle-next").isDisabled(),true);
    assert.equal(await page.locator(`[data-principle="${endNode}"]`).getAttribute("aria-pressed"),"true");
    await page.locator("#principle-prev").click();
    assert.equal(await page.locator("#principle-next").isDisabled(),false);
  }
  checks.push({viewport,name:"3条路径逐步追踪与首尾边界",steps:[6,5,5],status:"passed"});
  await page.locator('[data-map-route="relay"]').click();
  assert.match(await page.locator('[data-principle="transport"] .ov-text').textContent(),/中继转发密文/);
  assert.match(await page.locator("#map-route-note").innerText(),/没有抓包/);
  await page.locator('[data-map-route="direct"]').click();
  assert.match(await page.locator('[data-principle="transport"] .ov-text').textContent(),/可行时直连/);
  await page.locator('[data-principle="session"]').focus();
  await page.keyboard.press("Enter");
  assert.equal(await page.locator("#principle-title").innerText(),"PTY / 会话");
  await page.locator('[data-principle="agent"]').focus();
  await page.keyboard.press("Space");
  assert.equal(await page.locator("#principle-title").innerText(),"Agent 与工具");
  await page.locator("#principle-next").click();
  assert.match(await page.locator("#principle-step-count").innerText(),/01/);
  checks.push({viewport,name:"直连/中继、Enter/Space与自由查看后重新追踪",status:"passed"});
  const width=await page.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth}));
  assert.equal(width.document,width.viewport);
  await page.locator('[data-map-view="full"]').click();
  assert.equal(await page.locator("#principle-explorer").isVisible(),false);
  assert.match(await page.locator('[data-principle="transport"] .ov-text').textContent(),/直连 \/ 密文中继/);
  checks.push({viewport,name:"视图恢复与页面无横向溢出",width,status:"passed"});
}
(async()=>{
  const browser=await chromium.launch({headless:true});
  try {
    const page=await browser.newPage({viewport:{width:1440,height:1100},reducedMotion:"reduce",acceptDownloads:true});
    const errors=[];
    page.on("pageerror",e=>errors.push(e.message));
    page.on("console",m=>{if(m.type()==="error")errors.push(m.text())});
    page.on("requestfailed",r=>errors.push(`failed: ${r.url()}`));
    await exercise(page,1440);
    for(const format of ["svg","png"]){
      const event=page.waitForEvent("download");
      await page.locator(`.map-toolbar a[download="vibe42-understanding-overview.${format}"]`).click();
      const download=await event;
      const bytes=fs.readFileSync(await download.path());
      assert.equal(download.suggestedFilename(),`vibe42-understanding-overview.${format}`);
      if(format==="svg")assert.match(bytes.toString("utf8"),/远程控制Agent的能力/);
      else assert.equal(bytes.subarray(1,4).toString(),"PNG");
    }
    checks.push({name:"SVG与PNG实际下载",status:"passed"});
    await page.locator('[data-map-view="principle"]').click();
    await page.locator('[data-principle="agent"]').click();
    await page.locator('[data-map-route="relay"]').click();
    await page.locator(".map-toolbar").scrollIntoViewIfNeeded();
    await page.screenshot({path:path.join(project,"assets","05-overview-interaction-desktop.png")});
    await page.emulateMedia({media:"print"});
    assert.equal(await page.locator(".overview-print-image").isVisible(),true);
    assert.equal(await page.locator(".understanding-canvas").isVisible(),false);
    checks.push({name:"原理视图打印仍显示完整静态图",status:"passed"});
    await page.emulateMedia({media:"screen"});
    await page.setViewportSize({width:390,height:844});
    await exercise(page,390);
    await page.locator('[data-map-view="principle"]').click();
    await page.locator('[data-principle="session"]').click();
    await page.locator("#principle-explorer").scrollIntoViewIfNeeded();
    await page.screenshot({path:path.join(project,"assets","06-overview-interaction-mobile.png")});
    await page.setViewportSize({width:320,height:844});
    const measured=await page.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth}));
    assert.equal(measured.document,320);
    checks.push({name:"320px布局",measured,status:"passed"});
    const nojs=await browser.newContext({javaScriptEnabled:false});
    const staticPage=await nojs.newPage();
    await staticPage.goto(url,{waitUntil:"networkidle"});
    assert.match(await staticPage.locator("#understanding").textContent(),/可扩展方向|扩展：/);
    checks.push({name:"关闭JavaScript保留完整理解图",status:"passed"});
    assert.deepEqual(errors,[]);
    const result={date:new Date().toISOString(),browser:`Chromium ${browser.version()}`,scope:"原创理解图与教学交互；未运行真实产品",checks,errors};
    fs.writeFileSync(path.join(__dirname,"results","overview-check.json"),JSON.stringify(result,null,2)+"\n");
    console.log(JSON.stringify({checks:checks.length,errors:errors.length,browser:result.browser},null,2));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
