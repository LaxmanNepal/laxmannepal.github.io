import { loadBloggerPosts } from "@/lib/content";
import SearchClient from "./search-client";

export default function Page() {
  return <SearchClient posts={loadBloggerPosts()} />;
}
