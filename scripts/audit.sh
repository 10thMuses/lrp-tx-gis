#!/usr/bin/env bash
# Telemetry snapshot per OPERATING.md §15. Read-only.
#
# Usage:
#   bash scripts/audit.sh
#
# Prints a human-readable summary to stdout:
#   - OPERATING.md line count   (target ≤250)
#   - WIP_OPEN.md byte size     (target ≤8KB)
#   - merge commits in last 30  (proxy for chat count)
#   - close-out usage signal    (merge-commit format conformance)
#   - stranded branches         (target 0)
#
# Drift in any metric is the prompt for a structural fix per §14, not a new
# prose rule.

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

echo "=== LRP GIS audit — $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo ""

# 1. OPERATING.md line count.
OP_LINES=$(wc -l < OPERATING.md)
OP_STATUS="OK"
[ "$OP_LINES" -gt 250 ] && OP_STATUS="DRIFT"
printf "OPERATING.md lines:     %4d   target ≤250    %s\n" "$OP_LINES" "$OP_STATUS"

# 2. WIP_OPEN.md byte size.
WIP_BYTES=$(wc -c < WIP_OPEN.md)
WIP_STATUS="OK"
[ "$WIP_BYTES" -gt 8192 ] && WIP_STATUS="DRIFT"
printf "WIP_OPEN.md bytes:      %4d   target ≤8192   %s\n" "$WIP_BYTES" "$WIP_STATUS"

# 3. Recent merge commits on main = chat count proxy.
git fetch origin --quiet 2>/dev/null || true
MERGE_COUNT=$(git log --merges --format=%H -n 30 origin/main 2>/dev/null | wc -l || echo 0)
printf "merge commits (last 30): %3d   (each ≈ one shipping chat)\n" "$MERGE_COUNT"

# 4. close-out conformance: merge messages should match
#    "Merge <branch>: <title> (deploy <id>)" or "(no deploy)".
CONFORMANT=$(git log --merges --format=%s -n 30 origin/main 2>/dev/null | \
  grep -cE '^Merge [^ ]+: .* \((deploy [0-9a-f]+|no deploy)\)$' || true)
printf "close-out conformant:   %4d / %d\n" "$CONFORMANT" "$MERGE_COUNT"

echo ""

# 5. Stranded branches: anything on origin that isn't main.
echo "--- stranded branches on origin ---"
STRANDED=$(git ls-remote --heads origin 2>/dev/null | awk '{print $2}' | sed 's|refs/heads/||' | grep -v '^main$' || true)
if [ -z "$STRANDED" ]; then
  echo "  (none)"
else
  while read -r BR; do
    [ -z "$BR" ] && continue
    AHEAD=$(git rev-list --count "origin/main..origin/$BR" 2>/dev/null || echo "?")
    BEHIND=$(git rev-list --count "origin/$BR..origin/main" 2>/dev/null || echo "?")
    LAST=$(git log -1 --format=%cI "origin/$BR" 2>/dev/null || echo "?")
    printf "  %-50s ahead=%s behind=%s last=%s\n" "$BR" "$AHEAD" "$BEHIND" "$LAST"
  done <<< "$STRANDED"
fi

echo ""

# 6. Repo size sanity.
REPO_BYTES=$(du -sb . 2>/dev/null | awk '{print $1}' || echo 0)
REPO_MB=$((REPO_BYTES / 1024 / 1024))
printf "repo size:              %4d MB\n" "$REPO_MB"

echo ""
echo "=== audit complete ==="
