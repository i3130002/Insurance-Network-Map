const { chromium } = require('/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');
const fs = require('fs');

const tiers = [
  ['fmc', 'standard-network', 'FMC Standard Network'],
  ['fmc', 'standard-network-3', 'FMC Standard Network 3'],
  ['fmc', 'standard-network-2', 'FMC Standard Network 2'],
  ['dubai-care', 'n1', 'Dubai Care N1'],
  ['dubai-care', 'n2-exclusive', 'Dubai Care N2 Exclusive'],
  ['dubai-care', 'n2', 'Dubai Care N2'],
  ['dubai-care', 'n3', 'Dubai Care N3'],
  ['dubai-care', 'n4', 'Dubai Care N4'],
  ['dubai-care', 'n5-enhanced', 'Dubai Care N5 Enhanced'],
  ['dubai-care', 'enhanced-n5-op', 'Dubai Care Enhanced N5 OP'],
  ['dubai-care', 'n5-op', 'Dubai Care N5 OP'],
  ['dubai-care', 'n5-ip', 'Dubai Care N5 IP'],
  ['lifeline', 'empire', 'DNI Lifeline Empire Current'],
  ['e-care', 'blue', 'E-Care Blue Current'],
  ['e-care', 'green', 'E-Care Green Current'],
  ['e-care', 'classic', 'E-Care Classic Current'],
  ['e-care', 'silver', 'E-Care Silver Current'],
  ['e-care', 'gold', 'E-Care Gold Current'],
];

const selectedTiers = process.argv[2]
  ? tiers.filter(([, , name]) => name.toLowerCase().startsWith(process.argv[2].toLowerCase()))
  : tiers;

function csv(value) { return `"${String(value ?? '').replaceAll('"', '""')}"`; }

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/snap/bin/brave', args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage();
    let rpcTemplate;
    for (const [tpa, slug, name] of selectedTiers) {
      let request;
      page.on('request', current => {
        if (current.url().includes('rpc/get_network_coverage')) request = current;
      });
      await page.goto(`https://www.medifinder.ae/medical/networks/${tpa}/${slug}`, { waitUntil: 'networkidle', timeout: 60000 });
      const loadMore = page.getByRole('button', { name: /Load .* more/ }).first();
      const hasLoadMore = (await loadMore.count()) > 0;
      if (hasLoadMore) {
        await loadMore.click();
        await page.waitForTimeout(500);
      }
      if (!request && rpcTemplate) request = rpcTemplate;
      if (!request) throw new Error(`coverage request missing for ${slug}`);
      rpcTemplate = request;
      if (!request) throw new Error(`coverage request missing for ${slug}`);
      const body = JSON.parse(request.postData());
      if (!hasLoadMore) {
        const match = (await page.content()).match(/networkId.{0,12}([0-9a-f-]{36})/i);
        if (!match) throw new Error(`network ID missing for ${slug}`);
        body.p_network_id = match[1];
      }
      body.p_page = 1;
      body.p_page_size = 1000;
      const headers = Object.fromEntries(Object.entries(await request.allHeaders()).filter(([key]) => !key.startsWith(':') && !['content-length', 'host'].includes(key)));
      const fetchPage = async (pageNumber) => {
        const pageBody = { ...body, p_page: pageNumber };
        const response = await page.request.post(request.url(), { headers, data: pageBody });
        if (!response.ok()) throw new Error(`RPC failed for ${slug}: ${response.status()}`);
        return response.json();
      };
      const providers = [];
      const partitions = tpa === 'e-care' ? [false, true] : [false];
      for (const hasCoords of partitions) {
        body.p_has_coords = hasCoords;
        const first = await fetchPage(1);
        providers.push(...first.providers);
        for (let pageNumber = 2; pageNumber <= first.total_pages; pageNumber += 1) {
          const next = await fetchPage(pageNumber);
          providers.push(...next.providers);
        }
      }
      const unique = [...new Map(providers.map(row => [row.id ?? `${row.canonical_name}|${row.emirate}|${row.region}`, row])).values()];
      const output = `sources/networks/${name}.csv`;
      const lines = ['PROVIDER NAME,EMIRATE,PROVIDER TYPE,AREA,ADDRESS,TELEPHONE,lat,lon,SOURCE'];
      for (const row of unique) lines.push([row.canonical_name, row.emirate, row.facility_type_norm, row.region, '', row.phone_norm, row.lat, row.lng, `https://www.medifinder.ae/medical/networks/${tpa}/${slug}`].map(csv).join(','));
      fs.writeFileSync(output, `${lines.join('\n')}\n`);
      console.log(`${name}: ${unique.length} from ${providers.length} API rows`);
      page.removeAllListeners('request');
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
