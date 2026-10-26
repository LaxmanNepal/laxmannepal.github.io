import type { Metadata } from "next";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import NewsDesk from "@/components/news-desk";

export const metadata: Metadata = {
  title: "Latest News — Nepal, World, Technology & Trending",
  description: "Browse automatically updated news from Nepal and around the world, including technology, business, politics, science, sports, entertainment and trending topics from the last seven days.",
  alternates: { canonical: "/news/" },
  openGraph: {
    title: "Latest News — Nepal, World, Technology & Trending",
    description: "A searchable digital news desk with headlines from the last seven days.",
    url: "https://laxmannepal.com.np/news/",
    type: "website",
  },
};

type Feed = { generated_at?: string; story_count?: number; stories?: Array<Record<string, unknown>> };

export default function Page() {
  let initialStories: Feed["stories"] = [];
  let initialGeneratedAt = "";
  try {
    const feed = JSON.parse(readFileSync(join(process.cwd(), "../news/news-feed.json"), "utf8")) as Feed;
    initialStories = (feed.stories || []).slice(0, 60);
    initialGeneratedAt = feed.generated_at || "";
  } catch {
    // Keep the page buildable if a first-time feed has not been generated yet.
  }
  return <NewsDesk initialStories={initialStories} initialGeneratedAt={initialGeneratedAt} />;
}
