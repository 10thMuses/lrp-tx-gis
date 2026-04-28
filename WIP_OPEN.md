# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat

**Chat 112 — ERCOT QUEUE GEOCODING SPRINT STAGE 1: EIA-860 + USWTDB joins.** All 1,778 `ercot_queue` rows currently sit at county centroids — visible as clusters at county center on the map. Stage 1 of the multi-chat sprint described below in `### ERCOT QUEUE PRECISE GEOCODING`.

### Task

1. Write `scripts/geocode_ercot_queue.py`. Reads `combined_points.csv` streaming; never loads into Claude context.
2. Build EIA-860 plant index from `outputs/refresh/eia860_plants_2026-04-25.csv` keyed `(normalized_plant_name, county)`. Normalize: lowercase, strip punctuation, collapse whitespace, drop suffixes (`solar`, `wind`, `battery`, `bess`, `farm`, `project`, `station`, `phase i/ii/iii`, roman/arabic numerals at end).
3. Build USWTDB project index from the canonical USWTDB CSV (path TBD — see if `outputs/refresh/uswtdb_*.csv` exists; if not, fetch from `https://eersc.usgs.gov/api/uswtdb/v1/turbines.csv`). Aggregate turbines per `p_name`: lat/lon = mean of turbine points; keyed `(normalized_p_name, county_set)`.
4. For each `ercot_queue` row in `combined_points.csv`: try EIA-860 fuzzy match first (rapidfuzz `WRatio` ≥ 88 within same county), fall back to USWTDB for wind, leave at centroid otherwise. Stamp `coords_source` prop = `eia860 | uswtdb | county_centroid`.
5. Atomic write per §6.15 (temp + `os.replace`).
6. Log match counts by source. Acceptance target ≥ 60% non-centroid for solar/wind/battery rows; whatever lands lands for gas/other.
7. Build → preview → prod per §8.

### Acceptance

- Build clean: `built=26 missing=0 errored=0`.
- ercot_queue feature count unchanged (1,778).
- New popup field `coords_source` visible (popup template needs no change — generic field renderer; verify in dist).
- Local↔prod md5 identical post-deploy.
- Branch merged + deleted same chat per §6.12.
- Match-rate log printed in build summary or saved to `outputs/refresh/_geocode_ercot_log.txt`.

### Branch

`refinement-chat112-ercot-geocode-stage1`

### Pre-flight

- Chat 111 shipped clean. `county_labels` extended from 46 (West Texas only) to 254 (all of Texas, FIPS 48) via TIGER 2024 county polygons. Source: `https://www2.census.gov/geo/tiger/TIGER2024/COUNTY/tl_2024_us_county.zip` (84 MB, gitignored). Position = `shapely.representative_point()` per county polygon, not centroid (handles concave shapes, e.g. river-meander lobes). Naming convention preserved: `<NAME> County` matching the existing 46. Replacement strategy (drop all 46 old, append 254 new) per Task §4 — TIGER NAME field is authoritative. Build clean: `built=26 missing=0 errored=0 tiles_total=11595 KB` (+96 KB vs 110c — county_labels tile grew from 46→254 features). Local↔prod md5 identical (`4fb699f478ad530c04f44ab350493bd1`). Deploy `69f01efe66cedded36ed2e99`. Canonical script: `scripts/extend_county_labels.py`.
- **Side observation worth flagging.** Operator's Chat 111 framing implied data-coverage gap: "Visible counties without labels at typical viewing zooms include Loving, Ector, Sterling, Hudspeth, Presidio, Val Verde, Kimble, Kinney." All 8 of those counties were already in the original 46-feature set. Coords post-Chat-111 (rep-points): Loving `[-103.57, 31.83]`, Ector `[-102.54, 31.87]`, Sterling `[-101.05, 31.82]`, Hudspeth `[-105.42, 31.32]`, Presidio `[-104.24, 29.94]`, Val Verde `[-101.05, 29.76]`, Kimble `[-99.71, 30.50]`, Kinney `[-100.41, 29.35]`. If those still appear missing post-deploy, root cause is rendering, not data — likely MapLibre symbol-collision declutter (with 254 labels at low zoom, the engine drops overlapping labels) or the `min_zoom: 5` setting (107d) gating short-name labels under specific layout conditions. Chat 112 stays focused on ERCOT geocoding; operator can flag rendering as a sprint item if visual review confirms the issue persists.
- Chats 110/110b/110c/111 chain: incremental UI/data refinements, all clean atomic deploys. Pattern works; no process-level changes needed.

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### ERCOT QUEUE PRECISE GEOCODING

**Multi-chat sprint.** Stage 1 promoted to Chat 112 (above). Remaining stages:

- **Stage 2 (Chat 113):** dc_anchors exact-name match + TPIT substation/line proximity for points lacking other matches + popup field for `coords_source`. ercot_queue popup template currently renders all props generically — verify `coords_source` shows up cleanly without template change.
- **Stage 3 (Chat 114, optional):** operator spot-check + manual overrides for high-value misses (anchor tenants, large MW gas peakers).

Approach reference for Stage 1 in §Task above. Expected match rate 60–80%; 20–40% will stay imprecise.

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
- Last published deploy: `69f01efe66cedded36ed2e99` (Chat 111, 2026-04-28). State=ready. `county_labels` extended 46 → 254 (all TX counties via TIGER 2024). Local↔prod md5 identical (`4fb699f478ad530c04f44ab350493bd1`). Build clean: `built=26 missing=0 errored=0 tiles_total=11595 KB`.
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
- `ercot_queue`: 1,778/1,778 rows currently at county centroids — Chat 112 sprint addresses.
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
