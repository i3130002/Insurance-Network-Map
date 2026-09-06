const { chromium } = require('/tmp/nextcare-playwright/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage();
    await page.goto('https://www.medgulf.ae/Network-List', { waitUntil: 'domcontentloaded', timeout: 60000 });
    for (const [selector, value] of [
      ['#ContentPlaceHolder1_ddlnetwork', 'Nextcare'],
      ['#ContentPlaceHolder1_ddlcountry', 'UAE'],
      ['#ContentPlaceHolder1_ddlcity', 'Dubai'],
      ['#ContentPlaceHolder1_ddlarea', 'AL AROBA ST'],
      ['#ContentPlaceHolder1_ddltype', 'Clinic'],
    ]) {
      await page.locator(selector).selectOption({ label: value });
      await page.waitForTimeout(2500);
    }
    console.log('tables', await page.locator('table').count(), 'rows', await page.locator('table tr').count());
  } finally { await browser.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });
