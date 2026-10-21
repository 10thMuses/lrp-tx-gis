# LRP Texas Energy GIS Map

Interactive map of Texas energy, land, water and grid infrastructure, built for Permian
Basin investment analysis and distributed to a peer list.

**39 layers · ~180,000 features · MapLibre + PMTiles + tippecanoe · static, no backend**

🗺️ **[https://lrp-tx-gis.netlify.app](https://lrp-tx-gis.netlify.app)** — password-gated

---

## Start here

| I want to… | Go to |
|---|---|
| **Look at the map** | [https://lrp-tx-gis.netlify.app](https://lrp-tx-gis.netlify.app) — enter your email and the LRP access password. [Access instructions](docs/handbook/01-PROJECT-OVERVIEW.md#2-accessing-the-portal) |
| **Understand the project** | [Project Handbook](docs/handbook/README.md) |
| **Move it to another account** | [Migration Runbook](docs/handbook/00-MIGRATION-RUNBOOK.md) |
| **Know where the data comes from** | [Data Sources](docs/handbook/02-DATA-SOURCES.md) |
| **Refresh, build and deploy** | [Operations Runbook](docs/handbook/04-OPERATIONS-RUNBOOK.md) |
| **Add a layer or change the map** | [Editing the Map](docs/handbook/05-EDITING-THE-MAP.md) |
| **Find a credential or grant access** | [Accounts & Access](docs/handbook/06-ACCOUNTS-AND-ACCESS.md) |
| **See what's broken or planned** | [Roadmap & Gaps](docs/handbook/08-ROADMAP-AND-GAPS.md) |

---

## Quick start

```bash
git clone https://github.com/10thMuses/lrp-tx-gis.git
cd lrp-tx-gis
bash scripts/bootstrap-claude-code.sh     # tippecanoe, python deps, .env, smoke test
# edit .env → GITHUB_PAT, NETLIFY_PAT

python3 build.py                          # full build → dist/
bash scripts/deploy.sh --rebuild          # build, deploy, verify → prints deployId
```

Full setup: [Operations Runbook §1](docs/handbook/04-OPERATIONS-RUNBOOK.md#1-first-time-setup).

## Common tasks

```bash
# Start a change
git checkout main && git pull --ff-only && git checkout -b refinement-<slug>

# Refresh a source
python3 build.py refresh wells                              # RRC wellbores, weekly
python3 scripts/geocode_ercot_queue.py                      # ERCOT queue, monthly
python3 scripts/refresh_eia860.py --year 2024               # EIA-860, annual

# Merge a refresh file into the canonical data
python3 build.py merge <layer_id> <refresh_file>

# Ship (deploy + merge + delete branch, atomic)
bash scripts/ship.sh refinement-<slug> "<summary>" -- --rebuild

# Verify and audit
python3 scripts/verify_deployed_layers.py
bash scripts/audit.sh
```

---

## Repo layout

```
layers.yaml            THE layer registry — 39 entries, the single config
build.py               Build orchestrator + merge/refresh subcommands
build_template.html    The entire frontend (no framework, no bundler)
combined_points.csv    All point layers, tagged by layer_id
combined_geoms.geojson All line/fill features, tagged by layer_id
data/                  Standalone + archival layer sources
scripts/               Setup, refresh, deploy, close-out, audit
docs/handbook/         Full documentation ← start here
```

## The five rules

1. **Never read source data files into context** — stream through subprocesses only
2. **Never `git add -A`** — always stage explicit paths
3. **Never hand-code coordinates or feature values** — no source, no layer
4. **Atomic in-place writes** — `os.replace`, never `'w'` mode mid-process
5. **Deploy and merge are one unit** — use `scripts/ship.sh`

Full context: [Operations Runbook §8](docs/handbook/04-OPERATIONS-RUNBOOK.md#8-hard-rules)
· `OPERATING.md`

---

## Project docs

| File | Role |
|---|---|
| `docs/handbook/` | **Complete manual — the canonical documentation** |
| `CLAUDE.md` | Session bootstrap for Claude Code (auto-loaded) |
| `OPERATING.md` | Execution rules and build/deploy cycles |
| `ARCHITECTURE.md` | Schema, palette, fragility table *(partially stale — see [drift table](docs/handbook/08-ROADMAP-AND-GAPS.md#1-documentation-drift-found-2026-08-18))* |
| `WIP_OPEN.md` | Active sprints and backlog |

## Sources

All data is US federal or Texas state public data, or OpenStreetMap (ODbL). No paid or
licensed feeds. Primary sources: RRC · EIA-860 · ERCOT · USWTDB · HIFLD · Census TIGER ·
BTS · OSM · TCEQ · FCC BDC · TWDB · Texas Comptroller.

Per-layer provenance, scope filters and known fragility:
[Data Sources](docs/handbook/02-DATA-SOURCES.md).
