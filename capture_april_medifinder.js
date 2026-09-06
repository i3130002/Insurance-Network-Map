const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');
const fs = require('fs');
const tier = process.argv[2] || 'classic';
const output = `sources/raw/April International ${tier} MediFinder Current.html`;

async function main() {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage();
    await page.goto(`https://www.medifinder.ae/medical/networks/april-international/${tier}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(8000);
    for (let i = 0; i < 120; i += 1) {
      const controls = page.getByRole('button', { name: /Load \d+ more/ });
      if (!(await controls.count())) break;
      const loadMore = controls.last();
      await loadMore.click();
      await page.waitForTimeout(1200);
      if (i % 5 === 4) {
        fs.writeFileSync(output, await page.content());
        console.log('checkpoint', i + 1, await page.locator('h3').count());
      }
    }
    fs.writeFileSync(output, await page.content());
    console.log('saved', await page.locator('h3').count(), 'cards');
    console.log('controls', await page.locator('button').allTextContents());
    console.log('load contexts', await page.getByRole('button', { name: /Load \d+ more/ }).evaluateAll(nodes => nodes.map(node => {
      let current = node;
      for (let i = 0; i < 4 && current; i += 1) current = current.parentElement;
      return current?.innerText.slice(0, 180);
    })));
    const cards = await page.locator('h3').evaluateAll(nodes => nodes.slice(0, 3).map(node => {
      let current = node;
      for (let i = 0; i < 5 && current; i += 1) current = current.parentElement;
      return current?.innerText;
    }));
    console.log(JSON.stringify(cards));
  } finally { await browser.close(); }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
