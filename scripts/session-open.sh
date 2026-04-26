#!/usr/bin/env bash
# Canonical session-open procedure for shipping chats.
#
# Enforces three OPERATING.md rules as executable gates so they cannot be
# skipped by a partial session-open block in WIP_OPEN.md:
#
#   - OPERATING.md §10 "branch-ahead rule" — fetch origin branch before
#     creating local; if remote has commits, check them out instead of
#     reconstructing.
#   - OPERATING.md §11 "trust handoff recon" — detect `docs/_<slug>_handoff.md`
#     and print its contents so the executor cannot proceed without reading.
#   - OPERATING.md §5 "empty branch upstream push" — if the branch is new to
#     origin, push it immediately so every subsequent commit has an upstream.
#
# Usage (from inside freshly-cloned /home/claude/repo):
#   bash scripts/session-open.sh <branch-name> [<handoff-slug>]
#
# <handoff-slug> defaults to the branch name stripped of a leading
# `refinement-` prefix. Handoff docs are expected at
# `docs/_<slug>_handoff.md` (see OPERATING.md §10).
#
# Exit codes:
#   0   clean — either no remote branch existed (fresh push) or remote
#       existed and was checked out; handoff printed if present.
#   2   remote branch existed and had divergent local uncommitted state
#       (should be impossible on a fresh clone, but guards against reuse).
#   3   missing branch argument.

set -euo pipefail

BRANCH="${1:-}"
if [ -z "$BRANCH" ]; then
  echo "ERROR: branch name required as arg 1" >&2
  exit 3
fi

SLUG="${2:-${BRANCH#refinement-}}"
HANDOFF="docs/_${SLUG}_handoff.md"

echo "=== session-open: branch=$BRANCH slug=$SLUG ==="

# Git identity (idempotent)
git config user.email "claude@lrp.local"
git config user.name  "Claude (LRP GIS)"

# Build deps (idempotent). Fresh containers lack tippecanoe (apt) and cairosvg (pip).
# Install only if missing. Failures are logged but do not abort session-open;
# build.py will surface a hard error later if a missing dep actually blocks a build.
if ! command -v tippecanoe >/dev/null 2>&1; then
  echo "[deps] tippecanoe not found — installing"
  apt-get install -y tippecanoe >/dev/null 2>&1 || echo "[deps] tippecanoe install failed (non-fatal; build will error if needed)"
fi
if ! python3 -c "import cairosvg" 2>/dev/null; then
  echo "[deps] cairosvg not found — installing"
  pip install -q cairosvg --break-system-packages >/dev/null 2>&1 || echo "[deps] cairosvg install failed (non-fatal; build will error if needed)"
fi

# 1. Branch-ahead check (OPERATING.md §10). Fetch origin first.
git fetch origin --quiet

REMOTE_SHA="$(git ls-remote --heads origin "$BRANCH" | awk '{print $1}')"

if [ -n "$REMOTE_SHA" ]; then
  echo "[§10] remote branch $BRANCH exists at $REMOTE_SHA — checking out from origin"
  git checkout -B "$BRANCH" "origin/$BRANCH"
  # Show what's on the branch beyond main so executor sees prior work
  echo "--- commits on branch beyond origin/main ---"
  git log --oneline origin/main.."origin/$BRANCH" || true
  echo "--- files changed vs origin/main ---"
  git diff --stat origin/main "origin/$BRANCH" || true
else
  echo "[§10] remote branch $BRANCH does not exist — creating fresh from main"
  git checkout -B "$BRANCH" origin/main
  # OPERATING.md §5: push empty branch immediately so origin tracks
  git push -u origin "$BRANCH"
  echo "[§5] empty branch pushed to origin with upstream tracking"
fi

# 2. Handoff-doc detection (OPERATING.md §11).
if [ -f "$HANDOFF" ]; then
  echo ""
  echo "=================================================================="
  echo "[§11] HANDOFF DOC PRESENT: $HANDOFF"
  echo "  TRUST ITS RECON. Do not re-verify line numbers / file structure."
  echo "  Apply edits directly per its instructions."
  echo "=================================================================="
  echo ""
  cat "$HANDOFF"
  echo ""
  echo "=================================================================="
  echo "[§11] END HANDOFF. Executor must apply edits per above; not re-recon."
  echo "=================================================================="
else
  echo "[§11] no handoff doc at $HANDOFF — fresh session"
fi

# 3. Production sanity check (always run; blast-radius low).
echo ""
echo "--- prod sanity ---"
curl -sI -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | head -1 || true
LAYERS="$(curl -s -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | grep -oE '"id":"[a-z_][a-z0-9_]*"' | sort -u | wc -l || echo 0)"
echo "prod layer count: $LAYERS"

echo ""
echo "=== session-open complete ==="
