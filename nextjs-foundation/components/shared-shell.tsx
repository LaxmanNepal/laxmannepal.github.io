'use client';
import { useState } from "react";
import { usePathname } from "next/navigation";

const nav = [
  ["Home", "/"], ["Tools", "/tools/"], ["AI Tools", "/ai-tools/"],
  ["Blog", "/blog/"], ["YouTube", "/youtube-tools/"],
];
const explore = [["News & Updates", "/news/"], ["Guides", "/guides/"], ["Mobile", "/mobile/"], ["Apps", "/apps/"], ["Contact", "/contact/"]];
const mobile = [["🏠 Home", "/"], ["🧰 Tools", "/tools/"], ["✨ AI Tools", "/ai-tools/"], ["📝 Blog", "/blog/"], ["📦 Apps", "/apps/"], ["▶ YouTube", "/youtube-tools/"], ["📖 Guides", "/guides/"], ["📰 News", "/news/"], ["About", "/about/"]];

export default function SharedShell({ children }: { children: React.ReactNode }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const pathname = usePathname();
  return <>
    <header className="shared-header" data-shared-shell="header">
      <a className="shared-brand" href="/" aria-label="Laxman Nepal home"><span className="shared-logo">LN</span><span><strong>Laxman Nepal</strong><small>Tools · AI · Blog · YouTube</small></span></a>
      <nav className="shared-desktop-nav" aria-label="Main menu">
        {nav.map(([label, href]) => <a key={href} href={href} aria-current={pathname === href || (href !== "/" && pathname.startsWith(href)) ? "page" : undefined}>{label}</a>)}
        <details className="nav-dropdown"><summary>Explore</summary><div className="nav-dropdown-menu">{explore.map(([label, href]) => <a key={href} href={href}>{label}</a>)}</div></details>
      </nav>
      <div className="shared-actions">
        <form className="shared-search-box" action="/search/" method="get"><span aria-hidden="true">⌕</span><input name="q" type="search" autoComplete="off" aria-label="Search Laxman Nepal" placeholder="Search tools & guides…" /></form>
        <button className="shared-menu-btn" type="button" onClick={() => setMenuOpen(v => !v)} aria-label={menuOpen ? "Close menu" : "Open menu"} aria-expanded={menuOpen}>☰</button>
      </div>
    </header>
    {menuOpen && <><div className="shared-menu-backdrop" style={{display:"block"}} onClick={() => setMenuOpen(false)} aria-hidden="true" /><nav className="shared-mobile-menu open" aria-label="Mobile menu"><div className="shared-mobile-head"><strong>Laxman Nepal</strong><button type="button" onClick={() => setMenuOpen(false)} aria-label="Close menu">×</button></div>{mobile.map(([label, href]) => <a key={href} href={href}>{label}</a>)}</nav></>}
    {children}
    <footer className="shared-footer" data-shared-shell="footer">
      <div className="shared-footer-grid">
        <div><div className="shared-footer-brand"><span className="shared-logo">LN</span><strong>Laxman Nepal</strong></div><p>Practical tools, AI resources, tutorials and useful digital guides built by Laxman Nepal.</p></div>
        <div><strong>Tools</strong><a href="/tools/">All Tools</a><a href="/ai-tools/">AI Tools</a><a href="/apps/">Apps</a><a href="/youtube-tools/">YouTube Tools</a><a href="/search/">Search</a></div>
        <div><strong>Content</strong><a href="/blog/">Blog</a><a href="/news/">News</a><a href="/guides/">Guides</a><a href="/about/">About</a></div>
        <div><strong>Connect</strong><a href="https://www.youtube.com/@laxmannepalofficial">YouTube</a><a href="https://www.instagram.com/laxmannepalsir/">Instagram</a><a href="https://github.com/LaxmanNepal">GitHub</a><a href="/contact/">Contact</a></div>
      </div>
      <div className="shared-footer-bottom"><span>© {new Date().getFullYear()} Laxman Nepal · All rights reserved</span><span>Built for usefulness.</span></div>
    </footer>
  </>;
}
