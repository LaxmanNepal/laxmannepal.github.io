import fs from "node:fs";
import path from "node:path";
import type { ContentItem, ContentType } from "./content-model";

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

export function getAllContent(): ContentItem[] {
  return loadBloggerPosts().map(post=>({
    id:post.path,type:((post as BloggerPost & {type?:ContentType}).type || "blog") as ContentType,locale:"en" as Locale,
    title:(post.title||"Untitled post").trim(),path:post.path,
    published:post.published,updated:post.updated,source:"blogger" as const,
    tags:(post as BloggerPost & {tags?:string[]}).tags || ["blog","technology"],
    translatedFrom:undefined
  }));
}

export function getContentByType(type: ContentType, locale: Locale = defaultLocale) {
  return getAllContent().filter(item=>item.type===type && item.locale===locale);
}

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
