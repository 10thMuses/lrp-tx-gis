# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat`** = task spec for the immediately-next shipping chat. **`## Sprint queue`** = N+2 and beyond. Multi-step sprint detail lives in `docs/sprint-plan.md` (deleted per item when shipped).

---

## Next chat

**Chat 100 — DC AUTO-REFRESH CRON: GitHub Actions weekly refresh of dc_anchors with LLM-in-the-loop parser.** Third and final of the DC sub-sequence (research ✓ Chat 98 → layer build ✓ Chat 99 → auto-refresh). Stand up `.github/workflows/dc-anchors-refresh.yml` cron weekly Mondays 06:00 UTC, scraping the per-entry `sources[*].url` plus a watchlist of TX datacenter trade-press feeds; LLM-in-the-loop parser proposes diffs against `data/datacenters/dc_anchors.json`; diffs surface as a PR for human review (never auto-merged).

### Task

1. Create `.github/workflows/dc-anchors-refresh.yml`. Cron `0 6 * * 1`. Manual trigger via `workflow_dispatch`.
2. Refresh script in `scripts/refresh_dc_anchors.py` (new). Inputs: existing `dc_anchors.json` + watchlist URL feed. Outputs: proposed diff JSON to stdout + write candidate `dc_anchors.json.proposed`.
3. LLM-in-the-loop parser path: prompt template stored in repo (`scripts/dc_anchors_parser_prompt.md`); workflow calls Anthropic API (key in repo secrets) with current entries + scraped article excerpts; parser returns structured diff (`status_change`, `capacity_revision`, `new_entry`, `accessed_bump`).
4. PR-creation step: workflow opens PR with diff summary in body. New entries flagged `single_source: true` until reviewer adds a second source. `accessed` dates bump only on confirmation.
5. Acceptance protocol for first run: dry-run via `workflow_dispatch`, inspect proposed diff manually, do NOT merge unless plausible. Cron only goes live after one successful manual dry-run.
6. WIP next-chat = backlog from `## Sprint queue` ordering at that time; ABATEMENT PERMIAN-CORE if Akamai unblock has landed by then, else MOBILE-FRIENDLY MAP or COMPTROLLER LDAD SCRAPE per operator priority.

### Acceptance

- `.github/workflows/dc-anchors-refresh.yml` exists, syntax-valid (`gh workflow view` clean).
- Manual `workflow_dispatch` run completes without error; output PR created with at least an `accessed` date bump on one entry (smoke test).
- Anthropic API key added to repo secrets (operator action; ask pattern per OPERATING.md §2).
- Cron scheduled but tested only via `workflow_dispatch` — do not wait for first scheduled run.
- Branch merged + deleted same chat per §6.12.

### Branch

`refinement-chat100-dc-cron`.

### Pre-flight

- Chat 99 shipped clean. `dc_anchors` layer live on prod with 8 features. Local↔prod md5 identical (`efc81b2a01cffb1f20793a72a4b8180d` index, `7d8c6243bdb2c7088c930aee624336c5` pmtiles). Build clean: `built=26 missing=0 errored=0 tiles_total=18865 KB`.
- Symbology shipped: graduated radius via SIZING_RULES (mw mode); status color (announced=slate `#94a3b8`, permitted=amber `#f59e0b`, under_construction=blue `#0ea5e9`, operational=green `#16a34a`); coord_accuracy=county_centroid dimmed to 0.45 opacity. Wired in `build_template.html` via `dcAnchorsColorExpr()` + `dcAnchorsOpacityExpr()` + extension of the `layerPaint` per-id dispatcher (was ercot_queue-only, now ercot_queue + dc_anchors).
- Popup uses standard `popup_labels` rendering — sources surfaced as `sources_count` (int) and `sources_urls` (newline-joined string). Custom expandable-footer popup not implemented (kept Rule 7 minimization). If operator wants per-URL link rendering, that's a follow-up template patch via `dcAnchorsPopupHtml(props)` mirroring `ercotQueuePopupHtml`.
- Filter fields: `status` (categorical), `county` (categorical), `capacity_mw_announced` (numeric), `developer` (text), `name` (text).
- Hard prerequisite for cron: Anthropic API key added to repo secrets. Operator must add via GitHub UI; PAT in `CREDENTIALS.md` lacks repo-secrets-write scope.
- Tool budget for cron stand-up: 4–8 (workflow yaml + refresh script + parser prompt + first dry-run + WIP write + close-out).

---

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### ABATEMENT PERMIAN-CORE + PERIPHERAL

Permian-core (Andrews, Ector, Glasscock, Loving, Martin, Midland, Ward, Winkler) → peripheral (Crane, Crockett, Irion, Reagan, Schleicher, Sutton, Upton) county scrape sequence. 4–6 chats. **Hard constraint:** CivicEngage/Akamai bot-block on `reevescounty.org` extends to any county on the same CMS hosting platform — adapter fixes verifiable only after residential-proxy or whitelisted egress provisioned. Detail in `docs/sprint-plan.md`.

### COMPTROLLER LDAD SCRAPE

Supersedes prior "operator manual XLSX download" ask. There is no bulk XLSX. Canonical source: `https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`. Blocked pending operator authorization for JS-rendered scrape (Selenium / Playwright — same authorization class as CRPUB / RRC MFT). Until authorized: backstop only.

### ABATEMENT WEEKLY CRON

`.github/workflows/abatement-scrape.yml`. Cron weekly Monday 06:00 UTC. Commit diff to `data/abatements/abatement_hits_latest.csv` + rolling history. **Hard prerequisite:** `reevescounty.org` Akamai block must be resolved before cron ships, otherwise Reeves silently produces 0 hits.

### MOBILE-FRIENDLY MAP

Responsive breakpoints, touch-friendly controls, pinch-zoom tuning, measure tool + print-to-PDF mobile usability, popup sizing. 2–3 chats.

### ERCOT QUEUE PROJECT AGGREGATION POPUP  *(low priority)*

`ercot_queue` has 1,205 distinct project `group` keys; 394 groups have 2+ components. Build-time aggregation in `build.py`: compute `group_total_mw`, `group_count`, `group_breakdown` per group; popup template renders summary line + breakdown list. Test case Longfellow__Pecos: 6 rows, 2,153.3 MW total.

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
