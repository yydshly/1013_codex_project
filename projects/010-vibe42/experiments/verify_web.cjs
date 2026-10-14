"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");
const project = path.resolve(__dirname, "..");
const url = process.argv[2] || "http://127.0.0.1:8775/010-vibe42/";
const checks = [];
const errors = [];
const failedRequests = [];
const localResponses = new Map();
const check = (name, details) => checks.push({ name, details, status: "passed" });

async function exercise(page) {
  assert.equal(await page.locator(".reading-content .research-section").count(), 16);
  assert.equal(await page.locator("#comparison tbody tr").count(), 12);
  assert.equal(await page.locator(".source-list li").count(), 21);
  assert.equal(await page.locator("[data-evidence-kind]").count(), 18);
  const anchors = await page.locator('a[href^="#"]').evaluateAll((links) => links.map((a) => a.getAttribute("href").slice(1)).filter((id) => !document.getElementById(id)));
  assert.deepEqual(anchors, []);
  for (const key of ["client", "control", "relay", "companion", "session", "agent", "notify"]) {
    const button = page.locator(`[data-module="${key}"]`);
    await button.click();
    assert.equal(await button.getAttribute("aria-pressed"), "true");
    assert.equal(await page.locator("#module-detail h3").innerText(), await button.evaluate((el) => el.childNodes[1].textContent));
  }
  check("完整正文、来源、锚点和七个模块", "理解总览+14专题+来源；12对比维度；21来源；18证据");
  await page.locator('[data-step="0"]').click();
  assert.equal(await page.locator("#step-prev").isDisabled(), true);
  for (let i = 1; i < 6; i++) {
    await page.locator("#step-next").click();
    assert.match(await page.locator("#step-count").innerText(), new RegExp(`0${i + 1} / 06`));
  }
  assert.equal(await page.locator("#step-next").isDisabled(), true);
  assert.match(await page.locator("#terminal-output").innerText(), /模拟状态/);
  await page.locator("#step-prev").click();
  assert.match(await page.locator("#step-count").innerText(), /05/);
  check("六步示意与边界", "首尾禁用、前后切换、模拟输出标签");
  for (const [key, pattern] of [["phone", /产品说明/], ["sleep", /系统机制推导/], ["service", /Companion退出/], ["restart", /原生历史续接/]]) {
    await page.locator("#failure-select").selectOption(key);
    assert.match(await page.locator("#failure-result").innerText(), pattern);
  }
  await page.locator('[data-route="relay"]').click();
  assert.equal(await page.locator("#route-path > *").count(), 5);
  assert.match(await page.locator("#route-explanation").innerText(), /尚未独立抓包/);
  await page.locator('[data-route="direct"]').focus();
  await page.keyboard.press("Space");
  assert.equal(await page.locator("#route-path > *").count(), 3);
  assert.equal(await page.locator('[data-route="direct"]').getAttribute("aria-pressed"), "true");
  check("故障条件、路由与键盘", "4种生命周期；2种路径；Space键可操作");
  for (const kind of ["official", "inference", "proposal", "unverified", "all"]) {
    await page.locator(`[data-evidence-filter="${kind}"]`).click();
    const expected = kind === "all" ? 18 : await page.locator(`[data-evidence-kind="${kind}"]`).count();
    assert.equal(await page.locator("[data-evidence-kind]:visible").count(), expected);
    assert.equal(await page.locator("#evidence-count").innerText(), `显示 ${expected} 项研究记录`);
  }
  check("证据筛选", "4层证据与全部恢复，数量一致");
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: "reduce", acceptDownloads: true });
    const page = await context.newPage();
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("console", (msg) => { if (msg.type() === "error") errors.push(msg.text()); });
    page.on("requestfailed", (request) => failedRequests.push({ url: request.url(), error: request.failure()?.errorText }));
    page.on("response", (response) => { if (response.url().startsWith(url)) localResponses.set(response.url(), response.status()); });
    const response = await page.goto(url, { waitUntil: "networkidle" });
    assert.equal(response.status(), 200);
    await exercise(page);
    for (const [relative, content] of [["assets/architecture.svg", /Vibe42 三端逻辑架构/], ["styles.css", /--paper/], ["app.js", /VIBE42_RESEARCH/], ["data/evidence.json", /未连接真实产品/], ["data/research-notes.txt", /研究基线与来源/]]) {
      const resource = await context.request.get(new URL(relative, url).href);
      assert.equal(resource.status(), 200);
      assert.match(await resource.text(), content);
    }
    const downloadEvent = page.waitForEvent("download");
    await page.locator('.download-panel a[href="./data/research-notes.txt"]').click();
    const download = await downloadEvent;
    assert.equal(download.suggestedFilename(), "research-notes.txt");
    assert.match(fs.readFileSync(await download.path(), "utf8"), /原仓库与源码 commit/);
    check("静态资源与真实下载", "HTTP 200；TXT下载成功且保留研究边界");
    await page.goto(new URL("../", url).href, { waitUntil: "networkidle" });
    assert.match(await page.title(), /项目与产品研究/);
    assert.match(await page.locator("body").innerText(), /产品网站 · 公开资料研究/);
    await page.locator('.project-name a[href="./010-vibe42/"]').click();
    assert.equal(page.url(), url);
    check("构建索引与独立子路径", "首页网站来源标签与010-vibe42往返成功");
    fs.mkdirSync(path.join(project, "assets"), { recursive: true });
    await page.screenshot({ path: path.join(project, "assets", "01-web-desktop.png") });
    await page.setViewportSize({ width: 1440, height: 1200 });
    await page.locator('.reading-nav a[href="#architecture"]').click();
    await page.waitForFunction(() => document.querySelector('.reading-nav a[href="#architecture"]').getAttribute("aria-current") === "location");
    await page.screenshot({ path: path.join(project, "assets", "02-web-architecture.png") });
    await page.locator('.reading-nav a[href="#comparison"]').click();
    await page.waitForFunction(() => document.querySelector('.reading-nav a[href="#comparison"]').getAttribute("aria-current") === "location");
    await page.screenshot({ path: path.join(project, "assets", "03-web-comparison.png") });
    check("章节导航与阅读位置", "点击锚点后长章节的当前导航同步");
    const widths = [];
    for (const width of [1440, 1024, 768, 390, 320]) {
      await page.setViewportSize({ width, height: width < 620 ? 844 : 1000 });
      const measured = await page.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth }));
      assert.ok(measured.document <= measured.viewport + 1, `page overflow at ${width}: ${measured.document}`);
      widths.push(measured);
    }
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(url, { waitUntil: "networkidle" });
    await exercise(page);
    await page.goto(url, { waitUntil: "networkidle" });
    await page.screenshot({ path: path.join(project, "assets", "04-web-mobile.png") });
    check("桌面/平板/手机布局", widths);
    await page.emulateMedia({ media: "print" });
    assert.equal(await page.locator("#comparison tbody tr").count(), 12);
    assert.equal(await page.locator(".reading-nav").isVisible(), false);
    check("打印样式", "完整比较表保留，交互导航隐藏；未导出PDF");
    const offline = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 1024, height: 800 } });
    const staticPage = await offline.newPage();
    await staticPage.goto(url, { waitUntil: "networkidle" });
    assert.equal(await staticPage.locator(".source-list li").count(), 21);
    assert.match(await staticPage.locator("#implementation").innerText(), /阶段/);
    check("关闭JavaScript阅读", "完整正文、来源与实现路线可见");
    assert.deepEqual(errors, []);
    assert.deepEqual(failedRequests, []);
    assert.ok([...localResponses.values()].every((status) => status === 200));
    check("浏览器错误与请求", "无pageerror/console error/failed request；观察到本项目资源均200");
    const result = { date: new Date().toISOString(), browser: `Chromium ${browser.version()}`, baseUrl: url, scope: "静态研究页面；不验证真实Vibe42", checks, localResponses: [...localResponses].map(([url, status]) => ({ url, status })), errors, failedRequests, screenshots: ["01-web-desktop.png", "02-web-architecture.png", "03-web-comparison.png", "04-web-mobile.png"] };
    const resultDirectory = path.join(__dirname, "results");
    fs.mkdirSync(resultDirectory, { recursive: true });
    fs.writeFileSync(path.join(resultDirectory, "browser-check.json"), JSON.stringify(result, null, 2) + "\n");
    console.log(JSON.stringify({ browser: result.browser, passed: checks.length, errors: errors.length, failedRequests: failedRequests.length, widths, screenshots: result.screenshots }, null, 2));
  } finally { await browser.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });
