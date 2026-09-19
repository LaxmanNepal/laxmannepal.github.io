import { notFound } from "next/navigation";
import { getAllContent, getContentByPath, getRelatedContent } from "@/lib/content";
import type { ContentItem } from "@/lib/content-model";
import type { Metadata } from "next";
import fs from "node:fs";
import path from "node:path";

function readArticle(item: ContentItem) {
  try {
    const file = path.join(process.cwd(), "..", item.path.replace(/^\//, ""));
    return fs.readFileSync(file, "utf8");
  } catch {
    return "";
  }
}

function stripDocument(html: string) {
  return html.replace(/<!doctype[^>]*>/i,"").replace(/<html[^>]*>/i,"").replace(/<\/html>/i,"").replace(/<head[\s\S]*?<\/head>/i,"").replace(/<body[^>]*>/i,"").replace(/<\/body>/i,"");
}

export async function generateStaticParams() {
  return getAllContent().map(item => ({ year: item.path.split("/")[1], month: item.path.split("/")[2], slug: item.path.split("/")[3]?.replace(/\.html$/i,"") || "" })).filter(p=>p.year&&p.month&&p.slug);
}
export const dynamicParams = false;

export async function generateMetadata({params}:{params:Promise<{year:string;month:string;slug:string}>}):Promise<Metadata>{
  const p=await params; const item=getContentByPath(`/${p.year}/${p.month}/${p.slug}.html`);
  if(!item) return {};
  return {title:item.title,description:`Read ${item.title} on Laxman Nepal.`,alternates:{canonical:item.path},openGraph:{title:item.title,description:`Read ${item.title} on Laxman Nepal.`,url:item.path}};
}

export default async function ArticlePage({params}:{params:Promise<{year:string;month:string;slug:string}>}) {
  const p=await params; const item=getContentByPath(`/${p.year}/${p.month}/${p.slug}.html`);
  if(!item) notFound();
  const html=readArticle(item); if(!html) notFound();
  const related=getRelatedContent(item.path,4);
  return <main className="container article-shell">
    <div className="article-meta"><span className="tag">{item.type.toUpperCase()}</span><span className="tag">{item.published ? new Intl.DateTimeFormat("en",{year:"numeric",month:"short",day:"numeric"}).format(new Date(item.published)) : ""}</span></div>
    <h1 className="article-title">{item.title}</h1>
    <p className="article-lead">Practical technology, tools and AI information from Laxman Nepal.</p>
    <article className="article-frame">
      <div className="article-content" dangerouslySetInnerHTML={{__html:stripDocument(html)}} />
      <p className="article-source">Original article URL preserved: {item.path}</p>
    </article>
    {related.length>0 && <section className="article-related"><h2>More from Laxman Nepal</h2><div className="related-grid">{related.map(r=><a className="card" href={r.path} key={r.id}><span className="tag">{r.type.toUpperCase()}</span><h3>{r.title}</h3><p>Read article →</p></a>)}</div></section>}
  </main>;
}