# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat

**Chat 102 — ERCOT QUEUE PROJECT AGGREGATION POPUP.** `ercot_queue` has 1,205 distinct project `group` keys; 394 groups have 2+ components. Build-time aggregation (totals + breakdown per group) plus popup template change to render group summary above per-row detail.

### Task

1. **Aggregation in `build.py`.** Read `combined_points.csv` rows where `layer_id == ercot_queue`. Group by the `group` field. Compute per-group: `group_total_mw` (sum of `capacity_mw`), `group_count` (row count), `group_breakdown` (newline-joined or JSON-encoded list of component lines: `<project_name> · <capacity_mw> MW · <county>`). Stamp these fields onto every queue row so each feature carries its group's aggregates.
2. **Atomic in-place write per §6.15.** Use temp-file + `os.replace` for the combined-csv rewrite.
3. **Popup template in `build_template.html`.** Conditional render: if `group_count > 1`, prepend a summary block above the per-row fields ("Group total: X MW across Y projects") followed by `group_breakdown` as a list. Test case Longfellow__Pecos: 6 rows, 2,153.3 MW expected.
4. **`layers.yaml` schema.** Register the three new fields under `ercot_queue.popup_fields` if the template reads them via the registry, OR confirm pass-through via the catch-all popup loop.
5. Standard build → preview → prod per §8.
6. WIP next-chat = Chat 103 (DC auto-refresh cron, blocked on Anthropic API key in repo secrets; Andrea must add via GitHub UI before that chat. If still blocked, jump to abatement workstreams).

### Acceptance

- `combined_points.csv` `ercot_queue` rows carry `group_total_mw`, `group_count`, `group_breakdown` populated for all 1,205 group keys.
- Popup on a group-2+ feature renders summary + breakdown above the per-row detail.
- Longfellow__Pecos popup: 2,153.3 MW total across 6 components.
- `built=26  missing=0  errored=0`.
- Local↔prod md5 identical post-deploy.
- Branch merged + deleted same chat per §6.12.

### Branch

`refinement-chat102-ercot-aggregation`

### Pre-flight

- Chat 101 shipped clean. Mobile stage 2 live on prod (deploy `69edeb7d83b23c994ffd00ed`). Layer count 26. CSS+JS-only patch, no PMTiles regenerated. Local↔prod md5 `3945461c8f188881ab029d93a787d943`. Mobile stage 2 acceptance: gesture rotation disabled below 768 px via matchMedia listener (re-enables past breakpoint); measure-vertex circle-radius 4→12 on mobile via setPaintProperty + initial radius from `_mqMobile.matches`; `.measure-readout` repositions to right edge when drawer open and exposes a × close button on mobile that delegates to existing measureBtn toggle; `#btn-print` collapses drawer on mobile before `window.print()` and restores via `afterprint`.
- Mobile stage 3 (polish + cross-device QA) was sprint-listed as optional. Folded into hotfix-on-demand: if Andrea surfaces issues in real-device testing, those become discrete patch chats; no scheduled stage 3.
- Sprint queue: ERCOT aggregation (this chat) → DC auto-refresh cron (paused at queue position 4 — needs API key) → abatement workstreams.
- Tool budget for aggregation chat with deploy: 6–8 (build.py aggregation helper + template popup edit + build with `ercot_queue` PMTiles regen + Netlify proxy + verify + WIP write + close-out). `ercot_queue` is the only PMTiles needing regen; rest stay prebuilt.
- Reference: aggregation logic likely belongs alongside `merge_csv` or as a separate `aggregate_ercot_groups` helper in `build.py`. Confirm whether the `group` field is already canonicalized in `combined_points.csv` or computed at build time. Group keying (e.g. `Longfellow__Pecos`) is the existing project-grouping algorithm output — verify field name is literal `group`.
- Known close-out script gap: `scripts/close-out.sh` fails on missing git identity in fresh containers. Workaround = `git config user.email "claude@anthropic.local" && git config user.name "Claude"` before `close-out.sh`. Structural fix (move into `session-open.sh`) deferrable; backlog item.
- Known build dep gap in fresh containers: `cairosvg` (pip) and `tippecanoe` (apt) not preinstalled. Resolve with `pip install cairosvg --break-system-packages && apt-get install -y tippecanoe` before `python3 build.py`. Structural fix (add to `session-open.sh`) deferrable; backlog item.

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### DC AUTO-REFRESH CRON

`.github/workflows/dc-anchors-refresh.yml`. Cron `0 6 * * 1`. Refresh script in `scripts/refresh_dc_anchors.py` reads existing `dc_anchors.json` + watchlist URL feed; LLM-in-the-loop parser proposes diffs (status changes, capacity revisions, new entries flagged `single_source: true`); diffs surface as PR for human review (never auto-merged). **Hard prerequisite:** Anthropic API key in repo secrets — operator must add via GitHub UI; PAT lacks scope. 1 chat once unblocked.

### ABATEMENT PERMIAN-CORE + PERIPHERAL

Permian-core (Andrews, Ector, Glasscock, Loving, Martin, Midland, Ward, Winkler) → peripheral (Crane, Crockett, Irion, Reagan, Schleicher, Sutton, Upton) county scrape sequence. 4–6 chats. **Hard constraint:** CivicEngage/Akamai bot-block on `reevescounty.org` extends to any county on the same CMS hosting platform — adapter fixes verifiable only after residential-proxy or whitelisted egress provisioned. Detail in `docs/sprint-plan.md`.

### COMPTROLLER LDAD SCRAPE

Supersedes prior "operator manual XLSX download" ask. There is no bulk XLSX. Canonical source: `https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`. Blocked pending operator authorization for JS-rendered scrape (Selenium / Playwright — same authorization class as CRPUB / RRC MFT). Until authorized: backstop only.

### ABATEMENT WEEKLY CRON

`.github/workflows/abatement-scrape.yml`. Cron weekly Monday 06:00 UTC. Commit diff to `data/abatements/abatement_hits_latest.csv` + rolling history. **Hard prerequisite:** `reevescounty.org` Akamai block must be resolved before cron ships, otherwise Reeves silently produces 0 hits.

### MOBILE STAGE 3 — HOTFIX ON DEMAND

Cross-device QA + polish for the mobile-friendly map work shipped in Chats 100–101. Not scheduled. Surfaced issues become discrete patch chats. 0–1 chat per issue.

---

## Prod status

- Layer count: **26**
- Last published deploy: `69edeb7d83b23c994ffd00ed` (Chat 101, 2026-04-26). State=ready. Mobile stage 2: gesture + measure tool + print handler. Two-finger rotate disabled below 768 px via `matchMedia` listener (`map.touchZoomRotate.disableRotation()` + `map.dragRotate.disable()` on mobile, `.enableRotation()`/`.enable()` past breakpoint); measure-vertex `circle-radius` 4→12 on mobile (initial value from `_mqMobile.matches` in `ensureMeasureLayers`, dynamic update via `setPaintProperty` in the matchMedia handler); `.measure-readout` repositions to right edge when drawer is open on mobile and exposes a × close button that delegates to the existing measureBtn toggle; `#btn-print` handler force-collapses the drawer on mobile before `window.print()` and restores via `afterprint`. Build clean: `built=26  missing=0  errored=0  tiles_total=18865 KB`. Local↔prod md5 identical (index `3945461c8f188881ab029d93a787d943`). CSS+JS-only — no PMTiles regenerated. iPhone-UA serves identical bundle (no UA-routed variants).
- Previous deploy: `69ede86f9d6157312033e693` (Chat 100, 2026-04-26). Mobile stage 1: 768 px breakpoint, off-canvas drawer at `min(86vw, 320px)`, ≥44 px tap targets on `.topbar button`, `.layer`, `.filter-multi > summary`, `.basemap-picker select`, `.maplibregl-ctrl-group button`. Popup max-width capped at `min(90vw, 360px)` with `max-height: 60vh; overflow-y: auto` and `word-break: break-word`.
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
- Fresh-container build deps: `cairosvg` (pip) and `tippecanoe` (apt) not preinstalled. Workaround documented in Pre-flight; structural fix = add install steps to `session-open.sh` if recurring (now confirmed recurring across Chats 100 and 101 — promote to active fix in Chat 102 or 103).

**Process:**
- Chat 92 §6.12 violation (deploy + merge atomic): published deploy `69ed2cdf4039c554a1316ad2` to prod but deferred close-out merge, citing scope-creep. Reconciled in Chat 93 (merge `3a59a73`). Root cause: doc-restructure work appeared on a feature branch alongside the data-layer work, blowing past §6.13 stage-fits-one-chat. Preventive structural fix: pre-commit hook could reject doc-structure changes on `refinement-*` branches; lower-effort alternative is operator-side discipline at branch-naming time.
- Chat 100 §6.12 deviation: deploy + merge were not atomic in the same chat — deploy `69ede86f9d6157312033e693` shipped, branch pushed, but merge to main + WIP rewrite ran in the operator-prompted close-out turn. Cause: tool-budget exhausted on build dep installs (cairosvg, tippecanoe) before merge step. Preventive fix tracked in Open backlog → Infrastructure (preinstall in `session-open.sh`).
- Chat 101 §6.12 compliant: deploy + merge atomic in single shipping flow.

**Outstanding credential hygiene:**
- `GITHUB_PAT` leak from Chat 87 unrotated per operator override. Token valid until 2027-04-21

**Permanently excluded:** see ARCHITECTURE.md §11

**Other (non-GIS):** Grid Wire Vol. 7. Tier 2 water availability assessments. Excel returns model.
