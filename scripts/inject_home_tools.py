from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# The new homepage already owns its tool section. Do not inject the legacy
# homepage block, which would duplicate UI and slow the page down.
if 'data-home-v2="true"' in s:
    print('Modern homepage detected; legacy tool injection skipped.')
else:
    css='<link rel="stylesheet" href="/assets/css/home-tools.css">'
    js='<script defer src="/assets/js/home-tools.js"></script>'
    if css not in s: s=s.replace('</head>',css+'\n</head>',1)
    if js not in s: s=s.replace('</body>',js+'\n</body>',1)
    p.write_text(s,encoding='utf-8')
    print('Legacy homepage tools injection applied.')
