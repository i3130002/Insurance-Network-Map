const { chromium } = require('/tmp/nextcare-playwright/node_modules/playwright');
const fs = require('fs');

function csv(value) {
  return `"${String(value || '').replaceAll('"', '""')}"`;
}

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.goto('https://www.medifinder.ae/medical/networks/daman/royal-ww', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(2500);
  for (let attempt = 0; attempt < 200; attempt += 1) {
    const button = page.locator('button').filter({ hasText: /^Load \d+ more$/ }).first();
    if (!(await button.count())) break;
    await button.click({ force: true });
    await page.waitForTimeout(1500);
  }
  const records = await page.locator('a[href*="/medical/providers/"]').evaluateAll((anchors) => {
    const emirates = { Dubai: 'DXB', 'Abu Dhabi': 'AUH', Sharjah: 'SHJ', Ajman: 'AJM', Fujairah: 'FUJ', 'Ras Al Khaimah': 'RAK', 'Umm Al Quwain': 'UMQ' };
    const seen = new Set();
    return anchors.flatMap((anchor) => {
      let card = anchor;
      while (card && (!card.innerText.includes('Directions') || card.querySelectorAll('a[href*="/medical/providers/"]').length !== 1)) card = card.parentElement;
      if (!card) return [];
      const lines = card.innerText.split('\n').map((line) => line.trim()).filter(Boolean);
      const key = anchor.getAttribute('href');
      if (!key || seen.has(key)) return [];
      seen.add(key);
      const location = lines.find((line) => emirates[line]);
      const type = lines.find((line) => ['Hospital', 'Clinic', 'Pharmacy', 'Dental', 'Healthcare Facility', 'Diagnostics'].includes(line));
      return [{ name: lines[0], emirate: emirates[location] || '', type: type || '', address: '', phone: '' }];
    });
  });
  const header = 'PROVIDER NAME,EMIRATE,PROVIDER TYPE,AREA,ADDRESS,TELEPHONE\n';
  const body = records.map((r) => [r.name, r.emirate, r.type, '', r.address, r.phone].map(csv).join(',')).join('\n');
  fs.writeFileSync('sources/networks/Daman Royal WW MediFinder July 2026.csv', header + body + '\n');
  console.log('records', records.length);
  await browser.close();
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
