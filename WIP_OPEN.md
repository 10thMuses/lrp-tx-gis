# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per Readme §10: **`## Next chat`** = paste-ready for next shipping chat. **`## Sprint queue`** = N+2 and beyond.

---

## Next chat

**Chat 93 — CHAT 92 MERGE + DOC RESTRUCTURE LAND.** Merge-only close-out. No build, no deploy. Chat 92 prod deploy `69ed2cdf4039c554a1316ad2` already published, verified, and serving.

### Task

1. Merge `refinement-chat92-field-expansion-wells` to main. Branch tip is 4 commits ahead of `origin/main`; tree carries Chat 92 §1-§3 work AND a doc restructure (Readme.md / GIS_SPEC.md / docs/principles.md / docs/settled.md / WIP_LOG.md added; ARCHITECTURE.md / OPERATING.md / docs/sidebar/ / scripts/{close-out,audit,deploy,ship,pre-commit} removed).
2. **Resolve `build.py` conflict by taking main's version.** Both sides independently fixed merge_csv/merge_geojson temp+rename guard per §6 #15. Main's form (`Path.with_suffix()` + explicit cleanup) is functionally equivalent to branch's (`str(out_path) + '.tmp'`); main's already integrated into other paths. Use `git checkout --theirs build.py` after the merge halts on conflict, then `git add build.py`.
3. Push main, delete origin branch.
4. Rewrite this `## Next chat` block. Default candidate: POWER PLANT DATA REFRESH per sprint queue. Operator may redirect.

### Acceptance

- Main HEAD merge commit message references deploy `69ed2cdf4039c554a1316ad2`.
- Main tree contains `Readme.md`, `GIS_SPEC.md`, `docs/principles.md`, `docs/settled.md`, `WIP_LOG.md`; lacks `ARCHITECTURE.md`, `OPERATING.md`, `docs/sidebar/`. Aligns with sidebar pointer docs (`/mnt/project/Commands.md`, `Environment.md`).
- `refinement-chat92-field-expansion-wells` deleted from origin.
- Prod unchanged at `69ed2cdf4039c554a1316ad2`. No re-deploy.

### Session open

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
cd /home/claude && rm -rf repo 2>/dev/null
git clone -q https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git repo && cd repo
git fetch origin refinement-chat92-field-expansion-wells
```

No tippecanoe / python deps needed; merge-only chat.

### Pre-flight

Chat 92 §1-§3 fully shipped to prod 2026-04-25. Branch tip `38f8654`. Merge-base `3950736` had the new doc structure but main HEAD `1ded060` ("Audit-3 sidebar pointers + WIP_OPEN trim + sprint-plan lift") regressed it — merge restores what operator's sidebar pointers describe as canonical.

`build.py` conflict expected and resolution prescribed (take main's, see Task §2). No other conflicts anticipated per pre-merge dry-run during Chat 92.

### Close-out (NON-NEGOTIABLE, per Readme §10)

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
git checkout main && git pull --rebase origin main
git merge --no-ff origin/refinement-chat92-field-expansion-wells \
  -m "Merge refinement-chat92-field-expansion-wells (Chat 92): tceq_gas_turbines popup expansion + tax_abatements popup rename + wells min_zoom raise + doc restructure (deploy 69ed2cdf4039c554a1316ad2)"
# On build.py conflict:
#   git checkout --theirs build.py  (--theirs = main's version per Task §2)
#   git add build.py
#   git commit  (uses prepared merge message)
# Rewrite WIP_OPEN.md §Next chat → Chat 94 (operator-priority)
# §Prod status: leave at 69ed2cdf4039c554a1316ad2 (no new deploy this chat)
git add WIP_OPEN.md && git commit -m "Chat 93 close-out: WIP_OPEN.md rewrite for Chat 94"
git push origin main
git push origin --delete refinement-chat92-field-expansion-wells
```

**Carry-forward backlog additions** (already in `## Open backlog` — confirm at close-out):
- `date_range` filter type implementation: touches `build.py compute_filter_stats` + `build_template.html filterFieldControlHtml` + matching predicate. `tax_abatements.commissioned` ships as `text` multi-select dropdown today.
- Audit-3 regression investigation: why `1ded060` reverted Readme.md / GIS_SPEC.md / principles.md / settled.md when commit message describes only sidebar pointer / WIP trim / sprint-plan lift work.

**Credential hygiene carry-forward:** `GITHUB_PAT` leak from Chat 87 unrotated per operator override. Token valid until 2027-04-21.

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
- **Chat 92 closed 2026-04-25** — `tceq_gas_turbines` popup expansion (8→12 fields, new popup_labels block, filterable_fields rebuilt 4→7 incl. funnel_stage Status filter); `tax_abatements` display-layer rename Commissioned→Approved date (popup 14→10 fields, filters 2→5); `wells` min_zoom 6→10. Layer count unchanged at 25.
- **Chat 90 closed 2026-04-25** — FCC fiber coverage layer shipped: `fcc_fiber_coverage` H3 res-8 hexes built from FCC BDC fixed-availability CSV (FTTP filter, 23-county Permian-focus footprint). Layer count 24 → 25.
- URL: https://lrp-tx-gis.netlify.app — requires real User-Agent on curl (`-A "Mozilla/5.0"`).
- Last published deploy: `69ed2cdf4039c554a1316ad2` (Chat 92 close-out, 2026-04-25). Supersedes `69ec91f62150e8257e82413d`. State=ready. Layer count 25 live. Verified via parsed `LAYERS=` JSON: `wells.min_zoom=10`, `tceq_gas_turbines` popup=12 fields, `tax_abatements` popup=10 with `commissioned` label="Approved date".
- Previous deploy: `69ec91f62150e8257e82413d` (Chat 90 close-out, 2026-04-25). `fcc_fiber_coverage` renders as cyan choropleth on `max_down_mbps` (3 bins: ≥1000 / 100–999 / <100), `default_on: false`, popup shows all six aggregate fields.
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

**UI/UX gaps:**
- **`date_range` filter type not implemented** (carryforward Chat 92). Build system supports only categorical / numeric / text. `tax_abatements.commissioned` ships as `text` (multi-select dropdown of distinct ISO dates — functional with 9 rows, not a true range slider). Implementation touches `build.py compute_filter_stats` + `build_template.html filterFieldControlHtml` + matching predicate.

**Doc-state anomaly (Chat 92 surfaced):**
- `origin/main` HEAD `1ded060` ("Audit-3 sidebar pointers + WIP_OPEN trim + sprint-plan lift") regressed the doc restructure that was on merge-base `3950736` (removed Readme.md / GIS_SPEC.md / docs/principles.md / docs/settled.md / WIP_LOG.md, restored ARCHITECTURE.md / OPERATING.md / scripts/{close-out,audit,deploy,ship,pre-commit}). Effect did not match commit message scope. Chat 93 merge restores the new structure. Investigate root cause to prevent recurrence — likely candidates: merge onto stale base, accidental `git add -A` on a working tree with old files, or a force-push.

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
