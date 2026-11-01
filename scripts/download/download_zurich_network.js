const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');
const fs = require('fs');

async function main() {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  try {
    const context = await browser.newContext();
    const response = await context.request.get('https://edge.sitecorecloud.io/zurichinsurf8c0-zwpshared-prod-d824/media/project/zurich-headless/middle-east/documents/adviser-suite/0522/me-medical-providers-panel-list.pdf');
    if (!response.ok()) throw new Error(`download failed: ${response.status()}`);
    fs.writeFileSync('sources/raw/Zurich ME Medical Providers Panel Current.pdf', await response.body());
    console.log(`saved (${response.status()})`);
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
