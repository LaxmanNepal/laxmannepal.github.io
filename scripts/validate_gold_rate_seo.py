#!/usr/bin/env python3
"""Validate the Nepal gold/silver SEO cluster before publishing."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

BASE = "https://laxmannepal.com.np"
CLUSTER = {
    "/gold-rates-nepal/": {"types": {"WebPage", "BreadcrumbList"}, "snapshot": False},
    "/gold-price-in-nepal-today/": {"types": {"WebPage", "FAQPage", "BreadcrumbList"}, "snapshot": True},
    "/gold-price-history-nepal/": {"types": {"WebPage", "BreadcrumbList"}, "snapshot": True},
    "/silver-price-in-nepal-today/": {"types": {"WebPage", "BreadcrumbList"}, "snapshot": True},
}

def fail(errors, msg):
    errors.append(msg)

def read(root, path):
    p = root / path.lstrip("/") / "index.html"
    if not p.is_file():
        return None
    return p.read_text(encoding="utf-8", errors="ignore")

def json_ld(doc, path, errors):
    blocks = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', doc, re.I | re.S)
    types = set()
    for i, raw in enumerate(blocks, 1):
        try:
            obj = json.loads(raw.strip())
        except Exception as exc:
            fail(errors, f"{path}: JSON-LD block {i} is invalid JSON: {exc}")
            continue
        if isinstance(obj, dict):
            typ = obj.get("@type")
            if isinstance(typ, str):
                types.add(typ)
            elif isinstance(typ, list):
                types.update(x for x in typ if isinstance(x, str))
    return types

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".", help="Source or final Pages root")
    ap.add_argument("--data", default="data/gold-nepal.json")
    ap.add_argument("--allow-stale-days", type=int, default=3)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    data_path = Path(args.data)
    if not data_path.is_absolute():
        data_path = root / data_path
    errors, warnings = [], []

    try:
        payload = json.loads(data_path.read_text(encoding="utf-8"))
        latest = payload["latest"]
        conversion = payload["conversion"]
    except Exception as exc:
        print(f"ERROR: cannot load gold data: {exc}")
        return 1

    for path, rules in CLUSTER.items():
        doc = read(root, path)
        if doc is None:
            fail(errors, f"{path}: missing index.html")
            continue

        expected = BASE + path
        canon = re.findall(r'<link[^>]+rel=["\']canonical["\'][^>]*>', doc, re.I)
        if len(canon) != 1 or expected not in canon[0]:
            fail(errors, f"{path}: canonical must be exactly {expected}")

        robots = re.findall(r'<meta[^>]+name=["\']robots["\'][^>]*>', doc, re.I)
        if not robots or not re.search(r'index\s*,?\s*follow', robots[0], re.I):
            fail(errors, f"{path}: robots must allow index,follow")
        if re.search(r'noindex', " ".join(robots), re.I):
            fail(errors, f"{path}: noindex directive detected")

        types = json_ld(doc, path, errors)
        missing = rules["types"] - types
        if missing:
            fail(errors, f"{path}: missing JSON-LD types: {', '.join(sorted(missing))}")

        if rules["snapshot"]:
            if path == "/gold-price-in-nepal-today/":
                start, end = "GOLD_SEO_SNAPSHOT_START", "GOLD_SEO_SNAPSHOT_END"
                expected_values = [f"Rs {latest['fine_gold_tola']:,}", f"Rs {latest['tejabi_gold_tola']:,}", f"Rs {latest['silver_tola']:,}"]
            elif path == "/gold-price-history-nepal/":
                start, end = "LATEST_GOLD_HISTORY_SNAPSHOT_START", "LATEST_GOLD_HISTORY_SNAPSHOT_END"
                expected_values = [f"Rs {latest['fine_gold_tola']:,}", f"Rs {latest['tejabi_gold_tola']:,}", f"Rs {latest['silver_tola']:,}"]
            else:
                start, end = "SILVER_SEO_SNAPSHOT_START", "SILVER_SEO_SNAPSHOT_END"
                ten = round(latest["silver_tola"] * 10 / float(conversion["tola_grams"]))
                expected_values = [f"Rs {latest['silver_tola']:,}", f"Rs {ten:,}"]
            if start not in doc or end not in doc:
                fail(errors, f"{path}: snapshot markers missing")
            else:
                block = doc[doc.index(start):doc.index(end) + len(end)]
                for value in expected_values:
                    if value not in block:
                        fail(errors, f"{path}: snapshot missing current value {value}")
                if latest["date"] not in block:
                    fail(errors, f"{path}: snapshot missing current date {latest['date']}")

    # Cross-links are part of the cluster's crawl path.
    links = {p: read(root, p) or "" for p in CLUSTER}
    for src, doc in links.items():
        for dst in CLUSTER:
            if src != dst and dst not in doc:
                warnings.append(f"{src}: no direct link to {dst}")

    sitemap = root / "sitemap.xml"
    if sitemap.is_file():
        xml = sitemap.read_text(encoding="utf-8", errors="ignore")
        for path in CLUSTER:
            if BASE + path not in xml:
                fail(errors, f"sitemap.xml: missing {BASE + path}")
    else:
        warnings.append("sitemap.xml not present; final deployment build should generate it")

    robots_path = root / "robots.txt"
    if robots_path.is_file():
        robots = robots_path.read_text(encoding="utf-8", errors="ignore")
        if f"Sitemap: {BASE}/sitemap.xml" not in robots:
            fail(errors, "robots.txt: sitemap declaration missing")
    else:
        warnings.append("robots.txt not present in this build root")

    try:
        latest_date = date.fromisoformat(latest["date"])
        age = (date.today() - latest_date).days
        if age > args.allow_stale_days:
            warnings.append(f"gold data is {age} days old ({latest['date']}); review source freshness")
        else:
            print(f"Rate freshness: {age} day(s) old; latest={latest['date']}")
    except Exception as exc:
        fail(errors, f"invalid latest date: {exc}")

    print(f"Validated Nepal gold-rate SEO cluster: {len(CLUSTER)} pages")
    if warnings:
        for w in warnings:
            print(f"WARN: {w}")
    if errors:
        print(f"FAILED: {len(errors)} validation error(s)")
        for e in errors:
            print(f"ERROR: {e}")
        return 1
    print("Gold-rate SEO validation passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
