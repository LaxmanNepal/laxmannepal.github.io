"use client";

import { usePathname } from "next/navigation";
import { locales, type Locale } from "@/lib/content";

const localizedPrefixes = ["/en", "/ne", "/hi"];

function switchPath(pathname: string, locale: Locale) {
  const normalized = pathname || "/";
  const source = localizedPrefixes.find((prefix) => normalized === prefix || normalized.startsWith(prefix + "/"));
  const basePath = source ? normalized.slice(source.length) || "/" : normalized;
  return locale === "en" ? basePath : `/${locale}${basePath === "/" ? "/" : basePath}`;
}

export default function LanguageSwitcher() {
  const pathname = usePathname() || "/";
  const current = localizedPrefixes.find((prefix) => pathname === prefix || pathname.startsWith(prefix + "/"))?.slice(1) as Locale | undefined;
  const active = current || "en";

  return <details className="language-switcher">
    <summary aria-label="Choose language">🌐 {active.toUpperCase()}</summary>
    <div className="language-menu">
      {Object.entries(locales).map(([code, locale]) => (
        <a href={switchPath(pathname, code as Locale)} key={code} aria-current={code === active ? "page" : undefined}>
          <strong>{locale.nativeLabel}</strong><small>{locale.label}</small>
        </a>
      ))}
    </div>
  </details>;
}
