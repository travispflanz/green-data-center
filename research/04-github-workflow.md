# GitHub Workflow — Should GreenCompute Move to GitHub + Push-to-Cloudflare?

*Research date: 2026-09-03. Verified against Cloudflare docs (Pages git integration, Workers CI/CD, rollbacks), wrangler-action README, GitHub docs.*

## The verdict: YES — move it to GitHub. Here's why, with receipts.

### 1. The native Pages GitHub integration works for your setup

Cloudflare Pages' native git integration connects a GitHub repo and auto-deploys on push, with **PR preview URLs** — verified: *"Every time you open a new pull request on your GitHub repository, Cloudflare Pages..."* (developers.cloudflare.com/pages/configuration/git-integration/github-integration). Your Workers-static-assets project with a custom `_worker.js` is the **Advanced Mode** equivalent — the docs confirm `_worker.js` is the Pages Functions advanced-mode entry point (developers.cloudflare.com/pages/functions/advanced-mode/). So the native integration is available.

**However** — your project is currently deployed as a **Workers service** (via `wrangler deploy`), not a Pages project. Two clean paths:

- **Path A (recommended): keep Workers, add GitHub Actions.** Use `cloudflare/wrangler-action@v4` (verified current major; 1,937 stars, actively maintained, last push 2026-07-29) to run `wrangler deploy` on push to `main`. This keeps your exact current architecture and adds CI.
- **Path B: convert to a Pages project** and use the native git integration (dashboard UI, PR previews, deploy history). More moving parts; the Workers path is simpler for a solo site.

### 2. The exact workflow (Path A)

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - name: Deploy Worker
        uses: cloudflare/wrangler-action@v4
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
      - name: Apply D1 migrations
        uses: cloudflare/wrangler-action@v4
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: d1 migrations apply greencompute-db --remote
```

Secrets: `CLOUDFLARE_API_TOKEN` (scoped: Workers Scripts:Edit + D1:Edit + Account:Read) and `CLOUDFLARE_ACCOUNT_ID` stored as GitHub Actions secrets (verified: `gh secret set` / Settings → Secrets → Actions). The D1 migration step is CI-safe — verified: *"When running the apply command in a CI/CD environment or another non-interactive command line, the confirmation step will be skipped."* (developers.cloudflare.com/d1/wrangler-commands)

**OIDC note**: wrangler-action OIDC auth is an open feature request (issue #402, discussion #435) — not yet supported. Use the API token secret for now.

### 3. Pros/cons matrix

| | Pros | Cons |
|---|---|---|
| **Offsite backup** | Repo lives on GitHub; local disk loss ≠ site loss | None |
| **Revert points** | Git tags/branches/reflog + Workers versions/rollbacks (dashboard: Deployments → select → rollback; verified docs) | None |
| **PR-based content workflow** | Content changes go through a reviewable PR; agent opens PRs, you approve | Slightly more ceremony than direct push |
| **CI build+deploy** | Push to main = deployed; no manual `wrangler deploy` | One more moving part (Actions) |
| **Portability** | Repo is the source of truth; can redeploy anywhere | — |
| **Secrets hygiene** | Tokens live in Actions secrets, not `.env` | Must not commit `.env` (already gitignored) |
| **Exposure** | Private repo = source stays private | Public repo = source visible (fine for a research hub, but private is safer) |

### 4. Repo hygiene checklist

- `.gitignore` already covers `.env` (verified). Add `.dev.vars` if you ever use local dev.
- `wrangler.toml` in the repo is fine — it contains no secrets (verified: account_id and D1 database_id are not secret).
- D1 migration files belong in the repo (`migrations/` dir, `wrangler d1 migrations apply`).
- Add an `AGENTS.md` (or `.hermes.md`) documenting the deploy workflow — Hermes auto-injects it into every session (verified in Hermes docs: context files).
- Never commit `state/`, `trials.db`, or any `.env.*` (your existing `.gitignore` handles this — keep it).

### 5. Rollback story (fastest recovery)

Three layers, fastest first:
1. **Cloudflare Workers versions + rollbacks** — dashboard: Deployments tab → select previous version → rollback. Instant, no redeploy. (Verified: developers.cloudflare.com/workers/versions-and-deployments/rollbacks/)
2. **Git revert + push** — reverts the content, CI redeploys. ~1-2 min.
3. **Git tags as release points** — tag each deploy (`v1.0.0`); `git checkout <tag>` + push restores any historical state.

### 6. Recommended setup for this case study

- **Private repo** (recommended): the site is a public research hub, but the source (including research notes and future unpublished work) stays private. You can make the README public later if you want a portfolio piece.
- **Branch strategy**: `main` = production (push = deploy). Content changes on short-lived branches → PR → merge → auto-deploy. The agent (Hermes) drives this via `gh` CLI: create branch, commit, push, open PR; you review and merge.
- **Tags**: `v1.0.0`, `v1.1.0`... at each meaningful release.

## 10-step migration plan

1. `gh auth login` (or `gh auth login --web`) — verify with `gh auth status`.
2. `gh repo create greencompute --private --source=. --push` (creates repo, pushes existing history — your 4 commits come along).
3. Verify: `git remote -v` shows origin; `gh repo view`.
4. Create `CLOUDFLARE_API_TOKEN` (scoped: Workers Scripts:Edit, D1:Edit, Account:Read) at dash.cloudflare.com/profile/api-tokens.
5. `gh secret set CLOUDFLARE_API_TOKEN` and `gh secret set CLOUDFLARE_ACCOUNT_ID` (value from `wrangler whoami` / wrangler.toml).
6. Add `.github/workflows/deploy.yml` (the file above).
7. Commit + push; watch the Actions run; verify the live site still 200s.
8. Add `AGENTS.md` documenting the workflow (deploy = push to main; D1 migrations auto-apply).
9. Tag the current state: `git tag v1.0.0 && git push --tags`.
10. Test a rollback: make a trivial change, deploy, then roll back via the dashboard Deployments tab — confirm you know how to undo.

## What this buys the case study

- **Cleanliness**: every change is a reviewed, versioned commit; the repo is the single source of truth.
- **Revert points**: git tags + Workers versions = three independent undo layers.
- **Agent-driven workflow**: Hermes opens PRs, you approve; the deploy is automatic and auditable.
- **Portability**: the same pattern (repo → CI → Cloudflare) scales to your future projects.

Sources: https://developers.cloudflare.com/pages/configuration/git-integration/github-integration , https://developers.cloudflare.com/pages/functions/advanced-mode/ , https://developers.cloudflare.com/workers/ci-cd/builds/ , https://github.com/cloudflare/wrangler-action , https://developers.cloudflare.com/workers/versions-and-deployments/rollbacks/ , https://developers.cloudflare.com/d1/wrangler-commands
