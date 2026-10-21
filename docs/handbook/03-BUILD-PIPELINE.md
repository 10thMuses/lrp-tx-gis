# 03 — Build Pipeline: inputs, transformations, outputs

Everything `python3 build.py` does, in order, and every file it reads and writes.

---

## 1. The contract in one paragraph

`build.py` reads `layers.yaml`, splits the two combined data files by `layer_id` into
per-layer NDGeoJSON in `/tmp`, streams each through `tippecanoe` into a `.pmtiles`
archive, computes per-layer filter statistics, renders `build_template.html` with the
layer registry injected, and writes everything to `dist/`. It never materialises source
data into anything but a subprocess pipe. It prints a build report and exits; a non-zero
`errored` count is a hard deploy blocker.

---

## 2. Inputs

### 2.1 Configuration

| File | Role |
|---|---|
| `layers.yaml` | **The single source of layer configuration.** 39 entries. Adding a layer means adding an entry here. |
| `build_template.html` | The entire frontend, with two substitution tokens |
| `sprite/*.png` | Icon sources, rebuilt into sprite sheets each build |
| `vendor/*` | MapLibre, PMTiles, Turf — copied to `dist/` so they are served same-origin |

### 2.2 Data

| File | Size | Contains |
|---|---|---|
| `combined_points.csv` | ~5.0 MB | Every point layer, one row per feature, tagged by a `layer_id` column |
| `combined_geoms.geojson` | ~2.0 MB | Every line/fill/label feature, tagged by a `layer_id` property |
| `data/oxy/*.geojson` (8) | ~200 KB | Standalone OXY footprint layers |
| `data/hifld/*.geojson` (4) | ~450 KB | Standalone HIFLD layers |
| `data/datacenters/dc_anchors.json` | 16 KB | Custom-schema JSON, loaded by a dedicated reader |
| `data/wells_permian6.csv` | ~large | **Gitignored.** Regenerated from RRC. |
| `data/permits_permian6.csv` | ~large | **Gitignored.** Regenerated from RRC. |
| *(none — fetched from prod)* | — | `rrc_pipelines`, `tiger_highways`, `bts_rail` |

### 2.3 Environment

Paths resolve from environment variables with `/mnt/...` fallbacks for chat-mode
compatibility. In Claude Code, `.env` overrides them:

| Variable | Code mode | Default (chat mode) |
|---|---|---|
| `LRP_PROJECT_DIR` | `.` | `/mnt/project` |
| `LRP_DIST_DIR` | `./dist` | `/mnt/user-data/outputs/dist` |
| `LRP_UPLOADS_DIR` | `./uploads` | `/mnt/user-data/uploads` |

Fixed paths: `TMP = /tmp/gis_build`, `SPLIT_DIR = /tmp/gis_build/split`.

---

## 3. Schemas

### 3.1 `combined_points.csv`

```
layer_id, name, lat, lon, <~100 union columns>
```

- `layer_id` is the **first column** and tags row membership.
- WGS84, 6 decimal places maximum.
- All other columns are the **union across every point layer**, blank where
  inapplicable. There are ~103 distinct fields across all layers' popup configs.
- Columns in `NUMERIC_KEYS` are coerced to numbers at split time; everything else stays
  a string:
  `mw, capacity, capacity_mw, cap_kw, depth_ft, year, plant_code, osm_id, acres,
  total_depth, spud_year, permit_year, completion_year`
- Blank values are **dropped** from feature properties rather than emitted as empty
  strings — this keeps tile size down.

**Column overloading.** Some layers reuse generic columns for domain-specific meaning.
The `tax_abatements` mapping is locked and documented in
[`02-DATA-SOURCES.md §3.8`](02-DATA-SOURCES.md#38-tax-abatements--ldad--commissioners-court-scrape).
Any future overload must follow the same pattern and be documented there.

### 3.2 `combined_geoms.geojson`

- EPSG:4326, **2D coordinates** — any Z is flattened by `_flatten_coords` (the Caramba
  source ships 3-tuples).
- Every feature's `properties` carries `layer_id`, `source`, `source_date`.
- Line/polygon simplification tolerance 0.002–0.005; coordinates rounded to 4 dp.

### 3.3 Standalone files

Same schemas, but with **no `layer_id` field** — membership is implied by the filename,
and the entire file becomes the layer.

### 3.4 `layers.yaml` entry schema

```yaml
- id: <layer_id>                    # required, unique, used as tile filename and source-layer name
  file: <path>                      # required unless prebuilt: true
  geom: point | line | fill | label # required
  group: <sidebar group>            # required, must appear in GROUP_ORDER
  label: <display name>             # required
  color: '#rrggbb'                  # required
  default_on: true | false          # required
  popup: [field, ...]               # required (may be empty)

  # optional
  description: <prose shown in the sidebar>
  popup_labels: {field: "Friendly Label"}
  filterable_fields: [{field, type, label, ...}]
  min_zoom: <int>                   # layer hidden below this zoom
  prebuilt: true                    # skip tippecanoe, resolve an existing .pmtiles
  sidebar_omit: true                # build it, but hide the toggle
  companions: [layer_id, ...]       # toggling this also toggles those
  radius / circle_radius: <px>      # point size
  line_width: <px>
  fill_opacity: <0..1>
  stroke_color / stroke_width
  show_marker: true
  tippecanoe: ['-zg', ...]          # per-layer tippecanoe args
  # build-time row filters (see §5)
  min_spud_year / exclude_recompletions / reclassify_inactive_production
  keep_technology / keep_county_scope / exclude_within
```

**Key usage across the 39 layers:** `filterable_fields` on 25, `description` on 17,
`tippecanoe` on 36, `min_zoom` on 7, `prebuilt` on 3, `sidebar_omit` on 2.

### 3.5 `filterable_fields` types

| `type` | UI rendered | Extras |
|---|---|---|
| `numeric` | Range slider | `quick_presets: [{label, min, max}]` renders one-click chips |
| `categorical` | Multi-select dropdown | `value_labels: {raw: "Friendly"}`, `group_presets: [{label, from, to}]`, `sort_by_count: true` |
| `date_range` | From/to date pickers | — |
| `text` | Searchable substring | Auto-promoted to a searchable multi-select if distinct values ≤ `CATEGORICAL_CAP` |

`CATEGORICAL_CAP = 2000`. Above it, a categorical is **silently demoted** to text
substring matching so the dropdown stays usable.

---

## 4. Build stages

`main()` in `build.py`, in execution order.

| # | Stage | What happens |
|---|---|---|
| 1 | **Clean** | `rm -rf dist/`, recreate `dist/` and `/tmp/gis_build/split/` |
| 2 | **Sprite** | `build_sprite_sheet()` regenerates `sprite/sprite.png` + `@2x` **into the repo** (committed) and copies to `dist/sprite/` |
| 3 | **Vendor** | Copies `vendor/` → `dist/vendor/`. Warns loudly if missing — without it the map libs would have to come from a CDN, which previously caused a total outage. |
| 4 | **Config** | `yaml.safe_load(layers.yaml)` |
| 5 | **Abatement index** | Pre-scans `tax_abatements` rows into a fuzzy-match index (see [§6.1](#61-tax-abatement-annotation)) |
| 6 | **ERCOT aggregates** | `compute_ercot_group_aggregates()` — rolls up multi-component queue projects |
| 7 | **Split CSV** | One pass over `combined_points.csv` → one NDGeoJSON per `layer_id` in `/tmp/gis_build/split/`, applying numeric coercion, blank-dropping, abatement annotation and ERCOT aggregates |
| 8 | **Split GeoJSON** | Same for `combined_geoms.geojson` |
| 9 | **Per-layer build** | `build_layer()` for each entry — see [§5](#5-per-layer-build) |
| 10 | **Filter stats** | `compute_filter_stats()` — scans each layer's NDGeoJSON to derive min/max for numeric, distinct values + counts for categorical, date bounds for date_range |
| 11 | **Stats attrs** | `write_stats_attrs()` — writes slim per-layer JSON to `dist/data/<layer>.json` for the live stats panel |
| 12 | **Render** | `render_html()` — see [§7](#7-html-render) |
| 13 | **Netlify config** | `write_netlify_config()` — see [§8](#8-dist-layout) |
| 14 | **Report** | Prints the per-layer table and the summary line |

---

## 5. Per-layer build

For each `layers.yaml` entry, `build_layer()`:

### 5.1 Prebuilt layers

If `prebuilt: true`, tippecanoe is skipped and an existing `.pmtiles` is resolved in
three tiers:

1. `$LRP_PROJECT_DIR/<id>.pmtiles`
2. `$LRP_UPLOADS_DIR/<id>.pmtiles`
3. `https://lrp-tx-gis.netlify.app/tiles/<id>.pmtiles` ← **the production CDN**

Tier 3 makes the build self-sustaining but also means **production is an input to the
build** for `rrc_pipelines`, `tiger_highways` and `bts_rail`. If the site moves or goes
down, those three layers disappear from the next build with no local fallback.

### 5.2 Source resolution for normal layers

`resolve_source()` tries, in order: `$LRP_PROJECT_DIR/<file>` → a `points_`/`geoms_`/`deal_`
prefixed subfolder variant → the repo root. Returns `None` if nothing matches, which is
reported as `MISSING` (not `ERROR`).

### 5.3 Format conversion

| Input | Converter |
|---|---|
| Split NDGeoJSON (from a combined file) | Used directly |
| Standalone `.csv` | `csv_to_ndgeojson()` |
| Standalone `.geojson` | `geojson_to_ndgeojson()` |
| `dc_anchors.json` | `dc_anchors_to_ndgeojson()` — bespoke reader for its custom schema |

### 5.4 Build-time row filters

Declared per layer in `layers.yaml` and applied to the NDGeoJSON **before** tippecanoe:

| Key | Function | Effect |
|---|---|---|
| `exclude_within` | `_load_exclusion_polys` + `_exclude_within` | Drops points inside a named layer's polygons. Used to remove 9 wells from inside Caramba North. |
| `min_spud_year` | `_filter_min_spud_year` | Drops rows below a spud year |
| `exclude_recompletions` | `_filter_exclude_recompletions` | Drops rows where `completion_year < spud_year` — i.e. workovers of pre-existing wells, so counts reflect genuine new wellbores |
| `reclassify_inactive_production` | `_reclassify_no_longer_producing` | Joins `data/well_prod_status.csv` and re-labels wells with no recent production as "Marginal or end-of-life" |
| `keep_technology`, `keep_county_scope` | `_filter_tax_keep` | Restricts `tax_abatements` to relevant technologies/counties |

### 5.5 tippecanoe

```bash
tippecanoe -fo dist/tiles/<id>.pmtiles -l <id> <per-layer args> <ndgeojson>
```

- `-l <id>` sets the **source-layer name inside the archive to the layer id** — the
  frontend depends on this.
- `--read-parallel` was **removed deliberately**: it caused intermittent
  `database is locked` errors on overlayfs/tmpfs. Layer-level serial builds are reliable
  and the speed gain was not worth the race.
- Non-zero exit raises and the layer is reported `ERROR`.

> **The `-zg` trap.** Auto-zoom (`-zg`) silently produces a **0-feature PMTiles** on
> single-feature inputs. For single-feature point layers use explicit `-Z0 -z14`.
> This has bitten the project before and is why `verify_deployed_layers.py` checks for
> non-empty tilesets rather than just HTTP 200.

---

## 6. Derived and annotated fields

Fields that exist in the tiles but not in any source file.

### 6.1 Tax-abatement annotation

A build-time fuzzy join stamps `abatement_*` properties onto rows in five layers —
`eia860_plants`, `ercot_queue`, `solar`, `wind`, `eia860_battery` — where a
`tax_abatements` applicant matches in the same county.

- Match key: `(county, applicant_norm ⊂ tokens of facility name / entity / operator / project)`
- **Subset-only matching**, not token overlap. Overlap produced false positives on
  generic tokens like `ii`, `bess`, `solar`.
- Applicant normalisation strips corporate suffixes via `_CORP_SUFFIX`
  (`LLC|INC|LP|LTD|CORP|CORPORATION|COMPANY|CO`) and non-word characters.
- Rows with status `zone_creation` or `relationship_signal` are **excluded** — they are
  not real abatement applicants.
- Single pass, no iterative refinement.

### 6.2 ERCOT group aggregates

`compute_ercot_group_aggregates()` rolls up multi-component queue projects so a single
project filed as three interconnection requests reports one combined capacity. Adds
`group_count` and aggregate capacity fields.

### 6.3 Production reclassification

`_reclassify_no_longer_producing()` joins `data/well_prod_status.csv` to
`wells_permian6` and sets `well_status = "Marginal or end-of-life"` where production has
lapsed. The frontend renders those wells at reduced opacity.

### 6.4 Filter statistics

`compute_filter_stats()` derives, per declared filterable field: numeric min/max,
categorical distinct values with counts (capped at `CATEGORICAL_CAP`), and date bounds.
These are injected into the layer registry so the filter UI can render correct ranges
without the browser scanning the tiles.

---

## 7. HTML render

`render_html()` builds a clean per-layer registry (id, label, group, geom, color,
default_on, sidebar_omit, companions, popup, popup_labels, description, min_zoom,
radius, fill_opacity, line_width, text_halo, color_steps, **feature count**, and
resolved `filterable_fields`), serialises it to compact JSON, and performs exactly two
token substitutions in `build_template.html`:

| Token | Replaced with |
|---|---|
| `/*__LAYERS__*/` | The layer registry JSON |
| `/*__BUILD_ID__*/` | `YYYYMMDDTHHMMSSZ-<4 random bytes hex>` |

> **Do not remove `/*__BUILD_ID__*/`.** Two things depend on every build producing a
> byte-unique `index.html`: Netlify deploy dedup-busting, and — more importantly — the
> md5-parity poll in `scripts/deploy.sh`. That poll is how the deploy script knows a
> deploy is both *ready* and *CDN-propagated* in a single signal. Remove the marker and
> the deploy script hangs for 5 minutes and exits 5 on every deploy.

Only layers that produced stats are included — a `MISSING` layer is silently absent from
the frontend rather than rendering a broken toggle.

---

## 8. `dist/` layout

Everything below is generated. `dist/` is gitignored; **never hand-edit any of it.**

```
dist/
├── index.html          The whole app, ~150 KB, registry inlined
├── tiles/*.pmtiles     39 archives, ~29 MB total
├── data/<layer>.json   Slim per-layer attribute JSON for the live stats panel
├── vendor/             maplibre-gl.js/.css, pmtiles.js, turf.min.js
├── sprite/             sprite.png, sprite@2x.png, + .json
├── _headers            CORS + cache headers for tiles
└── _redirects          SPA catch-all
```

`_headers`:

```
/tiles/*
  Access-Control-Allow-Origin: *
  Cache-Control: public, max-age=3600, must-revalidate
  Content-Type: application/octet-stream

/*.pmtiles
  Access-Control-Allow-Origin: *
  Content-Type: application/octet-stream
```

`_redirects`: `/*    /index.html   200`

> Note the CORS policy: **tiles are world-readable with no authentication.** This is
> required for PMTiles range requests to work, and it is why the password gate protects
> the interface rather than the data.

---

## 9. Build report

```
BUILD REPORT
layer                   total     kept  status
------------------------------------------------------------
counties                   46       46  OK
...
built=39  missing=0  errored=0  tiles_total=29594 KB
out: dist/index.html
```

| Status | Meaning | Deploy impact |
|---|---|---|
| `OK` | Tileset built with features | — |
| `MISSING` | Source file not resolvable | Layer silently absent. **Not** a deploy blocker — which is why `verify_deployed_layers.py` exists. |
| `ERROR` | tippecanoe failed or the layer raised | **Hard deploy blocker.** `deploy.sh` exits 2. |

**Acceptance target:** `built=39 missing=0 errored=0`. A clean clone will report
`missing=2` until the RRC refresh has produced `data/wells_permian6.csv` and
`data/permits_permian6.csv`.

`deploy.sh` additionally refuses to proceed if the build log contains no `built=` line at
all — a guard added after a YAML parse error once skipped the report entirely, left a
stale partial `dist/` in place, and got it shipped to production.

---

## 10. CLI subcommands

```bash
python3 build.py                              # full build
python3 build.py merge <layer_id> <file>      # merge a refresh file into a combined file
python3 build.py refresh <wells|permits|all>  # chain fetch_rrc.py + parse_rrc.py
```

### `merge`

Swaps all rows/features tagged `layer_id` in the combined file for the contents of the
refresh file. Atomic: writes a temp file and `os.replace`s it. If the refresh file has a
`layer_id` column, every value must equal the target id.

`merge` **does not rebuild.** Commit the combined-file diff, then run `build.py` as a
separate step.

### `refresh`

Chains `scripts/fetch_rrc.py <target>` → `scripts/parse_rrc.py <target>`. Note that
`cmd_refresh` still rejects `permits` with a stale "scoped-out" message referring to
`permits_pecos11`; the permits path now works and is run directly as two commands. See
[`08-ROADMAP-AND-GAPS.md §1`](08-ROADMAP-AND-GAPS.md#1-documentation-drift-found-2026-08-18).

---

## 11. Hard rules the pipeline enforces

| Rule | Enforcement |
|---|---|
| Never read source data into context | Structural — `build.py` only ever streams into subprocesses |
| Atomic in-place writes | `merge_csv` / `merge_geojson` / every refresh script use temp + `os.replace` |
| Never deploy with `errored>0` | `deploy.sh` greps the build log and exits 2 |
| Never deploy a build that did not complete | `deploy.sh` requires a `built=` line and a real `dist/index.html` + `dist/tiles/` |
| Never merge a broken deploy | `deploy.sh §8.7` runs `verify_deployed_layers.py` against **prod** and exits 7 before close-out if any layer is missing or zero-count |
| No files >1 MB committed accidentally | Optional `scripts/pre-commit` hook (`git config core.hooksPath scripts`) |
