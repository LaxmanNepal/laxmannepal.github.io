from pathlib import Path
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
errors = []

html_path = ROOT / 'index.html'
html = html_path.read_text(encoding='utf-8')

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

# Homepage must load each enhancement exactly once and never load the retired renderer.
for script_name in ('site-enhancements.js', 'apps-homepage.js', 'site-intelligence.js'):
    count = len(re.findall(r'<script\\s+src=["\'][^"\']*' + re.escape(script_name) + r'(?:\\?[^"\']*)?["\'][^>]*></script>', html, re.I))
    if count != 1:
        errors.append(f'{script_name} expected once, found {count}')
if re.search(r'<script\\s+src=["\'][^"\']*apps-renderer\\.js', html, re.I):
    errors.append('retired apps-renderer.js is still loaded')

# Prevent accidental insecure third-party resources on the HTTPS site.
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

if errors:
    print('\n'.join(f'ERROR: {e}' for e in errors))
    sys.exit(1)

print('Homepage QA passed.')
print('✓ JSON datasets parse')
print('✓ renderer scripts are unique')
print('✓ no retired renderer or insecure HTTP homepage resources')
print('✓ JavaScript assets pass node --check')
print('✓ sitemap is valid and synchronized with online apps')
