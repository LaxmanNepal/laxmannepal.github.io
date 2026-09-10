import json,re
from pathlib import Path
from datetime import datetime,timezone
p=Path('data/youtube.json'); d=json.loads(p.read_text(encoding='utf-8'))
raw=[]
for k in ('videos','popularVideos','topVideos','recentVideos','latestVideos','latestUploads'):
    if isinstance(d.get(k),list): raw += d[k]
seen={}
for v in raw:
    i=v.get('id') or v.get('videoId')
    if i: seen[i]=v
videos=list(seen.values())
channel_avg=sum(float(v.get('views') or v.get('statistics',{}).get('viewCount') or 0) for v in videos)/max(len(videos),1)
for v in videos:
    views=float(v.get('views') or v.get('statistics',{}).get('viewCount') or 0); likes=float(v.get('likes') or v.get('statistics',{}).get('likeCount') or 0); comments=float(v.get('comments') or v.get('statistics',{}).get('commentCount') or 0)
    pub=v.get('publishedAt') or v.get('publishDate') or ''
    try: age=max(1,(datetime.now(timezone.utc)-datetime.fromisoformat(pub.replace('Z','+00:00'))).days)
    except: age=365
    engagement=(likes+comments)/max(views,1)*100; v['_i']={'viewsPerDay':round(views/age,2),'engagementRate':round(engagement,3),'score':round(min(100,50*min(views/max(channel_avg,1),2)/2+30*min(engagement/5,1)+20*min((views/age)/max(channel_avg,1),2)/2),1)}
def avg(k): return round(sum(v['_i'][k] for v in videos)/max(len(videos),1),2)
ranked=sorted(videos,key=lambda v:v['_i']['score'],reverse=True)
words=re.findall(r'[A-Za-z0-9]+',' '.join(str(v.get('title','')) for v in videos).lower()); stop={'the','and','for','with','this','that','how','you','your','from','into','are','was','what','best','new','video','in','to','of','on'}
topics=[]
for w in dict.fromkeys(words):
    if w in stop or len(w)<3: continue
    g=[v for v in videos if w in str(v.get('title','')).lower()]
    if len(g)>=2: topics.append({'topic':w,'videos':len(g),'avgScore':round(sum(v['_i']['score'] for v in g)/len(g),1),'avgViewsPerDay':round(sum(v['_i']['viewsPerDay'] for v in g)/len(g),1)})
topics=sorted(topics,key=lambda x:(x['avgScore'],x['avgViewsPerDay']),reverse=True)[:10]
d['contentIntelligence']={'version':1,'updatedAt':datetime.now(timezone.utc).isoformat(),'videosAnalyzed':len(videos),'channelAverages':{'viewsPerDay':avg('viewsPerDay'),'engagementRate':avg('engagementRate'),'performanceScore':avg('score')},'topVideos':[{'id':v.get('id') or v.get('videoId'),'title':v.get('title'),'thumbnail':v.get('thumbnail'),'views':v.get('views'),'likes':v.get('likes'),'comments':v.get('comments'),'publishedAt':v.get('publishedAt'),'intelligence':v['_i']} for v in ranked[:20]],'topics':topics,'opportunities':[{'idea':f"{t['topic'].title()} for Nepali Creators",'opportunityScore':min(99,round(t['avgScore']+10,1)),'reason':f"{t['videos']} related videos average {t['avgScore']}/100"} for t in topics[:5]]}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8'); print(f'Analyzed {len(videos)} videos')
