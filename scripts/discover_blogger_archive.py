#!/usr/bin/env python3
"""Discover Blogger posts from sitemap/archives, then import exact URL paths."""
from __future__ import annotations
import html,json,re,shutil,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
BASE="https://www.laxmannepal.com.np"
OUT=ROOT
MANIFEST=ROOT/".blogger-migration.json"
NS={"sm":"http://www.sitemaps.org/schemas/sitemap/0.9"}

def fetch(url):
    req=Request(url,headers={"User-Agent":"LaxmanNepal-ArchiveImporter/2.0"})
    with urlopen(req,timeout=60) as r:return r.read()

def urls_from_xml(data):
    root=ET.fromstring(data)
    return [x.text for x in root.findall(".//sm:loc",NS) if x.text]

def discover():
    found=set()
    for endpoint in [BASE+"/sitemap.xml",BASE+"/atom.xml?redirect=false&start-index=1&max-results=500"]:
        try:
            data=fetch(endpoint)
            text=data.decode("utf-8","ignore")
            for u in re.findall(r'https?://(?:www\.)?laxmannepal\.com\.np/20\d\d/\d\d/[^\s<"\']+\.html',text):
                found.add(u)
            try:
                for u in urls_from_xml(data):
                    if re.search(r'/20\d\d/\d\d/.+\.html$',u): found.add(u)
            except Exception: pass
        except Exception as e: print("discover warning:",endpoint,e,file=sys.stderr)
    # Probe Blogger monthly archive feeds for every month from 2010 through current year.
    year=datetime.now().year
    for y in range(2010,year+1):
        for m in range(1,13):
            if y==year and m>datetime.now().month: continue
            feed=f"{BASE}/feeds/posts/default?alt=atom&start-index=1&max-results=500&published-min={y:04d}-{m:02d}-01T00:00:00Z&published-max={y+(m==12):04d}-{1 if m==12 else m+1:02d}-01T00:00:00Z"
            try:
                text=fetch(feed).decode("utf-8","ignore")
                for u in re.findall(r'<link[^>]+rel=["\']alternate["\'][^>]+href=["\']([^"\']+)',text):
                    if re.search(r'/20\d\d/\d\d/.+\.html$',u): found.add(html.unescape(u))
            except Exception: pass
    return sorted(found)

def post(u):
    data=fetch(u).decode("utf-8","ignore")
    title=re.search(r'<title[^>]*>(.*?)</title>',data,re.I|re.S)
    title=html.unescape(re.sub("<[^>]+>","",title.group(1)).strip()) if title else Path(urlparse(u).path).stem
    body=re.search(r'<body[^>]*>([\s\S]*?)</body>',data,re.I)
    content=body.group(1) if body else data
    pub=re.search(r'<meta[^>]+property=["\']article:published_time["\'][^>]+content=["\']([^"\']+)',data,re.I)
    path=urlparse(u).path
    return {"title":title,"published":pub.group(1) if pub else "","updated":pub.group(1) if pub else "","original_url":u,"path":path,"content":content}

def main():
    discovered=discover()
    print(f"Discovered {len(discovered)} historical Blogger URLs")
    old=json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    old_by={p.get("path"):p for p in old.get("posts",[])}
    posts=[]
    for u in discovered:
        path=urlparse(u).path
        if path in old_by:
            posts.append(old_by[path]); continue
        try:
            p=post(u); p["imported_url"]=BASE+p["path"]; p["type"]="blog"; p["tags"]=["blog","technology"]; 
            target=OUT/p["path"].lstrip("/")
            target.parent.mkdir(parents=True,exist_ok=True); target.write_text(p["content"],encoding="utf-8")
            p.pop("content",None); posts.append(p)
        except Exception as e: print("import warning:",u,e,file=sys.stderr)
    posts.sort(key=lambda x:x.get("published",""),reverse=True)
    MANIFEST.write_text(json.dumps({"source":"historical sitemap + monthly Blogger archive discovery","total_feed_entries":len(discovered),"imported_posts":len(posts),"generated_at":datetime.now(timezone.utc).isoformat(),"posts":posts},ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Archive migration now contains {len(posts)} posts")
if __name__=="__main__": main()
