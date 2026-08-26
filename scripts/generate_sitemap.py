import json, os
from xml.sax.saxutils import escape
BASE='https://apps.laxmannepal.com.np'
urls=[('/',1.0,'daily'),('/youtube/',0.95,'daily'),('/apps/',0.9,'weekly'),('/about/',0.7,'monthly')]
try:
    with open('data/youtube.json',encoding='utf-8') as f: d=json.load(f)
except Exception: d={}
seen=set(u[0] for u in urls)
for v in (d.get('popularVideos') or [])+(d.get('recentVideos') or [])+(d.get('latestVideos') or []):
    vid=v.get('id') or v.get('videoId')
    if vid and vid not in seen:
        urls.append((f'/youtube/video/?v={vid}',0.65,'monthly')); seen.add(vid)
lines=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for path,priority,freq in urls:
    lines += [f'  <url><loc>{escape(BASE+path)}</loc><changefreq>{freq}</changefreq><priority>{priority}</priority></url>']
lines.append('</urlset>')
os.makedirs('.',exist_ok=True)
with open('sitemap.xml','w',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
print(f'Generated {len(urls)} URLs')
