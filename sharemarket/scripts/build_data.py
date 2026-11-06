#!/usr/bin/env python3
"""Build a dated, auditable NEPSE JSON archive from the MIT-licensed Nepal Market Data CSVs.

The upstream dataset is a community archive sourced primarily from ShareSansar. It is not an
official NEPSE feed. Dates are source-published dates; missing sessions are never fabricated.
"""
from __future__ import annotations
import argparse, csv, json, math
from collections import defaultdict
from datetime import datetime, date, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

START = date(2026, 1, 1)
NPT = ZoneInfo("Asia/Kathmandu")
SOURCE = "https://github.com/binayabaral/nepal-market-data"
SOURCE_DATA = "https://github.com/binayabaral/nepal-market-data/tree/main/data/nepse"

def number(value):
    if value is None or str(value).strip() == "":
        return None
    try:
        n = float(str(value).replace(",", "").strip())
        return n if math.isfinite(n) else None
    except (TypeError, ValueError):
        return None

def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def rows_for(path):
    out = []
    for raw in read_csv(path):
        try:
            d = date.fromisoformat(raw.get("published_date", "")[:10])
        except ValueError:
            continue
        if d < START or d > date.today():
            continue
        row = {
            "date": d.isoformat(),
            "open": number(raw.get("open")),
            "high": number(raw.get("high")),
            "low": number(raw.get("low")),
            "close": number(raw.get("close")),
            "change_pct": number(raw.get("per_change")),
            "volume": number(raw.get("traded_quantity")),
            "turnover": number(raw.get("traded_amount")),
        }
        if row["close"] is not None:
            out.append(row)
    out.sort(key=lambda x: x["date"])
    # De-duplicate by source date, keeping the last source row.
    return list({r["date"]: r for r in out}.values())

def dump(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n", encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", required=True, help="Path to the cloned upstream repository")
    ap.add_argument("--output-dir", default="sharemarket/data")
    args = ap.parse_args()
    root, out = Path(args.source_dir), Path(args.output_dir)
    raw_dir = root / "data" / "nepse"
    ref_file = root / "data" / "reference" / "nepse-symbols.csv"
    if not raw_dir.is_dir() or not ref_file.is_file():
        raise SystemExit("Upstream dataset layout not found; refusing to publish empty data.")

    refs = read_csv(ref_file)
    symbols = []
    latest_prices = []
    for r in refs:
        symbol = (r.get("symbol") or "").strip()
        if not symbol:
            continue
        filename = symbol.replace("/", "-") + ".csv"
        source_file = raw_dir / filename
        if not source_file.is_file():
            continue
        history = rows_for(source_file)
        if not history:
            continue
        meta = {
            "symbol": symbol, "name": (r.get("name") or symbol).strip(),
            "source_category": r.get("source_category") or "",
            "instrument_type": r.get("instrument_type") or "unknown",
            "sector": r.get("sector") or "Unclassified",
            "status": r.get("status") or "unknown",
            "first_date": history[0]["date"], "last_date": history[-1]["date"],
            "observations": len(history),
        }
        symbols.append(meta)
        latest_prices.append({"symbol": symbol, "name": meta["name"], "instrument_type": meta["instrument_type"], "sector": meta["sector"], "status": meta["status"], **history[-1]})
        dump(out / "stocks" / f"{symbol.replace('/', '-')}.json", {
            "symbol": symbol, "name": meta["name"], "instrument_type": meta["instrument_type"],
            "sector": meta["sector"], "status": meta["status"], "source": SOURCE,
            "data_start": START.isoformat(), "history": history
        })

    symbols.sort(key=lambda x: x["symbol"])
    if not symbols:
        raise SystemExit("No stock history found from 2026-01-01; refusing to overwrite the archive.")
    dump(out / "symbols.json", {"source": SOURCE, "data_start": START.isoformat(), "symbols": symbols})
    dump(out / "latest-prices.json", {"source": SOURCE, "as_of_build": datetime.now(NPT).date().isoformat(), "prices": latest_prices})

    index_path = raw_dir / "NEPSE_INDEX.csv"
    index_history = rows_for(index_path) if index_path.is_file() else []
    dump(out / "index-history.json", {"symbol":"NEPSE", "name":"NEPSE Index", "source":SOURCE,
        "data_start":START.isoformat(), "history":index_history})

    ordinary = [s for s in symbols if s["instrument_type"] == "ordinary" and s["status"] == "listed"]
    latest_by_symbol = []
    for s in ordinary:
        hist_path = out / "stocks" / f'{s["symbol"].replace("/", "-")}.json'
        data = json.loads(hist_path.read_text(encoding="utf-8"))
        h = data["history"]
        if h:
            latest_by_symbol.append({"symbol":s["symbol"],"name":s["name"],"sector":s["sector"],
                "close":h[-1]["close"],"change_pct":h[-1]["change_pct"],"volume":h[-1]["volume"],
                "turnover":h[-1]["turnover"],"date":h[-1]["date"]})
    latest_dates = [x["date"] for x in latest_by_symbol]
    as_of = max(latest_dates) if latest_dates else (index_history[-1]["date"] if index_history else None)
    active = [x for x in latest_by_symbol if x["date"] == as_of and x["change_pct"] is not None]
    gainers = sorted([x for x in active if x["change_pct"] > 0], key=lambda x:x["change_pct"], reverse=True)
    losers = sorted([x for x in active if x["change_pct"] < 0], key=lambda x:x["change_pct"])
    unchanged = [x for x in active if x["change_pct"] == 0]
    total_turnover = sum((x["turnover"] or 0) for x in active)
    sector_map = defaultdict(list)
    for x in active:
        sector_map[x["sector"]].append(x)
    sectors = []
    for sector, items in sector_map.items():
        vals = [x["change_pct"] for x in items if x["change_pct"] is not None]
        sectors.append({"sector":sector,"count":len(items),"average_change_pct":sum(vals)/len(vals) if vals else None,
                        "turnover":sum((x["turnover"] or 0) for x in items)})
    sectors.sort(key=lambda x:x["average_change_pct"] if x["average_change_pct"] is not None else -999, reverse=True)

    fetched = datetime.now(timezone.utc).isoformat(timespec="seconds")
    dump(out / "market-summary.json", {
        "as_of":as_of,"fetched_at":fetched,"source":SOURCE,
        "market":{"advances":len(gainers),"declines":len(losers),"unchanged":len(unchanged),
                  "turnover":total_turnover,"traded_symbols":len(active)},
        "top_gainers":gainers[:10],"top_losers":losers[:10],
        "sector_performance":sectors,
        "index_latest":index_history[-1] if index_history else None,
        "index_previous":index_history[-2] if len(index_history)>1 else None
    })
    dump(out / "manifest.json", {
        "name":"Laxman Nepal NEPSE Open Data","market":"Nepal Stock Exchange",
        "data_start":START.isoformat(),"data_end":as_of,"fetched_at":fetched,
        "source":SOURCE,"source_data":SOURCE_DATA,"license":"MIT (upstream dataset)",
        "symbol_count":len(symbols),"ordinary_listed_count":len(ordinary),
        "index_observations":len(index_history),"stock_observations":sum(s["observations"] for s in symbols),
        "date_semantics":"Source-published trading dates. No weekend/holiday rows are invented or forward-filled.",
        "price_semantics":"Unadjusted traded prices; corporate actions can create discontinuities."
    })
    print(f"Built {len(symbols)} symbols, {sum(s['observations'] for s in symbols)} stock observations; index rows={len(index_history)}; as_of={as_of}")

if __name__ == "__main__":
    main()
