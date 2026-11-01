const { chromium } = require('/tmp/nextcare-playwright/node_modules/playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  try {
    await page.goto('https://mednet.com/members/locateprovider', { waitUntil: 'networkidle', timeout: 60000 });
    const token = await page.locator('meta[name="csrf-token"]').getAttribute('content');
    const request = (pageNumber) => page.evaluate(async ({ token, page }) => {
      const response = await fetch('/members/locateprovider/fetch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest', 'X-CSRF-TOKEN': token },
        body: JSON.stringify({ keyword: '', facilities: [], specialities: [], page, per_page: 100, view_mode: 'list' }),
      });
      return { status: response.status, body: await response.text() };
    }, { token, page: pageNumber });
    fs.mkdirSync('/tmp/mednet-pages', { recursive: true });
    const first = await request(1);
    const total = [...first.body.matchAll(/fetch\?page=(\d+)/g)].map((m) => Number(m[1])).reduce((a, b) => Math.max(a, b), 1);
    for (let pageNumber = 1; pageNumber <= total; pageNumber += 1) {
      const item = pageNumber === 1 ? first : await request(pageNumber);
      if (item.status !== 200) throw new Error(`page ${pageNumber}: HTTP ${item.status}`);
      fs.writeFileSync(`/tmp/mednet-pages/${pageNumber}.html`, item.body);
    }
    console.log('captured pages', total);
  } finally { await browser.close(); }
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
