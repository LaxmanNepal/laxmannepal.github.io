#!/usr/bin/env python3
"""Repair derived mobile-catalogue metadata without changing source prices."""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path("data/mobile-prices.json")


def numeric_price(item):
    value = item.get("price") if isinstance(item, dict) else None
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def repair(data):
    phones = data.get("phones") if isinstance(data, dict) else None
    if not isinstance(phones, list) or not phones:
        raise SystemExit("mobile-prices.json must contain a non-empty phones list")

    stores = set()
    offer_count = 0
    changed = 0

    for phone in phones:
        if not isinstance(phone, dict):
            continue
        prices = phone.get("prices")
        if not isinstance(prices, list):
            prices = []
            phone["prices"] = prices

        valid = [item for item in prices if numeric_price(item)]
        for item in valid:
            stores.add(str(item.get("store", "")).strip())
        offer_count += len(valid)

        best = min(valid, key=lambda item: float(item["price"])) if valid else None
        desired_count = len(valid)
        if phone.get("price_count") != desired_count:
            phone["price_count"] = desired_count
            changed += 1
        if best:
            for key, value in (("price", best["price"]), ("best_store", best.get("store")), ("best_url", best.get("url"))):
                if phone.get(key) != value:
                    phone[key] = value
                    changed += 1
        else:
            for key in ("price", "best_store", "best_url"):
                if phone.get(key) is not None:
                    phone[key] = None
                    changed += 1

    for key, value in (("variant_count", len(phones)), ("price_count", offer_count), ("store_count", len(stores))):
        if data.get(key) != value:
            data[key] = value
            changed += 1

    return changed


def main():
    data = json.loads(OUT.read_text(encoding="utf-8"))
    changed = repair(data)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Mobile catalogue metadata repair: {changed} fields updated.")


if __name__ == "__main__":
    main()
