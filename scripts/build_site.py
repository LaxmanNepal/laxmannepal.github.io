#!/usr/bin/env python3
"""Build blog, tool directory, search index, RSS and sitemap without dependencies."""
from __future__ import annotations
import html,json,re
from datetime import datetime,timezone
from email.utils import format_datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CFG=json.loads((ROOT/'site.config.json').read_text()); BASE=CFG['site_url'].rstrip('/'); BLOG=ROOT/'content/blog'; OUT=ROOT/'blog'; TOOLS=json.loads((ROOT/'data/tools.json').read_text()).get('tools',[])

def esc(v): return html.escape(str(v),quote=True)
def fm(text):
 m={}; body=text
 if text.startswith('---'):
  p=text.split('---',2)
  if len(p)==3:
   body=p[2].lstrip('\n')
   for line in p[1].splitlines():
    if ':' not in line: continue
    k,v=line.split(':',1); v=v.strip().strip('"\'')
    m[k.strip()]=[x.strip() for x in v.split(',') if x.strip()] if k.strip()=='tags' else v
 return m,body
def inline(t):
 t=html.escape(t,quote=False); t=re.sub(r'\[([^]]+)\]\((https?://[^)]+)\)',r'<a href="\2" rel="noopener noreferrer">\1</a>',t); t=re.sub(r'`([^`]+)`',r'<code>\1</code>',t); t=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',t); return re.sub(r'\*([^*]+)\*',r'<em>\1</em>',t)
def md(src):
 out=[]; para=[]; code=False; ul=False
 def flush():
  nonlocal para
  if para: out.append('<p>'+inline(' '.join(para))+'</p>'); para=[]
 for line in src.replace('\r\n','\n').split('\n'):
  if line.startswith('```'):
   if code: out.append('<pre><code>'+esc('\n'.join(para))+'</code></pre>'); para=[]; code=False
   else: flush(); code=True
   continue
  if code: para.append(line); continue
  if not line.strip(): flush();
  elif re.match(r'^#{1,3}\s+',line):
   flush();
   if ul: out.append('</ul>'); ul=False
   m=re.match(r'^(#{1,3})\s+(.+)$',line); lvl=len(m.group(1))+1; txt=inline(m.group(2)); ident=re.sub(r'[^a-z0-9]+','-',re.sub('<[^>]+>','',txt.lower())).strip('-'); out.append(f'<h{lvl} id="{esc(ident)}">{txt}</h{lvl}>')
  elif re.match(r'^[-*]\s+',line):
   flush()
   if not ul: out.append('<ul>'); ul=True
   out.append('<li>'+inline(re.sub(r'^[-*]\s+','',line))+'</li>')
  else:
   if ul: out.append('</ul>'); ul=False
   para.append(line)
 flush()
 if ul: out.append('</ul>')
 return '\n'.join(out)
def date(v,f):
 v=str(v or f)[:10]
 try: datetime.strptime(v,'%Y-%m-%d'); return v
 except ValueError: return f
def shell(title,desc,canonical,body,kind='website',image=''):
 img=f'<meta property="og:image" content="{esc(BASE+image if image.startswith("/") else image)}"><meta name="twitter:image" content="{esc(BASE+image if image.startswith("/") else image)}">' if image else ''
 schema='<script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@type':kind,'name':title,'url':canonical,'description':desc},ensure_ascii=False)+'</script>'
 return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#f5f7fb"><meta name="description" content="{esc(desc)}"><meta name="author" content="{esc(CFG["author"])}"><link rel="canonical" href="{esc(canonical)}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:type" content="{kind.lower()}"><meta property="og:url" content="{esc(canonical)}">{img}<meta name="twitter:card" content="summary_large_image"><title>{esc(title)} — {esc(CFG["site_name"])}</title><link rel="stylesheet" href="/assets/css/style.css"><link rel="stylesheet" href="/assets/css/light.css">{schema}</head><body><header class="site-header"><a class="brand" href="/"><span class="brand-mark">LN</span><span>Laxman Nepal</span></a><nav class="nav" aria-label="Primary navigation"><a href="/">Home</a><a href="/tools/">Tools</a><a href="/ai-tools/">AI Tools</a><a href="/blog/">Blog</a><a href="/#about">About</a></nav><a class="header-cta" href="/tools/">Explore <span>↗</span></a><button class="menu-button" aria-label="Open menu" aria-expanded="false">☰</button></nav></header><main>{body}</main><footer class="footer section-wrap"><div><strong>Laxman Nepal</strong><span>© {datetime.now().year} All rights reserved.</span></div><div><a href="/privacy/">Privacy</a><a href="/terms/">Terms</a><a href="/contact/">Contact</a><a href="/">Home ↑</a></div></footer><script defer src="/assets/js/app.js"></script></body></html>'
articles=[]
if BLOG.exists():
 for p in BLOG.glob('*.md'):
  if p.name.lower()=='readme.md': continue
  meta,src=fm(p.read_text(encoding='utf-8')); meta['title']=meta.get('title',p.stem.replace('-',' ').title()); meta['description']=meta.get('description','Practical technology, AI and productivity guidance by Laxman Nepal.'); meta['date']=date(meta.get('date'),datetime.now(timezone.utc).date().isoformat()); meta['updated']=date(meta.get('updated'),meta['date']); meta['author']=meta.get('author',CFG['author']); meta['category']=meta.get('category','Technology'); meta['tags']=meta.get('tags',[]) if isinstance(meta.get('tags',[]),list) else [str(meta['tags'])]; meta['slug']=re.sub(r'[^a-z0-9]+','-',p.stem.lower()).strip('-'); meta['url']=f'{BASE}/blog/{meta["slug"]}/'; meta['source']=src; articles.append(meta)
for a in articles:
 content=md(a['source']); words=len(re.findall(r"\b[\w’'-]+\b",re.sub('<[^>]+>',' ',content))); minutes=max(1,round(words/220)); tags=''.join(f'<a class="tag" href="/blog/?tag={esc(t)}">{esc(t)}</a>' for t in a['tags']); schema='<script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@type':'Article','headline':a['title'],'description':a['description'],'datePublished':a['date'],'dateModified':a['updated'],'author':{'@type':'Person','name':a['author']},'mainEntityOfPage':{'@type':'WebPage','@id':a['url']}},ensure_ascii=False)+'</script>'; body=f'<div class="article-wrap"><article><nav class="breadcrumbs"><a href="/">Home</a> / <a href="/blog/">Blog</a> / {esc(a["title"])}</nav><header class="article-header"><p class="eyebrow">{esc(a["category"])} · {minutes} min read</p><h1>{esc(a["title"])}</h1><p class="article-description">{esc(a["description"])}</p><div class="article-meta">By {esc(a["author"])} · Published {a["date"]} · Updated {a["updated"]}</div><div class="tags">{tags}</div></header><div class="article-content">{content}</div></article></div>'; out=OUT/a['slug']/ 'index.html'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(shell(a['title'],a['description'],a['url'],body,'Article',a.get('image','')).replace('</head>',schema+'</head>'),encoding='utf-8')
# Blog index with client-side tag filter
cards=''.join(f'<article class="post-card" data-tags="{esc(" ".join(a["tags"]))}" data-category="{esc(a["category"])}"><p class="eyebrow">{esc(a["category"])} · {a["date"]}</p><h2><a href="/blog/{a["slug"]}/">{esc(a["title"])}</a></h2><p>{esc(a["description"])}</p><a class="text-link" href="/blog/{a["slug"]}/">Read article →</a></article>' for a in sorted(articles,key=lambda x:x['date'],reverse=True)); b=f'<div class="article-wrap"><section class="blog-hero"><p class="eyebrow">Laxman Nepal Journal</p><h1>Useful ideas.<br><em>Explained simply.</em></h1><p>Practical guides about technology, AI, apps, productivity and digital work.</p><input id="blogFilter" class="search-box" placeholder="Filter by tag or category…" aria-label="Filter articles"></section><section class="post-grid" id="postGrid">{cards or "<p>No articles published yet.</p>"}</section></div><script>const q=new URLSearchParams(location.search).get("tag");const i=document.querySelector("#blogFilter");if(q&&i)i.value=q;function f(){const v=(i?.value||"").toLowerCase().trim();document.querySelectorAll("#postGrid .post-card").forEach(c=>c.hidden=v&&!((c.dataset.tags+" "+c.dataset.category).toLowerCase().includes(v)))}i?.addEventListener("input",f);f();</script>'; (OUT/'index.html').parent.mkdir(parents=True,exist_ok=True); (OUT/'index.html').write_text(shell('Blog — Laxman Nepal','Practical technology, AI, apps and productivity articles by Laxman Nepal.',BASE+'/blog/',b),encoding='utf-8')
# Tools generated from catalog
items=''.join(f'<a class="tool-card" href="{esc(t["url"])}" rel="noopener noreferrer"><span class="tool-icon">{esc(t.get("icon","✦"))}</span><span class="tool-category">{esc(t.get("category","Tools"))}</span><h2>{esc(t["name"])}</h2><p>{esc(t["description"])}</p><span class="tool-open">Open tool →</span></a>' for t in TOOLS)
tool_body=f'<div class="article-wrap"><section class="blog-hero"><p class="eyebrow">Laxman Apps</p><h1>Useful tools.<br><em>One place.</em></h1><p>Practical browser tools for Nepali users, productivity, finance and everyday digital work.</p><input id="toolSearch" class="search-box" placeholder="Search tools…" aria-label="Search tools"></section><section class="tools-grid" id="toolGrid">{items}</section><p class="tool-note">Catalog generated automatically from <code>data/tools.json</code>.</p></div><script>const s=document.querySelector("#toolSearch");s?.addEventListener("input",()=>{const v=s.value.toLowerCase();document.querySelectorAll("#toolGrid .tool-card").forEach(c=>c.hidden=!c.innerText.toLowerCase().includes(v))});</script>'
(OUT.parent/'tools'/'index.html').write_text(shell('Useful Tools — Laxman Nepal','Explore practical web tools and utilities by Laxman Nepal.',BASE+'/tools/',tool_body),encoding='utf-8')
# Search index
search=[{'title':a['title'],'description':a['description'],'url':a['url'],'type':'article','keywords':a['tags']} for a in articles]+[{'title':t['name'],'description':t['description'],'url':t['url'],'type':'tool','keywords':t.get('keywords',[])} for t in TOOLS]; (ROOT/'search-index.json').write_text(json.dumps(search,ensure_ascii=False,indent=2),encoding='utf-8')
# RSS
items=[]
for a in sorted(articles,key=lambda x:x['date'],reverse=True):
 dt=datetime.strptime(a['updated'],'%Y-%m-%d').replace(tzinfo=timezone.utc); items.append(f'<item><title>{esc(a["title"])}</title><link>{esc(a["url"])}</link><guid>{esc(a["url"])}</guid><pubDate>{format_datetime(dt,usegmt=True)}</pubDate><description>{esc(a["description"])}</description></item>')
(ROOT/'feed.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Laxman Nepal</title><link>'+BASE+'</link><description>'+esc(CFG['description'])+'</description>'+''.join(items)+'</channel></rss>',encoding='utf-8')
# Sitemap with real modified dates
urls={BASE+'/':datetime.now(timezone.utc).date().isoformat(),BASE+'/blog/':datetime.now(timezone.utc).date().isoformat(),BASE+'/tools/':datetime.now(timezone.utc).date().isoformat(),BASE+'/ai-tools/':datetime.now(timezone.utc).date().isoformat(),BASE+'/privacy/':datetime.now(timezone.utc).date().isoformat(),BASE+'/terms/':datetime.now(timezone.utc).date().isoformat(),BASE+'/contact/':datetime.now(timezone.utc).date().isoformat()}
for a in articles: urls[a['url']]=a['updated']
for t in TOOLS: urls[t['url']]=t.get('updated',urls[BASE+'/tools/'])
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{esc(u)}</loc><lastmod>{d}</lastmod></url>' for u,d in sorted(urls.items()))+'</urlset>',encoding='utf-8')
print(f'Built {len(articles)} articles and {len(TOOLS)} tools.')
