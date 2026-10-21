# Part 2 — Layer Catalog

Exhaustive per-layer reference for the 39 layers served by `layers.yaml` on https://lrp-tx-gis.netlify.app (MapLibre GL + PMTiles + tippecanoe, hosted on Netlify). Written for the Caramba North thesis (data-center site in Pecos County near Fort Stockton; 765 kV AEP Solstice; Waha gas; water; drilling vibration).

**Snapshot and evidence base.** Generated 2026-10-21 10:12 UTC from repo `/home/user/lrp-tx-gis` at committed HEAD `0c6564d` and from the live site's registry (`const LAYERS` parsed out of the served `index.html`: build id `20261021T100321Z-ec543126`, deploy `6ad88eb494745d960cbb78bd`, 2026-10-21). Source data files were never opened for content: only CSV headers and Python aggregates (row counts per `layer_id`, distinct-value counts for low-cardinality fields, numeric min/max, key lists, geometry types, bboxes) were computed. No feature rows, names or coordinates were printed; single-point layers are described without coordinates.

**Live = HEAD, unlike the prior deploy.** The site was redeployed on 2026-10-21 (`6ad88eb4`, WIP_OPEN.md) from commits `736a18d` (UI fixes) and `3cf3581` (multi-source data refresh), so live now matches HEAD for tiles, registry and page code (verified: 39 layers in the registry; `/data/wells_permian6.json` 35,355 rows and `/data/permits_permian6.json` 33,179 rows return 200; tile responses carry the CORS and 1-hour cache headers). The *prior deploy* (tiles of 2026-06-23 `6a3add…`, page of 2026-10-20 `6ad77b77…`) is the state described by `docs/OPERATING_MANUAL.md` (written 2026-10-20) and by the audit screenshots; where a card or note contrasts "prior deploy" with "live", that is the difference. Several defects in the manual's Known Defects list (#1 missing side-cars, #2 NAIP, #3 Carto watermark, #4 popup provenance, #11 missing `_headers`) are resolved by the 2026-10-21 deploy; the rest (e.g. #5 USWTDB API certificate, #6 fetchers, now partly closed) are noted inline.

**Count policy.** Feature counts are the live registry counts; "(prior N)" shows the count in the prior deploy where it changed. `wells_permian6`, `permits_permian6`, `rrc_pipelines`, `tiger_highways`, `bts_rail` can only be taken from the registry/tilestats because their sources are gitignored/absent here (`data/wells_permian6.csv`, `data/permits_permian6.csv`, `*.pmtiles`). Everything else was counted locally from HEAD files.

Known doc/repo inconsistencies are called out inline rather than silently resolved. Anything not found in the repo is marked "Not documented in repo". Line citations are `file:line` of `build.py` / `build_template.html` at HEAD `0c6564d`; they drift when those files change.

### The 2026-10-21 data refresh (commit `3cf3581`, live)

Working tree at snapshot: clean apart from this file (`docs/primer/_layers.md`).

Embedded verbatim from `outputs/refresh/CHANGELOG.md` (note: its oxy_drilling_permits row says 2,548; the committed file/commit message say 1,336):

> ## 2026-10-21 — multi-source refresh (wells, permits, OXY permits, EIA-860, TCEQ, USWTDB, LDAD, FCC BDC)
> 
> | Layer | Old | New | as_of | Merge |
> |---|---|---|---|---|
> | wells_permian6 (RRC dbf900) | 99,808 parsed / 35,198 mapped (2026-08-19 run) | 100,220 parsed / 35,355 mapped | 2026-10-21 (spud max 2026-09-24) | standalone `data/wells_permian6.csv` (gitignored), no merge |
> | permits_permian6 (RRC daf420 EOM, 110 snapshots) | 28,842 | 33,179 | snapshots through 2026-09-30; rows with coords through 2026-03-31 | standalone CSV, no merge |
> | oxy_drilling_permits | 294 (2020-2026, partial snapshot set) | 2,548 (2015-2026, all 110 snapshots) | 2026-09-30 | standalone geojson |
> | eia860_plants | 1,367 | 1,532 | EIA-860 2025 data (`eia8602025.zip`) | merged |
> | eia860_battery | 133 | 203 | EIA-860 2025 data | merged |
> | wind (USWTDB V9.1, file release) | 19,464 | 19,943 | 2026-09-28 | merged |
> | tceq_gas_turbines | 13 | 18 | turbine-lst v2026.10.7 | merged |
> | tax_abatements (LDAD) | 1,495 | 1,425 (1,416 LDAD + 9 seed) | LDAD API lastUpdated 2026-10-10 | transform_ldad.py |
> | fcc_fiber_coverage | 9,160 hexes (Jun 2025) | 8,211 hexes (Dec 2025) | 2025-12-31 | archive only (no layer in layers.yaml) |
> 
> Script changes: `parse_rrc.py` (permits) now reads `0109`/`0209` master/detail records and 27/28-byte location records (2024+ format; previously dropped), and `approved_date` offset corrected 120 -> 119 (previously garbage); `refresh_uswtdb.py` gains `--from-file` / `--from-url` (eersc.usgs.gov TLS cert expired; file release at energy.usgs.gov has valid cert); `refresh_tceq_gas_turbines.py` accepts an xlsx path arg; `refresh_fcc_fiber_coverage.py` AS_OF_DATE -> 2025-12-31; `build_oxy_drilling_permits.py` FIPS fallback += 6 counties.

`outputs/refresh/ercot_queue_2026-10-21.meta.json`: `{"rows": 1754, "source_report": "GIS_Report_September2026", "source_publish_date": "2026-10-01", "run_date": "2026-10-21", "fuels": ["GAS", "NUC", "OTH", "SOL", "WIN"], "coords_source_counts": {"eia860": 290, "county_centroid": 1301, "substation_poi": 69, "uswtdb": 9, "tpit_poi": 85}, "carried_forward": 1567, "newly_geocoded": 187}`.

`outputs/refresh/tpit_lines_2026-10-21.meta.json`: `{"features": 133, "source_url": "https://www.ercot.com/files/docs/2022/03/02/ERCOT-July-Ad-Hoc-TPIT-No-Cost-071326-UPDATE.xlsx", "source_last_modified": "Fri, 17 Jul 2026 18:45:59 GMT", "run_date": "2026-10-21", "attribute_changes": {"in_service": 30, "name": 7, "status": 7, "tier": 3, "owner": 5, "from_raw": 6, "to_raw": 5, "sheet": 10}, "geometry": "carried forward from combined_geoms.geojson by pid"}`.

New fetchers at 3cf3581 close two historical gaps (no ERCOT-queue fetch script; no TPIT script): `scripts/refresh_ercot_queue.py` and `scripts/refresh_tpit.py` (the latter refreshes attributes only; see the tpit_lines card).

---

## 0. Global rendering and UI behaviours (apply to every card)

These come from reading `build.py` and `build_template.html`; effects marked *(code-derived)* were not verified in a browser.

- **G1 — Popups are a generic attribute dump.** One handler serves every layer (`featurePopupHtml`, build_template.html:2225; wired in `wirePopups`, :2450). Click/tap only (no hover). It lists every populated property of the tapped tile feature except `layer_id`, `source`, `source_date` (and `completion_year` for wells), labelling keys via the layer's `popup_labels` (else the raw key); title = `name` | `Name` | `NAME` | layer label. The yaml `popup:` list is forwarded into the registry but never read by the template. `caramba_north` popups are disabled (`POPUP_DISABLED`, :2224). `ercotQueuePopupHtml`, `ercotQueueGroupSummaryHtml`, `abatementAnnotationHtml`, `plannedUpgradePopupHtml` (from :2110) are defined but never called, so build-time `abatement_*`, `group_*` and `coords_source` properties show as raw keys.
- **G2 — Registry pass-through gap.** `render_html` (build.py:1142; clean dict from :1168) forwards only: `id, label, group, geom, color, default_on, sidebar_omit, companions, popup, popup_labels, description, source, as_of, min_zoom, radius (default 3), fill_opacity (default 0.25), line_width (default 0.75), text_halo, color_steps, features, filterable_fields`. `circle_radius`, `stroke_color`, `stroke_width` are read by the template (:657) but never forwarded (confirmed absent from the live registry keys), so they fall back to stroke `#ffffff` 1.5 px and the sizing radius. Because `fill_opacity` always arrives (0.25 default) and the template uses `L.fill_opacity ?? 0.9` (:633), *(code-derived)* all point layers except `wells_permian6` and `dc_anchors` draw at circle-opacity 0.25 unless yaml sets one; `solstice_substation` and `waha_circle` (fill_opacity 0) get a transparent fill and a default 3 px / white 1.5 px outline instead of their yaml yellow rings.
- **G3 — Source / as-of footer in popups.** *Live (since 736a18d):* `popupSrcHtml` (:2207) uses the feature's `source`/`source_date` when present, else the layer-level yaml `source` + " · as of " + `as_of`, so all 39 layers show a footer (the sidebar text "Sources attributed in each popup", :321, is now accurate). *Prior deploy:* a footer appeared only for features whose tile properties carry lowercase `source` (+`source_date`): 13 of 39 layers by this audit (6 geoms-file layers `solstice_substation, waha_circle, labels_hubs, la_escalera, longfellow_ranch, gw_ranch` with `source`+`source_date`; 7 OXY layers with `source` only; Known Defect #4 counted ~11). `combined_points.csv` still has no source columns, HIFLD layers carry none (`hifld_ng_processing` has capital-S `Source`, shown as an ordinary row). The yaml `as_of` is one value per layer and for static layers equals the last data deploy date (e.g. 2026-06-23), not an upstream vintage (inference).
- **G4 — Data-driven sizing** (`SIZING_RULES`, build_template.html:512): `ercot_queue, solar, eia860_plants, eia860_battery` by `capacity_mw` (3-15 px, MW stops 0/50/200/500/1000/2000; static radius when <=0/blank); `wind` by `capacity_mw` (mode `mw_small`, 3-15 px at 0-5 MW); `substations`, `tpit_subs` by `voltage` (mode `kv`, stops 0-500; see caveat on `substations`: values are volts); `tpit_lines` width 0.65-1.5 by voltage (kV); `dc_anchors` by `capacity_mw_announced`; `permits_permian6`, `wells_permian6` by `total_depth` (3 px at surface to 8.5 px at 25,000 ft; wells additionally use a zoom ramp 2.5 -> 8 px over z7-14).
- **G5 — Data-driven colours:** `ercot_queue` by `technology` (GT/CC/IC/ST `#f59e0b`; PV `#eab308`; WT `#84cc16`; BA `#dc2626`; else `#64748b`); `dc_anchors` by `status` (announced `#94a3b8`, permitted `#f59e0b`, under_construction `#0ea5e9`, operational `#16a34a`, else `#64748b`) with opacity 0.45 for `county_centroid` accuracy; `wells_permian6`/`permits_permian6` by `oil_gas` (O/oil `#16a34a`, G/gas `#dc2626`, else `#9ca3af`); wells add a three-state treatment (Plugged = black centre + oil/gas-coloured ring; Marginal/EOL = grey 50%; Active = solid).
- **G6 — Min zoom and icons.** `min_zoom` becomes MapLibre `minzoom` (not tippecanoe `-Z`): `wind` 7, `substations` 7, `wells_permian6` 7, `tpit_subs` 6, `permits_permian6` 6, `labels_hubs` 4, `county_labels` 4. `ICON_MAP` (build_template.html:363) adds a symbol layer (`__icon`) from zoom 9 for `solar, wind, eia860_battery, eia860_plants` (and a stale `wells` key). Map min/max zoom 3/18.
- **G7 — Line casing.** Line layers with `line_width > 0.75` and non-white colour get a white casing (width+1, opacity 0.6) beneath (build_template.html:735): applies to `counties` (1.25), `hifld_crude_pipelines` (1), `hifld_hgl_pipelines` (1).
- **G8 — Draw order and sidebar order.** Layers are added in yaml order; `raiseOxy()` (build_template.html:804) re-raises all `oxy_*` layers after every (re)load. The sidebar iterates `GROUP_ORDER` (build_template.html:2467) then yaml order within a group; a layer whose `group` is not in `GROUP_ORDER` never appears in the sidebar. `sidebar_omit` hides `labels_hubs` and `permits_permian6` (37 sidebar rows for 39 layers). 19 layers default on.
- **G9 — Stats panel, scrubber, wells summary.** Only `permits_permian6` and `wells_permian6` have time anchors (`SCRUBBER_TIME_FIELD` :840: `permit_year`, `spud_year`; `STATS_LAYERS` :1172). Scrubber is a year slider (range from the filter stats min/max of those fields; 1 year per second when playing; default "All/cumulative"; the year is carried in the share URL as `yr=` since 736a18d). Both read `dist/data/<layer>.json` side-cars written by `write_stats_attrs` (build.py:960; fields in `STATS_ATTRS_FIELDS`, :947). The prior deploy lacked these side-cars (stats 0, scrubber min=max=2026, 0 resolved `filterable_fields` for wells/permits; Known Defect #1); the 2026-10-21 deploy has them (verified 2026-10-21: 35,355 and 33,179 rows) and the live registry now resolves 9 filter fields each for `wells_permian6` and `permits_permian6` (10 for `ercot_queue`).
- **G10 — Hash state and chrome.** `#lat=&lon=&zoom=&layers=&base=&filters=&sb=&yr=`; default view -102.9707 / 30.9112 z12 (Caramba), default basemap `esri_imagery`, `layers=` written only when the active set differs from the default-on set. The sidebar starts collapsed at <=640 px unless `sb` is given. "Built <date>" in the sidebar footer and the watermark date use the *client's* current date, not the build date. Watermark: prior deploy = red "CONFIDENTIAL — <date>"; live = neutral "LRP · Texas Energy GIS — <date>", bottom-centre, hidden <=900 px except in print.

---

## 1. Summary table — all 39 served layers (sidebar group order = `GROUP_ORDER`)

Sidebar `GROUP_ORDER`: Reference · Land & Deal · OXY — Occidental Footprint · Local Focal Points · Local Hyperscale DC & Power Campuses · Power Generation · Transmission & Grid · Pipelines · Energy Infrastructure · Permits · Oil & Gas Spud Wells · Projects. (`Broadband` appears in ARCHITECTURE.md §7 but is not in `GROUP_ORDER`; no layer uses it.) Within a group, rows follow yaml order. Geometry is the yaml `geom` (drives the MapLibre layer type); `labels_hubs` and `county_labels` are text symbol layers.

| layer_id | sidebar label | group | geometry | feature count | default | min zoom | source dataset (publisher) | as-of | refresh path |
|---|---|---|---|---:|---|---:|---|---|---|
| `counties` | Counties (Outline) | Reference | line/polygon data | 46 | ON | 0 | U.S. Census Bureau, TIGER/Line county boundaries | TIGER 2024 per yaml (docs conflict: ARCHITECTURE.md §5 says 2023) | None in repo (static; rare) |
| `cities` | Cities | Reference | point | 9 | ON | 0 | LRP hand-entered toponyms (no upstream dataset) | Not documented (yaml as_of 2026-06-23 is the deploy date) | None (static) |
| `county_labels` | County Labels | Reference | label | 254 | ON | 4 | U.S. Census Bureau, TIGER/Line county boundaries (representative points) | TIGER 2024 (Chat 111) | scripts/extend_county_labels.py (one-off) |
| `tiger_highways` | Highways (Interstate + US) | Reference | line | 8,010 | ON | 0 | U.S. Census Bureau, TIGER/Line primary roads (Interstate + US) | TIGER vintage Not documented; yaml as_of 2026-06-23 = deploy date | Prebuilt PMTiles (no script in repo) |
| `bts_rail` | Rail (Main Lines) | Reference | line | 16,522 | ON | 0 | U.S. DOT BTS, rail network (main lines) | Not documented; yaml as_of 2026-06-23 = deploy date | Prebuilt PMTiles (no script in repo) |
| `caramba_north` | Caramba North (1,300 ac) | Land & Deal | fill | 1 | ON | 0 | LRP / AgriWebb paddock export (tenant farm-management polygon) | 2023-02-01 (source_date) | None (static) |
| `oxy_power` | OXY power & NET Power | OXY — Occidental Footprint | point | 15 | ON | 0 | EIA-860 generators + OSM/HIFLD substations (LRP-curated OXY footprint) | 2026-06-23 deploy (yaml); source snapshots 2026-04-25/28 | scripts/build_oxy_map_layers.py (manual) |
| `oxy_midstream` | OXY midstream / pipeline / processing | OXY — Occidental Footprint | point | 4 | ON | 0 | HIFLD/EIA-757 processing, EIA-860, OSM, EPA FRS (LRP-curated) | 2026-06-23 deploy; 4 points upgraded to precise coords that deploy | scripts/build_oxy_map_layers.py (manual) |
| `oxy_ercot` | OXY in the ERCOT queue | OXY — Occidental Footprint | point | 3 | ON | 0 | ERCOT interconnection queue (LRP-curated OXY subset) | 2026-04-21 (yaml as_of) | scripts/build_oxy_map_layers.py (manual) |
| `oxy_permits` | OXY air & emission permits (TCEQ) | OXY — Occidental Footprint | point | 4 | ON | 0 | TCEQ air authorizations (NSR / Title V) via LRP-curated OXY footprint | 2026-06-23 deploy; permit dates Jul-Nov 2025 | scripts/build_oxy_map_layers.py (manual) |
| `oxy_water` | OXY water infrastructure | OXY — Occidental Footprint | point | 4 | ON | 0 | OSM, NM OCD facilities DB, public company releases (LRP-curated) | 2026-06-23 deploy; WES release 17 Jun 2026 | scripts/build_oxy_map_layers.py (manual) |
| `oxy_carbon` | OXY carbon infrastructure | OXY — Occidental Footprint | point | 4 | ON | 0 | EIA-860, EPA Class VI permit, RRC strat-test wells, company filings (LRP-curated) | 2026-06-23 deploy | scripts/build_oxy_map_layers.py (manual) |
| `oxy_drilling_permits` | OXY drilling permits (RRC W-1) | OXY — Occidental Footprint | point | 1,336 (prior 294) | off | 0 | Railroad Commission of Texas, Drilling Permit Master + Lat/Lon (daf420 EOM) | Live: snapshots through 2026-09-30 (yaml as_of 2026-09-30); prior deploy: 2026-06-23 (294 permits) | scripts/fetch_rrc.py permits -> scripts/build_oxy_drilling_permits.py |
| `solstice_substation` | AEP Solstice Substation | Local Focal Points | point | 1 | ON | 0 | OpenStreetMap way 500535889 (AEP Texas Solstice substation) | 2026-04-27 (source_date) | None (one-off edit_local_devs.py) |
| `waha_circle` | WAHA Natural Gas Hub | Local Focal Points | point | 1 | ON | 0 | Natural gas hub (Waha), LRP hand-placed | 2026-04-21 (source_date) | None (one-off edits) |
| `labels_hubs` | WAHA Hub Label | Local Focal Points | label | 1 | ON | 4 | Natural gas hub (Waha), LRP hand-placed | 2026-04-21 | None |
| `mpgcd_zone1` | Groundwater District Management Zone 1 | Local Focal Points | fill | 1 | ON | 0 | Middle Pecos GCD management-zone PDF (hand-digitized; APPROXIMATE) | Not documented (yaml as_of 2026-06-23 = deploy date) | None; "replace when TWDB publishes" |
| `la_escalera` | La Escalera Ranch (Apex Clean Energy) | Local Hyperscale DC & Power Campuses | fill | 1 | ON | 0 | Public reporting (kjas.com 2024-09; Pecos County School Fund lease; ranch literature) | 2026-04-27 (source_date) | None (one-off edit_local_devs.py) |
| `longfellow_ranch` | Longfellow Ranch | Local Hyperscale DC & Power Campuses | fill | 1 | ON | 0 | Poolside Project Horizon announcement (2025-10); Longfellow Ranches public materials | 2026-04-27 (source_date) | None (edit_109b + edit_110c) |
| `gw_ranch` | GW Ranch (Pacifico Energy) | Local Hyperscale DC & Power Campuses | fill | 1 | ON | 0 | Pacifico Energy GW Ranch press materials; TCEQ permit; Texas Tribune / DCD / Big Bend Sentinel | 2026-04-27 (source_date) | None (edit_109b_consolidate.py) |
| `eia860_plants` | Power Plants (EIA-860) | Power Generation | point | 1,532 (prior 1,367) | off | 0 | U.S. EIA, Form EIA-860 annual generator survey (2025 data live; 2024 data in the prior deploy) | Live: 2025 data (yaml: released 2026-09-10; refreshed 2026-10-21). Prior deploy: 2024 data (refreshed 2026-04-25/28) | scripts/refresh_eia860.py [--year] + build.py merge |
| `eia860_battery` | Battery Storage (EIA-860) | Power Generation | point | 203 (prior 133) | off | 0 | U.S. EIA, Form EIA-860 (2025 data live; 2024 data in the prior deploy), energy-storage sheet | Live: 2025 data refreshed 2026-10-21. Prior deploy: 2024 data | scripts/refresh_eia860.py + build.py merge |
| `wind` | Wind Turbines (USWTDB) | Power Generation | point | 19,943 (prior 19,464) | off | 7 | USGS / LBNL / ACP, U.S. Wind Turbine Database (USWTDB) V9.1 (live) | Live: V9.1 file release, as_of 2026-09-28 (refreshed 2026-10-21). Prior deploy: 2026-04-25/28 API pull | scripts/refresh_uswtdb.py [--from-file/--from-url] + build.py merge |
| `solar` | Solar Farms (EIA-860) | Power Generation | point | 180 | off | 0 | U.S. EIA, Form EIA-860 (2024 release), solar generators | 2024 data year; 2026-04-28 (yaml) | Not documented (no solar output in refresh_eia860.py) |
| `substations` | Substations (OSM) | Transmission & Grid | point | 1,637 | off | 7 | OpenStreetMap via Overpass API | 2026-04-28 (layer inventory; refresh plan says 2026-04-23) | None in repo (Overpass pulled in chat sessions) |
| `tpit_subs` | Planned Substation Upgrades (TPIT) | Transmission & Grid | point | 141 | off | 6 | ERCOT Transmission Project and Information Tracking (TPIT) report | 2026-04 (layer inventory) | None in repo (XLSX scrape not in repo) |
| `transmission` | Transmission ≥100 kV | Transmission & Grid | line | 6,244 | off | 0 | HIFLD electric power transmission lines (ArcGIS Online), >=100 kV | 2026-04 (2026-04-25) | None (hand-merged; HIFLD AGOL) |
| `tpit_lines` | Planned Transmission Upgrades (TPIT) | Transmission & Grid | line | 133 | off | 0 | ERCOT Transmission Project and Information Tracking (TPIT) report | Live: attributes from the July 2026 ad-hoc TPIT update (xlsx Last-Modified 2026-07-17; refreshed 2026-10-21). Prior deploy: 2026-04 | scripts/refresh_tpit.py (new at 3cf3581; attributes only) + build.py merge tpit_lines |
| `rrc_pipelines` | Oil & Gas Pipelines (>20", RRC) | Pipelines | line | 35,879 | off | 0 | Railroad Commission of Texas pipeline layer (>20 in; 2019 extract) | 2019 baseline | Prebuilt PMTiles (no script in repo) |
| `hifld_ng_pipelines` | Natural Gas Pipelines (HIFLD/EIA) | Energy Infrastructure | line | 907 | off | 0 | HIFLD / U.S. EIA natural gas interstate + intrastate pipelines (FEMA Region 6 ArcGIS mirror) | 2026-05 (fetched 2026-05-13) | scripts/fetch_hifld.py hifld_ng_pipelines <url> |
| `hifld_crude_pipelines` | Crude Oil Trunk Pipelines (HIFLD/EIA) | Energy Infrastructure | line | 21 | off | 0 | HIFLD / U.S. EIA crude oil trunk pipelines (FEMA Region 6 ArcGIS mirror) | 2026-05 (fetched 2026-05-13) | scripts/fetch_hifld.py hifld_crude_pipelines <url> |
| `hifld_hgl_pipelines` | Hydrocarbon Gas Liquids Pipelines (HIFLD/EIA) | Energy Infrastructure | line | 15 | off | 0 | HIFLD / U.S. EIA hydrocarbon gas liquids pipelines (FEMA Region 6 ArcGIS mirror) | 2026-05 (fetched 2026-05-13) | scripts/fetch_hifld.py hifld_hgl_pipelines <url> |
| `hifld_ng_processing` | Natural Gas Processing Plants (HIFLD/EIA) | Energy Infrastructure | point | 53 | off | 0 | HIFLD / U.S. EIA natural gas processing plants (ArcGIS Online) | 2017 EIA survey period (all 53 rows); fetched 2026-05-13 | scripts/fetch_hifld.py hifld_ng_processing <url> |
| `tceq_gas_turbines` | Gas Turbine Air Permits (TCEQ, recent filings) | Permits | point | 18 (prior 13) | off | 0 | TCEQ Issued/Pending Turbine Air Permits list (turbine-lst.xlsx) | Live: v2026.10.7 (yaml as_of 2026-10-12; refreshed 2026-10-21). Prior deploy: v2026.4.3 file of 2026-04-25 (13 rows) | scripts/refresh_tceq_gas_turbines.py [xlsx path] + build.py merge |
| `permits_permian6` | Permits (RRC W-1, 6-county Permian) | Permits | point | 33,179 (prior 28,842) | off | 6 | Railroad Commission of Texas, Drilling Permit Master + Lat/Lon (daf420 EOM) | Live: 33,179 rows from 110 EOM snapshots through 2026-09-30 (coords through 2026-03-31). Prior deploy: 28,842 (2026-05-13) | scripts/fetch_rrc.py permits -> scripts/parse_rrc.py permits |
| `tax_abatements` | Approved Tax Abatements (Local / Ch.381 + Ch.312) | Permits | point | 9 served (CSV 1,425; prior 1,495) | off | 0 | Texas Comptroller LDAD (Ch. 312 open-data) + county commissioners-court agendas | Live: LDAD API lastUpdated 2026-10-10 (refreshed 2026-10-21); court seed 2026-04-24. Prior deploy: LDAD 2026-04-29 | scripts/scrape_ldad.py -> transform_ldad.py; scrape_abatements.py -> transform_abatements.py |
| `wells_permian6` | Wells — new drilling (1964-present) | Oil & Gas Spud Wells | point | 35,355 (prior 35,081) | off | 7 | Railroad Commission of Texas, Full Wellbore ASCII (dbf900) | Live: re-fetched 2026-10-21 (100,220 parsed / 35,355 mapped; spud max 2026-09-24). Prior deploy: 35,081 mapped (2026-05-13 build) | build.py refresh wells (fetch_rrc.py + parse_rrc.py) |
| `ercot_queue` | ERCOT Interconnect Queue (GIS Report, Sep 2026) | Projects | point | 1,754 (prior 1,778) | off | 0 | ERCOT Generation Interconnection Status (GIS) report; LRP geocoding | Live: Sep 2026 report (published 2026-10-01), fetched 2026-10-21. Prior deploy: March-2026 report (label said 2026-04-21) | scripts/refresh_ercot_queue.py (new at 3cf3581) -> build.py merge ercot_queue; geocode_ercot_queue.py |
| `dc_anchors` | Datacenter Anchors (≥100 MW) | Projects | point | 8 | off | 0 | LRP-curated datacenter anchor index (public announcements/filings) | generated 2026-04-25; newest source accessed 2026-08-23 | scripts/refresh_dc_anchors.py (weekly CI proposes diffs; manual merge) |

Notes: "prior N" = count in the prior deploy (tiles of 2026-06-23) where it changed with the 2026-10-21 refresh. `tax_abatements` serves only the court-seed rows (9 of 1,425 CSV rows pass the build filter). Feature counts for `rrc_pipelines`, `tiger_highways`, `bts_rail` come from PMTiles `tilestats` (build.py:46). `as-of` for static hand-placed layers is the feature `source_date` where present; the yaml `as_of` of 2026-06-23 on `cities`, `mpgcd_zone1`, `tiger_highways`, `bts_rail`, `oxy_*` equals the last data deploy date rather than an upstream vintage (inference).

---

## 2. Layer cards

Field legend: *Upstream source* = publisher + dataset + URL as recorded in code/docs. *Attributes* are the property keys in the tiles (`layer_id` is stripped at build). Tippecanoe base command is `tippecanoe -fo <id>.pmtiles -l <id> <flags> <id>.ndjson` (build.py:764); default flags `-zg` when the yaml `tippecanoe:` list is absent. `-zg` on single-feature *point* inputs silently yields 0 features (ARCHITECTURE.md §6), hence `-Z0 -z14` on small layers.

## 2.1 Reference

### counties

- **Label:** Counties (Outline)
- **Group / geometry / default / min zoom:** Reference / `line` / ON / 0
- **Feature count:** 46 features (Polygon x46) = live 46
- **Purpose / thesis relevance:** Orientation outline for the 46 West Texas counties around Caramba North. Draws the Pecos (subject) vs Reeves/Ward and Midland/Martin/Reagan (peer) county frame used by the wells/permits sale-area-vs-peer analysis.
- **Storage:** `combined_geoms.geojson` (properties.layer_id = `counties`), split at build (build.py:417)
- **Upstream source:** U.S. Census Bureau TIGER/Line county polygons (publisher). ARCHITECTURE.md:104-108 lists "Census TIGER 2023"; docs/layer_inventory_2026-05-13.md says "TIGER 2024 census release"; the yaml `as_of` says 2024. Exact download URL for this 46-county subset: Not documented in repo (the 254-county label extractor uses `https://www2.census.gov/geo/tiger/TIGER2024/COUNTY/tl_2024_us_county.zip`, scripts/extend_county_labels.py).
- **Acquisition / scripts:** No fetch/refresh script for the 46-county outline. Present in `combined_geoms.geojson` since early chats; edited only by hand/one-off scripts. Original build chat: Not documented in repo.
- **Attributes carried:** GeoJSON properties (HEAD): `GEOID`, `NAME`
- **Build-time filters / transforms:** `split_combined_geojson` (build.py:417): Z flattened to 2D, `layer_id` stripped from tile properties. No other filter.
- **Tippecanoe flags:** `-zg` `--extend-zooms-if-still-dropping` `--simplification=8`
- **Styling (layers.yaml):** colour `#64748b`, line_width `1.25`
- **UI filters (filterable_fields):** none declared
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `NAME`->County, `GEOID`->FIPS; footer in the prior deploy: no (props lack `source`); footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "U.S. Census Bureau, TIGER/Line county boundaries"; `as_of` 2024
- **As-of date + evidence:** TIGER vintage 2023 vs 2024: conflicting repo evidence (see source).
- **Refresh cadence (upstream vs actual):** Upstream: annual TIGER release. Actual: never refreshed (static reference; layer_inventory "rare-cadence reference").
- **Known caveats:** yaml `geom: line` but the 46 features are Polygon; MapLibre draws them as outlines only (no fill). Because line_width 1.25 > 0.75 and colour is not white, a white casing line (width 2.25, opacity 0.6) is added (build_template.html:735). Colour changed `#fbbf24` -> `#64748b` on 2026-05-18 (WIP_OPEN.md). Properties are only `GEOID`, `NAME`; no source/as-of in popup footer.

### cities

- **Label:** Cities
- **Group / geometry / default / min zoom:** Reference / `point` / ON / 0
- **Feature count:** 9 rows (live registry 9)
- **Purpose / thesis relevance:** Nine reference city dots (names only) so a viewer can place Caramba North relative to nearby towns without a labelled basemap (which towns: not enumerated here per the data-file rule).
- **Storage:** `combined_points.csv` (layer_id = `cities`), split to NDJSON at build (build.py:314)
- **Upstream source:** ARCHITECTURE.md:109 labels the source "Hand toponyms"; the 9 city names/coordinates are not enumerated here per the data-file rule. Underlying coordinate source for each toponym: Not documented in repo (ARCHITECTURE.md §3 / hard rule 3 would normally require a public dataset).
- **Acquisition / scripts:** Hand-entered rows in `combined_points.csv`, layer_id `cities`. No script.
- **Attributes carried:** combined_points.csv columns populated at HEAD (non-blank rows of 9): `name` (9)
- **Build-time filters / transforms:** `split_combined_csv` only (lat/lon range check, blank props dropped, `NUMERIC_KEYS` coercion).
- **Tippecanoe flags:** `-zg`
- **Styling (layers.yaml):** colour `#1e293b`, radius `4`
- **UI filters (filterable_fields):** none declared
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->City; footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "LRP hand-entered city toponyms"; `as_of` 2026-06-23
- **As-of date + evidence:** Not documented in repo (yaml `as_of: 2026-06-23` equals the last deploy date, not a vintage).
- **Refresh cadence (upstream vs actual):** Rare / never.
- **Known caveats:** Name-only popup. There is no text label layer for cities: they render as `#1e293b` circles (radius 4); city names appear only in the popup. Bbox of the 9 points spans ~30.3-32.0 N, ~-104.0 to -101.9 W.

### county_labels

- **Label:** County Labels
- **Group / geometry / default / min zoom:** Reference / `label` / ON / 4
- **Feature count:** 254 features (Point x254) = live 254
- **Purpose / thesis relevance:** Names all 254 Texas counties so the Pecos / Reeves / Ward / Midland / Martin / Reagan frame is readable at regional zoom.
- **Storage:** `combined_geoms.geojson` (properties.layer_id = `county_labels`), split at build (build.py:417)
- **Upstream source:** U.S. Census Bureau TIGER 2024 county polygons, filtered `STATEFP == 48`; label position = shapely `representative_point()` (scripts/extend_county_labels.py docstring). URL: `https://www2.census.gov/geo/tiger/TIGER2024/COUNTY/tl_2024_us_county.zip` (auto-fetched, gitignored as `outputs/refresh/tl_*.zip`).
- **Acquisition / scripts:** scripts/extend_county_labels.py (Chat 111): replaces the layer's features in `combined_geoms.geojson` atomically (temp + os.replace). Extended the layer from 46 to 254 features.
- **Attributes carried:** GeoJSON properties (HEAD): `name`
- **Build-time filters / transforms:** `split_combined_geojson`; no filter. Symbol layer reads `name`.
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#ffffff`
- **UI filters (filterable_fields):** none declared
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: (no popup_labels; raw keys shown); footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "U.S. Census Bureau, TIGER/Line county boundaries (label points)"; `as_of` 2024
- **As-of date + evidence:** TIGER 2024.
- **Refresh cadence (upstream vs actual):** Upstream: annual. Actual: one-off (Chat 111).
- **Known caveats:** Rendered by `addLayer` as a symbol layer: font `Noto Sans Bold` 13 px, white text with auto dark halo (light colour -> halo `#0f172a`, width 2), `text-allow-overlap: true`, `text-ignore-placement: true` (build_template.html:724) so labels can collide. Glyphs come from `https://tiles.openfreemap.org/fonts/...` (rasterStyle). WIP_OPEN.md "county_labels render review": operator-named counties may still appear unlabeled at zoom 7-9; unverified. Popup shows `name` only (it is a point at the representative point, not the county polygon).

### tiger_highways

- **Label:** Highways (Interstate + US)
- **Group / geometry / default / min zoom:** Reference / `line` / ON / 0
- **Feature count:** 8,010 live (registry/tilestats only; source not present in this checkout)
- **Purpose / thesis relevance:** Road access context: shows Interstate/US highways relevant to site access, construction logistics and haul routes to Caramba North.
- **Storage:** prebuilt PMTiles `tiles/tiger_highways.pmtiles` (not in git; resolved `$LRP_PROJECT_DIR/tiger_highways.pmtiles` -> `$LRP_UPLOADS_DIR/tiger_highways.pmtiles` -> https://lrp-tx-gis.netlify.app/tiles/tiger_highways.pmtiles; build.py:793)
- **Upstream source:** U.S. Census Bureau TIGER/Line primary roads, filtered `RTTYP` in {I, U} (docs/archive/wip_log_pre_chat83.md:564, Chat 43). Specific TIGER year: Not documented in repo.
- **Acquisition / scripts:** Prebuilt PMTiles produced outside this repo (chat-era refresh batch, Chat 43; "tiger_highways RTTYP=I+U + DP 0.012"). No script in `scripts/`. `build.py:793` resolves `tiger_highways.pmtiles` from `$LRP_PROJECT_DIR`, then `$LRP_UPLOADS_DIR`, then range-fetches the live `https://lrp-tx-gis.netlify.app/tiles/tiger_highways.pmtiles`.
- **Attributes carried:** From yaml popup/popup_labels: `name`, `rttyp` (labelled "Road type"). Actual property keys in the prebuilt tiles: Not verifiable locally (`*.pmtiles` is gitignored and absent).
- **Build-time filters / transforms:** None (prebuilt copy). Feature count read from PMTiles `tilestats` (build.py:46). Live registry: 8,010 features (Chat 43 tier-2 build had 3,926, so the prebuilt was regenerated later by an undocumented process).
- **Tippecanoe flags:** n/a (prebuilt; not run)
- **Styling (layers.yaml):** colour `#fbbf24`, line_width `0.75`
- **UI filters (filterable_fields):** none declared
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: (no popup_labels; raw keys shown); footer in the prior deploy: unknown (tile properties unverifiable); footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "U.S. Census Bureau, TIGER/Line primary roads (Interstate + US)"; `as_of` 2026-06-23
- **As-of date + evidence:** Not documented (TIGER year unknown).
- **Refresh cadence (upstream vs actual):** Upstream: annual TIGER. Actual: static; re-pulled from prod on every build.
- **Known caveats:** Not in git (`*.pmtiles` ignored); only copy is the live site, so a prod loss would lose the layer. `data/tiger/primary_roads_wtx.geojson` (188 LineStrings, `name` only) is NOT this layer's source; it is consumed by OXY map scripts (scripts/oxy_maps.py, scripts/extract_map_geometry.py). Default on; colour `#fbbf24`.

### bts_rail

- **Label:** Rail (Main Lines)
- **Group / geometry / default / min zoom:** Reference / `line` / ON / 0
- **Feature count:** 16,522 live (registry/tilestats only; source not present in this checkout)
- **Purpose / thesis relevance:** Rail access context for heavy-haul equipment (transformers, turbines) and bulk materials to the Fort Stockton / Pecos County corridor.
- **Storage:** prebuilt PMTiles `tiles/bts_rail.pmtiles` (not in git; resolved `$LRP_PROJECT_DIR/bts_rail.pmtiles` -> `$LRP_UPLOADS_DIR/bts_rail.pmtiles` -> https://lrp-tx-gis.netlify.app/tiles/bts_rail.pmtiles; build.py:793)
- **Upstream source:** Bureau of Transportation Statistics (BTS) North American rail network lines, main lines only (`net = M`) per docs/archive/wip_log_pre_chat83.md:564 (Chat 43). Dataset vintage and URL: Not documented in repo.
- **Acquisition / scripts:** Prebuilt PMTiles produced outside the repo (Chat 43 batch); same 3-tier resolution as tiger_highways (build.py:793).
- **Attributes carried:** From yaml: `owner`, `subdivision`, `net` ("Network class"). Real tile keys: not verifiable locally.
- **Build-time filters / transforms:** None (prebuilt). Live registry count 16,522 (Chat 43 build: 5,722).
- **Tippecanoe flags:** n/a (prebuilt; not run)
- **Styling (layers.yaml):** colour `#94a3b8`, line_width `0.75`
- **UI filters (filterable_fields):** none declared
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: (no popup_labels; raw keys shown); footer in the prior deploy: unknown; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "U.S. DOT Bureau of Transportation Statistics, rail network (main lines)"; `as_of` 2026-06-23
- **As-of date + evidence:** Not documented.
- **Refresh cadence (upstream vs actual):** Upstream: BTS NTAD periodic. Actual: static.
- **Known caveats:** Default on, colour `#94a3b8`, width 0.75. Only copy is prod.

## 2.2 Land & Deal

### caramba_north

- **Label:** Caramba North (1,300 ac)
- **Group / geometry / default / min zoom:** Land & Deal / `fill` / ON / 0
- **Feature count:** 1 features (Polygon x1) = live 1
- **Purpose / thesis relevance:** The subject site: Caramba North tract (Pecos County, near Fort Stockton). Everything else on the map is measured against this polygon (distance to Solstice 765 kV hub, Waha gas, water district zone, drilling vibration radius).
- **Storage:** `combined_geoms.geojson` (properties.layer_id = `caramba_north`), split at build (build.py:417)
- **Upstream source:** AgriWebb farm-management export of paddock "Caramba Farms North" (properties `source = LRP/AgriWebb`, `source_date = 2023-02-01`; AgriWebb creation date 2023-02-24 epoch-ms). Publisher: AgriWebb (tenant farm app) via LRP.
- **Acquisition / scripts:** Hand-loaded GeoJSON into `combined_geoms.geojson`; no script. `build.py` flattens its 3-tuple coordinates (ARCHITECTURE.md §9).
- **Attributes carried:** AgriWebb export fields (58 keys): Name, title, type=paddock, landSize, arableLandSize, cropType, pastureState, area_metric_*/area_user_* (hectare / m2), centre_*, label_*, farmId, tenantId, creator, creationDate, lastModifiedDate, latitude/longitude, etc. Only `Name`, `arableLandSize`, `cropType` are in yaml popup_labels.
- **Build-time filters / transforms:** `split_combined_geojson`; `-zg` on a single feature works for this polygon (live count 1).
- **Tippecanoe flags:** `-zg`
- **Styling (layers.yaml):** colour `#2E7D32`, fill_opacity `0.25`
- **UI filters (filterable_fields):** none declared
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `Name`->Tract, `arableLandSize`->Arable acres, `cropType`->Land type; footer in the prior deploy: n/a (popup disabled); footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "LRP / AgriWebb project boundary"; `as_of` 2023-02
- **As-of date + evidence:** Source date 2023-02-01 (AgriWebb record); yaml `as_of: 2023-02`.
- **Refresh cadence (upstream vs actual):** Persistent project boundary; never refreshed.
- **Known caveats:** (1) Label says "(1,300 ac)" (OM CONFIG `acres_max: 1300`, counterparty-supplied) but the polygon carries `area_metric_value = 682.57 hectare` (= 6,825,722 m2 = ~1,687 acres) and `landSize/arableLandSize = 682.57` which are hectares, while the yaml popup_label says "Arable acres". The three figures are inconsistent. (2) Popup is disabled (POPUP_DISABLED, build_template.html:2224). (3) The polygon bbox is ~[-102.987, 30.896, -102.959, 30.925] (about 1.7 mi x 2 mi); the OM memo cites centroid ~30.9032 N, -102.9747 W; map default view is -102.9707 / 30.9112 z12. (4) Sibling polygon `caramba_south` exists in the file but is not served (section 3).

## 2.3 OXY — Occidental Footprint

### oxy_power

- **Label:** OXY power & NET Power
- **Group / geometry / default / min zoom:** OXY — Occidental Footprint / `point` / ON / 0
- **Feature count:** 15 features (Point x15) = live 15
- **Purpose / thesis relevance:** Occidental/NET Power power assets (Goldsmith solar, Wasson CO2-removal captive turbine, NET Power La Porte demo, divested OxyChem cogen) and OXY-named substations: shows OXY as a power-side counterparty/neighbour in the OXY partnership view of Caramba North.
- **Storage:** standalone `data/oxy/oxy_power.geojson` (read directly; build.py:894)
- **Upstream source:** EIA-860 (generation) and OSM/HIFLD (substations) rows from this repo, curated by LRP. Feature `source` property: `EIA-860` (5) / `OSM/HIFLD substations` (10).
- **Acquisition / scripts:** Built by scripts/build_oxy_assets.py -> data/oxy/oxy_assets.geojson (9 curated facility points, intermediate, not served) and scripts/build_oxy_map_layers.py -> six categorised files. Every coordinate is extracted from an already-sourced layer in this repo (combined_points.csv ercot_queue / eia860_plants / substations; data/hifld/hifld_ng_processing.geojson) or a public record cited in each feature's `source`; a few facilities lacking a public point are placed at the TIGER county centroid and flagged `accuracy = "approximate (county centroid)"` (script docstrings).
- **Attributes carried:** GeoJSON properties: `name`, `asset`, `fuel` (5/15), `technology` (5/15), `capacity_mw` (5/15), `county` (5/15), `operator`, `online` (5/15), `status`, `source`, `accuracy`, `voltage` (10/15)
- **Build-time filters / transforms:** Standalone GeoJSON -> NDJSON (`geojson_to_ndgeojson`, build.py:738); no exclude/filter keys.
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#ca8a04`, radius `6`, stroke_color `#ffffff`, stroke_width `1.5`
- **UI filters (filterable_fields):** `asset` (categorical, "Class"); `status` (categorical, "Status"); `fuel` (categorical, "Fuel"); `county` (categorical, "County"); `capacity_mw` (numeric, "Capacity (MW)")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Asset, `asset`->Class, `status`->Status, `fuel`->Fuel, `technology`->Technology, `capacity_mw`->Capacity (MW), `county`->County, `operator`->Operator, `online`->Online, `voltage`->Voltage, `source`->Source; footer in the prior deploy: source only (no source_date); footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "EIA-860 generators and OSM/HIFLD substations; LRP-curated OXY footprint"; `as_of` 2026-06-23
- **As-of date + evidence:** Built for deploy 6a3add… (2026-06-23, WIP_OPEN.md). Underlying EIA/OSM snapshots 2026-04-25/28. Per-feature `online` year where populated.
- **Refresh cadence (upstream vs actual):** On demand; no schedule. Upstream EIA annual / OSM continuous.
- **Known caveats:** 15 points: 5 Generation + 10 Substation; 13 Operating, 2 "Divested to Berkshire (Jan 2026)". Counties populated only on generation rows (HARRIS x3, YOAKUM, ECTOR). All 15 `accuracy = precise`. Most rows are outside the Permian (HARRIS County Oxy Vinyls LP assets, Yoakum, Ector). Drawn above the dense layers via `raiseOxy()` (build_template.html:804).

### oxy_midstream

- **Label:** OXY midstream / pipeline / processing
- **Group / geometry / default / min zoom:** OXY — Occidental Footprint / `point` / ON / 0
- **Feature count:** 4 features (Point x4) = live 4
- **Purpose / thesis relevance:** OXY gas/CO2 processing and midstream: Century (Pecos), Block 31 (Crane), Wasson/Denver Unit CO2-EOR (Yoakum) and the Denver City CO2 hub (Cortez/Bravo/Sheep Mountain trunklines). Context for gas supply/CO2 infrastructure near the Pecos/Crane corridor.
- **Storage:** standalone `data/oxy/oxy_midstream.geojson` (read directly; build.py:894)
- **Upstream source:** HIFLD/EIA-757 Natural Gas Processing Plant Survey, EIA-860 (Wasson CO2-removal), OSM, and EPA FRS Registry (OXY Denver Unit CO2 Recovery Plant; NAD83) per feature `source`.
- **Acquisition / scripts:** See the oxy_power card: built by scripts/build_oxy_assets.py + scripts/build_oxy_map_layers.py from already-sourced repo layers/public records; any county-centroid placements are flagged in `accuracy`.
- **Attributes carried:** GeoJSON properties: `name`, `facility`, `county`, `operator`, `detail`, `status`, `source`, `accuracy`
- **Build-time filters / transforms:** Standalone GeoJSON; no filters.
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#b45309`, radius `7`, stroke_color `#ffffff`, stroke_width `1.5`
- **UI filters (filterable_fields):** `facility` (categorical, "Facility type"); `county` (categorical, "County"); `status` (categorical, "Status")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Asset, `facility`->Facility type, `status`->Status, `operator`->Operator, `detail`->Detail, `county`->County, `accuracy`->Location accuracy, `source`->Source; footer in the prior deploy: source only; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "HIFLD/EIA-757 processing, EIA-860 and OSM; LRP-curated OXY footprint"; `as_of` 2026-06-23
- **As-of date + evidence:** 2026-06-23 deploy (WIP_OPEN.md: "upgraded 4 OXY carbon/midstream points to precise sourced coords").
- **Refresh cadence (upstream vs actual):** On demand.
- **Known caveats:** 4 features: 3 `precise`, 1 `precise (EPA FRS)`. FRS coordinate is NAD83 stored as lon/lat with no datum shift (OPERATING_MANUAL.md §3; ~1-2 m, immaterial). Counties Pecos 1, Crane 1, Yoakum 2 (Yoakum is Wasson/Denver City, outside Pecos).

### oxy_ercot

- **Label:** OXY in the ERCOT queue
- **Group / geometry / default / min zoom:** OXY — Occidental Footprint / `point` / ON / 0
- **Feature count:** 3 features (Point x3) = live 3
- **Purpose / thesis relevance:** OXY / NET Power generation in the ERCOT interconnection queue (Santa Garcias Solar, NET Power Demonstration, TRIFECTA Gas): signals OXY's own power-supply intent and competition for interconnection capacity.
- **Storage:** standalone `data/oxy/oxy_ercot.geojson` (read directly; build.py:894)
- **Upstream source:** Rows streamed from this repo's `ercot_queue` layer (ERCOT GIS report); coordinates inherit that layer's `coords_source` stage (see ercot_queue).
- **Acquisition / scripts:** See the oxy_power card: built by scripts/build_oxy_assets.py + scripts/build_oxy_map_layers.py from already-sourced repo layers/public records; any county-centroid placements are flagged in `accuracy`.
- **Attributes carried:** GeoJSON properties: `name`, `capacity_mw`, `fuel`, `technology`, `county`, `zone`, `filing_entity`, `status`, `source`, `accuracy`
- **Build-time filters / transforms:** Standalone GeoJSON; no filters.
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#7c3aed`, radius `7`, stroke_color `#ffffff`, stroke_width `1.5`
- **UI filters (filterable_fields):** `status` (categorical, "Queue status"); `fuel` (categorical, "Fuel"); `county` (categorical, "County"); `capacity_mw` (numeric, "Capacity (MW)")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Project, `status`->Queue status, `capacity_mw`->Capacity (MW), `fuel`->Fuel, `technology`->Technology, `county`->County, `zone`->Zone, `filing_entity`->Filing entity, `source`->Source; footer in the prior deploy: source only; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "ERCOT interconnection queue; LRP-curated OXY footprint"; `as_of` 2026-04-21
- **As-of date + evidence:** ERCOT queue snapshot (2026-04-21 per ercot_queue label); statuses mention Feb 2026 / Apr 2026 events.
- **Refresh cadence (upstream vs actual):** On demand; depends on ercot_queue refresh (which has no fetch script).
- **Known caveats:** 3 points (Midland, Harris, Kleberg); all `accuracy = precise`. Queue-row coordinates may themselves come from county-centroid fallbacks for other rows; for these 3 they are labelled precise by the build script.

### oxy_permits

- **Label:** OXY air & emission permits (TCEQ)
- **Group / geometry / default / min zoom:** OXY — Occidental Footprint / `point` / ON / 0
- **Feature count:** 4 features (Point x4) = live 4
- **Purpose / thesis relevance:** OXY facilities with TCEQ air authorizations (Century NSR; Block 31 Title V; Wasson Title V O553; Denver Unit Title V O3051) - emission-permit footprint of the neighbouring operator.
- **Storage:** standalone `data/oxy/oxy_permits.geojson` (read directly; build.py:894)
- **Upstream source:** TCEQ authorizations as recorded in feature props; point sources: oxy_assets (Century), HIFLD (Block 31), EIA-860 (Wasson), EPA FRS (Denver Unit, NAD83).
- **Acquisition / scripts:** See the oxy_power card: built by scripts/build_oxy_assets.py + scripts/build_oxy_map_layers.py from already-sourced repo layers/public records; any county-centroid placements are flagged in `accuracy`.
- **Attributes carried:** GeoJSON properties: `name`, `county`, `permit_type`, `status`, `source`, `accuracy`
- **Build-time filters / transforms:** Standalone GeoJSON; no filters.
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#475569`, radius `7`, stroke_color `#ffffff`, stroke_width `1.5`
- **UI filters (filterable_fields):** `permit_type` (categorical, "Permit type"); `status` (categorical, "Status"); `county` (categorical, "County")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Facility, `permit_type`->Permit type, `status`->Status, `county`->County, `accuracy`->Location accuracy, `source`->Source; footer in the prior deploy: source only; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "TCEQ air authorizations (NSR / Title V) via LRP-curated OXY footprint"; `as_of` 2026-06-23
- **As-of date + evidence:** 2026-06-23 deploy; statuses cite renewals 10 Jul 2025 / 15 Oct 2025 / 25 Nov 2025.
- **Refresh cadence (upstream vs actual):** On demand.
- **Known caveats:** 4 points (Pecos, Crane, Yoakum x2); co-location note: Denver Unit placed near Wasson per layer description.

### oxy_water

- **Label:** OXY water infrastructure
- **Group / geometry / default / min zoom:** OXY — Occidental Footprint / `point` / ON / 0
- **Feature count:** 4 features (Point x4) = live 4
- **Purpose / thesis relevance:** OXY / Western Midstream produced-water recycling, desalination pilot and water pipelines - relevant to the Caramba water thesis (produced water as an alternative/competing supply in Reeves/Loving).
- **Storage:** standalone `data/oxy/oxy_water.geojson` (read directly; build.py:894)
- **Upstream source:** OSM way 457948592 + RRC lease 08-40691 (South Curtis Ranch), NM OCD Facilities (Select Water "Lost Tank" recycling), WES release 17 Jun 2026 + USGS Red Bluff Dam gage 08410100, Loving county centroid (Pathfinder pipeline).
- **Acquisition / scripts:** See the oxy_power card: built by scripts/build_oxy_assets.py + scripts/build_oxy_map_layers.py from already-sourced repo layers/public records; any county-centroid placements are flagged in `accuracy`.
- **Attributes carried:** GeoJSON properties: `name`, `water_type`, `county`, `operator`, `detail`, `status`, `source`, `accuracy`
- **Build-time filters / transforms:** Standalone GeoJSON; no filters.
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#0891b2`, radius `7`, stroke_color `#ffffff`, stroke_width `1.5`
- **UI filters (filterable_fields):** `water_type` (categorical, "Water type"); `county` (categorical, "County"); `accuracy` (categorical, "Location accuracy")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Asset, `water_type`->Water type, `status`->Status, `operator`->Operator, `detail`->Detail, `county`->County, `accuracy`->Location accuracy, `source`->Source; footer in the prior deploy: source only; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "OSM, NM OCD facilities and public company releases; LRP-curated OXY footprint"; `as_of` 2026-06-23
- **As-of date + evidence:** 2026-06-23 deploy; newest source cited 17 Jun 2026.
- **Refresh cadence (upstream vs actual):** On demand.
- **Known caveats:** ONLY 1 of 4 points is precise (NM OCD facility, which is in Lea County, NM - outside Texas). The other three are approximate: co-located at an OXY substation (recycling plant within ~1-3 mi), near Red Bluff Reservoir (exact site not published), and Loving county centroid for a linear asset. Do not read these as site-precise. `accuracy` is a filter field.

### oxy_carbon

- **Label:** OXY carbon infrastructure
- **Group / geometry / default / min zoom:** OXY — Occidental Footprint / `point` / ON / 0
- **Feature count:** 4 features (Point x4) = live 4
- **Purpose / thesis relevance:** OXY carbon management: Century CO2 capture (Pecos), Wasson/Denver Unit storage (Yoakum, Subpart RR MRV), STRATOS DAC (Ector, Class VI wells), King Ranch DAC + storage hub (Kleberg). Carbon-side context for the OXY partnership.
- **Storage:** standalone `data/oxy/oxy_carbon.geojson` (read directly; build.py:894)
- **Upstream source:** oxy_assets @ Century; EIA-860 @ Wasson; EPA Class VI permit (BRP CCS1 injection well, Penwell); centroid of RRC stratigraphic-test wells (NAD83).
- **Acquisition / scripts:** See the oxy_power card: built by scripts/build_oxy_assets.py + scripts/build_oxy_map_layers.py from already-sourced repo layers/public records; any county-centroid placements are flagged in `accuracy`.
- **Attributes carried:** GeoJSON properties: `name`, `carbon_type`, `county`, `detail`, `status`, `source`, `accuracy`
- **Build-time filters / transforms:** Standalone GeoJSON; no filters.
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#15803d`, radius `7`, stroke_color `#ffffff`, stroke_width `1.5`
- **UI filters (filterable_fields):** `carbon_type` (categorical, "Carbon type"); `county` (categorical, "County"); `status` (categorical, "Status")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Asset, `carbon_type`->Carbon type, `status`->Status, `detail`->Detail, `county`->County, `accuracy`->Location accuracy, `source`->Source; footer in the prior deploy: source only; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "EIA-860, EPA Class VI permit record and public company filings; LRP-curated OXY footprint"; `as_of` 2026-06-23
- **As-of date + evidence:** 2026-06-23 deploy (4 points upgraded to precise sourced coordinates that day).
- **Refresh cadence (upstream vs actual):** On demand.
- **Known caveats:** Accuracy values: `precise` x2, `precise (EPA Class VI permit)` x1, `precise (RRC strat-test well cluster)` x1 (a centroid of three wells, NAD83 unshifted). Kleberg/Ector are far from the Pecos site.

### oxy_drilling_permits

- **Label:** OXY drilling permits (RRC W-1)
- **Group / geometry / default / min zoom:** OXY — Occidental Footprint / `point` / off / 0
- **Feature count:** 1,336 features (Point x1336) = live 1,336 (prior deploy 294)
- **Purpose / thesis relevance:** OXY's drilling footprint (approved RRC W-1 permits 2020-2026) - shows where the neighbouring operator is actively drilling (Midland Basin core) vs the Pecos/Trans-Pecos site area, useful for the "no new drilling near Caramba" vibration argument.
- **Storage:** standalone `data/oxy/oxy_drilling_permits.geojson` (read directly; build.py:894)
- **Upstream source:** RRC "Drilling Permit EOM + Lat/Lon" monthly snapshots (`daf420.dat.MM-DD-YYYY`) from the GoAnywhere MFT folder `https://mft.rrc.texas.gov/link/f5dfea9c-…` (docs/refresh_automation_plan.md §3). Operator filter regex `(OXY|OCCIDENTAL)`: OXY USA INC. (#630591), OCCIDENTAL PERMIAN LTD (#617544), OXY USA WTP LP, OXY USA EOR LLC.
- **Acquisition / scripts:** `python3 scripts/fetch_rrc.py permits` (caches `data/rrc_raw/daf420.dat.*`; most-recent monthlies are NOT in folder-tail order - pull by parsed date) then `python3 scripts/build_oxy_drilling_permits.py`. Dual record-format reader (0108 master for 2018-2023, 0109 for 2024-2026; lat/lon range-anchored regex over 26-28 byte `14`/`15` location records). De-duplicated by permit number.
- **Attributes carried:** GeoJSON properties: `permit_no`, `operator`, `lease`, `well_no`, `county`, `county_fips`, `district`, `approved_date`, `submitted_date`, `permit_year`, `source`, `accuracy`
- **Build-time filters / transforms:** Standalone GeoJSON; no filters. Output atomic write.
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#e11d48`, radius `4`, stroke_color `#ffffff`, stroke_width `0.8`
- **UI filters (filterable_fields):** `operator` (categorical, "Operator"); `county` (categorical, "County"); `permit_year` (categorical, "Permit year")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `permit_no`->Permit no., `operator`->Operator, `lease`->Lease, `well_no`->Well no., `county`->County, `district`->RRC district, `approved_date`->Approved, `submitted_date`->Submitted, `accuracy`->Location accuracy, `source`->Source; footer in the prior deploy: source only; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "Railroad Commission of Texas, Drilling Permit Master + Lat/Lon (daf420 EOM monthly)"; `as_of` 2026-09-30
- **2026-10-21 refresh note:** Refreshed 2026-10-21 (commit 3cf3581, live since deploy 6ad88eb4): 294 -> 1,336 permits (full 110-snapshot set, scope 2020+, upstream filers only); yaml as_of 2026-09-30; script FIPS fallback map gained 6 counties; script now has MIN_YEAR 2020 and an EXCLUDE_OPS regex (LOW CARBON).
- **As-of date + evidence:** Live (3cf3581): all 110 EOM snapshots through 2026-09-30, scope permit_year >= 2020 (counts by year: 2020 103, 2021 194, 2022 253, 2023 277, 2024 257, 2025 175, 2026 77). Prior deploy: 294 permits from a partial snapshot set (2026-06-23).
- **Refresh cadence (upstream vs actual):** Upstream: RRC monthly EOM. Actual: manual; built 2026-06-23 and again 2026-10-21 (snapshots through 2026-09-30).
- **Known caveats:** Now: 1,336 permits (prior deploy 294): operators OXY USA INC.: 611, OCCIDENTAL PERMIAN LTD.: 510, OXY USA WTP LP: 214, OXY USA EOR, LLC: 1; 24 counties; accuracy values: precise (RRC operator-reported): 1,336. The CHANGELOG 2026-10-21 table says 2,548 (2015-2026) but the committed file, commit message and layer scope say 1,336 with 2020+ and upstream filers only (the script filters `permit_year >= 2020` and drops "LOW CARBON" entities). Off by default (only OXY layer with `default_on: false`). The layer carries no `name`, so the popup title falls back to the layer label. Uses the unverified empirical record layout (docs/rrc_layouts/permit_purpose_codes.md; RRC does not publish the daf420 layout).

## 2.4 Local Focal Points

### solstice_substation

- **Label:** AEP Solstice Substation
- **Group / geometry / default / min zoom:** Local Focal Points / `point` / ON / 0
- **Feature count:** 1 features (Point x1) = live 1
- **Purpose / thesis relevance:** The 765 kV hub for the thesis: AEP Solstice is the terminus of the Permian Basin Reliability Plan (Howard-Solstice 765 kV; Bottlebrush-Solstice 345 kV; Faulkner-Solstice 345 kV). Interconnect point for Caramba North (OM CONFIG `solstice_miles: 15`, counterparty-supplied).
- **Storage:** `combined_geoms.geojson` (properties.layer_id = `solstice_substation`), split at build (build.py:417)
- **Upstream source:** OpenStreetMap (ODbL) way 500535889 (feature `source`); status/role text is editorial from the Permian Basin Reliability Plan.
- **Acquisition / scripts:** scripts/edit_local_devs.py: surgical atomic edit adding the `solstice_substation` point to `combined_geoms.geojson`. Not refreshed since.
- **Attributes carried:** `name, operator, county (Pecos), voltage_kv, status ("Operational; 765 kV expansion planned"), role, osm_id, source, source_date`.
- **Build-time filters / transforms:** `split_combined_geojson` -> `-Z0 -z14`.
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#FFD400`, circle_radius `22`, fill_opacity `0`, stroke_color `#FFD400`, stroke_width `5`
- **UI filters (filterable_fields):** none declared
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Substation, `operator`->Operator, `county`->County, `voltage_kv`->Voltage (kV), `status`->Status, `role`->Role, `osm_id`->OSM ID; footer in the prior deploy: yes (source + source_date); footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "OpenStreetMap way 500535889"; `as_of` 2026-04-27
- **As-of date + evidence:** 2026-04-27 (feature source_date; yaml as_of agrees).
- **Refresh cadence (upstream vs actual):** Persistent. No refresh.
- **Known caveats:** Single point. Yaml styling (yellow ring, circle_radius 22, stroke_width 5, fill_opacity 0) is largely not applied: `circle_radius`/`stroke_*` are not forwarded to the client (build.py:1168) and fill_opacity 0 makes the fill transparent, so by code reading the marker renders as a small (radius 3) hollow circle with the default white 1.5 px outline. Code-derived; not verified visually. Point position is the OSM way geometry (precision not documented).

### waha_circle

- **Label:** WAHA Natural Gas Hub
- **Group / geometry / default / min zoom:** Local Focal Points / `point` / ON / 0 / companions ['labels_hubs']
- **Feature count:** 1 features (Point x1) = live 1
- **Purpose / thesis relevance:** Marks the Waha natural-gas pricing hub in Pecos County (Coyanosa area) - the gas-supply reference for Caramba North (OM CONFIG `waha_miles: 20`; counterparty gas quote 200,000 MMBtu/d, 15 yr).
- **Storage:** `combined_geoms.geojson` (properties.layer_id = `waha_circle`), split at build (build.py:417)
- **Upstream source:** `source = "Natural gas hub (Waha)"` - not a dataset. Waha is a pricing hub, not a single facility; the marker position is editorial.
- **Acquisition / scripts:** scripts/edit_109b_consolidate.py ("Reposition WAHA from Reeves into Pecos") and scripts/edit_local_devs.py ("Reposition WAHA features (waha_circle, labels_hubs) to Coyanosa, Pecos County and uppercase name to WAHA"). Hand-placed coordinates (predates the no-hand-coded-coordinates rule); no public dataset cited.
- **Attributes carried:** `name, source, source_date`.
- **Build-time filters / transforms:** `-Z0 -z14`. Declared `companions: [labels_hubs]` (toggling the circle also toggles the text label + marker).
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#FFD400`, circle_radius `16`, fill_opacity `0`, stroke_color `#FFD400`, stroke_width `2.5`
- **UI filters (filterable_fields):** none declared
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Hub; footer in the prior deploy: yes; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "Natural gas hub (Waha), LRP hand-placed"; `as_of` 2026-04-21
- **As-of date + evidence:** 2026-04-21.
- **Refresh cadence (upstream vs actual):** Persistent.
- **Known caveats:** Hand-placed toponym (see acq); precision not documented. Same ring-styling caveat as solstice_substation (circle_radius 16 / stroke 2.5 / fill 0 not forwarded; renders as small hollow circle by code reading).

### labels_hubs

- **Label:** WAHA Hub Label
- **Group / geometry / default / min zoom:** Local Focal Points / `label` / ON / 4 / sidebar-hidden (`sidebar_omit`) / `show_marker`
- **Feature count:** 1 features (Point x1) = live 1
- **Purpose / thesis relevance:** Text label ("WAHA") companion to waha_circle.
- **Storage:** `combined_geoms.geojson` (properties.layer_id = `labels_hubs`), split at build (build.py:417)
- **Upstream source:** Same feature set as waha_circle (`source = "Natural gas hub (Waha)"`).
- **Acquisition / scripts:** Same one-off edit scripts as waha_circle.
- **Attributes carried:** `name, source, source_date`.
- **Build-time filters / transforms:** `-Z0 -z14`; `min_zoom: 4`.
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#fef3c7`
- **UI filters (filterable_fields):** none declared
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Hub; footer in the prior deploy: yes; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "Natural gas hub (Waha), LRP hand-placed"; `as_of` 2026-04-21
- **As-of date + evidence:** 2026-04-21.
- **Refresh cadence (upstream vs actual):** Persistent.
- **Known caveats:** Sidebar-hidden (`sidebar_omit: true`); toggled only through waha_circle `companions`. `show_marker: true` adds a circle (radius 6, `#fef3c7`, white 2 px stroke) under the text. Light colour -> dark text halo.

### mpgcd_zone1

- **Label:** Groundwater District Management Zone 1
- **Group / geometry / default / min zoom:** Local Focal Points / `fill` / ON / 0
- **Feature count:** 1 features (Polygon x1) = live 1
- **Purpose / thesis relevance:** Water thesis: the groundwater-district management zone covering the Caramba area (the tract bbox lies inside this polygon's bbox). Frames the 47,418 AF/yr groundwater permit referenced in the OM (CONFIG `water_af_yr`).
- **Storage:** `combined_geoms.geojson` (properties.layer_id = `mpgcd_zone1`), split at build (build.py:417)
- **Upstream source:** MPGCD management-zone PDF map (ARCHITECTURE.md §5/§9: "MPGCD PDF (APPROXIMATE)", "No vector source"). The layer-level yaml `source` (HEAD 736a18d) expands the acronym to Middle Pecos Groundwater Conservation District; the repo's tracked docs only use "MPGCD". PDF URL: Not documented in repo.
- **Acquisition / scripts:** Hand-digitized polygon (18 vertices) in `combined_geoms.geojson`; no script. ARCHITECTURE.md §5 cadence: "Replace when TWDB publishes" a vector.
- **Attributes carried:** `NAME, ZONE (=1), ACCURACY ("APPROXIMATE"), note`.
- **Build-time filters / transforms:** `-zg` (single polygon; renders).
- **Tippecanoe flags:** `-zg`
- **Styling (layers.yaml):** colour `#8b5cf6`, fill_opacity `0`, stroke_color `#a78bfa`, stroke_width `1.5`
- **UI filters (filterable_fields):** none declared
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `NAME`->District, `ZONE`->Zone, `ACCURACY`->Accuracy, `note`->Note; footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "Middle Pecos Groundwater Conservation District management-zone PDF; approximate boundary"; `as_of` 2026-06-23
- **As-of date + evidence:** Not documented.
- **Refresh cadence (upstream vs actual):** Static until an official vector exists.
- **Known caveats:** APPROXIMATE boundary - not a legal description; do not use for parcel-level water-rights claims. Polygon bbox ~[-103.06, 30.75, -102.80, 30.95]. fill_opacity 0 (outline only), colour `#8b5cf6`, stroke yaml `#a78bfa` (not forwarded). No source in props, so no popup footer. TWDB aquifers polygons exist in the file but are not served (section 3).

## 2.5 Local Hyperscale DC & Power Campuses

### la_escalera

- **Label:** La Escalera Ranch (Apex Clean Energy)
- **Group / geometry / default / min zoom:** Local Hyperscale DC & Power Campuses / `fill` / ON / 0
- **Feature count:** 1 features (Polygon x1) = live 1
- **Purpose / thesis relevance:** Competing large-load/power campus in Pecos County: Lyda Family La Escalera Ranch, site of Apex Clean Energy's Pecos Flat 3.3 GW wind/solar/green-hydrogen complex. Competitive context for land, transmission and water in Pecos.
- **Storage:** `combined_geoms.geojson` (properties.layer_id = `la_escalera`), split at build (build.py:417)
- **Upstream source:** Public reporting (kjas.com 2024-09), Pecos County School Fund lease, ranch literature (feature `source`).
- **Acquisition / scripts:** scripts/edit_local_devs.py added the polygon ("La Escalera Ranch / Apex Pecos Flat (APPROXIMATE)"). Boundary digitized from public references, not a survey.
- **Attributes carried:** `name, owner (Lyda Family), developer, county ("Pecos (primary); Brewster"), acres, project, ACCURACY, source, source_date`.
- **Build-time filters / transforms:** `-Z0 -z14`.
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#ef4444`, fill_opacity `0`, stroke_color `#ef4444`, stroke_width `2.5`
- **UI filters (filterable_fields):** none declared
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Tract, `owner`->Owner, `developer`->Developer, `county`->County, `acres`->Acres, `project`->Project, `ACCURACY`->Boundary accuracy; footer in the prior deploy: yes; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "Public reporting (kjas.com 2024-09; Pecos County School Fund lease; ranch literature); approximate boundary"; `as_of` 2026-04-27
- **As-of date + evidence:** 2026-04-27.
- **Refresh cadence (upstream vs actual):** Persistent; no refresh.
- **Known caveats:** ACCURACY property: "APPROXIMATE - ranch boundary digitized from public-domain references; not a survey product" (11 vertices; bbox ~[-103.05, 30.35, -102.66, 30.69]; ~223,000-acre outline per description). Outline-only (fill_opacity 0, `#ef4444`; outline layer uses colour width 2 - yaml stroke_width 2.5 not forwarded).

### longfellow_ranch

- **Label:** Longfellow Ranch
- **Group / geometry / default / min zoom:** Local Hyperscale DC & Power Campuses / `fill` / ON / 0
- **Feature count:** 1 features (Polygon x1) = live 1
- **Purpose / thesis relevance:** Direct comparable: Mitchell family ranch hosting Poolside's 2 GW "Project Horizon" AI campus (anchor tenant CoreWeave) in central Pecos County - the nearest hyperscale DC/power campus to the Caramba thesis.
- **Storage:** `combined_geoms.geojson` (properties.layer_id = `longfellow_ranch`), split at build (build.py:417)
- **Upstream source:** Poolside Project Horizon announcement (2025-10); Longfellow Ranches public materials (feature `source`). Corroborating layers: tceq_gas_turbines (Poolside LF Phase 2 DC Ops, Fort Stockton), tax_abatements (Poolside/CoreWeave load notes).
- **Acquisition / scripts:** Created in scripts/edit_109b_consolidate.py; geometry REPLACED in scripts/edit_110c_trans_fix.py because the original polygon sat on the ranch homestead in southern Pecos/Terrell/Brewster, not at the Project Horizon site (the central-Pecos ERCOT cluster). Both are hand-digitized.
- **Attributes carried:** `name, owner ("Mitchell Family / Riata / Mitchell Group"), developer, campus, capacity, county ("Pecos / Terrell / Brewster"), ACCURACY, source, source_date`.
- **Build-time filters / transforms:** `-Z0 -z14`.
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#ef4444`, fill_opacity `0`, stroke_color `#ef4444`, stroke_width `2.5`
- **UI filters (filterable_fields):** none declared
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Tract, `owner`->Owner, `developer`->Developer, `campus`->Type, `capacity`->Capacity, `county`->County, `ACCURACY`->Boundary accuracy; footer in the prior deploy: yes; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "Poolside Project Horizon announcement (2025-10); Longfellow Ranches public materials; approximate boundary"; `as_of` 2026-04-27
- **As-of date + evidence:** 2026-04-27.
- **Refresh cadence (upstream vs actual):** Persistent.
- **Known caveats:** ACCURACY: "APPROXIMATE - ranch boundary digitized from public references; project area is a sub-portion" (8 vertices; bbox ~[-102.78, 30.69, -102.59, 30.84]). The polygon is the ranch, not the campus parcel. Previously mislocated once (see acq).

### gw_ranch

- **Label:** GW Ranch (Pacifico Energy)
- **Group / geometry / default / min zoom:** Local Hyperscale DC & Power Campuses / `fill` / ON / 0
- **Feature count:** 1 features (Polygon x1) = live 1
- **Purpose / thesis relevance:** Pacifico Energy's 7.65 GW off-grid gas + battery + solar DC campus on Hwy 18, ~17 mi N of Fort Stockton (largest TCEQ-permitted DC campus in the U.S.): the nearest direct competitor for Waha gas and Pecos County power/land, and a bypass-the-grid comparable.
- **Storage:** `combined_geoms.geojson` (properties.layer_id = `gw_ranch`), split at build (build.py:417)
- **Upstream source:** Pacifico Energy press materials; TCEQ permit; Texas Tribune / DCD / Big Bend Sentinel reporting (feature `source`).
- **Acquisition / scripts:** scripts/edit_109b_consolidate.py appended the polygon. Hand-digitized footprint.
- **Attributes carried:** `name, developer, campus, capacity, status ("Permitted; first power Q1 2027; 1 GW online 2028; 5+ GW by 2031"), grid ("Off-grid / private (no ERCOT interconnect)"), county (Pecos), ACCURACY, source, source_date`.
- **Build-time filters / transforms:** `-Z0 -z14`.
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#ef4444`, fill_opacity `0`, stroke_color `#ef4444`, stroke_width `2.5`
- **UI filters (filterable_fields):** none declared
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Project, `developer`->Developer, `campus`->Type, `capacity`->Capacity, `status`->Status, `grid`->Grid, `county`->County, `ACCURACY`->Boundary accuracy; footer in the prior deploy: yes; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "Pacifico Energy GW Ranch press materials; TCEQ permit; Texas Tribune / DCD / Big Bend Sentinel reporting"; `as_of` 2026-04-27
- **As-of date + evidence:** 2026-04-27.
- **Refresh cadence (upstream vs actual):** Persistent.
- **Known caveats:** ACCURACY: "APPROXIMATE - campus footprint approximated from public reporting (Hwy 18, ~17 mi N of Fort Stockton)". 5 vertices, bbox ~[-102.87, 31.11, -102.81, 31.16]. data/datacenters/README.md notes sources disagree (17 mi N vs 33 mi S of Fort Stockton; the more-cited figure was used).

## 2.6 Power Generation

### eia860_plants

- **Label:** Power Plants (EIA-860)
- **Group / geometry / default / min zoom:** Power Generation / `point` / off / 0
- **Feature count:** 1,532 rows (live registry 1,532) (prior deploy 1,367)
- **Purpose / thesis relevance:** Existing generation fleet statewide: shows nearby thermal/renewable plants and who owns them (Pecos/Reeves/Ward/Ector area supply context, comparables for capacity and fuel mix).
- **Storage:** `combined_points.csv` (layer_id = `eia860_plants`), split to NDJSON at build (build.py:314)
- **Upstream source:** U.S. Energy Information Administration, Form EIA-860 annual zip `https://www.eia.gov/electricity/data/eia860/xls/eia860<year>.zip` (needs `Referer: https://www.eia.gov/electricity/data/eia860/` and a browser UA or EIA returns 503). HEAD data = 2025 data-year release (`eia8602025.zip`; yaml says released 2026-09-10); the prior deploy carried the 2024 release (`eia8602024.zip`).
- **Acquisition / scripts:** `python scripts/refresh_eia860.py [--year 2024] [--out outputs/refresh]` -> `outputs/refresh/eia860_plants_<date>.csv` and `eia860_battery_<date>.csv` (31-col combined_points schema, Texas only). Capacity/technology/fuel are aggregated from the Generator sheet (`Status == OP`, sum nameplate MW, mode of Technology / Energy Source 1), NOT the Plant sheet (ARCHITECTURE.md §4). Then `python3 build.py merge eia860_plants <file>`.
- **Attributes carried:** combined_points.csv columns populated at HEAD (non-blank rows of 1,532): `name` (1,532), `plant_code` (1,532), `county` (1,532), `technology` (1,003), `sector` (1,532), `fuel` (1,003), `commissioned` (1,003), `capacity_mw` (1,003), `operator` (1,532)
- **Build-time filters / transforms:** `split_combined_csv`: fuel codes relabelled (e.g. `NG` -> "Natural Gas (NG)", build.py:350); fuzzy tax-abatement join annotates matched plants with `abatement_*` props (ABATEMENT_TARGET_LAYERS, build.py:107-212). Numeric coercion for `plant_code, capacity_mw`.
- **Tippecanoe flags:** `-zg`
- **Styling (layers.yaml):** colour `#22d3ee`, radius `6`
- **UI filters (filterable_fields):** `county` (categorical, "County"); `technology` (categorical, "Technology"); `fuel` (categorical, "Fuel"); `capacity_mw` (numeric, "Capacity (MW)"); `commissioned` (numeric, "Commissioned (year)"); `name` (text, "Plant name")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Plant, `plant_code`->EIA Plant Code, `county`->County, `operator`->Operator, `sector`->Sector, `commissioned`->Commissioned, `capacity_mw`->Capacity (MW), `technology`->Technology, `fuel`->Fuel; footer in the prior deploy: no (combined_points has no source columns); footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "U.S. EIA, Form EIA-860 annual generator survey (2025 data, released 2026-09-10)"; `as_of` 2026-10-21
- **2026-10-21 refresh note:** Refreshed 2026-10-21 (commit 3cf3581, live since deploy 6ad88eb4): 1,367 -> 1,532 rows; EIA-860 2025 data (`eia8602025.zip`; yaml source says released 2026-09-10); yaml as_of 2026-10-21. Per CHANGELOG 2026-10-21.
- **As-of date + evidence:** Live (3cf3581 / deploy 6ad88eb4): EIA-860 2025 data, refreshed 2026-10-21 (outputs/refresh/CHANGELOG.md). Prior deploy: 2024 data, refreshed 2026-04-25/28 (docs/layer_inventory_2026-05-13.md).
- **Refresh cadence (upstream vs actual):** Upstream: annual (EIA-860 2025 data released 2026-09-10 per yaml). Actual: manual; refreshed 2026-04 and 2026-10-21.
- **Known caveats:** HEAD: capacity/technology/fuel/commissioned populated for 1,003/1,532 plants (65.5%); the rest lack capacity so sizing falls back to the static radius 6 (prior 2024 data: 891/1,367 = 65.2%, 476 without; template comment build_template.html:511). `commissioned` is a year (numeric), 1927–2025 (prior 1927-2024). Statewide (220 distinct counties), not Permian-only. Sector counts at HEAD: IPP Non-CHP: 1,224, Electric Utility: 117, Commercial Non-CHP: 99, Industrial CHP: 48, Industrial Non-CHP: 19, IPP CHP: 17, Commercial CHP: 8. Icon overlay `plant` from zoom 9. Popup title = plant `name`; `abatement_*` rows appear as raw keys if matched (113 plants matched now; 104 on the prior data).

### eia860_battery

- **Label:** Battery Storage (EIA-860)
- **Group / geometry / default / min zoom:** Power Generation / `point` / off / 0
- **Feature count:** 203 rows (live registry 203) (prior deploy 133)
- **Purpose / thesis relevance:** Operating battery storage statewide: co-location/fast-ramp context for a data-center load and BESS-heavy ERCOT queue.
- **Storage:** `combined_points.csv` (layer_id = `eia860_battery`), split to NDJSON at build (build.py:314)
- **Upstream source:** EIA-860 energy-storage workbook (`3_4_Energy_Storage_Y<year>.xlsx` in 2024+ releases; script comment build line 67).
- **Acquisition / scripts:** Same script/command as eia860_plants (two CSVs per run).
- **Attributes carried:** combined_points.csv columns populated at HEAD (non-blank rows of 203): `name` (203), `plant_code` (203), `county` (203), `technology` (203), `capacity` (203), `commissioned` (203), `capacity_mw` (203), `operator` (203)
- **Build-time filters / transforms:** Fuel relabel not relevant (no `fuel`); abatement fuzzy join annotates matches (11 now; 7 on the prior data).
- **Tippecanoe flags:** `-zg`
- **Styling (layers.yaml):** colour `#f472b6`, radius `4`
- **UI filters (filterable_fields):** `county` (categorical, "County"); `technology` (categorical, "Technology"); `capacity_mw` (numeric, "Capacity (MW)"); `commissioned` (numeric, "Commissioned (year)"); `name` (text, "Plant name")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Battery, `plant_code`->EIA Plant Code, `county`->County, `operator`->Operator, `commissioned`->Commissioned, `capacity_mw`->Capacity (MW), `technology`->Technology; footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "U.S. EIA, Form EIA-860 annual generator survey (2025 data, released 2026-09-10)"; `as_of` 2026-10-21
- **2026-10-21 refresh note:** Refreshed 2026-10-21 (commit 3cf3581, live since deploy 6ad88eb4): 133 -> 203 rows; EIA-860 2025 data; yaml as_of 2026-10-21.
- **As-of date + evidence:** Live (3cf3581): EIA-860 2025 data (2026-10-21). Prior deploy: 2024 data (2026-04-25/28).
- **Refresh cadence (upstream vs actual):** Annual upstream; manual refresh (2026-04, 2026-10-21).
- **Known caveats:** HEAD: 203 rows (technology: LIB: 201, OTH: 2); `capacity` and `capacity_mw` are duplicate columns (1.5–304 MW); commissioned 2012–2025 (prior deploy: 133 rows, LIB 131 / OTH 2, 1.5-300 MW, 2012-2024). Icon `battery` from zoom 9.

### wind

- **Label:** Wind Turbines (USWTDB)
- **Group / geometry / default / min zoom:** Power Generation / `point` / off / 7
- **Feature count:** 19,943 rows (live registry 19,943) (prior deploy 19,464)
- **Purpose / thesis relevance:** Turbine-level wind fleet statewide (Pecos/Reeves/Upton wind belt): shows wind build-out near Caramba and Solstice and the renewable context behind the queue and abatements.
- **Storage:** `combined_points.csv` (layer_id = `wind`), split to NDJSON at build (build.py:314)
- **Upstream source:** USWTDB PostgREST API `https://eersc.usgs.gov/api/uswtdb/v1/turbines?t_state=eq.TX` (no auth; paged by `case_id`, 1,000-row cap). Operator-verified 2026-10-20: the API TLS certificate is expired upstream (OPERATING_MANUAL.md Known Defect #5).
- **Acquisition / scripts:** `python scripts/refresh_uswtdb.py [--out outputs/refresh] [--from-file F | --from-url U]` -> `outputs/refresh/wind_<date>.csv`; `capacity_mw` computed from `t_cap` (kW); only `t_state == TX`. The `--from-file/--from-url` file-release path (valid TLS, `https://energy.usgs.gov/uswtdb/assets/data/uswtdbCSV.zip`) was added at 3cf3581 because the API certificate is expired; the 2026-10-21 refresh used it (V9.1). Then `build.py merge wind <file>`.
- **Attributes carried:** combined_points.csv columns populated at HEAD (non-blank rows of 19,943): `county` (19,943), `commissioned` (19,705), `capacity_mw` (19,204), `project` (19,943), `manu` (19,204), `model` (19,203), `cap_kw` (19,204), `year` (19,705)
- **Build-time filters / transforms:** Tippecanoe `-zg -r1 --drop-densest-as-needed --extend-zooms-if-still-dropping`; `min_zoom 7`; sizing `mw_small`. `operator`/`name` are blank by design (USWTDB `p_owner` deprecated).
- **Tippecanoe flags:** `-zg` `-r1` `--drop-densest-as-needed` `--extend-zooms-if-still-dropping`
- **Styling (layers.yaml):** colour `#84cc16`, radius `2`
- **UI filters (filterable_fields):** `county` (categorical, "County"); `capacity_mw` (numeric, "Capacity (MW)"); `commissioned` (numeric, "Commissioned (year)"); `manu` (categorical, "Manufacturer"); `project` (text, "Project")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `project`->Project, `county`->County, `commissioned`->Commissioned, `capacity_mw`->Turbine MW, `manu`->Manufacturer, `model`->Model; footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "USGS / LBNL / ACP, U.S. Wind Turbine Database (USWTDB) V9.1"; `as_of` 2026-09-28
- **2026-10-21 refresh note:** Refreshed 2026-10-21 (commit 3cf3581, live since deploy 6ad88eb4): 19,464 -> 19,943 rows from the USWTDB V9.1 file release (as_of 2026-09-28) because the API certificate is expired; `refresh_uswtdb.py` gained `--from-file/--from-url`.
- **As-of date + evidence:** Live (3cf3581): USWTDB V9.1 file release (yaml as_of 2026-09-28), merged 2026-10-21. Prior deploy: 2026-04-25 file (yaml then said 2026-04-28).
- **Refresh cadence (upstream vs actual):** Upstream: quarterly. Actual: manual (2026-04, 2026-10-21).
- **Known caveats:** No `name` field, so popup title is the layer label; `project` identifies the wind farm. Now: capacity_mw populated 19,204/19,943, commissioned 1999–2026, 294 projects, 23 manufacturers, 103 counties (prior deploy: 19,267/19,464 with capacity, 1999-2025, 281 projects, 23 manufacturers). 0 turbines get an abatement annotation (no `name`/`entity`/`operator`; `project` only).

### solar

- **Label:** Solar Farms (EIA-860)
- **Group / geometry / default / min zoom:** Power Generation / `point` / off / 0
- **Feature count:** 180 rows (live registry 180)
- **Purpose / thesis relevance:** Utility solar plants statewide: comparable/peer supply and queue-conversion context for the West Texas solar belt.
- **Storage:** `combined_points.csv` (layer_id = `solar`), split to NDJSON at build (build.py:314)
- **Upstream source:** EIA-860 solar sheet (promoted to `3_3` in the 2024+ release, scripts/refresh_eia860.py comment). ARCHITECTURE.md §9: USPVDB has chronic 503s so EIA-860 `3_3_Solar_Y2024.xlsx` is used.
- **Acquisition / scripts:** `scripts/refresh_eia860.py` docstring says it emits only plants and battery CSVs; no script in the repo documents how the `solar` rows were produced or how to refresh them. docs/refresh_automation_plan.md classes it "static (EIA-860 derived), refreshed alongside eia860". Not documented in repo.
- **Attributes carried:** combined_points.csv columns populated at HEAD (non-blank rows of 180): `name` (180), `plant_code` (180), `county` (180), `capacity_mw` (180)
- **Build-time filters / transforms:** Abatement fuzzy join annotates matches (23 now; 22 on the prior data). Sizing by capacity.
- **Tippecanoe flags:** `-zg`
- **Styling (layers.yaml):** colour `#facc15`, radius `4`
- **UI filters (filterable_fields):** `county` (categorical, "County"); `capacity_mw` (numeric, "Capacity (MW)"); `name` (text, "Plant name")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Plant, `plant_code`->EIA Plant Code, `county`->County, `capacity_mw`->Capacity (MW); footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "U.S. EIA, Form EIA-860 (2024 release), solar generators"; `as_of` 2026-04-28
- **As-of date + evidence:** 2026-04-28 / EIA 2024 data year.
- **Refresh cadence (upstream vs actual):** Annual upstream; no refresh path.
- **Known caveats:** Only `name, plant_code, county, capacity_mw` (1.1-631.98 MW) - no operator, technology or commissioning year. Icon `solar` from zoom 9.

## 2.7 Transmission & Grid

### substations

- **Label:** Substations (OSM)
- **Group / geometry / default / min zoom:** Transmission & Grid / `point` / off / 7
- **Feature count:** 1,637 rows (live registry 1,637)
- **Purpose / thesis relevance:** Substation locations/voltages near the site: where a 138/345/765 kV interconnect could physically land and who owns the nearby grid (Solstice neighbourhood).
- **Storage:** `combined_points.csv` (layer_id = `substations`), split to NDJSON at build (build.py:314)
- **Upstream source:** OpenStreetMap `power=substation` features via the Overpass API (3-endpoint fallback; ARCHITECTURE.md §9). HIFLD substations are token-gated/68-row subset so OSM is the documented source.
- **Acquisition / scripts:** No script (OPERATING_MANUAL.md §3: "OSM Overpass pulled in chat sessions"). Query text/bbox: Not documented in repo.
- **Attributes carried:** combined_points.csv columns populated at HEAD (non-blank rows of 1,637): `osm_id` (1,637), `name` (958), `operator` (798), `voltage` (1,446)
- **Build-time filters / transforms:** `-zg --drop-densest-as-needed`, `min_zoom 7`. Radius sizing rule `kv` (see caveats).
- **Tippecanoe flags:** `-zg` `--drop-densest-as-needed`
- **Styling (layers.yaml):** colour `#a78bfa`, radius `3`
- **UI filters (filterable_fields):** `voltage` (numeric, "Voltage (V)"); `operator` (text, "Operator"); `name` (text, "Name")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Name, `operator`->Operator, `voltage`->Voltage (V), `osm_id`->OSM ID; footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "OpenStreetMap via Overpass API"; `as_of` 2026-04-28
- **As-of date + evidence:** 2026-04-28 per docs/layer_inventory_2026-05-13.md; 2026-04-23 per docs/refresh_automation_plan.md (conflict).
- **Refresh cadence (upstream vs actual):** OSM continuous; actual one-time pull (quarterly recommended, never automated).
- **Known caveats:** `voltage` is in VOLTS as strings (69000-345000; 1,137 of 1,446 populated values numeric, 309 are multi-voltage strings like "138000;69000") but SIZING_RULES mode `kv` interpolates on 0-500 kV, so every numeric value is far above the last stop and renders at the max radius (14 px); multi-voltage strings fall back to the static radius. Code-derived. 958/1,637 have a name, 798 an operator (70 distinct). Also used as POI target in ERCOT queue geocode Stage 2 (`substation_poi`).

### tpit_subs

- **Label:** Planned Substation Upgrades (TPIT)
- **Group / geometry / default / min zoom:** Transmission & Grid / `point` / off / 6
- **Feature count:** 141 rows (live registry 141)
- **Purpose / thesis relevance:** Planned substation upgrades in the ERCOT regional-planning pipeline - shows where grid capacity is being added near Pecos/Solstice.
- **Storage:** `combined_points.csv` (layer_id = `tpit_subs`), split to NDJSON at build (build.py:314)
- **Upstream source:** ERCOT TPIT report XLSX (monthly). The repo only writes "ERCOT TPIT"/"TPIT XLSX"; the expansion in the layer yaml `source` is not in the older docs. Exact URL: Not documented in repo.
- **Acquisition / scripts:** None in repo as a producer. scripts/refresh_tpit.py (3cf3581) documents that every `tpit_subs` row is an exact copy of an OSM `substations` row (same name/lat/lon/operator/voltage) with no TPIT attributes - so the layer is "OSM substations that are endpoints of TPIT projects", and there is nothing TPIT-specific to refresh.
- **Attributes carried:** combined_points.csv columns populated at HEAD (non-blank rows of 141): `name` (141), `operator` (129), `voltage` (138)
- **Build-time filters / transforms:** `-zg`; `min_zoom 6`; kv sizing rule (same volts-vs-kV mismatch as substations).
- **Tippecanoe flags:** `-zg`
- **Styling (layers.yaml):** colour `#a78bfa`, radius `3.5`
- **UI filters (filterable_fields):** `voltage` (numeric, "Voltage (V)"); `operator` (categorical, "Operator"); `name` (text, "Name")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Substation, `voltage`->Voltage (V), `operator`->Operator; footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "ERCOT Transmission Project and Information Tracking (TPIT) report"; `as_of` 2026-04
- **As-of date + evidence:** 2026-04 / 2026-04-25.
- **Refresh cadence (upstream vs actual):** Upstream monthly; actual one-time.
- **Known caveats:** `voltage` populated 138/141 (volts; 78 numeric, rest multi-voltage strings). `operator` 129 populated (21 distinct). Because rows are OSM copies, the label "Planned Substation Upgrades (TPIT)" overstates what the points carry (no status/in-service/project attributes). Recoloured from cyan to `#a78bfa` (same as substations) in scripts/edit_110c_trans_fix.py. Used as POI target for ERCOT geocode Stage 2 (`tpit_poi`).

### transmission

- **Label:** Transmission ≥100 kV
- **Group / geometry / default / min zoom:** Transmission & Grid / `line` / off / 0
- **Feature count:** 6,244 features (LineString x6225, MultiLineString x19) = live 6,244
- **Purpose / thesis relevance:** Existing high-voltage network: how close Caramba North is to the 345/500 kV backbone and the Solstice terminus; baseline against which TPIT planned lines (incl. 765 kV) are read.
- **Storage:** `combined_geoms.geojson` (properties.layer_id = `transmission`), split at build (build.py:417)
- **Upstream source:** HIFLD Electric Power Transmission Lines FeatureServer `services1.arcgis.com/Hp6G80Pky0om7QvQ/.../Electric_Power_Transmission_Lines/FeatureServer/0` (docs/archive/wip_history_pre_2026-05-18.md:227-229).
- **Acquisition / scripts:** No script (docs/refresh_automation_plan.md: "combined-csv (hand-edited)"). Edited once by scripts/edit_110c_trans_fix.py (sidebar order only).
- **Attributes carried:** GeoJSON properties (HEAD): `V`, `O`
- **Build-time filters / transforms:** `-zg --simplification=8 --coalesce-densest-as-needed`; coordinates 4-decimal (ARCHITECTURE.md §4).
- **Tippecanoe flags:** `-zg` `--simplification=8` `--coalesce-densest-as-needed`
- **Styling (layers.yaml):** colour `#38bdf8`
- **UI filters (filterable_fields):** `V` (numeric, "Voltage (kV)"); `O` (text, "Operator")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `V`->Voltage (kV), `O`->Operator; footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "HIFLD electric power transmission lines (ArcGIS Online), >=100 kV"; `as_of` 2026-04
- **As-of date + evidence:** 2026-04 (layer inventory: HIFLD AGOL 2026-04).
- **Refresh cadence (upstream vs actual):** Upstream: annual. Actual: one-time.
- **Known caveats:** Label says >=100 kV but values present are 138 (5,181), 345 (660), 161 (256), 230 (139), 500 (8) kV only - no 69 or 115 kV and no 765 kV (planned 765 kV lines exist only in tpit_lines). Layer inventory notes the R2.5 spec asked for >=69 kV (not done). Properties: `V` (kV), `O` (operator; 90 distinct). Static 0.75 width: `transmission` is not in SIZING_RULES (the "no voltage" comment in the template is stale; V exists). 6,244 features incl. 19 MultiLineString; extent spans beyond Texas (bbox ~[-108.5, 25.9, -93.2, 37.9]).

### tpit_lines

- **Label:** Planned Transmission Upgrades (TPIT)
- **Group / geometry / default / min zoom:** Transmission & Grid / `line` / off / 0
- **Feature count:** 133 features (LineString x133) = live 133
- **Purpose / thesis relevance:** Planned/under-construction transmission upgrades by tier and in-service date, including the three 765 kV segments that tie to Solstice.
- **Storage:** `combined_geoms.geojson` (properties.layer_id = `tpit_lines`), split at build (build.py:417)
- **Upstream source:** ERCOT Planning page `https://www.ercot.com/gridinfo/planning`, link "Transmission Project and Information Tracking"; the 2026-10-21 refresh used `https://www.ercot.com/files/docs/2022/03/02/ERCOT-July-Ad-Hoc-TPIT-No-Cost-071326-UPDATE.xlsx` (Last-Modified Fri, 17 Jul 2026 18:45:59 GMT). Sheets Future*/Planned*/Completed*/Cancelled*.
- **Acquisition / scripts:** Geometry: NOT produced by any script in the repo. scripts/refresh_tpit.py (new at 3cf3581) documents that every line is a straight 2-point line between two OSM `substations` rows (`from`/`to` = the matched substation names) selected from ~1,340 TPIT projects with both terminals, and that the terminal-to-substation matching rule is not reproducible (the repo fuzzy kernel agrees with only ~51-66% of the 266 endpoints). The script therefore refreshes ATTRIBUTES only (status, tier, sheet, in_service, owner, voltage, county, name, from_raw/to_raw keyed on ERCOT project number `pid`), carrying geometry forward; cancelled projects are dropped. Output `outputs/refresh/tpit_lines_<date>.geojson` -> `python3 build.py merge tpit_lines <file>`. 2026-10-21 run: 133 features, attribute changes in_service 30, name 7, status 7, tier 3, owner 5, from_raw 6, to_raw 5, sheet 10.
- **Attributes carried:** GeoJSON properties (HEAD): `name`, `pid`, `owner`, `county`, `from`, `to`, `from_raw`, `to_raw`, `voltage`, `status`, `tier`, `sheet`, `in_service`
- **Build-time filters / transforms:** `-zg --simplification=8`; `line_width 0.75` in yaml but SIZING rule `kv_line` sets width 0.65-1.5 by voltage (kV values are correct here).
- **Tippecanoe flags:** `-zg` `--simplification=8`
- **Styling (layers.yaml):** colour `#06b6d4`, line_width `0.75`
- **UI filters (filterable_fields):** `owner` (categorical, "Owner"); `voltage` (categorical, "Voltage (kV)"); `status` (categorical, "Status"); `tier` (categorical, "TPIT tier"); `county` (categorical, "County"); `name` (text, "Project name")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Project, `owner`->Owner, `voltage`->Voltage (kV), `status`->Status, `tier`->TPIT tier, `in_service`->In-service date, `from`->From, `to`->To, `county`->County; footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "ERCOT Transmission Project and Information Tracking (TPIT) report, July 2026 update (attributes); geometry from April 2026 match"; `as_of` 2026-07-17
- **2026-10-21 refresh note:** Refreshed 2026-10-21 (commit 3cf3581, live since deploy 6ad88eb4): attributes refreshed from the July 2026 TPIT update via the new scripts/refresh_tpit.py; geometry unchanged.
- **As-of date + evidence:** Live (3cf3581): July 2026 TPIT update (xlsx dated 2026-07-17), refreshed 2026-10-21; geometry unchanged since the 2026-04 build. Prior deploy: 2026-04.
- **Refresh cadence (upstream vs actual):** Upstream: TPIT replaced in place (ad-hoc/monthly). Actual: refreshed once 2026-10-21.
- **Known caveats:** Properties: `name`, `pid`, `owner`, `county`, `from`, `to`, `from_raw`, `to_raw`, `voltage`, `status`, `tier`, `sheet`, `in_service`. Status counts now: Planned: 106, In-Service: 18, Under Construction: 5, Conceptual: 4. Voltage (kV): 138: 73, 69: 28, 345: 28, 765: 3, (blank): 1. Tiers: Tier 4: 62, Tier 1: 35, Tier 3: 28, Tier 2: 8. Geometry is straight lines between matched OSM substations, not engineered routes. Raw property keys (pid, sheet, from_raw, to_raw) show in the generic popup. Yaml colour `#06b6d4` (an earlier amber recolour in the archive is superseded). The three 765 kV segments are the only 765 kV lines on the map (`transmission` has none).

## 2.8 Pipelines

### rrc_pipelines

- **Label:** Oil & Gas Pipelines (>20", RRC)
- **Group / geometry / default / min zoom:** Pipelines / `line` / off / 0
- **Feature count:** 35,879 live (registry/tilestats only; source not present in this checkout)
- **Purpose / thesis relevance:** Large-diameter oil & gas transmission pipelines (gas supply routes to Waha-area demand, crude/NGL right-of-way constraints).
- **Storage:** prebuilt PMTiles `tiles/rrc_pipelines.pmtiles` (not in git; resolved `$LRP_PROJECT_DIR/rrc_pipelines.pmtiles` -> `$LRP_UPLOADS_DIR/rrc_pipelines.pmtiles` -> https://lrp-tx-gis.netlify.app/tiles/rrc_pipelines.pmtiles; build.py:793)
- **Upstream source:** RRC pipeline GIS (ArcGIS), filtered `DIAMETER >= 20` and Permian bbox per Chat 43 (docs/archive/wip_log_pre_chat83.md:564). ARCHITECTURE.md §9: RRC pipelines AGOL `STATUS_CD='A'` returns 0 rows; the working slice uses `STATUS_CD='B'`.
- **Acquisition / scripts:** Prebuilt PMTiles (3-tier resolution, build.py:793); built outside the repo. No script. Live registry: 35,879 features.
- **Attributes carried:** From yaml: `operator, system, commodity, diameter_in, source_date` (real keys not verifiable locally).
- **Build-time filters / transforms:** None (prebuilt).
- **Tippecanoe flags:** n/a (prebuilt; not run)
- **Styling (layers.yaml):** colour `#fb7185`, line_width `0.75`
- **UI filters (filterable_fields):** none declared
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: (no popup_labels; raw keys shown); footer in the prior deploy: unknown; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "Railroad Commission of Texas, pipeline layer (>20 in; prebuilt 2019 extract)"; `as_of` 2019
- **As-of date + evidence:** 2019 (layer inventory: "RRC 2019 prebuilt"; WIP archive: "7-year age acceptable").
- **Refresh cadence (upstream vs actual):** Upstream: RRC annual. Actual: frozen 2019.
- **Known caveats:** Seven years old. Not in git (`*.pmtiles` ignored). Colour `#fb7185` width 0.75, default off. Different from the four hifld_* pipeline layers (EIA/HIFLD). `source_date` is listed in yaml popup; if present in tile properties it would be hidden from the table by POPUP_HIDE_KEYS and used as the footer date.

## 2.9 Energy Infrastructure

### hifld_ng_pipelines

- **Label:** Natural Gas Pipelines (HIFLD/EIA)
- **Group / geometry / default / min zoom:** Energy Infrastructure / `line` / off / 0
- **Feature count:** 907 features (LineString x906, MultiLineString x1) = live 907
- **Purpose / thesis relevance:** Gas transmission routes serving Waha and the Permian: proximity of firm gas supply/laterals to Caramba North; separates Interstate (237) from Intrastate (670) carriers.
- **Storage:** standalone `data/hifld/hifld_ng_pipelines.geojson` (read directly; build.py:894)
- **Upstream source:** `services2.arcgis.com/FiaPA4ga0iQKduv3/.../Natural_Gas_Interstate_and_Intrastate_Pipelines_1/FeatureServer/0` (layers.yaml description; HIFLD/EIA, FEMA Region 6 mirror).
- **Acquisition / scripts:** `python3 scripts/fetch_hifld.py <slug> <FeatureServer URL>`: queries the FeatureServer with bbox `HIFLD_BBOX = (-104.0, 30.0, -101.0, 32.6)` (lon/lat), `inSR/outSR=4326`, paginates and writes `data/hifld/<slug>.geojson` (scripts/fetch_hifld.py:28-51). The bbox is a rectangle (not the 6 counties) and features that intersect it are kept whole, not clipped, so line extents run well outside the box.
- **Attributes carried:** `FID, TYPEPIPE, Operator, Status, Shape_Leng, Shape__Length`; `Status` is "Operating" on all 907.
- **Build-time filters / transforms:** Standalone GeoJSON; `-zg --simplification=8 --coalesce-densest-as-needed`.
- **Tippecanoe flags:** `-zg` `--simplification=8` `--coalesce-densest-as-needed`
- **Styling (layers.yaml):** colour `#fb923c`, line_width `0.75`
- **UI filters (filterable_fields):** `TYPEPIPE` (categorical, "Pipe type"); `Operator` (categorical, "Operator"; sort_by_count); `Status` (categorical, "Status")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `TYPEPIPE`->Pipe type, `Operator`->Operator, `Status`->Status; footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "HIFLD / U.S. EIA natural gas pipelines (FEMA Region 6 ArcGIS mirror)"; `as_of` 2026-05
- **As-of date + evidence:** 2026-05-13 fetch; EIA source vintage Not documented.
- **Refresh cadence (upstream vs actual):** Upstream: annual-ish. Actual: one fetch (quarterly recommended in refresh plan, never automated).
- **Known caveats:** Raw ArcGIS attributes (`FID`, `Shape_Leng`, `Shape__Length`) show in popups (generic dump). Feature bbox ~[-106.3, 27.7, -96.2, 33.0] (not clipped). Operator filter sorted by count. Crude and natural gas are separate layers (Grid Wire rule: never conflate, docs/settled.md).

### hifld_crude_pipelines

- **Label:** Crude Oil Trunk Pipelines (HIFLD/EIA)
- **Group / geometry / default / min zoom:** Energy Infrastructure / `line` / off / 0
- **Feature count:** 21 features (LineString x21) = live 21
- **Purpose / thesis relevance:** Crude trunk lines in the Delaware/Midland corridor (right-of-way and neighbouring-operator context).
- **Storage:** standalone `data/hifld/hifld_crude_pipelines.geojson` (read directly; build.py:894)
- **Upstream source:** `services2.arcgis.com/FiaPA4ga0iQKduv3/.../Crude_Oil_Trunk_Pipelines_1/FeatureServer/0`.
- **Acquisition / scripts:** `python3 scripts/fetch_hifld.py <slug> <FeatureServer URL>`: queries the FeatureServer with bbox `HIFLD_BBOX = (-104.0, 30.0, -101.0, 32.6)` (lon/lat), `inSR/outSR=4326`, paginates and writes `data/hifld/<slug>.geojson` (scripts/fetch_hifld.py:28-51). The bbox is a rectangle (not the 6 counties) and features that intersect it are kept whole, not clipped, so line extents run well outside the box.
- **Attributes carried:** `FID, Opername, Pipename, Shape_Leng, Shape__Length`.
- **Build-time filters / transforms:** Standalone; `-zg --simplification=8`.
- **Tippecanoe flags:** `-zg` `--simplification=8`
- **Styling (layers.yaml):** colour `#7f1d1d`, line_width `1`
- **UI filters (filterable_fields):** `Opername` (categorical, "Operator"; sort_by_count); `Pipename` (text, "Pipeline name")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `Pipename`->Pipeline name, `Opername`->Operator; footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "HIFLD / U.S. EIA crude oil trunk pipelines (FEMA Region 6 ArcGIS mirror)"; `as_of` 2026-05
- **As-of date + evidence:** 2026-05-13.
- **Refresh cadence (upstream vs actual):** Annual-ish upstream; one fetch.
- **Known caveats:** 21 LineStrings; bbox ~[-104.1, 27.6, -94.0, 36.0].

### hifld_hgl_pipelines

- **Label:** Hydrocarbon Gas Liquids Pipelines (HIFLD/EIA)
- **Group / geometry / default / min zoom:** Energy Infrastructure / `line` / off / 0
- **Feature count:** 15 features (LineString x14, MultiLineString x1) = live 15
- **Purpose / thesis relevance:** NGL/propane/butane/ethane lines (midstream context; Waha-area processing takeaway).
- **Storage:** standalone `data/hifld/hifld_hgl_pipelines.geojson` (read directly; build.py:894)
- **Upstream source:** `services2.arcgis.com/FiaPA4ga0iQKduv3/.../Hydrocarbon_Gas_Liquids_Pipelines_1/FeatureServer/0`.
- **Acquisition / scripts:** `python3 scripts/fetch_hifld.py <slug> <FeatureServer URL>`: queries the FeatureServer with bbox `HIFLD_BBOX = (-104.0, 30.0, -101.0, 32.6)` (lon/lat), `inSR/outSR=4326`, paginates and writes `data/hifld/<slug>.geojson` (scripts/fetch_hifld.py:28-51). The bbox is a rectangle (not the 6 counties) and features that intersect it are kept whole, not clipped, so line extents run well outside the box.
- **Attributes carried:** `FID, Opername, Pipename, Shape_Leng, Shape__Length`.
- **Build-time filters / transforms:** Standalone; `-zg --simplification=8`.
- **Tippecanoe flags:** `-zg` `--simplification=8`
- **Styling (layers.yaml):** colour `#a16207`, line_width `1`
- **UI filters (filterable_fields):** `Opername` (categorical, "Operator"; sort_by_count); `Pipename` (text, "Pipeline name")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `Pipename`->Pipeline name, `Opername`->Operator; footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "HIFLD / U.S. EIA hydrocarbon gas liquids pipelines (FEMA Region 6 ArcGIS mirror)"; `as_of` 2026-05
- **As-of date + evidence:** 2026-05-13.
- **Refresh cadence (upstream vs actual):** Annual-ish upstream; one fetch.
- **Known caveats:** 15 features (14 LineString, 1 MultiLineString). bbox extends to ~41.4 N (WY/CO) because lines are not clipped.

### hifld_ng_processing

- **Label:** Natural Gas Processing Plants (HIFLD/EIA)
- **Group / geometry / default / min zoom:** Energy Infrastructure / `point` / off / 0
- **Feature count:** 53 features (Point x53) = live 53
- **Purpose / thesis relevance:** Gas processing plants around Waha: where Permian associated gas is treated before it hits the hub; capacity (MMcfd) for gas-supply sizing.
- **Storage:** standalone `data/hifld/hifld_ng_processing.geojson` (read directly; build.py:894)
- **Upstream source:** `services2.arcgis.com/ZOdjAzAQ2B0f85zi/.../NaturalGas_ProcessingPlants_US_EIA/FeatureServer/0` (EIA-757 survey; HIFLD-equivalent).
- **Acquisition / scripts:** `python3 scripts/fetch_hifld.py <slug> <FeatureServer URL>`: queries the FeatureServer with bbox `HIFLD_BBOX = (-104.0, 30.0, -101.0, 32.6)` (lon/lat), `inSR/outSR=4326`, paginates and writes `data/hifld/<slug>.geojson` (scripts/fetch_hifld.py:28-51). The bbox is a rectangle (not the 6 counties) and features that intersect it are kept whole, not clipped, so line extents run well outside the box.
- **Attributes carried:** `FID, Plant_Name, Owner, Operator, City, State, County, ZipCode, Period, Cap_MMcfd, Plant_Flow, BTU_Conten, Dry_Stor, NGL_Stor, Longitude, Latitude, Source`.
- **Build-time filters / transforms:** Standalone; `-Z0 -z14`. Capital-S `Source` property is displayed as a normal row (POPUP_HIDE_KEYS only hides lowercase `source`).
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#15803d`, radius `6`, stroke_width `1.5`
- **UI filters (filterable_fields):** `County` (categorical, "County"); `Operator` (categorical, "Operator"; sort_by_count); `Owner` (categorical, "Owner"; sort_by_count); `Cap_MMcfd` (numeric, "Capacity (MMcfd)"); `Period` (numeric, "Reporting year")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `Plant_Name`->Plant, `Owner`->Owner, `Operator`->Operator, `County`->County, `City`->City, `Cap_MMcfd`->Capacity (MMcfd), `Plant_Flow`->Plant flow (MMcfd), `Period`->Reporting year; footer in the prior deploy: no (capital-S `Source` row only); footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "HIFLD / U.S. EIA natural gas processing plants (ArcGIS Online)"; `as_of` 2026-05
- **As-of date + evidence:** `Period = 2017` on all 53 features (reporting year) - the data is a 2017 EIA-757 vintage even though the fetch was 2026-05; the yaml `as_of: 2026-05` is the fetch month.
- **Refresh cadence (upstream vs actual):** EIA-757 periodic; one fetch.
- **Known caveats:** 53 plants, bbox ~[-103.9, 30.5, -101.2, 32.5]. Feeds oxy_midstream (Block 31 point source). Plant status (operating/retired) is not in the attributes.

## 2.10 Permits

### tceq_gas_turbines

- **Label:** Gas Turbine Air Permits (TCEQ, recent filings)
- **Group / geometry / default / min zoom:** Permits / `point` / off / 0
- **Feature count:** 18 rows (live registry 18) (prior deploy 13)
- **Purpose / thesis relevance:** Behind-the-meter / merchant gas-turbine air permits (>=20 MW) in the West Texas county set - the leading indicator of captive gas power for data-center campuses (Poolside LF Phase 2 at Fort Stockton, Featherwood, CPV Basic Ranch) competing for Waha gas.
- **Storage:** `combined_points.csv` (layer_id = `tceq_gas_turbines`), split to NDJSON at build (build.py:314)
- **Upstream source:** `https://www.tceq.texas.gov/downloads/permitting/air/memos/turbine-lst.xlsx` (sheets "Issued Turbine Air Permits" and "Pending Turbine Air Permits"; source version v2026.10.7 live, v2026.4.3 in the prior deploy).
- **Acquisition / scripts:** `python scripts/refresh_tceq_gas_turbines.py` (3cf3581 added an optional xlsx path arg) -> `outputs/refresh/tceq_gas_turbines_<date>.csv`; geocode by OpenStreetMap Nominatim `{city}, {county} County, Texas, USA`, 1.1 s throttle (Census geocoder returned 0/6). Scope: 23-county West Texas set, Received year >= 2020. outputs/refresh/CHANGELOG.md.
- **Attributes carried:** combined_points.csv columns populated at HEAD (non-blank rows of 18): `name` (18), `plant_code` (18), `county` (18), `technology` (18), `fuel` (18), `mw` (18), `zone` (18), `entity` (18), `funnel_stage` (18), `commissioned` (13), `capacity_mw` (18), `operator` (18), `project` (18), `manu` (18), `model` (18), `year` (18)
- **Build-time filters / transforms:** `-Z0 -z14`; none of the build-time filters.
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#f0abfc`, radius `7`, stroke_width `2`
- **UI filters (filterable_fields):** `county` (categorical, "County"); `technology` (categorical, "Mode"); `manu` (categorical, "Manufacturer"); `operator` (categorical, "Operator"); `funnel_stage` (categorical, "Status"); `capacity_mw` (numeric, "Project MW"); `year` (numeric, "Received year")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Project, `entity`->Company, `operator`->Operator, `county`->County, `capacity_mw`->Project MW, `mw`->Project MW (alt), `technology`->Mode, `fuel`->Fuel, `manu`->Manufacturer, `model`->Turbine model, `project`->Number of CTs, `funnel_stage`->Status, `zone`->Received date, `commissioned`->Issue date, `year`->Received year, `plant_code`->Permit No.; footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "TCEQ, Issued Turbine Air Permits list (turbine-lst.xlsx)"; `as_of` 2026-10-12
- **2026-10-21 refresh note:** Refreshed 2026-10-21 (commit 3cf3581, live since deploy 6ad88eb4): 13 -> 18 rows; turbine-lst v2026.10.7 (yaml as_of 2026-10-12); `refresh_tceq_gas_turbines.py` accepts an xlsx path.
- **As-of date + evidence:** Live (3cf3581): 18 rows from turbine-lst v2026.10.7 (yaml as_of 2026-10-12). Prior deploy: 13 rows from v2026.4.3 (CHANGELOG records only the initial 6 of 2026-04-23).
- **Refresh cadence (upstream vs actual):** Per TCEQ filing (monthly suggested); manual.
- **Known caveats:** GEOCODE PRECISION: municipality/community centroid (Nominatim city + county), NOT a site coordinate - there is no `accuracy` field. `mw` and `capacity_mw` duplicate; `project` holds number of CTs (some multi-line values); `zone` holds the Received date (ISO), `commissioned` the Issue date, `plant_code` the TCEQ Permit No. (field overload, popup labels remap). Pre-2020 grandfathered permits excluded (CHANGELOG lists them). Status counts now: issued: 9, pending: 5, renewed: 4; counties: Reeves: 5, Ward: 3, Ector: 3, Upton: 2, Winkler: 2, Martin: 1, Pecos: 1, Reagan: 1; received year: 2025: 9, 2024: 5, 2026: 4.

### permits_permian6

- **Label:** Permits (RRC W-1, 6-county Permian)
- **Group / geometry / default / min zoom:** Permits / `point` / off / 6 / sidebar-hidden (`sidebar_omit`)
- **Feature count:** 33,179 live (registry/tilestats only; source not present in this checkout) (prior deploy 28,842)
- **Purpose / thesis relevance:** Forward-looking drilling activity: approved W-1 permits for subject (Pecos, Reeves, Ward) vs peer (Midland, Martin, Reagan) counties - the sale-area-vs-boom-area contrast and a leading indicator for any drilling near Caramba (depth-scaled symbols make "deep, remote" visible).
- **Storage:** standalone `data/permits_permian6.csv` (read directly; build.py:894)
- **Upstream source:** RRC "Drilling Permit EOM + Lat/Lon" (`daf420.dat.MM-DD-YYYY`), GoAnywhere MFT folder `https://mft.rrc.texas.gov/link/f5dfea9c-…` (monthly). Layout unpublished; reverse-engineered in docs/rrc_layouts/permit_purpose_codes.md. Planned 1976-2017 backfill: W-1 JSP scrape `https://webapps.rrc.state.tx.us/DP/initializePublicQueryAction.do` (scripts/scrape_rrc_w1.py + scrape_rrc_w1_detail_coords.py, ~7 h throttled).
- **Acquisition / scripts:** `python3 scripts/fetch_rrc.py permits` then `python3 scripts/parse_rrc.py permits` (6-county FIPS filter 317/329/371/383/389/475; Texas-county from master-id last 3 digits; lat/lon from records 14/15) -> `data/permits_permian6.csv` (gitignored, absent here). `parse_rrc.py` appends/merges the W-1 backfill CSV when present (dedup by permit_no + api_no). NOTE `build.py refresh permits` exits 2 with a stale "scoped-out" message - use the scripts.
- **Attributes carried:** CSV: `layer_id, permit_no, status_no, api_no, county_fips, county_name, county_role (subject|peer), district, lease_name, well_no, operator_name, submitted_date, approved_date, permit_year, status, wellbore_profile, filing_purpose, oil_gas, total_depth, lat, lon`.
- **Build-time filters / transforms:** `-zg -r1 --drop-densest-as-needed --extend-zooms-if-still-dropping`; `min_zoom 6`; depth sizing 3->8.5 px; oil/gas colour split. Parser drops permits without parseable `total_depth` (R2-2) and without lat/lon. `STATS_ATTRS_FIELDS` emits `dist/data/permits_permian6.json` for the stats panel/scrubber (time field `permit_year`).
- **Tippecanoe flags:** `-zg` `-r1` `--drop-densest-as-needed` `--extend-zooms-if-still-dropping`
- **Styling (layers.yaml):** colour `#dc2626`, radius `3`
- **UI filters (filterable_fields):** `county_name` (categorical, "County"); `county_role` (categorical, "Role (subject/peer)"); `wellbore_profile` (categorical, "Wellbore profile"); `status` (categorical, "Status"); `oil_gas` (categorical, "Oil/Gas"); `district` (categorical, "District"); `total_depth` (numeric, "Total depth (ft)"; quick_presets); `permit_year` (numeric, "Permit year (1976-present once Round 2.5 backfill ships; 2018-present today)"; quick_presets); `operator_name` (text, "Operator"; sort_by_count)
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `permit_no`->Permit, `api_no`->API, `county_name`->County, `county_role`->Role, `district`->District, `lease_name`->Lease, `well_no`->Well, `operator_name`->Operator, `submitted_date`->Submitted, `approved_date`->Approved, `permit_year`->Year, `status`->Status, `wellbore_profile`->Wellbore profile, `filing_purpose`->Filing purpose code, `oil_gas`->Oil/Gas, `total_depth`->Total depth (ft); footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "Railroad Commission of Texas, Drilling Permit Master + Lat/Lon (daf420 EOM monthly snapshots)"; `as_of` 2026-09-30
- **2026-10-21 refresh note:** Refreshed 2026-10-21 (commit 3cf3581, live since deploy 6ad88eb4): 28,842 -> 33,179 rows from 110 EOM snapshots through 2026-09-30 (rows with coordinates through 2026-03-31); `parse_rrc.py` now reads 0109/0209 master/detail and 27/28-byte location records (2024+ format, previously dropped) and the approved_date offset was corrected 120 -> 119 (previously garbage); yaml as_of 2026-09-30.
- **As-of date + evidence:** Live (3cf3581; CHANGELOG 2026-10-21): 110 EOM snapshots through 2026-09-30; rows with coordinates through 2026-03-31; yaml as_of 2026-09-30. Prior deploy: 28,842 rows (EOM Jan 2018-Dec 2025, 2026-05-13). Backfill to 1976 still deferred.
- **Refresh cadence (upstream vs actual):** Upstream monthly EOM; actual manual (refresh plan proposes weekly probe, never implemented).
- **Known caveats:** SIDEBAR-HIDDEN (`sidebar_omit`) - reachable only via URL `#layers=` or the scrubber/stats; superseded visually by wells_permian6. `oil_gas` is derived from the unverified `filing_purpose` code and is often "unknown" (template comment build_template.html:615). Prior deploy: 0 resolved filter fields and no stats side-car (Known Defect #1); fixed by the 2026-10-21 deploy (9 filter fields, side-car with 33,179 rows). `oil_gas` filter, `filing_purpose` codes X/E/P/3 are tentative (permit_purpose_codes.md).

### tax_abatements

- **Label:** Approved Tax Abatements (Local / Ch.381 + Ch.312)
- **Group / geometry / default / min zoom:** Permits / `point` / off / 0
- **Feature count:** 9 served (1,425 rows in the CSV; prior deploy served 9 of 1,495)
- **Purpose / thesis relevance:** Local tax-abatement / Ch.381 economic-development agreements - the leading local signal that a large load or generator is coming to a county (Pecos/Reeves abatements tied to Poolside/CoreWeave and gas projects).
- **Storage:** `combined_points.csv` (layer_id = `tax_abatements`), split to NDJSON at build (build.py:314)
- **Upstream source:** (a) Comptroller LDAD: `https://api.comptroller.texas.gov/open-data/v1/tables/ch312-abatement?limit=10000` (live: 1,416 statewide records, API lastUpdated 2026-10-10; prior deploy: 1,486 from 2026-04-29). (b) 9 hand-curated Pecos/Reeves commissioners-court rows (`data/abatements_court_seed.csv`; agendas `https://www.co.pecos.tx.us/category/notices-announcements/commissioners-court-agendas/` and `https://www.reevescounty.org`, the latter Akamai-blocked from cloud runners).
- **Acquisition / scripts:** `python3 scripts/scrape_ldad.py` (JSON -> `outputs/refresh/comptroller_ldad_<date>.csv`; coords = TIGER county centroid, `coords_source = ldad_county_centroid`) then `python3 scripts/transform_ldad.py` (drops prior centroid rows, keeps `commissioner_court` rows, dedupes against the seed, coerces `1900-01-01` placeholders to blank, atomic write). Court-agenda path: scripts/scrape_abatements.py (Pecos WordPress + Reeves CivicEngage adapters validated; 21 other counties stubs) -> transform_abatements.py.
- **Attributes carried:** Overloaded columns (ARCHITECTURE.md §4): `inr` <- agreement/permit id, `funnel_stage` <- "{agmt_type}|{status}|flags", `zone` <- received date, `project` <- reinvestment zone, `poi` <- agenda/detail URL, `operator` <- applicant, `entity` <- taxing unit, `commissioned` <- approved/meeting date, `technology` <- project type (only the 9 court rows), `coords_source`.
- **Build-time filters / transforms:** `keep_technology: [natural_gas, renewable]` + `keep_county_scope` whitelist (Pecos, Reeves, Ward, Midland, Martin, Reagan) via `_filter_tax_keep` (build.py:669): a row is kept if its technology is gas/renewable OR its county is in the six; derived `status` = first token of `funnel_stage`. EFFECT (live): of 1,425 rows 9 are tiled (the commissioners-court rows; every LDAD row has blank `technology` and none lies in the six counties). The full 1,423-row index still feeds the facility fuzzy join (annotating matched plants/queue rows/solar/batteries).
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#ef4444`, radius `7`, stroke_width `2`
- **UI filters (filterable_fields):** `county` (categorical, "County"); `technology` (categorical, "Project type"); `commissioned` (date_range, "Approved date"); `mw` (numeric, "Project MW"); `capacity` (numeric, "Capex ($M)")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Applicant, `operator`->Applicant (alt), `county`->County, `commissioned`->Approved date, `funnel_stage`->Status, `technology`->Project type, `mw`->Project MW, `capacity`->Capex ($M), `use`->Abatement schedule, `sector`->Taxing entities, `project`->Reinvestment zone, `poi`->Agenda URL; footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "Texas Comptroller LDAD (Ch. 312 abatement open-data) and county commissioners-court agendas"; `as_of` 2026-10-10
- **2026-10-21 refresh note:** Refreshed 2026-10-21 (commit 3cf3581, live since deploy 6ad88eb4), LDAD refresh via transform_ldad.py: 1,495 -> 1,425 CSV rows (1,416 LDAD + 9 seed), LDAD API lastUpdated 2026-10-10 (yaml description now says 1,416 statewide LDAD records). The tiled set stays the 9 court-seed rows under the unchanged build filter (inference).
- **As-of date + evidence:** Live (3cf3581): LDAD API lastUpdated 2026-10-10 (yaml as_of 2026-10-10); court seed 2026-04-24 (data/abatements/abatement_hits_20260424_092810.csv, pinned). Prior deploy: LDAD 2026-04-29.
- **Refresh cadence (upstream vs actual):** Planned weekly (never automated); actual manual. Daily-refresh routine logs end 2026-08-19 (external).
- **Known caveats:** (1) Served count = 9 (same as the prior deploy), not the 1,425 in the CSV (the sidebar count shows the served number). (2) The layer description still says "6-county Permian scope: 5 records, all Ch.381" but 9 are served (funnel_stage: abatement|renewable: 2, abatement|renewable|load:CoreWeave: 1, abatement: 1, abatement|renewable|load:Poolside: 1, zone_creation: 1, abatement|gas|capex:150-200M: 1, relationship_signal: 1, abatement|gas|midstream|capex:50M: 1). (3) 1,416 of the 1,425 rows are at county centroids (`ldad_county_centroid`) - not site-precise even if they were shown. (4) Provenance of the 9 court-row coordinates: Not documented in repo beyond "curated coords" (transform_ldad.py). (5) Chapter 313 successors and Ch.312 (city-level) are not separately mapped; Comptroller Ch.312 API returned 0 in-scope records (ARCHITECTURE.md §7).

## 2.11 Oil & Gas Spud Wells

### wells_permian6

- **Label:** Wells — new drilling (1964-present)
- **Group / geometry / default / min zoom:** Oil & Gas Spud Wells / `point` / off / 7
- **Feature count:** 35,355 live (registry/tilestats only; source not present in this checkout) (prior deploy 35,081)
- **Purpose / thesis relevance:** The drilling-vibration thesis in map form: every RRC wellbore in the six-county scope (subject Pecos/Reeves/Ward vs peer Midland/Martin/Reagan), filtered to genuine new drilling, with plug and production status. Supports the finding that new drilling is deep and remote from Caramba and that shallow wells near the site are decades-old, mostly plugged.
- **Storage:** standalone `data/wells_permian6.csv` (read directly; build.py:894)
- **Upstream source:** RRC "Full Wellbore" ASCII `dbf900.txt.gz` (~366 MB compressed, ~1.97 GB raw; 247-byte records, segments 01 WBROOT, 02 WBCOMPL, 03 WBDATE, 13 WBNEWLOC) from GoAnywhere MFT folder `https://mft.rrc.texas.gov/link/b070ce28-…` (weekly). Layout: docs/rrc_layouts/wba091_well-bore-database.pdf. Production join: RRC PDQ dump `https://mft.rrc.texas.gov/link/1f5ddb8d-329a-4459-b7f8-177b4f5ee60d` (`PDQ_DSV.zip`, ~3.44 GB, monthly last Saturday).
- **Acquisition / scripts:** `python3 build.py refresh wells` = `scripts/fetch_rrc.py wells` (PrimeFaces GoAnywhere POST protocol -> `data/rrc_raw/dbf900.txt.gz`) + `scripts/parse_rrc.py wells` -> `data/wells_permian6.csv` (gitignored, absent here), then `python3 build.py`. Production status: `scripts/fetch_pdq_dump.py` -> `scripts/build_lease_status.py` (`data/lease_status.csv`) -> `scripts/build_well_prod_status.py` (`data/well_prod_status.csv`, api8 -> trailing-6-month gas/oil).
- **Attributes carried:** CSV: `layer_id, api_no, county_fips, county_name, county_role, district, well_no, lease_no, oil_gas, total_depth, completion_date, completion_year, spud_date, spud_year, newest_permit_no, plug_flag, active_flag, lat, lon` + build-derived `well_status`.
- **Build-time filters / transforms:** yaml keys `min_spud_year: 1964` (drop null/<1964 spud_year), `exclude_recompletions: true` (drop completion_year < spud_year; this is RULE H "genuine new drill" = completion_year blank OR >= spud_year), `reclassify_inactive_production: true` (derive `well_status`: Plugged if plug_flag=Y; "Marginal or end-of-life" if trailing-6-mo gas <= 125 Mcf/d AND oil <= 25 bbl/d by 8-digit API join to well_prod_status.csv, ~99.6% of non-plugged wells match; else Active). `exclude_within` (point-in-polygon vs a polygon layer, e.g. caramba_north; -9 wells) is implemented in build.py:531 and WIP_OPEN says it shipped 2026-05-18, but the current layers.yaml has NO `exclude_within` key. Tippecanoe `-zg -r1 --drop-densest-as-needed --extend-zooms-if-still-dropping`, `min_zoom 7`. `write_stats_attrs` emits `dist/data/wells_permian6.json` (stats panel, scrubber, Wells summary, PDF export).
- **Tippecanoe flags:** `-zg` `-r1` `--drop-densest-as-needed` `--extend-zooms-if-still-dropping`
- **Styling (layers.yaml):** colour `#6b21a8`, radius `2`
- **UI filters (filterable_fields):** `well_status` (categorical, "Well status"); `county_name` (categorical, "County"); `oil_gas` (categorical, "Oil/Gas"); `district` (categorical, "District"); `plug_flag` (categorical, "Plug status"; value_labels); `total_depth` (numeric, "Total depth (ft)"; quick_presets); `spud_year` (categorical, "Spud year (multi-select)"; group_presets); `spud_date` (date_range, "Spud date"); `completion_date` (date_range, "Completion date")
- **Saved views:** the 12 `spud_*` saved views set this layer's `county_name` + `total_depth` filters and show only this layer (build_template.html:2582)
- **Popup:** generic full-attribute dump (G1); labels: `api_no`->API, `county_name`->County, `county_role`->Role, `district`->District, `well_no`->Well, `lease_no`->Lease, `oil_gas`->Oil/Gas, `total_depth`->Total depth (ft), `completion_date`->Completion date, `newest_permit_no`->Newest drilling permit, `plug_flag`->Plug status, `active_flag`->Active flag, `well_status`->Status (production-based); footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "Railroad Commission of Texas, Full Wellbore ASCII (dbf900)"; `as_of` 2026-10-21
- **2026-10-21 refresh note:** Refreshed 2026-10-21 (commit 3cf3581, live since deploy 6ad88eb4): parsed 99,808 -> 100,220 rows; mapped 35,198 (2026-08-19 run) -> 35,355 after the filters (spud max 2026-09-24); standalone gitignored CSV, no merge; yaml as_of 2026-10-21. Deployed registry still shows 35,081.
- **As-of date + evidence:** Live (3cf3581; CHANGELOG 2026-10-21): 100,220 wellbores parsed, 35,355 mapped, spud max 2026-09-24, yaml as_of 2026-10-21. Earlier: 99,224 -> 99,808 rows (re-fetched 2026-08-19, CARAMBA-OM-REBUILD-NOTES.md). Prior deploy registry: 35,081.
- **Refresh cadence (upstream vs actual):** Upstream weekly; actual manual (2026-05-13, 2026-08-19, 2026-10-21; the Monday cron in docs/refresh_automation_plan.md was never built).
- **Known caveats:** (1) `spud_date`/`spud_year` come from the WBDATE segment byte-32 field `WB-W2-G1-DATE`, i.e. the W-2/G-1 completion-form filing date, deliberately treated as spud by operator instruction R2-6 (parse_rrc.py `parse_wbdate`). (2) RULE H boundary: RRC re-stamped two 2025 Mongoose "Viper" wells to spud 2026 / completion 2025 (6.94/6.95 mi from the tract) so RULE H now drops them; open decision whether to treat `spud_year - completion_year <= 1` as a paperwork boundary (WIP_OPEN.md backlog 3; OM rebuild notes §3). (3) lease_status.csv docstring says oil < 150 bbl/d but build.py/OM use <= 25 bbl/d (build.py is authoritative). (4) Lat/lon: dbf900 longitude is stored positive; parser forces negative and bounds lat 25-38 / |lon| 93-107.5. (5) Popup hides `completion_year`; `plug_flag` shown as "Plugged / Abandoned"/"Active". (6) The prior deploy showed 0 resolved filter fields and lacked the stats/scrubber side-car (Known Defect #1); the 2026-10-21 deploy has 9 filter fields and the side-car (35,355 rows). (7) Marker: black centre = plugged (ring in oil/gas colour), grey 50% = marginal, solid oil(green)/gas(red) = active; radius ramps 2.5 -> 8 px over zoom 7-14.

## 2.12 Projects

### ercot_queue

- **Label:** ERCOT Interconnect Queue (GIS Report, Sep 2026)
- **Group / geometry / default / min zoom:** Projects / `point` / off / 0
- **Feature count:** 1,754 rows (live registry 1,754) (prior deploy 1,778)
- **Purpose / thesis relevance:** Who is trying to interconnect where: statewide queue by fuel/stage/zone; the demand-and-competition read for West zone, Solstice-area POIs and the BESS/solar glut that shapes a data-center site's grid timeline.
- **Storage:** `combined_points.csv` (layer_id = `ercot_queue`), split to NDJSON at build (build.py:314)
- **Upstream source:** ERCOT MIS report type 15933 "GIS Report": doc list `https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=15933`, download `https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>`; Live = `GIS_Report_September2026` (DocID 1281327706, published 2026-10-01), sheet "Project Details - Large Gen". Prior deploy = the March-2026 report (docs/refresh_automation_plan.md §3 lists the monthly-gis-reports landing page).
- **Acquisition / scripts:** `python3 scripts/refresh_ercot_queue.py` (new at 3cf3581; fetch -> parse -> column map -> geocode -> merge-ready CSV, does not touch combined_points.csv) then `python3 build.py merge ercot_queue outputs/refresh/ercot_queue_<date>.csv`. Derived fields: `under_construction`, `commissioned` (approved for sync <= publish date), `funnel_stage` 1_no_ia..5_commissioned, `group` (carried forward by INR else best-effort `<NAME TOKEN>__<COUNTY>`; original keying logic not in repo). Coordinates: (1) INR already present with the same county -> carry lat/lon + `coords_source` forward; (2) new INR -> geocode_ercot_queue.py Stage 1 (EIA-860/USWTDB name+county fuzzy) and Stage 2 (TPIT POI, OSM-substation POI, dc_anchors alias; WRatio >= 88); (3) else TIGER-2024 county centroid + deterministic +/-0.02 deg jitter keyed on INR (`county_centroid`). Other post-processors: scripts/enrich_ercot_coords.py (abatement cross-reference -> `abatement_match`), scripts/enrich_ercot_substation_match.py (`substation_match`). Stage 3 (`manual_override`) is still blocked on operator CSV `data/ercot_queue_overrides.csv` (WIP_OPEN.md Active sprints). Run meta: outputs/refresh/ercot_queue_2026-10-21.meta.json (1,567 rows carried forward, 187 newly geocoded; fuels GAS/NUC/OTH/SOL/WIN).
- **Attributes carried:** combined_points.csv columns populated at HEAD (non-blank rows of 1,754): `name` (1,754), `county` (1,754), `technology` (1,754), `inr` (1,754), `fuel` (1,754), `mw` (1,680), `zone` (1,754), `poi` (1,754), `entity` (1,754), `funnel_stage` (1,754), `group` (1,754), `under_construction` (1,754), `commissioned` (1,754), `capacity_mw` (1,680), `coords_source` (1,754)
- **Build-time filters / transforms:** `compute_ercot_group_aggregates` stamps `group_total_mw`, `group_count`, `group_breakdown` on every row (1,177 groups, 390 with 2+ components); abatement fuzzy join annotates 26 rows. Tippecanoe `-zg`. Colour by technology: GT/CC/IC/ST amber `#f59e0b`, PV `#eab308`, WT `#84cc16`, BA `#dc2626`, other `#64748b`; sidebar swatch is a 5-colour gradient; sizing by `capacity_mw`.
- **Tippecanoe flags:** `-zg`
- **Styling (layers.yaml):** colour `#ec4899`, radius `5`
- **UI filters (filterable_fields):** `mw` (numeric, "MW"); `fuel` (categorical, "Fuel"); `technology` (categorical, "Technology"); `zone` (categorical, "ERCOT zone"); `funnel_stage` (categorical, "Funnel stage"); `commissioned` (categorical, "Commissioned (Y/N)"); `under_construction` (categorical, "Under construction"); `county` (categorical, "County"); `entity` (text, "Developer"); `name` (text, "Project")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: (no popup_labels; raw keys shown); footer in the prior deploy: no; footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "ERCOT GIS Report (Generation Interconnection Status), September 2026, published 2026-10-01; LRP geocoding"; `as_of` 2026-10-01
- **2026-10-21 refresh note:** Refreshed 2026-10-21 (commit 3cf3581, live since deploy 6ad88eb4): layer replaced from the March-2026 report (1,778 rows) with the September 2026 report (1,754 rows) via the new scripts/refresh_ercot_queue.py; yaml label/source/as_of changed accordingly.
- **As-of date + evidence:** Live (3cf3581): Sep 2026 GIS Report, published 2026-10-01, fetched 2026-10-21 (yaml label "ERCOT Interconnect Queue (GIS Report, Sep 2026)", as_of 2026-10-01). Prior deploy: March-2026 report (the new script's docstring: column map "validated against the March-2026 report == existing layer"), although the prior label said 2026-04-21 (layer inventory 2026-04-28; refresh plan 2026-04-25).
- **Refresh cadence (upstream vs actual):** Upstream monthly (mid-month). Actual: refreshed once 2026-10-21 by the new fetcher; no schedule/automation.
- **Known caveats:** GEOCODE MATCH RATES (live): 1,301 of 1,754 rows (74.2%) remain at `county_centroid`; non-centroid 453 = eia860 290, tpit_poi 85, substation_poi 69, uswtdb 9 (prior March data: 1,299/1,778 = 73.1% centroid; eia860 324, tpit_poi 78, substation_poi 67, uswtdb 10). Pre-refresh log (outputs/refresh/_geocode_ercot_log.txt): solar+wind+battery match rate Stage 1 18.4%, Stage 1+2 27.0% (452/1,676). No `abatement_match`/`substation_match`/`manual_override` rows exist yet. County-centroid points are NOT sites (the refresh script reproduces a +/-0.02 deg deterministic jitter). `capacity_mw` ranges -53.3–3000 (74 blank; non-positive values fall back to the static radius). `funnel_stage` now: 1_no_ia: 1,143, 2_ia_fis_pending: 267, 3_ia_fis_complete: 209, 5_commissioned: 111, 4_construction: 24. Technology now: BA: 846, PV: 609, WT: 159, GT: 54, CC: 45, IC: 32, ST: 5, OT: 4. Purpose-built popup HTML (`ercotQueuePopupHtml`, group summary) is dead code; the generic popup dumps raw keys incl. `coords_source`, `group_*`, `abatement_*`.

### dc_anchors

- **Label:** Datacenter Anchors (≥100 MW)
- **Group / geometry / default / min zoom:** Projects / `point` / off / 0
- **Feature count:** 8 entries = live 8
- **Purpose / thesis relevance:** Large (>=100 MW) Texas data-center/AI campus anchors - the demand-side comparables (Stargate Abilene, Project Matador, Longfellow, GW Ranch...) for sizing how much load competes for Waha gas, Solstice capacity and Pecos land.
- **Storage:** standalone `data/datacenters/dc_anchors.json` (read directly; build.py:894)
- **Upstream source:** Per-entry `sources[].url` (permits, SEC filings, ERCOT INR, tier-1 trade press; quality ranking in data/datacenters/README.md).
- **Acquisition / scripts:** Hand-curated `data/datacenters/dc_anchors.json`. `scripts/refresh_dc_anchors.py` (Anthropic API fact-check proposer) runs in `.github/workflows/dc-anchors-refresh.yml` every Monday 06:00 UTC, writes `outputs/refresh/dc_anchors_proposed.json` and opens a proposal PR; never auto-merged (~14 unmerged PRs per OPERATING_MANUAL.md). Coordinates are never proposed by the script.
- **Attributes carried:** JSON entry: `id, name, developer, county, lat, lon, coord_accuracy (precise|approximate|county_centroid), status, capacity_mw_announced, commissioned_target, power_source, sources[]`; loader adds `sources_count`, `sources_urls`.
- **Build-time filters / transforms:** `dc_anchors_to_ndgeojson` (build.py:693); `-Z0 -z14`; colour by `status` (announced slate, permitted amber, under_construction blue, operational green, other slate); opacity 0.45 when `coord_accuracy = county_centroid` else 0.9; sizing by `capacity_mw_announced`.
- **Tippecanoe flags:** `-Z0` `-z14`
- **Styling (layers.yaml):** colour `#fbbf24`, radius `7`, stroke_width `1.5`
- **UI filters (filterable_fields):** `status` (categorical, "Status"); `county` (categorical, "County"); `capacity_mw_announced` (numeric, "Capacity (MW)"); `developer` (text, "Developer"); `name` (text, "Project")
- **Saved views:** none
- **Popup:** generic full-attribute dump (G1); labels: `name`->Project, `developer`->Developer, `county`->County, `status`->Status, `capacity_mw_announced`->Announced capacity (MW), `commissioned_target`->Target commissioning, `power_source`->Power source / notes, `coord_accuracy`->Coord accuracy, `sources_count`->Sources, `sources_urls`->Source URLs; footer in the prior deploy: no (URLs in `sources_urls` row); footer now (live): feature `source`/`source_date`, else the layer-level yaml source + 'as of' below (G3)
- **Layer-level `source` / `as_of` (layers.yaml):** "LRP-curated datacenter anchor index from public announcements and filings"; `as_of` 2026-04-25
- **As-of date + evidence:** `generated: 2026-04-25`; 8 entries (WIP_OPEN.md: missing Chevron WTPP, TPL+Bolt JV, LandBridge Alpha Digital, Longfellow cluster; holds OM section 7 at 9.7 GW vs ~25 GW).
- **Refresh cadence (upstream vs actual):** Weekly proposals (CI succeeding); actual merges: none since 2026-04-25.
- **Known caveats:** 8 entries: status operational 2, under_construction 4, permitted 1, "seeking anchor tenant / phase 1 construction" 1 (not in the colour match, falls to slate); coord_accuracy approximate 6, county_centroid 2; counties Pecos 2, Taylor 2, Carson, Shackelford, Milam, Bell; capacity 198-11,000 MW. Only 2 in Pecos County and 2 within ~60 mi. Several entries have `commissioned_target` 2025-2027 that may already be past. Source accessed dates run to 2026-08-23 although `generated` was not bumped.


---

## 3. Orphan / unserved datasets and other data assets

### 3.1 Orphans: present in the combined files but not in `layers.yaml` (not tiled, not served)

`build.py` still splits them into `/tmp/gis_build/split/<id>.ndjson` (no PMTiles are produced), so they cost build time only. The template `ICON_MAP` still has a `wells: 'well'` key for the removed TWDB layer.

| asset | location | what it is | size / shape | producer | consumers |
|---|---|---|---|---|---|
| `wells` (TWDB groundwater wells) | `combined_points.csv` layer_id `wells` | Texas Water Development Board Groundwater Database wells (ARCHITECTURE.md §5: "TWDB Groundwater, quarterly"); earlier sidebar label "Groundwater Wells (TWDB)" (docs/archive/wip_log_pre_chat83.md:258) | 14,700 rows; columns `name` (14,700), `county` (28 distinct), `depth_ft` (11,125 populated, 5-17,876 ft), `use` (21 distinct), `aquifer` (26 distinct); bbox ~[-104.65, 29.13, -100.80, 32.30] | Chat-era TWDB fetch; no script in repo | none in build; `ICON_MAP.wells` stale. Why removed from yaml: Not documented in repo |
| `aquifers` | `combined_geoms.geojson` layer_id `aquifers` | TWDB Major (2) + Minor (3) aquifer polygons: Edwards-Trinity (Plateau), Pecos Valley (major); Rustler, Dockum, Capitan Reef Complex (minor) | 5 features (3 MultiPolygon, 2 Polygon; 22,000+ vertices); props `name`, `source`; the bboxes of Edwards-Trinity, Pecos Valley, Rustler and Capitan Reef each contain the Caramba tract (bbox-level only; not an intersection test) | chat-era TWDB ArcGIS pull; dropped from yaml in Chat ~51 ("drop aquifers layer", wip_log_pre_chat83.md:632) | scripts/oxy_assets_data.py; OXY report. Water-thesis relevance: the only aquifer geometry in the repo |
| `caramba_south` | `combined_geoms.geojson` | AgriWebb paddock "Caramba Farms South" (same export as caramba_north, 2023-02-01) | 1 Polygon, bbox ~[-103.05, 30.87, -102.99, 30.90]; 58 export keys | AgriWebb export; removed from yaml in the filter-UI refinement ("caramba_south deleted 22->21") | scripts/build_vector_maps.py, scripts/extract_map_geometry.py (OM exhibits) |
| `water_mains_approx` | `combined_geoms.geojson` | 3 hand-traced water mains: "hand-traced from public CRMWD service maps", "approximated from FSH-Midland public filings", "approximated from district service area"; all `accuracy = APPROXIMATE` | 3 LineStrings; props `name, operator, accuracy, source`; bbox ~[-102.90, 30.86, -101.17, 32.60] | hand-digitized (Chat 43 batch) | scripts/extract_map_geometry.py -> `outputs/reports/om_exhibits/map_geometry.json` |
| `drilling_permit_density` | `combined_geoms.geojson` | County polygons carrying W-1 permit counts and permits per sq mi over all-time / 20 / 10 / 5-year windows (all, 2006+, 2016+, 2021+) | 11 Polygons (Pecos, Reeves, Ward, Loving, Winkler, Culberson, Crane, Upton, Reagan, Crockett, Terrell); `source = RRC W-1 Public Query`, `source_date 2026-04-30` | scripts/build_drilling_density.py (reads gitignored `outputs/refresh/rrc_w1_counts.csv`; geodesic area via pyproj) | none (never given a yaml entry; related archived scaffolding `docs/archive/chat127-drilling-permits-point.patch`) |

### 3.2 Standalone/prebuilt layers named in docs but absent from the repo and from `layers.yaml`

| asset | what | status |
|---|---|---|
| `parcels_pecos` (`geoms_parcels_pecos.geojson` / prebuilt PMTiles) | Pecos County parcel polygons, StratMap/TNRIS (14,720 fills, ARCHITECTURE.md §5); previously sidebar-hidden | not in repo; no yaml entry; refresh plan: annual manual |
| `fcc_fiber_coverage` (`fcc_fiber_coverage.geojson`) | FCC Broadband Data Collection fixed-availability H3-res-8 hexes (June 2025 vintage), bsl_count, fiber_* counts, `as_of_date 2025-06-30`; source `https://services8.arcgis.com/peDZJliSvYims39Q/.../FCC_Broadband_Data_Collection_December_2024_View/FeatureServer/5` | producer scripts/refresh_fcc_fiber_coverage.py; archives `outputs/refresh/fcc_fiber_coverage_2026-04-25.geojson` (4,056,237 B, 9,160 hexes) and, from the 2026-10-21 refresh, `fcc_fiber_coverage_2026-10-21.geojson` (8,211 hexes, Dec 2025 vintage, `as_of_date 2025-12-31` per CHANGELOG); not in yaml, no "Broadband" group in `GROUP_ORDER` |
| `data/rrc_raw/`, `data/wells_permian6.csv`, `data/permits_permian6.csv` | RRC raw downloads and parsed county-filtered CSVs (hundreds of MB) | gitignored; absent from this checkout; required to build `wells_permian6` / `permits_permian6` |

### 3.3 Files under `data/` (names and sizes from the checkout)

| path | size | what it is | producer | consumer |
|---|---:|---|---|---|
| `data/abatements/abatement_hits_20260424_092810.csv` | 5,833 B (9 rows) | Pinned commissioners-court agenda scrape (Pecos/Reeves); cols `county, meeting_date, agenda_url, agenda_type, item_number, raw_text, applicant, reinvestment_zone, flags, capacity_or_usd, project_type, source_system`. Later daily probe files are gitignored | scripts/scrape_abatements.py | scripts/transform_abatements.py (historical) |
| `data/abatements_court_seed.csv` | 2,584 B (9 rows) | Curated Pecos/Reeves commissioners-court rows in the 32-column `combined_points` schema; `coords_source = commissioner_court` | Chat 83 intel | scripts/transform_ldad.py -> `tax_abatements` (these are the 9 served rows) |
| `data/bead_bdo/` | README 1,428 B; `bead_deployment-projects.xlsx` 38,311 B (152 projects); `bead_subgrantees.xlsx` 23,406 B (41 awardees) | Texas BDO BEAD Final Proposal artifacts (Comptroller). No `bead_fiber_planned` layer: neither file carries county or coordinates (README) | Chat 91 archive | none |
| `data/datacenters/dc_anchors.json` | 20,756 B; README 6,731 B | Source for `dc_anchors`: schema_version 1.0, `generated 2026-04-25`, 8 entries; entry keys `id, name, developer, county, lat, lon, coord_accuracy, status, capacity_mw_announced, commissioned_target, power_source, sources[{url, accessed, claim}]` (optional `single_source`); README defines inclusion (>=100 MW or strategically material), accuracy enum, status enum, quality ranking | hand-curated; weekly CI proposer | `dc_anchors` layer; scripts/geocode_ercot_queue.py (alias snap) |
| `data/fracfocus/DisclosureList_1.csv` | 60,366,537 B (246,776 rows) | FracFocus hydraulic-fracturing disclosure list; cols `DisclosureId, JobStartDate, JobEndDate, APINumber, StateName, CountyName, OperatorName, WellName, Latitude, Longitude, Projection, TVD, TotalBaseWaterVolume, TotalBaseNonWaterVolume, FFVersion, FederalWell, IndianWell` (`FracFocusCSV.zip` gitignored) | downloaded manually | scripts/caramba_om_data.py, outputs/reports/fracfocus_*.py, OXY deck (Finding 10: no new-drill frack within 2 mi of the tract ever) |
| `data/hifld/` | 399,272 / 14,222 / 11,201 / 27,608 B | the four `hifld_*` layer sources | scripts/fetch_hifld.py | layers.yaml |
| `data/oxy/` | `oxy_assets.geojson` 5,184 B (9 pts, intermediate); `oxy_power` 6,356; `oxy_water` 2,598; `oxy_midstream` 2,190; `oxy_carbon` 2,131; `oxy_ercot` 1,627; `oxy_permits` 1,786; `oxy_drilling_permits` 177,978 B | OXY footprint sources | scripts/build_oxy_assets.py, build_oxy_map_layers.py, build_oxy_drilling_permits.py | 7 `oxy_*` layers; `oxy_assets.geojson` also read by scripts/build_oxy_deck.py |
| `data/tiger/primary_roads_wtx.geojson` | 895,301 B | 188 LineStrings, only `name`; West-Texas primary roads | not documented in repo | scripts/oxy_maps.py, scripts/extract_map_geometry.py (not the `tiger_highways` layer) |
| `data/lease_status.csv` | 1,264,472 B (33,088 rows) | Per-lease trailing-6-month production: `oil_gas, district, lease_no, gas_mcf_d, oil_bbl_d, window, months_present` | scripts/fetch_pdq_dump.py + build_lease_status.py (RRC PDQ_DSV.zip, `OG_COUNTY_LEASE_CYCLE`) | scripts/build_well_prod_status.py |
| `data/well_prod_status.csv` | 1,438,343 B (69,056 rows) | API-level production lookup `api8, gas_mcf_d, oil_bbl_d` (RRC API->lease crosswalk `OG_WELL_COMPLETION_DATA_TABLE`) | scripts/build_well_prod_status.py | build.py `_reclassify_no_longer_producing` (wells `well_status`), scripts/caramba_om_data.py |
| `data/production_permian6.xlsx` | 151,820 B | 6 tabs: Annual by county (205x7), Top 20 operators (21x6), Top 100 leases (101x12), Monthly time-series (402x5), Sale-area vs peer (35x9), Raw county-month (2,407x7); 6-county, 1993-present monthly aggregates | scripts/build_production_deliverable.py (RRC PDQ_DSV.zip) | direct distribution (not a map layer; Hanwha exhibit) |
| `data/production_permian6_summary.pdf` | 51,874 B (4 pages) | Summary of the above | same | same |
| `data/wells_howard_loving.csv` | 3,122,491 B (27,197 rows: Howard 18,380; Loving 8,817) | dbf900 wellbores for Howard (FIPS 227) + Loving (301) in the `wells_permian6` schema (`layer_id = wells_permian6`; spud_year 1927-2026); peer-county comparison data | outputs/reports/howard_loving_extract.py (re-scopes parse_rrc.py) | scripts/caramba_om_data.py (peer counties) |

### 3.4 `outputs/refresh/` staging (not layers)

`CHANGELOG.md` (append-only refresh log: TCEQ 2026-04-23 and the multi-source 2026-10-21 entry); `_geocode_ercot_log.txt` (170,816 B, ERCOT geocoding run log on the March data: Stage 1 18.4%, Stage 1+2 27.0% solar+wind+battery); `comptroller_ldad_2026-04-29.csv` (435,192 B, 1,486 rows, 15 cols); April-2026 snapshots `eia860_plants_2026-04-25.csv` (1,367 rows), `eia860_battery_2026-04-25.csv` (133), `wind_2026-04-25.csv` (19,464), `tceq_gas_turbines_2026-04-23.csv` (6) and `_2026-04-25.csv` (13), `turbine-lst_2026-04-23.xlsx`, `fcc_fiber_coverage_2026-04-25.geojson` (4,056,237 B, 9,160 hexes Jun 2025 vintage); `daily/` (90 daily-refresh reports, last 2026-08-19; the external routine stopped). The 2026-10-21 refresh outputs (committed in `3cf3581`):

| file | size (B) | rows/features |
|---|---:|---:|
| `comptroller_ldad_2026-10-21.csv` | 413,942 | 1,416 |
| `eia860_battery_2026-10-21.csv` | 26,990 | 203 |
| `eia860_plants_2026-10-21.csv` | 228,993 | 1,532 |
| `ercot_queue_2026-10-21.csv` | 392,358 | 1,754 |
| `ercot_queue_2026-10-21.meta.json` | 739 |  |
| `fcc_fiber_coverage_2026-10-21.geojson` | 3,636,456 | 8,211 |
| `tceq_gas_turbines_2026-10-21.csv` | 4,924 | 18 |
| `tpit_lines_2026-10-21.geojson` | 69,203 | 133 |
| `tpit_lines_2026-10-21.meta.json` | 550 |  |
| `turbine-lst_2026-10-21.xlsx` | 86,733 |  |
| `wind_2026-10-21.csv` | 2,320,228 | 19,943 |

`rrc_w1_*` backfill scratch is gitignored and absent.

---

## 4. Schema reference

### 4.1 `combined_points.csv`

Header (32 columns, `layer_id` first; WGS84, <=6 decimals; LF line endings forced by `merge_csv`):

```
layer_id,lat,lon,name,plant_code,county,technology,capacity,sector,inr,fuel,mw,zone,poi,entity,funnel_stage,group,under_construction,commissioned,capacity_mw,operator,voltage,osm_id,depth_ft,use,aquifer,project,manu,model,cap_kw,year,coords_source
```

Per ARCHITECTURE.md §4 the columns are the union across point layers, blank where inapplicable, and several are overloaded per layer. Meaning of each column, with the layer-specific readings found in code/data:

| column | canonical meaning | layer-specific use (evidence) |
|---|---|---|
| `layer_id` | layer tag; must equal the yaml `id` | stripped from tile properties |
| `lat`, `lon` | WGS84 decimal degrees; rows with missing or out-of-range values are dropped at split (build.py:337) | `ercot_queue`/`tax_abatements` may be county centroids (see `coords_source`) |
| `name` | display name | plant, battery, project, applicant (tax), substation, TWDB well, city |
| `plant_code` | EIA plant code (numeric) | `tceq_gas_turbines`: TCEQ Permit No. |
| `county` | county name | free text; case varies by source |
| `technology` | EIA technology | `ercot_queue`: ERCOT code BA/PV/WT/GT/CC/IC/ST/OT; `tceq`: "Gas turbine SC/CC"; `tax_abatements`: project type (natural_gas/renewable/...) |
| `capacity` | capacity (MW) | `eia860_battery` duplicate of `capacity_mw`; `tax_abatements`: Capex ($M) (popup label) |
| `sector` | EIA sector | `eia860_plants` only (popup label "Taxing entities" for tax is unused in data) |
| `inr` | ERCOT interconnection request number | `tax_abatements`: agreement/permit id (overload) |
| `fuel` | fuel code | EIA codes relabelled at build (NG, WND, SUN, MWH...); `ercot_queue`: GAS/SOL/WIN/OTH; `tceq`: `natural_gas` |
| `mw` | MW | `ercot_queue` (= `capacity_mw`), `tceq` project MW, `tax_abatements` project MW |
| `zone` | ERCOT zone | `ercot_queue`: SOUTH/WEST/NORTH/COASTAL/HOUSTON/PANHANDLE; `tceq`: Received date ISO (overload) |
| `poi` | ERCOT point of interconnection text | `tax_abatements`: agenda/detail URL |
| `entity` | interconnecting entity/developer | `tceq`: company; `tax_abatements`: taxing unit |
| `funnel_stage` | ERCOT funnel stage `1_no_ia..5_commissioned` | `tceq`: issued/pending/renewed; `tax_abatements`: `{agmt_type}\|{status}\|flags` |
| `group` | ERCOT project-group key (components of the same project) | `tax_abatements`: constant "Permits" |
| `under_construction` | Yes/No | `ercot_queue` only |
| `commissioned` | ERCOT: Yes/No; EIA/USWTDB: year (numeric) | `tceq`: Issue date; `tax_abatements`: approved/meeting date |
| `capacity_mw` | nameplate / queue MW (numeric) | all generation layers |
| `operator` | operator/owner | EIA operator, OSM operator, TPIT operator, TCEQ operator, abatement applicant |
| `voltage` | voltage in VOLTS as text, may be a `;` list | `substations`, `tpit_subs` |
| `osm_id` | OSM id (numeric) | `substations` |
| `depth_ft` | well depth ft | orphan TWDB `wells` |
| `use` | well use | orphan TWDB `wells` |
| `aquifer` | aquifer | orphan TWDB `wells` |
| `project` | project / farm name | `wind`: wind-farm name; `tceq`: number of CTs; `tax_abatements`: reinvestment zone |
| `manu`, `model` | turbine manufacturer, model | `wind`, `tceq_gas_turbines` |
| `cap_kw` | turbine kW | `wind` |
| `year` | year | `wind`: commissioning year; `tceq`: received year; `tax_abatements`: approval year |
| `coords_source` | coordinate-provenance stamp (added by geocoding) | `ercot_queue`: county_centroid / eia860 / uswtdb / tpit_poi / substation_poi (script also defines abatement_match, substation_match, manual_override; not yet present); `tax_abatements`: ldad_county_centroid / commissioner_court |

`NUMERIC_KEYS` coerced to numbers at build (build.py:91): `mw, capacity, capacity_mw, cap_kw, depth_ft, year, plant_code, osm_id, acres, total_depth, spud_year, permit_year, completion_year`. All other columns stay strings (so `voltage`, `commissioned`, `zone` are strings in tiles; filters/expressions use `to-number`).

Column population matrix at HEAD (non-blank row counts; "·" = none):

| column | `cities` | `solar` | `substations` | `tpit_subs` | `wells` | `eia860_plants` | `eia860_battery` | `tceq_gas_turbines` | `wind` | `tax_abatements` | `ercot_queue` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| rows | 9 | 180 | 1,637 | 141 | 14,700 | 1,532 | 203 | 18 | 19,943 | 1,425 | 1,754 |
| `name` | 9 | 180 | 958 | 141 | 14,700 | 1,532 | 203 | 18 | · | 1,425 | 1,754 |
| `plant_code` | · | 180 | · | · | · | 1,532 | 203 | 18 | · | · | · |
| `county` | · | 180 | · | · | 14,700 | 1,532 | 203 | 18 | 19,943 | 1,425 | 1,754 |
| `technology` | · | · | · | · | · | 1,003 | 203 | 18 | · | 9 | 1,754 |
| `capacity` | · | · | · | · | · | · | 203 | · | · | 2 | · |
| `sector` | · | · | · | · | · | 1,532 | · | · | · | · | · |
| `inr` | · | · | · | · | · | · | · | · | · | 1,416 | 1,754 |
| `fuel` | · | · | · | · | · | 1,003 | · | 18 | · | · | 1,754 |
| `mw` | · | · | · | · | · | · | · | 18 | · | 1 | 1,680 |
| `zone` | · | · | · | · | · | · | · | 18 | · | · | 1,754 |
| `poi` | · | · | · | · | · | · | · | · | · | 1,422 | 1,754 |
| `entity` | · | · | · | · | · | · | · | 18 | · | 1,416 | 1,754 |
| `funnel_stage` | · | · | · | · | · | · | · | 18 | · | 1,425 | 1,754 |
| `group` | · | · | · | · | · | · | · | · | · | 1,425 | 1,754 |
| `under_construction` | · | · | · | · | · | · | · | · | · | · | 1,754 |
| `commissioned` | · | · | · | · | · | 1,003 | 203 | 13 | 19,705 | 1,363 | 1,754 |
| `capacity_mw` | · | 180 | · | · | · | 1,003 | 203 | 18 | 19,204 | · | 1,680 |
| `operator` | · | · | 798 | 129 | · | 1,532 | 203 | 18 | · | 1,424 | · |
| `voltage` | · | · | 1,446 | 138 | · | · | · | · | · | · | · |
| `osm_id` | · | · | 1,637 | · | · | · | · | · | · | · | · |
| `depth_ft` | · | · | · | · | 11,125 | · | · | · | · | · | · |
| `use` | · | · | · | · | 14,700 | · | · | · | · | · | · |
| `aquifer` | · | · | · | · | 14,700 | · | · | · | · | · | · |
| `project` | · | · | · | · | · | · | · | 18 | 19,943 | 1,423 | · |
| `manu` | · | · | · | · | · | · | · | 18 | 19,204 | · | · |
| `model` | · | · | · | · | · | · | · | 18 | 19,203 | · | · |
| `cap_kw` | · | · | · | · | · | · | · | · | 19,204 | · | · |
| `year` | · | · | · | · | · | · | · | 18 | 19,705 | 1,363 | · |
| `coords_source` | · | · | · | · | · | · | · | · | · | 1,425 | 1,754 |

### 4.2 `combined_geoms.geojson`

FeatureCollection, no top-level `crs` (EPSG:4326 by convention), 2D coordinates (Z flattened at build), simplification 0.002-0.005 and 4-decimal rounding per ARCHITECTURE.md §4. Every feature's `properties.layer_id` tags its layer; hand-placed/edited features also carry `source` and `source_date`. Standalone files (hifld, oxy, dc_anchors) carry no `layer_id`. Contents at HEAD:

| layer_id | features | geometry | property keys (count if not all) | bbox |
|---|---:|---|---|---|
| `aquifers` (ORPHAN) | 5 | MultiPolygon x3, Polygon x2 | `name`, `source`, `layer_id` | [-104.96, 29.17, -98.4, 36.5] |
| `counties` (served) | 46 | Polygon x46 | `GEOID`, `NAME`, `layer_id` | [-106.65, 28.97, -99.3, 32.96] |
| `mpgcd_zone1` (served) | 1 | Polygon x1 | `NAME`, `ZONE`, `ACCURACY`, `note`, `layer_id` | [-103.06, 30.75, -102.8, 30.95] |
| `transmission` (served) | 6244 | LineString x6225, MultiLineString x19 | `V`, `O`, `layer_id` | [-108.46, 25.89, -93.19, 37.91] |
| `caramba_north` (served) | 1 | Polygon x1 | 58 AgriWebb export keys (Name, title, landSize, arableLandSize, cropType, area_*, centre_*, label_*, farmId, tenantId, creator, …) + `source`, `source_date`, `layer_id` | [-102.99, 30.9, -102.96, 30.93] |
| `caramba_south` (ORPHAN) | 1 | Polygon x1 | 58 AgriWebb export keys (Name, title, landSize, arableLandSize, cropType, area_*, centre_*, label_*, farmId, tenantId, creator, …) + `source`, `source_date`, `layer_id` | [-103.05, 30.87, -102.99, 30.9] |
| `labels_hubs` (served) | 1 | Point x1 | `layer_id`, `name`, `source`, `source_date` | single point (coordinates omitted) |
| `waha_circle` (served) | 1 | Point x1 | `layer_id`, `name`, `source`, `source_date` | single point (coordinates omitted) |
| `water_mains_approx` (ORPHAN) | 3 | LineString x3 | `name`, `operator`, `accuracy`, `source`, `layer_id` | [-102.9, 30.86, -101.17, 32.6] |
| `solstice_substation` (served) | 1 | Point x1 | `layer_id`, `name`, `operator`, `county`, `voltage_kv`, `status`, `role`, `osm_id`, `source`, `source_date` | single point (coordinates omitted) |
| `la_escalera` (served) | 1 | Polygon x1 | `layer_id`, `name`, `owner`, `developer`, `county`, `acres`, `project`, `ACCURACY`, `source`, `source_date` | [-103.05, 30.34, -102.66, 30.68] |
| `longfellow_ranch` (served) | 1 | Polygon x1 | `layer_id`, `name`, `owner`, `developer`, `campus`, `capacity`, `county`, `ACCURACY`, `source`, `source_date` | [-102.78, 30.69, -102.59, 30.84] |
| `gw_ranch` (served) | 1 | Polygon x1 | `layer_id`, `name`, `developer`, `campus`, `capacity`, `status`, `grid`, `county`, `ACCURACY`, `source`, `source_date` | [-102.87, 31.11, -102.81, 31.16] |
| `county_labels` (served) | 254 | Point x254 | `layer_id`, `name` | [-106.17, 26.12, -93.74, 36.28] |
| `drilling_permit_density` (ORPHAN) | 11 | Polygon x11 | `layer_id`, `county`, `geoid`, `area_sqmi`, `permit_count_all`, `permit_count_20yr`, `permit_count_10yr`, `permit_count_5yr`, `permits_per_sqmi_all`, `permits_per_sqmi_20yr`, `permits_per_sqmi_10yr`, `permits_per_sqmi_5yr`, `source`, `source_date` | [-104.92, 29.78, -100.96, 32.09] |
| `tpit_lines` (served) | 133 | LineString x133 | `name`, `pid`, `owner`, `county`, `from`, `to`, `from_raw`, `to_raw`, `voltage`, `status`, `tier`, `sheet`, `in_service`, `layer_id` | [-106.77, 29.22, -99.53, 33.49] |

### 4.3 `layers.yaml` field reference

Top level: a single `layers:` list (39 entries). Key usage counts: `id` (39), `file` (36), `geom` (39), `group` (39), `label` (39), `source` (39), `as_of` (39), `color` (39), `line_width` (8), `default_on` (39), `popup` (39), `tippecanoe` (36), `popup_labels` (34), `radius` (21), `fill_opacity` (7), `description` (17), `stroke_width` (17), `stroke_color` (13), `filterable_fields` (25), `circle_radius` (2), `companions` (1), `sidebar_omit` (2), `show_marker` (1), `min_zoom` (7), `prebuilt` (3), `min_spud_year` (1), `exclude_recompletions` (1), `reclassify_inactive_production` (1), `keep_technology` (1), `keep_county_scope` (1).

| key | consumed by | effect |
|---|---|---|
| `id` | build.py, template | tippecanoe `-l <id>`, `tiles/<id>.pmtiles`, MapLibre source-layer, `lyr_<id>`; equals `layer_id` for combined files |
| `file` | `build_layer` | `combined_points.csv` / `combined_geoms.geojson` -> pre-split NDJSON by `layer_id`; otherwise `resolve_source()` (PROJECT then repo ROOT); `.csv` -> `csv_to_ndgeojson`, `.json` -> `dc_anchors_to_ndgeojson` (dc schema only), else `geojson_to_ndgeojson`. Absent on prebuilt layers |
| `prebuilt` | `build_layer` | skip tippecanoe; copy `<id>.pmtiles` from `$LRP_PROJECT_DIR`, `$LRP_UPLOADS_DIR`, else range-download from the live site (8 MB chunks, 5 retries); `<1024 B` = ERROR; count from PMTiles tilestats (`feature_count` yaml fallback, unused) |
| `geom` | template | `point`->circle (+icon), `line`->line (+casing), `fill`->fill + outline line, `label`->symbol text |
| `group` | template | sidebar group (must be in `GROUP_ORDER`) |
| `label` | template | sidebar text |
| `color` | template | paint colour (overridden by expressions for ercot_queue, dc_anchors, wells, permits) |
| `default_on` | template | initial visibility (URL `layers=` overrides) |
| `description` | template | `title` tooltip on the sidebar row |
| `popup` | forwarded, unused | not read by the template (G1) |
| `popup_labels` | template | field label map |
| `radius` | template | circle radius fallback (registry default 3) |
| `line_width` | template | line width (registry default 0.75); casing threshold >0.75; `tpit_lines` overridden by kv sizing |
| `fill_opacity` | template | fill opacity (registry default 0.25); also point circle-opacity (G2) |
| `circle_radius`, `stroke_color`, `stroke_width` | template reads, **never forwarded** | no effect (G2) |
| `min_zoom` | template | MapLibre `minzoom` (not tippecanoe) |
| `tippecanoe` | `run_tippecanoe` | extra flags (default `['-zg']`) |
| `companions` | template | layer ids toggled with this layer (waha_circle -> labels_hubs) |
| `sidebar_omit` | template | hide from sidebar (labels_hubs, permits_permian6) |
| `show_marker` | template | add a circle marker under a label layer |
| `filterable_fields` | `compute_filter_stats`, template | per-field filter UI; types `numeric` (range), `categorical` (multi-select; >2,000 distinct -> text), `date_range` (first 10 chars), `text` (auto-promoted to categorical when <=2,000 distinct). Sub-keys: `field, type, label`, optional `sort_by_count` (6), `quick_presets` (3, chips), `group_presets` (1, spud-year eras), `value_labels` (1, plug_flag Y/N) |
| `min_spud_year` | `_filter_min_spud_year` | drop features with missing/older `spud_year` (wells: 1964) |
| `exclude_recompletions` | `_filter_exclude_recompletions` | drop rows with `completion_year < spud_year` (RULE H) |
| `reclassify_inactive_production` | `_reclassify_no_longer_producing` | derive `well_status` from `data/well_prod_status.csv` (gas <= 125 Mcf/d and oil <= 25 bbl/d) |
| `keep_technology`, `keep_county_scope` | `_filter_tax_keep` | tax_abatements declutter (combined-file path only) |
| `exclude_within` | `_exclude_within` (standalone path) | read by build.py but **not set on any layer** in the current yaml |
| `color_steps`, `text_halo` | forwarded | read by template for fill step colours / label halo; unused in current yaml |
| `source`, `as_of` | `render_html` (HEAD 736a18d) -> template `popupSrcHtml` | popup footer fallback when features carry no `source`/`source_date` (G3) |

Also in `build.py` (not yaml): `ABATEMENT_TARGET_LAYERS` (eia860_plants, ercot_queue, solar, wind, eia860_battery) fuzzy-join to `tax_abatements` (subset-token rule; matches now: eia860_plants 113, ercot_queue 26, solar 23, eia860_battery 11 (total 173; index of 1,423 abatement rows; wind 0); prior deploy: eia860_plants 104, ercot_queue 31, solar 22, eia860_battery 7, wind 0); `compute_ercot_group_aggregates`; `STATS_ATTRS_FIELDS` (permits: `permit_year, oil_gas, wellbore_profile, total_depth, county_name, county_role, status, operator_name`; wells: `spud_year, oil_gas, completion_year, total_depth, county_name, county_role, plug_flag, active_flag, district, well_status`); `CATEGORICAL_CAP = 2000`; `_headers`/`_redirects` emission (`/* /index.html 200`; tiles CORS `*`, `max-age=3600, must-revalidate`).

---

## 5. Basemaps, glyphs and sprite icons

`BASEMAPS` (build_template.html:391), selector `#basemap-select` (:310), default `esri_imagery` (`initBase`, :459); the map is first created with the `carto_light` style and `applyBasemap(initBase)` swaps to imagery on load (:2888). HTTP status probed 2026-10-21 by fetching one tile / the style (status, type and size only).

| id | selector label (live) | URL (live) | prior deploy (page of 2026-10-20; audit screenshots) | live since 736a18d / deploy 6ad88eb4 |
|---|---|---|---|---|
| `carto_light` | "Light Gray (Esri)" (was "Carto Light") | prior: raster `https://{a,b,c}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png`; live: `https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}` (maxzoom 16; key name kept so old `#base=carto_light` links work) | The "light" option was actually Carto **Voyager** raster; tiles return HTTP 200 but carry an API-key placeholder watermark (operator-verified; docs/audit-2026-10-20/03_carto_api_key_watermark.png; Known Defect #3). The probe returned a 2,049-byte PNG | Esri World Light Gray Canvas, probe HTTP 200 image/jpeg; Carto removed (a Carto tile probe still returns HTTP 200 with a 2,049-byte PNG, consistent with the placeholder) |
| `esri_streets` | Esri Streets | `https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}` | HTTP 200 | unchanged |
| `esri_imagery` | Esri World Imagery | `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}` (attribution "Tiles © Esri, DigitalGlobe, Earthstar") | HTTP 200; **default** | unchanged |
| `openfreemap` | OpenFreeMap | vector style `https://tiles.openfreemap.org/styles/liberty` (`kind: 'style'`, `map.setStyle(url, {diff:false})`) | HTTP 200 (JSON). Replaces glyph/sprite set with Liberty's, so the custom `/sprite/sprite` icons will not resolve under this basemap *(code-derived)* | unchanged |
| `naip` | NAIP aerial | prior: `https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPPlus/ImageServer/tile/{z}/{y}/{x}`; live: `.../USGSNAIPImagery/ImageServer/exportImage?bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&size=256,256&format=jpgpng&f=image` (maxzoom 18) | **HTTP 404** (blank map; operator-verified docs/audit-2026-10-20/04_naip_blank.png; Known Defect #2) | exportImage probe HTTP 200 image/jpeg |

`applyBasemap` (build_template.html:2645) re-runs `addLayer` for every layer after each style change, re-raises OXY, restores visibility/filters and rewires popups. Raster basemaps use `rasterStyle()` with `glyphs: https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf` (HTTP 200 for `Noto Sans Bold`, the only font used, by `county_labels` and `labels_hubs`) and `sprite: /sprite/sprite` (same-origin). Every label layer therefore depends on the OpenFreeMap glyph host on every raster basemap. Other third-party runtime dependencies: Google Fonts (Inter), jsDelivr SheetJS `xlsx@0.18.5` (stats XLSX export, loaded on demand), Esri, USGS National Map (NAIP); Carto only in the prior deploy. MapLibre GL 4.7.1, pmtiles.js 4.3.0 and turf are vendored same-origin in `vendor/` (ARCHITECTURE.md §1).

**Sprite icons** (`sprite/sprite.png|json` 48x48 px @1x and `sprite@2x.*` 96x96 px, regenerated each build by `build_sprite.py` from inline SVG via cairosvg; x-offsets 0/48/96/144/192): `solar`, `wind`, `battery`, `plant`, `well`. `ICON_MAP` (build_template.html:363): `solar`->solar, `wind`->wind, `eia860_battery`->battery, `eia860_plants`->plant, `wells`->well (stale; the served well layer is `wells_permian6` and has no icon). Icons are symbol layers drawn above the circle layers from zoom 9, sized by `sizingIconSizeExpr` (0.45-1.2 for MW layers; 0.6 default; 0.45-1.1 for wind).

**Other front-end features** (for completeness): Views dropdown (`#saved-views-select`, `SAVED_VIEWS` at build_template.html:2582) holds exactly 12 saved views `spud_{pecos|other5|all6}_{all|lt5k|5to10k|10kplus}` = "Spud wells — {Pecos | Other 5 counties | Pecos vs. other 5} — {all depths | <5,000 ft | 5,000–10,000 ft | 10,000 ft+}"; each activates only `wells_permian6` with `county_name` and `total_depth` filters (no permits, no scrubber year). Toolbar: Measure (turf distance/area), Reset, Share (copies the hash URL), Print (landscape, legend of active layers). A sidebar toggle collapses the panel (`#sb=1`). The access gate was removed 2026-10-20 (map public, no access logging).
