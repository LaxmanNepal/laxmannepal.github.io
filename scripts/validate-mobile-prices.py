#!/usr/bin/env python3
"""Validate and repair obvious mobile-price parsing errors before publication.

The scraper keeps retailer prices separate. This pass only changes a price when
there is strong internal evidence that a decimal/zero was lost (for example
12,000 vs 120,000): a 10x correction must land close to the other stores' price.
Apple/iPhone prices also get a conservative floor so a malformed five-digit price
cannot become the cheapest offer without verification.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import median

OUT = Path("data/mobile-prices.json")
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

        # Strong tenfold-error signal: corrected price is close to the peer median.
        if reference and price < reference / 5:
            candidate = price * 10
            if 1000 < candidate < MAX_REASONABLE_NPR and abs(candidate - reference) / reference <= 0.30:
                item["price"] = int(round(candidate))
                item["price_validation"] = "auto-corrected-10x"
                changes += 1
                continue

        # iPhone listings below NPR 50k are treated as malformed unless the
        # 10x correction is strongly supported by peer-store evidence.
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

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Price validation complete: {changed} corrected, {removed} suspicious offers removed.")


if __name__ == "__main__":
    main()
