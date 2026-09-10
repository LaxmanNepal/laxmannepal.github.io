import json, sys, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timezone

path = Path("data/apps.json")
data = json.loads(path.read_text(encoding="utf-8"))
apps = data.get("apps", [])
errors = []
seen_ids, seen_urls = set(), set()

required = ("id", "name", "description", "category", "url", "icon")
for app in apps:
    missing = [key for key in required if not app.get(key)]
    if missing:
        errors.append(f"{app.get('id','<unknown>')}: missing {', '.join(missing)}")
    if app.get("id") in seen_ids:
        errors.append(f"duplicate id: {app['id']}")
    if app.get("url") in seen_urls:
        errors.append(f"duplicate url: {app['url']}")
    seen_ids.add(app.get("id"))
    seen_urls.add(app.get("url"))

if errors:
    print("\n".join(errors))
    sys.exit(1)

checked = 0
for app in apps:
    req = urllib.request.Request(app["url"], headers={"User-Agent":"LaxmanNepal-AppHealth/2.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            code = response.status
            app["status"] = "online" if 200 <= code < 400 else "degraded"
            app["httpStatus"] = code
    except urllib.error.HTTPError as error:
        app["httpStatus"] = error.code
        app["status"] = "degraded" if error.code < 500 else "offline"
    except Exception:
        app["httpStatus"] = None
        app["status"] = "offline"
    app["lastChecked"] = datetime.now(timezone.utc).isoformat()
    checked += 1

data["updatedAt"] = datetime.now(timezone.utc).isoformat()
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Validated and checked {checked} apps successfully.")
