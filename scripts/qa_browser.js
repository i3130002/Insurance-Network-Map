/** Run rendered-page QA with the installed Playwright and Brave browser. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/home/tony/.npm/_npx/db89d7302a373f10/node_modules/playwright');

const plans = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/plans.json')));
const largest = plans.reduce((a, b) => a.providers > b.providers ? a : b);
const server = http.createServer((request, response) => {
    const name = request.url.split('?')[0];
    if (!['/', '/index.html'].includes(name) && !/^\/data\/[\w-]+\.json$/.test(name)) {
        response.writeHead(404).end();
        return;
    }
    const file = path.join(__dirname, name === '/' ? 'index.html' : name);
    fs.readFile(file, (error, body) => {
        response.writeHead(error ? 404 : 200, { 'Content-Type': file.endsWith('.json') ? 'application/json' : 'text/html' });
        response.end(error ? 'Not found' : body);
    });
});

async function checkViewport(browser, base, viewport) {
    const page = await browser.newPage({ viewport });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(base, { waitUntil: 'networkidle' });
    assert.equal(await page.locator('#insurerSelect').isEnabled(), true);
    await page.selectOption('#insurerSelect', largest.insurer);
    const start = Date.now();
    await page.selectOption('#planSelect', `${largest.file}|${largest.id}`);
    await page.waitForFunction(count => typeof cluster !== 'undefined' && cluster?.getLayers().length === count, largest.providers);
    const loadMs = Date.now() - start;
    const provider = await page.evaluate(() => selectedPlan[0]);
    await page.fill('#providerSearch', provider['PROVIDER NAME']);
    await page.selectOption('#emirateFilter', provider.P);
    await page.selectOption('#typeFilter', provider['PROVIDER TYPE']);
    assert.ok(await page.evaluate(() => cluster.getLayers().length > 0));
    await page.fill('#providerSearch', 'no-such-provider-93842');
    assert.equal(await page.evaluate(() => cluster.getLayers().length), 0);
    await page.click('#resetFilters');
    assert.equal(await page.evaluate(() => cluster.getLayers().length), largest.providers);
    const links = await page.evaluate(() => {
        const marker = cluster.getLayers()[0];
        marker.openPopup();
        const container = document.createElement('div');
        container.innerHTML = marker.getPopup().getContent();
        return [...container.querySelectorAll('a')].map(a => ({ text: a.textContent, url: a.href }));
    });
    assert.ok(links.some(link => link.text.includes('Google Maps') && new URL(link.url).protocol === 'https:'));
    assert.ok(links.some(link => link.text.includes('Zavis') && new URL(link.url).hostname.endsWith('zavis.ai')));
    const layout = await page.evaluate(() => {
        const panel = document.querySelector('#panel').getBoundingClientRect();
        return { panelHeight: panel.height, viewportHeight: innerHeight,
            mapExposedBelowPanel: innerHeight - panel.bottom,
            horizontalOverflow: document.documentElement.scrollWidth > innerWidth };
    });
    assert.equal(layout.horizontalOverflow, false);
    if (viewport.width <= 520) assert.ok(layout.mapExposedBelowPanel >= viewport.height * 0.4,
        'The mobile panel must leave room to use the map');
    fs.mkdirSync(path.join(__dirname, '.qa'), { recursive: true });
    await page.screenshot({ path: path.join(__dirname, `.qa/map-${viewport.width}.png`) });
    await page.selectOption('#planSelect', '');
    assert.equal(await page.evaluate(() => cluster), null);
    assert.equal(await page.locator('#providerSearch').isEnabled(), false);
    const empty = plans.find(plan => plan.providers === 0);
    await page.selectOption('#insurerSelect', empty.insurer);
    await page.selectOption('#planSelect', `${empty.file}|${empty.id}`);
    await page.waitForFunction(() => document.querySelector('#status').textContent.includes('No providers'));
    assert.equal(await page.evaluate(() => cluster.getLayers().length), 0);
    await page.selectOption('#insurerSelect', '');
    assert.equal(await page.locator('#planSelect').isEnabled(), false);
    assert.deepEqual(errors, []);
    await page.close();
    return { viewport, largestPlan: largest.id, providers: largest.providers, loadMs, layout, links, errors };
}

async function main() {
    await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
    let browser;
    try {
        browser = await chromium.launch({ headless: true, executablePath: process.env.BROWSER_PATH || '/snap/bin/brave', args: ['--no-sandbox'] });
        const base = `http://127.0.0.1:${server.address().port}`;
        const local = [];
        for (const viewport of [{ width: 1440, height: 900 }, { width: 390, height: 844 }, { width: 360, height: 640 }]) {
            local.push(await checkViewport(browser, base, viewport));
        }
        const deployed = await browser.newPage();
        const response = await deployed.goto('https://i3130002.github.io/Insurance-Network-Map/', { waitUntil: 'networkidle' });
        const published = { status: response.status(), title: await deployed.title(),
            companySelector: await deployed.locator('#insurerSelect').count() };
        const report = { checkedAt: new Date().toISOString(), local, published };
        fs.writeFileSync(path.join(__dirname, '.qa/browser-report.json'), JSON.stringify(report, null, 2));
        console.log(JSON.stringify(report, null, 2));
    } finally {
        if (browser) await browser.close();
        server.close();
    }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
