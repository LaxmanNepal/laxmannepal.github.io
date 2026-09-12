from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "products.json"
OUT = ROOT / "products"


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def shell(title, description, body):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} | Laxman Nepal</title><meta name="description" content="{escape(description)}"><link rel="stylesheet" href="/assets/css/gadgetbyte-home.css"><link rel="stylesheet" href="/assets/css/portal-pages.css"><link rel="stylesheet" href="/assets/css/product-pages.css"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"></head><body class="gb-product-page"><header class="gb-header"><div class="gb-container gb-nav"><a class="gb-logo" href="/"><strong>LAXMAN</strong><span>NEPAL</span></a><nav><a href="/news/">News</a><a href="/reviews/">Reviews</a><a href="/mobile/">Mobile</a><a href="/laptop/">Laptops</a><a href="/guides/">Buying Guides</a><a href="/gadgets/">Gadgets</a><a href="/brands/">Brands</a><a href="/search/">Search</a></nav></div></header><div class="gb-categorybar"><div class="gb-container"><a href="/mobile/">Smartphones</a><a href="/laptop/">Laptops</a><a href="/gadgets/tablets/">Tablets</a><a href="/gadgets/audio/">Audio</a><a href="/gadgets/wearables/">Wearables</a><a href="/gadgets/cameras/">Cameras</a></div></div>{body}<footer class="gb-footer"><div class="gb-container"><strong>Laxman Nepal</strong><span>Technology, reviews, buying guides and useful tools.</span></div></footer></body></html>'''


def product_card(p):
    return f'''<a class="product-mini" href="/products/{escape(p['slug'])}/"><div class="product-mini-media">{('<img src="'+escape(p['image'])+'" alt="" loading="lazy">') if p.get('image') else '<i class="fa-solid fa-mobile-screen-button"></i>'}</div><strong>{escape(p['name'])}</strong><small>{escape(p.get('brand',''))} · {escape(p.get('category',''))}</small></a>'''


def page(p, products):
    name = p["name"]
    brand = p.get("brand", "")
    category = p.get("category", "Gadgets")
    price = p.get("price")
    price_text = escape(str(price)) if price not in (None, "") else "Price not listed"
    specs = p.get("specifications", {})
    related = [x for x in products if x.get("slug") != p["slug"] and (x.get("category") == category or x.get("brand") == brand)][:4]
    image = f'<img class="product-hero-image" src="{escape(p["image"])}" alt="{escape(name)}" loading="eager">' if p.get("image") else '<div class="product-image-placeholder"><i class="fa-solid fa-mobile-screen-button"></i><span>Add product image in products.json</span></div>'
    spec_rows = ''.join(f'<div class="spec-row"><span>{escape(str(k))}</span><strong>{escape(str(v))}</strong></div>' for k,v in specs.items()) or '<div class="empty-note">Specifications will appear here when verified data is added.</div>'
    pros = ''.join(f'<li>{escape(str(x))}</li>' for x in p.get("pros", [])) or '<li>Not added yet</li>'
    cons = ''.join(f'<li>{escape(str(x))}</li>' for x in p.get("cons", [])) or '<li>Not added yet</li>'
    rating = p.get("rating")
    rating_block = f'<div class="rating"><strong>{escape(str(rating))}</strong><span>/ 10</span></div>' if rating not in (None, "") else '<div class="rating muted">No verified rating yet</div>'
    related_html = ''.join(product_card(x) for x in related) or '<div class="empty-note">Related products will appear as the catalog grows.</div>'
    body = f'''<main class="gb-main"><div class="gb-container"><div class="breadcrumbs"><a href="/">Home</a><span>/</span><a href="/{escape(category.lower().replace(" ", "-"))}/">{escape(category)}</a><span>/</span><strong>{escape(name)}</strong></div><section class="product-hero"><div class="product-visual">{image}</div><div class="product-intro"><span class="eyebrow">{escape(brand)} · {escape(category)}</span><h1>{escape(name)}</h1><p>{escape(p.get('summary', 'Product details, specifications, pricing and buying information.'))}</p><div class="product-price"><small>Best listed price</small><strong>{price_text}</strong></div><div class="product-actions"><a class="btn-primary" href="/compare/?a={escape(p['slug'])}"><i class="fa-solid fa-code-compare"></i> Compare</a><button class="btn-secondary" type="button" onclick="navigator.share?.({{title:document.title,url:location.href}})"><i class="fa-solid fa-share-nodes"></i> Share</button></div></div></section><section class="product-layout"><div><section class="product-section"><div class="section-heading"><span>01</span><h2>Key specifications</h2></div><div class="spec-grid">{spec_rows}</div></section><section class="product-section"><div class="section-heading"><span>02</span><h2>Pros &amp; cons</h2></div><div class="pros-cons"><div><h3><i class="fa-solid fa-circle-check"></i> Pros</h3><ul>{pros}</ul></div><div><h3><i class="fa-solid fa-circle-xmark"></i> Cons</h3><ul>{cons}</ul></div></div></section></div><aside class="product-sidebar"><div class="score-card"><span>Review score</span>{rating_block}<small>{escape(p.get('rating_note','Only verified editorial/user ratings should be added.'))}</small></div><div class="info-card"><strong>Best for</strong><p>{escape(p.get('best_for','Everyday use'))}</p></div></aside></section><section class="product-section"><div class="section-heading"><span>03</span><h2>Related products</h2></div><div class="product-mini-grid">{related_html}</div></section></div></main>'''
    return shell(name, p.get("summary", f"{name} specifications, price and buying information."), body)


def main():
    try:
        raw = json.loads(DATA.read_text(encoding="utf-8"))
    except Exception:
        raw = {"products": []}
    products = raw.get("products", [])
    OUT.mkdir(exist_ok=True)
    for p in products:
        p = dict(p)
        p.setdefault("slug", slugify(p.get("name", "product")))
        (OUT / p["slug"]).mkdir(parents=True, exist_ok=True)
        (OUT / p["slug"] / "index.html").write_text(page(p, products), encoding="utf-8")
    print(f"Generated {len(products)} product pages")


if __name__ == "__main__":
    main()
