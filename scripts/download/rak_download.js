const { chromium } = require('/tmp/nextcare-playwright/node_modules/playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  const context = await browser.newContext({ acceptDownloads: true });
  const page = await context.newPage();
  try {
    await page.goto('https://www.rakinsurance.com/product/medical', { waitUntil: 'domcontentloaded', timeout: 60000 });
    const candidates = page.getByText(/MedNet.*Network List/i);
    console.log('candidates', await candidates.count());
    const downloadPromise = page.waitForEvent('download', { timeout: 30000 }).catch(() => null);
    await candidates.first().click({ noWaitAfter: true });
    const download = await downloadPromise;
    if (!download) throw new Error('no download event');
    const path = '/home/tony/Documents/Projects/Temp/Insurance Network Map/sources/raw/RAK Insurance MedNet UAE Network List.xlsx';
    const stream = await download.createReadStream();
    const chunks = [];
    for await (const chunk of stream) chunks.push(chunk);
    const body = Buffer.concat(chunks);
    if (!body.length) throw new Error(`empty download: ${download.failure()}`);
    fs.writeFileSync(path, body);
    console.log('saved', path, download.suggestedFilename(), body.length);
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
