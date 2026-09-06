const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  try {
    const context = await browser.newContext();
    const response = await context.request.get('https://www.aesinternational.com/hubfs/Employee%20benefits/Now%20Health/MEA%20Network%20List.pdf', { timeout: 60000 });
    if (!response.ok()) throw new Error(`download failed: ${response.status()}`);
    fs.writeFileSync('sources/raw/Now Health MEA Network List Reference.pdf', await response.body());
    console.log('saved Now Health MEA Network List Reference.pdf');
  } finally { await browser.close(); }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
