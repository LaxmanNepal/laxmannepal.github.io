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
