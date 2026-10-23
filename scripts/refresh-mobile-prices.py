#!/usr/bin/env python3
"""Refresh phone listings from the public GadgetByte Nepal mobile-price category.
Only publish values actually found in the source; never invent prices/specifications.
"""
from __future__ import annotations
import json, re, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

BASE = "https://www.gadgetbytenepal.com/category/mobile-price-in-nepal/"
OUT = Path("data/mobile-prices.json")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LaxmanNepalPriceDirectory/1.0; +https://laxmannepal.com.np/)"}
PRICE_RE = re.compile(r"(?:NPR|Rs\.?|रु\.?|रु)\s*([\d,]{4,})", re.I)
RAM_RE = re.compile(r"\b(\d{1,2})\s*GB\s*(?:RAM)?\b", re.I)
STORAGE_RE = re.compile(r"\b(\d{2,4})\s*GB\s*(?:ROM|storage|internal)?\b|\b(1|2)\s*TB\b", re.I)
BRANDS = ["Apple","Samsung","Xiaomi","Redmi","Poco","OnePlus","Vivo","OPPO","Oppo","Realme","Motorola","Nothing","Honor","Huawei","Tecno","Infinix","Nokia","Google","iQOO","Itel","ZTE","Lava","CMF","Lenovo"]

def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def fetch(url: str):
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def find_brand(title: str) -> str:
    low = title.lower()
    for b in sorted(BRANDS, key=len, reverse=True):
        if re.search(r"\b" + re.escape(b.lower()) + r"\b", low):
            return "OPPO" if b.lower() == "oppo" else b
    return "Other"

def first_price(text: str):
    # Prefer explicitly labelled phone price lines, not arbitrary specs or dates.
    for line in text.splitlines():
        if re.search(r"\b(price|priced|cost|नेपालमा मूल्य|मूल्य)\b", line, re.I):
            m = PRICE_RE.search(line)
            if m:
                return int(m.group(1).replace(",", ""))
    m = PRICE_RE.search(text)
    return int(m.group(1).replace(",", "")) if m else None

def specs_from(text: str):
    ram = storage = display = battery = None
    # Keep RAM/storage conservative: only parse near explicit labels.
    for line in text.splitlines():
        if not ram and re.search(r"\bRAM\b", line, re.I):
            m = re.search(r"\b(\d{1,2})\s*GB\s*RAM\b", line, re.I)
            if m: ram = m.group(1) + "GB"
        if not storage and re.search(r"\b(ROM|storage|internal storage)\b", line, re.I):
            m = re.search(r"\b(\d{2,4})\s*GB\b|\b(1|2)\s*TB\b", line, re.I)
            if m: storage = (m.group(1) + "GB") if m.group(1) else (m.group(2) + "TB")
        if not display:
            m = re.search(r"(\d(?:\.\d{1,2})?)\s*(?:-inch|inch|inches|″)", line, re.I)
            if m: display = m.group(1) + " inch"
        if not battery:
            m = re.search(r"\b(\d{3,5})\s*mAh\b", line, re.I)
            if m: battery = m.group(1) + "mAh"
    return ram, storage, display, battery

def main():
    soup = fetch(BASE)
    candidates = []
    seen = set()
    # WordPress category cards; deliberately avoid navigation/sidebar links.
    for a in soup.select("article a[href], .post a[href], .jeg_post_title a[href], h2 a[href], h3 a[href]"):
        href = urljoin(BASE, a.get("href", "").strip())
        title = clean(a.get_text(" ", strip=True))
        if not title or len(title) < 7 or not href.startswith("https://www.gadgetbytenepal.com/"):
            continue
        if "/category/" in urlparse(href).path or urlparse(href).path in ("/", ""):
            continue
        if href in seen: continue
        seen.add(href)
        parent = a.find_parent("article") or a.find_parent(class_=re.compile(r"post|item|article", re.I)) or a.parent
        img = parent.select_one("img") if parent else None
        image = None
        if img:
            image = img.get("data-src") or img.get("data-lazy-src") or img.get("src")
            if image and image.startswith("//"): image = "https:" + image
            if image and not image.startswith("http"): image = urljoin(BASE, image)
        candidates.append({"title": title, "url": href, "image": image})
    # Fetch individual article pages to extract real values, with a polite delay.
    phones = []
    for item in candidates[:180]:
        try:
            detail = fetch(item["url"])
            article = detail.select_one("article .entry-content, .entry-content, .jeg_post_content, article")
            text = clean(article.get_text("\n", strip=True) if article else detail.get_text("\n", strip=True))
            # Keep likely phone/list articles, not unrelated category noise.
            title = item["title"]
            if not re.search(r"\b(price|mobile|phone|smartphone|series|iphone|galaxy|redmi|pixel|oneplus|vivo|oppo|realme|poco|motorola|nothing|honor|infinix|tecno|nokia|iqoo)\b", title, re.I):
                continue
            price = first_price(text)
            ram, storage, display, battery = specs_from(text)
            phones.append({
                "brand": find_brand(title), "model": title, "title": title,
                "price": price, "price_text": None if price else "Price not confirmed",
                "ram": ram, "storage": storage, "display": display, "battery": battery,
                "image": item["image"], "url": item["url"],
                "updated_at": datetime.now(timezone.utc).date().isoformat()
            })
            time.sleep(0.35)
        except Exception as exc:
            print(f"Skipping {item['url']}: {exc}")
    # Stable de-duplication by canonical article URL.
    unique, final = set(), []
    for p in phones:
        if p["url"] not in unique:
            unique.add(p["url"]); final.append(p)
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source": "GadgetByte Nepal",
        "source_url": BASE,
        "status": "Daily automated refresh; extracted fields may be incomplete",
        "phones": final
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(final)} listings to {OUT}")
    if not final:
        raise SystemExit("No listings were extracted; refusing to publish an empty refresh.")

if __name__ == "__main__":
    main()
