from pathlib import Path
import json
import re
import html

ROOT = Path(__file__).resolve().parents[1]

BASE_HEADER = '''<header class="gb-header"><div class="gb-container gb-header-main"><a class="gb-logo" href="/"><span class="gb-logo-mark">LN</span><span>Laxman Nepal</span></a><nav class="gb-menu" aria-label="Primary navigation"><a href="/news/">News</a><a href="/reviews/">Reviews</a><a href="/mobile/">Mobile</a><a href="/laptop/">Laptops</a><a href="/guides/">Buying Guides</a><a href="/gadgets/">Gadgets</a><a href="/brands/">Brands</a><a href="/tools/">Tools</a></nav><form class="gb-search" action="/search/" method="get"><input name="q" type="search" placeholder="Search technology..." aria-label="Search"><button aria-label="Search"><i class="fa-solid fa-magnifying-glass"></i></button></form><button class="gb-mobile" id="gb-mobile" aria-label="Open menu" aria-expanded="false"><i class="fa-solid fa-bars"></i></button></div><div class="gb-category"><div class="gb-container"><a href="/mobile/">Smartphones</a><a href="/laptop/">Laptops</a><a href="/gadgets/tablets/">Tablets</a><a href="/gadgets/audio/">Earbuds</a><a href="/gadgets/wearables/">Smartwatches</a><a href="/gadgets/">Speakers</a><a href="/gadgets/">Chargers</a><a href="/gadgets/cameras/">Cameras</a><a href="/brands/">Brands</a><a href="/news/">AI &amp; Tech</a></div></div></header><div class="gb-breaking"><div class="gb-container"><span class="gb-breaking-label">TRENDING</span><div class="gb-breaking-track">AI · Smartphones · Nepal gadget prices · Reviews · Buying Guides · Apps &amp; Tools</div></div></div>'''


def load_articles():
    try:
        data = json.loads((ROOT / 'search-index.json').read_text(encoding='utf-8'))
        return [x for x in data if x.get('type') == 'article']
    except Exception:
        return []


def sidebar(current_url, articles):
    links = []
    for item in articles:
        if item.get('url') == current_url:
            continue
        links.append(f'<a href="{html.escape(item.get("url", "#"), quote=True)}">{html.escape(item.get("title", "Article"))}</a>')
        if len(links) >= 6:
            break
    if not links:
        links = ['<a href="/news/">Browse latest news</a>', '<a href="/reviews/">Read latest reviews</a>', '<a href="/guides/">Explore buying guides</a>']
    return f'''<aside class="portal-sidebar"><section class="portal-widget"><h2>Most Read</h2>{''.join(links)}</section><section class="portal-widget"><h2>Explore</h2><a href="/mobile/">Mobile</a><a href="/laptop/">Laptops</a><a href="/gadgets/">Gadgets</a><a href="/brands/">Brands</a><a href="/tools/">Tools</a></section></aside>'''


def article_enhancements(text, current_url, articles):
    share = '''<div class="portal-share" aria-label="Share article"><a href="https://www.facebook.com/sharer/sharer.php?u=" target="_blank" rel="noopener" aria-label="Share on Facebook"><i class="fa-brands fa-facebook-f"></i></a><a href="https://twitter.com/intent/tweet?url=" target="_blank" rel="noopener" aria-label="Share on X"><i class="fa-brands fa-x-twitter"></i></a><a href="mailto:?body=" aria-label="Share by email"><i class="fa-solid fa-envelope"></i></a></div>'''
    text = text.replace('</div><div class="tags">', '</div>' + share + '<div class="tags">', 1)
    if '</article></div>' in text:
        text = text.replace('</article></div>', sidebar(current_url, articles) + '</div>', 1)
    # Make the share links point at the current page without introducing inline JS dependencies.
    text = text.replace('sharer.php?u="', 'sharer.php?u=" + encodeURIComponent(location.href)', 1)
    text = text.replace('intent/tweet?url="', 'intent/tweet?url=" + encodeURIComponent(location.href)', 1)
    text = text.replace('mailto:?body="', 'mailto:?body=" + encodeURIComponent(location.href)', 1)
    return text


def process(path, articles):
    text = path.read_text(encoding='utf-8')
    if 'portal-article.css' not in text:
        text = text.replace('</head>', '<link rel="stylesheet" href="/assets/css/gadgetbyte-home.css"><link rel="stylesheet" href="/assets/css/portal-article.css"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"></head>', 1)
    text = re.sub(r'<header class="site-header">.*?</header>', BASE_HEADER, text, count=1, flags=re.S)
    text = text.replace('<body>', '<body class="gb-page portal-article">', 1)

    if '<main class="gb-main">' not in text:
        text = text.replace('<main>', '<main class="gb-main"><div class="gb-container">', 1)
        text = text.replace('</main>', '</div></main>', 1)

    is_article = '/blog/' in str(path.parent).replace('\\', '/') and path.name == 'index.html' and path.parent.name != 'blog'
    if is_article:
        # Build site output has article-wrap directly inside main. Add the sidebar beside the article.
        current_url = ''
        m = re.search(r'<link rel="canonical" href="([^"]+)"', text)
        if m:
            current_url = html.unescape(m.group(1))
        text = article_enhancements(text, current_url, articles)

    script = '''<script>(function(){const b=document.getElementById('gb-mobile');const m=document.querySelector('.gb-menu');if(b&&m)b.addEventListener('click',()=>{const open=m.classList.toggle('open');b.setAttribute('aria-expanded',open?'true':'false')});document.querySelectorAll('.portal-share a').forEach(a=>{try{const u=encodeURIComponent(location.href);a.href=a.href.replace('sharer.php?u=','sharer.php?u='+u).replace('intent/tweet?url=','intent/tweet?url='+u).replace('mailto:?body=','mailto:?body='+u)}catch(e){}})})();</script>'''
    if 'id="gb-mobile"' not in text[text.find('</body>'):]:
        text = text.replace('</body>', script + '</body>', 1)
    path.write_text(text, encoding='utf-8')


articles = load_articles()
for p in ROOT.glob('blog/*/index.html'):
    process(p, articles)
for p in [ROOT / 'blog/index.html', ROOT / 'tools/index.html']:
    if p.exists():
        process(p, articles)

print(f'Finished portal styling for {len(list(ROOT.glob("blog/*/index.html")))} article pages.')
