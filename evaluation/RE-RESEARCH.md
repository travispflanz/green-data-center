# GreenCompute Re-Research & Site Evaluation

**Date:** 2026-09-02/03
**Method:** All 8 original Gemini-session prompts re-run as parallel fresh research (7 subagents completed, 1 transcript-inventory task superseded by direct analysis), plus a full local audit of every site page and a live-site evaluation.

---

## 0. Executive Summary

The user's two instincts are both correct:

1. **The research depth exists in the import but never made it into the site.** The imported transcript (`import/raw/green-data-center-plan.md`, 28,276 lines) contains a complete research report with **41 unique source URLs** and hundreds of named entities (FERC ×262, EnEfG ×174, CRU ×126, DC-CFA2 ×112, Moro Hub ×140, Susquehanna ×96, etc.). The site carries only **24 URLs** and compresses the narrative into tables and cards. The "output before building" was richer because it was — the site is a lossy compression of it.

2. **The site reads as a pile of assets, not a story.** Every page is: badge → H1 → lead → table/cards → footer. Sources are dumped in a flat 9-link bibliography. Three of six pages have **zero internal links** in their body copy. There are no bylines, no dates, no inline citations, no related-content blocks.

**Verdict:** The site needs a narrative restructure (pillar → deep-dive arcs with contextual interlinking), an editorial design system (serif display + humanist sans + mono figures, warm paper palette, hairline rules), and inline source citation woven into prose. The research content to support all of this already exists in the transcript.

---

## 1. Prompt-by-Prompt Findings

### Prompt 1 — AI maintenance guide + add-ons
**Fresh research:** A good AI_GUIDE.md/CLAUDE.md must include: project overview + audience, tech stack + versions, build/test/deploy commands, project structure, coding conventions, and critical rules (no secrets, static-export constraints, accessibility). JSON-LD is Google's recommended schema format. Cookieless analytics can be a small Cloudflare Worker or Cloudflare Web Analytics.
**Site gaps:** AI_GUIDE.md exists (11.3KB) and is solid, but the site's client-side search only filters 3 cards on index.html; sources are split into a flat bibliography with no inline citations; no analytics enabled (placeholder comment only).
**Recommendations:** Keep AI_GUIDE.md (already good); upgrade search to Pagefind (indexes all pages, zero infra); enable Cloudflare Web Analytics; add inline citation convention to AI_GUIDE SOPs.

### Prompt 2 — Add-ons + email signup
**Fresh research:** Buttondown is the best developer-fit newsletter service for static sites (Markdown-first, REST API, free ≤100 subscribers). Formspree is simplest for one-off forms. Cloudflare D1 native is fine for pure collection. Pagefind is the zero-config search upgrade.
**Site gaps:** No double opt-in (GDPR/CAN-SPAM risk); no spam protection (no Turnstile/honeypot/rate-limit on /api/subscribe); no unsubscribe; no sending capability; copy mismatch between index inline form and shared newsletter.js; duplicated client JS.
**Recommendations:** Keep D1 for now (free, deduped, graceful fallback) but harden it: add Cloudflare Turnstile or honeypot + rate limiting; switch to Buttondown when ready to actually send; optionally Resend for confirmations.

### Prompt 3 — Native Cloudflare D1 + images with credits
**Fresh research:** Workers static-assets "Advanced Mode" = `main` + `assets.directory`; worker accesses assets via `env.ASSETS.fetch`. D1 schema should use versioned `wrangler d1 migrations` rather than a single schema.sql. Image SEO: descriptive alt text, width/height, lazy loading, srcset, and proper Wikimedia attribution (license + author + source link).
**Site gaps:** D1 schema is a single schema.sql (no migrations/ folder, no rollback); no `preview_database_id` (local/remote drift risk); images have alt/width/height/lazy but no srcset; attribution is present in captions (good) but not consistently linked from prose.
**Recommendations:** Adopt `wrangler d1 migrations`; add `preview_database_id`; add srcset for hero images; keep the caption-attribution pattern (it's correct) and extend it with inline source links.

### Prompt 4 — Zip export + least-friction deploy
**Fresh research:** Cloudflare is converging on Workers — Pages is in maintenance mode; static asset serving is free on Workers. New greenfield static sites should be Workers + static assets. Workers Builds (git integration) is the zero-touch path.
**Site gaps:** Deploy requires local Node/npx + token in .env (manual, environment-dependent); zip only produced when deploy.sh runs (no standalone "give me the zip" path); no git repo connected to Cloudflare (no auto-deploy).
**Recommendations:** Keep Workers static-assets (correct target); add a standalone `make-zip` script; document Workers Builds as the future zero-touch path once the repo is on GitHub.

### Prompt 5 — Pages Functions vs _worker.js error
**Fresh research:** For new full-stack projects in 2026, Cloudflare's recommended path is Workers with static assets (single wrangler.toml: assets + API routes + bindings in one deployment). The original drag-and-drop `/functions` error is real (drag-and-drop only fails on `/functions` folders, not `_worker.js`).
**Site gaps:** `not_found_handling = "none"` + no `html_handling` forces hand-rolled clean-URL logic that the platform does natively; worker runs on EVERY request instead of only `/api/*`; `_worker.js` sits inside the asset dir relying on `.assetsignore`; stale `compatibility_date`; D1 failure silently masked; no rate limiting.
**Recommendations:** Set `html_handling = "auto-trailing-slash"` and `not_found_handling = "404-page"` (or keep worker but simplify); move `_worker.js` out of the assets dir; bump `compatibility_date`; add error handling + rate limiting to /api/subscribe.

### Prompt 6 — Expand, modern design, avoid AI look (THE BIG ONE)
**Fresh research (editorial design):** Sites that read as human (CarbonPlan, Our World in Data, IEEE Spectrum, The Verge, Rest of World, MIT Tech Review) share: restrained serif or humanist type, bylines + author bios + publication dates, inline citation/footnote markers, real photography with captions, hedged specific language, pull quotes, asymmetric editorial rhythm. The single strongest anti-AI-slop signal is **named human authors and dated, revisable content**.
**Slop diagnostic of current site:** Score ~7/10. Tells that fire: feature-tile card grids (equal-weight cards), badge toppers on every section, generic CTA links ("Inspect X →"), no bylines/dates (anonymous generated feel), flat bibliography, uniform card layout with no editorial rhythm, marketing-style section headers.
**Fresh news (data-center sustainability, 2026):** Subagent collected 10-15 recent items across Google News RSS (renewable energy, closed-loop cooling, water usage, nuclear PPAs) — details in the full digest; key theme: nuclear PPAs (Crane/TMI, Kairos/Google, Susquehanna/AWS) and water-stress-driven closed-loop adoption remain the dominant 2026 storylines.
**Recommendations:** Restructure index as longform narrative with sticky section nav; add bylines/dates/"last updated" stamps; weave inline citations into prose; vary layout rhythm (pull quotes, full-bleed figures, asymmetric grids); reintroduce facility case-study depth from the transcript; replace generic hero with real photography.

### Prompt 7 — Evaluate live site and repair
**Live evaluation:** All primary pages HTTP 200 with strong security headers (HSTS, CSP, X-Frame-Options, nosniff). Clean URLs work. **Errors found:** GET /api/subscribe returns Cloudflare 1101 (HTTP 500) instead of 405 (worker only handles POST, falls through to asset handler); unknown paths return 404 without a styled 404 page; canonical/og:url/sitemap/feed URLs point to `.html` forms while clean URLs are the canonical form (inconsistent); no og:image on any page; no breadcrumbs; no related-content blocks.
**SEO research (internal linking):** Pillar-page hubs with contextual anchor text outperform footer-only links; anchor text should be descriptive (not "click here"); related-content blocks at article ends improve crawlability and UX.
**Recommendations:** Fix /api/subscribe GET → 405; add styled 404; unify canonicals to clean URLs; add og:image; add breadcrumbs; add related-content blocks; weave contextual internal links into prose.

### Prompt 8 — Full session transcript export
**Transcript inventory (direct analysis):** The transcript contains the complete research report: power-density transitions (5-10 → 50-200 kW/rack), AI workload volatility (checkpointing swings, inference 90% lifecycle energy), BESS at 1500V DC, cooling thermodynamics (PUE/WUE, 1.5-3.0 L/kWh evaporative, 7.6 L/kWh supply-chain water, 125M liters saved), nuclear PPAs (Crane/TMI $1.6B, Kairos Hermes 2 500MW, Susquehanna/AWS 960MW), regulatory matrices (EnEfG, CRU, DC-CFA2, EU EED), facility case studies (Moro Hub, Verne Global, Lefdal, SINES, St. Ghislain, SolarNova, Microsoft DLC, NVIDIA DSX, Meta), and the full investigative taxonomy (Who/What/When/Where/Why/How).
**Missing from site:** NVIDIA DSX AI Factory (75% propylene glycol, 45°C return), Meta greenfield closed-loop campuses (WUE 0.20→0.0), Microsoft SolarNova Singapore (200 MWp PPA), Lefdal Mine Datacenter detail, the 30% BTM / 90% recent-announcement stat, supply-chain bottleneck thesis (transformers/switchgear as critical path), the full 4-vector macroeconomic outlook, and most inline source links.

---

## 2. Site Audit Summary (Local, All Pages)

| Page | Internal links in body | Inline citations | Bylines/dates | Issues |
|---|---|---|---|---|
| index.html | 3 (card footers) | 0 | none | Search only filters 3 cards; hero image OK; taxonomy table good but not linked to deep pages |
| facilities.html | 3 (card footers) | 0 | none | Table + 3 case cards; missing Lefdal/SolarNova/NVIDIA/Meta depth |
| cooling-tech.html | 0 | 0 | none | Calculator good; no links to facilities/regulations; missing NVIDIA DSX/Meta |
| regulations.html | 0 | 0 | none | **Duplicate `</html>` bug (lines 153-154)**; matrix good; no links to facilities/cooling |
| baseload-nuclear.html | 0 | 0 | none | Good narrative; no links to regulations/sources inline |
| sources.html | 0 (outbound 9) | n/a | none | Flat bibliography; no annotations/dates; no back-links from prose |

**Cross-cutting:** No breadcrumbs, no related-content, no og:image, no styled 404, canonicals use `.html` while clean URLs are canonical, GET /api/subscribe → 500, no rate limiting on subscribe, no analytics enabled.

---

## 3. Redesign Plan (Synthesis)

### Narrative architecture (the "complete story")
The site should read as one editorial publication with a clear arc:

1. **index.html — The Story Hub (pillar).** Longform narrative: "How AI rewired the data center" → power density → water crisis → closed-loop cooling → clean baseload → regulation. Each section ends with a contextual link into the deep-dive page. Sticky section nav + reading progress. Bylines, date, "last updated".
2. **facilities.html — The Directory.** Facility profiles as editorial case studies (not just a table): Moro Hub, Verne Global, Lefdal, SINES, St. Ghislain, SolarNova, Microsoft DLC, NVIDIA DSX, Meta. Each links to its source + related cooling/regulation pages.
3. **cooling-tech.html — The Engineering.** Thermodynamics narrative with the calculator embedded mid-article; links to facilities (who deploys this) and regulations (what mandates it).
4. **regulations.html — The Law.** Jurisdiction-by-jurisdiction narrative with the matrix as a reference table; links to facilities (who's affected) and cooling (what's mandated).
5. **baseload-nuclear.html — The Power.** Nuclear PPA narrative (Crane, Kairos, Susquehanna) with FERC docket citations inline; links to regulations (FERC jurisprudence) and facilities.
6. **sources.html — The Bibliography.** Annotated, dated, categorized source index — the *destination* of inline citations, not a standalone dump.

### Interlinking rules (SEO-standard)
- Every factual claim with a source gets an **inline citation link** → `sources.html#anchor`.
- Every page links to 2+ sibling pages with **descriptive anchor text** in prose (not "click here").
- Every page ends with a **"Related reading"** block (3 links).
- Breadcrumbs on every page.
- Canonicals, sitemap, feed, og:url all unified to **clean URLs** (`/facilities` not `/facilities.html`).

### Design system
- **DESIGN.md written and linted** (0 errors): warm paper palette, Source Serif 4 display + Source Sans 3 body + IBM Plex Mono figures, hairline rules, one green accent, editorial grid.
- Anti-slop: no gradients, no glassmorphism, no icon-topper cards, no equal-weight feature grids, no Inter default, no "Insights/Growth" labels. Bylines + dates everywhere.

### Technical fixes
- Fix duplicate `</html>` in regulations.html.
- Fix GET /api/subscribe → 405; add rate limiting + honeypot.
- Add styled 404 page; add og:image; add breadcrumbs; add related-content blocks.
- `html_handling`/`not_found_handling` in wrangler.toml; bump compatibility_date.
- Adopt `wrangler d1 migrations` + `preview_database_id` (follow-up).
- Enable Cloudflare Web Analytics (needs user's beacon token or auto-injection).

---

## 4. Acceptance Criteria

The redesign is done when:
1. The site reads as one coherent editorial narrative (index → deep dives → sources), not a pile of assets.
2. Sources are linked **in content** — every claim with a source has an inline citation; the bibliography is the destination, not the dump.
3. Every page has 2+ contextual internal links with descriptive anchor text + a related-reading block.
4. The slop diagnostic scores ≤3/10 (was ~7).
5. All technical bugs fixed (duplicate `</html>`, 405, 404 page, canonicals, og:image).
6. The research depth from the transcript (NVIDIA DSX, Meta, SolarNova, Lefdal, supply-chain thesis, 4-vector outlook) is restored into the narrative.
7. Verified locally (all pages 200, links resolve, no stale domains) and deployed live.
