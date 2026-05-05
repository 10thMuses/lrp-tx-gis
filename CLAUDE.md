# CLAUDE.md

Bootstrap doc for Claude Code sessions on this repo. Auto-loaded into every session's context.

---

## Operator

**Andrea Himmel**, Land Resource Partners (LRP). Works at the intersection of energy infrastructure, land, and real estate — ERCOT, Texas data centers, advanced nuclear, GPU/AI infrastructure financing, grid policy. Tracks these markets for investment analysis and as a content/intelligence product distributed to peers (Mel Riggs, Mark, Dory Wiley, John Lane).

## Voice

Peer-level industry tone. Concise, factual, professional, direct. No fluff, no recap, no repetitive language. No "should I proceed" hedging — when the next move is named and unblocked, execute. Substantive data integrated. Minimize tokens.

## Project

LRP Texas Energy GIS Map. MapLibre + PMTiles + tippecanoe stack. Deployed to Netlify (`https://lrp-tx-gis.netlify.app`, siteId `01b53b80-687e-4641-b088-115b7d5ef638`). `main` is canonical.

---

## Session start — required reading

Every shipping session, in order:

1. `OPERATING.md` — execution rules, session protocol, hard rules, trigger phrases, build/refresh/merge cycles
2. `ARCHITECTURE.md` — schema, layer catalog, palette, fragility table
3. `WIP_OPEN.md` — `## Next chat` block carries the active task

Conversational sessions: read `WIP_OPEN.md` only if state-dependent. Skip the rest.

## Environment delta from prior chat-based sessions

This repo's `OPERATING.md` was written for ephemeral chat containers where state evaporates on reset. In Claude Code the working dir is persistent local. Adjust accordingly:

- **No clone-edit-push bracket.** Working dir is the local clone. Edits land in place.
- **`/mnt/project/` does not exist.** `CREDENTIALS.md` content lives in `.env` at repo root (gitignored). GitHub auth uses local git credentials, not the PAT-over-MCP pattern.
- **Push-on-commit (§6.9) is discipline, not survival.** Container doesn't reset. Still good practice for backup and CI triggers.
- **Session-open script (§5) skipped.** No clone needed. Run only the handoff-doc detection portion if useful.
- **Close-out script** still valid for branch merge + WIP_OPEN update + push.
- **Tool-call budgets (§12) do not apply.** No per-session cap.
- **`present_files` does not exist.** Local files are already accessible to the operator. Just name the path.

When `OPERATING.md` and this section disagree on environment specifics, this section wins. When they disagree on execution discipline (banned asks, blast radius, hard rules 1–8, 10–15), `OPERATING.md` wins.

## First-time setup

```bash
git clone https://github.com/10thMuses/lrp-tx-gis.git
cd lrp-tx-gis
bash scripts/bootstrap-claude-code.sh
# edit .env to fill in GITHUB_PAT and NETLIFY_PAT
```

`bootstrap-claude-code.sh` is idempotent. It installs tippecanoe + python deps, copies `.env.example` → `.env` if missing, sets git identity, and runs a smoke test.

## Build paths

`build.py` resolves paths from environment variables with chat-mode fallbacks:

| Variable | Code mode (.env) | Chat mode default |
|---|---|---|
| `LRP_PROJECT_DIR` | `.` | `/mnt/project` |
| `LRP_DIST_DIR` | `./dist` | `/mnt/user-data/outputs/dist` |
| `LRP_UPLOADS_DIR` | `./uploads` | `/mnt/user-data/uploads` |

Same for `scripts/deploy.sh`: NETLIFY_PAT resolves from `.env` first, then `/mnt/project/CREDENTIALS.md`, then shell env.

## Hard constraints worth repeating

These are the highest-cost failure modes; surface them in working memory:

- **Never read source data files into context.** Stream through `tippecanoe` subprocesses only. No `cat`/`head`/`view` of `combined_points.csv`, `combined_geoms.geojson`, or any layer source file.
- **Never `git add -A`.** Always stage explicit paths.
- **Never hand-code coordinates or feature values.** No source, no layer.
- **Atomic in-place writes** for any read-modify-write helper (`os.replace`, not `'w'` mode).

## Credentials

`.env` at repo root, gitignored. See `.env.example` for the full template. Required keys: `GITHUB_PAT`, `NETLIFY_PAT`. GitHub PAT is needed only for scripted operations that require explicit auth — most git operations use the local credential helper. NETLIFY_PAT is required for `scripts/deploy.sh`; without it the script falls back to in-chat Netlify MCP (chat mode only).

## Repo

`github.com/10thMuses/lrp-tx-gis` — `main` canonical. Branch naming: `refinement-<slug>` for shipping work. `<slug>` is 2–4 words.
