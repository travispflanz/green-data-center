# GreenCompute — Cloudflare Platform Case Study (Research Phase)

*Phase 1 deliverable: platform logistics, real-world experience, Hermes integration surface, and GitHub workflow evaluation for the GreenCompute Research site (`greencompute-site.travis-097.workers.dev`). Research date: 2026-09-03.*

## Reports

| File | What it covers |
|---|---|
| [01-platform-mechanics.md](01-platform-mechanics.md) | How the deployment actually works (Workers static-assets mode), per-page HTML proof, D1 database-driven patterns, exact free-tier limits, the compatibility-date gotcha |
| [02-community-experience.md](02-community-experience.md) | Real-world Reddit/HN/blog/YouTube findings with verbatim quotes — cache pain, D1 in production, platform comparisons, individual voices |
| [03-hermes-integration.md](03-hermes-integration.md) | MCP servers / CLIs / CI actions for driving Cloudflare from Hermes — the Cloudflare MCP catalog entry, GitHub MCP verdict, comparison table |
| [04-github-workflow.md](04-github-workflow.md) | GitHub hosting + push-to-Cloudflare playbook — verdict, exact workflow YAML, pros/cons, rollback story, 10-step migration plan |

## Key conclusions (summary)

1. **Architecture**: Workers static-assets mode — each page is its own HTML file; D1 powers the newsletter API. This is the community-validated sweet spot for a small content site.
2. **Database-driven**: already partly true (newsletter → D1); the ladder to more is cheap (HTMLRewriter → edge framework).
3. **Hermes integration**: `hermes mcp install cloudflare` (one command, OAuth, ~1,900 curated tools). GitHub MCP deliberately skipped — gh CLI skills are the documented better path.
4. **GitHub**: yes — private repo + `wrangler-action@v4` CI + tags + Workers rollbacks = cleanliness, revert points, and an agent-driven PR workflow.
5. **Next phase**: content research (deferred per user), plus the high-value add-ons from AI_GUIDE (Web Analytics, Turnstile, custom domain).

*All load-bearing claims verified against fetched documentation, the live site, or the actual repos — see per-file source lists.*
