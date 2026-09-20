import type { Metadata } from "next";
import { ArchiveCards, sectionPosts } from "@/lib/section-content";
export const metadata: Metadata={title:"Practical technology guides",description:"Automatically surfaced how-to, tutorial and technology help articles."};
export default function Page(){
 const posts=sectionPosts("guides",30);
 return <main className="container page"><p className="eyebrow">GUIDES</p><h1>Practical technology guides</h1><p className="muted">Automatically surfaced how-to, tutorial and technology help articles.</p><div className="section-head" style={{marginTop:38}}><div><h2>Latest from the archive</h2><p className="section-note">{posts.length} articles available</p></div></div><ArchiveCards posts={posts} tag="GUIDES"/></main>;
}
