import type { MetadataRoute } from "next";

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  return [{ url: "https://laxmannepal.com.np", changeFrequency: "daily", priority: 1 }];
}
