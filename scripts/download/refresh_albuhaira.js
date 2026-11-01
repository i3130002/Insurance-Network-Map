const { chromium } = require('/tmp/nextcare-playwright/node_modules/playwright');
const fs = require('fs');

const tiers = [
  ['COMPREHENSIVE', 'Al Buhaira Comprehensive.csv'],
  ['COMPREHENSIVE PLUS', 'Al Buhaira Comprehensive Plus.csv'],
  ['LIMITED', 'Al Buhaira Limited.csv'],
  ['RESTRICTED', 'Al Buhaira Restricted.csv'],
  ['STANDARD', 'Al Buhaira Standard.csv'],
];

function decode(value) {
  return value.replace(/<[^>]+>/g, '').replace(/&amp;/g, '&')
    .replace(/&nbsp;/g, ' ').replace(/&#39;/g, "'").replace(/&quot;/g, ' ')
    .replace(/\s+/g, ' ').trim();
}

function rowsFromHtml(html) {
  return [...html.matchAll(/<tr>\s*(.*?)\s*<\/tr>/gs)].flatMap((match) => {
    const cells = [...match[1].matchAll(/<td[^>]*>(.*?)<\/td>/gs)]
      .map((cell) => decode(cell[1]));
    if (cells.length !== 8 || !/^\d+$/.test(cells[0])) return [];
    return [{
      'PROVIDER NAME': cells[5], EMIRATE: ({
        'ABU DHABI': 'AUH', DUBAI: 'DXB', SHARJAH: 'SHJ', AJMAN: 'AJM',
        FUJAIRAH: 'FUJ', 'RAS AL KHAIMAH': 'RAK', 'UMM AL QUWAIN': 'UMQ',
        'AL AIN': 'ALAIN',
      })[cells[2]] || cells[2], 'PROVIDER TYPE': '', AREA: '',
      ADDRESS: cells[7], TELEPHONE: cells[6],
    }];
  });
}

function csv(rows) {
  const fields = ['PROVIDER NAME', 'EMIRATE', 'PROVIDER TYPE', 'AREA', 'ADDRESS', 'TELEPHONE'];
  const quote = (value) => `"${String(value).replaceAll('"', '""')}"`;
  return `${fields.join(',')}\n${rows.map((row) => fields.map((field) => quote(row[field])).join(',')).join('\n')}\n`;
}

async function fetchTier(request, tier) {
  const first = await request.get(`https://albuhaira.com/medical-network?networkType=${encodeURIComponent(tier)}`);
  const html = await first.text();
  const pages = Math.max(1, ...[...html.matchAll(/networkType=[^"&]+(?:&amp;|&)page=(\d+)/g)].map((m) => Number(m[1])));
  const rows = [...rowsFromHtml(html)];
  for (let start = 2; start <= pages; start += 12) {
    const batch = await Promise.all(Array.from({ length: Math.min(12, pages - start + 1) }, (_, offset) =>
      request.get(`https://albuhaira.com/medical-network?networkType=${encodeURIComponent(tier)}&page=${start + offset}`)));
    for (const response of batch) rows.push(...rowsFromHtml(await response.text()));
  }
  return rows;
}

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  const context = await browser.newContext();
  for (const [tier, filename] of tiers) {
    const rows = await fetchTier(context.request, tier);
    fs.writeFileSync(`sources/networks/${filename}`, csv(rows));
    console.log(tier, rows.length, filename);
  }
  await browser.close();
})().catch((error) => { console.error(error); process.exitCode = 1; });
