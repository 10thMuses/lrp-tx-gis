## Chat 77 — 2026-04-23 — EIA-860 enrichment + capacity_mw coalesce + deploy path migration

**Classification:** shipping, MEDIUM blast radius. Data-pipeline refresh (`combined_points.csv`) + yaml popups + template sizing expressions. No schema changes. Build + deploy + close-out.

**Commit:** `9d40df4` on `main`. Parent `a379539` (Chat 76 UI polish).

**Shipped:**

| Area | Change |
|---|---|
| `combined_points.csv` | EIA-860 Form 2024 join on `plant_code` — 891/1367 plants (65.2%) gained `capacity_mw` + `technology` + `fuel`. Fuel code map: NG→Natural gas, WAT→Hydro, NUC→Nuclear, SUB/BIT/LIG→Coal, DFO→Oil, SUN→Solar, WND→Wind, MWH→Battery. Unknowns nulled (not invented). |
| `combined_points.csv` | Capacity column coalesce: `eia860_battery.capacity → capacity_mw`; `ercot_queue.mw → capacity_mw`; `wind.cap_kw / 1000 → capacity_mw`; `solar` + `tceq_gas_turbines` already on `capacity_mw`. Source columns retained for provenance. |
| `layers.yaml` | Popup additions: `eia860_plants` adds `capacity_mw` + `technology` + `fuel`; `ercot_queue` swaps `mw` → `capacity_mw`; `eia860_battery` + `wind` add `capacity_mw`. |
| `build_template.html` | Sizing expressions updated: `ercot_queue` sizing field `mw` → `capacity_mw`; `wind` sizing field `cap_kw` → `capacity_mw` with MW-range rescale (0–5 MW instead of 0–5000 kW). |

**Expected-vs-actual coverage post-enrichment:** `eia860_plants` 891/1367 ✓, `eia860_battery` 133/133 ✓, `ercot_queue` 1708/1778, `solar` 180/180, `wind` 19269/19464, `tceq_gas_turbines` 6/6. Total ~22,187 rows with capacity data.

**Build verify:** `python build.py` → `built=22, missing=0, errored=0, tiles_total=17529 KB`. All 22 layers clean.

**Deploy:** `69ea73f92acb1109e87b4ddc` — via **Netlify REST API + `NETLIFY_PAT`** (not MCP proxy). Deploy state reached `ready` on first poll (~6s). Prod verified post-warmup (~90s): HTTP/2 200, 22 layer IDs in HTML, 17 `capacity_mw` popup references, tile + sprite spot-checks all 200.

**Anomalies — Netlify MCP proxy 503 (blocker):**

1. **First attempt (Chat 77 shipping chat):** `npx @netlify/mcp@latest --proxy-path <url>` returned 503 on `zipAndBuild`. Netlify MCP surfaces this as `Error: Failed to deploy site: 503 Service Unavailable` from `netlify-mcp.js:540`. Chat 77 closed with commit pushed but deploy blocked.
2. **Second attempt (resume chat):** Pulled fresh proxy URL via `Netlify:netlify-deploy-services-updater` MCP call. Same 503, same call site. `netlifystatus.com` showed all systems operational — failure is in the MCP proxy service (`netlify-mcp.netlify.app`), which is a separate Netlify-hosted app not covered by the main status page.
3. **Resolution:** Migrated deploy path to Netlify REST API. Operator generated PAT at `app.netlify.com/user/applications/personal` (description: "Claude GIS deploys"), pasted into chat context. Deploy via `curl -X POST -H "Authorization: Bearer $PAT" -H "Content-Type: application/zip" --data-binary @/tmp/d.zip https://api.netlify.com/api/v1/sites/$SITE/deploys`. Succeeded first try. CDN warmup took ~90s (vs. 45s prior norm) before edge 503s cleared.

**Process change:** Netlify REST API is now canonical deploy path for this site. `WIP_OPEN.md` "Prod status" block updated to note this. Future chats' `## Next chat` spec references REST API with PAT pulled from `CREDENTIALS.md` (when present) or pasted at top of resume prompt.

**Credentials state:** Project knowledge file `CREDENTIALS.md` is not editable in current Claude UI (no edit or delete affordance). `NETLIFY_PAT` could not be added to the file during this chat — operator pasted token directly into chat context instead. Going forward either (a) operator pastes token into each chat resume prompt, or (b) CREDENTIALS.md edit path becomes available and token gets committed there.

**npm cache corruption (incidental):** First MCP retry attempt in resume chat hit `npm error ENOENT` on `@netlify/zip-it-and-ship-it` — tarball corruption mid-install. Cleared `/home/claude/.npm/_npx` + `_cacache`; second attempt made it past npm install to the actual 503. Not a recurring concern once REST API is adopted.

**Diff size:** data columns repopulated across 21k+ rows in `combined_points.csv`; ~6 lines in `layers.yaml`; ~4 lines in `build_template.html` sizing expressions. Net commit delta modest at line level but data content meaningful.

**Close-out note:** Close-out docs (this entry + WIP_OPEN rewrite) landed in the resume chat, not the shipping chat, because the shipping chat stopped at the MCP 503 blocker before writing close-out.

**Next-chat trigger:** `Resume.` → Chat 78 (semantic icons + MW-driven sizing). Spec in `WIP_OPEN.md` `## Next chat`.

---

## Chat 76 — 2026-04-23 — UI polish — 10 label/layout tweaks shipped

**Classification:** shipping, LOW blast radius. Yaml + template only — no data pipeline, no new layers, no schema changes. Build + deploy + close-out.

**Commit:** `a379539` on `main`. Parent `8da2b0f` (Chat 75b close-out).

**Shipped (10 of 11; #4 deferred to Chat 78 per plan):**

| # | Change | File |
|---:|---|---|
| 1 | Sidebar multi-select filters → collapsible `<details>` dropdowns with live selection count in summary (e.g. `County (12)` / `County — 3 selected`). CSS + `filterFieldControlHtml()` refactor. | `build_template.html` |
| 2 | Title-case all multi-word layer labels. | `layers.yaml` |
| 3 | `"Solar plants (EIA-860)"` → `"Solar Farms (EIA-860)"`. | `layers.yaml` |
| 4 | **DEFERRED to Chat 78** — semantic icons by fuel/technology. Requires EIA-860 enrichment (Chat 77). | — |
| 5 | `"EIA-860 plants"` → `"Power Plants (EIA-860)"`. | `layers.yaml` |
| 6 | `GROUP_ORDER` reordered: `Water & Regulatory` moved to end (after `Reference`). | `build_template.html` |
| 7 | `"Natural gas hub"` → `"WAHA Natural Gas Hub"`; `show_marker: true` on `labels_hubs` (label layer) renders a circle marker via new `${id}__marker` circle sublayer wired through `addLayer()` + `setLayerVisibility()` + `applyLayerFilter()`. | `layers.yaml` + `build_template.html` |
| 8 | `"ERCOT GIR queue"` → `"ERCOT Interconnect Queue (as of 2026-04-21)"`. Vintage from ERCOT xlsx source date. | `layers.yaml` |
| 9 | `"TWDB wells"` → `"Groundwater Wells (TWDB)"`. | `layers.yaml` |
| 10 | `"MPGCD Zone 1 (approx.)"` → `"Groundwater District Management Zone 1"`. | `layers.yaml` |
| 11 | `"RRC pipelines (≥20\" transmission)"` → `Oil & Gas Pipelines (>20\", RRC)`. | `layers.yaml` |

**Template additions for `geom: label` + `show_marker`:**
- `addLayer()`: new `${id}__marker` circle sublayer (radius 6, fill = layer color, white 2px stroke) inserted below the label symbol layer.
- `setLayerVisibility()`: marker toggle wired alongside existing icon handling.
- `applyLayerFilter()`: marker filter wired.

**Handoff doc removed:** `docs/_chat76_handoff.md` (210 lines) — specs folded into commit message and this log entry.

**Build verify:** deferred per commit authorship. Deploy gate verified post-fact via live HTML parse: `layer count = 22`, all 10 renamed labels present, `GROUP_ORDER` ends `…Reference, Water & Regulatory`, `WAHA Natural Gas Hub` live.

**Deploy:** commit shipped to prod; specific Netlify `deployId` not captured in-session (Netlify MCP deploy call made outside chat-level close-out). Prod commit reference: `a379539`. Live verification via `curl -s -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/` confirms all tweaks in served HTML.

**Diff size:** `+49 / -229` (net `-180` lines — handoff doc deletion dominates). Actual tweak delta: `build_template.html +37 / -4`, `layers.yaml +~15 / -15` (renames).

**Close-out note:** Close-out docs (this WIP_LOG entry + WIP_OPEN rewrite) landed in a follow-up chat, not in the shipping commit. `WIP_OPEN.md` `## Next chat` had remained at Chat 76 until Chat 77 opened; state reconciled then.

**Next-chat trigger:** `Resume.` → Chat 77 (EIA-860 enrichment). Spec already in `WIP_OPEN.md` `## Next chat`.

---

## Chat 71 (part 2) — 2026-04-22 — Stage 4 SIZING + WATERMARK shipped

**Classification:** shipping, MEDIUM blast radius. Template-only change (no yaml, no data). Branch + build + deploy + merge.

**Branch:** `refinement-sizing-watermark` from `main` (`2f18ea8`). Commit `c202428`. Merged via `--no-ff` → merge commit `026eff2`. Remote branch delete pending next session-cleanup (kept for traceability this session).

**Shipped in `build_template.html`:**
- `SIZING_RULES` lookup + helpers (`sizingRadiusExpr`, `sizingLineWidthExpr`, `sizingIconSizeExpr`) with MapLibre `interpolate` expressions.
- **MW scaling (circle-radius 3→15px, icon-size 0.45→1.2):** `ercot_queue` (field `mw`), `solar` (`capacity_mw`), `eia860_battery` (`capacity`), `wind` (`cap_kw` ÷ 1000).
- **kV scaling:** `substations`, `tpit_subs` (circle-radius 3→14); `tpit_lines` (line-width 1.5→4).
- Wired into `layerPaint()` for `circle-radius` + `line-width`, and symbol layer for `icon-size`.
- Watermark: `<div class="watermark">CONFIDENTIAL — <span id="wm-date">YYYY-MM-DD</span></div>`, bottom-right, 78% red on white pill, cleared above scale+attribution stack. Date populated in `map.on('load')`.
- Print CSS repositions watermark to corner when sidebar/topbar hidden. Also wired `print-date` (previously hardcoded-empty) with build date.

**Sizing gaps flagged (not guessed):**
- `eia860_plants` 1367 rows, 0 with non-zero `capacity_mw` / `mw` / `capacity` — no data-driven sizing; static radius.
- `transmission` geoms have no `voltage` field in sample — no data-driven sizing; static width 2.
- `tpit_subs` only 78/141 have voltage; `substations` 1137/1637. Fallback expression uses `L.radius` when value is 0.

**Data audit** (from `combined_points.csv`):

| layer | total | mw | capacity | capacity_mw | cap_kw | voltage |
|---|---:|---:|---:|---:|---:|---:|
| ercot_queue | 1778 | **1702** | — | — | — | — |
| solar | 180 | — | — | **180** | — | — |
| wind | 19464 | — | — | — | **19267** | — |
| eia860_battery | 133 | — | **133** | — | — | — |
| substations | 1637 | — | — | — | — | **1137** |
| tpit_subs | 141 | — | — | — | — | **78** |
| eia860_plants | 1367 | 0 | 0 | 0 | 0 | — |

**Build verify:** `python3 build.py` clean — 21/21 layers, 0 missing, 0 errored, 17,478 KB tiles_total. Template output confirmed: `class="watermark"` ×1, `SIZING_RULES` ×4, `sizingRadiusExpr` ×2.

**Deploy:** `69e96a36b4de5c3af264ab27` via Netlify MCP (first attempt failed with 500 upstream, retried with fresh proxy token → succeeded). Verification:
- `GET /` → 200
- Served HTML contains `class="watermark"` + `SIZING_RULES` (confirmed via `curl | grep -c`)
- `GET /sprite/sprite.png` → 200 (Stage 3 artifacts intact)

**Merge push:** `2f18ea8..026eff2` on `main`.

**Budget:** 8 additional tool calls for Stage 4 (1 refinement-seq view + 1 field audit + 2 template views + 1 patch+build + 1 MCP deploy-call + 1 deploy+verify + 1 WIP+log). Combined chat total: ~21 tool calls.

**Scope note — TCEQ REFRESH deferred:**

Operator requested "do gis for 3 and then stage 4" this chat. Stage 4 shipped. TCEQ REFRESH (item 3) NOT attempted. Reasons: (a) `tceq_pws` carries pre-existing "scope-confirm needed" flag from prior chat, (b) CRPUB scrape complexity is unbounded discovery, (c) §7.6 rule "one shipping chat at a time" already strained by dual close-out (Stage 3 merge + Stage 4 ship).

**TCEQ scope ask for next chat (batched per §2):**

1. **`tceq_pws` in or out?** Original endpoint returns HTTP 400. Options: (a) drop entirely, (b) retry with new endpoint discovery, (c) operator supplies CSV.
2. **Data acquisition approach for `tceq_gas_turbines` / `tceq_nsr_pending` / `tceq_pbr`?** CRPUB (TCEQ Central Registry Public) is ASP.NET PostBack-heavy; scrape is possible but session-state fragile. Alternatives: TCEQ bulk air-permit downloads (if exist), operator-provided CSVs from CRPUB UI.
3. **Geographic scope?** 23-county West Texas (matching abatement scope) or statewide?
4. **Time/status filters?** All permits vs. active only vs. date-filed ≥ 2020?

Without these inputs, TCEQ REFRESH cannot ship cleanly.

**Next-chat trigger:** `start tceq refresh` (after answering the 4 scope questions above) OR `start abatement discovery` (parallel-safe, requires no additional scope).

---

## Chat 71 — 2026-04-22 — Stage 3 Visual Overhaul closed, prod deploy

**Classification:** shipping, MEDIUM blast radius. Merge + build + deploy + branch delete.

**Branch:** `refinement-visual-overhaul` merged to `main` via `git merge --no-ff` → merge commit `ebe5634`. Remote branch deleted post-merge.

**Shipped:**
- Palette revisions on `rrc_pipelines`, `tpit_subs`, `tpit_lines`, `counties` (resolved 5 blue/gray collision points identified Chat 69).
- Contrast/weight bump per Stage 3 plan.
- Sprite sheet: 5 icons (solar, wind, battery, plant, well) @ 1x + 2x, generated via `build_sprite.py` using cairosvg. `sprite/sprite.png` (5108 B), `sprite/sprite@2x.png` (11266 B) + `.json` manifests committed at repo root.
- `build_template.html` rewired: `rasterStyle()` now loads `/sprite/sprite`, symbol layer uses `icon-image` on 5 point layers.
- Handoff doc `docs/_stage3_handoff.md` retired on branch prior to merge.

**Build verify:** `python3 build.py` clean — 21/21 layers built, 0 missing, 0 errored, 17,478 KB tiles_total. Sprite generator wrote 5 icons @ 1x + 2x as expected.

**Deploy:** `69e95f7ddf3b142326cb43cc` via Netlify MCP (`npx @netlify/mcp@latest --no-wait`). Verification:
- `GET /` → 200
- `GET /sprite/sprite.png` → 200, `image/png`, 5108 B
- `GET /sprite/sprite@2x.png` → 200, 11266 B

**Merge push:** `f83bd70..ebe5634` on `main`. Remote branch delete: `git push origin --delete refinement-visual-overhaul` clean.

**Budget:** 7 tool calls (2 view + 1 clone/merge/build bash + 1 MCP deploy-tool + 1 deploy bash + 1 verify bash + 1 WIP/log bash + 1 final commit/push). Within §11 build-chat budget.

**Next-chat trigger:** no specific trigger set. Stage 4 per `docs/refinement-sequence.md` available when operator chooses.

---

## Chat 70 — 2026-04-22 — Token-efficiency doc-only sweep

**Classification:** doc-only, LOW blast radius. No code, no build, no deploy.

**Driver:** cross-project protocol advisory + prior-response sidebar audit. Merged priority list: ship structural cuts now, instruct next chat on behavioral cuts + operator-side sidebar purge.

**Shipped:**
- Deleted from repo: `COMMANDS.md` (8.5 KB, triggers optional per settled.md), `ENVIRONMENT.md` (3.6 KB, stale per principles.md §103), `HANWHA_SPRINT_closed.md` (archive, belongs in git history).
- `GIS_SPEC.md`: cut §12–18 (lines 256–496, 241 lines of session-protocol content duplicating `Readme.md` §7 + `docs/principles.md` §2). Replaced with pointer. File: 570 → 324 lines.
- `WIP_OPEN.md`: trimmed recent-sessions table from 13 → 3 rows, removed "Refinement sequence queue" block (duplicated `docs/refinement-sequence.md`), compressed prod-status. File: 90 → 64 lines.
- `docs/principles.md`: closed both "Deferred / future cleanup" items (ENVIRONMENT.md + GIS_SPEC §12–18) — both shipped this chat.
- `Readme.md` §13: removed `COMMANDS.md` reference.
- `userMemories.recent_updates`: pruned stale Chat 54/Chat 64 bloat; retained only load-bearing pointers. (Executed via `memory_user_edits`.)

**Not shipped this chat (deferred):**
- Sidebar purge of `/mnt/project/` — Claude cannot write to `/mnt/project/`. Requires operator action via claude.ai project-knowledge UI. Ask issued in chat body (single ask, qualifies under Readme §2 acceptable-asks #1: irreversible structural change to project config).
- `docs/refinement-sequence.md` split into stub + per-stage files — deferred; current file is 12 KB and loaded only when refinement-sequence chat runs. Revisit if a chat not touching refinement still pulls it.

**Scope discipline note:** prior response framed GIS_SPEC consolidation as "higher blast radius, do in separate chat." Reassessed: deletion of sections entirely covered by canonical docs, with pointer replacement, is LOW. Shipped.

**Budget:** doc-only commit, 5 tool calls (view principles + inventory bash + surgery bash + log+commit bash + memory edit). Within §11 doc-only budget (2–6).

**Next-chat trigger:** `resume visual overhaul` (unchanged). Stage 3 branch still pending.

---

## Chat 69 — 2026-04-22 — Stage 3 Visual Overhaul recon + branch push

**Branch:** `refinement-visual-overhaul` cut from `main` post-Stage-2-merge. Pushed to origin. No code commits; recon only.

**Handoff:** `docs/_stage3_handoff.md` committed at `b25db48`. Content per §7.8 voice rules (second-person to next Claude, unconditional execution on arrival). Sections: recon findings (current palette table + render hook line numbers + existing defaults), 8-step execution plan (palette → contrast bump → sprite gen → template wire → build verify → commit cadence → PR → WIP close), budget expectations, boundary flags.

**Recon output embedded in handoff:**
- Five blue/gray collision points identified in current palette (counties ↔ rrc_pipelines; transmission/substations/tpit_subs/tpit_lines all in blue family).
- Render hooks located: `layerPaint()` at `build_template.html:274`; `ICON_MAP` emoji approach at `:157`; symbol layer branch at `:359`.
- Stage scope confirmed: `docs/refinement-sequence.md` §91–111.

**Palette resolution planned (not yet committed):**
- `rrc_pipelines` `#64748b` → `#7c2d12` (fossil industrial, away from grid blues)
- `tpit_subs` `#075985` → `#b45309` (planned-upgrade amber family, dark)
- `tpit_lines` `#38bdf8` → `#f59e0b` (amber, matches "Planned" badge)
- `counties` `#64748b` → `#475569` (darker slate reference outline)

**Sprite sheet approach planned:**
- 5 icons: solar, wind, battery, plant, well — SVG generated inline in build.py, rasterized via cairosvg (fallback: Pillow primitives), composited to `sprite/sprite.png` + `sprite.json` + `@2x` variants at repo root (not under `dist/` to avoid gitignore issues).
- Template wire: `rasterStyle()` gains `sprite: '/sprite/sprite'`; symbol layer switches from `text-field` to `icon-image`.

**Deploy:** none.

**Next-chat trigger:** `resume visual overhaul` or `continue stage 3`.

---



**Branch:** `refinement-bug-sweep` → merged to `main` via `git merge --no-ff`. Branch can be deleted on next chat.
**PR:** none opened (PAT lacks `pull_requests:write` — direct merge with no-ff merge commit instead, matches Chat 65 anomaly workaround).
**Deploy:** none.

**Shipped on branch pre-merge:**
- Fix 3 (measure tool persists through popup clicks, commit `fc81eb0`): 4-line diff in `build_template.html`. CSS rule `.measure-on .maplibregl-popup { display: none !important }` + toggle `measure-on` class on map container on activate/deactivate + `hoverPopup.remove()` on activate.
- Handoff doc deleted (`ecd1eec`): `docs/_stage2_handoff.md` removed.

**Merged to main:**
- All three Stage 2 fixes (`c8cbd68` + `fc81eb0`) plus orphan handoff-doc add/delete (`f65f72c` + `ecd1eec`, net-zero).
- Local build 21/21 clean post-merge, verified.

**Process changes to `Readme.md` §7:**
- §7.8 added: "Always ship before handoff. Handoffs are for context exhaustion only." Shipping chats finish their stage in-chat; no proposing a handoff as alternative to shipping.
- §7.8 also codifies **handoff-doc voice**: instructions in handoff docs are addressed to the next Claude, not the operator. No "say 'go' and I'll..." or "confirm and I'll..." phrasing — next chat parses these as wait-for-user gates and stalls. Conditionality belongs in branching steps, not wait-gates.

**Bug that drove the §7.8 handoff-voice rule:** Chat 66's final chat message ended with "When you return, say 'go' and I'll execute steps 1–9 in one pass." Chat 67 (parallel) partially executed but stalled on the trigger ambiguity; operator reported "stuck — deciphering ambiguous instruction phrasing about execution timing."

**Anomalies:**
1. Parallel-chat collision: Chats 66 and 67 ran against the same `/home/claude/` container, producing overlapping commits + divergent `main` branch state mid-session. Reconciled by fast-forwarding and inspecting reflog. Not a repeatable pattern — single-shipping-chat rule (§7.6) is the right protection.
2. PAT permission gap: gh REST calls to `/pulls` return 403 ("Resource not accessible by personal access token"). PAT scope is Contents R/W only; PR create/merge via API not available. Workaround: direct merge commit with `--no-ff`. Upgrade PAT at next convenient rotation.

**Budget:** ~22 tool calls across the shipping portion of this chat. Within ceiling.



**Branch:** `refinement-filter-ui` @ `37cfdaf` (force-pushed over prior empty pointer `a437329` from Chat 63 attempt)
**PR:** not yet opened — 1/21 build regression must be resolved first
**Deploy:** none

**Shipped on branch:**
- `layers.yaml` — 21 layers (caramba_south removed), `tpit_subs` popup reordered `[name, voltage, operator]`, `labels_hubs` min_zoom 5→4, `county_labels` min_zoom 6→5, `ercot_queue` popup expanded (+technology, +under_construction, +inr, +poi), `filterable_fields` declared on 10 combined-file layers.
- `build.py` — `compute_filter_stats()` (second pass over `SPLIT_DIR/*.ndjson`); categorical >100 distinct auto-demoted to text; `render_html` accepts + embeds `filterable_fields` in registry; main wires through.
- `build_template.html` — filter UI CSS, per-layer collapsible panel (numeric range / categorical multi-select / text substring), `buildFilterExpr` with null-safe `['has', field]` guards, `setFilter` applied to `lyr_<id>` + `__casing`/`__outline`/`__icon` companions, `filters=` hash round-trip, onload + basemap-change filter replay, `updateActiveCount` on `idle`.

**Blocker:** Build produces 20/21 OK. `county_labels` returns MISSING from `split_combined_geojson` despite 46 features tagged `layer_id=county_labels` existing in `combined_geoms.geojson` (confirmed via standalone Counter on raw file). After build, `/tmp/gis_build/split/` contains `labels_hubs.ndjson` (1 feature) but no `county_labels.ndjson`. Pre-existing bug — not introduced by this chat's edits. Likely in label-geom Point handling in `_flatten_coords` or the geometry-type check. Diagnose + fix before PR.

**Anomalies:**
1. PAT lacks `pull_requests: write` scope — branch push works (Contents R/W), but direct API PR creation 403s. Operator opens PR manually via UI at compare URL, or updates PAT scope.
2. Stale `aquifers.ndjson` (not in yaml) gets written to `SPLIT_DIR` during split — no functional impact (layers.yaml drives builds; orphan ndjson ignored), but a small cleanup opportunity.
3. `caramba_south.ndjson` still gets written during split (old feature still tagged in `combined_geoms.geojson`) — since layer removed from yaml, ndjson is orphaned and ignored. Actual feature could be scrubbed from combined_geoms in a later cleanup chat if desired.

**Budget:** ~25 tool calls. Heavy on recon (3 view calls on build_template sections) + 1 build verify + 7 str_replace edits + 1 commit/push + WIP updates. Well under shipping-chat ceiling.

# SESSION_LOG.md

Append-only log. Every GIS chat appends one header line + one outcome line + any anomaly lines. Never edit historical entries. Rotate after 500 lines (interstitial task).

Format:
```
## [N] YYYY-MM-DD HH:MM — <title>
outcome: <one-line summary>
anomalies: <if any, else "none">
```

---

## [34] 2026-04-19 — Batch 3b parcels_pecos — halted, source missing

outcome: halted at pre-flight; `geoms_parcels_pecos.geojson` not in `/mnt/project/`; no build or deploy attempted.
anomalies: project knowledge at 7.1/12.7 MB cap; parcels file 9.8 MB cannot fit alongside existing geoms.

---

## [34-continuation] 2026-04-19 — Refactor to combined architecture

outcome: designed + partially executed post-parcels-pecos-blocker refactor. Combined all `points_*.csv` into `combined_points.csv` (4.48 MB, 39,409 rows, 31 cols); combined all `geoms_*.geojson` into `combined_geoms.geojson` (2.27 MB, 7,207 features); rewrote `layers.yaml` for 15 layers on combined files + parcels_pecos standalone; rewrote `build.py` with pre-split + merge subcommand; updated `PROJECT_INSTRUCTIONS.md` with `merge.` trigger. Files written to `/mnt/user-data/outputs/refactored/`.
anomalies: GIS_SPEC.md + COMMANDS.md + final zip bundle not completed — ran out of tool-call budget. No circuit-breaker protocol existed at the time.

---

## [35] 2026-04-20 05:44 — Finish GIS refactor doc updates — halted, artifacts lost

outcome: halted. Refactored files from chat 34 lived at `/mnt/user-data/outputs/refactored/` — ephemeral — lost to container reset. `/mnt/project/` had not received the combined files (operator had not uploaded yet). Chat could not proceed to doc updates + zip without source artifacts. Operator to re-upload in next chat.
anomalies:
- Chat 34 handoff did not anchor that `/mnt/user-data/outputs/` does not persist.
- Pattern now in §15 Rule 1: deferred-fact red flags include "files at outputs/..." when the next chat happens in a new container.
- Protocol install queued for chat 36 to prevent recurrence.

---

## [36] 2026-04-20 (planned) — Session protocol install + refactor finish

Planned outcome: install the three-part protocol (autonomous execution, interstitial cadence, handoff quality gate) into `GIS_SPEC.md §12-§15`, `COMMANDS.md §9-§10`, `PROJECT_INSTRUCTIONS.md`. Seed `SESSION_LOG.md`, `WIP_OPEN.md`, `README.md`, `CREDENTIALS.md`. Finish combined-architecture refactor. Bundle zip.

Planned anomalies: none expected. High-tier chat (doc + refactor + schema); budget 15/12.

---

*(Future entries go below this line. Claude appends at close-out of every chat.)*

## [37] 2026-04-20 09:15 — Build halted at pre-flight — 2 data files missing

outcome: halted at pre-flight composite bash. `/mnt/project/` contained 12 files; handoff manifest required 13. Missing: `combined_geoms.geojson` (~2.2 MB) and `geoms_parcels_pecos.geojson` (~9.8 MB). `combined_points.csv` (4.48 MB, 39,409 rows) present; toolchain (3 files) and docs (8 files) all present. Proceeding would have produced 9 of 18 layers errored/missing and a broken prod deploy. No build attempted; memory chat-counter incremented; updated WIP "Next chat" scopes chat 38 re-run with 3 operator-choice paths (A: upload all 3; B: drop parcels_pecos; C: compress parcels further).
anomalies:
- Likely root cause: project-knowledge cap. combined_points (4.48 MB) + combined_geoms (~2.2 MB) + parcels_pecos (~9.8 MB) = ~16.5 MB vs. 12.7 MB cap noted in chat-34 anomaly. Chat 37's handoff did not cross-check against the cap — §15 Rule 3 amendment committed.
- Pre-flight caught the drift before budget spend (2 calls used of 12 ceiling). Protocol §18 signal #5 working as designed.
- No downstream damage — prod URL unchanged, no partial deploy.

---

## [39] 2026-04-21 — First build + deploy under new protocol + Hanwha sprint planning

outcome: Chat opened with chat-38 handoff trigger (`docs + combined_geoms uploaded. build. deploy to prod.`). Pre-flight clean: 13 files in `/mnt/project/`, `combined_points.csv` (4.48 MB), `combined_geoms.geojson` (2.27 MB), `layers.yaml` registered 17 layers. Build ran clean: 17/17 layers built (0 errored, 0 missing), 2.6 MB total tiles. Deployed to prod — deployId `69e678b6e8a7d7195df93c8f`, live at https://lrp-tx-gis.netlify.app. Build + deploy consumed 4 tool calls per §4 target. Remainder of chat consumed by Hanwha sprint planning (scope definition, layer sourcing Q&A, decision locking, sprint control doc authoring). Created `HANWHA_SPRINT.md` formalizing 4-chat sprint (Chats 41-44) targeting Tue Apr 21 6:00 PM EST Hanwha data room URL delivery. Locked decisions: RRC T-4 pipelines (replace HIFLD 2019), RRC wells Permian-filtered, TCEQ gas turbines ≥20 MW + NSR pending + PBR (scoped subset), TIGER highways + BTS rail, TCEQ PWS service areas + approximate water mains, Planned Upgrade styling for tpit_subs + tpit_lines, custom layer icons, OpenFreeMap (Protomaps shortcut), skip Landsat, skip password. Sprint handoff contract (§3): each sprint chat close-out produces paste-ready prompt for next chat adapted to actual findings.
anomalies:
- First-line chat label used date `2026-04-20` (should have been `2026-04-21`). Label error, no protocol impact. Noted for future.
- Chat did double duty (build + plan). No explicit handoff between the two phases — sprint urgency justified. Consumed ~18 tool calls vs. 4-call build-chat target; overage entirely in planning phase.
- Chat-counter reconciliation: memory counter at session open showed `next=39`; user-memory static snapshot (system prompt) showed `next=43`. Bumped live counter to `next=41` to match sprint plan (Chat 41 = parcels). 1-chat gap (38 skipped in log; 40 rolled into this chat's planning phase).
- Prebuilt PMTiles pattern + Planned Upgrade styling pattern queued for `GIS_SPEC.md §3` documentation post-sprint (added to §14 category table in WIP_OPEN.md).

## [41] 2026-04-21 14:39 — parcels_pecos pre-build + ERCOT popup + Waha label — build clean, deploy handed off

outcome: built-and-staged (deploy pending Chat 42). parcels_pecos.pmtiles pre-built at 4.86 MB (-Z11 -z14, first-try pass, under 5 MB cap). build.py patched with ~18-line `prebuilt:true` branch (copy-from-project, skip tippecanoe). build_template.html patched with (a) ercotQueuePopupHtml formatter (MW/fuel/commissioned/funnel_stage/county/zone/entity rows) dispatched via `L.id==='ercot_queue'`, (b) `geom:'label'` support via MapLibre symbol layer type (text-field from `name`, Open Sans Bold, white 2px halo). Waha point injected into combined_geoms.geojson at 31.215,-103.183 with `layer_id:labels_hubs`. layers.yaml updated: ercot_queue popup fields expanded; parcels_pecos + labels_hubs appended. In-session dry build: 19/19 layers OK, 0 errored, 7.58 MB total tiles, dist/ validated. Netlify MCP `deploy-site` returned error twice (transient tool error, not build content issue); `npx @netlify/mcp` CLI fallback timed out at 180s during npm install. Handoff to Chat 42 with all 5 modified files staged at `/mnt/user-data/outputs/` for re-upload; Chat 42 scope reduces to upload-and-deploy (4-call target).

anomalies:
- Tippecanoe zoom range 11–14 vs. spec draft 10–16. Rationale: 10 unused (min_zoom:11 in yaml); 15–16 would breach 5 MB cap. Fidelity sufficient for parcel-level viewing in Pecos County.
- tippecanoe `-zg` (auto-zoom) fails on single-feature layers — `Read 0.00 million features` with no crash but empty output. Caught by dry-run. Fixed with explicit `['-Z0', '-z14']`. Adding to §9 fragility table via Chat 42 close-out: *single-feature point layers require explicit tippecanoe zoom args; `-zg` silently produces 0-feature pmtiles.*
- First tippecanoe bash timed out at ~60s because the Z10-z16 retry ladder was all-in-one with no per-zoom timeout. Rebuilt one-zoom-at-a-time with 240s timeout. Retry ladder pattern worth documenting in §4.
- Netlify MCP deploy-site tool errored twice consecutively. Unknown transient cause. Chat 42 should retry MCP first; if consistent, fallback to `npx -y @netlify/mcp@latest` run against `dist/`.
- Tool-call budget: projected 20, ceiling 22; actual 25. Overage from mid-chat pivot (realizing session edits don't persist → produce outputs/) and from labels_hubs tippecanoe diagnostic loop. Acceptable — circuit-breaker condition (parcels retry exceeds -z14) did not fire, and the overage bought a pre-validated handoff.


## [42] 2026-04-21 15:15 — Chat 41 artifacts deployed to prod + build.py prebuilt branch hardened

outcome: deployed. Pre-flight caught 5 files "missing" on first ls; root cause was sequencing — Andrea completed upload (4 of 5 files: build.py, build_template.html, layers.yaml, combined_geoms.geojson) between the halt report and her reply. parcels_pecos.pmtiles (5.10 MB) deliberately excluded from project knowledge: Andrea reported 98% cap without it, would have hit 270% with it. File attached to session at `/mnt/user-data/uploads/parcels_pecos.pmtiles` instead.

Architecture decision: shrinking parcels_pecos further (5.10 MB → ~100 KB) would destroy fidelity; rejected. Instead, patched build.py prebuilt branch to a 3-tier resolver: (1) `/mnt/project/<id>.pmtiles` (2) `/mnt/user-data/uploads/<id>.pmtiles` (3) `https://lrp-tx-gis.netlify.app/tiles/<id>.pmtiles`. Tier 3 means any prebuilt pmtiles deployed once self-sustains from prod for all subsequent builds. parcels_pecos.pmtiles now lives on Netlify only.

Bootstrap for this chat: `cp /mnt/user-data/uploads/parcels_pecos.pmtiles /mnt/project/` (tier 1), then normal build. Build report: 19/19 layers OK, 0 errored, 7,582 KB total (matches Chat 41 dry run to the byte). Netlify deploy via MCP→CLI proxy fallback: first attempt 503, 10s backoff, second attempt succeeded. deployId `69e795343124ef21cb4829d3`, state=ready, deploy_time=4s, 20 files (1 HTML + 19 pmtiles). CDN propagation: all 4 verify URLs returned 503 at +0s post-deploy, clean 200s at +30s — consistent with Netlify CDN warm-up window. Final sizes on prod: index.html 21,579 B; parcels_pecos.pmtiles 5,098,834 B (md5 match with uploaded source); labels_hubs.pmtiles 2,930 B; ercot_queue.pmtiles 251,059 B.

Patched build.py validated live: syntax OK, tier-2 functional test (moved /mnt/project/parcels_pecos.pmtiles out, rebuild resolved from uploads/ in 0.2s, 4979 KB output). Source restored, md5 MATCH. Patched file staged at `/mnt/user-data/outputs/build.py` for Andrea to re-upload to project knowledge (584 lines vs. prior ~566; +18 lines net for the 3-tier resolver).

anomalies:
- Ordering issue in Chat 42 open: pre-flight ls ran before operator upload completed. Halt report was accurate at time of posting but stale by next turn. No budget impact — halt saved a misbuild; continuation worked.
- Netlify CDN edge returned 503 for ~30 seconds post-deploy-ready. Not a deploy failure, not a Netlify status-page incident. Undocumented warm-up window. Added to §9 fragility table candidate list: *first curl HEAD after deploy may 503; wait 30s and retry before escalating.*
- MCP `deploy-site` tool returned CLI proxy command rather than deploying directly (same behavior observed in Chat 41). Behavior appears to be by design now — tool returns a one-time-token proxy URL, actual deploy runs locally via `npx @netlify/mcp`. CLI proxy first call 503, retry succeeded — second-attempt retry should be the default pattern, not an exception.
- Tool-call budget: 10 calls actual vs. 4-call build-chat target. Overage drivers: (a) halt false-positive + re-ls (2 calls recovered data); (b) MCP→CLI fallback + retry (2 calls vs. 1); (c) build.py patch + live validation (3 calls not in baseline); (d) tool_search for Netlify MCP (1 call). (a), (b), (d) are recurrent; (c) was architectural work worth the budget. New baseline for build-chat with deploy retry: 6 calls.


## [43] 2026-04-21 16:35 — 9-source refresh batch — 4/9 OK, cap-aware tier-2 merge staged

outcome: 4 of 9 sources succeeded (rrc_pipelines, tiger_highways, bts_rail, water_mains_approx); 5 FETCH_FAILED. Merged successful layers into `combined_geoms.geojson` via aggressive cap-aware tier ladder (Tier 2 landed): rrc_pipelines filtered to DIAMETER≥20 + Permian bbox + DP 0.02 → 7,158 features; tiger_highways RTTYP=I+U + DP 0.012 → 3,926; bts_rail net=M (main) + DP 0.015 → 5,722; water_mains_approx hand-digitized → 3. Old HIFLD `pipelines` layer (776 features) dropped per sprint locked decision. Final `combined_geoms.geojson`: 6,885,580 bytes (6.57 MB vs prior 2.27 MB). `combined_points.csv` copied unchanged (4.28 MB) — zero point-source yield this batch. Project-knowledge cap check: 10.97 MB / 12.70 MB, +1.73 MB headroom. Raw 62 MB of refresh outputs retained at `/mnt/user-data/outputs/refresh/` for audit, not uploaded to project knowledge.

FETCH_FAILED sources (defer post-Hanwha unless fast alternative surfaces in Chat 44):
- `rrc_wells_permian` (P0 per HANWHA_SPRINT §4 — **scope adjustment forced by reality**): HTTP 404 on `/Public/Wells/MapServer/0`. RRC wells endpoint appears moved/renamed; discovery requires browsing `gis.rrc.texas.gov` services listing or falling back to RRC FTP/bulk CSV path.
- `tceq_gas_turbines` (P1): no public GIS endpoint; CRPUB scrape + Census geocoder required. Manual-CSV source pattern like `dc_sites`.
- `tceq_nsr_pending` (P2): same as above.
- `tceq_pbr` (P2): same.
- `tceq_pws` (P2): HTTP 400 on `TWSBV_Retail_Water_Service_Boundary` FeatureServer — endpoint either gated or schema-shifted. Alternatives for Chat 44 triage: `data.texas.gov` catalog, TWDB CCN/MCS layer, TCEQ map viewer AGOL.

anomalies:
- Initial `refresh_batch.py` timed out at ~120s on combined long-running AGOL fetches; 4 layers persisted to disk mid-run as partial success. Tool timeout did not cleanly interrupt — a phantom concurrent Python process ("build_standalone.py") was observed running against the same outputs directory; PID 204/207/209 killed at recovery, origin unclear (prior-chat container bleed suspected). Three PMTiles files the phantom produced were cleaned up before close-out.
- Tier 1 compression (DIAMETER≥16, I+U, M+O, DP 0.015/0.010/0.012) exceeded cap: 8.96 MB combined_geoms → 13.37 MB total, −0.67 MB headroom. Tier 2 (DIAMETER≥20, I+U, M-only, DP 0.020/0.012/0.015) fit: 6.57 MB combined_geoms → 10.97 MB total, +1.73 MB headroom.
- Pattern to add to GIS_SPEC §5 (merge cycle) post-sprint: **cap-aware tier ladder for large-source merges** — dry-measure serialized combined size before commit, tier down to fit.
- Banned `.pmtiles` artifact hazard: phantom-produced standalone PMTiles in `/mnt/user-data/outputs/` must not be uploaded to project knowledge. Checklist item for refresh chats: post-merge, inventory `/mnt/user-data/outputs/` and prune artifacts NOT in upload manifest.
- Tool-call budget: 12 actual vs. 14 ceiling. Drivers: initial script timeout + recovery (~2 calls), property-distribution inspection before tier selection (1 call), two-tier merge attempt (1 call over baseline). Within margin; no circuit-breaker trigger.
- Budget delta to flag: no "wells-class" point yield from this batch. Chat 44 yaml additions reduce from 9 planned to 4 — scope simplification; display overhaul budget effectively expands.


## [44] 2026-04-21 16:37 — Hanwha sprint FINAL — 22/22 clean, display overhaul live, URL delivered

outcome: **sprint closed.** 22/22 layers built clean (0 errored, 17,546 KB total tiles) and deployed to prod on first attempt. deployId `69e7a7859da0044dc5b0f714`, state=ready, deploy_time=quick. Hanwha-ready URL live: https://lrp-tx-gis.netlify.app. Delivery ~5.5 hrs ahead of 6 PM EST deadline.

Execution path was single-chat end-to-end per sprint prompt:
1. Bootstrapped 3 prebuilt PMTiles from `/mnt/user-data/uploads/` → `/mnt/project/` (rrc_pipelines 4.85 MB, tiger_highways 3.18 MB, bts_rail 2.22 MB).
2. Filtered combined_geoms.geojson to drop stale tiger_highways + pipelines features: 9,982 → 6,435 features, 2.14 MB (down from 6.57 MB post-Chat-43 merge).
3. layers.yaml: removed `pipelines` block, appended 4 new blocks (rrc_pipelines, tiger_highways, bts_rail, water_mains_approx) — now 22 layers.
4. build_template.html fully rewrote (431 lines): added Turf.js CDN import, ICON_MAP (5 emoji icons for solar/wind/battery/gas/wells, rendered as symbol overlays from zoom 9+ with white 2px halo), BASEMAPS overhaul (5 options: Carto Light / Esri Streets / Esri Imagery / OpenFreeMap / NAIP; two kinds — raster + external style URL; `applyBasemap` dispatcher handles both), `plannedUpgradePopupHtml` dispatched for tpit_subs + tpit_lines with amber "PLANNED UPGRADE" badge + kV/completion/project/operator fields, measure tool (click-to-add points, double-click-to-close, Turf.js distance in miles + area in acres, amber dashed line + light fill polygon, readout overlay top-left), print-to-PDF overhaul (@page landscape, print-only LRP branded header strip with dated, print-only footer attribution line, scale bar preserved with black border, all chrome hidden via @media print).
5. Build + deploy single-pass: tippecanoe cached from prior sessions (warm), build.py ran in ~15s across 22 layers, Netlify MCP returned CLI proxy URL, `npx @netlify/mcp` completed in one shot (no 503 retry needed on deploy this time).
6. CDN warm-up: first verify at +30s post-deploy returned 503 across the board (matches Chat 42 pattern); second verify at +75s returned 200 OK on all 4 target PMTiles + index.html. All 6 display-feature sentinels (ICON_MAP, USGSNAIPPlus, measure-readout, openfreemap, planned-badge, turf.min.js) present in deployed HTML. Layer count 22/22 in the `LAYERS` const.

anomalies:
- `create_file` refused to overwrite `/mnt/project/build_template.html` despite the directory being writable — had to `rm` first. Minor 1-call overhead. Pattern: if a full-file rewrite of a project file is needed, `rm` via bash first, then `create_file`. Adding to §11 banned-patterns inverse: "full template rewrite: prefer `create_file` after `rm`, not str_replace chains, when >10 edits needed."
- CDN warm-up ~60-75s post-deploy-ready this chat vs. ~30s in Chat 42. Suggests 45-60s is safer default pre-retry wait than 30s. §9 fragility candidate update.
- `data.json` encoded the deployed `LAYERS` const's `features` field as 0 for all prebuilt layers (rrc_pipelines, tiger_highways, bts_rail, parcels_pecos). build.py reports 0 "kept" for prebuilts because it doesn't parse PMTiles metadata. Count shows 0 in sidebar for those layers — cosmetic issue, not functional. Feature counts via tippecanoe probe would require an extra subprocess step per prebuilt. Deferring; not a Hanwha blocker. Adding to backlog.
- `tiger_highways` default_on=True per sprint spec; places the map in a state where highways render immediately on open. Confirmed correct per COMMANDS/HANWHA_SPRINT.
- Tool-call budget: ~10 actual vs. 6-call ceiling for new-layer chats. Overage drivers: (a) full build_template.html rewrite (1 rm + 1 create_file vs. 1 str_replace baseline), (b) double CDN verify cycle (2 calls vs. 1). Acceptable given scope (display overhaul + 4 new layers in one chat vs. normal single-layer-addition baseline). Not a circuit-breaker event.

Sprint close-out per HANWHA_SPRINT §3 contract:
- One-line status: **Hanwha data room URL live at https://lrp-tx-gis.netlify.app with 22 layers and full display overhaul.**
- No Chat 45 prompt generated; sprint closed with no pre-defined successor.
- HANWHA_SPRINT.md not further amended — sprint can be archived.
- WIP_OPEN.md updated with post-sprint state.
- Tool-call budget learning folded into this entry.


## [45] 2026-04-21 — rrc_wells_permian endpoint discovery — path (b) bulk-CSV via mft.rrc.texas.gov

outcome: discovery chat, no build. Per Chat-44-close WIP recommendation, evaluated the three paths for the missing rrc_wells_permian source from Chat 43 FETCH_FAILED. Selected **(b) bulk-CSV fallback via `mft.rrc.texas.gov`** (Texas RRC Managed File Transfer portal). Path (a) endpoint re-probe on `gis.rrc.texas.gov` rejected as stale; path (c) TCEQ-pattern manual-CSV rejected in favor of RRC-supplied bulk data. Outcome moves rrc_wells_permian from blocked/discovery into the implementation queue under the manual-CSV pattern: download RRC wellbore bulk export, filter to Permian bbox (Pecos / Reeves / Ward + surrounding counties), emit as `points_rrc_wells_permian.csv` or `geoms_rrc_wells_permian.geojson` per record structure. Next chat on this source = fetch + stage; WIP_OPEN backlog updated.
anomalies: entry rebuilt retrospectively from memory + Chat 44 WIP recommendation in Chat 47 (GitHub sync setup chat). Exact timestamp, tool-call budget, specific MFT export name, and fetch-side verification not captured at the time — treated as bounded discovery outcome rather than implementation spec.


## [47] 2026-04-21 15:00 — GitHub-backed project sync setup — protocol installed, repo init pending

outcome: installed GitHub sync protocol as authoritative state layer. Repo layout: flat, mirroring `/mnt/project/` (no subfolders — preserves every existing `/mnt/project/<file>` reference in docs and `build.py`). Tracked: all .md spec/state/archive files, build toolchain, layers.yaml, combined_points.csv (4.48 MB), combined_geoms.geojson (2.14 MB post-Chat-44-filter). Gitignored: `CREDENTIALS.md` (secrets stay in Project Knowledge only), `dist/`, `__pycache__/`, `.venv/`, `tmp*/`. No Git LFS at current file sizes; revisit if any single file crosses ~50 MB. Session-open protocol: `git clone --depth=1` into `/home/claude/repo/` as first bash call, using PAT from `/mnt/project/CREDENTIALS.md`. Session-close protocol: `git add -A && git commit && git push` as last bash call before final response, no-op if no changes. Push-rejected fallback = pull-rebase-push once, then halt and report. Authority: GitHub `main` = canonical; `/mnt/project/` = read-only fallback only if GitHub unreachable at session open. Files staged this chat (for re-upload to Project Knowledge): rebuilt `WIP_OPEN.md` (Chat 45 outcome + sprint-closed state + GitHub sync section), updated `SESSION_LOG.md` (Chat 45 + Chat 47 entries appended), updated `PROJECT_INSTRUCTIONS.md` (Hanwha sprint block removed per its own self-destruct, GitHub sync section added). Actual repo initialization (initial push of `/mnt/project/` contents to empty GitHub repo) deferred pending PAT + repo URL from Andrea.
anomalies:
- Chat counter gap: memory said `next=47`, previous logged chat was 44, Chat 45 was the rrc discovery, Chat 46 has no log entry. No reconstruction attempted for 46 — either non-GIS work or a counter skip. Flagged in WIP_OPEN recent-sessions table.
- No build, no deploy, no data refresh this chat. Prod state unchanged from Chat 44 close.
- Tool-call budget used for documentation + file staging only. Net new capability: state-layer persistence decoupled from Project Knowledge 12.7 MB cap.


## [48] 2026-04-21 21:43 — GitHub sync initialized — repo live at 10thMuses/lrp-tx-gis

outcome: one-time `github init.` trigger executed. Cloned empty `github.com/10thMuses/lrp-tx-gis.git` into `/home/claude/repo/`, copied all `/mnt/project/` contents except `CREDENTIALS.md` (14 tracked files: 8 .md + 2 build toolchain + 1 layers.yaml + 2 combined_* data files + .gitignore), added `.gitignore` (CREDENTIALS.md, dist/, *.pmtiles, __pycache__, .venv, tmp*, .DS_Store, /mnt/user-data/), committed, pushed to `origin/main`. Commit: `7f8ca54 Chat 48: GitHub sync init — mirror /mnt/project/ (post-Hanwha, 22 layers)`. Verified: (1) CREDENTIALS.md excluded from working tree and index; (2) actual PAT value (`github_pat_11B6VWBKY0dk…` prefix) NOT in git history (only documentation strings matching the `GITHUB_PAT=` pattern appear in PROJECT_INSTRUCTIONS.md — intended); (3) .gitignore rule tested by staging a copy of CREDENTIALS.md — correctly ignored. Authority layer is now live: from Chat 49 forward, every GIS chat opens with `git clone` per PROJECT_INSTRUCTIONS.md §GitHub sync and closes with `git add/commit/push`. `/mnt/project/` remains only as read-only fallback if GitHub unreachable at session open.
anomalies: none. Tool-call budget: 5 bash + 2 view = 7 calls, within 6–12 envelope for non-build maintenance chat.


## [51] 2026-04-21 — Hanwha polish patch authored — not landed

outcome: patch authored in-session to add FIELD_LABELS dict, hover popup singleton, line-casing underlay on line layers, county_labels label-layer (via 46 centroid points appended to combined_geoms.geojson), and to drop aquifers layer. Edits staged to /mnt/project/ and /home/claude/repo/ but not committed to GitHub or deployed. Container reset before close — patch.py lost. Prod state unchanged from Chat 48.
anomalies: chat closed without git push; treated as uncommitted WIP requiring reconstruction at next touch. Learning pinned: in-session edits to /mnt/project do not persist across container resets; GitHub main is the only authoritative state layer.


## [52] 2026-04-21 21:50 EDT — Hanwha polish LANDED — 22/22 clean, patches reconstructed

outcome: Chat 51 polish reconstructed and deployed. deployId `69e82c344f3101e36a99b60e`, state=ready, layers=22/22 (0 errored, 17,484 KB total tiles). Polish deltas all live and verified via sentinel grep on deployed index.html: `FIELD_LABELS` (raw-key → display-label dict, 50+ entries covering all generic popup keys across current layer set), `__casing` (white 3.5px underlay on line layers, rendered before the main line in addLayer, visibility-synced in setLayerVisibility, line-cap/join round), `hoverPopup` (singleton Popup w/ closeButton=false, wired via mousemove/mouseleave on every lyr_*, suppressed while measureActive), `county_labels` (46 centroid points computed via shapely.representative_point on the 46 county polygons in combined_geoms, tagged layer_id=county_labels, rendered as label geom with text-halo). aquifers removed from layers.yaml (5 features left stale in combined_geoms but inert — no tile built, no registry entry, no client effect). Tile endpoint GET https://lrp-tx-gis.netlify.app/tiles/county_labels.pmtiles returned HTTP 200 with CORS.

Execution path:
1. Session-open: git clone clean (13 files), curl prod 200, diff against /mnt/project showed no local state — Chat 51 edits fully lost as predicted.
2. Wrote /home/claude/patch.py — idempotent, dual-target (/mnt/project + /home/claude/repo), handled all four deltas in one script. Post-patch diff between trees clean.
3. Installed tippecanoe via apt (v2.49.0) and shapely via pip (v2.1.2); both first-use this chat.
4. build.py ran clean: 22/22 OK, 0 errored. county_labels built 25KB @ 46 features.
5. Netlify MCP deploy-site single-shot, proxy URL consumed in one npx call, deploy-ready without CDN retry.
6. Verify: +45s post-deploy curl returned 200 on both root and tile endpoint; sentinel grep found FIELD_LABELS, __casing, county_labels, hoverPopup (and aquifers absent as expected).

anomalies:
- Chat 51 handoff text claimed `/home/claude/patch.py` was idempotent and would replay the edits on re-clone. In fact patch.py was lost to container reset (it was never part of /mnt/project or the repo), and the edits to /mnt/project and /home/claude/repo were also lost because /mnt/project changes don't persist and repo was re-cloned. Reconstruction cost ~1 thinking turn + 1 create_file call; the reconstruction itself was bounded and clean. Learning now pinned in WIP_OPEN.md protocol section: in-session /mnt/project edits are ephemeral; only GitHub persists.
- Tool-call budget: ~10 bash + 1 create_file (patch.py) + 1 create_file (WIP_OPEN) + 1 MCP deploy + 1 tool_search = ~14 calls vs. ~6-call baseline for new-layer chats. Overage drivers: (a) session-open diff investigation to confirm scope (~3 calls); (b) dual-target patch authoring needed one full script rather than the usual str_replace chain; (c) dependency install for shapely + tippecanoe + combined_geoms inspection before patch. Within acceptable margin given scope; not a circuit-breaker event. If the patch script had survived per the original Chat 51 handoff, this would have been a ~5-call build+deploy+verify chat.
- Flagged in task step 8: `combined_points.csv` has blanks in operator / commissioned / technology / fuel / capacity_mw across eia860_plants, eia860_battery, solar, wind, ercot_queue. `ercot_queue` has entity populated (Developer slot OK). Popups degrade cleanly on blanks (empty rows dropped by filter), but a future EIA-860 + USWTDB refresh must carry those fields or Generation layers stay name-only under hover/click. Logged in WIP_OPEN backlog.
- Scope note moved to WIP_OPEN: TCEQ sources (gas_turbines, nsr_pending, pbr) scoped to fossil/emissions only — gas-fired peakers and emission-permitted combustion sources, not renewables. dc_sites removed from open backlog per Chat 52 task directive.


## [53] 2026-04-21 22:15 EDT — rrc_wells_permian HALTED, source EXCLUDED from scope

outcome: no build, no deploy, no data change. Prod state unchanged from Chat 52 (deployId `69e82c344f3101e36a99b60e`, 22 layers, 17,484 KB tiles). Session-open clean (repo clone, prod curl 200, layers.yaml count=22, county_labels present, aquifers absent — matches §Prod-status table). Task was rrc_wells_permian fetch via Chat-45-resolved bulk-CSV path at `mft.rrc.texas.gov`; halted at discovery phase per explicit task instruction ("HALT if endpoint requires registration/login — do not guess"). Andrea's response: exclude RRC oil/gas wells from current scope. Backlog entry moved to EXCLUDED state in WIP_OPEN.md with full context preserved for any future re-scope.

findings preserved for any Chat-N future re-scope:
- RRC public data-sets page (`rrc.texas.gov/resource-center/research/data-sets-available-for-download/`) exposes UUID shared-link endpoints at `mft.rrc.texas.gov/link/<uuid>` that resolve to file listings without login. Target for well-bore points: `d551fb20-442e-4b67-84fa-ac3f23ecabb4` ("Well Layers by County") lists 250+ `well<FIPS>.zip` shapefile archives, one per Texas county, updated twice weekly.
- Target Permian FIPS (3-digit state-level): Pecos=371, Reeves=389, Ward=475, Loving=301, Winkler=495, Ector=135, Midland=329, Upton=461, Crane=103, Crockett=105, Terrell=443, Culberson=109 (12 files).
- **Blocker**: downloads are driven by GoAnywhere PrimeFaces AJAX (JSESSIONID + ViewState + selectRow POSTs). Direct `/link/<uuid>/<filename>` returns 404. No `.zip` or `octet-stream` content-type surfaced on any UUID probed. Proxy egress to `mft.rrc.texas.gov` also flaky ("DNS cache overflow" / "upstream connect error" on 2 of ~8 probes this chat).
- **Alternatives probed and eliminated**: (a) `gis.rrc.texas.gov/arcgis/rest/services` — 404 on REST catalog, no public ArcGIS endpoint; (b) "Full Wellbore" and "Wellbore Query Data" bulk ASCII files — no lat/lon fields, cannot serve as point layers without a geocoding pass against separate API-number-to-surface-location table; (c) AGOL world-wide search for RRC-owned Feature Services — zero results.
- **Clean reopening paths** (for re-scope only): (A) Andrea manually browser-downloads 12 county shapezips to `/mnt/user-data/uploads/` and Claude processes via pyshp → combined_points merge; (B) Claude implements PrimeFaces session-downloader in Python (estimated +5-8 calls, moderate fragility, aligns with §9 AGOL/Overpass fragility pattern); (C) Substitute "Drilling Permit End of Month with Lat/Lon" (`f5dfea9c-bb39-4a5e-a44e-fb522e088cba`) as a drilling-activity layer — narrower coverage (permits, not wellbores) but single-file statewide with embedded lat/lon.

anomalies:
- Chat budget overran refresh envelope: 8 bash + 1 web_fetch + 3 view + 1 str_replace-fail = ~13 calls, vs. 4-10 refresh ceiling. Overage drivers: (a) catalog mapping was non-trivial (RRC page is a giant table with PrimeFaces-generated anchors, not plain hrefs, requiring HTML parse to resolve UUID→row-label mapping); (b) multiple alternative-path probes before halting (gis.rrc REST, AGOL search, single-file share direct-URL tests); (c) attempted str_replace on file I'd modified via view-only shortcut (non-fatal, corrected in follow-up). None of these overruns produced prod state change — the chat shipped documentation/backlog updates only.
- Protocol note: task instruction specified "HALT and ask" on endpoint-login, which resolved cleanly. The actual blocker was "endpoint is AJAX-only, not login" — same functional halt class, but a broader category. §9 fragility table candidate addition: "GoAnywhere MFT public share" → "Downloads require PrimeFaces session simulation; direct-URL append returns 404" → "Skip source; log; ask operator for browser-download or alternative".


## [58] 2026-04-22 14:30 — Prod recovery + TPIT label rename deploy

outcome: prod recovered from 24h+ 503 outage ("DNS cache overflow" on Netlify edge, affecting alias AND raw deploy permalink — platform-side, not deploy-content). Operator manually republished prior `ready` deploy (Yesterday 12:36 PM) from Netlify UI after locking auto-publish to surface the Publish button. Edge re-cache cleared; prod returned 200 across all paths. With prod up, executed deferred TPIT label rename from Chat 57: `tpit_subs.label` → "Substation Upgrades", `tpit_lines.label` → "Transmission Upgrades" (IDs unchanged). Build ran clean: 21/22 built, 1 missing (county_labels — expected, no rows in combined_geoms.geojson), 0 errored. Tier-3 prebuilt fetch from prod URL succeeded for parcels_pecos, rrc_pipelines, tiger_highways, bts_rail. Fresh deploy uploaded to Netlify (deployId `69e8e002c4782d80d2949109`), state=ready, published_at=null — awaiting manual publish by operator because auto-publish remained locked at deploy time. Same Netlify CLI "Service Unavailable" polling failure pattern as Chat 55 — deploy succeeded server-side despite CLI error.

anomalies:
- Chat 55's operator/owner field refresh (eia860_plants, eia860_battery, solar, wind) confirmed **lost**: not in GitHub `main`, not in /mnt/project/, zero operator populations across 1,367 + 133 + 180 + 19,464 rows (only 19/180 solar baseline pre-existed). Memory line stating Chat 55 "committed to repo ... persists" was incorrect — Chat 55's errored deploy + CLI timeout also blocked its git push. Chat 57's TPIT edits similarly never committed; redone this chat. Operator decision (Chat 58 mid-chat): field refresh not worth redoing — operator was illustrative, actual filter leverage is generic filter UI (Chat 59 queued). Field refresh dropped from scope.
- Rollback to Yesterday 12:36 PM caused zero regression: only deploy newer than 12:36 PM was the 10:02 PM deploy which was returning 503 to every user from deploy to present. No working post-12:36-PM state existed to roll back "past."
- Netlify MCP toolset has no rollback/publish-deploy operation. Publish-prior-deploy requires operator UI step (Deploys → Lock to stop auto publishing → click prior deploy → Publish deploy). Pattern documented for future edge-outage recovery.
- CLI deploy timeout ("Error fetching deploy status: Service Unavailable") recurred — same pattern as Chat 55. Deploy completes server-side; MCP get-deploy-for-site is the reliable status source. COMMANDS.md should reflect: on CLI timeout, poll via MCP reader, not retry CLI.
- Build tool-call budget: ~12 calls this chat vs. 6-call new-layer ceiling. Overage driven by: (a) preflight + platform diagnosis + status-page search (~4 extra calls), (b) MCP publish-deploy absence workaround via operator UI (~2 extra calls requiring back-and-forth with operator), (c) Chat 55 data-state investigation (~2 extra calls). Not a circuit-breaker event given the recovery-chat nature.
- Auto-publish lock remains enabled post-deploy. Operator to unlock after publishing new deploy, or future deploys will require manual publish.

pending operator actions:
1. Publish deploy `69e8e002c4782d80d2949109` via https://app.netlify.com/projects/lrp-tx-gis/deploys/69e8e002c4782d80d2949109 → "Publish deploy" button.
2. Unlock auto-publishing on Deploys list page.


## [48] 2026-04-21 — GitHub sync GO-LIVE — repo initialized, session bracket active

outcome: `github init.` executed. Repo `github.com/10thMuses/lrp-tx-gis` initialized with flat layout mirroring `/mnt/project/`, 14 tracked files. `CREDENTIALS.md` gitignored, PAT not in history. Working dir `/home/claude/repo/` established. Session-open (clone) + session-close (commit + push) bracket active for all subsequent shipping chats. `/mnt/project/` demoted to read-only fallback per `PROJECT_INSTRUCTIONS.md` authority hierarchy. Historical anchor — preserved as WIP_LOG entry retroactively during Chat 62 protocol port.
anomalies: original Chat 48 close-out did not produce its own SESSION_LOG entry at the time. Entry reconstructed from memory for continuity.

---

## [61] 2026-04-22 — Cross-project protocol consultation

outcome: 10M-project Claude was consulted on whether to port its operating protocol to the GIS project. Initial GIS-side analysis (Chat 61 close) found cognitive-briefing overhead already low due to trigger phrases and master-prompt convention, but identified five touchpoints the existing setup retained: (1) `CURRENT TASK:` / `UPCOMING TASKS:` framing as labor every chat open, (2) trigger-vs-conversational invocation as operator decision, (3) semantic overlap across `PROJECT_INSTRUCTIONS.md` / `SESSION_LOG.md` / `GIS_SPEC.md` / `COMMANDS.md` / `ENVIRONMENT.md`, (4) userMemories churn and recency bias, (5) mid-chat handoffs requiring operator re-state on resume. 10M Claude produced a self-contained 8-phase advisory recommending full port. Consultation closed; port queued for Chat 62. Historical anchor.
anomalies: none.

---

## [62] 2026-04-22 — 10M operating-protocol port executed

outcome: doc-only port executed end-to-end per 10M advisory. Created `Readme.md` (13-section operating protocol), `docs/settled.md` (permanent decisions), `docs/principles.md` (engineering patterns). Renamed `SESSION_LOG.md` → `WIP_LOG.md` (this file). Deprecated `README.md` and `PROJECT_INSTRUCTIONS.md` — content absorbed. Restructured `WIP_OPEN.md` top to current-workstream-first convention. Single `main` commit. Preserved: Chat 48 clone-push bracket, `/mnt/project/CREDENTIALS.md` gitignore pattern, Option B prebuilt PMTiles, flat data layout, single-`layers.yaml` config, tool-call budgets, trigger phrases (now optional input shape). Operator-facing change: `CURRENT TASK:` / `UPCOMING TASKS:` framing retired; natural-language prompts route correctly. Zero operator asks mid-port after mapping-table approval.
anomalies: Chats 48–61 not all logged in real time. Chat 48 and Chat 61 reconstructed retroactively above as historical anchors. Gap between Chat 47 (last real-time entry) and Chat 62 not fully reconstructed; memory retains summary across the gap (22 layers live, TCEQ reactivated Chat 56, rrc_wells_permian excluded Chat 53).

## [63] 2026-04-22 — Filter UI stage — recon + design, no code committed

outcome: Stage 1 of refinement sequence opened per `docs/refinement-sequence.md`. Cloned repo, profiled all 11 combined-file layers in `combined_points.csv` and 13 geom layers in `combined_geoms.geojson` for field coverage, distinct counts, numeric ranges. Branch `refinement-filter-ui` created locally (not pushed; zero commits). Locked design: `filterable_fields` yaml schema (numeric/categorical/text per field), `build.py` stats computation in split pass (min/max for numeric; sorted distinct capped at 100 for categorical with text fallback), `build_template.html` collapsible per-layer filter panel wired to `map.setFilter` on `lyr_<id>` + `__casing`/`__outline`/`__icon` companions, null-safe expressions via `['has', field]`, hash round-trip via new `filters=` key, prebuilt layers lazy-populate via `querySourceFeatures`. Piggyback tweaks scoped: drop caramba_south, reorder tpit_subs popup → `[name, voltage, operator]`, lower `min_zoom` on `labels_hubs` (5→4) and `county_labels` (6→5), expand popup lists per layer with internal-field whitelist (critical: caramba_north has 50+ internal metadata fields — do NOT auto-include). Handoff written into chat body per `Readme.md` §10; next chat resumes at code-write via `conversation_search`.
anomalies: Budget spent on recon before any code write — borderline. Profile-first approach prevented design errors on numeric-vs-categorical classification (`ercot_queue.commissioned` is Yes/No boolean, not date — would have mis-rendered as date range). "Road labels" in stage spec task 3 matches no existing layer; `tiger_highways` is a line layer with no text rendering. Interpreted as lowering min_zoom on existing label-geom layers; flagged for operator confirmation in PR body.

## [64] 2026-04-22 — Filter UI Stage 1 code shipped to branch

outcome: Branch `refinement-filter-ui` pushed to remote (commit `a437329`) with full filter-UI code. `layers.yaml`: `caramba_south` deleted (22→21 layers), `filterable_fields` schema added to 12 layers, popup reorder on `tpit_subs`, `min_zoom` lowered on `labels_hubs` (5→4) and `county_labels` (6→5), popup whitelists applied. `build.py`: `compute_filter_stats()` in split pass tracks per-field stats (numeric min/max; categorical sorted-distinct capped at 100 with text fallback); stats embedded in registry. `build_template.html`: `FILTER_STATE` object, `buildFilterExpression()` null-safe via `['has', field]`, `renderFilterPanel()` collapsible per-layer UI, `ensureLazyStats()` lazy-populates prebuilt-layer values via `querySourceFeatures` on first open. Hash round-trip via new `filters=` key. Local build: 20/20 non-combined layers OK; `county_labels` errored.
anomalies: `county_labels` build failed — surfaced as "missing from combined_geoms" at the time and flagged for Bug Sweep. Actual root cause identified in Chat 65 below. PR open + WIP_OPEN update deferred to Chat 65.

---

## [65] 2026-04-22 — Filter UI Stage 1 closed — ROOT fix, PR merged

outcome: Diagnosed Chat 64's `county_labels` failure. `build.py` split pass was reading `PROJECT / COMBINED_CSV` and `PROJECT / COMBINED_GJ` (lines 631–632) — `PROJECT` resolves to `/mnt/project/` (sidebar), which is stale per `Readme.md` §1 (repo is canonical). Chat 52's `county_labels` addition lives in the repo's `combined_geoms.geojson`, not the sidebar copy. Two-line fix: `PROJECT` → `ROOT`. Committed (`f829bb6`) and pushed to `refinement-filter-ui`. Local verification: `built=21 missing=0 errored=0`, `county_labels 46/46 OK`. PR `main...refinement-filter-ui` opened via GitHub UI (token lacks `pull_requests:write`) and merged. `WIP_OPEN.md` + `WIP_LOG.md` updated on branch (ship with PR merge). No prod deploy — filter UI deploys in its own session after Stage 2 Bug Sweep per `docs/refinement-sequence.md`.
anomalies: Tippecanoe not preinstalled in container (expected per environment spec); installed via apt + source build in ~60s. First two build attempts had transient HTTP 503s on prebuilt PMTile fetches (`rrc_pipelines`, `tiger_highways`, `bts_rail`, `parcels_pecos`); third attempt clean. Per-chat retry pattern noted; not protocol-worthy.

## [66] 2026-04-22 — Bug sweep recon + Readme §7.7 added

outcome: Stage 2 opened per `docs/refinement-sequence.md`. Branch `refinement-bug-sweep` cut from `main`. Stale `refinement-filter-ui` remote branch deleted. Recon committed to branch as `docs/_stage2_handoff.md` covering all 3 bugs (Waha, parcels_pecos, measure/popup) with file paths, diagnostic hypotheses, and execution order. Also added `Readme.md` §7.7 directly to `main` (`9fd44b0`): mandatory mid-chat handoff file on context exhaustion.
anomalies: Branch cut from main BEFORE §7.7 commit landed; Chat 67 rebased to pick it up. Hit tool budget before starting any bug-fix code — consistent with new §7.7 doctrine (commit handoff, don't start work you can't finish).

## [67] 2026-04-22 — Stage 2 fixes 1+2 shipped; §7.7 rewritten

outcome: Branch `refinement-bug-sweep` rebased onto `main` to pick up §7.7. Local build run (tippecanoe rebuilt). Diagnosed all 3 bugs with evidence: (1) Waha — `rasterStyle()` omits `glyphs` URL, symbol layers silently unrenderable on 4 raster basemaps; (2) parcels_pecos — `.pmtiles` valid on prod CDN (z11-14, vector_layer `parcels_pecos`, 5.1 MB), but container egress proxy intermittently returns HTTP 503 body `"DNS cache overflow"` on full-file GETs, while Range requests work reliably; (3) measure/popup — `measureActive` guards prevent NEW popups but existing popups remain interactive. Fix 1 (`build_template.html`): added OpenFreeMap glyphs URL + `text-font: ['Noto Sans Bold']`. Fix 2 (`build.py`): replaced single `urllib.urlopen` with HEAD probe + 8 MB chunked Range GETs + 5-try exponential backoff. Committed both fixes + updated handoff (`c8cbd68`). Also rewrote Readme §7.7 on `main` (`dbb86d8`): "progress over summary — continuous commit, minimum chat message" — reserve 20% budget for close-out, handoff doc is authoritative state, final message is minimum-viable pointer.
anomalies: Mid-chat §7.7 violation: Fix 1 + Fix 2 edits sat in `/home/claude/repo/` for several turns before a status-summary message was drafted; operator caught it in real-time and directed commit-now. Corrected. §7.7 rewrite triggered directly by this incident. Fix 3 (measure/popup) + build verification + PR deferred to Chat 68.

## [72] 2026-04-23 — TCEQ REFRESH recon + gas-turbine bulk pull

outcome: Scope-confirmed 4 deferred questions with operator. Bulk-source recon (2 tool-call cap): `turbine-lst.xlsx` (TCEQ Issued Air Permits for Gas Turbines ≥20 MW, v2026.4.3) is clean programmatic bulk source for `tceq_gas_turbines`. No bulk source exists for `tceq_nsr_pending` or `tceq_pbr` (CRPUB HTML-only, RRC-MFT analog). Operator authorized: gas-turbines only, NSR pending deferred indefinitely, PBR + PWS scoped out permanently, TCEQ MERGE folded into next chat. Pipeline built: xlsx → 23-county filter → Received ≥ 2020 → Nominatim geocode → `combined_points.csv` schema. Record flow: 229 → 12 → 6 → 6/6 geocoded. Census `locations/onelineaddress` returned 0/6 matches on city-level queries; fell back to OSM Nominatim (city + county + state, 1.1s throttle). Deliverables on branch `refinement-tceq-refresh` (HEAD `606b277`, pushed): `scripts/refresh_tceq_gas_turbines.py`, `outputs/refresh/tceq_gas_turbines_2026-04-23.csv`, `outputs/refresh/turbine-lst_2026-04-23.xlsx` (source archive), `outputs/refresh/CHANGELOG.md`. No merge to main. No prod deploy. Chat 73 to close TCEQ REFRESH + TCEQ MERGE in single shipping session.
anomalies: Original stage spec called for Census geocoder + CRPUB scrape. Both paths deviated: Census is a street-address geocoder, not a place geocoder, and returned zero matches on West-TX municipality queries (Fort Stockton, Midkiff, Monahans, Pecos, Barstow all missed). CRPUB scrape not authorized — bulk source found instead. Stage spec language ("CRPUB scrape + Census geocoder per manual-CSV pattern; fossil/emissions scope only") now partially superseded; `outputs/refresh/CHANGELOG.md` documents the deviations.

## [73] 2026-04-23 — TCEQ refresh branch merged to main

outcome: Branch `refinement-tceq-refresh` (HEAD `606b277`) merged to main as `ea7e39d`. Brought in `scripts/refresh_tceq_gas_turbines.py`, `outputs/refresh/tceq_gas_turbines_2026-04-23.csv`, `outputs/refresh/turbine-lst_2026-04-23.xlsx` source archive, `outputs/refresh/CHANGELOG.md`. No layer integration yet — data lives in refresh outputs only. No build, no deploy.
anomalies: none.

## [74] 2026-04-23 — TCEQ data/config + EIA-860 research committed; build deferred

outcome: Two commits on main. `4292bf2`: appended 6 `tceq_gas_turbines` rows to `combined_points.csv`, added layer + new "Permits" sidebar group to `layers.yaml` + `build_template.html`. `3aada1c`: EIA-860 Generator-sheet research captured in `docs/settled.md` (capacity lives in Generator sheet not Plant sheet; 891/1367 plant coverage via OP-filter + Plant Code groupby; Referer header required for current-release zip fetch). Build deferred on tool budget — data + config landed, execution pushed to next chat.
anomalies: Build deferred across chat boundary is a new pattern; captured in subsequent WIP_OPEN handoff and executed cleanly in Chat 75. User upload of `combined_points.csv` audited and found equivalent to repo state (float serialization differences only, 31/31 rows matched on entity keys); no merge.

## [75] 2026-04-23 — Abatement discovery spec + multi-chat refinement rules; TCEQ built locally; no deploy

outcome: Two tracks in one chat. Track 1 (abatement): `docs/refinement-abatement-spec.md` committed (`92d25c72`, 198 lines) — regulatory correction (Ch. 313 expired 12/31/2022; JETI excludes renewables; Ch. 312 + Ch. 381 are active mechanisms), commissioners-court agenda scrape identified as canonical leading signal over Comptroller registries (30-day Tax Code §312.207(d) notice requirement), keyword taxonomy, `extract_applicant()` regex with `re.I` + `\b` fixes, field catalog, schema Options A/B, county adapter status (2 validated / 3 stubbed / 18 TODO), 4 live hits, 8 BUILD-gate open questions. Multi-chat refinement rules added to `docs/refinement-sequence.md` (branch+PR workflow, stage scoping, dependency map). Track 2 (TCEQ): full build ran in fresh container, built=22, errored=0, `tceq_gas_turbines feature_count=6`. Deploy halted per operator direction to preserve budget for abatement track. Handoff: Chat 75b to rebuild in fresh container, deploy, land close-out docs.
anomalies: Two-track chat unusual; succeeded because tracks were fully orthogonal (abatement doc-only, TCEQ build local-only). Would not repeat if either track needed prod state. Operator direction to stop pre-deploy was correct — abatement track consumed most of the budget.

## [75b] 2026-04-23 — TCEQ SHIP complete; Readme §2 ban-ship-it rule; close-out docs in same chat

outcome: Three things shipped in one chat. (1) Readme §2 extended on main (`939ff16`): banned phrases now include `"Say ship it and I'll..."` / `"Confirm to ship."` / any phrasing that makes action conditional on re-affirmation once the next move is named and unblocked; new bullet added to specific-bans list; rule text "When the next shipping target is named and dependencies clear, ship." (2) TCEQ build ran clean in fresh container (built=22, errored=0, `tceq_gas_turbines=6`); deploy via Netlify MCP succeeded on second proxy URL (first consumed on transient error); deployId `69ea32c7d3733641c9a1bb7c`, state=ready, published_at 14:55:09Z. Prod verified 200 with real User-Agent; `tceq_gas_turbines.pmtiles` endpoint 200; all 22 tiles present. (3) Close-out docs appended in same chat rather than split to 75c per operator direction — `docs/settled.md` gained TCEQ-sources-closed paragraph + Netlify-UA-503 operational note under `## Data sources`; this `WIP_LOG.md` appended four entries; `WIP_OPEN.md` rewritten to Chat 76 UI-polish next target.
anomalies: Sidebar `/mnt/project/WIP_OPEN.md` was ~13 chats stale (last-updated Chat 62 content) — execution driven off canonical repo `WIP_OPEN.md` per Readme §1. GitHub PAT in `CREDENTIALS.md` not auto-used on first raw-CDN fetches (fetches 404'd on private repo); fixed mid-chat. First Netlify deploy proxy URL consumed on a 503 `zipAndBuild` error with no deploy created; fresh proxy URL on retry succeeded. Default `curl` User-Agent returns 503 on prod edge; real UA returns 200 — new operational requirement captured in `docs/settled.md`.
