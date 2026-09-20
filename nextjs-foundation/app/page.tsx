import { getAllContent, loadBloggerPosts } from "@/lib/content";
import { ArchiveCards, sectionPosts, sectionPostsMany } from "@/lib/section-content";
import BlogArchive from "@/app/blog-archive";


const quick = [
  ["01", "Free Tools", "Converters, generators & utilities", "/tools/"],
  ["02", "AI Hub", "Useful AI tools & workflows", "/ai/"],
  ["03", "Product Lab", "Specs, prices & comparisons", "/products/"],
  ["04", "YouTube", "Channels, trends & creator data", "/youtube/"],
];


const projects = [
  ["Kritim", "AI & web tools", "A growing collection of practical AI experiments and utilities.", "Kritim", "https://github.com/LaxmanNepal/Kritim"],
  ["Mausam", "Nepal weather", "A Nepal-focused weather experience designed for fast daily checks.", "mausam", "https://github.com/LaxmanNepal/mausam"],
  ["Nepali Patro", "Nepali calendar", "A modern Nepali calendar experience with a legacy-friendly route.", "Nepali-Patro", "https://github.com/LaxmanNepal/Nepali-Patro"],
  ["YouTube Channels", "Creator tools", "Channel identity, data and creator-focused experiments.", "youtube-channels", "https://github.com/LaxmanNepal/youtube-channels"],
  ["MyTTS", "AI voice", "Nepali + English voice experimentation and creator workflow tooling.", "mytts", "https://github.com/LaxmanNepal/mytts"],
];

const topics = [
  ["NEWS", "What's happening", "Useful technology updates without the noise.", "/news/"],
  ["REVIEWS", "Before you buy", "Real-world context for phones, laptops and gadgets.", "/reviews/"],
  ["GUIDES", "Learn & solve", "Step-by-step tutorials for software, devices and AI.", "/guides/"],
];

export default function HomePage() {
  const posts = loadBloggerPosts();
  const allContent = getAllContent();
  const latest = [...allContent].sort((a,b)=>new Date(b.published||b.updated||0).getTime()-new Date(a.published||a.updated||0).getTime()).slice(0,6);
  const recentCutoff = Date.now() - 1000*60*60*24*120;
  const trendingTopics = ["technology","ai","mobile","apps","productivity","nepal","creator","guides"].map(slug => {
    const items = allContent.filter(item => (item.sections||[]).includes(slug as never));
    const recent = items.filter(item => new Date(item.published||item.updated||0).getTime() >= recentCutoff).length;
    return {slug, count:items.length, recent, score:recent*3+items.length};
  }).sort((a,b)=>b.score-a.score).slice(0,5);
  const recommended = [...allContent].filter(item => item.type !== "news").sort((a,b)=>{
    const score = (item:typeof a) => ((item.sections||[]).length*4) + (new Date(item.published||item.updated||0).getTime()/1e12);
    return score(b)-score(a);
  }).slice(0,4);

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

      <section className="container home-section project-section">
        <div className="section-head">
          <div><p className="eyebrow">PROJECT LAB</p><h2>Built, tested, shipped.</h2><p className="section-note">Live experiments and open-source projects from the Laxman Nepal workspace.</p></div>
          <a href="https://github.com/LaxmanNepal?tab=repositories">View GitHub →</a>
        </div>
        <div className="project-grid">
          {projects.map(([title, category, description, repo, href], i) => (
            <a className="project-card glass" href={href} key={repo} target="_blank" rel="noreferrer">
              <div className="project-snapshot"><img src={`https://opengraph.githubassets.com/1/LaxmanNepal/${repo}`} alt={`${title} GitHub project snapshot`} loading="lazy" /></div>
              <div className="project-body"><div><span className="tag">{category}</span><h3>{title}</h3><p>{description}</p></div><span className="project-link">Open repo ↗</span></div>
            </a>
          ))}
        </div>
      </section>

      <section className="container home-section">
        <div className="section-head">
          <div><p className="eyebrow">FROM THE ARCHIVE</p><h2>All articles.</h2><p className="section-note">{posts.length ? String(posts.length) + " posts from the Blogger archive — newest first" : "Your Blogger archive will appear here."}</p></div>
          <a href="/search/">View all →</a>
        </div>
        {posts.length ? <BlogArchive posts={posts} /> : <div className="empty-card">No migrated Blogger posts were found during this build.</div>}
      </section>


      <section className="container home-section home-intelligence">
        <div className="section-head">
          <div><p className="eyebrow">CONTENT INTELLIGENCE</p><h2>What to explore next.</h2><p className="section-note">A static editorial layer generated from your article dataset — no fake views or engagement numbers.</p></div>
          <a href="/topics/">Browse topics →</a>
        </div>
        <div className="intelligence-grid">
          <div className="intelligence-panel glass">
            <div className="feed-heading"><div><span className="tag">LATEST</span><h3>Fresh articles</h3></div><a href="/news/">All news →</a></div>
            <div className="intel-list">{latest.map((p,i)=><a className="intel-item" href={p.path} key={p.id}><span>{String(i+1).padStart(2,"0")}</span><div><b>{p.title}</b><small>{p.published || p.updated || "Archive"} · {(p.sections||[]).slice(0,2).join(" · ")}</small></div><strong>→</strong></a>)}</div>
          </div>
          <div className="intelligence-panel glass">
            <div className="feed-heading"><div><span className="tag">TRENDING TOPICS</span><h3>What’s active</h3></div><a href="/topics/">Topics →</a></div>
            <div className="trend-list">{trendingTopics.map((t,i)=><a className="trend-item" href={"/topics/"+t.slug+"/"} key={t.slug}><span className="trend-rank">{String(i+1).padStart(2,"0")}</span><div><b>{t.slug[0].toUpperCase()+t.slug.slice(1)}</b><small>{t.recent} recent · {t.count} total articles</small></div><strong>↗</strong></a>)}</div>
          </div>
        </div>
        <div className="intelligence-recommended glass">
          <div className="feed-heading"><div><span className="tag">RECOMMENDED READING</span><h3>Useful next reads</h3></div><a href="/blog/">Full archive →</a></div>
          <div className="post-grid">{recommended.map((p,i)=><article className="post-card" key={p.id}><div className="post-top"><span className="post-number">{String(i+1).padStart(2,"0")}</span><span className="tag">{(p.sections||["ARTICLE"])[0].toUpperCase()}</span></div><h3>{p.title}</h3><p>{p.published || p.updated || "Archive"}</p><a className="read" href={p.path}>Read article →</a></article>)}</div>
        </div>
      </section>

      <section className="container home-section home-auto-section">
        <div className="section-head">
          <div><p className="eyebrow">AUTOMATIC HUB</p><h2>Fresh from the archive.</h2><p className="section-note">These sections update automatically from your existing content.</p></div>
          <a href="/content/">Explore content hub →</a>
        </div>
        <div className="home-feed-block">
          <div className="feed-heading"><div><span className="tag">NEWS</span><h3>Latest technology</h3></div><a href="/news/">View all →</a></div>
          <ArchiveCards posts={sectionPosts("news",6)} tag="NEWS"/>
        </div>
        <div className="home-feed-block">
          <div className="feed-heading"><div><span className="tag">PHONES</span><h3>Phones & mobile</h3></div><a href="/phones/">View all →</a></div>
          <ArchiveCards posts={sectionPosts("phones",6)} tag="PHONES"/>
        </div>
        <div className="home-feed-block">
          <div className="feed-heading"><div><span className="tag">NEPAL MARKET</span><h3>Mobile prices & buying</h3></div><a href="/mobile-prices-in-nepal/">View all →</a></div>
          <ArchiveCards posts={sectionPosts("mobile-prices",6)} tag="PRICES"/>
        </div>
        <div className="home-feed-block">
          <div className="feed-heading"><div><span className="tag">GUIDES & REVIEWS</span><h3>Learn and decide</h3></div><a href="/guides/">View guides →</a></div>
          <ArchiveCards posts={sectionPostsMany(["guides","reviews"],6)} tag="GUIDES"/>
        </div>
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