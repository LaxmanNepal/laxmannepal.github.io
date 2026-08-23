import datetime, json, os, urllib.error, urllib.parse, urllib.request

CLIENT_ID = os.environ["YOUTUBE_CLIENT_ID"].strip()
CLIENT_SECRET = os.environ["YOUTUBE_CLIENT_SECRET"].strip()
REFRESH = os.environ["YOUTUBE_REFRESH_TOKEN"].strip()
API = os.environ.get("YOUTUBE_API_KEY", "").strip()


def post(url, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw)
        except json.JSONDecodeError:
            detail = {}
        error = detail.get("error", "unknown_error")
        description = detail.get("error_description", "No description returned by Google.")
        if error == "invalid_client":
            raise SystemExit("OAuth error: invalid_client. YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET do not match or the OAuth client is invalid.")
        if error == "invalid_grant":
            raise SystemExit("OAuth error: invalid_grant. YOUTUBE_REFRESH_TOKEN is revoked/expired or was generated for a different OAuth client. Generate a new refresh token with the SAME Client ID and Client Secret.")
        raise SystemExit(f"OAuth error (HTTP {exc.code}): {error} — {description}")


def get(url, token=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw)
        except json.JSONDecodeError:
            detail = {}
        raise SystemExit(f"YouTube API error (HTTP {exc.code}): {detail.get('error', 'api_error')} — {detail.get('message', detail.get('error_description', raw[:300]))}")


token_response = post("https://oauth2.googleapis.com/token", {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "refresh_token": REFRESH, "grant_type": "refresh_token"})
access = token_response.get("access_token")
if not access:
    raise SystemExit("OAuth error: Google returned no access_token.")

end = datetime.date.today() - datetime.timedelta(days=1)
start = end - datetime.timedelta(days=29)
analytics_url = "https://youtubeanalytics.googleapis.com/v2/reports?" + urllib.parse.urlencode({
    "ids": "channel==MINE", "startDate": start.isoformat(), "endDate": end.isoformat(),
    "metrics": "views,estimatedMinutesWatched,averageViewDuration,likes,comments,subscribersGained,subscribersLost",
    "dimensions": "day", "sort": "day"
})
daily = get(analytics_url, access)
rows = daily.get("rows", [])
headers = [column["name"] for column in daily.get("columnHeaders", [])]
D = [dict(zip(headers, row)) for row in rows]
summary = {key: sum(float(item.get(key, 0) or 0) for item in D) for key in ["views", "estimatedMinutesWatched", "likes", "comments", "subscribersGained", "subscribersLost"]}
summary["averageViewDuration"] = sum(float(item.get("averageViewDuration", 0) or 0) * float(item.get("views", 0) or 0) for item in D) / max(summary["views"], 1)

params = {"part": "statistics", "mine": "true"}
if API:
    params["key"] = API
public = get("https://www.googleapis.com/youtube/v3/channels?" + urllib.parse.urlencode(params), access)
if not public.get("items"):
    raise SystemExit("YouTube Data API returned no channel for the authenticated account. Authorize the Google account that owns the YouTube channel.")
stat = public["items"][0]["statistics"]

out = {
    "subscriberCount": int(stat.get("subscriberCount", 0) or 0),
    "viewCount": int(stat.get("viewCount", 0) or 0),
    "videoCount": int(stat.get("videoCount", 0) or 0),
    "watchTimeText": f"{summary['estimatedMinutesWatched'] / 60:,.1f} hours (30d)",
    "analyticsStatus": "ok", "lastUpdated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "period": {"start": start.isoformat(), "end": end.isoformat()}, "summary": summary, "daily": D
}
os.makedirs("data", exist_ok=True)
with open("data/youtube.json", "w", encoding="utf-8") as output_file:
    json.dump(out, output_file, indent=2)
print(json.dumps({"status": "ok", "period": out["period"], "rows": len(D)}))
