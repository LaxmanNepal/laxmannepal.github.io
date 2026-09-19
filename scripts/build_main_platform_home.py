from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Laxman Nepal — Technology, Tools, AI & Creator Intelligence</title>
<meta name="description" content="Laxman Nepal brings technology news, product intelligence, comparisons, free web tools, AI resources and YouTube creator intelligence into one practical platform.">
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://laxmannepal.com.np/">
<meta property="og:type" content="website">
<meta property="og:title" content="Laxman Nepal — Technology, Tools, AI & Creator Intelligence">
<meta property="og:description" content="Technology, product data, free tools, AI and creator intelligence in one platform.">
<meta property="og:url" content="https://laxmannepal.com.np/">
<link rel="stylesheet" href="/assets/css/main-platform.css">
</head>
<body>
<header class="site-header"><div class="wrap nav">
<a class="brand" href="/">LAXMAN<span>NEPAL</span></a>
<nav><a href="/news/">News</a><a href="/reviews/">Reviews</a><a href="/guides/">Guides</a><a href="/products/">Products</a><a href="/compare/">Compare</a><a href="/tools/">Tools</a><a href="/youtube/">YouTube</a></nav>
<a class="nav-cta" href="/search/">Search</a>
</div></header>
<main>
<section class="hero wrap"><div class="hero-copy">
<p class="eyebrow">TECHNOLOGY • TOOLS • AI • CREATOR INTELLIGENCE</p>
<h1>Technology that helps you <em>do more.</em></h1>
<p class="lead">A practical technology platform for news, product research, comparisons, free web tools, AI workflows and YouTube intelligence.</p>
<div class="actions"><a class="btn primary" href="/news/">Explore technology</a><a class="btn" href="/tools/">Open free tools</a></div>
</div><div class="hero-panel"><span class="panel-label">THE PLATFORM</span>
<div class="metric"><b>News</b><small>Useful updates, not noise</small></div><div class="metric"><b>Data</b><small>Products, specs, prices & comparisons</small></div><div class="metric"><b>Tools</b><small>Free utilities for everyday work</small></div><div class="metric"><b>AI</b><small>Practical workflows & resources</small></div>
</div></section>

<section class="section wrap"><div class="section-head"><div><p class="eyebrow">LATEST</p><h2>Stay ahead without the clutter.</h2></div><a href="/news/">View all news →</a></div>
<div class="grid three"><a class="card" href="/news/"><span class="tag">NEWS</span><h3>Latest technology news</h3><p>Phones, laptops, apps, AI and technology stories worth knowing.</p></a><a class="card" href="/reviews/"><span class="tag">REVIEWS</span><h3>Hands-on reviews</h3><p>Practical buying context, strengths, limitations and real-world use.</p></a><a class="card" href="/guides/"><span class="tag">GUIDES</span><h3>How-to guides</h3><p>Clear tutorials for apps, devices, software, AI and everyday tech.</p></a></div></section>

<section class="section database"><div class="wrap"><div class="section-head"><div><p class="eyebrow">TECH DATABASE</p><h2>Research before you buy.</h2></div><a href="/products/">Open product database →</a></div>
<div class="grid four"><a class="db-card" href="/phones/"><strong>Phones</strong><span>Specs · variants · prices</span></a><a class="db-card" href="/laptops/"><strong>Laptops</strong><span>Specs · configurations · prices</span></a><a class="db-card" href="/compare/"><strong>Compare</strong><span>Side-by-side decisions</span></a><a class="db-card" href="/price/"><strong>Price history</strong><span>Track changes over time</span></a></div></div></section>

<section class="section wrap"><div class="section-head"><div><p class="eyebrow">PRODUCT INTELLIGENCE</p><h2>More than a specification sheet.</h2></div></div>
<div class="grid three"><a class="card" href="/products/"><h3>Product database</h3><p>Structured brands, products, variants and specifications for fast research.</p></a><a class="card" href="/deals/"><h3>Deals & price signals</h3><p>Surface useful pricing information and deal opportunities as the data grows.</p></a><a class="card" href="/recommend/"><h3>Recommendations</h3><p>Turn product specifications and priorities into clearer shortlists.</p></a></div></section>

<section class="section tools"><div class="wrap"><div class="section-head light"><div><p class="eyebrow">FREE TOOLS + AI</p><h2>Useful tools, built to save time.</h2></div><a href="/tools/">Browse all tools →</a></div>
<div class="tool-grid"><a href="/tools/" class="tool"><span>01</span><b>Everyday tools</b><small>Converters, generators and practical utilities.</small></a><a href="/ai/" class="tool"><span>02</span><b>AI tools</b><small>Discover useful AI workflows and websites.</small></a><a href="/youtube/" class="tool"><span>03</span><b>Creator tools</b><small>Research, SEO and YouTube utilities.</small></a><a href="/seo/" class="tool"><span>04</span><b>SEO tools</b><small>Make content easier to discover.</small></a></div></div></section>

<section class="section wrap"><div class="youtube-box"><div><p class="eyebrow">YOUTUBE INTELLIGENCE</p><h2>Understand channels, videos and trends.</h2><p>Track your channels, competitors, viral videos, topics and performance snapshots in one workspace.</p></div><a class="btn primary" href="/youtube/">Open YouTube intelligence</a></div></section>

<section class="section wrap"><div class="section-head"><div><p class="eyebrow">THE LAXMAN NEPAL ECOSYSTEM</p><h2>One platform. Multiple useful destinations.</h2></div></div>
<div class="grid four ecosystem"><a class="card" href="/news/"><b>Technology</b><span>News, reviews & guides</span></a><a class="card" href="/products/"><b>Product data</b><span>Phones, laptops & prices</span></a><a class="card" href="/tools/"><b>Free tools</b><span>Utilities & AI resources</span></a><a class="card" href="/youtube/"><b>Creator intelligence</b><span>Channels, videos & trends</span></a></div></section>

<section class="section final-cta"><div class="wrap cta"><div><p class="eyebrow">BUILT FOR PRACTICAL USE</p><h2>Less searching. More doing.</h2></div><a class="btn primary" href="/tools/">Start with the tools →</a></div></section>
</main>
<footer><div class="wrap footer"><div><strong>LAXMAN NEPAL</strong><p>Technology · Tools · AI · Creator Intelligence</p></div><div><a href="/about/">About</a><a href="/contact/">Contact</a><a href="/privacy/">Privacy</a></div></div></footer>
</body></html>"""
(ROOT / "index.html").write_text(HTML, encoding="utf-8")
print("Built main platform homepage")
