import type { Metadata } from "next";
import { ArchiveCards, sectionPosts } from "@/lib/section-content";

export const metadata: Metadata={
 title:"Compare Phones, Laptops & Gadgets",
 description:"Compare technology products using Laxman Nepal's growing archive of phone, laptop and gadget research."
};

export default function Page(){
 const posts=sectionPosts(["compare","vs","versus","difference","best","phone","laptop","xiaomi","iphone","samsung","redmi"],30);
 return <main className="container page">
  <p className="eyebrow">COMPARE</p>
  <h1>Compare technology products</h1>
  <p className="muted">Comparison and buying-research articles are automatically collected from the archive.</p>
  <div className="section-head" style={{marginTop:38}}><div><h2>Comparison & buying research</h2><p className="section-note">{posts.length} articles available</p></div></div>
  <ArchiveCards posts={posts} tag="COMPARE"/>
 </main>;
}