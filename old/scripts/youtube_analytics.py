import datetime, json, os, urllib.error, urllib.parse, urllib.request

CLIENT_ID=os.environ["YOUTUBE_CLIENT_ID"].strip(); CLIENT_SECRET=os.environ["YOUTUBE_CLIENT_SECRET"].strip(); REFRESH=os.environ["YOUTUBE_REFRESH_TOKEN"].strip(); API=os.environ.get("YOUTUBE_API_KEY","").strip()
def req(url,data=None,token=None):
    if data is not None: body=urllib.parse.urlencode(data).encode(); r=urllib.request.Request(url,data=body,headers={"Content-Type":"application/x-www-form-urlencoded"},method="POST")
    else: r=urllib.request.Request(url,headers={"Authorization":f"Bearer {token}","Accept":"application/json"} if token else {"Accept":"application/json"})
    try:
        with urllib.request.urlopen(r,timeout=30) as x:return json.load(x)
    except urllib.error.HTTPError as e:
        raw=e.read().decode("utf-8","replace")
        try:d=json.loads(raw)
        except: d={}
        raise SystemExit(f"YouTube/OAuth error (HTTP {e.code}): {d.get('error','api_error')} — {d.get('error_description',d.get('message',raw[:300]))}")
tok=req("https://oauth2.googleapis.com/token",{"client_id":CLIENT_ID,"client_secret":CLIENT_SECRET,"refresh_token":REFRESH,"grant_type":"refresh_token"}); access=tok.get("access_token")
if not access: raise SystemExit("OAuth error: Google returned no access_token.")
end=datetime.date.today()-datetime.timedelta(days=1); start=end-datetime.timedelta(days=29)
q={"ids":"channel==MINE","startDate":start.isoformat(),"endDate":end.isoformat(),"metrics":"views,estimatedMinutesWatched,averageViewDuration,likes,comments,subscribersGained,subscribersLost","dimensions":"day","sort":"day"}
ana=req("https://youtubeanalytics.googleapis.com/v2/reports?"+urllib.parse.urlencode(q),token=access); rows=ana.get("rows",[]); heads=[x["name"] for x in ana.get("columnHeaders",[])]; daily=[dict(zip(heads,r)) for r in rows]
keys=["views","estimatedMinutesWatched","likes","comments","subscribersGained","subscribersLost"]; summary={k:sum(float(x.get(k,0) or 0) for x in daily) for k in keys}; summary["averageViewDuration"]=sum(float(x.get("averageViewDuration",0) or 0)*float(x.get("views",0) or 0) for x in daily)/max(summary["views"],1)
base={"part":"snippet,contentDetails,statistics","mine":"true"};
if API:base["key"]=API
ch=req("https://www.googleapis.com/youtube/v3/channels?"+urllib.parse.urlencode(base),token=access); item=ch.get("items",[{}])[0]; cs=item.get("statistics",{}); sn=item.get("snippet",{}); uploads=item.get("contentDetails",{}).get("relatedPlaylists",{}).get("uploads")
# Collect channel uploads, capped to keep Actions/API usage reasonable.
vids=[]
if uploads:
    pl={"part":"snippet","playlistId":uploads,"maxResults":50};
    if API:pl["key"]=API
    page=req("https://www.googleapis.com/youtube/v3/playlistItems?"+urllib.parse.urlencode(pl),token=access)
    vids=[x.get("contentDetails",{}).get("videoId") for x in page.get("items",[]) if x.get("contentDetails",{}).get("videoId")]
video_items=[]
for i in range(0,len(vids),50):
    vp={"part":"snippet,contentDetails,statistics","id":",".join(vids[i:i+50])};
    if API:vp["key"]=API
    video_items += req("https://www.googleapis.com/youtube/v3/videos?"+urllib.parse.urlencode(vp),token=access).get("items",[])
def dur(sec):
    import re;m=re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",sec or "");return (int(m.group(1) or 0)*3600+int(m.group(2) or 0)*60+int(m.group(3) or 0)) if m else 0
videos=[]
for v in video_items:
    s=v.get("statistics",{});snip=v.get("snippet",{}); seconds=dur(v.get("contentDetails",{}).get("duration")); views=int(s.get("viewCount",0) or 0); likes=int(s.get("likeCount",0) or 0); comments=int(s.get("commentCount",0) or 0); age=max((datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(snip.get("publishedAt").replace('Z','+00:00'))).total_seconds()/86400,1) if snip.get("publishedAt") else 1
    videos.append({"id":v.get("id"),"title":snip.get("title",""),"description":snip.get("description",""),"publishedAt":snip.get("publishedAt"),"thumbnail":snip.get("thumbnails",{}).get("high",snip.get("thumbnails",{}).get("medium",{})).get("url",""),"views":views,"likes":likes,"comments":comments,"durationSeconds":seconds,"isShort":seconds<=60 and seconds>0,"viewsPerDay":round(views/age,1),"engagementRate":round((likes+comments)/max(views,1)*100,2)})
videos.sort(key=lambda x:x["views"],reverse=True); avg=sum(x["views"] for x in videos)/max(len(videos),1); shorts=sum(x["isShort"] for x in videos); long=len(videos)-shorts
for v in videos:v["performanceScore"]=round(min(100,(v["views"]/max(avg,1))*55+v["engagementRate"]*12+min(v["viewsPerDay"]/max(avg/30,1),3)*11),1)
out={"channel":{"title":sn.get("title","Laxman Nepal"),"description":sn.get("description",""),"thumbnail":sn.get("thumbnails",{}).get("high",sn.get("thumbnails",{}).get("default",{})).get("url",""),"statistics":{"subscriberCount":int(cs.get("subscriberCount",0) or 0),"viewCount":int(cs.get("viewCount",0) or 0),"videoCount":int(cs.get("videoCount",0) or 0)}},"subscriberCount":int(cs.get("subscriberCount",0) or 0),"viewCount":int(cs.get("viewCount",0) or 0),"videoCount":int(cs.get("videoCount",0) or 0),"analyticsStatus":"ok","lastUpdated":datetime.datetime.now(datetime.timezone.utc).isoformat(),"period":{"start":start.isoformat(),"end":end.isoformat()},"summary":summary,"daily":daily,"videos":videos,"popularVideos":[x for x in videos if not x["isShort"]],"recentVideos":sorted(videos,key=lambda x:x.get("publishedAt") or "",reverse=True),"analysis":{"videosFetched":len(videos),"shortsCount":shorts,"longFormCount":long,"totalViewsFetched":sum(x["views"] for x in videos),"totalLikesFetched":sum(x["likes"] for x in videos),"totalCommentsFetched":sum(x["comments"] for x in videos),"averageEngagementRate":sum(x["engagementRate"] for x in videos)/max(len(videos),1),"averageViews":avg}}
os.makedirs("data",exist_ok=True);json.dump(out,open("data/youtube.json","w",encoding="utf-8"),indent=2);print(json.dumps({"status":"ok","videos":len(videos),"period":out["period"]}))
