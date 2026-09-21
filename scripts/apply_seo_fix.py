#!/usr/bin/env python3
"""Apply a narrowly scoped SEO title/description/H1 change to one HTML file."""
import re, sys
from pathlib import Path

def main():
    if len(sys.argv) != 5:
        raise SystemExit("Usage: apply_seo_fix.py <path> <title> <description> <h1>")
    path=Path(sys.argv[1])
    title, description, h1 = [str(x).strip() for x in sys.argv[2:]]
    if not path.is_file() or path.suffix.lower() != ".html":
        raise SystemExit(f"Invalid HTML target: {path}")
    if ".." in path.parts:
        raise SystemExit("Path traversal is not allowed.")
    text=path.read_text(encoding="utf-8")
    new=re.sub(r"(<title\b[^>]*>).*?(</title>)", lambda m:m.group(1)+title+m.group(2), text, count=1, flags=re.I|re.S)
    if not re.search(r"<title\b", new, re.I):
        new=re.sub(r"(<head\b[^>]*>)", r"\1<title>"+title+"</title>", new, count=1, flags=re.I|re.S)
    meta_pat=r'(<meta\b[^>]*\bname=["\']description["\'][^>]*\bcontent=["\'])(.*?)(["\'][^>]*>)'
    if re.search(meta_pat,new,re.I|re.S):
        new=re.sub(meta_pat, lambda m:m.group(1)+description+m.group(3), new, count=1, flags=re.I|re.S)
    else:
        new=re.sub(r"(<head\b[^>]*>)", r'\1<meta name="description" content="'+description.replace('"','&quot;')+'">', new, count=1, flags=re.I|re.S)
    h1_pat=r"(<h1\b[^>]*>).*?(</h1>)"
    if not re.search(h1_pat,new,re.I|re.S):
        raise SystemExit("No H1 found; refusing to invent page structure.")
    new=re.sub(h1_pat, lambda m:m.group(1)+h1+m.group(2), new, count=1, flags=re.I|re.S)
    if new == text:
        raise SystemExit("No changes were produced.")
    path.write_text(new,encoding="utf-8")

if __name__=="__main__":
    main()
