import datetime
import json
import os
import urllib.error
import urllib.parse
import urllib.request

API_KEY = os.environ["YOUTUBE_API_KEY"].strip()
HANDLE = os.environ.get("YOUTUBE_HANDLE", "@laxmannepalofficial").strip()
CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID", "").strip()
BASE = "https://www.googleapis.com/youtube/v3/"


def get(endpoint, params):
    query = dict(params)
    query["key"] = API_KEY
    url = BASE + endpoint + "?" + urllib.parse.urlencode(query)
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "LaxmanNepalProfile/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            payload = json.loads(raw)
            error = payload.get("error", {})
            reason = (error.get("errors") or [{}])[0].get("reason", "unknown")
            message = error.get("message", raw[:300])
        except Exception:
            reason, message = "unknown", raw[:300]
        raise SystemExit(f"YouTube API error HTTP {exc.code}: {reason} — {message}")


def iso_duration_seconds(value):
    # ISO-8601 duration such as PT1H2M3S.
    import re
    match = re.fullmatch(r"P(?:([0-9]+)D)?T(?:([0-9]+)H)?(?:([0-9]+)M)?(?:([0-9]+)S)?", value or "")
    if not match:
        return 0
    days, hours, minutes, seconds = (int(x or 0) for x in match.groups())
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


if not API_KEY:
    raise SystemExit("YOUTUBE_API_KEY is missing. Add it as a GitHub Actions secret.")

# A fixed channel ID avoids an expensive search.list call and prevents a
# similarly named channel from being selected. The handle search is only a
# fallback when CHANNEL_ID has not been configured yet.
if not CHANNEL_ID:
    search = get("search", {"part": "snippet", "q": HANDLE, "type": "channel", "maxResults": 10})
    matches = [x for x in search.get("items", []) if x.get("snippet", {}).get("customUrl", "").lower() == HANDLE.lower()]
    if not matches:
        matches = search.get("items", [])
    if not matches:
        raise SystemExit(f"No YouTube channel found for {HANDLE}. Set YOUTUBE_CHANNEL_ID to the channel ID for a deterministic lookup.")
    CHANNEL_ID = matches[0]["snippet"]["channelId"]

channel = get("channels", {"part": "snippet,statistics,contentDetails,brandingSettings", "id": CHANNEL_ID})
if not channel.get("items"):
    raise SystemExit(f"YouTube returned no channel for channel ID {CHANNEL_ID}")

c = channel["items"][0]
snippet = c.get("snippet", {})
stat = c.get("statistics", {})
content = c.get("contentDetails", {})
branding = c.get("brandingSettings", {})
uploads = content.get("relatedPlaylists", {}).get("uploads")

# Pull the latest 100 uploads. playlistItems.list is cheap and deterministic.
upload_items = []
next_page = None
while len(upload_items) < 100 and uploads:
    params = {"part": "snippet,contentDetails,status", "playlistId": uploads, "maxResults": 50}
    if next_page:
        params["pageToken"] = next_page
    page = get("playlistItems", params)
    upload_items.extend(page.get("items", []))
    next_page = page.get("nextPageToken")
    if not next_page:
        break

video_ids = []
for item in upload_items:
    vid = item.get("contentDetails", {}).get("videoId")
    if vid and vid not in video_ids:
        video_ids.append(vid)

videos = []
for offset in range(0, len(video_ids), 50):
    batch = video_ids[offset:offset + 50]
    result = get("videos", {"part": "snippet,statistics,contentDetails,status", "id": ",".join(batch)})
    videos.extend(result.get("items", []))

video_map = {v["id"]: v for v in videos}


def normalize(v):
    s = v.get("statistics", {})
    sn = v.get("snippet", {})
    cd = v.get("contentDetails", {})
    thumbs = sn.get("thumbnails", {})
    thumb = thumbs.get("maxres") or thumbs.get("standard") or thumbs.get("high") or thumbs.get("medium") or thumbs.get("default") or {}
    views = int(s.get("viewCount", 0) or 0)
    likes = int(s.get("likeCount", 0) or 0)
    comments = int(s.get("commentCount", 0) or 0)
    return {
        "id": v["id"],
        "title": sn.get("title", ""),
        "description": sn.get("description", ""),
        "publishedAt": sn.get("publishedAt"),
        "channelId": sn.get("channelId"),
        "categoryId": sn.get("categoryId"),
        "duration": cd.get("duration"),
        "durationSeconds": iso_duration_seconds(cd.get("duration")),
        "definition": cd.get("definition"),
        "caption": cd.get("caption"),
        "thumbnail": thumb.get("url"),
        "views": views,
        "likes": likes,
        "comments": comments,
        "engagementRate": round(((likes + comments) / views) * 100, 3) if views else 0,
        "url": f"https://www.youtube.com/watch?v={v['id']}",
    }

normalized = [normalize(video_map[x]) for x in video_ids if x in video_map]
normalized.sort(key=lambda x: x.get("publishedAt") or "", reverse=True)
popular = sorted(normalized, key=lambda x: x["views"], reverse=True)

recent = normalized[:20]
latest_10 = normalized[:10]

# Lightweight local aggregates from the latest 100 uploads. These are public
# Data API statistics, not private YouTube Analytics data.
aggregate_views = sum(v["views"] for v in normalized)
aggregate_likes = sum(v["likes"] for v in normalized)
aggregate_comments = sum(v["comments"] for v in normalized)

output = {
    "schemaVersion": 2,
    "channelId": CHANNEL_ID,
    "channelTitle": snippet.get("title"),
    "channelDescription": snippet.get("description", ""),
    "channelUrl": f"https://www.youtube.com/channel/{CHANNEL_ID}",
    "customHandle": HANDLE,
    "customUrl": snippet.get("customUrl"),
    "publishedAt": snippet.get("publishedAt"),
    "country": snippet.get("country"),
    "thumbnail": (snippet.get("thumbnails", {}).get("high") or snippet.get("thumbnails", {}).get("default") or {}).get("url"),
    "subscriberCount": int(stat.get("subscriberCount", 0) or 0),
    "viewCount": int(stat.get("viewCount", 0) or 0),
    "videoCount": int(stat.get("videoCount", 0) or 0),
    "hiddenSubscriberCount": bool(stat.get("hiddenSubscriberCount", False)),
    "uploadsPlaylistId": uploads,
    "branding": branding,
    "popularVideos": popular[:20],
    "recentVideos": recent,
    "latestVideos": latest_10,
    "latest100Aggregate": {
        "videoCount": len(normalized),
        "views": aggregate_views,
        "likes": aggregate_likes,
        "comments": aggregate_comments,
        "averageViews": round(aggregate_views / len(normalized)) if normalized else 0,
        "averageLikes": round(aggregate_likes / len(normalized)) if normalized else 0,
        "averageComments": round(aggregate_comments / len(normalized)) if normalized else 0,
    },
    "lastUpdated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "dataSource": "YouTube Data API v3",
}

os.makedirs("data", exist_ok=True)
with open("data/youtube-public.json", "w", encoding="utf-8") as handle:
    json.dump(output, handle, indent=2, ensure_ascii=False)

print(json.dumps({
    "status": "ok",
    "channel": output["channelTitle"],
    "channelId": CHANNEL_ID,
    "subscribers": output["subscriberCount"],
    "views": output["viewCount"],
    "videos": output["videoCount"],
    "popularVideos": len(output["popularVideos"]),
    "recentVideos": len(output["recentVideos"]),
}))
