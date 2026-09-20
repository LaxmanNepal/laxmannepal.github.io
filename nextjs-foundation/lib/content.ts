import fs from "node:fs";
import path from "node:path";
import type { ContentItem, ContentSection, ContentType } from "./content-model";

export type Locale = "en" | "ne" | "hi";
export type BloggerPost = { title?: string; published?: string; updated?: string; path: string; original_url?: string; type?: ContentType; tags?: string[] };

export const locales: Record<Locale, {label:string; nativeLabel:string; href:string}> = {
  en:{label:"English",nativeLabel:"English",href:"/en/"},
  ne:{label:"Nepali",nativeLabel:"नेपाली",href:"/ne/"},
  hi:{label:"Hindi",nativeLabel:"हिन्दी",href:"/hi/"},
};
export const defaultLocale: Locale = "en";

function manifestPath() { return path.join(process.cwd(),"..",".blogger-migration.json"); }

export function loadBloggerPosts(): BloggerPost[] {
  try {
    const manifest=JSON.parse(fs.readFileSync(manifestPath(),"utf8"));
    return Array.isArray(manifest.posts) ? manifest.posts.filter((p:BloggerPost)=>p?.path).sort(
      (a:BloggerPost,b:BloggerPost)=>new Date(b.published||b.updated||0).getTime()-new Date(a.published||a.updated||0).getTime()
    ) : [];
  } catch { return []; }
}

const SECTION_RULES:Array<{section:ContentSection;terms:string[]}>= [
{section:"mobile-prices",terms:["mobile price","phone price","smartphone price","price in nepal","cost in nepal","price list","mrp"]},
{section:"compare",terms:["compare","comparison"," vs "," versus ","difference between"]},
{section:"phones",terms:["phone","mobile","iphone","xiaomi","redmi","samsung","galaxy","pixel","oneplus","oppo","vivo","realme","nothing phone"]},
{section:"laptops",terms:["laptop","notebook","macbook","dell"," hp ","lenovo","asus","acer","msi","chromebook","computer"]},
{section:"ai",terms:["artificial intelligence"," ai ","chatgpt","gemini","claude","copilot","midjourney","openai","deepseek","ai tool"]},
{section:"youtube",terms:["youtube","youtuber","creator","channel","subscriber","thumbnail","youtube seo"]},
{section:"tools",terms:["online tool","converter","generator","calculator","download tool","utility"]},
{section:"reviews",terms:["review","hands-on","unboxing","tested","experience with"]},
{section:"guides",terms:["how to","tutorial","guide","install","setup","fix ","download","step by step","tips"]},
{section:"news",terms:["news","technology update","launch","announced","announcement","latest","report","release"]},
{section:"products",terms:["product","specification","specs","gadget","device","buying"]}
];
const norm=(v:string)=>v.toLowerCase().replace(/[–—]/g,"-").replace(/\\s+/g," ").trim();
export function classifyPost(post:BloggerPost):ContentSection[]{
 const text=[norm(post.title||""),...(post.tags||[]).map(norm),norm(post.path)].join(" ");
 const found:ContentSection[]=[];
 if(post.type==="news")found.push("news"); if(post.type==="guide")found.push("guides"); if(post.type==="review")found.push("reviews"); if(post.type==="ai")found.push("ai"); if(post.type==="youtube")found.push("youtube"); if(post.type==="tool")found.push("tools");
 for(const rule of SECTION_RULES) if(rule.terms.some(t=>text.includes(norm(t)))) found.push(rule.section);
 return [...new Set(found)].length?[...new Set(found)]:["general"];
}

export function getAllContent(): ContentItem[] {
  return loadBloggerPosts().map(post=>{const sections=classifyPost(post);return {id:post.path,type:(post.type||"blog") as ContentType,section:sections[0],sections,locale:"en" as Locale,title:(post.title||"Untitled post").trim(),path:post.path,published:post.published,updated:post.updated,source:"blogger" as const,tags:post.tags||["blog","technology"],translatedFrom:undefined};});
}

export function getContentByType(type: ContentType, locale: Locale = defaultLocale) {
  return getAllContent().filter(item=>item.type===type && item.locale===locale);
}

export function getContentBySection(section:ContentSection,limit=24,locale:Locale=defaultLocale){return getAllContent().filter(item=>item.locale===locale&&(item.sections||[item.section||"general"]).includes(section)).sort((a,b)=>new Date(b.published||b.updated||0).getTime()-new Date(a.published||a.updated||0).getTime()).slice(0,limit);}
export function getLatestBySections(sections:ContentSection[],limit=12,locale:Locale=defaultLocale){const wanted=new Set(sections);return getAllContent().filter(item=>item.locale===locale&&(item.sections||[item.section||"general"]).some(s=>wanted.has(s))).sort((a,b)=>new Date(b.published||b.updated||0).getTime()-new Date(a.published||a.updated||0).getTime()).slice(0,limit);}
export function getLatestContent(limit=12, locale: Locale = defaultLocale) {
  return getAllContent().filter(item=>item.locale===locale)
    .sort((a,b)=>new Date(b.published||b.updated||0).getTime()-new Date(a.published||a.updated||0).getTime())
    .slice(0,limit);
}

export function getContentByPath(contentPath:string) {
  return getAllContent().find(item=>item.path===contentPath);
}

export function getRelatedContent(currentPath: string, limit = 4) {
  const current = getContentByPath(currentPath);
  return getAllContent()
    .filter(item => item.path !== currentPath && (!current || item.type === current.type))
    .slice(0, limit);
}

export function localePath(locale: Locale, pathname="/") {
  const clean=pathname.startsWith("/")?pathname:`/${pathname}`;
  return locale===defaultLocale?clean:`/${locale}${clean==="/"?"":clean}`;
}
