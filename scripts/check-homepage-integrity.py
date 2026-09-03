from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
html = (root / 'index.html').read_text(encoding='utf-8')
errors = []

# Exactly one primary homepage renderer and one app-discovery enhancement.
renderer_scripts = re.findall(r'<script\s+src=["\']([^"\']*site-enhancements\.js[^"\']*)["\'][^>]*></script>', html, re.I)
app_scripts = re.findall(r'<script\s+src=["\']([^"\']*apps-homepage\.js[^"\']*)["\'][^>]*></script>', html, re.I)
intel_scripts = re.findall(r'<script\s+src=["\']([^"\']*site-intelligence\.js[^"\']*)["\'][^>]*></script>', html, re.I)
if len(renderer_scripts) != 1:
    errors.append(f'expected exactly 1 site-enhancements.js script, found {len(renderer_scripts)}')
if len(app_scripts) != 1:
    errors.append(f'expected exactly 1 apps-homepage.js script, found {len(app_scripts)}')
if len(intel_scripts) != 1:
    errors.append(f'expected exactly 1 site-intelligence.js script, found {len(intel_scripts)}')

# Obsolete renderer and legacy inline data rendering must not return.
if re.search(r'<script\s+src=["\'][^"\']*apps-renderer\.js[^"\']*["\']', html, re.I):
    errors.append('obsolete apps-renderer.js is still loaded')
if re.search(r'\basync\s+function\s+(?:loadYT|loadApps)\s*\(', html):
    errors.append('legacy inline YouTube/Apps renderer is still present')

# Dynamic data sources must exist and remain available.
for path in ('data/apps.json', 'data/youtube.json'):
    if not (root / path).is_file():
        errors.append(f'missing required data file: {path}')

apps_path = root / 'data/apps.json'
if apps_path.is_file() and apps_path.stat().st_size == 0:
    errors.append('data/apps.json is empty')

yt_path = root / 'data/youtube.json'
if yt_path.is_file() and yt_path.stat().st_size == 0:
    errors.append('data/youtube.json is empty')

# Keep the sitemap synchronized with every online app URL.
if apps_path.is_file() and (root / 'sitemap.xml').is_file():
    try:
        data = json.loads(apps_path.read_text(encoding='utf-8'))
        sitemap = (root / 'sitemap.xml').read_text(encoding='utf-8')
        for app in data.get('apps', []):
            if app.get('status') == 'online' and app.get('url') and app['url'] not in sitemap:
                errors.append(f'online app missing from sitemap: {app["url"]}')
    except Exception as exc:
        errors.append(f'could not validate sitemap against apps.json: {exc}')

if errors:
    print('\n'.join(f'ERROR: {e}' for e in errors))
    raise SystemExit(1)

print('Homepage integrity check passed.')
print(f'Primary renderer: {renderer_scripts[0]}')
print(f'App discovery renderer: {app_scripts[0]}')
print(f'Site intelligence renderer: {intel_scripts[0]}')
print('Obsolete apps renderer: not loaded')
print('Legacy inline data renderer: not present')
print('Required data files: present')
print('Online app URLs: present in sitemap')
