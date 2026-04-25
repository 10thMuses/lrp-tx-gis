# Architecture — LRP Texas Energy GIS Map

Static reference. Stack, schema, layer catalog, fragility table, color palette. Read on architecture-touching chats only; not part of the standard session-open read.

Operating rules (session protocol, GitHub sync, handoffs, tool-call budgets) live in `OPERATING.md`.

---

## 1. Stack

- **Frontend:** MapLibre GL JS 4.7.1 + pmtiles.js 4.3.0 (vendored same-origin since Chat 27)
- **Tile format:** PMTiles binary archives. Browser fetches only visible tiles via HTTP range requests.
- **Bundle:** single `index.html` (~18 KB) with layer registry inlined.
- **Basemaps:** Carto (Light/Dark), Esri (Streets/Satellite), OSM. No token.
- **Build toolchain:** tippecanoe (felt fork). Installed cold per chat via apt + git clone + make. ~45s.
- **Hosting:** Netlify Team Pro. Site `lrp-tx-gis`, siteId `01b53b80-687e-4641-b088-115b7d5ef638`. Link-only access.

---

## 2. Project file layout

All files flat at repo root. No subfolders for data files. The flat layout is settled; revisit only if file count exceeds ~50.

```
/                                 (repo root = working dir during chat)
  OPERATING.md                    operating rules (single canonical doc)
  ARCHITECTURE.md                 this file
  WIP_OPEN.md                     forward state, handoffs
  CREDENTIALS.md                  credential registry (gitignored)

  build.py                        reads layers.yaml + combined files, streams to tippecanoe
  build_template.html             MapLibre + PMTiles shell, /*__LAYERS__*/ placeholder
  build_sprite.py                 sprite-sheet builder
  layers.yaml                     layer registry — single config

  combined_points.csv             all point layers; layer_id column tags each row
  combined_geoms.geojson          all line/polygon features; layer_id property tags each feature
  geoms_parcels_pecos.geojson     standalone (large)
  fcc_fiber_coverage.geojson      standalone

  data/                           source archives (not read at build time)
  docs/                           supporting reference docs
  outputs/                        build outputs and refresh staging
  scripts/                        session-open, close-out, refresh, scrape utilities
  sprite/                         icon source PNGs
```

Standalone files are kept only when size or update cadence justifies it (e.g., `parcels_pecos`, prebuilt PMTiles ≥10MB).

---

## 3. Data pipeline

```
combined_*.{csv,geojson}  (committed to repo; canonical)
    │
    ▼  build.py filters by layer_id, splits to NDGeoJSON in /tmp
tippecanoe (per layer, via subprocess)
    │
    ▼
/mnt/user-data/outputs/dist/tiles/*.pmtiles   (ephemeral; rebuilt per chat)
    │
    ▼  Netlify MCP → CLI proxy deploy
https://lrp-tx-gis.netlify.app/tiles/*.pmtiles
    │
    ▼  HTTP range requests
browser
```

Build never materializes source data into model context. Streaming subprocess only.

---

## 4. Canonical schemas

**Combined points CSV:** `layer_id, name, lat, lon, <layer-specific...>`. WGS84, 6 decimals max. `layer_id` is first column. All other columns union across layers (blank where inapplicable).

**Combined geoms GeoJSON:** EPSG:4326, 2D coords (Z flattened). Every feature's `properties` carries `layer_id`, `source`, `source_date`. Line/polygon simplify tolerance 0.002–0.005, coords rounded to 4 decimals.

**Standalone files:** same schemas, no `layer_id` field (derived from filename).

**Tax-abatement column overload** (Chat 88 schema, locked): `inr` ← permit_no, `funnel_stage` ← permit status, `zone` ← received_date ISO, `project` ← num_units, `poi` ← agenda URL, `operator` ← applicant, `commissioned` ← meeting_date, `technology` ← project_type. Documented here because it's the canonical mapping; future schema additions follow the same pattern when `combined_points.csv` columns are reused for layer-specific fields.

**EIA-860 capacity** lives in the Generator sheet (`3_1_Generator_Y<year>.xlsx`), not the Plant sheet. Group generators by `Plant Code`, filter `Status == 'OP'`, sum `Nameplate Capacity (MW)`. Mode of `Technology` and `Energy Source 1` give plant-level fuel/tech labels. Coverage scales with vintage; 2024 release covers 891/1,367 of `eia860_plants` (65.2%, 178,542 MW total).

---

## 5. Layer catalog (current)

| Layer | Type | Features | Source | Cadence | Storage |
|---|---|---:|---|---|---|
| counties | line | 46 | Census TIGER 2023 | Rare | combined |
| cities | point | 9 | Hand toponyms | Rare | combined |
| caramba_north | fill | 1 | Project GeoJSON | Persistent | combined |
| mpgcd_zone1 | fill | 1 | MPGCD PDF (APPROXIMATE) | Replace when TWDB publishes | combined |
| aquifers | fill | 5 | TWDB ArcGIS | Annual | combined |
| wells | point | 14,700 | TWDB Groundwater | Quarterly | combined |
| eia860_plants | point | 1,367 | EIA-860 annual | Annual | combined |
| eia860_battery | point | 133 | EIA-860 annual | Annual | combined |
| wind | point | 19,464 | USWTDB API | Annual | combined |
| solar | point | 180 | EIA-860 3_3 | Annual | combined |
| transmission | line | 6,244 | HIFLD AGOL | Annual | combined |
| substations | point | 1,637 | OSM Overpass | Annual | combined |
| tpit_subs | point | 141 | ERCOT TPIT XLSX | Monthly | combined |
| tpit_lines | line | 133 | ERCOT TPIT XLSX | Monthly | combined |
| pipelines | line | 776 | RRC 2019 | Annual | combined |
| ercot_queue | point | 1,778 | ERCOT xlsx | Monthly | combined |
| tax_abatements | point | 9 | Commissioners-court agenda scrape | Weekly cron (planned) | combined |
| tceq_gas_turbines | point | 6 | TCEQ turbine-lst.xlsx | Annual | combined |
| tiger_highways | line | — | Census TIGER | Rare | prebuilt |
| rrc_pipelines | line | — | RRC | Annual | prebuilt |
| bts_rail | line | — | BTS | Rare | prebuilt |
| parcels_pecos | fill | 14,720 | StratMap TNRIS | Annual | prebuilt |
| fcc_fiber_coverage | fill | — | FCC BDC fixed-availability | Quarterly | standalone |
| waha_circle | point | 1 | Hand-placed | Persistent | combined |
| labels_hubs | point | — | Hand toponyms | Rare | combined |

**25 layers total live in prod** as of last close-out. Update this table when count changes.

**Prebuilt PMTiles** are resolved at build time via 3-tier lookup: `/mnt/project/<id>.pmtiles` → `/mnt/user-data/uploads/<id>.pmtiles` → `https://lrp-tx-gis.netlify.app/tiles/<id>.pmtiles`. Sources ≥10MB use this pattern with `prebuilt: true` in `layers.yaml`.

---

## 6. Adding a layer

1. `refresh <layer>` — produces file in `outputs/refresh/`.
2. `merge <layer> from outputs/refresh/<file>` — updated combined file in `outputs/`.
3. Operator uploads to `/mnt/project/` (or commit directly via clone-edit-push).
4. `add layer <id> from outputs/refresh. build. deploy to prod.`
5. `layers.yaml` append:

```yaml
- id: <layer>
  file: combined_points.csv | combined_geoms.geojson | <standalone>
  geom: point | line | fill
  group: <group>
  label: <display>
  color: '#<hex>'
  default_on: false
  popup: [field1, field2]
  min_zoom: 0
  tippecanoe: ['-zg']
```

For combined files, `build.py` infers row/feature membership by `layer_id`. For standalone files, the entire file is read.

`-zg` (auto-zoom) silently produces 0-feature PMTiles on single-feature inputs. Use explicit `-Z0 -z14` for single-feature point layers.

---

## 7. Frontend features

Sidebar grouped toggles (Land & Deal · Water & Regulatory · Generation · Transmission & Grid · Pipelines · Permits · Projects · Reference · Broadband). Basemap switcher, popups with source attribution, URL hash share, print view, coordinate readout, scale, fullscreen, nav, min-zoom gating, layer feature counts, Inter typeface.

Sidebar collapse via `#sb=1` URL hash. `parcels_pecos` is sidebar-hidden. Default basemap = `esri_imagery`. Default viewport = `-102.9707/30.9112 z12`.

Data-driven sizing live on: `ercot_queue`, `solar`, `eia860_plants`, `eia860_battery`, `wind`, `substations`, `tpit_subs`, `tpit_lines`. Static fallback gaps: `eia860_plants` 476/1367 null on capacity_mw; `transmission` no voltage attribute.

Filter UI: `filterable_fields:` schema in `layers.yaml` per layer. Numeric → range; categorical → multi-select (capped at 2000 distinct values, demoted to text-substring above cap); date → range; text → searchable substring.

Tax-abatement annotation: build-time fuzzy join matches `tax_abatements` applicants to `eia860_plants`, `ercot_queue`, `solar`, `wind`, `eia860_battery` rows by `(county, applicant_norm subset-of facility-name/entity/operator/project tokens)`. 5 annotations live; 9 abatement-layer features. Match rule is subset-only (Chat 85 tightening — token-overlap produces false positives on generic tokens like `ii`, `bess`, `solar`).

Backlog (no build without explicit ask): cross-layer search; measure tool persistence improvements; custom domain; legend-on-print; mobile-friendly responsive breakpoints.

---

## 8. Deployment

Netlify MCP returns single-use proxy URL. CLI proxy uploads. CDN warm-up window: 45–75s post-deploy. HEAD requests to `https://lrp-tx-gis.netlify.app/` return 503 even when GET is healthy — bot-detection heuristic. Verify with `curl -sI -A "Mozilla/5.0"` and grep GET output for layer-id count.

Default `curl` UA returns 503 on prod edge. Always pass `-A "Mozilla/5.0"`.

`build.py` emits `dist/_headers`, `dist/_redirects`, vendored `dist/pmtiles.js`. Never hand-edit those.

---

## 9. Known fragility

| Source | Issue | Countermeasure |
|---|---|---|
| AGOL FeatureServer cold fetch | 503 "DNS cache overflow" | 5-retry, 10s sleep |
| HIFLD transmission AGOL | 503 under retry | Same |
| RRC pipelines AGOL | 403 transient; `STATUS_CD='A'` → 0 rows | Use `STATUS_CD='B'` |
| Overpass API | All 3 endpoints can 503 | 3-endpoint fallback; else last cached |
| USPVDB | Chronic 503 | Skip to EIA-860 `3_3_Solar_Y2024.xlsx` |
| EIA-860 xlsx numerics | Whitespace, "NA", blanks | Route through `fnum()` |
| EIA-860M | URL returns HTML | Use annual zip only |
| EIA-860 annual zip | 503 without `Referer` header | `-H 'Referer: https://www.eia.gov/electricity/data/eia860/'` + `-A 'Mozilla/5.0'` |
| HIFLD Substations AGOL | Token-gated / 68-row subset | Use OSM Overpass only |
| TWDB AGOL layout | Dataset URL shifts | Use `arcgis.com/sharing/rest/search` |
| MPGCD Zone 1 | No vector source | APPROXIMATE digitization |
| Caramba GeoJSON | 3-tuple coords | `build.py` flattens to 2D |
| ERCOT TPIT page | 503 patterns | One attempt per session; skip on fail |
| Tippecanoe install | Container reset | Pin to felt fork, apt + make |
| TxGIO StratMap AGOL | Token-gated 499 | Use DataHub county zip route |
| Census Geocoder | 0 matches on West-TX municipalities | Fall back to OSM Nominatim, 1.1s throttle |
| Comptroller search DBs | JS-gated, 12–24mo lag | Use commissioners-court agenda scrape |
| Reeves County (`reevescounty.org`) | Akamai datacenter-egress block | No solution from cloud runners; flagged |
| Netlify prod URL `curl` | Default UA returns 503 | `-A "Mozilla/5.0"` |
| Netlify HEAD on root | 503 even when GET healthy | Use GET, grep markers |

---

## 10. Color palette

Pick from group hues; avoid reusing existing layer colors.

| Group | Hex |
|---|---|
| Land & Deal | `#78350f`, `#92400e`, `#6b7280` |
| Water & Regulatory | `#8b5cf6`, `#a855f7`, `#9333ea` |
| Generation | `#f59e0b`, `#dc2626`, `#84cc16`, `#eab308`, `#FFD400` |
| Transmission & Grid | `#0ea5e9`, `#0369a1`, `#075985`, `#38bdf8` |
| Pipelines | `#64748b` |
| Permits | `#6b21a8` |
| Projects | `#ec4899`, `#2E7D32` |
| Broadband | `#06b6d4` |
| Reference | `#64748b`, `#1e293b`, `#475569` |

---

## 11. Scoped-out sources

Permanently excluded. Revisit only on the listed condition.

| Source | Reason | Revisit if |
|---|---|---|
| `rrc_wells_permian` | RRC MFT GoAnywhere PrimeFaces — no direct-URL bulk | Bulk endpoint published |
| `tceq_pws` | HTTP 400 on original endpoint; operator declined | TCEQ publishes alternate feed |
| `tceq_pbr` | CRPUB HTML-only scrape; authorization declined | Operator authorizes scrape |
| `tceq_nsr_pending` | Same as `tceq_pbr` | Same |
| Comptroller LDAD bulk XLSX | Doesn't exist; per-record CSV only via JS-gated UI | Operator authorizes Selenium/Playwright |
| Per-county / per-chunk fetching at fetch time | No workflow fix; data-source-shape problem | Bulk endpoint discovered |

---

## 12. Appendix — fetch utilities

Used in refresh chats. Lives in `scripts/` rather than copy-pasted into chat code.

```python
import requests, time

def fetch_with_retry(url, params=None, attempts=5, timeout=60, headers=None, sleep=10):
    for i in range(attempts):
        try:
            r = requests.get(url, params=params, timeout=timeout, headers=headers or {})
            if r.status_code == 200:
                return r
        except Exception as e:
            print(f"  attempt {i+1} error: {e}")
        time.sleep(sleep)
    return None

def fnum(v):
    try:
        if v is None or v == '': return None
        x = float(v)
        return x if x == x else None
    except (TypeError, ValueError):
        return None
```
