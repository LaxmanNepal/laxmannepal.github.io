import type { Metadata } from "next";
import { ArchiveCards, sectionPosts } from "@/lib/section-content";
export const metadata: Metadata={title:"Phones",description:"Phone guides, comparisons and smartphone resources from the archive."};
export default function Page(){
 const posts=sectionPosts("phones",30);
 return <main className="container page"><p className="eyebrow">PHONES</p><h1>Phones</h1><p className="muted">Phone guides, comparisons and smartphone resources from the archive.</p><div className="section-head" style={{marginTop:38}}><div><h2>Latest from the archive</h2><p className="section-note">{posts.length} articles available</p></div></div><ArchiveCards posts={posts} tag="PHONES"/></main>;
}
