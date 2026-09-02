# AI Maintenance & Operations Manual (SOP)

This document provides system rules and standard operating procedures for AI agents maintaining the **GreenCompute DB** repository on Cloudflare Pages/Workers.

## 1. Core Architecture
- **Framework**: Static semantic HTML5, vanilla CSS (`styles.css`), and vanilla JavaScript.
- **Backend**: Cloudflare Pages Advanced Mode via root `_worker.js` connected to Cloudflare D1 SQL database (`schema.sql`).
- **Styling Rules**: Maintain the Swiss-editorial layout using CSS custom variables defined in `:root` and `[data-theme="dark"]`. Do not introduce bloated external JS frameworks.

## 2. Standard Operating Procedures (SOPs)

### SOP 1: Adding a New Facility to `facilities.html`
1. Add a new row to the table in `facilities.html` matching existing column scopes.
2. If detailed coverage is warranted, add an `<article class="article-card">` under the case studies grid.
3. Register supporting links in `sources.html` and update `<lastmod>` in `sitemap.xml`.

### SOP 2: Amending Regulatory Codes in `regulations.html`
1. Update the corresponding row in the summary matrix table.
2. Update the statute cards.
3. Ensure links point directly to official government bodies (e.g., `gesetze-im-internet.de`, `eur-lex.europa.eu`).