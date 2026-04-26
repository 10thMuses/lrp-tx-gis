# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat

**Chat 106 — WIND OPERATOR/TECHNOLOGY FILL via EIA-860 JOIN.** USWTDB schema lacks `operator`, `technology`, `fuel` fields — currently 19,464/19,464 structural blanks. EIA-860 wind plants table carries operator + technology by plant. Spatial join (USWTDB turbine point → nearest EIA-860 plant centroid within ~5 miles) backfills these fields for the bulk of turbines.

### Task

1. **Refresh EIA-860 wind plants subset.** `scripts/refresh_eia860.py` already pulls full EIA-860; extend to emit a `wind_plants` slice (filter rows where `prime_mover_code == 'WT'` or technology contains 'wind'). Output to `outputs/refresh/eia860_wind_plants_<date>.csv` with columns: plant_code, plant_name, operator_name, prime_mover_code, technology, lat, lon, capacity_mw, commissioned_year.
2. **Spatial join script** at `scripts/join_wind_eia860.py`: for each USWTDB row in `outputs/refresh/wind_<date>.csv`, find nearest EIA-860 wind plant within 8 km (5 miles); copy operator_name → `operator`, technology → `technology`, plant fuel → `fuel`. Log unmatched rows for review. Atomic rewrite per §6.15.
3. **Merge** updated wind subset into `combined_points.csv` via `python build.py merge wind outputs/refresh/wind_<date>.csv`.
4. **Build → preview → prod** per §8. Verify popup shows operator/technology on at least 5 sample turbines.
5. WIP next-chat = Chat 107 (date_range filter for tax_abatements OR Comptroller LDAD scrape, pending operator decision held from Chat 105).

### Acceptance

- ≥80% of USWTDB turbines have populated `operator` after join.
- `wind` layer popup shows operator + technology values where joined.
- Build clean: `built=26 missing=0 errored=0`.
- Local↔prod md5 identical post-deploy.
- Branch merged + deleted same chat per §6.12.

### Branch

`refinement-chat106-wind-operator-fill`

### Pre-flight

- Chat 106a shipped (parallel insurance chat). Cloud build+deploy workflow at `.github/workflows/build-and-deploy.yml`: workflow_dispatch trigger, Linux runner with apt-installed tippecanoe, env-driven `LRP_DIST_DIR`, deploys via netlify-cli to prod. **Operator must add `NETLIFY_AUTH_TOKEN` and `NETLIFY_SITE_ID` to repo Secrets before first cloud build.** Site ID = `01b53b80-687e-4641-b088-115b7d5ef638`. Token from `app.netlify.com → User Settings → Applications → Personal Access Tokens`. Once added, cloud builds become a third independent build path.
- Chat 105 shipped clean. PMTiles feature counts now correct in sidebar for all 4 prebuilt layers (parcels_pecos=14720, rrc_pipelines=35879, tiger_highways=8010, bts_rail=16522). Fix structural: `read_pmtiles_feature_count(pm_path)` helper in `build.py` reads `tilestats.layers[*].count` from PMTiles metadata via python-pmtiles; prebuilt layer return statement now uses helper with YAML-fallback. Deploy `69ee25b25be421df2f22b294`. Index-only delta (1 file uploaded), no PMTiles regenerated. Local↔prod md5 = `423773f3346c6868fff66d8da43e0842`. python-pmtiles added as build dep (was implicit; not added to a pip requirements file because there isn't one — relies on session-open.sh apt/pip install layer; consider promoting to `requirements.txt` if dep count grows).
- Sprint queue: wind operator fill (this chat) → date_range filter for tax_abatements → Comptroller LDAD scrape (Playwright, AUTHORIZED Chat 106a) → Permian abatement work [DROPPED per Chat 105 strategic reset].
- Tool budget for Chat 106: 8–12 (refresh script edit + join script + merge + build + preview + prod + verify + close-out).
- **For Claude Code post-migration:** wind operator fill is mostly script-edit work (CC-friendly). Build + deploy at the end requires tippecanoe — three independent paths now available: (a) chat container, (b) WSL2 on Windows desktop after one-time install, (c) `build-and-deploy.yml` cloud workflow via GitHub Actions UI button.

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

- Layer count: **26**
- Last published deploy: `69ee25b25be421df2f22b294` (Chat 105, 2026-04-26). State=ready. PMTiles feature counts fix for prebuilt layers. `read_pmtiles_feature_count(pm_path)` helper added to `build.py` (reads `tilestats.layers[*].count` via python-pmtiles); prebuilt layer return path now uses helper with YAML-fallback to `feature_count` field then 0. Sidebar now shows: parcels_pecos=14720, rrc_pipelines=35879, tiger_highways=8010, bts_rail=16522 (previously all 0). Build clean: `built=26 missing=0 errored=0 tiles_total=18933 KB`. Index-only delta (1 file uploaded), no PMTiles regenerated. Local↔prod md5 = `423773f3346c6868fff66d8da43e0842`.
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
