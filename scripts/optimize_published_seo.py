#!/usr/bin/env python3
"""Post-build SEO optimizer for every published HTML page."""
from __future__ import annotations
import hashlib, html, re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://laxmannepal.com.np"
PAGES = ROOT / ".pages"

NOINDEX_PARTS = ("/old/", "/scripts/")

def clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return html.unescape(re.sub(r"<[^>]+>", " ", s)).strip()

def title_from(path: Path, doc: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", doc, re.I | re.S)
    if m:
        t = clean_text(m.group(1))
        if t and t.lower() not in {"loading...", "untitled"}:
            return t[:65]
    m = re.search(r"<h1[^>]*>(.*?)</h1>", doc, re.I | re.S)
    if m:
        t = clean_text(m.group(1))
        if t:
            return t[:65]
    stem = path.stem.replace("-", " ").replace("_", " ")
    return stem.title() if stem else "Laxman Nepal"

def description_from(title: str, doc: str) -> str:
    m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', doc, re.I | re.S)
    if m and clean_text(m.group(1)):
        return clean_text(m.group(1))[:160]
    m = re.search(r"<p[^>]*>(.*?)</p>", doc, re.I | re.S)
    p = clean_text(m.group(1)) if m else ""
    return (p or f"{title} — practical tools, tutorials and digital resources from Laxman Nepal.")[:160]

def url_for(path: Path) -> str:
    rel = path.relative_to(PAGES).as_posix()
    if rel == "index.html":
        return SITE + "/"
    if rel.endswith("/index.html"):
        return SITE + "/" + rel[:-10].rstrip("/") + "/"
    return SITE + "/" + rel

def replace_or_insert(doc: str, pattern: str, tag: str) -> str:
    if re.search(pattern, doc, re.I):
        return re.sub(pattern, tag, doc, count=1, flags=re.I)
    return doc.replace("</head>", tag + "\n</head>", 1)

def optimize(path: Path) -> bool:
    doc = path.read_text(encoding="utf-8", errors="ignore")
    if "<html" not in doc.lower() or "</head>" not in doc.lower():
        return False
    title = title_from(path, doc)
    desc = description_from(title, doc)
    canonical = url_for(path)
    noindex = any(part in canonical for part in NOINDEX_PARTS)

    doc = re.sub(r"<title[^>]*>.*?</title>", f"<title>{html.escape(title)}</title>", doc, count=1, flags=re.I|re.S)
    if "<title" not in doc.lower():
        doc = doc.replace("</head>", f"<title>{html.escape(title)}</title>\n</head>", 1)

    tags = [
        (r'<meta[^>]+name=["\']description["\'][^>]*>', f'<meta name="description" content="{html.escape(desc, quote=True)}">'),
        (r'<link[^>]+rel=["\']canonical["\'][^>]*>', f'<link rel="canonical" href="{html.escape(canonical, quote=True)}">'),
        (r'<meta[^>]+property=["\']og:title["\'][^>]*>', f'<meta property="og:title" content="{html.escape(title, quote=True)}">'),
        (r'<meta[^>]+property=["\']og:description["\'][^>]*>', f'<meta property="og:description" content="{html.escape(desc, quote=True)}">'),
        (r'<meta[^>]+property=["\']og:url["\'][^>]*>', f'<meta property="og:url" content="{html.escape(canonical, quote=True)}">'),
        (r'<meta[^>]+name=["\']twitter:title["\'][^>]*>', f'<meta name="twitter:title" content="{html.escape(title, quote=True)}">'),
        (r'<meta[^>]+name=["\']twitter:description["\'][^>]*>', f'<meta name="twitter:description" content="{html.escape(desc, quote=True)}">'),
    ]
    for pattern, tag in tags:
        doc = replace_or_insert(doc, pattern, tag)

    robots_tag = '<meta name="robots" content="noindex,follow">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">'
    doc = replace_or_insert(doc, r'<meta[^>]+name=["\']robots["\'][^>]*>', robots_tag)

    if not re.search(r'property=["\']og:type["\']', doc, re.I):
        doc = doc.replace("</head>", '<meta property="og:type" content="article">\n</head>', 1)

    if not re.search(r'itemtype=["\']https://schema.org/(WebPage|Article)["\']', doc, re.I):
        schema_type = "Article" if path.name != "index.html" and "/blog/" in canonical else "WebPage"
        schema = {
            "@context": "https://schema.org",
            "@type": schema_type,
            "name": title,
            "description": desc,
            "url": canonical,
            "isPartOf": {"@type": "WebSite", "name": "Laxman Nepal", "url": SITE}
        }
        import json
        block = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False, separators=(",", ":")) + '</script>'
        doc = doc.replace("</head>", block + "\n</head>", 1)

    if doc != path.read_text(encoding="utf-8", errors="ignore"):
        path.write_text(doc, encoding="utf-8")
        return True
    return False

def main():
    files = list(PAGES.rglob("*.html"))
    changed = sum(optimize(p) for p in files)
    urls = []
    for p in files:
        u = url_for(p)
        if any(x in u for x in NOINDEX_PARTS):
            continue
        urls.append(u)
    urls = sorted(set(urls))
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap += [f"  <url><loc>{html.escape(u)}</loc></url>" for u in urls]
    sitemap.append("</urlset>")
    (PAGES / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    (PAGES / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nDisallow: /old/\nDisallow: /scripts/\n\n"
        f"Sitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print(f"SEO optimized {changed}/{len(files)} HTML pages; sitemap contains {len(urls)} indexable URLs.")

if __name__ == "__main__":
    main()
