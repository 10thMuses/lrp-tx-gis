# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat

**Chat 128 — ERCOT QUEUE GEOCODING STAGE 3 OR SUBSTITUTION.** Stage 3 gated on `data/ercot_queue_overrides.csv` for fourteen consecutive slots; if CSV present at session-open, ship Stage 3. If absent, fall through to one of the substitution candidates below.

### Task

1. **Session-open check.** If `data/ercot_queue_overrides.csv` exists at session-open → execute Stage 3 per `docs/sprint-plan.md` ERCOT entry / WIP sprint queue spec (Stage 2.d pass in `scripts/geocode_ercot_queue.py`, manual_override coords_source, atomic write per §6.15). If absent → execute substitution.
2. **Substitution candidates (operator picks one if no CSV):**
   - (a) **Counties color holistic contrast review.** Revisit `#fbbf24` (amber) chosen under time pressure in Chat 120. Verify against `satellite`, `carto_light`, and dark basemaps; check for clash with hyperscale campus strokes (`la_escalera`, `gw_ranch`, `longfellow_ranch` lines) and tiger_highways amber. Pick a color that survives all three basemaps + doesn't compete with overlays. Pure `layers.yaml` edit + visual review. 1 chat.
   - (b) **county_labels render review (conditional).** Per sprint queue — if operator-named counties still appear unlabeled at zoom 7–9, inspect MapLibre `text-allow-overlap` / `symbol-sort-key` / `text-padding` on the county_labels source-layer config in `build_template.html`. Conditional on visual confirmation.
   - (c) **Mobile QA Stage 2 — popup audit.** Chat 127 fixed three mobile issues (topbar overflow, sb-toggle off-screen at 320px, drawer dismissal). Remaining mobile risk surface is feature-popup density: ercot_queue group-aggregation popup (Chat 102) can have many breakdown rows; tax_abatements popup carries long text fields. Verify `60vh` max-height + scroll behavior holds at mobile widths against the worst-offender popups. Diagnostic-first; if no issues found, replan as no-deploy.
3. **Build + atomic deploy + merge per §6.12.**
4. **Close-out.** `bash scripts/close-out.sh refinement-chat128-<slug> <deployId>`.

### Acceptance

- Build clean `built=26 missing=0 errored=0`.
- Local↔prod md5 identical on index + any tile delta.
- Branch merged + deleted same chat per §6.12.
- If Stage 3: `coords_source = manual_override` rows present in prod registry per CSV row count; aggregate solar+wind+battery match rate logged.
- If substitution: substitution-specific check per chosen candidate.

### Branch

`refinement-chat128-ercot-stage3` if CSV present, else branch slug matches the chosen substitution: `-counties-color-pass`, `-county-labels-render`, or `-mobile-popup-audit`. Fresh from main.

### Pre-flight

- Chat 127 (2026-05-05): shipped. Deploy `69f99009df0672911f61e588`. Three mobile QA hotfixes in `build_template.html` (CSS+JS, no schema/data delta). (1) Topbar overflow at ≤768px: hid decorative `.title`, tightened topbar `gap` 16→8 + `padding` 16→8, shrank button labels `Share view`→`Share` + `Print / PDF`→`Print`, tightened button padding 14→10. Reduced fixed topbar content from ~600px to ~304px so all four buttons + brand fit at 320px viewports without clipping under `body{overflow:hidden}`; tooltip text preserved via `title=` attrs. (2) `sb-toggle` chevron off-screen at 320px viewport (drawer-open math `min(86vw,320px)+8px+44px` = 327.2 vs 320): clamped left to `min(calc(min(86vw,320px)+8px), calc(100vw - 52px))` so chevron right edge always sits ≥8px inside viewport. (3) No drawer-dismiss except finding 44px chevron at far right edge: added second `map.on('click')` that closes drawer when (a) viewport matches mobile MQ, (b) measureActive false, (c) drawer not already collapsed; delegates to existing `sbToggle.click()` so transition + grid + `map.resize()` behavior is identical. Single commit `1d59da7`. Build clean `built=26 missing=0 errored=0 tiles_total=12064 KB` (unchanged from Chat 126 — pure code change, no data delta). Local↔prod md5 identical (`f6818dabd3ddeacd962f8acc483177f5`). Branch `refinement-chat127-mobile-qa` merged + deleted same chat per §6.12. Tool-budget: ~10 calls vs 4–6 estimate; cause: tool_search needed to load Netlify MCP (deploy.sh requires `NETLIFY_PAT` not in CREDENTIALS.md, fall-through to in-chat MCP per §8 — same issue retrospectively documented in Chat 126, persists).
- ERCOT Stage 3 spec unchanged from Chat 113 settled: WRatio≥88, norm-name suffix-stripping, idempotent CSV read, last-precedence pass, `coords_source = manual_override`. Override CSV remains absent at `data/ercot_queue_overrides.csv` for 14 consecutive slots.

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### ERCOT QUEUE PRECISE GEOCODING

**Multi-chat sprint.** Stage 2 (Chat 113) hit a structural data-coverage ceiling. Stage 3 was queued as Next chat for five consecutive slots (Chats 114–117) without the operator-curated override CSV at `data/ercot_queue_overrides.csv` materializing; substitutions shipped on Chats 118 (LDAD scrape), 119 (date_range filter), 120 (counties color hotfix), 121 (commissioner-court overlay + 1900-01-01 fix + commissioned filter migration). Stage 3 stays alive here and **resumes on CSV arrival** — the moment `data/ercot_queue_overrides.csv` exists in the repo, this entry can be re-promoted to Next chat without any rework.

- **Stage 1 (Chat 112, shipped):** EIA-860 + USWTDB joins. Aggregate match rate 18.4% (309/1,676 solar+wind+battery). Structural ceiling — EIA-860 indexes operating plants while queue is forward-looking by design.
- **Stage 2 (Chat 113, shipped):** TPIT POI proximity (78 matches), OSM substations POI proximity (67 matches; added per §7 ambiguity rule beyond the named TPIT scope), dc_anchors exact-alias (0 matches; no curated tenant alias hit any same-county queue row). Aggregate solar+wind+battery 27.0% (452/1,676) — below the 60% target. Structural ceiling: queue POI universe includes substations being built FOR the project (not in TPIT or OSM today) or named ambiguously without a substation handle. Further programmatic lift requires new substation sources not currently in scope.
- **Stage 3 (deferred — resumes on CSV arrival):** operator-curated manual override CSV at `data/ercot_queue_overrides.csv`, applied as a final precedence-winning pass. Idempotent; operator can edit and re-run anytime. Spec details: add a Stage 2.d pass to `scripts/geocode_ercot_queue.py` that loads the override CSV, builds an `inr → (lat, lon, reason)` map, applies LAST in the pipeline, and stamps `coords_source = manual_override`. Reason logged in run log only (no schema change). Atomic write per §6.15. WRatio threshold (88) and norm-name suffix-stripping settled in Chat 113 — do not retune.

### COUNTY_LABELS RENDER REVIEW (CONDITIONAL)

If post-Chat-111 visual review confirms operator-named counties still appear unlabeled at zoom 7–9, root cause is symbol-collision declutter or min_zoom gating, not data. Diagnostic chat: inspect MapLibre `text-allow-overlap` / `symbol-sort-key` / `text-padding` on the county_labels source-layer config in `build_template.html`. Likely 1 chat. **Conditional on visual confirmation** — do not pre-empt operator review.

### MOBILE STAGE 3 — HOTFIX ON DEMAND

Cross-device QA + polish for the mobile-friendly map work shipped in Chats 100–101. Not scheduled. Surfaced issues become discrete patch chats. 0–1 chat per issue.

---

## Prod status

- Layer count: **24** (display layers — `county_labels` + `counties` count once each in the registry)
- Last published deploy: `69f99009df0672911f61e588` (Chat 127, 2026-05-05). State=ready. **Mobile QA hotfix triple — `build_template.html` CSS+JS only, no schema or data delta.** Diagnostic-first sweep surfaced three latent mobile issues since the Chat 100/101 mobile foundation, ranked High/Low/Medium. (1) **Topbar overflow ≤768px:** brand + 4 buttons + decorative title text summed to ~600px content against a 360px viewport, with the right-side buttons (`Print / PDF`, `Share view`) clipping under `body{overflow:hidden}`. Fix: hide `.title` on mobile, tighten `.topbar` `gap` 16→8 + `padding` 16→8, shrink button labels to `Share` and `Print`, tighten button padding 14→10. Final fixed-width content ~304px at 360px viewport (spacer ≥56px); fits to 320px. Long tooltip text preserved via `title=` attrs. (2) **`sb-toggle` chevron off-screen at 320px:** existing rule `left: calc(min(86vw,320px) + 8px)` plus 44px button width = right edge at 327.2px against 320px viewport. Fix: clamp left to `min(calc(min(86vw,320px)+8px), calc(100vw - 52px))` so chevron right edge always sits ≥8px inside viewport at any width. (3) **No drawer-dismiss except chevron at far right edge:** drawer is z-index 10 overlay covering 86vw of map; on mobile, the only way to dismiss it was finding the chevron, which itself was at the worst-case off-screen position before fix #2. Added second `map.on('click')` that closes drawer when (a) `_mqMobile.matches`, (b) `measureActive` is false (taps are vertex-add then), (c) `sidebarCollapsed` is false; delegates to existing `sbToggle.click()` so transition + grid-template-columns animation + `map.resize()` behavior is byte-identical to chevron tap. Single commit `1d59da7`. Build clean: `built=26 missing=0 errored=0 tiles_total=12064 KB` (unchanged from Chat 126 — pure code change, no data delta). Local↔prod md5 identical (`f6818dabd3ddeacd962f8acc483177f5`). All three fix markers verified prod-side. Branch `refinement-chat127-mobile-qa` merged + deleted same chat per §6.12. Tool-budget: ~10 calls vs 4–6 estimate; cause: same as Chat 126 — `deploy.sh` requires `NETLIFY_PAT` not in CREDENTIALS, fall-through to in-chat Netlify MCP. Persistent infra item; not protocol drift.
- Previous deploy: `69f8c521328f51630cbcefc2` (Chat 126, 2026-05-04). State=ready. **Two-line `layers.yaml` hygiene cleanup.** (a) Dropped dead `solar.commissioned` filter declaration — EIA-860 solar layer carries 100% empty commissioned data (180/180 rows blank), so `compute_filter_stats` was silently dropping it from the built HTML at every build since the field was added. Declaration was dead. (c) Re-labeled `ercot_queue.commissioned` filter from `Commissioned` to `Commissioned (Y/N)` — field is a Yes/No flag indicating whether the project has been commissioned, while sibling `Commissioned (year)` filters on eia860_plants/battery/wind (added Chat 121) are year-numeric ranges; the shared label `Commissioned` was visually conflicting at the filter UI. Both edits per §7 rule 7 (yaml-only, no template touch). Single commit `be8bdd4`. Build clean: `built=26 missing=0 errored=0 tiles_total=12064 KB` (unchanged from Chat 125 — pure code change, no data delta). Local↔prod md5 identical (`2e4b4c5c92f8d147dc43bee71b5d164c`). Built filter-spec verified prod-side: solar layer registry no longer references commissioned; ercot_queue.commissioned label = `Commissioned (Y/N)`. Branch `refinement-chat126-filter-hygiene` merged + deleted same chat per §6.12. Tool-budget: ~10 calls vs 4–6 estimate; cause: tool_search needed to load Netlify MCP (deploy.sh requires NETLIFY_PAT not in CREDENTIALS.md, fall-through to in-chat MCP per §8). Documented for retrospective.
- Previous deploy: `69f3f2040c4cac644f1ad96d` (Chat 125, 2026-04-30). State=ready. **`drilling_permit_density` layer pulled from prod per operator decision.** Static-density choropleth misrepresented the time-trend story (Pecos's 4th-highest absolute permit count gets buried under low density driven by huge 4,750 sq mi area; recent-years drop from 506 in 2019 to 116 in 2025 invisible in a single color). yaml stanza removed (71 lines deleted); aggregator script `scripts/build_drilling_density.py`, scraper `scripts/scrape_rrc_w1.py`, and 11 augmented features in `combined_geoms.geojson` (county / area_sqmi / 4-window permit_count / 4-window permits_per_sqmi / source / source_date) all preserved as warm data — resurrection = re-add yaml stanza, no rebuild of underlying data. Build clean: `built=26 missing=0 errored=0 tiles_total=12064 KB` (-7 KB vs Chat 124, attributable to dropping `drilling_permit_density.pmtiles` 6 KB + index.html schema delta from one fewer layer registration). Local↔prod md5 identical (`e5a76dc03ae7246d4b277a3ce7a4da68` — byte-identical to Chat 121's index since intervening Chats 122/123 didn't touch build artifacts and Chat 124's drilling stanza is now reverted). **Trend Excel delivered separately** to operator: `RRC_W1_Drilling_Permits_Trend.xlsx`, 4 sheets (Decade View story-first; Summary by 10-yr density desc; Counts by Year raw 51-row matrix; Notes with provenance + caveats), 240 formulas, 0 errors per LibreOffice recalc. Year-by-year matrix exposes the structural narrative absent from a flat color: Pecos 1976–1985 boom (3,897 permits), 1986–95 collapse (1,491), 2006–15 mini-rebound (3,137), 2016–25 secondary rollover (2,411) vs Reeves 480 → 13,757 / Loving 537 → 9,058 / Upton 1,663 → 11,057 over the same 50-yr arc. Branch `refinement-chat125-drilling-density-revert` merged + deleted same chat per §6.12. Tool-budget: ~12 calls vs 8–14 estimate; cause: parallel scrape (1 long-blocking call), Excel build + recalc + extract verification (3 calls), full deploy chain.
- **Older deploys (24 entries, Chats 124 → 102):** archived to git history. Recover with `git log --merges --grep "deploy [0-9a-f]" main` or read merge commit messages. Trimmed Chat 127c per OPERATING.md §15 (WIP_OPEN.md ≤8 KB target). Operationally relevant detail (drilling_permit_density warm-data resurrection path, ERCOT queue Stage 1+2 match rates, ERCOT no-deploy slots 115/116/117) lives in `## Sprint queue` and `## Open backlog`.
- URL: `https://lrp-tx-gis.netlify.app` — requires real User-Agent on curl (`-A "Mozilla/5.0"`).

## Open backlog

**Data-pipeline gaps** (non-blocking):
- `eia860_plants`: 476/1367 rows still null `capacity_mw` (down from 529), 529/1367 null `commissioned`, 438/1367 null `technology`. EIA-860 source-side gaps; will not improve without alternate source.
- `wind`: USWTDB schema has no `operator`, `technology`, or `fuel`; structural blanks (19464/19464). `commissioned` populated for 19364/19464 (down from 0); `manu` and `model` populated. Filling operator would require joining a project-layer source (e.g. EIA-860 wind plants) — separate sprint item if pursued.
- `ercot_queue`: Stages 1+2 (Chats 112–113) geocoded 479/1,778 rows precisely via cascading sources — eia860 324, tpit_poi 78, substation_poi 67, uswtdb 10, dc_anchors 0. Remaining 1,299 carry `coords_source=county_centroid` provenance. Aggregate solar+wind+battery 452/1,676 (27.0%); structural ceiling on programmatic match rate. Stage 3 (Chat 116) targets remaining high-value misses via operator-curated manual override CSV.
- `tax_abatements`: 1,495 rows (Chat 121) = 1,486 LDAD-scraped (`coords_source=ldad_county_centroid`) + 9 commissioner-court seed (`coords_source=commissioner_court`, sourced from Chat 83 intel restored via `data/abatements_court_seed.csv`). LDAD is agreement-level, not site-level — per-record lat/lon is not exposed in the API or detail pages, so the 1,486 LDAD rows ride county centroids. Lift path if site-level precision becomes a priority: parse property addresses out of detail-page PDFs (where present) and geocode; expect ≤30% lift since most records reference reinvestment zones rather than street addresses. The 9 seed rows carry curated coords from Chat 83's commissioner-court scrape; `transform_ldad.py` preserves them across refreshes by selectively dropping only `coords_source=ldad_county_centroid` rows.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar
- BEAD `bead_fiber_planned` layer (Chat 91 §1 dropped): BDO XLSX trio archived to `data/bead_bdo/` but contains no county or coords. Three unblock paths documented in `data/bead_bdo/README.md`

**UI/UX:**
- Counties outline color `#fbbf24` (amber) shipped Chat 120 as a basemap-universal hotfix. Was `#ffffff` (Chat 107c, satellite-only). Revisit choice with a holistic contrast pass when not under time pressure — amber works on both basemaps but may clash with other styling (warning-color overlap with hyperscale campus strokes, etc.). **Tracked as Chat 128 substitution candidate (a).**
- `date_range` filter literal extension to eia860_plants/battery/wind: would require padding `yyyy` → `yyyy-01-01` in 3 ingest scripts (`refresh_eia860.py` plants/battery + `refresh_uswtdb.py` wind). Currently those layers use `numeric` year-slider per Chat 121 — works fine, low priority.
- Filter inputs (`.filter-text`, `.filter-range input`) sized at 40 px on mobile, not strictly the 44 px WCAG bar. Acceptable per Apple HIG (≥40 px) but flag for review if operator testing surfaces hit-rate issues.
- `county_labels` declutter at low zoom: post-Chat-111 with 254 labels, MapLibre symbol-collision will hide overlaps below ~zoom 7. Conditional sprint item above; do not pre-empt visual review.

**Infrastructure:**
- `GITHUB_PAT` can push branches, 403 on PR creation. Direct-merge-to-main is the protocol (OPERATING.md §9)
- **Akamai datacenter-egress block on `reevescounty.org`** — cloud-runner / GitHub-Actions traffic 403s regardless of UA / TLS fingerprint. Hard prerequisite for the abatement-weekly-cron sprint item. Unblock options: residential-proxy egress (paid), Akamai allowlisting via Reeves County IT (low likelihood), search-API result pages
- Fresh-container build deps + git identity gaps — promoted to **active fix in Chat 103**. Currently both worked around manually (cairosvg + tippecanoe install at session start; `git config user.email/.name` before close-out.sh).

**Process:**
- Historical §6.12 / tool-budget retrospectives (Chats 92, 100, 102, 111) archived to git history. Recoverable via `git log --grep "§6.12" main`. Net learnings absorbed into OPERATING.md hard rules and `scripts/ship.sh` atomic deploy+merge.

**Outstanding credential hygiene:**
- `GITHUB_PAT` leak from Chat 87 unrotated per operator override. Token valid until 2027-04-21

**Permanently excluded:** see ARCHITECTURE.md §11

**Other (non-GIS):** Grid Wire Vol. 7. Tier 2 water availability assessments. Excel returns model.
