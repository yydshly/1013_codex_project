/* Rasterize the original SVGs without changing their content. */
const {chromium} = require(process.env.FCC_PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
(async () => {
  const root = path.resolve(__dirname, '..');
  const browser = await chromium.launch({headless:true});
  try {
    for (const [name,height] of [['understanding-overview',2460],['gateway-internals',1320]]) {
      const page = await browser.newPage({viewport:{width:1600,height},deviceScaleFactor:1});
      await page.goto('file:///' + path.join(root,'assets',name+'.svg').replaceAll('\\','/'));
      await page.evaluate(() => document.fonts.ready);
      const outside = await page.locator('svg text').evaluateAll(elements => elements.flatMap(element => {
        const b=element.getBBox(); const svg=element.ownerSVGElement.viewBox.baseVal;
        return b.x<0 || b.y<0 || b.x+b.width>svg.width-15 || b.y+b.height>svg.height-8 ? [{text:element.textContent,x:b.x,right:b.x+b.width,bottom:b.y+b.height}] : [];
      }));
      assert.deepEqual(outside,[],name+' clipped text');
      const png = path.join(root,'assets',name+'.png');
      await page.screenshot({path:png});
      fs.copyFileSync(png,path.join(root,'web/assets',name+'.png'));
      console.log(JSON.stringify({image:name,width:1600,height,bytes:fs.statSync(png).size,text_bounds:'passed'}));
      await page.close();
    }
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
