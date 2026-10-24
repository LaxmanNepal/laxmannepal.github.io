import json,re,unicodedata,datetime,urllib.request
from difflib import SequenceMatcher
from html import unescape

DATA='laptop-price-in-nepal/data/laptops.json'
UA='Mozilla/5.0 (compatible; LaxmanNepalLaptopBot/1.0)'

def norm(s):
    s=unicodedata.normalize('NFKD',str(s or '')).lower()
    s=re.sub(r'[^a-z0-9]+',' ',s)
    return ' '.join(s.split())

def price(v):
    if isinstance(v,(int,float)): return int(v)
    m=re.search(r'(?:rs\.?|npr)\s*([0-9][0-9,]*)',str(v),re.I)
    return int(m.group(1).replace(',','')) if m else None

def walk_json(x,out):
    if isinstance(x,dict):
        if '@type' in x and ('Product' in str(x['@type']) or 'ItemList' in str(x['@type'])): out.append(x)
        for v in x.values(): walk_json(v,out)
    elif isinstance(x,list):
        for v in x: walk_json(v,out)

def extract(url):
    req=urllib.request.Request(url,headers={'User-Agent':UA})
    html=urllib.request.urlopen(req,timeout=25).read().decode('utf-8','ignore')
    found=[]
    for m in re.finditer(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',html,re.I|re.S):
        try: walk_json(json.loads(unescape(m.group(1))),found)
        except Exception: pass
    rows=[]
    for x in found:
        if x.get('@type')=='Product':
            o=x.get('offers',{})
            if isinstance(o,list): o=o[0] if o else {}
            rows.append({'name':x.get('name',''),'price':price(o.get('price') or o.get('lowPrice')),'url':o.get('url') or x.get('url') or url})
        for item in x.get('itemListElement',[]) if isinstance(x,dict) else []:
            p=item.get('item',item) if isinstance(item,dict) else {}
            if isinstance(p,dict):
                o=p.get('offers',{})
                if isinstance(o,list): o=o[0] if o else {}
                rows.append({'name':p.get('name',''),'price':price(o.get('price') or o.get('lowPrice')),'url':o.get('url') or p.get('url') or url})
    return [r for r in rows if r['name'] and r['price']]

def main():
    d=json.load(open(DATA,encoding='utf-8')); today=datetime.date.today().isoformat(); changed=0
    sources={s['id']:s['url'] for s in d['stores'] if s['id'] in {'bt-planet','tech-chautari'}}
    for sid,url in sources.items():
        try: rows=extract(url)
        except Exception as e:
            print('source failed',sid,e); continue
        for p in d['products']:
            target=norm(p['brand']+' '+p['name']+' '+p['variant'])
            best=max(rows,key=lambda r:SequenceMatcher(None,target,norm(r['name'])).ratio(),default=None)
            if not best: continue
            score=SequenceMatcher(None,target,norm(best['name'])).ratio()
            if score < .62: continue
            old=next((o for o in p['offers'] if o['storeId']==sid),None)
            new={'storeId':sid,'price':best['price'],'availability':'Listed; confirm stock','url':best['url'],'checked':today}
            if old != new:
                if old: p['offers'][p['offers'].index(old)]=new
                else: p['offers'].append(new)
                p['priceFrom']=min(o['price'] for o in p['offers']); changed+=1
    d['generatedAt']=today
    json.dump(d,open(DATA,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
    print('Updated offers:',changed)

if __name__=='__main__': main()
