import fs from "node:fs";
import path from "node:path";

type BloggerPost={title?:string;published?:string;updated?:string;path:string;original_url?:string};

function loadBloggerPosts(): BloggerPost[] {
  const manifestPath=path.join(process.cwd(),"..",".blogger-migration.json");
  try {
    const manifest=JSON.parse(fs.readFileSync(manifestPath,"utf8"));
    return Array.isArray(manifest.posts)
      ? manifest.posts.filter((post: BloggerPost)=>post?.path).sort((a: BloggerPost,b: BloggerPost)=>
          new Date(b.published||b.updated||0).getTime()-new Date(a.published||a.updated||0).getTime())
      : [];
  } catch {
    return [];
  }
}

function postDescription(title:string){
  const t=title.toLowerCase();
  if(t.includes("youtube")) return "Practical YouTube tools, analytics, SEO, research and creator workflows.";
  if(t.includes("ai")) return "Practical AI resources, tools, workflows and productivity ideas.";
  if(t.includes("converter")||t.includes("generator")||t.includes("downloader")||t.includes("scanner")) return "A practical free tool and guide for everyday digital work.";
  return "Practical technology guide, resource or tool from the Laxman Nepal archive.";
}

const sections=[{tag:"NEWS",title:"Latest technology news",text:"Phones, laptops, apps, AI and technology stories worth knowing.",href:"/news/"},{tag:"REVIEWS",title:"Hands-on reviews",text:"Practical buying context, strengths, limitations and real-world use.",href:"/reviews/"},{tag:"GUIDES",title:"How-to guides",text:"Clear tutorials for apps, devices, software, AI and everyday tech.",href:"/guides/"}];
const db=[["Phones","Specs · variants · prices","/phones/"],["Laptops","Specs · configurations · prices","/laptops/"],["Compare","Side-by-side research","/compare/"],["Price history","Track changes over time","/price/"]];

export default function HomePage(){
  const posts=loadBloggerPosts();
  return <main>
<section className="container hero"><div className="hero-copy"><p className="eyebrow">TECHNOLOGY • TOOLS • AI • CREATOR INTELLIGENCE</p><h1>Technology that helps you <em>do more.</em></h1><p className="lead">A practical technology platform for news, product research, comparisons, free web tools, AI workflows and YouTube intelligence.</p><div className="actions"><a className="btn primary" href="/news/">Explore technology</a><a className="btn" href="/tools/">Open free tools</a></div></div><div className="hero-panel"><span className="panel-label">THE PLATFORM</span><div className="metric"><b>News</b><small>Useful updates, not noise</small></div><div className="metric"><b>Data</b><small>Products, specs, prices & comparisons</small></div><div className="metric"><b>Tools</b><small>Free utilities for everyday work</small></div><div className="metric"><b>AI</b><small>Practical workflows & resources</small></div></div></section>

<section className="container section"><div className="section-head"><div><p className="eyebrow">FROM THE BLOG</p><h2>Latest articles & tools.</h2><p className="section-note">{posts.length ? `${posts.length} migrated posts · automatically synced from your Blogger archive.` : "Your migrated Blogger archive will appear here automatically."}</p></div><a href="/search/">Explore archive →</a></div>
{posts.length ? <div className="post-grid">{posts.map((post,i)=>{const title=(post.title||"Untitled post").trim();const date=post.published||post.updated;const dateLabel=date?new Intl.DateTimeFormat("en",{year:"numeric",month:"short"}).format(new Date(date)):"Archive";return <a className="post-card" href={post.path} key={post.path}><div className="post-top"><span className="post-number">{String(i+1).padStart(2,"0")}</span><span className="tag">{dateLabel}</span></div><h3>{title}</h3><p>{postDescription(title)}</p><span className="read">Read article →</span></a>})}</div> : <div className="empty-card">No migrated Blogger posts were found during this build.</div>}
</section>

<section className="container section"><div className="section-head"><div><p className="eyebrow">LATEST</p><h2>Stay ahead without the clutter.</h2></div><a href="/news/">View all news →</a></div><div className="grid three">{sections.map(x=><a className="card" href={x.href} key={x.tag}><span className="tag">{x.tag}</span><h3>{x.title}</h3><p>{x.text}</p></a>)}</div></section>
<section className="database section"><div className="container"><div className="section-head"><div><p className="eyebrow">TECH DATABASE</p><h2>Research before you buy.</h2></div><a href="/products/">Open product database →</a></div><div className="grid four">{db.map(([a,b,c])=><a className="db-card" href={c} key={a}><strong>{a}</strong><span>{b}</span></a>)}</div></div></section>
<section className="container section"><div className="section-head"><div><p className="eyebrow">PRODUCT INTELLIGENCE</p><h2>More than a specification sheet.</h2></div></div><div className="grid three"><a className="card" href="/products/"><h3>Product database</h3><p>Structured brands, products, variants and specifications for fast research.</p></a><a className="card" href="/deals/"><h3>Deals & price signals</h3><p>Surface useful pricing information as the data grows.</p></a><a className="card" href="/recommend/"><h3>Recommendations</h3><p>Turn product specifications and priorities into clearer shortlists.</p></a></div></section>
<section className="tools section"><div className="container"><div className="section-head"><div><p className="eyebrow">FREE TOOLS + AI</p><h2>Useful tools, built to save time.</h2></div><a href="/tools/">Browse all tools →</a></div><div className="tool-grid">{[["01","Everyday tools","Converters, generators and practical utilities.","/tools/"],["02","AI tools","Useful AI workflows and websites.","/ai/"],["03","Creator tools","Research, SEO and YouTube utilities.","/youtube/"],["04","SEO tools","Make content easier to discover.","/seo/"]].map(x=><a href={x[3]} className="tool" key={x[0]}><span>{x[0]}</span><b>{x[1]}</b><small>{x[2]}</small></a>)}</div></div></section>
<section className="container section"><div className="youtube-box"><div><p className="eyebrow">YOUTUBE INTELLIGENCE</p><h2>Understand channels, videos and trends.</h2><p>Track channels, competitors, viral videos, topics and performance snapshots in one workspace.</p></div><a className="btn primary" href="/youtube/">Open YouTube intelligence</a></div></section>
<section className="container section final"><div className="cta"><div><p className="eyebrow">BUILT FOR PRACTICAL USE</p><h2>Less searching. More doing.</h2></div><a className="btn primary" href="/tools/">Start with the tools →</a></div></section>
</main>}