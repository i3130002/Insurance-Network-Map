const { chromium } = require('/tmp/nextcare-playwright/node_modules/playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  const context = await browser.newContext({ acceptDownloads: true });
  const page = await context.newPage();
  try {
    await page.goto('https://adamjeeinsurance.ae/family-care/', { waitUntil: 'domcontentloaded', timeout: 60000 });
    const link = page.getByText('Network List July 2023', { exact: true });
    console.log('links', await link.count());
    const downloadPromise = page.waitForEvent('download', { timeout: 30000 });
    await link.first().click({ noWaitAfter: true });
    const download = await downloadPromise;
    const stream = await download.createReadStream();
    const chunks = [];
    for await (const chunk of stream) chunks.push(chunk);
    const body = Buffer.concat(chunks);
    if (!body.length) throw new Error('empty download');
    const path = '/home/tony/Documents/Projects/Temp/Insurance Network Map/sources/raw/Adamjee MedNet Network List July 2023.pdf';
    fs.writeFileSync(path, body);
    console.log('saved bytes', body.length);
  } finally { await browser.close(); }
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
