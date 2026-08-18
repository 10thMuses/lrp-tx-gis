# 01 — Project Overview

What the LRP Texas Energy GIS Map is, what it is made of, and how to use it.

---

## 1. What it is

A single-page interactive web map of Texas energy, land, water and grid infrastructure,
built for investment analysis in the Permian Basin and distributed as an intelligence
product to a small peer list.

Its analytical spine is a comparison: a **sale area** (Pecos, Reeves, Ward counties)
against an **active Permian peer area** (Midland, Martin, Reagan). Well, permit and
drilling layers carry a `county_role` field tagged `subject` or `peer` so that
comparison survives any filter the user applies. Layered on top of that are the ERCOT
interconnection queue, generation and storage, transmission, pipelines, groundwater,
tax abatements, broadband and a curated index of ≥100 MW datacenter campuses — the
inputs that determine whether a piece of West Texas land is worth anything to a
hyperscaler.

**39 layers**, ~180,000 features, served as PMTiles from a static CDN with no backend
and no database behind the map itself.

---

## 2. Accessing the portal

### 2.1 The URL

```
https://lrp-tx-gis.netlify.app
```

Works in any modern browser, desktop or mobile. There is no app to install.

### 2.2 The password gate

The map opens on a full-screen **"Confidential access"** panel asking for an email and
an access password.

- **Email** — any valid address. It is not checked against a list; it is recorded for
  the access log, so people should enter their real one.
- **Password** — a single shared password for all viewers, stored server-side in
  Supabase (`oxy_config.gate_password`).

Once accepted, the browser remembers the session in `localStorage` for **12 hours**, so
regular viewers see the gate about once a day.

**Where the password lives and how to change it** — see
[`06-ACCOUNTS-AND-ACCESS.md §4`](06-ACCOUNTS-AND-ACCESS.md#4-the-portal-password-gate).
Rotating it is a one-row SQL update with no rebuild or redeploy.

> **What the gate does and does not do.** It keeps casual visitors out of the interface.
> It does not protect the data: the PMTiles archives under `/tiles/*.pmtiles` are served
> publicly with `Access-Control-Allow-Origin: *` and no authentication. Treat the map as
> "unlisted", not "secure".

### 2.3 Sharing a specific view

The map writes its full state into the URL hash, so a copied URL reproduces exactly what
the sender was looking at. The **Share** button in the toolbar copies that URL.

| Hash key | Meaning | Example |
|---|---|---|
| `lat`, `lon` | Centre point, 4 dp | `lat=30.9112&lon=-102.9707` |
| `zoom` | Zoom level, 2 dp | `zoom=12.00` |
| `layers` | Comma-separated layer IDs that are switched on | `layers=wells_permian6,ercot_queue` |
| `base` | Basemap key | `base=esri_imagery` |
| `filters` | URL-encoded JSON of every active filter | `filters=%7B%22wells_permian6%22...%7D` |
| `sb` | `1` collapses the sidebar — use for embeds and screenshots | `sb=1` |

Example — Pecos County wells, satellite basemap, no sidebar:

```
https://lrp-tx-gis.netlify.app/#lat=30.9112&lon=-102.9707&zoom=10&base=esri_imagery&layers=wells_permian6,counties&sb=1
```

Defaults when the hash is empty: centre `-102.9707 / 30.9112`, zoom `12`, basemap
`esri_imagery`, and whichever layers carry `default_on: true` in `layers.yaml`.

### 2.4 What a viewer can do without any technical knowledge

| Control | Where | What it does |
|---|---|---|
| **Layer toggles** | Sidebar, grouped into 12 sections | Switch layers on/off. Feature counts shown per layer. |
| **Views** | Sidebar, top | Saved thesis views — one-click preset combinations of layers, filters and viewport |
| **Filters** | Under each layer in the sidebar | Numeric ranges (with quick presets), multi-select categoricals, date ranges, text search. An active-filter banner across the top shows exactly what is being excluded, with per-filter clear buttons. |
| **Basemap** | Sidebar dropdown | Carto Light, Esri Streets, Esri World Imagery, OpenFreeMap Liberty, USGS NAIP |
| **Popups** | Click any feature | Labelled attributes plus source and source date |
| **Stats panel** | Bottom of screen | Live counts, histograms and breakdowns for the visible/filtered set. Recomputes on every filter change. |
| **Time scrubber** | Stats panel | Animate a layer through time (spud year, permit year) |
| **Compare** | Stats panel | Toggle the sale-area vs peer-area split view |
| **Measure** | Toolbar | Distance and area |
| **Share** | Toolbar | Copy the current view as a URL |
| **Print** | Toolbar | Landscape print/PDF with an LRP header, a 4-column legend on its own page, and a source footer |
| **Reset** | Toolbar | Back to default layers and viewport |

### 2.5 Getting data out

Every layer's filter panel has export buttons that respect the **currently active
filters**:

| Button | Output |
|---|---|
| **CSV** | Filtered rows, downloaded |
| **XLSX** | Multi-sheet workbook (SheetJS, loaded on demand) |
| **Copy MD** | Markdown table to clipboard — for pasting into memos |
| **Print PDF** | Print view of the current selection |
| **Spuds Summary (PDF)** | `wells_permian6` only — the drilling-decline exhibit, always split across the six thesis counties regardless of active filters |

### 2.6 Viewer analytics

Logins and in-map behaviour are logged: `page_view`, `layer_toggle`, `map_move`,
`heartbeat` (every 30 s), `visibility`, `leave` — keyed to the email entered at the gate.
The data is queryable via a separate password-protected endpoint. See
[`06-ACCOUNTS-AND-ACCESS.md §5`](06-ACCOUNTS-AND-ACCESS.md#5-viewer-analytics).

---

## 3. Stack

| Layer | Choice | Notes |
|---|---|---|
| Map engine | **MapLibre GL JS 4.7.1** | Vendored at `vendor/maplibre-gl.js`, served same-origin. Loading it from a CDN broke the worker pipeline and took the map down — this is a hard architectural rule, not a preference. |
| Tile format | **PMTiles 4.3.0** | Single-file tile archives. The browser fetches only the tiles it needs via HTTP range requests. No tile server. |
| Tile builder | **tippecanoe** (felt fork) | Invoked per layer as a subprocess by `build.py` |
| Geometry helpers | **turf.js** | Vendored, used for measure and point-in-polygon |
| Frontend | **One hand-written HTML file** | `build_template.html`, 2,966 lines. No React, no bundler, no framework. |
| Hosting | **Netlify** | Static; direct zip upload via REST API. Not Git-linked. |
| Access gate | **Supabase Edge Functions** | The only server-side component in the whole system |
| Build language | **Python 3** | `build.py`, 1,534 lines. Deps: `pyyaml`, `pmtiles`, `requests` (plus per-script extras). |

### 3.1 Settled decisions

Per `OPERATING.md §9` — do not re-litigate without a strong reason:

- MapLibre + PMTiles + tippecanoe. Not Leaflet. Not Mapbox GL JS (licence).
- Netlify. Not Vercel, not Cloudflare Pages. The deploy path and CDN behaviour are calibrated.
- Single-page app, no build framework. The property being protected is *edit one file,
  see the result*.
- Combined data files with a `layer_id` tag column, split per layer at build time.
  Standalone files only where size or schema forces it.
- `main` is canonical. `refinement-<slug>` feature branches. Direct merge to `main`, no PRs.

---

## 4. How the pieces fit

```
 SOURCES (public: RRC, EIA, ERCOT, TWDB, HIFLD, OSM, Census, TCEQ, FCC, USGS)
     │
     │  scripts/fetch_*.py  scripts/refresh_*.py  scripts/scrape_*.py
     ▼
 STAGED REFRESH FILES            outputs/refresh/<layer>_<date>.csv|geojson
     │
     │  python3 build.py merge <layer_id> <file>      (atomic in-place)
     ▼
 CANONICAL DATA (committed)      combined_points.csv       ~5.0 MB, all point layers
                                 combined_geoms.geojson    ~2.0 MB, all line/fill layers
                                 data/**                   standalone layer sources
     │
     │  python3 build.py  ← reads layers.yaml, splits by layer_id,
     │                      streams NDGeoJSON into tippecanoe per layer
     ▼
 BUILD OUTPUT (gitignored)       dist/index.html           the whole app, ~150 KB
                                 dist/tiles/*.pmtiles      39 archives, ~29 MB
                                 dist/vendor/ dist/sprite/ dist/data/
                                 dist/_headers dist/_redirects
     │
     │  bash scripts/deploy.sh --rebuild   (zip → Netlify REST API → md5-parity poll
     │                                      → per-layer tile verification gate)
     ▼
 PRODUCTION                      https://lrp-tx-gis.netlify.app
     │
     │  HTTP range requests per visible tile
     ▼
 BROWSER — gated by Supabase oxy-gate
```

Full detail in [`03-BUILD-PIPELINE.md`](03-BUILD-PIPELINE.md).

---

## 5. Repo map

```
lrp-tx-gis/
├── CLAUDE.md                  Session bootstrap for Claude Code (auto-loaded)
├── OPERATING.md               Execution rules, hard rules, build/deploy cycles
├── ARCHITECTURE.md            Schema, layer catalog, palette, fragility table
├── WIP_OPEN.md                Active sprints and backlog (the resume pointer)
│
├── layers.yaml                THE layer registry — 39 entries, single config
├── build.py                   Build orchestrator + `merge` and `refresh` subcommands
├── build_template.html        The entire frontend; token-substituted at render
├── build_sprite.py            Icon sprite-sheet builder
│
├── combined_points.csv        All point layers, tagged by `layer_id` column
├── combined_geoms.geojson     All line/fill features, tagged by `layer_id` property
│
├── data/                      Standalone + archival layer sources
│   ├── oxy/                   8 curated OXY footprint GeoJSONs
│   ├── hifld/                 4 HIFLD pipeline / processing GeoJSONs
│   ├── datacenters/           dc_anchors.json + its schema README
│   ├── tiger/  bead_bdo/  abatements/  fracfocus/
│   ├── wells_permian6.csv     GITIGNORED — regenerated from RRC
│   └── permits_permian6.csv   GITIGNORED — regenerated from RRC
│
├── scripts/                   46 files — see §6
├── docs/
│   ├── handbook/              ← you are here
│   ├── rrc_layouts/           RRC fixed-width record-layout PDFs (parser reference)
│   ├── refresh_automation_plan.md
│   └── archive/               Historical session logs and specs
│
├── outputs/
│   ├── refresh/               Staged refresh files + archives
│   │   └── daily/             89 daily auto-refresh run reports
│   └── reports/               Client deliverables + analysis scripts
│
├── vendor/                    maplibre-gl.js/.css, pmtiles.js, turf.min.js
├── sprite/                    Icon sprite sheets (1x + 2x)
└── .github/workflows/         build-and-deploy.yml, dc-anchors-refresh.yml
```

**Not in the repo** (gitignored, and correctly so): `.env`, `dist/`, `*.pmtiles`,
`data/rrc_raw/`, `data/wells_permian6.csv`, `data/permits_permian6.csv`,
`data/abatements/abatement_hits_*.csv` (except the pinned snapshot),
`outputs/refresh/rrc_w1_*`, `__pycache__/`, `.claude/`.

---

## 6. Script inventory

46 files in `scripts/`, in five families.

### Operational (run these)

| Script | Purpose |
|---|---|
| `bootstrap-claude-code.sh` | One-shot idempotent setup: tippecanoe, Python deps, `.env`, git identity, smoke test |
| `bootstrap-windows.ps1` | Windows/WSL equivalent |
| `session-open.sh <branch>` | Start work: fetch, branch-ahead check, push upstream, prod sanity check |
| `deploy.sh [--rebuild]` | Build → zip → Netlify REST → md5-parity poll → per-layer verification. Prints `deployId`. |
| `close-out.sh <branch> <deployId\|none> "<msg>"` | Push, rebase `main`, merge `--no-ff`, push, delete origin branch |
| `ship.sh <branch> ["<title>"]` | `deploy.sh` + `close-out.sh` as one indivisible call |
| `audit.sh` | Drift telemetry: doc sizes, merge conformance, stranded branches, repo size |
| `verify_deployed_layers.py` | Reads each live PMTiles tilestats via HTTP range; exit 1 if any layer is missing or empty |
| `pre-commit` | Optional hook: rejects staged files >1 MB, warns on non-canonical paths. Enable with `git config core.hooksPath scripts` |

### Fetchers and refreshers (upstream → `outputs/refresh/`)

`fetch_rrc.py` · `parse_rrc.py` · `fetch_hifld.py` · `fetch_pdq_dump.py` ·
`refresh_eia860.py` · `refresh_uswtdb.py` · `refresh_tceq_gas_turbines.py` ·
`refresh_fcc_fiber_coverage.py` · `refresh_dc_anchors.py` · `scrape_ldad.py` ·
`scrape_abatements.py` · `scrape_rrc_w1.py` · `scrape_rrc_w1_detail_coords.py`

### Enrichment and transformation

`geocode_ercot_queue.py` (28 KB — the three-stage ERCOT coordinate pipeline) ·
`enrich_ercot_coords.py` · `enrich_ercot_substation_match.py` ·
`transform_abatements.py` · `transform_ldad.py` · `extend_county_labels.py` ·
`build_lease_status.py` · `build_well_prod_status.py` · `build_drilling_density.py`

### OXY deliverable generators (report product, not the map)

`build_oxy_assets.py` · `build_oxy_drilling_permits.py` · `build_oxy_map_layers.py` ·
`build_oxy_report.py` · `build_oxy_deck.py` · `build_oxy_docx.py` · `oxy_maps.py` ·
`oxy_build_maps.py` · `oxy_assets_data.py` · `build_production_deliverable.py`

### One-off edit scripts (historical; kept for provenance)

`edit_109b_consolidate.py` · `edit_110c_trans_fix.py` · `edit_local_devs.py`

---

## 7. Using the map (no code)

If you only ever want to look at the map and pull numbers out of it, everything you need
is [§2](#2-accessing-the-portal) above. In one line:

> Go to **https://lrp-tx-gis.netlify.app**, enter your email and the LRP access
> password, toggle layers in the left sidebar, click features for detail, use the
> filter panels to narrow, and hit **CSV** or **XLSX** under a layer to export exactly
> what you are looking at. **Share** copies a link that reopens your exact view.

---

## 8. Where to go next

| You want to… | Read |
|---|---|
| Move the project to the team account | [`00-MIGRATION-RUNBOOK.md`](00-MIGRATION-RUNBOOK.md) |
| Know where a number on the map came from | [`02-DATA-SOURCES.md`](02-DATA-SOURCES.md) |
| Understand or modify the build | [`03-BUILD-PIPELINE.md`](03-BUILD-PIPELINE.md) |
| Refresh data and ship it | [`04-OPERATIONS-RUNBOOK.md`](04-OPERATIONS-RUNBOOK.md) |
| Add a layer, change a colour, add a filter | [`05-EDITING-THE-MAP.md`](05-EDITING-THE-MAP.md) |
| Find a credential or grant someone access | [`06-ACCOUNTS-AND-ACCESS.md`](06-ACCOUNTS-AND-ACCESS.md) |
| Understand the crons | [`07-AUTOMATION.md`](07-AUTOMATION.md) |
| Know what is broken or missing | [`08-ROADMAP-AND-GAPS.md`](08-ROADMAP-AND-GAPS.md) |
