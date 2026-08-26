import datetime,json,os
from pathlib import Path
src=Path('data/youtube.json'); hist=Path('data/youtube-history.json')
if not src.exists(): raise SystemExit('data/youtube.json not found')
d=json.loads(src.read_text(encoding='utf-8')); now=datetime.datetime.now(datetime.timezone.utc).isoformat()
entry={'timestamp':now,'subscribers':int(d.get('subscriberCount',0) or 0),'views':int(d.get('viewCount',0) or 0),'videos':int(d.get('videoCount',0) or 0),'summary':d.get('summary',{})}
items=[]
if hist.exists():
 try: items=json.loads(hist.read_text(encoding='utf-8'))
 except Exception: items=[]
if items and items[-1].get('subscribers')==entry['subscribers'] and items[-1].get('views')==entry['views'] and items[-1].get('videos')==entry['videos']:
 items[-1]=entry
else: items.append(entry)
# Keep one observation per day plus today's latest observation.
byday={x.get('timestamp','')[:10]:x for x in items if x.get('timestamp')}
byday[entry['timestamp'][:10]]=entry
items=sorted(byday.values(),key=lambda x:x['timestamp'])[-366:]
hist.write_text(json.dumps({'version':1,'updatedAt':now,'points':items},indent=2),encoding='utf-8')
print(f'History points: {len(items)}')
