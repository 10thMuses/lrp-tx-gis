# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat

**Chat 105 — COSMETIC: PMTILES FEATURE COUNTS IN SIDEBAR.** Currently the sidebar shows `0` for prebuilt-PMTiles layers' feature counts (carryforward from Chat 91). Fix involves either reading PMTiles metadata at build time or letting the client fetch on layer-on. Small, no schema change.

### Task

1. Identify the sidebar feature-count rendering code in `build_template.html` (search for `feature_count` or sidebar layer-row template).
2. For prebuilt PMTiles layers, the count is currently set to 0 because the build step that populates `feature_count` only runs for layers built from `combined_*` files. Either:
   - **Option A (build-time):** in `build.py`, after each layer's PMTiles is finalized, run `tippecanoe-decode --stats` (or use `python-pmtiles` to read tile metadata) to count features and stamp into the layer's manifest entry.
   - **Option B (client-time):** in `build_template.html`, on layer-on event, fetch the PMTiles header and count tiles for the visible bbox. Higher complexity, less accurate.
3. Recommended: Option A. PMTiles metadata can be read once at build with python-pmtiles or `tippecanoe-decode`.
4. Test with `eia860_plants` and `wells` (both prebuilt) — counts should appear in sidebar.
5. Standard build → preview → prod sequence per §8.

### Acceptance

- Prebuilt layers show non-zero feature counts in sidebar.
- Build clean: `built=26 missing=0 errored=0`.
- Local↔prod md5 identical post-deploy.
- Branch merged + deleted same chat per §6.12.

### Branch

`refinement-chat105-pmtiles-feature-counts`

### Pre-flight

- Chat 104 shipped clean. DC auto-refresh cron live: `scripts/refresh_dc_anchors.py` reads `data/datacenters/dc_anchors.json` source URLs directly (no separate watchlist file), fetches each, asks Claude API for proposed diffs (status, capacity, commissioned_target, power_source, additional_sources). `.github/workflows/dc-anchors-refresh.yml` runs cron `0 6 * * 1` (Monday 06:00 UTC) + `workflow_dispatch` for manual trigger; opens PR with `outputs/refresh/dc_anchors_proposed.json` if any meaningful proposals; never auto-merges. ANTHROPIC_API_KEY in repo Secrets confirmed by operator. Local URL-fetch smoke-test passed (186 KB from poolside.ai). End-to-end smoke-test deferred to first manual `workflow_dispatch` trigger from GitHub Actions UI.
- Sprint queue: cosmetic PMTiles feature counts (this chat) → wind operator/technology fill via EIA-860 join → Permian abatement work (UNBLOCKED — operator authorized PacketStream proxy spend; sequence: proxy account setup → 1 chat to wire proxy into existing scrapers → resume Permian county sequence) → Comptroller LDAD scrape (UNBLOCKED — operator authorized Playwright; 1-2 chats after Permian abatement core).
- Tool budget for Chat 105: 6–10 (read sidebar code, modify build.py, test with two layers, build, preview, prod, close-out).

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### DC AUTO-REFRESH CRON

`.github/workflows/dc-anchors-refresh.yml`. Cron `0 6 * * 1`. Refresh script in `scripts/refresh_dc_anchors.py` reads existing `dc_anchors.json` + watchlist URL feed; LLM-in-the-loop parser proposes diffs (status changes, capacity revisions, new entries flagged `single_source: true`); diffs surface as PR for human review (never auto-merged). **Hard prerequisite:** Anthropic API key in repo secrets — operator must add via GitHub UI; PAT lacks scope. 1 chat once unblocked.

### ABATEMENT PERMIAN-CORE + PERIPHERAL

Permian-core (Andrews, Ector, Glasscock, Loving, Martin, Midland, Ward, Winkler) → peripheral (Crane, Crockett, Irion, Reagan, Schleicher, Sutton, Upton) county scrape sequence. 4–6 chats. **Hard constraint:** CivicEngage/Akamai bot-block on `reevescounty.org` extends to any county on the same CMS hosting platform — adapter fixes verifiable only after residential-proxy or whitelisted egress provisioned. Detail in `docs/sprint-plan.md`.

### COMPTROLLER LDAD SCRAPE

Supersedes prior "operator manual XLSX download" ask. There is no bulk XLSX. Canonical source: `https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`. Blocked pending operator authorization for JS-rendered scrape (Selenium / Playwright — same authorization class as CRPUB / RRC MFT). Until authorized: backstop only.

### ABATEMENT WEEKLY CRON

`.github/workflows/abatement-scrape.yml`. Cron weekly Monday 06:00 UTC. Commit diff to `data/abatements/abatement_hits_latest.csv` + rolling history. **Hard prerequisite:** `reevescounty.org` Akamai block must be resolved before cron ships, otherwise Reeves silently produces 0 hits.

### MOBILE STAGE 3 — HOTFIX ON DEMAND

Cross-device QA + polish for the mobile-friendly map work shipped in Chats 100–101. Not scheduled. Surfaced issues become discrete patch chats. 0–1 chat per issue.

---

## Prod status

- Layer count: **26**
- Last published deploy: `69ee07134b63d09184004cf9` (Chat 102, 2026-04-26). State=ready. ERCOT queue project aggregation popup. `compute_ercot_group_aggregates(csv_path)` streams `combined_points.csv` once and returns `{group_key: {group_total_mw, group_count, group_breakdown}}` (breakdown is `\n`-joined `<name> · <mw> MW · <county>` lines, sorted by MW desc). `split_combined_csv()` stamps these fields onto every ercot_queue feature's props during NDGeoJSON write. Popup helper `ercotQueueGroupSummaryHtml(props)` renders a summary block (sage-pink card with project group label, total MW, component count, breakdown list) above the per-row table when `group_count > 1`; empty for singletons. Build clean: `built=26  missing=0  errored=0  tiles_total=18933 KB` (+68 KB from prior deploy carrying 3 new fields × 1,778 ercot_queue rows). Local↔prod md5 identical. Aggregation reach: 1,205 groups total, 394 with 2+ components.
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
