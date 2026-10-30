'use client';
import { useCallback, useEffect, useMemo, useState } from "react";
import "./news-desk-enhancements.css";

type Story = { id?: string; title: string; url: string; published_at: string; source?: string; category?: string; description?: string; image?: string; region?: string; language?: string };
const CATEGORIES = ["All","General","Politics","Business","Technology","Science","Sports","Entertainment","Trending","Health","Education"];
const CATEGORY_NE: Record<string,string> = { All:"सबै", General:"सामान्य", Politics:"राजनीति", Business:"अर्थतन्त्र", Technology:"प्रविधि", Science:"विज्ञान", Sports:"खेलकुद", Entertainment:"मनोरञ्जन", Trending:"ट्रेन्डिङ", Health:"स्वास्थ्य", Education:"शिक्षा" };
const WEEK = 7 * 86400000;
const PAGE_SIZE = 18;

function safeUrl(value?: string) {
  try { const u = new URL(value || ""); return ["https:","http:"].includes(u.protocol) ? u.href : ""; } catch { return ""; }
}
function clean(value: Story): Story | null {
  const url = safeUrl(value.url), date = Date.parse(value.published_at || ""), title = String(value.title || "").replace(/\s+/g," ").trim();
  if (!url || !title || !Number.isFinite(date) || Date.now() - date > WEEK || date > Date.now() + 3600000) return null;
  const inferredRegion = /नेपाल|nepal|nepalese/i.test(title + " " + String(value.source || "")) || value.category === "Nepal" ? "Nepal" : "World";
  const language = value.language === "ne" || /[\u0900-\u097F]/.test(title) ? "ne" : "en";
  return { id:value.id || url, title, url, published_at:new Date(date).toISOString(), source:String(value.source || "Original publisher").slice(0,100), category:value.category === "Nepal" ? "General" : CATEGORIES.includes(value.category || "") && value.category !== "All" ? value.category : "Trending", region:value.region === "Nepal" || value.region === "World" ? value.region : inferredRegion, language, description:String(value.description || "").replace(/<[^>]*>/g," ").replace(/\s+/g," ").trim().slice(0,320), image:safeUrl(value.image) };
}
function dateLabel(value:string) { return new Date(value).toLocaleDateString("ne-NP",{year:"numeric",month:"short",day:"numeric"}); }
function ago(value:string) { const m=Math.max(0,Math.floor((Date.now()-Date.parse(value))/60000)); return !Number.isFinite(m)?"भर्खरै":m<60?`${m} मिनेटअघि`:m<1440?`${Math.floor(m/60)} घण्टाअघि`:m<2880?"हिजो":`${Math.floor(m/1440)} दिनअघि`; }

type NewsDeskProps = { initialStories?: Story[]; initialGeneratedAt?: string };

export default function NewsDesk({ initialStories = [], initialGeneratedAt = "" }: NewsDeskProps) {
  const [stories,setStories]=useState<Story[]>(initialStories.map(clean).filter((s): s is Story => Boolean(s)));
  const [region,setRegion]=useState("Nepal");
  const [language,setLanguage]=useState("ne");
  const [category,setCategory]=useState("All");
  const [query,setQuery]=useState("");
  const [sort,setSort]=useState("newest");
  const [limit,setLimit]=useState(PAGE_SIZE);
  const [loading,setLoading]=useState(initialStories.length===0);
  const [error,setError]=useState("");
  const [generatedAt,setGeneratedAt]=useState(initialGeneratedAt);
  const [savedStories,setSavedStories]=useState<Story[]>([]);
  const [savedLoaded,setSavedLoaded]=useState(false);
  const [showSaved,setShowSaved]=useState(false);
  const [compact,setCompact]=useState(false);
  const [brokenImages,setBrokenImages]=useState<string[]>([]);

  useEffect(()=>{
    try { const raw=window.localStorage.getItem("ln-news-saved-v1"); if(raw){const parsed=JSON.parse(raw);if(Array.isArray(parsed))setSavedStories(parsed.filter((v):v is Story=>Boolean(v&&typeof v==="object"&&typeof v.url==="string"&&typeof v.title==="string"&&safeUrl(v.url)===v.url)));} }
    catch { /* Saved stories are optional; private browsing may block storage. */ }
    setSavedLoaded(true);
  },[]);
  useEffect(()=>{if(savedLoaded){try{window.localStorage.setItem("ln-news-saved-v1",JSON.stringify(savedStories));}catch{/* Continue without persistent saves if storage is unavailable. */}}},[savedStories,savedLoaded]);
  const savedUrls=useMemo(()=>savedStories.map(s=>s.url),[savedStories]);
  const toggleSaved=useCallback((story:Story)=>setSavedStories(current=>current.some(s=>s.url===story.url)?current.filter(s=>s.url!==story.url):[story,...current]),[]);
  const isSaved=useCallback((url:string)=>savedUrls.includes(url),[savedUrls]);
  const markImageBroken=useCallback((url:string)=>setBrokenImages(current=>current.includes(url)?current:[...current,url]),[]);

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
    return (showSaved?savedStories:stories).filter(s=>s.region===region&&(language==="all"||s.language===language)&&(category==="All"||s.category===category)&&(!q||[s.title,s.description,s.source,s.category].join(" ").toLocaleLowerCase().includes(q)))
      .sort((a,b)=>sort==="oldest"?Date.parse(a.published_at)-Date.parse(b.published_at):Date.parse(b.published_at)-Date.parse(a.published_at));
  },[stories,savedStories,region,language,category,query,sort,showSaved]);
  const featured=filtered[0], hasFeatured=category==="All"&&!query&&sort==="newest"&&Boolean(featured);
  const visible=filtered.slice(hasFeatured?1:0,limit+(hasFeatured?1:0));
  const hasMore=filtered.length>limit+(hasFeatured?1:0);
  const regionStories=useMemo(()=>(showSaved?savedStories:stories).filter(s=>s.region===region&&(language==="all"||s.language===language)),[stories,savedStories,showSaved,region,language]);
  const counts=useMemo(()=>Object.fromEntries(CATEGORIES.filter(c=>c!=="All").map(c=>[c,regionStories.filter(s=>s.category===c).length])),[regionStories]);
  const refreshed=generatedAt?new Date(generatedAt).toLocaleString("ne-NP",{month:"short",day:"numeric",hour:"numeric",minute:"2-digit"}):"पहिलो अपडेटको प्रतीक्षामा";

  return <main className="newsdesk container" lang="ne">
    <section className="newsdesk-hero">
      <div className="newsdesk-kicker"><span className="newsdesk-live-dot"/> समाचार कक्ष · स्वचालित अपडेट</div>
      <h1>नेपालका ताजा समाचार।<br/><span>विश्वभरका खबर पनि।</span></h1>
      <p>नेपालका पछिल्ला सात दिनका समाचार नेपाली भाषामा पढ्नुहोस्। राजनीति, अर्थतन्त्र, प्रविधि, खेलकुद, स्वास्थ्य, शिक्षा र मनोरञ्जनका विषय छान्नुहोस्। विश्व छान्दा विश्वसम्बन्धी समाचार देखिन्छन्।</p>
      <div className="newsdesk-meta"><span>{filtered.length.toLocaleString()} समाचार · पछिल्ला ७ दिन</span><span>अन्तिम अपडेट {refreshed}</span><div className="newsdesk-toolbar-actions"><button className={showSaved?"newsdesk-save-toggle active":"newsdesk-save-toggle"} type="button" aria-pressed={showSaved} onClick={()=>{setShowSaved(v=>!v);setLimit(PAGE_SIZE);}}>★ सुरक्षित ({savedUrls.length})</button><button className="newsdesk-refresh" onClick={()=>void refresh()} disabled={loading} type="button">{loading?"अपडेट हुँदैछ…":"↻ समाचार अपडेट"}</button></div></div>
    </section>
    <section className="newsdesk-controls" aria-label="समाचार खोज र फिल्टर">
      <label className="newsdesk-search"><span aria-hidden="true">⌕</span><input type="search" value={query} onChange={e=>{setQuery(e.target.value);setLimit(PAGE_SIZE);}} placeholder="समाचार, विषय वा प्रकाशक खोज्नुहोस्…" aria-label="समाचार खोज्नुहोस्"/></label>
      <label className="newsdesk-sort"><span>क्रम</span><select value={sort} onChange={e=>setSort(e.target.value)} aria-label="समाचार क्रम"><option value="newest">नयाँ पहिले</option><option value="oldest">पुराना पहिले</option></select></label><button className={compact?"newsdesk-view-toggle active":"newsdesk-view-toggle"} type="button" aria-pressed={compact} onClick={()=>setCompact(v=>!v)}>{compact?"▦ कार्ड दृश्य":"☰ Compact सूची"}</button>
    </section>
    <div className="newsdesk-tabs newsdesk-region-tabs" role="group" aria-label="समाचार क्षेत्र">
      <button type="button" className={region==="Nepal"?"active":""} aria-pressed={region==="Nepal"} onClick={()=>{setRegion("Nepal");setLanguage("ne");setCategory("All");setLimit(PAGE_SIZE);}}>🇳🇵 नेपाल</button>
      <button type="button" className={region==="World"?"active":""} aria-pressed={region==="World"} onClick={()=>{setRegion("World");setLanguage("all");setCategory("All");setLimit(PAGE_SIZE);}}>🌍 विश्व</button>
      <label className="newsdesk-sort"><span>भाषा</span><select value={language} onChange={e=>{setLanguage(e.target.value);setLimit(PAGE_SIZE);}} aria-label="समाचार भाषा"><option value="ne">नेपाली</option><option value="all">सबै भाषा</option></select></label>
    </div>
    <div className="newsdesk-tabs" role="tablist" aria-label="समाचारका विधा">{CATEGORIES.map(c=><button type="button" role="tab" aria-selected={category===c} className={category===c?"active":""} key={c} onClick={()=>{setCategory(c);setLimit(PAGE_SIZE);}}>{CATEGORY_NE[c]}{c!=="All"&&<span>{counts[c]||0}</span>}</button>)}</div>
    {error&&<div className="newsdesk-notice" role="status"><strong>समाचार अपडेट हुन सकेन।</strong> {stories.length?"पहिले लोड भएका समाचार देखाइँदैछन्। ":""}{error} <button type="button" onClick={()=>void refresh()}>फेरि प्रयास गर्नुहोस्</button></div>}
    {!error&&!loading&&stories.length===0&&<div className="newsdesk-notice" role="status"><strong>हालसालैका समाचार भेटिएनन्।</strong> समाचार स्रोत अस्थायी रूपमा उपलब्ध नहुन सक्छन्। केहीबेरपछि फेरि प्रयास गर्नुहोस्।</div>}
    {hasFeatured&&featured&&<section className="newsdesk-featured" aria-label="Top recent story" lang={featured.language==="ne"?"ne":"en"}>
      <div className="newsdesk-featured-copy"><span className="newsdesk-label">मुख्य समाचार</span><span className="newsdesk-category">{CATEGORY_NE[featured.category||"Trending"]||featured.category}</span><h2><a href={featured.url} target="_blank" rel="noopener noreferrer">{featured.title}</a></h2>{featured.description&&<p>{featured.description}</p>}<div className="newsdesk-byline"><span>{featured.source}</span><span>{ago(featured.published_at)}</span></div><button className={isSaved(featured.url)?"newsdesk-bookmark saved":"newsdesk-bookmark"} type="button" aria-pressed={isSaved(featured.url)} onClick={()=>toggleSaved(featured)}>{isSaved(featured.url)?"★ सुरक्षित गरिएको":"☆ पछि पढ्न सुरक्षित"}</button><a className="newsdesk-read-link" href={featured.url} target="_blank" rel="noopener noreferrer">मूल स्रोतमा पढ्नुहोस् ↗</a></div>
      {featured.image&&!brokenImages.includes(featured.image)?<a className="newsdesk-featured-image" href={featured.url} target="_blank" rel="noopener noreferrer"><img src={featured.image} alt={`समाचारको तस्बिर: ${featured.title}`} loading="lazy" referrerPolicy="no-referrer" onError={()=>markImageBroken(featured.image||"")}/><span className="newsdesk-image-caption">प्रकाशकको फिडमा समावेश तस्बिर</span></a>:<div className="newsdesk-featured-art" aria-label="प्रकाशकले तस्बिर उपलब्ध गराएको छैन"><span>LN</span><small>तस्बिर उपलब्ध छैन</small></div>}
    </section>}
    <div className="newsdesk-section-head"><div><span className="newsdesk-label">पछिल्ला सात दिन</span><h2>{region==="Nepal"?"नेपालका समाचार":"विश्व समाचार"}{category!=="All"?` · ${CATEGORY_NE[category]}`:""}</h2><p>नयाँ समाचार पहिले · मूल प्रकाशकको लिंक</p></div><strong>{filtered.length.toLocaleString()} समाचार</strong></div>
    {loading&&stories.length===0?<div className="newsdesk-loading" aria-label="समाचार लोड हुँदैछ"><i/><i/><i/><i/><i/><i/></div>:
      <div className={compact?"newsdesk-grid compact":"newsdesk-grid"}>{visible.map(s=><article className={compact?"newsdesk-card compact":"newsdesk-card"} key={s.id||s.url} lang={s.language==="ne"?"ne":"en"}>
        {s.image&&!brokenImages.includes(s.image)?<a className="newsdesk-card-image" href={s.url} target="_blank" rel="noopener noreferrer"><img src={s.image} alt={`समाचारको तस्बिर: ${s.title}`} loading="lazy" referrerPolicy="no-referrer" onError={()=>markImageBroken(s.image||"")}/><span className="newsdesk-image-caption">प्रकाशकको तस्बिर</span></a>:<div className="newsdesk-card-placeholder" aria-label="प्रकाशकको फिडमा तस्बिर छैन">📰 <span>तस्बिर उपलब्ध छैन</span></div>}
        <div className="newsdesk-card-body"><div className="newsdesk-card-meta"><span className="newsdesk-category">{CATEGORY_NE[s.category||"Trending"]||s.category}</span><time dateTime={s.published_at}>{ago(s.published_at)}</time></div><h3><a href={s.url} target="_blank" rel="noopener noreferrer">{s.title}</a></h3>{s.description&&<p>{s.description}</p>}<div className="newsdesk-card-source"><span>{s.source} · {dateLabel(s.published_at)}</span><div className="newsdesk-card-actions"><button className={isSaved(s.url)?"newsdesk-bookmark saved":"newsdesk-bookmark"} type="button" aria-label={isSaved(s.url)?`Remove saved story: ${s.title}`:`Save story: ${s.title}`} aria-pressed={isSaved(s.url)} onClick={()=>toggleSaved(s)}>{isSaved(s.url)?"★":"☆"}</button><a href={s.url} target="_blank" rel="noopener noreferrer" aria-label={`Read ${s.title} at original source`}>पढ्नुहोस् ↗</a></div></div></div>
      </article>)}{!visible.length&&<div className="newsdesk-empty"><strong>मिल्दो समाचार भेटिएन</strong><span>अर्को विधि वा शब्दबाट खोज्नुहोस्।</span><button type="button" onClick={()=>{setCategory("All");setQuery("");setShowSaved(false);setLanguage(region==="Nepal"?"ne":"all");}}>फिल्टर हटाउनुहोस्</button></div>}</div>}
    {hasMore&&<button className="newsdesk-more" type="button" onClick={()=>setLimit(n=>n+PAGE_SIZE)}>थप समाचार ({Math.min(PAGE_SIZE,filtered.length-limit-(hasFeatured?1:0))} थप)</button>}
    <p className="newsdesk-disclaimer">समाचारका शीर्षक, सारांश र उपलब्ध तस्बिर RSS फिड वा प्रकाशकबाट आउँछन्। मिल्दो तस्बिर नभेटिएमा सामान्य तस्बिर राखिँदैन। Laxman Nepal ले मूल प्रकाशकमा लिंक गर्छ। सुरक्षित समाचार यही ब्राउजरमा मात्र रहन्छ।</p>
  </main>;
}
