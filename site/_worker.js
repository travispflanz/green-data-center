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
      <a href="/contact.html">Contact</a>
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

    // Admin panel (Path B) — protected by ADMIN_PASSWORD secret. Instant-publish to D1.
    if (url.pathname.startsWith('/admin')) {
      const authHeader = request.headers.get('Authorization') || '';
      const [scheme, encoded] = authHeader.split(' ');
      let isAuthed = false;
      try {
        isAuthed = scheme === 'Basic' && atob(encoded || '') === `admin:${env.ADMIN_PASSWORD}`;
      } catch { isAuthed = false; }   // malformed base64 → treat as unauthorized, never 500
      if (!isAuthed) {
        return new Response('Unauthorized', {
          status: 401,
          headers: { 'WWW-Authenticate': 'Basic realm="GreenCompute Admin"' }
        });
      }

      // GET /admin — post list with edit links
      if (url.pathname === '/admin' || url.pathname === '/admin/') {
        const posts = await env.DB
          .prepare("SELECT id, slug, title, status, published_at FROM posts ORDER BY created_at DESC")
          .all();
        const rows = posts.results.map(p =>
          `<tr><td><a href="/admin/edit/${p.id}">${esc(p.title)}</a></td><td>${esc(p.slug)}</td><td>${esc(p.status)}</td><td>${esc(p.published_at) || '—'}</td></tr>`
        ).join('');
        return new Response(`<!DOCTYPE html><html><head><meta charset="utf-8"><title>Admin</title><style>body{font-family:sans-serif;max-width:900px;margin:2rem auto;padding:1rem}table{width:100%;border-collapse:collapse}td,th{border:1px solid #ccc;padding:.5rem;text-align:left}</style></head><body>
          <h1>GreenCompute Admin</h1>
          <p><a href="/admin/new">+ New Post</a></p>
          <table><thead><tr><th>Title</th><th>Slug</th><th>Status</th><th>Published</th></tr></thead>
          <tbody>${rows}</tbody></table></body></html>`, {
          headers: { 'Content-Type': 'text/html; charset=utf-8' }
        });
      }

      // GET /admin/new — new post form
      if (url.pathname === '/admin/new' && request.method === 'GET') {
        return new Response(adminPostForm({}), { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
      }

      // GET /admin/edit/:id — edit existing post
      if (url.pathname.startsWith('/admin/edit/') && request.method === 'GET') {
        const id = url.pathname.replace('/admin/edit/', '');
        const post = await env.DB.prepare("SELECT * FROM posts WHERE id=?").bind(id).first();
        if (!post) return new Response('Not found', { status: 404 });
        return new Response(adminPostForm(post), { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
      }

      // POST /admin/save — create or update post
      if (url.pathname === '/admin/save' && request.method === 'POST') {
        const form = await request.formData();
        const id = form.get('id');
        const slug = form.get('slug')?.toString().trim().toLowerCase().replace(/[^a-z0-9-]/g, '-');
        const title = form.get('title')?.toString().trim();
        const subtitle = form.get('subtitle')?.toString().trim() || null;
        const body_html = form.get('body_html')?.toString().trim();
        const summary = form.get('summary')?.toString().trim() || null;
        const topic_slug = form.get('topic_slug')?.toString() || null;
        const status = form.get('status')?.toString() || 'draft';
        const published_at = status === 'published' ? new Date().toISOString() : null;

        if (id) {
          await env.DB.prepare(
            "UPDATE posts SET slug=?,title=?,subtitle=?,body_html=?,summary=?,topic_slug=?,status=?,published_at=COALESCE(published_at,?),updated_at=datetime('now') WHERE id=?"
          ).bind(slug,title,subtitle,body_html,summary,topic_slug,status,published_at,id).run();
        } else {
          await env.DB.prepare(
            "INSERT INTO posts (slug,title,subtitle,body_html,summary,topic_slug,status,published_at) VALUES (?,?,?,?,?,?,?,?)"
          ).bind(slug,title,subtitle,body_html,summary,topic_slug,status,published_at).run();
        }
        return Response.redirect(new URL('/admin', request.url).toString(), 302);
      }

      // Any other /admin/* → back to the list
      return Response.redirect(new URL('/admin', request.url).toString(), 302);
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

    // 1. Contact form endpoint
    if (url.pathname === "/api/contact") {
      if (request.method !== "POST") {
        return json({ success: false, message: "Method not allowed." }, 405);
      }
      if (rateLimited(ip)) {
        return json({ success: false, message: "Too many requests. Please try again later." }, 429);
      }

      try {
        const contentType = request.headers.get("content-type") || "";
        let name = "", email = "", subject = "", message = "", honeypot = "", sourceUrl = "";

        if (contentType.includes("application/json")) {
          const data = await request.json();
          name      = (data.name      || "").toString().trim();
          email     = (data.email     || "").toString().trim().toLowerCase();
          subject   = (data.subject   || "").toString().trim();
          message   = (data.message   || "").toString().trim();
          honeypot  = (data.website   || "").toString();
          sourceUrl = (data.source_url|| "").toString().trim();
        } else {
          const fd  = await request.formData();
          name      = (fd.get("name")       || "").toString().trim();
          email     = (fd.get("email")      || "").toString().trim().toLowerCase();
          subject   = (fd.get("subject")    || "").toString().trim();
          message   = (fd.get("message")    || "").toString().trim();
          honeypot  = (fd.get("website")    || "").toString();
          sourceUrl = (fd.get("source_url") || "").toString().trim();
        }

        // Honeypot: filled field means a bot — silently succeed
        if (honeypot) {
          return json({ success: true, message: "Message sent! We will be in touch soon." });
        }

        // Validate
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email || !emailRegex.test(email)) {
          return json({ success: false, message: "Please provide a valid email address." }, 400);
        }
        if (!message || message.length < 10) {
          return json({ success: false, message: "Message is too short (minimum 10 characters)." }, 400);
        }
        if (message.length > 5000) {
          return json({ success: false, message: "Message exceeds the 5,000-character limit." }, 400);
        }

        // Save to D1
        await env.DB.prepare(
          "INSERT INTO contact_submissions (name, email, subject, message, source_url) VALUES (?, ?, ?, ?, ?)"
        ).bind(name || null, email, subject || null, message, sourceUrl || null).run();

        // Email notification via Resend (fire-and-forget — never let failure block the user)
        try {
          const resendKey = env.RESEND_API_KEY;
          const notifyTo  = env.CONTACT_NOTIFY_EMAIL;
          if (resendKey && notifyTo) {
            const subjectLine = subject
              ? `[GreenCompute Contact] ${subject}`
              : "[GreenCompute Contact] New message";
            await fetch("https://api.resend.com/emails", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${resendKey}`,
              },
              body: JSON.stringify({
                from:    "onboarding@resend.dev",
                to:      [notifyTo],
                subject: subjectLine,
                text: `New contact form submission on GreenCompute.\n\nFrom: ${name || "(no name)"} <${email}>\nSubject: ${subject || "(none)"}\nSource: ${sourceUrl || "(unknown)"}\n\n${message}`,
                html: `<p><strong>New contact form submission on GreenCompute.</strong></p>
<table style="border-collapse:collapse;font-family:sans-serif;font-size:14px">
  <tr><td style="padding:4px 12px 4px 0;font-weight:bold">From</td><td>${esc(name || "(no name)")} &lt;${esc(email)}&gt;</td></tr>
  <tr><td style="padding:4px 12px 4px 0;font-weight:bold">Subject</td><td>${esc(subject || "(none)")}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;font-weight:bold">Source</td><td>${esc(sourceUrl || "(unknown)")}</td></tr>
</table>
<hr>
<pre style="font-family:sans-serif;white-space:pre-wrap">${esc(message)}</pre>`,
              }),
            });
          }
        } catch (_emailErr) {
          // Email failure is silent — submission was already saved to D1
        }

        return json({ success: true, message: "Message sent! We will be in touch soon." });
      } catch (err) {
        return json({ success: false, message: "Server error processing request. Please try again." }, 500);
      }
    }

    // 2. Newsletter subscription endpoint
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

// Escape text for safe interpolation into HTML (attributes, text nodes, and <textarea> content).
function esc(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// Admin post editor form (module scope).
function adminPostForm(post) {
  const topics = ['cooling','energy','regulations','facilities'];
  const opts = topics.map(t => `<option value="${t}" ${post.topic_slug===t?'selected':''}>${t}</option>`).join('');
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><title>${post.id ? 'Edit' : 'New'} Post — Admin</title>
  <style>body{font-family:sans-serif;max-width:900px;margin:2rem auto;padding:1rem}textarea{width:100%;height:300px;font-family:monospace}input,select{width:100%;margin:.25rem 0;padding:.4rem}label{display:block;margin-top:.75rem;font-weight:bold}</style></head><body>
  <h1>${post.id ? 'Edit Post' : 'New Post'}</h1>
  <p><a href="/admin">← Back</a></p>
  <form method="POST" action="/admin/save">
    <input type="hidden" name="id" value="${esc(post.id)}">
    <label>Title<input name="title" required value="${esc(post.title)}"></label>
    <label>Slug (URL-safe)<input name="slug" required value="${esc(post.slug)}"></label>
    <label>Subtitle<input name="subtitle" value="${esc(post.subtitle)}"></label>
    <label>Summary (one sentence)<input name="summary" value="${esc(post.summary)}"></label>
    <label>Topic<select name="topic_slug"><option value="">— none —</option>${opts}</select></label>
    <label>Status<select name="status">
      <option value="draft" ${post.status!=='published'?'selected':''}>Draft</option>
      <option value="published" ${post.status==='published'?'selected':''}>Published</option>
    </select></label>
    <label>Body HTML<textarea name="body_html">${esc(post.body_html)}</textarea></label>
    <br><button type="submit" style="margin-top:1rem;padding:.5rem 1.5rem">Save</button>
  </form>
</body></html>`;
}
