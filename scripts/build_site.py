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

def build_toc(content):
 items=re.findall(r'<h([2-6])[^>]*\bid="([^"]+)"[^>]*>(.*?)</h\1>',content,re.I|re.S)
 if not items: return ''
 links=[]
 for level,anchor,inner in items:
  label=re.sub(r'<[^>]+>',' ',inner); label=re.sub(r'\s+',' ',html.unescape(label)).strip()
  if label: links.append(f'<a class="toc-link toc-level-{level}" href="#{esc(anchor)}">{esc(label,False)}</a>')
 return ''.join(links)

def related_articles(current, articles, limit=4):
 terms=set(re.findall(r'[a-z0-9]+', (current.get('title','')+' '+current.get('category','')).lower()))
 scored=[]
 for item in articles:
  if item.get('slug')==current.get('slug'): continue
  item_terms=set(re.findall(r'[a-z0-9]+', (item.get('title','')+' '+item.get('category','')).lower()))
  score=(3 if item.get('category')==current.get('category') else 0)+len(terms & item_terms)
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
 for a in articles:
  url=f'{BASE}/blog/{a["slug"]}/'; mins=max(1,round(len(re.findall(r'\b[\w’\'-]+\b',a['source']))/220))
  related=related_articles(a,articles,4)
  related_html=''.join(f'<article class="post-card"><p class="eyebrow">{esc(r["category"])} · {r["date"]}</p><h2><a href="/blog/{r["slug"]}/">{esc(r["title"])}</a></h2><p>{esc(r["description"])}</p><a class="text-link" href="/blog/{r["slug"]}/">Read article →</a></article>' for r in related)
  breadcrumbs={'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':BASE+'/'},{'@type':'ListItem','position':2,'name':'Blog','item':BASE+'/blog/'},{'@type':'ListItem','position':3,'name':a['title'],'item':url}]}
  article_html=add_heading_ids(a['source'])
  toc=build_toc(article_html)
  toc_html=f'<aside class="article-toc" aria-label="Table of contents"><div class="toc-title">On this page</div>{toc}</aside>' if toc else ''
  article_tools='''<div class="article-tools" aria-label="Article actions"><button type="button" data-share>↗ Share</button><button type="button" data-copy>⧉ Copy link</button></div>'''
  article_script='''<script>(()=>{const bar=document.querySelector('[data-reading-progress] span'),article=document.querySelector('.article-content');const update=()=>{if(!bar||!article)return;const r=article.getBoundingClientRect(),top=window.scrollY+r.top,total=Math.max(1,article.scrollHeight-innerHeight*.35),p=Math.min(1,Math.max(0,(window.scrollY-top+innerHeight*.2)/total));bar.style.width=(p*100)+'%'};addEventListener('scroll',update,{passive:true});addEventListener('resize',update);update();const share=document.querySelector('[data-share]');share?.addEventListener('click',async()=>{try{if(navigator.share)await navigator.share({title:document.title,text:document.querySelector('.article-description')?.textContent||'',url:location.href});else await navigator.clipboard.writeText(location.href)}catch(e){}});const copy=document.querySelector('[data-copy]');copy?.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href);const old=copy.textContent;copy.textContent='✓ Copied';setTimeout(()=>copy.textContent=old,1600)}catch(e){copy.textContent='Copy unavailable'}})})();</script>'''
  body=f'''<div class="reading-progress" data-reading-progress aria-hidden="true"><span></span></div><div class="article-wrap"><article><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/blog/">Blog</a> / {esc(a["title"])}</nav><header class="article-header"><p class="eyebrow">{esc(a["category"])} · ~{mins} min read</p><h1>{esc(a["title"])}</h1><p class="article-description">{esc(a["description"])}</p><div class="article-meta">By {esc(a["author"])} · Published {a["date"]} · Updated {a["updated"]}</div>{article_tools}</header>{toc_html}<div class="article-content">{article_html}</div></article><section class="related-section"><div class="section-head"><div><p class="eyebrow">KEEP READING</p><h2>Related articles</h2><p>More from {esc(a["category"])} and nearby topics.</p></div><a href="/blog/">View all →</a></div><div class="post-grid">{related_html}</div></section></div>'''
  og_image=write_og_svg(a['title'],a['slug'],a['description'])
  body += article_script
  d=OUT/a['slug']; d.mkdir(parents=True,exist_ok=True); (d/'index.html').write_text(shell(a['title'],a['description'],url,body,'Article',{'datePublished':a['date'],'dateModified':a['updated'],'breadcrumb':breadcrumbs,'image':og_image},og_image),encoding='utf-8')
  if a.get('legacy_path'): migration.append({'old_path':a['legacy_path'],'old_url':a.get('original_url',''),'new_path':'/blog/'+a['slug']+'/','new_url':url,'title':a['title']})
 cards=''.join(f'<article class="post-card"><p class="eyebrow">{esc(a["category"])} · {a["date"]}</p><h2><a href="/blog/{a["slug"]}/">{esc(a["title"])}</a></h2><p>{esc(a["description"])}</p><a class="text-link" href="/blog/{a["slug"]}/">Read article →</a></article>' for a in articles)
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
