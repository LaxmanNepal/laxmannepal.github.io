from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
html = (root / 'index.html').read_text(encoding='utf-8')

errors = []

# Exactly one active homepage enhancement renderer.
renderer_scripts = re.findall(r'<script\s+src=["\']([^"\']*site-enhancements\.js[^"\']*)["\'][^>]*></script>', html, re.I)
if len(renderer_scripts) != 1:
    errors.append(f'expected exactly 1 site-enhancements.js script, found {len(renderer_scripts)}')

# The obsolete renderer must not be loaded.
if re.search(r'<script\s+src=["\'][^"\']*apps-renderer\.js[^"\']*["\']', html, re.I):
    errors.append('obsolete apps-renderer.js is still loaded')

# Dynamic data sources must exist and remain referenced.
for path in ('data/apps.json', 'data/youtube.json'):
    if not (root / path).is_file():
        errors.append(f'missing required data file: {path}')

apps = (root / 'data/apps.json')
if apps.is_file() and apps.stat().st_size == 0:
    errors.append('data/apps.json is empty')

yt = (root / 'data/youtube.json')
if yt.is_file() and yt.stat().st_size == 0:
    errors.append('data/youtube.json is empty')

if errors:
    print('\n'.join(f'ERROR: {e}' for e in errors))
    raise SystemExit(1)

print('Homepage integrity check passed.')
print(f'Renderer: {renderer_scripts[0]}')
print('Obsolete apps renderer: not loaded')
print('Required data files: present')
