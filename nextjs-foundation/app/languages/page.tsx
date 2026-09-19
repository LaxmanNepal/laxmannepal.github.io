import { locales } from "@/lib/content";
import { siteConfig } from "@/lib/site-config";

export default function LanguagesPage() {
  return <main className="container page">
    <p className="eyebrow">LANGUAGES</p><h1>Choose your language.</h1>
    <p className="muted">Publish technology, tools and AI content in multiple languages while keeping existing article URLs stable.</p>
    <div className="listing">{Object.entries(locales).map(([code, locale]) => <a className="card" href={locale.href} key={code}><span className="tag">{code.toUpperCase()}</span><h3>{locale.nativeLabel}</h3><p>{locale.label}</p></a>)}</div>
    <div className="card" style={{marginTop:"24px"}}><span className="tag">CONTENT SYSTEM</span><h3>One platform, multiple languages.</h3><p>Current foundation: {siteConfig.locales.length} locales, shared navigation and a reusable content model.</p></div>
  </main>;
}