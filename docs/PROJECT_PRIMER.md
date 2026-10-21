# LRP Texas Energy GIS — Project Primer

**Status date:** 2026-10-21
**Live deploy:** `6ad88eb494745d960cbb78bd`
**Repo:** `github.com/10thMuses/lrp-tx-gis`, `main` @ `0c6564d` or later
**Live URL:** https://lrp-tx-gis.netlify.app (public; no login since 2026-10-20)

This primer is the single entry point for anyone (human or AI) optimizing the project. It has three parts.

| Part | File | Contents |
|---|---|---|
| 1 | this file | What the project is; how a multi-layer mapping tool like this is built; object model; source families; current state; open defects |
| 2 | [`docs/primer/02_LAYER_CATALOG.md`](primer/02_LAYER_CATALOG.md) | Every one of the 39 layers: summary table plus one card per layer (source, URL, script, fields, filters, styling, as-of, caveats). Also: orphan datasets, full schemas, `layers.yaml` key reference, basemaps, sprites |
| 3 | [`docs/primer/03_OPERATIONS_AND_HISTORY.md`](primer/03_OPERATIONS_AND_HISTORY.md) | Operator and audience; rules; exact workflow commands; analytical methods (RULE H etc.); script registry; deliverables registry; external services; chronology; backlog; environment pitfalls |

Companion documents:
- `docs/OPERATING_MANUAL.md`: architecture, stack, ETL, CRS, tiling, environment, runbooks, troubleshooting.
- `docs/HANDOFF_PROMPT.md`: the brief for an optimizing AI.
- `CLAUDE.md`, `OPERATING.md`, `ARCHITECTURE.md`, `WIP_OPEN.md`: the repo's own canonical rules and state.

Where Part 3 (written before the 2026-10-21 refresh) disagrees with §6 of this file, **§6 wins**.

---

## 1. What the project is

**Business purpose.** Land Resource Partners (operator: Andrea Himmel) is marketing **Caramba North**: an up-to-1,300-acre contiguous tract on I-10, about 5 miles west of Fort Stockton, Pecos County, Texas, offered as powered land for data-center / AI-compute development. The map is the evidence layer behind the offering memorandum (OM). Every figure in the OM is meant to be verifiable feature by feature on the map.

The thesis has five pillars:
1. **Power cost:** Waha-basis gas.
2. **765 kV transmission:** AEP Solstice substation, about 15 mi from the site.
3. **Water:** 47,418 AF/yr permitted on adjacent affiliated land.
4. **Surrounding demand:** 25+ GW of announced data-center demand.
5. **Zoning:** as-of-right development in unzoned Pecos County.

A sixth, defensive pillar is **subsurface quiet**:
- No new well of any kind within 5 mi since 2020.
- No new-drill frack within 2 mi, ever.
- About 90% of county "drilling activity" is rework of existing wells.

**Secondary uses.** The same platform and data feed:
- the *Grid Wire* newsletter (an ERCOT/Texas energy intelligence product sent to peers);
- an OXY (Occidental) intelligence report and partnership deck;
- a Crusoe special report;
- diligence reports on Stargate Abilene and Pacifico GW Ranch.

**Audience.** Newmark deal team (buyer side), peers (Mel Riggs, Mark, Dory Wiley, John Lane), and the site owner.

## 2. How a multi-layer mapping tool like this is built

The system is a **static-site GIS**. It has no server, no database and no tile server. Every design choice follows from that.

```
PUBLIC SOURCES ──► INGEST SCRIPTS ──► CANONICAL FLAT FILES ──► BUILD ──► STATIC SITE ──► BROWSER
(EIA, ERCOT, RRC,   scripts/refresh_*  combined_points.csv      build.py   dist/ on       MapLibre GL +
 TCEQ, USGS, OSM,   fetch_*, scrape_*  combined_geoms.geojson   +tippe-    Netlify CDN    PMTiles range
 Census, HIFLD,     parse_rrc.py       data/<standalone>        canoe                     requests
 Comptroller...)    build.py refresh   layers.yaml (registry)
```

### 2.1 Stages

1. **Acquire.**
   - One script per source downloads the publisher's file or API and filters to scope. Scope is usually Texas, the six-county Permian set (Pecos, Reeves, Ward, Midland, Martin, Reagan), or a 23-county West Texas set.
   - Each script normalizes to the shared schema and writes a dated snapshot to `outputs/refresh/<layer>_<YYYY-MM-DD>.csv|geojson`.
   - Rule: no hand-coded coordinates. Every point comes from the publisher, a documented geocoder (Nominatim, county centroid, POI match), or a sourced geometry.
2. **Merge.**
   - `python3 build.py merge <layer_id> <file>` swaps all rows for one `layer_id` in the canonical combined file, writing atomically.
   - Points go to `combined_points.csv`, a 32-column shared schema keyed by `layer_id`.
   - Lines and polygons go to `combined_geoms.geojson`, with `properties.layer_id` on each feature.
   - Large or special layers live as standalone files: the RRC wells/permits CSVs (gitignored, regenerated from RRC), `data/oxy/*.geojson`, `data/hifld/*.geojson` and `data/datacenters/dc_anchors.json`.
3. **Register.**
   - `layers.yaml` is the layer registry: id, file, geometry, group, label, `source`, `as_of`, color, zoom, filters and build-time transforms.
   - Example transforms: `min_spud_year`, `exclude_recompletions`, `keep_technology`, `exclude_within`.
   - Adding a layer means adding a registry entry plus data. No front-end code change is needed unless the layer needs a custom popup or style.
4. **Build.** `python3 build.py`:
   - Splits the combined files per layer and applies the build-time transforms.
   - Runs **tippecanoe** to produce one **PMTiles** archive per layer (`dist/tiles/<id>.pmtiles`).
   - Computes filter statistics (value lists and ranges for the UI) and writes slim stats JSON for the wells and permits panels (`dist/data/*.json`).
   - Injects the registry and a build ID into `build_template.html` to produce `dist/index.html`.
   - Writes Netlify `_headers` and `_redirects`.
   - Prints `built=N missing=N errored=N`.
5. **Deploy and verify.**
   - Publish `dist/` to Netlify, through `scripts/deploy.sh` (REST API with `NETLIFY_PAT`) or the Netlify MCP proxy.
   - Check that the live `index.html` md5 matches the build.
   - Run `scripts/verify_deployed_layers.py`, which reads each PMTiles header over HTTP range requests and checks feature counts.
   - Then close out by merging the branch to `main` (`scripts/close-out.sh`).
6. **Client.**
   - The single-page app uses MapLibre GL 4.7.1 with the pmtiles protocol; the libraries are vendored in `vendor/`.
   - Sidebar layer groups with toggles and static feature counts.
   - Per-layer filter panels built from the injected filter statistics; filters run client-side via `setFilter`.
   - Saved Views for the wells analysis.
   - A time scrubber for spud and permit years.
   - Popups with a source and as-of footer.
   - Measure (turf), Share (URL hash state), Print, and a basemap picker.

### 2.2 Why this architecture

- **Zero runtime infrastructure.** Hosting cost is near zero and nothing can go down except the CDN.
- **PMTiles.** One file per layer, read by HTTP range requests, so no tile server is needed.
- **Flat files in git.** Every data change is diffable and reviewable.

The tradeoffs are:
- Freshness requires a rebuild and redeploy.
- There is no server-side query, so spatial analytics run offline in Python and reach the OM through its build scripts.
- Large raw sources (RRC wellbore, about 369 MB) are kept out of git and must be re-fetched on any new machine.

### 2.3 Object model

| Object | Where | Key fields |
|---|---|---|
| Layer | `layers.yaml` entry → injected `LAYERS` registry | `id`, `file`, `geom` (point/line/fill/label), `group`, `label`, `source`, `as_of`, `color`, `min_zoom`, `default_on`, `filterable_fields`, transforms |
| Point feature | `combined_points.csv` row | `layer_id`, `lat`, `lon`, `name`, plus a typed subset of the 32 columns (mw, fuel, technology, county, operator, status, year, …); see Part 2 §4.1 |
| Line or polygon feature | `combined_geoms.geojson` feature | `properties.layer_id`, plus layer-specific properties; see Part 2 §4.2 |
| Standalone layer | `data/...` file referenced by `file:` | Native schema (e.g. RRC wellbore fields `api_no`, `spud_year`, `completion_year`, `total_depth`, `county_name`, status flags) |
| Tile archive | `dist/tiles/<id>.pmtiles` | Generated; never committed |
| Stats side-car | `dist/data/<id>.json` | Slim arrays for the wells and permits panels |
| Refresh snapshot | `outputs/refresh/<layer>_<date>.*` (+ `.meta.json`) | Audit trail of each source pull |

### 2.4 Source families

| Family | Publisher | Layers | Cadence (publisher) | Acquisition |
|---|---|---|---|---|
| Generation fleet | EIA-860 (annual) | eia860_plants, eia860_battery, solar | Annual (final release about Sep) | `refresh_eia860.py --year` |
| Wind | USGS/LBNL USWTDB | wind | Quarterly-ish | `refresh_uswtdb.py --from-url` (API certificate expired) |
| Interconnection queue | ERCOT GIS Report (MIS report type 15933) | ercot_queue | Monthly | `refresh_ercot_queue.py` (new 2026-10-21) |
| Planned transmission | ERCOT TPIT | tpit_lines, tpit_subs | Monthly / ad hoc | `refresh_tpit.py` (attributes only) |
| Grid topology | HIFLD (transmission), OSM Overpass (substations) | transmission, substations | Annual / live | Manual; no script |
| Oil and gas | RRC dbf900 wellbore, daf420 permits | wells_permian6, permits_permian6, oxy_drilling_permits | Weekly / monthly | `build.py refresh wells`, `fetch_rrc.py` + `parse_rrc.py` |
| Midstream | HIFLD/EIA pipelines + processing; RRC pipelines (2019) | hifld_*, rrc_pipelines | Annual | `fetch_hifld.py`; prebuilt |
| Air permits | TCEQ turbine list | tceq_gas_turbines | Irregular | `refresh_tceq_gas_turbines.py [xlsx]` |
| Tax abatements | Texas Comptroller LDAD + commissioners-court agendas | tax_abatements | Rolling | `scrape_ldad.py` / `transform_ldad.py` / `scrape_abatements.py` |
| Data-center anchors | Public announcements (LRP-curated) | dc_anchors | Event-driven | `refresh_dc_anchors.py` (Claude proposes, human merges) |
| Reference | Census TIGER, BTS rail | counties, county_labels, tiger_highways, bts_rail | Static | Prebuilt / one-off |
| Deal and focal | LRP / owner / public reporting | caramba_north, la_escalera, longfellow_ranch, gw_ranch, solstice_substation, waha_circle, labels_hubs, mpgcd_zone1, cities | Static | One-off edit scripts |
| OXY footprint | Curated from EIA, TCEQ, EPA, OSM, filings | oxy_* | Manual | `build_oxy_map_layers.py`, `build_oxy_drilling_permits.py` |

Full per-layer detail is in Part 2.

## 3. Repository map

```
build.py                 build / merge / refresh CLI (the core)
build_template.html      the entire front end (HTML+CSS+JS, ~2,900 lines)
build_sprite.py          SVG -> sprite PNG/JSON (cairosvg, Pillow)
layers.yaml              layer registry (39 layers)
combined_points.csv      canonical point features
combined_geoms.geojson   canonical line and polygon features
data/                    standalone layer data, caches, inputs (wells/permits CSVs and rrc_raw/ gitignored)
scripts/                 ingest, transform, geocode, deploy, audit, deliverable builders (om2/ = current OM)
outputs/refresh/         dated source snapshots + CHANGELOG
outputs/reports/         deliverables (OM, teaser, decks, briefs, Grid Wire, OXY, Crusoe, vibration memo)
docs/                    manual, primer, plans, settled decisions, archive, audit screenshots
vendor/                  maplibre-gl, pmtiles, turf (vendored)
sprite/                  icon sprite
.github/workflows/       build-and-deploy.yml (manual), dc-anchors-refresh.yml (weekly)
```

## 4. Rules any optimizer must keep

These come from `CLAUDE.md` and `OPERATING.md`, and are explained in Part 3 §2.

1. **Never read source data files into an LLM context.** Stream through subprocesses; print only aggregates.
2. **Never hand-code coordinates or feature values.** If there is no source, there is no layer.
3. **Never `git add -A`.** Stage explicit paths.
4. **Atomic writes** (`os.replace`) for any read-modify-write.
5. **Deploy and merge together.** A deploy without the matching merge to `main` in the same session is a violation.
6. **Keep each layer's `source` and `as_of` in `layers.yaml` current on every refresh.** The popups show them.

## 5. How to run it from zero

```bash
git clone https://github.com/10thMuses/lrp-tx-gis.git && cd lrp-tx-gis
bash scripts/bootstrap-claude-code.sh      # tippecanoe + python deps (needs libcairo2 for cairosvg)
cp .env.example .env                        # set NETLIFY_PAT (and GITHUB_PAT) if deploying via deploy.sh
python3 build.py refresh wells              # RRC wellbore -> data/wells_permian6.csv (~369 MB download)
python3 scripts/fetch_rrc.py permits && python3 scripts/parse_rrc.py permits
LRP_PROJECT_DIR=. LRP_UPLOADS_DIR=./uploads LRP_DIST_DIR=./dist python3 build.py
bash scripts/deploy.sh                      # or the Netlify MCP proxy; then verify:
python3 scripts/verify_deployed_layers.py --quiet
```

## 6. Current state as of 2026-10-21 (supersedes older docs)

### 6.1 Done 2026-10-20/21

| Item | Result |
|---|---|
| Access gate | Removed. The map is public. Supabase `oxy-gate`/`oxy-track` are no longer called and there is no access logging. |
| Data refresh | ERCOT queue → Sep 2026 GIS Report (published 2026-10-01). TPIT attributes → July 2026. EIA-860 → 2025 data. USWTDB → V9.1. TCEQ → v2026.10.7. LDAD → 2026-10-10. RRC wells (100,220 wellbores) and permits (33,179, snapshots through 2026-09-30). OXY permits 294 → 1,336. |
| New fetchers | `scripts/refresh_ercot_queue.py`, `scripts/refresh_tpit.py` |
| Parser fix | `parse_rrc.py` now reads 2024+ permit formats (`0109`/`0209`, 27/28-byte location lines). `approved_date` offset fixed. |
| Map fixes | NAIP basemap working (slow to load). Light basemap = Esri Light Gray. Popup source and as-of on all layers. Public watermark. Share URL carries the scrubber year. Wells/permits stats panels restored. Mobile sidebar starts collapsed. Accessibility labels. `_headers` (tile caching and CORS) restored. |
| Verification | `built=39 missing=0 errored=0`. 39/39 layers live, 163,430 features. Browser test clean. |
| Docs | `docs/OPERATING_MANUAL.md`, this primer, `docs/HANDOFF_PROMPT.md`, `docs/audit-2026-10-20/` |

### 6.2 Material changes to OM figures

The OM is not yet regenerated.

| OM figure | OM (Jul/Aug 2026) | Current data |
|---|---|---|
| Pecos County ERCOT queue | 12.0 GW / 39 projects | **21.4 GW / 56 projects** (Sep 2026 report) |
| Six adjacent counties queue | 24.6 GW | 26.0 GW / 92 projects |
| Data-center catchment | "25+ GW" (text) vs. 9.7 GW in the data | Still 8 anchors; Chevron WTPP, TPL+Bolt, Alpha Digital and Longfellow are still not in `dc_anchors.json` |
| New-drill wells ≤ 10 mi | 3 (Jul) → 1 (Aug, RULE H re-stamp) | Re-check against the 2026-10-21 wellbore pull |
| "Real-time" / "weekly-to-monthly refresh" claim | Stated in the OM and the cover email | Not true. Refresh is manual until the scheduled workflow is approved. |
| Access policy text ("credentials", "access is logged") | In the OM appendix, teaser and buyer email | Map is public. The appendix still prints the old password (`scripts/om2/build_om_master.py:528`). |

### 6.3 Open defects and gaps, ranked

1. **No automated refresh.** The scheduled refresh, build and deploy workflow was not built: automated production deploys need the operator's explicit approval. It also needs repo secrets `NETLIFY_AUTH_TOKEN` and `NETLIFY_SITE_ID`. Design notes are in `docs/refresh_automation_plan.md` and Part 3.
2. **`dc_anchors` stale** (2026-04-25, 8 entries). `ANTHROPIC_API_KEY` is not set locally. About 14 weekly proposal PRs sit unmerged. This is the main reason §7 of the OM cannot reach 25 GW.
3. **Registry drops style keys.** `build.py` (registry block about line 1168) does not pass `circle_radius`, `stroke_color` or `stroke_width`. The template reads `L.circle_radius`, `L.stroke_color` and `L.stroke_width` (`build_template.html:635-657`), so per-layer settings in `layers.yaml` are ignored. Point layers draw at the default 0.25 fill opacity, and the Solstice/Waha rings do not render as configured.
4. **Substation sizing.** `substations` and `tpit_subs` voltage is stored in volts but sized on a 0–500 kV scale, so every substation renders at the maximum radius.
5. **`tax_abatements` serves 9 of 1,425 rows.** `keep_technology ['natural_gas','renewable']` plus the county whitelist pass only the court-seed rows.
6. **ERCOT queue geocoding.** 74% of rows sit at county centroids (with jitter). Stage 3 (operator override CSV) is described in `WIP_OPEN.md` but has no code (no `--stage` flag). The EIA and wind indexes used by `geocode_ercot_queue.py` are hard-coded to the 2026-04-25 files.
7. **TPIT.** Only the 133 existing lines are refreshed. New projects need a reproducible terminal-to-substation matcher; the original rule is undocumented. `tpit_subs` are copies of OSM substations.
8. **No refresh script** for `substations` (OSM Overpass), `transmission` (HIFLD), `solar` (not emitted by `refresh_eia860.py`), the prebuilt `tiger_highways`, `bts_rail` and `rrc_pipelines` (only copy is on the live site), or `hifld_ng_processing` (2017 survey data).
9. **Permits coordinate lag.** RRC daf420 carries lat/lon only through about 2026-03-31. 1,825 recent permits have no coordinates. The 2025-05-31 snapshot is missing on the RRC server.
10. **Caramba polygon area.** The polygon is about 682.6 ha (about 1,687 ac), but the label says 1,300 ac. Source: AgriWebb paddock export.
11. **Popup `popup:` field lists unused.** The generic popup prints every property.
12. **Other.**
    - `exclude_within` (Caramba well exclusion) is implemented but set on no layer.
    - `ICON_MAP` keys the removed `wells` layer.
    - Orphan datasets in the combined files: `wells` (TWDB), `aquifers`, `caramba_south`, `water_mains_approx`, `drilling_permit_density`.
    - No dependency manifest (`requirements.txt`).
    - `build.py` does not load `.env`.
    - `WIP_OPEN.md` is over its 8,192-byte audit budget.
    - About 89 stale `daily-refresh` branches on origin.
    - Unused Supabase functions remain deployed.
    - Third-party runtime dependencies: OpenFreeMap glyphs, Google Fonts, jsDelivr SheetJS.
13. **Deliverables lineage.** The current OM set (`scripts/om2/`) hard-codes its figures. The older `build_caramba_om.py` + `caramba_om_data.py` path derives them from data.
