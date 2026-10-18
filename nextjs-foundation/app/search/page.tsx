import { Suspense } from "react";
import { loadBloggerPosts } from "@/lib/content";
import SearchClient from "./search-client";

export default function Page() {
  return (
    <Suspense fallback={<main className="container page"><h1>Search</h1><p className="muted">Loading search…</p></main>}>
      <SearchClient posts={loadBloggerPosts()} />
    </Suspense>
  );
}
