"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {chromium}=require("playwright");
const project=path.resolve(__dirname,"..");
(async()=>{
  const browser=await chromium.launch({headless:true});
  try{
    const page=await browser.newPage({viewport:{width:1400,height:2250},deviceScaleFactor:1});
    const svgUrl=process.argv[2]||"http://127.0.0.1:8775/010-vibe42/assets/understanding-overview.svg";
    assert.ok(["http:","https:"].includes(new URL(svgUrl).protocol));
    await page.goto(svgUrl,{waitUntil:"load"});
    await page.evaluate(()=>document.fonts.ready);
    const clipped=await page.locator("text").evaluateAll(nodes=>nodes.map(node=>({text:node.textContent,box:node.getBBox()})).filter(({box})=>box.x<0||box.y<0||box.x+box.width>1400||box.y+box.height>2250).map(({text})=>text));
    assert.deepEqual(clipped,[],"SVG text must stay within export canvas");
    const png=path.join(project,"assets","understanding-overview.png");
    await page.screenshot({path:png});
    fs.copyFileSync(png,path.join(project,"web","assets","understanding-overview.png"));
    console.log(JSON.stringify({size:[1400,2250],clippedText:clipped.length,pngBytes:fs.statSync(png).size},null,2));
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1});
