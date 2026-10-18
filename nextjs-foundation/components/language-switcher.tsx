"use client";

import { usePathname } from "next/navigation";
import { locales, type Locale } from "@/lib/locales";

const localizedPrefixes = ["/en", "/ne", "/hi"];

function switchPath(locale: Locale) {
  // Only the localized home pages are guaranteed to exist; do not create broken translated deep links.
  return locale === "en" ? "/en/" : `/${locale}/`;
}

export default function LanguageSwitcher() {
  const pathname = usePathname() || "/";
  const current = localizedPrefixes.find((prefix) => pathname === prefix || pathname.startsWith(prefix + "/"))?.slice(1) as Locale | undefined;
  const active = current || "en";

  return <details className="language-switcher">
    <summary aria-label="Choose language">🌐 {active.toUpperCase()}</summary>
    <div className="language-menu">
      {Object.entries(locales).map(([code, locale]) => (
        <a href={switchPath(code as Locale)} key={code} aria-current={code === active ? "page" : undefined}>
          <strong>{locale.nativeLabel}</strong><small>{locale.label}</small>
        </a>
      ))}
    </div>
  </details>;
}
