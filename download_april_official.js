const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');
const fs = require('fs');

async function main() {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  try {
    const context = await browser.newContext();
    const response = await context.request.get('https://assets.april.fr/april-international/Network/zip-network-april-insurance-middle-east-network-list-en.zip');
    if (!response.ok()) throw new Error(`download failed: ${response.status()}`);
    fs.writeFileSync('sources/raw/APRIL International Middle East Network Official.zip', await response.body());
    console.log(`saved (${response.status()}, ${response.headers()['content-length'] || 'unknown'} bytes)`);
  } finally { await browser.close(); }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
