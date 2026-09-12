from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT
BASE = 'https://apps.laxmannepal.com.np'
DATA = ROOT / 'data' / 'prices.json'

DEFAULT = {'mobile': [], 'laptop': []}
if DATA.exists():
    try:
        DEFAULT.update(json.loads(DATA.read_text(encoding='utf-8')))
    except Exception:
        pass

def shell(title, active, body):
    nav=''.join(f'<a class="{("active" if k==active else "")}" href="{u}">{l}</a>' for k,l,u in [('news','News','/news/'),('reviews','Reviews','/reviews/'),('mobile','Mobile','/mobile/'),('laptop','Laptops','/laptop/'),('gadgets','Gadgets','/gadgets/'),('guides','Guides','/guides/'),('brands','Brands','/brands/'),('tools','Tools','/tools/')])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{escape(title)} — updated Nepal technology price directory by Laxman Nepal."><meta name="theme-color" content="#111"><title>{escape(title)} · Laxman Nepal</title><link rel="stylesheet" href="/assets/css/style.css"><link rel="stylesheet" href="/assets/css/light.css"><link rel="stylesheet" href="/assets/css/gadgetbyte-home.css"><link rel="stylesheet" href="/assets/css/portal-pages.css"><link rel="stylesheet" href="/assets/css/price-pages.css"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"></head><body class="gb-page portal-page"><header class="gb-header"><div class="gb-container gb-header-main"><a class="gb-logo" href="/"><span class="gb-logo-mark">LN</span><span>Laxman Nepal</span></a><nav class="gb-menu">{nav}</nav><form class="gb-search" action="/search/" method="get"><input name="q" type="search" placeholder="Search technology..." aria-label="Search"><button aria-label="Search"><i class="fa-solid fa-magnifying-glass"></i></button></form><button class="gb-mobile" id="price-menu" aria-label="Open menu"><i class="fa-solid fa-bars"></i></button></div><div class="gb-category"><div class="gb-container"><a href="/mobile/">Smartphones</a><a href="/laptop/">Laptops</a><a href="/gadgets/tablets/">Tablets</a><a href="/gadgets/audio/">Audio</a><a href="/gadgets/wearables/">Wearables</a><a href="/reviews/">Reviews</a><a href="/guides/">Buying Guides</a><a href="/brands/">Brands</a><a href="/tools/">Apps & Tools</a></div></div></header><div class="gb-breaking"><div class="gb-container"><span class="gb-breaking-label">PRICE DIRECTORY</span><div class="gb-breaking-track">Nepal gadget prices · Mobile prices · Laptop prices · Buying guides · Reviews</div></div></div><main class="portal-main"><div class="gb-container">{body}</div></main><footer class="gb-footer"><div class="gb-container"><div class="gb-footer-grid"><div><h3>Laxman Nepal</h3><p>Practical technology news, reviews, guides and Nepal-focused price information.</p></div><div><h3>Prices</h3><a href="/mobile/price/">Mobile Prices</a><a href="/laptop/price/">Laptop Prices</a></div><div><h3>Explore</h3><a href="/guides/">Buying Guides</a><a href="/reviews/">Reviews</a><a href="/brands/">Brands</a></div></div><div class="gb-footer-bottom"><span>© <span id="year"></span> Laxman Nepal</span><span>Prices are data-driven and should be verified before purchase.</span></div></div></footer><script>const y=document.getElementById('year');if(y)y.textContent=new Date().getFullYear();document.getElementById('price-menu')?.addEventListener('click',()=>document.querySelector('.gb-menu')?.classList.toggle('open'));</script></body></html>'''

def make(kind, title, intro):
    rows=DEFAULT.get(kind, [])
    brands=[]
    for item in rows:
        brand=item.get('brand','Other')
        if brand not in brands: brands.append(brand)
    options=''.join(f'<button class="price-filter" data-brand="{escape(b,quote=True)}">{escape(b)}</button>' for b in brands)
    groups=[]
    for brand in brands:
        items=[x for x in rows if x.get('brand','Other')==brand]
        trs=''.join(f'<tr><td><strong>{escape(x.get("model",""))}</strong>{("<small>"+escape(x.get("variant",""))+"</small>") if x.get("variant") else ""}</td><td>{escape(x.get("specs","—"))}</td><td class="price">{escape(x.get("price","—"))}</td></tr>' for x in items)
        groups.append(f'<section class="price-brand" data-brand="{escape(brand,quote=True)}"><div class="price-brand-head"><h2>{escape(brand)}</h2><span>{len(items)} models</span></div><div class="price-table-wrap"><table><thead><tr><th>Model</th><th>Configuration</th><th>Price in Nepal</th></tr></thead><tbody>{trs}</tbody></table></div></section>')
    if not groups:
        groups=['<section class="price-empty"><div class="price-empty-icon"><i class="fa-solid fa-tags"></i></div><h2>Price database is ready</h2><p>No verified price entries have been published yet. Add products to <code>data/prices.json</code> and this page will automatically build brand sections, filters and tables.</p><a href="/guides/">Explore buying guides →</a></section>']
    body=f'''<section class="portal-heading price-hero"><span>NEPAL PRICE DIRECTORY</span><h1>{escape(title)}</h1><p>{escape(intro)}</p><div class="price-tools"><input id="price-search" type="search" placeholder="Search model or brand..." aria-label="Search prices"><span id="price-count"></span></div></section><div class="price-filters"><button class="price-filter active" data-brand="">All brands</button>{options}</div><div id="price-groups">{''.join(groups)}</div><section class="price-note"><i class="fa-solid fa-circle-info"></i><div><strong>Price accuracy matters.</strong><p>Only publish verified distributor or retailer pricing in the data file. Include the last verified date when the database is expanded.</p></div></section><script>(function(){const q=document.getElementById('price-search'),buttons=[...document.querySelectorAll('.price-filter')],groups=[...document.querySelectorAll('.price-brand')],count=document.getElementById('price-count');let brand='';function run(){const term=(q.value||'').toLowerCase().trim();let visible=0;groups.forEach(g=>{const okBrand=!brand||g.dataset.brand===brand;const okText=!term||g.innerText.toLowerCase().includes(term);g.hidden=!(okBrand&&okText);if(okBrand&&okText)visible++});count.textContent=visible+' brand section'+(visible===1?'':'s')+' shown'}buttons.forEach(b=>b.addEventListener('click',()=>{buttons.forEach(x=>x.classList.remove('active'));b.classList.add('active');brand=b.dataset.brand;run()}));q.addEventListener('input',run);run()})();</script>'''
    folder=OUT/kind/'price';folder.mkdir(parents=True,exist_ok=True)
    (folder/'index.html').write_text(shell(title,kind,body),encoding='utf-8')

make('mobile','Mobile Prices in Nepal','Browse smartphone models and configurations with a clean, searchable Nepal price directory.')
make('laptop','Laptop Prices in Nepal','Browse laptop models and configurations with a clean, searchable Nepal price directory.')
print('Generated mobile and laptop price pages.')
