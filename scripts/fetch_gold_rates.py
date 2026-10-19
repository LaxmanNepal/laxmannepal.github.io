#!/usr/bin/env python3
from __future__ import annotations
import json, re
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "gold-nepal.json"
LIVE_DATA = ROOT / "data" / "gold-nepal-live.json"
PAGE = ROOT / "gold-price-in-nepal-today" / "index.html"
HISTORY_PAGE = ROOT / "gold-price-history-nepal" / "index.html"
SILVER_PAGE = ROOT / "silver-price-in-nepal-today" / "index.html"
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
    # Require a source-published date so cached data is never labelled as today's rate.
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.I|re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    date_match = re.search(r"\b(\d{1,2})[-/ ](Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[-/ ](\d{4})\b", text, re.I)
    if not date_match:
        raise RuntimeError("Source-published date not detected; refusing to label unverified rates as current")
    source_date = datetime.strptime(date_match.group(0).replace("/", "-").replace(" ", "-"), "%d-%b-%Y").date()
    def near(label, low, high, window=360):
        # A page may mention a metal in its title before its actual rate card.
        # Inspect each label occurrence and accept only a value in the plausible rate range.
        for m in re.finditer(label, text, re.I):
            nums = re.findall(r"(?:Rs\.?\s*)?([0-9][0-9,]{3,})", text[m.end():m.end()+window])
            for raw in nums:
                value = int(raw.replace(",", ""))
                # Ignore purity labels (9999), dates/years and unrelated counts.
                if low <= value <= high and not 1900 <= value <= 2100:
                    return value
        return None
    fine = near(r"(?:Gold Hallmark|Fine gold 9999|Fine Gold)", 200000, 500000)
    tejabi = near(r"(?:Gold Tajabi|Tejabi Gold|22\s*KT|22K)", 200000, 500000)
    silver = near(r"Silver", 2000, 10000)
    return source_date, fine, tejabi, silver

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

def update_schema_date(page_text, local_date):
    return re.sub(r'("dateModified"\s*:\s*")[0-9]{4}-[0-9]{2}-[0-9]{2}(")', rf'\g<1>{local_date}\g<2>', page_text, count=1)

def replace_marked(text, start, end, block):
    if start not in text or end not in text:
        raise RuntimeError(f"Missing snapshot markers: {start}")
    a=text.index(start); b=text.index(end)+len(end)
    return text[:a]+block+text[b:]

def update_cluster_snapshots(record):
    date=record["date"]
    display=datetime.strptime(date,"%Y-%m-%d").strftime("%d %B %Y")
    fine=f'{record["fine_gold_tola"]:,}'; tejabi=f'{record["tejabi_gold_tola"]:,}' if record.get("tejabi_gold_tola") else "Not reported"; silver=f'{record["silver_tola"]:,}'
    ten=f'{round(record["silver_tola"]*10/11.6638125):,}'
    history=HISTORY_PAGE.read_text(encoding="utf-8")
    hs="<!-- LATEST_GOLD_HISTORY_SNAPSHOT_START -->"; he="<!-- LATEST_GOLD_HISTORY_SNAPSHOT_END -->"
    hb=f'''{hs}<h2>Latest published gold rate in Nepal</h2><p><strong>Fine Gold: Rs {fine} per tola</strong> · <strong>Tejabi Gold: Rs {tejabi} per tola</strong> · <strong>Silver: Rs {silver} per tola</strong> (<time datetime="{date}">{display}</time>).</p><p class="muted">This snapshot is updated automatically from the stored daily rate record.</p>{he}'''
    HISTORY_PAGE.write_text(replace_marked(history,hs,he,hb),encoding="utf-8")
    silver_page=SILVER_PAGE.read_text(encoding="utf-8")
    ss="<!-- SILVER_SEO_SNAPSHOT_START -->"; se="<!-- SILVER_SEO_SNAPSHOT_END -->"
    sb=f'''{ss}<strong>Silver price in Nepal today — latest published rate</strong><p><time datetime="{date}">{display}</time>: <strong>Rs {silver} per tola</strong> and <strong>Rs {ten} per 10 grams</strong>.</p><p class="muted">This crawlable snapshot is updated automatically from the stored daily rate record.</p>{se}'''
    SILVER_PAGE.write_text(replace_marked(silver_page,ss,se,sb),encoding="utf-8")

def main():
    old = load()
    found = None
    errors = []
    for name, url in SOURCES:
        try:
            html = fetch(url)
            source_date, fine, tejabi, silver = parse_rates(html)
            age_days = (datetime.now(ZoneInfo("Asia/Kathmandu")).date() - source_date).days
            if age_days < 0 or age_days > 3:
                errors.append(f"{name}: source date {source_date} is outside the allowed freshness window ({age_days} days old)")
                continue
            if not fine or not silver or not (200000 <= fine <= 500000 and 200000 <= (tejabi or fine) <= 500000 and 2000 <= silver <= 10000):
                errors.append(f"{name}: parsed values failed plausibility checks (fine={fine}, tejabi={tejabi}, silver={silver})")
                continue
            found = {"source": name, "url": url, "date": source_date.isoformat(), "fine_tola": fine, "tejabi_tola": tejabi, "silver_tola": silver}
            break
        except Exception as e:
            errors.append(f"{name}: {e}")

    now = datetime.now(timezone.utc)
    stamp = now.isoformat()
    if not found:
        payload = old
        payload["status"] = "stale"
        payload["last_attempted_at"] = stamp
        payload["errors"] = errors
        serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        DATA.write_text(serialized, encoding="utf-8")
        LIVE_DATA.write_text(serialized, encoding="utf-8")
        raise SystemExit("No rate source could be parsed: " + " | ".join(errors))

    fine = found["fine_tola"]
    tejabi = found["tejabi_tola"]
    silver = found["silver_tola"]
    if not (200000 <= fine <= 500000 and 200000 <= (tejabi or fine) <= 500000 and 2000 <= silver <= 10000):
        raise SystemExit(f"Sanity check failed: fine={fine}, tejabi={tejabi}, silver={silver}")

    local_now = now.astimezone(ZoneInfo("Asia/Kathmandu"))
    record = {
        "date": found["date"],
        "updated_at": stamp,
        "fine_gold_tola": fine,
        "tejabi_gold_tola": tejabi,
        "silver_tola": silver,
        "source": found["source"],
        "source_url": found["url"],
        "unit": "NPR per tola",
    }
    old_date = (old.get("latest") or {}).get("date", "")
    if old_date and record["date"] < old_date:
        raise SystemExit(f"Refusing to replace newer stored rate {old_date} with older source date {record['date']}")
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
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    DATA.write_text(serialized, encoding="utf-8")
    LIVE_DATA.write_text(serialized, encoding="utf-8")
    page = PAGE.read_text(encoding="utf-8")
    page = update_seo_snapshot(page, record)
    PAGE.write_text(update_schema_date(page, record["date"]), encoding="utf-8")
    update_cluster_snapshots(record)
    print(json.dumps(record, ensure_ascii=False))

if __name__ == "__main__":
    main()
