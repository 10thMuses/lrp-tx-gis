# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat`** = task spec for the immediately-next shipping chat. **`## Sprint queue`** = N+2 and beyond. Multi-step sprint detail lives in `docs/sprint-plan.md` (deleted per item when shipped).

---

## Next chat

**Chat 94 — POWER PLANT DATA REFRESH (data-only).** Re-pull EIA-860 (plants, battery) and USWTDB (wind) to fill blank `operator` / `commissioned` / `technology` / `fuel` / `capacity_mw` fields. Build, deploy to prod. Popup-template redesign deferred to Chat 95 per §6.13 (stage fits one chat).

Selected because ABATEMENT PERMIAN-CORE remains blocked on Akamai egress (see Open backlog) and POWER PLANT REFRESH has no external blockers and a clean acceptance signal (null-rate drop on `eia860_plants` capacity_mw / technology / fuel).

### Task

1. `refresh eia860_plants, eia860_battery, wind.` — fetch EIA-860 (latest 2025 release at `eia.gov/electricity/data/eia860/`) and USWTDB (`eersc.usgs.gov/api/uswtdb/v1/turbines`). Validate non-empty + bounded lat/lon + required columns per refresh-cycle protocol (OPERATING.md §8). Write to `outputs/refresh/`.
2. One-line null-rate diff for each layer: before vs. after on `operator`, `commissioned`, `technology`, `fuel`, `capacity_mw`. Goal: meaningful drop on `eia860_plants` (currently 476/1367 null on capacity_mw / technology / fuel per Open backlog).
3. `merge eia860_plants from outputs/refresh/...`, then same for `eia860_battery` and `wind`. Write updated `combined_points.csv`.
4. `build. deploy to prod.` Verify per §8 step 4 (curl with real UA, 25 layer ids in HTML, EIA point popups carry refreshed fields). Tile spot-check on one EIA point.
5. Close-out per §5.

### Acceptance

- `outputs/refresh/eia860_plants_<date>.csv`, `outputs/refresh/eia860_battery_<date>.csv`, `outputs/refresh/wind_<date>.csv` all present and non-empty.
- `combined_points.csv` row count for `layer_id` in {`eia860_plants`, `eia860_battery`, `wind`} unchanged in shape (rows replaced 1:1 by `(latitude, longitude)` join key, not appended).
- `eia860_plants` null rate on `capacity_mw` drops below 35% of rows (vs. current 35%).
- New deploy `state=ready`. Prod HTML grep returns 25 layer ids. `eia860_plants` popup_labels rendered with at least `capacity_mw`, `technology`, `fuel`, `operator`, `commissioned`.
- Branch merged to main + deleted same chat per §6.12.

### Branch

`refinement-chat94-power-plant-refresh`.

### Pre-flight

- Source URLs unchanged from prior pulls. If EIA-860 2025 release URL has shifted, update `scripts/refresh_eia860.py` headers and proceed.
- USWTDB API stable; no auth required.
- No build.py / build_template.html edits required (data-only change).
- Tool-call budget: shipping ceiling 12. Composite bash for refresh + diff (1), composite for merge + build + deploy (1), MCP deploy (2), poll/curl verify (1), close-out (1). Reserve 6 for blocker recovery.

---

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### POWER PLANT POPUP REDESIGN

Follow-on to Chat 94 data refresh. Rewrite popup templates for `eia860_plants`, `eia860_battery`, `solar`, `wind`, `ercot_queue`: DROP `sector`; ADD `commissioned` / COD date, `operator`, `capacity_mw`, `fuel` / `technology`. Filter UI reflects same fields. Detail in `docs/sprint-plan.md`.

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
- Last published deploy: `69ed2cdf4039c554a1316ad2` (Chat 92, 2026-04-25). State=ready. Carries §1 tceq_gas_turbines field expansion + §2 tax_abatements popup rename + §3 wells min_zoom 6→10. Reconciled to main in Chat 93 (merge `3a59a73`).
- URL: `https://lrp-tx-gis.netlify.app` — requires real User-Agent on curl (`-A "Mozilla/5.0"`).

---

## Open backlog

**Data-pipeline gaps** (non-blocking):
- `eia860_plants`: 476/1367 rows null `capacity_mw` / `technology` / `fuel` — targeted by Chat 94
- `combined_points.csv` blank `operator` / `commissioned` on EIA point layers — targeted by Chat 94
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
