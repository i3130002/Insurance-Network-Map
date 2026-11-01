const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  try {
    const context = await browser.newContext();
    const response = await context.request.get('https://www.allianzcare.com/content/dam/onemarketing/azcare/allianzcare/en/docs/DOC-IBG-Dubai-Northern-Emirates-EN-0126.pdf', { timeout: 60000 });
    console.log('status', response.status(), 'type', response.headers()['content-type']);
    if (!response.ok()) throw new Error(`download failed: ${response.status()}`);
    require('fs').writeFileSync('sources/raw/Allianz Dubai Northern Emirates Benefit Guide January 2026.pdf', await response.body());
    console.log('saved factsheet');
  } finally { await browser.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });
