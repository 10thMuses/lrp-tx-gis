# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat

**Chat 101 — MOBILE-FRIENDLY MAP (sprint stage 2 of 2–3).** Continuation of the mobile sprint started Chat 100. Stage 1 shipped: 768 px breakpoint, off-canvas drawer, ≥44 px tap targets on primary controls, popup max-width capped at `min(90vw, 360px)` with overflow scroll. Stage 2 covers the gesture + tool surfaces deferred from Chat 100.

### Task

1. **Pinch-zoom tuning.** MapLibre defaults: `touchZoomRotate` and `dragRotate` both on. On phones the rotate-on-two-finger-twist surprises users and triggers the bearing indicator. Disable rotation by default below 768 px (`map.touchZoomRotate.disableRotation()` and `map.dragRotate.disable()` in a small `matchMedia` block in `build_template.html`); keep pinch-zoom enabled. Re-enable rotation if viewport widens past breakpoint.
2. **Measure tool mobile usability.** `.sb-toggle`-style entry button is reachable but the measure interaction (tap-tap-tap to add vertices) needs to (a) keep `.measure-readout` visible above the bottom sheet / drawer when sidebar is open, (b) widen vertex hit-test radius (default 4 px → 12 px on mobile), and (c) make the readout closable on mobile via a tap target inside the readout (currently it auto-clears only when measure mode is exited). Touch handler is in `build_template.html` measure-tool block.
3. **Print-to-PDF mobile usability.** Tapping `#btn-print` on mobile currently invokes `window.print()` which on iOS Safari opens the share sheet → Print Preview, but landscape `@page` may not render correctly because the print preview computes from the live mobile viewport (sidebar drawer overlay is included in capture if open). Fix: in the `btn-print` click handler, if `window.matchMedia('(max-width: 768px)').matches`, force `document.body.classList.add('sb-collapsed')` before `print()` so the drawer is hidden. Verify `@media print` block already hides `.sb-toggle` (it does, line 115) — confirm no leakage.
4. Smoke-test on mobile UA (curl `Mozilla/5.0 (iPhone…)`) — confirm rendered HTML diff vs Chat 100 prod is contained to the gesture + measure + print blocks.
5. Standard build → preview → prod sequence per §8.
6. WIP next-chat = Chat 102 (mobile sprint stage 3 if needed: polish + cross-device QA; otherwise jump to ERCOT queue project aggregation popup).

### Acceptance

- `map.dragRotate.disable()` + `map.touchZoomRotate.disableRotation()` invoked when viewport ≤768 px (and re-enabled on resize past breakpoint).
- Measure tool: vertex hit-test radius widened on mobile; `.measure-readout` has a visible close button (or equivalent dismissal) below 768 px.
- `#btn-print` handler collapses sidebar before invoking `window.print()` on mobile.
- `built=26 missing=0 errored=0` on final build line.
- Local↔prod md5 identical post-deploy.
- Branch merged + deleted same chat per §6.12.

### Branch

`refinement-chat101-mobile-2`.

### Pre-flight

- Chat 100 shipped clean. Mobile stage 1 live on prod (deploy `69ede86f9d6157312033e693`). Layer count 26. CSS-only patch — no JS, build.py, or layers.yaml touched.
- Sprint queue: mobile stage 2 (this chat) → mobile stage 3 (if needed) → ERCOT queue project aggregation popup → DC auto-refresh cron (paused at queue position 4) → abatement workstreams.
- Tool budget for mobile stage 2 with deploy: 8–10 (touches both `<style>` block and `<script>` block in `build_template.html`; gesture handler + measure tool patch + print handler patch + build + Netlify proxy + verify + WIP write + close-out). All edits in `build_template.html`; no `build.py` or `layers.yaml` touch needed.
- Reference: gesture init lives in the MapLibre `map = new maplibregl.Map(...)` block; measure tool is a separate event-handler block; print handler is at line ~974 (`document.getElementById('btn-print').addEventListener`).
- Known close-out script gap: `scripts/close-out.sh` fails on missing git identity in fresh containers. Workaround = `git config user.email "claude@anthropic.local" && git config user.name "Claude"` before `close-out.sh`. Structural fix (move into `session-open.sh`) deferrable; track as backlog item.
- Known build dependency gap in fresh containers: `cairosvg` (Python) and `tippecanoe` (apt) are not preinstalled. Resolve with `pip install cairosvg --break-system-packages && apt-get install -y tippecanoe` before `python3 build.py`. Add to `session-open.sh` if it recurs in Chat 102.

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### MOBILE-FRIENDLY MAP — STAGE 3

Polish + cross-device QA after stage 2 ships. Optional — may be folded into a routine polish chat if stages 1–2 hold up under operator testing. 0–1 chat.

### ERCOT QUEUE PROJECT AGGREGATION POPUP

`ercot_queue` has 1,205 distinct project `group` keys; 394 groups have 2+ components. Build-time aggregation in `build.py`: compute `group_total_mw`, `group_count`, `group_breakdown` per group; popup template renders summary line + breakdown list. Test case Longfellow__Pecos: 6 rows, 2,153.3 MW total. 1 chat.

### DC AUTO-REFRESH CRON

`.github/workflows/dc-anchors-refresh.yml`. Cron `0 6 * * 1`. Refresh script in `scripts/refresh_dc_anchors.py` reads existing `dc_anchors.json` + watchlist URL feed; LLM-in-the-loop parser proposes diffs (status changes, capacity revisions, new entries flagged `single_source: true`); diffs surface as PR for human review (never auto-merged). **Hard prerequisite:** Anthropic API key in repo secrets — operator must add via GitHub UI; PAT lacks scope. 1 chat once unblocked.

### ABATEMENT PERMIAN-CORE + PERIPHERAL

Permian-core (Andrews, Ector, Glasscock, Loving, Martin, Midland, Ward, Winkler) → peripheral (Crane, Crockett, Irion, Reagan, Schleicher, Sutton, Upton) county scrape sequence. 4–6 chats. **Hard constraint:** CivicEngage/Akamai bot-block on `reevescounty.org` extends to any county on the same CMS hosting platform — adapter fixes verifiable only after residential-proxy or whitelisted egress provisioned. Detail in `docs/sprint-plan.md`.

### COMPTROLLER LDAD SCRAPE

Supersedes prior "operator manual XLSX download" ask. There is no bulk XLSX. Canonical source: `https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`. Blocked pending operator authorization for JS-rendered scrape (Selenium / Playwright — same authorization class as CRPUB / RRC MFT). Until authorized: backstop only.

### ABATEMENT WEEKLY CRON

`.github/workflows/abatement-scrape.yml`. Cron weekly Monday 06:00 UTC. Commit diff to `data/abatements/abatement_hits_latest.csv` + rolling history. **Hard prerequisite:** `reevescounty.org` Akamai block must be resolved before cron ships, otherwise Reeves silently produces 0 hits.

---

## Prod status

- Layer count: **26**
- Last published deploy: `69ede86f9d6157312033e693` (Chat 100, 2026-04-26). State=ready. Mobile-friendly stage 1: `@media (max-width: 768px)` block in `build_template.html` adds (a) off-canvas drawer sidebar at width `min(86vw, 320px)`, (b) ≥44 px tap targets on `.topbar button`, `.layer`, `.filter-multi > summary`, `.basemap-picker select`, and `.maplibregl-ctrl-group button`, (c) popup max-width capped at `min(90vw, 360px)` with `max-height: 60vh; overflow-y: auto` and `word-break: break-word` on values so long-text fields (`power_source`, `legal_desc`) scroll/wrap inside the bubble. Build clean: `built=26 missing=0 errored=0 tiles_total=18865 KB`. Local↔prod md5 identical (index `b05fc7753b97b1daf00986b0e523ab8d`). CSS-only — no PMTiles regenerated.
- Previous deploy: `69ed6743f0d200d1782b60e7` (Chat 99, 2026-04-26). `dc_anchors` layer added (Projects group): 8 Texas datacenter anchor points from `data/datacenters/dc_anchors.json` via custom JSON loader (`dc_anchors_to_ndgeojson` in `build.py`). Symbology: graduated radius on `capacity_mw_announced` (mw mode); status-keyed circle color via `dcAnchorsColorExpr()`; `coord_accuracy=county_centroid` dimmed to 0.45 opacity via `dcAnchorsOpacityExpr()`.
- URL: `https://lrp-tx-gis.netlify.app` — requires real User-Agent on curl (`-A "Mozilla/5.0"`).

---

## Open backlog

**Data-pipeline gaps** (non-blocking):
- `eia860_plants`: 476/1367 rows still null `capacity_mw` (down from 529), 529/1367 null `commissioned`, 438/1367 null `technology`. EIA-860 source-side gaps; will not improve without alternate source.
- `wind`: USWTDB schema has no `operator`, `technology`, or `fuel`; structural blanks (19464/19464). `commissioned` populated for 19364/19464 (down from 0); `manu` and `model` populated. Filling operator would require joining a project-layer source (e.g. EIA-860 wind plants) — separate sprint item if pursued.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar
- BEAD `bead_fiber_planned` layer (Chat 91 §1 dropped): BDO XLSX trio archived to `data/bead_bdo/` but contains no county or coords. Three unblock paths documented in `data/bead_bdo/README.md`

**UI/UX:**
- `date_range` filter type not implemented (carryforward from Chat 92 handoff). `tax_abatements` `commissioned` filter ships as `text` multi-select over distinct ISO dates — functional with 9 rows but not a true range slider. Touches `build.py compute_filter_stats` + `build_template.html filterFieldControlHtml` + matching predicate.
- Filter inputs (`.filter-text`, `.filter-range input`) sized at 40 px on mobile (Chat 100), not strictly the 44 px WCAG bar. Acceptable per Apple HIG (≥40 px) but flag for review if operator testing surfaces hit-rate issues.

**Infrastructure:**
- `NETLIFY_PAT` absent from `CREDENTIALS.md`. Netlify MCP proxy path canonical
- `GITHUB_PAT` can push branches, 403 on PR creation. Direct-merge-to-main is the protocol (OPERATING.md §9)
- **Akamai datacenter-egress block on `reevescounty.org`** — cloud-runner / GitHub-Actions traffic 403s regardless of UA / TLS fingerprint. Hard prerequisite for the abatement-weekly-cron sprint item. Unblock options: residential-proxy egress (paid), Akamai allowlisting via Reeves County IT (low likelihood), search-API result pages
- `scripts/close-out.sh` fails on missing git identity in fresh containers. Workaround documented in Pre-flight; structural fix = move identity init into `session-open.sh`. Backlog.
- Fresh-container build deps: `cairosvg` (pip) and `tippecanoe` (apt) not preinstalled. Workaround documented in Pre-flight; structural fix = add install steps to `session-open.sh` if recurring.

**Process:**
- Chat 92 §6.12 violation (deploy + merge atomic): published deploy `69ed2cdf4039c554a1316ad2` to prod but deferred close-out merge, citing scope-creep. Reconciled in Chat 93 (merge `3a59a73`). Root cause: doc-restructure work appeared on a feature branch alongside the data-layer work, blowing past §6.13 stage-fits-one-chat. Preventive structural fix: pre-commit hook could reject doc-structure changes on `refinement-*` branches; lower-effort alternative is operator-side discipline at branch-naming time.
- Chat 100 §6.12 deviation: deploy + merge were not atomic in the same chat — deploy `69ede86f9d6157312033e693` shipped, branch pushed, but merge to main + WIP rewrite ran in the operator-prompted close-out turn. Cause: tool-budget exhausted on build dep installs (cairosvg, tippecanoe) before merge step. Preventive fix tracked in Open backlog → Infrastructure (preinstall in `session-open.sh`).

**Outstanding credential hygiene:**
- `GITHUB_PAT` leak from Chat 87 unrotated per operator override. Token valid until 2027-04-21

**Permanently excluded:** see ARCHITECTURE.md §11

**Other (non-GIS):** Grid Wire Vol. 7. Tier 2 water availability assessments. Excel returns model.
