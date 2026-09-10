#!/usr/bin/env python3
"""Zero-dependency static SEO builder for apps.laxmannepal.com.np."""
from __future__ import annotations
import html, json, re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "site.config.json").read_text(encoding="utf-8"))
BASE = CONFIG["site_url"].rstrip("/")
BLOG = ROOT / "content" / "blog"
OUT = ROOT / "blog"


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def frontmatter(text: str):
    meta = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            raw, body = parts[1], parts[2].lstrip("\n")
            for line in raw.splitlines():
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                value = value.strip().strip('"\'')
                if key.strip() == "tags":
                    value = [x.strip() for x in value.split(",") if x.strip()]
                meta[key.strip()] = value
    return meta, body


def markdown(src: str) -> str:
    lines = src.replace("\r\n", "\n").split("\n")
    out, paragraph, in_code = [], [], False
    for line in lines:
        if line.startswith("```"):
            if in_code:
                out.append("<pre><code>" + esc("\n".join(paragraph)) + "</code></pre>")
                paragraph, in_code = [], False
            else:
                if paragraph:
                    out.append("<p>" + inline(" ".join(paragraph)) + "</p>")
                    paragraph = []
                in_code = True
            continue
        if in_code:
            paragraph.append(line)
            continue
        if not line.strip():
            if paragraph:
                out.append("<p>" + inline(" ".join(paragraph)) + "</p>")
                paragraph = []
            continue
        m = re.match(r"^(#{1,3})\s+(.+)$", line)
        if m:
            if paragraph:
                out.append("<p>" + inline(" ".join(paragraph)) + "</p>")
                paragraph = []
            level = len(m.group(1)) + 1
            text = inline(m.group(2))
            ident = re.sub(r"[^a-z0-9]+", "-", re.sub("<[^>]+>", "", text.lower())).strip("-")
            out.append(f'<h{level} id="{esc(ident)}">{text}</h{level}>')
        elif re.match(r"^[-*]\s+", line):
            if paragraph:
                out.append("<p>" + inline(" ".join(paragraph)) + "</p>")
                paragraph = []
            if not out or not out[-1].startswith("<ul>"):
                out.append("<ul>")
            out.append("<li>" + inline(re.sub(r"^[-*]\s+", "", line)) + "</li>")
        else:
            if out and out[-1] == "</li>":
                out.append("</ul>")
            paragraph.append(line)
    if paragraph:
        out.append("<p>" + inline(" ".join(paragraph)) + "</p>")
    if out and out[-1] == "</li>":
        out.append("</ul>")
    return "\n".join(out)


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" rel="noopener">\1</a>', text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


def slug(path: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")


def iso_date(value, fallback):
    value = str(value or fallback)[:10]
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        return fallback


def template(title, description, canonical, body, schema=""):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#0b0d12"><meta name="description" content="{esc(description)}"><meta name="author" content="{esc(CONFIG['author'])}"><link rel="canonical" href="{esc(canonical)}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="article"><meta property="og:url" content="{esc(canonical)}"><meta name="twitter:card" content="summary_large_image"><title>{esc(title)} — {esc(CONFIG['site_name'])}</title><link rel="stylesheet" href="/assets/css/style.css"><link rel="stylesheet" href="/assets/css/blog.css">{schema}</head><body><header class="site-header"><a class="brand" href="/" aria-label="Laxman Nepal home"><span class="brand-mark">LN</span><span>Laxman Nepal</span></a><nav class="nav" aria-label="Primary navigation"><a href="/">Home</a><a href="/tools/">Tools</a><a href="/ai-tools/">AI Tools</a><a href="/blog/">Blog</a></nav></header><main class="article-wrap">{body}</main><footer class="footer section-wrap"><div><strong>Laxman Nepal</strong><span>© {datetime.now().year} All rights reserved.</span></div><a href="/">Back home ↑</a></footer></body></html>'''

articles = []
if BLOG.exists():
    for path in sorted(BLOG.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        meta, source = frontmatter(path.read_text(encoding="utf-8"))
        s = slug(path)
        if not meta.get("title"):
            meta["title"] = path.stem.replace("-", " ").title()
        meta["description"] = meta.get("description", "Practical technology, AI and productivity guidance by Laxman Nepal.")
        meta["date"] = iso_date(meta.get("date"), datetime.now(timezone.utc).date().isoformat())
        meta["updated"] = iso_date(meta.get("updated"), meta["date"])
        meta["author"] = meta.get("author", CONFIG["author"])
        meta["category"] = meta.get("category", "Technology")
        meta["tags"] = meta.get("tags", []) if isinstance(meta.get("tags", []), list) else [str(meta["tags"])]
        meta["slug"] = s
        meta["url"] = f"{BASE}/blog/{s}/"
        meta["source"] = source
        articles.append(meta)

for article in articles:
    out = OUT / article["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    content = markdown(article["source"])
    words = len(re.findall(r"\b[\w’'-]+\b", re.sub(r"<[^>]+>", " ", content)))
    minutes = max(1, round(words / 220))
    tags = "".join(f'<a class="tag" href="/blog/?tag={esc(t)}">{esc(t)}</a>' for t in article["tags"])
    schema = '<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "Article", "headline": article["title"],
        "description": article["description"], "datePublished": article["date"], "dateModified": article["updated"],
        "author": {"@type": "Person", "name": article["author"]}, "publisher": {"@type": "Person", "name": CONFIG["author"]},
        "mainEntityOfPage": {"@type": "WebPage", "@id": article["url"]}
    }, ensure_ascii=False) + '</script>'
    body = f'<article><nav class="breadcrumbs"><a href="/">Home</a> / <a href="/blog/">Blog</a> / {esc(article["title"])}</nav><header class="article-header"><p class="eyebrow">{esc(article["category"])} · {minutes} min read</p><h1>{esc(article["title"])}</h1><p class="article-description">{esc(article["description"])}</p><div class="article-meta">By {esc(article["author"])} · Published {article["date"]} · Updated {article["updated"]}</div><div class="tags">{tags}</div></header><div class="article-content">{content}</div></article>'
    out.write_text(template(article["title"], article["description"], article["url"], body, schema), encoding="utf-8")

# Blog index
cards = "".join(f'<article class="post-card"><p class="eyebrow">{esc(a["category"])} · {a["date"]}</p><h2><a href="/blog/{esc(a["slug"])}/">{esc(a["title"])}</a></h2><p>{esc(a["description"])}</p><a class="text-link" href="/blog/{esc(a["slug"])}/">Read article →</a></article>' for a in sorted(articles, key=lambda x: x["date"], reverse=True))
blog_body = f'<section class="blog-hero"><p class="eyebrow">Laxman Nepal Journal</p><h1>Useful ideas.<br><em>Explained simply.</em></h1><p>Practical guides about technology, AI, apps, productivity and digital work.</p></section><section class="post-grid">{cards or "<p>No articles published yet. Add Markdown files to content/blog.</p>"}</section>'
(OUT / "index.html").parent.mkdir(parents=True, exist_ok=True)
(OUT / "index.html").write_text(template("Blog — Laxman Nepal", "Practical technology, AI, apps and productivity articles by Laxman Nepal.", f"{BASE}/blog/", blog_body), encoding="utf-8")

# RSS
items = []
for a in sorted(articles, key=lambda x: x["date"], reverse=True):
    items.append(f'<item><title>{esc(a["title"])}</title><link>{esc(a["url"])}</link><guid>{esc(a["url"])}</guid><pubDate>{a["date"]}</pubDate><description>{esc(a["description"])}</description></item>')
feed = '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Laxman Nepal</title><link>' + BASE + '</link><description>' + esc(CONFIG["description"]) + '</description>' + ''.join(items) + '</channel></rss>'
(ROOT / "feed.xml").write_text(feed, encoding="utf-8")

# Sitemap: important public pages + generated articles.
urls = {BASE + "/", BASE + "/blog/", BASE + "/tools/", BASE + "/ai-tools/"}
for a in articles:
    urls.add(a["url"])
now = datetime.now(timezone.utc).date().isoformat()
sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{esc(u)}</loc><lastmod>{now}</lastmod></url>' for u in sorted(urls)) + '</urlset>'
(ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
print(f"Built {len(articles)} blog articles, blog index, RSS and sitemap.")
