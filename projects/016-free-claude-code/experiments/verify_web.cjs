/* Verify the static research page only. No real agents, credentials or models. */
const { chromium } = require(process.env.FCC_PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

(async () => {
  const url = process.argv[2] || 'http://127.0.0.1:8875/016-free-claude-code/';
  const root = path.resolve(__dirname, '..');
  const report = {checked_on: '2026-10-14', url, scope: '静态研究网页和固定教学模拟；不运行 FCC 或模型。', checks: [], screenshots: [], resources: []};
  const browser = await chromium.launch({headless: true});
  try {
    const page = await browser.newPage({viewport: {width: 1440, height: 1050}, reducedMotion: 'reduce'});
    const failures = [];
    const requests = [];
    page.on('pageerror', error => failures.push(String(error)));
    page.on('requestfailed', request => failures.push(request.url() + ': ' + request.failure()?.errorText));
    page.on('request', request => requests.push(request.url()));
    const response = await page.goto(url, {waitUntil: 'networkidle'});
    assert.equal(response.status(), 200);
    assert.equal(await page.locator('h1').count(), 1);
    assert.equal(await page.locator('section[id]').count(), 15);
    assert.ok((await page.locator('body').innerText()).includes('无需把模型加载进这个库'));
    report.checks.push('完整正文与单一主标题显示');

    for (const asset of ['styles.css', 'app.js', 'assets/understanding-overview.svg', 'assets/understanding-overview.png', 'assets/gateway-internals.svg', 'assets/gateway-internals.png', 'data/evaluation-template.txt']) {
      const resource = await page.request.get(new URL(asset, url).href);
      assert.equal(resource.status(), 200, asset);
      report.resources.push({path: asset, status: resource.status(), bytes: (await resource.body()).length});
    }
    const anchors = await page.locator('a[href^="#"]').evaluateAll(items => items.map(item => item.getAttribute('href').slice(1)));
    for (const anchor of anchors) assert.equal(await page.locator(`[id="${anchor}"]`).count(), 1, anchor);
    assert.equal(await page.locator('a[data-source]:not([href])').count(), 0);
    for (const picture of await page.locator('main img').all()) {
      await picture.scrollIntoViewIfNeeded();
      await picture.evaluate(image => image.decode());
    }
    assert.equal(await page.locator('main img').evaluateAll(items => items.every(item => item.complete && item.naturalWidth > 0)), true);
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    report.checks.push('章节锚点、固定版本来源、两张 SVG / PNG 和全部静态资源可用');
    await page.screenshot({path: path.join(root, 'assets/01-web-overview.png')});
    report.screenshots.push('assets/01-web-overview.png');

    await page.locator('#request-lab').scrollIntoViewIfNeeded();
    for (let step = 1; step < 6; step++) {
      await page.locator('#next-step').click();
      assert.equal(await page.locator('[data-step][aria-current="step"]').getAttribute('data-step'), String(step));
    }
    assert.ok((await page.locator('#step-title').innerText()).includes('再次交给模型'));
    await page.locator('#reset-lab').click();
    assert.equal(await page.locator('[data-step][aria-current="step"]').getAttribute('data-step'), '0');
    await page.locator('[data-agent="codex"]').click();
    assert.equal(await page.locator('#ingress-label').innerText(), '/v1/responses');
    assert.ok((await page.locator('#request-payload').innerText()).includes('"input"'));
    await page.locator('#model-select').selectOption('ollama');
    assert.equal(await page.locator('#target-label').innerText(), 'ollama/demo-model');
    await page.locator('#fallback-toggle').check();
    await page.locator('[data-step="1"]').click();
    assert.equal(await page.locator('#fallback-note').isVisible(), true);
    assert.ok((await page.locator('#step-title').innerText()).includes('备用'));
    assert.equal(await page.locator('#target-label').innerText(), 'backup/demo-model');
    await page.locator('[data-step="3"]').click();
    assert.ok((await page.locator('#request-payload').innerText()).includes('function_call'));
    const captureStyle = await page.addStyleTag({content: '.site-header,.skip-link{visibility:hidden!important}'});
    await page.locator('#request-lab').screenshot({path: path.join(root, 'assets/02-request-flow.png')});
    await captureStyle.evaluate(style => style.remove());
    report.screenshots.push('assets/02-request-flow.png');
    await page.locator('#fallback-toggle').uncheck();
    await page.locator('#reset-lab').click();
    await page.locator('#model-select').selectOption('custom');
    assert.equal(await page.locator('#target-label').innerText(), 'custom_demo/demo-model');
    report.checks.push('六步往返、重置、Codex 协议、本地与自定义模型、备用条件及工具响应切换');

    const faq = page.locator('#faq details').nth(1);
    await faq.locator('summary').click();
    assert.equal(await faq.getAttribute('open'), '');
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.locator('#evidence a[download="fcc-evaluation-template.csv"]').click()
    ]);
    assert.equal(download.suggestedFilename(), 'fcc-evaluation-template.csv');
    assert.equal(await download.failure(), null);
    report.checks.push('问答展开与 CSV 下载');

    const overviewLink = page.locator('#evidence a[download="fcc-understanding-overview.svg"]');
    const [imageDownload] = await Promise.all([page.waitForEvent('download'), overviewLink.click()]);
    assert.equal(imageDownload.suggestedFilename(), 'fcc-understanding-overview.svg');
    assert.equal(await imageDownload.failure(), null);
    report.checks.push('原创总览 SVG 下载');

    assert.ok((await page.locator('#essence').innerText()).includes('接入解耦'));
    assert.ok((await page.locator('#comparison').innerText()).includes('FreeLLMAPI'));
    assert.ok((await page.locator('#comparison').innerText()).includes('Thompson Sampling'));
    await page.locator('#understanding [data-diagram]').click();
    assert.equal(await page.locator('#diagram-dialog').isVisible(), true);
    assert.equal(await page.locator('#diagram-dialog-title').innerText(), '适配解耦：完整理解总览');
    const beforeZoom = Number.parseInt(await page.locator('#diagram-scale').innerText(), 10);
    await page.locator('#diagram-zoom-in').click();
    assert.ok(Number.parseInt(await page.locator('#diagram-scale').innerText(), 10) > beforeZoom);
    await page.locator('#diagram-fit').click();
    await page.locator('#diagram-close').click();
    assert.equal(await page.locator('#diagram-dialog').isVisible(), false);
    await page.locator('#gateway-internals [data-diagram]').click();
    assert.ok((await page.locator('#diagram-full-image').getAttribute('src')).includes('gateway-internals.svg'));
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#diagram-dialog').isVisible(), false);
    const moduleCaptureStyle = await page.addStyleTag({content: '.site-header,.skip-link{visibility:hidden!important}'});
    await page.locator('#gateway-internals').screenshot({path:path.join(root,'assets/05-gateway-internals-page.png')});
    await moduleCaptureStyle.evaluate(style=>style.remove());
    report.screenshots.push('assets/05-gateway-internals-page.png');
    for (const [selector,name] of [['#understanding a[download="fcc-understanding-overview.png"]','fcc-understanding-overview.png'],['#gateway-internals a[download="fcc-gateway-internals.png"]','fcc-gateway-internals.png'],['#gateway-internals a[download="fcc-gateway-internals.svg"]','fcc-gateway-internals.svg']]) {
      const [artifact] = await Promise.all([page.waitForEvent('download'),page.locator(selector).click()]);
      assert.equal(artifact.suggestedFilename(),name);
      assert.equal(await artifact.failure(),null);
    }
    report.checks.push('适配解耦和旧项目对比正文、双图放大/适应/关闭/键盘退出及全部图示下载');

    await page.setViewportSize({width: 390, height: 844});
    await page.goto(url, {waitUntil: 'networkidle'});
    const dimensions = await page.evaluate(() => ({width: innerWidth, scroll: document.documentElement.scrollWidth}));
    assert.ok(dimensions.scroll <= dimensions.width, JSON.stringify(dimensions));
    await page.screenshot({path: path.join(root, 'assets/03-mobile-overview.png')});
    report.screenshots.push('assets/03-mobile-overview.png');
    await page.locator('#request-lab').scrollIntoViewIfNeeded();
    await page.locator('[data-agent="codex"]').click();
    await page.locator('#model-select').selectOption('ollama');
    await page.locator('#next-step').click();
    assert.ok((await page.locator('#step-title').innerText()).includes('真实目标'));
    assert.equal(await page.locator('#ingress-label').innerText(), '/v1/responses');
    report.checks.push('390px 手机布局无全页横向溢出，交互可用');

    await page.locator('#understanding [data-diagram]').click();
    assert.equal(await page.locator('#diagram-dialog').isVisible(),true);
    await page.locator('#diagram-zoom-in').click();
    const scrollable=await page.locator('#diagram-viewport').evaluate(element=>element.scrollWidth>element.clientWidth && element.scrollHeight>element.clientHeight);
    assert.equal(scrollable,true);
    await page.screenshot({path:path.join(root,'assets/06-mobile-diagram-reader.png')});
    report.screenshots.push('assets/06-mobile-diagram-reader.png');
    await page.locator('#diagram-close').click();
    report.checks.push('手机大图可放大并双向滚动，关闭后返回正文');

    await page.setViewportSize({width: 1600, height: 2460});
    await page.goto(new URL('assets/understanding-overview.svg', url).href);
    await page.screenshot({path: path.join(root, 'assets/04-overview-render.png')});
    report.screenshots.push('assets/04-overview-render.png');

    const noScript = await browser.newPage({javaScriptEnabled: false, viewport: {width: 1280, height: 900}});
    assert.equal((await noScript.goto(url)).status(), 200);
    assert.equal(await noScript.locator('a[data-source]:not([href])').count(), 0);
    assert.ok((await noScript.locator('body').innerText()).includes('完整原理'));
    assert.ok((await noScript.locator('#value').innerText()).includes('研究价值'));
    report.checks.push('禁用 JavaScript 后正文、来源与原理说明仍可读');
    const localFile = 'file:///' + path.join(root, 'web/index.html').replaceAll('\\', '/');
    await noScript.goto(localFile);
    assert.ok((await noScript.locator('h1').innerText()).includes('通过网关解耦'));
    report.checks.push('保存的 HTML 文件可直接打开，静态正文不依赖预览服务器');
    assert.deepEqual(failures, []);
    assert.ok(requests.every(request => new URL(request).origin === new URL(url).origin));
    report.browser_errors = failures;
    report.external_requests = 0;
    report.result = 'passed';
    fs.mkdirSync(path.join(root, 'experiments/results'), {recursive: true});
    fs.writeFileSync(path.join(root, 'experiments/results/browser-checks.json'), JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify(report, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});
