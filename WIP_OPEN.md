# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat`** = task spec for the immediately-next shipping chat. **`## Sprint queue`** = N+2 and beyond. Multi-step sprint detail lives in `docs/sprint-plan.md` (deleted per item when shipped).

---

## Next chat

**Chat 92 resume — FIELD EXPANSION + WELLS HIDE.** Branch `refinement-chat92-field-expansion-wells` has §1 partial committed; complete §2 + §3, build, deploy, merge.

### Task

1. **§2 `tax_abatements` popup/filter rename.** Display-layer only; Chat 88 schema stays locked. Rename `commissioned` label "Commissioned" → "Approved date". Popup field order + filter set per `docs/sprint-plan.md` FIELD EXPANSION §2. `layers.yaml` edit + popup template; no data file change.
2. **§3 `wells` hide.** Raise `min_zoom: 10` in `layers.yaml`. Do NOT delete PMTiles. Fallback `hidden: true` if min_zoom alone insufficient.
3. **Build + deploy to prod.** Net layer count stays at 25. Verify §1 (gas-turbine field expansion) renders + §2 popup + §3 wells hidden at default zoom.

### Acceptance

- §2: `tax_abatements` popup shows new field order; filter UI reflects the listed set.
- §3: `wells` not visible until zoom 10.
- `built=25 missing=0 errored=0` in build report; deploy state=ready; layer-id grep on prod returns expected count.

### Branch

`refinement-chat92-field-expansion-wells` — already on origin with §1 commit `8a396c2`.

### Pre-flight

Audit-3 cleanup (this chat) lifted FIELD EXPANSION detail into `docs/sprint-plan.md`, trimmed WIP_OPEN.md under 8KB, and rewrote sidebar pointer docs (`docs/sidebar/COMMANDS.md`, `docs/sidebar/ENVIRONMENT.md` — operator must re-upload to project knowledge from the Audit-3 bundle). Stranded branches `chat76-wip` and `refinement-tceq-refresh` already absent from origin at audit time (Audit-3 spec was based on stale audit). Handoff doc `docs/_chat92-field-expansion-wells_handoff.md` on the chat92 branch carries detailed §1 status and §2/§3 plan — read it first per §10 stale-handoff heuristic.

---

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### ABATEMENT PERMIAN-CORE + PERIPHERAL

Permian-core (Andrews, Ector, Glasscock, Loving, Martin, Midland, Ward, Winkler) → peripheral (Crane, Crockett, Irion, Reagan, Schleicher, Sutton, Upton) county scrape sequence. 4–6 chats. **Hard constraint:** CivicEngage/Akamai bot-block on `reevescounty.org` extends to any county on the same CMS hosting platform — adapter fixes verifiable only after residential-proxy or whitelisted egress provisioned. Detail in `docs/sprint-plan.md`.

### POWER PLANT DATA REFRESH + POPUP REDESIGN

Re-pull EIA-860 (plants, battery) + USWTDB (wind) to fill blanks; rewrite popup templates for `eia860_plants`, `eia860_battery`, `solar`, `wind`, `ercot_queue` (drop sector; add COD/operator/capacity/fuel). Filter UI reflects same fields. Detail in `docs/sprint-plan.md`.

### COMPTROLLER LDAD SCRAPE

Supersedes prior "operator manual XLSX download" ask. There is no bulk XLSX. Canonical source: `https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`. Blocked pending operator authorization for JS-rendered scrape (Selenium / Playwright — same authorization class as CRPUB / RRC MFT). Until authorized: backstop only.

### ABATEMENT WEEKLY CRON

`.github/workflows/abatement-scrape.yml`. Cron weekly Monday 06:00 UTC. Commit diff to `data/abatements/abatement_hits_latest.csv` + rolling history. **Hard prerequisite:** `reevescounty.org` Akamai block must be resolved before cron ships, otherwise Reeves silently produces 0 hits.

### LEGEND ON PRINT / SHARE / PDF

Print CSS at `build_template.html` hides `.sidebar` on `@media print`. Sidebar IS the legend; prints ship without it. Inject print-only legend element enumerating active layers (name + color swatch + symbol) into print header or footer. Fit within 10.3"×7.1" landscape. Handle >15 active layers via multi-column or multi-page.

### DC RESEARCH → DC BUILD → DC AUTO-REFRESH

3-chat sub-sequence. Research anchors: Longfellow/Poolside (Pecos), Stargate (Abilene), Project Matador/Fermi → structured data file → layer build → GitHub Actions weekly refresh with LLM-in-the-loop parser. Detail in `docs/sprint-plan.md`.

### MOBILE-FRIENDLY MAP

Responsive breakpoints, touch-friendly controls, pinch-zoom tuning, measure tool + print-to-PDF mobile usability, popup sizing. 2–3 chats.

### ERCOT QUEUE PROJECT AGGREGATION POPUP  *(low priority)*

`ercot_queue` has 1,205 distinct project `group` keys; 394 groups have 2+ components. Build-time aggregation in `build.py`: compute `group_total_mw`, `group_count`, `group_breakdown` per group; popup template renders summary line + breakdown list. Test case Longfellow__Pecos: 6 rows, 2,153.3 MW total.

---

## Prod status

- Layer count: **25**
- Last published deploy: `69ec91f62150e8257e82413d` (Chat 90 close-out, 2026-04-25). State=ready.
- URL: `https://lrp-tx-gis.netlify.app` — requires real User-Agent on curl (`-A "Mozilla/5.0"`).

---

## Open backlog

**Data-pipeline gaps** (non-blocking):
- `eia860_plants`: 476/1367 rows null `capacity_mw` / `technology` / `fuel`
- `combined_points.csv` blank `operator` / `commissioned` on EIA point layers
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar
- BEAD `bead_fiber_planned` layer (Chat 91 §1 dropped): BDO XLSX trio archived to `data/bead_bdo/` but contains no county or coords. Three unblock paths documented in `data/bead_bdo/README.md`

**Infrastructure:**
- `NETLIFY_PAT` absent from `CREDENTIALS.md`. Netlify MCP proxy path canonical
- `GITHUB_PAT` can push branches, 403 on PR creation. Direct-merge-to-main is the protocol (OPERATING.md §9)
- **Akamai datacenter-egress block on `reevescounty.org`** — cloud-runner / GitHub-Actions traffic 403s regardless of UA / TLS fingerprint. Hard prerequisite for the abatement-weekly-cron sprint item. Unblock options: residential-proxy egress (paid), Akamai allowlisting via Reeves County IT (low likelihood), search-API result pages

**Outstanding credential hygiene:**
- `GITHUB_PAT` leak from Chat 87 unrotated per operator override. Token valid until 2027-04-21

**Permanently excluded:** see ARCHITECTURE.md §11

**Other (non-GIS):** Grid Wire Vol. 7. Tier 2 water availability assessments. Excel returns model.
