const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');
const fs = require('fs');

const OUTPUT = process.env.OUTPUT || 'sources/networks/MEDGULF Assigned Providers UAE Current.csv';

async function readRows(page, tpa) {
  return page.locator('table').last().locator('tr').evaluateAll((rows, network) => rows.slice(1)
    .map(row => [...row.cells].map(cell => cell.innerText.trim()))
    .filter(row => row.length >= 8 && row[1])
    .map(row => ({ network, city: row[1], type: row[2], name: row[3], area: row[4], address: row[5], phone: row[6], remarks: row[7] })), tpa);
}

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  const all = [];
  try {
    for (const tpa of process.env.TPA ? [process.env.TPA] : ['Nextcare', 'NAS', 'Mednet', 'Neuron']) {
      await page.goto('https://www.medgulf.ae/Network-List', { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.selectOption('#ContentPlaceHolder1_ddlnetwork', tpa);
      await page.waitForTimeout(2500);
      const country = page.locator('#ContentPlaceHolder1_ddlcountry option').filter({ hasText: /^(UAE|United Arab Emirates)$/ });
      await country.waitFor({ state: 'attached', timeout: 30000 });
      await page.selectOption('#ContentPlaceHolder1_ddlcountry', { label: await country.first().innerText() });
      await page.waitForTimeout(1800);
      for (let pageNo = 1; pageNo <= 100; pageNo += 1) {
        const rows = await readRows(page, tpa);
        all.push(...rows);
        const next = page.locator('a').filter({ hasText: String(pageNo + 1) }).last();
        if (!(await next.count()) || !(await next.isVisible())) break;
        await next.click();
        await page.waitForTimeout(1200);
      }
      console.log(tpa, all.filter(row => row.network === tpa).length);
    }
  } finally { await browser.close(); }
  const fields = ['network', 'city', 'type', 'name', 'area', 'address', 'phone', 'remarks'];
  const csv = [fields.join(','), ...all.map(row => fields.map(field => JSON.stringify(row[field] || '')).join(','))].join('\n') + '\n';
  fs.writeFileSync(OUTPUT, csv);
  console.log('saved', OUTPUT, all.length);
})().catch(error => { console.error(error); process.exitCode = 1; });
