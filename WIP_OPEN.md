# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

---

## Current workstream

**Filter UI stage — code pushed to branch, one blocker before PR.** Chat 64 committed full implementation to `refinement-filter-ui` (commit `37cfdaf`, force-pushed over prior WIP pointer). Build runs to completion but produces 20/21 layers — `county_labels` comes back `MISSING` from `split_combined_geojson`. Pre-existing bug, not introduced by this chat (the splitter handles label-geom Point features and something in that path drops the 46 features tagged `layer_id=county_labels`). 

**Next-chat resume trigger:** `diagnose county_labels split and finish filter ui` or `continue filter ui stage`. Clone, checkout `refinement-filter-ui`, diagnose splitter against `combined_geoms.geojson` (46 features exist — confirmed via standalone Counter; `/tmp/gis_build/split/` after build contains no `county_labels.ndjson`). Fix in `build.py split_combined_geojson`. Re-run `python3 build.py` expecting 21/21 OK. Commit, push, open PR via GitHub UI (token lacks `pull_requests:write`) — compare URL: `https://github.com/10thMuses/lrp-tx-gis/compare/main...refinement-filter-ui`.

**PR body draft** (paste when opening PR):
- Removes `caramba_south`
- Reorders `tpit_subs` popup → `[name, voltage, operator]`
- Lowers `min_zoom`: `labels_hubs` 5→4, `county_labels` 6→5
- Expands `ercot_queue` popup: adds `technology`, `under_construction`, `inr`, `poi`
- Adds `filterable_fields` on 10 combined-file layers (wells, eia860_plants, eia860_battery, wind, solar, transmission, substations, tpit_subs, tpit_lines, ercot_queue). Prebuilt layers deferred — need lazy `querySourceFeatures` pattern for next iteration.
- `build.py` `compute_filter_stats()` — second pass over split ndjson, numeric → min/max, categorical > 100 distinct auto-demoted to text.
- Template: generic filter UI, null-safe expressions, `filters=` hash round-trip, active-count readout.
- Flag for operator: "road labels" in Stage 1 spec task 3 matches no layer in scope — `tiger_highways` has no text rendering. Interpreted as min_zoom on existing label-geom layers only.

No pending deploys. Prod unchanged since Chat 58.

---

## Recent sessions

| Chat | Date | Outcome |
|---:|---|---|
| 44 | 2026-04-21 | **Hanwha sprint complete.** 22/22 clean, deployId `69e7a7859da0044dc5b0f714`. |
| 48 | 2026-04-21 | **GitHub sync live.** Repo `github.com/10thMuses/lrp-tx-gis`. |
| 52 | 2026-04-21 | **Hanwha polish landed.** 22/22 clean, deployId `69e82c344f3101e36a99b60e`. |
| 53 | 2026-04-21 | `rrc_wells_permian` excluded from scope (MFT GoAnywhere/PrimeFaces AJAX-only). |
| 58 | 2026-04-22 | **Prod recovery + TPIT rename.** Netlify edge 503 recovered via operator manual republish. Fresh TPIT-rename build deployed `69e8e002c4782d80d2949109`. |
| 61 | 2026-04-22 | Cross-project protocol consultation (doc-only). Advisory produced for port. |
| 62 | 2026-04-22 | **10M operating-protocol port executed** (doc-only). `Readme.md` + `docs/` created, `SESSION_LOG.md` → `WIP_LOG.md`, `PROJECT_INSTRUCTIONS.md` + `README.md` deprecated. |
| 63 | 2026-04-22 | **Filter UI stage — recon + design, no code.** Budget spent on data profiles + schema design. Branch `refinement-filter-ui` not pushed; handoff in chat body. Resume next chat. |
| 64 | 2026-04-22 | **Filter UI stage — code pushed, one blocker.** Full implementation committed to `refinement-filter-ui` @ `37cfdaf`. Build runs 20/21; `county_labels` missing from splitter output (pre-existing bug). PR not opened. Resume next chat to diagnose splitter and open PR. |

Full per-session detail in `WIP_LOG.md`.

---

## Prod status

- URL: https://lrp-tx-gis.netlify.app
- Last known published: `69e7a7859da0044dc5b0f714` (Chat 44 Hanwha) OR `69e8e002c4782d80d2949109` (Chat 58 TPIT-rename) if operator has published since. Verify at next session open via MCP.
- Auto-publish: unlocked post-Chat-58.
- Layer set: 22 (county_labels added Chat 52; aquifers dropped Chat 52).
- Display features (cumulative): custom icons, Planned Upgrade styling on tpit_subs/tpit_lines, measure tool (mi + ac), print-to-PDF (landscape + LRP header), 5 basemaps, hover popups, FIELD_LABELS dict, line casings.
- Prebuilt PMTiles: parcels_pecos (4.98 MB), rrc_pipelines (4.73 MB), tiger_highways (3.11 MB), bts_rail (2.16 MB).

---

## Open backlog

**Deferred sources (manual-CSV pattern):**
- `tceq_gas_turbines`, `tceq_nsr_pending`, `tceq_pbr` — CRPUB scrape + Census geocoder. Fossil/emissions scope only. Queued in refinement sequence.
- `tceq_pws` — HTTP 400 on original endpoint; scope-confirm needed at next touch.

**Permanently excluded:**
- `rrc_wells_permian` — see `docs/settled.md` §"Scoped-out data sources".

**Data-pipeline gaps (non-blocking):**
- `combined_points.csv` has blank `operator` / `commissioned` / `technology` / `fuel` / `capacity_mw` on several point layers. Dropped from scope Chat 58. Generic filter UI in refinement sequence provides actual leverage.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar. Fix = tippecanoe-probe subprocess per prebuilt. Not blocking.

**Other open items:**
- Grid Wire Vol. 7.
- Tier 2 water availability assessments, cluster intelligence sheets, Excel returns model.

---

## Refinement sequence queue

Planned discrete shipping chats (full spec in Andrea's project instructions):

1. **Filter UI + yaml piggyback tweaks** (foundation — blocks everything else)
2. **Bug sweep** (Waha, Pecos parcels, measure-tool popup interaction)
3. **Visual overhaul** (contrast, separation, semantic icons via sprite sheet)
4. **MW/kV sizing + confidential watermark** (data-driven icon size + branded export)
5. **Renewable abatement discovery** → **layer build** (Chapter 312/313; 23-county scope)
6. **DC layer research** → **layer build** → **weekly auto-refresh** (GitHub Actions)
7. **TCEQ refresh** → **merge** (nsr / pbr / gas_turbines; fossil/emissions subset)

Parallel-safe (after foundation): abatement research, DC research, TCEQ refresh.

---

## GitHub sync — live

Repo: `github.com/10thMuses/lrp-tx-gis`. Authority: `main` = canonical. Working dir: `/home/claude/repo/`. Protocol: `Readme.md` §7 + `docs/principles.md` §5.
