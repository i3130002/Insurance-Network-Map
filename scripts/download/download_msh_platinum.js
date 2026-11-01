const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  try {
    const response = await (await browser.newContext()).request.get('https://laplace-groupe.com/documents/pdf/265/emiratexpatsante-reseau-platinium-msh.pdf', { timeout: 60000 });
    if (!response.ok()) throw new Error(`download failed: ${response.status()}`);
    fs.writeFileSync('sources/raw/MSH UAE Platinum Network Reference.pdf', await response.body());
    console.log('saved MSH UAE Platinum Network Reference.pdf');
  } finally { await browser.close(); }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
