const news = [
  { tag: "AI", title: "AI tools that actually save time", text: "Practical tools and workflows tested for everyday creators." },
  { tag: "PHONES", title: "What to check before buying a phone", text: "Specs, software, battery and real-world value in one guide." },
  { tag: "TOOLS", title: "Free tools built for creators", text: "Useful browser tools without unnecessary complexity." },
];

const products = [
  { type: "PHONE", name: "Phone Database", text: "Compare specs, variants and prices." },
  { type: "LAPTOP", name: "Laptop Database", text: "Find the right laptop for your budget." },
  { type: "COMPARE", name: "Product Compare", text: "Put products side by side." },
];

const tools = [
  ["AI Tools", "Discover practical AI tools and workflows."],
  ["Creator Tools", "Utilities for YouTube, thumbnails and content."],
  ["Web Tools", "Fast, free tools that work in your browser."],
];

export default function Home() {
  return (
    <main>
      <header className="site-header">
        <div className="container nav">
          <a className="brand" href="/">Laxman Nepal</a>
          <nav>
            <a href="/news/">News</a><a href="/reviews/">Reviews</a><a href="/phones/">Phones</a>
            <a href="/laptops/">Laptops</a><a href="/compare/">Compare</a><a href="/tools/">Tools</a>
            <a href="/ai/">AI</a><a href="/youtube/">YouTube</a>
          </nav>
        </div>
      </header>

      <section className="hero container">
        <div>
          <p className="eyebrow">TECHNOLOGY • TOOLS • AI</p>
          <h1>Technology that helps you <span>do more.</span></h1>
          <p className="hero-copy">Practical technology news, product data, comparisons, free tools and creator intelligence — built by Laxman Nepal.</p>
          <div className="actions"><a className="button primary" href="/news/">Explore technology</a><a className="button" href="/tools/">Browse free tools</a></div>
        </div>
        <div className="hero-card"><p>YOUR TECH HUB</p><strong>News + Data + Tools</strong><small>One platform for technology and creators.</small></div>
      </section>

      <section className="container section">
        <div className="section-head"><div><p className="eyebrow">LATEST</p><h2>Technology worth knowing</h2></div><a href="/news/">View all →</a></div>
        <div className="news-grid">{news.map((item) => <article className="card" key={item.title}><span>{item.tag}</span><h3>{item.title}</h3><p>{item.text}</p><a href="/news/">Read more →</a></article>)}</div>
      </section>

      <section className="container section">
        <div className="section-head"><div><p className="eyebrow">TECH DATABASE</p><h2>Research before you buy</h2></div><a href="/compare/">Compare →</a></div>
        <div className="product-grid">{products.map(([type,name,text]) => <a className="product-card" href={type === "PHONE" ? "/phones/" : type === "LAPTOP" ? "/laptops/" : "/compare/"} key={name}><span>{type}</span><h3>{name}</h3><p>{text}</p><b>Explore →</b></a>)}</div>
      </section>

      <section className="container section dark-section">
        <p className="eyebrow">TOOLS & AI</p><h2>Useful tools. No noise.</h2>
        <div className="tool-grid">{tools.map(([name,text]) => <a className="tool-card" href={name === "AI Tools" ? "/ai/" : "/tools/"} key={name}><h3>{name}</h3><p>{text}</p><b>Open →</b></a>)}</div>
      </section>

      <section className="container section youtube-card">
        <div><p className="eyebrow">YOUTUBE INTELLIGENCE</p><h2>Understand what is working.</h2><p>Track your channels, competitors, viral videos and emerging topics from one dashboard.</p></div>
        <a className="button primary" href="/youtube/">Open YouTube Intelligence</a>
      </section>

      <footer className="container footer"><strong>Laxman Nepal</strong><span>Technology • Tools • AI • Creator Intelligence</span></footer>
    </main>
  );
}
