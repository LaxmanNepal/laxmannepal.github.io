#!/usr/bin/env python3
"""Fail fast when mobile-price JSON metadata or generated detail pages drift."""
from __future__ import annotations
import json
import math
from pathlib import Path
DATA = Path("data/mobile-prices.json")
DETAILS = Path("mobile-price-in-nepal/phones")
def valid_offer(offer):
    if not isinstance(offer, dict):
        return False
    price = offer.get("price")
    return isinstance(price, (int, float)) and not isinstance(price, bool) and math.isfinite(float(price)) and float(price) > 0 and bool(str(offer.get("store", "")).strip())
def audit(data, root=Path(".")):
    phones = data.get("phones") if isinstance(data, dict) else None
    if not isinstance(phones, list) or not phones:
        raise ValueError("Catalogue must contain a non-empty phones list")
    slugs = [phone.get("slug") for phone in phones if isinstance(phone, dict)]
    if len(slugs) != len(phones) or any(not slug for slug in slugs):
        raise ValueError("Every phone must be an object with a slug")
    if len(set(slugs)) != len(slugs):
        raise ValueError("Phone slugs must be unique")
    offers = [offer for phone in phones for offer in (phone.get("prices") if isinstance(phone.get("prices"), list) else []) if valid_offer(offer)]
    stores = {str(offer["store"]).strip() for offer in offers}
    if data.get("price_count") != len(offers):
        raise ValueError(f"price_count mismatch: metadata={data.get('price_count')} valid offers={len(offers)}")
    if data.get("store_count") != len(stores):
        raise ValueError(f"store_count mismatch: metadata={data.get('store_count')} valid stores={len(stores)}")
    if data.get("variant_count", len(phones)) != len(phones):
        raise ValueError("variant_count mismatch")
    missing = []
    for phone in phones:
        for offer in phone.get("prices", []) if isinstance(phone.get("prices"), list) else []:
            if isinstance(offer, dict) and offer.get("price") is not None:
                price = offer.get("price")
                if not isinstance(price, (int, float)) or isinstance(price, bool) or not math.isfinite(float(price)) or float(price) < 1000:
                    raise ValueError(f"Suspicious price for {phone.get('model') or phone.get('slug')}: {price}")
        path = root / DETAILS / phone["slug"] / "index.html"
        if not path.is_file():
            missing.append(str(path))
            continue
        html = path.read_text(encoding="utf-8", errors="ignore")
        if "<title" not in html.lower() or 'rel="canonical"' not in html.lower():
            raise ValueError(f"Generated phone page missing title/canonical: {path}")
    if missing:
        raise ValueError("Missing generated phone pages: " + ", ".join(missing[:20]))
    return len(phones), len(offers), len(stores)
def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    variants, offers, stores = audit(data)
    print(f"Mobile catalogue audit passed: {variants} variants, {offers} valid priced offers, {stores} stores; generated detail pages verified.")
if __name__ == "__main__":
    main()
