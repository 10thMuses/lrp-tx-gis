# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat`** = task spec for the immediately-next shipping chat. **`## Sprint queue`** = N+2 and beyond.

---

## Next chat

**Audit-3 — STRANDED BRANCH CLEANUP + SIDEBAR HYGIENE.** Doc/repo housekeeping. No layer changes; no deploy.

### Task

1. **Resolve stranded origin branches.** `audit.sh` reports four. Delete the two abandoned: `chat76-wip` (1 commit, 80 behind main, last 2026-04-23) and `refinement-tceq-refresh` (0 ahead, 89 behind, scoped out per ARCHITECTURE.md §11). Leave `refinement-chat92-field-expansion-wells` (2 ahead, active sprint item) and the chat's own in-flight branch. `git push origin --delete chat76-wip refinement-tceq-refresh`.

2. **Sidebar pointer rewrite.** `/mnt/project/COMMANDS.md` and `/mnt/project/ENVIRONMENT.md` reference docs deleted in Audit-1 (`Readme.md`, `WIP_LOG.md`, `docs/principles.md`, `docs/settled.md`, `docs/refinement-sequence.md`, `GIS_SPEC.md`) and duplicate content now in OPERATING.md §5/§7/§10. Rewrite both as ~30-line pointer docs ("see OPERATING.md §X for trigger phrases / session protocol / etc."). Output bundle includes both for operator re-upload to project knowledge.

3. **WIP_OPEN.md size reduction.** `audit.sh` reports 9261B vs 8KB target. Per OPERATING.md §10, lift verbose Sprint queue entries (FIELD EXPANSION, ABATEMENT PERMIAN-CORE, POWER PLANT REFRESH, DC RESEARCH sub-sequence) into `docs/sprint-plan.md`. Keep only one-paragraph pointers in WIP_OPEN.md.

4. **Re-run `audit.sh`** at session close to confirm: stranded count ≤2, WIP_OPEN.md <8192B, OPERATING.md still 306 (separate fix; not in scope here), close-out conformance now 1/20+ (lags monotonically).

### Acceptance

- `git ls-remote --heads origin` shows ≤2 non-main branches.
- COMMANDS.md and ENVIRONMENT.md rewritten as pointers; bundle presented for operator re-upload.
- WIP_OPEN.md <8192B (audit.sh OK on size).
- `audit.sh` runs clean at close-out.

### Branch

`refinement-audit-3-cleanup`

### Pre-flight

Audit-2 added `close-out.sh`, `deploy.sh`, `ship.sh`, `audit.sh`, `pre-commit` under five per-unit commits on `refinement-audit-2-operational-scripts`, merged to main with deploy=none. `deploy.sh` is bash-complete but errors at `NETLIFY_PAT` lookup until Open-backlog item provisions the credential — canonical deploy path remains MCP-via-chat. `close-out.sh` enforces §6.14 (rejects merges with zero non-handoff commits) and accepts `none` as deploy-id sentinel for doc-only chats.

---

## Sprint queue

Ordered by operator priority. N+2 and beyond.

### FIELD EXPANSION + WELLS HIDE

Bundled `layers.yaml` + refresh-script maintenance chat. No layer-count change (stays at 25). One chat.

1. **`tceq_gas_turbines` extend refresh** — `scripts/refresh_tceq_gas_turbines.py` captures 13 of ~18 source columns. Add: full `received_date` (ISO; only `year` captured today), TCEQ `permit_no` (distinct from INR which is in `plant_code`), `num_units`, permit `status`. Map via abatement-style overload (ARCHITECTURE.md §4): `inr` ← permit_no, `funnel_stage` ← permit status, `zone` ← received_date ISO, `project` ← num_units. Add to popup + `filterable_fields` (numeric on `mw`, `year`; categorical on `technology`, `manu`, `operator`, `county`, `funnel_stage`).

2. **`tax_abatements` popup/filter rename** — display layer only; Chat 88 schema stays locked. Rename `commissioned` label "Commissioned" → "Approved date". Popup field order: `name` (Applicant), `county`, `commissioned` (Approved date), `technology` (Project type), `mw` (Project MW), `capacity` (Capex $M), `use` (Abatement schedule), `sector` (Taxing entities), `project` (Reinvestment zone), `poi` (Agenda URL). `filterable_fields`: county, technology, commissioned (date range), mw, capacity. No status in popup or filters. Technology filter set: natural_gas, gas_peaker, solar, wind, battery, renewable_other.

3. **`wells` hide** — current state: `default_on: false`, `min_zoom: 6`, thousands of statewide features. Primary: raise `min_zoom: 10`. Fallback: flag entry with `hidden: true` and skip sidebar render in `build_template.html`. Do NOT delete PMTiles.

### ABATEMENT PERMIAN-CORE + PERIPHERAL

Permian-core (Andrews, Ector, Glasscock, Loving, Martin, Midland, Ward, Winkler) → peripheral (Crane, Crockett, Irion, Reagan, Schleicher, Sutton, Upton). PDF-only counties dropped. 4–6 chats. **Constraint:** any county on the same CivicEngage CMS hosting platform now used by Reeves (`reevescounty.org`) is Akamai bot-protected from datacenter egress; adapter URL fixes are correct but cannot be verified from cloud runners until residential-proxy or whitelisted egress is provisioned.

### POWER PLANT DATA REFRESH + POPUP REDESIGN

Re-pull EIA-860 (plants, battery) + USWTDB (wind) to fill blank operator/commissioned/technology/fuel/capacity_mw. Rewrite popup templates for `eia860_plants`, `eia860_battery`, `solar`, `wind`, `ercot_queue`: DROP sector; ADD commissioned/COD date, operator, capacity_mw, fuel/technology. Filter UI reflects same fields.

### COMPTROLLER LDAD SCRAPE

Supersedes prior "operator manual XLSX download" ask. There is no bulk XLSX. Canonical source: `https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`. Blocked pending operator authorization for JS-rendered scrape (Selenium / Playwright — same authorization class as CRPUB / RRC MFT). Until authorized: backstop only.

### ABATEMENT WEEKLY CRON

`.github/workflows/abatement-scrape.yml`. Cron weekly Monday 06:00 UTC. Commit diff to `data/abatements/abatement_hits_latest.csv` + rolling history. **Hard prerequisite:** `reevescounty.org` Akamai block must be resolved before cron ships, otherwise Reeves silently produces 0 hits.

### LEGEND ON PRINT / SHARE / PDF

Print CSS at `build_template.html` hides `.sidebar` on `@media print`. Sidebar IS the legend; prints ship without it. Inject print-only legend element enumerating active layers (name + color swatch + symbol) into print header or footer. Fit within 10.3"×7.1" landscape. Handle >15 active layers via multi-column or multi-page.

### DC RESEARCH → DC BUILD → DC AUTO-REFRESH (3-chat sub-sequence)

Research anchors: Longfellow/Poolside (Pecos), Stargate (Abilene), Project Matador/Fermi. Capture per-project: name, county, coords, MW, announcement date, completion date, owner/operator/developer, tenant, source, confidence level. Deliver structured data file → layer build → GitHub Actions weekly refresh with LLM-in-the-loop parser.

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
