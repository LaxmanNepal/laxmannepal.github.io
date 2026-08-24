import json, os, urllib.parse, urllib.request, urllib.error, datetime

API_KEY = os.environ["YOUTUBE_API_KEY"].strip()
HANDLE = os.environ.get("YOUTUBE_HANDLE", "@laxmannepalofficial").strip()
BASE = "https://www.googleapis.com/youtube/v3/"

def get(endpoint, params):
    params = dict(params, key=API_KEY)
    url = BASE + endpoint + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try: d = json.loads(raw)
        except Exception: d = {}
        err = d.get("error", {})
        raise SystemExit(f"YouTube API error HTTP {e.code}: {err.get('status', 'ERROR')} — {err.get('message', raw[:300])}")

# Resolve channel from handle.
search = get("search", {"part":"snippet", "q":HANDLE, "type":"channel", "maxResults":5})
items = search.get("items", [])
if not items:
    raise SystemExit(f"No YouTube channel found for {HANDLE}")
channel_id = items[0]["snippet"]["channelId"]

channel = get("channels", {"part":"snippet,statistics,contentDetails", "id":channel_id})
if not channel.get("items"):
    raise SystemExit("YouTube returned no channel details")
c = channel["items"][0]
stat = c.get("statistics", {})
snippet = c.get("snippet", {})
uploads = c.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")

videos = []
next_page = None
while len(videos) < 50 and uploads:
    p = {"part":"snippet,contentDetails", "playlistId":uploads, "maxResults":50}
    if next_page: p["pageToken"] = next_page
    page = get("playlistItems", p)
    videos.extend(page.get("items", []))
    next_page = page.get("nextPageToken")
    if not next_page: break

video_ids = [x.get("contentDetails", {}).get("videoId") for x in videos]
video_ids = [x for x in video_ids if x]
video_details = {}
for i in range(0, len(video_ids), 50):
    result = get("videos", {"part":"snippet,statistics,contentDetails", "id":",".join(video_ids[i:i+50])})
    for v in result.get("items", []): video_details[v["id"]] = v

popular = []
for item in videos:
    vid = item.get("contentDetails", {}).get("videoId")
    v = video_details.get(vid)
    if not v: continue
    s = v.get("statistics", {})
    popular.append({
        "id":vid,
        "title":v.get("snippet",{}).get("title",""),
        "publishedAt":v.get("snippet",{}).get("publishedAt"),
        "thumbnail":v.get("snippet",{}).get("thumbnails",{}).get("high",v.get("snippet",{}).get("thumbnails",{}).get("default",{})).get("url"),
        "views":int(s.get("viewCount",0) or 0),
        "likes":int(s.get("likeCount",0) or 0),
        "comments":int(s.get("commentCount",0) or 0),
        "url":f"https://www.youtube.com/watch?v={vid}"
    })
popular.sort(key=lambda x:x["views"], reverse=True)

out = {
    "channelId":channel_id,
    "channelTitle":snippet.get("title"),
    "channelDescription":snippet.get("description",""),
    "channelUrl":f"https://www.youtube.com/channel/{channel_id}",
    "customHandle":HANDLE,
    "subscriberCount":int(stat.get("subscriberCount",0) or 0),
    "viewCount":int(stat.get("viewCount",0) or 0),
    "videoCount":int(stat.get("videoCount",0) or 0),
    "hiddenSubscriberCount":bool(stat.get("hiddenSubscriberCount",False)),
    "thumbnail":snippet.get("thumbnails",{}).get("high",snippet.get("thumbnails",{}).get("default",{})).get("url"),
    "popularVideos":popular[:12],
    "recentVideos":popular[:12],
    "lastUpdated":datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "dataSource":"YouTube Data API v3"
}
os.makedirs("data",exist_ok=True)
with open("data/youtube-public.json","w",encoding="utf-8") as f: json.dump(out,f,indent=2,ensure_ascii=False)
print(json.dumps({"status":"ok","channel":out["channelTitle"],"subscribers":out["subscriberCount"],"views":out["viewCount"],"videos":out["videoCount"],"popular":len(popular[:12])}))
