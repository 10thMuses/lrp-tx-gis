# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

---

## Current workstream

**Stage 2 — Bug Sweep.** Filter UI (Stage 1) merged to `main` via PR from `refinement-filter-ui`; no prod deploy yet (filter UI ships alongside bug-sweep fixes per refinement sequence, unless operator triggers earlier).

**Next-chat trigger:** `open bug sweep` or `start stage 2`. Scope per `docs/refinement-sequence.md` §Stage 2:
- Waha hub icon/labeling verification
- `parcels_pecos` zoom/visibility behavior
- Measure-tool interaction with popups (click-through suppression)
- Cosmetic prebuilt feature-count 0s in sidebar (deferred-probe fix if budget permits)

No pending deploys. Prod remains on Chat 58's TPIT-rename deploy (`69e8e002c4782d80d2949109`) or its successor — verify at session open.

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
| 64 | 2026-04-22 | **Filter UI Stage 1 code shipped to branch.** `refinement-filter-ui` pushed (commit `a437329`). yaml + build.py (`compute_filter_stats`) + template (`FILTER_STATE`, `buildFilterExpression`, `renderFilterPanel`, `ensureLazyStats`) edits. 21 layers (caramba_south deleted), 12 with `filterable_fields`. Popup copy-lock applied. Local build 20/20 OK (`county_labels` errored — deferred). PR + WIP update deferred. |
| 65 | 2026-04-22 | **Filter UI Stage 1 closed.** Root-cause `county_labels` failure: `build.py` split pass read `PROJECT / COMBINED_GJ` (stale sidebar) instead of `ROOT / COMBINED_GJ` (repo canonical). Two-line fix committed (`f829bb6`). Local build 21/21 OK. PR opened + merged to `main`. No prod deploy (ships with Stage 2 Bug Sweep). |

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
