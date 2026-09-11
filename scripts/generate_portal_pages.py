from pathlib import Path
from html import escape
from datetime import datetime
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT
BLOG = ROOT / 'content' / 'blog'
BASE = 'https://apps.laxmannepal.com.np'


def parse_md(path):
    text = path.read_text(encoding='utf-8')
    fm = {}
    body = text
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) == 3:
            for line in parts[1].splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    fm[k.strip()] = v.strip().strip('"').strip("'")
            body = parts[2]
    title = fm.get('title') or path.stem.replace('-', ' ').title()
    desc = fm.get('description') or re.sub(r'[#*`>\[\]]', '', body).strip().replace('\n', ' ')[:180]
    date = fm.get('date', '1970-01-01')
    category = fm.get('category', 'Technology')
    tags = fm.get('tags', '')
    image = fm.get('image', '')
    slug = fm.get('slug') or path.stem
    author = fm.get('author', 'Laxman Nepal')
    return dict(title=title, description=desc, date=date, category=category, tags=tags, image=image, author=author, slug=slug)


def articles():
    items = [parse_md(p) for p in BLOG.glob('*.md') if p.name.lower() != 'readme.md']
    return sorted(items, key=lambda x: x['date'], reverse=True)


def slugify(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')


def card(a, cls='portal-card'):
    if a['image']:
        media = f'<img class="portal-card-media" src="{escape(a["image"], quote=True)}" alt="{escape(a["title"], quote=True)}" loading="lazy">'
    else:
        media = '<div class="portal-card-media portal-media-fallback"><span>LN</span></div>'
    return f'<a class="{cls}" href="/blog/{escape(a["slug"], quote=True)}/">{media}<div class="portal-card-body"><span>{escape(a["category"])}</span><h3>{escape(a["title"])}</h3><p>{escape(a["description"])}</p><small>{escape(a["author"])} · {escape(a["date"])}</small></div></a>'


def shell(title, active, content):
    nav = ''.join(f'<a class="{"active" if active == key else ""}" href="{url}">{label}</a>' for key,label,url in [
        ('news','News','/news/'),('reviews','Reviews','/reviews/'),('mobile','Mobile','/mobile/'),('laptop','Laptops','/laptop/'),('gadgets','Gadgets','/gadgets/'),('guides','Guides','/guides/'),('brands','Brands','/brands/'),('tools','Tools','/tools/')])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Laxman Nepal technology portal — news, reviews, guides, gadgets and useful tools."><meta name="theme-color" content="#111"><title>{escape(title)} · Laxman Nepal</title><link rel="stylesheet" href="/assets/css/style.css"><link rel="stylesheet" href="/assets/css/light.css"><link rel="stylesheet" href="/assets/css/gadgetbyte-home.css"><link rel="stylesheet" href="/assets/css/portal-pages.css"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"></head><body class="gb-page portal-page"><header class="gb-header"><div class="gb-container gb-header-main"><a class="gb-logo" href="/"><span class="gb-logo-mark">LN</span><span>Laxman Nepal</span></a><nav class="gb-menu">{nav}</nav><form class="gb-search" action="/search/" method="get"><input name="q" type="search" placeholder="Search technology..." aria-label="Search"><button aria-label="Search"><i class="fa-solid fa-magnifying-glass"></i></button></form><button class="gb-mobile" id="portal-menu" aria-label="Open menu"><i class="fa-solid fa-bars"></i></button></div><div class="gb-category"><div class="gb-container"><a href="/mobile/">Smartphones</a><a href="/laptop/">Laptops</a><a href="/gadgets/tablets/">Tablets</a><a href="/gadgets/audio/">Audio</a><a href="/gadgets/wearables/">Wearables</a><a href="/reviews/">Reviews</a><a href="/guides/">Buying Guides</a><a href="/brands/">Brands</a><a href="/tools/">Apps & Tools</a><a href="/news/">AI & Tech</a></div></div></header><div class="gb-breaking"><div class="gb-container"><span class="gb-breaking-label">TRENDING</span><div class="gb-breaking-track">AI · Smartphones · Laptops · Nepal gadget prices · Reviews · Buying guides</div></div></div><main class="portal-main"><div class="gb-container">{content}</div></main><footer class="gb-footer"><div class="gb-container"><div class="gb-footer-grid"><div><h3>Laxman Nepal</h3><p>Practical technology news, reviews, guides, gadgets and useful digital tools.</p></div><div><h3>Explore</h3><a href="/news/">News</a><a href="/reviews/">Reviews</a><a href="/mobile/">Mobile</a><a href="/laptop/">Laptops</a></div><div><h3>Discover</h3><a href="/gadgets/">Gadgets</a><a href="/guides/">Guides</a><a href="/brands/">Brands</a><a href="/tools/">Tools</a></div><div><h3>Connect</h3><a href="https://www.youtube.com/@laxmannepalofficial">YouTube</a><a href="https://www.instagram.com/laxmannepalsir/">Instagram</a><a href="https://github.com/LaxmanNepal">GitHub</a></div></div><div class="gb-footer-bottom"><span>© <span id="year"></span> Laxman Nepal</span><span>Built for Nepal · Built for usefulness.</span></div></div></footer><script>(function(){const y=document.getElementById('year');if(y)y.textContent=new Date().getFullYear();const m=document.getElementById('portal-menu');m&&m.addEventListener('click',()=>document.querySelector('.gb-menu')?.classList.toggle('open'));})();</script></body></html>'''


def section_page(folder, title, active, intro, items, categories):
    cats = ''.join(f'<a href="{u}">{escape(c)}</a>' for c,u in categories)
    cards = ''.join(card(a) for a in items[:18])
    if not cards:
        cards = '<div class="portal-empty">New content will appear here automatically when you publish an article.</div>'
    ranks = ''.join(f'<a class="portal-rank" href="/blog/{escape(a["slug"])}/"><b>{i:02d}</b><span>{escape(a["title"])}</span></a>' for i,a in enumerate(items[:5],1))
    content = f'<section class="portal-heading"><span>TECH PORTAL</span><h1>{escape(title)}</h1><p>{escape(intro)}</p></section><div class="portal-chips">{cats}</div><div class="portal-layout"><section><div class="portal-section-title"><h2>Latest {escape(title)}</h2><span>{len(items)} articles</span></div><div class="portal-grid">{cards}</div></section><aside class="portal-sidebar"><h2>Most Read</h2>{ranks or "<p>No articles yet.</p>"}</aside></div>'
    d=OUT/folder
    d.mkdir(parents=True, exist_ok=True)
    (d/'index.html').write_text(shell(title, active, content), encoding='utf-8')


def filtered(items, *terms):
    words = [x.lower() for x in terms]
    return [a for a in items if any(w in (a['title']+' '+a['category']+' '+a['tags']).lower() for w in words)]


def brand_page(brand, items):
    relevant = filtered(items, brand)
    title = f'{brand}'
    intro = f'Latest {brand} news, reviews, prices, launches and buying information from Laxman Nepal.'
    section_page(f'brands/{slugify(brand)}', title, 'brands', intro, relevant, [('All Brands','/brands/'),('Mobile','/mobile/'),('Reviews','/reviews/'),('Prices','/mobile/price/')])


def gadget_page(folder, title, terms, items):
    relevant = filtered(items, *terms)
    section_page(f'gadgets/{folder}', title, 'gadgets', f'{title} news, reviews, guides and useful recommendations.', relevant, [('All Gadgets','/gadgets/'),('Reviews','/reviews/'),('Guides','/guides/'),('Brands','/brands/')])


def write_search(items):
    index = [{k:a[k] for k in ('title','description','date','category','tags','image','author','slug')} for a in items]
    import json
    (OUT/'search-index.json').write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
    content = '''<section class="portal-heading"><span>SEARCH</span><h1>Search Laxman Nepal</h1><p>Find news, reviews, guides and technology articles across the site.</p></section><div class="portal-search-page"><form id="site-search-form" class="portal-search-form"><input id="site-search-input" type="search" placeholder="Search phones, AI, laptops, reviews..." autocomplete="off"><button>Search</button></form><p id="search-meta" class="portal-search-meta"></p><div id="search-results" class="portal-grid"></div></div><script>(function(){const input=document.getElementById('site-search-input'),form=document.getElementById('site-search-form'),out=document.getElementById('search-results'),meta=document.getElementById('search-meta');let data=[];function esc(s){return String(s||'').replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]))}function render(q){q=(q||'').trim().toLowerCase();const found=!q?data:data.filter(a=>(a.title+' '+a.description+' '+a.category+' '+a.tags).toLowerCase().includes(q));meta.textContent=q?(found.length+' result'+(found.length===1?'':'s')+' for “'+q+'”'):(data.length+' articles available');out.innerHTML=found.slice(0,30).map(a=>'<a class="portal-card" href="/blog/'+encodeURIComponent(a.slug)+'/">'+(a.image?'<img class="portal-card-media" src="'+esc(a.image)+'" alt="'+esc(a.title)+'" loading="lazy">':'<div class="portal-card-media portal-media-fallback"><span>LN</span></div>')+'<div class="portal-card-body"><span>'+esc(a.category)+'</span><h3>'+esc(a.title)+'</h3><p>'+esc(a.description)+'</p><small>'+esc(a.author)+' · '+esc(a.date)+'</small></div></a>').join('')||'<div class="portal-empty"><h3>No results found</h3><p>Try a different keyword.</p></div>'}fetch('/search-index.json').then(r=>r.json()).then(d=>{data=d;const q=new URLSearchParams(location.search).get('q')||'';input.value=q;render(q)}).catch(()=>{meta.textContent='Search index unavailable.'});form.addEventListener('submit',e=>{e.preventDefault();const q=input.value.trim();history.replaceState({},'',q?'?q='+encodeURIComponent(q):location.pathname);render(q)});})();</script>'''
    (OUT/'search').mkdir(parents=True, exist_ok=True)
    (OUT/'search/index.html').write_text(shell('Search','',content), encoding='utf-8')


def main():
    items = articles()
    reviews = filtered(items, 'review')
    guides = filtered(items, 'guide', 'buying', 'best', 'tutorial')
    news = [a for a in items if a not in reviews and a not in guides] or items

    section_page('news','News','news','Latest technology news, AI updates, apps, products and practical digital stories.',news,[('All','/news/'),('AI','/news/'),('Smartphones','/mobile/'),('Apps','/tools/'),('Nepal Tech','/news/')])
    section_page('reviews','Reviews','reviews','Hands-on reviews, testing, comparisons and honest buying verdicts.',reviews,[('All','/reviews/'),('Phones','/mobile/'),('Laptops','/laptop/'),('Gadgets','/gadgets/')])
    section_page('guides','Buying Guides','guides','Straightforward recommendations for phones, laptops, gadgets, apps and AI tools.',guides,[('Phones','/mobile/'),('Laptops','/laptop/'),('Gadgets','/gadgets/'),('AI Tools','/tools/')])
    section_page('mobile','Mobile','mobile','Smartphone news, comparisons, buying guides and Nepal-focused mobile coverage.',filtered(items,'phone','smartphone','mobile','iphone','galaxy','redmi','xiaomi') or items,[('Mobile Prices','/mobile/price/'),('Best Phones','/guides/'),('Brands','/brands/'),('Reviews','/reviews/')])
    section_page('laptop','Laptops','laptop','Laptop news, buying advice, reviews and practical recommendations.',filtered(items,'laptop','notebook','macbook') or items,[('Laptop Prices','/laptop/price/'),('Best Laptops','/guides/'),('Brands','/brands/'),('Reviews','/reviews/')])
    section_page('gadgets','Gadgets','gadgets','Explore tablets, earbuds, smartwatches, cameras, drones, monitors and accessories.',items,[('Tablets','/gadgets/tablets/'),('Audio','/gadgets/audio/'),('Wearables','/gadgets/wearables/'),('Cameras','/gadgets/cameras/')])

    write_search(items)

    brands=['Apple','Samsung','Xiaomi','Redmi','POCO','OnePlus','OPPO','vivo','Realme','Honor','Google','Nothing','Dell','HP','Lenovo','ASUS','Acer']
    brand_cards=''.join(f'<a class="brand-tile" href="/brands/{slugify(b)}/"><strong>{escape(b)}</strong><span>News · Reviews · Prices</span></a>' for b in brands)
    content=f'<section class="portal-heading"><span>BRANDS</span><h1>Gadget Brands</h1><p>Explore technology brands, their products, reviews, prices and latest news.</p></section><div class="brand-grid">{brand_cards}</div>'
    d=OUT/'brands';d.mkdir(parents=True, exist_ok=True);(d/'index.html').write_text(shell('Brands','brands',content),encoding='utf-8')
    for b in brands:
        brand_page(b, items)

    gadget_page('tablets','Tablets',['tablet','ipad','tab'],items)
    gadget_page('audio','Audio',['earbud','buds','headphone','speaker','audio','airpods'],items)
    gadget_page('wearables','Wearables',['watch','smartwatch','wearable','band','fitness'],items)
    gadget_page('cameras','Cameras',['camera','drone','gopro','action cam'],items)

    # Create empty but valid destination hubs referenced by the navigation.
    for folder,title,terms in [('mobile/best','Best Mobile Phones',['phone','smartphone','mobile']),('laptop/best','Best Laptops',['laptop','notebook'])]:
        section_page(folder,title,'mobile' if folder.startswith('mobile') else 'laptop',f'Curated recommendations for {title.lower()} in Nepal.',filtered(items,*terms) or items,[('Guides','/guides/'),('Reviews','/reviews/'),('Prices','/mobile/price/' if folder.startswith('mobile') else '/laptop/price/'),('Brands','/brands/')])

    # Keep homepage navigation consistent with the generated portal.
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
        for a,b in replacements.items(): text=text.replace(a,b)
        home.write_text(text,encoding='utf-8')

if __name__=='__main__':
    main()
