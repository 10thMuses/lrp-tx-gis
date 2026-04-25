#!/usr/bin/env bash
# Atomic deploy + merge + delete-branch wrapper.
#
# Encodes OPERATING.md §6 hard rule 12 ("deploy + merge + delete-branch is
# atomic") as one indivisible call. Replaces the manual sequence of two
# separate commands.
#
# Usage (from inside /home/claude/repo, on the feature branch):
#   bash scripts/ship.sh <branch> [<title>] [-- deploy.sh-args...]
#
# Sequence:
#   1. Run scripts/deploy.sh (with any args after `--`).
#   2. Capture deployId from its stdout.
#   3. Run scripts/close-out.sh <branch> <deployId> [<title>].
#
# Exit codes:
#   propagates from deploy.sh or close-out.sh; non-zero halts the chain.

set -euo pipefail

BRANCH="${1:-}"
if [ -z "$BRANCH" ]; then
  echo "ERROR: usage: ship.sh <branch> [<title>] [-- deploy.sh-args...]" >&2
  exit 3
fi
shift

TITLE=""
DEPLOY_ARGS=()
if [ $# -gt 0 ] && [ "$1" != "--" ]; then
  TITLE="$1"
  shift
fi
if [ $# -gt 0 ] && [ "$1" = "--" ]; then
  shift
  DEPLOY_ARGS=("$@")
fi

echo "=== ship: branch=$BRANCH ===" >&2

# 1+2. Deploy and capture deployId on stdout.
DEPLOY_ID=$(bash scripts/deploy.sh "${DEPLOY_ARGS[@]:-}")
if [ -z "$DEPLOY_ID" ]; then
  echo "ERROR: deploy.sh returned empty deployId" >&2
  exit 4
fi

# 3. Close out.
if [ -n "$TITLE" ]; then
  bash scripts/close-out.sh "$BRANCH" "$DEPLOY_ID" "$TITLE"
else
  bash scripts/close-out.sh "$BRANCH" "$DEPLOY_ID"
fi

echo "=== ship complete: deploy=$DEPLOY_ID ===" >&2
