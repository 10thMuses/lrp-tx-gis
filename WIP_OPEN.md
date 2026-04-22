# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

---

## Current workstream

**Filter UI stage — recon + design complete, zero code committed.** Chat 63 burned budget on recon (data profiles for all 11 combined-file layers + 13 geom layers) and locked the design. Branch `refinement-filter-ui` created locally but NOT pushed; no commits exist. Next chat resumes at code-write phase.

**Next-chat resume trigger:** `continue filter ui stage` or `resume filter ui`. First action: `conversation_search` on "filter ui" keywords — full handoff (yaml edits, filterable_fields tables, build.py changes, template JS patterns, PR body) is in Chat 63 body per `Readme.md` §10.

**Condensed design summary** (full detail in Chat 63 handoff):

- `layers.yaml`: delete `caramba_south`; reorder `tpit_subs` popup → `[name, voltage, operator]`; lower `min_zoom` on `labels_hubs` (5→4) and `county_labels` (6→5); expand popup lists per layer (whitelist — do NOT auto-include `caramba_north` internal metadata); add new `filterable_fields: [{field, type, label?}]` key per filter-eligible layer.
- `build.py`: in split pass, track per-field stats for declared `filterable_fields` (numeric → min/max; categorical → sorted distinct capped at 100 else fall back to text); embed in `render_html` registry.
- `build_template.html`: collapsible per-layer filter panel in sidebar; numeric=range inputs, categorical=multi-select, text=contains; apply via `map.setFilter` on `lyr_<id>` + `__casing`/`__outline`/`__icon` companions; null-safe expressions wrapped in `['has', field]`; hash round-trip via new `filters=` key; prebuilt layers populate values lazily via `querySourceFeatures` on first open.
- Verify: `python3 build.py` exits 0, layer count drops from 22 → 21 (caramba_south gone).
- PR to main with body including: open question on "road labels" (no such layer exists — interpreted as lowering min_zoom on existing label-geom layers; flagged for confirmation).

No pending deploys. Prod is on Chat 58's TPIT-rename deploy (`69e8e002c4782d80d2949109`) or its successor — verify at next session open.

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
