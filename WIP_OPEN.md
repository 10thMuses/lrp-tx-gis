# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per Readme §10: **`## Next chat`** = paste-ready for next shipping chat. **`## Sprint queue`** = N+2 and beyond.

---

## Next chat

**Chat 92 — FIELD EXPANSION + WELLS HIDE.** Bundled `layers.yaml` + refresh-script maintenance chat. No layer-count change (stays at 25). Fits one chat; no sprint-plan doc warranted.

### Task

1. **`tceq_gas_turbines` — extend refresh to capture all source XLSX fields.** Current `scripts/refresh_tceq_gas_turbines.py` captures 13 of ~18 source columns. Add: full `received_date` (ISO; only `year` captured today), TCEQ `permit_no` (distinct from INR which is in `plant_code`), `num_units`, permit `status` (issued / pending / renewed / modified). Map into unused `combined_points.csv` columns via the abatement-style overload (Chat 88 schema): `inr` ← permit_no, `funnel_stage` ← permit status, `zone` ← received_date ISO, `project` ← num_units. Add new fields to popup + `filterable_fields` (numeric on `mw`, `year`; categorical on `technology`, `manu`, `operator`, `county`, `funnel_stage`).

2. **`tax_abatements` — popup/filter rename + field additions (display layer only; Chat 88 schema stays locked).**
   - Rename `commissioned` popup+filter label "Commissioned" → **"Approved date"**.
   - Popup field order: `name` (Applicant), `county`, `commissioned` (Approved date), `technology` (Project type), `mw` (Project MW), `capacity` (Capex $M), `use` (Abatement schedule), `sector` (Taxing entities), `project` (Reinvestment zone), `poi` (Agenda URL).
   - `filterable_fields`: `county` (categorical), `technology` (categorical), `commissioned` (date range, "Approved date"), `mw` (numeric), `capacity` (numeric).
   - No `status` in popup or filters.
   - Technology filter set: `natural_gas`, `gas_peaker`, `solar`, `wind`, `battery`, `renewable_other` (no new pull).

3. **`wells` — hide to reduce memory footprint.** Current state: `default_on: false`, `min_zoom: 6`, thousands of statewide features. Primary: raise `min_zoom: 10`. Fallback if memory persists: flag entry with `hidden: true` and skip sidebar render in `build_template.html`. Do NOT delete PMTiles — keep on disk for future re-enable without re-refresh.

### Acceptance

- Layer count unchanged (25).
- `tceq_gas_turbines` popup + filter UI shows all populated source fields.
- `tax_abatements` popup shows "Approved date" label; filter UI has 5 filters (county, technology, approved_date range, mw, capacity); no status anywhere.
- `wells` not loaded below zoom 10 (or absent from sidebar if fallback chosen).
- Build + deploy + CDN verification per standard protocol; live site returns HTTP 200 with 25 layer ids.

### Session open

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
cd /home/claude && rm -rf repo 2>/dev/null
git clone -q https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git repo && cd repo
bash scripts/session-open.sh refinement-chat92-field-expansion-wells
apt-get install -y tippecanoe libcairo2 -q
pip install shapely pmtiles pyyaml cairosvg pandas requests openpyxl --break-system-packages -q
```

### Deploy pattern (CANONICAL)

Unchanged: Netlify MCP → CLI proxy. REST-API dead.

1. `Netlify:netlify-deploy-services-updater` `{operation: "deploy-site", params: {siteId: "01b53b80-687e-4641-b088-115b7d5ef638"}}` → single-use `--proxy-path` URL.
2. `cd /mnt/user-data/outputs/dist && npx -y @netlify/mcp@latest --site-id 01b53b80-687e-4641-b088-115b7d5ef638 --proxy-path "<URL>" --no-wait` → `{"deployId":"...","buildId":"..."}`.
3. Poll `get-deploy-for-site` until `state=ready`.
4. `sleep 45` for CDN warm-up. HEAD may 503; GET is source of truth.
5. `curl -s -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | grep -oE '"id":"[a-z_][a-z0-9_]*"' | sort -u | wc -l` → 25.

Proxy URL single-use. On 503 upload error, request fresh URL.

### Pre-flight

Chat 91 closed 2026-04-25: BEAD `bead_fiber_planned` layer dropped per 30-min ship rule (no downloadable footprint geometry — BDO XLSX trio archived to `data/bead_bdo/`); Reeves adapter URL migrated `co.reeves.tx.us` → `reevescounty.org` (old DNS dead; new domain Akamai-blocked from datacenter egress, so adapter cannot be verified from cloud runners). Layer count unchanged at 25. Branch `refinement-chat91-bead-fiber-reeves` merged and deleted. Start from clean `main`.

### Close-out (NON-NEGOTIABLE, per Readme §10)

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
git fetch origin refinement-chat92-field-expansion-wells
git checkout main && git pull --rebase origin main
git merge --no-ff origin/refinement-chat92-field-expansion-wells -m "Merge refinement-chat92-field-expansion-wells (Chat 92): tceq_gas_turbines field expansion + tax_abatements popup rename + wells min_zoom raise (deploy <id>)"
# Rewrite WIP_OPEN.md §Next chat → next sprint-queue chat (operator decides at close-out: Permian-core abatement, power-plant refresh, or DC sub-sequence)
# Update §Prod status with new deployId
# Drop the just-promoted entry from §Sprint queue
git commit -am "Chat 92 close-out"
git push
git push --delete origin refinement-chat92-field-expansion-wells
```

**Credential hygiene carry-forward:** `GITHUB_PAT` leak from Chat 87 remains unrotated per operator override. Token valid until 2027-04-21. Flag again in Chat 92 close-out if still outstanding.

---

## Sprint queue

Ordered by operator priority. N+2 and beyond. Multi-chat active sprint detail lives in `docs/sprint-plan.md`; one-paragraph pointers below.

### Chat 93+ — ABATEMENT PERMIAN-CORE + PERIPHERAL

Permian-core (Andrews, Ector, Glasscock, Loving, Martin, Midland, Ward, Winkler) → peripheral (Crane, Crockett, Irion, Reagan, Schleicher, Sutton, Upton). PDF-only counties dropped per spec §12.3. 4–6 chats. **Constraint surfaced Chat 91:** any county on the same CivicEngage CMS hosting platform now used by Reeves (`reevescounty.org`) is Akamai bot-protected from datacenter egress — adapter URL fixes are correct but cannot be verified from cloud runners or GitHub Actions until residential proxy or whitelisted egress is provisioned. Promoted to `docs/sprint-plan.md` when it enters the active 5-chat window.

### Chat — POWER PLANT DATA REFRESH + POPUP REDESIGN

Re-pull EIA-860 (plants, battery) + USWTDB (wind) to fill blank operator/commissioned/technology/fuel/capacity_mw. Rewrite popup templates for `eia860_plants`, `eia860_battery`, `solar`, `wind`, `ercot_queue`: DROP sector; ADD commissioned/COD date, operator, capacity_mw, fuel/technology. Filter UI reflects same fields (drop sector filter). Promoted to `docs/sprint-plan.md` when it enters active window.

### Chat — COMPTROLLER LDAD SCRAPE (was: manual XLSX)

Supersedes prior "operator manual XLSX download" ask. There is no bulk
XLSX — Comptroller registry is JS-gated with per-record CSV only.

Canonical source: https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php
(SB 1340 unified Ch. 380/381/312 Local Development Agreement DB).

Blocked pending operator authorization for JS-rendered scrape
(Selenium / Playwright pattern — same authorization class as CRPUB /
RRC MFT). Until authorized: backstop only, not leading signal;
commissioners-court agenda scrape remains primary.

### Chat — ABATEMENT WEEKLY CRON

`.github/workflows/abatement-scrape.yml`. Cron weekly Monday 06:00 UTC.
Commit diff to `data/abatements/abatement_hits_latest.csv` + rolling
history. Alerting deferred per spec §12.8.

Challenges: runner egress reliability on county CMS endpoints; silent
drift if selectors break (no alerting in v1). **Hard prerequisite
(surfaced Chat 91):** `reevescounty.org` (Akamai-protected, the
post-migration host for the Reeves CivicEngage CMS) returns 403 to
all GitHub-Actions egress regardless of UA / TLS fingerprint. Cron
cannot ship until residential-proxy egress or Akamai allowlisting
is provisioned, otherwise Reeves silently produces 0 hits forever.

### Chat — LEGEND ON PRINT / SHARE / PDF  *(new, surfaced 2026-04-24)*

Current gap: print CSS at `build_template.html:96-110` hides `.sidebar`
on `@media print`. The sidebar IS the legend; prints/PDFs ship without
it. Share-URL flow also has no legend.

Scope: inject a print-only legend element enumerating active layers
(name + color swatch + symbol) into print header or footer. Fit within
10.3"×7.1" landscape print area. Handle >15 active layers via
multi-column or multi-page. Verify share-URL flow still reproduces
layer state correctly.

Challenges: active-layer enumeration at print time; style system must
match main-map rendering (point vs line vs polygon); legend height
budget.

### Chat — DC RESEARCH → DC BUILD → DC AUTO-REFRESH (3-chat sub-sequence)

Per `docs/refinement-sequence.md`. Research anchors: Longfellow/Poolside
(Pecos), Stargate (Abilene), Project Matador/Fermi. Capture per-project:
name, county, coords, MW, announcement date, completion date,
owner/operator/developer, tenant, source, confidence level. Deliver
structured data file → layer build → GitHub Actions weekly refresh with
LLM-in-the-loop parser.

Challenges: signal quality (announced vs rumored); coord precision when
only county disclosed; LLM parser reliability for auto-refresh.

### Chat — MOBILE-FRIENDLY MAP (UI/UX stage)

Responsive breakpoints, touch-friendly controls, pinch-zoom tuning,
measure tool + print-to-PDF mobile usability, popup sizing. Candidate
for promotion into `docs/refinement-sequence.md`. Estimate 2–3 chats.

Challenges: measure tool UX on touch; sidebar collapse behavior on
narrow viewports; popup sizing with long field lists.

### Chat — ERCOT QUEUE PROJECT AGGREGATION POPUP  *(new, low priority)*

Current state: `ercot_queue` has 1,205 distinct project `group` keys
(e.g., `LONGFELLOW__PECOS`); 394 groups have 2+ components. Popup today
shows single-row data only.

Scope: build-time aggregation in `build.py` — compute `group_total_mw`,
`group_count`, and `group_breakdown` (list of name / fuel / MW per
component) per group; inject into each row's properties. Popup template
renders summary line (total MW, component count) + breakdown list.

Verified test case — Longfellow__Pecos: 6 rows, 2,153.3 MW total
(Solar I 178.2 + Solar II 207.4 + BESS I 55.0 + BESS II 105.8 +
Comanche Creek gas 107.0 + Big Canyon Wind 1,500.0).

Challenges: rows with null `group` (handle as pass-through);
popup rendering of breakdown list; no regression to data-driven icon
sizing.

### Chat — STRANDED BRANCH CLEANUP  *(deferred from Chat 87, surfaced 2026-04-24)*

Two branches exist on origin without a clear paper trail: `chat76-wip`
(HEAD `4d6ca08`) and `refinement-tceq-refresh` (HEAD `606b2771`). Neither
is referenced in current `WIP_OPEN.md`, `WIP_LOG.md`, or
`docs/sprint-plan.md`.

Scope: diff each against current `main`; identify what's on the branch
and whether it's still relevant; either promote salvageable work to a
proper sprint-queue entry, rebase onto current main as a new branch, or
delete. Do NOT merge without review — `refinement-tceq-refresh` was
explicitly scoped out per `docs/settled.md`, so if its commits include
tceq work, they should not land.

One-shot housekeeping chat; should take 3-5 tool calls.

### Outstanding merges

None. `refinement-abatement-annotate` merged and deleted from origin Chat 85.

Historical notes:
- Chat 84: `refinement-sidebar-collapse` commits had deployed to prod Chat 81 but were never merged to main, creating a silent regression on Chat 84's build (prod lost sidebar collapse feature transiently). Fixed Chat 84a via merge + redeploy `69eb707c56bb04f8c221f5af`.
- Chat 85: matcher tightening was amended onto the feature branch AFTER the initial merge, which picked up the pre-amendment local-tracking ref and silently dropped the fix. Resolved by re-applying tightening as a follow-up commit on main. Lesson codified in §Next chat close-out: `git fetch origin <branch>` before `git merge` when the branch was amended post-push.
- Running principle: every deployed branch must merge to main same-chat; every post-push amendment must force-push and re-fetch before merge.

---

## Prod status

- **Chat 91 closed 2026-04-25** — No deploy. §1 BEAD `bead_fiber_planned` layer dropped per 30-min ship rule (no downloadable footprint geometry; BDO XLSX trio archived to `data/bead_bdo/` for future render-path work). §2 Reeves CivicEngage adapter URL migrated `co.reeves.tx.us` → `reevescounty.org` (old DNS dead); new domain is Akamai-protected and 403s all datacenter egress, so adapter fix is structurally correct but cannot be verified from cloud runners. Search-engine crawlers confirmed three live abatement entities on the new domain: August Draw Solar LLC, Energy Forge One LLC, Pecos Power Plant LLC. Branch `refinement-chat91-bead-fiber-reeves` merged and deleted. Layer count unchanged at 25.
- **Chat 90 closed 2026-04-25** — FCC fiber coverage layer shipped: `fcc_fiber_coverage` H3 res-8 hexes built from FCC BDC fixed-availability CSV (FTTP filter, 23-county Permian-focus footprint). Layer count 24 → 25.
- URL: https://lrp-tx-gis.netlify.app — requires real User-Agent on curl (`-A "Mozilla/5.0"`).
- Last published deploy: `69ec91f62150e8257e82413d` (Chat 90 close-out, 2026-04-25). Supersedes `69ebcfbbe97514ce84df1591`. State=ready. Layer count 25 live. `fcc_fiber_coverage` renders as cyan choropleth on `max_down_mbps` (3 bins: ≥1000 / 100–999 / <100), `default_on: false`, popup shows all six aggregate fields.
- Previous deploy: `69ebcfbbe97514ce84df1591` (Chat 88 close-out, 2026-04-24 20:17:05Z) — Chat 88 tax_abatements schema artifacts confirmed: label `Property Tax Abatements (Ch.312 / LDAD, new or expansion)`, all 4 new popup_labels present (`Abatement term (yrs)`, `Jobs commitment`, `Taxing entities`, `Reinvestment zone`).
- **CDN quirk (persistent, note for future chats):** HEAD requests to `https://lrp-tx-gis.netlify.app/` return 503 even when the site is serving healthy GET responses. Do not treat HEAD 503 as failure — grep GET output for layer-id count and schema markers.
- Previous deploy: `69ebb64823c1c470e0c6f0b1` (Chat 87 bugfix, 2026-04-24 18:28:29Z) — all 4 Chat 87 styling edits confirmed (`tiger_highways line_width: 0.6`, `waha_circle`, `caramba_north #2E7D32` + `Caramba North (1,300 ac)`).
- **Chat 87 bug caught at post-close-out verification (2026-04-24 18:26Z):** Initial deploy `69eb952306288390a3d6a3c0` (16:07Z) shipped only 3 of 4 Chat 87 styling edits. `tiger_highways line_width: 0.6` was dead on prod because `build.py render_html()` layer-dict serializer (line 633–647) did not emit `line_width` — template `sizingLineWidthExpr` on line 338 read `undefined ?? 2` and every line layer rendered at width 2 regardless of `layers.yaml` value. Fix: added `'line_width': L.get('line_width', 2)` to the serializer dict. Redeployed as `69ebb64823c1c470e0c6f0b1`. This bug predates Chat 87 (every line layer was always rendered at width 2); Chat 87 was the first chat to set `line_width` in yaml and thus first to surface it.
- **Process lesson:** Chat 87 close-out initially proceeded without live-site verification due to concurrent Netlify-wide edge outage (16:07Z–18:22Z, `DNS cache overflow` site-wide). Operator override accepted the risk. Post-recovery verification then caught the bug. The halt rule in `WIP_OPEN.md §Next chat` ("if verification fails, halt") exists precisely to prevent this. Future chats: if CDN verification is blocked by infrastructure, override is permissible but the next chat's first act must be post-hoc live verification. Do not consider a close-out complete until served HTML has been grepped.
- Main HEAD includes Chat 90 merge commit (FCC fiber coverage layer). Branch `refinement-chat90-fcc-fiber` deleted from origin.
- Auto-publish: unlocked.
- **Deploy path: Netlify MCP → CLI proxy.** REST-API dead.
- Layer set: **25 built clean**. `tax_abatements` schema = Chat 88 mapping; 9 rows live, 5 abatement annotations apply to `eia860_plants`/`ercot_queue`/`solar` facilities. `fcc_fiber_coverage` is a polygon/hex layer (H3 res-8) added Chat 90.
- **Chat 87 styling edits live in build:** tiger_highways `line_width: 0.6` (thinner at z=8); `waha_circle` yellow ring (`#FFD400`, 1 feature) above Waha Hub; caramba_north green (`#2E7D32`) with label `Caramba North (1,300 ac)`; `build_template.html` `sizingLineWidthExpr` reads `L.line_width ?? 2`; `layerPaint()` point block honors optional `circle_radius` / `stroke_color` / `stroke_width` / `fill_opacity`.
- **Credential hygiene (outstanding):** `GITHUB_PAT` leaked in push-URL echo during Chat 87 edit session. Operator override 2026-04-24 permitted Chat 87 resume to execute with leaked token; rotation still recommended, token valid until 2027-04-21.
- Prebuilt PMTiles (4): `parcels_pecos` 4.98 MB, `rrc_pipelines` 4.73 MB, `tiger_highways` 3.11 MB, `bts_rail` 2.16 MB.
- Sprite sheet: 5 icons @ 1x + 2x at `/sprite/sprite.png` + `sprite@2x.png`.
- Data-driven sizing live: `ercot_queue`, `solar`, `eia860_plants`, `eia860_battery`, `wind`; `substations`, `tpit_subs`, `tpit_lines`.
- UI state: sidebar collapsible (`#sb=1`); `parcels_pecos` sidebar-hidden; default-ON layers; default basemap = esri_imagery; default viewport = -102.9707/30.9112 z12.
- Sizing gaps (static fallback): `eia860_plants` 476/1367 null; `transmission` no voltage.
- **CDN warmup timing:** 45–75s post-deploy. Proxy URL single-use — request fresh URL on 503.

### Abatement layer notes (Chat 83–85)

- **9 features live** (8 Pecos-agenda rows + Matterhorn Express Pipeline LLC with meeting date 2022-07-25). All geocoded to **county centroid only** — no sub-county spatial precision. Do not represent as true point locations.
- **Column-mapping caveats** (schema constraint — `combined_points.csv` has fixed columns):
  - `agenda_url` stored in the `poi` column.
  - `flags` stored in the `funnel_stage` column. **`status` is derived at build time** as `funnel_stage.split('|')[0]` — present in popups + filter UI as its own field.
  - `applicant` stored in `operator`; `reinvestment_zone` in `project`; `project_type` in `technology`; `meeting_date` in `commissioned`.
- **Silver Basin Digital row** has `technology=abatement_other` (not a canonical project_type). Filter via `project=` (reinvestment zone) rather than `technology=` to isolate canonical project-type categories.
- **Filter UI** on tax_abatements: county, technology (project type), status, commissioned (meeting date).
- **Facility annotation (Chat 85, spec §12.1):** build-time fuzzy join matches `tax_abatements` applicants to `eia860_plants`, `ercot_queue`, `solar`, `wind`, `eia860_battery` by `(county, applicant_norm subset-of or equals facility-name/entity/operator/project tokens)`. Zone_creation and relationship_signal rows skipped. Annotated facilities get `abatement_*` properties rendered in popup via `abatementAnnotationHtml()` helper. **5 annotations live:**
  - `Tolivar Power Plant (TEF- Due Diligence)` (ercot_queue, Reeves) ← Pecos Power Plant LLC
  - `Tolivar Power Plant Phase 2` (ercot_queue, Reeves) ← Pecos Power Plant LLC
  - `Tierra Bonita BESS SLF` (ercot_queue, Pecos) ← Greasewood II BESS, LLC
  - `Greasewood II LLC` (eia860_plants, Pecos) ← Greasewood II BESS, LLC (same-parent-family match)
  - `Greasewood II LLC` (solar, Pecos) ← Greasewood II BESS, LLC (same-parent-family match)
- **Match rule tightened mid-chat 85** — initial "≥2 token overlap" rule fired on generic tokens (`ii`, `bess`, `ridge`, `solar`) producing 3 false positives (Elk Ridge Solar, Longfellow BESS II, Sherbino II BESS SLF). Rule reduced to subset-match only.

- **Chat 89 — Trans-Pecos 6-county scrape (2026-04-24):** All 6 counties (Brewster, Culberson, Hudspeth, Jeff Davis, Presidio, Terrell) run on Texas CIRA `state.tx.us` hosting platform (not CivicEngage/CivicPlus). Single-pass scrape yielded **0 new hits**. Adapter type + reason per county:
  - **Brewster** `cira_state` — PDF archive at `/page/open/946/0/*.pdf`, 2023 vintage; no 2025/2026 HTML agendas. §12.3 drop+flag.
  - **Culberson** `cira_state` — `/page/Commissioners.Court` (200) but no agenda archive published; `/page/culberson.agendas` → 403.
  - **Hudspeth** `cira_state` — `/page/hudspeth.commissioner` (200) has 2 non-agenda PDFs; `/page/hudspeth.agendas` → 503.
  - **Jeff Davis** `cira_state` — minutes archive at `/upload/page/6560/` but 2023 vintage only; no 2025/2026 material. §12.3 drop+flag.
  - **Presidio** `cira_state` — 72 recent-year agenda PDFs at `/upload/page/4657/YYYY/*.pdf`. §12.3 drop+flag.
  - **Terrell** `cira_state` — 73 recent-year minutes PDFs at `/upload/page/6319/`. §12.3 drop+flag.
- **Selector regression NOT suspected** for any of the 6. All are genuine "PDF-only per §12.3" or "no HTML agenda archive." Revisit only if (a) any county migrates to CivicEngage/CivicPlus, or (b) operator authorizes a Texas-rural PDF OCR pipeline.
- **Implication for Chat 92+ (Permian-core + peripheral):** CIRA state.tx.us platform is pervasive across rural TX counties; similar coverage gaps expected. A Texas-rural PDF OCR pipeline would unlock ~200 PDFs across Brewster/Jeff Davis/Presidio/Terrell alone; defer to its own sprint rather than blocking the Permian-core wave.
---

## Open backlog

**Standing watch item:** TCEQ diesel-genset NSR permits live only in CRPUB. Revisit only if TCEQ publishes bulk feed or operator authorizes scrape.

**Data-pipeline gaps (non-blocking):**
- `eia860_plants`: 476/1367 rows null `capacity_mw`/`technology`/`fuel`.
- `combined_points.csv` blank `operator` / `commissioned` on EIA point layers.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar.
- ~~Reeves CivicEngage adapter returned 0 rows on first run — URL pattern or selector needs re-verify~~ **RESOLVED Chat 91 (URL-side):** old domain `co.reeves.tx.us` dead; adapter migrated to `reevescounty.org`. New domain Akamai-protected; cloud-runner egress blocked, see infrastructure section below.
- **BEAD `bead_fiber_planned` layer (Chat 91 §1 dropped):** TX Comptroller BDO XLSX trio (`subgrantees`, `deployment-projects`, `locations`) archived to `data/bead_bdo/` but contains no county or coordinates. `locations.xlsx` keys by FCC BSL ID without coords (geocoding requires the licensed FCC BSL Fabric). PAU/award map at `register.broadband.texas.gov` is JS-rendered SPA. NTIA NBAM project-level data is partner-login-gated. Three independent unblock paths documented in `data/bead_bdo/README.md`: (a) BDO Region 1–24 polygon shapefile + project-name region-suffix parser, (b) UEI → SAM.gov HQ geocode for awardee markers, (c) authorized headless-browser scrape of register.broadband.texas.gov vector tiles.

**Infrastructure:**
- `NETLIFY_PAT=` absent from `CREDENTIALS.md`. Netlify MCP proxy path canonical.
- `GITHUB_PAT` can push branches, 403 on PR creation. Operator opens PRs via GitHub UI.
- **Akamai datacenter-egress block on `reevescounty.org` (surfaced Chat 91).** Cloud-runner / GitHub-Actions traffic 403s regardless of UA, header set, or TLS fingerprint. Search-engine crawlers get through (web search confirmed live abatement notices on the new domain Chat 91: August Draw Solar LLC, Energy Forge One LLC, Pecos Power Plant LLC). Hard prerequisite for the abatement-weekly-cron sprint item; structurally affects any future county that migrates to the same CivicEngage hosting platform. Unblock options: residential-proxy egress (paid service), Akamai allowlisting via Reeves County IT (low likelihood), or selector-equivalent fetch via search-API result pages.

**Permanently excluded / settled:**
- `rrc_wells_permian`, `tceq_pws`, `tceq_pbr`, `tceq_nsr_pending` — see `docs/settled.md`.

**UI/UX backlog (unscheduled):**
- Mobile-friendly map — candidate for promotion into `docs/refinement-sequence.md` after abatement sequence completes.

**Other (non-GIS):**
- Grid Wire Vol. 7.
- Tier 2 water availability assessments, cluster intelligence sheets, Excel returns model.

---

## GitHub sync — live

Repo: `github.com/10thMuses/lrp-tx-gis`. Authority: `main` = canonical. Working dir: `/home/claude/repo/`. Protocol: `Readme.md` §7 + `docs/principles.md` §5.
