from pathlib import Path
import posixpath
import re
import sys
from urllib.parse import unquote, urlsplit

TARGET = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
TARGET = TARGET.resolve()
EXCLUDED = {'.git', 'node_modules', '.pages', 'out', '.next'}
ATTR_RE = re.compile(r'''\b(?:href|src|poster|action)\s*=\s*["']([^"']+)["']''', re.I)
SRCSET_RE = re.compile(r'''\bsrcset\s*=\s*["']([^"']+)["']''', re.I)
SKIP_SCHEMES = {'http', 'https', 'mailto', 'tel', 'javascript', 'data', 'blob'}
SKIP_VALUES = {'', '#', '/', '/#'}

def html_files(root):
    return [p for p in root.rglob('*.html') if not any(x in EXCLUDED for x in p.relative_to(root).parts)]

def is_dynamic(value):
    return any(x in value for x in ('${', '{{', '}}', '<%', '%>'))

def candidate_paths(root, source, page):
    split = urlsplit(unquote(source))
    path = split.path
    if not path or path == '/': return []
    if path.startswith('/'): rel = posixpath.normpath(path.lstrip('/'))
    else:
        base = page.parent.relative_to(root).as_posix()
        rel = posixpath.normpath(posixpath.join(base, path))
    if rel.startswith('../') or rel == '..': return []
    p = Path(rel)
    candidates = [root / rel]
    if p.suffix == '': candidates += [root / rel / 'index.html', root / (rel + '.html')]
    return candidates

def exists_reference(root, source, page):
    candidates = candidate_paths(root, source, page)
    return not candidates or any(p.is_file() for p in candidates)

pages = html_files(TARGET)
errors = []
checked = 0
for page in sorted(pages):
    try: text = page.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError): continue
    refs = ATTR_RE.findall(text)
    for srcset in SRCSET_RE.findall(text):
        refs.extend(part.strip().split()[0] for part in srcset.split(',') if part.strip())
    for raw in refs:
        value = raw.strip()
        if value in SKIP_VALUES or value.startswith('#') or is_dynamic(value): continue
        if urlsplit(value).scheme.lower() in SKIP_SCHEMES or value.startswith('//') or value.startswith('www.'): continue
        checked += 1
        if not exists_reference(TARGET, value, page): errors.append((str(page.relative_to(TARGET)), value))

print(f'Audited {len(pages)} HTML pages and {checked} local references under {TARGET}')
if errors:
    print(f'Found {len(errors)} broken local references:')
    for page, value in errors[:150]: print(f'- {page}: {value}')
    if len(errors) > 150: print(f'... {len(errors)-150} more')
    sys.exit(1)
print('No broken local references found.')