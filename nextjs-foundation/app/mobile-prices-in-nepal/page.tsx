import type { Metadata } from "next";
import { getAllContent } from "@/lib/content";
export const metadata: Metadata={title:"Mobile Prices in Nepal",description:"Latest mobile phone price guides, Nepal market information and smartphone buying resources."};
export default function Page(){
 const posts=getAllContent().filter(p=>/price|nepal|iphone|samsung|xiaomi|redmi|phone|mobile/i.test((p.title||"")+" "+p.tags.join(" "))).slice(0,24);
 return <main className="container page"><p className="eyebrow">NEPAL MARKET</p><h1>Mobile Prices in Nepal</h1><p className="muted">Automatically collected phone-price and buying content from the Laxman Nepal archive.</p><div className="post-grid">{posts.map((p,i)=><a className="post-card" key={p.id} href={p.path}><span className="post-number">{String(i+1).padStart(2,"0")}</span><h3>{p.title}</h3><p>Explore Nepal mobile price and buying information.</p><span className="read">Read →</span></a>)}</div></main>;
}