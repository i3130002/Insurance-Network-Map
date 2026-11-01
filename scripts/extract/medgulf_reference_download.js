const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  try {
    const context = await browser.newContext();
    const response = await context.request.get('https://erp.daambroker.com.sa/Files/Providers%20list%20Medgulf%20globla.pdf', { timeout: 60000 });
    console.log('status', response.status(), 'type', response.headers()['content-type']);
    if (!response.ok()) throw new Error(`download failed: ${response.status()}`);
    require('fs').writeFileSync('sources/raw/MEDGULF Provider List Broker Archive.pdf', await response.body());
    console.log('saved reference PDF');
  } finally { await browser.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });
