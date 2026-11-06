# NEPSE Share Market — backend and dashboard

Route: https://laxmannepal.com.np/sharemarket/

## Data pipeline

`.github/workflows/update-nepse-data.yml` runs at 16:00 Nepal time, Monday–Friday, and can also be started manually from GitHub Actions. It clones the public, MIT-licensed `binayabaral/nepal-market-data` dataset, converts its source CSVs to compact JSON, validates the generated files and commits changes. The workflow also runs after changes to the builder so the first historical archive is seeded automatically.

The archive window begins **2026-01-01** and includes all source rows available through the latest published session. A missed source update does not create fake rows: dates remain source-published trading dates and weekends/holidays stay absent.

### JSON endpoints

- `data/manifest.json` — coverage, freshness, source and counts.
- `data/symbols.json` — instrument master.
- `data/latest-prices.json` — latest available row per symbol.
- `data/market-summary.json` — latest-session breadth, turnover, movers and sector aggregation.
- `data/index-history.json` — NEPSE index history.
- `data/stocks/{SYMBOL}.json` — dated OHLC, percentage change, volume and turnover for each security.

## Source and limitations

Initial backend source: [Nepal Market Data (MIT)](https://github.com/binayabaral/nepal-market-data), whose NEPSE price history is sourced primarily from [ShareSansar](https://www.sharesansar.com/) and historical backfill sources listed in its README. This is an unofficial community dataset, not an official NEPSE feed. A later source-adapter stage should add independently reconciled NEPSE official API data and other sources; do not merge conflicting values without source provenance and a reconciliation rule.

Prices are **unadjusted**. Bonus shares, rights issues, splits, mergers and other corporate actions can make raw returns misleading. The current first release does not yet claim fundamentals, broker flows, live quotes, order-book depth, IPO calendars, dividend records or official notices are covered.

## Dashboard

Open-source Chart.js is used for charts (MIT). The dashboard includes index trend, breadth, turnover, gainers/losers, sector performance, instrument filters, stock history, SMA/RSI snapshots, browser-local watchlists, portfolio tracking, price alerts and JSON downloads. Personal lists and holdings stay in the visitor's browser; no account or server database is used.

## Run the builder locally

```bash
git clone --depth 1 https://github.com/binayabaral/nepal-market-data.git /tmp/nepal-market-data
python sharemarket/scripts/build_data.py --source-dir /tmp/nepal-market-data
```

The output is written to `sharemarket/data/`. The GitHub Actions workflow validates JSON before committing it.
