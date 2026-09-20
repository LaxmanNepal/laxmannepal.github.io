#!/usr/bin/env python3
"""Post-build SEO + analytics optimizer for every published HTML page."""
from __future__ import annotations
import html, re, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://laxmannepal.com.np"
GA4_ID = "G-VG1MHSYGQ0"
PAGES = ROOT / ".pages"

NOINDEX_PARTS = ("/old/", "/scripts/", "/search/", "/analytics/")

ANALYTICS = f"""<!-- Laxman Nepal GA4 analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
<script>
window.dataLayer=window.dataLayer||[];
function gtag(){{dataLayer.push(arguments);}}
gtag('js',new Date());
gtag('config','{GA4_ID}',{{anonymize_ip:true,send_page_view:true}});
(function(){{
  const send=(name,params={{}})=>{{try{{gtag('event',name,params)}}catch(e){{}}}};
  document.addEventListener('click',function(e){{
    const a=e.target.closest('a');
    if(!a)return;
    const href=a.href||'';
    const sameHost=href.startsWith(location.origin);
    if(!sameHost) send('outbound_click',{{link_url:href,link_text:(a.innerText||a.getAttribute('aria-label')||'').trim().slice(0,100)}});
    if(/\\.(pdf|zip|docx?|xlsx?|pptx?|csv|txt)$/i.test(href)) send('file_download',{{file_url:href,file_name:href.split('/').pop().split('?')[0]}});
    if(a.closest('[data-tool]')||/\\/(tools|ai)\\//i.test(new URL(href,location.href).pathname))
      send('tool_open',{{tool_name:(a.innerText||a.getAttribute('aria-label')||'').trim().slice(0,100),tool_url:href}});
  }});
  const seen={{}};
  const thresholds=[25,50,75,90];
  const onScroll=()=>{{
    const h=document.documentElement.scrollHeight-innerHeight;
    if(h<=0)return;
    const pct=Math.round((scrollY/h)*100);
    thresholds.forEach(t=>{{if(pct>=t&&!seen[t]){{seen[t]=1;send('scroll_depth',{{percent:t}});}}}});
  }};
  addEventListener('scroll',onScroll,{{passive:true}});
  const searchForms=document.querySelectorAll('form');
  searchForms.forEach(f=>f.addEventListener('submit',()=>{{
    const input=f.querySelector('input[name="q"],input[type="search"],input[placeholder*="Search" i]');
    if(input&&input.value.trim()) send('site_search',{{search_term:input.value.trim().slice(0,100)}});
  }}));
}})();
</script>
"""

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
    m = re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']description["\']', doc, re.I | re.S)
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
        schema = {"@context":"https://schema.org","@type":schema_type,"name":title,"description":desc,"url":canonical,"isPartOf":{"@type":"WebSite","name":"Laxman Nepal","url":SITE}}
        block = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False, separators=(",", ":")) + '</script>'
        doc = doc.replace("</head>", block + "\n</head>", 1)

    if "googletagmanager.com/gtag/js" not in doc and "G-VG1MHSYGQ0" not in doc:
        doc = doc.replace("</head>", ANALYTICS + "\n</head>", 1)

    original = path.read_text(encoding="utf-8", errors="ignore")
    if doc != original:
        path.write_text(doc, encoding="utf-8")
        return True
    return False

def main():
    if not PAGES.exists():
        raise SystemExit("Missing .pages build directory")
    files = list(PAGES.rglob("*.html"))
    changed = sum(optimize(p) for p in files)
    urls = []
    for p in files:
        u = url_for(p)
        if any(x in u for x in NOINDEX_PARTS):
            continue
        urls.append(u)
    urls = sorted(set(urls))
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap += [f"  <url><loc>{html.escape(u)}</loc></url>" for u in urls]
    sitemap.append("</urlset>")
    (PAGES / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    (PAGES / "robots.txt").write_text("User-agent: *\nAllow: /\nDisallow: /old/\nDisallow: /scripts/\n\n" + f"Sitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print(f"SEO + GA4 optimized {changed}/{len(files)} HTML pages; sitemap contains {len(urls)} indexable URLs.")

if __name__ == "__main__":
    main()
