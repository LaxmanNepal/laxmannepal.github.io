# LaxmanNepal Next.js Foundation

Migration foundation for the future LaxmanNepal platform.

## Target architecture

- Next.js + React + TypeScript frontend
- Laravel versioned API backend
- PostgreSQL structured content/product database
- Redis caching and queues
- Cloudflare CDN/WAF

This directory is intentionally isolated from the existing GitHub Pages application. Production remains unchanged while the migration is developed incrementally.

## Planned modules

- Editorial: news, reviews, guides, authors, categories, tags
- Product data: phones, laptops, specifications, prices, price history
- Utility: comparison, search, tools
- Creator intelligence: YouTube channels, videos and analytics
- Admin: content, products, media and publishing workflow

## Migration rules

1. Do not break existing public URLs without redirects.
2. Do not replace the current production homepage yet.
3. Reuse existing content/data where practical.
4. Keep frontend, API and data models separated.
5. Prefer structured content over HTML blobs.
