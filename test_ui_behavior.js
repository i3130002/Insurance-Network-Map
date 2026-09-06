/** Exercise the page's actual selection code with controlled fetch timing. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { test } = require('node:test');

function createPage() {
    const elements = new Map();
    const requests = [];
    const document = {
        getElementById(id) {
            if (!elements.has(id)) elements.set(id, {
                value: '', disabled: true, textContent: '', innerHTML: '',
                classList: { toggle() {} }, append() {}, addEventListener() {},
            });
            return elements.get(id);
        },
        createElement() { return {}; },
    };
    const map = { setView() { return this; }, removeLayer() {}, addLayer() {}, fitBounds() {} };
    const context = vm.createContext({
        document, console, Option: function(text, value) { return { text, value }; },
        fetch(url) { return new Promise((resolve, reject) => requests.push({ url, resolve, reject })); },
        L: {
            map() { return map; }, tileLayer() { return { addTo() {} }; },
            divIcon(options) { return options; },
            marker() { return { bindPopup() { return this; }, addTo(group) { group.layers.push(this); } }; },
            markerClusterGroup() {
                return { layers: [], getLayers() { return this.layers; },
                    getBounds() { return { pad() {} }; } };
            },
        },
    });
    const html = fs.readFileSync(`${__dirname}/index.html`, 'utf8');
    vm.runInContext(html.match(/<script>\s*([\s\S]*?)<\/script>/)[1], context);
    return { document, requests, run: code => vm.runInContext(code, context) };
}

const providers = JSON.parse(fs.readFileSync(`${__dirname}/data/moh-complete.json`, 'utf8'));
const mappedCount = providers.filter(p => p.lat >= 22 && p.lat <= 26.6 && p.lon >= 51 && p.lon <= 56.6).length;
const response = { ok: true, json: async () => providers };

test('clearing a plan removes markers and disables filters', async () => {
    const page = createPage();
    const loading = page.run("loadPlan('data/test.json|test')");
    page.requests.at(-1).resolve(response);
    await loading;
    assert.equal(page.run('cluster.getLayers().length'), mappedCount);
    await page.run("loadPlan('')");
    assert.equal(page.run('selectedPlan.length'), 0);
    assert.equal(page.run('cluster'), null);
    assert.equal(page.document.getElementById('providerSearch').disabled, true);
});

test('a previous company response cannot restore its providers', async () => {
    const page = createPage();
    const loading = page.run("loadPlan('data/old.json|old')");
    page.run("populatePlanOptions('Another company')");
    page.requests.at(-1).resolve(response);
    await loading;
    assert.equal(page.run('selectedPlan.length'), 0);
    assert.equal(page.document.getElementById('status').textContent, 'Select an insurance plan');
});

test('the latest plan wins when responses arrive out of order', async () => {
    const page = createPage();
    const oldLoading = page.run("loadPlan('data/old.json|old')");
    const oldRequest = page.requests.at(-1);
    const newLoading = page.run("loadPlan('data/new.json|new')");
    page.requests.at(-1).resolve({ ok: true, json: async () => providers.slice(0, 1) });
    await newLoading;
    oldRequest.resolve(response);
    await oldLoading;
    assert.equal(page.run('selectedPlan.length'), 1);
    assert.equal(page.run('cluster.getLayers().length'), 1);
});

test('a stale error cannot overwrite the latest status', async () => {
    const page = createPage();
    const loading = page.run("loadPlan('data/old.json|old')");
    page.run("populatePlanOptions('')");
    page.requests.at(-1).reject(new Error('old request failed'));
    await loading;
    assert.equal(page.document.getElementById('status').textContent, 'Select an insurance company');
});

test('search and filters combine, empty results clear markers, reset restores providers', async () => {
    const page = createPage();
    const loading = page.run("loadPlan('data/test.json|test')");
    page.requests.at(-1).resolve(response);
    await loading;
    const provider = providers[0];
    page.document.getElementById('providerSearch').value = provider['PROVIDER NAME'].toLowerCase();
    page.document.getElementById('emirateFilter').value = provider.P;
    page.document.getElementById('typeFilter').value = provider['PROVIDER TYPE'];
    page.run('renderProviders()');
    assert.ok(page.run('cluster.getLayers().length') > 0);
    assert.ok(page.run('cluster.getLayers().length') < providers.length);
    page.document.getElementById('providerSearch').value = 'no-such-provider-93842';
    page.run('renderProviders()');
    assert.equal(page.run('cluster.getLayers().length'), 0);
    assert.match(page.document.getElementById('status').textContent, /No providers match/);
    page.run('resetFilters()');
    assert.equal(page.run('cluster.getLayers().length'), mappedCount);
});
