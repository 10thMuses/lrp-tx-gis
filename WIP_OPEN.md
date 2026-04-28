# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat

**Chat 111 — COUNTY LABELS COVERAGE EXTENSION.** `county_labels` currently has 46 features (West Texas only). Visible counties without labels at typical viewing zooms include Loving, Ector, Sterling, Hudspeth, Presidio, Val Verde, Kimble, Kinney, and ~200 others statewide. Operator wants comprehensive coverage.

### Task

1. Fetch TIGER 2024 county polygons for all of Texas (FIPS 48) — single shapefile from Census `https://www2.census.gov/geo/tiger/TIGER2024/COUNTY/`.
2. Compute representative point (`pyshp`/`shapely.representative_point()`, not centroid — handles concave shapes) per county.
3. Stream into `combined_geoms.geojson` as `layer_id: county_labels` features with `name: <COUNTY>` property.
4. Drop the existing 46 `county_labels` features first (replace, don't dedupe by name — TIGER NAME field is authoritative).
5. Counties (Outline) layer is a separate question — leave at 46 for now unless operator requests extending. Sprint item if so.
6. Build → preview → prod per §8.

### Acceptance

- `county_labels` feature count ≥ 254.
- Build clean: `built=26 missing=0 errored=0`.
- Visual check at zoom 7–9: every visible Texas county has a label.
- Local↔prod md5 identical post-deploy.
- Branch merged + deleted same chat per §6.12.

### Branch

`refinement-chat111-county-labels-statewide`

### Pre-flight

- Chat 110c shipped clean. Final state: `tpit_subs` recolored `#06b6d4 → #a78bfa` matching `substations` (semantic pairing); Transmission & Grid sidebar order now `[substations, tpit_subs, transmission, tpit_lines]`; `longfellow_ranch` polygon moved from southern Pecos/Terrell/Brewster (~30.3, -102.6 — Mitchell family ranch homestead) to central Pecos (~30.77, -102.68) at the ERCOT queue cluster operator confirmed visually as the actual Project Horizon AI campus location. Resolves overlap with `la_escalera`. Gap to `gw_ranch` (~31.13, -102.84) now ~18 mi. Edit script `scripts/edit_110c_trans_fix.py` is the canonical source of the new polygon coords. Deploy `69f008f6187338b50dc2a829`. Local↔prod md5 identical (`5fbac81d4e356c58b5eab73777027ba6`). Build clean: `built=26 missing=0 errored=0 tiles_total=11499 KB` (-57 KB vs 110b — Longfellow polygon is smaller).
- Chats 110/110b/110c chain: parent (sidebar overhaul) + 110b (fill-opacity falsy bug) + 110c (this). Operator-driven incremental refinement; each shipped clean atomically per §6.12. Pattern is acceptable but suggests pre-flight visual review before declaring a UI chat done — would have caught 110b's red-fill bug and several 110c items in one cycle.

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### ERCOT QUEUE PRECISE GEOCODING

**Multi-chat sprint.** All 1,778 `ercot_queue` rows currently sit at county centroids — operator caught this visually (clusters at county center on map). Most projects can be cross-referenced to existing rich-coordinate sources:

- **EIA-860 plants** (1,367 rows, lat/lon present) — match on plant_name fuzzy + county. Highest hit rate for solar/wind/battery already-operating projects.
- **USWTDB** (19,464 turbines, lat/lon present) — match on project_name for wind aggregates.
- **dc_anchors** (8 rows) — exact name match for DC tenants in queue.
- **TPIT** — substation/line proximity for points lacking other matches.

Approach: write `scripts/geocode_ercot_queue.py` that reads `combined_points.csv`, joins against the four sources (in priority order above), updates lat/lon in-place, logs match-rate by source, atomic write. For unmatched rows, leave at county centroid + flag `coords_source: county_centroid` in props. Expected match rate 60–80%; 20–40% will stay imprecise. Sprint = 2–3 chats: (1) EIA-860 + USWTDB joins, (2) dc_anchors + TPIT proximity + popup field for `coords_source`, (3) operator-spot-check + manual overrides for high-value misses.

### DATE-RANGE FILTER FOR `tax_abatements.commissioned`

True range slider replacing current text-multi-select on distinct ISO dates. Touches `build.py compute_filter_stats` + `build_template.html filterFieldControlHtml` + matching predicate. 1–2 chats. **Deferred** — operator's chat-110 series surfaced higher-priority data-quality work above.

### COMPTROLLER LDAD SCRAPE

Operator authorized Chat 106a. Playwright headless against `https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`. Paginate result pages, write to `outputs/refresh/comptroller_ldad_<date>.csv`, merge into `tax_abatements` layer. Provides statewide abatement coverage to complement existing 9 county-scraped records. 1–2 chats.

### MOBILE STAGE 3 — HOTFIX ON DEMAND

Cross-device QA + polish for the mobile-friendly map work shipped in Chats 100–101. Not scheduled. Surfaced issues become discrete patch chats. 0–1 chat per issue.

---

## Prod status

- Layer count: **24**
- Last published deploy: `69f008f6187338b50dc2a829` (Chat 110c, 2026-04-28). State=ready. Transmission & Grid reorder + tpit_subs recolor + Longfellow polygon move. Sidebar order within group now `[substations, tpit_subs, transmission, tpit_lines]`; both substation layers share `#a78bfa` purple. `longfellow_ranch` polygon repositioned from southern Pecos/Terrell/Brewster (~30.3, -102.6) to central Pecos at the actual Project Horizon AI campus (~30.77, -102.68) per operator visual identification; resolves la_escalera overlap. Local↔prod md5 identical (`5fbac81d4e356c58b5eab73777027ba6`). Build clean: `built=26 missing=0 errored=0 tiles_total=11499 KB`.
- Previous deploy: `69f00661239f04d4b9bec06f` (Chat 110b, 2026-04-28). Hotfix: `fill-opacity || 0.25` → `?? 0.25`; `mpgcd_zone1` default_on true.
- Previous deploy: `69efdc12326f632c49033ed2` (Chat 110, 2026-04-27). Sidebar overhaul.
- Previous deploy: `69ef926ed31a462a98b27f77` (Chat 109b, 2026-04-27). State=ready. Hyperscale DC & Power Campuses group consolidation + WAHA Pecos fix + Solstice visibility.
- Previous deploy: `69ef8b0a7ca58c0d4d25ae4d` (Chat 108b, 2026-04-27). State=ready. Local Developments group + popup audit + permit visibility.
- Previous deploy: `69ee7b6cffaa366af764784c` (Chat 107d, 2026-04-26). State=ready. Critical bug fix on top of 107c: build.py was defaulting `line_width` to **2** in the layer registry render path (line 825), overriding template defaults — so the JS template's 0.5 default never took effect. Fixed: `'line_width': L.get('line_width', 0.5)`. Also: county_labels switched to dark text (`#0f172a`) with halo opt-out via new `text_halo: false` YAML flag; template halo logic now auto-picks contrast (light text → dark halo, dark text → light halo). Counties `line_width` raised 0.5 → 1. county_labels `min_zoom: 4 → 5`.
- Previous deploy: `69ee76fc43cd26b6f3460922` (Chat 107c, 2026-04-26). State=ready. Contrast/legibility/fuel pass.
- Previous deploy: `69ee72bcbd5d65c5bac1e0eb` (Chat 107a, 2026-04-26).
- Previous deploy: `69ee25b25be421df2f22b294` (Chat 105, 2026-04-26). PMTiles feature counts fix for prebuilt layers.
- Previous deploy: `69ee07134b63d09184004cf9` (Chat 102, 2026-04-26). State=ready. ERCOT queue project aggregation popup. `compute_ercot_group_aggregates(csv_path)` streams `combined_points.csv` once and returns `{group_key: {group_total_mw, group_count, group_breakdown}}` (breakdown is `\n`-joined `<name> · <mw> MW · <county>` lines, sorted by MW desc). `split_combined_csv()` stamps these fields onto every ercot_queue feature's props during NDGeoJSON write. Popup helper `ercotQueueGroupSummaryHtml(props)` renders a summary block (sage-pink card with project group label, total MW, component count, breakdown list) above the per-row table when `group_count > 1`; empty for singletons. Build clean: `built=26  missing=0  errored=0  tiles_total=18933 KB` (+68 KB from prior deploy carrying 3 new fields × 1,778 ercot_queue rows). Local↔prod md5 identical. Aggregation reach: 1,205 groups total, 394 with 2+ components.
- URL: `https://lrp-tx-gis.netlify.app` — requires real User-Agent on curl (`-A "Mozilla/5.0"`).

---

## Open backlog

**Data-pipeline gaps** (non-blocking):
- `eia860_plants`: 476/1367 rows still null `capacity_mw` (down from 529), 529/1367 null `commissioned`, 438/1367 null `technology`. EIA-860 source-side gaps; will not improve without alternate source.
- `wind`: USWTDB schema has no `operator`, `technology`, or `fuel`; structural blanks (19464/19464). `commissioned` populated for 19364/19464 (down from 0); `manu` and `model` populated. Filling operator would require joining a project-layer source (e.g. EIA-860 wind plants) — separate sprint item if pursued.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar
- BEAD `bead_fiber_planned` layer (Chat 91 §1 dropped): BDO XLSX trio archived to `data/bead_bdo/` but contains no county or coords. Three unblock paths documented in `data/bead_bdo/README.md`

**UI/UX:**
- `date_range` filter type not implemented (carryforward from Chat 92 handoff). `tax_abatements` `commissioned` filter ships as `text` multi-select over distinct ISO dates — functional with 9 rows but not a true range slider. Touches `build.py compute_filter_stats` + `build_template.html filterFieldControlHtml` + matching predicate.
- Filter inputs (`.filter-text`, `.filter-range input`) sized at 40 px on mobile (Chat 100), not strictly the 44 px WCAG bar. Acceptable per Apple HIG (≥40 px) but flag for review if operator testing surfaces hit-rate issues.

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

**Outstanding credential hygiene:**
- `GITHUB_PAT` leak from Chat 87 unrotated per operator override. Token valid until 2027-04-21

**Permanently excluded:** see ARCHITECTURE.md §11

**Other (non-GIS):** Grid Wire Vol. 7. Tier 2 water availability assessments. Excel returns model.
