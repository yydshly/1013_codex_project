// Render our authored SVG; this is not a product screenshot or an agent run.
const fs = require("node:fs");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const assert = require("node:assert/strict");
const { chromium } = require(process.argv[2] || "playwright");
const root = path.resolve(__dirname, "..");

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1200, height: 2600 }, deviceScaleFactor: 2 });
    await page.goto(pathToFileURL(path.join(root, "assets", "understanding-overview.svg")).href);
    const overflow = await page.locator("svg text").evaluateAll(items => {
      const boxes = [...document.querySelectorAll("rect")].map(item => item.getBBox()).filter(box => box.width * box.height < 1200 * 2600);
      return items.flatMap(item => {
        const text = item.getBBox();
        const centerY = text.y + text.height / 2;
        const box = boxes.filter(box => text.x >= box.x && text.x < box.x + box.width && centerY >= box.y && centerY <= box.y + box.height).sort((a, b) => a.width * a.height - b.width * b.height)[0];
        if (text.x < 0 || text.x + text.width > 1200 || (box && text.x + text.width > box.x + box.width - 8)) return [{ text: item.textContent, x: text.x, width: text.width, containerRight: box?.x + box?.width }];
        return [];
      });
    });
    assert.deepEqual(overflow, [], "Diagram text must fit its canvas and panels");
    const png = path.join(root, "assets", "understanding-overview.png");
    await page.screenshot({ path: png });
    fs.copyFileSync(png, path.join(root, "web", "assets", "understanding-overview.png"));
    await page.setViewportSize({ width: 1200, height: 1300 });
    fs.mkdirSync(path.join(__dirname, "results"), { recursive: true });
    await page.screenshot({ path: path.join(__dirname, "results", "overview-top.png"), clip: { x: 0, y: 0, width: 1200, height: 1300 } });
    await page.evaluate(() => window.scrollTo(0, 1300));
    await page.screenshot({ path: path.join(__dirname, "results", "overview-bottom.png") });
    fs.writeFileSync(path.join(__dirname, "results", "diagram-checks.json"), JSON.stringify({ checked_at: new Date().toISOString(), canvas: [1200, 2600], png_pixels: [2400, 5200], text_overflow: overflow, scope: "Original explanatory SVG, not upstream UI or model output" }, null, 2) + "\n");
    console.log("PASS diagram panel text bounds; exported PNG 2400 x 5200");
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
