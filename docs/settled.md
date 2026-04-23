# Settled Decisions

Never re-ask. Never re-litigate. If a decision lives here, it's final. Revisit only if the ground shifts materially (new data source appears, platform constraint lifts, thesis pivots).

Append only. Do not rewrite history. If a decision is overturned, strike it through, add the reversal below with date and reason.

---

## Architecture & build

**Option B: prebuilt PMTiles for large GeoJSON.** Layers whose source GeoJSON exceeds ~10 MB bypass project-knowledge ingestion entirely. Pre-built `.pmtiles` files are checked in as binary to the repo, or resolved at build time from one of three tiers: (1) `/mnt/project/<id>.pmtiles`, (2) `/mnt/user-data/uploads/<id>.pmtiles`, (3) `https://lrp-tx-gis.netlify.app/tiles/<id>.pmtiles`. `layers.yaml` flags these with `prebuilt: true`. `build.py` skips tippecanoe for these layers and copies the PMTiles through. First applied to `parcels_pecos` (Chat 41–42).

**Flat data layout at repo root.** All `points_*.csv`, `geoms_*.geojson`, `deal_*.geojson`, `combined_*.{csv,geojson}` files live flat at the repo root. No nested `data/` folder. Rationale: every existing `build.py` and doc path would break with subfolders, and the flat layout already works. Revisit only if file count exceeds ~50.

**Single `layers.yaml` config.** Adding a layer = one yaml append. `build.py` and `build_template.html` are never modified as part of a layer addition. Styling tweaks (color, default_on, min_zoom, popup fields, radius, labels, groups) are yaml edits only.

**Full rebuild every chat.** Container resets between chats; there is no incremental-build state to preserve. The full rebuild is the accepted cost of the isolation model. Each shipping chat emits `dist/index.html` + `dist/tiles/*.pmtiles`.

**Data files never read into Claude's context.** CSVs and GeoJSONs stream through tippecanoe subprocesses only. Reading them into context for model inspection burns tokens and produces nothing useful. Enforced in `GIS_SPEC.md` Hard Rule #1.

---

## Deploy

**PMTiles deploys via proxy bash, not MCP.** Netlify MCP `deploy-site` returns a one-time-token proxy URL; actual deploy runs locally via `npx @netlify/mcp`. File sizes exceed MCP inline limits. Pattern: MCP call → CLI proxy command → retry on 503 with ~45–75s CDN warm-up window.

**Never deploy to prod if build report shows `errored > 0`.** Stop and report. No exceptions.

---

## GitHub sync

**Clone-push bracket for shipping sessions** (established Chat 48). First bash call: `git clone --depth=1` into `/home/claude/repo/`. Last bash call before final response: `git add -A && git commit && git push`. No-op if no changes. Push-reject fallback = `git pull --rebase && git push` once; still rejected → halt, report, leave repo in detached state.

**Git Data API tree commit for doc-only edits** that don't need tooling. No clone required. Reduces tool-call budget for small doc changes.

**Main branch direct commit.** No PR workflow for routine GIS chats. Branch + PR workflow applies only when explicitly scoped (e.g., structured refinement sequences).

**PAT in gitignored `/mnt/project/CREDENTIALS.md`.** Never in userMemories. Never in repo history. Fine-grained single-repo scope, `contents: read/write` only. Classic PAT with `repo` scope acceptable.

**No Git LFS.** Revisit if any single file >50 MB. Current max: `combined_points.csv` at ~4.5 MB.

---

## Scoped-out data sources

**`rrc_wells_permian` excluded** (Chat 53 decision). RRC MFT portal (`mft.rrc.texas.gov`) is GoAnywhere PrimeFaces AJAX — no direct-URL path for bulk downloads. Re-scope would require either manual browser-downloads of 12 Permian-county shapezips or implementing an AJAX downloader. Neither is worth the cost given the per-county fetching overhead.

**Per-county / per-chunk fetching is a data-source-shape problem.** There is no workflow fix. Sources that require per-county iteration at fetch time (e.g., RRC MFT) are scoped out by default unless a bulk endpoint is discovered.

---

## Newsletter (Grid Wire)

**Structure locked:** 8 sections + LRP appendix + Blackstone QTS standing section + Transactions & Comps section. Volume-numbered, dated. Weekly cadence.

**Write-first approach.** Targeted gap-fill searches only. Broad parallel pre-loading exhausts context before synthesis.

**Voice:** Munger / Sanders / Burry register — dry, declarative, contrarianism implicit, short sentences, minimal adjectives. ≤3 hashtags per LinkedIn post.

---

## Operating cadence

**One chat = one operation.** Build, refresh, add-layer, doc update — each is a separate chat. Sequential operation is architecturally correct for this workload.

**Trigger phrases optional.** `build.`, `refresh X.`, `add layer...` remain valid shipping-classifier inputs. Natural-language shipping prompts also route correctly. Operator picks whichever is faster to type.

---

## Data sources

**EIA-860 capacity lives in the Generator sheet, not the Plant sheet.** `2___Plant_Y<year>.xlsx` contains plant metadata only (location, utility, status, no capacity). Nameplate capacity, Technology, Prime Mover, and Energy Source are in `3_1_Generator_Y<year>.xlsx` at generator level. To populate plant-level capacity: group generators by `Plant Code`, filter `Status == 'OP'`, sum `Nameplate Capacity (MW)`. Mode of `Technology` and `Energy Source 1` give plant-level fuel/tech labels. With EIA-860 2024 release, this join covers **891/1,367 of our `eia860_plants` rows (65.2%)**, total 178,542 MW. Coverage scales with release vintage (2023 gave 58.7%). The remaining ~35% are retired, sub-threshold, or post-2024 additions. Discovered Chat 74.

**EIA-860 annual zip fetch requires `Referer` header.** Direct `curl` to `https://www.eia.gov/electricity/data/eia860/xls/eia860<YYYY>.zip` returns HTTP 503 (18-byte body). With `-H 'Referer: https://www.eia.gov/electricity/data/eia860/'` and `-A 'Mozilla/5.0'`, same URL returns 200 + full zip. Archive-path URLs (`/archive/xls/`) return 200 without the header but serve older vintages only. Current-release URLs require the Referer. Confirmed Chat 74 with 2024 release (22 MB zip).

**EIA-860M monthly is HTML-only landing page.** URL pattern `eia.gov/electricity/data/eia860m/` returns a landing page, not a zip. Use annual releases for bulk capacity/technology/fuel data. Monthly releases are not a drop-in replacement. Previously confirmed in GIS_SPEC.md; re-confirmed Chat 74.

**`combined_points.csv` capacity is fragmented across four columns by source layer.** `eia860_battery.capacity` (MW), `ercot_queue.mw` (MW), `solar.capacity_mw` (MW), `wind.cap_kw` (kilowatts, needs /1000), `tceq_gas_turbines.capacity_mw` (MW). No single canonical column covers all generation layers. Single-column queries (filters, MW-driven icon sizing, fleet totals) require coalescing into `capacity_mw` with wind unit-conversion. Original source columns retained in CSV for provenance; popups/filters shifted to `capacity_mw` after coalesce. Audit established Chat 74; execution pending.

**User-uploaded `combined_points.csv` (2026-04-23) is equivalent to repo pre-TCEQ state.** Row count identical per layer (39,409 rows, 9 layers). Column population rates identical. 31 rows differ by `(lat, lon)` key but are the same entities (matched 31/31 on `name` for tpit_subs, `osm_id` for wind, `plant_code` for eia860_plants) — difference is float serialization only (`32.5028` vs `32.502800`, `28` vs `28.0`). No new data to merge. Repo version remains canonical. Decision: no merge; enhancement opportunity is the capacity coalesce and EIA-860 Generator-sheet join, not row-level merging from uploaded file.

**Comptroller Ch. 312 / 381 / 313 search databases are JavaScript-gated with multi-month reporting lag.** `comptroller.texas.gov/economy/development/search-tools/ch312/abatements-simple.php` returns literal "Error Loading Page" to static `curl` — same failure mode as RRC MFT GoAnywhere portal. Plus biennial/annual reporting lag makes registry records trail actual filings by 12–24 months. **Canonical leading signal is county commissioners-court agendas + public-notices pages** (Tax Code §312.207(d) requires ≥30 days notice before abatement vote, with applicant, site description, anticipated improvements, estimated cost). Comptroller Local Development Agreements DB (Ch. 380/381/312 union) excluded on same grounds — no material uplift over commissioners-court scrape. Discovery 2026-04-23 per `docs/refinement-abatement-spec.md`.

**Ch. 313 expired 12/31/2022; Ch. 403/JETI (eff 1/1/2024) excludes renewables.** JETI statute bars "non-dispatchable electric generation facility or electric energy storage facility" — solar, wind, standalone BESS explicitly out. Active renewable abatement mechanisms are Ch. 312 (city/county) and Ch. 381 (county economic development agreements). Fixed in spec 2026-04-23; do not re-cite Ch. 313 or JETI as active renewable pathways.

**TCEQ sources closed 2026-04-23.** `tceq_gas_turbines` shipped via bulk `turbine-lst.xlsx` (Chat 75b deploy `69ea32c7d3733641c9a1bb7c`, 6 features, 23-county West-TX scope). `tceq_pws` dropped (HTTP 400 on original endpoint, operator decision). `tceq_pbr` and `tceq_nsr_pending` scoped out (CRPUB HTML-scrape authorization declined — same failure class as RRC MFT GoAnywhere). Nominatim fallback accepted for Census geocoder zero-match (1.1s throttle). Standing watch item: TCEQ diesel-genset NSR permits live only in CRPUB; gap for data-center backup-power intelligence. Revisit only if TCEQ publishes bulk feed or operator authorizes CRPUB scrape.

**Netlify prod URL requires real User-Agent on curl verification.** `curl https://lrp-tx-gis.netlify.app/` with default `curl/x.y.z` UA returns HTTP 503 even when deploy `state=ready` and tiles are live. Adding `-A "Mozilla/5.0"` returns 200. Bot-blocking heuristic on the Netlify edge. Post-deploy verification pattern is `curl -sI -A "Mozilla/5.0"` on both root and one tile endpoint. Confirmed Chat 75b.
