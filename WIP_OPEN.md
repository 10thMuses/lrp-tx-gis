# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat

**Chat 116 — ERCOT QUEUE GEOCODING SPRINT STAGE 3: operator-curated manual overrides.** Re-promoted from Chat 115 (Chat 115 reduced to handoff-write only because operator-gated Stage 3 input was again absent at session-open; Chat 114 had previously displaced the same task to a WAHA paint-order fix for the same reason). Stage 2 (Chat 113) hit a structural ceiling at 27.0% solar+wind+battery match rate; the 60% target from the Chat 113 WIP is dropped per operator-acknowledged data limits (see Pre-flight below). Stage 3 trades programmatic breadth for surgical precision on high-value rows where Stage 2 missed.

### Task

1. **Operator provides** a manual-override CSV at `data/ercot_queue_overrides.csv` with columns `inr,lat,lon,override_reason` (inr = ERCOT INR id, the queue row's stable identifier; override_reason free text). If file absent at session-open, Chat 116 reduces to handoff-write only.
2. Add a Stage 2.d pass to `scripts/geocode_ercot_queue.py`: load the override CSV, build an `inr → (lat, lon, reason)` map, and apply LAST in the pipeline. Override stamps take precedence over ALL upstream stages (operator authority) and snap to the override coords with `coords_source = manual_override`. Reason logged in run log; not stamped on the row (no schema change).
3. Atomic write per §6.15.
4. Append run log with: total override rows, INRs not found in queue (warn, do not fail), per-bucket override count, before/after match-rate delta.
5. Build → deploy to prod per §8.

### Acceptance

- Build clean: `built=26 missing=0 errored=0`.
- ercot_queue feature count unchanged (1,778).
- Every override-CSV INR present in queue is stamped `manual_override`.
- Override INRs not found in queue logged as warnings (do not fail the run).
- Local↔prod md5 identical.
- Branch merged + deleted same chat per §6.12.

### Branch

`refinement-chat116-ercot-overrides`

### Pre-flight

- Chat 115 was a handoff-write-only chat. Override CSV absent at `data/ercot_queue_overrides.csv` at session-open, so per the Chat 115 task spec item 1, the chat reduced to WIP rewrite + close-out: Stage 3 re-promoted to Chat 116, deploy log marked no-deploy, branch `refinement-chat115-handoff` merged to main with `(no deploy)` tag. Layer count 24 unchanged. Last published deploy still Chat 114 `69f10553bbc94b136581c584`. Second consecutive session reduced for the same input-precondition gap; if Chat 116 also opens without the CSV, operator should consider whether Stage 3 is the right next-chat task or whether the sprint queue should be reordered.
- Chat 114 shipped clean. Deploy `69f10553bbc94b136581c584` (2026-04-28). WAHA paint-order fix: layers.yaml reorder moved `waha_circle` and `labels_hubs` to before `la_escalera` (now at LAYERS array indices 4-5 vs campus polygons at 6-8). Local↔prod md5 identical (`2f8f2597c2aa3b08766cd27378b5308f`). Build clean: `built=26 missing=0 errored=0 tiles_total=11606 KB`. Sidebar Local Focal Points group within-order changed from solstice → mpgcd_zone1 → waha to solstice → waha → mpgcd_zone1 (cosmetic side effect; sidebar group order unchanged via GROUP_ORDER constant in template). The Chat 114 Stage-3 spec is re-promoted unchanged below; only the chat number, branch name, and deploy ID are updated.
- Chat 113 shipped clean. Deploy `69f0c593e361c81f37ca36ee` (2026-04-28). Match counts: Stage 1 eia860 324, uswtdb 10; Stage 2 tpit_poi 78, substation_poi 67, dc_anchors 0; county_centroid 1,299. Aggregate solar+wind+battery 452/1,676 (27.0%).
- **Structural ceiling on programmatic match rate.** TPIT (141 planned-upgrade substations) + OSM substations (1,637 rows, only 792 indexable after no-county / no-name drops) cannot cover queue projects whose POI substations are being built FOR the project (not in either source) or named ambiguously ("138kV tap to Line X" with no substation handle). Further programmatic lift requires new data sources (e.g., ERCOT GIS Report substation tabular layer, FERC Form 715), not in scope here.
- Stage 2 scope assumption noted: WIP_OPEN named TPIT + dc_anchors as the two passes; per OPERATING.md §7 ambiguity rule, Chat 113 added a third Stage-2 pass against the OSM `substations` layer (same matching kernel, distinct `substation_poi` provenance) to chase the 60% target. Three Stage-2 passes within one chat; no §6.13 violation. dc_anchors pass stamped 0 rows — no curated tenant alias matched any same-county queue row, expected for a forward-looking generation queue where anchor tenants don't typically appear as queue developers.
- Override application is idempotent: re-running the pipeline with the same override CSV produces the same coords. Operator can edit the CSV and re-run anytime.
- WRatio threshold (88) and norm_name / norm_substation_name suffix-stripping settled in Chat 113. Do not retune in Stage 3.

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### ERCOT QUEUE PRECISE GEOCODING

**Multi-chat sprint.** Stage 2 (Chat 113) hit a structural data-coverage ceiling. Stage 3 has been queued for three consecutive next-chat slots (originally Chat 114, then Chat 115, now Chat 116) but each has opened without the operator-curated override CSV at `data/ercot_queue_overrides.csv`.

- **Stage 1 (Chat 112, shipped):** EIA-860 + USWTDB joins. Aggregate match rate 18.4% (309/1,676 solar+wind+battery). Structural ceiling — EIA-860 indexes operating plants while queue is forward-looking by design.
- **Stage 2 (Chat 113, shipped):** TPIT POI proximity (78 matches), OSM substations POI proximity (67 matches; added per §7 ambiguity rule beyond the named TPIT scope), dc_anchors exact-alias (0 matches; no curated tenant alias hit any same-county queue row). Aggregate solar+wind+battery 27.0% (452/1,676) — below the 60% target. Structural ceiling: queue POI universe includes substations being built FOR the project (not in TPIT or OSM today) or named ambiguously without a substation handle. Further programmatic lift requires new substation sources not currently in scope.
- **Stage 3 (Chat 116, promoted to Next chat):** operator-curated manual override CSV at `data/ercot_queue_overrides.csv`, applied as a final precedence-winning pass. Idempotent; operator can edit and re-run anytime. (Chat 114 displaced to WAHA paint-order fix and Chat 115 reduced to handoff-write only, both because Stage 3 input was absent at session-open. If the CSV is absent at Chat 116 open, operator should consider whether to deprioritize Stage 3 or substitute alternative work.)

### DATE-RANGE FILTER FOR `tax_abatements.commissioned`

True range slider replacing current text-multi-select on distinct ISO dates. Touches `build.py compute_filter_stats` + `build_template.html filterFieldControlHtml` + matching predicate. 1–2 chats. **Deferred** — operator's chat-110/111 series surfaced higher-priority data-quality work above.

### COMPTROLLER LDAD SCRAPE

Operator authorized Chat 106a. Playwright headless against `https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`. Paginate result pages, write to `outputs/refresh/comptroller_ldad_<date>.csv`, merge into `tax_abatements` layer. Provides statewide abatement coverage to complement existing 9 county-scraped records. 1–2 chats.

### COUNTY_LABELS RENDER REVIEW (CONDITIONAL)

If post-Chat-111 visual review confirms operator-named counties still appear unlabeled at zoom 7–9, root cause is symbol-collision declutter or min_zoom gating, not data. Diagnostic chat: inspect MapLibre `text-allow-overlap` / `symbol-sort-key` / `text-padding` on the county_labels source-layer config in `build_template.html`. Likely 1 chat. **Conditional on visual confirmation** — do not pre-empt operator review.

### MOBILE STAGE 3 — HOTFIX ON DEMAND

Cross-device QA + polish for the mobile-friendly map work shipped in Chats 100–101. Not scheduled. Surfaced issues become discrete patch chats. 0–1 chat per issue.

---

## Prod status

- Layer count: **24** (display layers — `county_labels` + `counties` count once each in the registry)
- Last published deploy: `69f10553bbc94b136581c584` (Chat 114, 2026-04-28). State=ready. WAHA paint-order fix: `waha_circle` (lines 559-578) and `labels_hubs` (lines 579-595) moved before `la_escalera` (line 82) in `layers.yaml`, so MapLibre `addLayer` iteration paints WAHA marker + label BEFORE Hyperscale campus polygons, putting the campus polygon strokes ON TOP. LAYERS array indices: solstice_substation 3, waha_circle 4, labels_hubs 5, la_escalera 6, longfellow_ranch 7, gw_ranch 8, mpgcd_zone1 9. Sidebar Local Focal Points group within-order changed from solstice → mpgcd_zone1 → waha to solstice → waha → mpgcd_zone1 (mild cosmetic side effect; labels_hubs `sidebar_omit: true` so unaffected). GROUP_ORDER constant in `build_template.html` unchanged, so cross-group sidebar order intact. Build clean: `built=26 missing=0 errored=0 tiles_total=11606 KB` (unchanged from Chat 113). Local↔prod md5 identical (index.html `2f8f2597c2aa3b08766cd27378b5308f`). Operator-visible result: GW Ranch's 3.5-mi-wide red campus stroke renders unobscured at all zooms. WAHA hub readability preserved (radius/styling untouched).
- Chat 115 (2026-04-28): **no deploy.** Handoff-write only. Override CSV absent at `data/ercot_queue_overrides.csv` at session-open, so per the Chat 115 task spec item 1 the chat reduced to WIP rewrite + close-out: Stage 3 re-promoted to Chat 116, sprint queue updated, branch `refinement-chat115-handoff` merged to main with `(no deploy)` tag. Layer count, schema, prod artifacts all unchanged from Chat 114.
- Previous deploy: `69f0c593e361c81f37ca36ee` (Chat 113, 2026-04-28). State=ready. ERCOT queue geocoding Stage 2: 78 rows matched via TPIT POI proximity (planned-upgrade substations, fuzzy WRatio≥88, same-county via TIGER 2024 point-in-polygon county derivation), 67 rows via OSM substations layer (same matching kernel, distinct `substation_poi` provenance), 0 rows via dc_anchors exact-alias match. Final coords_source distribution: county_centroid 1,299; eia860 324; tpit_poi 78; substation_poi 67; uswtdb 10. Build clean: `built=26 missing=0 errored=0 tiles_total=11606 KB`. Local↔prod md5 identical (index.html `0b630fd927c6d76adbb1ee8e9a518a6c`; ercot_queue.pmtiles `dbff4c440340bee1ebb2dcd0572a3851`). Aggregate solar+wind+battery match rate 27.0% (452/1,676) — below 60% target for structural reasons (queue POI universe extends beyond available substation catalogs). Stage 2 scope assumption: WIP named two passes (TPIT + dc_anchors); per §7 ambiguity rule, Chat 113 added a third pass against OSM substations to chase the target.
- Previous deploy: `69f0ad1c2ffe34b3320d0e1e` (Chat 112, 2026-04-28). State=ready. ERCOT queue geocoding Stage 1: 334 rows matched via EIA-860 (324) + USWTDB (10); 1,444 retained existing approximate coords with `coords_source=county_centroid` provenance label. New `coords_source` field stamped on all 1,778 ercot_queue rows. Build clean: `built=26 missing=0 errored=0 tiles_total=11603 KB`. Local↔prod md5 identical (`0b630fd927c6d76adbb1ee8e9a518a6c`).
- Previous deploy: `69f01efe66cedded36ed2e99` (Chat 111, 2026-04-28). State=ready. `county_labels` extended 46 → 254 (all TX counties via TIGER 2024). Local↔prod md5 identical (`4fb699f478ad530c04f44ab350493bd1`). Build clean: `built=26 missing=0 errored=0 tiles_total=11595 KB`.
- Previous deploy: `69f008f6187338b50dc2a829` (Chat 110c, 2026-04-28). State=ready. Transmission & Grid reorder + tpit_subs recolor + Longfellow polygon move.
- Previous deploy: `69f00661239f04d4b9bec06f` (Chat 110b, 2026-04-28). Hotfix: `fill-opacity || 0.25` → `?? 0.25`; `mpgcd_zone1` default_on true.
- Previous deploy: `69efdc12326f632c49033ed2` (Chat 110, 2026-04-27). Sidebar overhaul.
- Previous deploy: `69ef926ed31a462a98b27f77` (Chat 109b, 2026-04-27). State=ready. Hyperscale DC & Power Campuses group consolidation + WAHA Pecos fix + Solstice visibility.
- Previous deploy: `69ef8b0a7ca58c0d4d25ae4d` (Chat 108b, 2026-04-27). State=ready. Local Developments group + popup audit + permit visibility.
- Previous deploy: `69ee7b6cffaa366af764784c` (Chat 107d, 2026-04-26). State=ready. Critical bug fix on top of 107c: build.py was defaulting `line_width` to **2** in the layer registry render path (line 825), overriding template defaults — so the JS template's 0.5 default never took effect. Fixed: `'line_width': L.get('line_width', 0.5)`. Also: county_labels switched to dark text (`#0f172a`) with halo opt-out via new `text_halo: false` YAML flag; template halo logic now auto-picks contrast (light text → dark halo, dark text → light halo). Counties `line_width` raised 0.5 → 1. county_labels `min_zoom: 4 → 5`.
- Previous deploy: `69ee76fc43cd26b6f3460922` (Chat 107c, 2026-04-26). State=ready. Contrast/legibility/fuel pass.
- Previous deploy: `69ee72bcbd5d65c5bac1e0eb` (Chat 107a, 2026-04-26).
- Previous deploy: `69ee25b25be421df2f22b294` (Chat 105, 2026-04-26). PMTiles feature counts fix for prebuilt layers.
- Previous deploy: `69ee07134b63d09184004cf9` (Chat 102, 2026-04-26). State=ready. ERCOT queue project aggregation popup. `compute_ercot_group_aggregates(csv_path)` streams `combined_points.csv` once and returns `{group_key: {group_total_mw, group_count, group_breakdown}}` (breakdown is `\n`-joined `<n> · <mw> MW · <county>` lines, sorted by MW desc). `split_combined_csv()` stamps these fields onto every ercot_queue feature's props during NDGeoJSON write. Popup helper `ercotQueueGroupSummaryHtml(props)` renders a summary block (sage-pink card with project group label, total MW, component count, breakdown list) above the per-row table when `group_count > 1`; empty for singletons. Build clean: `built=26  missing=0  errored=0  tiles_total=18933 KB` (+68 KB from prior deploy carrying 3 new fields × 1,778 ercot_queue rows). Local↔prod md5 identical. Aggregation reach: 1,205 groups total, 394 with 2+ components.
- URL: `https://lrp-tx-gis.netlify.app` — requires real User-Agent on curl (`-A "Mozilla/5.0"`).

---

## Open backlog

**Data-pipeline gaps** (non-blocking):
- `eia860_plants`: 476/1367 rows still null `capacity_mw` (down from 529), 529/1367 null `commissioned`, 438/1367 null `technology`. EIA-860 source-side gaps; will not improve without alternate source.
- `wind`: USWTDB schema has no `operator`, `technology`, or `fuel`; structural blanks (19464/19464). `commissioned` populated for 19364/19464 (down from 0); `manu` and `model` populated. Filling operator would require joining a project-layer source (e.g. EIA-860 wind plants) — separate sprint item if pursued.
- `ercot_queue`: Stages 1+2 (Chats 112–113) geocoded 479/1,778 rows precisely via cascading sources — eia860 324, tpit_poi 78, substation_poi 67, uswtdb 10, dc_anchors 0. Remaining 1,299 carry `coords_source=county_centroid` provenance. Aggregate solar+wind+battery 452/1,676 (27.0%); structural ceiling on programmatic match rate. Stage 3 (Chat 116) targets remaining high-value misses via operator-curated manual override CSV.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar
- BEAD `bead_fiber_planned` layer (Chat 91 §1 dropped): BDO XLSX trio archived to `data/bead_bdo/` but contains no county or coords. Three unblock paths documented in `data/bead_bdo/README.md`

**UI/UX:**
- `date_range` filter type not implemented (carryforward from Chat 92 handoff). `tax_abatements` `commissioned` filter ships as `text` multi-select over distinct ISO dates — functional with 9 rows but not a true range slider. Touches `build.py compute_filter_stats` + `build_template.html filterFieldControlHtml` + matching predicate.
- Filter inputs (`.filter-text`, `.filter-range input`) sized at 40 px on mobile (Chat 100), not strictly the 44 px WCAG bar. Acceptable per Apple HIG (≥40 px) but flag for review if operator testing surfaces hit-rate issues.
- `county_labels` declutter at low zoom: post-Chat-111 with 254 labels, MapLibre symbol-collision will hide overlaps below ~zoom 7. Conditional sprint item above; do not pre-empt visual review.

**Infrastructure:**
- `NETLIFY_PAT` absent from `CREDENTIALS.md`. Netlify MCP proxy path canonical
- `GITHUB_PAT` can push branches, 403 on PR creation. Direct-merge-to-main is the protocol (OPERATING.md §9)
- **Akamai datacenter-egress block on `reevescounty.org`** — cloud-runner / GitHub-Actions traffic 403s regardless of UA / TLS fingerprint. Hard prerequisite for the abatement-weekly-cron sprint item. Unblock options: residential-proxy egress (paid), Akamai allowlisting via Reeves County IT (low likelihood), search-API result pages
- Fresh-container build deps + git identity gaps — promoted to **active fix in Chat 103**. Currently both worked around manually (cairosvg + tippecanoe install at session start; `git config user.email/.name` before close-out.sh).

**Process:**
- Chat 92 §6.12 violation (deploy + merge atomic): published deploy `69ed2cdf4039c554a1316ad2` to prod but deferred close-out merge, citing scope-creep. Reconciled in Chat 93 (merge `3a59a73`). Root cause: doc-restructure work appeared on a feature branch alongside the data-layer work, blowing past §6.13 stage-fits-one-chat. Preventive structural fix: pre-commit hook could reject doc-structure changes on `refinement-*` branches; lower-effort alternative is operator-side discipline at branch-naming time.
- Chat 100 §6.12 deviation: deploy + merge were not atomic in the same chat. Tracked as fixed via session-open.sh structural fix scheduled for Chat 103.
- Chats 101 + 102 §6.12 compliant: deploy + merge atomic in single shipping flow.
- Chat 102 tool-budget overrun: 14 tool calls vs 6–8 estimate. Cause: heavy verification of stamped-fields encoding (tippecanoe-decode iterations + pmtiles metadata read) before deploying. Lesson: PMTiles metadata schema check via python-pmtiles is the single sufficient verification step; skip tippecanoe-decode tile-by-tile sampling.
- Chat 111 tool-budget: ~14 tool calls vs ~8 estimate. Cause: npx cache corruption on first deploy attempt forced a clean-and-retry; one Netlify MCP read errored mid-poll. Both transient infra hiccups, not protocol drift.

**Outstanding credential hygiene:**
- `GITHUB_PAT` leak from Chat 87 unrotated per operator override. Token valid until 2027-04-21

**Permanently excluded:** see ARCHITECTURE.md §11

**Other (non-GIS):** Grid Wire Vol. 7. Tier 2 water availability assessments. Excel returns model.
