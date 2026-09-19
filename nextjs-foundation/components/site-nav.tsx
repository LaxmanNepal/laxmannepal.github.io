"use client";

import { useState } from "react";
import LanguageSwitcher from "@/components/language-switcher";

const links = [
  ["News","/news/"],["Phones","/phones/"],["Mobile Prices","/mobile-prices-in-nepal/"],
  ["Reviews","/reviews/"],["Guides","/guides/"],["Products","/products/"],["Compare","/compare/"],
  ["Tools","/tools/"],["AI","/ai/"],["YouTube","/youtube/"]
];

export default function SiteNav() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const q = query.trim();
    window.location.href = q ? "/search/?q=" + encodeURIComponent(q) : "/search/";
    setOpen(false);
  }

  return <header className="site-header">
    <div className="container nav">
      <a className="brand" href="/" onClick={() => setOpen(false)}>LAXMAN<span>NEPAL</span></a>
      <nav className="desktop-nav" aria-label="Primary">{links.map(([label,href])=><a key={href} href={href}>{label}</a>)}</nav>
      <div className="nav-actions">
        <form className="search-pill" onSubmit={submit} role="search">
          <span aria-hidden="true">⌕</span><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search" aria-label="Search articles"/>
        </form>
        <LanguageSwitcher />
        <button className="menu-toggle" type="button" aria-expanded={open} aria-controls="mobile-menu" onClick={()=>setOpen(v=>!v)}>{open ? "×" : "☰"}<span>{open ? "Close" : "Menu"}</span></button>
      </div>
    </div>
    <div id="mobile-menu" className={open ? "mobile-menu open" : "mobile-menu"} aria-hidden={!open}>
      <div className="container mobile-menu-inner">
        <form className="mobile-search" onSubmit={submit} role="search"><span>⌕</span><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search Laxman Nepal…" aria-label="Search Laxman Nepal"/><button type="submit">Search</button></form>
        <nav aria-label="Mobile primary">{links.map(([label,href])=><a key={href} href={href} onClick={()=>setOpen(false)}>{label}<span>→</span></a>)}</nav>
        <div className="mobile-language"><span>Language</span><LanguageSwitcher /></div>
      </div>
    </div>
  </header>;
}
