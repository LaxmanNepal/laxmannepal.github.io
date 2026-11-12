#!/usr/bin/env python3
"""Audit public All Sites Link URLs; reports observations, never edits source data."""
import concurrent.futures
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DATA = Path("allsiteslink/osint-links.json")
OUT = Path("audit-output")
TIMEOUT = 12
WORKERS = 16
UA = "LaxmanNepal-AllSitesLink-LinkAudit/1.0 (+https://laxmannepal.com.np/allsiteslink/)"

def check(item):
    url = item["url"]
    base = {"category": item["category"], "title": item["title"], "url": url}
    headers = {"User-Agent": UA}
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                return {**base, "status": response.status, "result": "reachable", "final_url": response.geturl(), "method": method, "checked_at": datetime.now(timezone.utc).isoformat()}
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in (403, 405, 501):
                continue
            return {**base, "status": exc.code, "result": "http_error", "final_url": exc.geturl(), "method": method, "checked_at": datetime.now(timezone.utc).isoformat()}
        except Exception as exc:
            if method == "HEAD":
                continue
            return {**base, "status": None, "result": "connection_error", "error": str(exc)[:240], "method": method, "checked_at": datetime.now(timezone.utc).isoformat()}
    return {**base, "status": None, "result": "unknown", "method": "GET", "checked_at": datetime.now(timezone.utc).isoformat()}

def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    items = [{"category": c["name"], **x} for c in data["categories"] for x in c["items"]]
    OUT.mkdir(exist_ok=True)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for index, result in enumerate(pool.map(check, items), 1):
            results.append(result)
            if index % 100 == 0:
                print(f"Checked {index}/{len(items)}", flush=True)
    results.sort(key=lambda x: (x["result"] == "reachable", x["category"], x["title"]))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = OUT / f"link-audit-{stamp}.json"
    csv_path = OUT / f"link-audit-{stamp}.csv"
    json_path.write_text(json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(), "source_count": len(items), "results": results}, indent=2, ensure_ascii=False), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=sorted({k for row in results for k in row}))
        writer.writeheader()
        writer.writerows(results)
    counts = {}
    for row in results:
        counts[row["result"]] = counts.get(row["result"], 0) + 1
    summary = {"total": len(results), **counts}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Reports: {json_path} and {csv_path}")

if __name__ == "__main__":
    main()
