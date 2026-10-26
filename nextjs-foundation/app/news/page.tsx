import type { Metadata } from "next";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import NewsDesk from "@/components/news-desk";

export const metadata: Metadata = {
  title: "नेपाली समाचार — नेपाल, विश्व, प्रविधि र ताजा खबर",
  description: "नेपालका पछिल्ला सात दिनका नेपाली भाषाका समाचार। राजनीति, अर्थतन्त्र, प्रविधि, विज्ञान, खेलकुद, मनोरञ्जन, स्वास्थ्य र शिक्षाका ताजा खबर; विश्व समाचारका लागि छुट्टै फिल्टर।",
  alternates: { canonical: "/news/" },
  openGraph: {
    title: "नेपाली समाचार — नेपाल, विश्व, प्रविधि र ताजा खबर",
    description: "नेपालका नेपाली भाषाका ताजा समाचार र विश्वका समाचार एउटै ठाउँमा।",
    url: "https://laxmannepal.com.np/news/",
    type: "website",
  },
};

type FeedStory = { id?: string; title: string; url: string; published_at: string; source?: string; category?: string; description?: string; image?: string };
type Feed = { generated_at?: string; story_count?: number; stories?: FeedStory[] };

export default function Page() {
  let initialStories: Feed["stories"] = [];
  let initialGeneratedAt = "";
  try {
    const feed = JSON.parse(readFileSync(join(process.cwd(), "../news/news-feed.json"), "utf8")) as Feed;
    initialStories = (feed.stories || []).filter(story => story.region === "Nepal" && story.language === "ne").slice(0, 60);
    initialGeneratedAt = feed.generated_at || "";
  } catch {
    // Keep the page buildable if a first-time feed has not been generated yet.
  }
  return <NewsDesk initialStories={initialStories} initialGeneratedAt={initialGeneratedAt} />;
}
