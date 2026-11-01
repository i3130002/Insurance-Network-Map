const { chromium } = require('/tmp/nextcare-playwright/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  try {
    const context = await browser.newContext();
    const response = await context.request.get('https://www.aesinternational.com/hubfs/Employee%20benefits/Allianz/Allianz%20Network%20List%20in%20the%20UAE.pdf', { timeout: 60000 });
    console.log('status', response.status(), 'type', response.headers()['content-type']);
    if (!response.ok()) throw new Error(`download failed: ${response.status()}`);
    require('fs').writeFileSync('sources/raw/Allianz Network List UAE Intermediary Reference.pdf', await response.body());
    console.log('saved reference PDF');
  } finally { await browser.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });
