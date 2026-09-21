#!/usr/bin/env python3
"""Upgrade all migrated Blogger articles to the current responsive site CSS."""
from __future__ import annotations
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/".blogger-migration.json"
CSS="/assets/css/blogger-modern.css"

def upgrade(path:Path)->bool:
    text=path.read_text(encoding="utf-8")
    changed=False
    if 'href="'+CSS+'"' not in text and "href='"+CSS+"'" not in text:
        if re.search(r"</head\s*>",text,re.I):
            text=re.sub(r"</head\s*>",f'<link rel="stylesheet" href="{CSS}">\n</head>',text,count=1,flags=re.I)
            changed=True
    if 'id="laxman-modern-article"' in text:
        text,n=re.subn(r'<style\s+id=["\']laxman-modern-article["\'][^>]*>.*?</style>\s*',"",text,count=1,flags=re.I|re.S)
        changed=changed or n>0
    if 'name="viewport"' not in text.lower():
        if re.search(r"</head\s*>",text,re.I):
            text=re.sub(r"</head\s*>",'<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n</head>',text,count=1,flags=re.I)
            changed=True
    text2,n=re.subn(r'<body(?![^>]*class=["\'][^"\']*blogger-modern-page)[^>]*>',
                    lambda m:m.group(0)[:-1]+' class="blogger-modern-page">',text,count=1,flags=re.I)
    if n: changed=True;text=text2
    if changed:path.write_text(text,encoding="utf-8")
    return changed

def main():
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    changed=0; total=0
    for meta in data.get("posts",[]):
        rel=str(meta.get("path","")).lstrip("/")
        if not rel or not rel.startswith(("2024/","2025/","2026/")): continue
        p=ROOT/rel
        if p.is_file():
            total+=1
            if upgrade(p): changed+=1
    print(f"Responsive Blogger CSS: upgraded {changed}/{total} migrated 2024-2026 posts.")

if __name__=="__main__": main()
