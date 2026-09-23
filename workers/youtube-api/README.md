# YouTube Analytics API Proxy

This directory contains the server-side proxy required by
`2026/07/youtube-channel-analytics-pro.html`.

## Why this exists

GitHub Pages is static hosting. It cannot execute a server-side API route or keep a
YouTube API key secret at runtime. The analytics page therefore calls a small
serverless proxy instead of exposing the key in browser JavaScript.

## Cloudflare Worker setup

1. Create a Cloudflare Worker.
2. Deploy `worker.js`.
3. Add a Worker secret named:

`YOUTUBE_API_KEY`

4. Enable **YouTube Data API v3** for the Google Cloud project.
5. Restrict the Google API key to the YouTube Data API.
6. Set the Worker route/custom domain to your chosen API hostname.
7. Set this on the analytics page before its script loads:

```html
<script>
  window.LAXMAN_YOUTUBE_API_BASE = "https://YOUR-WORKER-DOMAIN";
</script>
```

Do not put the API key in this repository or in browser JavaScript.

## Routes used by the tool

- `GET /search?q=...`
- `GET /channels?id=...`
- `GET /playlistItems?playlistId=...`
- `GET /videos?id=...`

The worker forwards only these public read endpoints.

## Important

The public analytics tool intentionally does not claim to know private YouTube
Studio revenue or watch-time data for arbitrary channels.
