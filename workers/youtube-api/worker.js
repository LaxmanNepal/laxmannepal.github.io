/**
 * Laxman Nepal — YouTube Data API proxy
 *
 * Deploy as a Cloudflare Worker and add:
 *   YOUTUBE_API_KEY = <Google/YouTube API key>
 *
 * Routes:
 *   /search
 *   /channels
 *   /playlistItems
 *   /videos
 *
 * The browser never receives the YouTube API key.
 */

const ALLOWED = new Set(["/search", "/channels", "/playlistItems", "/videos"]);
const ALLOWED_ORIGINS = new Set([
  "https://laxmannepal.com.np",
  "https://www.laxmannepal.com.np"
]);

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";

    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: corsHeaders(origin)
      });
    }

    if (!ALLOWED.has(url.pathname)) {
      return json({ error: "Not found" }, 404, origin);
    }

    if (!env.YOUTUBE_API_KEY) {
      return json({ error: "YouTube API service is not configured." }, 503, origin);
    }

    const params = new URLSearchParams(url.search);

    // Keep the proxy intentionally narrow. The page only needs public GET methods.
    const part = params.get("part");
    if (part && part.length > 200) {
      return json({ error: "Invalid request." }, 400, origin);
    }

    params.set("key", env.YOUTUBE_API_KEY);

    const target = new URL("https://www.googleapis.com/youtube/v3" + url.pathname);
    target.search = params.toString();

    try {
      const upstream = await fetch(target.toString(), {
        method: "GET",
        headers: { "Accept": "application/json" }
      });

      const body = await upstream.text();

      return new Response(body, {
        status: upstream.status,
        headers: {
          "Content-Type": upstream.headers.get("Content-Type") || "application/json; charset=utf-8",
          "Cache-Control": "public, max-age=60, s-maxage=300",
          ...corsHeaders(origin)
        }
      });
    } catch {
      return json({ error: "YouTube service request failed." }, 502, origin);
    }
  }
};

function corsHeaders(origin) {
  const allowed = ALLOWED_ORIGINS.has(origin) ? origin : "https://laxmannepal.com.np";
  return {
    "Access-Control-Allow-Origin": allowed,
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Accept, Content-Type",
    "Vary": "Origin"
  };
}

function json(data, status, origin) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      ...corsHeaders(origin)
    }
  });
}
