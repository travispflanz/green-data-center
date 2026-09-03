# Hermes Integration Surface — MCP Servers, CLIs, and Tools for Driving Cloudflare

*Research date: 2026-09-03. All claims verified against the actual GitHub repos, Hermes docs (hermes-agent.nousresearch.com), and the Hermes MCP catalog manifest.*

## The short answer

**You do not need to hand-configure anything.** Hermes ships a curated MCP catalog, and **Cloudflare is already in it**. The install is one command:

```
hermes mcp install cloudflare
```

It connects to Cloudflare's official remote MCP server (`https://mcp.cloudflare.com/mcp?codemode=false`), authenticates via OAuth 2.1 (browser flow, you pick which account permissions the agent gets), and exposes ~1,900 curated tools covering **DNS, Workers, R2, KV, D1, Queues, Pages, WAF, rulesets, tunnels, Access, Stream, Images, AI, Vectorize** — everything a small site needs. The catalog manifest (verified at `optional-mcps/cloudflare/manifest.yaml` in the hermes-agent repo) ships a curated exclude list for enterprise-only surfaces (Zero Trust org-fleet, Radar, Magic Transit, etc.), so you're not flooded with irrelevant tools.

## Verified state of the official Cloudflare MCP

- **Repo**: `cloudflare/mcp-server-cloudflare` — 4.1k stars, 489 forks, 385 commits, Apache-2.0, last push 2026-09-01 (actively maintained).
- **It has evolved**: the old local `npx @cloudflare/mcp-server-cloudflare` install is gone. It's now a **monorepo of remote Streamable-HTTP servers** at `*.mcp.cloudflare.com/mcp` (docs search, Workers bindings, observability, browser rendering, audit logs, Radar, etc.).
- **The main API server** lives at `mcp.cloudflare.com/mcp` (repo `cloudflare/mcp`, 797 stars). Two modes:
  - **Code Mode** (default): 3 meta-tools (`docs`, `search`, `execute`) — the agent writes JS that runs in a Cloudflare sandbox. Token-efficient (~1k tokens) but indirect.
  - **`?codemode=false`**: ~2,500 individual endpoint tools with real JSON schemas. The Hermes catalog pins this mode deliberately, because Hermes already has its own tool-search layer — stacking two search layers would be wasteful. (Verified in the manifest: *"With codemode=false the server registers each API endpoint as its own tool (~3,300 as of July 2026)... Calls go straight to the Cloudflare API; no sandbox indirection."*)
- **Auth**: OAuth 2.1 with PKCE (Hermes handles discovery, DCR, token exchange, refresh automatically — `auth: oauth` in config). Headless/CI alternative: `CLOUDFLARE_API_TOKEN` as a bearer header.
- **Tool naming**: `mcp__cloudflare__<tool>`; per-server filtering via `tools.include`/`tools.exclude` in `~/.hermes/config.yaml`.

## GitHub MCP: deliberately skipped — and that's correct

The user asked whether a "bypassed tool" (GitHub) matters. **Hermes' own docs answer this explicitly**: GitHub is deliberately **not** in the MCP catalog because *"its hosted MCP requires each client to bring its own OAuth app (generic dynamic client registration is rejected), and Hermes's bundled `github/*` skills driving the `gh` CLI are a more capable integration."*

The official `github/github-mcp-server` (32.7k stars, very mature) exists and supports repo/PR/issue/actions tools — but for driving a repo from Hermes, the `gh` CLI + bundled skills (`github-auth`, `github-pr-workflow`, `github-issue-to-pr`, etc.) are the documented, more capable path. **Verdict: skip the GitHub MCP; use the gh CLI skills.**

## Hugging Face angle

- HF hosts an official MCP server (`huggingface.co/mcp` — verified reachable; `mcp.huggingface.co` is dead). It's in the Hermes catalog as `hugging_face`.
- Relevance to this workflow: low. HF is for models/datasets; your site doesn't need them yet. If you later add Workers AI inference, models come from Cloudflare's catalog (which includes HF models) — no HF MCP needed.

## Comparison: MCP server vs wrangler CLI vs GitHub Actions

| Capability | Cloudflare MCP (Hermes) | wrangler CLI (terminal) | GitHub Actions |
|---|---|---|---|
| Query D1 | ✅ `d1 execute`-style tools | ✅ `wrangler d1 execute` | ✅ via workflow |
| Deploy | ✅ Workers API tools | ✅ `wrangler deploy` | ✅ `wrangler-action@v4` |
| Rollback | ✅ versions/rollbacks tools | ✅ `wrangler versions deploy` | ✅ via workflow |
| Auth friction | OAuth once, browser | Token in `.env` | Secrets in repo |
| Determinism | Natural-language (agent decides) | Exact commands | Exact, repeatable |
| Risk | Agent could mutate anything (filter tools!) | Same as MCP | Gated by branch rules |
| Best for | Ad-hoc ops, DB queries, debugging | Scripted deploys, migrations | Push-to-deploy, PR previews |

**Verdict**: use all three for different jobs — MCP for interactive ops (query the DB, check a Worker), CLI for scripted deploys, GitHub Actions for the push-to-deploy pipeline. They don't conflict; the MCP server literally wraps the same Cloudflare API the CLI uses.

## What Hermes already has (verified in `~/.hermes/config.yaml`)

6 MCP servers configured: Context7, Tavily, claude-code-docs, sequentialthinking, codebase-memory-mcp, agent-reach. **No Cloudflare, no GitHub** — the two gaps this research fills. Adding Cloudflare = `hermes mcp install cloudflare` + restart. Adding GitHub = nothing (gh CLI skills already bundled).

## Hermes features that matter for this workflow (verified in docs)

- **Remote HTTP MCP support**: `url:` + `headers:` + `auth: oauth` in `mcp_servers` — Cloudflare's remote servers connect directly.
- **`/reload-mcp`** — reload MCP config without restarting.
- **Webhooks**: Hermes can receive GitHub events (push, PR) to trigger agent runs — a future "content change → agent reviews → deploys" loop.
- **Git worktrees**: run multiple Hermes agents safely on the same repo.
- **Checkpoints & rollback**: Hermes has filesystem safety nets (shadow git repos, snapshots) for destructive operations.
- **Context files**: `AGENTS.md`/`.hermes.md` in the repo are auto-injected into every conversation — the right place to document the deploy workflow for future agent sessions.

Sources: https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp , https://hermes-agent.nousresearch.com/docs/reference/mcp-config-reference , https://github.com/cloudflare/mcp-server-cloudflare , https://github.com/cloudflare/mcp , https://github.com/github/github-mcp-server , https://github.com/NousResearch/hermes-agent/tree/main/optional-mcps/cloudflare
