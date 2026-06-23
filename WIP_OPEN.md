# WIP_OPEN.md

Active work + execution queue. Updated when something completes or a new sprint
item is added. Round/decision-log history is archived in
`docs/archive/wip_history_pre_2026-05-18.md`; layer/schema canonical detail in
`ARCHITECTURE.md`; multi-step task breakdowns in `docs/sprint-plan.md`.

---

## Last deploy

`6a3adddefa163a0a17902c54` — 2026-06-23. 39 layers. Build clean
`built=39 missing=0 errored=0 tiles_total=29594 KB`. Added `oxy_drilling_permits`
(294 OXY/Occidental RRC W-1 permits 2020-2026); upgraded 4 OXY carbon/midstream
points to precise sourced coords; `raiseOxy()` draw-order fix.

Older deploy history: `git log --merges --grep "deploy [0-9a-f]" main`.

---

## Queue (resume pointer)

The single `## Next chat` pointer convention was retired at the Round-26
restructure. The canonical queue is this section plus `## Active sprints`.
Resume trigger `resume.` = clone, read this `## Queue`, execute the top
unblocked item on a fresh `refinement-<slug>` branch per `OPERATING.md §4`.

**2026-05-18 — two operator batches, all shipped** (deploy IDs + full detail in `git log --merges`):
- Batch 1: doc/audit hygiene · counties `#fbbf24`→`#64748b` · mobile-popup audit (clean) · wells `filterable_fields` +8 / `permits_permian6` `sidebar_omit` (+`build.py` standalone-ndjson fix).
- Batch 2: county_labels visibility · removed `counterparty_assets` (33→32) · wells own `Wells` group / −5 filters / `exclude_within` Caramba (−9 wells) · wells spud thesis XLSX+PDF export (+`write_stats_attrs` ndjson source).

No pending operator-queued items — see `## Active sprints` + `## Backlog`.

---

## Active sprints

### ERCOT queue geocoding — Stage 3

**Status:** blocked on operator-curated override CSV at `data/ercot_queue_overrides.csv`.

**Spec** (settled, do not re-litigate):
- WRatio ≥ 88 (rapidfuzz partial_ratio fallback to ratio)
- Norm-name suffix-stripping: drop `LLC`, `INC`, `LP`, `LTD`, `CORP`, `CO`, trailing parenthetical project codes
- Idempotent CSV read — re-running the geocode pass with the same CSV produces no diff
- Last-precedence pass — manual override always beats Stage 1+2 algorithmic match
- `coords_source = manual_override` for all rows touched by Stage 3
- Atomic write per `OPERATING.md §3 rule 4` — temp file + `os.replace`

**Resume:** when CSV exists, run `python3 scripts/geocode_ercot_queue.py --stage 3` (verify against Stage 2 invocation pattern). Then full build, deploy, verify aggregate match rate vs Stage 2 baseline, commit + merge.

**Acceptance:** `coords_source = manual_override` rows in built registry equal CSV row count; aggregate solar+wind+battery match rate logged and improved vs Stage 2; no regression in Stage 1+2 rows.

### county_labels render review

If operator-named counties still appear unlabeled at zoom 7–9, inspect MapLibre
`text-allow-overlap` / `symbol-sort-key` / `text-padding` on the county_labels
source-layer config in `build_template.html`. Conditional on visual
confirmation the issue still exists.

---

## Backlog

### Infrastructure
- Akamai datacenter-egress block on `reevescounty.org` 403s any cloud-runner traffic regardless of UA/TLS. Hard prerequisite for the Reeves abatement-weekly-cron item. Unblock paths: residential-proxy egress (paid), Akamai allowlisting via Reeves IT (low likelihood), search-API result pages.
- `GITHUB_PAT` can push branches + merge, 403 on PR creation. Direct-merge-to-main is the protocol per `OPERATING.md §6`.

### Data
- ✅ Shipped 2026-06-23: `oxy_drilling_permits` layer — `scripts/build_oxy_drilling_permits.py` filters the RRC daf420 EOM master+lat/lon snapshots (dual 0108/0109 record-format reader) to OXY operators (#630591, #617544, OXY USA WTP LP), 294 unique permits 2020-2026, operator-reported coords. Off by default; filter by operator/county/year. Refresh: `python3 scripts/fetch_rrc.py permits` (most-recent monthlies are NOT in folder-tail order — pull by parsed date) → `python3 scripts/build_oxy_drilling_permits.py`.
- ❌ NOT feasible — `oxy_minerals_pecos` (OXY mineral ownership, Pecos): Texas mineral ownership is **not** public GIS geometry. Free public data yields only a non-spatial owner roll (Pecos CAD certified mineral roll, Pickett-appraised; or paid aggregators TexasFile/MineralHolders) keyed to abstract/survey legal descriptions — **no polygons/coords**. GLO publishes state-owned mineral geometry only; StratMap `parcels_pecos` is **surface**, not mineral. A true mineral-footprint map needs paid data + deed-by-deed title platting (hand-coding coords — barred by hard rule 3). Deliverable if wanted: a sourced OXY mineral-account *table*, optionally shaded at abstract level, not a tract-precise layer.
- RRC permits 1976–2017 backfill: overnight W-1 scrape; scratch in `outputs/refresh/rrc_w1_*` (gitignored). When `rrc_w1_permits_with_coords.csv` is complete: `python3 scripts/parse_rrc.py permits` (auto-merges, deduped by permit_no+api_no) → `python3 build.py` → deploy.
- HIFLD remaining layers; ERCOT deeper geocoding (FERC EQR + PUC CCN); counterparty boundary precision upgrade. Detail in `docs/sprint-plan.md` + archive.

### UI / UX
- ✅ Fixed 2026-05-18: `GROUP_ORDER` += `Energy Infrastructure` (deploy `6a0b3441…` — 4 `hifld_*` layers now render in sidebar); `value_labels` pass-through in `render_html` (deploy `6a0b34a3…` — plug_flag/active_flag show friendly labels).
- No-browser-env note: county_labels (visual) + the **Spuds Summary (PDF)** export (PDF-only button in the Wells stats panel) verified via config/bundle/math re-derivation, not in-browser render — eyeball once on prod.
- Standalone-layer filter panels now render (2026-05-18 `build.py` fix): `hifld_*` (and `permits_permian6`, though sidebar-hidden) gained their declared filter UIs — previously silently empty. Intended; noted for awareness.
- `date_range` filter for eia860_plants/battery/wind needs `yyyy`→`yyyy-01-01` padding in 3 ingest scripts; low priority (numeric year-slider works).
- Filter inputs 40px on mobile vs 44px WCAG; acceptable per Apple HIG (≥40px); flag if operator testing surfaces hit-rate issues.

### Audit drift (`bash scripts/audit.sh`)
`OPERATING.md` ≤250 lines · `WIP_OPEN.md` ≤8192 bytes · 0 stranded `refinement-*`/`claude/*` branches on origin · close-out conformance 100%.

**Stranded branches — resolved 2026-05-18 (operator decision):** `dc-anchors-refresh-3/4/5/6` deleted (stale unreviewed proposals; canonical `dc_anchors` is on main). `refinement-chat127-drilling-permits-point` archived to `docs/archive/chat127-drilling-permits-point.patch` (full `drilling_permits` scaffolding; re-apply via `git am`), branch deleted. Origin stranded-branch count → 0.

---

## Process notes

- `scripts/close-out.sh` enforces atomic deploy+merge and the `refinement-*` branch lifecycle. Use it; don't hand-roll merges to `main`.
- `scripts/audit.sh` is cheap; include it in verification for medium/high blast-radius work.
- The `/*__BUILD_ID__*/` token substitution in `build.py:render_html` (UTC timestamp + nonce) makes `deploy.sh`'s md5-parity poll a reliable readiness signal. Removing the marker breaks the poll.
- Daily probe + W-1 backfill scratch (`data/abatements/abatement_hits_*.csv`, `outputs/refresh/rrc_w1_*`) are gitignored — the unattended daily-refresh routine must never commit them.
