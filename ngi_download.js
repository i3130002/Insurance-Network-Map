const { chromium } = require('/tmp/nextcare-playwright/node_modules/playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('https://ngi.ae/downloads/', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(1500);
  const plans = page.getByText('HealthNet Plans', { exact: true });
  for (let index = 0; index < await plans.count(); index += 1) {
    const link = plans.nth(index).locator('xpath=..').locator('a').nth(1);
    const action = await link.getAttribute('onclick');
    const match = action && action.match(/(?:https?:)?[^"' ]+\.(?:pdf|xlsx)(?:[^"' ]*)?/i);
    if (!match) throw new Error(`Missing network target ${index}`);
    const response = await context.request.get(new URL(match[0], 'https://ngi.ae').toString());
    if (!response.ok()) throw new Error(`HTTP ${response.status()} for network ${index}`);
    const name = ['Abu Dhabi', 'Dubai', 'Northern Emirates'][index];
    fs.writeFileSync(`sources/raw/NGI HealthNet ${name} Network.pdf`, await response.body());
    console.log(name, (await response.body()).length);
  }
  await browser.close();
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
