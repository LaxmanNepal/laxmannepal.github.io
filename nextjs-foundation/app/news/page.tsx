import { ArchiveCards, sectionPosts } from "@/lib/section-content";
export default function Page(){
 const posts=sectionPosts(["news","technology","launch","update","ai","phone","laptop"],30);
 return <main className="container page"><p className="eyebrow">NEWS</p><h1>Latest technology news</h1><p className="muted">Phone launches, Nepal gadget prices, AI tools, software, apps and technology updates.</p><div className="section-head" style={{marginTop:38}}><div><h2>Latest from the archive</h2><p className="section-note">{posts.length} articles available</p></div></div><ArchiveCards posts={posts} tag="NEWS"/></main>
}