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

## Dashboard and user workspace

The page uses the same shared Laxman Nepal header, navigation, search, footer and design tokens as the main website. It is not a separately branded microsite.

The dashboard starts with a prominent global stock search. Search by ticker or company name to jump directly to that security's research chart. The screener also supports symbol/company search, sector and instrument filters, and pagination.

Open-source Chart.js (MIT) powers the interactive index and stock charts. The workspace includes index performance ranges, market breadth, turnover, gainers/losers, sector performance, stock history, SMA/RSI snapshots, browser-local watchlists, a portfolio tracker, price alerts and JSON downloads. Cards and sections animate on entry; chart transitions and hover/focus states are enabled while respecting reduced-motion preferences.

Personal lists, holdings and alerts stay in the visitor's browser; there is no account system or server-side personal-data database. Alerts are evaluated when the page is opened, not continuously in the background.

## Run the builder locally

```bash
git clone --depth 1 https://github.com/binayabaral/nepal-market-data.git /tmp/nepal-market-data
python sharemarket/scripts/build_data.py --source-dir /tmp/nepal-market-data
```

The output is written to `sharemarket/data/`. The GitHub Actions workflow validates JSON before committing it.


## Advanced research tools (static edition)

The dashboard also includes a local quantitative research workspace:

- **Advanced screener:** minimum/maximum latest close, minimum volume and minimum daily percentage change, alongside symbol, sector, instrument and listing-status filters.
- **Relative performance comparison:** compare up to three symbols over their common available trading dates, normalized to 0% at the start.
- **Technical indicators:** EMA 12/26, MACD and signal, 20-session Bollinger bands, ATR 14 and an approximate annualized 60-session volatility estimate, in addition to SMA and RSI.
- **SMA crossover backtest:** configurable fast/slow moving averages and per-side transaction fee, with strategy return, buy-and-hold comparison, maximum drawdown, round-trip count and win rate.

Backtest assumptions and limitations: signals use information through the prior session and trades execute at the next available session close. The simulation is long-only, all-in/all-out, and uses close prices. It does not model slippage, liquidity, taxes, brokerage minimums, partial fills, dividends, rights/bonus shares, suspensions or corporate-action-adjusted prices. Historical results are not forecasts and can be misleading on unadjusted prices.

### Deliberately not presented as available data

The current archive does not contain verified live quotes, market depth, floorsheet/broker transactions, issuer financial statements, valuation ratios, IPO calendars, dividends or corporate-action histories. These modules must not display fabricated metrics. They require additional source adapters, date-level provenance, field validation and reconciliation before integration. GitHub Pages can host the resulting public JSON, but persistent personal accounts, secure private API keys, server-side portfolios and continuous push notifications require a separate backend.
