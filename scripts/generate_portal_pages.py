from pathlib import Path
from html import escape
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT
BLOG = ROOT / 'content' / 'blog'


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
    date = fm.get('date', '')
    category = fm.get('category', 'Technology')
    image = fm.get('image', '')
    slug = path.stem
    return dict(title=title, description=desc, date=date, category=category, image=image, slug=slug)


def articles():
    items = [parse_md(p) for p in BLOG.glob('*.md') if p.name.lower() != 'readme.md']
    return sorted(items, key=lambda x: x['date'], reverse=True)


def card(a, cls='portal-card'):
    img = f'<div class="portal-card-media" style="background-image:url(\'{escape(a["image"], quote=True)}\')"></div>' if a['image'] else '<div class="portal-card-media portal-media-fallback"></div>'
    return f'<a class="{cls}" href="/blog/{escape(a["slug"], quote=True)}/">{img}<div class="portal-card-body"><span>{escape(a["category"])}</span><h3>{escape(a["title"])}</h3><p>{escape(a["description"])}</p><small>{escape(a["date"])}</small></div></a>'


def shell(title, active, content):
    nav = ''.join(f'<a class="{"active" if active == key else ""}" href="{url}">{label}</a>' for key,label,url in [
        ('news','News','/news/'),('reviews','Reviews','/reviews/'),('mobile','Mobile','/mobile/'),('laptop','Laptops','/laptop/'),('gadgets','Gadgets','/gadgets/'),('guides','Guides','/guides/'),('brands','Brands','/brands/'),('tools','Tools','/tools/')])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Laxman Nepal technology portal — news, reviews, guides, gadgets and useful tools."><title>{escape(title)} · Laxman Nepal</title><link rel="stylesheet" href="/assets/css/style.css"><link rel="stylesheet" href="/assets/css/light.css"><link rel="stylesheet" href="/assets/css/gadgetbyte-home.css"><link rel="stylesheet" href="/assets/css/portal-pages.css"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"></head><body class="gb-page portal-page"><header class="gb-header"><div class="gb-container gb-header-main"><a class="gb-logo" href="/"><span class="gb-logo-mark">LN</span><span>Laxman Nepal</span></a><nav class="gb-menu">{nav}</nav><form class="gb-search" onsubmit="return false"><input id="portal-search" type="search" placeholder="Search technology..."><button aria-label="Search"><i class="fa-solid fa-magnifying-glass"></i></button></form><button class="gb-mobile" id="portal-menu"><i class="fa-solid fa-bars"></i></button></div><div class="gb-category"><div class="gb-container"><a href="/mobile/">Smartphones</a><a href="/laptop/">Laptops</a><a href="/gadgets/">Tablets & Gadgets</a><a href="/reviews/">Reviews</a><a href="/guides/">Buying Guides</a><a href="/brands/">Brands</a><a href="/tools/">Apps & Tools</a><a href="/news/">AI & Tech</a></div></div></header><div class="gb-breaking"><div class="gb-container"><span class="gb-breaking-label">TRENDING</span><div class="gb-breaking-track">AI · Smartphones · Laptops · Nepal gadget prices · Reviews · Buying guides</div></div></div><main class="portal-main"><div class="gb-container">{content}</div></main><footer class="gb-footer"><div class="gb-container"><div class="gb-footer-grid"><div><h3>Laxman Nepal</h3><p>Practical technology news, reviews, guides, gadgets and useful digital tools.</p></div><div><h3>Explore</h3><a href="/news/">News</a><a href="/reviews/">Reviews</a><a href="/mobile/">Mobile</a><a href="/laptop/">Laptops</a></div><div><h3>Discover</h3><a href="/gadgets/">Gadgets</a><a href="/guides/">Guides</a><a href="/brands/">Brands</a><a href="/tools/">Tools</a></div><div><h3>Connect</h3><a href="https://www.youtube.com/@laxmannepalofficial">YouTube</a><a href="https://www.instagram.com/laxmannepalsir/">Instagram</a><a href="https://github.com/LaxmanNepal">GitHub</a></div></div><div class="gb-footer-bottom"><span>© <span id="year"></span> Laxman Nepal</span><span>Built for Nepal · Built for usefulness.</span></div></div></footer><script>(function(){const y=document.getElementById('year');if(y)y.textContent=new Date().getFullYear();const m=document.getElementById('portal-menu');m&&m.addEventListener('click',()=>document.querySelector('.gb-menu')?.classList.toggle('open'));const s=document.getElementById('portal-search');s&&s.addEventListener('keydown',e=>{if(e.key==='Enter'&&s.value.trim())location.href='/blog/?q='+encodeURIComponent(s.value.trim())})})();</script></body></html>'''


def section_page(folder, title, active, intro, items, categories):
    top = f'<section class="portal-heading"><span>TECH PORTAL</span><h1>{escape(title)}</h1><p>{escape(intro)}</p></section>'
    cats = ''.join(f'<a href="{u}">{escape(c)}</a>' for c,u in categories)
    grid = ''.join(card(a) for a in items[:12]) or '<div class="portal-empty">New content is coming soon.</div>'
    side = ''.join(f'<a class="portal-rank" href="/blog/{escape(a["slug"])}/"><b>{i:02d}</b><span>{escape(a["title"])}</span></a>' for i,a in enumerate(items[:5],1))
    content = top + f'<div class="portal-chips">{cats}</div><div class="portal-layout"><section><div class="portal-section-title"><h2>Latest {escape(title)}</h2><span>{len(items)} articles</span></div><div class="portal-grid">{grid}</div></section><aside class="portal-sidebar"><h2>Most Read</h2>{side}</aside></div>'
    d=OUT/folder
    d.mkdir(parents=True, exist_ok=True)
    (d/'index.html').write_text(shell(title, active, content), encoding='utf-8')


def main():
    items=articles()
    section_page('news','News','news','Latest technology news, AI updates, apps, products and practical digital stories.',items,[('All','/news/'),('AI','/news/'),('Smartphones','/mobile/'),('Apps','/tools/'),('Nepal Tech','/news/')])
    section_page('reviews','Reviews','reviews','Hands-on reviews, testing, comparisons and honest buying verdicts.',[a for a in items if 'review' in a['category'].lower()] or items,[('All','/reviews/'),('Phones','/mobile/'),('Laptops','/laptop/'),('Gadgets','/gadgets/')])
    section_page('guides','Buying Guides','guides','Straightforward recommendations for phones, laptops, gadgets, apps and AI tools.',[a for a in items if any(x in (a['category']+' '+a['title']).lower() for x in ['guide','buy','best'])] or items,[('Phones','/mobile/'),('Laptops','/laptop/'),('Gadgets','/gadgets/'),('AI Tools','/tools/')])
    section_page('mobile','Mobile','mobile','Smartphone news, comparisons, buying guides and Nepal-focused mobile coverage.',items,[('Mobile Prices','/mobile/price/'),('Best Phones','/mobile/best/'),('Brands','/brands/'),('Reviews','/reviews/')])
    section_page('laptop','Laptops','laptop','Laptop news, buying advice, reviews and practical recommendations.',items,[('Laptop Prices','/laptop/price/'),('Best Laptops','/laptop/best/'),('Brands','/brands/'),('Reviews','/reviews/')])
    section_page('gadgets','Gadgets','gadgets','Explore tablets, earbuds, smartwatches, cameras, drones, monitors and accessories.',items,[('Tablets','/gadgets/tablets/'),('Audio','/gadgets/audio/'),('Wearables','/gadgets/wearables/'),('Cameras','/gadgets/cameras/')])
    brands=['Apple','Samsung','Xiaomi','Redmi','POCO','OnePlus','OPPO','vivo','Realme','Honor','Google','Nothing','Dell','HP','Lenovo','ASUS','Acer']
    brand_cards=''.join(f'<a class="brand-tile" href="/brands/{re.sub(r"[^a-z0-9]+","-",b.lower()).strip("-")}/"><strong>{escape(b)}</strong><span>News · Reviews · Prices</span></a>' for b in brands)
    content=f'<section class="portal-heading"><span>BRANDS</span><h1>Gadget Brands</h1><p>Explore technology brands, their products, reviews, prices and latest news.</p></section><div class="brand-grid">{brand_cards}</div>'
    d=OUT/'brands';d.mkdir(exist_ok=True);(d/'index.html').write_text(shell('Brands','brands',content),encoding='utf-8')

if __name__=='__main__': main()
