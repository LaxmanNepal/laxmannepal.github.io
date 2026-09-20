import { getAllContent } from "@/lib/content";
export default function Page(){
 const posts=getAllContent().filter(p=>/phone|mobile|iphone|xiaomi|redmi|samsung|pixel|oneplus/i.test((p.title||"")+" "+p.tags.join(" "))).slice(0,30);
 return <main className="container page"><p className="eyebrow">PHONES</p><h1>Phones</h1><p className="muted">Phone guides, comparisons, prices and smartphone resources from the archive.</p><div className="post-grid">{posts.map((p,i)=><a className="post-card" key={p.id} href={p.path}><span className="post-number">{String(i+1).padStart(2,"0")}</span><h3>{p.title}</h3><p>Phone resource · {p.published?.slice(0,10)||"Archive"}</p><span className="read">Explore →</span></a>)}</div></main>;
}