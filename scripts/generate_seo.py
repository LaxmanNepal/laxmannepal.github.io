#!/usr/bin/env python3
"""Generate static discovery files for the GitHub Pages build."""
from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".blogger-migration.json"
PUBLIC = ROOT / "nextjs-foundation" / "public"
BASE = "https://laxmannepal.com.np"

INDEXABLE_STATIC_PATHS = [
    "/", "/en/", "/ne/", "/hi/", "/languages/",
    "/news/", "/reviews/", "/guides/", "/products/",
    "/compare/", "/tools/", "/ai/", "/youtube/", "/tech-news/",
    "/gold-price-in-nepal-today/",
    "/gold-price-history-nepal/",
    "/silver-price-in-nepal-today/",
]

def load_posts():
    if not MANIFEST.exists():
        return []
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return [p for p in data.get("posts", []) if p.get("path")]

def main():
    PUBLIC.mkdir(parents=True, exist_ok=True)
    posts = load_posts()
    tech_root = ROOT / "tech-news"
    tech_urls = []
    if tech_root.exists():
        for p in sorted(tech_root.glob("*/index.html")):
            tech_urls.append("/" + p.relative_to(ROOT).parent.as_posix() + "/")

    urls = []
    for path in INDEXABLE_STATIC_PATHS + tech_urls + [p["path"] for p in posts]:
        if path.startswith("/old/") or path.startswith("/scripts/") or path.startswith("/search/"):
            continue
        if path not in urls:
            urls.append(path)

    items = [f"  <url><loc>{escape(BASE + path)}</loc></url>" for path in urls]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n' + (
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(items)
        + "\n</urlset>\n"
    )
    (PUBLIC / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    robots = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /old/\n"
        "Disallow: /scripts/\n"
        "\nSitemap: " + BASE + "/sitemap.xml\n"
    )
    (PUBLIC / "robots.txt").write_text(robots, encoding="utf-8")

    feed_items = []
    for post in posts[:50]:
        title = escape(post.get("title", "Untitled post"))
        link = BASE + post["path"]
        published = post.get("published") or post.get("updated")
        pub = f"<pubDate>{escape(published)}</pubDate>" if published else ""
        feed_items.append(
            "<item>"
            f"<title>{title}</title>"
            f"<link>{escape(link)}</link>"
            f'<guid isPermaLink="true">{escape(link)}</guid>'
            f"{pub}"
            "</item>"
        )

    rss = '<?xml version="1.0" encoding="UTF-8"?>\n' + (
        '<rss version="2.0"><channel>'
        "<title>Laxman Nepal</title>"
        "<link>" + BASE + "</link>"
        "<description>Technology, tools, AI and creator intelligence.</description>"
        + "".join(feed_items)
        + "</channel></rss>\n"
    )
    (PUBLIC / "feed.xml").write_text(rss, encoding="utf-8")
    print(f"Generated SEO files for {len(posts)} migrated posts and {len(urls)} sitemap URLs.")

if __name__ == "__main__":
    main()
