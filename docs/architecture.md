# Laxman Nepal Platform Architecture

## Target stack
- Web: Next.js + React + TypeScript
- API: Laravel/PHP
- Database: PostgreSQL
- Cache/queues: Redis
- CDN/WAF: Cloudflare

## Migration rule
The current Next.js foundation stays isolated until redirects, data migration, analytics, and production deployment are verified. Existing public URLs are contracts; create an explicit 301 redirect map before cutover.

## Core domains
1. Editorial: news, reviews, guides, explainers, categories, tags, authors, media.
2. Product database: brands, products, variants, specifications, prices, retailers, price history.
3. Comparison: normalized specs and side-by-side comparison pages.
4. Tools: free web tools, AI tools, creator utilities.
5. YouTube intelligence: channels, videos, metric snapshots, competitor/topic tracking.
6. Community: users, comments, newsletter subscriptions.

## Target monorepo
apps/web, apps/admin, backend, packages/ui, packages/types, packages/seo, database, docs.

## Rendering
Use ISR/static rendering for SEO-heavy pages; server rendering where freshness matters; client components only for interactive tools, comparisons, dashboards and filters.

## Migration phases
1. Next.js foundation
2. API contract + PostgreSQL schema
3. Laravel implementation
4. Data/import layer
5. Public routes + SEO migration
6. Admin/editorial workflows
7. Search/cache/performance
8. Production cutover with rollback plan
