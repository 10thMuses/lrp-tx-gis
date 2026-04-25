#!/usr/bin/env bash
# Canonical close-out procedure for shipping chats.
#
# Encodes OPERATING.md §5 close-out, §6 hard rules 12 & 14, and §9 GitHub-sync
# merge sequence as one indivisible call. Replaces the multi-step bash block
# formerly pasted into WIP_OPEN.md ## Next chat.
#
# Usage (from inside /home/claude/repo, on the feature branch):
#   bash scripts/close-out.sh <branch-name> <deploy-id> [<title>]
#
# <deploy-id> use the literal string `none` for doc-only chats (no deploy).
# <title>     optional one-line summary for the merge commit; defaults to
#             the branch slug (refinement- prefix stripped, hyphens→spaces).
#
# Sequence (in order):
#   1. Stage any pending WIP_OPEN.md edits and commit them on the feature branch.
#   2. Push the feature branch to origin.
#   3. Enforce §6 rule 14: HEAD must have ≥1 non-handoff commit beyond main.
#      "non-handoff" = touches at least one path NOT matching docs/_*_handoff.md.
#   4. Delete any handoff doc on the branch (per §10 — branch is the truth).
#   5. Checkout main; pull --rebase origin main.
#   6. Merge --no-ff origin/<branch> with deploy-id in the message.
#   7. Push main.
#   8. Delete origin branch.
#
# Exit codes:
#   0   clean
#   3   bad args
#   4   §6 rule 14 violation (recon-only chat — refusing to merge)
#   5   merge conflict (manual intervention required)
#   6   push rejected (operator must investigate)

set -euo pipefail

BRANCH="${1:-}"
DEPLOY_ID="${2:-}"
TITLE="${3:-}"

if [ -z "$BRANCH" ] || [ -z "$DEPLOY_ID" ]; then
  echo "ERROR: usage: close-out.sh <branch> <deploy-id|none> [<title>]" >&2
  exit 3
fi

if [ -z "$TITLE" ]; then
  TITLE="$(echo "${BRANCH#refinement-}" | tr '-' ' ')"
fi

if [ "$DEPLOY_ID" = "none" ]; then
  MSG="Merge ${BRANCH}: ${TITLE} (no deploy)"
else
  MSG="Merge ${BRANCH}: ${TITLE} (deploy ${DEPLOY_ID})"
fi

echo "=== close-out: branch=$BRANCH deploy=$DEPLOY_ID ==="

# 0. Sanity: must be on feature branch.
CURRENT="$(git rev-parse --abbrev-ref HEAD)"
if [ "$CURRENT" != "$BRANCH" ]; then
  echo "ERROR: HEAD is on '$CURRENT', expected '$BRANCH'" >&2
  exit 3
fi

# 1. Commit any uncommitted WIP_OPEN.md changes (canonical: WIP_OPEN.md is the
#    last edit before close-out).
if ! git diff --quiet -- WIP_OPEN.md 2>/dev/null; then
  git add WIP_OPEN.md
  git commit -m "WIP_OPEN.md: handoff to next chat"
fi
# Also stage any other pending tracked changes from in-flight work — close-out
# is the LAST gate; no uncommitted state should leak past it.
if ! git diff --quiet 2>/dev/null; then
  echo "ERROR: uncommitted tracked changes outside WIP_OPEN.md. Commit explicitly first." >&2
  git status --short >&2
  exit 3
fi

# 2. Push feature branch.
git fetch origin --quiet
git push origin "$BRANCH"

# 3. §6 rule 14: count non-handoff commits on origin/<branch> beyond origin/main.
NON_HANDOFF=0
while read -r SHA; do
  [ -z "$SHA" ] && continue
  PATHS="$(git diff-tree --no-commit-id --name-only -r "$SHA")"
  if echo "$PATHS" | grep -vE '^docs/_.*_handoff\.md$' | grep -q .; then
    NON_HANDOFF=$((NON_HANDOFF + 1))
  fi
done < <(git log --format=%H "origin/main..origin/$BRANCH")

echo "[§6.14] non-handoff commits on $BRANCH beyond main: $NON_HANDOFF"

if [ "$NON_HANDOFF" -eq 0 ]; then
  echo "ERROR: §6 rule 14 — recon-only chat (zero non-handoff commits). Refusing to merge." >&2
  exit 4
fi

# 4. Remove handoff doc if present (branch is the truth — doc never lands on main).
SLUG="${BRANCH#refinement-}"
HANDOFF="docs/_${SLUG}_handoff.md"
if [ -f "$HANDOFF" ]; then
  git rm -- "$HANDOFF"
  git commit -m "remove handoff doc on close-out"
  git push origin "$BRANCH"
fi

# 5. Checkout main; rebase against origin.
git checkout main
git pull --rebase origin main

# 6. Merge --no-ff with deploy-id in message.
if ! git merge --no-ff "origin/$BRANCH" -m "$MSG"; then
  echo "ERROR: merge conflict on $BRANCH → main. Resolve manually." >&2
  exit 5
fi

# 7. Push main.
if ! git push origin main; then
  echo "ERROR: push to main rejected. Manual investigation required." >&2
  exit 6
fi

# 8. Delete origin branch.
git push origin --delete "$BRANCH" || echo "WARN: origin branch delete failed (may already be gone)"

echo "=== close-out complete: $MSG ==="
