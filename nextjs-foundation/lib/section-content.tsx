import { getAllContent } from "@/lib/content";

export function sectionPosts(keywords:string[], limit=24){
  const all=getAllContent();
  const matches=all.filter(p=>keywords.some(k=>((p.title||"")+" "+p.tags.join(" ")).toLowerCase().includes(k.toLowerCase())));
  return (matches.length?matches:all).slice(0,limit);
}
export function ArchiveCards({posts,tag="ARTICLE"}:{posts:any[],tag?:string}){
  return <div className="post-grid">{posts.map((p:any,i:number)=><article className="post-card" key={p.id}>
    <div className="post-top"><span className="post-number">{String(i+1).padStart(2,"0")}</span><span className="tag">{tag}</span></div>
    <h3>{p.title}</h3><p>{p.published?new Intl.DateTimeFormat("en",{year:"numeric",month:"short",day:"numeric"}).format(new Date(p.published)):"Archive"}</p>
    <a className="read" href={p.path}>Read article →</a>
  </article>)}</div>
}
