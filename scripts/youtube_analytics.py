import json, os, datetime, urllib.parse, urllib.request

CLIENT_ID=os.environ['YOUTUBE_CLIENT_ID']; CLIENT_SECRET=os.environ['YOUTUBE_CLIENT_SECRET']; REFRESH=os.environ['YOUTUBE_REFRESH_TOKEN']; API=os.environ.get('YOUTUBE_API_KEY','')

def post(url,data):
    req=urllib.request.Request(url,data=urllib.parse.urlencode(data).encode(),headers={'Content-Type':'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
def get(url,token=None):
    h={'Authorization':f'Bearer {token}'} if token else {}
    req=urllib.request.Request(url,headers=h)
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)

tok=post('https://oauth2.googleapis.com/token',{'client_id':CLIENT_ID,'client_secret':CLIENT_SECRET,'refresh_token':REFRESH,'grant_type':'refresh_token'})
access=tok['access_token']
end=datetime.date.today()-datetime.timedelta(days=1); start=end-datetime.timedelta(days=29)
base='https://youtubeanalytics.googleapis.com/v2/reports?'+urllib.parse.urlencode({'ids':'channel==MINE','startDate':start.isoformat(),'endDate':end.isoformat(),'metrics':'views,estimatedMinutesWatched,averageViewDuration,likes,comments,subscribersGained,subscribersLost','dimensions':'day','sort':'day'})
daily=get(base,access)
rows=daily.get('rows',[]); headers=[x['name'] for x in daily.get('columnHeaders',[])]
def rowdict(r):return dict(zip(headers,r))
D=[rowdict(r) for r in rows]
summary={k:sum(float(x.get(k,0)) for x in D) for k in ['views','estimatedMinutesWatched','likes','comments','subscribersGained','subscribersLost']}
summary['averageViewDuration']=sum(float(x.get('averageViewDuration',0))*float(x.get('views',0)) for x in D)/max(summary['views'],1)
public=get('https://www.googleapis.com/youtube/v3/channels?part=statistics&mine=true&key='+urllib.parse.quote(API),access)
stat=public['items'][0]['statistics']
try:stat['subscriberCount']=int(stat.get('subscriberCount',0))
except:pass
out={'subscriberCount':int(stat.get('subscriberCount',0)),'viewCount':int(stat.get('viewCount',0)),'videoCount':int(stat.get('videoCount',0)),'watchTimeText':f"{summary['estimatedMinutesWatched']/60:,.1f} hours (30d)",'analyticsStatus':'ok','lastUpdated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'period':{'start':start.isoformat(),'end':end.isoformat()},'summary':summary,'daily':D}
with open('data/youtube.json','w') as f:json.dump(out,f,indent=2)
print(json.dumps({'status':'ok','period':out['period'],'rows':len(D)}))
