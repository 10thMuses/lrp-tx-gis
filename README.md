# Land Resource Partners — Texas Energy GIS Map

**Owner:** Andrea Himmel
**Prod URL:** https://lrp-tx-gis.netlify.app
**Netlify siteId:** `01b53b80-687e-4641-b088-115b7d5ef638`

This project has two deliverables: the Texas Energy GIS Map (this stack) and the Grid Wire newsletter (separate chats, shares this project's memory).

---

## Source-of-truth hierarchy

**`/mnt/project/` > sidebar system prompt > `memory_user_edits`**

If any of the three disagree, `/mnt/project/` wins. `/mnt/project/` is the repo-equivalent. Memory catches up on next update cycle.

---

## Read order for every new GIS chat

Every session's first tool call is a composite `bash`: `ls /mnt/project/` + `head` of the key docs. Pre-flight check.

1. **`GIS_SPEC.md`** — architecture, triggers, hard rules, fragility table, session protocol (§12-§18). Authoritative.
2. **`COMMANDS.md`** — trigger phrase reference. Matches `GIS_SPEC.md` §0.
3. **`PROJECT_INSTRUCTIONS.md`** — operating principles. First line after project identity: **zero asks per chat target.**
4. **`WIP_OPEN.md`** — "Recent sessions" + "Next chat" handoff + pinned "Forward protocol" block at bottom.
5. **`SESSION_LOG.md`** — append-only log of every chat's outcome + anomalies.
6. **`ENVIRONMENT.md`** — capabilities Claude has vs. doesn't in this runtime. Consulted when a task might hit a platform limit.
7. **`CREDENTIALS.md`** — credential registry (minimal today).

---

## File inventory

### Toolchain (never touch without a protocol amendment)
- `build.py` — reads `layers.yaml` + combined data files, streams through tippecanoe, writes `dist/`
- `build_template.html` — MapLibre + PMTiles shell; `/*__LAYERS__*/` placeholder replaced at build
- `layers.yaml` — layer registry, single source of truth for the map UI

### Data (combined architecture post-chat-34 refactor)
- `combined_points.csv` — all point layers, `layer_id` column selects
- `combined_geoms.geojson` — all line/polygon layers, `layer_id` property selects
- Standalone large files only when needed (e.g., `geoms_parcels_pecos.geojson`)

### Docs
- `GIS_SPEC.md`, `COMMANDS.md`, `PROJECT_INSTRUCTIONS.md` — authoritative rules
- `README.md` — this file
- `SESSION_LOG.md` — append-only outcome log
- `WIP_OPEN.md` — forward state + handoffs
- `CREDENTIALS.md` — credential registry (minimal today)

---

## How to open a new chat

Any one-sentence trigger. Pre-flight handles the rest. Examples:

- `build. deploy to prod.`
- `refresh ercot_queue.`
- `add layer X from outputs/refresh. build. deploy.`
- `merge <refreshed_file>.` (post-refactor trigger for updating combined files)
- `resume.` (reads `WIP_OPEN.md` "Next chat" block, continues)
- `audit.` (drift check only, no build/deploy)

Full trigger list in `COMMANDS.md`.

---

## Environment constraint (unavoidable)

`/mnt/project/` is mounted read-only by the Claude platform. No tool writes back to project knowledge. Every chat's output lands in `/mnt/user-data/outputs/` as a zip — you re-upload affected files to project knowledge between chats. Autonomy protocol eliminates intra-chat asks but not this one inter-chat sync. Budget: ~30 seconds per chat cycle.
