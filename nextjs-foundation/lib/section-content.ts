import { getAllContent, type BloggerPost } from "./content";

export function sectionPosts(keywords:string[], limit=30){
 const terms=keywords.map(k=>k.toLowerCase());
 return getAllContent()
  .filter(p=>terms.some(t=>((p.title||"")+" "+p.tags.join(" ")+" "+p.path).toLowerCase().includes(t)))
  .sort((a,b)=>new Date(b.published||b.updated||0).getTime()-new Date(a.published||a.updated||0).getTime())
  .slice(0,limit);
}

export function ArchiveCards({posts,tag="ARCHIVE"}:{posts:BloggerPost[]|any[];tag?:string}){
 return <div className="post-grid">{posts.map((p:any,i:number)=>
  <a className="post-card" key={p.id||p.path} href={p.path}>
   <span className="post-number">{String(i+1).padStart(2,"0")}</span>
   <span className="tag">{tag}</span>
   <h3>{p.title||"Untitled post"}</h3>
   <p>{p.published?.slice(0,10)||"Archive"} · Explore the full article.</p>
   <span className="read">Read article →</span>
  </a>
 )}</div>
}
