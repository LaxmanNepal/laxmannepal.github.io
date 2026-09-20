import type { Metadata } from "next";
import "./globals.css";
import LanguageSwitcher from "@/components/language-switcher";

export const metadata: Metadata = {
  metadataBase: new URL("https://laxmannepal.com.np"),
  title: { default: "Laxman Nepal — Technology, Tools & AI", template: "%s | Laxman Nepal" },
  description: "Practical technology news, reviews, guides, product research, free tools, AI resources and YouTube intelligence.",
  openGraph: { title: "Laxman Nepal — Technology, Tools & AI", description: "Technology, product research, free tools, AI and creator intelligence.", url: "https://laxmannepal.com.np", siteName: "Laxman Nepal", type: "website" },
};

const nav = [
  ["News","/news/"],["Phones","/phones/"],["Laptops","/laptops/"],
  ["Mobile Prices","/mobile-prices-in-nepal/"],["Reviews","/reviews/"],["Guides","/guides/"],
  ["Products","/products/"],["Compare","/compare/"],["Tools","/tools/"],["YouTube","/youtube/"]
];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>
    <header className="site-header">
      <div className="container nav">
        <a className="brand" href="/">LAXMAN<span>NEPAL</span></a>
        <nav className="desktop-nav" aria-label="Primary">{nav.map(([label,href])=><a key={href} href={href}>{label}</a>)}</nav>
        <div className="nav-actions">
          <form className="search-pill" action="/search/" method="get"><span aria-hidden="true">⌕</span><input name="q" aria-label="Search" placeholder="Search" /></form>
          <LanguageSwitcher />
          <details className="mobile-nav-details">
            <summary className="menu-toggle" aria-label="Open navigation">☰ <span>Menu</span></summary>
            <div className="mobile-menu">
              <div className="mobile-menu-inner">
                <form className="mobile-search" action="/search/" method="get">
                  <span aria-hidden="true">⌕</span><input name="q" placeholder="Search articles, phones, guides…" aria-label="Search articles, phones, guides" />
                  <button type="submit">Search</button>
                </form>
                <nav aria-label="Mobile navigation">{nav.map(([label,href])=><a key={href} href={href}>{label}<span>→</span></a>)}</nav>
                <div className="mobile-language"><span>Language</span><LanguageSwitcher /></div>
              </div>
            </div>
          </details>
        </div>
      </div>
    </header>
    {children}
    <footer><div className="container footer-grid">
      <div><a className="brand" href="/">LAXMAN<span>NEPAL</span></a><p>Technology · Tools · AI · Creator Intelligence</p></div>
      <div><strong>Explore</strong><a href="/news/">News</a><a href="/phones/">Phones</a><a href="/laptops/">Laptops</a><a href="/mobile-prices-in-nepal/">Mobile Prices</a></div>
      <div><strong>Content</strong><a href="/reviews/">Reviews</a><a href="/guides/">Guides</a><a href="/products/">Products</a><a href="/compare/">Compare</a></div>
      <div><strong>Tools</strong><a href="/tools/">Free Tools</a><a href="/ai/">AI</a><a href="/youtube/">YouTube</a></div>
    </div><div className="container footer-bottom">© {new Date().getFullYear()} Laxman Nepal · Built for usefulness.</div></footer>
  </body></html>;
}
