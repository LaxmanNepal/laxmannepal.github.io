from pathlib import Path
from html import escape
import json, re
from datetime import date

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/products.json'
INTEL=ROOT/'data/product-intelligence.json'
OUT=ROOT/'products'

def load(path, fallback):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return fallback

def money(v):
    if isinstance(v,(int,float)): return float(v)
    if isinstance(v,str):
        m=re.search(r'\d+(?:,\d{3})*(?:\.\d+)?',v.replace('NPR','').replace('Rs.',''))
        return float(m.group(0).replace(',','')) if m else None
    return None

def esc(v): return escape(str(v if v is not None else ''))

def spark(history):
    vals=[money(x.get('price')) for x in history]
    vals=[x for x in vals if x is not None]
    if len(vals)<2: return '<span class="v10-no-chart">Not enough history</span>'
    lo,hi=min(vals),max(vals); span=hi-lo or 1; w,h=260,72
    pts=[]
    for i,v in enumerate(vals): pts.append(f'{round(i/(len(vals)-1)*(w-8)+4,1)},{round(h-6-(v-lo)/span*(h-12),1)}')
    return f'<svg class="v10-spark" viewBox="0 0 {w} {h}" role="img" aria-label="Price history trend"><polyline points="{" ".join(pts)}" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><circle cx="{pts[-1].split(",")[0]}" cy="{pts[-1].split(",")[1]}" r="4" fill="currentColor"/></svg>'

def patch_product(path,p,info):
    s=path.read_text(encoding='utf-8')
    drop=info.get('price_drop_percent',0) or 0
    best=info.get('best_verified_price')
    last=info.get('last_verified') or info.get('last_checked')
    badges=''.join([
        '<span class="v10-badge v10-deal">BEST DEAL</span>' if info.get('best_deal') else '',
        f'<span class="v10-badge v10-drop">-{drop}%</span>' if drop>0 else '',
    ])
    panel=f'''<section class="v10-intelligence"><div class="v10-intel-head"><div><span class="eyebrow">BUYING INTELLIGENCE</span><h2>Should you buy this?</h2></div><div class="v10-badges">{badges or '<span class="v10-badge">DATA-DRIVEN</span>'}</div></div><div class="v10-intel-grid"><div class="v10-intel-card"><small>Best verified price</small><strong>{esc(best) if best is not None else 'Not verified'}</strong><span>Checked {esc(last or 'not yet')}</span></div><div class="v10-intel-card"><small>Price trend</small>{spark(p.get('price_history',[]))}<span>{'Falling' if drop>0 else 'History available'}</span></div><div class="v10-intel-card"><small>Buy signal</small><strong>{'GOOD TIME' if drop>=5 else ('WATCH' if drop>0 else 'WAIT FOR VERIFIED DATA')}</strong><span>Based only on available verified catalog data</span></div></div></section>'''
    marker='<section class="product-layout">'
    if 'v10-intelligence' not in s and marker in s: s=s.replace(marker,panel+marker,1)
    path.write_text(s,encoding='utf-8')

def deals(products,intel):
    by={x.get('slug'):x for x in intel.get('products',[])}
    rows=[]
    for p in products:
        i=by.get(p.get('slug'),{})
        score=(1 if i.get('best_deal') else 0, float(i.get('price_drop_percent') or 0), float(i.get('value_score') or 0))
        if score[0] or score[1]>0: rows.append((score,p,i))
    rows.sort(key=lambda x:x[0],reverse=True)
    cards=[]
    for _,p,i in rows[:24]:
        badges=''.join([ '<span class="v10-badge v10-deal">BEST DEAL</span>' if i.get('best_deal') else '', f'<span class="v10-badge v10-drop">-{i.get("price_drop_percent",0)}%</span>' if (i.get('price_drop_percent') or 0)>0 else '' ])
        cards.append(f'<article class="v10-deal-card"><div class="v10-deal-top">{badges}</div><h2><a href="/products/{esc(p.get("slug"))}/">{esc(p.get("name"))}</a></h2><p>{esc(p.get("brand", ""))} · {esc(p.get("category", "Gadget"))}</p><strong>{esc(i.get("best_verified_price") or p.get("price") or "Price not verified")}</strong><a class="v10-view" href="/products/{esc(p.get("slug"))}/">View analysis →</a></article>')
    body=''.join(cards) or '<div class="catalog-empty"><h2>No verified deals yet</h2><p>Add verified product prices and history to unlock deal intelligence.</p></div>'
    html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Data-driven technology deals and price drops."><title>Best Tech Deals | Laxman Nepal</title><link rel="stylesheet" href="/assets/css/gadgetbyte-home.css"><link rel="stylesheet" href="/assets/css/portal-pages.css"><link rel="stylesheet" href="/assets/css/catalog.css"><link rel="stylesheet" href="/assets/css/product-v10.css"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"></head><body class="gb-product-page"><header class="gb-header"><div class="gb-container gb-header-main"><a class="gb-logo" href="/"><span class="gb-logo-mark">LN</span><span>Laxman Nepal</span></a><nav class="gb-menu"><a href="/news/">News</a><a href="/reviews/">Reviews</a><a href="/mobile/">Mobile</a><a href="/laptop/">Laptops</a><a href="/guides/">Guides</a><a href="/gadgets/">Gadgets</a><a href="/products/">Products</a><a href="/brands/">Brands</a><a href="/search/">Search</a></nav><button class="gb-mobile" aria-label="Open menu"><i class="fa-solid fa-bars"></i></button></div><div class="gb-categorybar"><div class="gb-container"><a href="/mobile/">Smartphones</a><a href="/laptop/">Laptops</a><a href="/gadgets/audio/">Audio</a><a href="/gadgets/wearables/">Wearables</a><a href="/mobile/price/">Prices</a></div></div></header><main class="gb-main"><div class="gb-container"><section class="portal-heading price-hero"><span>PRODUCT INTELLIGENCE</span><h1>Best Tech Deals</h1><p>Price drops and deal signals generated from verified catalog data — no invented prices.</p></section><section class="v10-deal-grid">{body}</section></div></main><footer class="gb-footer"><div class="gb-container"><strong>Laxman Nepal</strong><span>Nepal-focused technology news, reviews, guides and product data.</span></div></footer><script>document.querySelector('.gb-mobile')?.addEventListener('click',()=>document.querySelector('.gb-menu')?.classList.toggle('open'));</script></body></html>'''
    d=OUT/'deals'; d.mkdir(parents=True,exist_ok=True); (d/'index.html').write_text(html,encoding='utf-8')

def main():
    products=load(DATA,{'products':[]}).get('products',[])
    intel=load(INTEL,{'products':[]})
    by={x.get('slug'):x for x in intel.get('products',[])}
    for p in products:
        slug=p.get('slug') or re.sub(r'[^a-z0-9]+','-',p.get('name','product').lower()).strip('-')
        target=OUT/slug/'index.html'
        if target.exists(): patch_product(target,p,by.get(slug,{}))
    deals(products,intel)
    print(f'V10 product detail intelligence upgraded: {len(products)} products')

if __name__=='__main__': main()
