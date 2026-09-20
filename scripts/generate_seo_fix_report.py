#!/usr/bin/env python3
"""Generate a reviewable SEO fix report from the analytics snapshot."""
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'analytics/data.json'; OUT=ROOT/'analytics/seo-fix-report.md'
def clean(s): return re.sub(r'\\s+',' ',str(s or '')).strip()
def short(s,n):
    s=clean(s); return s if len(s)<=n else s[:n-1].rstrip(' ,:;-')+'…'
def main():
    if not DATA.exists(): raise SystemExit('analytics/data.json not found')
    d=json.loads(DATA.read_text(encoding='utf-8')); pages=d.get('seoHealth',{}).get('pages',[])
    gp={clean(x.get('keys',[''])[0]):x for x in d.get('searchConsole',{}).get('pages',[])}; grouped={}
    for x in d.get('searchConsole',{}).get('pageQueries',[]): grouped.setdefault(clean(x.get('keys',['',''])[0]),[]).append(x)
    rows=[]
    for a in pages:
        path=a.get('path','/'); qs=sorted(grouped.get(path,[]),key=lambda x:float(x.get('impressions',0)),reverse=True)
        q=clean(qs[0].get('keys',['',''])[1] if qs else '') or clean(a.get('h1Text')) or clean(a.get('title')) or path.strip('/').replace('-',' ')
        rows.append((a,qs,short(q+' | Laxman Nepal',60),short('Learn about '+q+' with practical steps, useful tips and clear guidance from Laxman Nepal.',155),short(q or 'Laxman Nepal',70),gp.get(path,{})))
    rows.sort(key=lambda x:(x[0].get('score',100),-float(x[5].get('impressions',0))))
    md=['# SEO Fix Report','',f"Generated from the latest analytics snapshot: {d.get('generatedAt','unknown')}.",'','This report is review-only. It does not modify published pages. Recommendations use page metadata and Search Console query signals.','']
    md.append('## Priority pages')
    for a,qs,title,desc,h1,g in rows:
        issues=a.get('issues',[])
        if not issues and float(g.get('impressions',0))<50: continue
        md += [f"### {a.get('path','/')} — SEO score {a.get('score',0)}/100",f"- Issues: {', '.join(issues) if issues else 'No structural issue detected'}",f"- Search: {int(float(g.get('clicks',0)))} clicks · {int(float(g.get('impressions',0)))} impressions · {float(g.get('ctr',0))*100:.1f}% CTR · position {float(g.get('position',0)):.1f}",f"- Current title: {clean(a.get('title')) or 'Missing'}",f"- Recommended title: {title}",f"- Current description: {clean(a.get('description')) or 'Missing'}",f"- Recommended description: {desc}",f"- Recommended H1: {h1}",'- Top queries: '+(', '.join(clean(x.get('keys',['',''])[1]) for x in qs[:5]) or 'No page-query rows'),'']
    md += ['## Safety checklist','','Before applying a recommendation:','1. Confirm the page intent matches the query.','2. Keep titles/descriptions truthful and specific to the page.','3. Keep one primary H1 and avoid keyword stuffing.','4. Recheck canonical/noindex settings after deployment.','']
    OUT.write_text('\n'.join(md),encoding='utf-8'); print(f'Wrote {OUT}')
if __name__=='__main__': main()
