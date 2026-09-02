The AI Maintenance & Operations Protocol (AI_GUIDE.md)

To enable any Large Language Model (LLM) or AI agent to maintain, update, and scale the static website on Cloudflare Pages without corrupting semantic structure, SEO authority, or internal link equity, the following protocol should be placed in the repository root as AI_GUIDE.md (or .cursorrules / CLAUDE.md).

1. Site Architecture & Directory Conventions
/
├── index.html               # Topic pillar hub; overview and primary navigation
├── facilities.html          # Global facility directory (solar, wind, zero-water, closed-loop)
├── cooling-tech.html        # Engineering and thermodynamic deep-dives (PUE/WUE, DLC, dry coolers)
├── regulations.html         # Comparative legal analyses (Germany, Singapore, Ireland, EU, US)
├── baseload-nuclear.html    # Baseload power, SMRs, behind-the-meter colocation, and FERC dockets
├── sources.html             # Master bibliography with direct statutory, regulatory, and press links
├── styles.css               # Core CSS variables and utility classes (zero heavy frameworks)
├── sitemap.xml              # XML index of canonical URLs
├── robots.txt               # Crawler directives
├── _headers                 # Cloudflare edge security and cache control headers
└── AI_GUIDE.md              # System prompt and operational checklist for AI agents

2. Standard Operating Procedures (SOPs) for AI Agents
SOP 1: Adding a New Facility to facilities.html

When instructed to add a newly announced or operational data center:

Locate Target Section: Insert the new entry into <section id="facility-directory"> within the appropriate categorical container (e.g., <!-- Category: 100% Solar / Wind --> or <!-- Category: Closed-Loop / Zero-Water -->).

Apply Semantic Card Markup: Use the standardized card template:

HTML
<article class="facility-card" id="facility-[slug]">
  <header>
    <span class="badge badge-renewable">[Energy Vector: e.g., 100% Solar]</span>
    <span class="badge badge-cooling">[Cooling Vector: e.g., Closed-Loop DLC]</span>
    <h3>[Facility / Campus Name]</h3>
    <p class="facility-meta">[City, Country] | Operator: [Company Name]</p>
  </header>
  <div class="facility-specs">
    <ul>
      <li><strong>Power Capacity:</strong> [X MW / GW IT Load]</li>
      <li><strong>PUE / WUE:</strong> [PUE ≤ X.XX] | [WUE = 0.0 L/kWh]</li>
      <li><strong>Cooling Technology:</strong> [Direct-to-Chip cold plates, exterior dry coolers]</li>
      <li><strong>Interconnection / PPA:</strong> [Behind-the-Meter / Dedicated PPA details]</li>
    </ul>
    <p>[2–3 concise sentences summarizing infrastructure innovations, grid interface, and community impact.]</p>
  </div>
  <footer>
    <a href="sources.html#[source-slug]" class="source-link">Inspect Official Documentation →</a>
  </footer>
</article>


Register Primary Source: Open sources.html and append an entry in the matching category (<!-- Category: Infrastructure Whitepapers & Press Releases -->) with the exact link, title, publication date, and archival status.

Update Aggregated Counters: If index.html or facilities.html maintains summary stats (e.g., "Tracking X Zero-Water Facilities"), increment the integer count.

SOP 2: Adding or Amending Legislation in regulations.html

When updating an existing statute (e.g., revisions to Germany’s Energieeffizienzgesetz) or adding a new jurisdiction:

Update Comparison Matrix: Update the summary table on regulations.html. Retain single-space Markdown or standard HTML <table> cells with <th scope="row"> for jurisdiction names.

Add/Edit the Statute Section:

HTML
<section class="statute-block" id="policy-[country-slug]">
  <h3>[Country]: [Official Name of Law / Regulation]</h3>
  <p class="legal-citation">Enacted: [Date] | Governing Agency: [Ministry / Utility Commission]</p>
  <div class="mandate-grid">
    <div class="mandate-item">
      <h4>Renewable Mandate</h4>
      <p>[Specific % targets and compliance deadlines, e.g., 100% renewable electricity by 2027/2030]</p>
    </div>
    <div class="mandate-item">
      <h4>Cooling & PUE Caps</h4>
      <p>[Statutory PUE limits, e.g., PUE ≤ 1.2 for new builds]</p>
    </div>
    <div class="mandate-item">
      <h4>Waste Heat Reuse</h4>
      <p>[Mandatory export quotas and connection criteria]</p>
    </div>
  </div>
  <p class="regulatory-analysis">[Legal breakdown, enforcement mechanisms, and practical hurdles.]</p>
  <p><a href="[Direct Official Government URL]" target="_blank" rel="noopener" class="statutory-link">Read Statutory Text on [Official Government Portal] ↗</a></p>
</section>


Update Schema Markup: Update the Legislation or GovernmentService JSON-LD script block on regulations.html.

Cross-Link to Cooling/Baseload: If the law mandates waste heat reuse, add an inline cross-link pointing to cooling-tech.html#heat-reuse.

SOP 3: Maintaining Site-Wide SEO & Internal PageRank

Whenever modifying any page:

Canonical Validation: Ensure <link rel="canonical" href="https://[domain]/[page].html"> is preserved and points to the clean production URL.

Open Graph / Meta Tags: Verify <meta name="description"> remains between 140 and 160 characters and aligns with target long-tail keywords.

No Broken Links: Never delete an anchor ID without redirecting or updating references in other files.

Contextual Internal Linking: When mentioning technical concepts on any page, use keyword-rich anchor text:

For "closed-loop dry coolers" → link to cooling-tech.html#dry-coolers.

For "German EnEfG requirements" → link to regulations.html#germany-enefg.

For "FERC co-location rulings" → link to baseload-nuclear.html#ferc-dockets.

Update sitemap.xml: Update the <lastmod> tag for any modified file to the current date (YYYY-MM-DD).

3. Strict Development Rules for AI Agents

Semantic HTML First: Use <header>, <nav>, <main>, <article>, <section>, <aside>, and <footer>. Never nest entire pages inside meaningless <div> wrappers.

Zero Heavy Frameworks: Do not introduce React, Vue, jQuery, or bloated CSS frameworks. Keep styles in styles.css using modern CSS grid, flexbox, and CSS custom properties (variables).

Link Integrity:

External links MUST have target="_blank" rel="noopener" (use rel="noopener follow" for primary government, academic, and major news portals to maximize topical authority signals).

Internal links MUST use relative or root-relative paths (href="cooling-tech.html#direct-to-chip"), never absolute localhost or placeholder links (href="#" is forbidden).

Table Accessibility: Format all comparison tables using <thead>, <tbody>, <th scope="col">, and <th scope="row">.

Evolution of the Guide: Pre-Build vs. Post-Build

The instructions provided to an AI must evolve as the repository shifts from conceptual planning to concrete code:

Dimension	Pre-Build Phase (Current)	Post-Build Phase (Live Repository)
Selectors & Styling	Abstract CSS guidelines ("use modern variables and cards").	Explicit class names and utility tokens (e.g., .facility-card, .badge-solar, --color-accent-teal).
DOM IDs & Anchors	Conceptual anchors (e.g., #germany-policy).	Fixed anchor registry (e.g., #de-enefg-s11, #us-ferc-er24-2172, #cooling-dlc-flow).
JSON-LD Schema	Schema recommendations (FAQPage, Legislation).	Exact JSON-LD structures already embedded in <head> requiring only node-level appends.
Verification Tasks	Theoretical link validation.	Concrete validation script (e.g., running a headless crawler or link checker script before Git commit).
Site Map	Abstract URL list.	Hardcoded XML entries where only the <lastmod> timestamp and new <url> tags are adjusted.
Recommended High-Value Add-Ons and Integrations

For a high-impact, static platform hosted on Cloudflare Pages, these lightweight integrations maximize visitor utility and owner visibility without introducing heavy database overhead:

1. Static In-Browser Search (Pagefind)

What it is: An open-source, fully static search library engineered specifically for static sites.

Why it fits: It runs zero server-side code. During deployment, Pagefind builds a static indexing dictionary (typically under 50 KB). Visitors get instantaneous, typo-tolerant, full-text search across all statutes, engineering whitepapers, and facilities.

Implementation: Add an empty <div id="search"></div> and load Pagefind’s static JS/CSS via two lightweight tags.

2. Interactive PUE & WUE Impact Calculator

What it is: A vanilla JavaScript calculator embedded directly into cooling-tech.html or index.html.

Visitor Utility: Users can move sliders for Compute IT Load (MW), Operating Ambient Temperature, and Cooling Architecture (Evaporative Towers vs. Direct-to-Chip Dry Coolers) to calculate:

Annual estimated water consumption (Millions of Gallons / Megaliters).

Net water conserved per year (e.g., demonstrating how closed loops eliminate 125+ million liters of annual evaporative loss).  

Power Usage Effectiveness (PUE) vs. Water Usage Effectiveness (WUE) trade-off curves.

Owner Benefit: High engagement rate, prolonged dwell time, and natural backlink generation from journalists and infrastructure analysts looking for interactive modeling tools.

3. Zero-Cookie Edge Analytics (Cloudflare Web Analytics)

What it is: Cloudflare’s privacy-preserving, edge-rendered analytics engine.

Why it fits: It requires no cookie consent banners (GDPR-compliant out of the box), introduces zero client-side latency, and records authentic visits while filtering out scraper bots.

Owner Benefit: Accurate visibility into search traffic, visitor referrers, and most-read case studies without degrading Google PageSpeed scores.

4. Verified Legal Status Badges & Last-Checked Flags

What it is: A visual indicator attached to each regulatory policy section (e.g., Status: Enacted (In Force), Status: Proposed Revision Pending Parliamentary Review).

Why it fits: Energy legislation changes rapidly (e.g., pending revisions to the German EnEfG thresholds or regional FERC interconnection proceedings).  

Visitor Utility: Establishes high journalistic credibility by showing the exact date an attorney or researcher verified the docket status.

5. Syndication Feed (feed.xml)

What it is: A standard RSS/Atom XML feed located at /feed.xml.

Why it fits: Industry analysts, sustainability officers, and journalists rely on RSS readers to track policy updates and new greenfield data center approvals.

Owner Benefit: Automated content distribution to industry trackers and newsletter aggregators without requiring an active email marketing platform.

6. Theme Engine (Automatic Light / Dark Mode)

What it is: A 15-line vanilla CSS and JavaScript script that respects the user’s operating system preferences (prefers-color-scheme) with a manual toggle switch in the header.

Why it fits: Technical audiences and engineers frequently prefer dark backgrounds for reading dense engineering diagrams and legal matrices.

Production File Generation Readiness

With the architectural blueprint, the AI operations protocol, and the integration stack finalized, the next step is building the actual code files (index.html, facilities.html, cooling-tech.html, regulations.html, baseload-nuclear.html, sources.html, styles.css, _headers, and sitemap.xml) for immediate deployment to Cloudflare Pages.