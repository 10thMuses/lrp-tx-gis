# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat`** = task spec for the immediately-next shipping chat. **`## Sprint queue`** = N+2 and beyond. Multi-step sprint detail lives in `docs/sprint-plan.md` (deleted per item when shipped).

---

## Next chat

**Chat 96 — POWER PLANT POPUP REDESIGN (yaml-only) — RESUME, partial state on branch.** Branch `refinement-chat96-power-plant-popup-redesign` already exists on origin with 4 of 5 layers edited: `eia860_plants`, `eia860_battery`, `wind` (commit `6dccf4d`) + `solar` (commit added Chat 96b). Session-open detects + checks out the existing branch. Resume from there.

### Task

1. **Already on branch (do NOT recreate)**: 4 yaml edits landed. Verify with `git log --oneline -4`.
2. **Edit `layers.yaml` for the remaining 1 layer**:
   - **`ercot_queue`**: popup ADD `operator` (insert after `entity` or wherever logical). Filterable_fields: flip `county` from `text` to `categorical` to match the pattern across the other 4 layers. Existing `mw` numeric + `commissioned` categorical satisfy the rest of the contract.
3. Commit + push (§6.11).
4. `build. deploy to prod.` Verify per §8 step 4 (curl real UA, 25 layer ids).
5. Spot-check rendered popup HTML for one feature in each of the 5 layers (grep prod HTML for the popup template; tile data already verified Chat 95).
6. Close-out per §5 — **this chat must merge to main** since it deploys (§6.12 atomic deploy+merge+delete).

### Field contract

Unchanged from original Chat 96 spec — see prior `## Next chat` template archived in WIP_LOG when this chat ships. The 3 edits already on branch establish the pattern; mirror it for `solar` and `ercot_queue`.

### Acceptance

- All 5 layers' popup spec in prod HTML omits `sector` and includes `commissioned` + `operator` (USWTDB-driven `wind` exempt from operator per Chat 95 schema gap).
- `eia860_plants` popup spec includes at minimum: `operator`, `commissioned`, `capacity_mw`, `technology`, `fuel`.
- Build errored=0, layer count=25, deploy state=ready.
- Branch merged + deleted same chat per §6.12.

### Branch

`refinement-chat96-power-plant-popup-redesign` (already exists with partial work; session-open will detect + check out).

### Pre-flight

- Schema verified Chat 96 partial: all required fields present in `combined_points.csv` header (operator, commissioned, capacity_mw, technology, fuel, manu, model). Skip re-verification.
- `commissioned` ships as `categorical` (build.py auto-promotes/demotes based on `CATEGORICAL_CAP`). Matches `ercot_queue` precedent. Pattern established in commit `6dccf4d`.
- `cairosvg` and `openpyxl` may need install in the build container (`pip install --break-system-packages cairosvg openpyxl`); see Chat 95 gotcha (`build.py` imports `build_sprite` at module top which hard-imports `cairosvg`).
- Tool-call budget: 5. yaml edit + commit (1), build (1), deploy MCP + npx (2), poll + verify + spot-check + close-out (1).

---

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### ABATEMENT PERMIAN-CORE + PERIPHERAL

Permian-core (Andrews, Ector, Glasscock, Loving, Martin, Midland, Ward, Winkler) → peripheral (Crane, Crockett, Irion, Reagan, Schleicher, Sutton, Upton) county scrape sequence. 4–6 chats. **Hard constraint:** CivicEngage/Akamai bot-block on `reevescounty.org` extends to any county on the same CMS hosting platform — adapter fixes verifiable only after residential-proxy or whitelisted egress provisioned. Detail in `docs/sprint-plan.md`.

### COMPTROLLER LDAD SCRAPE

Supersedes prior "operator manual XLSX download" ask. There is no bulk XLSX. Canonical source: `https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`. Blocked pending operator authorization for JS-rendered scrape (Selenium / Playwright — same authorization class as CRPUB / RRC MFT). Until authorized: backstop only.

### ABATEMENT WEEKLY CRON

`.github/workflows/abatement-scrape.yml`. Cron weekly Monday 06:00 UTC. Commit diff to `data/abatements/abatement_hits_latest.csv` + rolling history. **Hard prerequisite:** `reevescounty.org` Akamai block must be resolved before cron ships, otherwise Reeves silently produces 0 hits.

### LEGEND ON PRINT / SHARE / PDF

Print CSS at `build_template.html` hides `.sidebar` on `@media print`. Sidebar IS the legend; prints ship without it. Inject print-only legend element enumerating active layers (name + color swatch + symbol) into print header or footer. Fit within 10.3"×7.1" landscape. Handle >15 active layers via multi-column or multi-page.

### DC RESEARCH → DC BUILD → DC AUTO-REFRESH

3-chat sub-sequence. Research anchors: Longfellow/Poolside (Pecos), Stargate (Abilene), Project Matador/Fermi → structured data file → layer build → GitHub Actions weekly refresh with LLM-in-the-loop parser. Detail in `docs/sprint-plan.md`.

### MOBILE-FRIENDLY MAP

Responsive breakpoints, touch-friendly controls, pinch-zoom tuning, measure tool + print-to-PDF mobile usability, popup sizing. 2–3 chats.

### ERCOT QUEUE PROJECT AGGREGATION POPUP  *(low priority)*

`ercot_queue` has 1,205 distinct project `group` keys; 394 groups have 2+ components. Build-time aggregation in `build.py`: compute `group_total_mw`, `group_count`, `group_breakdown` per group; popup template renders summary line + breakdown list. Test case Longfellow__Pecos: 6 rows, 2,153.3 MW total.

---

## Prod status

- Layer count: **25**
- Last published deploy: `69ed43136147a9a6b3966ebd` (Chat 95, 2026-04-25). State=ready. Carries EIA-860 (2024-data) plants + battery refresh and full USWTDB wind refresh merged into `combined_points.csv`. Prod tile bytes verified match local build (`eia860_plants.pmtiles` 87061 B header md5 identical local↔prod).
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

**Infrastructure:**
- `NETLIFY_PAT` absent from `CREDENTIALS.md`. Netlify MCP proxy path canonical
- `GITHUB_PAT` can push branches, 403 on PR creation. Direct-merge-to-main is the protocol (OPERATING.md §9)
- **Akamai datacenter-egress block on `reevescounty.org`** — cloud-runner / GitHub-Actions traffic 403s regardless of UA / TLS fingerprint. Hard prerequisite for the abatement-weekly-cron sprint item. Unblock options: residential-proxy egress (paid), Akamai allowlisting via Reeves County IT (low likelihood), search-API result pages

**Process:**
- Chat 92 §6.12 violation (deploy + merge atomic): published deploy `69ed2cdf4039c554a1316ad2` to prod but deferred close-out merge, citing scope-creep. Reconciled in Chat 93 (merge `3a59a73`). Root cause: doc-restructure work appeared on a feature branch alongside the data-layer work, blowing past §6.13 stage-fits-one-chat. Preventive structural fix: pre-commit hook could reject doc-structure changes on `refinement-*` branches; lower-effort alternative is operator-side discipline at branch-naming time.

**Outstanding credential hygiene:**
- `GITHUB_PAT` leak from Chat 87 unrotated per operator override. Token valid until 2027-04-21

**Permanently excluded:** see ARCHITECTURE.md §11

**Other (non-GIS):** Grid Wire Vol. 7. Tier 2 water availability assessments. Excel returns model.
