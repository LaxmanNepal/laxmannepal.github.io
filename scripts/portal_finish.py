from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
BASE_HEADER='''<header class="gb-header"><div class="gb-container gb-header-main"><a class="gb-logo" href="/"><span class="gb-logo-mark">LN</span><span>Laxman Nepal</span></a><nav class="gb-menu"><a href="/news/">News</a><a href="/reviews/">Reviews</a><a href="/mobile/">Mobile</a><a href="/laptop/">Laptops</a><a href="/guides/">Buying Guides</a><a href="/gadgets/">Gadgets</a><a href="/brands/">Brands</a><a href="/tools/">Tools</a></nav><form class="gb-search" action="/search/" method="get"><input name="q" type="search" placeholder="Search technology..." aria-label="Search"><button><i class="fa-solid fa-magnifying-glass"></i></button></form><button class="gb-mobile" id="gb-mobile"><i class="fa-solid fa-bars"></i></button></div><div class="gb-category"><div class="gb-container"><a href="/mobile/">Smartphones</a><a href="/laptop/">Laptops</a><a href="/gadgets/tablets/">Tablets</a><a href="/gadgets/audio/">Earbuds</a><a href="/gadgets/wearables/">Smartwatches</a><a href="/gadgets/">Speakers</a><a href="/gadgets/">Chargers</a><a href="/gadgets/cameras/">Cameras</a><a href="/brands/">Brands</a><a href="/news/">AI & Tech</a></div></div></header><div class="gb-breaking"><div class="gb-container"><span class="gb-breaking-label">TRENDING</span><div class="gb-breaking-track">AI · Smartphones · Nepal gadget prices · Reviews · Buying Guides · Apps & Tools</div></div></div>'''

def process(path):
    text=path.read_text(encoding='utf-8')
    if 'gadgetbyte-home.css' not in text:
        text=text.replace('</head>','<link rel="stylesheet" href="/assets/css/gadgetbyte-home.css"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"></head>',1)
    text=re.sub(r'<header class="site-header">.*?</header>',BASE_HEADER,text,count=1,flags=re.S)
    text=text.replace('<main><div class="article-wrap">','<main class="gb-main"><div class="gb-container"><div class="article-wrap">',1)
    if '<main class="gb-main"><div class="gb-container">' in text and '</main>' in text:
        # close the portal container around the original article body
        pos=text.rfind('</main>')
        if pos>=0 and '</div></div>' not in text[pos-30:pos]: text=text[:pos]+'</div></div>'+text[pos:]
    text=text.replace('<body>','<body class="gb-page portal-article">',1)
    text=text.replace('<script defer src="/assets/js/app.js"></script>','<script defer src="/assets/js/app.js"></script><script>document.getElementById("gb-mobile")?.addEventListener("click",()=>document.querySelector(".gb-menu")?.classList.toggle("open"));</script>')
    path.write_text(text,encoding='utf-8')

for p in ROOT.glob('blog/*/index.html'):
    process(p)
for p in [ROOT/'blog/index.html',ROOT/'tools/index.html']:
    if p.exists(): process(p)
