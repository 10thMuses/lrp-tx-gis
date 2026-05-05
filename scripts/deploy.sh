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
#   4. Poll prod URL for md5 parity vs local dist/index.html. Parity == both
#      (a) deploy state=ready and (b) CDN propagated, in one signal. Replaces
#      the prior get-deploy-for-site MCP poll + blind 45s CDN sleep.
#   5. Echo deployId on stdout.
#
# Exit codes:
#   0   ready and verified
#   2   build errored (errored>0 in build report)
#   3   missing NETLIFY_PAT (canonical path: see WIP_OPEN.md Open backlog)
#   4   verify failed (HTTP non-200 on root or tile)
#   5   poll timeout (md5 parity not reached within 5 minutes)

set -euo pipefail

# Logging helper: stderr only — stdout reserved for deployId.
log() { echo "$@" >&2; }

# Repo root: parent of scripts/ regardless of where this is invoked from.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

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
# Resolution order: .env at repo root (Claude Code mode), then
# /mnt/project/CREDENTIALS.md (chat mode), then current shell env.
# awk with `=$1=$2…` pattern picks the last non-empty NETLIFY_PAT= line.
read_pat() {
  local f="$1"
  [ -f "$f" ] || return 0
  awk -F= 'BEGIN{v=""} /^NETLIFY_PAT=/ {sub(/^NETLIFY_PAT=/,""); if(length($0)>0) v=$0} END{print v}' "$f"
}
NETLIFY_PAT=$(read_pat "$ROOT/.env")
if [ -z "${NETLIFY_PAT:-}" ]; then
  NETLIFY_PAT=$(read_pat /mnt/project/CREDENTIALS.md)
fi
if [ -z "${NETLIFY_PAT:-}" ]; then
  NETLIFY_PAT="${NETLIFY_PAT_ENV:-}"
fi
if [ -z "${NETLIFY_PAT:-}" ]; then
  log "ERROR: NETLIFY_PAT not found."
  log "       Resolution order: .env at repo root, /mnt/project/CREDENTIALS.md, NETLIFY_PAT_ENV var."
  log "       Until provisioned, deploy via Netlify MCP in chat (OPERATING.md §8)."
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
  # On failure, dump full output so the operator can see deprecation warnings,
  # auth errors, npm noise, etc. On success we already have what we need.
  log "ERROR: upload produced no deployId. Output: $UPLOAD_OUT"
  exit 3
fi
log "[§8.3] deployId: $DEPLOY_ID"

# 4–6. Fused md5-parity poll: prod==local md5 means (a) deploy state=ready AND
# (b) CDN has propagated. Eliminates the separate get-deploy-for-site MCP poll
# (saved ~3KB JSON per call × N polls) AND the blind 45s CDN sleep. The poll
# converges in 5–60s typically; falls back to the same 5-minute ceiling.
#
# Correctness depends on every build producing a byte-unique index.html so
# parity-already-true cannot be the pre-deploy state. Guaranteed by the
# /*__BUILD_ID__*/ token substitution in build.py:render_html (per-build UTC
# timestamp + random nonce). Removing that marker breaks this poll.
LOCAL_INDEX="$DIST/index.html"
if [ ! -f "$LOCAL_INDEX" ]; then
  log "ERROR: $LOCAL_INDEX missing — cannot compute md5-parity target"
  exit 4
fi
LOCAL_MD5=$(md5sum "$LOCAL_INDEX" | awk '{print $1}')
log "[§8.4] polling for prod md5 == local md5 ($LOCAL_MD5)"
TIMEOUT=300
ELAPSED=0
PROD_MD5=""
ROOT_CODE=""
while [ "$PROD_MD5" != "$LOCAL_MD5" ] && [ "$ELAPSED" -lt "$TIMEOUT" ]; do
  sleep 5
  ELAPSED=$((ELAPSED + 5))
  ROOT_CODE=$(curl -sI -A "Mozilla/5.0" -o /dev/null -w "%{http_code}" "https://lrp-tx-gis.netlify.app/" || echo "000")
  if [ "$ROOT_CODE" = "200" ]; then
    PROD_MD5=$(curl -s -A "Mozilla/5.0" "https://lrp-tx-gis.netlify.app/" | md5sum | awk '{print $1}')
  fi
  log "  ${ELAPSED}s root=$ROOT_CODE prod_md5=${PROD_MD5:-none}"
done
if [ "$PROD_MD5" != "$LOCAL_MD5" ]; then
  log "ERROR: md5-parity timeout after ${TIMEOUT}s. prod=$PROD_MD5 local=$LOCAL_MD5"
  exit 5
fi
log "[§8.6] verified: root 200, md5 parity local↔prod"

# 7. Emit deployId on stdout (single line).
echo "$DEPLOY_ID"
log "=== deploy complete ==="
