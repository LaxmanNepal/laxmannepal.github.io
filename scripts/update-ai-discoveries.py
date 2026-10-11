#!/usr/bin/env python3
"""Refresh the public open-source AI discoveries feed from GitHub's public API."""
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "ai-tools" / "discoveries.json"
TODAY = datetime.now(timezone.utc).date()
SINCE = (TODAY - timedelta(days=30)).isoformat()
QUERIES = [
    f"topic:artificial-intelligence stars:>20 pushed:>={SINCE}",
    f"topic:llm stars:>20 pushed:>={SINCE}",
    f"topic:ai-tools stars:>5 pushed:>={SINCE}",
]

def fetch(query):
    params = urllib.parse.urlencode({"q": query, "sort": "updated", "order": "desc", "per_page": 30})
    request = urllib.request.Request(
        "https://api.github.com/search/repositories?" + params,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "LaxmanNepal-AI-Tools-Directory",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("items", [])

def main():
    merged = {}
    errors = []
    for query in QUERIES:
        try:
            for repo in fetch(query):
                if repo.get("fork") or repo.get("archived") or not repo.get("html_url"):
                    continue
                name = repo.get("full_name", "").strip()
                if not name or name.lower() == "laxmannepal/laxmannepal.github.io":
                    continue
                previous = merged.get(name)
                candidate = {
                    "name": repo.get("name") or name,
                    "url": repo["html_url"],
                    "description": (repo.get("description") or "Open-source AI project on GitHub.")[:260],
                    "language": repo.get("language") or "Open source",
                    "stars": int(repo.get("stargazers_count") or 0),
                    "updatedAt": repo.get("pushed_at"),
                    "fullName": name,
                }
                if previous is None or candidate["stars"] > previous["stars"]:
                    merged[name] = candidate
        except Exception as exc:
            errors.append(str(exc))
    if not merged:
        raise RuntimeError("No GitHub discovery query succeeded; preserving existing feed. " + "; ".join(errors))
    projects = sorted(merged.values(), key=lambda item: (item["updatedAt"] or "", item["stars"]), reverse=True)[:24]
    payload = {
        "updatedAt": TODAY.isoformat(),
        "source": "GitHub public repository search",
        "count": len(projects),
        "tools": projects,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated daily AI discovery feed with {len(projects)} projects for {TODAY.isoformat()}")

if __name__ == "__main__":
    main()
