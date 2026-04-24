# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per Readme §10: **`## Next chat`** = paste-ready for next shipping chat. **`## Sprint queue`** = N+2 and beyond.

---

## Next chat

**Chat 86 — ABATEMENT COUNTY EXPANSION (Trans-Pecos phase).** Chat 85 deployed tax_abatements annotation: fuzzy applicant→facility join, `status` derivation + filter, Matterhorn row. Prod has 9 tax_abatements features + 5 facility annotations. `refinement-abatement-annotate` merged to main, branch deleted from origin.

**This chat's scope (unblocked, ready to execute):**

Per spec §12.2 sequencing, Trans-Pecos phase: scrape commissioners-court agendas for **Brewster, Culberson, Hudspeth, Jeff Davis, Presidio, Terrell** (Pecos already done, Reeves adapter has regression flagged below). Generate `data/abatements/abatement_hits_<timestamp>.csv` with the same schema as `data/abatements/abatement_hits_20260424_092810.csv`. Merge new hits into `combined_points.csv` under layer_id=`tax_abatements` using the same column-mapping conventions (§Prod status).

Sequencing: CivicEngage/CivicPlus adapters first (Brewster, Jeff Davis likely on CivicPlus), then bespoke county sites. PDF-only counties drop out per spec §12.3 — flag in close-out.

**Re-verify Reeves CivicEngage adapter** (regression: 0 hits on first run Chat 82). Pecos Power Plant LLC Reeves abatement was hand-seeded from spec §8 — scraper must reproduce it or explain the miss.

Estimate 3–5 counties per chat; 6 Trans-Pecos counties → 1–2 chats to complete this phase. Permian-core phase follows (Chat 87+).

Expected counterfactual: most Trans-Pecos counties (very rural, low commercial activity) likely produce 0–2 hits per county. Success criterion is completeness, not hit volume.

### Session open (single block)

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
cd /home/claude && rm -rf repo 2>/dev/null
git clone -q https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git repo && cd repo
git config user.email "claude@lrp.local" && git config user.name "Claude (LRP GIS)"
git checkout -b refinement-abatement-transpecos origin/main
apt-get install -y tippecanoe libcairo2 -q
pip install shapely pmtiles pyyaml cairosvg pandas requests beautifulsoup4 --break-system-packages -q
curl -sI -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | head -1
curl -s -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | grep -oE '"id":[ ]*"[a-z0-9_]+"' | sort -u | wc -l   # expect 23
```

### Deploy pattern (CANONICAL)

`NETLIFY_PAT=` absent from `CREDENTIALS.md`. REST-API deploy path is DEAD. Only working path is Netlify MCP → CLI proxy:

1. Call `Netlify:netlify-deploy-services-updater` with `{operation: "deploy-site", params: {siteId: "01b53b80-687e-4641-b088-115b7d5ef638"}}` → returns single-use `--proxy-path` URL.
2. `cd /mnt/user-data/outputs/dist && npx -y @netlify/mcp@latest --site-id 01b53b80-687e-4641-b088-115b7d5ef638 --proxy-path "<URL>" --no-wait` → returns `{"deployId": "...", "buildId": "..."}`.
3. Poll `Netlify:netlify-deploy-services-reader` `get-deploy-for-site` until `state=ready`.
4. `sleep 45` for CDN warm-up (503 at 30s normal; 503 at 75s retry).
5. `curl -sI -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/` → HTTP 200; layer count → 23.

Proxy URL is single-use. On 503 upload error, request a fresh URL from the updater.

### Close-out (NON-NEGOTIABLE, per Readme §10)

Simplified 3-action rule, plus **amendment discipline** (Chat 85 lesson):

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
# If any edits were made AFTER the initial branch push (matcher tightening,
# bug fixes found during build audit), amend and force-push FIRST before merge:
git commit --amend --no-edit
git fetch origin <branch>   # refresh local ref before force-push
git push --force "https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git" <branch>
# Then merge:
git checkout main && git pull --rebase origin main
git fetch origin <branch>   # CRITICAL: refresh local ref to pick up amendment
git merge --no-ff origin/<branch> -m "Merge <branch> (Chat 86): <summary>"
# Rewrite WIP_OPEN.md §Next chat → Chat 87 per §Sprint queue; update §Prod status
git commit -am "Chat 86 close-out" && git push
git push --delete origin <branch>
```

**Chat 85 lesson (merge-freshness):** amending a branch after initial push requires a `git fetch origin <branch>` before `git merge` — otherwise merge pulls the stale local-tracking ref and the amendment is silently lost. Same silent-regression class as Chat 84's sidebar-collapse.

**Merge to main.** `GITHUB_PAT` can push to main directly. No PR step needed.

---

## Sprint queue

Ordered by operator priority. N+2 and beyond.

### Chat 87+ — ABATEMENT COUNTY EXPANSION (Permian-core + peripheral)

Per spec §12.2 sequencing (Trans-Pecos in Chat 86). Remaining order:
Permian-core (Andrews, Ector, Glasscock, Loving, Martin, Midland, Ward,
Winkler) → peripheral (Crane, Crockett, Irion, Reagan, Schleicher, Sutton,
Upton). PDF-only counties dropped per §12.3 and flagged. Estimate 3–5
counties per chat — 4–6 chats to complete after Trans-Pecos.

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
