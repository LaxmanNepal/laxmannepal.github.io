#!/usr/bin/env python3
"""Generate the site's searchable resource index from HTML files."""
from pathlib import Path
import json, re, html
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "search-index.json"
SKIP = {"search/index.html", "search.html", "404.html", "2025/07/image-to-url.html", "2025/07/qr-code-scanner.html", "2025/07/usefull-links.html", "2025/08/20-free-ai-tools-to-skyrocket-your.html", "2025/11/youtube-trending-keywords.html", "2025/11/youtube-tag-extractor.html", "2025/11/youtube-thumbnail-downloader.html", "2025/11/youtube-video-seo-analyzer.html", "2025/11/ai-powered-youtube-seo-deep-analyzer.html", "2025/11/youtube-channel-info-extractor.html", "2025/11/youtube-channel-id-finder-analytics.html", "2025/11/youtube-video-title-description-tag.html", "2025/11/youtube-description-extractor.html", "2025/11/youtube-hashtag-extractor.html", "2025/11/youtube-title-generator.html", "2025/11/youtube-nepal-trend-explorer.html", "2025/11/youtube-video-analytics.html", "2025/12/strong-password-generator.html", "2025/12/qr-code-generator.html", "2026/02/youtube-tag-generator.html", "2026/02/laxman-nepal-youtube-thumbnail.html", "2026/01/facebook-post-generator.html"}
SKIP_PREFIXES = ("old/", "youtube-tools/archive/")

def clean(value):
    return html.unescape(re.sub(r"\s+", " ", value or "")).strip()

def meta(content, name):
    m = re.search(r'<meta[^>]+name=["\']' + re.escape(name) + r'["\'][^>]+content=["\']([^"\']*)["\']', content, re.I)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']' + re.escape(name) + r'["\']', content, re.I)
    return clean(m.group(1)) if m else ""

def image_meta(content):
    for pattern in (
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']',
        r'<img[^>]+src=["\']([^"\']+)["\']',
    ):
        m = re.search(pattern, content, re.I)
        if m:
            return clean(m.group(1))
    return ""

def title(content):
    m = re.search(r"<title[^>]*>(.*?)</title>", content, re.I | re.S)
    return clean(re.sub(r"<[^>]+>", "", m.group(1))) if m else ""

def canonical_url(content):
    patterns = (
        r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)',
        r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']',
    )
    for pattern in patterns:
        m = re.search(pattern, content, re.I)
        if m:
            value = clean(m.group(1))
            parsed = urlparse(value)
            if parsed.scheme == "https" and parsed.netloc == "laxmannepal.com.np":
                page_path = parsed.path or "/"
                if page_path == "/index.html":
                    return "/"
                if page_path.endswith("/index.html"):
                    return page_path[:-10]
                return page_path
    return ""

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
    if rel in SKIP or rel.startswith(SKIP_PREFIXES) or rel.startswith(".git/"):
        continue
    try:
        content = file.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    t = title(content)
    if not t or re.search(r"\b(redirecting|article moved)\b", t, re.I):
        continue
    robots = meta(content, "robots").lower()
    if "noindex" in robots or re.search(r'<meta[^>]+http-equiv=["\']refresh["\']', content, re.I):
        continue
    desc = meta(content, "description") or t
    cat = category(rel, t)
    image = image_meta(content)
    if rel.startswith("blogs/") and (file.parent / "thumbnail.jpg").is_file():
        image = "/" + (file.parent / "thumbnail.jpg").relative_to(ROOT).as_posix()
    if image and (re.search(r"\$\{|\$\(|example\.com|undefined|null", image, re.I) or image.startswith("data:")):
        image = ""
    canonical = canonical_url(content)
    page_url = canonical or url_for(rel)
    source = " ".join((t, desc, rel.replace("/", " ").replace("-", " ").replace("_", " ")))
    keywords = " ".join(dict.fromkeys(re.findall(r"[\w][\w+.-]{1,}", source.lower(), re.UNICODE)))
    items.append({"title": t, "category": cat, "type": "article" if cat == "Article" else "tool" if cat == "Tools" else "resource", "url": page_url, "description": desc[:220], "keywords": keywords[:500], "image": image})

# Collapse files that resolve to the same canonical URL.
unique = {}
for item in items:
    key = item["url"].split("#", 1)[0].rstrip("/") or "/"
    current = unique.get(key)
    if current is None or len(item["description"]) > len(current["description"]):
        unique[key] = item
items = sorted(unique.values(), key=lambda x: (x["title"].lower(), x["url"]))
OUT.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Generated {len(items)} searchable resources.")
