'use client';
import { useCallback, useEffect, useMemo, useState } from "react";

type Story = { id?: string; title: string; url: string; published_at: string; source?: string; category?: string; description?: string; image?: string };
const CATEGORIES = ["All","Nepal","World","Politics","Business","Technology","Science","Sports","Entertainment","Trending","Health","Education"];
const WEEK = 7 * 86400000;
const PAGE_SIZE = 18;

function safeUrl(value?: string) {
  try { const u = new URL(value || ""); return ["https:","http:"].includes(u.protocol) ? u.href : ""; } catch { return ""; }
}
function clean(value: Story): Story | null {
  const url = safeUrl(value.url), date = Date.parse(value.published_at || ""), title = String(value.title || "").replace(/\s+/g," ").trim();
  if (!url || !title || !Number.isFinite(date) || Date.now() - date > WEEK || date > Date.now() + 3600000) return null;
  return { id:value.id || url, title, url, published_at:new Date(date).toISOString(), source:String(value.source || "Original publisher").slice(0,100), category:CATEGORIES.includes(value.category || "") && value.category !== "All" ? value.category : "World", description:String(value.description || "").replace(/<[^>]*>/g," ").replace(/\s+/g," ").trim().slice(0,320), image:safeUrl(value.image) };
}
function ago(value:string) { const m=Math.max(0,Math.floor((Date.now()-Date.parse(value))/60000)); return !Number.isFinite(m)?"Recently":m<60?`${m} min ago`:m<1440?`${Math.floor(m/60)} hr ago`:m<2880?"Yesterday":`${Math.floor(m/1440)} days ago`; }
function dateLabel(value:string) { return new Date(value).toLocaleString("en",{month:"short",day:"numeric",hour:"numeric",minute:"2-digit"}); }

type NewsDeskProps = { initialStories?: Story[]; initialGeneratedAt?: string };\n\nexport default function NewsDesk({ initialStories = [], initialGeneratedAt = "" }: NewsDeskProps) {
  const [stories,setStories]=useState<Story[]>(initialStories.map(clean).filter((s): s is Story => Boolean(s)));
  const [category,setCategory]=useState("All");
  const [query,setQuery]=useState("");
  const [sort,setSort]=useState("newest");
  const [limit,setLimit]=useState(PAGE_SIZE);
  const [loading,setLoading]=useState(initialStories.length===0);
  const [error,setError]=useState("");
  const [generatedAt,setGeneratedAt]=useState(initialGeneratedAt);

  const refresh=useCallback(async(quiet=false)=>{
    if(!quiet)setLoading(true);
    try {
      const response=await fetch(`/news/news-feed.json?t=${Date.now()}`,{cache:"no-store"});
      if(!response.ok)throw new Error(`News feed returned HTTP ${response.status}`);
      const data=await response.json(), raw:Story[]=Array.isArray(data)?data:(data.stories||data.items||[]);
      const unique=new Map<string,Story>();
      raw.map(clean).filter((s):s is Story=>Boolean(s)).forEach(s=>{
        const key=s.url.replace(/[?#].*$/,"").replace(/\/$/,"").toLowerCase(),old=unique.get(key);
        if(!old||Date.parse(s.published_at)>Date.parse(old.published_at))unique.set(key,s);
      });
      setStories([...unique.values()].sort((a,b)=>Date.parse(b.published_at)-Date.parse(a.published_at)));
      setGeneratedAt(data.generated_at||data.updated_at||"");setError("");
    } catch(e) { setError(e instanceof Error?e.message:"The news feed could not be loaded."); }
    finally { setLoading(false); }
  },[]);
  useEffect(()=>{void refresh();const timer=window.setInterval(()=>void refresh(true),300000);return()=>window.clearInterval(timer);},[refresh]);

  const filtered=useMemo(()=>{
    const q=query.trim().toLocaleLowerCase();
    return stories.filter(s=>(category==="All"||s.category===category)&&(!q||[s.title,s.description,s.source,s.category].join(" ").toLocaleLowerCase().includes(q)))
      .sort((a,b)=>sort==="oldest"?Date.parse(a.published_at)-Date.parse(b.published_at):Date.parse(b.published_at)-Date.parse(a.published_at));
  },[stories,category,query,sort]);
  const featured=filtered[0], hasFeatured=category==="All"&&!query&&sort==="newest"&&Boolean(featured);
  const visible=filtered.slice(hasFeatured?1:0,limit+(hasFeatured?1:0));
  const hasMore=filtered.length>limit+(hasFeatured?1:0);
  const counts=useMemo(()=>Object.fromEntries(CATEGORIES.filter(c=>c!=="All").map(c=>[c,stories.filter(s=>s.category===c).length])),[stories]);
  const refreshed=generatedAt?new Date(generatedAt).toLocaleString("en",{month:"short",day:"numeric",hour:"numeric",minute:"2-digit"}):"Waiting for first refresh";

  return <main className="newsdesk container">
    <section className="newsdesk-hero">
      <div className="newsdesk-kicker"><span className="newsdesk-live-dot"/> NEWSROOM · UPDATED AUTOMATICALLY</div>
      <h1>What’s happening.<br/><span>In Nepal and beyond.</span></h1>
      <p>One place for the past seven days of Nepal, world, technology, business, politics, science, sports, entertainment and trending stories. Every headline links to its original publisher.</p>
      <div className="newsdesk-meta"><span>{stories.length.toLocaleString()} recent stories · 7-day window</span><span>Feed updated {refreshed}</span><button className="newsdesk-refresh" onClick={()=>void refresh()} disabled={loading} type="button">{loading?"Refreshing…":"↻ Refresh news"}</button></div>
    </section>
    <section className="newsdesk-controls" aria-label="Search and filter news">
      <label className="newsdesk-search"><span aria-hidden="true">⌕</span><input type="search" value={query} onChange={e=>{setQuery(e.target.value);setLimit(PAGE_SIZE);}} placeholder="Search headlines, topics or publishers…" aria-label="Search headlines, topics or publishers"/></label>
      <label className="newsdesk-sort"><span>Sort</span><select value={sort} onChange={e=>setSort(e.target.value)} aria-label="Sort news"><option value="newest">Newest first</option><option value="oldest">Oldest first</option></select></label>
    </section>
    <div className="newsdesk-tabs" role="tablist" aria-label="News categories">{CATEGORIES.map(c=><button type="button" role="tab" aria-selected={category===c} className={category===c?"active":""} key={c} onClick={()=>{setCategory(c);setLimit(PAGE_SIZE);}}>{c}{c!=="All"&&<span>{counts[c]||0}</span>}</button>)}</div>
    {error&&<div className="newsdesk-notice" role="status"><strong>Could not refresh the feed.</strong> {stories.length?"Showing the last stories already loaded. ":""}{error} <button type="button" onClick={()=>void refresh()}>Try again</button></div>}
    {!error&&!loading&&stories.length===0&&<div className="newsdesk-notice" role="status"><strong>No recent stories were returned.</strong> The scheduled collector may be temporarily unable to reach its RSS sources. Try again shortly.</div>}
    {hasFeatured&&featured&&<section className="newsdesk-featured" aria-label="Top recent story">
      <div className="newsdesk-featured-copy"><span className="newsdesk-label">LATEST HEADLINE</span><span className="newsdesk-category">{featured.category}</span><h2><a href={featured.url} target="_blank" rel="noopener noreferrer">{featured.title}</a></h2>{featured.description&&<p>{featured.description}</p>}<div className="newsdesk-byline"><span>{featured.source}</span><span>{ago(featured.published_at)}</span></div><a className="newsdesk-read-link" href={featured.url} target="_blank" rel="noopener noreferrer">Read at original source ↗</a></div>
      {featured.image?<a className="newsdesk-featured-image" href={featured.url} target="_blank" rel="noopener noreferrer"><img src={featured.image} alt="" loading="lazy" referrerPolicy="no-referrer"/></a>:<div className="newsdesk-featured-art" aria-hidden="true"><span>LN</span><small>NEWS · WORLD · TECHNOLOGY</small></div>}
    </section>}
    <div className="newsdesk-section-head"><div><span className="newsdesk-label">THE LAST SEVEN DAYS</span><h2>{category==="All"?"Latest headlines":`${category} news`}</h2><p>Latest first · Original publisher links · No full articles copied</p></div><strong>{filtered.length.toLocaleString()} stories</strong></div>
    {loading&&stories.length===0?<div className="newsdesk-loading" aria-label="Loading news"><i/><i/><i/><i/><i/><i/></div>:
      <div className="newsdesk-grid">{visible.map(s=><article className="newsdesk-card" key={s.id||s.url}>
        {s.image?<a className="newsdesk-card-image" href={s.url} target="_blank" rel="noopener noreferrer"><img src={s.image} alt="" loading="lazy" referrerPolicy="no-referrer"/></a>:<div className="newsdesk-card-placeholder" aria-hidden="true">📰</div>}
        <div className="newsdesk-card-body"><div className="newsdesk-card-meta"><span className="newsdesk-category">{s.category}</span><time dateTime={s.published_at}>{ago(s.published_at)}</time></div><h3><a href={s.url} target="_blank" rel="noopener noreferrer">{s.title}</a></h3>{s.description&&<p>{s.description}</p>}<div className="newsdesk-card-source"><span>{s.source} · {dateLabel(s.published_at)}</span><a href={s.url} target="_blank" rel="noopener noreferrer" aria-label={`Read ${s.title} at original source`}>Read ↗</a></div></div>
      </article>)}{!visible.length&&<div className="newsdesk-empty"><strong>No matching stories</strong><span>Try another category or search term.</span><button type="button" onClick={()=>{setCategory("All");setQuery("");}}>Clear filters</button></div>}</div>}
    {hasMore&&<button className="newsdesk-more" type="button" onClick={()=>setLimit(n=>n+PAGE_SIZE)}>Load more headlines ({Math.min(PAGE_SIZE,filtered.length-limit-(hasFeatured?1:0))} more)</button>}
    <section className="newsdesk-bottom"><div><span className="newsdesk-label">COVERAGE</span><h2>More than one beat.</h2><p>Follow the stories that matter to you, from Nepal and the region to global technology and culture.</p></div><div className="newsdesk-category-list">{CATEGORIES.filter(c=>c!=="All").map(c=><button type="button" key={c} onClick={()=>{setCategory(c);setLimit(PAGE_SIZE);window.scrollTo({top:360,behavior:"smooth"});}}><span>{c}</span><strong>{counts[c]||0}</strong><span>↗</span></button>)}</div></section>
    <p className="newsdesk-disclaimer">Headlines, summaries and images are supplied by feeds and their publishers. Laxman Nepal links to original reporting and does not claim authorship of third-party news.</p>
  </main>;
}
