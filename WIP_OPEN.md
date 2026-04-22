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
| 66 | 2026-04-22 | **Bug sweep recon + §7.7 Readme rule.** Branch `refinement-bug-sweep` cut from `main`. Handoff doc `docs/_stage2_handoff.md` committed with 3-bug scope + recon. Added Readme §7.7 (mid-chat handoff on context exhaustion) on `main` (`9fd44b0`). |
| 67 | 2026-04-22 | **Stage 2 fixes 1+2 shipped to branch.** Fix 1: added `glyphs` URL to `rasterStyle()` + `text-font: ['Noto Sans Bold']` (Waha label now renders on raster basemaps). Fix 2: `build.py` prebuilt fetcher rewritten with HEAD probe + chunked Range GETs + exponential backoff (parcels_pecos tier-3 resilient to container egress 503). Branch @ `c8cbd68`. Also: Readme §7.7 rewritten to "progress over summary — continuous commit, minimum chat message" (`dbb86d8`). Fix 3 (measure/popup) + build verify + PR pending next chat. |
| 68 | 2026-04-22 | **Stage 2 Bug Sweep merged to `main`.** Fix 3 (measure/popup) shipped (`fc81eb0`): CSS `.measure-on .maplibregl-popup { display: none }` + class toggle + `hoverPopup.remove()` on activate. Handoff doc deleted (`ecd1eec`). Branch merged to `main` via `git merge --no-ff`. Local build 21/21 clean. Readme §7.8 added: "Always ship before handoff" + handoff-doc voice (instructions addressed to next Claude, not operator — fixes ambiguity that stalled Chat 68). No prod deploy. |
| 69 | 2026-04-22 | **Stage 3 Visual Overhaul — recon only, branch pushed.** `refinement-visual-overhaul` cut from `main`. Handoff doc `docs/_stage3_handoff.md` (`b25db48`) covers palette revision (resolve pipelines/TPIT blue ambiguity), contrast/weight bumps in `layerPaint()`, sprite-sheet replacement for emoji `ICON_MAP` (5 icons: solar/wind/battery/plant/well), 4-commit cadence, PR + WIP sequence. No code edits, no build run, no PR. Resume next chat. |

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
