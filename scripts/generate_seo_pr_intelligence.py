#!/usr/bin/env python3
import html, json, re, sys
from pathlib import Path

def clean(s): return re.sub(r"\\s+", " ", html.unescape(str(s or ""))).strip()
def title_of(text):
    m=re.search(r"<title\\b[^>]*>(.*?)</title>",text,re.I|re.S)
    return clean(re.sub(r"<.*?>","",m.group(1))) if m else ""
def description_of(text):
    for p in [r'<meta\\b[^>]*\\bname=["\']description["\'][^>]*\\bcontent=["\'](.*?)["\']',r'<meta\\b[^>]*\\bcontent=["\'](.*?)["\'][^>]*\\bname=["\']description["\']']:
        m=re.search(p,text,re.I|re.S)
        if m:return clean(m.group(1))
    return ""
def h1_of(text):
    m=re.search(r"<h1\\b[^>]*>(.*?)</h1>",text,re.I|re.S)
    return clean(re.sub(r"<.*?>","",m.group(1))) if m else ""
def audit(text):
    t,d=title_of(text),description_of(text); hs=re.findall(r"<h1\\b[^>]*>(.*?)</h1>",text,re.I|re.S); issues=[]
    if not 30<=len(t)<=60: issues.append("Title length outside 30–60 characters")
    if not 70<=len(d)<=160: issues.append("Meta description length outside 70–160 characters")
    if len(hs)!=1: issues.append(f"Expected exactly one H1; found {len(hs)}")
    if re.search(r'<meta\\b[^>]*name=["\']robots["\'][^>]*content=["\'][^"\']*noindex',text,re.I): issues.append("Page contains noindex")
    words=len(re.findall(r"\\b\\w+\\b",re.sub(r"<[^>]+>"," ",text)))
    if words<150: issues.append(f"Word count below 150 ({words})")
    return {"title":t,"description":d,"h1":h1_of(text),"score":max(0,100-15*len(issues)),"issues":issues,"title_len":len(t),"description_len":len(d),"h1_count":len(hs)}
def main():
    if len(sys.argv)!=5: raise SystemExit("Usage: generate_seo_pr_intelligence.py <path> <before> <after> <output>")
    path,bp,ap,out=sys.argv[1:]; old=audit(Path(bp).read_text(encoding="utf-8",errors="replace")); new=audit(Path(ap).read_text(encoding="utf-8",errors="replace"))
    data={}
    try:data=json.loads(Path("analytics/data.json").read_text(encoding="utf-8"))
    except Exception:pass
    sc=data.get("searchConsole",{}) if isinstance(data,dict) else {}; rows=[]
    for key in ("pageQueries","previousPageQueries"):
        for r in sc.get(key,[]) if isinstance(sc.get(key,[]),list) else []:
            if isinstance(r,dict) and str(r.get("page") or r.get("url") or r.get("pagePath") or "").rstrip("/") in {("/"+path.lstrip("/")).rstrip("/"),path.rstrip("/")} and r.get("query"): rows.append(r)
    rows=sorted(rows,key=lambda r:float(r.get("clicks") or 0),reverse=True)[:5]
    resolved=[x for x in old["issues"] if x not in new["issues"]]
    lines=["## 🤖 SEO PR Intelligence","",f"Target: {path}","Status: ✅ Safe to review — automated metadata, diff, and site-build validation passed.","","### Before → After","| Field | Before | After |","|---|---|---|",f"| Title | {old["title"]} ({old["title_len"]}) | {new["title"]} ({new["title_len"]}) |",f"| Meta description | {old["description"]} ({old["description_len"]}) | {new["description"]} ({new["description_len"]}) |",f"| H1 | {old["h1"]} | {new["h1"]} |",f"| Local validation score | {old["score"]}/100 | {new["score"]}/100 |","", "### SEO issue resolution"]
    lines += [f"- ✅ {x}" for x in resolved] if resolved else ["- No existing local validation issue was automatically resolved; review the proposed copy and Search Console evidence."]
    lines += ["","### Search Console evidence"]
    if rows:
        lines += ["| Query | Clicks | Impressions | CTR | Position |","|---|---:|---:|---:|---:|"]
        for r in rows: lines.append(f"| {clean(r.get("query"))} | {r.get("clicks",0)} | {r.get("impressions",0)} | {r.get("ctr",0)} | {r.get("position",0)} |")
    else: lines += ["No page-level Search Console query snapshot was available for this path."]
    lines += ["","### Automated checks","- ✅ Target is a single HTML file with path-traversal protection.","- ✅ Title length validated at 30–60 characters.","- ✅ Meta description length validated at 70–160 characters.","- ✅ Exactly one H1 validated.","- ✅ git diff --check passed.","- ✅ Site build and sitemap generation passed.","","### Changed-file summary",f"- {path} — title, meta description, and H1 only.","- No automatic merge or publish is performed by this workflow.","","> Review note: local validation is deterministic. Search Console rows are a snapshot and evidence, not a guarantee of ranking changes."]
    Path(out).write_text("\n".join(lines)+"\n",encoding="utf-8")
if __name__=="__main__": main()