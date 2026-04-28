# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat

**Chat 113 — ERCOT QUEUE GEOCODING SPRINT STAGE 2: TPIT POI proximity + dc_anchors exact match.** Stage 2 is the **primary** geocoding mechanism for the queue. Stage 1 (Chat 112) handled the 18.4% of queue rows that already exist in EIA-860 as operating plants; this stage targets the forward-looking remainder via each row's declared POI substation.

### Task

1. Verify the queue's POI/substation column. Inspect `combined_points.csv` schema for ercot_queue rows (likely `poi_substation` or `poi`; whatever the source ERCOT GIR field name lands as in the existing pipeline).
2. Extend `scripts/geocode_ercot_queue.py` (or add a Stage 2 helper invoked from it) with two new passes:
   - **TPIT POI proximity:** index TPIT substation features (`outputs/refresh/tpit_*.geojson` or however tpit_subs is sourced — verify path) keyed `(normalized_substation_name, county)`; for each ercot_queue row not already matched in Stage 1, fuzzy-match the row's POI field to the TPIT substation index (rapidfuzz `WRatio` ≥ 88, same county). Stamp `coords_source = tpit_poi`.
   - **dc_anchors exact-name match:** the 8 `dc_anchors` features carry anchor-tenant names (e.g., CoreWeave, Crusoe). For ercot_queue rows whose developer/project name matches a dc_anchors entry exactly, snap to dc_anchors centroid. Stamp `coords_source = dc_anchors`.
3. Preserve Stage 1 matches (`eia860`, `uswtdb`); never overwrite. Stage-2 passes only operate on rows currently `coords_source = county_centroid`.
4. Atomic write per §6.15.
5. Append match-rate log to `outputs/refresh/_geocode_ercot_log.txt`.
6. Build → deploy to prod per §8.

### Acceptance

- Build clean: `built=26 missing=0 errored=0`.
- ercot_queue feature count unchanged (1,778).
- Aggregate (Stage 1 + Stage 2) match rate ≥ 60% non-centroid for solar/wind/battery (the original target moved here from Stage 1).
- Local↔prod md5 identical.
- Branch merged + deleted same chat per §6.12.

### Branch

`refinement-chat113-ercot-geocode-stage2`

### Pre-flight

- Chat 112 shipped clean. Deploy `69f0ad1c2ffe34b3320d0e1e` (2026-04-28), md5 `0b630fd927c6d76adbb1ee8e9a518a6c`. Build clean: `built=26 missing=0 errored=0 tiles_total=11603 KB` (+8 KB vs Chat 111 — new `coords_source` field × 1,778 ercot_queue rows).
- Stage 1 match rates by bucket — for context only, do not retune Stage 1: solar 131/625 (21.0%), wind 56/155 (36.1%), battery 132/896 (14.7%), gas 25/98 (25.5%). Aggregate solar+wind+battery 309/1,676 (18.4%). Structural reason for missing the 60% target documented in Chat 112 handoff: EIA-860 indexes operating plants, queue is forward-looking. Do not lower WRatio threshold below 88; do not retune `norm_name` suffix-stripping.
- The Stage 1 popup label "County centroid (approximate)" describes provenance reliability, not literal geometric centroid placement. Coords already varied per row pre-Stage-1 (187 counties hold up to 36 distinct coord pairs each). Acceptable unless operator wants stricter language.
- **Side observation queued for separate chat** (not in scope here): WAHA Natural Gas Hub marker visually obscures GW Ranch campus polygon at typical viewing zooms — paint-order issue, see Sprint queue.

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### ERCOT QUEUE PRECISE GEOCODING

**Multi-chat sprint.** Reframed after Chat 112: Stage 2 is the **primary** lever, not a minor extension.

- **Stage 1 (Chat 112, shipped):** EIA-860 + USWTDB joins for queue rows that already exist as operating plants. Final aggregate match rate 18.4% (309/1,676 solar+wind+battery). Structural ceiling — EIA-860 indexes operating plants while queue is forward-looking by design. Coverage at this level was not a tuning failure, it was the data limit.
- **Stage 2 (Chat 113, promoted to Next chat):** TPIT substation POI proximity + dc_anchors exact-name match. Targets the ~80% of queue rows still at county-centroid provenance after Stage 1. This stage owns the original ≥60% target.
- **Stage 3 (Chat 114, optional):** operator spot-check + manual overrides for high-value misses (anchor tenants, large-MW gas peakers).

### WAHA MARKER OBSCURES GW RANCH (PAINT ORDER)

Surfaced Chat 112 close-out. WAHA Natural Gas Hub renders as a large filled orange marker near 31.16°N, -102.82°W. GW Ranch (Pacifico Energy) campus polygon sits ~2 mi south at 31.13°N within the WAHA marker's render footprint at typical viewing zooms — its 3.5-mi-wide red stroke is fully obscured. Operator-visible symptom: only 2 of 3 hyperscale-campus red outlines (Escalera + Longfellow) render in West Texas; GW Ranch invisible. Diagnosis confirmed: gw_ranch is 1 Polygon, 1 part, present in `combined_geoms.geojson`; not a data bug.

Fix options (1 chat, low blast radius):
- Reorder MapLibre layer paint stack so campus polygon strokes draw above `waha_circle` / `labels_hubs` marker fills.
- Reduce `waha_circle` radius (configured in `build_template.html` paint block).
- Both. Investigate first; preferred fix is paint-order reorder so map readability of the WAHA hub itself isn't compromised.

Touches `build_template.html` only. No data change.

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
- Last published deploy: `69f0ad1c2ffe34b3320d0e1e` (Chat 112, 2026-04-28). State=ready. ERCOT queue geocoding Stage 1: 334 rows matched via EIA-860 (324) + USWTDB (10); 1,444 retained existing approximate coords with `coords_source=county_centroid` provenance label. New `coords_source` field stamped on all 1,778 ercot_queue rows. Build clean: `built=26 missing=0 errored=0 tiles_total=11603 KB`. Local↔prod md5 identical (`0b630fd927c6d76adbb1ee8e9a518a6c`). Aggregate solar+wind+battery match rate 18.4% — below the original 60% target for structural reasons (EIA-860 indexes operating plants only). Stage 2 (TPIT POI proximity) carries the 60% target.
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
- `ercot_queue`: Stage 1 (Chat 112) geocoded 334/1,778 rows precisely via EIA-860+USWTDB; remaining 1,444 carry `coords_source=county_centroid` provenance. Stage 2 (Chat 113) targets the remainder via TPIT POI proximity, owns the ≥60% match-rate target.
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
