# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per Readme §10: **`## Next chat`** = paste-ready for next shipping chat. **`## Sprint queue`** = N+2 and beyond.

---

## Next chat

**Chat 87 (resume) — FINISH STYLING + CARAMBA LABEL.** All pre-build edits shipped to branch `refinement-chat87-styling` as commit `c81ebb5` (pushed 2026-04-24). **Do NOT create a new branch. Do NOT re-execute the edits.** Checkout the existing branch and proceed to build + deploy + merge.

Pre-build state on branch:
- `layers.yaml`: `waha_circle` inserted before `labels_hubs`; `tiger_highways` has `line_width: 0.6`; `caramba_north` is green (`#2E7D32`) + label `1,300 ac`.
- `build_template.html`: `sizingLineWidthExpr` baseline reads `L.line_width ?? 2`; `layerPaint()` point block reads optional `circle_radius` / `stroke_color` / `stroke_width` / `fill_opacity`.
- `combined_geoms.geojson`: Waha feature duplicated with `layer_id: 'waha_circle'` (1 feature).

Remaining tasks:

1. Build (`python3 build.py`) — expect 24 layers clean.
2. Deploy via Netlify MCP → CLI proxy (canonical path below).
3. Verify: HTTP 200 + layer-id grep returning 24. **If verification fails, halt. Do not merge or close out. Report and stop.** A bad build that reaches close-out silently consumes the sprint queue.
4. Visual verification: tiger_highways thinner at z=8; Waha yellow ring visible; Caramba North green + "1,300 ac" label.
5. Merge branch to main per amended-branch protocol (§Chat 85 lesson: `git fetch origin refinement-chat87-styling` before `git merge`); delete branch.
6. **Close-out (non-negotiable):**
   - Open `docs/sprint-plan.md`, copy §Chat 88 section verbatim into `WIP_OPEN.md §Next chat` (replacing this Chat 87-resume block entirely).
   - Delete §Chat 87 section from `docs/sprint-plan.md`.
   - Update §Prod status with new deployId and bump layer count to 24.
   - Commit to main: `"Chat 87 close-out"`.

**Out of scope for this chat (deferred to next housekeeping chat):** stranded branches `chat76-wip` and `refinement-tceq-refresh` on origin. A placeholder entry for their cleanup has been added to §Sprint queue below under "STRANDED BRANCH CLEANUP" — do not touch them in this chat.

Credential hygiene: `GITHUB_PAT` was leaked in a push-URL echo during Chat 87 edit session. Rotate before next chat runs and update `CREDENTIALS.md` on main. If rotation hasn't happened, the next chat should halt and flag before pushing.

Expected layer count post-build: **24** (23 baseline + `waha_circle`).

### Session open (single block)

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
cd /home/claude && rm -rf repo 2>/dev/null
git clone -q https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git repo && cd repo
git config user.email "claude@lrp.local" && git config user.name "Claude (LRP GIS)"
git checkout refinement-chat87-styling   # EXISTING branch, do not recreate
git log --oneline -3                      # verify HEAD is c81ebb5
apt-get install -y tippecanoe libcairo2 -q
pip install shapely pmtiles pyyaml cairosvg pandas --break-system-packages -q
curl -sI -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | head -1
curl -s -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | grep -oE '"id":"[a-z_][a-z0-9_]*"' | sort -u | wc -l   # expect 23 pre-deploy, 24 post-deploy
```

### Deploy pattern (CANONICAL)

`NETLIFY_PAT=` absent from `CREDENTIALS.md`. REST-API deploy path is DEAD. Only working path is Netlify MCP → CLI proxy:

1. Call `Netlify:netlify-deploy-services-updater` with `{operation: "deploy-site", params: {siteId: "01b53b80-687e-4641-b088-115b7d5ef638"}}` → returns single-use `--proxy-path` URL.
2. `cd /mnt/user-data/outputs/dist && npx -y @netlify/mcp@latest --site-id 01b53b80-687e-4641-b088-115b7d5ef638 --proxy-path "<URL>" --no-wait` → returns `{"deployId": "...", "buildId": "..."}`.
3. Poll `Netlify:netlify-deploy-services-reader` `get-deploy-for-site` until `state=ready`.
4. `sleep 45` for CDN warm-up (503 at 30s normal; 503 at 75s retry).
5. `curl -sI -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/` → HTTP 200; layer count → 24.

Proxy URL is single-use. On 503 upload error, request a fresh URL from the updater.

### Close-out (NON-NEGOTIABLE, per Readme §10)

Per Readme §10 "Sprint-plan doc" rule: close-out re-reads downstream briefs in `docs/sprint-plan.md` (§Chat 88–91); edits any whose assumptions changed; promotes Chat 88 brief to §Next chat; deletes Chat 87 section from sprint-plan.md.

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
# If branch was amended post-push (bug fix during build audit):
git commit --amend --no-edit
git fetch origin refinement-chat87-styling
git push --force "https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git" refinement-chat87-styling
# Merge:
git checkout main && git pull --rebase origin main
git fetch origin refinement-chat87-styling
git merge --no-ff origin/refinement-chat87-styling -m "Merge refinement-chat87-styling (Chat 87): tiger_highways thinner + waha_circle + caramba green + caramba label"
# Rewrite WIP_OPEN.md §Next chat → Chat 88 brief (full paste-ready, from sprint-plan.md §Chat 88)
# Edit docs/sprint-plan.md: delete §Chat 87 section; re-read §Chat 88–91 and edit if Chat 87 changed assumptions
# Update §Prod status
git commit -am "Chat 87 close-out" && git push
git push --delete origin refinement-chat87-styling
```

**Chat 85 lesson (merge-freshness):** amending a branch after initial push requires a `git fetch origin <branch>` before `git merge` — otherwise merge pulls the stale local-tracking ref and the amendment is silently lost.

**Merge to main.** `GITHUB_PAT` can push to main directly. No PR step needed.

---

## Sprint queue

Ordered by operator priority. N+2 and beyond. Multi-chat active sprint detail lives in `docs/sprint-plan.md`; one-paragraph pointers below.

### Chat 88 — ABATEMENT REFACTOR

Schema refactor on existing 9-row tax_abatements layer. Label rename to "Property Tax Abatements (Ch.312 / LDAD, new or expansion)"; drop meeting-date filter; add 8 new column mappings (mw→project MW, capacity→capex, zone→abatement term, use→schedule, year→announcement year, entity→developer, cap_kw→jobs, sector→taxing entities); rewrite popup order + filter UI; back-populate existing 9 rows. No new data. Layer count unchanged at 24. Full brief: `docs/sprint-plan.md` §Chat 88.

### Chat 89 — ABATEMENT TRANS-PECOS EXPANSION

Scrape Brewster, Culberson, Hudspeth, Jeff Davis, Presidio, Terrell. Gas + renewable filter. Single-pass; 0-hit counties flagged. Reeves deferred to Chat 91. Uses Chat 88's schema (not Chat 85's). Layer count unchanged at 24. Full brief: `docs/sprint-plan.md` §Chat 89.

### Chat 90 — FCC FIBER COVERAGE

New `fcc_fiber_coverage` layer. FCC BDC Texas CSV, FTTP filter (technology_code=50, low_latency=1), H3 res 8 aggregation across 23 counties, 3-bin choropleth on max_down_mbps, cyan palette, default OFF. Layer count 24 → 25. Full brief: `docs/sprint-plan.md` §Chat 90.

### Chat 91 — BEAD FIBER PLANNED + REEVES RE-VERIFY

Conditional `bead_fiber_planned` layer (TX Comptroller BEAD map primary; NTIA fallbacks; 30-min ship rule). Plus Reeves CivicEngage adapter re-verify. Layer count 25 → 26 if BEAD ships, 25 if dropped. Closes the active sprint — `docs/sprint-plan.md` deleted at close-out. Full brief: `docs/sprint-plan.md` §Chat 91.

### Chat 92+ — ABATEMENT PERMIAN-CORE + PERIPHERAL

Permian-core (Andrews, Ector, Glasscock, Loving, Martin, Midland, Ward, Winkler) → peripheral (Crane, Crockett, Irion, Reagan, Schleicher, Sutton, Upton). PDF-only counties dropped per spec §12.3. 4–6 chats. Reeves-shared-CMS counties pick up whatever the Chat 91 adapter re-verify yields. Promoted to `docs/sprint-plan.md` when it enters the active 5-chat window.

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
drift if selectors break (no alerting in v1).

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

- URL: https://lrp-tx-gis.netlify.app — requires real User-Agent on curl (`-A "Mozilla/5.0"`).
- Last published deploy: `69eb7bccd5cbc81ee84c32c0` (Chat 85, 2026-04-24 14:18:57Z). State=ready, CDN-verified, 23 layer ids live, 9 tax_abatements features, 5 facility annotations (Tolivar ×2 in Reeves, Tierra Bonita BESS + Greasewood II LLC ×2 in Pecos). Supersedes `69eb707c56bb04f8c221f5af`.
- Main HEAD includes `refinement-abatement-annotate` (merged Chat 85) + tightened-matcher follow-up commit. Branch deleted from origin.
- Auto-publish: unlocked.
- **Deploy path: Netlify MCP → CLI proxy.** REST-API dead.
- Layer set: **23 built clean**.
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

---

## Open backlog

**Standing watch item:** TCEQ diesel-genset NSR permits live only in CRPUB. Revisit only if TCEQ publishes bulk feed or operator authorizes scrape.

**Data-pipeline gaps (non-blocking):**
- `eia860_plants`: 476/1367 rows null `capacity_mw`/`technology`/`fuel`.
- `combined_points.csv` blank `operator` / `commissioned` on EIA point layers.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar.
- Reeves CivicEngage adapter returned 0 rows on first run — URL pattern or selector needs re-verify Chat 86 (Pecos Power Plant LLC Reeves row remains hand-seeded from spec §8).

**Infrastructure:**
- `NETLIFY_PAT=` absent from `CREDENTIALS.md`. Netlify MCP proxy path canonical.
- `GITHUB_PAT` can push branches, 403 on PR creation. Operator opens PRs via GitHub UI.

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
