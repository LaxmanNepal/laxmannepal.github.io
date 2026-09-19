import Link from "next/link";
import { getAllContent } from "@/lib/content";

const sections = [
  { path:"/news/", type:"news", title:"News", description:"Technology and digital updates." },
  { path:"/guides/", type:"guide", title:"Guides", description:"Practical how-to articles and tutorials." },
  { path:"/reviews/", type:"review", title:"Reviews", description:"Hands-on product and software coverage." },
  { path:"/tools/", type:"tool", title:"Tools", description:"Free tools built for everyday use." },
  { path:"/ai/", type:"ai", title:"AI", description:"Useful AI tools, workflows and explainers." },
  { path:"/youtube/", type:"youtube", title:"YouTube", description:"Creator intelligence, analytics and strategy." },
] as const;

export default function ContentHub() {
  const posts=getAllContent();
  const latest=posts.slice(0,12);
  return <main className="container page">
    <section className="hero"><p className="eyebrow">CONTENT HUB</p><h1>Technology, tools & AI — organized.</h1><p className="muted">One content engine for news, guides, reviews, tools and creator intelligence.</p></section>
    <section className="section"><div className="section-heading"><div><p className="eyebrow">EXPLORE</p><h2>What are you looking for?</h2></div></div>
      <div className="listing">{sections.map(s=><Link className="card" href={s.path} key={s.type}><span className="tag">{s.type.toUpperCase()}</span><h3>{s.title}</h3><p>{s.description}</p></Link>)}</div>
    </section>
    <section className="section"><div className="section-heading"><div><p className="eyebrow">LATEST</p><h2>Latest articles</h2></div><span className="muted">{posts.length} indexed</span></div>
      <div className="post-grid">{latest.map((post,i)=><article className="post-card" key={post.id}><span className="post-number">{String(i+1).padStart(2,"0")}</span><div><span className="tag">{post.type}</span><h3>{post.title}</h3><p className="muted">{post.published?new Intl.DateTimeFormat("en",{year:"numeric",month:"short",day:"numeric"}).format(new Date(post.published)):""}</p><a href={post.path}>Read article →</a></div></article>)}</div>
    </section>
  </main>;
}
