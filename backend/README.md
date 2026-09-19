# Laravel API Backend

This directory is reserved for the Laravel API implementation described in `docs/api-contract.md`.

## Implementation order
1. Create Laravel application.
2. Configure PostgreSQL and Redis.
3. Add /api/v1 route groups.
4. Implement models and migrations from database-schema.md.
5. Add authentication and admin authorization.
6. Add cache and queue jobs.
7. Add import jobs for legacy, product, and YouTube data.

Never commit production secrets. Keep `.env.example` non-sensitive.

Deployment target: `api.laxmannepal.com.np` behind Cloudflare.