import type { Metadata } from "next";
import { getAllContent, getContentByType, type Locale } from "@/lib/content";
import type { ContentType } from "@/lib/content-model";

const labels: Record<Locale, Record<string,string>> = {
  en:{blog:"Blog",news:"News",guide:"Guides",review:"Reviews",tool:"Tools",ai:"AI",youtube:"YouTube"},
  ne:{blog:"ब्लग",news:"समाचार",guide:"गाइड",review:"रिभ्यु",tool:"टुल्स",ai:"एआई",youtube:"युट्युब"},
  hi:{blog:"ब्लॉग",news:"समाचार",guide:"गाइड",review:"रिव्यू",tool:"टूल्स",ai:"एआई",youtube:"यूट्यूब"},
};

const routes: Array<{slug:string;type:ContentType}> = [
  {slug:"blog",type:"blog"},{slug:"news",type:"news"},{slug:"guides",type:"guide"},
  {slug:"reviews",type:"review"},{slug:"tools",type:"tool"},{slug:"ai",type:"ai"},{slug:"youtube",type:"youtube"},
];

function description(title:string) {
  const t=title.toLowerCase();
  if(t.includes("youtube")) return "YouTube, creator and channel intelligence.";
  if(t.includes("ai")) return "Practical AI tools, workflows and resources.";
  if(/converter|generator|downloader|scanner|calculator/.test(t)) return "Useful tools and practical how-to resources.";
  return "Practical technology content from Laxman Nepal.";
}

function Card({item,locale}:{item:ReturnType<typeof getAllContent>[number];locale:Locale}) {
  return <a className="card" href={locale==="en"?item.path:`/${locale}${item.path}`}>
    <span className="tag">{item.type.toUpperCase()}</span><h3>{item.title}</h3>
    <p>{description(item.title)}</p><small>{item.published ? new Intl.DateTimeFormat("en",{year:"numeric",month:"short",day:"numeric"}).format(new Date(item.published)) : "Published"}</small>
  </a>;
}

export function generateStaticParams() {
  return routes.flatMap(route=>["en","ne","hi"].map(locale=>({locale,slug:route.slug})));
}

export const dynamicParams=false;

export async function generateMetadata({params}:{params:Promise<{locale:string;slug:string}>}):Promise<Metadata>{
  const {locale,slug}=await params;
  const loc=(locale==="ne"||locale==="hi"?locale:"en") as Locale;
  const route=routes.find(r=>r.slug===slug)!;
  return {title:`${labels[loc][route.type]} — Laxman Nepal`,description:`Explore ${labels[loc][route.type]} from Laxman Nepal.`};
}

export default async function CategoryPage({params}:{params:Promise<{locale:string;slug:string}>}) {
  const {locale,slug}=await params;
  const loc=(locale==="ne"||locale==="hi"?locale:"en") as Locale;
  const route=routes.find(r=>r.slug===slug)!;
  const items=getContentByType(route.type,loc);
  const all=getAllContent();
  const fallback=route.type==="blog" ? all : [];
  const visible=items.length ? items : fallback;
  return <main className="container page">
    <p className="eyebrow">{labels[loc][route.type].toUpperCase()}</p>
    <h1>{labels[loc][route.type]}</h1>
    <p className="muted">{visible.length} content items · automatically generated from the central content engine.</p>
    <section className="listing">{visible.map(item=><Card key={item.id} item={item} locale={loc}/>)}</section>
    {!visible.length && <div className="card"><h3>Coming soon</h3><p>This section is ready for native {labels[loc][route.type].toLowerCase()} content.</p></div>}
  </main>;
}
