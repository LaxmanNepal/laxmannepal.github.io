#!/usr/bin/env python3
"""Build a deterministic, content-aware search index from local HTML pages."""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import html, json, re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "search-index.json"
SKIP_PREFIXES = (".git/",)
IGNORED_TAGS = {"script", "style", "noscript", "svg", "nav", "header", "footer", "form", "button", "input", "textarea", "select", "template"}
WORD_RE = re.compile(r"[\w][\w+.#-]{1,}", re.UNICODE)

def clean(value):
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()

class PageParser(HTMLParser):
    """Extract visible text and SEO metadata without external dependencies."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta, self.title_parts, self.h1_parts, self.heading_parts, self.body_parts = {}, [], [], [], []
        self.image, self.canonical, self.robots = "", "", ""
        self.skip_depth = self.title_depth = self.h1_depth = self.heading_depth = 0
        self.in_body = False
        self.has_refresh = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            key = (attrs.get("name") or attrs.get("property") or "").lower()
            if key: self.meta.setdefault(key, attrs.get("content", ""))
            if key == "robots": self.robots = attrs.get("content", "").lower()
            if (attrs.get("http-equiv") or "").lower() == "refresh": self.has_refresh = True
        elif tag == "link" and "canonical" in (attrs.get("rel") or "").lower().split():
            self.canonical = attrs.get("href", "")
        elif tag == "img" and not self.image:
            self.image = attrs.get("src", "")
        if tag in IGNORED_TAGS or attrs.get("aria-hidden") == "true": self.skip_depth += 1
        if self.skip_depth: return
        if tag == "title": self.title_depth += 1
        if tag == "h1": self.h1_depth += 1
        if tag in {"h1", "h2", "h3", "h4"}: self.heading_depth += 1
        if tag == "body": self.in_body = True

    def handle_endtag(self, tag):
        if tag == "title": self.title_depth = max(0, self.title_depth - 1)
        if tag == "h1": self.h1_depth = max(0, self.h1_depth - 1)
        if tag in {"h1", "h2", "h3", "h4"}: self.heading_depth = max(0, self.heading_depth - 1)
        if tag == "body": self.in_body = False
        if tag in IGNORED_TAGS and self.skip_depth: self.skip_depth -= 1

    def handle_data(self, data):
        if self.skip_depth: return
        value = clean(data)
        if not value: return
        if self.title_depth: self.title_parts.append(value)
        if self.h1_depth: self.h1_parts.append(value)
        if self.heading_depth: self.heading_parts.append(value)
        if self.in_body: self.body_parts.append(value)

def canonical_path(value, fallback):
    if not value: return fallback
    parsed = urlparse(value)
    if parsed.scheme and (parsed.scheme != "https" or parsed.netloc.lower() not in {"laxmannepal.com.np", "www.laxmannepal.com.np"}):
        return fallback
    path = parsed.path if parsed.scheme or parsed.netloc else value.split("#", 1)[0].split("?", 1)[0]
    if not path.startswith("/"): return fallback
    if path == "/index.html": return "/"
    if path.endswith("/index.html"): path = path[:-10]
    if path != "/" and not path.endswith("/") and not Path(path).suffix: path += "/"
    return path

def category(path, title):
    p, s = path.lower(), (path + " " + title).lower()
    if "/ai-tools" in p or any(x in s for x in (" ai ", "ai tool", "artificial intelligence", "prompt")): return "AI"
    if "/youtube" in p or any(x in s for x in ("youtube", "video", "thumbnail")): return "YouTube"
    if "/tools" in p or any(x in s for x in ("tool", "converter", "generator", "downloader", "scanner", "counter")): return "Tools"
    if "/mobile" in p or any(x in s for x in ("mobile", "phone", "smartphone", "android", "iphone")): return "Mobile"
    if "/news" in p or " news" in s: return "News"
    if p.startswith("/blogs/") or "/blog" in p or any(x in s for x in ("blog", "seo", "tutorial", "guide", "how to")): return "Articles"
    if "/apps" in p or " app" in s: return "Apps"
    if any(x in s for x in ("nepal", "nepali", "patro", "rashifal", "festival")): return "Nepali"
    return "Resources"

def parse_page(content, rel_path):
    rel = rel_path.replace("\\", "/").lstrip("./")
    if rel.startswith(SKIP_PREFIXES) or not rel.lower().endswith(".html"): return None
    parser = PageParser()
    try:
        parser.feed(content); parser.close()
    except Exception:
        return None
    title_text = clean(" ".join(parser.title_parts)) or clean(" ".join(parser.h1_parts)) or Path(rel).stem.replace("-", " ").replace("_", " ").strip().title() or rel
    # Every HTML file gets its own result and direct file URL. Do not let canonical,
    # noindex, refresh, or missing-title metadata hide repository pages.
    page_url = "/" + rel
    description = clean(parser.meta.get("description") or parser.meta.get("og:description") or " ".join(parser.h1_parts) or title_text)
    headings = clean(" ".join(parser.heading_parts))
    body = clean(" ".join(parser.body_parts))[:1800]
    date = clean(parser.meta.get("article:published_time") or parser.meta.get("date") or parser.meta.get("datepublished") or parser.meta.get("article:modified_time"))[:10]
    image = clean(parser.meta.get("og:image") or parser.meta.get("twitter:image") or parser.image)
    if image.startswith("//"): image = "https:" + image
    if image and not (image.startswith("/") or image.startswith("https://")): image = ""
    if re.search(r"\$\{|\$\(|example\.com|undefined|null", image, re.I) or image.startswith("data:"): image = ""
    source = " ".join((title_text, description, headings, body, rel.replace("/", " ").replace("-", " ").replace("_", " ")))
    keywords = " ".join(dict.fromkeys(WORD_RE.findall(source.lower())))[:900]
    cat = category(page_url, title_text)
    return {"title": title_text[:180], "category": cat, "type": "article" if cat == "Articles" else "tool" if cat == "Tools" else "resource",
            "url": page_url, "description": description[:260], "headings": headings[:700], "content": body,
            "keywords": keywords, "image": image, "date": date}

def build_index(root):
    items = []
    for file in root.rglob("*"):
        if not file.is_file() or file.suffix.lower() != ".html": continue
        rel = file.relative_to(root).as_posix()
        if rel.startswith(SKIP_PREFIXES): continue
        try: item = parse_page(file.read_text(encoding="utf-8", errors="ignore"), rel)
        except OSError: continue
        if item: items.append(item)
    # Keep one search result per HTML file, even when canonical metadata overlaps.
    return sorted(items, key=lambda item: (item["title"].casefold(), item["url"]))

def main():
    items = build_index(ROOT)
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(items)} searchable HTML pages.")

if __name__ == "__main__":
    main()
