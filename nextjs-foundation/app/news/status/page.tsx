import type { Metadata } from "next";
import Link from "next/link";
import { readFileSync } from "node:fs";
import { join } from "node:path";

export const metadata: Metadata = {
  title: "समाचार फिड स्थिति — Laxman Nepal",
  description: "स्वचालित समाचार फिडको अद्यावधिक समय, स्रोत स्थिति, समाचार संख्या र तस्बिर उपलब्धताको विवरण।",
  robots: { index: false, follow: false },
};

type FeedStatus = { name: string; status: string; stories: number; error?: string };
type Feed = { generated_at?: string; story_count?: number; feeds_checked?: number; feeds_failed?: string[]; feed_status?: FeedStatus[]; image_count?: number; stories?: unknown[] };

export default function NewsStatusPage() {
  let feed: Feed = {};
  let unavailable = false;
  try {
    feed = JSON.parse(readFileSync(join(process.cwd(), "../news/news-feed.json"), "utf8")) as Feed;
  } catch {
    unavailable = true;
  }
  const sources = feed.feed_status || [];
  const healthy = sources.filter(source => source.status === "ok").length;
  const failed = sources.filter(source => source.status !== "ok").length;
  const updated = feed.generated_at ? new Date(feed.generated_at).toLocaleString("ne-NP", { dateStyle: "medium", timeStyle: "short", timeZone: "Asia/Kathmandu" }) : "उपलब्ध छैन";

  return <main className="container" style={{ padding: "42px 0 72px", maxWidth: 1040 }}>
    <Link href="/news/" style={{ fontWeight: 800, fontSize: 13 }}>← समाचारमा फर्कनुहोस्</Link>
    <header style={{ margin: "24px 0" }}>
      <p style={{ color: "#667085", fontWeight: 800, fontSize: 11, letterSpacing: ".12em" }}>NEWS OPERATIONS</p>
      <h1 style={{ fontSize: "clamp(32px,5vw,54px)", letterSpacing: "-.05em", margin: "8px 0" }}>समाचार फिड स्थिति</h1>
      <p style={{ color: "#667085", lineHeight: 1.7 }}>यो सार्वजनिक read-only स्थिति पृष्ठ हो। यसले अन्तिम सफलतापूर्वक लेखिएको फिडको विवरण देखाउँछ; यसबाट फिड refresh वा स्रोत परिवर्तन गर्न मिल्दैन।</p>
    </header>
    {unavailable ? <section style={{ padding: 24, border: "1px solid #f0c6c6", borderRadius: 16, background: "#fff" }}>समाचार फिड फाइल उपलब्ध छैन। GitHub Actions मा feed refresh workflow जाँच गर्नुहोस्।</section> : <>
      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(160px,1fr))", gap: 12, margin: "24px 0" }}>
        {[
          ["कुल समाचार", String(feed.story_count ?? feed.stories?.length ?? 0)],
          ["सफल स्रोत", String(healthy)],
          ["असफल स्रोत", String(failed)],
          ["तस्बिर भएका समाचार", String(feed.image_count ?? "—")],
        ].map(([label, value]) => <article key={label} style={{ padding: 20, border: "1px solid #e5e7eb", borderRadius: 16, background: "#fff" }}><small style={{ color: "#667085", fontWeight: 700 }}>{label}</small><strong style={{ display: "block", fontSize: 30, marginTop: 8 }}>{value}</strong></article>)}
      </section>
      <p style={{ color: "#667085", fontSize: 13 }}>अन्तिम फिड लेखिएको समय (नेपाल): <strong style={{ color: "#101114" }}>{updated}</strong> · जाँचिएका स्रोत: {feed.feeds_checked ?? sources.length}</p>
      <section style={{ marginTop: 28 }}>
        <h2 style={{ fontSize: 22 }}>स्रोतहरूको अवस्था</h2>
        {sources.length ? <div style={{ border: "1px solid #e5e7eb", borderRadius: 16, overflow: "hidden", background: "#fff" }}>
          {sources.map((source, index) => <div key={source.name} style={{ display: "grid", gridTemplateColumns: "minmax(0,1fr) auto auto", alignItems: "center", gap: 14, padding: "13px 16px", borderBottom: index === sources.length - 1 ? 0 : "1px solid #eef0f2" }}>
            <strong style={{ fontSize: 14 }}>{source.name}</strong>
            <span style={{ color: "#667085", fontSize: 12 }}>{source.stories} समाचार</span>
            <span style={{ color: source.status === "ok" ? "#067647" : "#b42318", fontWeight: 800, fontSize: 12 }}>{source.status === "ok" ? "सफल" : "असफल"}{source.error ? ` · ${source.error}` : ""}</span>
          </div>)}
        </div> : <p style={{ color: "#667085" }}>स्रोतको विस्तृत अवस्था अर्को feed refresh पछि देखिनेछ।</p>}
      </section>
      <p style={{ marginTop: 24, color: "#667085", fontSize: 12, lineHeight: 1.7 }}>स्रोत सफल देखिनु भनेको स्रोतको RSS endpoint बाट डाटा प्राप्त भएको हो; त्यसले प्रत्येक समाचारको तथ्य स्वतन्त्र रूपमा पुष्टि भएको जनाउँदैन।</p>
    </>}
  </main>;
}
