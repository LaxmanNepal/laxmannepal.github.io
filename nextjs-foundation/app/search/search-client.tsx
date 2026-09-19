"use client";

import { useMemo, useState } from "react";
import type { BloggerPost } from "@/lib/content";

export default function SearchClient({ posts }: { posts: BloggerPost[] }) {
  const [query, setQuery] = useState("");
  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return posts.slice(0, 12);
    return posts.filter((post) => (post.title || "").toLowerCase().includes(q)).slice(0, 30);
  }, [posts, query]);

  return (
    <main className="container article-shell">
      <div className="article-meta"><span className="tag">SEARCH</span><span className="tag">{posts.length} POSTS</span></div>
      <h1 className="article-title">Search Laxman Nepal</h1>
      <p className="article-lead">Search the migrated Blogger archive instantly. No external API required.</p>
      <input className="search-input" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search articles…" aria-label="Search articles" />
      <section className="related-grid search-results">
        {results.map((post) => (
          <a className="card" href={post.path} key={post.path}>
            <span className="tag">{(post.type || "blog").toUpperCase()}</span>
            <h3>{post.title}</h3>
            <p>{post.published ? new Intl.DateTimeFormat("en", { year: "numeric", month: "short", day: "numeric" }).format(new Date(post.published)) : "Read article"} →</p>
          </a>
        ))}
      </section>
      {!results.length && <div className="empty-state">No matching articles found.</div>}
    </main>
  );
}
