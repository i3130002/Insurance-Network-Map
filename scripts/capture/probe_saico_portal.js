const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  const requests = [];
  page.on('request', request => {
    const url = request.url();
    if (/api|provider|network|search/i.test(url)) requests.push(`${request.method()} ${url}`);
  });
  await page.goto('https://health.damana.com', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(5000);
  console.log('title', await page.title());
  console.log('url', page.url());
  console.log(requests.slice(0, 30).join('\n'));
  await browser.close();
})().catch(error => { console.error(error.message); process.exitCode = 1; });
