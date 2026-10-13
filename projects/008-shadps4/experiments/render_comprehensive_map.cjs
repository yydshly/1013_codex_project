"use strict";
const fs = require("node:fs");
const path = require("node:path");
const {pathToFileURL} = require("node:url");
const {chromium} = require(process.env.SHAD_PLAYWRIGHT_MODULE || "playwright");
const root = path.resolve(__dirname,"..");
(async () => {
  const browser = await chromium.launch({headless:true});
  try {
    const page = await browser.newPage({viewport:{width:1800,height:1000}, deviceScaleFactor:1});
    await page.goto(pathToFileURL(path.join(root,"assets/comprehensive-map.svg")).href);
    await page.evaluate(() => document.fonts.ready);
    const problems = await page.evaluate(() => {
      const issues = [];
      const svg = document.querySelector("svg");
      const w = svg.viewBox.baseVal.width, h = svg.viewBox.baseVal.height;
      for (const label of svg.querySelectorAll("text")) {
        const b = label.getBBox();
        if (b.x<0 || b.y<0 || b.x+b.width>w+1 || b.y+b.height>h+1) issues.push({type:"canvas",text:label.textContent,box:{x:b.x,y:b.y,width:b.width,height:b.height}});
      }
      for (const group of svg.querySelectorAll("g[data-bounds]")) {
        const [x,y,width,height] = group.dataset.bounds.split(",").map(Number);
        for (const label of group.querySelectorAll("text")) {
          const b = label.getBBox();
          if (b.x<x-1 || b.y<y-1 || b.x+b.width>x+width+1 || b.y+b.height>y+height+1) issues.push({type:group.dataset.label,text:label.textContent,overflow:{left:x-b.x,right:b.x+b.width-x-width,top:y-b.y,bottom:b.y+b.height-y-height}});
        }
      }
      return {issues,texts:svg.querySelectorAll("text").length,boundedGroups:svg.querySelectorAll("g[data-bounds]").length,dimensions:[w,h]};
    });
    await page.locator("svg").screenshot({path:path.join(root,"assets/comprehensive-map.png"),type:"png"});
    fs.copyFileSync(path.join(root,"assets/comprehensive-map.png"),path.join(root,"web/assets/comprehensive-map.png"));
    const record = {date:"2026-10-14",renderer:`Chromium ${browser.version()}`,status:problems.issues.length ? "needs-layout-repair" : "passed",...problems,scope:"SVG 的实际文字边界与输出图尺寸；研究结论依据另见 README 与运行记录。"};
    fs.writeFileSync(path.join(__dirname,"results/diagram-verification.json"),JSON.stringify(record,null,2)+"\n","utf8");
    console.log(JSON.stringify(record));
    if (problems.issues.length) process.exitCode=1;
  } finally {await browser.close();}
})();
