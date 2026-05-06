# CLAUDE.md

Bootstrap doc for Claude Code sessions on this repo. Auto-loaded into every session.

---

## Operator

**Andrea Himmel**, Land Resource Partners (LRP). Works at the intersection of energy infrastructure, land, and real estate — ERCOT, Texas data centers, advanced nuclear, GPU/AI infrastructure financing, grid policy. Tracks these markets for investment analysis and as a content/intelligence product distributed to peers (Mel Riggs, Mark, Dory Wiley, John Lane).

## Voice

Peer-level industry tone. Concise, factual, professional, direct. No fluff, no recap, no repetitive language. No "should I proceed" hedging — when the next move is named and unblocked, execute. Substantive data integrated.

## Project

LRP Texas Energy GIS Map. MapLibre + PMTiles + tippecanoe stack. Deployed to Netlify (`https://lrp-tx-gis.netlify.app`, siteId `01b53b80-687e-4641-b088-115b7d5ef638`). `main` is canonical.

---

## First-time setup

```bash
git clone https://github.com/10thMuses/lrp-tx-gis.git
cd lrp-tx-gis
bash scripts/bootstrap-claude-code.sh
```

`bootstrap-claude-code.sh` is idempotent. It installs `tippecanoe` (via `brew` on macOS or `apt-get` on Linux), installs Python deps (`pyyaml`, `pmtiles`, `requests`), copies `.env.example` → `.env` if missing, sets git identity defaults, runs a smoke test.

Then edit `.env` to populate:
- `GITHUB_PAT` — fine-grained PAT with Contents R/W on `10thMuses/lrp-tx-gis`. Mint at https://github.com/settings/personal-access-tokens.
- `NETLIFY_PAT` — Netlify Personal Access Token. Mint at https://app.netlify.com/user/applications#personal-access-tokens.

`.env` is gitignored. The PATs in this file enable scripted builds and deploys; most ordinary `git` operations use the local credential helper.

---

## Required reading at session start

1. `OPERATING.md` — execution rules, hard rules, build/deploy cycles
2. `ARCHITECTURE.md` — schema, layer catalog, palette, fragility table
3. `WIP_OPEN.md` — active sprints and backlog

---

## Build paths

`build.py` and `scripts/deploy.sh` resolve paths from environment variables, falling back to `/mnt/...` for chat-mode compatibility. In Code mode, `.env` overrides:

| Variable | Code mode (.env) | Default |
|---|---|---|
| `LRP_PROJECT_DIR` | `.` | `/mnt/project` |
| `LRP_DIST_DIR` | `./dist` | `/mnt/user-data/outputs/dist` |
| `LRP_UPLOADS_DIR` | `./uploads` | `/mnt/user-data/uploads` |

`scripts/deploy.sh` reads `NETLIFY_PAT` from `.env` first, then `/mnt/project/CREDENTIALS.md`, then the `NETLIFY_PAT_ENV` shell var.

---

## Hard constraints worth repeating

These are the highest-cost failure modes; surface them in working memory.

- **Never read source data files into context.** Stream through `tippecanoe` subprocesses only. No `cat` / `head` / `view` of `combined_points.csv`, `combined_geoms.geojson`, or any layer source file.
- **Never `git add -A`.** Always stage explicit paths.
- **Never hand-code coordinates or feature values.** No source, no layer.
- **Atomic in-place writes** for any read-modify-write helper (`os.replace`, not `'w'` mode).
- **Atomic deploy + merge.** Never deploy without the matching merge in the same session.

---

## Repo

`github.com/10thMuses/lrp-tx-gis` — `main` canonical. Branch naming: `refinement-<slug>` for shipping work. `<slug>` is 2–4 words.

## Common workflows

**Start a change:**
```bash
git checkout main && git pull --ff-only
git checkout -b refinement-<slug>
```

**Build + deploy:**
```bash
bash scripts/deploy.sh --rebuild
```

**Close out:**
```bash
bash scripts/close-out.sh refinement-<slug> <deploy-id> "<message>"
```

**Single-layer refresh:**
```bash
python3 build.py merge <layer_id> <refresh_file>
git add combined_points.csv  # or combined_geoms.geojson
git commit -m "refresh: <layer_id> from <source> <date>"
```

**Audit drift:**
```bash
bash scripts/audit.sh
```
