import json,re
from datetime import datetime,timezone
from io import StringIO
import requests
import pandas as pd

SOURCE='https://www.gadgetbytenepal.com/cat/mobiles/'
HEADERS={'User-Agent':'Mozilla/5.0 (compatible; LaxmanMobileCatalog/1.0)'}
S=requests.Session();S.headers.update(HEADERS)
BRANDS={'iPhone':'Apple','Samsung':'Samsung','Vivo':'Vivo','Honor':'Honor','Motorola':'Motorola','Xiaomi':'Xiaomi','Redmi':'Xiaomi','Infinix':'Infinix','Realme':'Realme','OnePlus':'OnePlus','Poco':'POCO','POCO':'POCO','OPPO':'OPPO','Tecno':'Tecno','ZTE':'ZTE','Ai+':'AI+'}

def clean(s):return re.sub(r'\s+',' ',str(s or '')).strip()
def entries(text):
    text=clean(text);out=[]
    pattern=r'(?:NPR|Rs\.?)[ \t]*([\d,]+)(?:[ \t]+([\d,]+))?[ \t]*\(([^)]*)\)'
    for m in re.finditer(pattern,text,re.I):
        vals=[int(x.replace(',','')) for x in m.groups()[:2] if x]
        if vals:
            d={'price':vals[-1],'variant':clean(m.group(3))}
            if len(vals)>1:d['original_price']=vals[-2]
            out.append(d)
    if not out:
        for raw in re.findall(r'(?:NPR|Rs\.?)[ \t]*[\d,]+(?:[ \t]+[\d,]+)?',text,re.I):
            vals=[int(x.replace(',','')) for x in re.findall(r'[\d,]+',raw)]
            if vals:
                d={'price':vals[-1],'variant':''}
                if len(vals)>1:d['original_price']=vals[-2]
                out.append(d)
    return out

def parse_catalog(html):
    tables=pd.read_html(StringIO(html));out={}
    for df in tables:
        if len(df.columns)<2:continue
        current=None
        for _,row in df.iterrows():
            raw_name=row.iloc[0] if len(row)>0 else None;raw_price=row.iloc[1] if len(row)>1 else ''
            if pd.notna(raw_name) and clean(raw_name).lower()!='product name':current=clean(raw_name)
            if not current:continue
            es=entries(raw_price)
            if not es:continue
            first=current.split()[0];brand=BRANDS.get(first,first);pid=re.sub(r'[^a-z0-9]+','-',current.lower()).strip('-')
            p=out.get(pid,{'id':pid,'name':current,'brand':brand,'variants':[],'prices':[],'original_prices':[]})
            p['variants'] += [x['variant'] for x in es if x.get('variant')];p['prices'] += [x['price'] for x in es];p['original_prices'] += [x['original_price'] for x in es if x.get('original_price')];out[pid]=p
    products=[]
    for p in out.values():
        p['variants']=list(dict.fromkeys(p['variants']));p['prices']=sorted(set(p['prices']));p['price']=min(p['prices']);p['max_price']=max(p['prices']);p['original_price']=max(p['original_prices'] or [0]) or None
        ram=set();storage=set()
        for v in p['variants']:
            for token in re.findall(r'\d+(?:GB|TB)',v,re.I):
                n=int(re.search(r'\d+',token).group())
                if n<=32 and token.upper().endswith('GB'):ram.add(token.upper())
                elif n>=64 or token.upper().endswith('TB'):storage.add(token.upper())
        p['rams']=sorted(ram,key=lambda x:int(re.search(r'\d+',x).group()));p['storages']=sorted(storage,key=lambda x:int(re.search(r'\d+',x).group())*(1024 if 'TB' in x else 1));p['is_5g']=bool(re.search(r'\b5G\b',' '.join([p['name']]+p['variants']),re.I));p.pop('prices',None);p.pop('original_prices',None);products.append(p)
    return products

def main():
    r=S.get(SOURCE,timeout=45);r.raise_for_status();products=parse_catalog(r.text)
    if len(products)<50:raise RuntimeError(f'Catalog parser returned only {len(products)} models')
    payload={'updated_at':datetime.now(timezone.utc).isoformat(),'count':len(products),'products':products}
    with open('mobile/data.json','w',encoding='utf-8') as f:json.dump(payload,f,ensure_ascii=False,indent=2)
    print('Wrote',len(products),'models')
if __name__=='__main__':main()
