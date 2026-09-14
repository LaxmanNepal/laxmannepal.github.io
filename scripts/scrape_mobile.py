import json,re
from datetime import datetime,timezone
from io import StringIO
from concurrent.futures import ThreadPoolExecutor,as_completed
import requests
import pandas as pd
from bs4 import BeautifulSoup

SOURCE='https://www.gadgetbytenepal.com/cat/mobiles/'
HEADERS={'User-Agent':'Mozilla/5.0 (compatible; LaxmanMobileCatalog/2.0)'}
S=requests.Session();S.headers.update(HEADERS)
BRANDS={'iPhone':'Apple','Samsung':'Samsung','Vivo':'Vivo','Honor':'Honor','Motorola':'Motorola','Xiaomi':'Xiaomi','Redmi':'Xiaomi','Infinix':'Infinix','Realme':'Realme','OnePlus':'OnePlus','Poco':'POCO','POCO':'POCO','OPPO':'OPPO','Tecno':'Tecno','ZTE':'ZTE','Ai+':'AI+','Nothing':'Nothing'}

def clean(s):return re.sub(r'\s+',' ',str(s or '')).strip()
def slug(s):return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
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
    soup=BeautifulSoup(html,'html.parser');links={}
    for a in soup.select('a[href]'):
        text=clean(a.get_text(' ',strip=True));href=a.get('href','')
        if text and href and re.search(r'price|spec|iphone|galaxy|vivo|honor|xiaomi|redmi|poco|realme|oneplus|motorola|oppo|infinix|tecno|zte|nothing',href,re.I):links[text]=href
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
            first=current.split()[0];brand=BRANDS.get(first,first);pid=slug(current)
            p=out.get(pid,{'id':pid,'name':current,'brand':brand,'variants':[],'prices':[],'original_prices':[],'source_page':links.get(current,'')})
            p['variants'] += [x['variant'] for x in es if x.get('variant')];p['prices'] += [x['price'] for x in es];p['original_prices'] += [x['original_price'] for x in es if x.get('original_price')];out[pid]=p
    return list(out.values())

def parse_detail(p):
    url=p.pop('source_page','')
    if not url:return p
    try:
        r=S.get(url,timeout=25);r.raise_for_status();soup=BeautifulSoup(r.text,'html.parser')
        og=soup.find('meta',property='og:image')
        if og and og.get('content'):p['image']=og['content']
        if not p.get('image'):
            im=soup.select_one('article img, .post-content img, main img')
            if im and im.get('src'):p['image']=im['src']
        specs={};heading=None
        for h in soup.find_all(re.compile('^h[1-4]$')):
            if 'specification' in clean(h.get_text(' ',strip=True)).lower():heading=h;break
        nodes=[]
        if heading:
            for el in heading.find_all_next(['li','tr']):
                txt=clean(el.get_text(' ',strip=True))
                if txt:nodes.append(txt)
                if len(nodes)>=100:break
        if not nodes:
            for tr in soup.select('table tr'):
                cells=[clean(x.get_text(' ',strip=True)) for x in tr.find_all(['th','td'])]
                if len(cells)>=2:nodes.append(' — '.join(cells[:2]))
        for txt in nodes:
            parts=re.split(r'\s*[—:\|]\s*',txt,maxsplit=1)
            if len(parts)==2 and len(parts[0])<70:specs[parts[0].strip()]=parts[1].strip()
        body=clean(soup.get_text(' ',strip=True))
        patterns={'display':r'Display:\s*([^|.]{5,160})','chipset':r'Chipset:\s*([^|.]{5,160})','battery':r'Battery:\s*([^|.]{3,120})','camera':r'(?:Rear Camera|Camera):\s*([^|.]{5,180})'}
        for k,pat in patterns.items():
            m=re.search(pat,body,re.I)
            if m and k not in specs:specs[k]=clean(m.group(1))
        if specs:p['specifications']=specs
        p['is_5g']=bool(re.search(r'\b5g\b',' '.join([p['name']]+p['variants']+[json.dumps(specs)]),re.I))
    except Exception:
        pass
    return p

def main():
    r=S.get(SOURCE,timeout=45);r.raise_for_status();products=parse_catalog(r.text)
    if len(products)<50:raise RuntimeError(f'Catalog parser returned only {len(products)} models')
    with ThreadPoolExecutor(max_workers=8) as ex:
        products=[f.result() for f in as_completed([ex.submit(parse_detail,p) for p in products])]
    for p in products:
        p['variants']=list(dict.fromkeys(p['variants']));p['prices']=sorted(set(p['prices']));p['price']=min(p['prices']);p['max_price']=max(p['prices']);p['original_price']=max(p['original_prices'] or [0]) or None
        ram=set();storage=set()
        for v in p['variants']:
            for token in re.findall(r'\d+(?:GB|TB)',v,re.I):
                n=int(re.search(r'\d+',token).group())
                if n<=32 and token.upper().endswith('GB'):ram.add(token.upper())
                elif n>=64 or token.upper().endswith('TB'):storage.add(token.upper())
        p['rams']=sorted(ram,key=lambda x:int(re.search(r'\d+',x).group()));p['storages']=sorted(storage,key=lambda x:int(re.search(r'\d+',x).group())*(1024 if 'TB' in x else 1));p.pop('prices',None);p.pop('original_prices',None)
    products.sort(key=lambda x:x['name'])
    payload={'updated_at':datetime.now(timezone.utc).isoformat(),'count':len(products),'products':products}
    with open('mobile/data.json','w',encoding='utf-8') as f:json.dump(payload,f,ensure_ascii=False,indent=2)
    print('Wrote',len(products),'models with images/specifications')
if __name__=='__main__':main()
