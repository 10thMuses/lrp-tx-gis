# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat

**Chat 109 — GROUP-LEVEL TOGGLE-ALL CHECKBOXES IN SIDEBAR (was 107b).** Each group header in the sidebar (Local Developments, Land & Deal, Generation, Transmission & Grid, Permits, etc.) needs a tri-state checkbox that turns all layers in that group on or off in one action. Pure UI feature in `build_template.html` — no build pipeline change.

### Task

1. In `build_template.html` sidebar render code, each group header gets a checkbox prepended: unchecked = no layers in group on, checked = all on, indeterminate = some on.
2. Click handler: toggling group checkbox toggles all layers in that group (calls existing per-layer toggle for each).
3. Reactive update: when individual layer toggles change, recompute group checkbox state (all-on / none-on / mixed → indeterminate via `checkbox.indeterminate = true`).
4. CSS: subtle styling so group checkbox doesn't compete with layer checkboxes (smaller, lighter color, or use a different control like a button).
5. Smoke-test: build, click through every group's toggle, confirm individual + group state stays consistent.
6. Standard build → preview → prod per §8.

### Acceptance

- Every group header has a tri-state checkbox.
- Clicking group checkbox toggles all layers in that group.
- Toggling individual layers updates group checkbox to all/none/indeterminate correctly.
- Build clean: `built=24 missing=0 errored=0`.
- Local↔prod md5 identical post-deploy.
- Branch merged + deleted same chat per §6.12.

### Branch

`refinement-chat109-group-toggle`

### Pre-flight

- Chat 108 shipped clean. New `Local Developments` group at top of sidebar, default-on. Three highlight features added in yellow (#FFD400): `solstice_substation` (AEP Solstice Substation, point @ OSM way 500535889 → 30.94832, -103.36171); `la_escalera` (La Escalera Ranch / Apex Pecos Flat polygon, ACCURACY: APPROXIMATE, ~223,000 acres anchored in Pecos County); `waha_circle` + `labels_hubs` moved out of Reference, repositioned to Coyanosa/Pecos County (31.235, -103.207), feature `name` uppercased to "WAHA". Permits visibility pass: `tceq_gas_turbines` r=4→7 stroke 1.5→2, `tax_abatements` r=4→7 stroke 1.5→2. Popup audit pass — added `popup_labels` and missing fields across counties (+GEOID), eia860_plants (+sector), substations (+osm_id, "Voltage (V)" label), tceq_gas_turbines (+fuel/operator/year), tax_abatements (+operator/funnel_stage), and labels-only refinements on eia860_battery/wind/solar/transmission/tpit_subs/cities/mpgcd_zone1/caramba_north. Deploy `69ef88a531ab2405cddbc098`. Build clean: `built=24 missing=0 errored=0 tiles_total=11446 KB`. Local↔prod md5 identical (`58cf18ab760e9df639176e9918943cfc`).
- Resume note: deploy was blocked at end of original Chat 108 by Netlify upload 503; cleared on retry in Chat 108b (resume) without code changes.
- Tool budget for Chat 109: 6–10 (template edits + build + preview + prod + close-out).

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### DATE-RANGE FILTER FOR `tax_abatements.commissioned`

True range slider replacing current text-multi-select on distinct ISO dates. Touches `build.py compute_filter_stats` + `build_template.html filterFieldControlHtml` + matching predicate. 1–2 chats.

### COMPTROLLER LDAD SCRAPE

Operator authorized Chat 106a. Playwright headless against `https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`. Paginate result pages, write to `outputs/refresh/comptroller_ldad_<date>.csv`, merge into `tax_abatements` layer. Provides statewide abatement coverage to complement existing 9 county-scraped records. 1–2 chats.

### MOBILE STAGE 3 — HOTFIX ON DEMAND

Cross-device QA + polish for the mobile-friendly map work shipped in Chats 100–101. Not scheduled. Surfaced issues become discrete patch chats. 0–1 chat per issue.

---

## Prod status

- Layer count: **24**
- Last published deploy: `69ef88a531ab2405cddbc098` (Chat 108, 2026-04-27). State=ready. Local Developments group + popup audit + permit visibility. New layers: `solstice_substation` (AEP Solstice Substation point, OSM way 500535889 coords), `la_escalera` (Apex Pecos Flat ranch outline, ACCURACY: APPROXIMATE, ~223k acres). Moved `waha_circle` + `labels_hubs` from Reference to Local Developments; WAHA repositioned to Coyanosa/Pecos County (31.235, -103.207); name uppercased. `tceq_gas_turbines` r=4→7 stroke 1.5→2; `tax_abatements` r=4→7 stroke 1.5→2 (visibility pass per operator review). Popup completeness pass across all layers — added `osm_id` to substations, `sector` to eia860_plants, `GEOID` to counties, `fuel/operator/year` to tceq_gas_turbines, `operator/funnel_stage` to tax_abatements; popup_labels added to 12 layers for clarity. `GROUP_ORDER` prepends 'Local Developments' so it renders first in sidebar. Build clean: `built=24 missing=0 errored=0 tiles_total=11446 KB`. Local↔prod md5 identical (`58cf18ab760e9df639176e9918943cfc`).
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
