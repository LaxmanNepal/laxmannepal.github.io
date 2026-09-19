import fs from "node:fs";
import path from "node:path";

export type Locale = "en" | "ne" | "hi";
export type BloggerPost = { title?: string; published?: string; updated?: string; path: string; original_url?: string };

export const locales: Record<Locale, {label:string; nativeLabel:string; href:string}> = {
  en: { label: "English", nativeLabel: "English", href: "/en/" },
  ne: { label: "Nepali", nativeLabel: "नेपाली", href: "/ne/" },
  hi: { label: "Hindi", nativeLabel: "हिन्दी", href: "/hi/" },
};
export const defaultLocale: Locale = "en";

export function loadBloggerPosts(): BloggerPost[] {
  const manifestPath = path.join(process.cwd(), "..", ".blogger-migration.json");
  try {
    const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
    return Array.isArray(manifest.posts) ? manifest.posts.filter((post: BloggerPost) => post?.path).sort(
      (a: BloggerPost, b: BloggerPost) =>
        new Date(b.published || b.updated || 0).getTime() - new Date(a.published || a.updated || 0).getTime()
    ) : [];
  } catch { return []; }
}
export function localePath(locale: Locale, pathname = "/") {
  const clean = pathname.startsWith("/") ? pathname : `/${pathname}`;
  return locale === defaultLocale ? clean : `/${locale}${clean === "/" ? "/" : clean}`;
}
