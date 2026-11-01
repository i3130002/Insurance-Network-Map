const { chromium } = require('/tmp/nextcare-playwright/node_modules/playwright');
const fs = require('fs');

function csv(value) { return `"${String(value || '').replaceAll('"', '""')}"`; }

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.goto('https://www.medifinder.ae/medical/networks/daman/visitors-plan', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(2500);
  const records = await page.locator('a[href*="/medical/providers/"]').evaluateAll((anchors) => {
    const emirates = { Dubai: 'DXB', 'Abu Dhabi': 'AUH', Sharjah: 'SHJ', Ajman: 'AJM', Fujairah: 'FUJ', 'Ras Al Khaimah': 'RAK', 'Umm Al Quwain': 'UMQ' };
    const types = ['Hospital', 'Clinic', 'Pharmacy', 'Dental', 'Healthcare Facility', 'Diagnostics'];
    const seen = new Set();
    return anchors.flatMap((anchor) => {
      let card = anchor;
      while (card && (!card.innerText.includes('Directions') || card.querySelectorAll('a[href*="/medical/providers/"]').length !== 1)) card = card.parentElement;
      if (!card) return [];
      const lines = card.innerText.split('\n').map((line) => line.trim()).filter(Boolean);
      const key = anchor.getAttribute('href');
      if (!key || seen.has(key)) return [];
      seen.add(key);
      return [{ name: lines[0], emirate: emirates[lines.find((line) => emirates[line])] || '', type: lines.find((line) => types.includes(line)) || '' }];
    });
  });
  const rows = records.map((r) => [r.name, r.emirate, r.type, '', '', ''].map(csv).join(','));
  fs.writeFileSync('sources/networks/Daman Visitors Plan MediFinder July 2026.csv', `PROVIDER NAME,EMIRATE,PROVIDER TYPE,AREA,ADDRESS,TELEPHONE\n${rows.join('\n')}\n`);
  console.log('records', records.length);
  await browser.close();
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
