// Inspect the published index, original guide, application summaries and readability.
const {chromium}=require(process.env.FCC_PLAYWRIGHT_MODULE||'playwright');
const {execFileSync}=require('node:child_process');
const fs=require('node:fs');
const assert=require('node:assert/strict');
const path=require('node:path');
(async()=>{
  const commit=execFileSync('git',['rev-parse',process.argv[2]||'HEAD'],{encoding:'utf8'}).trim();
  const meta=JSON.parse(execFileSync('git',['show',`${commit}:projects/016-free-claude-code/project.json`],{encoding:'utf8'}));
  const base='https://yydshly.github.io/1013_codex_project/';
  const browser=await chromium.launch({headless:true});
  const report={asset_commit:commit,url:base,checks:[],checked_at:new Date().toISOString()};
  try{
    const page=await browser.newPage({viewport:{width:1440,height:1050},reducedMotion:'reduce'});
    const errors=[]; page.on('pageerror',error=>errors.push(String(error)));
    assert.equal((await page.goto(base,{waitUntil:'networkidle'})).status(),200);
    const row=page.locator('.project-index tbody tr').filter({has:page.locator('td.number').filter({hasText:/^016$/})});
    assert.equal(await row.count(),1);
    const sections=await row.locator('.summary-sections>div').evaluateAll(items=>items.map(item=>({label:item.querySelector('dt').textContent,text:item.querySelector('dd').textContent})));
    assert.deepEqual(sections,meta.summary_sections);
    report.summary_sections=sections.length;
    report.checks.push('十五项分段摘要逐字完整展示，与已提交元信息一致');
    const guide=page.locator('#guide-016 img');
    assert.equal(await guide.getAttribute('src'),'./previews/016-free-claude-code.png');
    assert.equal(await guide.getAttribute('alt'),meta.preview_caption);
    assert.equal(await page.locator('#guide-016 figcaption').innerText(),meta.preview_caption);
    await guide.scrollIntoViewIfNeeded();
    await guide.evaluate(image=>image.decode());
    assert.equal(await guide.evaluate(image=>image.naturalWidth),1600);
    report.checks.push('首页沿用完整理解引导图，替代文本与来源说明完整');
    assert.equal(await row.locator('a.primary').getAttribute('href'),'./016-free-claude-code/');
    assert.equal(meta.demo_url,base+'016-free-claude-code/');
    report.checks.push('正式公开地址登记正确，索引入口指向对应子路径');
    assert.equal((await page.goto(meta.demo_url,{waitUntil:'networkidle'})).status(),200);
    assert.equal(await page.locator('#essence table tbody tr').count(),4);
    assert.equal(await page.locator('#extensions table tbody tr').count(),6);
    const applicationTable=page.locator('#extensions .table-scroll');
    const contrast=await applicationTable.evaluate(element=>{
      const cell=element.querySelector('td');
      const foreground=getComputedStyle(cell).color;
      let node=cell, background;
      while(node){
        background=getComputedStyle(node).backgroundColor;
        if(background!=='rgba(0, 0, 0, 0)'&&background!=='transparent')break;
        node=node.parentElement;
      }
      const luminance=color=>{
        const rgb=color.match(/[\d.]+/g).slice(0,3).map(Number).map(value=>{
          const fraction=value/255;
          return fraction<=0.04045?fraction/12.92:((fraction+0.055)/1.055)**2.4;
        });
        return rgb[0]*0.2126+rgb[1]*0.7152+rgb[2]*0.0722;
      };
      const values=[luminance(foreground),luminance(background)].sort((a,b)=>a-b);
      return {foreground,background,ratio:(values[1]+0.05)/(values[0]+0.05)};
    });
    assert.ok(contrast.ratio>=4.5,'Readable normal table text must have at least 4.5:1 contrast');
    report.table_contrast=contrast;
    await applicationTable.scrollIntoViewIfNeeded();
    await page.screenshot({path:path.resolve('projects/016-free-claude-code/assets/07-public-extensions.png'),fullPage:false});
    report.checks.push('四问摘要与六类应用组合完整显示；公开网页扩展章节实拍');
    report.checks.push('扩展表格正文颜色对比度至少 4.5:1');
    await page.setViewportSize({width:390,height:844});
    await applicationTable.scrollIntoViewIfNeeded();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    assert.equal(await applicationTable.evaluate(element=>element.scrollWidth>element.clientWidth),true);
    report.checks.push('390px 手机下扩展表格在自身容器滚动，整页无横向溢出');
    assert.deepEqual(errors,[]);
    report.browser_errors=errors; report.all_passed=true;
    fs.writeFileSync('projects/016-free-claude-code/experiments/results/publication-index-final.json',JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report));
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1});
