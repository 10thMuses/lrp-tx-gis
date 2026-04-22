# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

---

## Current workstream

**Stage 3 — Visual Overhaul, RECON ONLY.** Branch `refinement-visual-overhaul` cut from `main` and pushed. Handoff doc `docs/_stage3_handoff.md` committed to branch (`b25db48`) with palette revision, contrast/weight bump, sprite-sheet implementation plan, build + commit cadence, PR + WIP close-out sequence.

No code written. No `layers.yaml` / `build_template.html` / `build.py` edits on branch. No build run. No PR open.

**Next-chat trigger:** `resume visual overhaul` (or `continue stage 3`). Next chat clones, checks out `refinement-visual-overhaul`, reads `docs/_stage3_handoff.md`, executes unconditionally per §7.8 (no operator gate), deletes handoff doc at end, opens PR, updates WIP.

No pending deploys. Prod remains on Chat 58's TPIT-rename deploy (`69e8e002c4782d80d2949109`) or its successor — verify at session open.

---

## Recent sessions

| Chat | Date | Outcome |
|---:|---|---|
| 68 | 2026-04-22 | **Stage 2 Bug Sweep merged to `main`.** Fix 3 (measure/popup) shipped (`fc81eb0`). 21/21 clean. No prod deploy. |
| 69 | 2026-04-22 | **Stage 3 Visual Overhaul — recon only.** Branch pushed, handoff doc `b25db48`. No code, no PR. |
| 70 | 2026-04-22 | **Token-efficiency sweep (doc-only).** COMMANDS/ENVIRONMENT/HANWHA archive deleted. GIS_SPEC §12–18 removed. WIP_OPEN trimmed. principles.md cleanup items closed. Memory `recent_updates` pruned. |

Full per-session detail in `WIP_LOG.md`.

---

## Prod status

- URL: https://lrp-tx-gis.netlify.app
- Last known published: `69e8e002c4782d80d2949109` (Chat 58 TPIT-rename). Verify at next session open via MCP.
- Auto-publish: unlocked post-Chat-58.
- Layer set: 22.
- Prebuilt PMTiles: parcels_pecos (4.98 MB), rrc_pipelines (4.73 MB), tiger_highways (3.11 MB), bts_rail (2.16 MB).

---

## Open backlog

**Deferred sources (manual-CSV pattern):**
- `tceq_gas_turbines`, `tceq_nsr_pending`, `tceq_pbr` — CRPUB scrape + Census geocoder. Fossil/emissions scope only.
- `tceq_pws` — HTTP 400 on original endpoint; scope-confirm needed at next touch.

**Permanently excluded:**
- `rrc_wells_permian` — see `docs/settled.md` §"Scoped-out data sources".

**Data-pipeline gaps (non-blocking):**
- `combined_points.csv` has blank `operator` / `commissioned` / `technology` / `fuel` / `capacity_mw` on several point layers. Dropped Chat 58. Filter UI provides leverage.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar.

**Refinement sequence queue:** see `docs/refinement-sequence.md`.

**Other:**
- Grid Wire Vol. 7.
- Tier 2 water availability assessments, cluster intelligence sheets, Excel returns model.

---

## GitHub sync — live

Repo: `github.com/10thMuses/lrp-tx-gis`. Authority: `main` = canonical. Working dir: `/home/claude/repo/`. Protocol: `Readme.md` §7 + `docs/principles.md` §5.
