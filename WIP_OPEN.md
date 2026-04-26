# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat`** = task spec for the immediately-next shipping chat. **`## Sprint queue`** = N+2 and beyond. Multi-step sprint detail lives in `docs/sprint-plan.md` (deleted per item when shipped).

---

## Next chat

**Chat 99 — DC LAYER BUILD: render dc_anchors as map layer.** Second of the 3-chat DC sub-sequence (research ✓ → layer build → auto-refresh cron). Consume `data/datacenters/dc_anchors.json` and ship a new `dc_anchors` layer to prod.

### Task

1. Append `dc_anchors` entry to `layers.yaml`. Source = `data/datacenters/dc_anchors.json` (custom JSON loader required — it's not GeoJSON or CSV in the canonical schema).
2. Add a custom loader path in `build.py` (or per existing pattern) that reads `dc_anchors.json` and emits a points GeoJSON consumable by tippecanoe. Map fields: `id`, `name`, `developer`, `county`, `status`, `capacity_mw_announced`, `commissioned_target`, `power_source`, `coord_accuracy`. Sources array → flatten to `sources_count` + `sources_urls` (joined string for popup) so it survives tile encoding.
3. Symbology: graduated-circle on `capacity_mw_announced` (e.g. 100–500 / 500–2000 / 2000–5000 / 5000+ MW buckets); dim-marker for `coord_accuracy=county_centroid`; status-color overlay (announced=grey, permitted=amber, under_construction=blue, operational=green) — match the existing layer palette in `ARCHITECTURE.md` if a similar precedent exists.
4. Popup template: name (bold), developer, county, status badge, capacity MW, target commissioning year, power-source paragraph, and a "Sources (N)" expandable footer with the URLs. Surface `coord_accuracy` as a small "approximate location" badge when not `precise`.
5. Sidebar entry with filter on `status` + `county`. Standard build → preview → prod sequence per §8.
6. WIP next-chat = Chat 100 (auto-refresh GitHub Actions cron with LLM-in-the-loop parser).

### Acceptance

- New layer `dc_anchors` renders 8 points (or whatever the JSON contains at chat-time) on prod.
- Popup surfaces all required fields; sources list links out correctly.
- Filter UI works for `status` and `county`.
- `built=26  missing=0  errored=0` on final build line.
- Local↔prod md5 identical post-deploy.
- Branch merged + deleted same chat per §6.12.

### Branch

`refinement-chat99-dc-layer`.

### Pre-flight

- Chat 98 closed clean (no deploy). 8 entries shipped to `data/datacenters/dc_anchors.json`: Project Horizon (Pecos, 2 GW, under_construction), Stargate Abilene (Taylor, 1.2 GW, operational), Microsoft–Crusoe Abilene (Taylor, 900 MW, under_construction), Project Matador / Fermi America (Carson, 11 GW, permitted), GW Ranch / Pacifico (Pecos, 7.65 GW, permitted), Stargate Frontier Shackelford (Shackelford, 1.4 GW, under_construction), Stargate Milam / SB Energy (Milam, 1.2 GW, under_construction), Meta Temple (Bell, 198 MW, operational). Total announced capacity: ~25.6 GW across 8 anchors.
- Coord accuracy bias: 2 entries are `county_centroid` (Shackelford, Milam — county-level only); 6 are `approximate` (right area, ≤10 km). None are `precise` parcel-level; precision can be tightened later via TCEQ permit lookups but is not blocking for layer-build.
- Schema doc at `data/datacenters/README.md`. Source-quality conventions and refresh cadence (weekly Mondays 06:00 UTC target) defined there.
- Tool budget for layer-build with deploy: 6–10 (yaml edit + loader patch + build + Netlify proxy + verify + WIP write + close-out script). The `dc_anchors` source is JSON not the canonical CSV/GeoJSON, so `build.py` will need a small dispatcher branch — keep it minimal, single-purpose.

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
