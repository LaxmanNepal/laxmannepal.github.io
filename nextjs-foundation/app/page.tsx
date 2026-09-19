const sections = [
  { title: "Latest Technology", items: ["News", "Reviews", "Guides"] },
  { title: "Tech Database", items: ["Phones", "Laptops", "Prices", "Compare"] },
  { title: "AI & Creator Tools", items: ["AI Tools", "YouTube", "SEO", "Creator Tools"] },
];

export default function HomePage() {
  return (
    <main>
      <header style={{ borderBottom: "1px solid var(--border)" }}>
        <div className="container" style={{ minHeight: 72, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 24 }}>
          <strong style={{ fontSize: 22 }}>LAXMAN NEPAL</strong>
          <nav aria-label="Primary navigation" style={{ display: "flex", gap: 18, flexWrap: "wrap" }}>
            <a href="/news">News</a>
            <a href="/reviews">Reviews</a>
            <a href="/guides">Guides</a>
            <a href="/phones">Phones</a>
            <a href="/laptops">Laptops</a>
            <a href="/tools">Tools</a>
            <a href="/youtube">YouTube</a>
          </nav>
        </div>
      </header>

      <section className="container" style={{ paddingBlock: 72 }}>
        <p style={{ color: "var(--muted)", marginBottom: 12 }}>THE NEXT LAXMANNEPAL PLATFORM</p>
        <h1 style={{ fontSize: "clamp(42px, 7vw, 84px)", lineHeight: 0.98, maxWidth: 900, margin: 0 }}>
          Technology, tools and creator intelligence — in one platform.
        </h1>
        <p style={{ color: "var(--muted)", fontSize: 18, lineHeight: 1.7, maxWidth: 720, marginTop: 24 }}>
          This is the isolated Next.js foundation. Existing production content remains untouched while the new architecture is built and tested.
        </p>
      </section>

      <section className="container" style={{ display: "grid", gap: 16, gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", paddingBottom: 72 }}>
        {sections.map((section) => (
          <article key={section.title} style={{ border: "1px solid var(--border)", borderRadius: 16, padding: 24, background: "var(--surface)" }}>
            <h2 style={{ marginTop: 0 }}>{section.title}</h2>
            <ul style={{ paddingLeft: 20, lineHeight: 1.9 }}>
              {section.items.map((item) => <li key={item}>{item}</li>)}
            </ul>
          </article>
        ))}
      </section>
    </main>
  );
}
