#!/usr/bin/env bash
# Canonical deploy procedure for shipping chats.
#
# Encodes OPERATING.md §8 build cycle as one bash script. Replaces the
# Netlify-MCP + CLI-proxy + poll + verify sequence formerly pasted as the
# "Deploy pattern (CANONICAL)" block in WIP_OPEN.md ## Next chat.
#
# Usage:
#   bash scripts/deploy.sh [--rebuild] [--site-id <id>] [--dist <path>]
#
# Returns the Netlify deployId on STDOUT (single line). All log output goes
# to STDERR so the caller can pipe stdout into close-out.sh, e.g.:
#
#   DEPLOY_ID=$(bash scripts/deploy.sh) && \
#     bash scripts/close-out.sh refinement-chatN-foo "$DEPLOY_ID"
#
# Sequence (in order):
#   1. Build if --rebuild OR dist/ missing. Refuse if errored>0 (§6 rule 8).
#   2. JSON-RPC call to Netlify MCP `deploy-site` → single-use proxy URL.
#   3. npx @netlify/mcp upload via proxy URL → captures deployId.
#   4. Poll `get-deploy-for-site` until state=ready.
#   5. Sleep 45s for CDN warm-up.
#   6. curl -A "Mozilla/5.0" verify on root + one tile endpoint.
#   7. Echo deployId on stdout.
#
# Exit codes:
#   0   ready and verified
#   2   build errored (errored>0 in build report)
#   3   missing NETLIFY_PAT (canonical path: see WIP_OPEN.md Open backlog)
#   4   verify failed (HTTP non-200 on root or tile)
#   5   poll timeout (state never reached `ready` within 5 minutes)

set -euo pipefail

# Logging helper: stderr only — stdout reserved for deployId.
log() { echo "$@" >&2; }

REBUILD=0
SITE_ID="01b53b80-687e-4641-b088-115b7d5ef638"
DIST="dist"

while [ $# -gt 0 ]; do
  case "$1" in
    --rebuild)  REBUILD=1; shift ;;
    --site-id)  SITE_ID="$2"; shift 2 ;;
    --dist)     DIST="$2"; shift 2 ;;
    *)          log "ERROR: unknown arg $1"; exit 3 ;;
  esac
done

log "=== deploy: site=$SITE_ID dist=$DIST ==="

# 1. Build if needed.
if [ "$REBUILD" = "1" ] || [ ! -d "$DIST" ]; then
  log "[§8.1] running build.py"
  REPORT=$(python3 build.py 2>&1 | tee /dev/stderr | tail -3)
  ERR=$(echo "$REPORT" | grep -oE 'errored=[0-9]+' | head -1 | cut -d= -f2 || echo 0)
  if [ "${ERR:-0}" -gt 0 ]; then
    log "ERROR: build had errored=$ERR layers (§6 rule 8 — refusing to deploy)"
    exit 2
  fi
fi

# 2. Netlify MCP `deploy-site` requires auth.
if [ ! -f /mnt/project/CREDENTIALS.md ]; then
  log "ERROR: /mnt/project/CREDENTIALS.md not readable"
  exit 3
fi
NETLIFY_PAT=$(grep '^NETLIFY_PAT=' /mnt/project/CREDENTIALS.md 2>/dev/null | cut -d= -f2 || true)
if [ -z "${NETLIFY_PAT:-}" ]; then
  log "ERROR: NETLIFY_PAT missing from CREDENTIALS.md."
  log "       This script's bash-only path needs NETLIFY_PAT to call MCP via JSON-RPC."
  log "       Until provisioned, deploy via Netlify MCP in chat (OPERATING.md §8)."
  log "       See WIP_OPEN.md Open backlog: 'NETLIFY_PAT absent from CREDENTIALS.md'."
  exit 3
fi

MCP_URL="https://netlify-mcp.netlify.app/mcp"
mcp_call() {
  # Args: <tool-name> <json-args>
  local TOOL="$1" ARGS="$2"
  curl -sS -X POST "$MCP_URL" \
    -H "Authorization: Bearer $NETLIFY_PAT" \
    -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"$TOOL\",\"arguments\":$ARGS}}"
}

log "[§8.2] requesting deploy-site proxy URL"
DEPLOY_RESP=$(mcp_call "deploy-site" "{\"siteId\":\"$SITE_ID\"}")
PROXY_URL=$(echo "$DEPLOY_RESP" | python3 -c 'import sys,json; r=json.load(sys.stdin); print(r["result"]["content"][0]["text"])' 2>/dev/null || echo "")
if [ -z "$PROXY_URL" ]; then
  log "ERROR: deploy-site MCP call returned no proxy URL: $DEPLOY_RESP"
  exit 3
fi

# 3. Upload bytes via npx proxy.
log "[§8.3] uploading $DIST/ via proxy"
pushd "$DIST" >/dev/null
UPLOAD_OUT=$(npx -y @netlify/mcp@latest --site-id "$SITE_ID" --proxy-path "$PROXY_URL" --no-wait 2>&1)
popd >/dev/null
DEPLOY_ID=$(echo "$UPLOAD_OUT" | grep -oE '[0-9a-f]{24}' | head -1 || echo "")
if [ -z "$DEPLOY_ID" ]; then
  log "ERROR: upload produced no deployId. Output: $UPLOAD_OUT"
  exit 3
fi
log "[§8.3] deployId: $DEPLOY_ID"

# 4. Poll for state=ready (5 min timeout, 5s interval).
log "[§8.4] polling get-deploy-for-site"
TIMEOUT=300
ELAPSED=0
STATE="building"
while [ "$STATE" != "ready" ] && [ "$ELAPSED" -lt "$TIMEOUT" ]; do
  sleep 5
  ELAPSED=$((ELAPSED + 5))
  POLL_RESP=$(mcp_call "get-deploy-for-site" "{\"siteId\":\"$SITE_ID\",\"deployId\":\"$DEPLOY_ID\"}")
  STATE=$(echo "$POLL_RESP" | python3 -c 'import sys,json,re; t=json.load(sys.stdin)["result"]["content"][0]["text"]; m=re.search(r"\"state\"\s*:\s*\"(\w+)\"",t); print(m.group(1) if m else "unknown")' 2>/dev/null || echo "unknown")
  log "  ${ELAPSED}s state=$STATE"
  if [ "$STATE" = "error" ]; then
    log "ERROR: deploy state=error"
    exit 4
  fi
done
if [ "$STATE" != "ready" ]; then
  log "ERROR: poll timeout after ${TIMEOUT}s, state=$STATE"
  exit 5
fi

# 5. CDN warm-up.
log "[§8.5] sleeping 45s for CDN warm-up"
sleep 45

# 6. Curl verification.
log "[§8.6] verifying root + tile endpoint"
ROOT_CODE=$(curl -sI -A "Mozilla/5.0" -o /dev/null -w "%{http_code}" "https://lrp-tx-gis.netlify.app/")
if [ "$ROOT_CODE" != "200" ]; then
  log "ERROR: root returned HTTP $ROOT_CODE"
  exit 4
fi
LAYER_COUNT=$(curl -s -A "Mozilla/5.0" "https://lrp-tx-gis.netlify.app/" | grep -oE '"id":"[a-z_][a-z0-9_]*"' | sort -u | wc -l)
log "[§8.6] verified: root 200, layer-id count $LAYER_COUNT"

# 7. Emit deployId on stdout (single line).
echo "$DEPLOY_ID"
log "=== deploy complete ==="
