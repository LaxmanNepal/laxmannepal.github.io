from pathlib import Path
import os
import re
import json

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MANIFEST = ROOT / ".blogger-migration.json"
SHARED_CSS = "/assets/css/shared-shell.css"
LEGACY_CSS = "/assets/css/legacy-normalizer.css"

HEADER = r'''<header class="shared-header" data-shared-shell="header">
<a class="shared-brand" href="/" aria-label="Laxman Nepal home"><span class="shared-logo">LN</span><span><strong>Laxman Nepal</strong><small>Tools · AI · Blog · Digital</small></span></a>
<nav class="shared-desktop-nav" aria-label="Main menu">
<a href="/tools/">Tools</a><a href="/ai-tools/">AI</a><a href="/blog/">Blog</a><a href="/apps/">Apps</a><a href="/youtube-tools/">YouTube</a>
<details class="nav-dropdown"><summary>Explore</summary><div class="nav-dropdown-menu"><a href="/news/">News & Updates</a><a href="/guides/">Guides</a><a href="/mobile/">Mobile</a><a href="/laptop/">Laptops</a><a href="/gadgets/">Gadgets</a><a href="/brands/">Brands</a></div></details>
</nav>
<div class="shared-actions"><form class="shared-search-box" action="/search/" method="get"><span aria-hidden="true">⌕</span><input name="q" type="search" autocomplete="off" aria-label="Search Laxman Nepal" placeholder="Search tools & guides…"></form><button class="shared-menu-btn" type="button" data-shared-menu aria-label="Open menu">☰</button></div>
</header>
<nav class="shared-mobile-menu" data-shared-mobile aria-label="Mobile menu"><div class="shared-mobile-head"><strong>Laxman Nepal</strong><button type="button" data-shared-close aria-label="Close menu">×</button></div><a href="/">🏠 Home</a><a href="/tools/">🧰 Tools</a><a href="/ai-tools/">✨ AI Tools</a><a href="/blog/">📝 Blog</a><a href="/apps/">📦 Apps</a><a href="/youtube-tools/">▶ YouTube</a><a href="/guides/">📖 Guides</a><a href="/news/">📰 News</a><a href="/about/">About</a></nav><div class="shared-menu-backdrop" data-shared-backdrop></div>'''

FOOTER = r'''<footer class="shared-footer" data-shared-shell="footer"><div class="shared-footer-grid"><div><div class="shared-footer-brand"><span class="shared-logo">LN</span><strong>Laxman Nepal</strong></div><p>Practical tools, AI resources, tutorials and useful digital guides built by Laxman Nepal.</p></div><div><strong>Tools</strong><a href="/tools/">All Tools</a><a href="/ai-tools/">AI Tools</a><a href="/apps/">Apps</a><a href="/youtube-tools/">YouTube Tools</a></div><div><strong>Content</strong><a href="/blog/">Blog</a><a href="/news/">News</a><a href="/guides/">Guides</a><a href="/about/">About</a></div><div><strong>Connect</strong><a href="https://www.youtube.com/@laxmannepalofficial">YouTube</a><a href="https://www.instagram.com/laxmannepalsir/">Instagram</a><a href="https://github.com/LaxmanNepal">GitHub</a><a href="/contact/">Contact</a></div></div><div class="shared-footer-bottom"><span>© <span id="year"></span> Laxman Nepal · All rights reserved</span><span>Built for usefulness.</span></div></footer>'''

SCRIPT = r'''<script data-shared-shell-script="laxman">(()=>{const m=document.querySelector('[data-shared-menu]'),n=document.querySelector('[data-shared-mobile]'),c=document.querySelector('[data-shared-close]'),b=document.querySelector('[data-shared-backdrop]');const hide=()=>{n?.classList.remove('open');if(b)b.style.display='none';document.body.style.overflow=''};m?.addEventListener('click',()=>{n?.classList.add('open');if(b)b.style.display='block';document.body.style.overflow='hidden'});c?.addEventListener('click',hide);b?.addEventListener('click',hide);n?.querySelectorAll('a').forEach(a=>a.addEventListener('click',hide));document.addEventListener('keydown',e=>{if(e.key==='Escape')hide()});const y=document.getElementById('year');if(y)y.textContent=new Date().getFullYear()})();</script>'''

def apply_shell(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False
    text = re.sub(r'<header\s+class=["\']shared-header["\'][^>]*>.*?</header>', '', text, count=1, flags=re.I | re.S)
    # Remove every previous shared mobile menu and backdrop. Older pages can place the backdrop outside the nav.
    text = re.sub(r'<nav\s+class=["\']shared-mobile-menu["\'][^>]*>.*?</nav>', '', text, count=0, flags=re.I | re.S)
    text = re.sub(r'<div\s+class=["\']shared-menu-backdrop["\'][^>]*>.*?</div>', '', text, count=0, flags=re.I | re.S)
    text = re.sub(r'<footer\s+class=["\']shared-footer["\'][^>]*>.*?</footer>', '', text, count=1, flags=re.I | re.S)
     text = re.sub(r'<link[^>]+(?:shared-shell\.css|legacy-normalizer\.css)[^>]*>', '', text, count=0, flags=re.I)
    text = re.sub(r'<header\s+class=["\']gb-header["\'][^>]*>.*?</header>', '', text, count=1, flags=re.I | re.S)
    text = re.sub(r'<footer\s+class=["\']gb-footer["\'][^>]*>.*?</footer>', '', text, count=1, flags=re.I | re.S)
    if re.search(r'</head\s*>', text, flags=re.I):
         text = re.sub(r'</head\s*>', f'<link rel="stylesheet" href="{SHARED_CSS}">\n<link rel="stylesheet" href="{LEGACY_CSS}">\n</head>', text, count=1, flags=re.I)
    body_match = re.search(r'<body\b[^>]*>', text, flags=re.I)
    if body_match:
        text = text[:body_match.end()] + HEADER + text[body_match.end():]
        text = re.sub(r'<script>\s*\(\(\)=>\{const y=document\.getElementById\(["\']year["\']\).*?</script>', '', text, count=1, flags=re.I | re.S)
        if re.search(r'</body\s*>', text, flags=re.I):
            text = re.sub(r'</body\s*>', FOOTER + SCRIPT + '\n</body>', text, count=1, flags=re.I)
    else:
        return False
    path.write_text(text, encoding="utf-8")
    return True

def main():
    target = Path(os.environ.get("SHELL_ROOT", str(ROOT))).resolve()
    excluded = {".git", "node_modules", ".pages", "out", ".next"}
    files = [p for p in target.rglob("*.html") if not any(part in excluded for part in p.relative_to(target).parts)]
    changed = sum(apply_shell(path) for path in sorted(files))
    print(f"Applied Laxman shared shell to {changed} HTML pages under {target}")

if __name__ == "__main__":
    main()
