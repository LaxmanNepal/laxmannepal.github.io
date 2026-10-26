import type { Metadata } from "next";
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

export default function Page() {
  return <NewsDesk />;
}
