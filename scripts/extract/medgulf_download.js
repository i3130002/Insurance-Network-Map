const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/snap/bin/brave',
    args: ['--no-sandbox'],
  });
  try {
    const context = await browser.newContext({ acceptDownloads: true });
    const page = await context.newPage();
    await page.goto('https://www.medgulf.ae/Network-List', {
      waitUntil: 'domcontentloaded',
      timeout: 60000,
    });
    require('fs').writeFileSync('sources/raw/MEDGULF Network List Current.html', await page.content());
    console.log('saved page source');
    const links = page.getByRole('link', { name: 'Download All Network List' });
    console.log('links', await links.count());
    console.log('hrefs', await links.evaluateAll((els) => els.map((el) => {
      const url = new URL(el.href);
      return `${url.origin}${url.pathname}`;
    })));
    console.log('forms', await page.locator('form').count());
    console.log('controls', await page.locator('input,button').evaluateAll((els) =>
      els.map((el) => `${el.tagName}:${el.getAttribute('type') || ''}:${el.getAttribute('name') || ''}`)
    ));
    page.on('download', async (download) => {
      const path = 'sources/raw/Medgulf All Network List.xls';
      await download.saveAs(path);
      console.log('saved', path);
    });
    page.on('request', (request) => {
      if (request.method() !== 'GET') console.log('request', request.method(), new URL(request.url()).pathname);
    });
    const formData = await page.locator('form').last().evaluate((form) => {
      const data = new URLSearchParams();
      for (const element of form.elements) {
        if (element.name && (element.type !== 'checkbox' || element.checked)) {
          data.append(element.name, element.value || '');
        }
      }
      data.set('__EVENTTARGET', 'ctl00$ContentPlaceHolder1$LinkButton2');
      data.set('__EVENTARGUMENT', '');
      return data.toString();
    });
    const cookies = (await context.cookies(page.url())).map((cookie) => `${cookie.name}=${cookie.value}`).join('; ');
    const response = await context.request.post(new URL(await page.locator('form').first().getAttribute('action'), page.url()).href, {
      headers: {
        'content-type': 'application/x-www-form-urlencoded',
        cookie: cookies,
        referer: page.url(),
        'user-agent': await page.evaluate(() => navigator.userAgent),
      },
      data: formData,
      timeout: 60000,
    });
    console.log('postback response', response.status(), response.headers()['content-type']);
    if (!response.ok()) throw new Error(`postback failed: ${response.status()}`);
    const path = 'sources/raw/Medgulf All Network List.xls';
    const contentType = response.headers()['content-type'] || '';
    if (!contentType.includes('text/html')) {
      require('fs').writeFileSync(path, await response.body());
      console.log('saved', path);
    } else {
      console.log('postback returned HTML; no workbook payload');
    }
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
