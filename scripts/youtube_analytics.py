import datetime, json, os, urllib.error, urllib.parse, urllib.request

CLIENT_ID = os.environ["YOUTUBE_CLIENT_ID"].strip()
CLIENT_SECRET = os.environ["YOUTUBE_CLIENT_SECRET"].strip()
REFRESH = os.environ["YOUTUBE_REFRESH_TOKEN"].strip()
API = os.environ.get("YOUTUBE_API_KEY", "").strip()


def post(url, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw)
        except json.JSONDecodeError:
            detail = {"raw": raw[:500]}
        error = detail.get("error", "unknown_error")
        description = detail.get("error_description", "No description returned by Google.")
        raise RuntimeError(
            f"Google OAuth token refresh failed (HTTP {exc.code}): {error} — {description}. "
            "Check that YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET and YOUTUBE_REFRESH_TOKEN "
            "belong to the same Google OAuth client and that the refresh token has not been revoked."
        ) from exc


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
            detail = {"raw": raw[:500]}
        error = detail.get("error", "api_error")
        message = detail.get("message", detail.get("error_description", "No description returned."))
        raise RuntimeError(f"YouTube API failed (HTTP {exc.code}): {error} — {message}") from exc


# Refresh the OAuth access token. The refresh token must have been issued for this exact client.
token_response = post(
    "https://oauth2.googleapis.com/token",
    {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH,
        "grant_type": "refresh_token",
    },
)

access = token_response["access_token"]
end = datetime.date.today() - datetime.timedelta(days=1)
start = end - datetime.timedelta(days=29)

analytics_url = "https://youtubeanalytics.googleapis.com/v2/reports?" + urllib.parse.urlencode(
    {
        "ids": "channel==MINE",
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "metrics": "views,estimatedMinutesWatched,averageViewDuration,likes,comments,subscribersGained,subscribersLost",
        "dimensions": "day",
        "sort": "day",
    }
)

daily = get(analytics_url, access)
rows = daily.get("rows", [])
headers = [column["name"] for column in daily.get("columnHeaders", [])]
D = [dict(zip(headers, row)) for row in rows]

summary = {
    key: sum(float(item.get(key, 0)) for item in D)
    for key in ["views", "estimatedMinutesWatched", "likes", "comments", "subscribersGained", "subscribersLost"]
}
summary["averageViewDuration"] = (
    sum(float(item.get("averageViewDuration", 0)) * float(item.get("views", 0)) for item in D)
    / max(summary["views"], 1)
)

# Public channel totals. Analytics authorization is still required for the private performance metrics.
public = get(
    "https://www.googleapis.com/youtube/v3/channels?part=statistics&mine=true&key="
    + urllib.parse.quote(API),
    access,
)
if not public.get("items"):
    raise RuntimeError("YouTube Data API returned no channel for the authenticated account.")

stat = public["items"][0]["statistics"]

out = {
    "subscriberCount": int(stat.get("subscriberCount", 0)),
    "viewCount": int(stat.get("viewCount", 0)),
    "videoCount": int(stat.get("videoCount", 0)),
    "watchTimeText": f"{summary['estimatedMinutesWatched'] / 60:,.1f} hours (30d)",
    "analyticsStatus": "ok",
    "lastUpdated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "period": {"start": start.isoformat(), "end": end.isoformat()},
    "summary": summary,
    "daily": D,
}

with open("data/youtube.json", "w", encoding="utf-8") as output_file:
    json.dump(out, output_file, indent=2)

print(json.dumps({"status": "ok", "period": out["period"], "rows": len(D)}))
