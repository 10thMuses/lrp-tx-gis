# LRP Texas Energy GIS — Operating Manual

Scope: repo `/home/user/lrp-tx-gis` (`github.com/10thMuses/lrp-tx-gis`, `main` canonical). Written 2026-10-20 against branch `claude/nice-ritchie-tgzt8b`, HEAD `f230ebd` ("Remove map access gate; record deploy 6ad77b77").

Conventions used in this document:

- `file:line` cites are to the working tree at the commit above. Template line numbers refer to `build_template.html` after gate removal.
- "verified 2026-10-20" marks facts established live in this session by the operator tooling (Netlify, Supabase, GitHub Actions, prod site). They are not derivable from repo code and are cited as given.
- "Not Configured / Absent from Source Code" means a grep of the repo found nothing.
- No secret values are reproduced here. Environment variables are listed by name only.
- Source data files (`combined_points.csv`, `combined_geoms.geojson`, `data/**`, `outputs/refresh/*`) were not opened for this document. Only CSV headers, YAML, scripts, docs, and aggregate counts computed in Python were used.

---

## 1. System Architecture & High-Level Data Flows

### Project Purpose

Internal and peer-distributed Texas energy-infrastructure web map for Land Resource Partners (operator: Andrea Himmel; `CLAUDE.md`). Primary subject area is the Permian/Trans-Pecos corridor around the Caramba North tract (Pecos County): ERCOT generation and interconnection queue, EIA-860 plants and storage, wind/solar, transmission and substations, TPIT planned upgrades, pipelines, RRC wells and drilling permits, tax abatements, data-center anchor projects, OXY (Occidental) footprint, broadband coverage, and reference geography (`ARCHITECTURE.md` §5; `layers.yaml`, 39 layers).

The repo also hosts non-map deliverables built from the same layer data: the Caramba North Offering Memorandum set, decks and briefs, the OXY dossier, and the "Grid Wire" intelligence-series production files (`outputs/reports/`, `scripts/om2/`, `docs/grid-wire-*`). Those are downstream consumers of the map data, not part of the web app.

Live site: `https://lrp-tx-gis.netlify.app`, Netlify siteId `01b53b80-687e-4641-b088-115b7d5ef638` (verified 2026-10-20). Current deploy `6ad77b77a79fe4d03c8ce377` (2026-10-20): same tiles and data as prior deploy `6a3adddefa163a0a17902c54` (2026-06-23), with the access gate removed. There is no longer any login or access logging (verified 2026-10-20; `WIP_OPEN.md:10-15`).

### Architectural Diagram/Flow

Run-time (user interaction):

```
Browser
  │  GET /                         (index.html, ~144 KB template + inlined LAYERS registry JSON)
  ▼
Netlify CDN (static files only; no functions, no edge functions, no netlify.toml)
  │  _redirects: /*  /index.html  200   (SPA fallback; build.py:1215)
  │  _headers:   /tiles/*  CORS *, Cache-Control public,max-age=3600,must-revalidate (build.py:1203-1211)
  │
  ├─ /vendor/maplibre-gl.js (4.7.1), pmtiles.js, turf.min.js, maplibre-gl.css   same-origin
  ├─ /sprite/sprite{,@2x}.{png,json}                                            5 icons
  ├─ /data/<layer>.json            slim attribute arrays for stats panel (wells_permian6, permits_permian6 only)
  └─ /tiles/<layer_id>.pmtiles     one PMTiles archive per layer
        ▲
        │  HTTP Range requests (pmtiles.Protocol, `pmtiles://tiles/<id>.pmtiles`, build_template.html:458-459, 691-697)
        │
MapLibre GL JS (WebGL) ── vector layers from PMTiles ── client-side filter expressions (setFilter)
        │                                                    time scrubber, stats panel, popups, measure (turf)
        ├─ Basemap raster/style requests to third parties:
        │     Esri World_Imagery / World_Street_Map (arcgisonline.com)
        │     Carto "voyager" rastertiles (cartocdn.com)
        │     OpenFreeMap liberty style + glyph PBFs (tiles.openfreemap.org)
        │     USGS NAIP ImageServer (imagery.nationalmap.gov)
        ├─ Google Fonts (Inter) at page load
        └─ SheetJS 0.18.5 from cdn.jsdelivr.net, loaded on demand for XLSX export only (build_template.html:1635-1641)
```

Build-time (operator machine, or GitHub Actions runner via `build-and-deploy.yml`):

```
Sources (public datasets; see §3)
   │  refresh_*.py / fetch_*.py / scrape_*.py / parse_rrc.py / transform_*.py / geocode_*.py / build_oxy_*.py
   ▼
Canonical committed inputs
   combined_points.csv        (layer_id-tagged points; 40,917 rows, 32 columns)
   combined_geoms.geojson     (layer_id-tagged lines/polygons/points; 6,705 features)
   data/oxy/*.geojson, data/hifld/*.geojson, data/datacenters/dc_anchors.json   (standalone, small)
   data/wells_permian6.csv, data/permits_permian6.csv                            (standalone, GITIGNORED, regenerated from RRC)
   │
   ▼  python3 build.py   (build.py:1421 main)
   1. rmtree DIST; regenerate sprite via cairosvg/Pillow (build_sprite.py); copy vendor/
   2. load layers.yaml; pre-scan tax_abatements into fuzzy-join index
   3. one-pass split combined files → /tmp/gis_build/split/<layer_id>.ndjson (build.py:74-75)
   4. per layer: optional filters (exclude_within, min_spud_year, exclude_recompletions,
      reclassify_inactive_production, keep_technology) → subprocess `tippecanoe -fo ... -l <id> <flags>`
      (prebuilt layers: copy <id>.pmtiles from PROJECT, UPLOADS, or the live prod URL)
   5. compute_filter_stats → filter UI metadata; write_stats_attrs → dist/data/<layer>.json
   6. render_html: substitute /*__LAYERS__*/ and /*__BUILD_ID__*/ into build_template.html → dist/index.html
   7. write dist/_headers, dist/_redirects; print BUILD REPORT (built / missing / errored)
   ▼
dist/  (index.html, tiles/*.pmtiles, data/*.json, vendor/, sprite/, _headers, _redirects)
   │
   ▼  bash scripts/deploy.sh --rebuild
   zip dist → POST https://api.netlify.com/api/v1/sites/<siteId>/deploys (Bearer NETLIFY_PAT)
   → poll prod `/` md5 == local dist/index.html md5 → verify_deployed_layers.py (pmtiles tilestats over Range)
   ▼
bash scripts/close-out.sh <branch> <deployId> "<msg>"   (push branch, merge --no-ff to main, push, delete branch)
```

Components that the request asked to be called out explicitly:

| Component | Status |
|---|---|
| API gateway | Not Configured / Absent from Source Code. No API routes, no Netlify Functions or Edge Functions, no `netlify.toml`. The only server-side rule is the `_redirects` SPA rewrite generated at `build.py:1215`. |
| AI orchestration layer | Not Configured / Absent from Source Code as a runtime component. The only LLM call in the repo is the batch script `scripts/refresh_dc_anchors.py` (single-shot Messages API calls, no tools, no agent loop, no memory, no retrieval). The map itself calls no AI. |
| GIS processing engines | Build-time only: tippecanoe (felt fork) invoked by `build.py:764-779`; Python `shapely`, `pyshp`, `pyproj.Geod`, `rapidfuzz`, `python-pmtiles` in scripts; client-side `turf.js` for measure. No GDAL/ogr2ogr, GeoPandas, Fiona, Mapshaper, or tile server (grep clean). |
| Back-end spatial/vector databases | Not Configured / Absent from Source Code. No PostGIS, no vector/embedding store, no database client in build or runtime code. State is flat files in git. See §2 for the Supabase projects that exist outside the repo, and the one SQLite file in `outputs/`. |
| Authentication / access control | None since deploy `6ad77b77a79fe4d03c8ce377` (verified 2026-10-20). `build_template.html` no longer contains gate markup, CSS, script, or Supabase calls (grep for `oxy-gate`/`supabase` in the template returns 0). |

---

## 2. Comprehensive Enterprise Tech Stack & Tooling

### Frontend Mapping & State

| Item | Detail | Source |
|---|---|---|
| Map library | MapLibre GL JS 4.7.1, vendored same-origin | `vendor/maplibre-gl.js` (header cites v4.7.1), `ARCHITECTURE.md` §1 |
| Tile protocol | pmtiles.js (global `pmtiles`), `maplibregl.addProtocol('pmtiles', protocol.tile)` | `vendor/pmtiles.js`; `build_template.html:458-459`. Version stated as 4.3.0 in `ARCHITECTURE.md:9`; not re-verified from the minified file |
| Geometry math | Turf.js (min build) for geodesic length (miles) and area (m² → acres ÷ 4046.856) in the Measure tool | `vendor/turf.min.js`; `build_template.html:2737-2751` |
| Framework | None. Single hand-edited HTML file, token substitution at build. Settled decision: no React/Vue/bundler | `OPERATING.md` §9; `build_template.html` |
| Layer registry | `const LAYERS = /*__LAYERS__*/;` replaced by JSON from `render_html` (id, label, group, geom, color, default_on, sidebar_omit, companions, popup, popup_labels, description, min_zoom, radius, fill_opacity, line_width, text_halo, color_steps, features, filterable_fields) | `build.py:1142-1198`; `build_template.html:357` |
| Basemaps | `esri_imagery` (default), `esri_streets`, `carto_light` (rastertiles/voyager), `openfreemap` (liberty vector style), `naip` | `build_template.html:387-412`; default at `:448` |
| Initial style | Map is constructed with `carto_light`, then `applyBasemap(initBase)` runs on `load` if different | `build_template.html:461-465, 2856` |
| Sidebar / grouping | Grouped checkboxes ordered by `GROUP_ORDER`; per-layer filter panels; saved views dropdown | `build_template.html:2436, 2463, 2551-2593` |
| Draw styling | Per-geometry `layerPaint`; data-driven radius/width (`SIZING_RULES`); special color expressions for `ercot_queue`, `dc_anchors`, oil/gas | `build_template.html:498-684` |
| Line casing / fill outline / icons | White casing under colored lines (width > 0.75); 2 px outline on fills; icon symbol layers at minzoom 9 for `ICON_MAP` ids | `build_template.html:688-770` |
| OXY draw order | `raiseOxy()` moves `oxy_*` layers to top after every (re)add | `build_template.html:790-797` |
| Filters | Filter types `numeric`, `date_range`, `categorical`, `text` compiled to MapLibre expressions and applied with `map.setFilter` (client-side, on already-loaded tiles) | `build_template.html:831-901` |
| Time scrubber | Year cutoff on `spud_year` (wells) / `permit_year` (permits); range derived from filter-stat min/max of those fields; default range 2026–2026 if neither layer carries stats | `build_template.html:825-830, 1872-1992` |
| Stats panel | Fetches `data/<layer>.json` (permits_permian6, wells_permian6), computes counts, depth stats (Tukey), decade histograms, county-role compare; exports CSV, Markdown, PDF (`window.print`), XLSX (SheetJS from jsdelivr) | `build_template.html:1151-1870` (fetch at `:1439`) |
| Wells summary panel | Separate cache, fetches `data/wells_permian6.json` | `build_template.html:2219-2417` (fetch at `:2409`) |
| Share / state | URL hash: `lat, lon, zoom, layers, base, filters (JSON), sb`. `layers` omitted when equal to defaults | `build_template.html:424-443, 2595-2611` |
| Popups | Click only. Dumps every populated property except `layer_id`, `source`, `source_date`; footer prints `source · source_date` if present. `L.popup` field list from `layers.yaml` is carried into the registry but is not used by `featurePopupHtml`; only `popup_labels` is. `caramba_north` popups disabled | `build_template.html:2187-2217, 2419-2434` |
| Measure | Click vertices; distance (mi) and area (ac); mobile vertex radius 12 px | `build_template.html:2711-2818` |
| Print | Landscape print view with active-layer legend and "CONFIDENTIAL — <date>" watermark element (still present after gate removal) | `build_template.html:349, 2656-2687` |
| Mobile | `max-width: 768px` media queries; rotation disabled on touch; drawer sidebar | `build_template.html:210-262, 478-496` |
| Fonts | Inter via Google Fonts `<link>`; map labels use `Noto Sans Bold` glyphs from OpenFreeMap | `build_template.html:8-10, 711` |
| Persistent browser state | None (no localStorage/cookies); all state lives in the URL hash | grep of template |

### Core Back-End & GIS Processing Engines

| Engine | Role | Where |
|---|---|---|
| Python 3 (3.11 in CI) | Build driver, refresh/ETL scripts | `build.py`, `scripts/*.py`, `.github/workflows/*.yml` |
| tippecanoe (felt fork) | GeoJSON/NDJSON → PMTiles (`-fo <out> -l <layer_id> <per-layer flags> <ndjson>`); `--read-parallel` deliberately removed (lock errors) | `build.py:764-779`; `ARCHITECTURE.md:15` |
| python-pmtiles | Reads `tilestats` from prebuilt/prod PMTiles (`read_pmtiles_feature_count`; `verify_deployed_layers.py`) | `build.py:46-68`; `scripts/verify_deployed_layers.py:99-124` |
| PyYAML | Reads `layers.yaml` | `build.py:1375, 1454` |
| cairosvg + Pillow | Sprite sheet rasterization (`build_sprite.py`), imported unconditionally by `build.py:43` | `build_sprite.py:1-138` |
| shapely, pyshp | County polygons, `STRtree` point-in-county lookup, `representative_point()`, polygon clipping | `scripts/geocode_ercot_queue.py:66, 280-330`; `scripts/extend_county_labels.py`; `scripts/refresh_fcc_fiber_coverage.py` |
| pyproj `Geod` | WGS84 geodesic polygon area for drilling-permit density | `scripts/build_drilling_density.py:15, 26, 47` |
| rapidfuzz | Name matching for ERCOT queue geocoding | `scripts/geocode_ercot_queue.py` |
| requests / urllib | HTTP fetch (RRC GoAnywhere, W-1, EIA, ArcGIS, Comptroller, Anthropic) | per script |
| BeautifulSoup (`bs4`) | County commissioners-court agenda HTML | `scripts/scrape_abatements.py` |
| openpyxl | EIA-860 and TCEQ xlsx parsing | `scripts/refresh_eia860.py`, `scripts/refresh_tceq_gas_turbines.py` |
| Playwright + headless Chromium | OM exhibit capture from the live map; HTML→PDF | `scripts/capture_om_exhibits.py`, `scripts/om2/_print.mjs` (Chromium path `/opt/pw-browsers/chromium`) |
| python-docx, matplotlib, pptxgenjs, docx (npm), sharp, react-icons | Report/deck builders (not in the map build path) | `scripts/build_brief_*.py`, `scripts/build_deck_*.js`, `scripts/render_icon_set.js` |
| WeasyPrint (+ Jost font) | Grid Wire PDFs | `outputs/reports/source/build_pdf*.py`; `docs/principles.md` |
| Netlify REST API | Deploy (zip POST to `/api/v1/sites/<id>/deploys`) | `scripts/deploy.sh:149-168` |
| netlify-cli | Deploy path used only by the (never-run) GitHub workflow | `.github/workflows/build-and-deploy.yml:84-111` |
| GitHub Actions | `dc-anchors-refresh.yml` (weekly), `build-and-deploy.yml` (manual) | `.github/workflows/` |

Dependency declaration: `Not Configured / Absent from Source Code`. There is no `requirements.txt`, `pyproject.toml`, `package.json`, or lockfile. `scripts/bootstrap-claude-code.sh:39` installs only `pyyaml pmtiles requests`; `build.py` additionally needs `cairosvg` and `Pillow` (via `build_sprite.py`), which the bootstrap does not install (`scripts/session-open.sh:30-37` installs `cairosvg` separately).

### Spatial & AI Databases

| Store | Status |
|---|---|
| PostGIS / PostgreSQL / SpatiaLite | Not Configured / Absent from Source Code. |
| Vector DB / embeddings / RAG index | Not Configured / Absent from Source Code. |
| Canonical data store | Flat files in git: `combined_points.csv`, `combined_geoms.geojson`, `data/**`, `layers.yaml`. |
| Derived stores | `dist/tiles/*.pmtiles` (gitignored, `*.pmtiles`), `dist/data/*.json` (stats attributes). |
| SQLite | One file, unrelated to the map: `outputs/reports/special/stranded-iron-20260727/global_rig_registry.db` (offshore drilling-rig registry for a Grid Wire special report; tables `rigs`, `power_plants`, `valuations`, `status_history`, `sources`, `segment_totals`; non-spatial; seeded by `expand_db.py`; plan in `GLOBAL_RIG_REGISTRY_PLAN.md`). |
| Supabase project `xvlpperttnedsduscgnq` ("10th-Muses") | External to the repo (verified 2026-10-20). Hosts edge functions `oxy-gate`, `oxy-track`, `oxy-stats` plus unrelated `promo-login-temp` and `tmp-*`. All were redeployed 2026-10-14 with `verify_jwt=true`, which broke the gate. The map no longer calls them. Repo residue: `outputs/reports/OXY-analytics-dashboard.html:76` still points at `…/functions/v1/oxy-stats` (the dashboard reads tables `oxy_sessions`/`oxy_events`, per its footer text, `:72`). No migrations or function source for these exist in the repo (no `supabase/` directory). |
| Supabase project `rhglbwoxuzgwoptycspc` ("lrp-tx-gis-rig") | Created 2026-08-24, no edge functions (verified 2026-10-20). Repo search (`supabase`, project ref, `lrp-tx-gis-rig`, `migrations`, `schema baseline`, `\brig\b` in code and in `git log --all`) finds no reference to this project and no migration or schema files. The only rig-related repo artifacts are commits `3c7bf53`, `86bad87`, `74c7817` (Stranded Iron special report plus the SQLite registry above). The PR "rig schema baseline" is not visible from the repo working tree. |

### AI Orchestration & Foundation Models

| Item | Detail |
|---|---|
| Only in-repo LLM use | `scripts/refresh_dc_anchors.py` (weekly via `.github/workflows/dc-anchors-refresh.yml`). |
| Model string (exact) | `claude-sonnet-4-5-20250929` (`scripts/refresh_dc_anchors.py:50`). Written into the output JSON field `model`. |
| API | Raw `urllib` POST to `https://api.anthropic.com/v1/messages`, header `anthropic-version: 2023-06-01`, `max_tokens = 2000`; no SDK, no tools, no streaming, no temperature override (`:49-51, 79-113`). |
| Retries | 3 attempts, `5 s × attempt` backoff; HTTP 401 re-raises immediately (`:97-113`). |
| Inputs | Each `dc_anchors.json` entry (minus `sources`) plus up to 30,000 chars per source page; each page read capped at 200,000 bytes; fetch timeout 30 s, 3 attempts (`:57-76, 151-198`). |
| Output | `outputs/refresh/dc_anchors_proposed.json` via `tempfile` + `os.replace`. Never auto-applied. Workflow opens a PR containing only that file; review checklist says never merge as-is. |
| Scope guard | The system prompt forbids proposing changes to coordinates, county, name, or developer; only `status`, `capacity_mw_announced`, `commissioned_target`, `power_source`, `additional_sources` (`:116-148`). |
| Other LLM use in code | None. The map, build, and other refresh scripts make no LLM calls. |
| Operator tooling (outside code) | Claude Code sessions run builds and deploys per `CLAUDE.md`. A scheduled "daily refresh" routine exists outside the repo and logged `outputs/refresh/daily/<date>.md` (90 files, last `2026-08-19.md`; verified 2026-10-20). Its definition is not in the repo. |
| Orchestration framework, agent loop, eval harness, prompt registry, token metering | Not Configured / Absent from Source Code. |

---

## 3. Geospatial Data Pipelines & ETL Infrastructure

### Ingestion Pipelines

Cadence is as claimed in repo docs (`ARCHITECTURE.md` §5, `docs/refresh_automation_plan.md` §1/§3), not as observed. "Automation" is what actually runs unattended. Last-run evidence is from the repo (file dates, `docs/layer_inventory_2026-05-13.md`, `outputs/refresh/`, `WIP_OPEN.md`), not from running anything.

| Layer(s) | Script | Source URL | Cadence claimed | Automation status | Last-run evidence |
|---|---|---|---|---|---|
| `wells_permian6` | `scripts/fetch_rrc.py wells` → `scripts/parse_rrc.py wells` (chained by `build.py refresh wells`, `build.py:1506`) | `https://mft.rrc.texas.gov/link/<UUID>` + POST `…/webclient/godrive/PublicGoDrive.xhtml` (folder UUID `b070ce28-…`, file `dbf900.txt.gz`) | Weekly | Manual trigger (`refresh wells.`). The planned weekly workflow does not exist. | Output `data/wells_permian6.csv` is gitignored and absent from this checkout; 2026-05-13 per refresh plan |
| `permits_permian6` | `scripts/fetch_rrc.py permits` → `scripts/parse_rrc.py permits` | Same host, folder UUID `f5dfea9c-…` (daf420 EOM + Lat/Lon monthly snapshots) | Monthly | Manual. `build.py refresh permits` exits 2 with a stale "scoped-out" message (`build.py:1506-1515`); use the scripts directly (as `CLAUDE.md` does) | Output gitignored and absent; 2026-05-13 |
| permits backfill 1976–2017 | `scripts/scrape_rrc_w1.py` (listing) → `scripts/scrape_rrc_w1_detail_coords.py` (lat/lon, resumable, ~7 h at 1.5 s throttle) | `https://webapps.rrc.state.tx.us/DP/initializePublicQueryAction.do` | One-time overnight | Manual, nohup | Scratch `outputs/refresh/rrc_w1_*` is gitignored; not present |
| RRC drilling permits pending | `scripts/fetch_rrc.py pending` | folder UUID `0ad92a65-…` | n/a | Manual | none |
| `oxy_drilling_permits` | `scripts/build_oxy_drilling_permits.py` (reads cached `data/rrc_raw/daf420.dat.*`) | Derived from RRC EOM snapshots | With permits | Manual | Deploy of 2026-06-23 (294 permits; `WIP_OPEN.md`); output `data/oxy/oxy_drilling_permits.geojson` |
| Well production status | `scripts/fetch_pdq_dump.py` → `scripts/build_lease_status.py` → `scripts/build_well_prod_status.py` | `https://mft.rrc.texas.gov/link/1f5ddb8d-329a-4459-b7f8-177b4f5ee60d` (`PDQ_DSV.zip`, ~3.44 GB) | Monthly (RRC: last Saturday) | Manual | `data/lease_status.csv` (33,088 rows), `data/well_prod_status.csv` (69,056 rows) committed |
| `eia860_plants`, `eia860_battery`, `solar` | `scripts/refresh_eia860.py [--year]` | `https://www.eia.gov/electricity/data/eia860/xls/eia860<year>.zip` (fallback to archive path); requires `Referer` header | Annual | Manual | `outputs/refresh/eia860_*_2026-04-25.csv`; refresh plan says 2026-04-28 |
| `wind` | `scripts/refresh_uswtdb.py` | `https://eersc.usgs.gov/api/uswtdb/v1/turbines` (PostgREST, `t_state=eq.TX`) | Quarterly/annual | Manual. Upstream API cert expired (verified 2026-10-20) | `outputs/refresh/wind_2026-04-25.csv` |
| `tceq_gas_turbines` | `scripts/refresh_tceq_gas_turbines.py` | `https://www.tceq.texas.gov/downloads/permitting/air/memos/turbine-lst.xlsx`; geocode via OSM Nominatim | Per filing | Manual | `outputs/refresh/tceq_gas_turbines_2026-04-25.csv`, `CHANGELOG.md` |
| `tax_abatements` (LDAD) | `scripts/scrape_ldad.py` → `scripts/transform_ldad.py` | `https://api.comptroller.texas.gov/open-data/v1/tables/ch312-abatement?limit=10000` | Weekly (planned) | Manual | `outputs/refresh/comptroller_ldad_2026-04-29.csv` |
| `tax_abatements` (court agendas) | `scripts/scrape_abatements.py` → `scripts/transform_abatements.py` | `https://www.co.pecos.tx.us/category/notices-announcements/commissioners-court-agendas/`; `https://www.reevescounty.org` (Akamai blocks datacenter egress) | Weekly (planned) | Manual; only Pecos and Reeves adapters validated | `data/abatements/abatement_hits_20260424_092810.csv` (pinned snapshot; later probes gitignored) |
| `hifld_*` (4 layers) | `scripts/fetch_hifld.py <slug> <FeatureServer URL>` (bbox `-104.0,30.0,-101.0,32.6`, inSR/outSR 4326) | HIFLD/EIA ArcGIS FeatureServers (URLs per `docs/refresh_automation_plan.md` §3) | Quarterly | Manual | `data/hifld/*.geojson`, 2026-05-13 |
| `fcc_fiber_coverage` (file not in layers.yaml today) | `scripts/refresh_fcc_fiber_coverage.py` | `https://services8.arcgis.com/peDZJliSvYims39Q/arcgis/rest/services/FCC_Broadband_Data_Collection_December_2024_View/FeatureServer/5` | Biannual | Manual | `outputs/refresh/fcc_fiber_coverage_2026-04-25.geojson` |
| `ercot_queue` | **No fetch script.** `scripts/geocode_ercot_queue.py` (stages 1–3), `scripts/enrich_ercot_coords.py`, `scripts/enrich_ercot_substation_match.py` only post-process rows already in `combined_points.csv` | ERCOT GIS Report (xlsx, manual download) | Monthly | None. Data is a March-2026 snapshot (`WIP_OPEN.md` backlog item 2). Stage 3 blocked on operator CSV `data/ercot_queue_overrides.csv` | `outputs/refresh/_geocode_ercot_log.txt`; plan says 2026-04-25 |
| `tpit_subs`, `tpit_lines` | **No fetch script** (refresh plan: "ERCOT TPIT XLSX scrape, not in repo") | ERCOT TPIT | Monthly | None | 2026-04-25 per refresh plan |
| `substations` | No script (OSM Overpass pulled in chat sessions) | Overpass API | Annual/on demand | None | 2026-04-28 per layer inventory |
| `transmission` | None (HIFLD AGOL, hand-merged) | HIFLD | Annual | None | 2026-04-25 |
| `dc_anchors` | `scripts/refresh_dc_anchors.py` (LLM diff proposer) | Per-entry `sources[].url` in `data/datacenters/dc_anchors.json` | Weekly | **GitHub Actions**, Mondays 06:00 UTC; succeeds; opens proposal PRs (~14 unmerged, verified 2026-10-20) | `dc_anchors.json` `generated: 2026-04-25`, 8 entries |
| `county_labels` (254 TX counties) | `scripts/extend_county_labels.py` | `https://www2.census.gov/geo/tiger/TIGER2024/COUNTY/tl_2024_us_county.zip` | Rare | Manual | Chat 111 |
| `oxy_*` (6 layers) | `scripts/build_oxy_assets.py`, `scripts/build_oxy_map_layers.py` | Extracted from other repo layers; a few county-centroid placements flagged `accuracy="approximate (county centroid)"` | On demand | Manual | `data/oxy/*.geojson` |
| `drilling_permit_density` (not in layers.yaml) | `scripts/build_drilling_density.py` | Counts from `outputs/refresh/rrc_w1_counts.csv` | On demand | Manual | 11 features in `combined_geoms.geojson` |
| Prebuilt: `rrc_pipelines`, `tiger_highways`, `bts_rail` | None in repo | `<id>.pmtiles` from PROJECT, UPLOADS, or live prod `/tiles/` | Rare | Re-pulled from prod on every build (`build.py:793-870`) | n/a |

Automation inventory (verified 2026-10-20): GitHub Actions has `dc-anchors-refresh.yml` (weekly, Mondays, succeeding, opens proposal PRs) and `build-and-deploy.yml` (`workflow_dispatch` only; never run). There is no other automation. `docs/refresh_automation_plan.md` proposes a `weekly-refresh.yml` that was never written. The external daily refresh routine (not in the repo) logged through 2026-08-19 only.

### Data Formats & Protocols

| Stage | Format / protocol |
|---|---|
| Canonical points | CSV, `layer_id,lat,lon,name,plant_code,county,technology,capacity,sector,inr,fuel,mw,zone,poi,entity,funnel_stage,group,under_construction,commissioned,capacity_mw,operator,voltage,osm_id,depth_ft,use,aquifer,project,manu,model,cap_kw,year,coords_source` (header only). LF line endings, forced in `merge_csv` (`build.py:1218`). Several columns are overloaded per layer (tax-abatement mapping in `ARCHITECTURE.md` §4). |
| Canonical geometries | GeoJSON FeatureCollection; `properties.layer_id` tags features; Z stripped by `_flatten_coords` (`build.py:265`); no top-level `crs` member. |
| Standalone layers | `.csv` (`csv_to_ndgeojson`), `.json` (`dc_anchors_to_ndgeojson`, `build.py:693`), `.geojson` (`geojson_to_ndgeojson`, `build.py:738`). |
| Intermediate | NDGeoJSON per layer in `/tmp/gis_build/split/` (hard-coded path, `build.py:74-75`). |
| Tiles | PMTiles v3 archives, vector, layer name = `layer_id`; served by static hosting via HTTP Range. |
| Client attribute side-cars | `dist/data/<layer>.json`, arrays of slim objects (fields in `STATS_ATTRS_FIELDS`, `build.py:947-957`). Only `permits_permian6` and `wells_permian6`. |
| Upstream protocols | RRC GoAnywhere PrimeFaces (GET landing → JSESSIONID + `javax.faces.ViewState` → POST row id; `scripts/fetch_rrc.py:1-38`); RRC fixed-width ASCII (`dbf900` 247-byte records, segment keys 01/02/03/13; `daf420` records `0108`/`0208`/`14`/`15` — layout reverse-engineered, `docs/rrc_layouts/permit_purpose_codes.md`); PDQ `}`-delimited DSV in a zip; ArcGIS REST `query` with `resultOffset` paging; PostgREST (USWTDB); xlsx (EIA, TCEQ, ERCOT); JSP form scrape (RRC W-1); WordPress/CivicEngage HTML (county agendas); Census TIGER shapefile zip. |
| Reference layouts | `docs/rrc_layouts/` (wba091 wellbore, pending permits, well API manual, pda001, EWA manual). |

### Coordinate Reference Systems (CRS) & Projections

- Storage CRS: WGS84 lon/lat, EPSG:4326, everywhere. Stated in `ARCHITECTURE.md:76-78` ("EPSG:4326, 2D coords"; 6-decimal points; 4-decimal simplified lines/polygons) and `data/datacenters/README.md:31-32`. No file carries a `crs` member; no `EPSG` string appears in code.
- Validation in the build is range only: `-180 ≤ lon ≤ 180`, `-90 ≤ lat ≤ 90`; rows with null lat/lon are dropped (`build.py:331-338, 468-474`). No Texas-bbox check at build.
- RRC wells (`dbf900`, segment 13): `PIC S9(3)V9(7)` zoned decimal with sign overpunch; longitude stored as positive magnitude, parser forces negative; accepts lat 25–38 and |lon| 93–107.5 only (`scripts/parse_rrc.py:225-240`; fragility row in `ARCHITECTURE.md` §9).
- RRC permits (`daf420`, records 14/15): signed 12-char lon and 10-char lat; lon forced negative (`scripts/parse_rrc.py:429-446`). No bounds check on permits.
- `pyproj` is used only for `Geod(ellps="WGS84")` geodesic area (`scripts/build_drilling_density.py:47`). No coordinate transformation anywhere.
- State Plane, NAD27: no references. NAD83: three OXY point sources are labelled NAD83 in their `source` text (`scripts/build_oxy_map_layers.py:144-192`) and are stored as lon/lat with no datum shift. (Outside-repo note: NAD83 vs WGS84 differ by roughly 1–2 m in Texas; not material at map scale.)
- ArcGIS queries: `inSR=4326`, `outSR=4326` (`scripts/fetch_hifld.py:50-51`, `scripts/refresh_fcc_fiber_coverage.py:70-73`).
- Tiling projection: no projection flags are passed to tippecanoe (no `-s_srs`/`--projection`). tippecanoe's behavior is WGS84 GeoJSON in, Web Mercator XYZ tiles out; MapLibre renders in EPSG:3857, matching the raster basemaps.
- Approximate positions: `mpgcd_zone1`, `la_escalera`, `longfellow_ranch`, `gw_ranch` are digitized boundaries labelled APPROXIMATE (`docs/layer_inventory_2026-05-13.md`; `ARCHITECTURE.md` §5). LDAD abatement and some OXY and ERCOT rows sit at county centroids (`coords_source` column: `ldad_county_centroid`, `county_centroid`, `abatement_match`, `substation_match`, `manual_override`).

### Spatial Indexing & Optimization

Tiling flags come from each layer's `tippecanoe:` list in `layers.yaml`; the default if absent is `['-zg']` (`build.py:848, 937`). `-fo` (force overwrite) and `-l <layer_id>` are always added by `run_tippecanoe`.

| Flag set | Layers |
|---|---|
| `-zg` | `cities`, `caramba_north`, `mpgcd_zone1`, `eia860_plants`, `eia860_battery`, `solar`, `tpit_subs`, `ercot_queue`, plus layers below with additions |
| `-zg --extend-zooms-if-still-dropping --simplification=8` | `counties` |
| `-zg -r1 --drop-densest-as-needed --extend-zooms-if-still-dropping` | `wind` (minzoom 7), `permits_permian6` (minzoom 6, sidebar-hidden), `wells_permian6` (minzoom 7) |
| `-zg --drop-densest-as-needed` | `substations` (minzoom 7) |
| `-zg --simplification=8` | `tpit_lines`, `hifld_crude_pipelines`, `hifld_hgl_pipelines` |
| `-zg --simplification=8 --coalesce-densest-as-needed` | `transmission`, `hifld_ng_pipelines` |
| `-Z0 -z14` | all single/few-feature layers: 7 `oxy_*`, `solstice_substation`, `waha_circle`, `labels_hubs` (minzoom 4), `la_escalera`, `longfellow_ranch`, `gw_ranch`, `hifld_ng_processing`, `county_labels` (minzoom 4), `tceq_gas_turbines`, `tax_abatements`, `dc_anchors` |
| Prebuilt (no tippecanoe) | `rrc_pipelines`, `tiger_highways`, `bts_rail` |

Why `-Z0 -z14`: `-zg` silently emits 0-feature tilesets on single-feature inputs (`ARCHITECTURE.md:155`).

Other optimization mechanisms:

- PMTiles internal index: PMTiles v3 directory (Hilbert-ordered tile entries) lets the browser fetch only visible tiles with Range requests. Not configured by the repo; inherent to the format.
- Client min-zoom gating via per-layer `min_zoom` (`build_template.html:704`); icons at minzoom 9.
- Layer toggle default: only `default_on: true` layers are visible at load (layers are still added as sources, but tiles are fetched only for visible layers).
- Filtering is client-side: MapLibre `setFilter` against tile features; no server-side query. Stats panel filters its own `data/<layer>.json` arrays in JS.
- Build-time pruning: `exclude_within` (even-odd ray-cast point-in-polygon against a polygon layer; `build.py:488-550`), `min_spud_year` (1964 for wells), `exclude_recompletions` (drop rows where `completion_year < spud_year`), `reclassify_inactive_production` (join to `data/well_prod_status.csv` by 8-digit API; flags "Marginal or end-of-life" at ≤125 Mcf/d gas and ≤25 bbl/d oil; `build.py:608-667`), `keep_technology` + `keep_county_scope` for `tax_abatements` (`build.py:669`).
- Categorical filter cap: 2000 distinct values, then demoted to text (`CATEGORICAL_CAP`, `build.py:100`).
- Spatial indexing in scripts: shapely `STRtree` for ERCOT-queue-to-county assignment (`scripts/geocode_ercot_queue.py:280-330`). turf is client-side measurement only. No R-tree or spatial index in `build.py`.
- Point sizing is data-driven by capacity, voltage, or depth (`SIZING_RULES`, `build_template.html:498-512`).

---

## 4. Granular Repository Structure & Asset Registry

### Directory-by-Directory Map

| Path | Contents |
|---|---|
| `/` | `build.py` (1,534 lines), `build_sprite.py`, `build_template.html` (2,865 lines at HEAD), `layers.yaml` (1,359 lines, 39 layers), `combined_points.csv` (~5.0 MB), `combined_geoms.geojson` (~2.0 MB), `CLAUDE.md`, `OPERATING.md`, `ARCHITECTURE.md`, `WIP_OPEN.md`, `WIP_LOG.md` (pointer to `git log --merges`), `Readme.md` (document map), `.env.example`, `.gitignore`. Not present: `package.json`, `requirements.txt`, `netlify.toml`, `tests/`, `.env`. |
| `.github/workflows/` | `dc-anchors-refresh.yml` (weekly Mon 06:00 UTC + dispatch), `build-and-deploy.yml` (dispatch only). |
| `vendor/` | `maplibre-gl.js`, `maplibre-gl.css`, `pmtiles.js`, `turf.min.js` (same-origin; added after a third-party CDN load broke MapLibre workers, `build.py:1432-1436`). |
| `sprite/` | `sprite.png/.json`, `sprite@2x.png/.json`; 5 icons (solar, wind, battery, plant, well) regenerated each build by `build_sprite.py`. |
| `data/` | See Spatial Asset Registry. Subdirs: `oxy/`, `hifld/`, `datacenters/` (`dc_anchors.json` + `README.md` schema), `tiger/`, `abatements/`, `bead_bdo/` (xlsx + README; no layer), `fracfocus/` (`DisclosureList_1.csv`, ~60 MB). Loose files: `lease_status.csv`, `well_prod_status.csv`, `wells_howard_loving.csv`, `abatements_court_seed.csv`, `production_permian6.xlsx`, `production_permian6_summary.pdf`. Gitignored and absent here: `data/rrc_raw/`, `data/wells_permian6.csv`, `data/permits_permian6.csv`. |
| `docs/` | `principles.md`, `settled.md`, `refinement-sequence.md` (pointers); `sprint-plan.md`; `refresh_automation_plan.md` (planning only); `layer_inventory_2026-05-13.md`; `redesign_content_brief.md` (OM facts source); `grid-wire-*.md` (series instructions, taxonomy, scheduled-task prompt; `.bak` file); `rrc_layouts/` (PDFs + `permit_purpose_codes.md`); `archive/` (history, `audit-1/CROSS_WALK.md`, `chat127-drilling-permits-point.patch`); `audit-2026-10-20/` (five PNG screenshots of the defects in §7). |
| `outputs/refresh/` | Refresh staging (EIA, wind, TCEQ, LDAD, FCC outputs dated 2026-04-23 to 04-29; `CHANGELOG.md`; geocode log) and `daily/` (90 reports, `2026-08-19.md` last). `rrc_w1_*` scratch is gitignored. |
| `outputs/reports/` | Deliverables: Caramba North OM (HTML/PDF/DOCX/PPTX), decks, briefs, teaser, OXY dossier and deck, special reports (`special/stranded-iron-20260727/`, `special/crusoe-20260922/`), `charts/`, `om_exhibits/` (JPG exhibits, `map_geometry.json`, `vector/` SVG, `icons/`, `_minimalist/`, `_technical/`), `source/` (Grid Wire build scripts and sources), `GRIDWIRE_LOG.md`, `CARAMBA-OM-REBUILD-NOTES.md`, `OXY-analytics-dashboard.html`. |
| `scripts/` | Grouped below. |
| `scripts/om2/` | Second-generation OM builders (`build_om_master.py`, `build_deck_*.py`, `build_brief_*.py`, `build_teaser_prenda.py`), theme/charts (`om_theme.py`, `om_charts.py`), `_print.mjs` (Playwright PDF), `_smoke.py`, `fonts/` (6 CSS font files: archivo, instrumentserif, newsreader, plexmono, plexsans, publicsans). `node_modules` is gitignored and absent. |

Scripts grouped by function:

| Group | Scripts |
|---|---|
| Build / release | `deploy.sh`, `close-out.sh`, `ship.sh` (deploy then close-out), `session-open.sh`, `audit.sh`, `pre-commit`, `verify_deployed_layers.py`, `bootstrap-claude-code.sh`, `bootstrap-windows.ps1` (WSL2 preflight) |
| RRC / Permian ingest | `fetch_rrc.py`, `parse_rrc.py`, `fetch_pdq_dump.py`, `build_lease_status.py`, `build_well_prod_status.py`, `scrape_rrc_w1.py`, `scrape_rrc_w1_detail_coords.py`, `build_drilling_density.py`, `build_oxy_drilling_permits.py` |
| Power / grid / infrastructure ingest | `refresh_eia860.py`, `refresh_uswtdb.py`, `refresh_tceq_gas_turbines.py`, `refresh_fcc_fiber_coverage.py`, `fetch_hifld.py`, `refresh_dc_anchors.py` |
| ERCOT queue geocoding | `geocode_ercot_queue.py`, `enrich_ercot_coords.py`, `enrich_ercot_substation_match.py` |
| Abatements | `scrape_ldad.py`, `transform_ldad.py`, `scrape_abatements.py`, `transform_abatements.py` |
| One-off combined-file edits (historical) | `edit_109b_consolidate.py`, `edit_110c_trans_fix.py`, `edit_local_devs.py`, `extend_county_labels.py` |
| OXY layers and dossier | `build_oxy_assets.py`, `build_oxy_map_layers.py`, `oxy_assets_data.py`, `oxy_maps.py`, `oxy_build_maps.py`, `build_oxy_report.py`, `build_oxy_docx.py`, `build_oxy_deck.py` |
| OM / marketing (consume layer data) | `caramba_om_data.py` (single data model), `build_caramba_om.py`, `build_caramba_om_docx.js`, `build_caramba_om_pptx.js`, `build_brief_executive.py`, `build_brief_technical.py`, `build_deck_{editorial,institutional,mapled,minimalist}.js`, `build_insight_pack.py`, `build_power_gravity_diagram.py`, `extract_map_geometry.py`, `build_vector_maps.py`, `capture_om_exhibits.py`, `build_*_exhibit*.py`, `build_minimalist_exhibit_crops.py`, `build_production_deliverable.py`, `render_icon_set.js` |

### Core Code Modules

| Module | Key locations |
|---|---|
| `build.py` | Paths/env `:71-89`; abatement fuzzy join `:107-212`; combined-file splitters `:314-460`; per-layer filters `:488-690`; `dc_anchors_to_ndgeojson` `:693`; `run_tippecanoe` `:764`; `build_layer` `:782-940`; `STATS_ATTRS_FIELDS`/`write_stats_attrs` `:947-1008`; `compute_filter_stats` `:1011`; `render_html` `:1142`; `write_netlify_config` `:1202`; `merge_csv`/`merge_geojson`/`cmd_merge` `:1218-1418`; `main` `:1421`; `cmd_refresh` `:1506`. |
| `build_template.html` | Basemaps `:387`; hash `:424-443`; map init `:461`; sizing `:498`; paint `:613`; `addLayer` `:688`; filters `:831`; `StatsPanel` `:1151`; `Scrubber` `:1872`; popups `:2187`; `WellsSummary` `:2219`; sidebar `:2463`; saved views `:2551`; `syncHash` `:2595`; `applyBasemap` `:2614`; measure `:2711`; `map.on('load')` `:2820`. |
| `layers.yaml` | Keys in use: `id, file, geom, group, label, color, description, default_on, sidebar_omit, companions, popup, popup_labels, radius, circle_radius, stroke_color, stroke_width, fill_opacity, line_width, min_zoom, show_marker, tippecanoe, prebuilt, filterable_fields, min_spud_year, exclude_recompletions, reclassify_inactive_production, keep_technology, keep_county_scope`. Template also reads `color_steps`, `text_halo`, `exclude_within` (none set in the current YAML). |
| `scripts/deploy.sh` | Build gate `:56-90`; PAT resolution `:92-107`; zip + REST POST `:139-168`; md5 poll `:186-214`; layer gate `:217-229`; deployId echo `:232`. Unused remnants: `MCP_URL`, `mcp_call` (`:109-129`). |
| `scripts/close-out.sh` | Clean-tree check `:64-75`; non-handoff-commit gate `:80-95`; merge `--no-ff` `:112`, push `:118`, branch delete `:124`. |
| `scripts/refresh_dc_anchors.py` | Constants `:49-54`; `SYSTEM_PROMPT` `:116-148`; `process_entry` `:151`; `main` `:237`. |
| `scripts/verify_deployed_layers.py` | Range-read tilestats `:60-124`; exit codes 0/1/2 in the module docstring. |
| `scripts/parse_rrc.py` | County scope `:65-76`; wellbore segments `:78-100, 225-240`; permit record slices `:339-358`; `parse_permits` `:468`. |

### Spatial Asset Registry

39 layers in `layers.yaml` (build report target `built=39 missing=0 errored=0`, `WIP_OPEN.md:17`). Feature counts are aggregates computed this session from combined files and standalone GeoJSON; RRC-derived counts are not computable here (CSV absent).

| # | Layer id | Source file | Geom | Group | Default on | Count |
|---|---|---|---|---|---|---:|
| 1 | counties | combined_geoms | line | Reference | yes | 46 |
| 2 | cities | combined_points | point | Reference | yes | 9 |
| 3 | caramba_north | combined_geoms | fill | Land & Deal | yes | 1 |
| 4–9 | oxy_power, oxy_midstream, oxy_ercot, oxy_permits, oxy_water, oxy_carbon | `data/oxy/<id>.geojson` | point | OXY — Occidental Footprint | yes | 15, 4, 3, 4, 4, 4 |
| 10 | oxy_drilling_permits | `data/oxy/oxy_drilling_permits.geojson` | point | OXY — Occidental Footprint | no | 294 |
| 11–12 | solstice_substation, waha_circle | combined_geoms | point | Local Focal Points | yes | 1, 1 |
| 13 | labels_hubs | combined_geoms | label | Local Focal Points (sidebar-hidden) | yes | 1 |
| 14–16 | la_escalera, longfellow_ranch, gw_ranch | combined_geoms | fill | Local Hyperscale DC & Power Campuses | yes | 1 each |
| 17 | mpgcd_zone1 | combined_geoms | fill | Local Focal Points | yes | 1 |
| 18–21 | eia860_plants, eia860_battery, wind, solar | combined_points | point | Power Generation | no | 1,367; 133; 19,464; 180 |
| 22–23 | substations, tpit_subs | combined_points | point | Transmission & Grid | no | 1,637; 141 |
| 24–25 | transmission, tpit_lines | combined_geoms | line | Transmission & Grid | no | 6,244; 133 |
| 26–28 | hifld_ng_pipelines, hifld_crude_pipelines, hifld_hgl_pipelines | `data/hifld/*.geojson` | line | Energy Infrastructure | no | 907; 21; 15 |
| 29 | hifld_ng_processing | `data/hifld/hifld_ng_processing.geojson` | point | Energy Infrastructure | no | 53 |
| 30 | ercot_queue | combined_points | point | Projects | no | 1,778 |
| 31 | county_labels | combined_geoms | label | Reference | yes | 254 |
| 32 | rrc_pipelines | prebuilt PMTiles | line | Pipelines | no | from tilestats |
| 33 | tceq_gas_turbines | combined_points | point | Permits | no | 13 |
| 34–35 | tiger_highways, bts_rail | prebuilt PMTiles | line | Reference | yes | from tilestats |
| 36 | permits_permian6 | `data/permits_permian6.csv` (gitignored) | point | Permits (sidebar-hidden) | no | RRC-derived |
| 37 | wells_permian6 | `data/wells_permian6.csv` (gitignored) | point | Oil & Gas Spud Wells | no | RRC-derived |
| 38 | tax_abatements | combined_points | point | Permits | no | 1,495 |
| 39 | dc_anchors | `data/datacenters/dc_anchors.json` | point | Projects | no | 8 |

Orphans (data present, no `layers.yaml` entry, therefore not built or served): in `combined_points.csv` the `wells` layer_id (14,700 TWDB rows); in `combined_geoms.geojson` `aquifers` (5), `caramba_south` (1), `water_mains_approx` (3), `drilling_permit_density` (11). `data/tiger/primary_roads_wtx.geojson` (188 features) is not referenced by any layer (`tiger_highways` is prebuilt). `ICON_MAP` in the template (`build_template.html:359`) still keys on `wells`, which no longer matches any layer id.

`ARCHITECTURE.md` §5 lists 32 layers and `OPERATING.md` §5 says "26 entries"; both are stale versus the 39 in `layers.yaml`.

Combined-file layer breakdown (for `merge`): points — cities 9, ercot_queue 1,778, solar 180, substations 1,637, tpit_subs 141, wells 14,700, tceq_gas_turbines 13, eia860_plants 1,367, eia860_battery 133, wind 19,464, tax_abatements 1,495 (total 40,917). Geoms — total 6,705 features across 16 layer_ids (list above plus caramba_north, counties, mpgcd_zone1, tpit_lines, transmission, labels_hubs, waha_circle, solstice_substation, la_escalera, longfellow_ranch, gw_ranch, county_labels).

Supporting spatial/tabular assets: `data/lease_status.csv`, `data/well_prod_status.csv` (production join for wells reclassification), `data/abatements_court_seed.csv` (9 curated Pecos/Reeves rows), `outputs/refresh/*` dated snapshots, `outputs/reports/om_exhibits/map_geometry.json` (clipped geometry bundle for OM vector exhibits), `outputs/reports/om_exhibits/*.jpg` (captured raster exhibits).

### AI Asset Registry

| Asset | Location |
|---|---|
| System prompt (spatial/fact-check, DC anchors) | `scripts/refresh_dc_anchors.py:116-148` (`SYSTEM_PROMPT`) |
| Model + limits | `scripts/refresh_dc_anchors.py:49-54` |
| Input corpus | `data/datacenters/dc_anchors.json` (8 entries, schema in `data/datacenters/README.md`) |
| Output / proposals | `outputs/refresh/dc_anchors_proposed.json` (produced in CI; committed only on the PR branch) |
| Workflow | `.github/workflows/dc-anchors-refresh.yml` |
| Other prompts, tool definitions, agents, fine-tunes, embeddings, eval sets | Not Configured / Absent from Source Code |
| Operator instruction docs (guide human/agent sessions, not application prompts) | `CLAUDE.md`, `OPERATING.md`, `docs/grid-wire-master-instructions-v4.md`, `docs/grid-wire-scheduled-task-prompt.md`, `docs/redesign_content_brief.md` |

---

## 5. Local Environment, Configuration & Seeding

### Prerequisites & Native Tooling

| Need | Used by | Status in this container (verified 2026-10-20) |
|---|---|---|
| Python 3 (3.11 in CI) with `pyyaml`, `pmtiles`, `requests` | `build.py`, `verify_deployed_layers.py`, fetchers | `yaml` present; `pmtiles` not installed |
| `cairosvg`, `Pillow` | `build_sprite.py` (imported by `build.py:43`) | `cairosvg` not installed; `Pillow` present |
| tippecanoe (felt fork) | `build.py` | Not installed |
| `curl`, `md5sum`, `zip` via Python, `awk`, `git` | `deploy.sh`, `close-out.sh`, `audit.sh` | Standard |
| Node 22 | OM deck/doc builders | Present at `/opt/node22/bin/node`; npm packages undeclared |
| `.env` | `deploy.sh` (PAT only) | Not present |
| Optional | `shapely`, `pyshp`, `rapidfuzz`, `pyproj`, `openpyxl`, `beautifulsoup4`, `playwright`, `python-docx`, `matplotlib`, WeasyPrint | Per script (see §2) |

Network egress needed at build: only for prebuilt layers (tier-3 pull from `https://lrp-tx-gis.netlify.app/tiles/<id>.pmtiles`); the combined-file build is offline.

### Step-by-Step Installation

Exact commands from `CLAUDE.md`, `scripts/bootstrap-claude-code.sh`, `.env.example`:

```bash
git clone https://github.com/10thMuses/lrp-tx-gis.git
cd lrp-tx-gis
bash scripts/bootstrap-claude-code.sh      # idempotent
```

What the bootstrap does: install tippecanoe (`brew install tippecanoe`, or `sudo apt-get install -y tippecanoe`); `pip install --upgrade pyyaml pmtiles requests`; copy `.env.example` → `.env` if missing; warn on empty `GITHUB_PAT`/`NETLIFY_PAT`; set git identity defaults (`claude@lrp.local`); smoke test `import yaml, pmtiles`. Windows: run `scripts/bootstrap-windows.ps1` first (installs WSL2 Ubuntu, then calls the bash bootstrap).

Gaps to close manually, from code behavior:

```bash
pip install cairosvg Pillow                 # required by build.py via build_sprite.py; not in bootstrap
set -a; . ./.env; set +a                    # build.py does NOT read .env (no dotenv); export LRP_* yourself
export LRP_PROJECT_DIR=. LRP_DIST_DIR=./dist LRP_UPLOADS_DIR=./uploads
git config core.hooksPath scripts           # optional: enables scripts/pre-commit
```

Verify: `python3 build.py` should end with `built=39 missing=0 errored=0` (RRC-derived layers need their gitignored CSVs; see Mocking & Seeding). `bash scripts/audit.sh` for drift.

Session workflow (`CLAUDE.md`, `OPERATING.md` §4, `docs/refinement-sequence.md`):

```bash
git checkout main && git pull --ff-only
git checkout -b refinement-<slug>               # 2–4 word slug
# ... change, commit with explicit paths (never `git add -A`) ...
bash scripts/deploy.sh --rebuild                # prints deployId on stdout
bash scripts/close-out.sh refinement-<slug> <deploy-id> "<message>"
```

### Comprehensive Environment Schema

Variables actually read by code (grep of `os.environ`, `getenv`, `process.env`, `${{ secrets }}`, shell `${VAR}`). Values are never printed here.

| Group | Variable | Read by | Behavior |
|---|---|---|---|
| Server/DB | none | n/a | No database or server variables exist. |
| Build paths | `LRP_DIST_DIR` | `build.py:84`; workflow sets it to `${{ github.workspace }}/dist` | Output dir. Default `/mnt/user-data/outputs/dist`; **no repo-root fallback**, so unset outside chat mode writes to `/mnt/...`. |
| Build paths | `LRP_PROJECT_DIR` | `build.py:85` (falls back to repo ROOT if path missing); `scripts/build_vector_maps.py:24`, `caramba_om_data.py:32`, `extract_map_geometry.py:25`, `om2/om_theme.py:18`, `om2/om_charts.py:21` | Source root. Default `/mnt/project`. |
| Build paths | `LRP_UPLOADS_DIR` | `build.py:86` | Tier-2 prebuilt PMTiles dir. Default `/mnt/user-data/uploads`. |
| Mapping/GIS tokens | none | n/a | No Mapbox/MapTiler/Esri tokens; all basemaps are keyless. Carto "voyager" rastertiles shows an API-key watermark (see §7). |
| AI/LLM | `ANTHROPIC_API_KEY` | `scripts/refresh_dc_anchors.py:238`; `dc-anchors-refresh.yml:36` (`secrets.ANTHROPIC_API_KEY`); noted in `build-and-deploy.yml:15` | Exit 1 if unset. |
| Deploy/CI | `NETLIFY_PAT` | `scripts/deploy.sh:98-107` parses it from `.env`, then `/mnt/project/CREDENTIALS.md`, then shell var `NETLIFY_PAT_ENV` | Exit 3 if absent. Used as Bearer token to `api.netlify.com`. |
| Deploy/CI | `NETLIFY_PAT_ENV` | `scripts/deploy.sh:102` | Shell fallback for the PAT. |
| Deploy/CI | `VERIFY_LAYERS` | `scripts/deploy.sh:217` | `0` skips the layer-integrity gate (default `1`). |
| Deploy/CI | `ALLOW_LARGE` | `scripts/pre-commit` | `1` lets staged files >1 MB through. |
| Deploy/CI | `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID` | `build-and-deploy.yml:89-90` (`secrets.*`) | Required for the manual cloud deploy; no evidence in repo that either secret is set. |
| Deploy/CI | `GITHUB_TOKEN` | `dc-anchors-refresh.yml:69` | Auto-provided; used by `peter-evans/create-pull-request@v6`. |
| Deploy/CI | `GITHUB_PAT` | `.env.example`, `bootstrap-claude-code.sh` (presence check only) | Not read by any script. `OPERATING.md` §6 says it is Contents R/W only, no PR permission. |
| Scripts (legacy) | `LRP_GIS_URL`, `LRP_GIS_EMAIL`, `LRP_GIS_PASSWORD` | `scripts/capture_om_exhibits.py:25-27` | Gate-login inputs. **Defaults for the email and password are hard-coded in the source** (lines 26–27). The gate no longer exists; remove the defaults and rotate that password if it is used anywhere else. |
| Scripts | `HTTPS_PROXY`, `https_proxy` | `scripts/capture_om_exhibits.py:241` | Proxy for Playwright. |

`.env` is gitignored; `CREDENTIALS.md` is gitignored (chat-mode credential registry, not in the repo).

### Mocking & Seeding

- Test suite, fixtures, mock servers: Not Configured / Absent from Source Code.
- Committed seed data (sufficient for most layers): `combined_points.csv`, `combined_geoms.geojson`, `data/oxy/*`, `data/hifld/*`, `data/datacenters/dc_anchors.json`, `data/well_prod_status.csv`, `data/lease_status.csv`, `data/abatements_court_seed.csv`, `data/abatements/abatement_hits_20260424_092810.csv` (the one un-ignored probe file).
- Not seedable from git: `wells_permian6` and `permits_permian6` (CSVs gitignored). Regenerate with:

```bash
python3 scripts/fetch_rrc.py wells && python3 scripts/parse_rrc.py wells        # or: python3 build.py refresh wells
python3 scripts/fetch_rrc.py permits && python3 scripts/parse_rrc.py permits
python3 build.py
```

  `dbf900.txt.gz` is ~366 MB compressed (~1.97 GB uncompressed); fetch is throttled at 1.5 s per request.
- Prebuilt layers (`rrc_pipelines`, `tiger_highways`, `bts_rail`) seed from prod via the tier-3 URL, so a first build offline marks them `ERROR` (counts toward `errored`).
- Without the RRC CSVs the build marks the two layers `MISSING` (`build.py:875, 897`); `MISSING` does not set `errored`, so `deploy.sh` would still proceed. The post-deploy layer gate (`verify_deployed_layers.py`) is what would catch it.
- Data-quality seeds for the abatement layer and OXY layers are produced by scripts (`transform_ldad.py`, `build_oxy_map_layers.py`), both idempotent.
- Cloud build: `build-and-deploy.yml` checks out git only, so it cannot produce the two RRC layers either.

---

## 6. Map Tiling, Performance & AI Evaluation

### Tiling Strategy

- One PMTiles archive per layer, layer name = `layer_id`, at `/tiles/<id>.pmtiles`. No combined/multi-layer archive. Total last verified size 29,594 KB for 39 tilesets (`WIP_OPEN.md:19`).
- Source splitting: one pass over each combined file writes per-layer NDGeoJSON (`build.py:314, 417`), then tippecanoe runs serially per layer (parallel reads removed for lock errors, `build.py:764-770`).
- Zoom strategy: `-zg` (auto max zoom) for ordinary layers; explicit `-Z0 -z14` for few-feature layers; dense layers add `-r1 --drop-densest-as-needed --extend-zooms-if-still-dropping`; lines add `--simplification=8` and optionally `--coalesce-densest-as-needed`. Flag table in §3. No `--maximum-tile-bytes`, `--no-feature-limit`, or buffer overrides, so tippecanoe defaults apply.
- Client gating: `min_zoom` on `wind` 7, `substations` 7, `wells_permian6` 7, `tpit_subs` 6, `permits_permian6` 6, `labels_hubs` 4, `county_labels` 4; map `minZoom 3`, `maxZoom 18` (`build_template.html:466-467`).
- Large/standalone data: prebuilt PMTiles for heavy layers; `parcels_pecos` (14,720 polygons) and `fcc_fiber_coverage` were prebuilt/standalone in earlier catalogs but have no `layers.yaml` entry now.
- Per-feature data volume control: wells/permits carry only the fields needed; the stats side-car JSON is limited to 8–10 attributes per row (`STATS_ATTRS_FIELDS`).

### Caching Strategies

| Layer | Implementation | Source |
|---|---|---|
| CDN headers for tiles | `/tiles/*`: `Access-Control-Allow-Origin: *`, `Cache-Control: public, max-age=3600, must-revalidate`, `Content-Type: application/octet-stream`. `/*.pmtiles`: CORS and content type only. | `build.py:1203-1211` (generated `dist/_headers`; do not hand-edit) |
| Headers for `index.html`, `vendor/`, `sprite/`, `data/*.json` | Not Configured / Absent from Source Code (Netlify defaults apply). | n/a |
| Build-id cache-bust | `/*__BUILD_ID__*/` = UTC timestamp + 4-byte hex nonce, injected into an HTML comment at `build_template.html:2` and used as the md5-parity readiness signal by `deploy.sh`. Removing it breaks the deploy poll. | `build.py:1196-1198`; `OPERATING.md` §4; `WIP_OPEN.md` Process notes |
| Prod `curl` quirks | Default UA gets 503 and HEAD on root 503 even when GET is healthy; use `-A "Mozilla/5.0"` and GET. CDN warm-up 45–90 s. | `ARCHITECTURE.md` §8; `scripts/deploy.sh:195` |
| Browser caching | HTTP caching only; PMTiles range responses cached per HTTP rules. Service worker, `localStorage`, IndexedDB: Not Configured / Absent from Source Code. | grep |
| Stats side-car cache | In-memory per page load (`cache` objects at `build_template.html:1163, 2223, 2402-2415`). | template |
| Server-side/app cache, tile cache invalidation | Not Configured / Absent from Source Code (static hosting only). Note `_redirects` rewrites any non-existent path to `index.html` with status 200, so a missing `/data/<layer>.json` is served as HTML (the JSON parse then fails and the panels fall back to empty arrays). | `build.py:1215`; `build_template.html:2409` (`.catch(() => [])`) |

### Evaluation & Validation

Build-time:

- Build report per layer with statuses `OK`, `MISSING` (no rows/file), `ERROR` (tippecanoe or prebuilt failure), `EMPTY` (standalone layer with 0 kept features). Summary line `built=N missing=M errored=E tiles_total=… KB` (`build.py:1486-1503`). Only `errored>0` blocks deploy.
- Prebuilt sanity: PMTiles smaller than 1,024 bytes is an `ERROR` (`build.py:855`).
- Row validation: lat/lon range check at split and at standalone conversion; null coordinates dropped.
- Filter-stat guards: numeric fields with no data are skipped; categorical fields over 2000 values demoted to text.
- Geometry validity: no `is_valid`/`make_valid` check in `build.py`; `buffer(0)` repairs exist only in county-polygon loaders (`scripts/geocode_ercot_queue.py:305-306`, `scripts/extend_county_labels.py:77-78`). No schema validation, no unit tests, no CI test job.

Deploy-time:

- `deploy.sh` refuses to ship when `build.py` exits non-zero, when no `built=` line exists, when `errored>0`, or when `dist/index.html` or `dist/tiles/` is missing (`:56-90`). Exit codes: 2 build, 3 PAT/args/API, 4 verify, 5 md5 timeout, 7 layer gate.
- Readiness: poll `GET /` until md5 equals local `dist/index.html` (5-minute cap, `:186-214`).
- `scripts/verify_deployed_layers.py`: for every `layers.yaml` id, range-reads `/tiles/<id>.pmtiles` tilestats and fails on 404/unreadable or zero count (exit 1). Cheap (header + metadata only). It runs after the deploy is live, so it blocks the merge, not the publication (`deploy.sh:217-229`).
- Close-out gates: feature branch must carry at least one non-handoff commit beyond `main` (exit 4); clean tracked tree (exit 3); merge conflict exit 5; push rejection exit 6.

Repo hygiene:

- `scripts/audit.sh` (read-only): `OPERATING.md` ≤250 lines, `WIP_OPEN.md` ≤8,192 bytes, merge commits in last 30, close-out message conformance (`Merge <branch>: <title> (deploy <id>|no deploy)`), stranded branches on origin (target 0), repo size. The 2026-10-20 state (about 14 dc-anchors proposal PR branches) would show as stranded.
- `scripts/pre-commit` (opt-in via `git config core.hooksPath scripts`): rejects staged files >1 MB unless `ALLOW_LARGE=1`; warns on non-canonical paths. Its canonical regex lists `README.md` while the file is `Readme.md`, so that file triggers the warning.
- Acceptance protocol by blast radius: `OPERATING.md` §3 rule 8 and §5.

AI evaluation: Not Configured / Absent from Source Code. No golden set, regression prompts, scoring, or logged token/latency metrics for `refresh_dc_anchors.py`. The only control is human PR review against `evidence_url` and `evidence_quote` fields the model must supply, plus the prompt's refusal rules.

---

## 7. Routine Operations, Runbooks & Troubleshooting

### Step-by-Step Runbooks

#### 1. Add or modify a system prompt handling spatial logic

Only one prompt exists: `SYSTEM_PROMPT` at `scripts/refresh_dc_anchors.py:116-148`. It is a fact-check prompt for data-center-anchor attributes; it deliberately excludes coordinates (hard rule 3: no hand-coded coordinates).

1. Branch: `git checkout main && git pull --ff-only && git checkout -b refinement-dc-prompt`.
2. Edit the `SYSTEM_PROMPT` string. Keep the output contract (`id`, `diff`, `additional_sources`, `conflicts`, `fetch_failures`, or `no_change`); the workflow's "meaningful proposal" check reads `diff`, `additional_sources`, `conflicts`, `parse_error`, `error` (`dc-anchors-refresh.yml:46-56`) and `process_entry` parses a single JSON object (code fences stripped, `:174-198`). Changing key names requires changing both.
3. If the prompt should consider spatial fields, note the current rule "Never propose coordinate, county, name, or developer changes". Relaxing it conflicts with `OPERATING.md` §3 rule 3 and needs an operator decision; if allowed, add evidence requirements (`evidence_url`, `evidence_quote`) and a check that proposed `lat`/`lon` fall in Texas before the proposal is written.
4. To change model or limits edit `MODEL` (`:50`), `MAX_TOKENS` (`:51`), fetch caps (`:52-54`, `:70`, `:166`).
5. Smoke-test one entry: `ANTHROPIC_API_KEY=… python3 scripts/refresh_dc_anchors.py <entry-id>` (writes `outputs/refresh/dc_anchors_proposed.json` atomically; do not commit it). Inspect only the proposal file.
6. Commit explicit paths (`git add scripts/refresh_dc_anchors.py`), push, then `bash scripts/close-out.sh refinement-dc-prompt none "<message>"` (no deploy: the prompt does not affect the site).
7. Next Monday's run (or Actions → dc-anchors-refresh → Run workflow) exercises it. Proposals are never auto-merged; applying one means hand-editing `data/datacenters/dc_anchors.json` and its `generated` date, then rebuilding (step 6 of runbook 2).

#### 2. Register and expose a new map layer

1. Branch `refinement-<slug>` from `main`.
2. Produce a refresh file with a documented public source (hard rule 3: no hand-coded coordinates). Points: CSV with `lat`, `lon`, `name`, plus schema columns from the `combined_points.csv` header (reuse overloaded columns per `ARCHITECTURE.md` §4; add `source`/`source_date` if the popup should show attribution; note the combined CSV has no such columns today, so adding them widens the header for all layers). Lines/polygons: GeoJSON, WGS84, 2D.
3. Choose storage. Combined: `python3 build.py merge <layer_id> <refresh_file>` (atomic in-place swap of that layer's rows/features; the header gets the union of columns; the layer must already exist in `layers.yaml`, so add the YAML entry first, `build.py:1356-1418`). Standalone: place under `data/<area>/<id>.geojson` (or `.csv`/`.json`; `.json` is routed to `dc_anchors_to_ndgeojson` and is only valid for that schema) and point `file:` at it. Files ≥10 MB: build the PMTiles elsewhere and set `prebuilt: true`.
4. Append to `layers.yaml` (fields in use are in §4). Minimum: `id`, `file`, `geom` (`point|line|fill|label`), `group` (must be in `GROUP_ORDER`, `build_template.html:2436`, else the sidebar group is not ordered), `label`, `color`, `default_on`, `min_zoom`, `tippecanoe`. Use `-Z0 -z14` for few-feature point layers; `-zg` for ordinary; add `--drop-densest-as-needed` for dense points and `--simplification=8` for lines. Add `popup_labels` for field names, and `filterable_fields` (`numeric|categorical|date_range|text`) for the filter UI. Add `sidebar_omit: true` to hide from the sidebar. Pick a color not already used by a layer in the group (`ARCHITECTURE.md` §10).
5. If the layer needs a time scrubber or stats panel, add its id to `SCRUBBER_TIME_FIELD` (`build_template.html:826`), `STATS_LAYERS` (`:1158`), and `STATS_ATTRS_FIELDS` (`build.py:947`).
6. Build and read the report: `python3 build.py` → expect `built=<N+1> missing=0 errored=0`. `MISSING` means the file/rows were not found; `EMPTY` means all features were filtered or lacked coordinates.
7. Optional local check: serve `dist/` statically (any static server) and toggle the layer.
8. Commit explicit paths only: `git add layers.yaml combined_points.csv` (or the standalone file) and any template/build edits.
9. Deploy and verify: `bash scripts/deploy.sh --rebuild`. Success requires md5 parity and the layer gate passing (new layer live with count > 0). High blast radius per `OPERATING.md` §3: also spot-check `curl -sA "Mozilla/5.0" -o /dev/null -w "%{http_code}" https://lrp-tx-gis.netlify.app/tiles/<id>.pmtiles` and view the layer on prod.
10. Close out: `bash scripts/close-out.sh refinement-<slug> <deployId> "<message>"`.
11. Update the stale catalog in `ARCHITECTURE.md` §5 and `WIP_OPEN.md` "Last deploy".

Caveat: because `deploy.sh` ships whatever the local `dist/` holds, building on a machine without the RRC CSVs omits `wells_permian6` and `permits_permian6` and their `data/*.json` files (see Known Defects).

#### 3. Update database schemas / add a PostGIS table or spatial index

PostGIS: Not Configured / Absent from Source Code. There is no database in the application path, so no schema, migration, or index runbook applies to the map. Equivalent operations on the flat-file "schema":

- Add a column to `combined_points.csv`: handled by `build.py merge`, which appends new columns to the union header (`build.py:1218-1270`). Backfill is blank for other layers.
- Add a filterable or sized field: `layers.yaml` `filterable_fields`, `SIZING_RULES` in the template, and `NUMERIC_KEYS` in `build.py:91` if the value must be numeric in tiles.
- Spatial index equivalents: tippecanoe zoom/drop flags per layer (§3), PMTiles directory (automatic), and `min_zoom` gating.

Supabase: two projects exist outside the repo (§2). Neither is referenced by shipped code now. For the "rig" project `rhglbwoxuzgwoptycspc` (no edge functions), the repo contains no migrations or schema, so a new baseline would be authored in Supabase, not in this repo; no `supabase/` folder or CLI config exists to extend. If PostGIS is ever introduced, it would be a new component: enable the `postgis` extension on that project, add migrations under a new `supabase/migrations/`, and decide how (and whether) the static map would read it, since the current architecture has no server tier. That is a materially different architecture and an operator decision (`OPERATING.md` §2 item 3).

### Troubleshooting Playbooks

**Projection mismatches / geometry drift**

- Symptom: features offset, or Texas points landing in the wrong hemisphere or Gulf.
- Facts: all stored data is lon/lat WGS84; the client is Web Mercator. Known producers of drift are source coordinate conventions, not reprojection (no reprojection code exists).
- Checks: (1) For RRC wellbores, confirm longitude is negative: `parse_rrc.py:235-238` bounds lat 25–38 and |lon| 93–107.5 and forces lon negative; permits do not bound-check (`:429-446`), so a sign or magnitude defect would pass through. (2) Compare `coords_source` values on a suspect layer (`county_centroid`, `ldad_county_centroid`, `abatement_match`, `substation_match`, `manual_override`): a centroid is expected to look "off" and `dc_anchors` renders `county_centroid` at 45% opacity (`build_template.html:594-600`). (3) OXY NAD83-labelled sources are used unshifted (§3). (4) `la_escalera`, `longfellow_ranch`, `gw_ranch`, `mpgcd_zone1` are approximate digitizations by design; `longfellow_ranch` was replaced once for misplacement (`scripts/edit_110c_trans_fix.py`).
- Fix path: correct at the source/transform script, rerun `build.py merge`, rebuild. Never hand-edit coordinates (hard rule 3). Add a range assertion in the parser for permits if a defect is found.

**Slow rendering / complex polygons**

- Symptom: sluggish pan/zoom, long tile loads, jagged or over-simplified lines.
- Levers actually available in code: (1) raise `min_zoom` for dense points (`wind`, `wells_permian6`, `permits_permian6` already gated at 6–7); (2) add `--drop-densest-as-needed` and `-r1`, or `--coalesce-densest-as-needed` and `--simplification=N` for lines (`transmission`, `hifld_ng_pipelines` already use them); (3) reduce per-feature attributes (popups dump every attribute, so wide properties inflate tiles; wells/permits side-car is already slim); (4) lower active layer count (only `default_on` layers load at start); (5) avoid many simultaneous `setFilter` expressions on dense layers; (6) text/categorical filters evaluate `downcase`/`in` per feature client-side.
- Polygon complexity: `parcels_pecos` (14,720 fills) is no longer in `layers.yaml`; the remaining polygons are few and small (`combined_geoms` fills: 1–5 features each). If a heavy polygon layer is added, use `prebuilt: true` PMTiles built with simplification, not per-build conversion.
- Measure: tippecanoe progress is not logged (stderr only returned on failure); time a single layer by running the printed command shape manually.
- Server side: tile cache `max-age=3600, must-revalidate`; first load after deploy can be slow during CDN warm-up (45–90 s).

**AI hallucinations about bounding boxes / invalid GeoJSON**

- Exposure in this repo is small by design: the only LLM step never emits geometry or coordinates and never writes to canonical data (proposal JSON → human PR review). Prompt forbids coordinate/county/name/developer changes; each diff must carry `evidence_url` and a ≤25-word `evidence_quote`.
- If a proposal looks wrong: check `conflicts` and `fetch_failures`; confirm the quote in the cited page; reject the PR (never merge as-is). `parse_error` entries indicate non-JSON model output (`raw_response` truncated to 1,000 chars).
- Invalid GeoJSON risk comes from hand edits and scripts, not the LLM. Build-time safeguards: coordinates flattened to 2D, null geometry skipped, lat/lon ranges enforced. No validity (self-intersection, ring orientation) checks exist; if tippecanoe errors the layer is `ERROR` and deploy is blocked. If a polygon renders as a sliver or missing fill, test with shapely `is_valid`/`buffer(0)` offline on the specific feature (do not print file contents).
- Bounding boxes: only fixed bboxes in code are `HIFLD_BBOX = (-104.0, 30.0, -101.0, 32.6)` (`fetch_hifld.py:28`) and the FCC bbox `-105.998,28.972,-100.115,32.525` (`refresh_fcc_fiber_coverage.py`). Not LLM-generated.

**AI API timeouts / token spikes / DB deadlocks**

- Anthropic API: 60 s timeout per call, 3 attempts, backoff `5 s × attempt`; 401 fails fast; all-attempt exhaustion raises and the entry is recorded as `{"id", "error"}` in the proposal while the run continues (`refresh_dc_anchors.py:97-113, 258-266`). Exit code 3 is documented but the per-entry handler records the error instead of aborting.
- Token control: input is capped by 30,000 chars per source page and a 200,000-byte read cap; output by `max_tokens=2000`. A spike comes from many sources per entry (8 entries now). To reduce, trim `sources[]` for the entry or lower the 30,000 cap. No token/cost logging exists, so inspect usage in the Anthropic console.
- Workflow-level: `timeout-minutes: 15`. If the run times out, no proposal is written.
- Database deadlocks: Not Configured / Absent from Source Code (no database).
- Related non-AI timeouts: RRC fetch 1.5 s throttle; ArcGIS 503 "DNS cache overflow" handled with 5 retries × 10 s (`ARCHITECTURE.md` §9, §12); `deploy.sh` md5 poll 300 s.

### Known Defects (2026-10-20)

Operator-verified live defects, as of this session (verified 2026-10-20), with the repo mechanism where the code explains them:

| # | Defect | Mechanism / location | Suggested fix |
|---|---|---|---|
| 1 | `data/wells_permian6.json` and `data/permits_permian6.json` missing from deploy. Stats panel shows 0; scrubber min = max = 2026. | `write_stats_attrs` only writes when the layer's split NDJSON or `data/<layer>.csv` exists (`build.py:960-980`; guard at `:974`); the CSVs are gitignored (`.gitignore`: `data/wells_permian6.csv`, `data/permits_permian6.csv`) and absent from this checkout, and the 2026-10-20 deploy was built from a mirror of the live file set because tippecanoe is missing (`WIP_OPEN.md:12-14`). The scrubber range comes from filter stats of `spud_year`/`permit_year`, which only exist when those layers are built (`build_template.html:1885-1899`, default `lo = hi = 2026`). With `_redirects` `/* → /index.html 200`, a missing JSON returns HTML and the client falls back to empty arrays (`:1439`, `:2409`). | Regenerate the CSVs (`fetch_rrc.py` + `parse_rrc.py`) on a machine with tippecanoe, run `python3 build.py`, confirm `dist/data/*.json` exist and `verify_deployed_layers.py` passes, then deploy. Consider committing the side-car JSON or removing the gitignore dependency. |
| 2 | NAIP basemap 404 | URL pattern `https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPPlus/ImageServer/tile/{z}/{y}/{x}` (`build_template.html:407-411`). | Point at a working tile endpoint or remove `naip` from `BASEMAPS` and the `<select>`. |
| 3 | "Carto Light" shows an API-KEY watermark | `carto_light` uses `…cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png` (`:388-392`); it is also the initial style before `applyBasemap` swaps to `esri_imagery`. | Replace with a keyless/allowed Carto style (e.g. the OpenFreeMap vector style already present) or a licensed endpoint. |
| 4 | Popups show source/as-of on ~11 of 39 layers | Footer reads `props.source` / `props.source_date` only (`:2192-2216`). `combined_points.csv` has no such columns (header verified), so every combined-points layer lacks them; geoms layers rely on per-feature properties. | Add `source` and `source_date` to each layer's data (or inject per-layer constants at build from `layers.yaml`), and decide whether to use the unused `popup:` field list. |
| 5 | USWTDB API certificate expired upstream | `scripts/refresh_uswtdb.py` targets `https://eersc.usgs.gov/api/uswtdb/v1/turbines`. | Wait for upstream fix; do not disable TLS verification. If urgent, fetch the USWTDB file release manually and merge via `build.py merge wind <file>`. |
| 6 | ERCOT queue and TPIT have no fetch scripts | Only post-processing scripts exist (§3). Queue is a March-2026 snapshot (`WIP_OPEN.md` backlog 2). | Write `scripts/refresh_ercot_queue.py` and `scripts/refresh_tpit.py` emitting the `combined_points.csv`/`combined_geoms.geojson` schema, then `build.py merge`. |
| 7 | tippecanoe, pmtiles, cairosvg not installed in this container; no `.env` | Prevents a local full build and the layer gate (`build.py:43, 46`). | Run `bash scripts/bootstrap-claude-code.sh` plus `pip install cairosvg Pillow`; create `.env` from `.env.example`. |
| 8 | Access gate removed; Supabase `oxy-gate`/`oxy-track`/`oxy-stats` redeployed with `verify_jwt=true` and now unused | Deploy `6ad77b77a79fe4d03c8ce377`. Residue: `outputs/reports/OXY-analytics-dashboard.html:76`, `scripts/capture_om_exhibits.py:25-27, 249-258`. | Decommission or delete the unused functions; update `capture_om_exhibits.py` (it still waits 8 s for `#oxy-gate-form` then continues; hard-coded credential defaults at `:26-27`). Remove or de-emphasize the "CONFIDENTIAL" watermark (`build_template.html:349`) now that the map is public. |
| 9 | `build-and-deploy.yml` never run; ~14 unmerged `dc-anchors-refresh-*` PRs | Verified 2026-10-20. Workflow also lacks the md5 and layer gates and cannot build the RRC layers (gitignored CSVs). | Triage and close stale proposal PRs (stranded-branch drift per `audit.sh`); either retire or harden the cloud workflow. |
| 11 | Deploy `6ad77b77…` shipped without `_headers` / `_redirects` | The mirror could not fetch them (Netlify consumes these files; it does not serve them). Live tiles now return `cache-control: public,max-age=0,must-revalidate` and no CORS header. Same-origin map is unaffected; tiles revalidate on every load. | Next deploy from `python3 build.py` restores both (`write_netlify_config`, `build.py:1202-1213`). |
| 10 | Daily refresh routine stopped | Logs end `outputs/refresh/daily/2026-08-19.md`; the routine is external to the repo (verified 2026-10-20). | Locate and re-enable or replace with an in-repo workflow per `docs/refresh_automation_plan.md`. |

Additional code-observed issues (found while writing this manual; not part of the operator-verified list):

- No dependency manifest (`requirements.txt`, `package.json`); bootstrap omits `cairosvg`/`Pillow` that `build.py` imports.
- `build.py` does not load `.env`; `CLAUDE.md`'s "`.env` overrides" only works if the shell exports the variables. `LRP_DIST_DIR` has no repo-root fallback.
- `MISSING` and `EMPTY` layers do not block `deploy.sh` (only `errored>0` does); the layer gate runs after publish.
- `ARCHITECTURE.md` (32 layers, wells/permits "Weekly" counts) and `OPERATING.md` §5 ("26 entries", npx proxy deploy) are stale; `docs/settled.md` says REST deploy is deprecated, but `deploy.sh` uses the REST API and leaves the MCP helpers unused.
- `ICON_MAP` references layer id `wells` which no longer exists; orphan data layers (`wells`, `aquifers`, `caramba_south`, `water_mains_approx`, `drilling_permit_density`) occupy the combined files without being served.
- `build.py refresh permits` is wired to exit 2 with an obsolete message (`build.py:1508-1511`).
- External runtime dependencies on third parties: Google Fonts, OpenFreeMap (glyphs for all label layers and the `openfreemap` basemap), Esri, Carto, jsDelivr (SheetJS). The OpenFreeMap glyph host is required by every `label` layer on every basemap (`rasterStyle().glyphs`, `build_template.html:415-418`).
- Prebuilt layers (`rrc_pipelines`, `tiger_highways`, `bts_rail`) have no copy in git (`*.pmtiles` ignored); the only source is the live site.
- Hard-coded credential defaults in `scripts/capture_om_exhibits.py:26-27` (values intentionally not reproduced here).

### Quick Reference

| Task | Command |
|---|---|
| Full build | `python3 build.py` (needs tippecanoe, cairosvg, Pillow, pyyaml, pmtiles; `LRP_DIST_DIR` exported) |
| Single-layer refresh | `python3 build.py merge <layer_id> <refresh_file>` then `git add combined_points.csv` (or `combined_geoms.geojson`) |
| RRC wells | `python3 build.py refresh wells` then `python3 build.py` |
| RRC permits | `python3 scripts/fetch_rrc.py permits && python3 scripts/parse_rrc.py permits && python3 build.py` |
| Deploy | `bash scripts/deploy.sh --rebuild` |
| Deploy + merge | `bash scripts/ship.sh refinement-<slug> "<title>" -- --rebuild` |
| Close-out | `bash scripts/close-out.sh refinement-<slug> <deploy-id\|none> "<msg>"` |
| Live layer check | `python3 scripts/verify_deployed_layers.py [--quiet] [--base <origin>]` |
| Drift audit | `bash scripts/audit.sh` |
| Prod curl | `curl -sA "Mozilla/5.0" https://lrp-tx-gis.netlify.app/` (GET, not HEAD) |
| DC anchors proposal (local) | `ANTHROPIC_API_KEY=… python3 scripts/refresh_dc_anchors.py [entry-id]` |

Hard rules (`OPERATING.md` §3, `CLAUDE.md`): never read source data files into context; never `git add -A`; never hand-code coordinates or feature values; atomic writes via `os.replace`; deploy and merge together; never deploy with `errored>0`; branch from `main` as `refinement-<slug>`.
