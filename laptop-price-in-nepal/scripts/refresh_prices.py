import datetime
import json
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher

DATA = "laptop-price-in-nepal/data/laptops.json"
UA = "Mozilla/5.0 (compatible; LaxmanNepalLaptopBot/1.1)"
MIN_PRICE = 5000
MAX_PRICE = 2_000_000
MIN_MATCH_SCORE = 0.82
MAX_PRICE_CHANGE_RATIO = 0.35


def norm(value):
    value = unicodedata.normalize("NFKD", str(value or "")).lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def price(value):
    if isinstance(value, (int, float)):
        result = int(value)
    else:
        match = re.search(r"(?:rs\.?|npr)\s*([0-9][0-9,]*)", str(value), re.I)
        if not match:
            return None
        result = int(match.group(1).replace(",", ""))
    return result if MIN_PRICE <= result <= MAX_PRICE else None


def walk_json(value, out):
    if isinstance(value, dict):
        types = value.get("@type", [])
        if isinstance(types, str):
            types = [types]
        if any(item in {"Product", "ItemList"} for item in types):
            out.append(value)
        for child in value.values():
            walk_json(child, out)
    elif isinstance(value, list):
        for child in value:
            walk_json(child, out)


def extract(url):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=25) as response:
        html = response.read().decode("utf-8", "ignore")

    found = []
    pattern = r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    for match in re.finditer(pattern, html, re.I | re.S):
        try:
            walk_json(json.loads(match.group(1)), found)
        except (json.JSONDecodeError, TypeError):
            continue

    rows = []
    for item in found:
        candidates = [item] if "Product" in str(item.get("@type", "")) else []
        entries = item.get("itemListElement", [])
        for entry in entries if isinstance(entries, list) else []:
            product = entry.get("item", entry) if isinstance(entry, dict) else {}
            if isinstance(product, dict):
                candidates.append(product)

        for product in candidates:
            offers = product.get("offers", {})
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            if not isinstance(offers, dict):
                continue
            amount = price(offers.get("price") or offers.get("lowPrice"))
            name = product.get("name", "")
            if not name or not amount:
                continue
            candidate_url = offers.get("url") or product.get("url") or ""
            if candidate_url:
                candidate_url = urllib.parse.urljoin(url, candidate_url)
            rows.append({"name": name, "price": amount, "url": candidate_url})

    # Deduplicate identical product/price rows without guessing between variants.
    unique = {}
    for row in rows:
        unique[(norm(row["name"]), row["price"], row["url"])] = row
    return list(unique.values())


def is_direct_product_url(candidate, source_url):
    if not candidate:
        return False
    candidate_parts = urllib.parse.urlsplit(candidate)
    source_parts = urllib.parse.urlsplit(source_url)
    if candidate_parts.netloc and candidate_parts.netloc != source_parts.netloc:
        return False
    candidate_path = candidate_parts.path.rstrip("/")
    source_path = source_parts.path.rstrip("/")
    return bool(candidate_path and candidate_path != source_path and candidate_path.startswith(source_path + "/") or
                candidate_path and candidate_path != source_path and source_parts.path in {"", "/"})


def main():
    with open(DATA, encoding="utf-8") as file:
        data = json.load(file)

    today = datetime.date.today().isoformat()
    changed = 0
    successful_sources = 0
    sources = {
        store["id"]: store["url"]
        for store in data["stores"]
        if store["id"] in {"bt-planet", "tech-chautari"}
    }

    for store_id, source_url in sources.items():
        try:
            rows = extract(source_url)
            successful_sources += 1
            print(f"{store_id}: extracted {len(rows)} priced product records")
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
            print(f"source failed {store_id}: {error}")
            continue

        for product in data["products"]:
            old = next((offer for offer in product["offers"] if offer["storeId"] == store_id), None)
            target = norm(product["brand"] + " " + product["name"])
            brand = norm(product["brand"])
            # Never match a listing that does not explicitly contain the brand.
            candidates = [
                row for row in rows
                if brand and brand in norm(row["name"])
            ]
            ranked = sorted(
                ((SequenceMatcher(None, target, norm(row["name"])).ratio(), row)
                 for row in candidates),
                key=lambda pair: pair[0],
                reverse=True,
            )
            if not ranked:
                continue
            score, best = ranked[0]
            # Reject weak or ambiguous matches instead of corrupting the catalogue.
            if score < MIN_MATCH_SCORE:
                continue
            if len(ranked) > 1 and ranked[1][0] >= score - 0.025:
                print(f"ambiguous match skipped: {product['id']} at {store_id}")
                continue
            if old:
                change_ratio = abs(best["price"] - old["price"]) / max(old["price"], 1)
                if change_ratio > MAX_PRICE_CHANGE_RATIO:
                    print(f"large price change skipped: {product['id']} at {store_id}")
                    continue
            direct_url = best.get("url", "")
            if not is_direct_product_url(direct_url, source_url):
                # Keep a known offer link; never replace it with a generic category page.
                if not old:
                    print(f"no direct product URL; offer not added: {product['id']} at {store_id}")
                    continue
                direct_url = old.get("url", "")

            new_offer = {
                "storeId": store_id,
                "price": best["price"],
                "availability": "Listed; confirm stock",
                "url": direct_url,
                "checked": today,
            }
            if old != new_offer:
                if old:
                    product["offers"][product["offers"].index(old)] = new_offer
                else:
                    product["offers"].append(new_offer)
                product["priceFrom"] = min(offer["price"] for offer in product["offers"])
                changed += 1

    if successful_sources:
        data["generatedAt"] = today
    with open(DATA, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")

    print(f"Sources fetched: {successful_sources}/{len(sources)}; offers changed: {changed}")
    if not successful_sources:
        raise SystemExit("No sources could be fetched; catalogue left unchanged except formatting.")


if __name__ == "__main__":
    main()
