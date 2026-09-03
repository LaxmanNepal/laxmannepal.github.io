from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
html = (root / 'index.html').read_text(encoding='utf-8')

errors = []

# Exactly one primary homepage renderer and one app-discovery enhancement.
renderer_scripts = re.findall(r'<script\s+src=["\']([^"\']*site-enhancements\.js[^"\']*)["\'][^>]*></script>', html, re.I)
app_scripts = re.findall(r'<script\s+src=["\']([^"\']*apps-homepage\.js[^"\']*)["\'][^>]*></script>', html, re.I)
if len(renderer_scripts) != 1:
    errors.append(f'expected exactly 1 site-enhancements.js script, found {len(renderer_scripts)}')
if len(app_scripts) != 1:
    errors.append(f'expected exactly 1 apps-homepage.js script, found {len(app_scripts)}')

# Obsolete renderer must not be loaded.
if re.search(r'<script\s+src=["\'][^"\']*apps-renderer\.js[^"\']*["\']', html, re.I):
    errors.append('obsolete apps-renderer.js is still loaded')

# Dynamic data sources must exist and remain available.
for path in ('data/apps.json', 'data/youtube.json'):
    if not (root / path).is_file():
        errors.append(f'missing required data file: {path}')

apps = root / 'data/apps.json'
if apps.is_file() and apps.stat().st_size == 0:
    errors.append('data/apps.json is empty')

yt = root / 'data/youtube.json'
if yt.is_file() and yt.stat().st_size == 0:
    errors.append('data/youtube.json is empty')

if errors:
    print('\n'.join(f'ERROR: {e}' for e in errors))
    raise SystemExit(1)

print('Homepage integrity check passed.')
print(f'Primary renderer: {renderer_scripts[0]}')
print(f'App discovery renderer: {app_scripts[0]}')
print('Obsolete apps renderer: not loaded')
print('Required data files: present')
