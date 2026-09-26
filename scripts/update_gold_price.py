#!/usr/bin/env python3
import json, re, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from html import unescape

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "gold-nepal.json"
HTML_PATH = ROOT / "gold-price-in-nepal-today" / "index.html"
SOURCE_URL = "https://www.ashesh.com.np/gold/widget.php?api=872076p237&header_color=0077e5"
SOURCE_NAME = "FENEGOSIDA published rate feed via Ashesh widget"

def fetch():
    req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "LaxmanNepal-GoldRate-Updater/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")

def clean(s):
    return re.sub(r"\s+", " ", unescape(s)).strip()

def parse(html):
    text = clean(re.sub(r"<[^>]+>", " ", html))
    date_m = re.search(r"(\d{1,2})-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-(\d{4})", text, re.I)
    if not date_m:
        raise RuntimeError("Could not find source date")
    date = datetime.strptime(date_m.group(0), "%d-%b-%Y").date().isoformat()
    patterns = {
        "fine_gold_tola": r"Fine gold 9999\s+(\d[\d,]*)\s+Tola",
        "tejabi_gold_tola": r"Gold Tajabi\s+(\d[\d,]*)\s+Tola",
        "silver_tola": r"Silver\s+(\d[\d,]*)\s+Tola",
    }
    values = {}
    for key, pat in patterns.items():
        m = re.search(pat, text, re.I)
        if not m:
            raise RuntimeError(f"Could not find {key}")
        values[key] = int(m.group(1).replace(",", ""))
    return date, values

def update_snapshot(html, latest):
    iso = latest["date"]
    pretty = datetime.fromisoformat(iso).strftime("%d %B %Y")
    html = html.replace('"dateModified":"2026-09-23"', f'"dateModified":"{iso}"')
    html = re.sub(
        r'Latest verified market figures for <time datetime="[^"]+">[^<]+</time>',
        f'Latest verified market figures for <time datetime="{iso}">{pretty}</time>',
        html, count=1)
    html = re.sub(r'(<span>Fine Gold \(9999\) per tola</span><b>)Rs [0-9,]+(</b>)',
                  rf'\g<1>Rs {latest["fine_gold_tola"]:,}\g<2>', html, count=1)
    html = re.sub(r'(<span>Tejabi Gold per tola</span><b>)Rs [0-9,]+(</b>)',
                  rf'\g<1>Rs {latest["tejabi_gold_tola"]:,}\g<2>', html, count=1)
    html = re.sub(r'(<span>Silver per tola</span><b>)Rs [0-9,]+(</b>)',
                  rf'\g<1>Rs {latest["silver_tola"]:,}\g<2>', html, count=1)
    return html

def main():
    html_source = fetch()
    date, values = parse(html_source)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    old = data.get("latest", {})
    old_date = old.get("date", "")

    # Never replace a newer verified record with an older/stale source response.
    if old_date and date < old_date:
        data["last_attempted_at"] = now
        data["status"] = "stale_source"
        data["errors"] = [f"Source returned {date}, older than stored verified record {old_date}."]
        DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(data["errors"][0])
        return

    if old.get("date") == date and all(int(old.get(k, -1)) == v for k, v in values.items()):
        print(f"No new gold rate. Source is still {date}.")
        return

    record = {
        "date": date, "updated_at": now, **values,
        "source": SOURCE_NAME, "source_url": SOURCE_URL, "unit": "NPR per tola"
    }
    history = [x for x in data.get("history", []) if x.get("date") != date]
    history.append(record)
    history = sorted(history, key=lambda x: x.get("date", ""))[-60:]
    data.update({
        "status": "verified", "last_attempted_at": now, "latest": record,
        "history": history,
        "conversion": {"tola_grams": 11.6638125, "aana_per_tola": 16, "lal_per_tola": 100},
        "errors": []
    })
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    page = HTML_PATH.read_text(encoding="utf-8")
    page = update_snapshot(page, record).replace("FENEGOSIDA published rate feed", SOURCE_NAME)
    HTML_PATH.write_text(page, encoding="utf-8")
    print(f"Updated gold data to {date}: {values}")

if __name__ == "__main__":
    main()
