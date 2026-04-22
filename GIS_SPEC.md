# Texas Energy GIS Map — Build Specification

**Owner:** Andrea Himmel, Land Resource Partners
**Audience:** Claude, every session. Read first. Replaces all prior specs.
**Stack:** MapLibre GL JS + PMTiles, built with tippecanoe, hosted on Netlify.
**Last updated:** 2026-04-20

---

## 0. TRIGGER PHRASES

| Phrase | Claude action |
|---|---|
| `build.` | Install tippecanoe if needed, run `build.py`, emit `dist/`. No deploy. |
| `build. deploy to preview.` | Build + deploy to Netlify branch preview. |
| `build. deploy to prod.` | Build + deploy to `https://lrp-tx-gis.netlify.app`. |
| `deploy to prod.` | Re-deploy existing `dist/` without rebuild. |
| `refresh <layer>[, <layer>...].` | Fetch listed layers, write to `outputs/refresh/`. No build. |
| `refresh all.` | Fetch every layer with a known source. Heavy session. |
| `merge <layer_id> from outputs/refresh/<file>.` | Read refresh file, swap that layer's rows/features inside `combined_points.csv` or `combined_geoms.geojson`, write updated combined file to `outputs/`. |
| `add layer <id> from outputs/refresh.` | Append block to `layers.yaml`, build, deploy to preview. |
| `promote to prod.` | Deploy current preview to prod. |
| `password-protect with <pw>.` | Call Netlify access-control MCP. |
| `resume.` | Read `WIP_OPEN.md` "Next chat" handoff block and execute. |

Ambiguity → Claude picks the most plausible interpretation, executes, notes assumption at close-out. Never asks "should I proceed?".

---

## 1. HARD RULES

1. **Build never reads source data into model context.** Combined files and any standalone data files stream through `tippecanoe` subprocesses. Claude never `cat`s or parses data files for its own reading. Single biggest token-burn failure mode.
2. **All project files flat in `/mnt/project/`.** No subfolders.
3. **Never fetch during build.** Missing source → skipped layer, logged to `SESSION_LOG.md`.
4. **Never hand-code coordinates or feature values.** If no source exists, skip.
5. **Never re-digitize from PDFs when a vector source exists.** Last resort only; mark `ACCURACY: APPROXIMATE`.
6. **One layer failure never aborts the run.** Try/except at dispatcher. Log, skip, continue.
7. **One chat = one final build.** No version numbering. Output always `dist/index.html` + `dist/tiles/*.pmtiles`.
8. **Adding a new layer = one yaml append + one data-file action.** Either drop a new standalone file into `/mnt/project/` OR merge into the combined file via the `merge.` trigger. Never edit `build.py` or `build_template.html` for a new layer.
9. **No recaps, no "ready to proceed?", no "let me know if".** Execute.
10. **Do not deploy to prod if build report shows `errored > 0`.** Stop and report.
11. **Pre-flight check mandatory.** First tool call of every GIS chat: composite `bash` of `ls /mnt/project/` + `head` of `WIP_OPEN.md` and `SESSION_LOG.md`.
12. **Handoff produced every chat.** Not just on budget exhaustion. Passes 3-rule gate in §15 before writing to `WIP_OPEN.md`.

---

## 2. PROJECT FILE LAYOUT

All files flat at `/mnt/project/`. No subfolders.

```
/mnt/project/
  ── Docs ─────────────────────────────
  README.md                   ← cold-context pointer
  PROJECT_INSTRUCTIONS.md     ← also pasted into project settings
  GIS_SPEC.md                 ← this doc, authoritative
  COMMANDS.md                 ← operator trigger reference
  CREDENTIALS.md              ← credential registry
  WIP_OPEN.md                 ← forward state, handoffs, pinned forward protocol
  SESSION_LOG.md              ← append-only outcome log

  ── Build toolchain ──────────────────
  build.py                    ← reads layers.yaml + combined files, streams to tippecanoe
  layers.yaml                 ← layer registry
  build_template.html         ← MapLibre + PMTiles shell, /*__LAYERS__*/ placeholder

  ── Data sources ─────────────────────
  combined_points.csv         ← all point layers, selected by `layer_id` column
  combined_geoms.geojson      ← all line/polygon layers, selected by `layer_id` property
  geoms_parcels_pecos.geojson ← standalone (large, post-compression)
  ── any other standalone when warranted by size ──
```

**Combined architecture (post-chat-34 refactor):**

- `combined_points.csv` — one canonical CSV with `layer_id` as first column; `build.py` filters per layer via `layer_id == <id>` before streaming.
- `combined_geoms.geojson` — one FeatureCollection; each feature has `properties.layer_id`; `build.py` filters per layer before streaming.
- Layers stay standalone only when size or update cadence warrants it (e.g., `parcels_pecos`).

---

## 3. ARCHITECTURE

### Runtime
- **Frontend:** MapLibre GL JS 4.7.1 + pmtiles.js 4.3.0 (pmtiles.js vendored same-origin as of chat 27).
- **Tile format:** PMTiles binary archives. Browser fetches only visible tiles via HTTP range requests.
- **Bundle:** single `index.html` (~18 KB) with layer registry inlined.
- **Basemaps:** Carto (Light/Dark), Esri (Streets/Satellite), OSM. No token.

### Data pipeline
```
/mnt/project/combined_*.{csv,geojson}  (operator uploads; persists)
    │
    ▼  build.py filters by layer_id
tippecanoe (per layer, via stdin)
    │
    ▼
/mnt/user-data/outputs/dist/tiles/*.pmtiles  (ephemeral; rebuilt per chat)
    │
    ▼  Netlify MCP deploy
https://lrp-tx-gis.netlify.app/tiles/*.pmtiles
    │
    ▼  HTTP range requests
browser
```

### Canonical schemas
- **Combined points CSV:** `layer_id, name, lat, lon, <layer-specific...>`. WGS84, 6 decimals max. `layer_id` is first column; all other columns union across layers (blank where inapplicable).
- **Combined geoms GeoJSON:** EPSG:4326, 2D coords (Z flattened). Every feature's `properties` has `layer_id`, `source`, `source_date`. Line/polygon simplify tolerance 0.002–0.005, coords rounded to 4 decimals.
- **Standalone files:** same schemas, no `layer_id` field (derived from filename).

---

## 4. BUILD CYCLE — cold chat to deployed URL

Target: 4 tool calls for `build. deploy to prod.`. See §12 for budget structure.

1. **Install + build** (one composite bash, ~45s cold, instant warm):
   ```bash
   which tippecanoe >/dev/null 2>&1 || (
     apt-get install -y build-essential libsqlite3-dev zlib1g-dev >/dev/null 2>&1 &&
     cd /tmp && git clone --depth 1 https://github.com/felt/tippecanoe.git >/dev/null 2>&1 &&
     cd tippecanoe && make -j4 >/dev/null 2>&1 && make install >/dev/null 2>&1
   )
   pip install pyyaml --break-system-packages -q
   cd /mnt/project && python3 build.py
   ```

2. **Deploy** (one MCP call): `Netlify:netlify-deploy-services-updater deploy-site --siteId=01b53b80-687e-4641-b088-115b7d5ef638`.

3. **Run proxy** (one bash): `cd /mnt/user-data/outputs/dist && npx -y @netlify/mcp@latest ...` → returns `siteUrl`.

4. **Present** (one present_files): `dist/index.html` + URL at close-out.

---

## 5. REFRESH + MERGE CYCLE

`refresh <layer>`:
1. Fetch via `fetch_with_retry(url, attempts=5, sleep=10)`.
2. Validate non-empty, required columns, bounded lat/lon.
3. Simplify line/polygon; round coords; trim to registered fields.
4. Write `/mnt/user-data/outputs/refresh/<canonical_filename>`.
5. Report one-line diff. Fetch failure: log `FETCH_FAILED` to `SESSION_LOG.md`; do not fake.

`merge <refreshed_file>`:
1. Read refreshed file.
2. Read `combined_points.csv` or `combined_geoms.geojson` (streamed; never into context as inspection).
3. Drop rows/features where `layer_id == <id>`; append refreshed with `layer_id` set.
4. Write updated combined file to `/mnt/user-data/outputs/`.
5. Operator uploads over the previous combined file in project knowledge.

Target: 4–10 tool calls.

---

## 6. LAYER CATALOG (as of 2026-04-20)

| Layer | Type | Features | Source | Cadence | In |
|---|---|---:|---|---|---|
| counties | line | 46 | Census TIGER 2023 | Rare | combined |
| cities | point | 9 | Hand toponyms | Rare | combined |
| caramba_north | fill | 1 | Project GeoJSON | Persistent | combined |
| caramba_south | fill | 1 | Project GeoJSON | Persistent | combined |
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
| parcels_pecos | fill | 14,720 | StratMap TNRIS | Annual | **standalone** |

**Pending:**
1. `tceq_permits` — CRPUB scrape + Census Geocoder
2. `dc_sites` — requires operator-compiled source CSV

---

## 7. FRONTEND FEATURES

Sidebar grouped toggles (Land & Deal / Water & Regulatory / Generation / Transmission & Grid / Pipelines / Projects / Reference), basemap switcher, popups with source attribution, URL hash share, print view, coordinate readout, scale, fullscreen, nav, min-zoom gating, layer feature counts, Inter typeface.

**Backlog** (no build without explicit ask): filter UI, cross-layer search, measure tool, custom domain, legend modal.

---

## 8. DEPLOYMENT

- **Site:** `lrp-tx-gis` | **siteId:** `01b53b80-687e-4641-b088-115b7d5ef638` | **Prod:** `https://lrp-tx-gis.netlify.app` | **Plan:** Team Pro | **Access:** link-only

`build.py` emits `dist/_headers`, `dist/_redirects`, and vendored `dist/pmtiles.js`. Never hand-edit.

---

## 9. KNOWN FRAGILITY

| Source | Issue | Countermeasure |
|---|---|---|
| AGOL FeatureServer cold fetch | 503 "DNS cache overflow" | 5-retry, 10s sleep |
| HIFLD transmission AGOL | 503 under retry | Same |
| RRC pipelines AGOL | 403 transient; `STATUS_CD='A'` → 0 rows | Use `STATUS_CD='B'` |
| Overpass API | All 3 endpoints can 503 | 3-endpoint fallback; else last cached |
| USPVDB | Chronic 503 | Skip to EIA-860 `3_3_Solar_Y2024.xlsx` |
| EIA-860 xlsx numerics | Whitespace, "NA", blanks | Route through `fnum()` |
| EIA-860M | URL returns HTML | Use annual zip only |
| HIFLD Substations AGOL | Token-gated / 68-row subset | Use OSM Overpass only |
| TWDB AGOL layout | Dataset URL shifts | Use `arcgis.com/sharing/rest/search` |
| MPGCD Zone 1 | No vector source | APPROXIMATE digitization |
| Caramba GeoJSON | 3-tuple coords | `build.py` flattens to 2D |
| ERCOT TPIT page | 503 patterns | One attempt per session; skip on fail |
| Tippecanoe install | Container reset | Pin to felt fork, apt + make |
| TxGIO StratMap AGOL | Token-gated 499 | Use DataHub county zip route |

---

## 10. ACCEPTANCE CRITERIA

**Build done:**
- `dist/index.html`, `dist/tiles/<id>.pmtiles`, `dist/_headers`, `dist/_redirects`, `dist/pmtiles.js` all exist.
- Every `layers.yaml` entry either has a tile file OR is logged MISSING/ERROR to `SESSION_LOG.md`.
- Final line: `built=<n>  missing=<n>  errored=<n>  tiles_total=<kb>`.

**Deploy done:** Netlify MCP returns `{"state":"ready", ..., "siteUrl":...}`; URL printed at close-out.

**Refresh done:** Each named layer has a file in `outputs/refresh/` OR logged `FETCH_FAILED`; one-line diff per layer.

**Chat done:** `WIP_OPEN.md` updated with shipped entry; `SESSION_LOG.md` appended; Next-chat handoff passes 3-rule gate; upload manifest printed.

---

## 11. CRITICAL GUARDRAILS

- **Chat label** first line of first response: `**N - YYYY-MM-DD HH:MM - Title**`. Increment `memory_user_edits` same turn.
- **Do-all mode.** Zero asks per chat target; one hard ceiling (see `PROJECT_INSTRUCTIONS.md`).
- **When in doubt, skip and log.** Never fabricate.
- **Read this doc on first turn of every GIS chat.**
- **Banned patterns** (token-waste prohibitions):
  - `cat` / `head` / `view` of data files — ever
  - Re-viewing a file immediately after `str_replace` to it
  - Duplicate `web_search` with rephrased terms in same chat
  - `ls /mnt/project/` twice in one chat
  - Re-reading `GIS_SPEC.md` sections already visible in context
  - `tippecanoe --version` after first install confirmation this chat
  - Re-fetching files just committed
  - Handoff anchors (counts, siteIds, byte sizes, paths) are authoritative — do not re-verify

---


## 12–18. Session Protocol

Consolidated into `Readme.md` §7 and `docs/principles.md` §2. Sections removed 2026-04-22 (Chat 70).

## APPENDIX A — Fetch utilities (refresh chats)

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

---

## APPENDIX B — Adding a layer (checklist)

1. `refresh <layer>` chat → file in `outputs/refresh/`.
2. `merge <layer> from outputs/refresh/<file>` chat → updated `combined_points.csv` or `combined_geoms.geojson` in `outputs/` (or keep standalone if >5 MB).
3. Operator uploads to `/mnt/project/`.
4. `add layer <id> from outputs/refresh. build. deploy to prod.`
5. `layers.yaml` append (under the `layers:` root key):
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
   For combined files, `build.py` infers which rows/features belong to this layer by matching `id` against the `layer_id` tag in the combined source. For standalone files, the entire file is read.
6. Build + deploy. `.5` handoff declared.

---

## APPENDIX C — Color palette

| Group | Hex |
|---|---|
| Land & Deal | `#78350f`, `#92400e`, `#6b7280` |
| Water & Regulatory | `#8b5cf6`, `#a855f7`, `#9333ea` |
| Generation | `#f59e0b`, `#dc2626`, `#84cc16`, `#eab308` |
| Transmission & Grid | `#0ea5e9`, `#0369a1`, `#075985`, `#38bdf8` |
| Pipelines | `#64748b` |
| Projects | `#ec4899` |
| Reference | `#64748b`, `#1e293b` |

Pick from group hues; avoid reusing existing layer colors.
