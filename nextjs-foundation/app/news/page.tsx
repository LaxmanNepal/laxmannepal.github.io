import { getAllContent } from "@/lib/content";
export default function Page(){
 const posts=getAllContent().slice(0,30);
 return <main className="container page"><p className="eyebrow">NEWS</p><h1>Latest technology news</h1><p className="muted">Automatically populated from the latest articles in the Laxman Nepal content archive.</p><div className="post-grid">{posts.map((p,i)=><a className="post-card" key={p.id} href={p.path}><span className="post-number">{String(i+1).padStart(2,"0")}</span><h3>{p.title}</h3><p>{p.published?.slice(0,10)||"Archive"}</p><span className="read">Read article →</span></a>)}</div></main>;
}