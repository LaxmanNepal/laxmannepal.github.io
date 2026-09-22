#!/usr/bin/env python3
"""Collect fresh technology-news candidates for editorial review.

RSS headlines/snippets are research leads only. This script deliberately does
not turn feeds into publishable articles. Final pages must be independently
written, fact-checked, original, useful, and reviewed before publication.
"""
from __future__ import annotations
import html, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/"tech-news"/"_queue"
UA="Mozilla/5.0 (compatible; LaxmanNepalTechResearch/2.0)"
QUERIES=[
    "smartphone OR iPhone OR Xiaomi OR Samsung technology",
    "artificial intelligence AI technology",
    "Qualcomm OR MediaTek OR chip technology",
    "Google OR Microsoft OR Apple technology",
    "gadgets OR wearable OR laptop technology",
]
def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=20) as r: return r.read()
def clean(s):
    return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",s or ""))).strip()
def rss(q):
    url="https://news.google.com/rss/search?"+urllib.parse.urlencode({"q":q,"hl":"en-US","gl":"US","ceid":"US:en"})
    root=ET.fromstring(get(url)); out=[]
    for item in root.findall(".//item"):
        title=clean(item.findtext("title")); link=item.findtext("link") or ""
        desc=clean(item.findtext("description")); date=item.findtext("pubDate") or ""
        if title and link: out.append((title,link,desc,date))
    return out
def main():
    today=datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stories=[]; seen=set()
    for q in QUERIES:
        try: items=rss(q)
        except Exception as e: print("RSS failed:",q,e); continue
        for title,link,desc,date in items:
            key=re.sub(r"[^a-z0-9]","",title.lower())
            if not key or key in seen: continue
            seen.add(key); stories.append((title,link,desc,date))
            if len(stories)>=5: break
        if len(stories)>=5: break
    if len(stories)<5: raise SystemExit(f"Only {len(stories)} candidates found; refusing to create a five-story queue.")
    QUEUE.mkdir(parents=True,exist_ok=True)
    lines=[f"# Tech News Editorial Queue — {today}","","> Research leads only — not publishable articles. Verify facts independently, write original English copy, add useful context, use an original/licensed image, and review before publication.",""]
    for i,(title,link,desc,date) in enumerate(stories,1):
        host=urllib.parse.urlparse(link).netloc.replace("www.","")
        lines += [f"## {i}. {title}",f"- Source: {link}",f"- Publisher: {host}",f"- Feed date: {date}",f"- Research summary: {desc[:500]}","- Review: confirm primary source; separate facts from claims/rumors; add original context; check Nepal relevance; proofread.",""]
    (QUEUE/f"{today}.md").write_text("\n".join(lines),encoding="utf-8")
    print(f"Created editorial queue with {len(stories)} candidates.")
if __name__=="__main__": main()
