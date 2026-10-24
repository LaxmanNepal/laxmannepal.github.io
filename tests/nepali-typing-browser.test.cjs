// Browser-level regression tests for the Nepali typing workspace.
// Run from the repository root after starting a local HTTP server on port 4173:
// NODE_PATH=/tmp/typing-browser/node_modules node --test tests/nepali-typing-browser.test.cjs
const test = require('node:test');
const assert = require('node:assert/strict');
const { chromium } = require('playwright');

let browser;
test.before(async () => { browser = await chromium.launch({ headless: true }); });
test.after(async () => { await browser?.close(); });

async function openPage(viewport = { width: 1280, height: 900 }) {
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  // Keep the suite deterministic and prove the local fallback works without network.
  await page.route('https://inputtools.google.com/**', route => route.abort());
  await page.goto('http://127.0.0.1:4173/tools/nepali-tools/type-nepali/', { waitUntil: 'domcontentloaded' });
  await page.locator('#editor').waitFor();
  return { context, page };
}

test('clicking a candidate replaces the whole word when the caret is mid-token', async () => {
  const { context, page } = await openPage();
  try {
    const editor = page.locator('#editor');
    await editor.fill('hello namaste world');
    await editor.evaluate(el => { el.setSelectionRange(10, 10); el.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowLeft', bubbles: true })); });
    const candidate = page.locator('.suggestion').filter({ hasText: 'नमस्ते' }).first();
    await candidate.waitFor({ state: 'visible' });
    await candidate.click();
    assert.equal(await editor.inputValue(), 'hello नमस्ते world');
  } finally { await context.close(); }
});

test('Space commits the local suggestion and leaves a space after it', async () => {
  const { context, page } = await openPage();
  try {
    const editor = page.locator('#editor');
    await editor.fill('namaste');
    await editor.press('Space');
    await page.waitForFunction(() => document.querySelector('#editor').value === 'नमस्ते ');
    assert.equal(await editor.inputValue(), 'नमस्ते ');
  } finally { await context.close(); }
});

test('local draft status and Nepali character statistics update as text changes', async () => {
  const { context, page } = await openPage();
  try {
    await page.locator('#editor').fill('नेपाली test');
    await page.waitForFunction(() => document.querySelector('#save-status').textContent.includes('Saved'));
    const counts = await page.locator('#counts').textContent();
    assert.match(counts, /words/);
    assert.match(counts, /characters/);
    assert.match(counts, /Nepali characters/);
  } finally { await context.close(); }
});

test('typing workspace fits a narrow mobile viewport without horizontal overflow', async () => {
  const { context, page } = await openPage({ width: 375, height: 812 });
  try {
    const dimensions = await page.evaluate(() => ({ viewport: document.documentElement.clientWidth, page: document.documentElement.scrollWidth }));
    assert.ok(dimensions.page <= dimensions.viewport + 1, `horizontal overflow: ${JSON.stringify(dimensions)}`);
    assert.ok(await page.locator('#editor').isVisible());
  } finally { await context.close(); }
});

test('cached typing page reloads and converts locally while offline', async () => {
  const { context, page } = await openPage();
  try {
    await page.evaluate(async () => { await navigator.serviceWorker.ready; });
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.evaluate(async () => { await navigator.serviceWorker.ready; });
    await context.setOffline(true);
    await page.reload({ waitUntil: 'domcontentloaded' });
    const editor = page.locator('#editor');
    await editor.fill('namaste');
    await editor.press('Space');
    await page.waitForFunction(() => document.querySelector('#editor').value === 'नमस्ते ');
    assert.equal(await editor.inputValue(), 'नमस्ते ');
    assert.match(await page.locator('#network-status').textContent(), /Offline/);
  } finally {
    await context.setOffline(false);
    await context.close();
  }
});

test('practice page updates accuracy locally and stops on exact completion', async () => {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();
  try {
    await page.goto('http://127.0.0.1:4173/tools/nepali-tools/nepali-typing-practice/', { waitUntil: 'domcontentloaded' });
    const target = page.locator('#target-text');
    const input = page.locator('#practice-input');
    await target.fill('नेपाल');
    await input.fill('ने');
    assert.equal(await page.locator('#accuracy').textContent(), '100%');
    await page.locator('#start').click();
    await input.fill('नेपाल');
    await page.waitForFunction(() => document.querySelector('#practice-status').textContent.includes('completed'));
    assert.equal(await page.locator('#correct').textContent(), '3');
    assert.equal(await page.locator('#start').isDisabled(), true);
  } finally { await context.close(); }
});

test('practice page fits a narrow mobile viewport', async () => {
  const context = await browser.newContext({ viewport: { width: 375, height: 812 } });
  const page = await context.newPage();
  try {
    await page.goto('http://127.0.0.1:4173/tools/nepali-tools/nepali-typing-practice/', { waitUntil: 'domcontentloaded' });
    const dimensions = await page.evaluate(() => ({ viewport: document.documentElement.clientWidth, page: document.documentElement.scrollWidth }));
    assert.ok(dimensions.page <= dimensions.viewport + 1, `horizontal overflow: ${JSON.stringify(dimensions)}`);
  } finally { await context.close(); }
});

test('Google suggestions are opt-in and local suggestions work by default', async () => {
  const context = await browser.newContext();
  const page = await context.newPage();
  let remoteRequests = 0;
  await page.route('https://inputtools.google.com/**', route => { remoteRequests++; return route.abort(); });
  try {
    await page.goto('http://127.0.0.1:4173/tools/nepali-tools/type-nepali/', { waitUntil: 'domcontentloaded' });
    const editor = page.locator('#editor');
    await editor.fill('namaste');
    await page.locator('.suggestion').filter({ hasText: 'नमस्ते' }).first().waitFor();
    assert.equal(await page.locator('#remote-suggestions').isChecked(), false);
    assert.equal(remoteRequests, 0);
    await page.locator('#remote-suggestions').check();
    await editor.fill('nepal');
    await page.waitForTimeout(250);
    assert.ok(remoteRequests > 0);
  } finally { await context.close(); }
});

test('local documents, templates, find/replace and delete-all work', async () => {
  const context = await browser.newContext();
  const page = await context.newPage();
  page.on('dialog', dialog => dialog.accept());
  try {
    await page.goto('http://127.0.0.1:4173/tools/nepali-tools/type-nepali/', { waitUntil: 'domcontentloaded' });
    await page.locator('.workspace-tools > summary').click();
    const editor = page.locator('#editor');
    await editor.fill('First draft नेपाल');
    await page.locator('#new-document').click();
    assert.equal(await editor.inputValue(), '');
    assert.equal(await page.locator('#document-select option').count(), 2);
    await editor.fill('Second document');
    await page.locator('#document-select').selectOption({ index: 0 });
    assert.equal(await editor.inputValue(), 'First draft नेपाल');
    await page.locator('#document-name').fill('First notes');
    await page.locator('#rename-document').click();
    assert.equal(await page.locator('#document-select option').nth(0).textContent(), 'First notes');
    await page.locator('#template-select').selectOption('leave');
    await page.locator('#insert-template').click();
    assert.match(await editor.inputValue(), /बिदा पाऊँ/);
    await editor.fill('नेपाल नेपाल');
    await page.locator('#find-text').fill('नेपाल');
    await page.locator('#replace-text').fill('देश');
    await page.locator('#replace-all').click();
    assert.equal(await editor.inputValue(), 'देश देश');
    await page.locator('#delete-local-data').click();
    const saved = await page.evaluate(() => ({
      draft: localStorage.getItem('ln-nepali-typing-draft'),
      docs: localStorage.getItem('ln-nepali-typing-documents-v1')
    }));
    assert.equal(saved.draft, null);
    assert.equal(saved.docs, null);
  } finally { await context.close(); }
});

test('Preeti converter converts both directions locally', async () => {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();
  try {
    await page.goto('http://127.0.0.1:4173/tools/nepali-tools/preeti-unicode-converter/', { waitUntil: 'domcontentloaded' });
    const source = page.locator('#source-text');
    const result = page.locator('#result-text');
    await source.fill("g]kfn ;/sf/sf k|wfgdGqLn] cfly{s ;'wf/sf] 3f]if0ff ug'{eof] .");
    assert.equal(await result.inputValue(), 'नेपाल सरकारका प्रधानमन्त्रीले आर्थिक सुधारको घोषणा गर्नुभयो ।');
    await page.locator('#direction').selectOption('unicode-to-preeti');
    await source.fill('नेपाल');
    assert.equal(await result.inputValue(), 'g]kfn');
    assert.match(await page.locator('#conversion-status').textContent(), /Preeti font/);
  } finally { await context.close(); }
});

test('Preeti converter fits a narrow mobile viewport', async () => {
  const context = await browser.newContext({ viewport: { width: 375, height: 812 } });
  const page = await context.newPage();
  try {
    await page.goto('http://127.0.0.1:4173/tools/nepali-tools/preeti-unicode-converter/', { waitUntil: 'domcontentloaded' });
    const dimensions = await page.evaluate(() => ({ viewport: document.documentElement.clientWidth, page: document.documentElement.scrollWidth }));
    assert.ok(dimensions.page <= dimensions.viewport + 1, `horizontal overflow: ${JSON.stringify(dimensions)}`);
  } finally { await context.close(); }
});

test('voice errors are actionable and final speech saves into the local document', async () => {
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.addInitScript(() => {
    class MockSpeechRecognition {
      constructor() { window.__mockSpeechRecognition = this; }
      start() { if (this.onstart) this.onstart(); }
      stop() { if (this.onend) this.onend(); }
    }
    window.SpeechRecognition = MockSpeechRecognition;
  });
  try {
    await page.goto('http://127.0.0.1:4173/tools/nepali-tools/type-nepali/', { waitUntil: 'domcontentloaded' });
    await page.locator('[data-mode="voice"]').click();
    await page.locator('#voice-toggle').click();
    assert.match(await page.locator('#voice-status').textContent(), /सुन्दैछ/);
    await page.evaluate(() => window.__mockSpeechRecognition.onerror({ error: 'not-allowed' }));
    assert.match(await page.locator('#voice-status').textContent(), /Microphone permission was denied/);
    await page.evaluate(() => window.__mockSpeechRecognition.onend());
    assert.match(await page.locator('#voice-status').textContent(), /Microphone permission was denied/);
    await page.locator('#voice-toggle').click();
    await page.evaluate(() => window.__mockSpeechRecognition.onresult({ results: [{ 0: { transcript: 'नमस्ते' }, isFinal: true }] }));
    assert.match(await page.locator('#editor').inputValue(), /नमस्ते/);
    const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('ln-nepali-typing-documents-v1') || '[]'));
    assert.ok(saved.some(doc => doc.content.includes('नमस्ते')));
    assert.equal(await page.locator('#voice-toggle').getAttribute('aria-pressed'), 'true');
  } finally { await context.close(); }
});

test('typing, practice and Preeti pages expose SEO metadata and FAQ structured data', async () => {
  const context = await browser.newContext();
  const page = await context.newPage();
  try {
    for (const path of [
      '/tools/nepali-tools/type-nepali/',
      '/tools/nepali-tools/nepali-typing-practice/',
      '/tools/nepali-tools/preeti-unicode-converter/'
    ]) {
      await page.goto('http://127.0.0.1:4173' + path, { waitUntil: 'domcontentloaded' });
      assert.ok(await page.locator('link[rel="canonical"]').count());
      assert.ok(await page.locator('meta[property="og:title"]').count());
      const jsonld = await page.locator('script[type="application/ld+json"]').textContent();
      assert.match(jsonld, /FAQPage/);
      assert.match(jsonld, /SoftwareApplication/);
    }
  } finally { await context.close(); }
});

test('smart local lexicon ranks common suffix forms in the typing UI', async () => {
  const { context, page } = await openPage();
  try {
    const editor = page.locator('#editor');
    await editor.fill('netaharulai');
    await page.locator('.suggestion').filter({ hasText: 'नेताहरूलाई' }).first().waitFor();
    assert.match(await page.locator('.suggestion').first().textContent(), /नेताहरूलाई/);
    await page.locator('.suggestion').first().click();
    assert.equal(await editor.inputValue(), 'नेताहरूलाई');
  } finally { await context.close(); }
});
