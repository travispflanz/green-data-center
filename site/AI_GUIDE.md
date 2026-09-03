# AI Maintenance & Operations Protocol (AI_GUIDE.md)

This protocol enables any LLM or AI agent to maintain, update, and scale the GreenCompute static website without corrupting semantic structure, SEO authority, narrative flow, or internal link equity. Place this file in the repository root (or reference it as CLAUDE.md / .cursorrules).

## 1. Site Architecture & Directory Conventions

```
/
├── index.html            # Research hub (pillar): the full narrative arc
├── facilities.html       # Facility directory: 100% renewable & closed-loop campuses
├── cooling-tech.html     # Engineering deep-dive: PUE/WUE, DLC, dry coolers, calculator
├── regulations.html      # Legal deep-dive: EnEfG, CRU, DC-CFA2, EU EED
├── baseload-nuclear.html # Power deep-dive: nuclear PPAs, SMRs, FERC dockets
├── sources.html          # Annotated bibliography — the DESTINATION of inline citations
├── 404.html              # Styled not-found page
├── styles.css            # Editorial design system (see DESIGN.md at repo root)
├── _worker.js            # Edge worker: static assets + /api/subscribe + clean URLs
├── _headers              # Cloudflare edge security and cache control headers
├── schema.sql            # D1 schema (subscribers table)
├── sitemap.xml           # XML index of canonical URLs (CLEAN URLs, no .html)
├── robots.txt            # Crawler directives
├── feed.xml              # RSS 2.0 syndication feed
├── newsletter.js         # Shared footer signup handler
└── AI_GUIDE.md           # This protocol
```

**URL convention:** All internal links and canonicals use **clean URLs** (`/facilities`, not `facilities.html`). The worker resolves clean URLs to `.html` files automatically. Never link to `.html` forms.

## 2. Design System (read DESIGN.md at repo root)

- **Palette:** warm paper (`#FAFAF7`), ink (`#1A1A18`), one green accent (`#0E6B45`), hairline rules (`#E4E2DA`). Dark theme via `[data-theme="dark"]`.
- **Type:** Source Serif 4 (display/headings), Source Sans 3 (body), IBM Plex Mono (labels/figures/citations).
- **Anti-slop rules:** no gradients, no glassmorphism, no icon-topper cards, no equal-weight feature grids, no "Insights/Growth" labels. Structure comes from whitespace + hairline rules.
- **Bylines:** every page carries a byline with "GreenCompute Research · Updated <date>". Update the date when you edit content.

## 3. Standard Operating Procedures (SOPs)

### SOP 1: Adding a New Facility to facilities.html

1. **Add a table row** in the summary matrix (facility name, entity, location, power vector, cooling topology, WUE, PUE). Link the facility name to its case-study card anchor (`#facility-slug`).
2. **Add a case-study card** in the appropriate section (`100% renewable campuses` or `closed-loop / zero-water implementations`) using the `.card` markup:
   ```html
   <div class="card" id="facility-slug">
     <span class="badge badge-amber">[Energy Vector]</span>
     <h3>[Facility / Campus Name] — [City, Country]</h3>
     <p class="card-meta">[Operator] · [key detail]</p>
     <p>[2–3 sentences: infrastructure, grid interface, community impact.]<a class="cite" href="/sources#source-slug">[n]</a></p>
     <p><a class="source-ref" href="/sources#source-slug" target="_blank" rel="noopener">[Source label] ↗</a></p>
   </div>
   ```
3. **Register the source** in sources.html: add a `.card` with `id="source-slug"` in the matching category, with the exact link, title, and a one-line relevance note.
4. **Cross-link:** add the facility to the "Related reading" block of at least one other page (cooling-tech, regulations, or baseload-nuclear) with descriptive anchor text.
5. **Update sitemap.xml** `<lastmod>` if the page's priority/URL changed.

### SOP 2: Adding or Amending Legislation in regulations.html

1. **Update the comparison matrix** (jurisdiction, scope, renewable target, PUE cap, thermal quota). Keep `<th scope="row">` for jurisdiction names.
2. **Add/edit the statute section** with `id="[country-slug]"` (e.g., `#germany`), using the prose + bullet structure. Include the statutory link as a `.source-ref` to the official government portal.
3. **Add an inline citation** `<a class="cite" href="/sources#source-slug">[n]</a>` at the first mention of the statute.
4. **Register/update the source** in sources.html.
5. **Cross-link** to cooling-tech (if the law mandates waste heat reuse or inlet temperatures) and facilities (if it affects specific campuses).

### SOP 3: Maintaining Site-Wide SEO & Internal PageRank

Whenever modifying any page:

1. **Canonical validation:** ensure `<link rel="canonical">` points to the clean production URL (`https://greencompute-site.travis-097.workers.dev/facilities`, no `.html`).
2. **Meta description:** keep 140–160 characters, aligned with target long-tail keywords.
3. **No broken links:** never delete an anchor ID without redirecting or updating references in other files. Every `href="/sources#anchor"` must have a matching `id="anchor"` in sources.html.
4. **Contextual internal linking:** every page must link to 2+ sibling pages with **descriptive anchor text** in prose (not "click here"). Every page ends with a "Related reading" block (3–4 links with one-line descriptions).
5. **Inline citations:** every factual claim with a source gets `<a class="cite" href="/sources#anchor">[n]</a>`. Number citations sequentially per page.
6. **Bylines & dates:** every page has `<p class="byline">GreenCompute Research · Updated <time datetime="YYYY-MM-DD">...</time></p>`. Update on content change.
7. **Breadcrumbs:** every page has a breadcrumb nav (`Home / Page`).

## 4. Add-Ons & Integrations (current state)

| Add-on | Status | Notes |
|---|---|---|
| Newsletter (D1) | ✅ Live | `/api/subscribe` → D1 `subscribers` table; rate-limited (5/min/IP); honeypot field |
| Theme engine | ✅ Live | `prefers-color-scheme` + manual toggle, persisted in localStorage |
| PUE/WUE calculator | ✅ Live | cooling-tech.html, vanilla JS |
| RSS feed | ✅ Live | feed.xml, clean URLs |
| Client-side search | ✅ Live | index.html quick-search |
| JSON-LD | ✅ Live | WebSite + TechArticle per page |
| Cloudflare Web Analytics | ⏸ Placeholder | Uncomment beacon in `<head>` and add token to enable |
| Newsletter sending | ⏸ Future | D1 collects; switch to Buttondown/Resend when ready to send |

## 5. Deployment Checklist

1. `./scripts/deploy.sh --dry-run` — validates files, image URLs, canonical consistency.
2. `./scripts/deploy.sh` — builds zip + deploys to Cloudflare Workers.
3. Verify live: all pages 200, `/feed.xml` 200, `/api/subscribe` POST works, clean URLs resolve.
4. Credentials live in `.env` (gitignored) — never commit tokens.
