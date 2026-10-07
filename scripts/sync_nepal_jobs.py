#!/usr/bin/env python3
from __future__ import annotations
import json, re, urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PORTAL=ROOT/"nepal-jobs"
URL="https://raw.githubusercontent.com/LaxmanNepal/nepal-jobs/main/jobs.json"

def main():
    req=urllib.request.Request(URL,headers={"User-Agent":"LaxmanNepal-JobsPortal/1.0"})
    with urllib.request.urlopen(req,timeout=30) as r:
        records=json.loads(r.read().decode("utf-8"))
    today=date.today().isoformat(); out=[]; seen=set()
    for j in records if isinstance(records,list) else []:
        deadline=str(j.get("deadline","")).strip()
        title=str(j.get("title","")).strip(); org=str(j.get("organization","")).strip()
        if deadline and deadline<today: continue
        if re.search(r"\b(bid request|call for quotation|call for bid|request for quotation|procurement notice|tender)\b",title,re.I): continue
        key=(title.lower(),org.lower(),deadline)
        if not title or key in seen: continue
        seen.add(key); out.append(j)
    out.sort(key=lambda x:(str(x.get("posted","")),str(x.get("deadline",""))),reverse=True)
    (PORTAL/"jobs.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (PORTAL/"jobs-data.js").write_text("window.NEPAL_JOBS_DATA="+json.dumps(out,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    html=(PORTAL/"index.html").read_text(encoding="utf-8")
    payload=json.dumps(out,ensure_ascii=False,separators=(",",":"))
    html=re.sub(r"<script>window\.NEPAL_JOBS_DATA=.*?</script><script src=\"\./jobs\.js\"></script>","<script>window.NEPAL_JOBS_DATA="+payload+";</script><script src=\"./jobs.js\"></script>",html,flags=re.S)
    html=re.sub(r'<meta name="jobs-deploy-check" content="[^"]*">',f'<meta name="jobs-deploy-check" content="{datetime.now(timezone.utc).strftime("%Y-%m-%d")}">',html)
    (PORTAL/"index.html").write_text(html,encoding="utf-8")
    print(f"Published {len(out)} active jobs")

if __name__=="__main__": main()
