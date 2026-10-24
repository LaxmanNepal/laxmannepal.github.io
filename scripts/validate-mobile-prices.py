#!/usr/bin/env python3
"""Validate and repair obvious mobile-price parsing errors before publication."""
from __future__ import annotations

import importlib.util
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

OUT = Path("data/mobile-prices.json")
DETAIL_ROOT = Path("mobile-price-in-nepal/phones")
HISTORY_OUT = Path("data/mobile-price-history.json")
STATUS_OUT = Path("data/mobile-price-refresh-status.json")
APPLE_MIN_NPR = 50_000
MAX_REASONABLE_NPR = 3_000_000


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v))


def is_iphone(phone):
    text = " ".join(str(phone.get(k, "")) for k in ("model", "title", "name", "brand"))
    return "iphone" in text.lower() or str(phone.get("brand", "")).lower() == "apple"


def repair_phone(phone):
    prices = phone.get("prices")
    if not isinstance(prices, list):
        return 0, 0

    values = [float(x["price"]) for x in prices if isinstance(x, dict) and is_num(x.get("price")) and 1000 < float(x["price"]) < MAX_REASONABLE_NPR]
    changes = 0
    removed = 0

    for item in prices:
        if not isinstance(item, dict) or not is_num(item.get("price")):
            continue
        price = float(item["price"])
        if not (1000 < price < MAX_REASONABLE_NPR):
            continue

        peers = [v for v in values if v != price]
        reference = median(peers) if peers else None

        if reference and price < reference / 5:
            candidate = price * 10
            if 1000 < candidate < MAX_REASONABLE_NPR and abs(candidate - reference) / reference <= 0.30:
                item["price"] = int(round(candidate))
                item["price_validation"] = "auto-corrected-10x"
                changes += 1
                continue

        if is_iphone(phone) and price < APPLE_MIN_NPR:
            if reference:
                candidate = price * 10
                if APPLE_MIN_NPR <= candidate < MAX_REASONABLE_NPR and abs(candidate - reference) / reference <= 0.30:
                    item["price"] = int(round(candidate))
                    item["price_validation"] = "auto-corrected-iphone-10x"
                    changes += 1
                    continue
            item["price_validation"] = "rejected-suspicious-iphone-price"
            item["price"] = None
            removed += 1

    phone["prices"] = [x for x in prices if not (isinstance(x, dict) and x.get("price_validation") == "rejected-suspicious-iphone-price")]
    return changes, removed


def regenerate_detail_pages(phones):
    """Regenerate generated phone pages so JSON and visible detail prices cannot diverge."""
    spec = importlib.util.spec_from_file_location("mobile_prices_scraper", "scripts/refresh-mobile-prices.py")
    if spec is None or spec.loader is None:
        raise SystemExit("Unable to load mobile price scraper for page regeneration")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    count = 0
    for phone in phones:
        slug = phone.get("slug")
        if not slug:
            continue
        target = DETAIL_ROOT / slug / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(mod.page_template(phone), encoding="utf-8")
        count += 1
    print(f"Regenerated {count} phone detail pages after price validation.")


def refresh_metadata(data, phones):
    """Normalize offer arrays and recompute per-phone and catalogue metadata."""
    valid_stores = set()
    valid_count = 0
    for phone in phones:
        if not isinstance(phone, dict):
            continue
        prices = phone.get("prices")
        if not isinstance(prices, list):
            prices = []
        prices = [
            item for item in prices
            if isinstance(item, dict)
            and is_num(item.get("price"))
            and float(item["price"]) > 0
            and str(item.get("store", "")).strip()
        ]
        prices.sort(key=lambda item: (bool(item.get("stale")), float(item["price"])))
        phone["prices"] = prices
        phone["price_count"] = len(prices)
        current_prices = [item for item in prices if not item.get("stale")]
        best = current_prices[0] if current_prices else (prices[0] if prices else None)
        phone["price_is_stale"] = bool(prices) and not bool(current_prices)
        phone["fresh_offer_count"] = len(current_prices)
        phone["stale_offer_count"] = len(prices) - len(current_prices)
        if best:
            phone["price"] = int(round(float(best["price"])))
            phone["best_store"] = best["store"]
            phone["best_url"] = best.get("url")
            valid_stores.update(str(item["store"]).strip() for item in prices)
            valid_count += len(prices)
        else:
            phone["price"] = None
            phone["best_store"] = None
            phone["best_url"] = None
    data["price_count"] = valid_count
    data["store_count"] = len(valid_stores)
    data["variant_count"] = len(phones)

def sync_today_history(phones, history_path=HISTORY_OUT):
    """Replace today's pre-validation snapshot with the validated catalogue."""
    if not history_path.exists():
        return 0
    try:
        history = json.loads(history_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise SystemExit(f"Unable to read mobile price history: {history_path}")
    if not isinstance(history, dict) or not isinstance(history.get("days"), list):
        raise SystemExit("mobile-price-history.json: expected a days list")

    today = datetime.now(timezone.utc).date().isoformat()
    snapshot_phones = []
    for phone in phones:
        if not isinstance(phone, dict):
            continue
        valid = [
            item for item in phone.get("prices", [])
            if isinstance(item, dict) and is_num(item.get("price")) and float(item["price"]) > 0 and item.get("store") and not item.get("stale")
        ]
        if not valid:
            continue
        valid.sort(key=lambda item: float(item["price"]))
        snapshot_phones.append({
            "slug": phone.get("slug"),
            "model": phone.get("model") or phone.get("title") or phone.get("slug"),
            "best_price": int(round(float(valid[0]["price"]))),
            "best_store": valid[0]["store"],
            "offers": [
                {"store": item["store"], "price": int(round(float(item["price"])))}
                for item in valid
            ],
        })

    days = [day for day in history["days"] if isinstance(day, dict) and day.get("date") != today]
    days.append({"date": today, "phones": snapshot_phones})
    history["days"] = sorted(days, key=lambda day: str(day.get("date", "")))[-180:]
    history["updated_at"] = datetime.now(timezone.utc).isoformat()

    by_slug = {}
    for day in history["days"]:
        for item in day.get("phones", []):
            if isinstance(item, dict) and item.get("slug"):
                by_slug.setdefault(item["slug"], []).append({
                    "date": day.get("date"),
                    "price": item.get("best_price"),
                })
    for phone in phones:
        if isinstance(phone, dict):
            phone["history"] = [
                item for item in by_slug.get(phone.get("slug"), [])
                if is_num(item.get("price")) and float(item["price"]) > 0
            ]

    history_path.write_text(json.dumps(history, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Synchronized validated catalogue into {today}'s price-history snapshot.")
    return len(snapshot_phones)

def main():
    data = json.loads(OUT.read_text(encoding="utf-8"))
    phones = data.get("phones") if isinstance(data, dict) else data
    if not isinstance(phones, list):
        raise SystemExit("mobile-prices.json: expected a top-level phones list")

    changed = removed = 0
    suspicious = []
    for phone in phones:
        if not isinstance(phone, dict):
            continue
        c, r = repair_phone(phone)
        changed += c
        removed += r
        for item in phone.get("prices", []):
            if isinstance(item, dict) and is_num(item.get("price")) and item["price"] < 1000:
                suspicious.append((phone.get("model") or phone.get("title"), item.get("price")))

    if suspicious:
        raise SystemExit(f"Suspicious published prices remain: {suspicious[:10]}")

    refresh_metadata(data, phones)
    sync_today_history(phones)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if STATUS_OUT.exists():
        try:
            status_doc = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"Unable to update mobile refresh status: {exc}")
        status_doc["model_variants"] = len(phones)
        status_doc["fresh_offers"] = sum(
            1 for phone in phones for offer in phone.get("prices", [])
            if isinstance(offer, dict) and is_num(offer.get("price")) and not offer.get("stale")
        )
        status_doc["stale_offers"] = sum(
            1 for phone in phones for offer in phone.get("prices", [])
            if isinstance(offer, dict) and is_num(offer.get("price")) and offer.get("stale")
        )
        STATUS_OUT.write_text(json.dumps(status_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    regenerate_detail_pages(phones)
    print(f"Price validation complete: {changed} corrected, {removed} suspicious offers removed.")
    print(f"Catalogue metadata: {data['variant_count']} variants, {data['price_count']} offers, {data['store_count']} stores.")


if __name__ == "__main__":
    main()
