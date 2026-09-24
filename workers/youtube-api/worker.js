/**
 * Laxman Nepal — central YouTube Data API proxy
 * The API key is stored as a Cloudflare Worker secret.
 */

const PREFIXES = ["/youtube", "/api/youtube"];
const ALLOWED = new Set(["/search", "/channels", "/playlistItems", "/videos", "/health"]);
const ALLOWED_ORIGINS = new Set([
  "https://laxmannepal.com.np",
  "https://www.laxmannepal.com.np"
]);

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }

    if (request.method !== "GET") {
      return json({ error: "Method not allowed." }, 405, origin);
    }

    const routePath = normalizeRoute(url.pathname);

    if (routePath === "/health") {
      return json({ ok: true, service: "youtube-api" }, 200, origin);
    }

    if (!ALLOWED.has(routePath)) {
      return json({ error: "Not found." }, 404, origin);
    }

    if (!env.YOUTUBE_API_KEY) {
      return json({ error: "YouTube API service is not configured." }, 503, origin);
    }

    const params = new URLSearchParams(url.search);
    const part = params.get("part");

    if (part && part.length > 200) {
      return json({ error: "Invalid request." }, 400, origin);
    }

    params.set("key", env.YOUTUBE_API_KEY);

    const target = new URL("https://www.googleapis.com/youtube/v3" + routePath);
    target.search = params.toString();

    try {
      const upstream = await fetch(target.toString(), {
        method: "GET",
        headers: { Accept: "application/json" }
      });

      const body = await upstream.text();

      return new Response(body, {
        status: upstream.status,
        headers: {
          "Content-Type": upstream.headers.get("Content-Type") || "application/json; charset=utf-8",
          "Cache-Control": upstream.ok ? "public, max-age=60, s-maxage=300" : "no-store",
          ...corsHeaders(origin)
        }
      });
    } catch {
      return json({ error: "YouTube service request failed." }, 502, origin);
    }
  }
};

function normalizeRoute(pathname) {
  for (const prefix of PREFIXES) {
    if (pathname === prefix) return "/health";
    if (pathname.startsWith(prefix + "/")) {
      return pathname.slice(prefix.length) || "/";
    }
  }
  if (pathname === "/health") return "/health";
  return pathname;
}

function corsHeaders(origin) {
  const headers = {
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Accept, Content-Type",
    "Vary": "Origin"
  };

  if (ALLOWED_ORIGINS.has(origin)) {
    headers["Access-Control-Allow-Origin"] = origin;
  }

  return headers;
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
