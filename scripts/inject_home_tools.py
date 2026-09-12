from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
css='<link rel="stylesheet" href="/assets/css/home-tools.css">'
js='<script defer src="/assets/js/home-tools.js"></script>'
if css not in s:s=s.replace('</head>',css+'\n</head>',1)
if js not in s:s=s.replace('</body>',js+'\n</body>',1)
start=s.find('<section class="home-tools"')
end=s.find('</section>',start) + len('</section>') if start>=0 else -1
if start>=0 and end>start:s=s[:start]+s[end:]
block='''<section class="gb-section home-tools" aria-labelledby="home-tools-title"><div class="home-tools-head"><div><h2 id="home-tools-title">Free Tools by Laxman Nepal</h2><p>Useful AI, creator, YouTube, image, PDF, Nepal, finance and productivity tools — all in one place.</p></div><a href="/tools/">View all tools →</a></div><div class="home-tools-search"><i class="fa-solid fa-magnifying-glass"></i><input id="home-tools-search" type="search" placeholder="Search tools..." aria-label="Search tools" autocomplete="off"></div><div class="home-tools-filters" id="home-tools-filters" aria-label="Tool categories"></div><div class="home-tools-grid" id="home-tools-grid" aria-label="Free tools"></div><div class="home-tools-empty" id="home-tools-empty">No tools match your search.</div></section>'''
anchor='<section class="gb-section"><div class="gb-home-xiaomi">'
if anchor in s:s=s.replace(anchor,block+'\n'+anchor,1)
else:s=s.replace('<main class="gb-main">', '<main class="gb-main">'+block,1)
p.write_text(s,encoding='utf-8')
print('Homepage tools showcase injected.')
