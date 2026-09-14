import json,re
from datetime import datetime,timezone
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

SOURCE='https://www.gadgetbytenepal.com/cat/mobiles/'
HEADERS={'User-Agent':'Mozilla/5.0 (compatible; LaxmanMobileCatalog/1.0)'}
ALIASES={'iPhone':'Apple','Poco':'POCO','Ai+':'AI+'}
S=requests.Session();S.headers.update(HEADERS)

def clean(s):return re.sub(r'\s+',' ',s or '').strip()
def price_line(line):
    line=clean(line).replace('NPR','').strip();m=re.search(r'\(([^()]*)\)\s*$',line);variant=clean(m.group(1)) if m else '';prefix=line[:m.start()].strip() if m else line;nums=re.findall(r'\d[\d,]*',prefix)
    if not nums:return None
    vals=[int(x.replace(',','')) for x in nums];d={'price':vals[-1],'variant':variant}
    if len(vals)>=2:d['original_price']=vals[-2]
    return d

def price_lines(cell):
    for br in cell.find_all('br'):br.replace_with('\n')
    return [clean(x) for x in cell.get_text('\n',strip=True).split('\n') if clean(x)]

def table_brand(table):
    h=table.find_previous(['h2','h3','h4'])
    if h:
        m=re.match(r'(.+?)\s+Mobile Price List',clean(h.get_text(' ',strip=True)),re.I)
        if m:return ALIASES.get(clean(m.group(1)),clean(m.group(1)))
    return ''

def parse_catalog(html):
    soup=BeautifulSoup(html,'html.parser');out={}
    for table in soup.find_all('table'):
        brand=table_brand(table)
        for row in table.find_all('tr'):
            cells=row.find_all(['td','th'])
            if len(cells)<2:continue
            a=cells[0].find('a');name=clean(a.get_text(' ',strip=True)) if a else ''
            if not name or name.lower()=='product name':continue
            entries=[price_line(x) for x in price_lines(cells[1])];entries=[x for x in entries if x]
            if not entries:continue
            if not brand:brand={'iPhone':'Apple','Redmi':'Xiaomi','POCO':'POCO','Poco':'POCO','OPPO':'OPPO','ZTE':'ZTE','Ai+':'AI+'}.get(name.split()[0],name.split()[0])
            pid=re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-');p=out.get(pid,{'id':pid,'name':name,'brand':brand,'variants':[],'prices':[],'original_prices':[]})
            p['variants'] += [x['variant'] for x in entries if x.get('variant')];p['prices'] += [x['price'] for x in entries];p['original_prices'] += [x['original_price'] for x in entries if x.get('original_price')]
            out[pid]=p
    products=[]
    for p in out.values():
        p['variants']=list(dict.fromkeys(p['variants']));p['prices']=sorted(set(p['prices']));p['price']=min(p['prices']);p['max_price']=max(p['prices']);p['original_price']=max(p['original_prices'] or [0]) or None;p['rams']=sorted(set(re.findall(r'\b\d+GB\b',' '.join(p['variants']))),key=lambda x:int(re.search(r'\d+',x).group()));p['storages']=sorted(set(re.findall(r'\b(?:\d+GB|\d+TB)\b',' '.join(p['variants']))),key=lambda x:int(re.search(r'\d+',x).group())*(1024 if 'TB' in x else 1));p['is_5g']=bool(re.search(r'\b5G\b',p['name'],re.I));p.pop('prices',None);p.pop('original_prices',None);products.append(p)
    return products

def main():
    r=S.get(SOURCE,timeout=45);r.raise_for_status();products=parse_catalog(r.text)
    if len(products)<50:raise RuntimeError(f'Catalog parser returned only {len(products)} models')
    payload={'updated_at':datetime.now(timezone.utc).isoformat(),'count':len(products),'products':products}
    with open('mobile/data.json','w',encoding='utf-8') as f:json.dump(payload,f,ensure_ascii=False,indent=2)
    print('Wrote',len(products),'models')
if __name__=='__main__':main()
