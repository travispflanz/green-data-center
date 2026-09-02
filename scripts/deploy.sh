#!/usr/bin/env bash
# GreenCompute DB — one-command Cloudflare deploy
#
# Usage:
#   ./scripts/deploy.sh             build zip + deploy to Cloudflare Workers
#   ./scripts/deploy.sh --dry-run   build zip + validate only (no push)
#
# Prereqs (one-time):
#   npx wrangler login        OR   export CLOUDFLARE_API_TOKEN=<token>
#   account_id filled into wrangler.toml (run `npx wrangler whoami`)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SITE_DIR="$ROOT/site"
DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then DRY_RUN=1; fi

echo "▶ GreenCompute deploy — site dir: $SITE_DIR"

# 1. Validate required files
echo "▶ Validating site..."
REQUIRED=(index.html facilities.html cooling-tech.html regulations.html baseload-nuclear.html sources.html styles.css _worker.js _headers schema.sql sitemap.xml robots.txt feed.xml newsletter.js AI_GUIDE.md)
for f in "${REQUIRED[@]}"; do
  if [[ ! -f "$SITE_DIR/$f" ]]; then
    echo "✗ Missing required file: $f"; exit 1
  fi
done

# 2. Image URL check: every wikimedia <img src> must return HTTP 200
echo "▶ Checking Wikimedia image URLs..."
BAD_IMG=0
while IFS= read -r url; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -L --max-time 15 "$url")
  if [[ "$code" != "200" ]]; then
    echo "✗ Broken image ($code): $url"; BAD_IMG=1
  fi
done < <(grep -oh 'https://upload\.wikimedia\.org[^"]*' "$SITE_DIR"/*.html | sort -u || true)
if [[ "$BAD_IMG" -eq 1 ]]; then
  echo "✗ One or more Wikimedia images are broken — refusing to deploy."
  exit 1
fi
echo "✓ Images OK"

# 3. Canonical consistency
if grep -rl 'sustainable-dc\.pages\.dev' "$SITE_DIR" --include="*.html" --include="*.xml" --include="*.txt" >/dev/null 2>&1; then
  echo "✗ Stale canonical domain (sustainable-dc.pages.dev) still present in:"
  grep -rl 'sustainable-dc\.pages\.dev' "$SITE_DIR" || true
  exit 1
fi
echo "✓ Canonical domain consistent"

# 4. Build the export zip (source of truth = site/ directory)
echo "▶ Building greencompute-site.zip..."
python3 "$SITE_DIR/build_zip.py" "$ROOT/greencompute-site.zip"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "✓ Dry run passed — no deployment performed."
  exit 0
fi

# 5. Deploy
echo "▶ Deploying to Cloudflare (service: greencompute-site)..."
if ! command -v npx >/dev/null 2>&1; then
  echo "✗ npx not found — install Node.js or run wrangler directly."; exit 1
fi
npx --yes wrangler deploy --config "$ROOT/wrangler.toml"

echo "✓ Deployed. Live: https://greencompute-site.travis-097.workers.dev/"
