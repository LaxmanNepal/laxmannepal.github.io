#!/usr/bin/env python3
"""Manage the native /blogs/<slug>/ article architecture.

This script is intentionally filesystem-first so it works locally and in GitHub
Actions. Every native blog directory is expected to contain:
  index.html
  article.json
  thumbnail.jpg

--fix creates missing article.json/thumbnail.jpg and synchronizes SEO metadata.
--check validates the complete blog contract without changing files.
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
BLOGS = ROOT / "blogs"
BASE = "https://laxmannepal.com.np"
AUTHOR = "Laxman Nepal"
REQUIRED = ("index.html", "article.json", "thumbnail.jpg")

FALLBACK_THUMBNAIL = None

META_KEYS = (
    ("name", "description"),
    ("name", "author"),
    ("name", "robots"),
    ("property", "og:type"),
    ("property", "og:title"),
    ("property", "og:description"),
    ("property", "og:url"),
    ("property", "og:image"),
    ("property", "og:image:alt"),
    ("name", "twitter:card"),
    ("name", "twitter:title"),
    ("name", "twitter:description"),
    ("name", "twitter:image"),
)


def clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def first(patterns: Iterable[str], text: str) -> str:
    for pattern in patterns:
        m = re.search(pattern, text, re.I | re.S)
        if m:
            return clean(m.group(1))
    return ""


def extract_title(text: str) -> str:
    return first((r"<title[^>]*>(.*?)</title>", r"<h1[^>]*>(.*?)</h1>"), text)


def extract_meta(text: str, attr: str, key: str) -> str:
    patterns = (
        rf'<meta[^>]+{attr}=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']*)',
        rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]+{attr}=["\']{re.escape(key)}["\']',
    )
    return first(patterns, text)


def extract_date(text: str, field: str) -> str:
    return first(
        (
            rf'"{re.escape(field)}"\s*:\s*"([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}})"',
            rf'{re.escape(field)}=["\']([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}})',
            rf'<time[^>]+datetime=["\']([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}})',
        ),
        text,
    )[:10]


def valid_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return True
    except (TypeError, ValueError):
        return False


def slug_from_dir(path: Path) -> str:
    return path.name


def article_url(slug: str) -> str:
    return f"{BASE}/blogs/{slug}/"


def thumbnail_url(slug: str) -> str:
    return f"{BASE}/blogs/{slug}/thumbnail.jpg"


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def make_article_json(folder: Path, existing: dict | None = None) -> dict:
    existing = existing or {}
    index = folder / "index.html"
    text = index.read_text(encoding="utf-8", errors="ignore")
    slug = slug_from_dir(folder)

    title = existing.get("title") or extract_title(text)
    title = re.sub(r"\s*\|\s*Laxman Nepal\s*$", "", title, flags=re.I).strip()
    title = re.sub(r"\s*—\s*Laxman Nepal\s*$", "", title, flags=re.I).strip()
    description = existing.get("description") or extract_meta(text, "name", "description")
    author = existing.get("author") or extract_meta(text, "name", "author") or AUTHOR

    published = str(existing.get("published") or extract_date(text, "datePublished") or "").strip()[:10]
    updated = str(existing.get("updated") or extract_date(text, "dateModified") or "").strip()[:10]

    if not valid_date(published):
        published = date.today().isoformat()
    if not valid_date(updated):
        updated = published

    kind = str(existing.get("type") or "TechArticle").strip() or "TechArticle"

    return {
        "title": title or slug.replace("-", " ").title(),
        "slug": slug,
        "description": description or "Practical technology, AI, apps and digital guidance by Laxman Nepal.",
        "author": author,
        "published": published,
        "updated": updated,
        "thumbnail": f"/blogs/{slug}/thumbnail.jpg",
        "canonical": article_url(slug),
        "type": kind,
    }


def remove_meta(text: str, attr: str, key: str) -> str:
    pattern = rf'<meta\s+[^>]*{attr}=["\']{re.escape(key)}["\'][^>]*>\s*'
    return re.sub(pattern, "", text, flags=re.I)
    

def remove_canonical(text: str) -> str:
    return re.sub(r'<link\s+[^>]*rel=["\']canonical["\'][^>]*>\s*', "", text, flags=re.I)


def inject_seo(text: str, article: dict) -> str:
    title = html.escape(article["title"], quote=True)
    desc = html.escape(article["description"], quote=True)
    canonical = html.escape(article["canonical"], quote=True)
    image = html.escape(f'{BASE}{article["thumbnail"]}', quote=True)

    for attr, key in META_KEYS:
        text = remove_meta(text, attr, key)
    text = remove_canonical(text)

    block = f'''<meta name="description" content="{desc}">
<meta name="author" content="{html.escape(article["author"], quote=True)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{image}">
<meta property="og:image:alt" content="{title}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{image}">
'''
    if re.search(r"</head\s*>", text, re.I):
        text = re.sub(r"</head\s*>", block + "</head>", text, count=1, flags=re.I)
    else:
        text = "<head>" + block + "</head>" + text
    return text


def ensure_schema(text: str, article: dict) -> str:
    if re.search(r'application/ld\+json', text, re.I):
        return text

    schema = {
        "@context": "https://schema.org",
        "@type": article["type"],
        "headline": article["title"],
        "description": article["description"],
        "image": [article["canonical"].rstrip("/") + "/thumbnail.jpg"],
        "author": {"@type": "Person", "name": article["author"], "url": BASE + "/"},
        "publisher": {"@type": "Person", "name": article["author"], "url": BASE + "/"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": article["canonical"]},
        "datePublished": article["published"],
        "dateModified": article["updated"],
    }
    tag = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False, separators=(",", ":")) + "</script>"
    return re.sub(r"</head\s*>", tag + "</head>", text, count=1, flags=re.I)


def fallback_thumbnail(folder: Path, title: str) -> bool:
    path = folder / "thumbnail.jpg"
    if path.exists():
        return False

    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        print(f"warning: Pillow unavailable; cannot create {path}", file=sys.stderr)
        return False

    image = Image.new("RGB", (1200, 630), (17, 24, 39))
    draw = ImageDraw.Draw(image)

    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]
    font = None
    for fp in font_paths:
        if Path(fp).exists():
            font = ImageFont.truetype(fp, 58)
            break
    if font is None:
        font = ImageFont.load_default()

    words = title.split()
    lines, line = [], ""
    for word in words:
        candidate = (line + " " + word).strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= 1030:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    lines = lines[:5] or ["Laxman Nepal"]

    y = 170
    draw.text((60, 70), "LAXMAN NEPAL · BLOG", fill=(156, 163, 175), font=font)
    for line in lines:
        draw.text((60, y), line, fill=(255, 255, 255), font=font)
        y += 82

    folder.mkdir(parents=True, exist_ok=True)
    image.save(path, "JPEG", quality=88, optimize=True, progressive=True)
    print(f"created fallback thumbnail: {path}")
    return True


def process_folder(folder: Path, fix: bool) -> tuple[bool, list[str]]:
    errors: list[str] = []
    index = folder / "index.html"
    if not index.is_file():
        return False, []

    raw = index.read_text(encoding="utf-8", errors="ignore")
    existing_path = folder / "article.json"
    existing = read_json(existing_path) if existing_path.exists() else {}
    article = make_article_json(folder, existing)

    if not article["title"]:
        errors.append("missing title")
    if not article["description"]:
        errors.append("missing description")

    if fix:
        folder.mkdir(parents=True, exist_ok=True)
        existing_path.write_text(json.dumps(article, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        updated_html = inject_seo(raw, article)
        updated_html = ensure_schema(updated_html, article)
        if updated_html != raw:
            index.write_text(updated_html, encoding="utf-8")
        fallback_thumbnail(folder, article["title"])

    for name in REQUIRED:
        if not (folder / name).is_file():
            errors.append(f"missing {name}")

    if existing_path.is_file():
        actual = read_json(existing_path)
        for key in ("title", "slug", "description", "author", "published", "updated", "thumbnail", "canonical", "type"):
            if not actual.get(key):
                errors.append(f"article.json missing {key}")
        if actual.get("slug") != folder.name:
            errors.append("article.json slug does not match folder")
        if actual.get("canonical") != article_url(folder.name):
            errors.append("article.json canonical is wrong")
        if actual.get("thumbnail") != f"/blogs/{folder.name}/thumbnail.jpg":
            errors.append("article.json thumbnail is wrong")
        if actual.get("type") != "TechArticle":
            errors.append("article.json type should be TechArticle")

    final_html = index.read_text(encoding="utf-8", errors="ignore")
    required_checks = (
        article["canonical"] in final_html,
        f'{BASE}{article["thumbnail"]}' in final_html,
        'property="og:title"' in final_html or "property='og:title'" in final_html,
        'property="og:image"' in final_html or "property='og:image'" in final_html,
        "application/ld+json" in final_html,
    )
    if not all(required_checks):
        errors.append("index.html is missing canonical/OG/schema metadata")

    return True, errors


def blog_folders() -> list[Path]:
    if not BLOGS.exists():
        return []
    return sorted(p for p in BLOGS.iterdir() if p.is_dir() and not p.name.startswith("."))



RELATED_START = "<!-- related-blogs:start -->"
RELATED_END = "<!-- related-blogs:end -->"

STOP_WORDS = {
    "about", "after", "also", "and", "are", "best", "can", "cmd", "for", "from",
    "guide", "how", "into", "learn", "more", "using", "with", "your", "the", "this",
    "that", "using", "what", "when", "where", "why", "you", "all", "new", "blog",
    "laxman", "nepal", "tutorial", "tips", "step", "complete", "easy", "free",
}

def article_tokens(article: dict) -> set[str]:
    text = " ".join(str(article.get(key, "")) for key in ("title", "description", "slug"))
    tokens = set(re.findall(r"[a-z0-9]{3,}", text.lower()))
    return tokens - STOP_WORDS


def related_articles(current: dict, all_articles: list[dict], limit: int = 3) -> list[dict]:
    current_tokens = article_tokens(current)
    ranked = []
    for candidate in all_articles:
        if candidate.get("slug") == current.get("slug"):
            continue
        tokens = article_tokens(candidate)
        overlap = len(current_tokens & tokens)
        union = len(current_tokens | tokens) or 1
        score = overlap / union
        # Keep useful suggestions even when titles cover different topics.
        ranked.append((score, str(candidate.get("published", "")), candidate))
    ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
    chosen = [item[2] for item in ranked[:limit] if item[0] > 0]
    if len(chosen) < limit:
        used = {item.get("slug") for item in chosen}
        for _, _, candidate in sorted(ranked, key=lambda item: item[1], reverse=True):
            if candidate.get("slug") not in used:
                chosen.append(candidate)
                used.add(candidate.get("slug"))
            if len(chosen) >= limit:
                break
    return chosen


def render_related_blogs(current: dict, articles: list[dict]) -> str:
    suggestions = related_articles(current, articles)
    if not suggestions:
        return ""
    cards = []
    for article in suggestions:
        title = html.escape(str(article.get("title") or article.get("slug") or "Read article"))
        description = html.escape(str(article.get("description") or "Read this practical guide."))
        url = html.escape(str(article.get("canonical") or article_url(str(article.get("slug", "")))))
        image = html.escape(str(article.get("thumbnail") or f"/blogs/{article.get('slug', '')}/thumbnail.jpg"))
        if image.startswith("/"):
            image = html.escape(BASE + image)
        cards.append(f"""<a class="related-blog-card" href="{url}">
<img src="{image}" alt="" loading="lazy" decoding="async">
<span class="related-blog-card-copy"><strong>{title}</strong><span>{description}</span><em>Read article →</em></span>
</a>""")
    return f"""
{RELATED_START}
<section class="related-blogs" aria-labelledby="related-blogs-title">
<style>
.related-blogs{{margin:54px 0 12px;padding-top:28px;border-top:1px solid #e5e7eb;color:#101828}}
.related-blogs h2{{font-size:clamp(23px,3vw,30px);line-height:1.2;margin:0 0 8px}}
.related-blogs .related-blogs-intro{{margin:0 0 20px;color:#667085;font-size:15px;line-height:1.6}}
.related-blogs-grid{{display:flex;gap:16px;overflow-x:auto;overflow-y:hidden;padding:4px 3px 16px;scroll-snap-type:x mandatory;scroll-padding-inline:3px;-webkit-overflow-scrolling:touch;overscroll-behavior-inline:contain;scrollbar-width:thin;scrollbar-color:#98a2b3 #f2f4f7}}.related-blogs-grid::-webkit-scrollbar{{height:8px}}.related-blogs-grid::-webkit-scrollbar-track{{background:#f2f4f7;border-radius:99px}}.related-blogs-grid::-webkit-scrollbar-thumb{{background:#98a2b3;border-radius:99px}}
.related-blog-card{{display:flex;flex:0 0 280px;flex-direction:column;min-width:0;overflow:hidden;border:1px solid #e5e7eb;border-radius:16px;background:#fff;color:inherit;text-decoration:none;scroll-snap-align:start;transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease}}
.related-blog-card:hover{{transform:translateY(-3px);border-color:#b2ccff;box-shadow:0 10px 24px rgba(16,24,40,.08)}}
.related-blog-card:focus-visible{{outline:3px solid #84adff;outline-offset:3px}}
.related-blog-card img{{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;background:#f2f4f7}}
.related-blog-card-copy{{display:flex;flex:1;flex-direction:column;align-items:flex-start;gap:9px;padding:15px}}
.related-blog-card-copy strong{{font-size:16px;line-height:1.4;color:#101828}}
.related-blog-card-copy span{{font-size:13px;line-height:1.55;color:#667085;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
.related-blog-card-copy em{{margin-top:auto;padding-top:3px;font-size:13px;font-style:normal;font-weight:650;color:#175cd3}}
@media(max-width:700px){{.related-blogs-grid{{gap:12px}}.related-blog-card{{flex-basis:250px}}.related-blog-card-copy{{padding:12px}}.related-blog-card-copy strong{{font-size:14px}}}}
@media(max-width:420px){{.related-blog-card{{flex-basis:min(82vw,280px)}}.related-blog-card-copy{{padding:12px}}}}
@media(prefers-reduced-motion:reduce){{.related-blog-card{{transition:none}}.related-blog-card:hover{{transform:none}}}}
</style>
<h2 id="related-blogs-title">You might also like</h2>
<p class="related-blogs-intro">More practical guides selected from the Laxman Nepal blog.</p>
<div class="related-blogs-grid">
{''.join(cards)}
</div>
<p style="margin:18px 0 0"><a href="/blogs/">Explore all blogs →</a></p>
</section>
{RELATED_END}
"""


def inject_related_blogs(folder: Path, articles: list[dict], fix: bool) -> list[str]:
    index = folder / "index.html"
    if not index.is_file():
        return []
    text = index.read_text(encoding="utf-8", errors="ignore")
    current = read_json(folder / "article.json")
    block = render_related_blogs(current, articles)
    pattern = re.compile(re.escape(RELATED_START) + r".*?" + re.escape(RELATED_END), re.I | re.S)
    if pattern.search(text):
        updated = pattern.sub(lambda _: block.strip(), text)
    else:
        updated = text
        insertion = re.search(r"</main\s*>", updated, re.I)
        if insertion:
            updated = updated[:insertion.start()] + block + updated[insertion.start():]
        else:
            insertion = re.search(r"</body\s*>", updated, re.I)
            if insertion:
                updated = updated[:insertion.start()] + block + updated[insertion.start():]
            else:
                updated += block
    if fix and updated != text:
        index.write_text(updated, encoding="utf-8")
    if len(articles) > 1 and (RELATED_START not in updated or "related-blog-card" not in updated):
        return ["missing related blog suggestions"]
    return []

def write_llms() -> None:
    links = []
    for folder in blog_folders():
        article_path = folder / "article.json"
        if not article_path.exists():
            continue
        data = read_json(article_path)
        if data.get("canonical") and data.get("title"):
            links.append((data["title"], data["canonical"]))
    lines = [
        "# Laxman Nepal",
        "",
        "> Practical technology, AI, apps, tutorials, tools and digital guides.",
        "",
        "## Blog",
        f"- {BASE}/blogs/",
        "- Each article uses /blogs/<slug>/ with index.html, article.json and thumbnail.jpg.",
        "- Prefer the canonical URL listed in each article's article.json.",
        "",
        "## Articles",
    ]
    lines.extend(f"- {url} — {title}" for title, url in links)
    lines.extend(
        [
            "",
            "## Discovery",
            f"- {BASE}/sitemap.xml",
            f"- {BASE}/search-index.json",
        ]
    )
    (ROOT / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fix", action="store_true", help="Create/synchronize metadata and fallback thumbnails.")
    parser.add_argument("--check", action="store_true", help="Validate blogs without modifying files.")
    args = parser.parse_args()

    fix = args.fix and not args.check
    if not args.fix and not args.check:
        parser.error("use --fix or --check")

    folders = blog_folders()
    failures = []
    processed = 0
    for folder in folders:
        ok, errors = process_folder(folder, fix)
        if ok:
            processed += 1
        if errors:
            failures.append((folder, errors))

    articles = []
    for folder in folders:
        data = read_json(folder / "article.json")
        if data.get("title") and data.get("slug") and data.get("canonical"):
            articles.append(data)

    for folder in folders:
        if not (folder / "index.html").is_file():
            continue
        related_errors = inject_related_blogs(folder, articles, fix)
        if related_errors:
            failures.append((folder, related_errors))

    if fix:
        write_llms()

    print(f"Checked {processed} native blog folders and related-article sections.")
    if failures:
        print("\nBlog validation failures:")
        for folder, errors in failures:
            print(f"- {folder.relative_to(ROOT)}: " + "; ".join(dict.fromkeys(errors)))
        return 1

    print("Blog architecture is healthy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
