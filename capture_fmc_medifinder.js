const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');
const fs = require('fs');

const networks = [
  ['standard-network-3', 'FMC Standard Network 3'],
  ['standard-network-2', 'FMC Standard Network 2'],
];

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage();
    for (const [slug, network] of networks) {
      await page.goto(`https://www.medifinder.ae/medical/networks/fmc/${slug}`, { waitUntil: 'networkidle', timeout: 60000 });
      while (await page.getByRole('button', { name: /Load .* more/ }).count()) {
        await page.getByRole('button', { name: /Load .* more/ }).first().click();
        await page.waitForTimeout(300);
      }
      const rows = await page.locator('h3 a').evaluateAll(links => links.map(link => {
        let card = link;
        for (let i = 0; i < 5; i += 1) card = card.parentElement;
        const meta = card.querySelector('[data-testid="mobile-card-meta"]');
        const type = card.querySelector('[data-testid="mobile-card-treatment"]');
        return { provider: link.textContent.trim(), meta: meta?.textContent.trim() || '', type: type?.textContent.trim() || '' };
      }));
      const output = `sources/networks/${network}.csv`;
      const lines = ['PROVIDER NAME,EMIRATE,PROVIDER TYPE,AREA,ADDRESS,TELEPHONE,SOURCE'];
      for (const row of rows) lines.push([row.provider, row.meta, row.type, '', '', '', `https://www.medifinder.ae/medical/networks/fmc/${slug}`].map(value => `"${value.replaceAll('"', '""')}"`).join(','));
      fs.writeFileSync(output, `${lines.join('\n')}\n`);
      console.log(`${network}: ${rows.length}`);
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
