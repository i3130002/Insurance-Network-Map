const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  const requests = [];
  page.on('response', async (response) => {
    if (response.url().includes('/Search/SearchResults')) console.log('search response', response.status(), (await response.body()).length);
  });
  page.on('request', (request) => {
    const url = request.url();
    if (/api|provider|network|locator|medical/i.test(url)) requests.push(`${request.method()} ${url}`);
  });
  try {
    await page.goto('https://locator.gig-gulf.com/Search/SearchPage?country=UAE', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(5000);
    console.log('title', await page.title());
    console.log('controls', await page.locator('select,input,button').count());
    console.log('selects', await page.locator('select').evaluateAll((items) => items.map((item) => ({ name: item.name, id: item.id, options: [...item.options].slice(0, 12).map((option) => option.textContent.trim()) }))));
    console.log('buttons', await page.locator('button,input[type=button],input[type=submit]').evaluateAll((items) => items.map((item) => ({ id: item.id, value: item.value, text: item.textContent.trim() }))));
    console.log('search text count', await page.getByText(/search/i).count());
    const scriptUrls = await page.locator('script[src]').evaluateAll((items) => items.map((item) => item.src));
    for (const url of scriptUrls) {
      const source = await page.evaluate(async (scriptUrl) => (await fetch(scriptUrl)).text(), url).catch(() => '');
      const matches = source.match(/[^"'` ]*(?:provider|network|search|facility)[^"'` ]*/gi) || [];
      if (matches.length) console.log('script', url, [...new Set(matches)].slice(0, 30));
    }
    await page.selectOption('#ddlCountries', { label: 'United Arab Emirates' });
    await page.waitForTimeout(1500);
    await page.selectOption('#ddlCities', { label: 'All' });
    await page.selectOption('#ddlNetwork', { index: 1 });
    await page.evaluate(() => SearchResults('', 'List'));
    await page.waitForTimeout(5000);
    console.log('result rows', await page.locator('table tr').count(), 'cards', await page.locator('.provider-list, .provider-item').count());
    const firstNames = await page.locator('.pharmacy-name').allTextContents();
    await page.evaluate(() => getPage('Next'));
    await page.waitForTimeout(3000);
    console.log('next names', (await page.locator('.pharmacy-name').allTextContents()).slice(0, 2), 'changed', firstNames[0] !== (await page.locator('.pharmacy-name').first().textContent()));
    console.log('body', (await page.locator('body').innerText()).slice(0, 1500));
    console.log('requests', [...new Set(requests)].slice(0, 80));
  } finally {
    await browser.close();
  }
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
