# TCEQ refresh changelog

Append-only. One entry per refresh run.

---

## 2026-04-23 — tceq_gas_turbines initial refresh

**Source:** `https://www.tceq.texas.gov/downloads/permitting/air/memos/turbine-lst.xlsx`
**Source version:** `2026.4.3` (from xlsx header)
**Source archive:** `outputs/refresh/turbine-lst_2026-04-23.xlsx`
**Refresh script:** `scripts/refresh_tceq_gas_turbines.py`
**Output:** `outputs/refresh/tceq_gas_turbines_2026-04-23.csv`

**Scope applied:**
- Sheet: `Issued Turbine Air Permits` only (active authorizations)
- Geographic: 23-county West Texas set per `docs/archive/refinement-sequence-2026-04.md` ABATEMENT DISCOVERY §4
- Time: `Received` date year ≥ 2020 (strict; `Received` cells with renewal-text history parsed to earliest date)
- Turbine-size: source dataset is pre-filtered to ≥20 MW electric output

**Record counts:**
| Stage | Rows |
|---|---|
| Issued-sheet total | 229 |
| In 23-county scope | 12 |
| Post-date filter (Received ≥ 2020) | **6** |
| Geocoded (Nominatim city+county centroid) | 6 / 6 |

**Excluded pre-2020 grandfathered rows (operator-reversible if in-scope for strategy):**
- 152884 QEP Energy — Tarzan, Martin (2018, 400 MW GE LM6000)
- 76990 Navasota Odessa Energy Partners — Odessa, Ector (2005, 550 MW GE F7EA)
- 110423 Ector County Energy Ctr — Goldsmith, Ector (2013, 330 MW GE 7FA.03)
- 135738 Powersite LLC — Wink, Winkler (2015, 372 MW R-R Trent 60)
- 41008 Luminant — Odessa, Ector (1999, 1000 MW GE F7FA)
- 9659 Luminant — Monahans, Ward (1985, 325 MW GE 7EA)

**Geocoder deviation from original spec:** Original spec referenced Census geocoder. Census `locations/onelineaddress` requires a street address and returned 0/6 matches on city+state queries. Fell back to OpenStreetMap Nominatim with `{city}, {county} County, Texas, USA` structured query; 6/6 matches, 1.1s/request per Nominatim ToS. Precision: municipality / community centroid. Sufficient for current layer rendering; revisit if parcel-precision is required in a later stage.

**Schema:** matches `combined_points.csv` header. Populated fields: `layer_id`, `lat`, `lon`, `name`, `plant_code` (permit #), `county`, `technology`, `fuel`, `mw`, `entity`, `commissioned` (Issue Date), `capacity_mw`, `operator`, `manu`, `model`, `year`. Remaining fields intentionally blank.

**Not refreshed this run:**
- `tceq_pws` — dropped permanently (operator, 2026-04-23)
- `tceq_pbr` — scoped out permanently as CRPUB HTML-scrape analog to RRC-MFT precedent; see `ARCHITECTURE.md §11`
- `tceq_nsr_pending` — deferred to next chat for EPA FRS / data.texas.gov recon pass

**Aggregate signal (23-county 2020+ gas-turbine permit wave):** 3,536 MW across 6 permits, of which one (Poolside LF Phase 2 DC Ops, Fort Stockton) is explicitly data-center branded. CPV Basic Ranch 1,320 MW combined-cycle+cogen at Barstow and Featherwood Capital 931 MW at Pecos/Reeves are the two largest; both non-utility developers.

---

## 2026-10-21 — multi-source refresh (wells, permits, OXY permits, EIA-860, TCEQ, USWTDB, LDAD, FCC BDC)

| Layer | Old | New | as_of | Merge |
|---|---|---|---|---|
| wells_permian6 (RRC dbf900) | 99,808 parsed / 35,198 mapped (2026-08-19 run) | 100,220 parsed / 35,355 mapped | 2026-10-21 (spud max 2026-09-24) | standalone `data/wells_permian6.csv` (gitignored), no merge |
| permits_permian6 (RRC daf420 EOM, 110 snapshots) | 28,842 | 33,179 | snapshots through 2026-09-30; rows with coords through 2026-03-31 | standalone CSV, no merge |
| oxy_drilling_permits | 294 (2020-2026, partial snapshot set) | 2,548 (2015-2026, all 110 snapshots) | 2026-09-30 | standalone geojson |
| eia860_plants | 1,367 | 1,532 | EIA-860 2025 data (`eia8602025.zip`) | merged |
| eia860_battery | 133 | 203 | EIA-860 2025 data | merged |
| wind (USWTDB V9.1, file release) | 19,464 | 19,943 | 2026-09-28 | merged |
| tceq_gas_turbines | 13 | 18 | turbine-lst v2026.10.7 | merged |
| tax_abatements (LDAD) | 1,495 | 1,425 (1,416 LDAD + 9 seed) | LDAD API lastUpdated 2026-10-10 | transform_ldad.py |
| fcc_fiber_coverage | 9,160 hexes (Jun 2025) | 8,211 hexes (Dec 2025) | 2025-12-31 | archive only (no layer in layers.yaml) |

Script changes: `parse_rrc.py` (permits) now reads `0109`/`0209` master/detail records and 27/28-byte location records (2024+ format; previously dropped), and `approved_date` offset corrected 120 -> 119 (previously garbage); `refresh_uswtdb.py` gains `--from-file` / `--from-url` (eersc.usgs.gov TLS cert expired; file release at energy.usgs.gov has valid cert); `refresh_tceq_gas_turbines.py` accepts an xlsx path arg; `refresh_fcc_fiber_coverage.py` AS_OF_DATE -> 2025-12-31; `build_oxy_drilling_permits.py` FIPS fallback += 6 counties.
