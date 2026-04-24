# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per Readme §10: **`## Next chat`** = paste-ready for next shipping chat. **`## Sprint queue`** = N+2 and beyond.

---

## Next chat

**Chat 88 — ABATEMENT REFACTOR (no new data).** Schema refactor on the existing 9-row `tax_abatements` layer. No new scrapes this chat. No layer count change (stays at 24).

### Tasks

1. **Label rename.** `layers.yaml` tax_abatements `label: "Tax Abatements"` → `"Property Tax Abatements (Ch.312 / LDAD, new or expansion)"`. If sidebar truncation is ugly, keep concise version and add full text to popup header or tooltip.

2. **Sidebar tooltip / popup header.** Add description: "County-level property tax abatements for new or expanded facilities. Chapter 312 reinvestment zones and Local Development Agreements (HB 5 / SB 1340 successors to the sunsetted Ch.313)." Implementation: new `description` key in `layers.yaml` per-layer, template renders it as popup-header text or sidebar `title` attribute. Requires template patch — inspect existing popup builder before editing to avoid schema collision.

3. **Drop meeting-date filter.** Remove `{field: commissioned, type: text, label: Meeting Date}` from tax_abatements `filterable_fields`. Leave `commissioned` column populated (for back-compat with existing 9 rows) but not user-facing.

4. **Column remapping — new fields.** Additive to Chat 85 mapping; columns exist in CSV schema but were unpopulated.

   | CSV column  | Abatement field          |
   |-------------|--------------------------|
   | `mw`        | project MW               |
   | `capacity`  | capex ($M)               |
   | `zone`      | abatement term (yrs)     |
   | `use`       | abatement schedule       |
   | `year`      | announcement year        |
   | `entity`    | developer                |
   | `cap_kw`    | jobs commitment          |
   | `sector`    | taxing entities          |

   Preserved Chat 85 mappings (unchanged): `poi`=agenda_url, `funnel_stage`=flags (status derived at build time), `operator`=applicant, `project`=reinvestment_zone, `technology`=project_type, `commissioned`=meeting_date.

5. **Popup order.** name, operator, entity, county, technology, mw, capacity, zone, use, cap_kw, project, sector, status, poi. Update `layers.yaml` tax_abatements `popup` list accordingly.

6. **Filter UI.** `filterable_fields`: technology, status only. Drop county, commissioned. No other filters.

7. **Back-populate Chat 85's 9 rows** where spec data supports the new fields. Matterhorn row (meeting date 2022-07-25): recover `year` (announcement year) from the agenda PDF if possible. If not recoverable, skip and note in §Abatement layer notes.

### Acceptance

- Layer count: 24 (unchanged).
- tax_abatements label, popup, filter UI reflect new schema.
- 9 existing rows still render, with new fields populated where spec data available.
- Build report `errored == 0`; dropped-features <5%.

### Close-out

Deploy → merge branch `refinement-chat88-abatement-refactor` → delete branch → promote Chat 89 brief to §Next chat → remove Chat 88 section from `docs/sprint-plan.md` → push.

### Session open (single block)

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
cd /home/claude && rm -rf repo 2>/dev/null
git clone -q https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git repo && cd repo
git config user.email "claude@lrp.local" && git config user.name "Claude (LRP GIS)"
git checkout -b refinement-chat88-abatement-refactor
apt-get install -y tippecanoe libcairo2 -q
pip install shapely pmtiles pyyaml cairosvg pandas --break-system-packages -q
curl -sI -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | head -1
curl -s -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | grep -oE '"id":"[a-z_][a-z0-9_]*"' | sort -u | wc -l   # expect 24
```

### Deploy pattern (CANONICAL)

`NETLIFY_PAT=` absent from `CREDENTIALS.md`. REST-API deploy path is DEAD. Only working path is Netlify MCP → CLI proxy:

1. Call `Netlify:netlify-deploy-services-updater` with `{operation: "deploy-site", params: {siteId: "01b53b80-687e-4641-b088-115b7d5ef638"}}` → returns single-use `--proxy-path` URL.
2. `cd /mnt/user-data/outputs/dist && npx -y @netlify/mcp@latest --site-id 01b53b80-687e-4641-b088-115b7d5ef638 --proxy-path "<URL>" --no-wait` → returns `{"deployId": "...", "buildId": "..."}`.
3. Poll `Netlify:netlify-deploy-services-reader` `get-deploy-for-site` until `state=ready`.
4. `sleep 45` for CDN warm-up (503 at 30s normal; 503 at 75s retry).
5. `curl -sI -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/` → HTTP 200; layer count → 24.

Proxy URL is single-use. On 503 upload error, request a fresh URL from the updater.

### Pre-flight: Netlify edge status check

Chat 87 deploy succeeded cleanly but post-deploy curl verification returned HTTP 503 `DNS cache overflow` across the entire Netlify edge (`netlify.com` itself also 503) from 16:07Z onward, 2+ hours continuous. This was a Netlify infrastructure outage, not our build. Chat 87 close-out proceeded without live verification per operator direction.

**At Chat 88 session-open, first check edge is up** before starting work: `curl -sI https://www.netlify.com/ | head -1` — if 503, halt and flag. If 200, proceed. Also verify Chat 87 deploy actually serves correctly: `curl -s https://lrp-tx-gis.netlify.app/ | grep -oE '"id":"[a-z_][a-z0-9_]*"' | sort -u | wc -l` → expect 24. If count mismatches, flag before building anything new (the last recorded good state is deployId `69eb952306288390a3d6a3c0`).

### Close-out (NON-NEGOTIABLE, per Readme §10)

Per Readme §10 "Sprint-plan doc" rule: close-out re-reads downstream briefs in `docs/sprint-plan.md` (§Chat 89–91); edits any whose assumptions changed; promotes Chat 89 brief to §Next chat; deletes Chat 88 section from sprint-plan.md.

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
git fetch origin refinement-chat88-abatement-refactor
git checkout main && git pull --rebase origin main
git merge --no-ff origin/refinement-chat88-abatement-refactor -m "Merge refinement-chat88-abatement-refactor (Chat 88): tax_abatements schema refactor"
# Rewrite WIP_OPEN.md §Next chat → Chat 89 brief (full paste-ready, from sprint-plan.md §Chat 89)
# Edit docs/sprint-plan.md: delete §Chat 88 section; re-read §Chat 89–91 and edit if Chat 88 changed assumptions
# Update §Prod status
git commit -am "Chat 88 close-out" && git push
git push --delete origin refinement-chat88-abatement-refactor
```

**Merge to main.** `GITHUB_PAT` can push to main directly. No PR step needed.

**Credential hygiene carry-forward:** `GITHUB_PAT` leak from Chat 87 edit session remains unrotated per operator override (Chat 87 resume, 2026-04-24). Rotation is still recommended but no longer a blocking condition; the exposed token will remain valid until 2027-04-21 or manual rotation. Flag again in Chat 88 close-out if still outstanding.

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
- Last published deploy: `69eb952306288390a3d6a3c0` (Chat 87, 2026-04-24 16:07:08Z). State=ready, Netlify API confirmed all files uploaded + 1 redirect + 2 header rules processed, 0 errors. **CDN verification was NOT completed this chat**: `netlify.com` itself + our site + deploy permalink all returned HTTP 503 `DNS cache overflow` continuously from 16:07Z through 18:21Z+ (2hr 14min) — Netlify-wide edge outage, not our deploy. Chat 87 close-out proceeded without live-curl verification per operator direction. First curl after edge recovery should return HTTP 200 + 24 layer ids. Supersedes `69eb7bccd5cbc81ee84c32c0`.
- Main HEAD includes `refinement-chat87-styling` (merged Chat 87, commit `7005f67`). Branch deleted from origin.
- Auto-publish: unlocked.
- **Deploy path: Netlify MCP → CLI proxy.** REST-API dead.
- Layer set: **24 built clean** (23 baseline + `waha_circle` added Chat 87).
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
