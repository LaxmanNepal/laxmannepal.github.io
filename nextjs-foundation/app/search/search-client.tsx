"use client";

import { useMemo, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import type { BloggerPost } from "@/lib/content";

function score(post:BloggerPost,q:string){
  const title=(post.title||"").toLowerCase(), tags=(post.tags||[]).join(" ").toLowerCase(), path=post.path.toLowerCase();
  let n=0;
  if(title===q)n+=100; else if(title.startsWith(q))n+=50; else if(title.includes(q))n+=30;
  if(tags.includes(q))n+=20;
  if(path.includes(q))n+=10;
  return n;
}

export default function SearchClient({posts}:{posts:BloggerPost[]}){
  const params=useSearchParams();
  const router=useRouter();
  const initial=params.get("q")||"";
  const [query,setQuery]=useState(initial);
  const [type,setType]=useState("all");

  const types=useMemo(()=>["all",...Array.from(new Set(posts.map(p=>p.type||"blog"))).sort()],[posts]);

  const results=useMemo(()=>{
    const q=query.trim().toLowerCase();
    let list=posts.filter(p=>type==="all"||(p.type||"blog")===type);
    if(!q)return list.slice(0,30);
    return list.filter(p=>{
      const hay=[p.title||"",...(p.tags||[]),p.path].join(" ").toLowerCase();
      return hay.includes(q);
    }).sort((a,b)=>score(b,q)-score(a,q)||new Date(b.published||b.updated||0).getTime()-new Date(a.published||a.updated||0).getTime()).slice(0,30);
  },[posts,query,type]);

  function updateQuery(value:string){
    setQuery(value);
    const next=new URLSearchParams(params.toString());
    if(value.trim())next.set("q",value.trim());else next.delete("q");
    router.replace(`/search/${next.toString()?`?${next.toString()}`:""}`,{scroll:false});
  }

  return <main className="container article-shell">
    <div className="article-meta"><span className="tag">SEARCH</span><span className="tag">{posts.length} POSTS</span></div>
    <h1 className="article-title">Search Laxman Nepal</h1>
    <p className="article-lead">Search titles, tags and archive paths. Results are ranked by relevance — no external API required.</p>
    <div className="search-controls">
      <input className="search-input" value={query} onChange={e=>updateQuery(e.target.value)} placeholder="Search articles, phones, AI, YouTube…" aria-label="Search articles"/>
      <div className="archive-years" role="group" aria-label="Filter search results by content type">
        {types.map(t=><button key={t} type="button" className={type===t?"active":""} onClick={()=>setType(t)}>{t==="all"?"All":t.toUpperCase()}</button>)}
      </div>
    </div>
    <div className="archive-status" aria-live="polite">Showing <strong>{results.length}</strong> results{query&&<> for <strong>“{query}”</strong></>}{type!=="all"&&<> · {type.toUpperCase()}</>}</div>
    <section className="related-grid search-results">
      {results.map(post=><a className="card" href={post.path} key={post.path}>
        <span className="tag">{(post.type||"blog").toUpperCase()}</span>
        <h3>{post.title}</h3>
        <p>{post.tags?.slice(0,4).join(" · ")||"Technology archive"} · {post.published?new Intl.DateTimeFormat("en",{year:"numeric",month:"short",day:"numeric"}).format(new Date(post.published)):"Archive"} →</p>
      </a>)}
    </section>
    {!results.length&&<div className="empty-state"><strong>No matching articles found.</strong><p>Try a broader keyword, another content type, or clear the search.</p></div>}
  </main>;
}
