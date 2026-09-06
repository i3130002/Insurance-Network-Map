const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  try {
    const context = await browser.newContext();
    const url = 'https://www.cigna-me.com/static/cigna-rebranding/pdf/cigna-me/en/Cigna-EBP-Network.pdf';
    const response = await context.request.get(url, { timeout: 60000 });
    console.log('status', response.status(), 'type', response.headers()['content-type']);
    if (!response.ok()) throw new Error(`download failed: ${response.status()}`);
    fs.writeFileSync('sources/raw/Cigna EBP Network Current.pdf', await response.body());
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
