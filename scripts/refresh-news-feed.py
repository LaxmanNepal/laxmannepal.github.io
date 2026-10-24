#!/usr/bin/env python3
"""Fetch RSS headlines, retain the last seven days, and write a static JSON feed."""
from __future__ import annotations
import calendar
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "news" / "news-feed.json"
NOW = datetime.now(timezone.utc)
CUTOFF = NOW - timedelta(days=7)
UA = "Mozilla/5.0 (compatible; LaxmanNepalNewsBot/1.0; +https://laxmannepal.com.np/news/)"
FEEDS = [
    ("Nepal", "Nepal news", "https://news.google.com/rss/search?q=" + urllib.parse.quote('Nepal news when:7d') + "&hl=en-NP&gl=NP&ceid=NP:en"),
    ("Politics", "Nepal politics", "https://news.google.com/rss/search?q=" + urllib.parse.quote('Nepal politics government when:7d') + "&hl=en-NP&gl=NP&ceid=NP:en"),
    ("Business", "Nepal business", "https://news.google.com/rss/search?q=" + urllib.parse.quote('Nepal economy business market when:7d') + "&hl=en-NP&gl=NP&ceid=NP:en"),
    ("World", "World news", "https://news.google.com/rss/search?q=" + urllib.parse.quote('world news when:7d') + "&hl=en-US&gl=US&ceid=US:en"),
    ("Politics", "World politics", "https://news.google.com/rss/search?q=" + urllib.parse.quote('world politics diplomacy election when:7d') + "&hl=en-US&gl=US&ceid=US:en"),
    ("Business", "World business", "https://news.google.com/rss/search?q=" + urllib.parse.quote('global business economy markets when:7d') + "&hl=en-US&gl=US&ceid=US:en"),
    ("Technology", "Technology", "https://news.google.com/rss/search?q=" + urllib.parse.quote('technology AI cybersecurity gadgets when:7d') + "&hl=en-US&gl=US&ceid=US:en"),
    ("Science", "Science and space", "https://news.google.com/rss/search?q=" + urllib.parse.quote('science space climate research when:7d') + "&hl=en-US&gl=US&ceid=US:en"),
    ("Sports", "Sports", "https://news.google.com/rss/search?q=" + urllib.parse.quote('sports football cricket when:7d') + "&hl=en-US&gl=US&ceid=US:en"),
    ("Entertainment", "Entertainment", "https://news.google.com/rss/search?q=" + urllib.parse.quote('entertainment movies music celebrity when:7d') + "&hl=en-US&gl=US&ceid=US:en"),
    ("Trending", "Trending stories", "https://news.google.com/rss/search?q=" + urllib.parse.quote('viral trending internet culture when:7d') + "&hl=en-US&gl=US&ceid=US:en"),
]
def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()
def child_text(node: ET.Element, names: set[str]) -> str:
    for child in node.iter():
        if local_name(child.tag) in names and child.text:
            return child.text.strip()
    return ""
def parse_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (TypeError, ValueError, OverflowError):
        pass
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None
def text_only(value: str) -> str:
    value = re.sub(r"<[^>]*>", " ", value or "")
    return re.sub(r"\s+", " ", unescape(value)).strip()
def parse_feed(url: str, category: str, label: str) -> list[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml"})
    with urllib.request.urlopen(req, timeout=20) as response:
        root = ET.fromstring(response.read())
    results = []
    for item in root.iter():
        if local_name(item.tag) not in {"item", "entry"}:
            continue
        title = text_only(child_text(item, {"title"}))
        link = ""
        for child in list(item):
            if local_name(child.tag) == "link":
                href = child.attrib.get("href", "").strip()
                if href and child.attrib.get("rel", "alternate") in {"alternate", ""}:
                    link = href
                    break
                if child.text and child.text.strip():
                    link = child.text.strip()
                    break
        published = parse_date(child_text(item, {"pubdate", "published", "updated", "date", "issued"}))
        if not title or not link or not published or published < CUTOFF or published > NOW + timedelta(hours=1):
            continue
        if not link.startswith(("https://", "http://")):
            continue
        description = text_only(child_text(item, {"description", "summary", "content"}))
        source = child_text(item, {"source"}) or label
        if " - " in title and source == label:
            maybe_title, maybe_source = title.rsplit(" - ", 1)
            if maybe_title.strip() and maybe_source.strip():
                title, source = maybe_title.strip(), maybe_source.strip()
        image = ""
        for el in item.iter():
            if local_name(el.tag) in {"thumbnail", "content"}:
                candidate = el.attrib.get("url", "")
                if candidate.startswith("https://"):
                    image = candidate
                    break
        results.append({
            "id": link,
            "title": title[:300],
            "url": link,
            "published_at": published.isoformat().replace("+00:00", "Z"),
            "source": text_only(source)[:100] or label,
            "category": category,
            "description": description[:360],
            "image": image,
        })
    return results

def main() -> None:
    stories: dict[str, dict] = {}
    failures = []
    for category, label, url in FEEDS:
        try:
            for story in parse_feed(url, category, label):
                key = story["url"].split("#", 1)[0].rstrip("/").lower()
                if key not in stories or story["published_at"] > stories[key]["published_at"]:
                    stories[key] = story
            print(f"OK: {label}")
        except (urllib.error.URLError, TimeoutError, ET.ParseError, ValueError, OSError) as exc:
            failures.append(f"{label}: {type(exc).__name__}")
            print(f"WARN: {label} feed failed: {exc}")
        time.sleep(0.15)
    items = sorted(stories.values(), key=lambda s: s["published_at"], reverse=True)
    # Do not replace a healthy existing feed with an empty result during a temporary upstream outage.
    if not items and OUTPUT.exists():
        previous = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if previous.get("stories"):
            raise SystemExit("All feeds failed or returned no recent stories; preserving previous feed.")
    payload = {
        "generated_at": NOW.isoformat().replace("+00:00", "Z"),
        "window_days": 7,
        "story_count": len(items),
        "feeds_checked": len(FEEDS),
        "feeds_failed": failures,
        "stories": items,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(items)} recent stories to {OUTPUT}")
if __name__ == "__main__":
    main()
