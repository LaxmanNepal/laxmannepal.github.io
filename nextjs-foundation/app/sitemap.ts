import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  return [{ url: "https://laxmannepal.com.np", changeFrequency: "daily", priority: 1 }];
}
