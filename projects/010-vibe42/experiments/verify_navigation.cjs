"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");
const root = path.resolve(__dirname, "..");
const url = process.argv[2] || "http://127.0.0.1:8775/010-vibe42/";

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, reducedMotion: "reduce" });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
    page.on("requestfailed", (request) => errors.push(`failed request: ${request.url()}`));
    await page.goto(url, { waitUntil: "networkidle" });
    await page.screenshot({ path: path.join(root, "assets", "01-web-desktop.png") });
    const navigation = [];
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: width === 1440 ? 1200 : 844 });
      const links = await page.locator(".reading-nav nav a").evaluateAll((nodes) => nodes.map((node) => node.getAttribute("href")));
      for (const href of links) {
        await page.locator(`.reading-nav nav a[href="${href}"]`).click();
        await page.waitForFunction((href) => document.querySelector(`.reading-nav nav a[href="${href}"]`).getAttribute("aria-current") === "location", href, { timeout: 5000 });
        navigation.push({ width, href, current: true });
        if (width === 1440 && href === "#architecture") await page.screenshot({ path: path.join(root, "assets", "02-web-architecture.png") });
        if (width === 1440 && href === "#comparison") await page.screenshot({ path: path.join(root, "assets", "03-web-comparison.png") });
      }
    }
    const widths = [];
    for (const width of [1440, 1024, 768, 390, 320]) {
      await page.setViewportSize({ width, height: 844 });
      const measured = await page.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth }));
      assert.ok(measured.document <= measured.viewport + 1);
      widths.push(measured);
    }
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(url, { waitUntil: "networkidle" });
    await page.screenshot({ path: path.join(root, "assets", "04-web-mobile.png") });
    const favicon = await page.request.get(new URL("assets/favicon.svg", url).href);
    assert.equal(favicon.status(), 200);
    assert.deepEqual(errors, []);
    const result = { date: new Date().toISOString(), browser: `Chromium ${browser.version()}`, scope: "长章节导航修复后的定向复验；其他交互见browser-check.json", navigation, widths, errors, faviconStatus: favicon.status() };
    fs.writeFileSync(path.join(__dirname, "results", "navigation-check.json"), JSON.stringify(result, null, 2) + "\n");
    console.log(JSON.stringify({ navigationChecks: navigation.length, widths, errors: errors.length, favicon: favicon.status() }, null, 2));
  } finally { await browser.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });
