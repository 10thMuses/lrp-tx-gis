# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat`** = task spec for the immediately-next shipping chat. **`## Sprint queue`** = N+2 and beyond. Multi-step sprint detail lives in `docs/sprint-plan.md` (deleted per item when shipped).

---

## Next chat

**Chat 97 — LEGEND ON PRINT/SHARE/PDF.** Promoted from sprint queue. Sidebar carries the legend in screen mode but is hidden by `@media print` in `build_template.html`, so prints/PDFs ship legend-less. Inject a print-only legend element enumerating only the active (toggled-on) layers — name + color swatch + symbol — into the print page.

### Task

1. Recon `build_template.html` `@media print` block + sidebar markup to identify the exact selectors hiding the legend and the available print real estate.
2. Add a print-only `<div id="print-legend">` (hidden in screen, shown in print) populated client-side from the same layer-state that drives the sidebar — only layers currently `default_on=true` OR toggled on by the user at print time.
3. Style: layer name + color swatch (12px box matching layer `color`) + geometry symbol (point dot / line dash / polygon outline). Two-column flex grid in the print footer or a dedicated final page. Must fit landscape 10.3"×7.1" with ≥15 active layers (multi-column or multi-page wrap).
4. `build. deploy to prod.` Verify by curling prod, opening print-preview locally on `dist/index.html`, and confirming the legend renders with at least the default-on layers.
5. Atomic close-out per §5 / §6.12.

### Acceptance

- Print preview of prod URL shows a visible legend listing every currently-active layer with name + color swatch + symbol matching its on-map style.
- Screen view is visually unchanged (no new sidebar element, no layout shift).
- ≥15 active layers wraps without overflow off the page.
- Build errored=0, layer count=25, deploy state=ready.
- Branch merged + deleted same chat per §6.12.

### Branch

`refinement-chat97-print-legend`.

### Pre-flight

- Chat 96 closed clean, deploy `69ed5ab2b573b4ee0b052773` (2026-04-26). 5 layer popup specs (`eia860_plants`, `eia860_battery`, `solar`, `wind`, `ercot_queue`) shipped with `commissioned` / `operator` / `capacity_mw` / `fuel` / `technology` per field contract; `sector` removed from all five (the 3 remaining `sector` hits in prod HTML are in `tax_abatements.popup_labels` → "Taxing entities", out of scope). Prod md5 matched local dist: `22be6d63c665968c3a843cd67d183ec3`.
- This is `build_template.html` work — touching the file directly is OK (it is the template, not a layer addition; §6 rule 7 does not apply).
- Color swatch source: `LAYERS_CONFIG[i].color` already in template scope. Geometry symbol can be derived from `LAYERS_CONFIG[i].geom` (`point` | `line` | `polygon`) — no new data plumbing.
- Active-layer set already exists in client state (whatever drives the sidebar checkboxes). Reuse, do not re-derive.
- Build deps: `pip install --break-system-packages cairosvg openpyxl pyyaml` before `python3 build.py` (build_sprite hard-imports cairosvg at module top). `tippecanoe` via `apt-get install -y tippecanoe` if cold.
- Tool-call budget: 8. recon (1), template edit (1), build (1), deploy MCP + npx (2), poll + verify (1), close-out (1). Reserve 1 for blocker recovery.

---

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### ABATEMENT PERMIAN-CORE + PERIPHERAL

Permian-core (Andrews, Ector, Glasscock, Loving, Martin, Midland, Ward, Winkler) → peripheral (Crane, Crockett, Irion, Reagan, Schleicher, Sutton, Upton) county scrape sequence. 4–6 chats. **Hard constraint:** CivicEngage/Akamai bot-block on `reevescounty.org` extends to any county on the same CMS hosting platform — adapter fixes verifiable only after residential-proxy or whitelisted egress provisioned. Detail in `docs/sprint-plan.md`.

### COMPTROLLER LDAD SCRAPE

Supersedes prior "operator manual XLSX download" ask. There is no bulk XLSX. Canonical source: `https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`. Blocked pending operator authorization for JS-rendered scrape (Selenium / Playwright — same authorization class as CRPUB / RRC MFT). Until authorized: backstop only.

### ABATEMENT WEEKLY CRON

`.github/workflows/abatement-scrape.yml`. Cron weekly Monday 06:00 UTC. Commit diff to `data/abatements/abatement_hits_latest.csv` + rolling history. **Hard prerequisite:** `reevescounty.org` Akamai block must be resolved before cron ships, otherwise Reeves silently produces 0 hits.

### LEGEND ON PRINT / SHARE / PDF

*(Promoted to Chat 97 — see `## Next chat`.)*

### DC RESEARCH → DC BUILD → DC AUTO-REFRESH

3-chat sub-sequence. Research anchors: Longfellow/Poolside (Pecos), Stargate (Abilene), Project Matador/Fermi → structured data file → layer build → GitHub Actions weekly refresh with LLM-in-the-loop parser. Detail in `docs/sprint-plan.md`.

### MOBILE-FRIENDLY MAP

Responsive breakpoints, touch-friendly controls, pinch-zoom tuning, measure tool + print-to-PDF mobile usability, popup sizing. 2–3 chats.

### ERCOT QUEUE PROJECT AGGREGATION POPUP  *(low priority)*

`ercot_queue` has 1,205 distinct project `group` keys; 394 groups have 2+ components. Build-time aggregation in `build.py`: compute `group_total_mw`, `group_count`, `group_breakdown` per group; popup template renders summary line + breakdown list. Test case Longfellow__Pecos: 6 rows, 2,153.3 MW total.

---

## Prod status

- Layer count: **25**
- Last published deploy: `69ed5ab2b573b4ee0b052773` (Chat 96, 2026-04-26). State=ready. Carries popup+filter redesign for the 5 power-related layers (`eia860_plants`, `eia860_battery`, `solar`, `wind`, `ercot_queue`): `sector` removed; `operator` / `commissioned` / `capacity_mw` / `fuel` / `technology` surfaced per field contract. Build clean: `built=25 missing=0 errored=0 tiles_total=18816 KB`. Local↔prod md5 identical (`22be6d63c665968c3a843cd67d183ec3`); Netlify upload deduped against Chat 95 PMTiles (data unchanged, template-only delta).
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
