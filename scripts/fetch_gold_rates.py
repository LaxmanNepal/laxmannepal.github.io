#!/usr/bin/env python3
from __future__ import annotations
import json, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "gold-nepal.json"
PAGE = ROOT / "gold-price-in-nepal-today" / "index.html"
DATA.parent.mkdir(parents=True, exist_ok=True)

SOURCES = [
    ("Ashesh.com.np · FENEGOSIDA feed", "https://www.ashesh.com.np/gold/widget.php?api=872076p237&header_color=0077e5"),
    ("FENEGOSIDA", "https://www.fenegosida.org/"),
]

def fetch(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 LaxmanNepalGoldRate/1.1"})
    with urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "ignore")

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
    return fine, tejabi, silver

def load():
    if DATA.exists():
        try: return json.loads(DATA.read_text(encoding="utf-8"))
        except Exception: pass
    return {"history": [], "latest": None}

def update_seo_snapshot(page_text, record):
    start = "<!-- GOLD_SEO_SNAPSHOT_START -->"
    end = "<!-- GOLD_SEO_SNAPSHOT_END -->"
    if start not in page_text or end not in page_text:
        raise RuntimeError("Gold SEO snapshot markers are missing from the page")
    local_date = record["date"]
    fine = f'{record["fine_gold_tola"]:,}'
    tejabi = f'{record["tejabi_gold_tola"]:,}' if record.get("tejabi_gold_tola") else "Not reported"
    silver = f'{record["silver_tola"]:,}'
    block = f'''{start}
<div class="seo-snapshot" aria-label="Today's Nepal gold and silver rates">
<strong>Gold price in Nepal today — latest published rates</strong>
<p class="muted" style="margin:6px 0 0">Latest verified market figures for <time datetime="{local_date}">{datetime.strptime(local_date, "%Y-%m-%d").strftime("%d %B %Y")}</time>, shown in Nepalese rupees.</p>
<div class="seo-snapshot-grid">
<div class="seo-snapshot-item"><span>Fine Gold (9999) per tola</span><b>Rs {fine}</b></div>
<div class="seo-snapshot-item"><span>Tejabi Gold per tola</span><b>Rs {tejabi}</b></div>
<div class="seo-snapshot-item"><span>Silver per tola</span><b>Rs {silver}</b></div>
</div>
</div>
{end}'''
    return page_text[:page_text.index(start)] + block + page_text[page_text.index(end) + len(end):]

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
        payload = old
        payload["status"] = "stale"
        payload["last_attempted_at"] = stamp
        payload["errors"] = errors
        DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise SystemExit("No rate source could be parsed: " + " | ".join(errors))

    fine = found["fine_tola"]
    tejabi = found["tejabi_tola"]
    silver = found["silver_tola"]
    if not (200000 <= fine <= 500000 and 200000 <= (tejabi or fine) <= 500000 and 2000 <= silver <= 10000):
        raise SystemExit(f"Sanity check failed: fine={fine}, tejabi={tejabi}, silver={silver}")

    local_now = now.astimezone(ZoneInfo("Asia/Kathmandu"))
    record = {
        "date": local_now.strftime("%Y-%m-%d"),
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
    page = PAGE.read_text(encoding="utf-8")
    PAGE.write_text(update_seo_snapshot(page, record), encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False))

if __name__ == "__main__":
    main()
