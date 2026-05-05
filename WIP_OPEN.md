# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat

**Chat 129 — FIRST CLAUDE CODE SESSION (post-migration smoke test) OR ERCOT STAGE 3 / SUBSTITUTION.**

Chat 128 migrated the build pipeline to be environment-agnostic. Next session opens in **Claude Code** unless operator explicitly stays in chat mode. First Claude Code session = bootstrap + smoke test; substantive work happens in Chat 130 onward.

### Task

**If first Claude Code session:**

1. `git clone https://github.com/10thMuses/lrp-tx-gis.git && cd lrp-tx-gis`
2. `bash scripts/bootstrap-claude-code.sh`
3. Edit `.env`: paste `GITHUB_PAT` (already in `/mnt/project/CREDENTIALS.md` — read once, paste into `.env`) and mint a Netlify PAT at `https://app.netlify.com/user/applications#personal-access-tokens` (description `lrp-tx-gis-deploy`, expiry 1 year) and paste as `NETLIFY_PAT`.
4. Smoke build: `python3 build.py` — expect `built=26 missing=0 errored=0`. Output goes to `./dist/` not `/mnt/user-data/outputs/dist/`.
5. **No deploy this chat.** Smoke test only. Optional: `bash scripts/deploy.sh --rebuild` end-to-end against prod once `.env` is populated, but treat as confirmation that scripts work — don't ship substantive changes in the bootstrap session.
6. Close-out: `bash scripts/close-out.sh refinement-chat129-cc-bootstrap none "Chat 129 first Claude Code session — bootstrap + smoke"`.

**If staying in chat mode (operator preference):**

Fall through to ERCOT Stage 3 / substitution per Chat 128's pre-migration spec. Substitution candidates remain: (a) counties color contrast review, (b) county_labels render review, (c) mobile popup audit. Override CSV at `data/ercot_queue_overrides.csv` still gates Stage 3 (slot 15).

### Acceptance

**Claude Code bootstrap:**
- `python3 build.py` produces `built=26 missing=0 errored=0` against the local clone with no `/mnt/...` paths.
- `bash scripts/deploy.sh --rebuild` resolves NETLIFY_PAT from `.env` (no exit 3 on credential resolution).
- Branch merged + deleted same session per §6.12 even though no deploy occurred.

**Chat-mode fall-through:** original Chat 128 acceptance criteria.

### Branch

`refinement-chat129-cc-bootstrap` if Claude Code; else `refinement-chat129-<ercot-or-substitution-slug>`. Fresh from main.

### Pre-flight

- Chat 128 (2026-05-05): shipped, no deploy. **Migration to environment-agnostic build pipeline.** `build.py` now resolves PROJECT, DIST, UPLOADS via env vars (`LRP_PROJECT_DIR`, `LRP_DIST_DIR`, `LRP_UPLOADS_DIR`) with chat-mode `/mnt/...` fallbacks. `scripts/deploy.sh` resolves NETLIFY_PAT from `.env` first, then `/mnt/project/CREDENTIALS.md`, then shell env (via robust awk reader that handles empty placeholder + populated value in same file). Added `.env.example` template, gitignored `.env`. New `scripts/bootstrap-claude-code.sh` (idempotent: tippecanoe install, python deps, `.env` copy, git identity, smoke test). `OPERATING.md §1` rewritten to be environment-agnostic with pointer to `CLAUDE.md` for env specifics. `OPERATING.md §5` adds Claude Code session-open variant. `CLAUDE.md` updated with first-time-setup section + build-paths table. Smoke-tested both modes locally: chat-mode build clean (`built=26 errored=0 tiles_total=12064 KB`, output to `/mnt/user-data/outputs/dist/`); Code-mode build clean (`built=26 errored=0 tiles_total=12064 KB`, output to `/tmp/cc_test_dist/`). Single commit, atomic merge to main per §6.12.
- ERCOT Stage 3 unchanged from Chat 113 settled spec. Override CSV still absent at `data/ercot_queue_overrides.csv` (15 consecutive slots).

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
- Last published deploy: `69f99009df0672911f61e588` (Chat 127, 2026-05-05). State=ready. **Mobile QA hotfix triple — `build_template.html` CSS+JS only, no schema or data delta.** Diagnostic-first sweep surfaced three latent mobile issues since the Chat 100/101 mobile foundation, ranked High/Low/Medium. (1) **Topbar overflow ≤768px:** brand + 4 buttons + decorative title text summed to ~600px content against a 360px viewport, with the right-side buttons (`Print / PDF`, `Share view`) clipping under `body{overflow:hidden}`. Fix: hide `.title` on mobile, tighten `.topbar` `gap` 16→8 + `padding` 16→8, shrink button labels to `Share` and `Print`, tighten button padding 14→10. Final fixed-width content ~304px at 360px viewport (spacer ≥56px); fits to 320px. Long tooltip text preserved via `title=` attrs. (2) **`sb-toggle` chevron off-screen at 320px:** existing rule `left: calc(min(86vw,320px) + 8px)` plus 44px button width = right edge at 327.2px against 320px viewport. Fix: clamp left to `min(calc(min(86vw,320px)+8px), calc(100vw - 52px))` so chevron right edge always sits ≥8px inside viewport at any width. (3) **No drawer-dismiss except chevron at far right edge:** drawer is z-index 10 overlay covering 86vw of map; on mobile, the only way to dismiss it was finding the chevron, which itself was at the worst-case off-screen position before fix #2. Added second `map.on('click')` that closes drawer when (a) `_mqMobile.matches`, (b) `measureActive` is false (taps are vertex-add then), (c) `sidebarCollapsed` is false; delegates to existing `sbToggle.click()` so transition + grid-template-columns animation + `map.resize()` behavior is byte-identical to chevron tap. Single commit `1d59da7`. Build clean: `built=26 missing=0 errored=0 tiles_total=12064 KB` (unchanged from Chat 126 — pure code change, no data delta). Local↔prod md5 identical (`f6818dabd3ddeacd962f8acc483177f5`). Branch `refinement-chat127-mobile-qa` merged + deleted same chat per §6.12.
- Chat 128 (2026-05-05): **no deploy.** Migration to environment-agnostic build pipeline. Three structural changes: (1) `build.py` resolves `PROJECT`, `DIST`, `UPLOADS` via env vars (`LRP_PROJECT_DIR`, `LRP_DIST_DIR`, `LRP_UPLOADS_DIR`) with chat-mode `/mnt/...` fallbacks via existence-check; both modes smoke-tested locally and produce identical `built=26 errored=0 tiles_total=12064 KB`. (2) `scripts/deploy.sh` resolves `NETLIFY_PAT` from `.env` first, then `/mnt/project/CREDENTIALS.md`, then shell env via robust awk reader that handles empty placeholder + populated value in same file (validated against three .env shapes). (3) New `.env.example` template + idempotent `scripts/bootstrap-claude-code.sh` (tippecanoe install, python deps, `.env` copy, git identity, smoke test). `OPERATING.md §1` rewritten environment-agnostic with pointer to `CLAUDE.md` for env specifics; `§5` adds Claude Code session-open variant. `CLAUDE.md` updated with first-time-setup section + build-paths table. Single commit, atomic merge to main per §6.12. Next session opens in **Claude Code** unless operator overrides.
- Chat 127c (2026-05-05): **no deploy.** WIP_OPEN.md drift cleanup — Prod status archived (38929 → 18434 bytes), obsolete `NETLIFY_PAT absent` line removed (per Chat 127b analysis: trade not worth account-wide credential), §12 budget table updated 4→3 to match §8 build-cycle target, 5 stale UI/UX items archived (Chat 121/126 cleanups already shipped), Process section collapsed (4 historical retrospectives → git log pointer). audit.sh remaining drift: OPERATING.md 329 lines (separate chat), 3 stranded branches (separate chat). Atomic merge per §6.12.
- Chat 127b (2026-05-05): **no deploy.** Token-budget trim — md5-parity poll replaces MCP `get-deploy-for-site` polling + 45s blind sleep in `deploy.sh` (saves one MCP round-trip per deploy plus ~3KB JSON envelope). Correctness depends on per-build byte-unique index.html, guaranteed by new `/*__BUILD_ID__*/` token injection in `build.py:render_html` (UTC timestamp + 4-byte random nonce; verified two consecutive builds produce distinct md5s). Session-open reading discipline codified in `OPERATING.md §5` — only `## Next chat` block as standing context. Build cycle target 4→3 calls.
- Previous deploy: `69f8c521328f51630cbcefc2` (Chat 126, 2026-05-04). State=ready. **Two-line `layers.yaml` hygiene cleanup.** (a) Dropped dead `solar.commissioned` filter declaration. (c) Re-labeled `ercot_queue.commissioned` → `Commissioned (Y/N)`. Build clean: `built=26 errored=0 tiles_total=12064 KB`. Local↔prod md5 identical (`2e4b4c5c92f8d147dc43bee71b5d164c`).
- Previous deploy: `69f3f2040c4cac644f1ad96d` (Chat 125, 2026-04-30). State=ready. **`drilling_permit_density` layer pulled from prod per operator decision.** yaml stanza removed (71 lines); aggregator script + 11 augmented features in `combined_geoms.geojson` preserved as warm data — resurrection = re-add yaml stanza, no rebuild of underlying data. Build clean: `built=26 errored=0 tiles_total=12064 KB`. **Trend Excel delivered separately:** `RRC_W1_Drilling_Permits_Trend.xlsx`, 4 sheets, 240 formulas. Year-by-year matrix exposes structural narrative absent from flat color: Pecos 1976–1985 boom (3,897 permits) → 1986–95 collapse (1,491) → 2006–15 mini-rebound (3,137) → 2016–25 secondary rollover (2,411) vs Reeves 480 → 13,757 / Loving 537 → 9,058 / Upton 1,663 → 11,057 over same 50-yr arc.
- **Older deploys (24 entries, Chats 124 → 102):** archived to git history. Recover with `git log --merges --grep "deploy [0-9a-f]" main` or read merge commit messages. Operationally relevant detail (drilling_permit_density warm-data resurrection path, ERCOT queue Stage 1+2 match rates, ERCOT no-deploy slots 115/116/117) lives in `## Sprint queue` and `## Open backlog`.
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
