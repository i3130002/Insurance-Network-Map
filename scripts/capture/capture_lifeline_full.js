const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');
const fs = require('fs');

function csv(value) { return `"${String(value ?? '').replaceAll('"', '""')}"`; }

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage();
    const requests = new Map();
    page.on('request', request => {
      if (request.url().includes('rpc/get_network_coverage')) {
        const body = JSON.parse(request.postData());
        requests.set(String(body.p_has_coords), request);
      }
    });
    for (const [slug, outputName] of [['empire', 'DNI Lifeline Empire Current'], ['pearl', 'DNI Lifeline Pearl Current'], ['sapphire', 'DNI Lifeline Sapphire Current']]) {
    await page.goto(`https://www.medifinder.ae/medical/networks/lifeline/${slug}`, { waitUntil: 'networkidle', timeout: 60000 });
    const buttons = page.getByRole('button', { name: /Load .* more/ });
    for (let i = 0; i < await buttons.count(); i += 1) {
      await buttons.nth(i).click();
      await page.waitForTimeout(600);
    }
    if (requests.size < 2) throw new Error(`expected two coverage requests, got ${requests.size}`);
    const providers = [];
    for (const request of requests.values()) {
      const body = JSON.parse(request.postData());
      body.p_page = 1;
      body.p_page_size = 1000;
      const headers = Object.fromEntries(Object.entries(await request.allHeaders()).filter(([key]) => !key.startsWith(':') && !['content-length', 'host'].includes(key)));
      const fetchPage = async pageNumber => {
        const response = await page.request.post(request.url(), { headers, data: { ...body, p_page: pageNumber } });
        if (!response.ok()) throw new Error(`RPC failed: ${response.status()}`);
        return response.json();
      };
      const first = await fetchPage(1);
      providers.push(...first.providers);
      for (let pageNumber = 2; pageNumber <= first.total_pages; pageNumber += 1) providers.push(...(await fetchPage(pageNumber)).providers);
    }
    const unique = new Map(providers.map(row => [`${row.canonical_name}|${row.emirate}|${row.region}`, row]));
    const lines = ['PROVIDER NAME,EMIRATE,PROVIDER TYPE,AREA,ADDRESS,TELEPHONE,lat,lon,SOURCE'];
    for (const row of unique.values()) lines.push([row.canonical_name, row.emirate, row.facility_type_norm, row.region, '', row.phone_norm, row.lat, row.lng, 'https://www.medifinder.ae/medical/networks/lifeline/empire'].map(csv).join(','));
    fs.writeFileSync(`sources/networks/${outputName}.csv`, `${lines.join('\n')}\n`);
    console.log(`${outputName}: merged ${unique.size} providers from ${providers.length} API rows`);
    requests.clear();
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
