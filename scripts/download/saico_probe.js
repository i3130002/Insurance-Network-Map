const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage();
    page.on('response', response => {
      const url = response.url();
      if (url.includes('api') || url.includes('provider') || url.includes('network')) console.log('response', response.status(), url);
    });
    await page.goto('https://providers.damana.com/', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(8000);
    console.log('url', page.url());
    console.log('title', await page.title());
    console.log('hostname', new URL(page.url()).hostname);
    console.log('links', await page.locator('a').count(), 'forms', await page.locator('form').count(), 'inputs', await page.locator('input').count(), 'buttons', await page.locator('button').count());
    console.log('body', (await page.locator('body').innerText()).slice(0, 1000));
  } finally { await browser.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });
