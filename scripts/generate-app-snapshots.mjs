import fs from 'node:fs/promises';
import path from 'node:path';
import { chromium } from 'playwright';

const owner = 'LaxmanNepal';
const outputDir = path.resolve('assets/app-snapshots');
const api = `https://api.github.com/users/${owner}/repos?per_page=100&sort=updated`;
const headers = { accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' };

function slugify(value) {
  return String(value).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

async function getRepos() {
  const response = await fetch(api, { headers });
  if (!response.ok) throw new Error(`GitHub API failed: ${response.status}`);
  return response.json();
}

await fs.mkdir(outputDir, { recursive: true });
const repos = (await getRepos()).filter(repo => !repo.fork && !repo.archived && repo.homepage && /^https?:\/\//i.test(repo.homepage));
const browser = await chromium.launch({ headless: true });
const desktop = await browser.newContext({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });

for (const repo of repos) {
  const filename = `${slugify(repo.name)}.webp`;
  const target = path.join(outputDir, filename);
  const page = await desktop.newPage();
  try {
    await page.goto(repo.homepage.trim(), { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForLoadState('networkidle', { timeout: 12000 }).catch(() => {});
    await page.waitForTimeout(1200);
    await page.screenshot({ path: target, type: 'webp', quality: 82, fullPage: false });
    console.log(`✓ ${repo.name}`);
  } catch (error) {
    console.warn(`⚠ ${repo.name}: ${error.message}`);
  } finally {
    await page.close();
  }
}

await browser.close();
console.log(`Generated snapshots for ${repos.length} apps.`);
