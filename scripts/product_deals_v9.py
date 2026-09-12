from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PRODUCTS=ROOT/'products'

SORT='<select id="product-sort"><option value="relevance">Best value</option><option value="deals">Biggest price drops</option><option value="price">Lowest verified price</option><option value="verified">Recently verified</option></select>'

def main():
    index=PRODUCTS/'index.html'
    if index.exists():
        s=index.read_text(encoding='utf-8')
        marker='<select id="product-category"><option>All categories</option></select>'
        if marker in s and 'id="product-sort"' not in s:
            s=s.replace(marker,marker+SORT)
        s=s.replace('<p>Search verified products, filter by brand or category, inspect detailed data and compare up to four products.</p>','<p>Search verified products, sort by value or price drops, inspect detailed data and compare up to four products.</p>')
        index.write_text(s,encoding='utf-8')
    hub=PRODUCTS/'deals'; hub.mkdir(parents=True,exist_ok=True)
    body='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Best verified technology deals and price drops in the Laxman Nepal product database."><title>Best Tech Deals | Laxman Nepal</title><link rel="stylesheet" href="/assets/css/gadgetbyte-home.css"><link rel="stylesheet" href="/assets/css/portal-pages.css"><link rel="stylesheet" href="/assets/css/catalog.css"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"></head><body class="gb-product-page"><header class="gb-header"><div class="gb-container gb-header-main"><a class="gb-logo" href="/"><span class="gb-logo-mark">LN</span><span>Laxman Nepal</span></a><nav class="gb-menu"><a href="/news/">News</a><a href="/reviews/">Reviews</a><a href="/mobile/">Mobile</a><a href="/laptop/">Laptops</a><a href="/guides/">Guides</a><a href="/gadgets/">Gadgets</a><a href="/products/">Products</a><a href="/brands/">Brands</a><a href="/search/">Search</a></nav><button class="gb-mobile" aria-label="Open menu"><i class="fa-solid fa-bars"></i></button></div></header><main class="gb-main"><div class="gb-container"><section class="portal-heading price-hero"><span>DEAL INTELLIGENCE</span><h1>Best Tech Deals</h1><p>Price-drop and value rankings are generated only from verified product and price data. Missing data is never invented.</p></section><section id="deal-grid" class="product-grid-catalog"><div class="catalog-empty">Loading deal intelligence…</div></section></div></main><footer class="gb-footer"><div class="gb-container"><strong>Laxman Nepal</strong><span>Nepal-focused technology news, reviews, guides and product data.</span></div></footer><script src="/assets/js/product-deals-v9.js"></script><script>document.querySelector('.gb-mobile')?.addEventListener('click',()=>document.querySelector('.gb-menu')?.classList.toggle('open'));</script></body></html>'''
    (hub/'index.html').write_text(body,encoding='utf-8')
    print('V9 deal hub generated')
if __name__=='__main__': main()
