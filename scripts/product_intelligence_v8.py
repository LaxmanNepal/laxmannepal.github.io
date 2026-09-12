from pathlib import Path
import json, re
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = ROOT / 'data/products.json'
PRICES = ROOT / 'data/prices.json'
OUT = ROOT / 'data/product-intelligence.json'

def slug(v):
    return re.sub(r'[^a-z0-9]+', '-', str(v).lower()).strip('-') or 'product'

def load(path, fallback):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return fallback

def money(v):
    if isinstance(v, (int, float)): return float(v)
    if isinstance(v, str):
        m = re.search(r'\d+(?:,\d{3})*(?:\.\d+)?', v.replace('NPR','').replace('Rs.',''))
        if m:
            try: return float(m.group(0).replace(',',''))
            except ValueError: pass
    return None

def norm(v): return re.sub(r'[^a-z0-9]+','',str(v).lower())

def main():
    pdata = load(PRODUCTS, {'products': []})
    prices = load(PRICES, {'mobile': [], 'laptop': []})
    products = pdata.get('products', [])
    price_rows = prices.get('mobile', []) + prices.get('laptop', [])
    index=[]
    for p in products:
        p.setdefault('slug', slug(p.get('name','product')))
        name = norm(p.get('name','')); brand = norm(p.get('brand',''))
        matches=[]
        for row in price_rows:
            rb=norm(row.get('brand','')); rm=norm(row.get('model',''))
            if rb and rb == brand and rm and (rm in name or name in rm):
                matches.append(row)
        values=[money(x.get('price')) for x in matches]
        values=[x for x in values if x is not None]
        best=min(values) if values else None
        index.append({'slug':p['slug'],'name':p.get('name',''),'brand':p.get('brand',''),'category':p.get('category',''),'matched_price_rows':len(matches),'best_verified_price':best,'has_price_drop':False,'price_drop_percent':0,'last_checked':date.today().isoformat()})
    for item in index:
        history=next((p.get('price_history',[]) for p in products if p.get('slug')==item['slug']),[])
        nums=[money(x.get('price')) for x in history]; nums=[x for x in nums if x is not None]
        if item['best_verified_price'] is not None and nums:
            old=nums[-1]
            if old>item['best_verified_price']:
                item['has_price_drop']=True; item['price_drop_percent']=round((old-item['best_verified_price'])/old*100,1)
    OUT.write_text(json.dumps({'schema_version':1,'generated_at':date.today().isoformat(),'products':index},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Generated V8 intelligence index for {len(index)} products')

if __name__=='__main__': main()
