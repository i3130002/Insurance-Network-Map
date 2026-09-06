const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');
const fs = require('fs');

const OUT = 'sources/networks';
const TIERS = [
  ['A.2', '15', 'Outpatient'], ['A.3', '17', 'Outpatient'],
  ['A.4', '23', 'Outpatient'], ['A.5', '26', 'Outpatient'], ['A.6', '29', 'Outpatient'],
];

function csv(value) { return `"${String(value ?? '').replaceAll('"', '""')}"`; }

async function capture(page, name, code, treatment) {
  await page.selectOption('#ddlNetwork', code);
  await page.selectOption('#ddlTreatment', treatment);
  await page.evaluate(() => { sPageActual = 1; sResultsPerPage = 0; });
  await Promise.all([
    page.waitForResponse((response) => response.url().includes('/Search/SearchResults'), { timeout: 30000 }),
    page.evaluate(() => SearchResults('', 'List')),
  ]);
  await page.waitForTimeout(2500);
  const total = Number(await page.locator('#hdnResults').getAttribute('value'));
  const rows = new Map();
  for (let pageNo = 1; pageNo <= Math.ceil(total / 10); pageNo += 1) {
    if (pageNo > 1) {
      await page.evaluate(() => getPage('Next'));
      await page.waitForTimeout(700);
    }
    const batch = await page.locator('.pharmacy-card').evaluateAll((cards) => cards.map((card) => ({
      name: card.querySelector('.pharmacy-name')?.textContent.trim() || '',
      phone: card.querySelector('.phone-number')?.textContent.trim() || '',
      address: card.querySelector('.pharmacy-address')?.textContent.trim() || '',
    })));
    for (const row of batch) rows.set(`${row.name}|${row.address}`, row);
    if (pageNo % 25 === 0) console.log(name, pageNo, rows.size, '/', total);
  }
  const lines = ['PROVIDER NAME,EMIRATE,PROVIDER TYPE,AREA,ADDRESS,TELEPHONE'];
  for (const row of rows.values()) lines.push([row.name, '', '', '', row.address, row.phone].map(csv).join(','));
  fs.writeFileSync(`${OUT}/GIG Gulf ${name} Current.csv`, `${lines.join('\n')}\n`);
  console.log('saved', name, rows.size, 'reported', total);
}

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  try {
    await page.goto('https://locator.gig-gulf.com/Search/SearchPage?country=UAE', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(1500);
    await page.selectOption('#ddlCountries', { label: 'United Arab Emirates' });
    await page.waitForTimeout(1500);
    await page.selectOption('#ddlCities', { label: 'All' });
    for (const tier of TIERS) {
      if (tier !== TIERS[0]) {
        await page.reload({ waitUntil: 'domcontentloaded', timeout: 60000 });
        await page.waitForTimeout(1500);
        await page.selectOption('#ddlCountries', { label: 'United Arab Emirates' });
        await page.waitForTimeout(1500);
        await page.selectOption('#ddlCities', { label: 'All' });
      }
      await capture(page, tier[0], tier[1], tier[2]);
    }
  } finally { await browser.close(); }
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
