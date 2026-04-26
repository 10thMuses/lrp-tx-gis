# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat

**Chat 100 — MOBILE-FRIENDLY MAP (sprint stage 1 of 2–3).** Per operator reprioritization 2026-04-26, mobile work moves ahead of DC auto-refresh cron and all abatement workstreams. First chat of the sprint sets up responsive breakpoints + touch-friendly controls; subsequent chats handle pinch-zoom tuning, measure tool + print-to-PDF mobile usability, and popup sizing.

### Task

1. Add mobile breakpoint at 768 px in `build_template.html`. Sidebar collapses to a bottom sheet or off-canvas drawer below breakpoint; map fills viewport.
2. Touch-friendly controls: increase tap targets to ≥44 px (WCAG); ensure layer toggles, filter chips, and the print/export buttons remain reachable on small viewports.
3. Popup sizing: cap popup max-width at `min(90vw, 360px)` on mobile; verify long-text fields (e.g. `power_source` on `dc_anchors`, `legal_desc` on `parcels_pecos`) scroll inside the popup rather than overflowing the viewport.
4. Smoke-test on a mobile UA via curl + render check; defer pinch-zoom tuning, measure-tool mobile, and print-to-PDF mobile to Chat 101 (sprint stage 2).
5. Standard build → preview → prod sequence per §8.
6. WIP next-chat = Chat 101 (mobile sprint stage 2: pinch-zoom + measure tool + print-mobile).

### Acceptance

- `index.html` includes a `@media (max-width: 768px)` block governing sidebar layout, control sizing, and popup max-width.
- Tap targets ≥44 px below breakpoint (verifiable via inspecting `min-height` / `min-width` declarations on `.layer-toggle`, `.filter-chip`, `#btn-print`, etc.).
- `built=26 missing=0 errored=0` on final build line.
- Local↔prod md5 identical post-deploy.
- Branch merged + deleted same chat per §6.12.

### Branch

`refinement-chat100-mobile-1`.

### Pre-flight

- Chat 99 shipped clean. `dc_anchors` layer live on prod (deploy `69ed6743f0d200d1782b60e7`). Layer count 26.
- DC auto-refresh cron deferred per operator priority change. Sub-sequence research ✓ (Chat 98) → build ✓ (Chat 99) → auto-refresh **paused at queue position 4** (after mobile sprint + ERCOT aggregation popup).
- Known close-out script gap: `scripts/close-out.sh` fails on missing git identity in fresh containers. Workaround = `git config user.email "claude@anthropic.local" && git config user.name "Claude"` before `close-out.sh`. Structural fix (move into `session-open.sh`) deferrable; track as backlog item.
- Tool budget for mobile stage 1 with deploy: 6–8 (template patch + build + Netlify proxy + verify + WIP write + close-out). All edits in `build_template.html`; no `build.py` or `layers.yaml` touch needed.
- Reference: existing template uses Tailwind-style utility classes inline + scoped `<style>` block. Add mobile rules in the existing `<style>` block, not a new file.

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### MOBILE-FRIENDLY MAP — STAGES 2–3

Continuation of the mobile sprint started at Chat 100. Stage 2 (Chat 101): pinch-zoom tuning, measure-tool mobile usability, print-to-PDF mobile usability. Stage 3 (Chat 102, if needed): polish + cross-device QA. 1–2 chats remaining after Chat 100.

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
- Last published deploy: `69ed6743f0d200d1782b60e7` (Chat 99, 2026-04-26). State=ready. Adds `dc_anchors` layer (Projects group): 8 Texas datacenter anchor points from `data/datacenters/dc_anchors.json` via custom JSON loader (`dc_anchors_to_ndgeojson` in `build.py`). Symbology: graduated radius on `capacity_mw_announced` (mw mode); status-keyed circle color via `dcAnchorsColorExpr()`; `coord_accuracy=county_centroid` dimmed to 0.45 opacity via `dcAnchorsOpacityExpr()`. Build clean: `built=26 missing=0 errored=0 tiles_total=18865 KB`. Local↔prod md5 identical (index `efc81b2a01cffb1f20793a72a4b8180d`, dc_anchors.pmtiles `7d8c6243bdb2c7088c930aee624336c5`).
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

**Infrastructure:**
- `NETLIFY_PAT` absent from `CREDENTIALS.md`. Netlify MCP proxy path canonical
- `GITHUB_PAT` can push branches, 403 on PR creation. Direct-merge-to-main is the protocol (OPERATING.md §9)
- **Akamai datacenter-egress block on `reevescounty.org`** — cloud-runner / GitHub-Actions traffic 403s regardless of UA / TLS fingerprint. Hard prerequisite for the abatement-weekly-cron sprint item. Unblock options: residential-proxy egress (paid), Akamai allowlisting via Reeves County IT (low likelihood), search-API result pages

**Process:**
- Chat 92 §6.12 violation (deploy + merge atomic): published deploy `69ed2cdf4039c554a1316ad2` to prod but deferred close-out merge, citing scope-creep. Reconciled in Chat 93 (merge `3a59a73`). Root cause: doc-restructure work appeared on a feature branch alongside the data-layer work, blowing past §6.13 stage-fits-one-chat. Preventive structural fix: pre-commit hook could reject doc-structure changes on `refinement-*` branches; lower-effort alternative is operator-side discipline at branch-naming time.

**Outstanding credential hygiene:**
- `GITHUB_PAT` leak from Chat 87 unrotated per operator override. Token valid until 2027-04-21

**Permanently excluded:** see ARCHITECTURE.md §11

**Other (non-GIS):** Grid Wire Vol. 7. Tier 2 water availability assessments. Excel returns model.
