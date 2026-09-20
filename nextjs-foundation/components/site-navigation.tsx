"use client";

import { useState } from "react";

const nav = [
  ["News","/news/"],["Phones","/phones/"],["Laptops","/laptops/"],["Mobile Prices","/mobile-prices-in-nepal/"],
  ["Reviews","/reviews/"],["Guides","/guides/"],["Products","/products/"],["Compare","/compare/"],["Tools","/tools/"],["AI","/ai/"],["YouTube","/youtube/"]
];

export default function SiteNavigation() {
  const [open,setOpen]=useState(false);
  const [query,setQuery]=useState("");
  const go=(e:React.FormEvent)=>{e.preventDefault();const q=query.trim();if(q) window.location.href="/search/?q="+encodeURIComponent(q);};
  return <>
    <nav className="desktop-nav" aria-label="Primary">{nav.map(([label,href])=><a key={href} href={href}>{label}</a>)}</nav>
    <div className="nav-actions">
      <form className="search-pill" onSubmit={go}><span aria-hidden="true">⌕</span><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search" aria-label="Search site"/></form>
      <LanguageSwitcherPlaceholder />
      <button className="menu-toggle" type="button" aria-expanded={open} aria-controls="mobile-navigation" onClick={()=>setOpen(!open)}>{open?"×":"☰"}<span>Menu</span></button>
    </div>
    <div id="mobile-navigation" className={"mobile-menu"+(open?" open":"")}>
      <div className="mobile-menu-inner">
        <form className="mobile-search" onSubmit={go}><span aria-hidden="true">⌕</span><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search phones, news, guides…" aria-label="Search articles and products"/><button type="submit">Search</button></form>
        <nav aria-label="Mobile navigation">{nav.map(([label,href])=><a key={href} href={href} onClick={()=>setOpen(false)}>{label}<span>→</span></a>)}</nav>
      </div>
    </div>
  </>;
}
function LanguageSwitcherPlaceholder(){return <LanguageSwitcher />}
