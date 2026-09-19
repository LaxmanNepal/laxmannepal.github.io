import { loadBloggerPosts } from "@/lib/content";

function postDescription(title: string) {
  const t = title.toLowerCase();
  if (t.includes("youtube")) return "Creator tools, analytics, SEO, research and practical workflows.";
  if (t.includes("ai")) return "Practical AI resources, tools, workflows and productivity ideas.";
  if (t.includes("converter") || t.includes("generator") || t.includes("downloader") || t.includes("scanner")) return "A useful free tool or practical guide for everyday digital work.";
  return "A practical technology guide, resource or tool from the Laxman Nepal archive.";
}

const quick = [
  ["01", "Free Tools", "Converters, generators & utilities", "/tools/"],
  ["02", "AI Hub", "Useful AI tools & workflows", "/ai/"],
  ["03", "Product Lab", "Specs, prices & comparisons", "/products/"],
  ["04", "YouTube", "Channels, trends & creator data", "/youtube/"],
];

const topics = [
  ["NEWS", "What's happening", "Useful technology updates without the noise.", "/news/"],
  ["REVIEWS", "Before you buy", "Real-world context for phones, laptops and gadgets.", "/reviews/"],
  ["GUIDES", "Learn & solve", "Step-by-step tutorials for software, devices and AI.", "/guides/"],
];

export default function HomePage() {
  const posts = loadBloggerPosts();

  return (
    <main className="home">
      <section className="container home-hero">
        <div className="hero-main glass">
          <div className="hero-orb orb-one" />
          <div className="hero-orb orb-two" />
          <p className="eyebrow">LAXMAN NEPAL · TECHNOLOGY PLATFORM</p>
          <h1>Tech that helps you <span>do more.</span></h1>
          <p className="hero-lead">News, product research, free tools, AI workflows and creator intelligence — built around practical use.</p>
          <div className="actions">
            <a className="btn primary" href="/tools/">Explore free tools <b>→</b></a>
            <a className="btn" href="/news/">Latest technology</a>
          </div>
          <div className="hero-trust"><span>✦ Practical</span><span>✦ Free tools</span><span>✦ Nepali creator</span></div>
        </div>

        <div className="hero-side">
          <a className="feature-card glass feature-dark" href="/products/">
            <span className="feature-kicker">PRODUCT LAB</span>
            <strong>Research smarter.</strong>
            <small>Compare products, specs and pricing signals.</small>
            <i>↗</i>
          </a>
          <a className="feature-card glass" href="/ai/">
            <span className="feature-kicker">AI HUB</span>
            <strong>Find useful AI.</strong>
            <small>Tools and workflows tested for real work.</small>
            <i>↗</i>
          </a>
        </div>
      </section>

      <section className="container quick-grid">
        {quick.map(([num, title, text, href]) => (
          <a className="quick-card glass" href={href} key={href}>
            <span>{num}</span><div><b>{title}</b><small>{text}</small></div><strong>↗</strong>
          </a>
        ))}
      </section>

      <section className="container home-section">
        <div className="section-head">
          <div><p className="eyebrow">DISCOVER</p><h2>Everything useful, in one place.</h2></div>
          <a href="/search/">Search the archive →</a>
        </div>
        <div className="topic-grid">
          {topics.map(([tag, title, text, href]) => (
            <a className="topic-card glass" href={href} key={tag}>
              <span className="topic-icon">{tag === "NEWS" ? "◉" : tag === "REVIEWS" ? "◈" : "✦"}</span>
              <div><span className="tag">{tag}</span><h3>{title}</h3><p>{text}</p></div>
              <b>Explore →</b>
            </a>
          ))}
        </div>
      </section>

      <section className="container home-section">
        <div className="section-head">
          <div><p className="eyebrow">FROM THE ARCHIVE</p><h2>Latest articles.</h2><p className="section-note">{posts.length ? String(posts.length) + " posts from the Blogger archive" : "Your Blogger archive will appear here."}</p></div>
          <a href="/search/">View all →</a>
        </div>
        {posts.length ? (
          <div className="post-grid home-post-grid">
            {posts.slice(0, 6).map((post, i) => {
              const title = (post.title || "Untitled post").trim();
              const date = post.published || post.updated;
              const dateLabel = date ? new Intl.DateTimeFormat("en", { year: "numeric", month: "short" }).format(new Date(date)) : "Archive";
              return <a className="post-card" href={post.path} key={post.path}>
                <div className="post-top"><span className="post-number">{String(i + 1).padStart(2, "0")}</span><span className="tag">{dateLabel}</span></div>
                <h3>{title}</h3><p>{postDescription(title)}</p><span className="read">Read article →</span>
              </a>;
            })}
          </div>
        ) : <div className="empty-card">No migrated Blogger posts were found during this build.</div>}
      </section>

      <section className="container home-section">
        <div className="tools-banner glass">
          <div><p className="eyebrow">FREE TOOLS</p><h2>Open a tool. Get the job done.</h2><p>Small utilities for converters, creators, students, developers and everyday digital work.</p></div>
          <div className="tool-pills"><a href="/tools/">All tools</a><a href="/tools/">Converters</a><a href="/ai/">AI tools</a><a href="/youtube/">Creator tools</a></div>
        </div>
      </section>

      <section className="container home-section home-final">
        <div className="final-panel">
          <p className="eyebrow">LAXMAN NEPAL</p>
          <h2>Less searching.<br /><span>More doing.</span></h2>
          <p>Built for people who want technology explained clearly and useful tools without unnecessary complexity.</p>
          <a className="btn primary" href="/tools/">Start exploring →</a>
        </div>
      </section>
    </main>
  );
}