"use strict";
// Checks the original teaching webpage; never runs OpenMontage or external APIs.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { chromium } = require("playwright");

const project = path.resolve(__dirname, "..");
const catalog = JSON.parse(fs.readFileSync(path.join(project, "web/research.json"), "utf8"));
const metadata = JSON.parse(fs.readFileSync(path.join(project, "project.json"), "utf8"));
const comparison = JSON.parse(fs.readFileSync(path.join(project, "web/comparison.json"), "utf8"));
const url = process.argv[2] || "http://127.0.0.1:8791/011-openmontage/";
const executablePath = process.argv[3];
const checks = [];
const errors = [];
const screenshots = [];
const publicRun = process.argv.includes("--public");
const shotName = name => publicRun ? "public-" + name : name;
const record = (name, details) => checks.push({name, status:"passed", ...(details ? {details} : {})});
const reportFile = path.join(__dirname, process.argv.includes("--public") ? "results/public-web-verification.json" : "results/web-verification.json");
let browser;
let browserVersion;

async function noOverflow(page, width) {
  const measure = await page.evaluate(() => ({
    viewport: innerWidth,
    document: document.documentElement.scrollWidth,
    images: [...document.images].every(img => img.complete && img.naturalWidth > 0)
  }));
  assert(measure.document <= measure.viewport + 1, `Overflow at ${width}px: ${JSON.stringify(measure)}`);
  assert(measure.images, `Image missing at ${width}px`);
  record(`响应式 ${width}px`, measure);
}

async function main() {
  browser = await chromium.launch({headless:true, ...(executablePath ? {executablePath} : {})});
  browserVersion = browser.version();
  const context = await browser.newContext({viewport:{width:1440, height:1000}, reducedMotion:"reduce"});
  const page = await context.newPage();
  const requests = [];
  page.on("pageerror", error => errors.push(error.message));
  page.on("console", message => { if(message.type() === "error") errors.push(message.text()); });
  page.on("request", request => requests.push(request.url()));
  const response = await page.goto(url, {waitUntil:"networkidle"});
  assert.equal(response.status(), 200);
  assert.match(await page.title(), /OpenMontage/);
  assert.equal(await page.locator("#capability-rows tr").count(), catalog.capabilities.length);
  assert.equal(await page.locator(".pipeline-card").count(), catalog.pipelines.length);
  assert.equal(await page.locator(".source-list li").count(), catalog.sources.length);
  record("完整静态目录", {capabilities:catalog.capabilities.length, pipelines:catalog.pipelines.length, sources:catalog.sources.length});
  assert.equal(await page.locator("#brief .brief-grid article").count(), 4);
  for(const label of ["能力", "原理", "核心价值", "可扩展场景"]) {
    assert((await page.locator("#brief").innerText()).includes(metadata.summary_sections.find(section => section.label === label).text));
  }
  record("四项导读与能力、原理、核心价值、可扩展场景摘要完全对应");
  const homeResponse = await context.request.get(new URL("../",url).href);
  const homeMarkup = await homeResponse.text();
  for(const section of metadata.summary_sections) {
    assert(homeMarkup.includes(section.text), section.label);
  }
  assert(homeMarkup.includes("./previews/011-openmontage.png"));
  record("首页完整保留全部分项摘要与完整图入口",{summary_sections:metadata.summary_sections.length});

  const badAnchors = await page.evaluate(() => [...document.querySelectorAll('a[href^="#"]')]
    .map(link => link.getAttribute("href")).filter(href => !document.getElementById(href.slice(1))));
  assert.deepEqual(badAnchors, []);
  const duplicateIds = await page.evaluate(() => {
    const ids = [...document.querySelectorAll("[id]")].map(item => item.id);
    return ids.filter((id, index) => ids.indexOf(id) !== index);
  });
  assert.deepEqual(duplicateIds, []);
  record("全部章节和证据锚点、唯一 ID");

  for(const relative of ["./styles.css", "./app.js", "./assets/overview.svg", "./assets/ability-map.svg", "./assets/ability-map.png", "./research.json", "./comparison.json", "./research-summary.txt", "../"]) {
    const result = await context.request.get(new URL(relative, url).href);
    assert.equal(result.status(), 200, relative);
  }
  assert((await context.request.get(new URL("./research-summary.txt", url).href)).headers()["content-type"].includes("text/plain"));
  record("站点子路径、首页返回与下载资源 HTTP 200");
  assert(await page.locator('#understanding img').evaluate(img => img.complete && img.naturalWidth === 2200 && img.naturalHeight === 4753));
  assert.equal(await page.locator('#understanding a[download]').count(), 2);
  for(const extension of ["png", "svg"]) {
    const download = page.waitForEvent("download");
    await page.locator(`#understanding a[download$=".${extension}"]`).click();
    const result = await download;
    assert.equal(result.suggestedFilename(), "openmontage-ability-map." + extension);
    assert.equal(await result.failure(), null);
  }
  const popupPromise = page.waitForEvent("popup");
  await page.locator('#understanding .poster-actions a[target="_blank"]').click();
  const popup = await popupPromise;
  await popup.waitForLoadState();
  assert(popup.url().endsWith("/assets/ability-map.png"));
  await popup.close();
  record("完整能力图加载、PNG/SVG 实际下载、原尺寸查看");

  const projectRows = page.locator("#project-comparison tbody tr");
  assert.equal(await projectRows.count(), comparison.projects.length);
  assert.deepEqual(await projectRows.evaluateAll(rows => rows.map(row => row.dataset.project)), comparison.projects.map(item => item.id));
  for(const item of comparison.projects) {
    const row = page.locator(`#project-comparison tr[data-project="${item.id}"]`);
    assert.equal(await row.locator("a").getAttribute("href"), item.evidence_url);
    assert((await row.innerText()).includes(item.output));
  }
  assert.equal(await page.locator(".two-product-table tbody tr").count(), 7);
  const comparisonDownload = page.waitForEvent("download");
  await page.locator("#comparison a[download]").click();
  const comparisonFile = await comparisonDownload;
  assert.equal(comparisonFile.suggestedFilename(), "openmontage-comparison.json");
  assert.equal(await comparisonFile.failure(), null);
  const downloaded = JSON.parse(fs.readFileSync(await comparisonFile.path(), "utf8"));
  assert.deepEqual(downloaded, comparison);
  const textSummary = await (await context.request.get(new URL("./research-summary.txt", url).href)).text();
  assert(textSummary.includes("OpenMontage 与 BaoCut：七个维度展开"));
  assert(textSummary.includes("Vibe42"));
  assert(textSummary.includes("尚未验证直接互通"));
  record("11 项对比、七维 BaoCut 对照、来源对应与完整 JSON/文字下载");

  await page.locator('#comparison h2').scrollIntoViewIfNeeded();
  await page.evaluate(() => window.scrollTo(0,document.querySelector('#comparison').getBoundingClientRect().top + scrollY - 105));
  await page.screenshot({path:path.join(project,"assets/",shotName("05-web-comparison.png"))});
  screenshots.push("assets/"+shotName("05-web-comparison.png"));
  await page.locator(".two-product-table").screenshot({path:path.join(project,"assets/",shotName("06-web-baocut.png"))});
  screenshots.push("assets/"+shotName("06-web-baocut.png"));

  await noOverflow(page, 1440);
  await page.evaluate(() => window.scrollTo(0,0));
  const overview = path.join(project, "assets/",shotName("01-web-overview.png"));
  await page.screenshot({path:overview});
  screenshots.push("assets/"+shotName("01-web-overview.png"));
  await page.locator("#brief").screenshot({path:path.join(project,"assets/",shotName("08-web-core-summary.png"))});
  screenshots.push("assets/"+shotName("08-web-core-summary.png"));

  for(const category of [...new Set(catalog.capabilities.map(item => item.category))]) {
    await page.locator(`[data-filter="${category}"]`).click();
    assert.equal(await page.locator("#capability-rows tr:visible").count(), catalog.capabilities.filter(item => item.category === category).length);
    assert.equal(await page.locator(`[data-filter="${category}"]`).getAttribute("aria-pressed"), "true");
  }
  await page.locator('[data-filter="all"]').click();
  await page.locator("#capability-search").fill("字幕");
  const visible = await page.locator("#capability-rows tr:visible").allTextContents();
  assert(visible.length > 0);
  assert(visible.every(text => text.includes("字幕")));
  await page.locator("#capability-search").fill("不存在的功能XYZ001");
  assert.equal(await page.locator("#capability-rows tr:visible").count(), 0);
  assert(await page.locator("#empty-results").isVisible());
  await page.locator("#capability-search").fill("");
  assert.equal(await page.locator("#capability-rows tr:visible").count(), catalog.capabilities.length);
  record("六类能力筛选、关键词、空结果、恢复全部");
  await page.locator("#capabilities").scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(project, "assets/",shotName("04-web-capabilities.png"))});
  screenshots.push("assets/"+shotName("04-web-capabilities.png"));

  for(const [key, expected] of [["generated", "模型生成素材"], ["footage", "检索真实镜头"], ["code", "代码描述画面"]]) {
    await page.locator(`[data-path="${key}"]`).click();
    assert((await page.locator("#path-detail h3").innerText()).includes(expected));
    assert.equal(await page.locator(`[data-path="${key}"]`).getAttribute("aria-pressed"), "true");
  }
  record("三条制作路径切换");

  await page.locator('[data-stage="4"]').click();
  await page.locator("#finish-stage").click();
  assert((await page.locator("#gate-status").innerText()).includes("前置阶段尚未完成"));
  assert(await page.locator("#approve-stage").isDisabled());
  await page.locator("#reset-flow").click();
  const gated = new Set([1,2,3,4,7]);
  for(let i = 0; i < 8; i++) {
    await page.locator(`[data-stage="${i}"]`).click();
    await page.locator("#finish-stage").click();
    if(gated.has(i)) {
      assert((await page.locator("#gate-status").innerText()).includes("等待模拟确认"));
      assert.equal(await page.locator(`[data-stage="${i}"].done`).count(), 0);
      await page.locator("#approve-stage").click();
    }
    assert.equal(await page.locator(`[data-stage="${i}"].done`).count(), 1);
    assert(await page.locator("#finish-stage").isDisabled());
  }
  assert.equal(await page.locator("[data-stage].done").count(), 8);
  await page.locator("#reset-flow").click();
  assert.equal(await page.locator("[data-stage].done").count(), 0);
  assert.equal(await page.locator('[data-stage="0"]').getAttribute("aria-pressed"), "true");
  record("前置阶段阻断、五个确认门、完整八阶段与重置");

  await page.locator('[data-stage="3"]').click();
  await page.locator(".workflow-demo").scrollIntoViewIfNeeded();
  await page.locator(".workflow-demo").screenshot({path:path.join(project, "assets/",shotName("02-web-workflow.png"))});
  screenshots.push("assets/"+shotName("02-web-workflow.png"));
  await page.locator("#stage-detail details summary").click();
  assert((await page.locator("#stage-detail pre").innerText()).includes("scene_plan"));
  record("交接材料示例展开");

  for(const width of [1024, 768, 390, 320]) {
    await page.setViewportSize({width, height:844});
    await noOverflow(page, width);
    assert.equal(await page.locator("#project-comparison tbody tr:visible").count(), 11);
    if(width <= 760) {
      assert.equal(await page.locator("#project-comparison tbody tr").first().evaluate(row => getComputedStyle(row).display), "block");
    }
    await page.locator('[data-filter="process"]').click();
    assert.equal(await page.locator("#capability-rows tr:visible").count(), 7);
    await page.locator('[data-filter="all"]').click();
    if(width === 390) {
      await page.evaluate(() => window.scrollTo(0,0));
      await page.screenshot({path:path.join(project, "assets/",shotName("03-web-mobile.png"))});
      screenshots.push("assets/"+shotName("03-web-mobile.png"));
      await page.locator('#comparison h2').scrollIntoViewIfNeeded();
      await page.evaluate(() => window.scrollTo(0,document.querySelector('#comparison').getBoundingClientRect().top + scrollY - 128));
      await page.screenshot({path:path.join(project,"assets/",shotName("07-web-comparison-mobile.png"))});
      screenshots.push("assets/"+shotName("07-web-comparison-mobile.png"));
    }
  }
  record("手机比较表逐项目显示、11 项完整可见且无横向溢出");

  const staticContext = await browser.newContext({javaScriptEnabled:false, viewport:{width:1280, height:900}});
  const staticPage = await staticContext.newPage();
  await staticPage.goto(url, {waitUntil:"networkidle"});
  assert.equal(await staticPage.locator("#capability-rows tr").count(), 34);
  assert.equal(await staticPage.locator(".pipeline-card").count(), 12);
  assert.equal(await staticPage.locator(".source-list li").count(), 27);
  assert(await staticPage.locator("noscript").isVisible());
  assert.equal(await staticPage.locator("#project-comparison tbody tr").count(), 11);
  assert.equal(await staticPage.locator(".two-product-table tbody tr").count(), 7);
  record("禁用 JavaScript 仍完整阅读");
  await staticContext.close();

  assert.deepEqual(errors, []);
  assert(requests.every(address => new URL(address).origin === new URL(url).origin));
  record("无脚本错误、无页面自动外部请求");
  const fileContext = await browser.newContext({viewport:{width:1280, height:900}, reducedMotion:"reduce"});
  const filePage = await fileContext.newPage();
  const fileErrors = [];
  filePage.on("pageerror", error => fileErrors.push(error.message));
  await filePage.goto(pathToFileURL(path.join(project, "web/index.html")).href, {waitUntil:"load"});
  assert.equal(await filePage.locator("#capability-rows tr").count(), 34);
  assert.equal(await filePage.locator("#project-comparison tbody tr").count(), 11);
  await filePage.locator('[data-filter="process"]').click();
  assert.equal(await filePage.locator("#capability-rows tr:visible").count(), 7);
  await filePage.locator('[data-stage="0"]').click();
  await filePage.locator("#finish-stage").click();
  await filePage.locator('[data-stage="1"]').click();
  await filePage.locator("#finish-stage").click();
  assert((await filePage.locator("#gate-status").innerText()).includes("等待模拟确认"));
  assert(await filePage.locator(".hero-figure img").evaluate(img => img.complete && img.naturalWidth > 0));
  assert.deepEqual(fileErrors, []);
  record("直接打开本地 HTML 的正文、图片、筛选与教学交互");
  await fileContext.close();
  await context.close();
}

(async () => {
  let failure;
  try { await main(); } catch(error) { failure = error.stack; }
  finally { if(browser) await browser.close(); }
  fs.mkdirSync(path.dirname(reportFile), {recursive:true});
  const report = {date:new Date().toISOString(), url, scope:"本仓库原创静态研究网页；不是上游视频制作验证", browser:executablePath || "Playwright Chromium", browser_version:browserVersion, status:failure ? "failed" : "passed", checks, errors, screenshots, ...(failure ? {failure} : {})};
  fs.writeFileSync(reportFile, JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify({status:report.status, checks:checks.length, screenshots, ...(failure ? {failure} : {})}, null, 2));
  if(failure) process.exitCode = 1;
})();
