# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

---

## Current workstream

**TCEQ REFRESH — Chat 72 in progress on branch `refinement-tceq-refresh` (HEAD `606b277`, pushed, not merged).** Bulk-source recon completed; `tceq_gas_turbines` pulled from `turbine-lst.xlsx` v2026.4.3 — 6 rows, 23-county West TX, Received ≥ 2020, Issued sheet only, 6/6 geocoded via Nominatim (Census zero-match fallback). Data + script + changelog + source archive committed to branch. **Chat 73 folds TCEQ MERGE into the same ship:** merge branch to main direct, append 6 rows to `combined_points.csv`, add layer to `layers.yaml` under new "Permits" group, build, deploy, write 3 `settled.md` entries (tceq_pws drop, tceq_pbr scope-out, Nominatim fallback).

**Parallel-safe queue after TCEQ MERGE:** ABATEMENT BUILD, DC RESEARCH/BUILD.

---

## Recent sessions

| Chat | Date | Outcome |
|---:|---|---|
| 69 | 2026-04-22 | **Stage 3 Visual Overhaul — recon only.** Branch pushed, handoff doc `b25db48`. No code, no PR. |
| 70 | 2026-04-22 | **Token-efficiency sweep (doc-only).** COMMANDS/ENVIRONMENT/HANWHA archive deleted. GIS_SPEC §12–18 removed. WIP_OPEN trimmed. |
| 71 | 2026-04-22 | **Stage 3 closed + Stage 4 SIZING+WATERMARK shipped.** Merges `ebe5634` + `026eff2`. Prod deploys `69e95f7d` + `69e96a36`. Sprite sheet + data-driven sizing + CONFIDENTIAL watermark all live. TCEQ REFRESH deferred pending operator scope ask. |
| 72 | 2026-04-23 | **TCEQ REFRESH recon + gas-turbine data pull.** Bulk source found (`turbine-lst.xlsx`). Branch `refinement-tceq-refresh` HEAD `606b277` pushed. 6 records, 6/6 geocoded. `tceq_pws` + `tceq_pbr` + `tceq_nsr_pending` scoped out. TCEQ MERGE folded into Chat 73. No deploy. |

Full per-session detail in `WIP_LOG.md`.

---

## Prod status

- URL: https://lrp-tx-gis.netlify.app
- Last published deploy: `69e96a36b4de5c3af264ab27` (Chat 71, Stage 4 Sizing + Watermark).
- Main HEAD: `026eff2` (pending final WIP-close commit).
- Auto-publish: unlocked.
- Layer set: 21 built clean (4 prebuilt PMTiles: parcels_pecos 4.98 MB, rrc_pipelines 4.73 MB, tiger_highways 3.11 MB, bts_rail 2.16 MB).
- Sprite sheet: 5 icons @ 1x + 2x at `/sprite/sprite.png` + `sprite@2x.png`.
- Data-driven sizing live on: `ercot_queue`, `solar`, `eia860_battery`, `wind` (MW scaling); `substations`, `tpit_subs`, `tpit_lines` (kV scaling).
- Sizing gaps flagged in code: `eia860_plants` (capacity_mw blank 1367/1367), `transmission` (no voltage in geoms) — static fallback.

---

## Open backlog

**Deferred sources:**
- `tceq_nsr_pending` — indefinite defer. No bulk source exists; CRPUB HTML-scrape authorization declined. Revisit only if TCEQ publishes a bulk feed or if operator authorizes scrape. See Chat 72 recon in `outputs/refresh/CHANGELOG.md`.

**Permanently excluded (pending `settled.md` entry in Chat 73):**
- `tceq_pws` — HTTP 400 on endpoint, operator drop 2026-04-23.
- `tceq_pbr` — CRPUB scrape analog to RRC-MFT precedent. Same per-chunk data-source-shape principle.
- `rrc_wells_permian` — see `docs/settled.md` §"Scoped-out data sources".

**Standing watch item:** TCEQ diesel-genset NSR permits live only in CRPUB (not in `turbine-lst.xlsx`). Gap for data-center backup-power intelligence if that becomes a use case.

**Data-pipeline gaps (non-blocking):**
- `combined_points.csv` has blank `operator` / `commissioned` / `technology` / `fuel` / `capacity_mw` on several point layers. Filter UI provides leverage.
- `eia860_plants` capacity_mw blank — sizing falls back to static radius. Refresh EIA-860 data when convenient.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar.

**Refinement sequence queue:** see `docs/refinement-sequence.md`. Next: ABATEMENT DISCOVERY (parallel-safe) or ABATEMENT BUILD (depends on DISCOVERY) or DC stages.

**Other:**
- Grid Wire Vol. 7.
- Tier 2 water availability assessments, cluster intelligence sheets, Excel returns model.

---

## GitHub sync — live

Repo: `github.com/10thMuses/lrp-tx-gis`. Authority: `main` = canonical. Working dir: `/home/claude/repo/`. Protocol: `Readme.md` §7 + `docs/principles.md` §5.
