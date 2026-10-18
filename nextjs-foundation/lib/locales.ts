export type Locale = "en" | "ne" | "hi";

export const locales: Record<Locale, { label: string; nativeLabel: string; href: string }> = {
  en: { label: "English", nativeLabel: "English", href: "/en/" },
  ne: { label: "Nepali", nativeLabel: "नेपाली", href: "/ne/" },
  hi: { label: "Hindi", nativeLabel: "हिन्दी", href: "/hi/" },
};

export const defaultLocale: Locale = "en";
