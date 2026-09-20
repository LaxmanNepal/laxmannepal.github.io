import type { Metadata } from "next";
import { ArchiveCards, sectionPosts } from "@/lib/section-content";
export const metadata: Metadata={title:"Laptops, specs & buying information",description:"Automatically surfaced laptop and PC content from the archive."};
export default function Page(){
 const posts=sectionPosts("laptops",30);
 return <main className="container page"><p className="eyebrow">LAPTOPS</p><h1>Laptops, specs & buying information</h1><p className="muted">Automatically surfaced laptop and PC content from the archive.</p><div className="section-head" style={{marginTop:38}}><div><h2>Latest from the archive</h2><p className="section-note">{posts.length} articles available</p></div></div><ArchiveCards posts={posts} tag="LAPTOPS"/></main>;
}
