import datetime
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

API_KEY = os.environ["YOUTUBE_API_KEY"].strip()
HANDLE = os.environ.get("YOUTUBE_HANDLE", "@laxmannepalofficial").strip()
CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID", "UCFl4DYgZNA-XuFTTihh-l9w").strip()
BASE = "https://www.googleapis.com/youtube/v3/"
MAX_UPLOADS = int(os.environ.get("YOUTUBE_MAX_UPLOADS", "250"))


def get(endpoint, params):
    query = dict(params)
    query["key"] = API_KEY
    url = BASE + endpoint + "?" + urllib.parse.urlencode(query)
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "LaxmanNepalProfile/2.0"})
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
    match = re.fullmatch(r"P(?:([0-9]+)D)?T(?:([0-9]+)H)?(?:([0-9]+)M)?(?:([0-9]+)S)?", value or "")
    if not match:
        return 0
    days, hours, minutes, seconds = (int(x or 0) for x in match.groups())
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def safe_int(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


if not API_KEY:
    raise SystemExit("YOUTUBE_API_KEY is missing. Add it as a GitHub Actions secret.")

if not CHANNEL_ID:
    search = get("search", {"part": "snippet", "q": HANDLE, "type": "channel", "maxResults": 10})
    matches = [x for x in search.get("items", []) if x.get("snippet", {}).get("customUrl", "").lower() == HANDLE.lower()]
    if not matches:
        matches = search.get("items", [])
    if not matches:
        raise SystemExit(f"No YouTube channel found for {HANDLE}")
    CHANNEL_ID = matches[0]["snippet"]["channelId"]

channel_response = get("channels", {"part": "snippet,statistics,contentDetails,brandingSettings,status", "id": CHANNEL_ID})
if not channel_response.get("items"):
    raise SystemExit(f"YouTube returned no channel for {CHANNEL_ID}")

channel = channel_response["items"][0]
snippet = channel.get("snippet", {})
statistics = channel.get("statistics", {})
content = channel.get("contentDetails", {})
branding = channel.get("brandingSettings", {})
uploads_playlist_id = content.get("relatedPlaylists", {}).get("uploads")

upload_items = []
next_page = None
while len(upload_items) < MAX_UPLOADS and uploads_playlist_id:
    params = {"part": "snippet,contentDetails,status", "playlistId": uploads_playlist_id, "maxResults": 50}
    if next_page:
        params["pageToken"] = next_page
    page = get("playlistItems", params)
    upload_items.extend(page.get("items", []))
    next_page = page.get("nextPageToken")
    if not next_page:
        break

video_ids = []
for item in upload_items:
    video_id = item.get("contentDetails", {}).get("videoId")
    if video_id and video_id not in video_ids:
        video_ids.append(video_id)

raw_videos = []
for offset in range(0, len(video_ids), 50):
    batch = video_ids[offset:offset + 50]
    response = get("videos", {"part": "snippet,statistics,contentDetails,status,topicDetails,recordingDetails,liveStreamingDetails", "id": ",".join(batch)})
    raw_videos.extend(response.get("items", []))

video_map = {video["id"]: video for video in raw_videos}


def normalize(video):
    s = video.get("statistics", {})
    sn = video.get("snippet", {})
    cd = video.get("contentDetails", {})
    status = video.get("status", {})
    thumbs = sn.get("thumbnails", {})
    thumb = thumbs.get("maxres") or thumbs.get("standard") or thumbs.get("high") or thumbs.get("medium") or thumbs.get("default") or {}
    views = safe_int(s.get("viewCount"))
    likes = safe_int(s.get("likeCount"))
    comments = safe_int(s.get("commentCount"))
    return {
        "id": video["id"],
        "title": sn.get("title", ""),
        "description": sn.get("description", ""),
        "publishedAt": sn.get("publishedAt"),
        "channelId": sn.get("channelId"),
        "channelTitle": sn.get("channelTitle"),
        "categoryId": sn.get("categoryId"),
        "tags": sn.get("tags", []),
        "defaultLanguage": sn.get("defaultLanguage"),
        "defaultAudioLanguage": sn.get("defaultAudioLanguage"),
        "duration": cd.get("duration"),
        "durationSeconds": iso_duration_seconds(cd.get("duration")),
        "definition": cd.get("definition"),
        "caption": cd.get("caption"),
        "licensedContent": cd.get("licensedContent"),
        "projection": cd.get("projection"),
        "dimension": cd.get("dimension"),
        "madeForKids": status.get("madeForKids"),
        "privacyStatus": status.get("privacyStatus"),
        "thumbnail": thumb.get("url"),
        "views": views,
        "likes": likes,
        "comments": comments,
        "engagementRate": round(((likes + comments) / views) * 100, 3) if views else 0,
        "likeRate": round((likes / views) * 100, 3) if views else 0,
        "commentRate": round((comments / views) * 100, 3) if views else 0,
        "url": f"https://www.youtube.com/watch?v={video['id']}",
    }

videos = [normalize(video_map[video_id]) for video_id in video_ids if video_id in video_map]
videos.sort(key=lambda item: item.get("publishedAt") or "", reverse=True)
popular = sorted(videos, key=lambda item: item["views"], reverse=True)

aggregate_views = sum(video["views"] for video in videos)
aggregate_likes = sum(video["likes"] for video in videos)
aggregate_comments = sum(video["comments"] for video in videos)
shorts = [video for video in videos if 0 < video["durationSeconds"] <= 60]
long_form = [video for video in videos if video["durationSeconds"] > 60]

monthly = {}
for video in videos:
    month = (video.get("publishedAt") or "")[:7]
    if not month:
        continue
    bucket = monthly.setdefault(month, {"videos": 0, "views": 0, "likes": 0, "comments": 0})
    bucket["videos"] += 1
    bucket["views"] += video["views"]
    bucket["likes"] += video["likes"]
    bucket["comments"] += video["comments"]
monthly = [{"month": month, **values} for month, values in sorted(monthly.items())]

output = {
    "schemaVersion": 3,
    "lastUpdated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "dataSource": "YouTube Data API v3",
    "apiMode": "public-channel-data",
    "channel": {
        "id": CHANNEL_ID,
        "handle": HANDLE,
        "title": snippet.get("title"),
        "description": snippet.get("description", ""),
        "url": f"https://www.youtube.com/channel/{CHANNEL_ID}",
        "customUrl": snippet.get("customUrl"),
        "publishedAt": snippet.get("publishedAt"),
        "country": snippet.get("country"),
        "thumbnail": (snippet.get("thumbnails", {}).get("high") or snippet.get("thumbnails", {}).get("default") or {}).get("url"),
        "keywords": branding.get("channel", {}).get("keywords", ""),
        "defaultLanguage": branding.get("channel", {}).get("defaultLanguage"),
        "statistics": {
            "subscriberCount": safe_int(statistics.get("subscriberCount")),
            "viewCount": safe_int(statistics.get("viewCount")),
            "videoCount": safe_int(statistics.get("videoCount")),
            "commentCount": safe_int(statistics.get("commentCount")),
            "hiddenSubscriberCount": bool(statistics.get("hiddenSubscriberCount", False)),
        },
        "uploadsPlaylistId": uploads_playlist_id,
    },
    "branding": branding,
    "analysis": {
        "videosFetched": len(videos),
        "totalViewsFetched": aggregate_views,
        "totalLikesFetched": aggregate_likes,
        "totalCommentsFetched": aggregate_comments,
        "averageViews": round(aggregate_views / len(videos)) if videos else 0,
        "averageLikes": round(aggregate_likes / len(videos)) if videos else 0,
        "averageComments": round(aggregate_comments / len(videos)) if videos else 0,
        "shortsCount": len(shorts),
        "longFormCount": len(long_form),
        "topVideo": popular[0] if popular else None,
    },
    "popularVideos": popular[:20],
    "recentVideos": videos[:20],
    "latestVideos": videos[:10],
    "videos": videos,
    "monthly": monthly,
}

os.makedirs("data", exist_ok=True)
for filename in ("data/youtube.json", "data/youtube-public.json"):
    with open(filename, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, ensure_ascii=False)

print(json.dumps({
    "status": "ok",
    "channel": snippet.get("title"),
    "channelId": CHANNEL_ID,
    "subscribers": output["channel"]["statistics"]["subscriberCount"],
    "views": output["channel"]["statistics"]["viewCount"],
    "videos": output["channel"]["statistics"]["videoCount"],
    "videosFetched": len(videos),
    "popularVideos": len(output["popularVideos"]),
}))
