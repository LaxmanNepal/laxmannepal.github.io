#!/usr/bin/env python3
"""Build the jobs dataset from explicitly approved sources.

This first aggregator pass uses only the source registry as a manifest.
A connector can be enabled per source when its public API/RSS contract is
confirmed. It never invents vacancies and never treats a search result as
an application URL.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
sources=json.loads((ROOT/"jobs/sources.json").read_text(encoding="utf-8"))
out=ROOT/"jobs/aggregator-status.json"

status={
 "updatedAt":datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
 "mode":"approved-source-manifest",
 "sources":[{**s,"enabled":False} for s in sources],
 "message":"Connect each source through an allowed API/RSS/public feed before automatic ingestion."
}
out.write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("Source registry checked:",len(sources))
