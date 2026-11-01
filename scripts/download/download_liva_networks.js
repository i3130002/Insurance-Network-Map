const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');
const fs = require('fs');

const files = [
  ['Inayah - Network List - Aug - 2026.xlsb', 'https://www.livainsurance.ae/sites/default/files/2026-08/Inayah%20-%20Network%20List%20-%20Aug%20-%202026.xlsb'],
  ['NAS - Network List - Aug - 2026.xlsx', 'https://www.livainsurance.ae/sites/default/files/2026-08/NAS%20-%20Network%20List%20-%20Aug%20-%202026.xlsx'],
  ['NAS - Network List - Aug - 2026 - Workers Lite Network.xlsx', 'https://www.livainsurance.ae/sites/default/files/2026-08/NAS%20-%20Network%20List%20-%20Aug%20-%202026%20-%20Workers%20Lite%20Network.xlsx'],
  ['NAS - Network List - Aug - 2026 - ValueLite Network.xlsx', 'https://www.livainsurance.ae/sites/default/files/2026-08/NAS%20-%20Network%20List%20-%20Aug%20-%202026%20-%20ValueLite%20Network.xlsx'],
  ['NAS - Network List - Aug - 2026 - Value Network.xlsx', 'https://www.livainsurance.ae/sites/default/files/2026-08/NAS%20-%20Network%20List%20-%20Aug%20-%202026%20-%20Value%20Network.xlsx'],
  ['Neuron - Network List - Aug - 2026.xlsx', 'https://www.livainsurance.ae/sites/default/files/2026-08/Neuron%20-%20Network%20List%20-%20Aug%20-%202026_0.xlsx'],
  ['Al Madallah - Network List - Aug - 2026.xlsx', 'https://www.livainsurance.ae/sites/default/files/2026-08/Al%20Madallah%20-%20Network%20List%20-%20Aug%20-%202026.xlsx'],
  ['Mednet - International Network List - Aug - 2026.xlsx', 'https://www.livainsurance.ae/sites/default/files/2026-08/Mednet%20-%20International%20Network%20List%20-%20Aug%20-%202026.xlsx'],
  ['Mednet - Network List - Aug - 2026.xlsx', 'https://www.livainsurance.ae/sites/default/files/2026-08/Mednet%20-%20Network%20List%20-%20Aug%20-%202026.xlsx'],
  ['NextCare - Network List - Aug - 2026.xlsx', 'https://www.livainsurance.ae/sites/default/files/2026-08/NextCare%20-%20Network%20List%20-%20Aug%20-%202026.xlsx'],
];

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  const request = await browser.newContext();
  try {
    for (const [name, url] of files) {
      const response = await request.request.get(url, { timeout: 60000 });
      console.log(name, response.status(), response.headers()['content-type']);
      if (!response.ok()) continue;
      fs.writeFileSync(`sources/raw/Liva ${name}`, await response.body());
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
