import type { Metadata } from "next";
import { ArchiveCards, sectionPosts } from "@/lib/section-content";
export const metadata: Metadata={title:"Mobile Prices in Nepal",description:"Phone-price and buying content from the Laxman Nepal archive."};
export default function Page(){
 const posts=sectionPosts("mobile-prices",30);
 return <main className="container page"><p className="eyebrow">NEPAL MARKET</p><h1>Mobile Prices in Nepal</h1><p className="muted">Phone-price and buying content from the Laxman Nepal archive.</p><div className="section-head" style={{marginTop:38}}><div><h2>Latest from the archive</h2><p className="section-note">{posts.length} articles available</p></div></div><ArchiveCards posts={posts} tag="PRICES"/></main>;
}
