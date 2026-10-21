# 05 — Editing and Improving the Map

How to make each kind of change, with worked examples. Every change follows the same
outer loop:

```bash
git checkout main && git pull --ff-only
git checkout -b refinement-<slug>
# ... make the change ...
python3 build.py                                   # verify build clean
bash scripts/ship.sh refinement-<slug> "<summary>" -- --rebuild
```

---

## 1. Where to change what

| You want to change | Edit |
|---|---|
| Which layers exist, their colours, groups, filters, popups, defaults | `layers.yaml` **only** |
| Map behaviour, UI controls, styling, export logic | `build_template.html` |
| Data pipeline, derived fields, build-time filters | `build.py` |
| Icons | `sprite/*.png` + `build_sprite.py` |
| Sidebar group order | `GROUP_ORDER` in `build_template.html` (line ~2459) |
| Basemaps | `BASEMAPS` in `build_template.html` (line ~410) |
| Access gate | Supabase Edge Functions + the `SUPA` constant in `build_template.html` |

**Most changes are `layers.yaml` changes.** Reach for `build_template.html` only when
the behaviour you want does not exist yet.

---

## 2. Adding a layer

### 2.1 Get the data in

Three storage options, in order of preference:

| Option | When | How |
|---|---|---|
| **Combined file** ✅ default | Point layer that fits the shared column set; line/fill layer of modest size | Merge into `combined_points.csv` / `combined_geoms.geojson` with a `layer_id` tag |
| **Standalone file** | Distinct schema, or large enough that merging would bloat the combined file | Drop a `.csv`/`.geojson` under `data/` and point `file:` at it |
| **Prebuilt PMTiles** | Source ≥10 MB, or already tiled | Set `prebuilt: true` and place the `.pmtiles` where the 3-tier resolver can find it |

Merging into a combined file:

```bash
python3 build.py merge <layer_id> outputs/refresh/<file>
git add combined_points.csv          # or combined_geoms.geojson
git commit -m "add: <layer_id> from <source> <date>"
```

### 2.2 Register it

Append to `layers.yaml`:

```yaml
- id: my_new_layer
  file: combined_points.csv
  geom: point
  group: Power Generation           # must exist in GROUP_ORDER
  label: My New Layer
  description: >
    One or two sentences the sidebar shows. State the upstream source and any
    scope filter applied — this is what a viewer reads to decide whether to trust
    the layer.
  color: '#f59e0b'
  default_on: false
  radius: 5
  popup:
    - name
    - county
    - capacity_mw
  popup_labels:
    name: Facility
    county: County
    capacity_mw: Capacity (MW)
  filterable_fields:
    - field: county
      type: categorical
      label: County
    - field: capacity_mw
      type: numeric
      label: Capacity (MW)
  tippecanoe:
    - -zg
```

### 2.3 Build and verify

```bash
python3 build.py
# confirm: built=<N+1>  missing=0  errored=0
# confirm your layer's row shows a non-zero feature count
```

### 2.4 Gotchas

- **`-zg` on a single-feature layer produces an empty tileset.** Use `-Z0 -z14`.
- The `group:` value must exist in `GROUP_ORDER` in `build_template.html`, or the layer
  builds fine and **never renders in the sidebar**. This exact bug hid four `hifld_*`
  layers until 2026-05-18.
- Pick a colour from the palette ([§4](#4-colours)) that no other layer uses.
- Layers with 10k+ features want a `min_zoom` so they do not render at state scale.

---

## 3. Changing a layer

All of these are single-key edits in `layers.yaml`, followed by a rebuild and deploy.

| Change | Key |
|---|---|
| Colour | `color: '#rrggbb'` |
| Sidebar name | `label:` |
| On by default | `default_on: true \| false` |
| Hide from sidebar but still build | `sidebar_omit: true` |
| Move to another group | `group:` (must exist in `GROUP_ORDER`) |
| Hide below a zoom level | `min_zoom: 7` |
| Point size | `radius:` or `circle_radius:` |
| Line thickness | `line_width:` |
| Fill transparency | `fill_opacity: 0.25` |
| Outline | `stroke_color:`, `stroke_width:` |
| Toggle sibling layers together | `companions: [other_layer_id]` |
| Sidebar blurb | `description:` |

---

## 4. Colours

Pick from the group's hues and avoid reusing an existing layer's colour.

| Group | Palette |
|---|---|
| Land & Deal | `#78350f` `#92400e` `#6b7280` |
| Water & Regulatory | `#8b5cf6` `#a855f7` `#9333ea` |
| Generation | `#f59e0b` `#dc2626` `#84cc16` `#eab308` `#FFD400` |
| Transmission & Grid | `#0ea5e9` `#0369a1` `#075985` `#38bdf8` |
| Pipelines | `#64748b` |
| Permits | `#6b21a8` |
| Projects | `#ec4899` `#2E7D32` |
| Broadband | `#06b6d4` |
| Reference | `#64748b` `#1e293b` `#475569` |

Check what is already taken:

```bash
python3 -c "import yaml; [print(f\"{l['color']}  {l['id']}\") for l in yaml.safe_load(open('layers.yaml'))['layers']]" | sort
```

---

## 5. Popups

```yaml
popup:
  - name
  - operator
  - capacity_mw
  - source
  - source_date
popup_labels:
  name: Facility
  operator: Operator
  capacity_mw: Capacity (MW)
  source: Source
  source_date: As of
```

- Field names must match the source data exactly.
- Fields with no `popup_labels` entry render with their raw name — always supply labels.
- Include `source` and `source_date` on any layer where provenance matters; that is the
  house convention and the reason a viewer can trust a number.
- Blank values are dropped at split time, so an empty field simply does not appear.

---

## 6. Filters

### 6.1 Numeric with quick presets

```yaml
- field: total_depth
  type: numeric
  label: Total depth (ft)
  quick_presets:
    - {label: "<5K",    min: 0,     max: 5000}
    - {label: "5-10K",  min: 5000,  max: 10000}
    - {label: "10-15K", min: 10000, max: 15000}
    - {label: ">15K",   min: 15000, max: 30000}
```

### 6.2 Categorical with friendly labels and group presets

```yaml
- field: plug_flag
  type: categorical
  label: Plug status
  value_labels:
    "Y": "Y = Plugged/Abandoned"
    "N": "N = Active"

- field: spud_year
  type: categorical
  label: Spud year (multi-select)
  group_presets:
    - {label: "1964-1979", from: 1964, to: 1979}
    - {label: "1980-1989", from: 1980, to: 1989}
    - {label: "2020+",     from: 2020, to: 2030}
```

### 6.3 Date range and text

```yaml
- field: spud_date
  type: date_range
  label: Spud date

- field: entity
  type: text
  label: Developer
```

### 6.4 Rules

- Min/max, distinct values and date bounds are **derived at build time** from the actual
  data — you do not supply them.
- A categorical with more than `CATEGORICAL_CAP` (2000) distinct values is **silently
  demoted** to text substring matching.
- `sort_by_count: true` orders a dropdown by frequency instead of alphabetically.
- Filters are per-layer and combine with AND within a layer.
- Active filters appear in the banner across the top with per-filter clear buttons, and
  are encoded in the URL hash so a filtered view is shareable.
- All export buttons respect the active filters — except the **Spuds Summary (PDF)**,
  which is deliberately always six-county.

---

## 7. Build-time row filters

For excluding rows from the tiles entirely rather than at view time.

```yaml
exclude_within: caramba_north       # drop points inside that layer's polygons
min_spud_year: 1964
exclude_recompletions: true         # drop rows where completion_year < spud_year
reclassify_inactive_production: true # join well_prod_status.csv, relabel stale wells
keep_technology: [...]              # tax_abatements scope filter
keep_county_scope: [...]
```

Use these when a row should never be visible, not merely defaulted off. They shrink the
tiles; view-time filters do not.

---

## 8. Frontend changes

`build_template.html` is 2,966 lines of hand-written HTML/CSS/JS with no build step.
Edit it, run `python3 build.py`, open `dist/index.html`.

### 8.1 Map

| Line ~ | What |
|---|---|
| 410 | `BASEMAPS` — add a raster or style-URL basemap |
| 469 | Default centre `-102.9707 / 30.9112`, zoom 12, basemap `esri_imagery` |
| 521 | `SIZING_RULES` — data-driven marker sizing per layer |
| 595–635 | Custom colour expressions: `ercotQueueColorExpr`, `dcAnchorsColorExpr`, `dcAnchorsOpacityExpr`, `oilGasColorExpr` |
| 636 | `layerPaint(L)` — the paint-property builder |
| 711 | `addLayer(L)` — source + layer registration |
| 810 | `raiseOxy()` — keeps OXY layers on top of the draw stack |
| 2459 | `GROUP_ORDER` — sidebar section order |

### 8.2 Data-driven sizing

Live on `ercot_queue`, `solar`, `eia860_plants`, `eia860_battery`, `wind`, `substations`,
`tpit_subs`, `tpit_lines`. Where the sizing field is null the layer falls back to its
static `radius`. Known gaps: 476/1367 `eia860_plants` are null on `capacity_mw`;
`transmission` has no voltage attribute at all.

### 8.3 Stats panel and exports

| Line ~ | What |
|---|---|
| 1173 | `StatsPanel` — reads `dist/data/<layer>.json`, recomputes on every filter change |
| 1428, 1538 | Export buttons: CSV, XLSX, Copy MD, Print PDF |
| 1716 | Wells Spuds Summary export — always six-county, filter-aware otherwise |

XLSX uses SheetJS, loaded on demand from a CDN the first time it is needed
(`ensureSheetJS`). This is the **one** runtime CDN dependency; everything else is
vendored same-origin.

### 8.4 Print view

`@media print` blocks at lines 152–272 produce a landscape layout with an LRP header,
a 4-column legend on its own page, and a source footer. Editing print styles requires
actually printing to check — they are invisible on screen.

### 8.5 Access gate

Lines 274–298 (markup) and 2888–2962 (logic). See
[`06-ACCOUNTS-AND-ACCESS.md §4`](06-ACCOUNTS-AND-ACCESS.md#4-the-portal-password-gate).

---

## 9. Icons

```bash
# add sprite/my-icon.png, then
python3 build_sprite.py
```

`build.py` regenerates the sprite sheet on every build into the repo `sprite/` (which is
committed) and mirrors it to `dist/sprite/`. Map a layer to an icon via `ICON_MAP` in
`build_template.html` (line ~382).

---

## 10. Adding a basemap

```javascript
// build_template.html, BASEMAPS (~line 410)
my_basemap: {
  kind: 'raster',                         // or 'style' with a `url`
  tiles: ['https://example.com/{z}/{x}/{y}.png'],
  attribution: '© Provider',
},
```

Then add an `<option>` to `#basemap-select` (~line 329). Use only free, unauthenticated
tile services within their published terms — the project deliberately has no map API keys.

---

## 11. Improving the map — where the leverage is

Ordered by value per unit of effort. Full backlog in
[`08-ROADMAP-AND-GAPS.md`](08-ROADMAP-AND-GAPS.md).

| # | Improvement | Why it matters | Effort |
|---|---|---|---|
| 1 | **Unblock ERCOT Stage-3 geocoding** — create `data/ercot_queue_overrides.csv` | 1,299 of 1,778 queue projects sit on county centroids. The queue is the highest-value layer for the thesis and it is the least precise. | Curation, not code |
| 2 | **Custom domain** | Removes `netlify.app` from every share link and makes future host moves a DNS change | 1 h |
| 3 | **Reconcile `layers.yaml` with the docs** | `ARCHITECTURE.md` describes layers that no longer exist and omits ones that do | 2 h |
| 4 | **Cross-layer search** | Currently you must know which layer a facility is in before you can find it | 1 day |
| 5 | **Mobile responsive breakpoints** | Peers open links on phones; the sidebar is desktop-first | 1–2 days |
| 6 | **Legend on print** | Already there — but verify it against a real print, which has never been done in-browser | 1 h |
| 7 | **Real access control** | Replace the shared password with per-viewer magic links | 2–3 days |
| 8 | **Complete the 1976–2017 permits backfill** | Extends permit history by 42 years | ~7 h unattended scrape |
| 9 | **Voltage attribute for `transmission`** | Unlocks voltage filtering and sizing; needs a source that carries it | Research |

---

## 12. Things not to do

- **Do not add a build framework.** No React, no bundler. The property being protected is
  *edit one file, see the result*. This is a settled decision.
- **Do not load MapLibre or PMTiles from a CDN.** It broke the worker pipeline and took
  the map down. Vendor same-origin.
- **Do not remove `/*__BUILD_ID__*/`** from `build_template.html` — it breaks the deploy
  md5-parity poll.
- **Do not re-add `--read-parallel`** to the tippecanoe invocation.
- **Do not hand-edit anything in `dist/`.** It is regenerated every build.
- **Do not hand-code coordinates.** If there is no source, there is no layer.
- **Do not commit `data/abatements/abatement_hits_*.csv`** — diagnostic probe output,
  not a layer source.
- **Do not deploy without merging in the same session.**
