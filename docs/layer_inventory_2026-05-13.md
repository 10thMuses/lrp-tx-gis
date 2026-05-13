# Layer inventory — 2026-05-13

Generated as Part 1 of the Round-2.5 batch. Currency cutoff (per operator
instruction): any layer whose source data is older than 90 days from today
(2026-02-12) is flagged **stale**.

## Status table

| Layer | Status | Latest data date | Coord quality | Action needed |
|---|---|---|---|---|
| counties | ✅ present | 2024 (TIGER 2024 census release) | precise (TIGER polygons) | none — rare-cadence reference |
| cities | ✅ present | rare (hand toponyms) | precise | none |
| caramba_north | ✅ present | persistent project boundary | precise | none |
| solstice_substation | ✅ present | persistent | precise | none |
| waha_circle | ✅ present | persistent | hand-placed | none |
| labels_hubs | ✅ present | persistent | precise | none |
| la_escalera | ✅ present | persistent (project ranch) | **approximate** (boundary digitized) | flagged for review |
| longfellow_ranch | ✅ present | persistent | **approximate** | flagged for review |
| gw_ranch | ✅ present | persistent | **approximate** | flagged for review |
| mpgcd_zone1 | ✅ present | persistent | **approximate** | flagged for review |
| eia860_plants | ✅ present | 2024 annual release (refreshed 2026-04-28) | precise (EIA lat/lon) | refresh on 2026 release ETA mid-2026 |
| eia860_battery | ✅ present | 2024 release (2026-04-28) | precise | same as above |
| wind | ✅ present | 2026-04-28 USWTDB snapshot | precise | live FeatureServer — refresh on demand |
| solar | ✅ present | 2024 release (2026-04-28) | precise | refresh on 2026 release ETA |
| substations | ✅ present | 2026-04-28 OSM Overpass | precise | OSM is live — refresh on demand |
| tpit_subs | ✅ present | 2026-04 ERCOT TPIT XLSX | precise | refresh monthly |
| transmission | ✅ present | 2026-04 HIFLD AGOL | precise | refresh annually — **≥100 kV cutoff only**, R2.5 spec asks for ≥69 kV |
| tpit_lines | ✅ present | 2026-04 ERCOT TPIT XLSX | precise | refresh monthly |
| ercot_queue | ✅ present | 2026-04-28 ERCOT GIS Report + Stage-2 geocode | **mixed** (precise via EIA/USWTDB join; remainder county-centroid) | **upgrade to R2.5 Part 3 precise geocoding (PUC + abatements join)** |
| county_labels | ✅ present | TIGER 2024 (254 statewide) | precise | none |
| rrc_pipelines | ✅ present | RRC 2019 prebuilt (`STATUS_CD='B'` workaround) | precise | refresh annually — R2.5 spec mentions HIFLD oil/gas pipelines |
| tceq_gas_turbines | ✅ present | 2026-04-25 TCEQ scrape | precise | refresh monthly |
| tiger_highways | ✅ present | TIGER (rare) | precise | none |
| bts_rail | ✅ present | BTS (rare) | precise | none |
| permits_permian6 | ✅ present | 2026-05-13 (RRC EOM Jan 2018–Dec 2025) | precise | 1976-2017 backfill deferred to R2.5 Part 2 |
| wells_permian6 | ✅ present | 2026-05-13 (RRC dbf900 weekly) | precise | refresh weekly via `python3 build.py refresh wells` |
| tax_abatements | ✅ present | 2026-04-29 LDAD scrape (1,486 statewide) | precise (LDAD-disclosed coords) | verify Ch.312 vs Ch.313 split per R2.5 Part 4C |
| dc_anchors | ✅ present | 2026-04-26 (8 anchors) | mixed (precise + county-centroid) | refresh via researched-anchor pipeline |

**26 layers shipping to prod** as of last close-out
(`6a04990a155513aedd0e842d`, 2026-05-13).

## Currency analysis vs the 30-day re-fetch threshold

Most freshly-refreshed dataset: `permits_permian6` / `wells_permian6` (today,
2026-05-13). All others were refreshed between 2026-04-25 and 2026-04-30 —
**13–18 days old**, comfortably inside the 30-day threshold. **No layer is
stale.**

The two "stale-risk" cases on a longer horizon:

1. `rrc_pipelines` — prebuilt was last refreshed 2019. RRC's `STATUS_CD='A'`
   filter returned 0 rows; the working `STATUS_CD='B'` slice was preserved.
   The data itself rarely changes (pipeline routes are decade-stable), so
   the 7-year age is acceptable but should be noted.
2. EIA-860 layers (`eia860_plants` / `eia860_battery` / `solar`) — 2024
   annual release. EIA's 2025 release lands mid-2026; the 2026 release lands
   mid-2027. Currently inside the refresh window.

## R2.5 Part 1 cross-reference check

The operator asked specifically about these layers; status against the
inventory:

| Operator-requested layer | Status | Notes |
|---|---|---|
| ERCOT generator interconnection queue | ✅ present (`ercot_queue`) | Stage-2 geocoded; R2.5 Part 3 upgrades to precise via PUC + abatements |
| EIA-860 power plants | ✅ present (`eia860_plants`) | 2024 release; refresh when 2025 lands |
| USWTDB wind turbines | ✅ present (`wind`) | 2026-04-28 snapshot — fresh |
| HIFLD transmission ≥69 kV | ⚠ partial (`transmission` is ≥100 kV) | R2.5 add: re-fetch with 69 kV cutoff |
| HIFLD substations | ⚠ partial (using OSM via `substations`, not HIFLD) | Token-gated HIFLD layer; OSM was the documented countermeasure per ARCHITECTURE §9 |
| HIFLD oil and gas pipelines | ⚠ partial (`rrc_pipelines` is RRC, not HIFLD) | RRC dataset covers >20" pipelines only; HIFLD covers more |
| HIFLD natural gas processing plants | ❌ missing | R2.5 add |
| HIFLD refineries | ❌ missing | R2.5 add |
| HIFLD natural gas storage | ❌ missing | R2.5 add |
| Comptroller Ch.312 abatements | ⚠ partial (`tax_abatements` is LDAD-sourced — mostly Ch.313 successors) | R2.5 Part 4C verify split |
| Comptroller Ch.313 abatements | ⚠ partial (same source) | R2.5 Part 4C verify split |

## Action plan for R2.5 batch (ordered)

1. **Part 2A** — Wells Spudded report integration (2005-current). Build
   `wells_spudded_permian6` layer.
2. **Part 2B** — Per-permit detail scrape script (1976-2004) **prepared but
   not executed** (overnight job).
3. **Part 4A** — EIA-860 2024 release already loaded; verify 2026 release
   isn't out yet (EIA cadence) — if it is, refresh.
4. **Part 4B** — USWTDB live FeatureServer refresh — refresh if any
   delta vs. 2026-04-28 snapshot.
5. **Part 4C** — Comptroller Ch.312 + Ch.313 abatements direct from
   `api.comptroller.texas.gov/open-data/v1/tables/ch312-abatement` —
   add as new layer alongside `tax_abatements`, document split.
6. **Part 4D** — HIFLD energy infrastructure (transmission ≥69 kV,
   substations, pipelines, NG processing plants, refineries, NG storage).
   Six new sub-layers.
7. **Part 3** — ERCOT queue precise geocoding via FERC EQR + PUC + abatement
   cross-reference.
8. **Part 5** — Counterparty asset boundaries (5 sites) via TCEQ + abatement
   sources.
9. **Part 6** — Sidebar integration for all new layers.
10. **Part 7** — Documentation updates (ARCHITECTURE §5, CLAUDE.md refresh
    triggers, WIP_OPEN summary).

Deferred (per operator instruction): County Appraisal District data, 1976-2004
per-permit detail scrape execution, abatement inactive/expired layer if it
overruns the 30-min budget.
