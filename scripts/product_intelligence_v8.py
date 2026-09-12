from pathlib import Path
import json, re
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = ROOT / 'data/products.json'
PRICES = ROOT / 'data/prices.json'
OUT = ROOT / 'data/product-intelligence.json'

def slug(v): return re.sub(r'[^a-z0-9]+','-',str(v).lower()).strip('-') or 'product'
def load(path, fallback):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return fallback
def money(v):
    if isinstance(v, (int,float)): return float(v)
    if isinstance(v,str):
        m=re.search(r'\d+(?:,\d{3})*(?:\.\d+)?',v.replace('NPR','').replace('Rs.',''))
        if m:
            try: return float(m.group(0).replace(',',''))
            except ValueError: pass
    return None
def norm(v): return re.sub(r'[^a-z0-9]+','',str(v).lower())
def numeric(v):
    try: return float(v)
    except (TypeError,ValueError): return None

def main():
    pdata=load(PRODUCTS,{'products':[]}); prices=load(PRICES,{'mobile':[],'laptop':[]})
    products=pdata.get('products',[]); rows=prices.get('mobile',[])+prices.get('laptop',[]); today=date.today().isoformat()
    index=[]
    for p in products:
        p.setdefault('slug',slug(p.get('name','product')))
        name=norm(p.get('name','')); brand=norm(p.get('brand','')); matches=[]
        for row in rows:
            rb=norm(row.get('brand','')); rm=norm(row.get('model',''))
            if rb and rb==brand and rm and (rm in name or name in rm): matches.append(row)
        vals=[money(x.get('price')) for x in matches]; vals=[x for x in vals if x is not None]
        history=p.get('price_history',[]); nums=[money(x.get('price')) for x in history]; nums=[x for x in nums if x is not None]
        current=nums[-1] if nums else money(p.get('price'))
        best=min(vals) if vals else None
        drop_amount=drop_percent=0
        if current and best and current>best: drop_amount=round(current-best,2); drop_percent=round(drop_amount/current*100,1)
        # Prefer explicitly verified review/rating data. Never invent a score.
        rating=numeric(p.get('rating')); value_score=None
        if rating is not None and (best or current):
            # Transparent score: rating out of 10, lightly adjusted for a verified discount.
            value_score=round(min(100,max(0,rating*10 + min(drop_percent,20)*0.5)),1)
        index.append({'slug':p['slug'],'name':p.get('name',''),'brand':p.get('brand',''),'category':p.get('category',''),'matched_price_rows':len(matches),'best_verified_price':best,'current_verified_price':current,'has_price_drop':drop_percent>0,'price_drop_amount':drop_amount,'price_drop_percent':drop_percent,'value_score':value_score,'rating':rating,'last_verified':today if matches or nums else None,'last_checked':today})
    # Rank only products with usable verified price data; keep missing-data products unranked.
    ranked=[x for x in index if x.get('best_verified_price') is not None or x.get('current_verified_price') is not None]
    ranked.sort(key=lambda x:(x.get('value_score') is not None, x.get('value_score') or -1, x.get('price_drop_percent') or 0),reverse=True)
    for i,x in enumerate(ranked,1): x['rank']=i
    for x in index:
        x.setdefault('rank',None)
        # Recommendation candidates: same category, then brand, closest verified price.
        base=x.get('best_verified_price') or x.get('current_verified_price')
        candidates=[]
        for y in index:
            if y['slug']==x['slug']: continue
            if y.get('best_verified_price') is None and y.get('current_verified_price') is None: continue
            score=(2 if y.get('category') and y.get('category')==x.get('category') else 0)+(1 if y.get('brand') and y.get('brand')==x.get('brand') else 0)
            yp=y.get('best_verified_price') or y.get('current_verified_price')
            if base and yp: score+=max(0,1-min(abs(yp-base)/max(base,1),1))
            candidates.append((score,y['slug']))
        x['recommendations']=[s for _,s in sorted(candidates,reverse=True)[:4]]
    deals=sorted([x for x in index if x.get('has_price_drop')],key=lambda x:x.get('price_drop_percent',0),reverse=True)
    best=sorted([x for x in index if x.get('best_verified_price') is not None],key=lambda x:(x.get('value_score') is not None,x.get('value_score') or -1,x.get('price_drop_percent') or 0),reverse=True)
    OUT.write_text(json.dumps({'schema_version':2,'generated_at':today,'summary':{'products':len(index),'verified_price_products':len(ranked),'price_drop_products':len(deals)},'best_deals':[x['slug'] for x in deals[:12]],'best_value':[x['slug'] for x in best[:12]],'products':index},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Generated V9 product intelligence for {len(index)} products')
if __name__=='__main__': main()
