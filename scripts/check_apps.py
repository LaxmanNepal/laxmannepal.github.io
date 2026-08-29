import json, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timezone
p=Path('data/apps.json'); d=json.loads(p.read_text(encoding='utf-8'))
for app in d.get('apps',[]):
    req=urllib.request.Request(app['url'],headers={'User-Agent':'LaxmanNepal-AppHealth/1.0'})
    try:
        with urllib.request.urlopen(req,timeout=12) as r:
            app['status']='online' if 200<=r.status<400 else 'degraded'; app['httpStatus']=r.status
    except urllib.error.HTTPError as e:
        app['status']='degraded' if e.code<500 else 'offline'; app['httpStatus']=e.code
    except Exception:
        app['status']='offline'; app['httpStatus']=None
    app['lastChecked']=datetime.now(timezone.utc).isoformat()
d['updatedAt']=datetime.now(timezone.utc).isoformat()
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Checked',len(d.get('apps',[])),'apps')
for a in d.get('apps',[]): print(a['name'],a['status'],a.get('httpStatus'))
