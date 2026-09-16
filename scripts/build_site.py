#!/usr/bin/env python3
"""Build the Laxman Nepal blog/tools layer without touching /apps."""
from __future__ import annotations
import html, json, re
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "site.config.json").read_text(encoding="utf-8"))
BASE = CFG["site_url"].rstrip("/")
BLOG = ROOT / "content" / "blog"
OUT = ROOT / "blog"
TOOLS = json.loads((ROOT / "data" / "tools.json").read_text(encoding="utf-8")).get("tools", [])

def esc(v): return html.escape(str(v), quote=True)

def frontmatter(text):
    meta, body = {}, text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            body = parts[2].lstrip("\n")
            for line in parts[1].splitlines():
                if ":" not in line: continue
                k, v = line.split(":", 1)
                v = v.strip().strip('"\'')
                meta[k.strip()] = [x.strip() for x in v.split(",") if x.strip()] if k.strip() == "tags" else v
    return meta, body

def clean_date(value):
    value = str(value or "")[:10]
    try: datetime.strptime(value, "%Y-%m-%d"); return value
    except ValueError: return datetime.now(timezone.utc).date().isoformat()

def markdown(src):
    out, para, code, ul = [], [], False, False
    def flush():
        nonlocal para
        if para:
            text = html.escape(" ".join(para), quote=False)
            text = re.sub(r"\[([^]]+)\]\((https?://[^)]+)\)", r'<a href="\2" rel="noopener noreferrer">\1</a>', text)
            text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
            text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
            out.append("<p>" + text + "</p>"); para = []
    for line in src.replace("\r\n", "\n").split("\n"):
        if line.startswith("```"):
            if code:
                out.append("<pre><code>" + esc("\n".join(para)) + "</code></pre>"); para=[]; code=False
            else: flush(); code=True
            continue
        if code: para.append(line); continue
        if not line.strip(): flush(); continue
        m = re.match(r"^(#{1,3})\s+(.+)$", line)
        if m:
            flush()
            if ul: out.append("</ul>"); ul=False
            level=len(m.group(1))+1; txt=html.escape(m.group(2), quote=False); ident=re.sub(r"[^a-z0-9]+","-",m.group(2).lower()).strip("-")
            out.append(f'<h{level} id="{esc(ident)}">{txt}</h{level}>')
        elif re.match(r"^[-*]\s+", line):
            flush()
            if not ul: out.append("<ul>"); ul=True
            out.append("<li>"+esc(re.sub(r"^[-*]\s+", "", line))+"</li>")
        else:
            if ul: out.append("</ul>"); ul=False
            para.append(line)
    flush()
    if ul: out.append("</ul>")
    return "\n".join(out)

HEADER = '''<header class="shared-header"><a class="shared-brand" href="/"><span class="shared-logo">LN</span><span><strong>Laxman Nepal</strong><small>Tools · AI · Blog · Digital</small></span></a><nav class="shared-desktop-nav" aria-label="Main menu"><a href="/tools/">Tools</a><a href="/ai-tools/">AI</a><a href="/blog/">Blog</a><a href="/apps/">Apps</a><a href="/youtube/">YouTube</a><details class="nav-dropdown"><summary>Explore</summary><div class="nav-dropdown-menu"><a href="/news/">News & Updates</a><a href="/guides/">Guides</a><a href="/mobile/">Mobile</a><a href="/laptop/">Laptops</a><a href="/gadgets/">Gadgets</a><a href="/brands/">Brands</a></div></details></nav><div class="shared-actions"><form class="shared-search-box" action="/search/" method="get"><span>⌕</span><input name="q" type="search" placeholder="Search tools & guides…" aria-label="Search"></form><button class="shared-menu-btn" type="button" data-shared-menu aria-label="Open menu">☰</button></div></header><nav class="shared-mobile-menu" data-shared-mobile><div class="shared-mobile-head"><strong>Laxman Nepal</strong><button type="button" data-shared-close>×</button></div><a href="/">🏠 Home</a><a href="/tools/">🧰 Tools</a><a href="/ai-tools/">✨ AI Tools</a><a href="/blog/">📝 Blog</a><a href="/apps/">📦 Apps</a><a href="/youtube/">▶ YouTube</a><a href="/guides/">📖 Guides</a><a href="/news/">📰 News</a><a href="/about/">About</a></nav><div class="shared-menu-backdrop" data-shared-backdrop></div>'''
FOOTER = '''<footer class="shared-footer"><div class="shared-footer-grid"><div><div class="shared-footer-brand"><span class="shared-logo">LN</span><strong>Laxman Nepal</strong></div><p>Practical tools, AI resources, tutorials and useful digital guides built by Laxman Nepal.</p></div><div><strong>Tools</strong><a href="/tools/">All Tools</a><a href="/ai-tools/">AI Tools</a><a href="/apps/">Apps</a><a href="/youtube/">YouTube Tools</a></div><div><strong>Content</strong><a href="/blog/">Blog</a><a href="/news/">News</a><a href="/guides/">Guides</a><a href="/about/">About</a></div><div><strong>Connect</strong><a href="https://www.youtube.com/@laxmannepalofficial">YouTube</a><a href="https://www.instagram.com/laxmannepalsir/">Instagram</a><a href="https://github.com/LaxmanNepal">GitHub</a><a href="/contact/">Contact</a></div></div><div class="shared-footer-bottom"><span>© <span id="year"></span> Laxman Nepal · All rights reserved</span><span>Built for usefulness.</span></div></footer>'''
SCRIPT = '''<script>(()=>{const m=document.querySelector('[data-shared-menu]'),n=document.querySelector('[data-shared-mobile]'),c=document.querySelector('[data-shared-close]'),b=document.querySelector('[data-shared-backdrop]');const hide=()=>{n?.classList.remove('open');if(b)b.style.display='none';document.body.style.overflow=''};m?.addEventListener('click',()=>{n?.classList.add('open');if(b)b.style.display='block';document.body.style.overflow='hidden'});c?.addEventListener('click',hide);b?.addEventListener('click',hide);n?.querySelectorAll('a').forEach(a=>a.addEventListener('click',hide));const y=document.getElementById('year');if(y)y.textContent=new Date().getFullYear()})();</script>'''

def shell(title, desc, canonical, body, kind="WebPage", image=""):
    og = f'<meta property="og:image" content="{esc(BASE+image if image.startswith("/") else image)}">' if image else ''
    schema={"@context":"https://schema.org","@type":kind,"name":title,"url":canonical,"description":desc}
    if image: schema["image"] = BASE+image if image.startswith("/") else image
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{esc(desc)}"><meta name="author" content="Laxman Nepal"><link rel="canonical" href="{esc(canonical)}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{esc(canonical)}">{og}<meta name="twitter:card" content="summary_large_image"><title>{esc(title)} — Laxman Nepal</title><link rel="stylesheet" href="/assets/css/shared-shell.css"><link rel="stylesheet" href="/assets/css/blog-images.css"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script></head><body>{HEADER}<main>{body}</main>{FOOTER}{SCRIPT}</body></html>'''

def load_articles():
    items=[]
    for p in sorted(BLOG.glob("*.md")):
        if p.name.lower()=="readme.md": continue
        meta,src=frontmatter(p.read_text(encoding="utf-8")); meta.setdefault("title",p.stem.replace("-"," ").title()); meta.setdefault("description","Practical technology, AI and productivity guidance by Laxman Nepal."); meta["date"]=clean_date(meta.get("date")); meta["updated"]=clean_date(meta.get("updated",meta["date"])); meta.setdefault("author","Laxman Nepal"); meta.setdefault("category","Technology"); meta["tags"]=meta.get("tags",[]) if isinstance(meta.get("tags",[]),list) else [str(meta["tags"])]; meta["slug"]=re.sub(r"[^a-z0-9]+","-",p.stem.lower()).strip("-"); meta["url"]=f"{BASE}/blog/{meta['slug']}/"; meta["source"]=src; items.append(meta)
    return sorted(items,key=lambda x:x["date"],reverse=True)

def main():
    articles=load_articles(); OUT.mkdir(parents=True,exist_ok=True)
    for a in articles:
        content=markdown(a["source"]); words=len(re.findall(r"\b[\w’'-]+\b",content)); mins=max(1,round(words/220)); hero=f'<img class="article-hero" src="{esc(a["image"])}" alt="{esc(a.get("image_alt",a["title"]))}" loading="eager">' if a.get("image") else ''
        body=f'''<div class="article-wrap"><article><nav class="breadcrumbs"><a href="/">Home</a> / <a href="/blog/">Blog</a> / {esc(a["title"])}</nav><header class="article-header"><p class="eyebrow">{esc(a["category"])} · {mins} min read</p><h1>{esc(a["title"])}</h1><p class="article-description">{esc(a["description"])}</p><div class="article-meta">By {esc(a["author"])} · Published {a["date"]} · Updated {a["updated"]}</div></header>{hero}<div class="article-content">{content}</div></article></div>'''
        (OUT/a["slug"]/"index.html").parent.mkdir(parents=True,exist_ok=True); (OUT/a["slug"]/"index.html").write_text(shell(a["title"],a["description"],a["url"],body,"Article",a.get("image","")),encoding="utf-8")
    cards="".join(f'<article class="post-card"><p class="eyebrow">{esc(a["category"])} · {a["date"]}</p><h2><a href="/blog/{a["slug"]}/">{esc(a["title"])}</a></h2><p>{esc(a["description"])}</p><a class="text-link" href="/blog/{a["slug"]}/">Read article →</a></article>' for a in articles)
    blog_body=f'<div class="article-wrap"><section class="blog-hero"><p class="eyebrow">Laxman Nepal Journal</p><h1>Useful ideas.<br><em>Explained simply.</em></h1><p>Practical guides about technology, AI, apps, productivity and digital work.</p><input id="blogFilter" class="search-box" placeholder="Filter articles…" aria-label="Filter articles"></section><section class="post-grid" id="postGrid">{cards or "<p>No articles published yet.</p>"}</section></div><script>const i=document.querySelector("#blogFilter");i?.addEventListener("input",()=>{const v=i.value.toLowerCase();document.querySelectorAll("#postGrid .post-card").forEach(c=>c.hidden=v&&!c.innerText.toLowerCase().includes(v))});</script>'
    (OUT/"index.html").write_text(shell("Blog","Practical technology, AI, apps and productivity articles by Laxman Nepal.",BASE+"/blog/",blog_body),encoding="utf-8")
    items="".join(f'<a class="tool-card" href="{esc(t["url"])}"><span class="tool-icon">{esc(t.get("icon","✦"))}</span><span class="tool-category">{esc(t.get("category","Tools"))}</span><h2>{esc(t["name"])}</h2><p>{esc(t["description"])}</p><span class="tool-open">Open tool →</span></a>' for t in TOOLS)
    tools_body=f'<div class="article-wrap"><section class="blog-hero"><p class="eyebrow">Laxman Tools</p><h1>Useful tools.<br><em>One place.</em></h1><p>Fast browser tools for creators, productivity, Nepal and everyday digital work.</p><input id="toolSearch" class="search-box" placeholder="Search tools…" aria-label="Search tools"></section><section class="tools-grid" id="toolGrid">{items}</section></div><script>const s=document.querySelector("#toolSearch");s?.addEventListener("input",()=>{const v=s.value.toLowerCase();document.querySelectorAll("#toolGrid .tool-card").forEach(c=>c.hidden=!c.innerText.toLowerCase().includes(v))});</script>'
    (ROOT/"tools"/"index.html").write_text(shell("Useful Tools","Explore practical web tools and utilities by Laxman Nepal.",BASE+"/tools/",tools_body),encoding="utf-8")
    search=[{"title":a["title"],"description":a["description"],"url":a["url"],"type":"article"} for a in articles]+[{"title":t["name"],"description":t["description"],"url":t["url"],"type":"tool"} for t in TOOLS]
    (ROOT/"search-index.json").write_text(json.dumps(search,ensure_ascii=False,indent=2),encoding="utf-8")
    feed_items=[]
    for a in articles:
        dt=datetime.strptime(a["updated"],"%Y-%m-%d").replace(tzinfo=timezone.utc); feed_items.append(f'<item><title>{esc(a["title"])}</title><link>{esc(a["url"])}</link><guid>{esc(a["url"])}</guid><pubDate>{format_datetime(dt,usegmt=True)}</pubDate><description>{esc(a["description"])}</description></item>')
    (ROOT/"feed.xml").write_text('<?xml version="1.0"?><rss version="2.0"><channel><title>Laxman Nepal</title><link>'+BASE+'</link>'+''.join(feed_items)+'</channel></rss>',encoding="utf-8")
    urls={BASE+"/":datetime.now(timezone.utc).date().isoformat(),BASE+"/blog/":datetime.now(timezone.utc).date().isoformat(),BASE+"/tools/":datetime.now(timezone.utc).date().isoformat()}
    for a in articles: urls[a["url"]]=a["updated"]
    for t in TOOLS: urls[t["url"]]=t.get("updated",urls[BASE+"/tools/"])
    (ROOT/"sitemap.xml").write_text('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{esc(u)}</loc><lastmod>{d}</lastmod></url>' for u,d in sorted(urls.items()))+'</urlset>',encoding="utf-8")
    print(f"Built {len(articles)} blog articles and {len(TOOLS)} tools; /apps was not modified.")

if __name__ == "__main__": main()
