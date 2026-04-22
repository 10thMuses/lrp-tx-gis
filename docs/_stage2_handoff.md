# Stage 2 Bug Sweep — in-flight handoff

**Temporary file.** Delete before opening PR.

Session-open recon complete on branch `refinement-bug-sweep`. Coding not started. Next chat resumes from this file; no prompt-parsing or conversation_search required.

---

## State at handoff

- Branch `refinement-bug-sweep` created from `main` (not pushed in prior chat; may need recreation).
- Stale `refinement-filter-ui` remote branch deleted.
- Zero commits on the branch.
- Filter UI (Stage 1) merged to `main` in Chat 65. No prod deploy — ships with Stage 2.

---

## Scope (three bugs, per `docs/refinement-sequence.md` §Stage 2)

1. Waha gas hub — diagnose why not showing; fix.
2. `parcels_pecos` — diagnose why nothing renders; fix. If data file broken, document and propose before rebuilding.
3. Measure tool closes when user clicks a popup. Fix so measure tool persists through popup clicks.

Do NOT touch: icons, colors, sizing, sprite sheet, watermark. Stage 3+.

---

## Recon findings (do not redo)

### Bug 1 — Waha (`labels_hubs`)

- 1 feature exists in `combined_geoms.geojson` tagged `layer_id:labels_hubs`, has `name`.
- `layers.yaml`: `geom: label`, `default_on: true`, `min_zoom: 4`, tippecanoe `-Z0 -z14`.
- `build_template.html`: label rendering at lines 288, 300, 324–333. Symbol layer, `text-field: ['get','name']`.
- Split pipeline uses `ROOT / COMBINED_GJ` (build.py:632) — NOT the Chat-65 PROJECT/ROOT path bug.

**Next diagnostic:** local build, then `pmtiles show dist/tiles/labels_hubs.pmtiles` (or inspect via tippecanoe-decode) to confirm feature reaches the tile with `name` preserved.

### Bug 2 — `parcels_pecos`

- `layers.yaml`: `prebuilt: true`, `min_zoom: 11`.
- Prebuilt resolver: `build.py:269` → `src_project = PROJECT / f'{lid}.pmtiles'`.
- `PROJECT = /mnt/project` (build.py:42), `ROOT = /home/claude/repo`.
- At session open, `ls -la` of repo root showed no `.pmtiles` files tracked.

**Likely root cause:** prebuilt `.pmtiles` missing from repo. In sidebar-mode chats it resolved via `/mnt/project/`, but post-port that path may be unreliable. First diagnostic: `ls /mnt/project/*.pmtiles` and `ls /home/claude/repo/*.pmtiles`.

**Secondary hypothesis:** internal source-layer name inside the pmtiles doesn't match `parcels_pecos` the template expects.

### Bug 3 — Measure tool / popup interaction

- Not yet inspected.
- Start: `grep -n 'measure\|Measure\|popup\|Popup' build_template.html`.
- Likely cause: `map.on('click', ...)` fires measure-tool teardown before popup bubbles.

---

## First bash commands next chat

```bash
cd /home/claude/repo
# If branch doesn't exist on remote (it won't, prior chat didn't push):
git checkout -b refinement-bug-sweep 2>/dev/null || git checkout refinement-bug-sweep
ls -la *.pmtiles /mnt/project/*.pmtiles 2>&1 | head
grep -n 'measure\|Measure\|popup\|Popup' build_template.html | head -40
```

---

## Execution order

1. Bug 2 first (parcels_pecos) — data/path diagnostic is the cheapest; unblocks whether a data-file question needs flagging.
2. Bug 1 (Waha) — local build + tile inspection; likely a quick fix.
3. Bug 3 (measure tool) — pure template JS; isolated from build pipeline.
4. Commit per bug with clear messages.
5. Local build to confirm 21/21 clean.
6. **Delete this file** (`docs/_stage2_handoff.md`).
7. Push branch, open PR → `main`, description per `Readme.md` §10.
8. Update `WIP_OPEN.md` + append `WIP_LOG.md` entry as final action.
9. Do NOT merge, do NOT deploy.

---

## File paths (fixed)

- `layers.yaml` — config
- `build.py` — 678 lines; `ROOT` = repo root, `PROJECT` = `/mnt/project/` read-only sidebar
- `build_template.html` — 891 lines; label rendering L288–333
- `combined_geoms.geojson` — 6481 features; `labels_hubs` = 1, `caramba_south` = 1 orphan (Stage 1 deleted from yaml but geoms.geojson still has the feature — harmless, ignore unless blocking)
- `combined_points.csv` — 39409 rows
