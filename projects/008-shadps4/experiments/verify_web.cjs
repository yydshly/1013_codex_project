"use strict";
// End-to-end checks against the same static subpath used by the repository site.
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const {chromium} = require(process.env.SHAD_PLAYWRIGHT_MODULE || "playwright");
const root = path.resolve(__dirname, "..");
const base = process.env.SHAD_WEB_URL || "http://127.0.0.1:8773/008-shadps4/";
const resultDir = path.join(__dirname, "results");
const checks = [];
const errors = [];
const screenshots = [];
function check(name, evidence) { checks.push({name, result:"pass", evidence}); }
async function screenshot(page, filename, locator) {
  const destination = path.join(root, "assets", filename);
  if (locator) await locator.screenshot({path:destination, type:"jpeg", quality:88, style:".topbar{visibility:hidden!important}"});
  else await page.screenshot({path:destination, type:"jpeg", quality:88});
  screenshots.push({path:`assets/${filename}`, description:filename.includes("mobile") ? "390 像素宽手机布局的实际浏览器截图" : "静态子路径的实际浏览器截图"});
  fs.writeFileSync(destination.replace(/\.jpg$/, ".source.json"), JSON.stringify({date:"2026-10-14",source:"本仓库中文导读网页的实际 Playwright 浏览器截图",url:base,viewport:page.viewportSize(),original_content:"本仓库撰写的解释、教学代码与实测记录；原生图片来源另见 openorbis-graphics-live.source.json",capture:"浏览器内容；长章节截图隐藏浮动顶部导航以避免遮挡；未修改研究内容"},null,2)+"\n", "utf8");
}
(async () => {
  const browser = await chromium.launch({headless:true});
  const version = browser.version();
  const context = await browser.newContext({viewport:{width:1440,height:1000}, reducedMotion:"reduce", acceptDownloads:true});
  const page = await context.newPage();
  page.on("pageerror", error => errors.push(error.message));
  page.on("console", message => {if (message.type() === "error") errors.push(message.text());});
  page.on("requestfailed", request => errors.push(`${request.url()} ${request.failure()?.errorText}`));
  try {
    const response = await page.goto(base, {waitUntil:"networkidle"});
    assert.equal(response.status(), 200);
    await page.locator("#runtime-status").filter({hasText:"公开示例已实际跑通"}).waitFor();
    for (const resource of ["styles.css","app.js","assets/understanding-map.svg","assets/comprehensive-map.svg","assets/comprehensive-map.png","assets/favicon.svg","assets/runtime-verification.json","assets/openorbis-graphics-live.jpg"]) {
      const resourceResponse = await context.request.get(new URL(resource, base).href);
      assert.equal(resourceResponse.status(), 200, resource);
    }
    await page.locator(".overview figure img").evaluate(img => img.decode());
    assert.equal(await page.locator(".overview figure img").evaluate(img => img.naturalHeight), 3290);
    check("静态子路径与资源", "HTML、CSS、JavaScript、完整 SVG / PNG 总览、简化流程、图标、实测 JSON 与实机截图均返回 200；网页加载的是 1800×3290 完整总览图。");
    const anchorTargets = await page.locator("#chapters a").evaluateAll(links => links.map(link => link.hash));
    assert.equal(anchorTargets.length, 11);
    for (const hash of anchorTargets) assert.equal(await page.locator(hash).count(), 1, hash);
    assert.equal(await page.locator("#source-table tr").count(), 12);
    assert.equal(await page.locator("#official-links a").count(), 3);
    check("章节和来源", "11 个目录目标、12 行固定版本源码依据、3 个上游案例入口存在。");
    assert.equal(await page.locator("#runtime-checks tr").count(), 7);
    await page.locator("#runtime-media img").scrollIntoViewIfNeeded();
    await page.locator("#runtime-media img").evaluate(img => img.decode());
    assert.equal(await page.locator("#runtime-media img").evaluate(img => img.naturalWidth), 1282);
    assert.match(await page.locator("#runtime-limit").innerText(), /不证明 GCN/);
    await page.locator(".runtime-card details summary").click();
    assert.match(await page.locator("#runtime-output").innerText(), /Hello world/);
    await page.locator(".runtime-card details summary").click();
    check("本机运行证据展示", "7 行执行记录、1282×752 原生窗口截图、实际日志与未验证范围可加载。");
    for (const scenario of ["attack","file","shader"]) {
      for (const fault of ["none","api","shader"]) {
        await page.locator("#scenario").selectOption(scenario);
        await page.locator("#fault").selectOption(fault);
        await page.locator("#replay").click();
        assert.equal(await page.locator("#step-count").innerText(), "1 / 7");
        assert.equal(await page.locator("#previous-step").isDisabled(), true);
        const finalStep = fault === "api" ? 2 : fault === "shader" ? 4 : 6;
        for (let i=0;i<finalStep;i++) await page.locator("#next-step").click();
        assert.equal(await page.locator("#step-count").innerText(), `${finalStep+1} / 7`);
        assert.equal(await page.locator("#next-step").isDisabled(), true);
        assert.equal(await page.locator("#trace-list li").count(), finalStep+1);
        assert.equal(await page.locator("#scene-state").innerText(), fault === "none" ? "画面已呈现" : "请求未完成");
        if (fault !== "none") assert.equal(await page.locator(".flow-node.failed").count(), 1);
        await page.locator("#previous-step").click();
        assert.equal(await page.locator("#next-step").isDisabled(), false);
        await page.locator("#replay").click();
      }
    }
    check("教学流程与失败停止", "3 个请求 × 3 种条件共 9 条路径；正常到第 7 步，接口缺失停在第 3 步，着色器失败停在第 5 步；后退和重播通过。");
    await page.locator("#fault").selectOption("none");
    await page.locator("#replay").focus();
    await page.keyboard.press("Enter");
    await page.locator("#next-step").focus();
    await page.keyboard.press("Space");
    assert.equal(await page.locator("#step-count").innerText(), "2 / 7");
    check("键盘操作", "Enter 重播、Space 推进教学流程通过；测试采用减少动画偏好。");
    await page.locator("#clear-cache").click();
    await page.locator("#draw-effect").click();
    assert.match(await page.locator("#cache-result").innerText(), /缓存为空/);
    await page.locator("#draw-effect").click();
    assert.match(await page.locator("#cache-result").innerText(), /复用教学缓存/);
    await page.locator("#clear-cache").click();
    await page.locator("#draw-effect").click();
    assert.match(await page.locator("#cache-result").innerText(), /第 1 次绘制：缓存为空/);
    check("缓存教学", "首次转换、第二次复用、清空后再次转换通过；仅验证教学状态。");
    await page.locator("#quiz-form button").click();
    assert.match(await page.locator("#quiz-result").innerText(), /请先回答三个问题/);
    for (const [name,value] of [["q1","a"],["q2","a"],["q3","b"]]) await page.locator(`input[name=${name}][value=${value}]`).check();
    await page.locator("#quiz-form button").click();
    assert.match(await page.locator("#quiz-result").innerText(), /第 1 题.*第 2 题.*第 3 题/);
    for (const [name,value] of [["q1","b"],["q2","b"],["q3","a"]]) await page.locator(`input[name=${name}][value=${value}]`).check();
    await page.locator("#quiz-form button").click();
    assert.match(await page.locator("#quiz-result").innerText(), /三个理解都正确/);
    check("理解核对", "未答提示、三题错误反馈和全部正确反馈通过。");
    const downloadPromise = page.waitForEvent("download");
    await page.locator("#download-record").click();
    const download = await downloadPromise;
    assert.equal(download.suggestedFilename(), "shadps4-runtime-record.csv");
    const downloadBytes = fs.readFileSync(await download.path());
    assert.deepEqual([...downloadBytes.subarray(0,3)], [239,187,191]);
    const columns = downloadBytes.toString("utf8").replace(/^\uFEFF/, "").trim().split(",");
    assert.equal(columns.length, 22);
    assert.equal(columns[0], "记录日期");
    assert.equal(columns[21], "未验证事项");
    check("CSV 下载", "下载名称正确，UTF-8 BOM 存在，22 列含版本、设备、场景、证据与未验证事项。");
    const widths = [1440, 1024, 768, 390, 320];
    for (const width of widths) {
      await page.setViewportSize({width,height:1000});
      const dimensions = await page.evaluate(() => ({window:window.innerWidth, document:document.documentElement.scrollWidth}));
      assert.ok(dimensions.document <= dimensions.window+1, `Horizontal page overflow at ${width}: ${JSON.stringify(dimensions)}`);
    }
    check("响应式布局", "1440、1024、768、390、320 像素宽均无整页横向溢出；宽表格在内部滚动。");
    await page.setViewportSize({width:1440,height:1000});
    await page.locator("#understanding").scrollIntoViewIfNeeded();
    await page.evaluate(() => window.scrollTo(0,0));
    await page.waitForFunction(() => document.querySelector('#chapters a[href="#understanding"]')?.classList.contains("active"));
    await screenshot(page, "01-web-overview.jpg");
    await screenshot(page, "05-web-diagram.jpg", page.locator(".overview figure"));
    await page.locator("#scenario").selectOption("attack");
    await page.locator("#fault").selectOption("none");
    await page.locator("#replay").click();
    for (let i=0;i<6;i++) await page.locator("#next-step").click();
    await screenshot(page, "02-web-demonstration.jpg", page.locator("#demonstration"));
    await screenshot(page, "03-web-runtime.jpg", page.locator(".runtime-card"));
    await page.setViewportSize({width:390,height:844});
    await page.evaluate(() => window.scrollTo(0,0));
    await screenshot(page, "04-web-mobile.jpg");
    const parentUrl = await page.locator(".back-link").evaluate(link => link.href);
    assert.equal((await context.request.get(parentUrl)).status(), 200);
    await page.locator(".back-link").click();
    await page.waitForURL(parentUrl);
    assert.ok(await page.getByText("shadPS4", {exact:false}).count());
    check("返回研究库", "返回链接在聚合站点子路径中打开根索引，索引包含本项目。");
    assert.deepEqual(errors, []);
    check("浏览器错误", "无 JavaScript 页面异常、错误控制台或失败网络请求。");
    console.log(JSON.stringify({status:"pass", checks:checks.length, browser:version, screenshots:screenshots.length}));
  } catch (error) {
    checks.push({name:"检查中断",result:"fail",evidence:error.message.replaceAll(root,"<project>")});
    process.exitCode = 1;
    console.error(error.message);
  } finally {
    fs.mkdirSync(resultDir,{recursive:true});
    const record = {date:"2026-10-14",status:process.exitCode ? "failed" : "passed",method:"Playwright Chromium / " + (base.startsWith("https://") ? "公网 GitHub Pages" : "本地静态聚合站点"),browser:version,url:base,checks,screenshots,errors,scope:"验证当前访问地址的网页教学、证据加载和静态子路径；原生模拟器执行另见 runtime-verification。未验证商业游戏或浏览器原生 PS4 执行。"};
    fs.writeFileSync(path.join(resultDir,"web-verification.json"), JSON.stringify(record,null,2)+"\n", "utf8");
    const lines=["# 网页实际验证", "", `日期：${record.date}。结果：${record.status}。浏览器：Chromium ${version}。`, "", `访问地址：${base}，通过独立静态子路径测试。`, "", "| 检查 | 结果 | 实际证据 |", "| --- | --- | --- |", ...checks.map(item => `| ${item.name} | ${item.result} | ${item.evidence.replaceAll("|"," / ").replaceAll("\n"," ")} |`), "", "截图为实际浏览器内容，保存于子项目 assets/；不是模板或上游游戏素材。", "", ...screenshots.map(item => `- [${item.path}](../../${item.path})：${item.description}。`), "", record.scope, "", "复现脚本：[verify_web.cjs](../verify_web.cjs)。需要 Playwright 与对应 Chromium；以 SHAD_WEB_URL 指定待检查的本地或公网地址。", ""];
    fs.writeFileSync(path.join(resultDir,"web-verification.md"), lines.join("\n"), "utf8");
    await browser.close();
  }
})();
