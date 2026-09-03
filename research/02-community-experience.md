# Community Experience — What Real People Say About Cloudflare Pages/Workers/D1

*Research date: 2026-09-03. Sources: Reddit (via pullpush.io mirror), Hacker News (Algolia API), individual developer blogs, YouTube transcripts. Quotes are verbatim from fetched content.*

## The headline: for a small site, the free tier is genuinely free — and people love it

**Finding 1 — "Free forever" is real for small static sites.** A Reddit user who'd hosted on Pages for over a year: *"I've been hosting my website on Cloudflare Pages for more than a year now and it doesn't have any downtime regardless of the traffic. It's basically free without any restrictions at all."* (r/CloudFlare, "Cloudflare Pages free forever. What's the catch?") The catch, per replies: file-size limits (25 MiB) and the expectation that you connect a git repo. For a small site, there is no catch.

**Finding 2 — The business model is enterprise, not your $0.** On HN's 607-point thread "Why is Cloudflare Pages' bandwidth unlimited?" (mattsayar.com), the consensus: *"It's the freemium model at work... The real money, and their focus as a company, is in enterprise contracts."* Another: *"We're building our startup infra on cloudflare over the other major hyperscalers and it turned out to be an amazing decision... Generous free tiers, pricing scales very competitively after that."* Small sites are the funnel; the product is genuinely good at the bottom.

**Finding 3 — Small-business users are told "yes, this works for you."** On r/CloudFlare ("Hosting a Simple Website for My Business"), the top advice: *"Cloudflare pages is not limited to 'three pages'... You can host a website with thousands of pages on Cloudflare Pages for free. That said Cloudflare pages is best suited for hosting static HTML/CSS/JS webpages."* Another thread ("Cloudflare Pages - small website", 1,000 visitors/month, Adobe Muse site): *"CloudFlare pages is perfect for your use case."*

## The #1 pain point: cache invalidation (you already hit this)

**Finding 4 — Stale CSS/JS is the most common complaint.** r/Hosting thread "Cloudflare CDN Stale Content Issue": *"It keeps serving old CSS/JS no matter what I do, and I have to manually purge the cache every time I update something."* Cloudflare's own community thread "Ensure users get my updated assets (.js, .css, etc.) following a Pages deployment" explains the fix: hash asset filenames (e.g. `styles.a1b2c3.css`) and cache those immutably, while HTML revalidates. **This is exactly the bug you fixed in commit a90ea64** (CSS was cached immutable for 1 year; HTML now revalidates every load). Your fix is the community-standard solution.

**Finding 5 — `workers.dev` subdomains don't get edge caching.** r/CloudFlare "Help with caching": *"CloudFlare caching is not enabled at all for endpoints on the workers.dev domain. You need to configure custom domain or subdomain for the worker to enable caching."* This is a strong argument for adding a custom domain to GreenCompute — you'd get the CDN cache on HTML/CSS/JS automatically.

## D1: loved for small apps, with honest caveats

**Finding 6 — D1 in production is real and working.** r/CloudFlare "is there anyone using D1 database for production?" (26 points): *"We've been using D1 for a few things and it's great. Super fast and can't beat the cost. Starting to migrate bigger projects now too."* And: *"I've been using it on a custom serverless proxy for caching. For my use case it's definitely the best, low latency and fast."*

**Finding 7 — The caveats are about scale, not small sites.** Same thread: *"Until they support direct SQL transactions and solve bugs with foreign keys, I will never use D1 for my production apps"* — a real concern for complex multi-table apps, irrelevant for a newsletter table. r/webdev "Cloudflare workers, Sqlite D1, experiences?": *"D1 is region specific and is not globally distributed"* and *"you're vendor-locking yourself to Cloudflare somewhat."* For a small site's newsletter, none of these bite.

**Finding 8 — Indexes matter even at small scale.** dev.to "Cloudflare D1: SQLite at the Edge After 6 Months in Production": *"Composite indexes matter more at the edge. SQLite's query planner is conservative. Without the right indexes, even small tables scan fully."* Your `subscribers` table is tiny; an index on `email` (for the `INSERT OR IGNORE` dedupe) is the one thing worth having.

## Platform comparisons: Cloudflare holds up

**Finding 9 — Cold starts: Cloudflare is the fastest.** punits.dev "Vercel vs Netlify vs Cloudflare: Serverless Cold Starts Compared" (fetched full text): Cloudflare's isolates start in single-digit milliseconds; Vercel and Netlify are slower, especially cold. r/nextjs "I measured Vercel vs Netlify vs Cloudflare cold start timings": *"Netlify is the slowest overall... Vercel serves pages fast (slower than CF though)."*

**Finding 10 — "Cloudflare for advanced, Vercel for simple."** r/webdev "Cloudflare, Vercel, or Netlify – which one actually holds up for YOU?": *"Cloudflare all day long."* / *"Vercel for simple projects. Cloudflare for advanced projects."* / *"workers & pages has been amazing - powering millions of requests per month for extremely cheap."* The Netlify $100k bill incident still gets mentioned as a cautionary tale.

## Individual voices worth reading

**Finding 11 — Matt Sayar** (mattsayar.com, "Why does Cloudflare Pages have such a generous Free tier?"): the best single explainer of Cloudflare's economics — free tier as customer acquisition for enterprise, with unlimited bandwidth as the hook. 607 points on HN.

**Finding 12 — Taras Glek** (taras.glek.net, "Cloudflare Pages: Best server tech since CGI-bin?", 406 HN points): celebrates how simple static hosting has become, with a real warning: *"Cloudflare pages will strip the file extension off of your html pages, and perform permanent redirects to those new URLs. Now if you're intending on moving to a new hosting service that doesn't do that... all Google search results to your site will 404."* (Clean URLs are great until you leave — another reason to keep a git repo and a migration plan.)

**Finding 13 — Tyler L. W. Smith** (dev.to, "12 things I learned about hosting serverless sites on Cloudflare"): practical gotchas including *"Initial deployments are SLOW"* (first deploy creates the Worker/Pages project) and the D1 migration workflow (`wrangler d1 migrations create`).

**Finding 14 — Simon Willison** (simonwillison.net/tags/cloudflare): uses Cloudflare heavily and documents it; his quote on building `cloudflare/workers-oauth-provider` with AI — *"It took me a few days to build the library with AI. I estimate it would have taken a few weeks, maybe months to write by hand"* — is a great example of the Workers ecosystem being AI-agent-friendly.

**Finding 15 — Wes Bos** (YouTube, "Here is what Cloudflare Workers do"): the clearest beginner explainer of what a Worker actually is (a script that runs on every request and can modify the response). Good first video for the case study.

## Cost reports

**Finding 16 — Real bills are $0.** Cloudflare community: *"If you're on the Free plan, and you don't add any paid services, yes, it's actually free... as long as it's a static site."* Multiple HN commenters report running personal sites and small products on the free tier for years with $0 bills. The paid tier ($5/mo Workers Paid) only becomes relevant past ~100K requests/day or when you need >10ms CPU.

## Bottom line for GreenCompute

- The architecture you have (static HTML + D1 newsletter API on Workers free) is the community-validated sweet spot for a small content site.
- The two upgrades with the most community support: **custom domain** (enables caching, professional URL) and **git-connected deploys** (PR previews, rollbacks — see the GitHub report).
- The cache-header fix you already made is the exact fix the community recommends.
