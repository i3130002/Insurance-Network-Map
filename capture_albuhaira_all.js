const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');
const fs = require('fs');

const output = 'sources/networks/Al Buhaira Medical Network Current.csv';

async function main() {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage();
    const stream = fs.createWriteStream(output);
    stream.write('NETWORK,EMIRATE,SPECIALITY,DOCTOR,PROVIDER,TELEPHONE,LOCATION,SOURCE\n');
    for (let number = 1; number <= 2557; number += 1) {
      await page.goto(`https://albuhaira.com/medical-network?page=${number}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
      const rows = await page.locator('table tbody tr').evaluateAll(items => items.map(row =>
        Array.from(row.querySelectorAll('td')).map(cell => cell.textContent.trim().replace(/\s+/g, ' '))));
      for (const row of rows) {
        if (row.length < 8) continue;
        // The first cell is the serial number. Keep the seven network fields.
        stream.write([...row.slice(1, 8), 'https://albuhaira.com/medical-network'].map(value =>
          `"${value.replaceAll('"', '""')}"`).join(',') + '\n');
      }
      if (number % 100 === 0) console.log(`Checkpoint ${number}; rows ${rows.length}`);
    }
    stream.end();
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
