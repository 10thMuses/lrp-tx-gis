# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

---

## Current workstream

**Stage 3 Visual Overhaul — CLOSED, shipped to prod.** Branch `refinement-visual-overhaul` merged to `main` via `--no-ff` (merge commit `ebe5634`). Remote branch deleted. Palette revision + contrast/weight bump + sprite sheet (5 icons @ 1x + 2x) all live.

**Next refinement stage:** Stage 4 per `docs/refinement-sequence.md`. No active trigger set. Operator picks up on next directed prompt.

---

## Recent sessions

| Chat | Date | Outcome |
|---:|---|---|
| 69 | 2026-04-22 | **Stage 3 Visual Overhaul — recon only.** Branch pushed, handoff doc `b25db48`. No code, no PR. |
| 70 | 2026-04-22 | **Token-efficiency sweep (doc-only).** COMMANDS/ENVIRONMENT/HANWHA archive deleted. GIS_SPEC §12–18 removed. WIP_OPEN trimmed. |
| 71 | 2026-04-22 | **Stage 3 Visual Overhaul closed, deployed to prod.** Branch merged (`ebe5634`), sprite sheet live, remote branch deleted. |

Full per-session detail in `WIP_LOG.md`.

---

## Prod status

- URL: https://lrp-tx-gis.netlify.app
- Last published deploy: `69e95f7ddf3b142326cb43cc` (Chat 71, Stage 3 Visual Overhaul). Root + `/sprite/sprite.png` (image/png, 5108 B) + `/sprite/sprite@2x.png` (11266 B) all returning 200.
- Main HEAD: `ebe5634`.
- Auto-publish: unlocked.
- Layer set: 21 built clean (4 prebuilt PMTiles: parcels_pecos 4.98 MB, rrc_pipelines 4.73 MB, tiger_highways 3.11 MB, bts_rail 2.16 MB).

---

## Open backlog

**Deferred sources (manual-CSV pattern):**
- `tceq_gas_turbines`, `tceq_nsr_pending`, `tceq_pbr` — CRPUB scrape + Census geocoder. Fossil/emissions scope only.
- `tceq_pws` — HTTP 400 on original endpoint; scope-confirm needed at next touch.

**Permanently excluded:**
- `rrc_wells_permian` — see `docs/settled.md` §"Scoped-out data sources".

**Data-pipeline gaps (non-blocking):**
- `combined_points.csv` has blank `operator` / `commissioned` / `technology` / `fuel` / `capacity_mw` on several point layers. Filter UI provides leverage.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar.

**Refinement sequence queue:** see `docs/refinement-sequence.md`.

**Other:**
- Grid Wire Vol. 7.
- Tier 2 water availability assessments, cluster intelligence sheets, Excel returns model.

---

## GitHub sync — live

Repo: `github.com/10thMuses/lrp-tx-gis`. Authority: `main` = canonical. Working dir: `/home/claude/repo/`. Protocol: `Readme.md` §7 + `docs/principles.md` §5.
