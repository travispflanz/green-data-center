// GreenCompute edge worker — static assets + newsletter API + clean URLs
// Runs on Cloudflare Workers (static-assets Advanced Mode).

const RATE_LIMIT = { windowMs: 60_000, max: 5 }; // 5 POSTs per minute per IP
const rateBuckets = new Map();

function rateLimited(ip) {
  const now = Date.now();
  const bucket = rateBuckets.get(ip);
  if (!bucket || now - bucket.start > RATE_LIMIT.windowMs) {
    rateBuckets.set(ip, { start: now, count: 1 });
    return false;
  }
  bucket.count += 1;
  return bucket.count > RATE_LIMIT.max;
}

function json(body, status = 200, extra = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Cache-Control": "no-store",
      ...extra,
    },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const ip = request.headers.get("CF-Connecting-IP") || "unknown";

    // 1. Newsletter subscription endpoint
    if (url.pathname === "/api/subscribe") {
      if (request.method !== "POST") {
        return json({ success: false, message: "Method not allowed." }, 405);
      }
      if (rateLimited(ip)) {
        return json({ success: false, message: "Too many requests. Please try again later." }, 429);
      }

      try {
        const contentType = request.headers.get("content-type") || "";
        let email = "";
        let sourcePage = "index";

        if (contentType.includes("application/json")) {
          const data = await request.json();
          email = data.email?.trim().toLowerCase();
          sourcePage = data.source || "index";
        } else if (contentType.includes("application/x-www-form-urlencoded")) {
          const formData = await request.formData();
          email = formData.get("email")?.toString().trim().toLowerCase();
          sourcePage = formData.get("source")?.toString() || "index";
        }

        // Honeypot: a filled "website" field means a bot
        if (request.method === "POST") {
          const formData = contentType.includes("application/x-www-form-urlencoded")
            ? await request.clone().formData().catch(() => null)
            : null;
          if (formData && formData.get("website")) {
            return json({ success: true, message: "Subscription recorded." }); // silently accept bots
          }
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email || !emailRegex.test(email)) {
          return json({ success: false, message: "Please provide a valid institutional email address." }, 400);
        }

        if (env.DB) {
          const statement = env.DB.prepare(
            "INSERT OR IGNORE INTO subscribers (email, source_page) VALUES (?, ?)"
          ).bind(email, sourcePage);
          const result = await statement.run();
          return json({
            success: true,
            message: result.meta?.changes > 0
              ? "Subscription verified. You are registered for regulatory alerts."
              : "Your email is already registered in the research index.",
          });
        }

        return json({ success: true, message: "Subscription recorded (Cloudflare D1 binding pending)." });
      } catch (error) {
        return json({ success: false, message: "Server error processing request. Please try again." }, 500);
      }
    }

    // 2. Static assets + clean-URL handling.
    // Cloudflare natively serves /404.html (status 404) for unknown paths
    // via not_found_handling = "404-page", so no manual 404 handling needed.
    let response = await env.ASSETS.fetch(request);

    // Clean URLs: /facilities → /facilities.html
    if (response.status === 404 && !url.pathname.includes(".")) {
      const cleanPath = url.pathname.replace(/\/$/, "") + ".html";
      const altUrl = new URL(cleanPath, request.url);
      const altResponse = await env.ASSETS.fetch(new Request(altUrl, request));
      if (altResponse.status !== 404) {
        return altResponse;
      }
    }

    return response;
  },
};
