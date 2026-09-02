# Green Data Center — Post-Import Evaluation & Advancement Plan

*Prepared by Hermes Agent after full-fidelity import of Gemini session `533c4962a18148c1` (2026-09-02).*

---

## 1. Import Fidelity — Verified

| Claim | Verification |
|---|---|
| 16 turns captured (8 user + 8 model) | ✅ `clean-session.jsonl` — sequential near-duplicate merge of 24 raw records |
| Full text, verbatim | ✅ `transcript-full.md` (379 KB); final message is Gemini's own 95.8 KB session archive |
| Code blocks | ✅ 25 blocks extracted in order to `code/msgNN_blockNN.txt` |
| Thinking / reasoning traces | ✅ Checked DOM exhaustively — **no "Show thinking" expanders exist in this session** (Gemini didn't expose them for this model/config); nothing lost |
| Images | ✅ 1 image message (the user's error screenshot) preserved; all site images are Wikimedia-hosted with attribution |
| Research sources | ✅ Embedded in messages (sitemap, worker URL, Wikimedia/Commons, Cloudflare Dashboard); `sources.md` lists unique links |
| **Reconstructed site vs. live deployment** | ✅ `index.html` **byte-identical** (md5 match) to `greencompute-site.travis-097.workers.dev` |
| Live site still up | ✅ HTTP 200, 11,900 bytes |

**Fidelity verdict: literal, not summarized.** The one caveat — see Finding 1 below.

---

## 2. What This Session Actually Built

A **publication-grade static research site** ("GreenCompute DB") on the sustainable data center / AI-infrastructure intersection:

- **6 pages**: `index.html` (investigative taxonomy hub + client search), `facilities.html` (Moro Hub, Microsoft sealed builds, Verne Global, SINES, Google St. Ghislain), `cooling-tech.html` (thermodynamics + interactive calculator), `regulations.html` (EnEfG §11, CRU LEU, DC-CFA2, EU EED 2023/1791), `baseload-nuclear.html` (TMI restart, FERC ER24-2172, Kairos SMRs), `sources.html`
- **Stack**: static semantic HTML5 + vanilla CSS (Swiss/editorial design system), Cloudflare Pages **Advanced Mode** `_worker.js` + **D1** SQL (`schema.sql`), newsletter endpoint `/api/subscribe`, security headers via `_headers`, sitemap/robots
- **AI maintainability**: `AI_GUIDE.md` SOP so LLM agents can extend the site safely
- **Workflow**: Gemini iterated 3× — v1 production codebase → `build_zip.py` one-click zip (after user refused to copy 12+ files) → Cloudflare warning repair → user deployed, found 5 live bugs → Gemini repaired (broken images, raw LaTeX, missing theme toggle, missing search, clean-URL 404s) → final expanded redesign

**Deployment history**: `greencompute-site.travis-097.workers.dev` (live, verified) → canonical URL in code still says `sustainable-dc.pages.dev` (user "will wait on a domain name").

---

## 3. Strengths (Grounded in the Content)

1. **Factually current** — IEA's 945 TWh by 2030 base case is confirmed by the IEA's own *Energy and AI* report; the session's regulatory citations (EnEfG, CRU, EU EED) are real statutes.
2. **Zero-dependency architecture** — no frameworks, no third-party JS, no cookies/trackers; CSP, HSTS, nosniff, Referrer-Policy all set. Fast and privacy-forward.
3. **Cost: $0** — Cloudflare free tier (D1: 5M reads/day + 5GB; Pages: unlimited bandwidth) is the correct platform choice for this use case.
4. **Editorial design direction** — CarbonPlan / Our World in Data / IEEE Spectrum-inspired Swiss grid, dark-mode engine with flash-prevention, real search.
5. **Self-documenting AI SOP** — the AI_GUIDE makes the site maintainable by agents (including this one) without tribal knowledge.
6. **The builder pattern** — `build_zip.py` is a neat "single artifact" delivery trick that avoided 12 file copies.

---

## 4. Findings & Fidelity Gaps

1. **⚠️ AI_GUIDE truncation in the shipped zip** — the build script's embedded `AI_GUIDE.md` is a 1.2 KB condensed SOP; the full 11.2 KB protocol Gemini wrote in message 1 was **not** carried into the zip. Restored here as `site/AI_GUIDE-full.md` + `./AI_GUIDE.md`. Action: push full version to the deployed site.
2. **Canonical URL mismatch** — code says `sustainable-dc.pages.dev`, live deployment is `greencompute-site.travis-097.workers.dev`. Sitemap/robots/canonical all point at the unclaimed domain → SEO split. Action: pick the real domain now (Cloudflare Pages custom domain or the worker URL) and update all 3 files.
3. **`greencompute-db.pages.dev` returns 000** — referenced in the archive as the D1-backed target; not currently deployed. Either deploy it or remove the reference.
4. **No analytics** — by design (privacy), but there's zero visibility into traffic, search usage, or newsletter conversion. Cloudflare Web Analytics is cookieless and free — can be added without violating the no-tracker ethos.
5. **Math without KaTeX** — message 13 says "KaTeX loaded as an enhancement"; the final `_headers` CSP allows `cdn.jsdelivr.net`, but need to verify KaTeX is actually linked in `cooling-tech.html` (the repaired semantic fractions work without it, but the enhancement matters for the calculator page).
6. **Newsletter is collect-only** — D1 table stores emails, but no double-opt-in, no unsubscribe, no send mechanism. Legal risk (GDPR/CAN-SPAM) + user said "I'll decide on integration later."
7. **All site content is in HTML tables/cards** — no structured data (schema.org/JSON-LD), no OG/Twitter cards, no RSS. Limits SEO surface and sharing.

---

## 5. Research-Backed Advancement Suggestions

### Tier 1 — Do now (low effort, high leverage)
| # | Suggestion | Why | Evidence |
|---|---|---|---|
| A1 | Resolve canonical domain; update sitemap/robots/canonical in all files; redeploy | Fixes SEO split; one real URL | Finding 2 |
| A2 | Restore full `AI_GUIDE.md` to deployed zip | Agent-maintainability is the site's core selling point | Finding 1 |
| A3 | Add Cloudflare Web Analytics (cookieless) | Traffic + search + newsletter visibility without privacy tradeoff | Cloudflare free tier |
| A4 | Verify KaTeX on `cooling-tech.html`; add JSON-LD `TechArticle`/`Dataset` to all pages | Math rendering + rich search snippets | Finding 5, 7 |

### Tier 2 — This quarter (medium)
| # | Suggestion | Why |
|---|---|---|
| B1 | Move to a **content pipeline**: keep the Markdown research docs (this project's `transcript/` + a `content/` folder) as source of truth, generate HTML from templates — no more hand-editing 6 HTML files (SOP becomes "edit content, run build") | Removes the exact pain point the AI_GUIDE tries to manage |
| B2 | RSS/Atom feed + newsletter integration (Buttondown, Beehiiv, or MailChannels free SMTP from Workers) | The collected emails become an audience; feed helps citations |
| B3 | Add interactive data (D1): page-view counters, facility lookup table, "compare jurisdictions" | Turns static research into a living database — user already chose D1 |
| B4 | Accessibility audit (axe) + contrast pass on dark theme | Institutional-research credibility; cheap wins |
| B5 | Image pipeline: migrate Wikimedia hotlinks to R2 or local assets with `loading=lazy` + width/height (CLS fix) | Wikimedia thumbnails already 404'd once (msg 13); R2 is free egress |

### Tier 3 — Strategic
| # | Suggestion | Why |
|---|---|---|
| C1 | **Hermes integration**: this project now has the full transcript + SOP; wire a Hermes cron to check IEA/press for new data-center stories monthly and propose new facility/statute cards via kanban | The AI_GUIDE SOP was written for exactly this — Hermes is the agent that can run it |
| C2 | GitHub repo + Cloudflare Git integration → auto-deploy on push; `build_zip.py` becomes `wrangler deploy` | One-command deploys, version history (repo also backs up this import) |
| C3 | Add a "research method" page + methodology transparency (sources linked per claim) | Distinguishes from AI-generated slop; builds authority |
| C4 | Consider `baseload-nuclear.html` → section expansion: SMR licensing tracker (NRC dockets) with D1 table | High-search-value niche, matches the taxonomy |

---

## 6. Integration with Hermes

- **Already done**: project `green-data-center` (p_436fed59) registered with Obsidian vault `_index.md`, `project-manifest.md` (kind: website-static, runtime: cloud-pages, deploy: Cloudflare Pages + D1), kanban board `green-data-center`, git-initialized primary folder.
- **Proposed**: monthly "green data center watch" cron → kanban card → Hermes executes SOP edits → wrangler deploy. The AI_GUIDE.md in this repo is the exact playbook.

---

## 7. Recommended Next Actions (Kanban-ready)

1. Fix canonical URL + redeploy (A1)
2. Push full AI_GUIDE.md (A2)
3. Add Cloudflare Web Analytics + verify KaTeX (A3, A4)
4. Decide newsletter integration (B2) — user deferred; recommend Buttondown for simplicity
5. Set up GitHub + auto-deploy (C2)
6. Schedule monthly content watch (C1)

*Full session content: `transcript/transcript-full.md`, `transcript/clean-session.jsonl`, `code/`, `site/`.*
