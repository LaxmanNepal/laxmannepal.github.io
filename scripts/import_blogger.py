#!/usr/bin/env python3
"""Safely copy public Blogger posts into the repository root using Blogger URL paths.

The importer preserves each Blogger post's original URL path and full HTML.
It never deletes or changes Blogger content and never stores the raw Atom feed.
"""
from __future__ import annotations
import argparse, html, json, re, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FEED = "https://www.laxmannepal.com.np/atom.xml?redirect=false&start-index=1&max-results=500"
NS = {"a":"http://www.w3.org/2005/Atom", "os":"http://a9.com/-/spec/opensearchrss/1.0/"}
MANIFEST_NAME = ".blogger-migration.json"

def fetch(url):
    req = Request(url, headers={"User-Agent":"LaxmanNepal-BloggerImporter/1.0"})
    with urlopen(req, timeout=60) as r:
        return r.read()

def node_text(node, path, default=""):
    x = node.find(path, NS)
    return x.text if x is not None and x.text else default

def post_url(entry):
    for link in entry.findall("a:link", NS):
        if link.attrib.get("rel") == "alternate" and link.attrib.get("href"):
            return link.attrib["href"]
    return ""

def output_path(url):
    path = re.sub(r"/+", "/", urlparse(url).path or "/").lstrip("/")
    if not path:
        path = "index.html"
    if not path.lower().endswith(".html"):
        path = path.rstrip("/") + "/index.html"
    return Path(path)

def inject_seo(content, title, description, canonical):
    tags = (f'<link rel="canonical" href="{html.escape(canonical, quote=True)}">'
            f'<meta property="og:title" content="{html.escape(title, quote=True)}">'
            f'<meta property="og:description" content="{html.escape(description, quote=True)}">'
            f'<meta property="og:url" content="{html.escape(canonical, quote=True)}">')
    if re.search(r"</head\s*>", content, re.I):
        return re.sub(r"</head\s*>", tags + "</head>", content, count=1, flags=re.I)
    return tags + content

def fetch_all(feed):
    """Fetch every post from a Blogger Atom feed, handling pagination safely."""
    entries, seen, start = [], set(), 1
    parsed = urlparse(feed)
    base_query = parse_qs(parsed.query, keep_blank_values=True)
    # Blogger accepts large pages, but some feeds cap results; 150 keeps pagination safe.
    page_size = 150
    total = None
    while True:
        query = {k: v[-1] if v else "" for k, v in base_query.items()}
        query["start-index"] = str(start)
        query["max-results"] = str(page_size)
        url = urlunparse(parsed._replace(query=urlencode(query)))
        root = ET.fromstring(fetch(url))
        feed_total = int(node_text(root, "os:totalResults", "0") or 0)
        if feed_total:
            total = feed_total
        batch = root.findall("a:entry", NS)
        if not batch:
            break
        new = 0
        for entry in batch:
            eid = node_text(entry, "a:id")
            if eid and eid not in seen:
                seen.add(eid)
                entries.append(entry)
                new += 1
        start += len(batch)
        if total and len(entries) >= total:
            break
        if new == 0 or len(batch) < page_size:
            break
    return entries

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feed", default=DEFAULT_FEED)
    ap.add_argument("--output", default=str(ROOT))
    ap.add_argument("--base-url", default="https://apps.laxmannepal.com.np")
    ap.add_argument("--inject-seo", action="store_true")
    ap.add_argument("--clean", action="store_true")
    args = ap.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / MANIFEST_NAME
    if args.clean and manifest_path.exists():
        try:
            previous = json.loads(manifest_path.read_text(encoding="utf-8"))
            for item in previous.get("posts", []):
                rel = item.get("path", "").lstrip("/")
                if not rel: continue
                target = out / rel
                if target.is_file(): target.unlink()
        except (OSError, ValueError, TypeError) as exc:
            raise RuntimeError(f"Unable to safely clean previous Blogger imports: {exc}") from exc
    entries = fetch_all(args.feed)
    manifest, used = [], set()
    for entry in entries:
        title = html.unescape(node_text(entry, "a:title"))
        published, updated = node_text(entry, "a:published"), node_text(entry, "a:updated")
        content_node = entry.find("a:content", NS)
        content = content_node.text if content_node is not None and content_node.text else ""
        original = post_url(entry)
        if not original or not content: continue
        rel = output_path(original)
        key = str(rel)
        if key in used: raise RuntimeError(f"Duplicate output path: {key}")
        used.add(key)
        description = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", content)).strip())[:155]
        target = args.base_url.rstrip("/") + "/" + key.replace("\\", "/")
        if args.inject_seo: content = inject_seo(content, title, description, target)
        dest = out / rel; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_text(content, encoding="utf-8")
        manifest.append({"title":title,"published":published,"updated":updated,"original_url":original,"imported_url":target,"path":"/"+key.replace("\\","/"),"type":"blog","tags":["blog","technology"]})
    manifest.sort(key=lambda x:x["published"], reverse=True)
    (manifest_path).write_text(json.dumps({"source":args.feed,"total_feed_entries":len(entries),"imported_posts":len(manifest),"generated_at":datetime.now(timezone.utc).isoformat(),"posts":manifest}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Imported {len(manifest)} Blogger posts into repository URL paths under {out}")

if __name__ == "__main__":
    try: main()
    except Exception as exc: print(f"ERROR: {exc}", file=sys.stderr); raise
