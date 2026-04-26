# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat`** = task spec for the immediately-next shipping chat. **`## Sprint queue`** = N+2 and beyond. Multi-step sprint detail lives in `docs/sprint-plan.md` (deleted per item when shipped).

---

## Next chat

**Chat 98 — DC RESEARCH: datacenter anchor index.** First of the 3-chat DC sub-sequence (research → layer build → auto-refresh cron). Produce a structured, source-cited datacenter-anchor data file. No build, no deploy — research-and-commit only.

### Task

1. Compile a structured JSON file at `data/datacenters/dc_anchors.json` covering Texas datacenter anchors, minimum: Longfellow/Poolside (Pecos), Stargate (Abilene), Project Matador (Pecos basin), Fermi (Amarillo), plus any other large announced/under-construction TX datacenter projects surfaced via web search.
2. Per entry: `id` (slugified), `name`, `developer`, `county`, `lat`, `lon` (point or centroid; mark `coord_accuracy` ∈ `precise|approximate|county_centroid`), `status` (`announced|permitted|under_construction|operational`), `capacity_mw_announced`, `commissioned_target` (year or null), `power_source` (free text), `sources` (array of {url, accessed: ISO date, claim}). Use ≥2 sources per non-trivial field; flag single-sourced entries with `single_source: true`.
3. Schema doc at `data/datacenters/README.md`: field definitions, data-quality conventions, refresh cadence target.
4. Commit + push. No build, no deploy. WIP next-chat = Chat 99 (layer build).

### Acceptance

- `data/datacenters/dc_anchors.json` exists with ≥5 entries, schema-valid (every required field populated or explicitly null with rationale).
- Every entry has ≥1 source URL with accessed-date.
- `data/datacenters/README.md` documents schema.
- Branch merged + deleted same chat per §6.12 (no deploy means atomic-with-merge only, not deploy).
- WIP next-chat updated for Chat 99 layer build.

### Branch

`refinement-chat98-dc-research`.

### Pre-flight

- Chat 97 closed clean, deploy `69ed60e59254f7df1a9cacdb` (2026-04-26). Print-only legend shipped: `#print-legend` element + `@media print` 4-column flow + `btn-print` handler populating from `activeLayerIds()` × `LAYERS` (filtering `sidebar_omit`, preserving ERCOT-queue gradient swatch). Prod md5 = local dist md5: `d114b4e7f7b1714bff721d7d432092d6`. Build clean: `built=25 missing=0 errored=0 tiles_total=18816 KB`. Netlify upload deduped against Chat 96 PMTiles (template-only delta). One transient `npx` proxy upload error on first attempt; succeeded on retry with fresh proxy URL.
- Research-only chat — no `build.py` invocation, no Netlify call, no tippecanoe. Tool budget for research-only: 6–10 (web_search × N + commit + push + WIP write).
- Schema lives in `data/datacenters/README.md`; Chat 99 will consume it for layer build via `layers.yaml` append + a custom loader. Coord precision matters because Chat 99 will render points; mark `county_centroid` entries clearly.
- Source-quality bar: official permits, SEC filings, primary press releases, ERCOT INR filings, county economic-development records preferred. Pure secondary tech press OK only as confirmation.

---

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### ABATEMENT PERMIAN-CORE + PERIPHERAL

Permian-core (Andrews, Ector, Glasscock, Loving, Martin, Midland, Ward, Winkler) → peripheral (Crane, Crockett, Irion, Reagan, Schleicher, Sutton, Upton) county scrape sequence. 4–6 chats. **Hard constraint:** CivicEngage/Akamai bot-block on `reevescounty.org` extends to any county on the same CMS hosting platform — adapter fixes verifiable only after residential-proxy or whitelisted egress provisioned. Detail in `docs/sprint-plan.md`.

### COMPTROLLER LDAD SCRAPE

Supersedes prior "operator manual XLSX download" ask. There is no bulk XLSX. Canonical source: `https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`. Blocked pending operator authorization for JS-rendered scrape (Selenium / Playwright — same authorization class as CRPUB / RRC MFT). Until authorized: backstop only.

### ABATEMENT WEEKLY CRON

`.github/workflows/abatement-scrape.yml`. Cron weekly Monday 06:00 UTC. Commit diff to `data/abatements/abatement_hits_latest.csv` + rolling history. **Hard prerequisite:** `reevescounty.org` Akamai block must be resolved before cron ships, otherwise Reeves silently produces 0 hits.

### DC RESEARCH → DC BUILD → DC AUTO-REFRESH

3-chat sub-sequence. Research anchors: Longfellow/Poolside (Pecos), Stargate (Abilene), Project Matador/Fermi → structured data file → layer build → GitHub Actions weekly refresh with LLM-in-the-loop parser. Detail in `docs/sprint-plan.md`.

### MOBILE-FRIENDLY MAP

Responsive breakpoints, touch-friendly controls, pinch-zoom tuning, measure tool + print-to-PDF mobile usability, popup sizing. 2–3 chats.

### ERCOT QUEUE PROJECT AGGREGATION POPUP  *(low priority)*

`ercot_queue` has 1,205 distinct project `group` keys; 394 groups have 2+ components. Build-time aggregation in `build.py`: compute `group_total_mw`, `group_count`, `group_breakdown` per group; popup template renders summary line + breakdown list. Test case Longfellow__Pecos: 6 rows, 2,153.3 MW total.

---

## Prod status

- Layer count: **25**
- Last published deploy: `69ed60e59254f7df1a9cacdb` (Chat 97, 2026-04-26). State=ready. Carries print-only legend: `#print-legend` element + `@media print` 4-column flow + `btn-print` handler populating from `activeLayerIds()` × `LAYERS` (filtering `sidebar_omit`, preserving ERCOT-queue gradient swatch). Build clean: `built=25 missing=0 errored=0 tiles_total=18816 KB`. Local↔prod md5 identical (`d114b4e7f7b1714bff721d7d432092d6`); Netlify upload deduped against Chat 96 PMTiles (template-only delta).
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
