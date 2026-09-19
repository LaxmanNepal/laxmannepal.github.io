#!/usr/bin/env python3
"""Classify imported Blogger posts into the site's content taxonomy.

Classification is deterministic and title-based so it works without paid APIs.
Manual overrides can be added to data/content-overrides.json.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERRIDES = ROOT / "data" / "content-overrides.json"

RULES = [
    ("youtube", ["youtube", "channel analytics", "youtuber", "subscriber", "video seo"]),
    ("ai", [" ai ", "artificial intelligence", "chatgpt", "gemini", "claude", "copilot", "ai tool"]),
    ("tool", ["converter", "generator", "downloader", "scanner", "calculator", "compressor", "qr code", "date converter"]),
    ("guide", ["how to", "tutorial", "guide", "tips", "step by step", "fix ", "reset", "install", "setup"]),
    ("review", ["review", "hands-on", "unboxing", "vs ", "comparison", "worth it"]),
    ("news", ["news", "launch", "launched", "announced", "update", "released", "release"]),
]

def classify(title: str) -> tuple[str, list[str]]:
    text = f" {title.lower()} "
    for content_type, keywords in RULES:
        if any(keyword in text for keyword in keywords):
            return content_type, [content_type, "technology"]
    return "blog", ["blog", "technology"]

def main():
    manifest_path = ROOT / ".blogger-migration.json"
    if not manifest_path.exists():
        raise SystemExit("Missing .blogger-migration.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    overrides = {}
    if OVERRIDES.exists():
        overrides = json.loads(OVERRIDES.read_text(encoding="utf-8"))
    changed = 0
    for post in manifest.get("posts", []):
        key = post.get("path", "")
        override = overrides.get(key) or overrides.get(post.get("original_url", ""))
        if override:
            post["type"] = override.get("type", "blog")
            post["tags"] = override.get("tags", [post["type"]])
        else:
            post["type"], post["tags"] = classify(post.get("title", ""))
        changed += 1
    manifest["classifier"] = {"version": 1, "method": "deterministic title rules + manual overrides"}
    manifest["classified_posts"] = changed
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Classified {changed} posts")

if __name__ == "__main__":
    main()
