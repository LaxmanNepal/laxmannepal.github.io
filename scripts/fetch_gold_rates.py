#!/usr/bin/env python3
from __future__ import annotations
import json, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "gold-nepal.json"
DATA.parent.mkdir(parents=True, exist_ok=True)

SOURCES = [
    ("Ashesh.com.np · FENEGOSIDA feed", "https://www.ashesh.com.np/gold/widget.php?api=872076p237&header_color=0077e5"),
    ("FENEGOSIDA", "https://www.fenegosida.org/"),
]

def fetch(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 LaxmanNepalGoldRate/1.0"})
    with urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "ignore")

def clean(text):
    return re.sub(r"[^0-9]", "", text or "")

def parse_rates(html):
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.I|re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    def near(label, window=260):
        m = re.search(label, text, re.I)
        if not m: return None
        nums = re.findall(r"(?:Rs\.?\s*)?([0-9][0-9,]{3,})", text[m.end():m.end()+window])
        return int(nums[0].replace(",","")) if nums else None
    fine = near(r"(?:Gold Hallmark|Fine gold 9999|Fine Gold)")
    tejabi = near(r"(?:Gold Tajabi|22\s*KT|22K)")
    silver = near(r"Silver")
    # Ashesh lists per-tola first and then 10g; prefer the first occurrence after each label.
    return fine, tejabi, silver

def parse_ashesh(html):
    # The widget currently exposes these labels and values as plain HTML.
    return parse_rates(html)

def load():
    if DATA.exists():
        try: return json.loads(DATA.read_text(encoding="utf-8"))
        except Exception: pass
    return {"history": [], "latest": None}

def main():
    old = load()
    found = None
    errors = []
    for name, url in SOURCES:
        try:
            html = fetch(url)
            fine, tejabi, silver = parse_rates(html)
            if fine and silver:
                found = {"source": name, "url": url, "fine_tola": fine, "tejabi_tola": tejabi, "silver_tola": silver}
                break
            errors.append(f"{name}: rates not detected")
        except Exception as e:
            errors.append(f"{name}: {e}")

    now = datetime.now(timezone.utc)
    stamp = now.isoformat()
    if not found:
        # Preserve the last verified record, but explicitly mark it stale.
        latest = old.get("latest")
        payload = old
        payload["status"] = "stale"
        payload["last_attempted_at"] = stamp
        payload["errors"] = errors
        DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        raise SystemExit("No rate source could be parsed: " + " | ".join(errors))

    fine = found["fine_tola"]
    tejabi = found["tejabi_tola"]
    silver = found["silver_tola"]
    # A tola is 11.6638125g; keep the conversion precise and calculate display values client-side too.
    record = {
        "date": now.strftime("%Y-%m-%d"),
        "updated_at": stamp,
        "fine_gold_tola": fine,
        "tejabi_gold_tola": tejabi,
        "silver_tola": silver,
        "source": found["source"],
        "source_url": found["url"],
        "unit": "NPR per tola",
    }
    history = [x for x in old.get("history", []) if x.get("date") != record["date"]]
    history.append(record)
    history = history[-60:]
    payload = {
        "status": "verified",
        "last_attempted_at": stamp,
        "latest": record,
        "history": history,
        "conversion": {"tola_grams": 11.6638125, "aana_per_tola": 16, "lal_per_tola": 100},
        "errors": errors,
    }
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False))

if __name__ == "__main__":
    main()
