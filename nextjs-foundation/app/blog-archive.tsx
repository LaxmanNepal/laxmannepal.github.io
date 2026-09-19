"use client";

import { useMemo, useState } from "react";
import type { BloggerPost } from "@/lib/content";

function postDescription(title: string) {
  const t = title.toLowerCase();
  if (t.includes("youtube")) return "Creator tools, analytics, SEO, research and practical workflows.";
  if (t.includes("ai")) return "Practical AI resources, tools, workflows and productivity ideas.";
  if (t.includes("converter") || t.includes("generator") || t.includes("downloader") || t.includes("scanner")) return "A useful free tool or practical guide for everyday digital work.";
  return "A practical technology guide, resource or tool from the Laxman Nepal archive.";
}

export default function BlogArchive({ posts }: { posts: BloggerPost[] }) {
  const years = useMemo(() => {
    const set = new Set(posts.map(p => (p.published || p.updated || "").slice(0, 4)).filter(Boolean));
    return ["All", ...Array.from(set).sort((a, b) => Number(b) - Number(a))];
  }, [posts]);

  const [query, setQuery] = useState("");
  const [year, setYear] = useState("All");

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    return posts.filter(post => {
      const title = (post.title || "").trim();
      const postYear = (post.published || post.updated || "").slice(0, 4);
      return (!q || title.toLowerCase().includes(q)) && (year === "All" || postYear === year);
    });
  }, [posts, query, year]);

  return (
    <>
      <div className="archive-controls">
        <div className="archive-search-wrap">
          <span aria-hidden="true">⌕</span>
          <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search all articles…" aria-label="Search all articles" />
          {query && <button type="button" onClick={() => setQuery("")} aria-label="Clear search">×</button>}
        </div>
        <div className="archive-years" role="group" aria-label="Filter articles by year">
          {years.map(y => (
            <button key={y} type="button" className={year === y ? "active" : ""} onClick={() => setYear(y)}>
              {y}
            </button>
          ))}
        </div>
      </div>

      <div className="archive-status" aria-live="polite">
        Showing <strong>{results.length}</strong> of {posts.length} articles
        {(query || year !== "All") && <> · <button type="button" onClick={() => { setQuery(""); setYear("All"); }}>Clear filters</button></>}
      </div>

      {results.length ? (
        <div className="post-grid home-post-grid">
          {results.map((post, i) => {
            const title = (post.title || "Untitled post").trim();
            const date = post.published || post.updated;
            const dateLabel = date ? new Intl.DateTimeFormat("en", { year: "numeric", month: "short" }).format(new Date(date)) : "Archive";
            return (
              <a className="post-card" href={post.path} key={post.path}>
                <div className="post-top"><span className="post-number">{String(i + 1).padStart(2, "0")}</span><span className="tag">{dateLabel}</span></div>
                <h3>{title}</h3>
                <p>{postDescription(title)}</p>
                <span className="read">Read article →</span>
              </a>
            );
          })}
        </div>
      ) : (
        <div className="empty-card">
          <strong>No matching articles.</strong>
          <p>Try another keyword or clear the year filter.</p>
        </div>
      )}
    </>
  );
}
