import type { Metadata } from "next";
import { ArchiveCards, sectionPosts } from "@/lib/section-content";
export const metadata: Metadata={title:"Latest technology news",description:"Automatically populated from the latest technology articles in the archive."};
export default function Page(){
 const posts=sectionPosts("news",30);
 return <main className="container page"><p className="eyebrow">NEWS</p><h1>Latest technology news</h1><p className="muted">Automatically populated from the latest technology articles in the archive.</p><div className="section-head" style={{marginTop:38}}><div><h2>Latest from the archive</h2><p className="section-note">{posts.length} articles available</p></div></div><ArchiveCards posts={posts} tag="NEWS"/></main>;
}
