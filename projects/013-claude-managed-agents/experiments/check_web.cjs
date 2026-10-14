// Local browser checks. This script does not call an agent or a model service.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require(process.argv[3] || "playwright");
const url = process.argv[2] || "http://127.0.0.1:8793/013-claude-managed-agents/";
const project = path.resolve(__dirname, "..");
const results = [];
const errors = [];

async function check(name, action) {
  await action();
  results.push({ name, result: "passed" });
  console.log(`PASS ${name}`);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 960 }, reducedMotion: "reduce" });
    page.on("pageerror", error => errors.push(String(error)));
    page.on("console", message => { if (message.type() === "error") errors.push(message.text()); });
    const response = await page.goto(url);
    assert.equal(response.status(), 200);
    await check("Seventeen chapters, unique anchors, twelve questions, and twelve sources", async () => {
      assert.equal(await page.locator("main section.section").count(), 17);
      assert.equal(await page.locator(".sources-list li").count(), 12);
      assert.equal(await page.locator("#questions details").count(), 12);
      const ids = await page.locator("[id]").evaluateAll(items => items.map(item => item.id));
      assert.equal(new Set(ids).size, ids.length);
      for (const href of await page.locator('a[href^="#"]').evaluateAll(items => items.map(item => item.getAttribute("href")))) {
        assert.equal(await page.locator(href).count(), 1, href);
      }
    });
    await check("Local resources and project navigation return HTTP 200", async () => {
      const links = await page.locator("[href], [src]").evaluateAll(items => items.map(item => item.getAttribute("href") || item.getAttribute("src")).filter(link => !link.startsWith("#") && !/^https?:/.test(link)));
      for (const link of new Set(links)) {
        const response = await page.request.get(new URL(link, url).href);
        assert.equal(response.status(), 200, link);
      }
      assert.equal(await page.locator("img").evaluateAll(items => items.every(item => item.complete && item.naturalWidth > 0)), true);
    });
    await check("Collaboration mode switches its explanation and pressed state", async () => {
      await page.locator('[data-mode="subagents"]').click();
      assert.match(await page.locator("#mode-title").textContent(), /分派任务/);
      assert.match(await page.locator("#mode-limit").textContent(), /25/);
      assert.equal(await page.locator('[data-mode="subagents"]').getAttribute("aria-pressed"), "true");
      assert.equal(await page.locator('[data-mode="workflow"]').getAttribute("aria-pressed"), "false");
      await page.locator('[data-mode="workflow"]').click();
      assert.match(await page.locator("#mode-title").textContent(), /服务端后台执行/);
    });
    for (const [scenario, steps, thirdState] of [["normal", 5, "待复核"], ["retry", 7, "首次失败"], ["evidence", 7, "待补证据"]]) {
      await check(`Teaching flow ${scenario}: intermediate status, completion, and reset`, async () => {
        await page.locator("#demo-scenario").selectOption(scenario);
        assert.equal(await page.locator("#demo-stage-number").textContent(), `步骤 1 / ${steps}`);
        await page.locator("#demo-next").click();
        await page.locator("#demo-next").click();
        assert.match(await page.locator("#demo-tasks tr").nth(1).textContent(), new RegExp(thirdState));
        for (let index = 3; index < steps; index++) await page.locator("#demo-next").click();
        assert.equal(await page.locator("#demo-stage-number").textContent(), `步骤 ${steps} / ${steps}`);
        assert.equal(await page.locator("#demo-next").isDisabled(), true);
        assert.equal(await page.locator("#demo-tasks .done").count(), 3);
        await page.locator("#demo-reset").click();
        assert.equal(await page.locator("#demo-stage-number").textContent(), `步骤 1 / ${steps}`);
        assert.equal(await page.locator("#demo-next").isDisabled(), false);
      });
    }
    await check("Chapter navigation and native questions expand", async () => {
      await page.locator('.sidebar nav a[href="#questions"]').click();
      await page.waitForFunction(() => document.querySelector('.sidebar nav a[href="#questions"]').hasAttribute("aria-current"));
      for (const item of await page.locator("#questions details").all()) {
        if (await item.evaluate(element => element.open)) await item.locator("summary").click();
        await item.locator("summary").click();
        assert.equal(await item.getAttribute("open"), "");
        assert.equal(await item.locator("p").isVisible(), true);
        await item.locator("summary").click();
      }
    });
    await check("Task template and overview diagram download", async () => {
      for (const selector of ['a[download$=".json"]', 'a[download$=".svg"]', 'a[download$=".png"]']) {
        const promise = page.waitForEvent("download");
        await page.locator(selector).click();
        const download = await promise;
        assert.equal(await download.failure(), null);
        assert.match(download.suggestedFilename(), /\.(json|svg|png)$/);
      }
      const response = await page.request.get(new URL("data/research-plan.example.json", url).href);
      assert.equal((await response.json()).example_only, true);
    });
    await check("Planning, six-field contracts, and black-box boundaries are present", async () => {
      assert.match(await page.locator("#decomposition").textContent(), /模型规划/);
      assert.equal(await page.locator(".contract-grid article").count(), 6);
      assert.match(await page.locator("#contract").textContent(), /Agent、任务和模块/);
      assert.match(await page.locator("#handoff").textContent(), /不能直接视为强制隔离/);
    });
    await check("Undersea phases: dependencies, partial checks, failed integration, and acceptance", async () => {
      const buttons = page.locator("[data-ocean-phase]");
      assert.equal(await buttons.count(), 6);
      for (let index = 0; index < 6; index++) {
        await buttons.nth(index).click();
        assert.equal(await page.locator("#ocean-stage-label").textContent(), `阶段 ${index + 1} / 6`);
        assert.equal(await page.locator('[data-ocean-phase][aria-pressed="true"]').count(), 1);
        if (index === 1) assert.match(await page.locator('[data-ocean-task="fish"] .ocean-status').textContent(), /等待基座/);
        if (index === 2) assert.match(await page.locator('[data-ocean-task="fish"] .ocean-status').textContent(), /临时数据开发/);
        if (index === 4) {
          assert.match(await page.locator('[data-ocean-task="fish"] .ocean-status').textContent(), /集成检查失败/);
          assert.equal(await page.locator(".ocean-status.failed").count(), 1);
          assert.equal(await page.locator(".ocean-status.done").count(), 3);
        }
        if (index === 5) assert.equal(await page.locator(".ocean-status.done").count(), 6);
      }
    });
    await check("Six undersea task contracts can be inspected independently", async () => {
      assert.equal(await page.locator("[data-ocean-task]").count(), 6);
      for (const button of await page.locator("[data-ocean-task]").all()) {
        const title = await button.locator("strong").textContent();
        await button.click();
        assert.equal(await page.locator("#ocean-task-title").textContent(), title);
        assert.equal(await page.locator("#ocean-task-contract dt").count(), 6);
        assert.equal(await page.locator('[data-ocean-task][aria-pressed="true"]').count(), 1);
      }
    });
    await check("Undersea controls work with keyboard activation", async () => {
      await page.locator('[data-ocean-task="fish"]').focus();
      await page.keyboard.press("Enter");
      assert.equal(await page.locator('[data-ocean-task="fish"]').getAttribute("aria-pressed"), "true");
      await page.locator('[data-ocean-phase="0"]').focus();
      await page.keyboard.press("Space");
      assert.equal(await page.locator("#ocean-stage-label").textContent(), "阶段 1 / 6");
    });
    for (const width of [320, 390, 760, 768, 1024, 1440]) {
      await check(`Viewport ${width}px: no document overflow`, async () => {
        await page.setViewportSize({ width, height: 960 });
        const metrics = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, viewport: innerWidth }));
        assert.ok(metrics.scroll <= metrics.viewport, JSON.stringify(metrics));
      });
    }
    await page.locator("#demo-scenario").selectOption("normal");
    await page.locator('[data-ocean-phase="4"]').click();
    await page.locator('[data-ocean-task="fish"]').click();
    await page.setViewportSize({ width: 1440, height: 960 });
    await page.locator(".ocean-explorer").screenshot({ path: path.join(project, "assets", "undersea-desktop.png"), style: ".header{visibility:hidden!important}" });
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({ path: path.join(project, "assets", "page-desktop.png") });
    await page.locator("#walkthrough").scrollIntoViewIfNeeded();
    await page.locator(".walkthrough").screenshot({ path: path.join(project, "assets", "flow-desktop.png") });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.locator(".ocean-explorer").screenshot({ path: path.join(project, "assets", "undersea-mobile.png"), style: ".header{visibility:hidden!important}" });
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({ path: path.join(project, "assets", "page-mobile.png") });
    await page.locator(".walkthrough").screenshot({ path: path.join(project, "assets", "flow-mobile.png") });
    await check("Mobile controls remain usable", async () => {
      await page.locator("#demo-scenario").selectOption("retry");
      await page.locator("#demo-next").click();
      assert.equal(await page.locator("#demo-stage-number").textContent(), "步骤 2 / 7");
      await page.locator("#demo-reset").click();
      await page.locator('[data-mode="subagents"]').click();
      assert.match(await page.locator("#mode-limit").textContent(), /25/);
    });
    await check("Undersea stages and contracts work on mobile", async () => {
      await page.locator('[data-ocean-phase="5"]').click();
      assert.equal(await page.locator(".ocean-status.done").count(), 6);
      await page.locator('[data-ocean-task="objectives"]').click();
      assert.match(await page.locator("#ocean-task-title").textContent(), /探索任务/);
    });
    const noScript = await browser.newPage({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
    await check("Core content and reading aids remain available without JavaScript", async () => {
      assert.equal((await noScript.goto(url)).status(), 200);
      assert.match(await noScript.locator("h1").textContent(), /编排与运行管理/);
      assert.equal(await noScript.locator("main section").count(), 17);
      assert.equal(await noScript.locator("noscript").count(), 2);
      assert.equal(await noScript.locator("noscript").first().isVisible(), true);
      assert.equal(await noScript.locator("#ocean-task-contract dt").count(), 6);
      assert.equal(await noScript.locator(".sources-list li").count(), 12);
    });
    await check("No browser script or console errors", async () => assert.deepEqual(errors, []));
    fs.mkdirSync(path.join(__dirname, "results"), { recursive: true });
    fs.writeFileSync(path.join(__dirname, "results", "browser-checks.json"), JSON.stringify({ checked_at: new Date().toISOString(), url, browser: await browser.version(), checks: results, errors, scope: "Local static website only; no model or agent service was called." }, null, 2) + "\n");
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
