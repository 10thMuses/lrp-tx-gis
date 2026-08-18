# 02 — Data Sources: exhaustive input inventory

Every layer on the map, where its data comes from, what filters and assumptions were
applied on the way in, how often it should be refreshed, and how it is known to break.

**Governing rule (`OPERATING.md §3.3`):** *never hand-code coordinates or feature values.*
Every point and polygon traces to a public dataset cited here. The five documented
exceptions are marked **APPROXIMATE** and are called out individually in [§4](#4-hand-placed-and-approximate-geometry).

---

## 1. Layer catalog — all 39 layers

Ordered as they appear in `layers.yaml`. `Default` = visible on first load.

| # | Layer ID | Group | Geom | Storage | Default | Source of truth |
|---|---|---|---|---|:---:|---|
| 1 | `counties` | Reference | line | combined | ✅ | Census TIGER 2023/2024 county boundaries |
| 2 | `cities` | Reference | point | combined | ✅ | Toponyms, 9 West-Texas municipalities |
| 3 | `caramba_north` | Land & Deal | fill | combined | ✅ | Project GeoJSON (1,300 ac tract) |
| 4 | `oxy_power` | OXY Footprint | point | `data/oxy/oxy_power.geojson` | ✅ | EIA-860 + OSM/HIFLD, curated |
| 5 | `oxy_midstream` | OXY Footprint | point | `data/oxy/oxy_midstream.geojson` | ✅ | EIA-757 / EPA FRS, curated |
| 6 | `oxy_ercot` | OXY Footprint | point | `data/oxy/oxy_ercot.geojson` | ✅ | ERCOT GIS queue, curated |
| 7 | `oxy_permits` | OXY Footprint | point | `data/oxy/oxy_permits.geojson` | ✅ | TCEQ air authorizations, curated |
| 8 | `oxy_water` | OXY Footprint | point | `data/oxy/oxy_water.geojson` | ✅ | Produced-water / desal facilities, curated |
| 9 | `oxy_carbon` | OXY Footprint | point | `data/oxy/oxy_carbon.geojson` | ✅ | EPA Class VI / Subpart RR, curated |
| 10 | `oxy_drilling_permits` | OXY Footprint | point | `data/oxy/oxy_drilling_permits.geojson` | ❌ | RRC daf420 EOM + Lat/Lon |
| 11 | `solstice_substation` | Local Focal Points | point | combined | ✅ | AEP Solstice substation |
| 12 | `waha_circle` | Local Focal Points | point | combined | ✅ | **Hand-placed** — Waha hub marker |
| 13 | `labels_hubs` | Local Focal Points | label | combined | ✅ | Toponym label (sidebar-hidden) |
| 14 | `la_escalera` | Hyperscale DC | fill | combined | ✅ | **APPROXIMATE** ranch outline |
| 15 | `longfellow_ranch` | Hyperscale DC | fill | combined | ✅ | **APPROXIMATE** ranch outline |
| 16 | `gw_ranch` | Hyperscale DC | fill | combined | ✅ | **APPROXIMATE** campus footprint |
| 17 | `mpgcd_zone1` | Local Focal Points | fill | combined | ✅ | **APPROXIMATE** — digitised from MPGCD PDF |
| 18 | `eia860_plants` | Power Generation | point | combined | ❌ | EIA-860 annual, Generator sheet |
| 19 | `eia860_battery` | Power Generation | point | combined | ❌ | EIA-860 `3_3_Energy_Storage` |
| 20 | `wind` | Power Generation | point | combined | ❌ | USWTDB (USGS/LBNL) API |
| 21 | `solar` | Power Generation | point | combined | ❌ | EIA-860 `3_3_Solar` |
| 22 | `substations` | Transmission & Grid | point | combined | ❌ | OSM Overpass |
| 23 | `tpit_subs` | Transmission & Grid | point | combined | ❌ | ERCOT TPIT XLSX |
| 24 | `transmission` | Transmission & Grid | line | combined | ❌ | HIFLD ArcGIS, ≥100 kV |
| 25 | `tpit_lines` | Transmission & Grid | line | combined | ❌ | ERCOT TPIT XLSX |
| 26 | `hifld_ng_pipelines` | Energy Infrastructure | line | `data/hifld/` | ❌ | HIFLD/EIA FEMA Region 6 mirror |
| 27 | `hifld_crude_pipelines` | Energy Infrastructure | line | `data/hifld/` | ❌ | Same — 21 features in scope |
| 28 | `hifld_hgl_pipelines` | Energy Infrastructure | line | `data/hifld/` | ❌ | Same — 15 features in scope |
| 29 | `hifld_ng_processing` | Energy Infrastructure | point | `data/hifld/` | ❌ | EIA via AGOL — 53 plants in scope |
| 30 | `ercot_queue` | Projects | point | combined | ❌ | ERCOT monthly GIS Report |
| 31 | `county_labels` | Reference | label | combined | ✅ | Derived from TIGER centroids |
| 32 | `rrc_pipelines` | Pipelines | line | **prebuilt** | ❌ | RRC 2019 snapshot — *no local source* |
| 33 | `tceq_gas_turbines` | Permits | point | combined | ❌ | TCEQ `turbine-lst.xlsx` |
| 34 | `tiger_highways` | Reference | line | **prebuilt** | ✅ | Census TIGER — *no local source* |
| 35 | `bts_rail` | Reference | line | **prebuilt** | ✅ | BTS — *no local source* |
| 36 | `permits_permian6` | Permits | point | `data/permits_permian6.csv` ⚠️ | ❌ | RRC daf420 EOM + Lat/Lon |
| 37 | `wells_permian6` | Oil & Gas Spud Wells | point | `data/wells_permian6.csv` ⚠️ | ❌ | RRC dbf900 Full Wellbore |
| 38 | `tax_abatements` | Permits | point | combined | ❌ | Commissioners-court agenda scrape (LDAD) |
| 39 | `dc_anchors` | Projects | point | `data/datacenters/dc_anchors.json` | ❌ | Hand-curated, multi-sourced |

⚠️ **`wells_permian6` and `permits_permian6` source files are gitignored.** They are
regenerated on demand from RRC. A clean clone will not build these two layers until you
run the RRC refresh — see [§3.1](#31-railroad-commission-of-texas-rrc).

**Prebuilt layers (32, 34, 35) have no source data anywhere in the repo.** They exist
only as `.pmtiles` files already on the production CDN, resolved at build time via
`build.py`'s tier-3 fallback to `https://lrp-tx-gis.netlify.app/tiles/<id>.pmtiles`.
Back them up before touching hosting — see
[`00-MIGRATION-RUNBOOK.md §8`](00-MIGRATION-RUNBOOK.md#8-code-changes-required-by-the-migration).

---

## 2. Geographic and temporal scope

Different layers use different footprints. Knowing which one applies prevents
misreading an empty area as "nothing there".

| Scope name | Counties | Applies to |
|---|---|---|
| **6-county Permian** | Pecos, Reeves, Ward (subject/sale area) · Midland, Martin, Reagan (peer/boom area) | `wells_permian6`, `permits_permian6`, all four `hifld_*` layers |
| **23-county West Texas** | Andrews, Borden, Brewster, Crane, Crockett, Culberson, Dawson, Ector, Fisher, Glasscock, Howard, Irion, Jeff Davis, Kent, Loving, Martin, Midland, Mitchell, Pecos, Reagan, Reeves, Schleicher, Scurry, Sterling, Sutton, Terrell, Tom Green, Upton, Ward, Winkler | `tceq_gas_turbines`, `scrape_abatements.py`, `fcc_fiber_coverage` |
| **Texas statewide** | — | `eia860_*`, `wind`, `solar`, `ercot_queue`, `substations`, `transmission`, `dc_anchors` |
| **Statewide, all counties** | — | `tax_abatements` (1,495 LDAD records; only 5 fall inside the 6-county scope) |

### The subject-vs-peer split

The `county_role` field (`subject` \| `peer`) is the analytical backbone. It was
introduced 2026-05-13 when the original 11-county `wells_pecos11` scope was reduced to
six counties to support the sale-area-versus-boom-area comparison. Any chart, export or
stats panel that groups by `county_role` is making that comparison. The **Spuds Summary
(PDF)** export always splits across all six counties *regardless of active filters*, by
design, so the comparison cannot be accidentally filtered away.

### Time coverage

| Layer | Coverage | Note |
|---|---|---|
| `wells_permian6` | 1964 – present | Recompletions/re-entries excluded (`completion_year < spud_year` filtered out) so counts are genuine new wellbores |
| `permits_permian6` | 2018-01 – present | 108 monthly EOM snapshots. **1976–2017 backfill is incomplete** — see [`08-ROADMAP-AND-GAPS.md`](08-ROADMAP-AND-GAPS.md) |
| `oxy_drilling_permits` | 2020 – 2026 | 294 permits, 3 OXY filer numbers |
| `tceq_gas_turbines` | Received ≥ 2020 | 6 permits pass. Six pre-2020 grandfathered turbines are **deliberately excluded** and listed in `outputs/refresh/CHANGELOG.md` |
| `ercot_queue` | Snapshot | Label carries the snapshot date (currently 2026-04-21) |
| `eia860_*`, `solar` | 2024 data year | Released 2025. Bump with `--year 2025` when EIA publishes. |
| `fcc_fiber_coverage` | 2025-06-30 vintage | Service URL slug says "December 2024"; the item is the June 2025 BDC release |
| `rrc_pipelines` | 2019 | Frozen snapshot; accepted per `ARCHITECTURE.md §11` |

---

## 3. Source-by-source detail

### 3.1 Railroad Commission of Texas (RRC)

The single most important and most fragile source. Feeds `wells_permian6`,
`permits_permian6`, `oxy_drilling_permits` and (frozen) `rrc_pipelines`.

**Endpoint:** `https://mft.rrc.texas.gov/link/<UUID>` — a GoAnywhere MFT PrimeFaces
folder browser. It is not a plain file URL.

**Protocol** (implemented end-to-end in `scripts/fetch_rrc.py`, validated 2026-05-13):

1. `GET` the landing page; harvest the `JSESSIONID` cookie and the
   `javax.faces.ViewState` token.
2. `POST` to `/webclient/godrive/PublicGoDrive.xhtml` with the ViewState plus
   `fileTable:<row>:j_id_2f` identifying the row you want.
3. Stream the response to `data/rrc_raw/<filename>` via atomic temp+replace.

**Files consumed:**

| File | Feeds | Layout reference |
|---|---|---|
| `dbf900.txt.gz` — Full Wellbore, ASCII fixed-width, 247-byte records, 28 segments keyed by a 2-byte record-ID prefix | `wells_permian6` | `docs/rrc_layouts/wba091_well-bore-database.pdf` |
| `daf420.dat.MM-DD-YYYY` — Drilling Permit Master, monthly EOM + Lat/Lon | `permits_permian6`, `oxy_drilling_permits` | Dual 0108/0109 record-format reader; layout **not published by RRC** — parsed forensically |
| W-1 listing pages at `webapps.rrc.state.tx.us/DP/` | 1976–2017 permit backfill (incomplete) | `docs/rrc_layouts/pendingdrillingpermits.pdf` |

**Segments the wellbore parser consumes** (`scripts/parse_rrc.py`, everything else skipped):

- `01 WBROOT` — county, well-unique ID, district, original completion date, total depth, newest drilling-permit number, plug flag
- `02 WBCOMPL` — oil/gas code, lease number, well number, active/inactive
- `13 WBNEWLOC` — WGS84 latitude and longitude, stored as `PIC S9(3)V9(7) DISPLAY`

**Known assumptions and traps:**

| Issue | Handling |
|---|---|
| **Longitude sign.** dbf900 stores longitude as a positive zoned-decimal magnitude — the sign overpunch is always positive. | The parser **forces longitude negative** for the Texas hemisphere. If you ever see Permian wells plotted in China, this is why. |
| Monthly EOM snapshots are **not in folder-tail order** | Pull by *parsed date*, never by position in the listing |
| `daf420` record layout is unpublished | Empirically derived; a silent RRC format change would produce garbage rather than an error. Spot-check row counts against the previous run. |
| ~9,295 in-scope wellbores have no lat/lon | Dropped from the layer, not plotted at a centroid. The layer therefore under-counts total wellbores. |

**Cadence:** wellbore weekly, permits monthly (EOM). Refresh commands in
[`04-OPERATIONS-RUNBOOK.md §3`](04-OPERATIONS-RUNBOOK.md#3-refreshing-data).

### 3.2 EIA-860 (Energy Information Administration)

Feeds `eia860_plants` (1,367), `eia860_battery` (133), `solar` (180).

- **Source:** `https://www.eia.gov/electricity/data/eia860/` — annual ZIP, released Feb–Mar.
  Currently on the **2024 data year**.
- **Script:** `scripts/refresh_eia860.py [--year 2024]`
- **Critical schema fact** (`ARCHITECTURE.md §4`): capacity, technology and fuel live in
  the **Generator** sheet (`3_1_Generator_Y<year>.xlsx`), *not* the Plant sheet. The
  script groups generators by `Plant Code`, filters `Status == 'OP'`, sums
  `Nameplate Capacity (MW)`, and takes the mode of `Technology` and `Energy Source 1`
  for plant-level labels.
- **Coverage caveat:** the 2024 release covers **891 of 1,367** `eia860_plants` rows on
  capacity (65.2%, 178,542 MW total). The other 476 are null on `capacity_mw`, so
  data-driven marker sizing falls back to a static radius for them. This is a source
  limitation, not a bug.
- **Fragility:** EIA returns **503 without a `Referer` header**. All fetches send both
  `User-Agent` and `Referer: https://www.eia.gov/electricity/data/eia860/`. EIA-860**M**
  (monthly) returns HTML rather than data — use the annual ZIP only.
- Numeric cells contain whitespace, `"NA"` and blanks; everything routes through `fnum()`.

### 3.3 USWTDB — U.S. Wind Turbine Database

Feeds `wind` (19,464 turbines).

- **Source:** `https://eersc.usgs.gov/api/uswtdb/v1/turbines` (PostgREST, no auth),
  filtered `t_state=eq.TX`.
- **Script:** `scripts/refresh_uswtdb.py`
- Endpoint caps responses at 1,000 rows; the script paginates by `case_id`.
- `capacity_mw` is computed from `t_cap` (kW). USWTDB deprecated `p_owner`, so
  `operator` is blank and is backfilled downstream from project layers where available.
- **Cadence:** quarterly. Joint USGS / LBNL / ACP product.

### 3.4 ERCOT

Feeds `ercot_queue` (1,778), `tpit_subs` (141), `tpit_lines` (133), `oxy_ercot`.

- **Queue source:** ERCOT monthly GIS Report (`ercot.com/.../monthly-gis-reports/`),
  published mid-month.
- **TPIT source:** ERCOT Transmission Project Information Tracking XLSX, monthly. The
  scraper for TPIT is **not in the repo** — this is a known gap.
- **Geocoding is the hard part.** ERCOT publishes county, not coordinates. Queue rows
  start at county centroid and are upgraded by `scripts/geocode_ercot_queue.py`, a
  three-stage cascade that stamps every row with a `coords_source` provenance label:

  | Stage | Method | `coords_source` |
  |---|---|---|
  | 1 | EIA-860 operating-plant + battery name+county fuzzy match | `eia860` |
  | 1 | USWTDB wind-farm name+county fuzzy match (wind rows only) | `uswtdb` |
  | 2 | TPIT planned-upgrade substation POI match, same county, WRatio ≥ 88. TPIT has no county column, so counties are derived per row by TIGER 2024 point-in-polygon. | `tpit_poi` |
  | 2 | Same matching kernel against the 1,637-row OSM `substations` layer | `substation_poi` |
  | 3 | Operator-curated override CSV, last precedence | `manual_override` |
  | — | Nothing matched | `county_centroid` |

- **Current state:** 479 of 1,778 rows (26.9%) are off county centroid, against a
  **≥60% target**. Stage 3 is **blocked** waiting on
  `data/ercot_queue_overrides.csv`, which does not exist. See
  [`08-ROADMAP-AND-GAPS.md §3`](08-ROADMAP-AND-GAPS.md#3-open-sprints).
- Name normalisation strips `LLC`, `INC`, `LP`, `LTD`, `CORP`, `CO` and trailing
  parenthetical project codes before matching. The pass is idempotent — re-running with
  the same inputs produces no diff.
- **Fragility:** the ERCOT TPIT page 503s intermittently. Policy is one attempt per
  session, then skip.

### 3.5 HIFLD / ArcGIS FeatureServers

Feeds `transmission`, and the four `hifld_*` layers.

| Layer | FeatureServer |
|---|---|
| `hifld_ng_pipelines` | `services2.arcgis.com/FiaPA4ga0iQKduv3/.../Natural_Gas_Interstate_and_Intrastate_Pipelines` |
| `hifld_crude_pipelines` | `services2.arcgis.com/FiaPA4ga0iQKduv3/.../Crude_Oil_Trunk_Pipelines_1/FeatureServer/0` |
| `hifld_hgl_pipelines` | `services2.arcgis.com/FiaPA4ga0iQKduv3/.../Hydrocarbon_Gas_Liquids_Pipelines_1/FeatureServer/0` |
| `hifld_ng_processing` | `services2.arcgis.com/ZOdjAzAQ2B0f85zi/.../NaturalGas_ProcessingPlants_US_EIA/FeatureServer/0` |

- **Script:** `scripts/fetch_hifld.py <slug> <featureserver_url>` — paginates the whole
  layer for a bbox and writes one GeoJSON FeatureCollection. **The 6-county Permian bbox
  is hardcoded** in `HIFLD_BBOX`; change it there if scope changes.
- **Fragility:** AGOL cold fetches return `503 "DNS cache overflow"`. Handled with 5
  retries at 10 s. HIFLD **Substations** is token-gated and returns only a 68-row
  subset — that is why substations come from OSM instead. RRC pipelines via AGOL 403
  intermittently and return 0 rows for `STATUS_CD='A'`; use `STATUS_CD='B'`.
- `transmission` carries **no voltage attribute**, so voltage-based styling and filtering
  are unavailable for it — a source limitation, permanently.

### 3.6 OpenStreetMap — Overpass

Feeds `substations` (1,637).

- Three Overpass endpoints with fallback; if all three 503, the last cached extract is used.
- Chosen over HIFLD because HIFLD's substation layer is token-gated and radically incomplete.
- **Licence:** ODbL. Attribution is rendered in the map footer.
- **Cadence:** quarterly probe. There is currently **no refresh script** for this layer —
  it is refreshed by hand into `combined_points.csv`.

### 3.7 TCEQ — gas turbine air permits

Feeds `tceq_gas_turbines` (6).

- **Source:** `https://www.tceq.texas.gov/downloads/permitting/air/memos/turbine-lst.xlsx`
- **Script:** `scripts/refresh_tceq_gas_turbines.py`
- **Filters applied, in order:** sheet = `Issued Turbine Air Permits` (and `Pending`) →
  23-county West Texas → `Received` year ≥ 2020. The source file is already pre-filtered
  to ≥20 MW electric output. 229 issued rows → 12 in scope → **6** after the date filter.
- **Status taxonomy:** `issued` · `renewed` (Received cell starts "renew", earliest date
  used) · `modified` (starts "upgraded") · `pending`.
- **Geocoding deviation:** the original spec called for the Census geocoder, which
  requires a street address and returned **0/6** matches on city+state queries. The
  script falls back to **OSM Nominatim** with a `{city}, {county} County, Texas, USA`
  structured query at 1.1 s/request per Nominatim ToS — 6/6 matched. Precision is
  **municipality/community centroid**, not parcel.
- **Deliberate exclusions** (pre-2020 grandfathered, reversible if wanted) — full list
  with permit numbers in `outputs/refresh/CHANGELOG.md`: QEP Energy Tarzan 400 MW (2018),
  Navasota Odessa 550 MW (2005), Ector County Energy Center 330 MW (2013), Powersite Wink
  372 MW (2015), Luminant Odessa 1,000 MW (1999), Luminant Monahans 325 MW (1985).
- **Aggregate signal:** 3,536 MW across the 6 in-scope permits; one (Poolside LF Phase 2
  DC Ops, Fort Stockton) is explicitly datacenter-branded.

### 3.8 Tax abatements — LDAD / commissioners-court scrape

Feeds `tax_abatements` (1,495 statewide).

- **Primary source:** county commissioners-court agendas. This is the *leading* signal —
  Tax Code §312.207(d) requires agenda posting **≥30 days before** an abatement vote,
  whereas the Comptroller's registries are JS-gated with a 12–24 month lag.
- **Scripts:** `scripts/scrape_abatements.py` (agenda probe, 23 counties) and
  `scripts/transform_abatements.py` (pinned snapshot → `combined_points.csv` rows).
- **Adapter status:** Pecos (WordPress) and Reeves (CivicEngage) are validated. The other
  21 counties are stubs returning `status='unverified_source'`.
- **Reeves is hard-blocked:** `reevescounty.org` sits behind an Akamai datacenter-egress
  block that 403s all cloud-runner traffic regardless of UA or TLS fingerprint. No
  solution from a cloud runner. Unblock paths: residential-proxy egress (paid), Akamai
  allowlisting via Reeves IT (unlikely), or search-API result pages.
- **The layer is fed only by a pinned snapshot** —
  `data/abatements/abatement_hits_20260424_092810.csv`. The daily probe writes
  timestamped diagnostic CSVs which are **gitignored and must never be committed**;
  `.gitignore` has an explicit negation to protect the pinned file.
- **Comptroller Ch.312 reconciliation (2026-05-13):** the state API at
  `api.comptroller.texas.gov/open-data/v1/tables/ch312-abatement` was probed and returns
  **0 records** in the 6-county Permian scope. All 5 in-scope LDAD records originate from
  Pecos County commissioners court under **Chapter 381** (county economic development
  agreements). No second `tax_abatements_312_state` layer was created because it would be
  empty. The import path is documented and ready if scope ever expands to urban Texas.
- **Schema note — column overload.** The `tax_abatements` layer reuses generic
  `combined_points.csv` columns for domain-specific fields. This mapping is **locked**:

  | Generic column | Actually holds |
  |---|---|
  | `inr` | permit number |
  | `funnel_stage` | permit status |
  | `zone` | received date, ISO |
  | `project` | number of units |
  | `poi` | agenda URL |
  | `operator` | applicant |
  | `commissioned` | meeting date |
  | `technology` | project type |

### 3.9 Datacenter anchors — `dc_anchors.json`

Feeds `dc_anchors`. **The only fully hand-curated layer**, and the only one with its own
formal schema doc (`data/datacenters/README.md` — read it before editing).

- **Inclusion criteria:** Texas-sited, hyperscale or AI-anchored, **≥100 MW announced**
  *or* strategically material in its county; status ∈ {announced, permitted,
  under_construction, operational}. Rumour is excluded, as is sub-100 MW colocation and
  crypto-only mining without an AI/HPC anchor.
- **Coordinate honesty:** every entry carries `coord_accuracy` ∈ `precise` (≤500 m,
  parcel-level) / `approximate` (≤10 km) / `county_centroid`. The renderer treats
  centroids differently — lower opacity, "approximate" badge in the popup — so a centroid
  pin is never mistaken for a parcel.
- **Source quality ladder** (high → low): official permits (TCEQ, county records, NRC) →
  SEC filings and developer press releases → ERCOT INR filings and county economic
  development records → tier-1 trade press → aggregators → wiki-style sources.
- **Every entry needs ≥1 source; ≥2 per non-trivial field is the target.** Single-sourced
  entries are flagged `single_source: true`.
- **Capacity convention:** when announced campus capacity materially exceeds
  permitted/contracted capacity (e.g. 11 GW announced vs 6 GW permitted + 1 GW of turbines
  acquired), `capacity_mw_announced` records the **full announced buildout** and
  `power_source` spells out the phasing reality in prose.
- **Refresh:** `scripts/refresh_dc_anchors.py` — a Claude-in-the-loop diff proposer run
  weekly by GitHub Actions. It fetches each entry's cited source URLs, asks the Anthropic
  API to propose factual updates, and writes a proposal file. **Diffs are never
  auto-applied**; a PR is opened for human review. It never proposes coordinate edits.

### 3.10 Census TIGER, BTS, StratMap

| Layer | Source | Note |
|---|---|---|
| `counties`, `county_labels` | Census TIGER 2023/2024 — `www2.census.gov/geo/tiger/TIGER2024/COUNTY/tl_2024_us_county.zip` | Also used for the point-in-polygon county derivation in the ERCOT geocoder |
| `tiger_highways` | Census TIGER primary roads | **Prebuilt only.** `data/tiger/primary_roads_wtx.geojson` exists but is not what the layer builds from. |
| `bts_rail` | Bureau of Transportation Statistics main lines | **Prebuilt only** |
| `parcels_pecos` | StratMap / TxGIO, 14,720 Pecos County surface parcels | Prebuilt, sidebar-hidden. **Not in `layers.yaml` any more** — see [`08-ROADMAP-AND-GAPS.md §1`](08-ROADMAP-AND-GAPS.md#1-documentation-drift-found-2026-08-18). TxGIO AGOL is token-gated (499); use the DataHub county-zip route. **Surface, not mineral.** |

Census Geocoder returns **0 matches** on West-Texas municipalities — every geocoding
path in this project falls back to OSM Nominatim at a 1.1 s throttle.

### 3.11 TWDB — groundwater

`aquifers` (5) and a 14,700-point groundwater `wells` layer appear in
`ARCHITECTURE.md §5` but are **not present in the current `layers.yaml`**. Treat them as
retired unless someone confirms otherwise. Source was TWDB ArcGIS via
`arcgis.com/sharing/rest/search` (the direct dataset URL shifts, so search by title).

### 3.12 FCC Broadband Data Collection

`fcc_fiber_coverage` — H3 resolution-8 hexes, 23-county West Texas, `TotalBSLs > 0`,
bbox `-105.998,28.972,-100.115,32.525`, spatially clipped to the county union.
Properties renamed to `bsl_count`, `fiber_served_bsls`, `fiber_underserved_bsls`,
`fiber_unserved_bsls`, `fiber_provider_count`, `as_of_date="2025-06-30"`.
Script: `scripts/refresh_fcc_fiber_coverage.py`. Cadence: biannual (June / December).
**Also not currently in `layers.yaml`** despite the refresh script and a 4 MB staged
GeoJSON existing.

### 3.13 Basemaps (third-party, no token)

| Key | Provider | URL pattern |
|---|---|---|
| `carto_light` | CARTO Voyager | `{a,b,c}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png` |
| `esri_streets` | Esri World Street Map | `server.arcgisonline.com/.../World_Street_Map/MapServer/tile/{z}/{y}/{x}` |
| `esri_imagery` ⭐ default | Esri World Imagery | `server.arcgisonline.com/.../World_Imagery/MapServer/tile/{z}/{y}/{x}` |
| `openfreemap` | OpenFreeMap Liberty | `tiles.openfreemap.org/styles/liberty` |
| `naip` | USDA NAIP via USGS | `imagery.nationalmap.gov/.../USGSNAIPPlus/ImageServer/tile/{z}/{y}/{x}` |

All are free, unauthenticated tile services used within their published terms.
Attribution is rendered on the map. They are the project's only runtime third-party
dependency — if one goes away, that basemap option breaks while everything else keeps
working.

---

## 4. Hand-placed and APPROXIMATE geometry

Hard rule 3 forbids hand-coded coordinates. These are the documented exceptions, all
labelled as such in the UI:

| Layer | What is approximate | Replace when |
|---|---|---|
| `mpgcd_zone1` | Groundwater District Management Zone 1 boundary, digitised from an MPGCD PDF | TWDB or MPGCD publishes a vector boundary |
| `la_escalera` | ~223,000-acre ranch outline | A parcel-derived boundary becomes available |
| `longfellow_ranch` | Ranch outline (Pecos/Terrell/Brewster) | Same |
| `gw_ranch` | Pacifico 7.65 GW campus footprint | TCEQ permit exhibit or parcel data |
| `waha_circle`, `cities`, `labels_hubs` | Toponym markers | Never — they are labels, not features |

`dc_anchors` entries at `coord_accuracy: county_centroid` are the systematic version of
the same honesty: approximate, and rendered so you can tell.

---

## 5. Fragility table

Consolidated from `ARCHITECTURE.md §9`, verified against the scripts.

| Source | Failure mode | Countermeasure |
|---|---|---|
| RRC MFT GoAnywhere | Every download needs GET landing → harvest JSESSIONID + ViewState → POST with row id | `scripts/fetch_rrc.py` implements the full PrimeFaces protocol |
| RRC dbf900 longitude | Sign overpunch always positive | Parser forces longitude negative |
| RRC daf420 | Record layout unpublished; format change fails silently | Empirical parser; spot-check row counts |
| RRC pipelines AGOL | 403 transient; `STATUS_CD='A'` → 0 rows | Use `STATUS_CD='B'` |
| AGOL FeatureServer | 503 "DNS cache overflow" on cold fetch | 5 retries, 10 s sleep |
| HIFLD transmission AGOL | 503 under retry | Same |
| HIFLD substations AGOL | Token-gated, 68-row subset | Use OSM Overpass instead |
| Overpass API | All 3 endpoints can 503 | 3-endpoint fallback, then last cached |
| USPVDB | Chronic 503 | Skip to EIA-860 `3_3_Solar` |
| EIA-860 annual ZIP | 503 without `Referer` | Send `Referer` + `User-Agent` |
| EIA-860M | Returns HTML | Use annual ZIP only |
| EIA-860 numerics | Whitespace, `"NA"`, blanks | Route through `fnum()` |
| TWDB AGOL | Dataset URL shifts | Search via `arcgis.com/sharing/rest/search` |
| TxGIO StratMap AGOL | Token-gated 499 | DataHub county-zip route |
| Census Geocoder | 0 matches on West-TX municipalities | Fall back to OSM Nominatim, 1.1 s throttle |
| Comptroller search DBs | JS-gated, 12–24 mo lag | Commissioners-court agenda scrape |
| **Reeves County site** | **Akamai datacenter-egress block — 403s all cloud runners** | **None. Hard blocker.** |
| ERCOT TPIT page | Intermittent 503 | One attempt per session, skip on fail |
| Caramba GeoJSON | 3-tuple coordinates | `build.py` flattens Z to 2D |
| tippecanoe | Missing after container reset | Pin to felt fork; `bootstrap-claude-code.sh` reinstalls |
| Netlify prod `curl` | Default UA returns 503 | Always `-A "Mozilla/5.0"` |
| Netlify HEAD on root | 503 even when GET is healthy | Use GET and grep for markers |

---

## 6. Permanently scoped-out sources

Excluded by decision. Revisit only on the stated condition (`ARCHITECTURE.md §11`).

| Source | Why excluded | Revisit if |
|---|---|---|
| `tceq_pws` (public water systems) | HTTP 400 on the original endpoint; operator declined the alternative | TCEQ publishes an alternate feed |
| `tceq_pbr` (permits by rule) | CRPUB is HTML-only scrape; authorisation declined | Operator authorises the scrape |
| `tceq_nsr_pending` | Same as `tceq_pbr` | Same |
| Comptroller LDAD bulk XLSX | Does not exist — per-record CSV only, behind a JS-gated UI | Operator authorises Selenium/Playwright |
| Per-county / per-chunk fetching at fetch time | Data-source-shape problem, not a workflow problem | A bulk endpoint is discovered |
| **`oxy_minerals_pecos`** | **Texas mineral ownership is not public GIS geometry.** Free public data yields only a non-spatial owner roll (Pecos CAD certified mineral roll) keyed to abstract/survey legal descriptions — no polygons or coordinates. GLO publishes state-owned mineral geometry only. `parcels_pecos` is **surface**, not mineral. A true mineral map needs paid data plus deed-by-deed title platting, i.e. hand-coded coordinates — barred by hard rule 3. | Never, on current data availability. The deliverable if wanted is a sourced OXY mineral-**account table**, optionally shaded at abstract level — not a tract-precise layer. |
| `bead_fiber_planned` | Neither BEAD source file carries county or coordinates; `locations.xlsx` maps opaque FCC BSL IDs with no coords, and geocoding needs the licensed FCC BSL Fabric. The public award map is a JS SPA with no static endpoint. | Any of: PUC region polygons + project-name region parser · subgrantee HQ geocode via SAM.gov UEI lookup · authorised headless scrape of `register.broadband.texas.gov` |

---

## 7. Attribution

The print footer and popups carry source attribution. Current footer text:

> Map prepared by Land Resource Partners · Sources: ERCOT TPIT, EIA-860, USWTDB, TWDB,
> RRC, HIFLD, TIGER, BTS, OSM, USGS, TCAD

Every feature in `combined_geoms.geojson` additionally carries `source` and `source_date`
properties, surfaced in its popup.

All primary sources are US federal or Texas state public data, or OpenStreetMap (ODbL).
No licensed or paid data feeds are used anywhere in the pipeline — which is exactly why
the mineral-ownership layer is not feasible.
