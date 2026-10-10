#!/usr/bin/env python3
"""Generate the site's searchable resource index from HTML files."""
from pathlib import Path
import json, re, html

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "search-index.json"
SKIP = {"search/index.html", "search.html", "404.html"}

def clean(value):
    value = html.unescape(re.sub(r"\s+", " ", value or "")).strip()
    return value

def meta(content, name):
    m = re.search(r'<meta[^>]+name=["\']' + re.escape(name) + r'["\'][^>]+content=["\']([^"\']*)["\']', content, re.I)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']' + re.escape(name) + r'["\']([^"\']*)["\']', content, re.I)
    return clean(m.group(1)) if m else ""

def image_meta(content):
    for pattern in (
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']',
        r'<img[^>]+src=["\']([^"\']+)["\']',
    ):
        m = re.search(pattern, content, re.I)
        if m: return clean(m.group(1))
    return ""

def title(content):
    m = re.search(r"<title[^>]*>(.*?)</title>", content, re.I | re.S)
    return clean(re.sub(r"<[^>]+>", "", m.group(1))) if m else ""

def category(path, title_text):
    p = path.lower()
    s = (p + " " + title_text.lower())
    if "/ai-tools" in p or any(x in s for x in (" ai ", "ai tool", "artificial intelligence", "prompt")): return "AI"
    if "/tools" in p or any(x in s for x in ("tool", "converter", "generator", "downloader", "scanner", "counter")): return "Tools"
    if "/mobile" in p or any(x in s for x in ("mobile", "phone", "smartphone", "android", "iphone")): return "Mobile"
    if "/news" in p or "news" in s: return "News"
    if p.startswith("blogs/") or "/blog" in p or any(x in s for x in ("blog", "seo", "tutorial", "guide", "how to")): return "Article"
    if "/apps" in p or " app" in s: return "Apps"
    if any(x in s for x in ("youtube", "video", "thumbnail")): return "YouTube"
    if any(x in s for x in ("nepal", "nepali", "patro", "rashifal", "festival")): return "Nepali"
    return "Resource"

def url_for(path):
    if path == "index.html": return "/"
    if path.endswith("/index.html"): return "/" + path[:-10]
    return "/" + path

items = []
for file in ROOT.rglob("*.html"):
    rel = file.relative_to(ROOT).as_posix()
    if rel in SKIP or rel.startswith(".git/"): continue
    try:
        content = file.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    t = title(content)
    if not t: continue
    robots = meta(content, "robots").lower()
    if "noindex" in robots: continue
    desc = meta(content, "description") or t
    cat = category(rel, t)
    image = image_meta(content)
    if rel.startswith("blogs/") and (file.parent / "thumbnail.jpg").is_file():
        image = "/" + (file.parent / "thumbnail.jpg").relative_to(ROOT).as_posix()
    # Include title, description, path and useful HTML keywords so legacy
    # Blogger-style .html pages are discoverable as well as newer /slug/ pages.
    source = " ".join((t, desc, rel.replace("/", " ").replace("-", " ").replace("_", " ")))
    keywords = " ".join(dict.fromkeys(re.findall(r"[\w][\w+.-]{1,}", source.lower(), re.UNICODE)))
    items.append({"title": t, "category": cat, "type": "article" if cat == "Article" else "tool" if cat == "Tools" else "resource", "url": url_for(rel), "description": desc[:220], "keywords": keywords[:500], "image": image})

# Prefer canonical-looking URLs and stable alphabetical ordering.
items.sort(key=lambda x: (x["title"].lower(), x["url"]))
OUT.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Generated {len(items)} searchable resources.")
