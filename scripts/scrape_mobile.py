import json,re
from datetime import datetime,timezone
import requests
from bs4 import BeautifulSoup

SOURCE='https://www.gadgetbytenepal.com/cat/mobiles/'
HEADERS={'User-Agent':'Mozilla/5.0 (compatible; LaxmanMobileCatalog/1.0)'}
ALIASES={'iPhone':'Apple','Poco':'POCO','Ai+':'AI+'}
S=requests.Session();S.headers.update(HEADERS)

def clean(s):return re.sub(r'\s+',' ',s or '').strip()

def entries_from_cell(cell):
    text=clean(cell.get_text(' ',strip=True));pattern=r'(?:NPR|Rs\.?)[ \t]*([\d,]+)(?:[ \t]+([\d,]+))?[ \t]*\(([^)]*)\)';entries=[]
    for m in re.finditer(pattern,text,re.I):
        vals=[int(x.replace(',','')) for x in m.groups()[:2] if x]
        if vals:
            d={'price':vals[-1],'variant':clean(m.group(3))}
            if len(vals)>1:d['original_price']=vals[-2]
            entries.append(d)
    if not entries:
        for raw in re.findall(r'(?:NPR|Rs\.?)[ \t]*[\d,]+(?:[ \t]+[\d,]+)?',text,re.I):
            vals=[int(x.replace(',','')) for x in re.findall(r'[\d,]+',raw)]
            if vals:
                d={'price':vals[-1],'variant':''}
                if len(vals)>1:d['original_price']=vals[-2]
                entries.append(d)
    return entries

def table_brand(table):
    h=table.find_previous(['h2','h3','h4'])
    if h:
        m=re.match(r'(.+?)\s+Mobile Price List',clean(h.get_text(' ',strip=True)),re.I)
        if m:return ALIASES.get(clean(m.group(1)),clean(m.group(1)))
    return ''

def parse_catalog(html):
    soup=BeautifulSoup(html,'html.parser');out={}
    for table in soup.find_all('table'):
        brand=table_brand(table);current=None
        for row in table.find_all('tr'):
            cells=row.find_all(['td','th'])
            if len(cells)<2:continue
            a=cells[0].find('a');name=clean(a.get_text(' ',strip=True)) if a else ''
            entries=entries_from_cell(cells[1])
            if name and name.lower()!='product name':
                if not brand:brand={'iPhone':'Apple','Redmi':'Xiaomi','POCO':'POCO','Poco':'POCO','OPPO':'OPPO','ZTE':'ZTE','Ai+':'AI+'}.get(name.split()[0],name.split()[0])
                pid=re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-')
                current=out.get(pid,{'id':pid,'name':name,'brand':brand,'variants':[],'prices':[],'original_prices':[]});out[pid]=current
            if current and entries:
                current['variants'] += [x['variant'] for x in entries if x.get('variant')]
                current['prices'] += [x['price'] for x in entries]
                current['original_prices'] += [x['original_price'] for x in entries if x.get('original_price')]
    products=[]
    for p in out.values():
        p['variants']=list(dict.fromkeys(p['variants']));p['prices']=sorted(set(p['prices']));p['price']=min(p['prices']);p['max_price']=max(p['prices']);p['original_price']=max(p['original_prices'] or [0]) or None
        ram=set();storage=set()
        for v in p['variants']:
            tokens=re.findall(r'\d+(?:GB|TB)',v,re.I)
            for token in tokens:
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
