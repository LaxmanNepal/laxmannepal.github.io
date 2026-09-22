from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
TARGET=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT

excluded={".git","node_modules",".pages","out",".next"}
files=[p for p in TARGET.rglob("*.html") if not any(x in excluded for x in p.relative_to(TARGET).parts)]

issues=[]
for p in sorted(files):
    try: s=p.read_text(encoding="utf-8")
    except (UnicodeDecodeError,OSError): continue
    rel=p.relative_to(TARGET)
    if not re.search(r'<meta[^>]+name=["\']viewport["\']',s,re.I):
        issues.append((str(rel),"missing viewport"))
    if len(re.findall(r'data-shared-shell=["\']header["\']',s,re.I)) != 1:
        issues.append((str(rel),"shared header count != 1"))
    if len(re.findall(r'data-shared-shell=["\']footer["\']',s,re.I)) != 1:
        issues.append((str(rel),"shared footer count != 1"))
    if not re.search(r'href=["\']/assets/css/shared-shell\.css["\']',s,re.I):
        issues.append((str(rel),"missing shared shell CSS"))
    if not re.search(r'href=["\']/assets/css/legacy-normalizer\.css["\']',s,re.I):
        issues.append((str(rel),"missing legacy normalizer CSS"))
    fixed=re.findall(r'(?:width|min-width)\s*:\s*(?:9\d\d|1\d{3,})px',s,re.I)
    if fixed:
        issues.append((str(rel),f"fixed width declarations: {len(fixed)}"))

print(f"Audited {len(files)} HTML pages under {TARGET}")
if issues:
    print(f"Found {len(issues)} compatibility warnings:")
    for path,msg in issues[:100]: print(f"- {path}: {msg}")
    if len(issues)>100: print(f"... {len(issues)-100} more")
else:
    print("No shared-shell compatibility warnings found.")
