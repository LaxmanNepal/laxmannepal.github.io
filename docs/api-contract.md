# API Contract v1

Base URL: `https://api.laxmannepal.com.np/api/v1`

## Editorial
- GET /articles?category=&tag=&page=&limit=
- GET /articles/{slug}
- GET /articles/{slug}/related

## Products
- GET /products?brand=&category=&page=&limit=
- GET /products/{slug}
- GET /products/{slug}/prices
- GET /products/{slug}/reviews
- GET /products/{slug}/related

## Taxonomy
- GET /brands
- GET /brands/{slug}
- GET /categories
- GET /categories/{slug}
- GET /tags/{slug}

## Comparison
- GET /compare?products=slug-a,slug-b
- GET /compare/products?ids=1,2,3

## Search
- GET /search?q=&type=&page=&limit=

## Tools
- GET /tools
- GET /tools/{slug}
- GET /tools/categories/{slug}

## YouTube
- GET /youtube/channels
- GET /youtube/channels/{slug}
- GET /youtube/channels/{slug}/videos
- GET /youtube/channels/{slug}/snapshots
- GET /youtube/videos/{id}

## Response conventions
Success: `{ "data": {}, "meta": {} }`
Error: `{ "error": { "code": "VALIDATION_ERROR", "message": "Readable message", "fields": {} } }`

Pagination uses page and limit, maximum public limit 100. Breaking changes require a new API version.