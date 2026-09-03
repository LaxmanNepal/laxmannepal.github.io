from pathlib import Path
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
errors = []

html = (ROOT / 'index.html').read_text(encoding='utf-8')

# JSON datasets must parse and contain the minimum runtime fields.
for name in ('apps', 'youtube'):
    path = ROOT / 'data' / f'{name}.json'
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if name == 'apps':
            if not isinstance(data.get('apps'), list) or not data['apps']:
                errors.append('apps.json has no apps')
        elif not data.get('channel', {}).get('statistics'):
            errors.append('youtube.json has no channel statistics')
    except Exception as exc:
        errors.append(f'{name}.json is invalid: {exc}')

# PWA manifest must be valid and its declared icon MIME type must match the SVG asset.
try:
    manifest = json.loads((ROOT / 'manifest.webmanifest').read_text(encoding='utf-8'))
    icons = manifest.get('icons', [])
    if not any(i.get('src') == '/assets/icon.svg' and i.get('type') == 'image/svg+xml' for i in icons):
        errors.append('manifest does not correctly declare /assets/icon.svg as image/svg+xml')
except Exception as exc:
    errors.append(f'manifest.webmanifest is invalid: {exc}')
if not (ROOT / 'sw.js').is_file():
    errors.append('sw.js is missing')
if 'rel="manifest"' not in html or '/manifest.webmanifest' not in html:
    errors.append('homepage is missing manifest reference')
if '/sw.js' not in html:
    errors.append('homepage is missing service-worker registration')

# Homepage must load each enhancement exactly once and never load the retired renderer.
for script_name in ('site-enhancements.js', 'apps-homepage.js', 'site-intelligence.js'):
    pattern = r'<script\s+src=["\'][^"\']*' + re.escape(script_name) + r'(?:\?[^"\']*)?["\'][^>]*></script>'
    count = len(re.findall(pattern, html, re.I))
    if count != 1:
        errors.append(f'{script_name} expected once, found {count}')
if re.search(r'<script\s+src=["\'][^"\']*apps-renderer\.js', html, re.I):
    errors.append('retired apps-renderer.js is still loaded')
if re.search(r'async\s+function\s+load(?:YT|Apps)\s*\(', html):
    errors.append('legacy inline data renderer functions are still present')

# App directory must have exactly one enhancement script so /apps/?q=... works.
directory_path = ROOT / 'apps' / 'index.html'
if not directory_path.is_file():
    errors.append('apps/index.html is missing')
else:
    directory = directory_path.read_text(encoding='utf-8')
    count = len(re.findall(r'<script\s+src=["\'][^"\']*apps-directory-search\.js(?:\?[^"\']*)?["\'][^>]*></script>', directory, re.I))
    if count != 1:
        errors.append(f'apps-directory-search.js expected once in app directory, found {count}')
    if '../Nepse/' in directory:
        errors.append('app directory contains retired /Nepse/ path')

# Prevent accidental insecure third-party resources on the HTTPS homepage.
for match in re.findall(r'(?:src|href)=["\'](http://[^"\']+)["\']', html, re.I):
    if not match.startswith('http://localhost'):
        errors.append(f'insecure HTTP resource in homepage: {match}')

# Every JavaScript asset in assets/ must pass Node's parser check.
for path in sorted((ROOT / 'assets').glob('*.js')):
    result = subprocess.run(['node', '--check', str(path)], capture_output=True, text=True)
    if result.returncode:
        errors.append(f'JavaScript syntax error in {path.relative_to(ROOT)}: {result.stderr.strip()}')

# Validate sitemap XML and ensure every online app URL is indexed.
try:
    ET.parse(ROOT / 'sitemap.xml')
except Exception as exc:
    errors.append(f'sitemap.xml is invalid XML: {exc}')
else:
    apps = json.loads((ROOT / 'data/apps.json').read_text(encoding='utf-8')).get('apps', [])
    sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
    for app in apps:
        if app.get('status') == 'online' and app.get('url') and app['url'] not in sitemap:
            errors.append(f'online app missing from sitemap: {app["url"]}')

# The human-readable app directory must not drift from the machine-readable catalog.
try:
    directory = directory_path.read_text(encoding='utf-8')
    apps = json.loads((ROOT / 'data/apps.json').read_text(encoding='utf-8')).get('apps', [])
    for app in apps:
        if app.get('status') != 'online' or not app.get('url'):
            continue
        path = re.sub(r'^https?://[^/]+', '', app['url'])
        relative = '../' + path.lstrip('/')
        if relative not in directory:
            errors.append(f'app directory missing online app link: {relative}')
except Exception as exc:
    errors.append(f'app directory check failed: {exc}')

if errors:
    print('\n'.join(f'ERROR: {e}' for e in errors))
    sys.exit(1)

print('Homepage QA passed.')
print('✓ JSON datasets parse')
print('✓ PWA manifest and service worker are wired correctly')
print('✓ renderer scripts are unique and legacy inline renderers are absent')
print('✓ app directory search enhancement is installed once')
print('✓ no retired renderer or insecure HTTP homepage resources')
print('✓ JavaScript assets pass node --check')
print('✓ sitemap and app directory are synchronized with online apps')
