"use strict";
// Render original vector artwork, check actual font bounds, export a PNG.
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const {chromium} = require("playwright");
const project = path.resolve(__dirname, "..");

(async () => {
  const browser = await chromium.launch({headless:true, executablePath:process.argv[2] || "C:/Program Files/Google/Chrome/Application/chrome.exe"});
  try {
    const page = await browser.newPage({viewport:{width:2200, height:1100}, deviceScaleFactor:1});
    const svgSource = fs.readFileSync(path.join(project, "assets/ability-map.svg"), "utf8");
    await page.setContent('<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0}svg{display:block}</style></head><body>'+svgSource+'</body></html>');
    await page.evaluate(() => document.fonts.ready);
    const dimensions = await page.locator("svg").evaluate(svg => ({width:svg.width.baseVal.value, height:svg.height.baseVal.value}));
    const issues = await page.evaluate(() => {
      const svg = document.querySelector("svg");
      return [...svg.querySelectorAll("text")].flatMap(item => {
        const box = item.getBBox();
        const max = Number(item.dataset.maxWidth);
        const outside = box.x < 0 || box.x + box.width > svg.width.baseVal.value || box.y < 0 || box.y + box.height > svg.height.baseVal.value;
        return (outside || (max && box.width > max + 2)) ? [{text:item.textContent, width:box.width, allowed:max || null, outside}] : [];
      });
    });
    assert.deepEqual(issues, [], "Actual font dimensions exceed allotted text widths");
    const catalog = JSON.parse(fs.readFileSync(path.join(project, "web/research.json"), "utf8"));
    const artworkText = await page.locator("svg").textContent();
    for(const cap of catalog.capabilities) assert(artworkText.includes(cap.name), cap.name);
    for(const pipeline of catalog.pipelines) assert(artworkText.includes(pipeline.name), pipeline.name);
    await page.screenshot({path:path.join(project, "assets/ability-map.png"), fullPage:true});
    fs.copyFileSync(path.join(project, "assets/ability-map.png"), path.join(project, "web/assets/ability-map.png"));
    // Sections at native size for visual inspection; these are render captures.
    for(const [name, y, height] of [["map-top",0,1100], ["map-capabilities",1100,1100], ["map-effects",2200,1100], ["map-extensions",3300,dimensions.height-3300]]) {
      await page.setViewportSize({width:2200,height});
      await page.evaluate(top => window.scrollTo(0,top), y);
      await page.screenshot({path:path.join(project, "assets/"+name+"-qa.png")});
    }
    const result = {date:new Date().toISOString(), status:"passed", ...dimensions, capabilities:catalog.capabilities.length, pipelines:catalog.pipelines.length, text_width_issues:issues, browser_version:browser.version(), source_ref:catalog.source_ref, scope:"原创 SVG 完整性、实际字体边界与 PNG 渲染；不代表上游制作实测"};
    fs.writeFileSync(path.join(__dirname,"results/ability-map-verification.json"), JSON.stringify(result,null,2)+"\n");
    console.log(JSON.stringify(result));
  } finally { await browser.close(); }
})().catch(error => {console.error(error); process.exitCode=1;});
