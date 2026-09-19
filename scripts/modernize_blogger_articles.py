#!/usr/bin/env python3
"""Apply the shared modern Laxman Nepal article shell to migrated Blogger HTML.

The original article body/scripts/styles are preserved. This only adds a shared
site header/footer, article metadata, JSON-LD, modern reading wrapper, and
responsive presentation around the legacy document.
"""
from __future__ import annotations
import html, json, re
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".blogger-migration.json"
BASE = "https://laxmannepal.com.np"
CSS = "/assets/css/shared-shell.css"

HEADER = '''<header class="modern-article-header">
<a class="modern-brand" href="/" aria-label="Laxman Nepal home"><span class="modern-logo">LN</span><span><strong>Laxman Nepal</strong><small>Technology · Tools · AI · Creator Intelligence</small></span></a>
<nav aria-label="Main navigation"><a href="/news/">News</a><a href="/reviews/">Reviews</a><a href="/guides/">Guides</a><a href="/tools/">Tools</a><a href="/ai/">AI</a><a href="/youtube/">YouTube</a></nav>
<a class="modern-search" href="/search/">⌕ <span>Search</span></a>
</header>'''

FOOTER = '''<footer class="modern-article-footer">
<div><a class="modern-brand" href="/"><span class="modern-logo">LN</span><span><strong>Laxman Nepal</strong><small>Technology · Tools · AI · Creator Intelligence</small></span></a><p>Practical technology, tools, AI resources and useful digital guides.</p></div>
<div><strong>Explore</strong><a href="/news/">News</a><a href="/guides/">Guides</a><a href="/tools/">Tools</a><a href="/apps/">Apps</a></div>
<div><strong>Connect</strong><a href="https://www.youtube.com/@laxmannepalofficial">YouTube</a><a href="https://www.instagram.com/laxmannepalsir/">Instagram</a><a href="https://github.com/LaxmanNepal">GitHub</a></div>
</footer>'''

STYLE = '''<style id="laxman-modern-article">
.modern-article-header{position:sticky;top:0;z-index:100;display:flex;align-items:center;gap:22px;min-height:70px;padding:12px clamp(18px,4vw,48px);background:rgba(255,255,255,.82);border-bottom:1px solid rgba(15,23,42,.09);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px)}
.modern-brand{display:flex;align-items:center;gap:10px;color:inherit;text-decoration:none;min-width:max-content}.modern-brand strong{display:block;font-size:15px;letter-spacing:-.02em}.modern-brand small{display:block;font-size:10px;opacity:.55;margin-top:2px}.modern-logo{width:38px;height:38px;display:grid;place-items:center;border-radius:12px;background:linear-gradient(135deg,#111827,#475569);color:#fff;font-weight:800;letter-spacing:-.06em}.modern-article-header nav{display:flex;gap:18px;margin-left:auto}.modern-article-header nav a,.modern-search{color:#475569;text-decoration:none;font-size:13px;font-weight:600}.modern-article-header nav a:hover,.modern-search:hover{color:#111827}.modern-search{padding:9px 13px;border:1px solid rgba(15,23,42,.1);border-radius:999px;background:rgba(255,255,255,.7)}
.modern-article-main{max-width:900px;margin:0 auto;padding:clamp(40px,7vw,88px) 20px 80px}.modern-breadcrumbs{font-size:12px;color:#64748b;margin-bottom:20px}.modern-breadcrumbs a{color:inherit}.modern-article-kicker{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px}.modern-pill{display:inline-flex;padding:6px 10px;border-radius:999px;background:#f1f5f9;color:#475569;font-size:11px;font-weight:700;letter-spacing:.06em}.modern-article-main h1{font-size:clamp(38px,6vw,72px);line-height:1.02;letter-spacing:-.055em;max-width:850px;margin:0 0 18px}.modern-dek{font-size:18px;line-height:1.7;color:#64748b;max-width:760px;margin:0 0 28px}.modern-reading-card{background:rgba(255,255,255,.92);border:1px solid rgba(15,23,42,.09);border-radius:28px;padding:clamp(22px,5vw,52px);box-shadow:0 24px 70px rgba(15,23,42,.08)}.modern-reading-card img{max-width:100%;height:auto;border-radius:16px}.modern-reading-card iframe{max-width:100%}.modern-reading-card h2{margin-top:40px;font-size:30px;letter-spacing:-.035em}.modern-reading-card h3{margin-top:28px;font-size:23px}.modern-reading-card p,.modern-reading-card li{font-size:17px;line-height:1.8}.modern-reading-card a{color:inherit;text-underline-offset:3px}.modern-related{margin-top:46px;padding:24px;border:1px solid rgba(15,23,42,.08);border-radius:22px;background:#f8fafc}.modern-related a{display:inline-block;margin-right:14px;margin-top:8px}.modern-article-footer{display:grid;grid-template-columns:2fr 1fr 1fr;gap:30px;padding:45px clamp(20px,5vw,60px);background:#0f172a;color:#e2e8f0}.modern-article-footer .modern-brand{color:#fff}.modern-article-footer p{color:#94a3b8;max-width:420px;line-height:1.6}.modern-article-footer strong{display:block;margin-bottom:12px}.modern-article-footer>a,.modern-article-footer div>a{display:block;color:#94a3b8;text-decoration:none;margin:8px 0;font-size:14px}
.modern-share{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:0 0 30px}.modern-share strong{font-size:13px;margin-right:4px}.modern-share a{padding:7px 11px;border:1px solid rgba(15,23,42,.1);border-radius:999px;text-decoration:none;font-size:12px;background:#fff}.modern-share a:hover{background:#f1f5f9}
@media(max-width:760px){.modern-article-header nav{display:none}.modern-article-header{justify-content:space-between}.modern-article-main{padding-top:38px}.modern-reading-card{border-radius:20px}.modern-article-footer{grid-template-columns:1fr}.modern-article-main h1{font-size:clamp(36px,11vw,58px)}}
</style>'''

def strip_existing_shell(body):
    # Remove the most common legacy site header/footer without touching article scripts.
    body = re.sub(r'<header\b[^>]*>.*?</header>', '', body, flags=re.I|re.S)
    body = re.sub(r'<footer\b[^>]*>.*?</footer>', '', body, flags=re.I|re.S)
    return body

def related_posts(posts, current):
    cur=current.get('path','')
    tags=set(current.get('tags',[]))
    ranked=[]
    for p in posts:
        if p.get('path')==cur: continue
        score=len(tags.intersection(set(p.get('tags',[])))) + (2 if p.get('type')==current.get('type') else 0)
        ranked.append((score,p))
    ranked.sort(key=lambda x:(x[0],x[1].get('published','')),reverse=True)
    return [p for _,p in ranked[:3]]

def modernize(path: Path, meta: dict, posts):
    text = path.read_text(encoding="utf-8")
    if 'id="laxman-modern-article"' in text:
        return False
    title = html.unescape(meta.get("title") or "")
    published = meta.get("published") or meta.get("updated") or ""
    canonical = BASE + meta.get("path", "")
    desc = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip()
    desc = desc[:155] + ("…" if len(desc) > 155 else "")
    title_esc, desc_esc, canonical_esc = (html.escape(x, quote=True) for x in (title, desc, canonical))
    plain = re.sub(r'\\s+', ' ', re.sub(r'<[^>]+>', ' ', text)).strip()
    reading_minutes = max(1, round(len(plain.split()) / 220))
    image_match = re.search(r'<img[^>]+src=["\\\']([^"\\\']+)', text, re.I)
    image = urljoin(canonical, image_match.group(1)) if image_match else ''
    schema = {
        "@context":"https://schema.org","@type":"Article","headline":title,
        "datePublished":published,"dateModified":meta.get("updated") or published,
        "mainEntityOfPage":{"@type":"WebPage","@id":canonical},
        "author":{"@type":"Person","name":"Laxman Nepal"},
        "publisher":{"@type":"Person","name":"Laxman Nepal"}
    }
    if image: schema['image'] = [image]
    head_add = f'<link rel="stylesheet" href="{CSS}"><link rel="canonical" href="{canonical_esc}"><meta name="description" content="{desc_esc}"><meta property="og:title" content="{title_esc}"><meta property="og:description" content="{desc_esc}"><meta property="og:url" content="{canonical_esc}"><meta property="og:type" content="article">{STYLE}<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'
    if re.search(r'</head\s*>', text, re.I):
        text = re.sub(r'</head\s*>', head_add+'</head>', text, count=1, flags=re.I)
    else:
        text = '<head>'+head_add+'</head>'+text
    body_match = re.search(r'<body\b([^>]*)>([\s\S]*?)</body>', text, re.I)
    if not body_match:
        return False
    inner = strip_existing_shell(body_match.group(2))
    date_label = ""
    if published:
        date_label = f'<span class="modern-pill">{html.escape(published[:10])}</span>'
    related = related_posts(posts, meta)
    related_html = ''.join('<a href="'+html.escape(p.get('path',''),quote=True)+'">'+html.escape(p.get('title','Read article'))+' →</a>' for p in related)
    share = '<div class="modern-share"><strong>Share</strong><a target="_blank" rel="noopener" href="https://www.facebook.com/sharer/sharer.php?u='+html.escape(canonical,quote=True)+'">Facebook</a><a target="_blank" rel="noopener" href="https://twitter.com/intent/tweet?url='+html.escape(canonical,quote=True)+'&text='+html.escape(title,quote=True)+'">X</a><a href="mailto:?subject='+html.escape(title,quote=True)+'&body='+html.escape(canonical,quote=True)+'">Email</a></div>'
    article = f'''<body>{HEADER}<main class="modern-article-main"><div class="modern-breadcrumbs"><a href="/">Laxman Nepal</a> / Blog / Article</div><div class="modern-article-kicker"><span class="modern-pill">ARTICLE</span>{date_label}<span class="modern-pill">{reading_minutes} MIN READ</span></div><h1>{title_esc}</h1><p class="modern-dek">{desc_esc}</p>{share}<article class="modern-reading-card">{inner}</article><section class="modern-related"><strong>Related from Laxman Nepal</strong><br>{related_html}<a href="/search/">Search all articles →</a></section></main>{FOOTER}</body>'''
    text = text[:body_match.start()] + article + text[body_match.end():]
    path.write_text(text, encoding="utf-8")
    return True

def main():
    if not MANIFEST.exists():
        print("No Blogger manifest; nothing to modernize.")
        return
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    changed=0
    for meta in data.get("posts",[]):
        rel=meta.get("path","").lstrip("/")
        if not rel: continue
        p=ROOT/rel
        if p.is_file() and modernize(p,meta,data.get('posts', [])): changed+=1
    print(f"Modernized {changed} Blogger article files.")

if __name__=="__main__":
    main()
