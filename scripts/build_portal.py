from pathlib import Path
from html import escape
from datetime import datetime
import re

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'content' / 'blog'
OUT = ROOT
BASE = 'https://apps.laxmannepal.com.np'


def frontmatter(text):
    data = {}
    body = text
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) == 3:
            for line in parts[1].splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    data[k.strip()] = v.strip().strip('"\'')
            body = parts[2]
    return data, body.strip()


def slug_from(path, meta):
    if meta.get('slug'):
        return meta['slug'].strip('/')
    return re.sub(r'[^a-z0-9]+', '-', meta.get('title', path.stem).lower()).strip('-')


def excerpt(body, description=''):
    if description:
        return description
    clean = re.sub(r'```.*?```', '', body, flags=re.S)
    clean = re.sub(r'[#>*_`\[\]()\-]', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean[:180] + ('…' if len(clean) > 180 else '')


def load_articles():
    items = []
    if not CONTENT.exists():
        return items
    for path in CONTENT.glob('*.md'):
        meta, body = frontmatter(path.read_text(encoding='utf-8'))
        title = meta.get('title', path.stem.replace('-', ' ').title())
        date = meta.get('date', '1970-01-01')
        try:
            sort_date = datetime.fromisoformat(date).timestamp()
        except Exception:
            sort_date = 0
        category = meta.get('category', 'Technology')
        item = {
            'title': title,
            'description': excerpt(body, meta.get('description', '')),
            'date': date,
            'updated': meta.get('updated', date),
            'author': meta.get('author', 'Laxman Nepal'),
            'category': category,
            'tags': meta.get('tags', ''),
            'image': meta.get('image', ''),
            'slug': slug_from(path, meta),
            'sort': sort_date,
        }
        item['url'] = f'/blog/{item["slug"]}/'
        items.append(item)
    return sorted(items, key=lambda x: x['sort'], reverse=True)


def img(item, cls='portal-thumb'):
    if item.get('image'):
        return f'<img class="{cls}" src="{escape(item["image"], quote=True)}" alt="{escape(item["title"], quote=True)}" loading="lazy">'
    return f'<div class="{cls} portal-placeholder"><span>LN</span></div>'


def card(item, cls='portal-card'):
    return f'''<a class="{cls}" href="{escape(item['url'])}">{img(item)}<div class="portal-card-body"><span class="portal-kicker">{escape(item['category'])}</span><h3>{escape(item['title'])}</h3><p>{escape(item['description'])}</p><small>{escape(item['author'])} · {escape(item['date'])}</small></div></a>'''


def shell(title, content):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#111"><meta name="description" content="Laxman Nepal — technology news, reviews, guides and gadgets."><title>{escape(title)} — Laxman Nepal</title><link rel="stylesheet" href="/assets/css/style.css"><link rel="stylesheet" href="/assets/css/light.css"><link rel="stylesheet" href="/assets/css/gadgetbyte-home.css"><link rel="stylesheet" href="/assets/css/gadgetbyte-portal.css"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><script defer src="/assets/js/app.js"></script></head><body class="gb-page portal-page"><header class="gb-header"><div class="gb-container gb-header-main"><a class="gb-logo" href="/"><span class="gb-logo-mark">LN</span><span>Laxman Nepal</span></a><nav class="gb-menu"><a href="/news/">News</a><a href="/reviews/">Reviews</a><a href="/mobile/">Mobile</a><a href="/laptop/">Laptop</a><a href="/guides/">Guides</a><a href="/gadgets/">Gadgets</a><a href="/tools/">Tools</a></nav><form class="gb-search" action="/search/" method="get"><input name="q" type="search" placeholder="Search technology..." aria-label="Search"><button><i class="fa-solid fa-magnifying-glass"></i></button></form><button class="gb-mobile" aria-label="Open menu"><i class="fa-solid fa-bars"></i></button></div><div class="gb-category"><div class="gb-container"><a href="/mobile/">Smartphones</a><a href="/laptop/">Laptops</a><a href="/gadgets/tablets/">Tablets</a><a href="/gadgets/audio/">Audio</a><a href="/reviews/">Reviews</a><a href="/guides/">Buying Guides</a><a href="/brands/">Brands</a><a href="/gadgets/">Gadgets</a><a href="/tools/">Apps & Tools</a><a href="/news/">AI</a></div></div></header><div class="gb-breaking"><div class="gb-container"><span class="gb-breaking-label">TRENDING</span><div class="gb-breaking-track">AI · Smartphones · Nepal Tech · Reviews · Buying Guides · Apps & Tools</div></div></div><main class="gb-main"><div class="gb-container">{content}</div></main><footer class="gb-footer"><div class="gb-container"><div class="gb-footer-grid"><div><h3>Laxman Nepal</h3><p>Practical technology news, reviews, buying guides, AI, apps and useful digital tools.</p></div><div><h3>Explore</h3><a href="/news/">News</a><a href="/reviews/">Reviews</a><a href="/guides/">Guides</a><a href="/gadgets/">Gadgets</a></div><div><h3>Prices</h3><a href="/mobile/price/">Mobile Prices</a><a href="/laptop/price/">Laptop Prices</a><a href="/brands/">Brands</a><a href="/tools/">Tools</a></div><div><h3>Follow</h3><a href="https://www.youtube.com/@laxmannepalofficial">YouTube</a><a href="https://www.instagram.com/laxmannepalsir/">Instagram</a><a href="https://github.com/LaxmanNepal">GitHub</a></div></div><div class="gb-footer-bottom"><span>© <span id="year"></span> Laxman Nepal. All rights reserved.</span><span>Built for Nepal · Built for usefulness.</span></div></div></footer><script>document.getElementById('year').textContent=new Date().getFullYear();</script></body></html>'''


def listing(title, subtitle, items, empty='More content will appear here automatically as you publish articles.'):
    cards = ''.join(card(x) for x in items)
    if not cards:
        cards = f'<div class="portal-empty"><i class="fa-regular fa-newspaper"></i><h3>No articles yet</h3><p>{escape(empty)}</p></div>'
    return shell(title, f'''<section class="portal-heading"><div><span class="portal-overline">LAXMAN NEPAL</span><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div></section><div class="portal-layout"><section><div class="portal-toolbar"><strong>{len(items)} articles</strong><span>Latest first</span></div><div class="portal-grid">{cards}</div></section><aside class="portal-sidebar"><div class="portal-panel"><h3>Explore</h3><a href="/news/">News</a><a href="/reviews/">Reviews</a><a href="/guides/">Buying Guides</a><a href="/mobile/">Mobile</a><a href="/laptop/">Laptop</a><a href="/gadgets/">Gadgets</a></div><div class="portal-panel"><h3>Most Read</h3>{''.join(f'<a class="portal-mini" href="{x["url"]}"><b>{i:02}</b><span>{escape(x["title"])}</span></a>' for i,x in enumerate(items[:5],1))}</div></aside></div>''')


def simple_hub(title, subtitle, links):
    tiles = ''.join(f'<a class="portal-hub-card" href="{u}"><span>{icon}</span><h3>{escape(t)}</h3><p>{escape(d)}</p></a>' for t,d,u,icon in links)
    return shell(title, f'<section class="portal-heading"><div><span class="portal-overline">LAXMAN NEPAL</span><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div></section><div class="portal-hub-grid">{tiles}</div>')


def write(path, html):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding='utf-8')


def main():
    articles = load_articles()
    reviews = [x for x in articles if 'review' in x['category'].lower() or 'review' in x['title'].lower()]
    guides = [x for x in articles if any(k in (x['category']+' '+x['title']).lower() for k in ['guide','how to','tutorial'])]
    news = [x for x in articles if x not in reviews and x not in guides]

    write(OUT/'news/index.html', listing('News', 'Latest technology, AI, apps, Nepal tech and gadget updates.', news or articles))
    write(OUT/'reviews/index.html', listing('Reviews', 'Real-world reviews, comparisons, testing and buying verdicts.', reviews))
    write(OUT/'guides/index.html', listing('Buying Guides', 'Practical recommendations to help you choose the right technology.', guides or articles))

    write(OUT/'mobile/index.html', simple_hub('Mobile', 'Smartphones, prices, comparisons and practical buying advice.', [('Mobile Prices','Browse mobile prices and model pages.','/mobile/price/','📱'),('Best Phones','Budget to flagship recommendations.','/guides/','🏆'),('Mobile News','Latest smartphone announcements and updates.','/news/','📰'),('Brands','Explore smartphone brands and models.','/brands/','◉')]))
    write(OUT/'mobile/price/index.html', simple_hub('Mobile Prices', 'A clean home for Nepal mobile prices, models and brand listings.', [('Samsung','Samsung phone prices and models.','/brands/samsung/','S'),('Apple','iPhone prices and models.','/brands/apple/','A'),('Xiaomi','Xiaomi and Redmi models.','/brands/xiaomi/','X'),('All Brands','Explore every available brand.','/brands/','+')]))
    write(OUT/'laptop/index.html', simple_hub('Laptop', 'Laptop news, prices, buying guides and recommendations.', [('Laptop Prices','Browse laptop price categories.','/laptop/price/','💻'),('Best Laptops','Recommendations by budget and use.','/guides/','🏆'),('Laptop News','Latest laptop announcements.','/news/','📰'),('Brands','Explore laptop brands.','/brands/','◉')]))
    write(OUT/'laptop/price/index.html', simple_hub('Laptop Prices', 'A dedicated Nepal laptop price experience.', [('Gaming','Gaming laptops by budget.','/guides/','🎮'),('Work & Study','Everyday productivity laptops.','/guides/','💼'),('Creator','Laptops for creators and professionals.','/guides/','🎬'),('All Brands','Explore laptop brands.','/brands/','+')]))
    write(OUT/'gadgets/index.html', simple_hub('Gadgets', 'Explore smartphones, tablets, audio, wearables, cameras and more.', [('Smartphones','Phones and mobile technology.','/mobile/','📱'),('Laptops','Computers for work, study and gaming.','/laptop/','💻'),('Tablets','Tablets and 2-in-1 devices.','/gadgets/tablets/','▣'),('Audio','Earbuds, headphones and speakers.','/gadgets/audio/','🎧'),('Smartwatches','Wearables and fitness devices.','/gadgets/wearables/','⌚'),('Cameras','Cameras, action cams and drones.','/gadgets/cameras/','📷')]))
    write(OUT/'brands/index.html', simple_hub('Brands', 'Browse technology by brand.', [('Apple','iPhone, iPad, Mac and Apple ecosystem.','/brands/apple/','A'),('Samsung','Galaxy phones, watches and more.','/brands/samsung/','S'),('Xiaomi','Xiaomi, Redmi and ecosystem products.','/brands/xiaomi/','X'),('OnePlus','Phones, audio and ecosystem products.','/brands/oneplus/','1'),('Vivo','Vivo smartphone coverage.','/brands/vivo/','V'),('Oppo','Oppo smartphone coverage.','/brands/oppo/','O')]))
    write(OUT/'search/index.html', listing('Search', 'Search results will use the same content database and site-wide search UI.', articles))

    # Keep the homepage navigation consistent with the generated portal.
    home = OUT/'index.html'
    if home.exists():
        text = home.read_text(encoding='utf-8')
        replacements = {
            'href="#news">News':'href="/news/">News',
            'href="#reviews">Reviews':'href="/reviews/">Reviews',
            'href="#guides">Buying Guides':'href="/guides/">Buying Guides',
            'href="#gadgets">Gadgets':'href="/gadgets/">Gadgets',
            'href="#news">Smartphones':'href="/mobile/">Smartphones',
            'href="#gadgets">Laptops':'href="/laptop/">Laptops',
            'href="#gadgets">Tablets':'href="/gadgets/tablets/">Tablets',
            'href="#brands">Brands':'href="/brands/">Brands',
        }
        for a,b in replacements.items():
            text = text.replace(a,b)
        home.write_text(text, encoding='utf-8')


if __name__ == '__main__':
    main()
