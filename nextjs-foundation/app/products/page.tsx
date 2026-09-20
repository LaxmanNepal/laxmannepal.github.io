import type { Metadata } from "next";
import { ArchiveCards, sectionPosts } from "@/lib/section-content";
export const metadata: Metadata={title:"Product research",description:"Product content automatically collected from the archive."};
export default function Page(){
 const posts=sectionPosts("products",30);
 return <main className="container page"><p className="eyebrow">PRODUCTS</p><h1>Product research</h1><p className="muted">Product content automatically collected from the archive.</p><div className="section-head" style={{marginTop:38}}><div><h2>Latest from the archive</h2><p className="section-note">{posts.length} articles available</p></div></div><ArchiveCards posts={posts} tag="PRODUCTS"/></main>;
}
