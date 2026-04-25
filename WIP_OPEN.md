# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat`** = task spec for the immediately-next shipping chat. **`## Sprint queue`** = N+2 and beyond.

---

## Next chat

**Audit-2 — OPERATIONAL SCRIPTS.** Doc-only commit chat. Encodes the procedural rules currently scattered across operator paste-buffers into reusable scripts. No layer changes; no deploy.

### Task

1. **`scripts/close-out.sh <branch> <deploy-id>`** — replaces the close-out bash block formerly pasted into `## Next chat`. Sequence: feature-branch push → checkout main → `git pull --rebase` → `git merge --no-ff origin/<branch>` with deploy-id in message → push main → `git push origin --delete <branch>`. Errors out if HEAD has zero non-handoff commits (enforces OPERATING.md §6 hard rule 14).

2. **`scripts/deploy.sh`** — replaces the Netlify-MCP + CLI-proxy + poll + verify sequence formerly pasted as "Deploy pattern (CANONICAL)". Calls Netlify MCP via the same JSON-RPC interface used in chat; polls `get-deploy-for-site` until `state=ready`; sleeps 45s; runs `curl -sI -A "Mozilla/5.0"` on root + one tile endpoint; greps `"id":"..."` count from served HTML. Returns deploy-id on stdout for piping into close-out.sh.

3. **`scripts/ship.sh <branch>`** — atomic deploy+merge+delete-branch wrapper. Runs `deploy.sh`, captures deploy-id, runs `close-out.sh <branch> <deploy-id>`. Single command for OPERATING.md §6 hard rule 12 (deploy + merge atomicity).

4. **`scripts/audit.sh`** — telemetry per OPERATING.md §15. Reports OPERATING.md line count, count of session-open / close-out invocations in last 30 commits, stranded branches on origin (ls-remote diff vs `main` and `refinement-*` patterns from recent commits), WIP_OPEN.md byte size. Outputs human-readable summary to stdout.

5. **Pre-commit hook** at `scripts/pre-commit` (operator opts in via `git config core.hooksPath scripts/`): rejects files >1MB unless on a `--allow-large` flag path; warns on staging files outside the explicit set.

### Acceptance

- All four scripts executable and committed.
- `bash scripts/audit.sh` runs clean and prints a snapshot.
- No production code, build pipeline, or layer changes.

### Branch

`refinement-audit-2-operational-scripts`

### Pre-flight

Audit-1 consolidated 6 docs (Readme + GIS_SPEC + principles + settled + 2 refinement-* archives) into OPERATING.md (305 lines) + ARCHITECTURE.md (262 lines). WIP_LOG.md archived. Cross-walk verification at `docs/archive/audit-1/CROSS_WALK.md`. Branches merged: `refinement-audit-1-doc-consolidation`, `refinement-audit-1-cleanup` (dangling-ref cleanup of session-open.sh, CHANGELOG.md, WIP_OPEN.md Pre-flight + persisted CROSS_WALK).

---

## Sprint queue

Ordered by operator priority. N+2 and beyond.

### Audit-3 — STRANDED BRANCH CLEANUP + SIDEBAR HYGIENE

Doc/repo housekeeping. Resolve `chat76-wip` and `refinement-tceq-refresh` (latter explicitly scoped out per ARCHITECTURE.md §11). Update sidebar system prompt to remove stale references (ENVIRONMENT.md ghost, COMMANDS.md duplication of OPERATING.md §7 trigger phrases). Validate `audit.sh` telemetry output now that scripts exist.

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
