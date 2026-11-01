const { chromium } = require('/tmp/nextcare-playwright/node_modules/playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  let captured = false;
  page.on('response', async (response) => {
    if (!response.url().includes('/rest/v1/networks')) return;
    fs.writeFileSync('/tmp/medifinder-networks.json', await response.body());
    captured = true;
  });
  await page.goto('https://www.medifinder.ae/medical/networks/daman/royal-ww', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(5000);
  console.log('captured', captured);
  await browser.close();
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
