from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
SHARED_CSS = "https://apps.laxmannepal.com.np/Nepali-Patro/css/shared-shell.css"

HEADER = r'''<header class="shared-header" data-shared-shell="header">
<a class="shared-brand" href="/" aria-label="Laxman Nepal home"><span class="shared-logo">LN</span><span><strong>Laxman Nepal</strong><small>Technology & Digital Nepal</small></span></a>
<nav class="shared-desktop-nav" aria-label="Main menu">
<a href="/news/">📰 News</a><a href="/reviews/">⭐ Reviews</a><a href="/mobile/">📱 Mobile</a><a href="/laptop/">💻 Laptops</a><a href="/guides/">📖 Guides</a><a href="/gadgets/">🔌 Gadgets</a>
<details class="nav-dropdown"><summary>🧰 Tools</summary><div class="nav-dropdown-menu"><a href="/tools/">🧰 All Tools</a><a href="/apps/nepali-patro/">📅 Nepali Patro</a><a href="/apps/nepse/">📈 NEPSE Pulse</a><a href="/tools/text-to-handwriting/">✍️ Text to Handwriting</a><a href="/progress-bar/">📊 Progress Bar</a></div></details>
<details class="nav-dropdown"><summary>🇳🇵 Nepal</summary><div class="nav-dropdown-menu"><a href="/brands/">🏷️ Brands</a><a href="/mobile/price/">📱 Mobile Prices</a><a href="/laptop/price/">💻 Laptop Prices</a><a href="/blog/">📝 Blog</a></div></details><a href="/tools/">▦ All</a>
</nav>
<div class="shared-actions"><form class="shared-search-box" action="/search/" method="get"><span aria-hidden="true">⌕</span><input name="q" type="search" autocomplete="off" aria-label="Search Laxman Nepal" placeholder="Search technology…"></form><button class="shared-menu-btn" type="button" data-shared-menu aria-label="Open menu">☰</button></div>
</header>
<nav class="shared-mobile-menu" data-shared-mobile aria-label="Mobile menu"><div class="shared-mobile-head"><strong>Laxman Nepal</strong><button type="button" data-shared-close aria-label="Close menu">×</button></div><a href="/">🏠 Home</a><a href="/news/">📰 News</a><a href="/reviews/">⭐ Reviews</a><a href="/mobile/">📱 Mobile</a><a href="/laptop/">💻 Laptops</a><a href="/guides/">📖 Buying Guides</a><a href="/gadgets/">🔌 Gadgets</a><a href="/tools/">🧰 All Tools</a><a href="/apps/nepali-patro/">📅 Nepali Patro</a><a href="/apps/nepse/">📈 NEPSE Pulse</a><a href="/brands/">🏷️ Brands</a></nav><div class="shared-menu-backdrop" data-shared-backdrop></div>'''

FOOTER = r'''<footer class="shared-footer" data-shared-shell="footer"><div class="shared-footer-grid"><div><div class="shared-footer-brand"><span class="shared-logo">LN</span><strong>Laxman Nepal</strong></div><p>Practical technology news, gadget reviews, buying guides, prices, AI and useful digital tools for Nepal.</p></div><div><strong>Explore</strong><a href="/news/">News</a><a href="/reviews/">Reviews</a><a href="/mobile/">Mobile</a><a href="/laptop/">Laptops</a><a href="/gadgets/">Gadgets</a></div><div><strong>Resources</strong><a href="/guides/">Buying Guides</a><a href="/brands/">Brands</a><a href="/mobile/price/">Mobile Prices</a><a href="/laptop/price/">Laptop Prices</a><a href="/tools/">Free Tools</a></div><div><strong>Creator & Apps</strong><a href="/apps/nepali-patro/">Nepali Patro</a><a href="/apps/nepse/">NEPSE Pulse</a><a href="https://www.youtube.com/@laxmannepalofficial">YouTube</a><a href="https://www.instagram.com/laxmannepalsir/">Instagram</a><a href="https://github.com/LaxmanNepal">GitHub</a></div></div><div class="shared-footer-bottom"><span>© <span id="year"></span> Laxman Nepal · All rights reserved</span><span>Built for Nepal · Built for usefulness.</span></div></footer>'''

SCRIPT = r'''<script data-shared-shell-script="laxman">(()=>{const m=document.querySelector('[data-shared-menu]'),n=document.querySelector('[data-shared-mobile]'),c=document.querySelector('[data-shared-close]'),b=document.querySelector('[data-shared-backdrop]');const hide=()=>{n?.classList.remove('open');if(b)b.style.display='none';document.body.style.overflow=''};m?.addEventListener('click',()=>{n?.classList.add('open');if(b)b.style.display='block';document.body.style.overflow='hidden'});c?.addEventListener('click',hide);b?.addEventListener('click',hide);n?.querySelectorAll('a').forEach(a=>a.addEventListener('click',hide));document.addEventListener('keydown',e=>{if(e.key==='Escape')hide()});const y=document.getElementById('year');if(y)y.textContent=new Date().getFullYear()})();</script>'''


def replace_once(text, pattern, replacement):
    new, count = re.subn(pattern, replacement, text, count=1, flags=re.I | re.S)
    if count != 1:
        raise RuntimeError(f"Required homepage element not found: {pattern}")
    return new


def main():
    text = INDEX.read_text(encoding="utf-8")
    if SHARED_CSS not in text:
        text = text.replace('</head>', f'<link rel="stylesheet" href="{SHARED_CSS}">\n</head>', 1)
    text = replace_once(text, r'<header\s+class=["\']gb-header["\'].*?</header>', HEADER)
    text = replace_once(text, r'<footer\s+class=["\']gb-footer["\'].*?</footer>', FOOTER)
    text = re.sub(r'<script>\s*\(\(\)=>\{const y=document\.getElementById\(["\']year["\']\).*?</script>', '', text, count=1, flags=re.I | re.S)
    if 'data-shared-shell-script="laxman"' not in text:
        text = text.replace('</body>', SCRIPT + '\n</body>', 1)
    INDEX.write_text(text, encoding="utf-8")
    print("Applied Nepali Patro-style header/footer with Laxman Nepal branding.")


if __name__ == "__main__":
    main()
