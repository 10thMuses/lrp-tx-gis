# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat

**Chat 107b — GROUP-LEVEL TOGGLE-ALL CHECKBOXES IN SIDEBAR.** Each group header in the sidebar (Generation, Transmission & Grid, Permits, etc.) needs a tri-state checkbox that turns all layers in that group on or off in one action. Pure UI feature in `build_template.html` — no build pipeline change.

### Task

1. In `build_template.html` sidebar render code, each group header (currently a `<div class="group-header">` or similar) gets a checkbox prepended: unchecked = no layers in group on, checked = all on, indeterminate = some on.
2. Click handler: toggling group checkbox toggles all layers in that group (calls existing per-layer toggle for each).
3. Reactive update: when individual layer toggles change, recompute group checkbox state (all-on / none-on / mixed → indeterminate via `checkbox.indeterminate = true`).
4. CSS: subtle styling so group checkbox doesn't compete with layer checkboxes (smaller, lighter color, or use a different control like a button).
5. Smoke-test in chat: build, preview locally, click through every group's toggle, confirm individual + group state stays consistent.
6. Standard build → preview → prod per §8.

### Acceptance

- Every group header has a tri-state checkbox.
- Clicking group checkbox toggles all layers in that group.
- Toggling individual layers updates group checkbox to all/none/indeterminate correctly.
- Build clean: `built=24 missing=0 errored=0`.
- Local↔prod md5 identical post-deploy.
- Branch merged + deleted same chat per §6.12.

### Branch

`refinement-chat107b-group-toggle`

### Pre-flight

- Chat 107a shipped clean. 24 layers (was 26): removed `parcels_pecos` (not for sharing) and `fcc_fiber_coverage` (FCC BDC residential broadband data — wrong concept for thesis). White county outlines visible at all zooms; lighter county labels for satellite contrast (#f1f5f9). Line widths halved on transmission/rail/pipelines (default 2→1; transmission voltage scaling 1.5–4 → 0.75–2 in `sizingLineWidthExpr` in `build_template.html`). Brighter colors for satellite contrast: rrc_pipelines `#7c2d12 → #fb923c`, bts_rail `#475569 → #cbd5e1`, tiger_highways `#f59e0b → #fde047`, tpit_subs/tpit_lines `#b45309/#f59e0b → #fbbf24`, counties `#475569 → #ffffff`. mpgcd_zone1: `fill_opacity 0` + stroke. Permits group labels: "Gas Turbine Air Permits (TCEQ, recent filings)" + "Approved Tax Abatements (energy & DC projects)". tpit_lines: added filterable owner/voltage/status/tier/county fields (was just name). build.py: removed `--read-parallel` (caused tippecanoe SQLite lock race on container's overlay filesystem). Deploy `69ee72bcbd5d65c5bac1e0eb`. Build clean: `built=24 missing=0 errored=0 tiles_total=12712 KB`.
- **Open follow-ups from operator review:**
  - Item 4 (more transmission upgrade filter fields): **shipped in 107a** — added owner/voltage/status/tier/county.
  - Item 11 (more reference layers — streets, townships): **defer**. Streets adds significant tile size; townships not applicable to TX (Spanish/Mexican land grants, not PLSS). Reconsider after Hanwha share.
  - Item 2/3 (solar + wind operator fills): Chat 106 still queued. Same EIA-860 join methodology applies to both.
- Sprint queue: group toggle UI (this chat) → wind+solar operator fill via EIA-860 join → Comptroller LDAD scrape (Playwright, authorized Chat 106a) → Permian abatement work [DROPPED Chat 105].
- Tool budget for Chat 107b: 6–10 (template edits + build + preview + prod + close-out).

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
- Last published deploy: `69ee72bcbd5d65c5bac1e0eb` (Chat 107a, 2026-04-26). State=ready. Pre-Hanwha share cleanup batch: removed `parcels_pecos` and `fcc_fiber_coverage` layers entirely (residential broadband BSL hexagons were confusing for the thesis); white county outlines visible at all zooms; lighter county labels for satellite contrast; line widths halved on transmission/rail/pipelines; brighter pipeline + rail + highway + TPIT colors; mpgcd_zone1 outline-only (no fill); Permits group labels improved ("Gas Turbine Air Permits (TCEQ, recent filings)" + "Approved Tax Abatements (energy & DC projects)"); tpit_lines now has filterable owner/voltage/status/tier/county; build.py no longer uses `--read-parallel` (caused tippecanoe SQLite lock race on overlay filesystems). Build clean: `built=24 missing=0 errored=0 tiles_total=12712 KB`.
- Previous deploy: `69ee25b25be421df2f22b294` (Chat 105, 2026-04-26). PMTiles feature counts fix for prebuilt layers.
- Previous deploy: `69ee07134b63d09184004cf9` (Chat 102, 2026-04-26). State=ready. ERCOT queue project aggregation popup. `compute_ercot_group_aggregates(csv_path)` streams `combined_points.csv` once and returns `{group_key: {group_total_mw, group_count, group_breakdown}}` (breakdown is `\n`-joined `<name> · <mw> MW · <county>` lines, sorted by MW desc). `split_combined_csv()` stamps these fields onto every ercot_queue feature's props during NDGeoJSON write. Popup helper `ercotQueueGroupSummaryHtml(props)` renders a summary block (sage-pink card with project group label, total MW, component count, breakdown list) above the per-row table when `group_count > 1`; empty for singletons. Build clean: `built=26  missing=0  errored=0  tiles_total=18933 KB` (+68 KB from prior deploy carrying 3 new fields × 1,778 ercot_queue rows). Local↔prod md5 identical. Aggregation reach: 1,205 groups total, 394 with 2+ components.
- Previous deploy: `69edeb7d83b23c994ffd00ed` (Chat 101, 2026-04-26). Mobile stage 2: gesture rotation disabled below 768 px via matchMedia, measure-vertex radius 4→12 on mobile, `.measure-readout` close button, `#btn-print` collapses drawer on mobile.
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
