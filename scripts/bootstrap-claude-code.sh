#!/usr/bin/env bash
# One-shot bootstrap for a fresh Claude Code session on this repo.
#
# Idempotent. Run once after `git clone`. Safe to re-run.
#
#   bash scripts/bootstrap-claude-code.sh
#
# Verifies / installs:
#   1. tippecanoe          — required for build.py
#   2. python3 deps        — yaml, pmtiles
#   3. .env                — copies from .env.example if missing, prompts for fill-in
#   4. git identity        — sets user.name/.email if unset (Chat 103 fix)
#   5. fonts (Jost, Inter) — for PDF generation pipelines (Grid Wire, etc.)
#   6. Smoke test          — `python3 build.py --help` returns 0
#
# Exits 0 on success, non-zero on any verification failure.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
log() { echo "[bootstrap] $@" >&2; }

cd "$ROOT"

# 1. tippecanoe ------------------------------------------------------------
if ! command -v tippecanoe >/dev/null 2>&1; then
  log "tippecanoe not found — installing"
  if command -v brew >/dev/null 2>&1; then
    brew install tippecanoe
  elif command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -qq && sudo apt-get install -y tippecanoe
  else
    log "ERROR: no supported package manager (brew/apt-get) found. Install tippecanoe manually:"
    log "       https://github.com/felt/tippecanoe"
    exit 1
  fi
fi
log "tippecanoe: $(tippecanoe --version 2>&1 | head -1)"

# 2. python deps -----------------------------------------------------------
PYDEPS="pyyaml pmtiles requests"
log "python deps: $PYDEPS"
python3 -m pip install --quiet --upgrade $PYDEPS 2>&1 | tail -3 || {
  log "pip install failed — try with --break-system-packages or a venv"
  exit 1
}

# 3. .env ------------------------------------------------------------------
if [ ! -f "$ROOT/.env" ]; then
  if [ -f "$ROOT/.env.example" ]; then
    cp "$ROOT/.env.example" "$ROOT/.env"
    log ".env created from .env.example — fill in GITHUB_PAT and NETLIFY_PAT"
  else
    log "WARN: .env.example missing; creating empty .env"
    touch "$ROOT/.env"
  fi
else
  log ".env exists"
fi

# Sanity: are tokens populated? Don't print values.
ENV_OK=1
for KEY in GITHUB_PAT NETLIFY_PAT; do
  VAL=$(grep "^${KEY}=" "$ROOT/.env" | cut -d= -f2-)
  if [ -z "$VAL" ]; then
    log "WARN: $KEY is empty in .env"
    ENV_OK=0
  fi
done
[ "$ENV_OK" = "1" ] && log "tokens: present"

# 4. git identity ----------------------------------------------------------
if [ -z "$(git config user.email 2>/dev/null)" ]; then
  log "setting git user.email = claude@lrp.local"
  git config user.email "claude@lrp.local"
fi
if [ -z "$(git config user.name 2>/dev/null)" ]; then
  log "setting git user.name = 'Claude (LRP GIS)'"
  git config user.name "Claude (LRP GIS)"
fi

# 5. fonts (optional — only if WeasyPrint pipeline will be used) ----------
if [ ! -d "$HOME/.fonts" ] || [ -z "$(ls -A "$HOME/.fonts" 2>/dev/null | grep -i jost)" ]; then
  log "Jost font not installed (skipped — only needed for Grid Wire PDFs)"
fi

# 6. smoke test ------------------------------------------------------------
if python3 -c "import yaml, pmtiles" 2>/dev/null; then
  log "smoke: python imports OK"
else
  log "ERROR: python imports failed (yaml, pmtiles)"
  exit 1
fi

log "=== bootstrap complete ==="
log "Next: edit .env to populate GITHUB_PAT and NETLIFY_PAT"
log "Then: bash scripts/deploy.sh --rebuild  (full build + deploy smoke)"
