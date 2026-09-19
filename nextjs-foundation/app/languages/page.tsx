import { locales } from "@/lib/content";

export default function LanguagesPage() {
  return <main className="container page"><p className="eyebrow">LANGUAGES</p><h1>Choose your language.</h1>
    <p className="muted">A multilingual foundation for Laxman Nepal, while existing Blogger URLs remain unchanged.</p>
    <div className="listing">{Object.entries(locales).map(([code, locale]) => <a className="card" href={locale.href} key={code}><span className="tag">{code.toUpperCase()}</span><h3>{locale.nativeLabel}</h3><p>{locale.label}</p></a>)}</div>
  </main>;
}