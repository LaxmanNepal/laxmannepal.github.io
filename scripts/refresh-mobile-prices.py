#!/usr/bin/env python3
"""Build a conservative Nepal phone catalogue from public retailer/product listings.

Only prices and specifications actually found on a page are published. A retailer
price is kept separate by store and variant; failed or ambiguous matches are omitted.
"""
from __future__ import annotations
import copy, json, math, re, time, hashlib, html
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

OUT = Path("data/mobile-prices.json")
HISTORY_OUT = Path("data/mobile-price-history.json")
STATUS_OUT = Path("data/mobile-price-refresh-status.json")
DETAIL_ROOT = Path("mobile-price-in-nepal/phones")
TODAY = datetime.now(timezone.utc).date().isoformat()
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}

# Public store category pages. The store label is what readers see; source provenance
# is kept in each price record as a direct product/listing URL for price verification.
SOURCES = [
    {"store":"Oliz Store","url":"https://cdn.olizstore.com/collections/phone","kind":"shopify"},
    {"store":"Brother Mart","url":"https://brother-mart.com/collections/smartphones-mobilephones-price-in-nepal","kind":"shopify"},
    {"store":"Neo Store","url":"https://www.neostore.com.np/product-category/mobile-brands","kind":"shop"},
    {"store":"GBN Store","url":"https://gbnstore.com/category/smartphones","kind":"catalog"},
    {"store":"Quality Computer","url":"https://qualitycomputer.com.np/shop?category=833&order=create_date+desc","kind":"shop"},
    {"store":"National Mobile","url":"https://store.nationalmobile.com.np/mobile-price-nepal/","kind":"shop"},

    {"store":"Daraz","url":"https://www.daraz.com.np/smartphones/","kind":"marketplace"},
]
SOURCES += [{"store":"GBN Store","url":f"https://gbnstore.com/category/smartphones?page={page}","kind":"catalog"} for page in range(2,9)]
BRANDS = ["Apple","Samsung","Xiaomi","Redmi","Poco","OnePlus","Vivo","OPPO","Realme","Motorola","Nothing","Honor","Huawei","Tecno","Infinix","Nokia","Google","iQOO","Itel","ZTE","Lava","CMF","Lenovo","Blackview"]
PRICE_RE = re.compile(r"(?:NPR|Rs\s*\.?|रु\s*\.?|रु)\s*([\d,]{4,10})", re.I)
VARIANT_RE = re.compile(r"\b(\d{1,2})\s*(?:GB)?\s*(?:\+|/|RAM)\s*(\d{2,4})\s*GB\b", re.I)

def clean(v): return re.sub(r"\s+", " ", str(v or "")).strip()
def request_with_retry(url, timeout=(4,10)):
    """Retry transient retailer timeouts/rate limits before declaring a source unavailable."""
    last_error = None
    for attempt in range(3):
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
    raise last_error

def fetch(url):
    return BeautifulSoup(request_with_retry(url).text,"html.parser")
def money(text):
    """Only accept text with one distinct currency amount."""
    matches=PRICE_RE.findall(clean(text))
    values=list(dict.fromkeys(int(v.replace(",","")) for v in matches))
    return values[0] if len(values)==1 and 1000 < values[0] < 3000000 else None

def current_price(root):
    """Prefer explicit current/sale price fields, never guess among crossed-out prices."""
    selectors=(
        'meta[itemprop="price"]','meta[property="product:price:amount"]',
        'meta[property="og:price:amount"]','ins .amount','ins .woocommerce-Price-amount',
        '.price ins','[class*="current-price"]','[class*="special-price"]',
        '.price .amount','.woocommerce-Price-amount','[itemprop="price"]'
    )
    for selector in selectors:
        for tag in root.select(selector):
            raw=tag.get("content") or tag.get("value") or tag.get("data-price") or tag.get_text(" ",strip=True)
            match=PRICE_RE.search(str(raw))
            classes=" ".join(tag.get("class",[]))
            old_parent=tag.find_parent(["del","s"]) or tag.find_parent(class_=re.compile(r"old|compare|strike|regular-price",re.I))
            if old_parent or re.search(r"old|compare|strike|regular-price",classes,re.I):
                continue
            if match:
                value=int(match.group(1).replace(",",""))
            else:
                digits=re.sub(r"[^0-9.]","",str(raw))
                try: value=int(float(digits)) if digits else None
                except Exception: value=None
            if value and 1000 < value < 3000000: return value
    # When the retailer uses crossed-out and sale prices without standard classes,
    # remove old-price markup before accepting the single remaining amount.
    clean_root=BeautifulSoup(str(root),"html.parser")
    for old_tag in clean_root.select("del,s,.old-price,[class*='old-price'],[class*='compare-at'],[class*='regular-price']"):
        old_tag.decompose()
    return money(clean_root.get_text(" ",strip=True))
def is_phone_title(title):
    t=clean(title)
    if len(t)>110 or len(t.split())<2: return False
    if re.search(r"\b(accessories|accessory|headphones|earphones|earbuds|buds|watch|smartwatch|smart watch|tablet|tablets|tab|pad|ipad|book|laptop|notebook|smarttag|smart tag|fitness tracker|smart band|choice\s+t\d+|mobile brands|phone brands|mobile accessories|phone cases|charger|charging cable|power bank|buy a phone|mobile price|phones list)\b",t,re.I): return False
    family=bool(re.search(r"\b(iphone|galaxy|redmi|poco|pixel|oneplus|vivo|oppo|realme|motorola|nothing|honor|infinix|tecno|nokia|samsung|xiaomi|cmf|nubia|zte|magic|spark|camon|hot|blackview)\b|\bai\+",t,re.I))
    has_brand=any(re.search(r"\b"+re.escape(b)+r"\b",t,re.I) for b in BRANDS)
    has_model=bool(re.search(r"\b(\d{1,4}[a-z]?|[A-Z]\d{1,4}|SE|Fold|Flip|Ultra|Pro|Plus|Lite|Note|Edge|Neo|Air|Max|Play|Spark|Camon|Hot|Smart)\b",t,re.I))
    return (family or has_brand) and has_model

def brand_for(name):
    if re.search(r"\biphone\b",name,re.I): return "Apple"
    if re.search(r"\bai\+",name,re.I): return "Ai+"
    for b in sorted(BRANDS,key=len,reverse=True):
        if re.search(r"\b"+re.escape(b)+r"\b",name,re.I):
            return "OPPO" if b.lower()=="oppo" else b
    return "Other"
def slugify(text):
    s=re.sub(r"[^a-z0-9]+","-",text.lower()).strip("-")
    return s[:90] or hashlib.sha1(text.encode()).hexdigest()[:12]
def jsonld_objects(soup):
    out=[]
    for tag in soup.select('script[type="application/ld+json"]'):
        try:
            val=json.loads(tag.string or tag.get_text())
            stack=val if isinstance(val,list) else [val]
            while stack:
                obj=stack.pop()
                if isinstance(obj,dict):
                    if isinstance(obj.get("@graph"),list): stack.extend(obj["@graph"])
                    out.append(obj)
                elif isinstance(obj,list): stack.extend(obj)
        except Exception: pass
    return out
def product_meta(soup, fallback_name):
    title=fallback_name; image=None; price=None; desc=None; availability=None; specs={}
    for obj in jsonld_objects(soup):
        typ=obj.get("@type",[])
        if isinstance(typ,str): typ=[typ]
        if "Product" not in typ: continue
        title=clean(obj.get("name") or title)
        desc=clean(obj.get("description"))
        im=obj.get("image")
        if isinstance(im,list): im=im[0] if im else None
        if isinstance(im,dict): im=im.get("url")
        if im: image=urljoin(str(soup.base.get("href")) if soup.base else "",str(im))
        offers=obj.get("offers",{})
        if isinstance(offers,list): offers=offers[0] if offers else {}
        if isinstance(offers,dict):
            availability=clean(offers.get("availability")) or None
            try: price=int(float(offers.get("price") or offers.get("lowPrice") or 0)) or None
            except Exception: pass
        break
    if not image:
        tag=soup.select_one('meta[property="og:image"],meta[name="twitter:image"]')
        if tag: image=tag.get("content")
    if not desc:
        tag=soup.select_one('meta[name="description"]')
        if tag: desc=clean(tag.get("content"))
    if not price:
        for tag in soup.select('meta[property="product:price:amount"],meta[itemprop="price"],meta[property="og:price:amount"]'):
            price=money(tag.get("content",""))
            if price: break
    text=clean(soup.get_text(" ",strip=True))
    if not price: price=current_price(soup)
    # Structured feature tables and explicit label/value rows only.
    for row in soup.select("tr, .woocommerce-product-attributes-item, .product-info-item, li"):
        bits=[clean(x.get_text(" ",strip=True)) for x in row.select("th,td,.label,.value,strong,b")]
        if len(bits)>=2:
            k=bits[0].lower().rstrip(":")
            v=bits[-1]
            if k and v and len(v)<120: specs[k]=v
    return {"title":title,"image":image,"price":price,"availability":availability,"description":desc,"specs":specs,"text":text}
def parse_listing(source):
    if source.get("kind")=="shopify":
        api=source["url"].rstrip("/")+"/products.json?limit=250"
        try:
            products=[]
            next_url=api
            seen_pages=set()
            # Shopify's public JSON feed exposes cursor pagination in the Link header.
            for _ in range(5):
                if not next_url or next_url in seen_pages:
                    break
                seen_pages.add(next_url)
                response=request_with_retry(next_url,timeout=12)
                products.extend(response.json().get("products",[]))
                next_url=(response.links.get("next") or {}).get("url")
            items=[]
            for product in products:
                title=clean(product.get("title"))
                if not is_phone_title(title): continue
                images=product.get("images") or []
                image=(images[0].get("src") if images and isinstance(images[0],dict) else None)
                handle=product.get("handle")
                if not handle: continue
                href=urljoin(source["url"],"/products/"+handle)
                for variant in product.get("variants") or []:
                    if variant.get("available") is False: continue
                    try: price=int(float(variant.get("price") or 0)) or None
                    except Exception: price=None
                    variant_title=clean(variant.get("public_title") or variant.get("title"))
                    full_title=title if not variant_title or variant_title.lower()=="default title" else title+" "+variant_title
                    if price and not (1000 < price < 3000000): price=None
                    description=clean(BeautifulSoup(product.get("body_html") or "", "html.parser").get_text(" ",strip=True))
                    items.append({"store":source["store"],"title":full_title,"url":href,"price":price,"image":image,"description":description,"text":description,"kind":"shopify"})
            if items:
                print(f'{source["store"]}: Shopify feed returned {len(items)} phone variants')
                return items
            print(f'{source["store"]}: Shopify feed had no available phone variants; falling back to page parser')
        except Exception as exc:
            print(f'{source["store"]}: Shopify feed unavailable ({exc}); falling back to page parser')
    fallback_kind="shop" if source.get("kind")=="shopify" else source["kind"]
    soup=fetch(source["url"])
    found=[]
    # Prefer cards/product links. Restrict to links with a visible price in the same card.
    selectors=[".product","li.product",".product-item",".product-card","article",".jeg_post","tr"]
    nodes=[]
    for sel in selectors:
        nodes=soup.select(sel)
        if len(nodes)>=3: break
    for node in nodes:
        text=clean(node.get_text(" ",strip=True))
        if len(text)<8 or re.search(r"\b(out of stock|sold out|unavailable)\b",text,re.I): continue
        price=current_price(node)
        anchors=node.select('a[href]')
        if not anchors: continue
        # Choose the longest plausible product title link, avoiding category/navigation links.
        choices=[]
        for a in anchors:
            img_tag=a.select_one("img")
            title=clean(a.get("aria-label") or a.get("title") or a.get_text(" ",strip=True) or (img_tag.get("alt") if img_tag else ""))
            href=urljoin(source["url"],a.get("href",""))
            if "error.html" in href.lower() or "/error/" in href.lower(): continue
            path=urlparse(href).path.lower()
            if len(title)<5 or href==source["url"] or any(x in path for x in ["/cart","/account","/category/","/collections/","/product-category/","/tag/"]): continue
            if not is_phone_title(title): continue
            choices.append((len(title),title,href,a))
        if not choices: continue
        _,title,href,a=max(choices,key=lambda x:x[0])
        # Prefer the product image inside this card.
        img=node.select_one("img")
        image=None
        if img:
            image=img.get("data-src") or img.get("data-lazy-src") or img.get("src") or img.get("srcset","").split(",")[0].split(" ")[0]
            if image: image=urljoin(source["url"],image)
        # If a listing price exists, it's evidence for that store. If absent, fetch product page.
        found.append({"store":source["store"],"title":title,"url":href,"source_url":source["url"],"price":price,"image":image,"description":text,"text":text,"kind":fallback_kind})
    # Product cards are often rendered differently; fall back to visible links then inspect pages.
    if not found:
        for a in soup.select('a[href]'):
            img_tag=a.select_one("img")
            title=clean(a.get("aria-label") or a.get("title") or a.get_text(" ",strip=True) or (img_tag.get("alt") if img_tag else ""))
            href=urljoin(source["url"],a.get("href",""))
            if "error.html" in href.lower() or "/error/" in href.lower(): continue
            parent_text=clean(a.parent.get_text(" ",strip=True) if a.parent else "")
            if re.search(r"\b(out of stock|sold out|unavailable)\b",parent_text,re.I): continue
            if len(title)<7 or not is_phone_title(title): continue
            if urlparse(href).netloc!=urlparse(source["url"]).netloc: continue
            found.append({"store":source["store"],"title":title,"url":href,"source_url":source["url"],"price":None,"image":None,"kind":source["kind"]})
    # De-dupe listing candidates by URL.
    unique={}
    for item in found: unique.setdefault(item["url"],item)
    return list(unique.values())
def variant_key(title):
    m=VARIANT_RE.search(title)
    if m: return f"{m.group(1)}GB/{m.group(2)}GB"
    m=re.search(r"\b(\d{1,2})\s*GB\s*\+\s*(\d{2,4})\s*GB\b",title,re.I)
    if m: return f"{m.group(1)}GB/{m.group(2)}GB"
    m=re.search(r"\b(\d{1,2})\s*GB\s+(?:RAM\s*)?(\d{2,4})\s*GB\b",title,re.I)
    if m: return f"{m.group(1)}GB/{m.group(2)}GB"
    storage=re.findall(r"\b(32|64|128|256|512|1024)\s*GB\b",title,re.I)
    return (storage[-1]+"GB") if storage else ""

def normalize_model(title):
    # Strip retailer SEO copy, camera/processor marketing and colour names before matching stores.
    s=clean(title)
    s=re.split(r"\s*[|–—]\s*",s)[0]
    s=re.sub(r"\s*(?:price\s+in\s+nepal|price\s+nepal).*$","",s,flags=re.I)
    s=re.sub(r"\s+\d[\d,]*\s*mAh.*$","",s,flags=re.I)
    s=re.sub(r"\s+(?:with|featuring)\b.*$","",s,flags=re.I)
    s=re.sub(r"\s+smartphone\b.*$","",s,flags=re.I)
    s=re.sub(r"\s*:\s*.*$","",s)
    s=re.sub(r"\s+\d{1,2}(?:\.\d+)?\s*(?:inch(?:es)?|[\"″]).*$","",s,flags=re.I)
    s=re.sub(r"\s+\d{2,3}\s*MP\b.*$","",s,flags=re.I)
    s=re.sub(r"\s+(?:A\d{1,2}\s+Bionic|Snapdragon\b|Dimensity\b|MediaTek\b|Helio\b|Exynos\b).*$","",s,flags=re.I)
    s=re.sub(r"\s+(?:32|64|128|256|512|1024)\s*GB(?:\s*(?:storage|rom))?$","",s,flags=re.I)
    s=re.sub(r"\b\d{1,2}\s*GB\s*(?:\+|/|RAM|\s+)\s*\d{2,4}\s*GB\b"," ",s,flags=re.I)
    s=re.sub(r"\b\d{1,2}\s*\+\s*\d{2,4}\s*GB\b"," ",s,flags=re.I)
    s=re.sub(r"\([^)]*(?:GB|RAM|ROM|storage)[^)]*\)"," ",s,flags=re.I)
    s=re.sub(r"\s+(?:awesome\s+\w+|midnight\s+black|sunrise\s+gold|ocean\s+blue|forest\s+green|diary\s+white|aston\s+martin\s+green|black|blue|pink|green|silver|white|orange|purple|gray|grey|gold|yellow|cream|teal|ultramarine|titanium|brown|lavender)\s*$","",s,flags=re.I)
    s=re.sub(r"\s+"," ",s).strip(" -|·")
    return s
def extract_specs(title, text, specs_map):
    blob=title+" "+text
    ram=storage=display=battery=chipset=camera=None
    # Prefer explicit row labels from the product page.
    def labelled(keys):
        for k,v in specs_map.items():
            if any(x in k for x in keys) and v and len(v)<80: return v
        return None
    ram=labelled(["ram","memory"])
    storage=labelled(["storage","rom","internal"])
    display=labelled(["display","screen"])
    battery=labelled(["battery","capacity"])
    chipset=labelled(["processor","chipset","cpu"])
    camera=labelled(["camera"])
    if not ram:
        m=re.search(r"\b(\d{1,2})\s*GB\s*RAM\b",blob,re.I); ram=m.group(1)+"GB" if m else None
    if not storage:
        m=re.search(r"\b(\d{2,4})\s*GB\s*(?:ROM|storage|internal storage)\b",blob,re.I); storage=m.group(1)+"GB" if m else None
    if not display:
        m=re.search(r"(\d(?:\.\d{1,2})?)\s*(?:-inch|inch|inches|″)",blob,re.I); display=m.group(1)+" inch" if m else None
    if not battery:
        m=re.search(r"\b(\d{3,5})\s*mAh\b",blob,re.I); battery=m.group(1)+"mAh" if m else None
    if not chipset:
        m=re.search(r"(?:Snapdragon|Dimensity|Helio|Exynos|Tensor|A\d+ Bionic)[^,.;]{0,45}",blob,re.I); chipset=clean(m.group(0)) if m else None
    if not camera:
        m=re.search(r"\b(\d{2,3})\s*MP\b",blob,re.I); camera=m.group(0) if m else None
    return {"ram":clean(ram) or None,"storage":clean(storage) or None,"display":clean(display) or None,"battery":clean(battery) or None,"chipset":clean(chipset) or None,"camera":clean(camera) or None}
def page_template(p):
    title=p["model"]; prices=p.get("prices",[])
    checked_date=p.get("updated_at") or TODAY
    fresh_prices=[x for x in prices if x.get("price") and not x.get("stale")]
    best=min(fresh_prices or [x for x in prices if x.get("price")],key=lambda x:x["price"],default=None)
    esc=lambda x:html.escape(str(x or ""),quote=True)
    canonical="https://laxmannepal.com.np/mobile-price-in-nepal/phones/"+p["slug"]+"/"
    price_rows="".join(f'<tr><td><a href="{esc(x["url"])}" target="_blank" rel="nofollow sponsored noopener">{esc(x["store"])}</a></td><td>Rs. {int(x["price"]):,}</td><td>{esc(x.get("warranty") or "Check with store")}</td><td>{esc(("STALE · " if x.get("stale") else "") + str(x.get("checked_at") or TODAY))}</td><td><a href="{esc(x["url"])}" target="_blank" rel="nofollow sponsored noopener">View offer ↗</a></td></tr>' for x in sorted(prices,key=lambda x:x.get("price") or 10**12))
    specs=[("Brand",p.get("brand")),("RAM",p.get("ram")),("Storage",p.get("storage")),("Display",p.get("display")),("Battery",p.get("battery")),("Chipset",p.get("chipset")),("Camera",p.get("camera"))]
    spec_rows="".join(f'<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>' for k,v in specs if v)
    seen_labels={k.lower() for k,v in specs if v}
    spec_rows += "".join(f'<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>' for k,v in (p.get("specifications") or {}).items() if v and k.lower() not in seen_labels)
    image=p.get("image") or ""
    jsonld={"@context":"https://schema.org","@type":"Product","name":title,"image":[image] if image else [],"brand":{"@type":"Brand","name":p.get("brand","Other")},"description":f"{title} Nepal price comparison, specifications and retailer offers.","url":canonical}
    if best and not p.get("price_is_stale"): jsonld["offers"]={"@type":"AggregateOffer","priceCurrency":"NPR","lowPrice":best["price"],"offerCount":sum(1 for x in prices if not x.get("stale")),"url":best["url"]}
    structured=json.dumps(jsonld,ensure_ascii=False).replace("</","<\\/")
    image_html=f'<img src="{esc(image)}" alt="{esc(title)} smartphone" loading="eager">' if image else '<div class="placeholder">📱</div>'
    best_html=(("Last known · " if p.get("price_is_stale") else "")+f'Rs. {best["price"]:,}') if best else 'No verified retailer price yet'
    history=p.get("history",[])
    valid_history=[h for h in history if h.get("price")]
    if len(valid_history)>=2:
        vals=[int(h["price"]) for h in valid_history]
        lo,hi=min(vals),max(vals)
        span=max(1,hi-lo)
        points=" ".join(f'{18+i*564/max(1,len(vals)-1):.1f},{128-(v-lo)/span*100:.1f}' for i,v in enumerate(vals))
        history_html=f'<section class="panel"><h2>Recorded price history</h2><p class="muted">{len(valid_history)} daily observations. This chart shows the lowest tracked offer recorded on each successful refresh, not a guaranteed current quote.</p><div style="width:100%;overflow:hidden"><svg viewBox="0 0 600 150" role="img" aria-label="Historical lowest phone price chart" style="width:100%;height:auto;max-height:220px"><line x1="18" y1="128" x2="582" y2="128" stroke="#d0d5dd"/><polyline points="{points}" fill="none" stroke="#2563eb" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/></svg></div><p class="muted">Lowest recorded: Rs. {lo:,} · Highest recorded: Rs. {hi:,} · Latest observation: {esc(valid_history[-1].get("date"))}</p></section>'
    else:
        history_html='<section class="panel"><h2>Recorded price history</h2><p class="muted">Price history is being collected. A trend will appear after at least two successful daily refreshes for this phone.</p></section>'
    body=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} Price in Nepal, Specs & Store Offers | Laxman Nepal</title><meta name="description" content="Compare {esc(title)} price in Nepal across stores. See the lowest recorded offer, store-wise prices, full available specifications and product images."><link rel="canonical" href="{canonical}"><meta property="og:title" content="{esc(title)} Price in Nepal & Full Specifications"><meta property="og:description" content="Compare retailer prices and specifications for {esc(title)} in Nepal."><meta property="og:type" content="product"><meta property="og:image" content="{esc(image)}"><script type="application/ld+json">{structured}</script><style>*{{box-sizing:border-box}}body{{margin:0;background:#f7f8fb;color:#101828;font:16px system-ui,sans-serif}}main{{max-width:1100px;margin:auto;padding:24px 16px 60px}}a{{color:#2563eb}}.back{{display:inline-block;margin:6px 0 22px}}.hero,.panel{{background:#fff;border:1px solid #e4e7ec;border-radius:20px;padding:clamp(18px,4vw,34px);margin-bottom:18px}}.hero{{display:grid;grid-template-columns:minmax(200px, .8fr) 1.2fr;gap:28px;align-items:center}}.photo{{min-height:250px;display:grid;place-items:center;background:#f8fafc;border-radius:16px;padding:15px}}.photo img{{width:100%;height:280px;object-fit:contain}}.placeholder{{font-size:80px}}.brand{{font-size:12px;font-weight:800;letter-spacing:.1em;color:#2563eb;text-transform:uppercase}}h1{{font-size:clamp(30px,5vw,48px);line-height:1.05;letter-spacing:-.04em;margin:10px 0}}.best{{font-size:clamp(24px,4vw,38px);font-weight:900;margin:14px 0}}.muted{{color:#667085;line-height:1.65}}h2{{margin-top:0}}.table-wrap{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;min-width:600px}}td,th{{text-align:left;padding:13px 10px;border-bottom:1px solid #eaecf0}}th{{font-size:12px;color:#667085}}.specs th{{width:35%}}.empty{{padding:18px;background:#f9fafb;border-radius:12px;color:#667085}}.cta{{display:inline-block;background:#111827;color:white;padding:11px 15px;border-radius:10px;text-decoration:none;font-weight:750}}@media(max-width:650px){{.hero{{grid-template-columns:1fr}}.photo{{min-height:180px}}.photo img{{height:220px}}}}</style></head><body><main><a class="back" href="/mobile-price-in-nepal/">← All mobile prices in Nepal</a><section class="hero"><div class="photo">{image_html}</div><div><div class="brand">{esc(p.get("brand"))}</div><h1>{esc(title)} Price in Nepal</h1><p class="muted">Compare store prices for this exact listing. Check the RAM/storage variant, stock and warranty with the seller before ordering.</p><div class="best">{best_html}</div><p class="muted">Lowest listed offer · Checked {checked_date}</p>{f'<a class="cta" href="{esc(best["url"])}" target="_blank" rel="nofollow sponsored noopener">View cheapest store ↗</a>' if best else ''}</div></section><section class="panel"><h2>Compare prices by store</h2><p class="muted">Offers are shown separately so you can find the lowest available price. Retailer prices and stock can change; confirm the final amount before paying.</p>{('<div class="table-wrap"><table><thead><tr><th>Store</th><th>Price</th><th>Warranty</th><th>Checked</th><th>Link</th></tr></thead><tbody>'+price_rows+'</tbody></table></div>') if prices else '<div class="empty">No current store offer could be confirmed for this model. Check back after the next refresh.</div>'}</section>{history_html}<section class="panel"><h2>{esc(title)} specifications</h2>{('<div class="table-wrap"><table class="specs">'+spec_rows+'</table></div>') if spec_rows else '<div class="empty">Full specifications are not yet confirmed. We publish only specifications found in product information.</div>'}<p class="muted">Specifications may vary by regional model and RAM/storage variant. Verify the model number and box details with the store.</p></section><section class="panel"><h2>Frequently asked questions</h2><h3>What is the lowest {esc(title)} price in Nepal?</h3><p class="muted">The lowest recorded retailer offer on this page is <strong>{best_html}</strong>{' at '+esc(best["store"]) if best else ''}. Offers may change after the displayed check date.</p><h3>Are these prices for the same variant?</h3><p class="muted">Compare the listed configuration and confirm RAM, storage, warranty and availability with the retailer before purchase.</p><h3>How do I buy this phone?</h3><p class="muted">Open the store offer from the table above and confirm final price, delivery, warranty and stock directly with that store.</p></section><p class="muted">Last checked: {checked_date}. Laxman Nepal is an independent comparison directory; store names and product marks belong to their respective owners.</p></main></body></html>'''
    tracking = """<script>
document.addEventListener('click', function(event) {
  const link = event.target.closest('a[rel~="sponsored"]');
  if (!link || typeof window.gtag !== 'function') return;
  window.gtag('event', 'retailer_click', {
    event_category: 'mobile_price',
    retailer: link.textContent.trim(),
    phone: %s,
    destination: link.href
  });
});
</script>""" % json.dumps(title)
    return body.replace("</body>", tracking + "</body>")

def write_category_pages(phones):
    root=Path("mobile-price-in-nepal")
    brands_root=root/"brands"
    budgets_root=root/"budgets"
    brands_root.mkdir(parents=True,exist_ok=True)
    budgets_root.mkdir(parents=True,exist_ok=True)
    esc=lambda x:html.escape(str(x or ""),quote=True)
    def render_page(title,description,slug,entries,kind):
        canonical="https://laxmannepal.com.np/mobile-price-in-nepal/"+kind+"/"+slug+"/"
        cards=[]
        for p in sorted(entries,key=lambda x:(x.get("price") or 10**12,x.get("model",""))):
            price=p.get("price")
            image=p.get("image")
            photo=f'<img src="{esc(image)}" alt="{esc(p.get("model"))}" loading="lazy">' if image else '<span>📱</span>'
            price_html=(("Last known · " if p.get("price_is_stale") else "")+f'Rs. {int(price):,}') if price else "Price not confirmed"
            cards.append(f'<article class="card"><a href="/mobile-price-in-nepal/phones/{esc(p["slug"])}/"><div class="photo">{photo}</div><div class="brand">{esc(p.get("brand"))}</div><h2>{esc(p.get("model"))}</h2><strong>{price_html}</strong><p>Lowest at {esc(p.get("best_store") or "No confirmed store")}</p><span>Compare offers and specifications →</span></a></article>')
        item_list={"@context":"https://schema.org","@type":"ItemList","name":title,"itemListElement":[{"@type":"ListItem","position":i+1,"url":"https://laxmannepal.com.np/mobile-price-in-nepal/phones/"+p["slug"]+"/","name":p.get("model")} for i,p in enumerate(entries)]}
        structured=json.dumps(item_list,ensure_ascii=False).replace("</","<\\/")
        body=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Laxman Nepal</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{canonical}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="website"><script type="application/ld+json">{structured}</script><style>*{{box-sizing:border-box}}body{{margin:0;background:#f7f8fb;color:#101828;font:16px system-ui,sans-serif}}main{{max-width:1180px;margin:auto;padding:24px 16px 60px}}a{{color:inherit;text-decoration:none}}.back{{color:#2563eb;font-weight:800}}.hero,.panel{{background:white;border:1px solid #e4e7ec;border-radius:20px;padding:clamp(18px,4vw,34px);margin:18px 0}}h1{{font-size:clamp(30px,5vw,48px);letter-spacing:-.04em;margin:14px 0}}p{{color:#667085;line-height:1.65}}.grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}}.card{{background:#fff;border:1px solid #e4e7ec;border-radius:16px;overflow:hidden}}.card a{{display:block;padding:12px}}.photo{{height:170px;background:#f8fafc;border-radius:10px;display:grid;place-items:center;margin-bottom:12px}}.photo img{{width:100%;height:100%;object-fit:contain}}.brand{{font-size:11px;color:#2563eb;font-weight:900;text-transform:uppercase}}h2{{font-size:15px;line-height:1.4}}.card strong{{font-size:20px}}.card p,.card span{{font-size:12px}}.card span{{color:#2563eb;font-weight:800}}.empty{{padding:24px;background:white;border-radius:12px}}@media(max-width:850px){{.grid{{grid-template-columns:repeat(3,minmax(0,1fr))}}}}@media(max-width:600px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}}.photo{{height:135px}}}}</style></head><body><main><a class="back" href="/mobile-price-in-nepal/">← All mobile prices in Nepal</a><section class="hero"><h1>{esc(title)}</h1><p>{esc(description)}</p><p>{len(entries)} phone models with a recorded offer. Prices can change; confirm stock, warranty and exact RAM/storage with the retailer.</p></section>{'<section class="grid">'+''.join(cards)+'</section>' if cards else '<section class="empty">No current verified offers are available in this category. Check back after a successful retailer refresh.</section>'}<section class="panel"><h2>Compare phone prices in Nepal</h2><p>Browse brand pages and model details to compare available store offers. Only recorded prices are shown; unavailable or ambiguous prices are not guessed.</p><a class="back" href="/mobile-price-in-nepal/">Browse all mobile prices →</a></section></main></body></html>'''
        folder=(brands_root if kind=="brands" else budgets_root)/slug
        folder.mkdir(parents=True,exist_ok=True)
        (folder/"index.html").write_text(body,encoding="utf-8")
    keep_brands=set()
    grouped={}
    for p in phones:
        if p.get("brand") and p["brand"]!="Other":
            grouped.setdefault(p["brand"],[]).append(p)
    for brand,entries in grouped.items():
        slug=slugify(brand)
        keep_brands.add(slug)
        render_page(f"{brand} Mobile Prices in Nepal",f"Compare {brand} phone prices in Nepal, including lowest recorded store offers, available specifications and individual model pages.",slug,entries,"brands")
    for folder in brands_root.iterdir():
        if folder.is_dir() and folder.name not in keep_brands:
            import shutil; shutil.rmtree(folder)
    ranges=[
        ("under-15000","Phones Under Rs. 15,000 in Nepal",lambda v:0<v<15000),
        ("15000-25000","Phones Rs. 15,000–25,000 in Nepal",lambda v:15000<=v<25000),
        ("25000-40000","Phones Rs. 25,000–40,000 in Nepal",lambda v:25000<=v<40000),
        ("40000-70000","Phones Rs. 40,000–70,000 in Nepal",lambda v:40000<=v<70000),
        ("70000-plus","Phones Above Rs. 70,000 in Nepal",lambda v:v>=70000),
    ]
    keep_budgets=set()
    for slug,title,predicate in ranges:
        entries=[p for p in phones if p.get("price") and predicate(int(p["price"]))]
        if not entries: continue
        keep_budgets.add(slug)
        render_page(title,f"Find smartphones in Nepal in this budget, compare current recorded store offers, and view each model's specifications.",slug,entries,"budgets")
    for folder in budgets_root.iterdir():
        if folder.is_dir() and folder.name not in keep_budgets:
            import shutil; shutil.rmtree(folder)

def offer_counts(phones):
    counts={}
    for phone in phones:
        for offer in phone.get("prices",[]) if isinstance(phone.get("prices"),list) else []:
            if isinstance(offer,dict) and offer.get("store") and offer.get("price"):
                counts[offer["store"]]=counts.get(offer["store"],0)+1
    return counts

def assess_source_health(fresh_phones, previous_phones, candidate_counts=None, source_errors=None):
    """Mark a store complete only when today's priced coverage is credible vs its history."""
    current=offer_counts(fresh_phones)
    previous=offer_counts(previous_phones)
    candidate_counts=candidate_counts or {}
    source_errors=source_errors or {}
    health={}
    status={}
    all_stores=set(current)|set(previous)|set(candidate_counts)|set(source_errors)|{s["store"] for s in SOURCES}
    for store in sorted(all_stores):
        prior=previous.get(store,0)
        found=current.get(store,0)
        required=1 if prior<3 else max(3,math.ceil(prior*0.35))
        complete=found>=required and found>0
        health[store]=complete
        status[store]={
            "candidates":int(candidate_counts.get(store,0)),
            "priced_offers_found":int(found),
            "previous_offers":int(prior),
            "minimum_expected_offers":int(required),
            "status":"complete" if complete and not source_errors.get(store) else ("partial" if complete else "stale"),
            "errors":source_errors.get(store,[]),
        }
    return health,status

def merge_previous_catalogue(fresh_phones, previous_phones, healthy_stores, today=None):
    """Use fresh offers where observed; retain last-known offers as explicitly stale if a store scrape is incomplete."""
    today=today or TODAY
    fresh_by_slug={p["slug"]:p for p in fresh_phones if p.get("slug")}
    old_by_slug={p["slug"]:p for p in previous_phones if p.get("slug")}
    merged=[]
    for slug in sorted(set(fresh_by_slug)|set(old_by_slug)):
        fresh=fresh_by_slug.get(slug)
        old=old_by_slug.get(slug)
        if fresh:
            phone=copy.deepcopy(fresh)
            if old:
                for key in ("image","description","ram","storage","display","battery","chipset","camera","specifications"):
                    if not phone.get(key) and old.get(key):
                        phone[key]=copy.deepcopy(old[key])
        else:
            phone=copy.deepcopy(old)
            phone["prices"]=[]
        current_by_store={o.get("store"):copy.deepcopy(o) for o in (fresh or {}).get("prices",[]) if o.get("store") and o.get("price")}
        old_by_store={o.get("store"):copy.deepcopy(o) for o in (old or {}).get("prices",[]) if o.get("store") and o.get("price")}
        final=[]
        for store in sorted(set(current_by_store)|set(old_by_store)):
            if store in current_by_store:
                offer=current_by_store[store]
                offer.pop("stale",None)
                offer.pop("stale_reason",None)
                final.append(offer)
            elif not healthy_stores.get(store,False) and store in old_by_store:
                offer=old_by_store[store]
                offer["stale"]=True
                offer["stale_reason"]="retailer-refresh-incomplete"
                final.append(offer)
        if not final and not fresh:
            continue
        final.sort(key=lambda o:(bool(o.get("stale")),int(o.get("price") or 10**12)))
        phone["prices"]=final
        current_prices=[o for o in final if not o.get("stale")]
        best=min(current_prices or final,key=lambda o:int(o.get("price") or 10**12),default=None)
        phone["price"]=int(best["price"]) if best else None
        phone["best_store"]=best.get("store") if best else None
        phone["best_url"]=best.get("url") if best else None
        phone["price_is_stale"]=bool(final) and not bool(current_prices)
        phone["price_count"]=len(final)
        phone["fresh_offer_count"]=len(current_prices)
        phone["stale_offer_count"]=len(final)-len(current_prices)
        phone["updated_at"]=today if current_prices else (old or {}).get("updated_at") or today
        merged.append(phone)
    merged.sort(key=lambda p:(p.get("brand",""),p.get("model","")))
    return merged

def main():
    try:
        previous_doc=json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
        previous_phones=previous_doc.get("phones",[]) if isinstance(previous_doc,dict) else []
        if not isinstance(previous_phones,list):
            previous_phones=[]
    except (OSError,json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot safely read previous catalogue; refusing refresh: {exc}")
    raw=[]
    candidate_counts={}
    source_errors={}
    for source in SOURCES:
        store=source["store"]
        try:
            items=parse_listing(source)
            candidate_counts[store]=candidate_counts.get(store,0)+len(items)
            print(f'{store}: found {len(items)} candidates at {source["url"]}')
            # Do not silently truncate ordinary retailer pages at 25 candidates.
            raw.extend(items[:500])
        except Exception as exc:
            source_errors.setdefault(store,[]).append(f'{source["url"]}: {type(exc).__name__}: {exc}')
            print(f'Unable to read {store} at {source["url"]}: {exc}')
    # Visit each candidate product page for price/image/specs when the listing card is incomplete.
    enriched=[]
    seen=set()
    for item in raw:
        dedupe_key=(item["url"],item["title"])
        if dedupe_key in seen: continue
        seen.add(dedupe_key)
        detail={"title":item["title"],"image":item.get("image"),"price":item.get("price"),"description":item.get("description"),"specs":{},"text":item.get("text") or ""}
        same_listing = bool(item.get("source_url")) and urlparse(item["url"]).path.rstrip("/") == urlparse(item["source_url"]).path.rstrip("/")
        if item.get("kind") not in ("shopify","catalog") and not same_listing:
            try:
                soup=fetch(item["url"])
                meta=product_meta(soup,item["title"])
                detail.update({k:v for k,v in meta.items() if v not in (None,"",{})})
            except Exception as exc: print(f'Skip detail {item["url"]}: {exc}')
        unavailable=bool(re.search(r"outofstock|discontinued|soldout",clean(detail.get("availability")).lower()))
        price=None if unavailable else ((item.get("price") or detail.get("price")) if item.get("kind") in ("shopify","catalog") else (detail.get("price") or item.get("price")))
        # Do not publish non-phone categories or pages without a plausible product name.
        title=clean(item["title"] if item.get("kind")=="shopify" else (detail.get("title") or item["title"]))
        if not is_phone_title(title): continue
        image=detail.get("image") or item.get("image")
        # Keep image only when it's a real HTTP URL.
        if image and not str(image).startswith("http"): image=urljoin(item["url"],str(image))
        specs={**detail.get("specs",{}), **extract_specs(title,detail.get("text",""),detail.get("specs",{}))}
        enriched.append({"store":item["store"],"title":title,"model":normalize_model(title),"variant":variant_key(title),"price":price,"url":item["url"],"image":image,"specs":specs,"description":detail.get("description"),"checked_at":TODAY,"warranty":None})
        if item.get("kind") not in ("shopify","catalog"): time.sleep(.25)
    # Group exact model/variant only; avoid merging different storage versions.
    groups={}
    for x in enriched:
        model=x["model"]
        if not model: continue
        key=slugify((model+" "+x["variant"]) if x["variant"] else model)
        p=groups.setdefault(key,{"slug":key,"brand":brand_for(model),"model":(model+" "+x["variant"]).strip(),"title":(model+" "+x["variant"]).strip(),"variant":x["variant"],"prices":[],"image":None,"description":None,"ram":None,"storage":None,"display":None,"battery":None,"chipset":None,"camera":None,"specifications":{},"updated_at":TODAY})
        if x["price"] and int(x["price"])>1000 and int(x["price"])<3000000:
            offer={"store":x["store"],"price":int(x["price"]),"url":x["url"],"checked_at":TODAY,"warranty":x["warranty"]}
            existing=next((pr for pr in p["prices"] if pr["store"]==x["store"]),None)
            if existing is None:
                p["prices"].append(offer)
            elif offer["price"]<existing["price"]:
                existing.update(offer)
        if not p["image"] and x["image"]: p["image"]=x["image"]
        if not p["description"] and x["description"]: p["description"]=x["description"]
        for k,v in x["specs"].items():
            if v and not p.get(k): p[k]=v
            if v and len(str(v))<160: p["specifications"].setdefault(k,v)
        vm=re.search(r"(\d{1,2})GB/(\d{2,4})GB",x["variant"])
        if vm:
            p["ram"]=p["ram"] or vm.group(1)+"GB"
            p["storage"]=p["storage"] or vm.group(2)+"GB"
    phones=[]
    for p in groups.values():
        p["prices"].sort(key=lambda x:x["price"])
        p["price"]=p["prices"][0]["price"] if p["prices"] else None
        p["best_store"]=p["prices"][0]["store"] if p["prices"] else None
        p["best_url"]=p["prices"][0]["url"] if p["prices"] else None
        p["price_count"]=len(p["prices"])
        phones.append(p)
    phones.sort(key=lambda p:(p["brand"],p["model"]))
    for p in phones: p["updated_at"]=TODAY
    healthy_stores,source_status=assess_source_health(phones,previous_phones,candidate_counts,source_errors)
    phones=merge_previous_catalogue(phones,previous_phones,healthy_stores,TODAY)
    fresh_offer_total=sum(1 for p in phones for offer in p.get("prices",[]) if offer.get("price") and not offer.get("stale"))
    if not phones or fresh_offer_total==0:
        raise SystemExit("No fresh confirmed phone prices extracted; preserving the last published catalogue.")
    for store,details in source_status.items():
        print(f'SOURCE HEALTH {store}: {details["status"]}; {details["priced_offers_found"]}/{details["previous_offers"]} current/previous priced offers')
    # Save one daily snapshot per model/variant and store, keeping 180 days for trend charts.
    HISTORY_OUT.parent.mkdir(parents=True,exist_ok=True)
    try:
        history_doc=json.loads(HISTORY_OUT.read_text(encoding="utf-8")) if HISTORY_OUT.exists() else {"updated_at":None,"days":[]}
    except Exception:
        history_doc={"updated_at":None,"days":[]}
    snapshot={"date":TODAY,"phones":[{"slug":p["slug"],"model":p["model"],"best_price":p["price"],"best_store":p["best_store"],"offers":[{"store":x["store"],"price":x["price"]} for x in p["prices"] if not x.get("stale")]} for p in phones if any(not x.get("stale") for x in p.get("prices",[]))]}
    days=[d for d in history_doc.get("days",[]) if d.get("date")!=TODAY]
    days.append(snapshot)
    days=sorted(days,key=lambda d:d.get("date",""))[-180:]
    history_doc={"updated_at":datetime.now(timezone.utc).isoformat(),"days":days}
    for p in phones:
        p["history"]=[{"date":d["date"],"price":next((x.get("best_price") for x in d.get("phones",[]) if x.get("slug")==p["slug"]),None)} for d in days if any(x.get("slug")==p["slug"] and x.get("best_price") for x in d.get("phones",[]))]
    HISTORY_OUT.write_text(json.dumps(history_doc,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    write_category_pages(phones)
    # Generate search-indexable detail pages, one per model/variant.
    DETAIL_ROOT.mkdir(parents=True,exist_ok=True)
    keep=set()
    for p in phones:
        folder=DETAIL_ROOT/p["slug"]; folder.mkdir(parents=True,exist_ok=True)
        (folder/"index.html").write_text(page_template(p),encoding="utf-8")
        keep.add(p["slug"])
    # Remove stale generated pages after a model disappears from the catalogue.
    for folder in DETAIL_ROOT.iterdir():
        if folder.is_dir() and folder.name not in keep:
            import shutil; shutil.rmtree(folder)
    refreshed_at=datetime.now(timezone.utc).isoformat()
    fresh_offer_count=sum(1 for p in phones for offer in p.get("prices",[]) if offer.get("price") and not offer.get("stale"))
    stale_offer_count=sum(1 for p in phones for offer in p.get("prices",[]) if offer.get("price") and offer.get("stale"))
    payload={"updated_at":refreshed_at,"status":"Daily retailer refresh; last-known offers are marked stale when a source refresh is incomplete","source_status":source_status,"fresh_offer_count":fresh_offer_count,"stale_offer_count":stale_offer_count,"phones":phones,"store_count":len({pr["store"] for p in phones for pr in p["prices"]}),"price_count":sum(len(p["prices"]) for p in phones)}
    status_doc={"updated_at":refreshed_at,"date":TODAY,"schedule":"daily","model_variants":len(phones),"fresh_offers":fresh_offer_count,"stale_offers":stale_offer_count,"stores":source_status}
    STATUS_OUT.parent.mkdir(parents=True,exist_ok=True)
    STATUS_OUT.write_text(json.dumps(status_doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f'Wrote {len(phones)} model variants; {fresh_offer_count} fresh and {stale_offer_count} last-known stale store offers')
    if not phones: raise SystemExit("No product variants extracted; refusing to overwrite the catalogue.")
if __name__=="__main__": main()
