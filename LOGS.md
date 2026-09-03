# GreenCompute — Where The Logs Live

**Short answer: everything below is a real, current log location. Nothing was destroyed.**
What *was* deleted: throwaway `/tmp/hermes-verify-*.py` scripts and `/tmp/wrangler-dev.log`
(a live debug log I treated as disposable during the 404 fix — that was a mistake, and is
why this project now has its own `logs/` dir + tee'd scripts. See "Project logs" below.)

## Project logs (this repo — the primary place to look)

| What | Where |
|---|---|
| Deploy runs | `logs/deploy-YYYYMMDD-HHMMSS.log` (+ `logs/deploy-latest.log` symlink) |
| Live verification runs | `logs/verify-YYYYMMDD-HHMMSS.log` (+ `logs/verify-latest.log` symlink) |
| How to run | `./scripts/deploy.sh` (auto-tees) · `./scripts/verify-live.sh` (auto-tees) |

`logs/` is gitignored (generated artifacts), so it will not clutter commits — but it lives
in the repo tree, so it survives and is always one `ls logs/` away.

## Cloudflare / wrangler logs

| What | Where | Notes |
|---|---|---|
| Wrangler's own log | `~/.config/.wrangler/logs/wrangler-*.log` | 31 files; one per wrangler invocation (login, deploy, dev). This is where `invalid_state` OAuth errors were confirmed. |
| Deployments (production) | `npx wrangler deployments list` | Every published version, by ID + timestamp. Version `d4f81764` is the live one. |
| Live runtime | Cloudflare dashboard → Workers → greencompute-site → **Logs** | Real request logs; requires dashboard login. |
| D1 query log | `npx wrangler d1 execute greencompute-db --remote --command "SELECT * FROM subscribers"` | Newsletter DB contents. |

## Git history (the change log)

`git log --oneline` — every state change is here: `21f4810` (re-eval) → `d0d8a25` (verify) →
`72bebe3` (deploy live) → `5b02124` (D1) → `a90ea64` (cache headers) → `d16c8d0` (editorial redesign).
`git show <commit>` for the full diff of any change.

## Hermes-side logs (research/delegation — where the 8 research agents ran)

| What | Where |
|---|---|
| Subagent live logs | `~/.hermes/cache/delegation/live/deleg_05b5d65b/task-{0..7}.log` |
| Delegation summary | `~/.hermes/cache/delegation/subagent-summary-0-20260902_214832_422758.txt` |
| Session transcripts | Hermes desktop → session history; or `session_search` |

## How the 404 bug was actually diagnosed (proof the logs were used)

1. `wrangler deployments list` → confirmed old version was live (silent deploy failures).
2. `wrangler dev --local` + hitting unknown path → reproduced 500 locally.
3. `/tmp/wrangler-dev.log` (now replaced by `logs/`) → exception text: `env.ASSETS` undefined.
4. Root cause: `wrangler.toml` assets config missing `binding = "ASSETS"`.
5. Fix shipped in `d16c8d0`; verified live: unknown path → 404, all routes 200, POST 200.

## Maintenance rule (kept from now on)

- Every deploy and every verification **tees to `logs/`** — nothing is discarded.
- If a debug log needs to exist, it gets a real path under `logs/` — never just `/tmp`.
- `verify-live.sh` is the permanent replacement for the deleted ad-hoc scripts.
