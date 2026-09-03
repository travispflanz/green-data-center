#!/usr/bin/env bash
# GreenCompute — live production verification (the thing that used to live in
# throwaway /tmp scripts and got deleted). Run after every deploy:
#   ./scripts/verify-live.sh
# Every check is printed with PASS/FAIL; exits nonzero if anything fails.
# Full output is ALSO appended to logs/verify-<timestamp>.log via tee.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGS_DIR="$ROOT/logs"
B="https://greencompute-site.travis-097.workers.dev"

mkdir -p "$LOGS_DIR"
LOG_FILE="$LOGS_DIR/verify-$(date +%Y%m%d-%H%M%S).log"
if [[ -z "${GREENCOMPUTE_TEE_DONE:-}" ]]; then
  GREENCOMPUTE_TEE_DONE=1 exec > >(tee -a "$LOG_FILE") 2>&1
fi
ln -sfn "$(basename "$LOG_FILE")" "$LOGS_DIR/verify-latest.log"
echo "▶ Verify log: $LOG_FILE"

fail=0
check() { # check <label> <expected_code> <path>
  local code
  code=$(curl -s -m 15 -o /dev/null -w "%{http_code}" "$B$3" 2>/dev/null)
  if [[ "$code" == "$2" ]]; then
    echo "[PASS] $1 ($3 -> $code)"
  else
    echo "[FAIL] $1 ($3 -> $code, expected $2)"
    fail=1
  fi
}

echo "=== Live route checks ==="
check "homepage"                200 "/"
check "facilities (clean URL)"  200 "/facilities"
check "cooling-tech (clean URL)" 200 "/cooling-tech"
check "regulations (clean URL)" 200 "/regulations"
check "baseload-nuclear"        200 "/baseload-nuclear"
check "sources (clean URL)"     200 "/sources"
check "feed.xml"                200 "/feed.xml"
check "GET /api/subscribe rejects" 405 "/api/subscribe"
check "unknown path -> styled 404" 404 "/this-page-does-not-exist"
check "dev tool build_zip.py blocked" 404 "/build_zip.py"
check "dev tool AI_GUIDE-full.md blocked" 404 "/AI_GUIDE-full.md"

echo "=== 404 page actually styled (not bare 1101) ==="
if curl -s -m 15 "$B/this-page-does-not-exist" | grep -q "This page doesn't exist"; then
  echo "[PASS] styled 404 content served"
else
  echo "[FAIL] 404 body missing expected content"
  fail=1
fi

echo "=== Newsletter POST round-trip (D1) ==="
resp=$(curl -s -m 15 -X POST "$B/api/subscribe" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"verify-$(date +%s)@greencompute.dev\"}")
if echo "$resp" | grep -q '"success":true'; then
  echo "[PASS] D1 subscribe accepted"
else
  echo "[FAIL] D1 subscribe: $resp"
  fail=1
fi

echo
if [[ "$fail" -eq 0 ]]; then
  echo "===== ALL CHECKS PASSED ====="
else
  echo "===== ${fail} CHECK(S) FAILED — see log above ====="
fi
exit "$fail"
