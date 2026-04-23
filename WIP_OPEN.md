# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

---

## Current workstream

**Stage 4 SIZING + WATERMARK — CLOSED, shipped to prod.** Data-driven MW/kV scaling on 7 layers, CONFIDENTIAL watermark on-map + print.

**Next work, awaiting scope input from operator:** TCEQ REFRESH stage (`refinement-tceq-refresh`). Four sub-questions flagged at Chat 71 close — see ask block at bottom of `WIP_LOG.md` Chat 71 entry. Cannot start without scope confirmation on (a) `tceq_pws`, (b) scrape vs. bulk-download vs. operator-CSV approach, (c) geographic scope, (d) permit-type filters.

**Parallel-safe queue (Stage 4 merged):** ABATEMENT BUILD, DC RESEARCH/BUILD, TCEQ REFRESH.

---

## Recent sessions

| Chat | Date | Outcome |
|---:|---|---|
| 69 | 2026-04-22 | **Stage 3 Visual Overhaul — recon only.** Branch pushed, handoff doc `b25db48`. No code, no PR. |
| 70 | 2026-04-22 | **Token-efficiency sweep (doc-only).** COMMANDS/ENVIRONMENT/HANWHA archive deleted. GIS_SPEC §12–18 removed. WIP_OPEN trimmed. |
| 71 | 2026-04-22 | **Stage 3 closed + Stage 4 SIZING+WATERMARK shipped.** Merges `ebe5634` + `026eff2`. Prod deploys `69e95f7d` + `69e96a36`. Sprite sheet + data-driven sizing + CONFIDENTIAL watermark all live. TCEQ REFRESH deferred pending operator scope ask. |

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

**Deferred sources (manual-CSV pattern) — pending scope confirmation:**
- `tceq_gas_turbines`, `tceq_nsr_pending`, `tceq_pbr` — CRPUB scrape + Census geocoder per TCEQ REFRESH stage spec.
- `tceq_pws` — HTTP 400 on original endpoint; scope-confirm needed.

**Permanently excluded:**
- `rrc_wells_permian` — see `docs/settled.md` §"Scoped-out data sources".

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
