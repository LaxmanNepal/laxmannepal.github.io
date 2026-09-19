import type { Metadata } from "next";
import "./globals.css";
import { locales } from "@/lib/content";

export const metadata: Metadata = {
  metadataBase: new URL("https://laxmannepal.com.np"),
  title: { default: "Laxman Nepal — Technology, Tools & AI", template: "%s | Laxman Nepal" },
  description: "Practical technology news, reviews, guides, product research, free tools, AI resources and YouTube intelligence.",
  openGraph: { title: "Laxman Nepal — Technology, Tools & AI", description: "Technology, product research, free tools, AI and creator intelligence.", url: "https://laxmannepal.com.np", siteName: "Laxman Nepal", type: "website" },
};

const nav = [["News","/news/"],["Reviews","/reviews/"],["Guides","/guides/"],["Products","/products/"],["Compare","/compare/"],["Tools","/tools/"],["YouTube","/youtube/"]];

function LanguageSwitcher() {
  return <details className="language-switcher">
    <summary aria-label="Choose language">🌐 EN</summary>
    <div className="language-menu">
      {Object.entries(locales).map(([code, locale]) => <a href={locale.href} key={code}><strong>{locale.nativeLabel}</strong><small>{locale.label}</small></a>)}
    </div>
  </details>;
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>
    <header className="site-header"><div className="container nav">
      <a className="brand" href="/">LAXMAN<span>NEPAL</span></a>
      <nav aria-label="Primary">{nav.map(([label,href])=><a key={href} href={href}>{label}</a>)}</nav>
      <div className="nav-actions"><a className="search-pill" href="/search/">⌕ <span>Search</span></a><LanguageSwitcher /></div>
    </div></header>
    {children}
    <footer><div className="container footer-grid">
      <div><a className="brand" href="/">LAXMAN<span>NEPAL</span></a><p>Technology · Tools · AI · Creator Intelligence</p></div>
      <div><strong>Explore</strong><a href="/news/">News</a><a href="/reviews/">Reviews</a><a href="/guides/">Guides</a><a href="/products/">Products</a></div>
      <div><strong>Tools</strong><a href="/tools/">Free Tools</a><a href="/ai/">AI</a><a href="/youtube/">YouTube</a><a href="/apps/">Apps</a></div>
      <div><strong>Language</strong><a href="/en/">English</a><a href="/ne/">नेपाली</a><a href="/hi/">हिन्दी</a></div>
    </div><div className="container footer-bottom">© {new Date().getFullYear()} Laxman Nepal · Built for usefulness.</div></footer>
  </body></html>;
}