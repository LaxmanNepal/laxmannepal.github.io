import type { Locale } from "./content";

export type ContentType = "blog" | "news" | "guide" | "review" | "tool" | "ai" | "youtube";
export type ContentSection = "news"|"phones"|"laptops"|"mobile-prices"|"reviews"|"guides"|"products"|"compare"|"ai"|"youtube"|"tools"|"general";
export type ContentItem = { id:string; type:ContentType; section?:ContentSection; sections?:ContentSection[]; locale:Locale; title:string; description?:string; path:string; published?:string; updated?:string; source:"blogger"|"github"; tags?:string[]; translatedFrom?:string };
export const contentTypes:ContentType[]=["blog","news","guide","review","tool","ai","youtube"];
export const contentSections:ContentSection[]=["news","phones","laptops","mobile-prices","reviews","guides","products","compare","ai","youtube","tools","general"];
export function isSupportedLocale(value:string):value is Locale{return value==="en"||value==="ne"||value==="hi";}
export function createBloggerContent(item:{title?:string;published?:string;updated?:string;path:string}):ContentItem{return {id:item.path,type:"blog",section:"general",sections:["general"],locale:"en",title:(item.title||"Untitled post").trim(),path:item.path,published:item.published,updated:item.updated,source:"blogger"};}
