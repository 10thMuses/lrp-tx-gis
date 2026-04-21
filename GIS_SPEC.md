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

## 12. SESSION PROTOCOL — BUDGETS + CIRCUIT BREAKERS

Every code-shipping session's **second silent step** (after pre-flight) declares a tool-call budget.

### Ceilings and circuit breakers by chat type

| Chat type | Ceiling | Circuit breaker | Typical use |
|---|---:|---:|---|
| Deploy-only | 3 | 2 | `deploy to prod.` no rebuild |
| Build + deploy | 4 | 3 | `build. deploy to prod.` |
| New-layer add + build + deploy | 6 | 5 | `add layer X. build. deploy.` |
| Refresh single layer | 4–10 | ceiling − 2 | `refresh <layer>.` |
| Merge + build + deploy | 8 | 6 | `merge X. build. deploy to prod.` |
| Interstitial (.5) | 12 | 10 | Hardening, observability, audit |
| Doc-install / refactor | 15 | 12 | Install or schema changes |

### Sub-allocation

- **Recon:** ≤2 composite bash calls per file touched; ≤5 total before first write
- **Writes:** 1 call per file (`str_replace` or `create_file`)
- **Commit-equivalent:** build = 1 `python3 build.py`; deploy = 1 MCP + 1 proxy bash
- **Verify:** 1 chained command (curl + grep + compare)
- **WIP update:** 1 call
- **Safety margin:** ceiling minus projected total; minimum 3 for doc-install and refactor chats

### Circuit breaker behavior

Fires at (ceiling − N) tool calls *without a shipped milestone*. A shipped milestone for GIS is:
- A PMTiles file written to `dist/tiles/`
- A file written to `outputs/refresh/`
- A `layers.yaml` block committed via `str_replace`
- A `WIP_OPEN.md` "Next chat" block committed

When circuit breaker fires: **abort, ship what's ready, write handoff to `WIP_OPEN.md`, close.** Do not attempt recovery. Next chat with a cleaner spec costs less.

---

## 13. SESSION PROTOCOL — AUTONOMOUS EXECUTION

See `PROJECT_INSTRUCTIONS.md` for the full rules. Summary of GIS-specific application:

### Banned phrases in code-shipping chats
- "Should I proceed with the build?"
- "Want me to deploy to prod or preview?"
- "Do you want me to refresh X first?"
- "Let me know if the popup fields look right."
- "Ready for the next batch?"
- "Before I do X, I wanted to check…"

### Acceptable asks (narrow, exhaustive)
1. Delete prod tiles / purge Netlify history / delete project files
2. Netlify plan upgrade, paid data source, custom domain
3. RRC pipelines 2019 vs. swap to PHMSA NPMS (data source fork)
4. AGOL / StratMap premium credentials
5. Layer naming for new thesis-specific layers; Grid Wire editorial decisions

Everything else Claude decides — tippecanoe flags, palette colors, popup order, default_on, min_zoom, §9 additions, handoff phrasing. Stated at close-out, not asked.

### Canonical automation patterns
- **Deploy chain:** Netlify MCP + proxy bash + verification curl chained with `&&`, one call.
- **New-layer add:** `str_replace` on `layers.yaml` + build + deploy. Three write-milestones, no re-reads.
- **Refresh merge:** fetch + merge + `str_replace` on nothing (data-only), one Python script per refresh.
- **Doc patches:** `str_replace` targeting section anchors, never full-file rewrites.
- **Verification:** `curl -sI https://lrp-tx-gis.netlify.app/tiles/<layer>.pmtiles | head -3 && curl -s https://lrp-tx-gis.netlify.app/ | grep -c <layer>` — one chained bash.

---

## 14. SESSION PROTOCOL — INTERSTITIAL CADENCE

Cross-cutting hardening ships in dedicated chats numbered `N.5` between feature chats (35 → 35.5 → 36 → 36.5 → …). `.5` does not increment the feature counter.

### Categories that always ship as interstitials
- §9 fragility table additions (new source failure patterns)
- `pmtiles.js` / CDN vendoring changes
- Popup field audits across layers
- `source_date` bookkeeping sweeps
- Tippecanoe flag density audits (when a dense layer drops features)
- Netlify `_headers` / `_redirects` / cache policy changes
- `SESSION_LOG.md` rotation / archival
- Credential provisioning audits

### Categories that are NOT interstitials
- Single-layer data refreshes tied to a feature chat
- `layers.yaml` schema changes tied to a new-layer chat
- MapLibre UI tweaks tied to a frontend feature

### Scheduling rule

Every feature chat N is scoped with its `.5` successor declared at the same time:

- New source → `.5` adds fragility entry + `fetch_with_retry` wrapper confirmation
- New layer density (>5k features) → `.5` audits tippecanoe flags + min_zoom
- New popup schema → `.5` audits source_date presence across all popups
- New MCP or credential surface → `.5` audits `CREDENTIALS.md`

If no such surface exists, handoff records explicit null: `.5: none warranted — styling tweak only, no new surface.` **Silent omission is a protocol regression.**

### Close-out gate

Every feature chat's close-out checklist (all mandatory):
1. `WIP_OPEN.md` updated with feature N's shipped entry
2. `SESSION_LOG.md` appended
3. N.5 handoff block declared (or null declaration)
4. Upload manifest printed (files to upload, files to delete)
5. Post-mortem sentence if budget overran or scope mis-set
6. Protocol amendment committed if operator corrected a banned behavior this chat

### Minimum viable interstitial rule

1. Default sink for observability is `SESSION_LOG.md`. New dedicated logs require justification.
2. Prefer extension over creation — extend `build.py` with a side effect rather than standing up a new script.
3. No speculative tooling. Ship primitives before analysis.
4. Split large surfaces across multiple `.5` chats if scope exceeds 12 calls.
5. Out-of-scope declaration mandatory in every `.5` handoff.

---

## 15. SESSION PROTOCOL — HANDOFF QUALITY GATE

Every handoff Claude writes to `WIP_OPEN.md` "Next chat" passes three checks before commit.

### Rule 1 — Facts pre-resolved, not deferred to recon

Before writing handoff, Claude resolves any concrete fact the execute chat would burn a recon call on: file paths, layer IDs, byte sizes, feature counts, tippecanoe flags in use, URLs, column names.

**"Check at recon" for a fact that exists NOW is a regression** — the handoff-write chat absorbs the cost because it's already in context.

**Red flag phrases (banned from handoffs):**
- "(or wherever X lives — confirm at recon)"
- "check what column name ercot_queue uses"
- "grep for the existing layer's popup fields"
- "find the tippecanoe flags for dense layers"
- "confirm the byte size"

Resolve inline at handoff-write time.

### Rule 2 — Verification tier matches blast radius

Every handoff states blast radius explicitly:

- **Low** (color change, label rename, single-layer min_zoom, popup field reorder): no in-chat verification; spot-check next session
- **Medium** (new layer, refresh + merge, new tippecanoe flag on dense layer, basemap change): chained curl tile probe + `grep -c <layer>` against live bundle + feature count check = one bash
- **High** (combined file schema change, `build.py` patch, `build_template.html` edit, Netlify `_headers` change, new credential surface, any refactor): full build + deploy-to-preview + curl probe of 3+ layers + URL hash share test + popup probe on sample features

Medium-tier verification on high-risk work is a regression. Specifically: any chat that modifies `build.py` or `build_template.html` is high-tier regardless of how small the diff looks.

### Rule 3 — Budget realism with line items

Handoff budget written as line items, not lump sum:

```
Recon: 1 composite bash (ls + head docs)
Writes: <n> files × 1 call each
Build: 1 python3 build.py
Deploy: 1 Netlify MCP + 1 proxy bash
Verify: 1 chained curl (tier per Rule 2)
WIP + SESSION_LOG update: 2 calls
Safety margin: 3
Projected: <total>
Ceiling: <tier ceiling from §12>
Circuit breaker: <ceiling − N>
```

Circuit breaker is an imminent-breach indicator, not a normal landing zone. If projected ≥ ceiling before margin, split the chat.

**Data-staging check (mandatory when handoff stages new data files for operator upload):**
Sum the bytes of all files the next chat expects in `/mnt/project/` — already-uploaded plus pending. If the total exceeds 12 MB (project-knowledge cap is ~12.7 MB), the handoff MUST flag this at write-time and offer the operator an explicit path decision (drop a file, compress, or pre-build to PMTiles). Silent omission of the staging check when adding a >2 MB data file is a §17-routed regression. Chat 36 failure pattern: handoff enumerated 3 data files summing ~16.5 MB without flagging the cap; chat 37 halted at pre-flight as a result.

---

## 16. SESSION PROTOCOL — PROTOCOL PERMANENCE

The three-part session protocol (§12-§15) survives across chats because it's anchored at four layers:

| Layer | Location | Consulted when |
|---|---|---|
| Rules doc | `GIS_SPEC.md` at `/mnt/project/` | First tool call of every GIS chat |
| Sidebar system prompt | Project Settings → Instructions field (`PROJECT_INSTRUCTIONS.md` content) | Every message, automatic |
| WIP doc | `WIP_OPEN.md` at `/mnt/project/` | Session open; close-out writes to it |
| Memory | `memory_user_edits` + project memory | Every message, automatic |

**Hierarchy:** `/mnt/project/` > sidebar > memory. If a rule in `/mnt/project/` contradicts memory, `/mnt/project/` wins. This prevents drift: memory-only rules are soft and can be forgotten; project-file rules are source-controlled via operator upload and survive.

**Build layer enforcement:** when a future `.5` interstitial lands a pre-commit check in `build.py` (e.g., "fail if `SESSION_LOG.md` not touched this chat"), protocol enforcement becomes four-layered — silent omission surfaces at build time, not just at next-chat pre-flight.

---

## 17. SESSION PROTOCOL — SELF-CORRECTION

When operator catches a protocol violation, the correction folds back as a rules-doc amendment **in the same session**. The amendment is permanent; operator should not have to correct the same thing twice.

### Amendment routing (where each category of correction lands)

| Correction | Target doc + section |
|---|---|
| Claude used a banned phrase | `PROJECT_INSTRUCTIONS.md` banned-phrases list + `GIS_SPEC.md §13` |
| Claude asked about something that was in the acceptable-asks list but narrower than stated | `GIS_SPEC.md §13` acceptable-asks refinement |
| Claude deferred a fact to recon that existed at handoff-write time | `GIS_SPEC.md §15` Rule 1 red-flag list |
| Claude used wrong verification tier for blast radius | `GIS_SPEC.md §15` Rule 2 high-risk category list |
| Claude understated budget at handoff | `GIS_SPEC.md §15` Rule 3 line-item template |
| Claude missed an N.5 successor that should have been declared | `GIS_SPEC.md §14` scheduling-rule category table |
| Claude re-read a file just written | `GIS_SPEC.md §11` banned-patterns list |
| New source failure mode discovered | `GIS_SPEC.md §9` fragility table |
| Environment constraint discovered | `README.md` environment section |

### Post-mortem discipline

When a session overruns budget, mis-scopes, or requests operator involvement that turned out to be unnecessary, close-out includes:
1. One sentence naming the failure mode
2. One rules-doc line preventing recurrence (committed in the same close-out, not a separate chat)

No separate "debrief" session. Folded into normal close-out.

### Cross-project learning

Learnings that generalize across projects (sister + this one + future siblings) get written generically enough to install on other projects. The `PROJECT_INSTRUCTIONS.md` banned-phrases list, `§15` red-flag handoff phrases, and `§14` interstitial category tables are examples — stack-agnostic rules that port directly.

When a learning lands in this project that would help the sister, operator propagates via a short additive install doc. When the sister's learnings arrive (as in chats 34-36), they fold into the relevant section here per the routing table above.

---

## 18. SESSION PROTOCOL — EXPECTED OPERATOR EXPERIENCE

If the protocol is working, operator should observe these shifts within 2-3 chats after install:

1. **Claude stops asking for confirmation on routine tasks.** Judgment calls appear as one-line statements at close-out instead of permission-seeking upfront.
2. **Handoff prompts Claude writes get longer and more specific.** Budget projections appear as line items. Blast radius explicit. File paths resolved inline. No "check at recon" for facts that exist at handoff-write time.
3. **Chat sequence alternates feature (N) and interstitial (N.5).** Observability + fragility coverage compounds automatically.
4. **Execute-chat sessions hit budgets more cleanly.** Fewer abort events. Fewer recon calls burned on fact-lookups. Circuit breaker fires rarely.
5. **Pre-flight check catches drift early.** `ls /mnt/project/` + `head` of WIP/SESSION_LOG at chat open prevents the chat-34 / chat-35 class of failure (handoff references a state that no longer exists).
6. **Session log accumulates, becomes useful.** By chat 45-50, `SESSION_LOG.md` is a queryable artifact — what source failures have we hit, what's the fragility drift, what chats over-ran.

**If any of these fail to materialize after 2-3 chats under the new protocol, the relevant section needs amendment.** Operator feedback triggers the self-correction loop per §17. Specifically:

- If Claude still asks permission → add the phrase used to banned list
- If handoffs stay vague → add phrases seen to §15 Rule 1 red flags
- If .5 chats get skipped → tighten §14 category table with the missed case
- If budgets still slip → revisit §12 ceilings with actual tool-call data from SESSION_LOG

---

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
