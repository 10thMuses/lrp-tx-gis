# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat

**Chat 111 — DATE-RANGE FILTER FOR `tax_abatements.commissioned`.** True range slider replacing the current text-multi-select on distinct ISO dates.

### Task

1. `build.py compute_filter_stats`: emit a `date_range` filter type with min/max ISO bounds for `tax_abatements.commissioned`.
2. `build_template.html filterFieldControlHtml`: render two date inputs (min/max) for `type === 'date_range'`.
3. `build_template.html buildFilterExpr`: matching predicate that compares ISO-formatted strings via `>=` / `<=`.
4. Build → preview → prod per §8.

### Acceptance

- `tax_abatements.commissioned` filter is a date range (two date pickers), not a multi-select.
- Build clean: `built=26 missing=0 errored=0`.
- Local↔prod md5 identical post-deploy.
- Branch merged + deleted same chat per §6.12.

### Branch

`refinement-chat111-date-range-filter`

### Pre-flight

- Chat 110 shipped clean over two sessions (resume after tool-use limit). Final state: sidebar overhaul. **GROUP_ORDER reordered** with `Reference` first and `Land & Deal` second (operator request); `Local Developments` → `Local Focal Points` (4 layers: solstice_substation, waha_circle, mpgcd_zone1 [moved from Water & Regulatory], labels_hubs[sidebar_omit]); `Hyperscale DC & Power Campuses` → `Local Hyperscale DC & Power Campuses` (3 layers, all already fill_opacity:0 outline-only); `Generation` → `Power Generation` (4 layers); `Water & Regulatory` group dropped (now empty). **WAHA consolidation**: `waha_circle` relabeled "WAHA Natural Gas Hub" with `companions:[labels_hubs]`; `labels_hubs` `sidebar_omit:true`; one sidebar entry now toggles both ring + label in lockstep via new `setLayerVisibilityWithCompanions(L, on)` helper. **Tri-state group checkboxes**: every group header gets a checkbox (unchecked = none / checked = all / indeterminate = some); click toggles all layers in group; reactive — individual layer toggles update parent group state via `updateGroupCheckbox(groupEl)`. **Outline swatch**: fill layers with `fill_opacity:0` render in the sidebar (and print legend) as a hollow outlined square instead of a filled square — mirrors what the map actually draws. New CSS class `.swatch.outline`. **build.py emits `companions` field** to template registry. Deploy `69efdc12326f632c49033ed2`. First deploy attempt `69efda7f3170e224bbc70d81` landed `state:error/skipped:true` (Netlify dedupe matched stale CAS entry, deploy permalink HTTP 500); resolved by injecting build-SHA marker comment into `build_template.html` so each build has a distinct bundle hash. Build clean: `built=26 missing=0 errored=0 tiles_total=11556 KB`. Local↔prod md5 identical (`3ff55097c8d710e35bc802b3407accea`). Layer count unchanged at 26; sidebar visible entries went 26 → 25 due to `labels_hubs` sidebar_omit.
- §6.12 deviation: deploy + merge atomic spanned two chat sessions (tool-use limit hit between build and deploy in initial session; resumed via "Continue"). Repo-state-as-truth held — branch was already pushed with all source edits + dist/ already built clean before the limit, so the resume picked up exactly where it left off. Logged as a process-discipline note: stage was at the upper bound of "fits one chat" (six UI changes + the deferred Chat 110 task = 4 commits, 3 subsystems touched).

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### COMPTROLLER LDAD SCRAPE

Operator authorized Chat 106a. Playwright headless against `https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`. Paginate result pages, write to `outputs/refresh/comptroller_ldad_<date>.csv`, merge into `tax_abatements` layer. Provides statewide abatement coverage to complement existing 9 county-scraped records. 1–2 chats.

### MOBILE STAGE 3 — HOTFIX ON DEMAND

Cross-device QA + polish for the mobile-friendly map work shipped in Chats 100–101. Not scheduled. Surfaced issues become discrete patch chats. 0–1 chat per issue.

---

## Prod status

- Layer count: **24**
- Last published deploy: `69efdc12326f632c49033ed2` (Chat 110, 2026-04-27). State=ready. Sidebar overhaul: GROUP_ORDER reordered (`Reference` + `Land & Deal` at top); `Local Developments` → `Local Focal Points` (now 4 layers incl. `mpgcd_zone1` moved from Water & Regulatory and `labels_hubs` as sidebar_omit companion of `waha_circle`); `Hyperscale DC & Power Campuses` → `Local Hyperscale DC & Power Campuses`; `Generation` → `Power Generation`; `Water & Regulatory` group dropped (empty). WAHA Hub Ring + WAHA Hub Label consolidated into one sidebar toggle "WAHA Natural Gas Hub" via new `companions` field (`waha_circle.companions:[labels_hubs]`) + new template helper `setLayerVisibilityWithCompanions`. Tri-state group checkbox on every group header (unchecked / checked / indeterminate; clicking toggles all layers in group). Outline-only swatch in sidebar + print legend for fill layers with `fill_opacity:0` (matches what the map draws — no fill, just outline). `build.py` emits new `companions` field to template registry. Build clean: `built=26 missing=0 errored=0 tiles_total=11556 KB`. Local↔prod md5 identical (`3ff55097c8d710e35bc802b3407accea`).
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
