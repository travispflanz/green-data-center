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

// Minimal HTML shell — inherits existing styles.css
function htmlShell(title, body) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title} — GreenCompute</title>
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <header class="site-header">
    <a href="/" class="site-logo">GreenCompute</a>
    <nav>
      <a href="/blog/">Blog</a>
      <a href="/facilities.html">Facilities</a>
      <a href="/sources.html">Sources</a>
    </nav>
  </header>
  <main>${body}</main>
  <footer class="site-footer">
    <p>&copy; 2026 GreenCompute. Edge-hosted on Cloudflare Workers.</p>
  </footer>
</body>
</html>`;
}

function renderBlogIndex(posts) {
  const items = posts.length
    ? posts.map(p => `<article class="post-card">
        <h2><a href="/blog/${p.slug}">${p.title}</a></h2>
        ${p.subtitle ? `<p class="subtitle">${p.subtitle}</p>` : ''}
        ${p.summary ? `<p>${p.summary}</p>` : ''}
        <time>${p.published_at ? p.published_at.split('T')[0] : ''}</time>
      </article>`).join('\n')
    : '<p>No articles published yet.</p>';
  return htmlShell('Blog', `<h1>Research Articles</h1>${items}`);
}

function renderPost(post) {
  return htmlShell(post.title, `
    <article class="post-full">
      <header>
        <h1>${post.title}</h1>
        ${post.subtitle ? `<p class="subtitle">${post.subtitle}</p>` : ''}
        <time>${post.published_at ? post.published_at.split('T')[0] : ''}</time>
        ${post.topic_slug ? `<a href="/topics/${post.topic_slug}" class="topic-badge">${post.topic_slug}</a>` : ''}
      </header>
      <div class="post-body">${post.body_html}</div>
    </article>`);
}

// Serve the 404.html asset body with a correct 404 status (avoids soft-404s)
async function notFound(request, env) {
  const res = await env.ASSETS.fetch(new Request(new URL('/404.html', request.url)));
  return new Response(res.body, { status: 404, headers: res.headers });
}

function renderTopicIndex(topic, posts) {
  const items = posts.length
    ? posts.map(p => `<li><a href="/blog/${p.slug}">${p.title}</a> — ${p.published_at ? p.published_at.split('T')[0] : 'draft'}</li>`).join('\n')
    : '<li>No articles yet.</li>';
  return htmlShell(topic.title, `
    <h1>${topic.title}</h1>
    <p>${topic.description || ''}</p>
    <ul>${items}</ul>`);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const ip = request.headers.get("CF-Connecting-IP") || "unknown";

    // Guard: never serve internal migration SQL as a public static asset
    // (site/migrations/ lives inside the ASSETS dir, so block it explicitly).
    if (url.pathname === "/migrations" || url.pathname.startsWith("/migrations/")) {
      return notFound(request, env);
    }

    // Dynamic routing — DB-driven virtual pages (before /api/subscribe and the ASSETS fallback)

    // Blog post: /blog/:slug  (empty slug → blog index)
    if (url.pathname.startsWith('/blog/')) {
      const slug = url.pathname.replace('/blog/', '').replace(/\/$/, '');
      if (!slug) {
        // Blog index — list all published posts
        const posts = await env.DB
          .prepare("SELECT slug, title, subtitle, summary, topic_slug, published_at FROM posts WHERE status='published' ORDER BY published_at DESC LIMIT 20")
          .all();
        return new Response(renderBlogIndex(posts.results), {
          headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'public, max-age=300' }
        });
      }
      const post = await env.DB
        .prepare("SELECT * FROM posts WHERE slug=? AND status='published'")
        .bind(slug).first();
      if (!post) return notFound(request, env);
      return new Response(renderPost(post), {
        headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'public, max-age=300' }
      });
    }

    // Topic index: /topics/:slug
    if (url.pathname.startsWith('/topics/')) {
      const topicSlug = url.pathname.replace('/topics/', '').replace(/\/$/, '');
      const [topic, posts] = await Promise.all([
        env.DB.prepare("SELECT * FROM topics WHERE slug=?").bind(topicSlug).first(),
        env.DB.prepare("SELECT slug, title, summary, published_at FROM posts WHERE topic_slug=? AND status='published' ORDER BY published_at DESC").bind(topicSlug).all()
      ]);
      if (!topic) return notFound(request, env);
      return new Response(renderTopicIndex(topic, posts.results), {
        headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'public, max-age=300' }
      });
    }

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
