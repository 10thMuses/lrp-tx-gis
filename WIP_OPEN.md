# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat

**Chat 118 — COMPTROLLER LDAD SCRAPE: statewide `tax_abatements` coverage.** Substituted into Next chat by Chat 117 replan after three consecutive sessions (Chats 114 displaced, 115+116 reduced to handoff-only) failed to advance ERCOT Stage 3 because the operator-curated override CSV did not land. ERCOT Stage 3 demoted to sprint queue with "resumes on CSV arrival" — substitution does not deprioritize Stage 3, only stops it from blocking the next-chat slot. LDAD work is operator-pre-authorized in Chat 106a, has no input precondition, and advances `tax_abatements` from 9 county-scraped records to statewide coverage.

### Task

1. Add `scripts/scrape_ldad.py` (or extend `scripts/scrape_abatements.py` if cleaner) that drives Playwright-headless against `https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`, paginates result pages, and writes `outputs/refresh/comptroller_ldad_<ISO-date>.csv`.
2. Required CSV columns (minimum): `agreement_id`, `taxing_unit`, `applicant`, `county`, `commissioned`, `lat`, `lon`. Geocode lat/lon to county centroid if no per-site coords are exposed; stamp `coords_source = ldad_county_centroid` for those rows.
3. Merge into combined points per OPERATING.md §8 merge cycle: drop existing `tax_abatements` rows from `combined_points.csv`, append refreshed rows, atomic write per §6.15.
4. Build → deploy to prod per §8.
5. Append run log: total LDAD rows scraped, rows merged into `tax_abatements`, before/after row count.

### Acceptance

- Build clean: `built=26 missing=0 errored=0`.
- `tax_abatements` row count grows from current 9 to scraped total (LDAD universe is ~hundreds of agreements statewide).
- No schema change to `tax_abatements` field set beyond what's already present (audit current fields before extending).
- Local↔prod md5 identical.
- Branch merged + deleted same chat per §6.12.
- If Akamai or Comptroller-side rate-limiting blocks the scrape mid-run, partial results are written and the chat reduces to a refresh-only commit (no merge into combined points until full coverage is in hand). Document any pagination or block boundary in the run log.

### Branch

`refinement-chat118-ldad-scrape`

### Pre-flight

- Chat 117 was a replan-only chat. Substituted Stage 3 → LDAD scrape because three consecutive next-chat slots (114, 115, 116) failed on the same CSV-input gap. Branch `refinement-chat117-replan` merged to main with `(no deploy)` tag. Layer count, schema, prod artifacts unchanged. Last published deploy still Chat 114 `69f10553bbc94b136581c584`.
- LDAD scope confirmed by Chat 106a operator authorization; sprint queue carried this entry through Chats 107–116 without contention. Two-chat ceiling per the queue entry; one chat sufficient if pagination + geocoding land cleanly, two if a schema-extension audit on `tax_abatements` is needed first.
- Akamai datacenter-egress block is documented for `reevescounty.org` (Chat 110 onward, see Open backlog §Infrastructure). `comptroller.texas.gov` has not exhibited the same behavior in prior chats but verify with a single sanity curl during recon before the full Playwright run.
- Geocoding strategy: LDAD records are agreement-level not site-level, so per-record lat/lon is unlikely to be exposed. County-centroid stamping with `coords_source = ldad_county_centroid` is the documented fallback. If site-level addresses ARE exposed in the search-result detail pages, prefer geocoding those over centroid; document the choice in the run log.
- ERCOT Stage 3 stays alive in the sprint queue. The override-CSV pipeline path remains valid and resumes the moment the CSV lands at `data/ercot_queue_overrides.csv` — no rework needed.

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### ERCOT QUEUE PRECISE GEOCODING

**Multi-chat sprint.** Stage 2 (Chat 113) hit a structural data-coverage ceiling. Stage 3 was queued as Next chat for four consecutive slots (Chats 114, 115, 116, 117) without the operator-curated override CSV at `data/ercot_queue_overrides.csv` materializing. Chat 117 substituted the next-chat slot to Comptroller LDAD scrape; Stage 3 stays alive here and **resumes on CSV arrival** — the moment `data/ercot_queue_overrides.csv` exists in the repo, this entry can be re-promoted to Next chat without any rework.

- **Stage 1 (Chat 112, shipped):** EIA-860 + USWTDB joins. Aggregate match rate 18.4% (309/1,676 solar+wind+battery). Structural ceiling — EIA-860 indexes operating plants while queue is forward-looking by design.
- **Stage 2 (Chat 113, shipped):** TPIT POI proximity (78 matches), OSM substations POI proximity (67 matches; added per §7 ambiguity rule beyond the named TPIT scope), dc_anchors exact-alias (0 matches; no curated tenant alias hit any same-county queue row). Aggregate solar+wind+battery 27.0% (452/1,676) — below the 60% target. Structural ceiling: queue POI universe includes substations being built FOR the project (not in TPIT or OSM today) or named ambiguously without a substation handle. Further programmatic lift requires new substation sources not currently in scope.
- **Stage 3 (deferred — resumes on CSV arrival):** operator-curated manual override CSV at `data/ercot_queue_overrides.csv`, applied as a final precedence-winning pass. Idempotent; operator can edit and re-run anytime. Spec details: add a Stage 2.d pass to `scripts/geocode_ercot_queue.py` that loads the override CSV, builds an `inr → (lat, lon, reason)` map, applies LAST in the pipeline, and stamps `coords_source = manual_override`. Reason logged in run log only (no schema change). Atomic write per §6.15. WRatio threshold (88) and norm-name suffix-stripping settled in Chat 113 — do not retune.

### DATE-RANGE FILTER FOR `tax_abatements.commissioned`

True range slider replacing current text-multi-select on distinct ISO dates. Touches `build.py compute_filter_stats` + `build_template.html filterFieldControlHtml` + matching predicate. 1–2 chats. **Deferred** — operator's chat-110/111 series surfaced higher-priority data-quality work above.

### COUNTY_LABELS RENDER REVIEW (CONDITIONAL)

If post-Chat-111 visual review confirms operator-named counties still appear unlabeled at zoom 7–9, root cause is symbol-collision declutter or min_zoom gating, not data. Diagnostic chat: inspect MapLibre `text-allow-overlap` / `symbol-sort-key` / `text-padding` on the county_labels source-layer config in `build_template.html`. Likely 1 chat. **Conditional on visual confirmation** — do not pre-empt operator review.

### MOBILE STAGE 3 — HOTFIX ON DEMAND

Cross-device QA + polish for the mobile-friendly map work shipped in Chats 100–101. Not scheduled. Surfaced issues become discrete patch chats. 0–1 chat per issue.

---

## Prod status

- Layer count: **24** (display layers — `county_labels` + `counties` count once each in the registry)
- Last published deploy: `69f10553bbc94b136581c584` (Chat 114, 2026-04-28). State=ready. WAHA paint-order fix: `waha_circle` (lines 559-578) and `labels_hubs` (lines 579-595) moved before `la_escalera` (line 82) in `layers.yaml`, so MapLibre `addLayer` iteration paints WAHA marker + label BEFORE Hyperscale campus polygons, putting the campus polygon strokes ON TOP. LAYERS array indices: solstice_substation 3, waha_circle 4, labels_hubs 5, la_escalera 6, longfellow_ranch 7, gw_ranch 8, mpgcd_zone1 9. Sidebar Local Focal Points group within-order changed from solstice → mpgcd_zone1 → waha to solstice → waha → mpgcd_zone1 (mild cosmetic side effect; labels_hubs `sidebar_omit: true` so unaffected). GROUP_ORDER constant in `build_template.html` unchanged, so cross-group sidebar order intact. Build clean: `built=26 missing=0 errored=0 tiles_total=11606 KB` (unchanged from Chat 113). Local↔prod md5 identical (index.html `2f8f2597c2aa3b08766cd27378b5308f`). Operator-visible result: GW Ranch's 3.5-mi-wide red campus stroke renders unobscured at all zooms. WAHA hub readability preserved (radius/styling untouched).
- Chat 117 (2026-04-29): **no deploy.** Replan only. Substituted ERCOT Stage 3 → Comptroller LDAD scrape on the next-chat slot after three consecutive sessions failed to advance Stage 3 because the operator-curated override CSV did not land at `data/ercot_queue_overrides.csv`. Stage 3 not abandoned — demoted into the sprint queue as "resumes on CSV arrival" with full spec preserved; the override-CSV pipeline path remains valid and the sprint resumes the moment the CSV exists in the repo. Branch `refinement-chat117-replan` merged to main with `(no deploy)` tag. Layer count, schema, prod artifacts unchanged from Chat 114. Last published deploy still Chat 114 `69f10553bbc94b136581c584`.
- Chat 116 (2026-04-28): **no deploy.** Handoff-write only. Override CSV absent at `data/ercot_queue_overrides.csv` at session-open, so per the Chat 116 task spec item 1 the chat reduced to WIP rewrite + close-out: Stage 3 re-promoted to Chat 117 (fourth consecutive next-chat slot), sprint queue updated with explicit substitution candidates (Comptroller LDAD scrape, date-range filter), branch `refinement-chat116-handoff` merged to main with `(no deploy)` tag. Layer count, schema, prod artifacts all unchanged from Chat 114.
- Chat 115 (2026-04-28): **no deploy.** Handoff-write only. Override CSV absent at `data/ercot_queue_overrides.csv` at session-open, so per the Chat 115 task spec item 1 the chat reduced to WIP rewrite + close-out: Stage 3 re-promoted to Chat 116, sprint queue updated, branch `refinement-chat115-handoff` merged to main with `(no deploy)` tag. Layer count, schema, prod artifacts all unchanged from Chat 114.
- Previous deploy: `69f0c593e361c81f37ca36ee` (Chat 113, 2026-04-28). State=ready. ERCOT queue geocoding Stage 2: 78 rows matched via TPIT POI proximity (planned-upgrade substations, fuzzy WRatio≥88, same-county via TIGER 2024 point-in-polygon county derivation), 67 rows via OSM substations layer (same matching kernel, distinct `substation_poi` provenance), 0 rows via dc_anchors exact-alias match. Final coords_source distribution: county_centroid 1,299; eia860 324; tpit_poi 78; substation_poi 67; uswtdb 10. Build clean: `built=26 missing=0 errored=0 tiles_total=11606 KB`. Local↔prod md5 identical (index.html `0b630fd927c6d76adbb1ee8e9a518a6c`; ercot_queue.pmtiles `dbff4c440340bee1ebb2dcd0572a3851`). Aggregate solar+wind+battery match rate 27.0% (452/1,676) — below 60% target for structural reasons (queue POI universe extends beyond available substation catalogs). Stage 2 scope assumption: WIP named two passes (TPIT + dc_anchors); per §7 ambiguity rule, Chat 113 added a third pass against OSM substations to chase the target.
- Previous deploy: `69f0ad1c2ffe34b3320d0e1e` (Chat 112, 2026-04-28). State=ready. ERCOT queue geocoding Stage 1: 334 rows matched via EIA-860 (324) + USWTDB (10); 1,444 retained existing approximate coords with `coords_source=county_centroid` provenance label. New `coords_source` field stamped on all 1,778 ercot_queue rows. Build clean: `built=26 missing=0 errored=0 tiles_total=11603 KB`. Local↔prod md5 identical (`0b630fd927c6d76adbb1ee8e9a518a6c`).
- Previous deploy: `69f01efe66cedded36ed2e99` (Chat 111, 2026-04-28). State=ready. `county_labels` extended 46 → 254 (all TX counties via TIGER 2024). Local↔prod md5 identical (`4fb699f478ad530c04f44ab350493bd1`). Build clean: `built=26 missing=0 errored=0 tiles_total=11595 KB`.
- Previous deploy: `69f008f6187338b50dc2a829` (Chat 110c, 2026-04-28). State=ready. Transmission & Grid reorder + tpit_subs recolor + Longfellow polygon move.
- Previous deploy: `69f00661239f04d4b9bec06f` (Chat 110b, 2026-04-28). Hotfix: `fill-opacity || 0.25` → `?? 0.25`; `mpgcd_zone1` default_on true.
- Previous deploy: `69efdc12326f632c49033ed2` (Chat 110, 2026-04-27). Sidebar overhaul.
- Previous deploy: `69ef926ed31a462a98b27f77` (Chat 109b, 2026-04-27). State=ready. Hyperscale DC & Power Campuses group consolidation + WAHA Pecos fix + Solstice visibility.
- Previous deploy: `69ef8b0a7ca58c0d4d25ae4d` (Chat 108b, 2026-04-27). State=ready. Local Developments group + popup audit + permit visibility.
- Previous deploy: `69ee7b6cffaa366af764784c` (Chat 107d, 2026-04-26). State=ready. Critical bug fix on top of 107c: build.py was defaulting `line_width` to **2** in the layer registry render path (line 825), overriding template defaults — so the JS template's 0.5 default never took effect. Fixed: `'line_width': L.get('line_width', 0.5)`. Also: county_labels switched to dark text (`#0f172a`) with halo opt-out via new `text_halo: false` YAML flag; template halo logic now auto-picks contrast (light text → dark halo, dark text → light halo). Counties `line_width` raised 0.5 → 1. county_labels `min_zoom: 4 → 5`.
- Previous deploy: `69ee76fc43cd26b6f3460922` (Chat 107c, 2026-04-26). State=ready. Contrast/legibility/fuel pass.
- Previous deploy: `69ee72bcbd5d65c5bac1e0eb` (Chat 107a, 2026-04-26).
- Previous deploy: `69ee25b25be421df2f22b294` (Chat 105, 2026-04-26). PMTiles feature counts fix for prebuilt layers.
- Previous deploy: `69ee07134b63d09184004cf9` (Chat 102, 2026-04-26). State=ready. ERCOT queue project aggregation popup. `compute_ercot_group_aggregates(csv_path)` streams `combined_points.csv` once and returns `{group_key: {group_total_mw, group_count, group_breakdown}}` (breakdown is `\n`-joined `<n> · <mw> MW · <county>` lines, sorted by MW desc). `split_combined_csv()` stamps these fields onto every ercot_queue feature's props during NDGeoJSON write. Popup helper `ercotQueueGroupSummaryHtml(props)` renders a summary block (sage-pink card with project group label, total MW, component count, breakdown list) above the per-row table when `group_count > 1`; empty for singletons. Build clean: `built=26  missing=0  errored=0  tiles_total=18933 KB` (+68 KB from prior deploy carrying 3 new fields × 1,778 ercot_queue rows). Local↔prod md5 identical. Aggregation reach: 1,205 groups total, 394 with 2+ components.
- URL: `https://lrp-tx-gis.netlify.app` — requires real User-Agent on curl (`-A "Mozilla/5.0"`).

---

## Open backlog

**Data-pipeline gaps** (non-blocking):
- `eia860_plants`: 476/1367 rows still null `capacity_mw` (down from 529), 529/1367 null `commissioned`, 438/1367 null `technology`. EIA-860 source-side gaps; will not improve without alternate source.
- `wind`: USWTDB schema has no `operator`, `technology`, or `fuel`; structural blanks (19464/19464). `commissioned` populated for 19364/19464 (down from 0); `manu` and `model` populated. Filling operator would require joining a project-layer source (e.g. EIA-860 wind plants) — separate sprint item if pursued.
- `ercot_queue`: Stages 1+2 (Chats 112–113) geocoded 479/1,778 rows precisely via cascading sources — eia860 324, tpit_poi 78, substation_poi 67, uswtdb 10, dc_anchors 0. Remaining 1,299 carry `coords_source=county_centroid` provenance. Aggregate solar+wind+battery 452/1,676 (27.0%); structural ceiling on programmatic match rate. Stage 3 (Chat 116) targets remaining high-value misses via operator-curated manual override CSV.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar
- BEAD `bead_fiber_planned` layer (Chat 91 §1 dropped): BDO XLSX trio archived to `data/bead_bdo/` but contains no county or coords. Three unblock paths documented in `data/bead_bdo/README.md`

**UI/UX:**
- `date_range` filter type not implemented (carryforward from Chat 92 handoff). `tax_abatements` `commissioned` filter ships as `text` multi-select over distinct ISO dates — functional with 9 rows but not a true range slider. Touches `build.py compute_filter_stats` + `build_template.html filterFieldControlHtml` + matching predicate.
- Filter inputs (`.filter-text`, `.filter-range input`) sized at 40 px on mobile (Chat 100), not strictly the 44 px WCAG bar. Acceptable per Apple HIG (≥40 px) but flag for review if operator testing surfaces hit-rate issues.
- `county_labels` declutter at low zoom: post-Chat-111 with 254 labels, MapLibre symbol-collision will hide overlaps below ~zoom 7. Conditional sprint item above; do not pre-empt visual review.

**Infrastructure:**
- `NETLIFY_PAT` absent from `CREDENTIALS.md`. Netlify MCP proxy path canonical
- `GITHUB_PAT` can push branches, 403 on PR creation. Direct-merge-to-main is the protocol (OPERATING.md §9)
- **Akamai datacenter-egress block on `reevescounty.org`** — cloud-runner / GitHub-Actions traffic 403s regardless of UA / TLS fingerprint. Hard prerequisite for the abatement-weekly-cron sprint item. Unblock options: residential-proxy egress (paid), Akamai allowlisting via Reeves County IT (low likelihood), search-API result pages
- Fresh-container build deps + git identity gaps — promoted to **active fix in Chat 103**. Currently both worked around manually (cairosvg + tippecanoe install at session start; `git config user.email/.name` before close-out.sh).

**Process:**
- Chat 92 §6.12 violation (deploy + merge atomic): published deploy `69ed2cdf4039c554a1316ad2` to prod but deferred close-out merge, citing scope-creep. Reconciled in Chat 93 (merge `3a59a73`). Root cause: doc-restructure work appeared on a feature branch alongside the data-layer work, blowing past §6.13 stage-fits-one-chat. Preventive structural fix: pre-commit hook could reject doc-structure changes on `refinement-*` branches; lower-effort alternative is operator-side discipline at branch-naming time.
- Chat 100 §6.12 deviation: deploy + merge were not atomic in the same chat. Tracked as fixed via session-open.sh structural fix scheduled for Chat 103.
- Chats 101 + 102 §6.12 compliant: deploy + merge atomic in single shipping flow.
- Chat 102 tool-budget overrun: 14 tool calls vs 6–8 estimate. Cause: heavy verification of stamped-fields encoding (tippecanoe-decode iterations + pmtiles metadata read) before deploying. Lesson: PMTiles metadata schema check via python-pmtiles is the single sufficient verification step; skip tippecanoe-decode tile-by-tile sampling.
- Chat 111 tool-budget: ~14 tool calls vs ~8 estimate. Cause: npx cache corruption on first deploy attempt forced a clean-and-retry; one Netlify MCP read errored mid-poll. Both transient infra hiccups, not protocol drift.

**Outstanding credential hygiene:**
- `GITHUB_PAT` leak from Chat 87 unrotated per operator override. Token valid until 2027-04-21

**Permanently excluded:** see ARCHITECTURE.md §11

**Other (non-GIS):** Grid Wire Vol. 7. Tier 2 water availability assessments. Excel returns model.
