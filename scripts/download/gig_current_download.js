const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  const context = await browser.newContext({ acceptDownloads: true });
  const page = await context.newPage();
  try {
    await page.goto('https://www.giggulf.ae/en-GB/personal/products/health-insurance/policy-documents', { waitUntil: 'domcontentloaded', timeout: 60000 });
    const links = page.locator('a');
    const labels = await links.allTextContents();
    console.log('network links', labels.filter((label) => /network|smart health|signature/i.test(label)).slice(0, 30));
    const candidates = page.getByRole('link', { name: /network list/i });
    console.log('candidate count', await candidates.count());
    for (let i = 0; i < await candidates.count(); i += 1) {
      const downloadPromise = page.waitForEvent('download', { timeout: 15000 }).catch(() => null);
      await candidates.nth(i).click({ noWaitAfter: true }).catch(() => null);
      const download = await downloadPromise;
      if (!download) continue;
      const body = await download.createReadStream();
      const chunks = [];
      for await (const chunk of body) chunks.push(chunk);
      const data = Buffer.concat(chunks);
      if (!data.length) continue;
      const path = `/home/tony/Documents/Projects/Temp/Insurance Network Map/sources/raw/GIG Current Network ${i + 1}.pdf`;
      fs.writeFileSync(path, data);
      console.log('saved', path, data.length);
    }
  } finally { await browser.close(); }
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
