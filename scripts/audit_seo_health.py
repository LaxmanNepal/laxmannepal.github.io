from pathlib import Path
import re, sys

TARGET = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.pages')
TARGET = TARGET.resolve()
files = sorted(TARGET.rglob('*.html'))
errors, warnings = [], []

def meta(doc, name=None, prop=None):
    if name: pat = rf'<meta[^>]+name=["\']{re.escape(name)}["\'][^>]*>'
    else: pat = rf'<meta[^>]+property=["\']{re.escape(prop)}["\'][^>]*>'
    return re.findall(pat, doc, re.I)

def content_value(tag):
    m = re.search(r'content=["\'](.*?)["\']', tag, re.I|re.S)
    return m.group(1).strip() if m else ''

def check_file(p):
    doc = p.read_text(encoding='utf-8', errors='ignore')
    rel = str(p.relative_to(TARGET))
    title = re.findall(r'<title[^>]*>(.*?)</title>', doc, re.I|re.S)
    if len(title) != 1 or not re.sub(r'<[^>]+>', '', title[0]).strip(): errors.append((rel,'missing/duplicate title'))
    descriptions = meta(doc, name='description')
    if len(descriptions) != 1 or not content_value(descriptions[0]): errors.append((rel,'missing/duplicate meta description'))
    canon = re.findall(r'<link[^>]+rel=["\']canonical["\'][^>]*>', doc, re.I)
    if len(canon) != 1 or not re.search(r'href=["\']https://laxmannepal\\.com\\.np/', canon[0], re.I): errors.append((rel,'missing/invalid canonical'))
    for kind in ('og:title','og:description','og:url'):
        tags = meta(doc, prop=kind)
        if len(tags) != 1 or not content_value(tags[0]): errors.append((rel,f'missing/duplicate {kind}'))
    for kind in ('twitter:title','twitter:description'):
        tags = meta(doc, name=kind)
        if len(tags) != 1 or not content_value(tags[0]): errors.append((rel,f'missing/duplicate {kind}'))
    if not re.search(r'property=["\']og:type["\']', doc, re.I): warnings.append((rel,'missing og:type'))
    if not re.search(r'<script[^>]+type=["\']application/ld\+json["\']', doc, re.I): warnings.append((rel,'missing JSON-LD structured data'))
    h1 = len(re.findall(r'<h1\b', doc, re.I))
    if h1 == 0: warnings.append((rel,'missing h1'))
    if h1 > 1: warnings.append((rel,f'multiple h1 tags: {h1}'))

for p in files:
    check_file(p)

print(f'Checked SEO health for {len(files)} HTML pages under {TARGET}')
if errors:
    print(f'Found {len(errors)} SEO errors:')
    for p,m in errors[:150]: print(f'- ERROR {p}: {m}')
    if len(errors)>150: print(f'... {len(errors)-150} more')
if warnings:
    print(f'Found {len(warnings)} SEO warnings:')
    for p,m in warnings[:100]: print(f'- WARN {p}: {m}')
    if len(warnings)>100: print(f'... {len(warnings)-100} more')
if errors: sys.exit(1)
print('SEO health audit passed.')