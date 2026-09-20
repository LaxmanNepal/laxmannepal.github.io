#!/usr/bin/env python3
"""Build the public blog/tools layer from GitHub content. Never modifies /apps."""
from __future__ import annotations
import html,json,re
from datetime import datetime,timezone
from email.utils import format_datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'site.config.json').read_text(encoding='utf-8')); BASE=CFG['site_url'].rstrip('/')
BLOG=ROOT/'content'/'blog'; LEGACY=ROOT/'blogger-import'; OUT=ROOT/'blog'
TOOLS=json.loads((ROOT/'data'/'tools.json').read_text(encoding='utf-8')).get('tools',[])
def esc(v,q=True): return html.escape(str(v),quote=q)
def date10(v):
 s=str(v or '')[:10]
 try: datetime.strptime(s,'%Y-%m-%d'); return s
 except ValueError: return datetime.now(timezone.utc).date().isoformat()
def slugify(s): return re.sub(r'[^a-z0-9]+','-',str(s).lower()).strip('-') or 'article'
def fm(text):
 meta={}; body=text
 if text.startswith('---'):
  p=text.split('---',2)
  if len(p)==3:
   body=p[2].lstrip('\n')
   for line in p[1].splitlines():
    if ':' in line:
     k,v=line.split(':',1); v=v.strip().strip('"\''); meta[k.strip()]=[x.strip() for x in v.split(',') if x.strip()] if k.strip()=='tags' else v
 return meta,body
def markdown(src):
 out=[]; para=[]; code=False; ul=False
 def flush():
  nonlocal para
  if para:
   t=esc(' '.join(para),False); t=re.sub(r'\[([^]]+)\]\((https?://[^)]+)\)',r'<a href="\2" rel="noopener noreferrer">\1</a>',t); t=re.sub(r'`([^`]+)`',r'<code>\1</code>',t); t=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',t); out.append('<p>'+t+'</p>'); para=[]
 for line in src.replace('\r\n','\n').split('\n'):
  if line.startswith('```'):
   if code: out.append('<pre><code>'+esc('\n'.join(para))+'</code></pre>'); para=[]; code=False
   else: flush(); code=True
   continue
  if code: para.append(line); continue
  if not line.strip(): flush(); continue
  h=re.match(r'^(#{1,3})\s+(.+)$',line)
  if h:
   flush();
   if ul: out.append('</ul>'); ul=False
   n=len(h.group(1))+1; txt=esc(h.group(2),False); out.append(f'<h{n} id="{slugify(h.group(2))}">{txt}</h{n}>')
  elif re.match(r'^[-*]\s+',line):
   flush();
   if not ul: out.append('<ul>'); ul=True
   out.append('<li>'+esc(re.sub(r'^[-*]\s+','',line))+'</li>')
  else:
   if ul: out.append('</ul>'); ul=False
   para.append(line)
 flush()
 if ul: out.append('</ul>')
 return '\n'.join(out)
HEADER='''<header class="shared-header"><a class="shared-brand" href="/"><span class="shared-logo">LN</span><span><strong>Laxman Nepal</strong><small>Tools · AI · Blog · Digital</small></span></a><nav class="shared-desktop-nav" aria-label="Main menu"><a href="/tools/">Tools</a><a href="/ai-tools/">AI</a><a href="/blog/">Blog</a><a href="/apps/">Apps</a><a href="/youtube/">YouTube</a><details class="nav-dropdown"><summary>Explore</summary><div class="nav-dropdown-menu"><a href="/news/">News & Updates</a><a href="/guides/">Guides</a><a href="/mobile/">Mobile</a><a href="/laptop/">Laptops</a><a href="/gadgets/">Gadgets</a><a href="/brands/">Brands</a></div></details></nav><div class="shared-actions"><form class="shared-search-box" action="/search/" method="get"><span>⌕</span><input name="q" type="search" placeholder="Search tools & guides…" aria-label="Search"></form><button class="shared-menu-btn" type="button" data-shared-menu aria-label="Open menu">☰</button></div></header><nav class="shared-mobile-menu" data-shared-mobile><div class="shared-mobile-head"><strong>Laxman Nepal</strong><button type="button" data-shared-close>×</button></div><a href="/">🏠 Home</a><a href="/tools/">🧰 Tools</a><a href="/ai-tools/">✨ AI Tools</a><a href="/blog/">📝 Blog</a><a href="/apps/">📦 Apps</a><a href="/youtube/">▶ YouTube</a><a href="/guides/">📖 Guides</a><a href="/news/">📰 News</a><a href="/about/">About</a></nav><div class="shared-menu-backdrop" data-shared-backdrop></div>'''
FOOTER='''<footer class="shared-footer"><div class="shared-footer-grid"><div><div class="shared-footer-brand"><span class="shared-logo">LN</span><strong>Laxman Nepal</strong></div><p>Practical tools, AI resources, tutorials and useful digital guides built by Laxman Nepal.</p></div><div><strong>Tools</strong><a href="/tools/">All Tools</a><a href="/ai-tools/">AI Tools</a><a href="/apps/">Apps</a><a href="/youtube/">YouTube Tools</a></div><div><strong>Content</strong><a href="/blog/">Blog</a><a href="/news/">News</a><a href="/guides/">Guides</a><a href="/about/">About</a></div><div><strong>Connect</strong><a href="https://www.youtube.com/@laxmannepalofficial">YouTube</a><a href="https://www.instagram.com/laxmannepalsir/">Instagram</a><a href="https://github.com/LaxmanNepal">GitHub</a><a href="/contact/">Contact</a></div></div><div class="shared-footer-bottom"><span>© <span id="year"></span> Laxman Nepal · All rights reserved</span><span>Built for usefulness.</span></div></footer>'''
SCRIPT='''<script>(()=>{const m=document.querySelector('[data-shared-menu]'),n=document.querySelector('[data-shared-mobile]'),c=document.querySelector('[data-shared-close]'),b=document.querySelector('[data-shared-backdrop]');const hide=()=>{n?.classList.remove('open');if(b)b.style.display='none';document.body.style.overflow=''};m?.addEventListener('click',()=>{n?.classList.add('open');if(b)b.style.display='block';document.body.style.overflow='hidden'});c?.addEventListener('click',hide);b?.addEventListener('click',hide);n?.querySelectorAll('a').forEach(a=>a.addEventListener('click',hide));const y=document.getElementById('year');if(y)y.textContent=new Date().getFullYear()})();</script>'''
def shell(title,desc,url,body,kind='WebPage',schema_extra=None,og_image=None):
 schema={'@context':'https://schema.org','@type':kind,'name':title,'url':url,'description':desc,'author':{'@type':'Person','name':'Laxman Nepal'}}
 if schema_extra: schema.update(schema_extra)
 image=og_image or BASE+'/assets/og-default.svg'
 return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{esc(desc)}"><meta name="author" content="Laxman Nepal"><link rel="canonical" href="{esc(url)}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{esc(url)}"><meta property="og:type" content="{'article' if kind=='Article' else 'website'}"><meta property="og:image" content="{esc(image)}"><meta property="og:image:alt" content="{esc(title)}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{esc(image)}"><title>{esc(title)} — Laxman Nepal</title><link rel="stylesheet" href="/assets/css/shared-shell.css"><link rel="stylesheet" href="/assets/css/blog-images.css"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script></head><body>{HEADER}<main>{body}</main>{FOOTER}{SCRIPT}</body></html>'''
def load_articles():
 items=[]; used=set()
 for p in sorted(BLOG.glob('*.md')):
  if p.name.lower()=='readme.md': continue
  meta,src=fm(p.read_text(encoding='utf-8')); slug=slugify(meta.get('slug',p.stem)); used.add(slug)
  items.append({'title':meta.get('title',p.stem.replace('-',' ').title()),'description':meta.get('description','Practical technology, AI and productivity guidance by Laxman Nepal.'),'date':date10(meta.get('date')),'updated':date10(meta.get('updated',meta.get('date'))),'author':meta.get('author','Laxman Nepal'),'category':meta.get('category','Technology'),'slug':slug,'source':markdown(src),'legacy':False})
 manifest=LEGACY/'manifest.json'
 if manifest.exists():
  data=json.loads(manifest.read_text(encoding='utf-8'))
  for x in data.get('posts',[]):
   raw=x.get('path','').lstrip('/'); src=LEGACY/raw
   if not src.exists(): continue
   base=slugify(Path(raw).stem); slug=base; i=2
   while slug in used: slug=f'{base}-{i}'; i+=1
   used.add(slug); text=src.read_text(encoding='utf-8',errors='replace'); m=re.search(r'<body[^>]*>(.*?)</body>',text,re.I|re.S); content=m.group(1) if m else text
   desc=re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',content)).strip()[:155]
   items.append({'title':str(x.get('title','')).strip() or slug.replace('-',' ').title(),'description':desc,'date':date10(x.get('published')),'updated':date10(x.get('updated',x.get('published'))),'author':'Laxman Nepal','category':'Imported','slug':slug,'source':content,'legacy':True,'original_url':x.get('original_url',''),'legacy_path':'/'+raw})
 return sorted(items,key=lambda a:a['date'],reverse=True)
def link_related_terms(content, current_slug, articles, limit=5):
 candidates=[]
 for item in articles:
  if item.get('slug')==current_slug: continue
  title=str(item.get('title','')).strip()
  words=[w for w in re.findall(r'[A-Za-z0-9]{4,}',title) if w.lower() not in {'with','from','this','that','your','what','how','guide','best'}]
  if words: candidates.append((item,words))
 candidates.sort(key=lambda x: len(x[1]),reverse=True)
 used=set()
 for item,words in candidates:
  if len(used)>=limit: break
  for term in sorted(set(words),key=len,reverse=True):
   pattern=re.compile(r'(?<![\w-])'+re.escape(term)+r'(?![\w-])',re.I)
   if pattern.search(content):
    url=f'/blog/{item["slug"]}/'
    repl=f'<a href="{url}" class="context-link">{term}</a>'
    updated,n=pattern.subn(lambda m: repl,content,count=1)
    if n:
     content=updated; used.add(item['slug']); break
 return content

def add_heading_ids(content):
 used=set(re.findall(r'\bid=["']([^"']+)["']',content,re.I))
 def repl(m):
  level,attrs,inner=m.group(1),m.group(2),m.group(3)
  if re.search(r'\bid\s*=',attrs,re.I): return m.group(0)
  label=re.sub(r'<[^>]+>',' ',inner); label=re.sub(r'\s+',' ',html.unescape(label)).strip()
  base=slugify(label); slug=base; i=2
  while slug in used: slug=f'{base}-{i}'; i+=1
  used.add(slug)
  return f'<h{level}{attrs} id="{slug}">{inner}</h{level}>'
 return re.sub(r'<h([2-6])([^>]*)>(.*?)</h\1>',repl,content,flags=re.I|re.S)

def detect_faq(content):
 pairs=[]
 heads=re.findall(r'<h([2-6])[^>]*>(.*?)</h\\1>\\s*<p[^>]*>(.*?)</p>',content,re.I|re.S)
 for level,q,a in heads:
  qtext=re.sub(r'<[^>]+>',' ',q); qtext=re.sub(r'\\s+',' ',html.unescape(qtext)).strip()
  if '?' in qtext:
   atext=re.sub(r'<[^>]+>',' ',a); atext=re.sub(r'\\s+',' ',html.unescape(atext)).strip()
   if atext: pairs.append((qtext,atext))
 return pairs[:8]

def build_toc(content):
 items=re.findall(r'<h([2-6])[^>]*\bid="([^"]+)"[^>]*>(.*?)</h\1>',content,re.I|re.S)
 if not items: return ''
 links=[]
 for level,anchor,inner in items:
  label=re.sub(r'<[^>]+>',' ',inner); label=re.sub(r'\s+',' ',html.unescape(label)).strip()
  if label: links.append(f'<a class="toc-link toc-level-{level}" href="#{esc(anchor)}">{esc(label,False)}</a>')
 return ''.join(links)

TOPICS=[
 {'slug':'technology','name':'Technology','description':'Practical technology news, explainers and digital workflows.','keywords':['technology','tech','computer','software','hardware','digital','windows','internet']},
 {'slug':'ai','name':'AI','description':'Artificial intelligence tools, tutorials, prompts and practical workflows.','keywords':['ai','artificial','intelligence','chatgpt','gemini','claude','copilot','prompt','llm','machine learning']},
 {'slug':'mobile','name':'Mobile','description':'Phones, mobile apps, Android, iPhone and mobile buying guides.','keywords':['phone','mobile','iphone','android','xiaomi','samsung','redmi','pixel','smartphone']},
 {'slug':'apps','name':'Apps','description':'Useful apps, websites, utilities and practical digital services.','keywords':['app','apps','application','website','web','tool','utility','software']},
 {'slug':'productivity','name':'Productivity','description':'Guides for working faster with office tools, automation and digital workflows.','keywords':['productivity','excel','office','word','powerpoint','workflow','automation','shortcut','tally']},
 {'slug':'nepal','name':'Nepal','description':'Technology, digital services, prices and practical guides relevant to Nepal.','keywords':['nepal','nepali','kathmandu','hetauda','nepse','nrb','ncell','ntc','daraz']},
 {'slug':'creator','name':'Creator','description':'YouTube, content creation, video, social media and creator workflows.','keywords':['youtube','creator','video','content','instagram','tiktok','thumbnail','channel','editing']},
 {'slug':'guides','name':'Guides','description':'Step-by-step tutorials and practical how-to articles.','keywords':['guide','how','tutorial','tips','step','fix','setup','install','download']}
]
def article_topics(article):
 text=' '.join(str(article.get(k,'')) for k in ('title','description','category','source')).lower()
 scored=[]
 for topic in TOPICS:
  score=sum(1 for kw in topic['keywords'] if re.search(r'(?<![a-z0-9])'+re.escape(kw)+r'(?![a-z0-9])',text))
  if score: scored.append((score,topic))
 scored.sort(key=lambda x:x[0],reverse=True)
 return [t for _,t in scored[:4]]
def editorial_signals(articles):
 """Deterministic editorial intelligence for static builds; no fake engagement metrics."""
 now=datetime.now(timezone.utc).date()
 signals={}
 for item in articles:
  try: age=max(0,(now-datetime.strptime(item.get('date','')[:10],'%Y-%m-%d').date()).days)
  except ValueError: age=3650
  topics={t['slug'] for t in article_topics(item)}
  freshness=max(0,120-age)
  breadth=min(4,len(topics))
  signals[item['slug']]={'freshness':freshness,'topic_breadth':breadth,'topics':topics,'score':freshness*2+breadth*8}
 return signals

def content_gaps(articles, limit=8):
 counts={t['slug']:0 for t in TOPICS}
 for item in articles:
  for t in article_topics(item): counts[t['slug']]+=1
 return sorted(((count,t) for t,count in counts.items()),key=lambda x:(x[0],x[1]))[:limit]

def topic_related_articles(current, articles, topic_slug, limit=6):
 scored=[]
 signals=editorial_signals(articles)
 for item in articles:
  if item.get('slug')==current.get('slug'): continue
  if topic_slug not in signals.get(item.get('slug'),{}).get('topics',set()): continue
  cur=set(re.findall(r'[a-z0-9]+',(current.get('title','')+' '+current.get('category','')).lower()))
  other=set(re.findall(r'[a-z0-9]+',(item.get('title','')+' '+item.get('category','')).lower()))
  s=signals.get(item.get('slug'),{})
  scored.append((len(cur & other)+(3 if item.get('category')==current.get('category') else 0)+s.get('freshness',0)*0.05,item.get('date',''),item))
 return [x[2] for x in sorted(scored,key=lambda x:(x[0],x[1]),reverse=True)[:limit]]
def topic_page(topic, posts):
 url=f'{BASE}/topics/{topic["slug"]}/'
 cards=''.join(f'<article class="topic-card"><p class="eyebrow">{esc(p["category"])} · {p["date"]}</p><h2><a href="/blog/{p["slug"]}/">{esc(p["title"])}</a></h2><p>{esc(p["description"])}</p><a class="text-link" href="/blog/{p["slug"]}/">Read article →</a></article>' for p in posts)
 pills=''.join(f'<a href="/topics/{t["slug"]}/">{esc(t["name"])}</a>' for t in TOPICS)
 body=f'<div class="article-wrap"><section class="topic-hero"><p class="eyebrow">TOPIC HUB</p><h1>{esc(topic["name"])}</h1><p>{esc(topic["description"])}</p><div class="topic-stats"><strong>{len(posts)}</strong><span>articles in this topic</span></div></section><section class="topic-list"><div class="section-head"><div><p class="eyebrow">EXPLORE</p><h2>Latest {esc(topic["name"])} articles</h2></div><a href="/blog/">All articles →</a></div><div class="post-grid">{cards or "<p>No articles in this topic yet.</p>"}</div></section><section class="topic-directory"><p class="eyebrow">BROWSE TOPICS</p><div class="topic-pills">{pills}</div></section></div>'
 schema={'@type':'CollectionPage','isPartOf':{'@type':'WebSite','name':'Laxman Nepal','url':BASE+'/'},'about':{'@type':'Thing','name':topic['name']},'numberOfItems':len(posts)}
 return url,shell(topic['name'],topic['description'],url,body,'CollectionPage',schema)

def related_articles(current, articles, limit=4):
 current_topics={t['slug'] for t in article_topics(current)}
 terms=set(re.findall(r'[a-z0-9]+', (current.get('title','')+' '+current.get('category','')).lower()))
 scored=[]
 for item in articles:
  if item.get('slug')==current.get('slug'): continue
  item_terms=set(re.findall(r'[a-z0-9]+', (item.get('title','')+' '+item.get('category','')).lower()))
  shared_topics=len(current_topics & {t['slug'] for t in article_topics(item)})
  score=(3 if item.get('category')==current.get('category') else 0)+(shared_topics*2)+len(terms & item_terms)
  scored.append((score,item.get('date',''),item))
 return [x[2] for x in sorted(scored,key=lambda x:(x[0],x[1]),reverse=True)[:limit]]

def write_og_svg(title,slug,description):
 assets=ROOT/'assets'; assets.mkdir(parents=True,exist_ok=True)
 safe_title=html.escape(str(title),quote=False)
 safe_desc=html.escape(str(description),quote=False)
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f5f7ff"/><stop offset="1" stop-color="#dcecff"/></linearGradient></defs><rect width="1200" height="630" fill="url(#g)"/><circle cx="1040" cy="110" r="190" fill="#007aff" opacity=".10"/><circle cx="110" cy="570" r="210" fill="#8b5cf6" opacity=".08"/><rect x="70" y="70" width="92" height="92" rx="26" fill="#111114"/><text x="116" y="130" text-anchor="middle" font-family="Arial,sans-serif" font-size="38" font-weight="800" fill="#fff">LN</text><text x="70" y="250" font-family="Arial,sans-serif" font-size="50" font-weight="800" fill="#111114">{safe_title}</text><text x="70" y="330" font-family="Arial,sans-serif" font-size="25" fill="#5f6368">{safe_desc[:110]}</text><text x="70" y="555" font-family="Arial,sans-serif" font-size="22" font-weight="700" fill="#007aff">LAXMAN NEPAL · TECHNOLOGY · TOOLS · AI</text></svg>'''
 (assets/f'og-{slug}.svg').write_text(svg,encoding='utf-8')
 return BASE+f'/assets/og-{slug}.svg'

def main():
 articles=load_articles(); OUT.mkdir(parents=True,exist_ok=True); migration=[]
 signals=editorial_signals(articles)
 gaps=content_gaps(articles)
 insights={
  'generated_at':datetime.now(timezone.utc).isoformat(),
  'articles_total':len(articles),
  'fresh_articles_120d':sum(1 for s in signals.values() if s['freshness']>0),
  'topics':[{'slug':t['slug'],'name':t['name'],'article_count':sum(1 for a in articles if t['slug'] in signals.get(a['slug'],{}).get('topics',set())),'fresh_count':sum(1 for a in articles if t['slug'] in signals.get(a['slug'],{}).get('topics',set()) and signals[a['slug']]['freshness']>0)} for t in TOPICS],
  'content_gaps':[{'slug':slug,'article_count':count} for count,slug in gaps]
 }
 (ROOT/'data'/'content-insights.json').write_text(json.dumps(insights,ensure_ascii=False,indent=2),encoding='utf-8')

 for a in articles:
  url=f'{BASE}/blog/{a["slug"]}/'; mins=max(1,round(len(re.findall(r'\b[\w’\'-]+\b',a['source']))/220))
  related=related_articles(a,articles,4)
  topics=article_topics(a)
  topic_links=''.join(f'<a href="/topics/{t["slug"]}/">{esc(t["name"])}</a>' for t in topics)
  related_html=''.join(f'<article class="post-card"><p class="eyebrow">{esc(r["category"])} · {r["date"]}</p><h2><a href="/blog/{r["slug"]}/">{esc(r["title"])}</a></h2><p>{esc(r["description"])}</p><a class="text-link" href="/blog/{r["slug"]}/">Read article →</a></article>' for r in related)
  breadcrumbs={'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':BASE+'/'},{'@type':'ListItem','position':2,'name':'Blog','item':BASE+'/blog/'},{'@type':'ListItem','position':3,'name':a['title'],'item':url}]}
  article_html=add_heading_ids(a['source'])
  article_html=link_related_terms(article_html,a['slug'],articles,5)
  toc=build_toc(article_html)
  faq_pairs=detect_faq(article_html)
  toc_html=f'<aside class="article-toc" aria-label="Table of contents"><div class="toc-title">On this page</div>{toc}</aside>' if toc else ''
  faq_schema={'@type':'FAQPage','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':ans}} for q,ans in faq_pairs]} if faq_pairs else None
  article_tools='''<div class="article-tools" aria-label="Article actions"><button type="button" data-share>↗ Share</button><button type="button" data-copy>⧉ Copy link</button></div>'''
  article_script='''<script>(()=>{const bar=document.querySelector('[data-reading-progress] span'),article=document.querySelector('.article-content');const update=()=>{if(!bar||!article)return;const r=article.getBoundingClientRect(),top=window.scrollY+r.top,total=Math.max(1,article.scrollHeight-innerHeight*.35),p=Math.min(1,Math.max(0,(window.scrollY-top+innerHeight*.2)/total));bar.style.width=(p*100)+'%'};addEventListener('scroll',update,{passive:true});addEventListener('resize',update);update();const share=document.querySelector('[data-share]');share?.addEventListener('click',async()=>{try{if(navigator.share)await navigator.share({title:document.title,text:document.querySelector('.article-description')?.textContent||'',url:location.href});else await navigator.clipboard.writeText(location.href)}catch(e){}});const copy=document.querySelector('[data-copy]');copy?.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href);const old=copy.textContent;copy.textContent='✓ Copied';setTimeout(()=>copy.textContent=old,1600)}catch(e){copy.textContent='Copy unavailable'}})})();</script>'''
  body=f'''<div class="reading-progress" data-reading-progress aria-hidden="true"><span></span></div><div class="article-wrap"><article><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/blog/">Blog</a> / {esc(a["title"])}</nav><header class="article-header"><p class="eyebrow">{esc(a["category"])} · ~{mins} min read</p><h1>{esc(a["title"])}</h1><p class="article-description">{esc(a["description"])}</p><div class="article-meta">By {esc(a["author"])} · Published {a["date"]} · Updated {a["updated"]}</div>{article_tools}</header>{toc_html}<div class="article-topics"><span>Topics</span>{topic_links}</div><div class="article-content">{article_html}</div></article><section class="related-section"><div class="section-head"><div><p class="eyebrow">KEEP READING</p><h2>Related articles</h2><p>More from {esc(a["category"])} and nearby topics.</p></div><a href="/blog/">View all →</a></div><div class="post-grid">{related_html}</div></section></div>'''
  og_image=write_og_svg(a['title'],a['slug'],a['description'])
  body += article_script
  schema_extra={'datePublished':a['date'],'dateModified':a['updated'],'breadcrumb':breadcrumbs,'image':{'@type':'ImageObject','url':og_image,'width':1200,'height':630},'mainEntityOfPage':{'@type':'WebPage','@id':url},'publisher':{'@type':'Person','name':'Laxman Nepal','url':BASE+'/about/'}}
  if faq_schema: schema_extra['subjectOf']=faq_schema
  d=OUT/a['slug']; d.mkdir(parents=True,exist_ok=True); (d/'index.html').write_text(shell(a['title'],a['description'],url,body,'Article',schema_extra,og_image),encoding='utf-8')
  if a.get('legacy_path'): migration.append({'old_path':a['legacy_path'],'old_url':a.get('original_url',''),'new_path':'/blog/'+a['slug']+'/','new_url':url,'title':a['title']})
 cards=''.join(f'<article class="post-card"><p class="eyebrow">{esc(a["category"])} · {a["date"]}</p><h2><a href="/blog/{a["slug"]}/">{esc(a["title"])}</a></h2><p>{esc(a["description"])}</p><a class="text-link" href="/blog/{a["slug"]}/">Read article →</a></article>' for a in articles)
 insights_cards=''.join(f'<div class="insight-card"><span>{esc(t["name"])}</span><strong>{t["article_count"]}</strong><small>{t["fresh_count"]} fresh in 120 days</small></div>' for t in insights["topics"])
 gap_cards=''.join(f'<div class="gap-row"><span>{esc(x["slug"].replace("-"," ").title())}</span><strong>{x["article_count"]}</strong><small>articles</small></div>' for x in insights["content_gaps"][:6])
 (ROOT/'content-insights.html').write_text(shell('Content Insights','Editorial coverage, freshness and content-gap signals for the Laxman Nepal archive.',BASE+'/content-insights/',f'<div class="article-wrap"><section class="blog-hero"><p class="eyebrow">EDITORIAL INTELLIGENCE</p><h1>Content<br><em>Insights.</em></h1><p>Build-time signals from the archive: coverage, freshness and topic gaps. No traffic or engagement is fabricated.</p><div class="insight-summary"><div><strong>{insights["articles_total"]}</strong><span>Total articles</span></div><div><strong>{insights["fresh_articles_120d"]}</strong><span>Fresh · 120 days</span></div></div></section><section class="insight-section"><div class="section-head"><div><p class="eyebrow">TOPIC COVERAGE</p><h2>Where the archive is strong</h2></div></div><div class="insight-grid">{insights_cards}</div></section><section class="insight-section"><div class="section-head"><div><p class="eyebrow">CONTENT GAPS</p><h2>Topics with less coverage</h2><p class="section-note">These are archive coverage gaps, not demand predictions.</p></div></div><div class="gap-list">{gap_cards}</div></section></div>'),encoding='utf-8')
 article_cards=cards or "<p>No articles published yet.</p>"
 (OUT/'index.html').write_text(shell('Blog','Practical technology, AI, apps and productivity articles by Laxman Nepal.',BASE+'/blog/',f'<div class="article-wrap"><section class="blog-hero"><p class="eyebrow">Laxman Nepal Journal</p><h1>Useful ideas.<br><em>Explained simply.</em></h1><p>Practical guides about technology, AI, apps, productivity and digital work.</p><input id="blogFilter" class="search-box" placeholder="Filter articles…" aria-label="Filter articles"></section><section class="post-grid" id="postGrid">{article_cards}</section></div><script>const i=document.querySelector("#blogFilter");i?.addEventListener("input",()=>{const v=i.value.toLowerCase();document.querySelectorAll("#postGrid .post-card").forEach(c=>c.hidden=v&&!c.innerText.toLowerCase().includes(v))});</script>'),encoding='utf-8')
 items=''.join(f'<a class="tool-card" href="{esc(t["url"])}"><span class="tool-icon">{esc(t.get("icon","✦"))}</span><span class="tool-category">{esc(t.get("category","Tools"))}</span><h2>{esc(t["name"])}</h2><p>{esc(t["description"])}</p><span class="tool-open">Open tool →</span></a>' for t in TOOLS)
 (ROOT/'tools').mkdir(exist_ok=True); (ROOT/'tools'/'index.html').write_text(shell('Useful Tools','Explore practical web tools and utilities by Laxman Nepal.',BASE+'/tools/',f'<div class="article-wrap"><section class="blog-hero"><p class="eyebrow">Laxman Tools</p><h1>Useful tools.<br><em>One place.</em></h1><p>Fast browser tools for creators, productivity, Nepal and everyday digital work.</p><input id="toolSearch" class="search-box" placeholder="Search tools…" aria-label="Search tools"></section><section class="tools-grid" id="toolGrid">{items}</section></div><script>const s=document.querySelector("#toolSearch");s?.addEventListener("input",()=>{const v=s.value.toLowerCase();document.querySelectorAll("#toolGrid .tool-card").forEach(c=>c.hidden=!c.innerText.toLowerCase().includes(v))});</script>'),encoding='utf-8')
 search=[{'title':a['title'],'description':a['description'],'url':f'{BASE}/blog/{a["slug"]}/','type':'article'} for a in articles]+[{'title':t['name'],'description':t['description'],'url':t['url'],'type':'tool'} for t in TOOLS]; (ROOT/'search-index.json').write_text(json.dumps(search,ensure_ascii=False,indent=2),encoding='utf-8')
 feed=''.join(f'<item><title>{esc(a["title"])}</title><link>{esc(BASE+"/blog/"+a["slug"]+"/")}</link><guid>{esc(BASE+"/blog/"+a["slug"]+"/")}</guid><pubDate>{format_datetime(datetime.strptime(a["updated"],"%Y-%m-%d").replace(tzinfo=timezone.utc),usegmt=True)}</pubDate><description>{esc(a["description"])}</description></item>' for a in articles); (ROOT/'feed.xml').write_text('<?xml version="1.0"?><rss version="2.0"><channel><title>Laxman Nepal</title><link>'+BASE+'</link>'+feed+'</channel></rss>',encoding='utf-8')
 urls={BASE+'/':date10(''),BASE+'/blog/':date10(''),BASE+'/tools/':date10('')}; urls.update({f'{BASE}/blog/{a["slug"]}/':a['updated'] for a in articles}); urls.update({t['url']:t.get('updated',urls[BASE+'/tools/']) for t in TOOLS}); (ROOT/'sitemap.xml').write_text('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{esc(u)}</loc><lastmod>{d}</lastmod></url>' for u,d in sorted(urls.items()))+'</urlset>',encoding='utf-8')
 (ROOT/'data'/'url-migration-map.json').write_text(json.dumps({'generated_at':datetime.now(timezone.utc).isoformat(),'source_domain':'https://www.laxmannepal.com.np','current_domain':BASE,'note':'Blogger-to-GitHub mapping. /apps is intentionally excluded.','mappings':migration},ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'data'/'content-migration-report.json').write_text(json.dumps({'generated_at':datetime.now(timezone.utc).isoformat(),'blog_articles_total':len(articles),'legacy_blogger_articles':sum(a.get('legacy',False) for a in articles),'native_markdown_articles':sum(not a.get('legacy',False) for a in articles),'migration_mappings':len(migration),'apps_touched':False},ensure_ascii=False,indent=2),encoding='utf-8')
 print(f'Built {len(articles)} blog articles ({len(migration)} Blogger imports) and {len(TOOLS)} tools; /apps was not modified.')
if __name__=='__main__': main()
