# Platform Mechanics — How the GreenCompute Site Actually Works

*Research date: 2026-09-03. All claims verified against developers.cloudflare.com (fetched 2026-09-03) and the live site.*

## 1. The deployment model: Workers static-assets mode

Your site is deployed as a **Cloudflare Worker with static assets** — the modern successor to both "Workers Sites" (legacy) and the classic "Pages" product. The `wrangler.toml` declares it:

```toml
name = "greencompute-site"
main = "site/_worker.js"
assets = { directory = "./site", binding = "ASSETS", not_found_handling = "404-page" }
compatibility_date = "2025-01-01"
```

What this means, in plain language:

- **`assets.directory = "./site"`** — Cloudflare uploads every file in `site/` to its global network. Each file is served from ~300 data centers worldwide. No origin server, no VPS, no monthly hosting bill.
- **`binding = "ASSETS"`** — your Worker script gets a handle (`env.ASSETS`) it can use to fetch those files programmatically.
- **`main = "site/_worker.js"`** — a small JavaScript program that runs *before* (or instead of) serving a file. Yours does two jobs: (1) handles `POST /api/subscribe` against D1, (2) rewrites clean URLs (`/facilities` → `/facilities.html`).
- **`not_found_handling = "404-page"`** — when nothing matches, serve your `site/404.html` with a real 404 status (not a silent SPA fallback).

### Is each page truly its own HTML file?

**Yes — literally.** The live site is 6 HTML files + a 404 + `styles.css` + `feed.xml` + `sitemap.xml`:

```
site/index.html            (17.4 KB)
site/sources.html          (15.6 KB)
site/baseload-nuclear.html (11.3 KB)
site/regulations.html      (13.5 KB)
site/cooling-tech.html     (13.6 KB)
site/facilities.html       (16.2 KB)
site/404.html              (3.0 KB)
site/styles.css            (12.9 KB)
```

Verified live: `curl` to `/`, `/facilities`, `/cooling-tech` all return 200 with the correct HTML; `/definitely-not-a-page` returns the 404 page with a `noindex` header. Each page is a complete, self-contained document with its own `<title>`, meta description, canonical URL, Open Graph tags, and JSON-LD structured data.

### How routing works (the exact flow)

1. Request arrives at `greencompute-site.travis-097.workers.dev/facilities`.
2. Because your `compatibility_date` is **2025-01-01** (before the 2025-04-01 cutoff), the Worker script **is** invoked on navigation requests. *(This is the subtle part — see the gotcha below.)*
3. `_worker.js` sees the path `/facilities`, rewrites it to `/facilities.html`, and calls `env.ASSETS.fetch()`.
4. The ASSETS binding serves the file from the edge cache.
5. If nothing matches, `not_found_handling = "404-page"` serves `404.html` with status 404.

### ⚠️ The compatibility-date gotcha (important for future edits)

Cloudflare's docs state: with the `assets_navigation_prefers_asset_serving` flag **or a compatibility date of 2025-04-01 or greater**, *navigation requests* (browser page loads) **skip the Worker script entirely** and go straight to the assets. Your clean URLs (`/facilities` without `.html`) work *only because* your compat date is 2025-01-01, so the Worker runs on every navigation.

**If anyone bumps `compatibility_date` to 2025-04-01+ without adding `run_worker_first = ["/api/*"]` (or similar), every clean URL will 404.** This is a documented footgun. Recommendation: add `run_worker_first = ["/api/*"]` to `wrangler.toml` now so the site survives a future compat-date bump. Source: https://developers.cloudflare.com/workers/static-assets/routing/worker-script/

## 2. Pages (classic) vs Workers static assets vs Workers Sites

| Product | What it is | Git-connected? | Custom `_worker.js`? |
|---|---|---|---|
| **Workers static assets** (yours) | Files + Worker script, deployed via `wrangler deploy` | Manual (or CI) | Yes — full control |
| **Pages (classic)** | Git-connected static hosting with built-in CI | Yes — native GitHub/GitLab integration, PR previews | Yes — "Advanced Mode" `_worker.js` |
| **Workers Sites (legacy)** | Old version of static assets | No | Deprecated |

Your setup is the "Advanced Mode" equivalent of Pages: same runtime, same ASSETS binding, but you control the deploy (currently via `scripts/deploy.sh` + wrangler). The practical difference: Pages gives you free PR preview URLs and a deploy-history UI in the dashboard; Workers static assets gives you the same via `wrangler versions` + the Deployments tab. Both are valid; yours is the more "code-first" path.

## 3. The full building-block catalog (what a small business can use)

| Product | One-line use case | Free tier (verified) |
|---|---|---|
| **D1** (SQLite at edge) | Newsletter signups, contact forms, any small relational data | 5M rows read/day, 100K rows written/day, 5 GB total, 10 DBs, 500 MB/DB, 7-day Time Travel, **no egress fees** |
| **KV** (key-value) | Session tokens, feature flags, cached API responses | 100K reads/day, 1K writes/day, 1 GB |
| **R2** (object storage) | Images, PDFs, downloads | 10 GB storage, 1M Class A ops/month, **unlimited egress** |
| **Queues** | Background jobs (e.g. email after signup) | 1M operations/month |
| **Durable Objects** | Real-time state, WebSockets, per-user coordination | 1M requests/month (beta pricing) |
| **Hyperdrive** | Speed up connections to external DBs | Included in Workers plans |
| **Vectorize** | Semantic search over your content | 5M vector dimensions free |
| **Workers AI** | Run small models at the edge (classification, summaries) | 10K neurons/day |
| **Cron Triggers** | Scheduled jobs (e.g. weekly digest) | 5 triggers/account |
| **Email Routing** | `hello@yourdomain` → your inbox, or → a Worker | Free |
| **Web Analytics** | Privacy-friendly visitor stats, no cookie banner | Free, unlimited |
| **Turnstile** | Invisible CAPTCHA for forms (spam protection) | Free, unlimited |
| **Bulk Redirects** | 301s for old URLs | Free |
| **Workers Observability** | Logs, metrics, traces for your Worker | Free tier included |

Sources: https://developers.cloudflare.com/workers/platform/limits/ , https://developers.cloudflare.com/d1/platform/pricing/ , https://developers.cloudflare.com/d1/platform/limits/

## 4. Database-driven patterns (what "database-driven" pragmatically means)

Your site is **already partly database-driven**: the newsletter form POSTs to `/api/subscribe`, which writes to D1. Verified live: a test POST returned 200 and inserted a row (then I deleted it via `wrangler d1 execute` — the full read/write cycle works; 6 real subscribers are in the DB).

The ladder of database-driven-ness, cheapest → most complex:

1. **Static shell + API endpoints (where you are now).** Pages stay HTML; D1 powers forms, comments, search, counters. Zero framework changes.
2. **Server-rendered fragments.** Use `HTMLRewriter` in the Worker to inject dynamic data (e.g. latest article list) into a static page at request time. Still no framework.
3. **Full edge framework** (Hono, Remix, Astro). The whole site becomes a Worker app that renders HTML from D1. More power, more complexity, more CPU time (free tier: 10 ms CPU/request — fine for small pages, tight for heavy rendering).

For a small business site, **pattern 1 is the sweet spot**: static pages are fast, cacheable, and free; D1 handles the interactive bits. Your current architecture is already the recommended pattern.

## 5. Free-tier reality check (exact numbers, verified)

- **Workers Free**: 100,000 requests/day (resets midnight UTC; Error 1027 if exceeded), 10 ms CPU/request, 128 MB memory, 50 subrequests/request, 20,000 static asset files per version, 25 MiB per file, 100 Workers/account.
- **D1 Free**: 5M rows read/day, 100K rows written/day, 5 GB total storage, 10 databases, 500 MB max per database, 7-day Time Travel, 50 queries per Worker invocation, **no egress/bandwidth charges**.
- A newsletter site with 1,000 subscribers and 10K page views/month uses a rounding error of these limits. The free tier is genuinely free for this use case — Cloudflare's own FAQ says the Free plan "will always include the ability to prototype and experiment with D1 for free."

## 6. What this means for GreenCompute specifically

- Each page is a real HTML file — you can edit, version, and diff them like documents.
- The newsletter API is a real database endpoint — you can query it, export it, and build on it.
- The two things that would most improve the setup: (1) add `run_worker_first` to future-proof clean URLs, (2) add a custom domain (see community report — `workers.dev` subdomains don't get edge caching).
