# WIP_OPEN.md

Active work. Updated when something completes or a new sprint item is added.

---

## Last deploy

`69f99009df0672911f61e588` — 2026-05-05. Mobile QA hotfix triple in `build_template.html` (topbar overflow, sb-toggle clamp at narrow viewports, tap-to-close drawer). Layer count 24. Build clean `built=26 missing=0 errored=0 tiles_total=12064 KB`.

For older deploy history, `git log --merges --grep "deploy [0-9a-f]" main`.

---

## Last deploy

`6a04990a155513aedd0e842d` — 2026-05-13. R2-3 + R2-5 shipped: completion_year + permit_year exposed for year sliders; oil/gas color split (oil=#16a34a, gas=#dc2626) and depth-scaled symbol size (3px→8.5px across 0-25K ft) for both wells_permian6 and permits_permian6. Build `built=28 missing=0 errored=0 tiles_total=33356 KB`.

For older deploy history, `git log --merges --grep "deploy [0-9a-f]" main`.

## Round 2.5 Part 2 — historical permits backfill

**Part 2A — Wells Spudded report (RRC 2005-current):** **deferred — no
machine-readable source.** Probed `rrc.texas.gov` for the canonical wells-
spudded series; the only first-party data is (a) a JS-rendered data-viz
dashboard at `/resource-center/data-visualization/oil-gas-data-visualization/wells-spudded/`,
and (b) "Monthly Drilling, Completion, and Plugging Summaries" available
only as PDFs from 2020+ at
`/oil-and-gas/research-and-statistics/drilling-information/monthly-drilling-completion-and-plugging-summaries/`.
The 2005-2019 range is not published as bulk CSV. Closest historical
artifact is a single 1960-2018 statewide-summary PDF
(`/media/3yhlylo4/drill_graph_2018.pdf`).

Resolvable paths if this becomes blocking:
1. Selenium/Playwright against the JS data-viz dashboard (operator hasn't
   authorized headless browsers).
2. Per-month PDF parse 2020-current for spud counts only (no per-well lat/lon).
3. Per-permit detail scrape via the W-1 JSP — covered by Part 2B below.

**Part 2B — 1976-2004 per-permit detail-page scrape:** **script written,
not yet run.** `scripts/scrape_rrc_w1_detail_coords.py` consumes the
existing `scripts/scrape_rrc_w1.py` listing output and fetches each in-scope
permit's detail page for surface lat/lon. Resumable via JSON checkpoint;
atomic CSV appends. Estimated runtime ~7 h throttled (~17k permits × 1.5 s).

To trigger overnight:

```bash
# 1. populate the listing-side output (1976-2004 backfill for 6-county scope)
python3 scripts/scrape_rrc_w1.py PECOS 1976 2004
python3 scripts/scrape_rrc_w1.py REEVES 1976 2004
python3 scripts/scrape_rrc_w1.py WARD 1976 2004
python3 scripts/scrape_rrc_w1.py MIDLAND 1976 2004
python3 scripts/scrape_rrc_w1.py MARTIN 1976 2004
python3 scripts/scrape_rrc_w1.py REAGAN 1976 2004

# 2. fetch coords (overnight)
nohup python3 scripts/scrape_rrc_w1_detail_coords.py \\
    --in outputs/refresh/rrc_w1_permits.csv \\
    --out outputs/refresh/rrc_w1_permits_with_coords.csv \\
    > /tmp/rrc_w1_coords.log 2>&1 &
```

When that file exists, the next sprint extends `scripts/parse_rrc.py` to merge
it into `data/permits_permian6.csv`.

## Round 2.5 — what's shipped, what's queued

**Shipped (2026-05-13):**
- Part 1 — Layer inventory: `docs/layer_inventory_2026-05-13.md` (26 layers
  catalogued, currency check clean, gaps identified).
- Part 2 — Permits historical backfill: Wells-Spudded source deferred
  (no machine-readable 2005-2019 source); `scripts/scrape_rrc_w1_detail_coords.py`
  written + documented as overnight nohup trigger.

**Queued for the next layer-data-only sprint (no template/JS work required):**

- **Part 3 — ERCOT precise geocoding upgrade.** Inventory tagged the
  existing layer as Stage-2 geocoded (precise via EIA-860 + USWTDB join,
  county-centroid fallback). The R2.5 spec calls for FERC EQR + PUC
  filings + Ch.312/313 cross-reference. Skipped this run for time;
  next sprint should target precise geocoding for the 30-40 projects
  in the 6-county Permian scope where confidence is currently `county_centroid`.
- **Part 4A/B — EIA-860 + USWTDB refresh checks.** Both layers refreshed
  2026-04-28 (inside the 30-day threshold). No action this sprint.
  Re-check after EIA-860 2025 annual release lands (mid-2026).
- **Part 4C — Comptroller Ch.312/313 split.** API verified working at
  `https://api.comptroller.texas.gov/open-data/v1/tables/ch312-abatement`.
  Returns full abatement metadata (status, value, dates, owner, locl_gov_nm
  = county appraisal district) but no lat/lon — geocoding required via
  property address or address-text in `abat_zone_nm`. Existing
  `tax_abatements` layer (LDAD scrape, 1,486 statewide records, already
  geocoded) likely covers most of the relevant 6-county slice; next
  sprint should reconcile vs. the 312/313 API instead of building a
  parallel layer.
- **Part 4D — HIFLD energy infrastructure layers** (transmission ≥69 kV,
  HIFLD substations, NG/HGL/crude pipelines, NG processing plants, refineries,
  NG storage). Six sub-layers; each fetch + filter + tippecanoe pass is
  ~30-60 min per layer. Atomic-branch one per layer.
- **Part 5 — Counterparty asset boundaries.** Five sites (Pacifico GW Ranch,
  Microsoft Reeves DC, Core Scientific Pecos, Belding Farms/Cockrell,
  Fort Stockton Holdings/Riggs/CWEI). TCEQ CRPUB scrape + Ch.312/313 join
  required per spec. Existing `gw_ranch` polygon already covers Pacifico;
  the other four are net-new boundary digitization. Defer until Part 4C
  abatement reconciliation lands (the abatement addresses are the
  cross-reference source).
- **Part 6 — Sidebar integration for new layers** — happens naturally
  via `filterable_fields` schema when the new layers land. No template
  surgery for new layers, only the R2-4/6/7 overhauls noted below.
- **Part 7 — Documentation updates.** `CLAUDE.md` refresh-trigger phrases
  for wells/permits already added this sprint; the rest land alongside
  their respective layer branches.

**Currency-check status (operator's 30-day rule):** Every present layer is
≤18 days old except `rrc_pipelines` (2019 prebuilt, slow-changing route
data, acceptable). No layer breached the 30-day threshold during this
session.

## Round 2 — deferred to next session

Heavy template/JS work that didn't fit this autonomous run. Each is its own atomic branch when picked up; the wells + permits data layers are already on prod with the right `filterable_fields` schema for the new UI to read.

- **R2-4: comprehensive sidebar filter panel** — top-level filter chips, depth bucket quick chips (<5K / 5-10K / 10-15K / >15K), year-range 5-year quick chips, operator searchable dropdown sorted by count with counts shown, "Showing: <filter summary>" banner at top of map, "Reset filters" button. Acceptance: every filter is reachable in one click from the sidebar root; numeric inputs are debounced; current filter state appears in a header banner. Implementation surface: ~80% in `build_template.html` (extend the existing `filterFieldControlHtml` + the `applyAllFilters` runtime).
- **R2-6: time-series scrubber** — shared bottom-of-map slider that animates feature buildup over time across both layers. Per-feature appearance date = `permit_year` (permits) / `completion_year` (wells). Play / pause / reset, 1 yr/sec, respects filter state. Implementation: new component, MapLibre `filter` expression on `<=` of slider value.
- **R2-7: live stats panel + downloads** — collapsible top-right panel with count/percentile/distribution stats per layer, IQR/Tukey outlier filtering on depth, PDF / CSV / XLSX / Markdown exports. Heaviest item — needs a stats compute engine + download serializers.
- **R2-8: sale-area vs peers comparison** — toggle that pivots stats panel into side-by-side subject (Pecos/Reeves/Ward) vs peer (Midland/Martin/Reagan) view. Per-county-normalized rates. The data already carries `county_role` for this; UI work only.
- **R2-9: thesis bookmarks (Saved views)** — sidebar dropdown with 8 pre-baked filter combinations ("Permits in last 10 years, sale-area only", etc.). URL hash updates for shareability. The template already reads `location.hash` at boot; this is a sidebar-component addition.

All five are well-scoped and unblocked — they just need a dedicated session (~6-10 hours total) on the front-end.

## Decision log — 2026-05-13 — 6-county rescope (Hanwha legal-defense framing)

Following R1 ship, the 11-county Permian scope (`wells_pecos11`) was rescoped to a tight 6-county sale-area-vs-peer set (`wells_permian6`). Rationale: this map is the visual exhibit for the Hanwha Energy USA land-sale defense, and the thesis ("drilling activity has collapsed in the sale area while the geological neighbors are booming") reads more clearly when the comparison set is just the immediate Permian peers, not 10 sparsely-drilled adjacent counties.

**Subject counties (sale area + immediate neighbors):** Pecos, Reeves, Ward.
**Active Permian peer counties (boom area for contrast):** Midland, Martin, Reagan.

Each well row carries `county_role` ∈ {subject, peer} for downstream comparison views (R2-8). Per-county wellbore counts:

| Role | County | Wells |
|---|---|---:|
| subject | Pecos | 17,501 |
| subject | Reeves | 12,957 |
| subject | Ward | 14,565 |
| peer | Martin | 18,050 |
| peer | Midland | 20,664 |
| peer | Reagan | 15,487 |
| **total** | | **99,224** |

Cardinality before/after: 115,908 (11-county) → 99,224 (6-county). Lat/lon-bearing: 101,408 → 89,944 (90.6% coverage on the 6-county filter). PMTiles 7.59 MB → 10.26 MB (the new `county_role` + `total_depth` numeric coercion add overhead).

## Decision log — 2026-05-13 — R2-1: wells layer filtered to active only

R2-1 spec asked for "wells status = active OR drilling" only, excluding
inactive / plugged / abandoned / dry-hole / P&A / other. Mapping derived
from the dbf900 wellbore database (wba091 layout):

- `plug_flag` at WBROOT byte 91 — `Y` = plugged / abandoned / P&A
  (33,709 of 115,908 wells in the original 11-county scope = 29%).
- `active_flag` at WBCOMPL byte 46 — sparse ('A' in only 5,373 of 99,224
  records; majority are blank). Not a reliable active marker on its own.
- Drilling-in-progress wells aren't represented in dbf900 — those live
  in the permits layer (`permits_permian6`). So "drilling" status maps
  to a different layer entirely.

Filter applied at the parser (`scripts/parse_rrc.py:flush()`): exclude
rows where `plug_flag == 'Y'`. The 6-county active well count:

| Role | County | Before (all wells) | After (active) | Plugged share |
|---|---|---:|---:|---:|
| subject | Pecos | 17,501 | 12,095 | 31% |
| subject | Reeves | 12,957 | 10,884 | 16% |
| subject | Ward | 14,565 | 9,950 | 32% |
| peer | Martin | 18,050 | 13,568 | 25% |
| peer | Midland | 20,664 | 14,827 | 28% |
| peer | Reagan | 15,487 | 10,004 | 35% |
| **total** | | **99,224** | **71,328** | **28%** |

## Decision log — 2026-05-13 — Part C: permits_permian6 (forensic parse)

The previous "scoped-out, no published daf-series layout" deferral was overridden. Forensic byte-position analysis of `daf420.dat.MM-DD-YYYY` (RRC EOM + Lat/Lon monthly snapshots) cracked the structure end-to-end. Field positions documented in `docs/rrc_layouts/permit_purpose_codes.md` and the `M_*` slice constants at the head of `scripts/parse_rrc.py`.

Key findings:
- The file is a multi-record-type concatenation: prefix `0108` = permit master (212 b), `0208` = permit detail (510 b), `14`/`15` = WGS84 lat/lon (26 b each), plus sub-records for remarks/casings.
- A permit "block" starts at each `0108` line and continues until the next.
- County FIPS lives at master bytes 11–13 (last 3 digits of the 10-digit master id) — verified against the 6-county scope.
- Total depth at detail bytes 322–331 (10-digit zero-padded feet) — verified on KING/UNIVERSITY/REED hand-decoded permits.
- Wellbore profile: byte 160 = "H" → horizontal (51% across 28,842 permits, matches real-world Permian rate). The earlier "HL" substring heuristic was too narrow.
- Filing-purpose code at byte 182 (X 64%, E 18%, P 12%, 3 6%) — exposed in popup as raw code; canonical RRC-published mapping unavailable.
- Oil/gas: **no reliable single-byte indicator** in this file. R2-5's color scheme will display "unknown" for all rows until a `permits_permian6 ⋈ wells_permian6` post-join is added.

Coverage: 105 monthly snapshots from 2018-01 through 2025-12 (the EOM+LatLon folder only goes back to 2018, so the user's "1976-present" wish is unachievable from this source — pre-2018 permits have no lat/lon and cannot be mapped). 30,927 in-scope permits, 28,842 with parseable total_depth → output layer. PMTiles 10.36 MB.

Per-county permits 2018-present:
| Role | County | Permits |
|---|---|---:|
| subject | Pecos | 1,409 |
| subject | Reeves | 7,979 |
| subject | Ward | 2,183 |
| peer | Martin | 7,357 |
| peer | Midland | 7,505 |
| peer | Reagan | 2,409 |
| **total** | | **28,842** |

Hanwha thesis sanity check (subject vs peer permit counts by year):
| Year | Subject | Peer | Peer/Subject |
|---:|---:|---:|---:|
| 2017 | 1,292 | 1,479 | 1.1× |
| 2020 |   980 | 1,708 | 1.7× |
| 2023 | 1,299 | 2,586 | 2.0× |
| 2024 |   608 | 1,406 | 2.3× |

The peer-to-subject ratio doubled from ~1× in 2017 to ~2× by 2023. Pecos alone (1,409 permits over 8 years = ~176/yr) is dramatically less active than Martin/Midland (~900-1,000/yr each). Thesis is supported by the data.

---

## Decision log — 2026-05-13 — RRC permits/wells sprint scope pivot

Sprint spec asked for two new layers (`permits_pecos11` + `wells_pecos11`, 1976-present, with lat/lon, 11 Permian counties). Delivered one (`wells_pecos11`) and deferred the other after source-discovery probing.

**What works:**
- `scripts/fetch_rrc.py` — RRC GoAnywhere PrimeFaces POST scrape (validated end-to-end). GET MFT folder link → harvest JSESSIONID + ViewState → POST row id to `/webclient/godrive/PublicGoDrive.xhtml`.
- `scripts/parse_rrc.py wells` — streams `dbf900.txt.gz` (29.6M segment-records, 1.2M wellbores) in 17s, filters to 11 counties → `data/wells_pecos11.csv`. Layout: `docs/rrc_layouts/wba091_well-bore-database.pdf`. Lat/lon from WBNEWLOC (seg 13) at pos 133/143, PIC S9(3)V9(7) zoned-decimal. RRC convention: longitude stored as positive magnitude — parser forces negative for Texas hemisphere.
- Layer build: 115,908 wells in scope, 101,408 with WGS84 coordinates (87.5%), 7.6 MB PMTiles, no cardinality issues.

**What's blocked — permits_pecos11:**
- RRC's "Drilling Permit Master & Trailer" file (`daf802.txt.gz`, 1.21 GB) has no published byte-position layout. The "Pending" file IS documented (pendingdrillingpermits.pdf) but its folder has been stale since 2021-02. The "EOM + Lat/Lon" `daf420.dat.MM-DD-YYYY` series has lat/lon but no public layout.
- Existing `scripts/scrape_rrc_w1.py` covers permit listing rows 1976-present but defers lat/lon to per-permit detail-page fetches (~40h throttled for the full Permian backfill).
- ARCHITECTURE.md §11 entry rewritten to reflect the actual blocker; revisit if RRC publishes the daf-series layout OR operator authorizes the long detail-page scrape.

**Deploy + push status:** local build clean (`built=27 missing=0 errored=0 tiles_total=19656 KB`), commit `90234c0` on local branch `refinement-rrc-permits-wells`. Push to origin AND deploy both blocked: this WSL clone has no `NETLIFY_PAT`, no `GITHUB_PAT`, no `.git-credentials`, no SSH key, no `gh` CLI — `git push` exits with `could not read Username for 'https://github.com'`. To ship: populate `.env` (both PATs) on the operator workstation, then `git push -u origin refinement-rrc-permits-wells && bash scripts/deploy.sh --rebuild && bash scripts/close-out.sh refinement-rrc-permits-wells <deploy-id> "Add wells_pecos11"`.

## Round 2 backlog — Hanwha thesis features (gated)

Round 2 spec received 2026-05-13. Ten items (R2-1 … R2-10) covering: wells filter to active+drilling, permits filter to production-purpose only, full historical depth (1976/1964-present), sidebar filter UX overhaul, oil/gas color + depth-scaled symbol size, time-series scrubber, live stats panel with PDF/CSV/XLSX export, Pecos-vs-active-Permian-peers comparison, pre-baked thesis bookmarks, verification + ship.

**Hard gate:** Round 2 explicitly conditions on "After the current RRC permits/wells task (Round 1) ships to prod, execute this Round 2 batch autonomously." R1 has not shipped to prod (push + deploy both blocked above).

**Soft gate — permits layer:** every R2 item that touches permits (R2-2, R2-3 perm half, R2-4 perm filters, R2-5 perm color, R2-6 perm half of scrubber, R2-7 perm stats panel, R2-8 perm comparison, R2-9 perm bookmarks) depends on `permits_pecos11` being a real layer. That layer is still scoped-out per the Round 1 decision above. R2-8 also wants Midland + Ector counties added for peer comparison — outside the 11-county scope by design.

**Foldable into R1 (deferred to keep R1 atomic per user's own protocol):** R2-1 (wells active+drilling filter at the parse layer) — would require remapping WBROOT plug_flag + active_flag codes to a true status field; R2-3 wells half (spud date) — would require adding WBDATE segment (key 03) `WB-W2-G1-DATE` to the parser; R2-5 wells color/size — pure `layers.yaml` edit. None folded; the user's instruction is "Each item is its own atomic branch." Once R1 ships, these become R2-1, R2-3, R2-5 atomic branches.

---

## Active sprints

### ERCOT queue geocoding — Stage 3

**Status:** blocked on operator-curated override CSV at `data/ercot_queue_overrides.csv`.

**Spec** (settled, do not re-litigate):
- WRatio ≥ 88 (rapidfuzz partial_ratio fallback to ratio)
- Norm-name suffix-stripping: drop `LLC`, `INC`, `LP`, `LTD`, `CORP`, `CO`, trailing parenthetical project codes
- Idempotent CSV read — re-running the geocode pass with the same CSV produces no diff
- Last-precedence pass — manual override always beats Stage 1+2 algorithmic match
- `coords_source = manual_override` for all rows touched by Stage 3
- Atomic write per `OPERATING.md §3 rule 4` — temp file + `os.replace`

**Resume:** when CSV exists at `data/ercot_queue_overrides.csv`, run `python3 scripts/geocode_ercot_queue.py --stage 3` (or whatever the script expects — verify against Stage 2 invocation pattern). Then full build, deploy, verify aggregate match rate against Stage 2 baseline, commit + merge.

**Acceptance for Stage 3:**
- `coords_source = manual_override` rows in built registry equal CSV row count
- Aggregate solar+wind+battery match rate logged and improved vs Stage 2
- No regression in Stage 1+2 rows (algorithmic matches preserved)

### Counties color holistic contrast review

`#fbbf24` (amber) was chosen under time pressure as a basemap-universal hotfix. Worth a calm review: verify against `satellite`, `carto_light`, and dark basemaps; check for clash with hyperscale campus strokes (`la_escalera`, `gw_ranch`, `longfellow_ranch` lines) and tiger_highways amber. Pick a color that survives all three basemaps without competing with overlays. Pure `layers.yaml` edit + visual review.

### county_labels render review

If operator-named counties still appear unlabeled at zoom 7–9, inspect MapLibre `text-allow-overlap` / `symbol-sort-key` / `text-padding` on the county_labels source-layer config in `build_template.html`. Conditional on visual confirmation that the issue still exists.

### Mobile popup audit

Chat-mode Chat 127 fixed three mobile chrome issues. Remaining mobile risk is feature-popup density: `ercot_queue` group-aggregation popup can have many breakdown rows; `tax_abatements` popup carries long text fields. Verify `60vh` max-height + scroll behavior holds at mobile widths against the worst-offender popups. Diagnostic-first; if no issues found, no deploy needed.

---

## Backlog

### Infrastructure

- Akamai datacenter-egress block on `reevescounty.org` 403s any cloud-runner traffic regardless of UA / TLS fingerprint. Hard prerequisite for the Reeves County abatement-weekly-cron sprint item if it ever resumes. Unblock paths: residential-proxy egress (paid), Akamai allowlisting via Reeves County IT (low likelihood), search-API result pages.
- `GITHUB_PAT` can push branches and merge, returns 403 on PR creation. Direct-merge-to-main is the protocol per `OPERATING.md §6`.

### UI / UX

- Counties outline color `#fbbf24` revisit (see active sprint above).
- `date_range` filter literal extension to eia860_plants/battery/wind would require padding `yyyy` → `yyyy-01-01` in 3 ingest scripts (`refresh_eia860.py` plants/battery + `refresh_uswtdb.py` wind). Currently those layers use `numeric` year-slider — works fine, low priority.
- Filter inputs (`.filter-text`, `.filter-range input`) are 40px on mobile, not strictly the 44px WCAG bar. Acceptable per Apple HIG (≥40px) but flag for review if operator testing surfaces hit-rate issues.
- `county_labels` declutter at low zoom — 254 labels means MapLibre symbol-collision will hide overlaps below ~zoom 7. Conditional sprint item above; do not pre-empt visual review.

### Audit drift (run `bash scripts/audit.sh` to recheck)

- `OPERATING.md` line count vs ≤250 target
- `WIP_OPEN.md` byte count vs ≤8192 target
- Stranded `refinement-*` branches on origin (should be 0)

---

## Process notes

- `scripts/close-out.sh` enforces atomic deploy+merge and the `refinement-*` branch lifecycle. Use it; don't hand-roll merges to `main`.
- `scripts/audit.sh` is cheap to run after any drift-prone change. Includes it in the verification step for medium/high blast-radius work.
- The `/*__BUILD_ID__*/` token substitution in `build.py:render_html` (UTC timestamp + nonce) is what makes `deploy.sh`'s md5-parity poll a reliable readiness signal. Removing the marker would break the poll.
