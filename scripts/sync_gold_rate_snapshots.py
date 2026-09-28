#!/usr/bin/env python3
"""Synchronize crawlable gold/silver rate snapshots in the final Pages artifact."""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / ".pages"
DATA = ROOT / "data" / "gold-nepal.json"

def replace_marked(path: Path, start: str, end: str, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    if start not in text or end not in text:
        raise SystemExit(f"Missing snapshot markers in {path}")
    a = text.index(start)
    b = text.index(end) + len(end)
    path.write_text(text[:a] + block + text[b:], encoding="utf-8")

def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    latest = payload["latest"]
    conversion = float(payload["conversion"]["tola_grams"])
    date = latest["date"]
    display = datetime.strptime(date, "%Y-%m-%d").strftime("%d %B %Y")
    fine = f'{latest["fine_gold_tola"]:,}'
    tejabi = f'{latest["tejabi_gold_tola"]:,}'
    silver = f'{latest["silver_tola"]:,}'
    ten = f'{round(latest["silver_tola"] * 10 / conversion):,}'

    replace_marked(
        PAGES / "gold-price-history-nepal" / "index.html",
        "<!-- LATEST_GOLD_HISTORY_SNAPSHOT_START -->",
        "<!-- LATEST_GOLD_HISTORY_SNAPSHOT_END -->",
        f'''<!-- LATEST_GOLD_HISTORY_SNAPSHOT_START --><h2>Latest published gold rate in Nepal</h2><p><strong>Fine Gold: Rs {fine} per tola</strong> · <strong>Tejabi Gold: Rs {tejabi} per tola</strong> · <strong>Silver: Rs {silver} per tola</strong> ({display}).</p><p class="muted">This snapshot is updated automatically from the stored daily rate record.</p><!-- LATEST_GOLD_HISTORY_SNAPSHOT_END -->'''
    )

    replace_marked(
        PAGES / "silver-price-in-nepal-today" / "index.html",
        "<!-- SILVER_SEO_SNAPSHOT_START -->",
        "<!-- SILVER_SEO_SNAPSHOT_END -->",
        f'''<!-- SILVER_SEO_SNAPSHOT_START --><strong>Silver price in Nepal today — latest published rate</strong><p><time datetime="{date}">{display}</time>: <strong>Rs {silver} per tola</strong> and <strong>Rs {ten} per 10 grams</strong>.</p><p class="muted">This crawlable snapshot is updated automatically from the stored daily rate record.</p><!-- SILVER_SEO_SNAPSHOT_END -->'''
    )

    print(f"Synchronized gold/silver SEO snapshots to {date}: fine={fine}, tejabi={tejabi}, silver={silver}")

if __name__ == "__main__":
    main()
