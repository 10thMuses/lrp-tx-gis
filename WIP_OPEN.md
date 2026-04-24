# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per Readme §10: **`## Next chat`** = paste-ready for next shipping chat. **`## Sprint queue`** = N+2 and beyond.

---

## Next chat

**Chat 83 — ABATEMENT SHIP.** Chat 82 landed scraper + Pecos/Reeves adapters + 9 real Pecos hits on branch `refinement-abatement-build` (HEAD `c4e71ef`). NOT deployed — paused at ~55% budget before transform/yaml/build/deploy to preserve close-out headroom. Stage split per Readme §7.10: scraper = Chat 82, layer ship = Chat 83.

**This chat's scope (unblocked, ready to execute):**

1. Re-run scraper with tightened regex: `python3 scripts/scrape_abatements.py data/abatements/` — verify zone/capacity/project_type fields clean up vs prior run.
2. Add §7 seed rows not captured by scrape: 2025-01-13 Pecos Longfellow zone creation, 2025-06-13 Reeves Pecos Power Plant LLC (226 MW natgas, $150–200M, Enterprise Zone §312.2011), 2025-11-10 Pecos Apex Clean Energy donation (relationship signal, not a filing — include with `flags=relationship_signal`).
3. Transform hits → `combined_points.csv` rows per spec §8 Option A mapping: `layer_id=tax_abatements`, `operator=applicant`, `funnel_stage=status`, `project=reinvestment_zone`, `technology=project_type`, `commissioned=meeting_date`. Geocode: county centroid fallback from `combined_geoms.geojson` county_labels (23 centroids confirmed available, listed below).
4. Append rows to `combined_points.csv` (never full-file read — append only per §9.1).
5. Add `tax_abatements` entry to `layers.yaml` after `water_mains_approx`. Template = `tceq_gas_turbines` pattern (no sprite icon, circle render). Color: `#dc2626` (red — distinct from existing categorical palette). `group: Permits`. `default_on: false`. Popup: name, operator, county, commissioned, project, technology, capacity_mw, agenda_url. Filterable: county (categorical), technology (categorical), commissioned (text/date).
6. Run `python3 build.py`. Expect 23 layers built clean.
7. Deploy via Netlify MCP proxy (canonical path — see below).
8. Verify: curl HTTP 200, layer count = 23.
9. Close-out per §10 (push, WIP_OPEN rewrite, WIP_LOG prepend, main push).

### 23 county centroids (for geocoding fallback, lon/lat pairs)

```
Andrews    -102.636000, 32.304500
Brewster   -103.084723, 29.816000
Crane      -102.540085, 31.490500
Crockett   -101.378010, 30.694000
Culberson  -104.488588, 31.552500
Ector      -102.543000, 31.876500
Glasscock  -101.522000, 31.868500
Hudspeth   -105.406975, 31.303000
Irion      -100.981238, 31.305500
Jeff Davis -104.130042, 30.931000
Loving     -103.569579, 31.820500
Martin     -101.951510, 32.304500
Midland    -102.031250, 31.869000
Pecos      -102.666594, 30.727000
Presidio   -104.238482, 29.942500
Reagan     -101.524747, 31.366000
Reeves     -103.645106, 31.381500
Schleicher -100.538514, 30.901500
Sutton     -100.538000, 30.500000
Terrell    -102.162869, 30.165000
Upton      -102.042750, 31.364000
Ward       -103.126510, 31.466000
Winkler    -103.063837, 31.830500
```

### Session open (single block)

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
cd /home/claude && rm -rf repo 2>/dev/null
git clone -q https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git repo && cd repo
git config user.email "claude@lrp.local" && git config user.name "Claude (LRP GIS)"
git checkout refinement-abatement-build              # resume branch, not new
git log --oneline main..HEAD                          # verify c4e71ef is HEAD
apt-get install -y tippecanoe libcairo2 -q
pip install shapely pmtiles pyyaml cairosvg pandas beautifulsoup4 requests --break-system-packages -q
```

### Deploy pattern (CANONICAL — confirmed Chat 81)

`NETLIFY_PAT=` line removed from `CREDENTIALS.md`. **REST-API deploy path is DEAD.** Only working deploy path is Netlify MCP → CLI proxy:

1. Call `Netlify:netlify-deploy-services-updater` MCP tool with `{operation: "deploy-site", params: {siteId: "01b53b80-687e-4641-b088-115b7d5ef638"}}` → returns `--proxy-path` URL (one-time token, single use).
2. `cd /mnt/user-data/outputs/dist && npx -y @netlify/mcp@latest --site-id 01b53b80-687e-4641-b088-115b7d5ef638 --proxy-path "<URL>" --no-wait` — returns `{"deployId": "...", "buildId": "..."}` on stdout.
3. Poll state via `Netlify:netlify-deploy-services-reader` `get-deploy-for-site` until `state=ready`.
4. `sleep 45` for CDN warm-up (503 at 30s normal; 503 at 75s retry).
5. Curl-verify: `curl -sI -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/` → HTTP 200; layer count → 23.

### PR + close-out (NON-NEGOTIABLE)

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
git push "https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git" refinement-abatement-build
```

Then on `main`:
- Rewrite `## Next chat` → Chat 84 promotion.
- Prepend `WIP_LOG.md` entry for Chat 83.
- `git commit -am "Chat 83 close-out" && git push`

**Token-budget rule (Readme §10):** stop active work at ~65%. Reserve ~35% for close-out.

### Known constraint (carried from Chat 79)

`GITHUB_PAT` lacks PR-creation scope — 403 on POST `/repos/.../pulls`. Branch push works; PR opened by operator via GitHub UI.

---

## Sprint queue

### Chat 84 — ABATEMENT ANNOTATION + FILTER UI

From spec §12.1 (locked): join `tax_abatements` hits to `eia860_plants`, `ercot_queue`, `solar`, `wind`, `eia860_battery`, future `dc_sites` by fuzzy applicant name + county + approx coords. Single pass, no iterative refinement. Add `abatement_*` fields to popups of matched facilities. Also: filter UI controls for `technology` / `commissioned` / `status` on the tax_abatements layer.

### Chat 85 — ABATEMENT COUNTY EXPANSION (21 unverified adapters)

Per spec §12.2 sequencing: Trans-Pecos (Brewster, Culberson, Hudspeth, Jeff Davis, Presidio, Terrell) → Permian-core (Andrews, Ector, Glasscock, Loving, Martin, Midland, Ward, Winkler) → peripheral (Crane, Crockett, Irion, Reagan, Schleicher, Sutton, Upton). Per spec §12.3 PDF-only counties dropped; flag in deliverable. URL research + adapter write per county; estimate 3–5 counties per chat given adapter pattern overhead.

### Chat 86 — ABATEMENT WEEKLY CRON

`.github/workflows/abatement-scrape.yml`. Cron weekly Monday 06:00 UTC. Commit diff to `data/abatements/abatement_hits_latest.csv` + rolling history. Alerting deferred per §12.8.

### Chat 87+ — Mobile-friendly map

UI/UX stage. Responsive breakpoints, touch-friendly controls, pinch-zoom tuning, measure tool + print-to-PDF mobile usability, popup sizing. Candidate for promotion into `docs/refinement-sequence.md`.

### Outstanding PR merges (operator)

- `refinement-ui-polish-v2` → `main` (Chat 79). Prod reflects via deploy `69ea9d1b8b51ad96ce674f5d`. Cleanup only.
- `refinement-sidebar-collapse` → `main` (Chat 81). Prod reflects via deploy `69eaf518997b708751d871bf`. Cleanup only.
- `refinement-abatement-build` → `main` (Chat 82 partial). Will be extended by Chat 83 before final merge. **Do not merge until Chat 83 ships layer.**

### Operator data ask (spec §12.5, non-blocking)

Comptroller Ch. 312 abatement registry spreadsheet — manual quarterly download from `comptroller.texas.gov`. Serves as authoritative statewide baseline + backstop for county scrape failure. Can land in Chat 84 or later. Drop in `/mnt/user-data/uploads/` when downloaded.

---

## Current workstream

ABATEMENT BUILD in progress across Chats 82–83. Chat 82 shipped scraper infrastructure + real data extraction (9 Pecos hits with AI-DC and BESS signal). Chat 83 completes the layer ship (transform + yaml + build + deploy). Chat 84 extends to facility annotation + filter UI. Chat 85 expands to 21 remaining county adapters. Chat 86 adds weekly cron.

Stage split rationale: original §12-scoped BUILD comprised 5+ distinct subsystems (scraper, transform/geocode, yaml/build/deploy, annotation, filter UI, workflow) — per Readme §7.10 split before continuing. Scraper was the first splittable unit and closed out cleanly.

---

## Recent sessions

| Chat | Date | Outcome |
|---:|---|---|
| 72 | 2026-04-23 | TCEQ REFRESH recon + data pull. 6 records geocoded. |
| 73 | 2026-04-23 | TCEQ refresh branch merged to main — `ea7e39d`. |
| 74 | 2026-04-23 | TCEQ data/config + EIA-860 research committed — `4292bf2`, `3aada1c`. |
| 75 | 2026-04-23 | Abatement discovery spec + multi-chat refinement rules — `92d25c72`. |
| 75b | 2026-04-23 | **TCEQ SHIP complete.** Deploy `69ea32c7d3733641c9a1bb7c`. 21→22 layers. |
| 76 | 2026-04-23 | **UI polish shipped.** 10 label/layout tweaks — `a379539`. |
| 77 | 2026-04-23 | **EIA-860 enrichment shipped.** 891/1367 plants enriched — `9d40df4`, deploy `69ea73f92acb1109e87b4ddc`. |
| 78 | 2026-04-23 | **MW-driven sizing shipped.** `f334601`, deploy `69ea83a786cf7142db291f87`. |
| 79 | 2026-04-23 | **UI POLISH v2 shipped.** Branch commit `c8ff838`, deploy `69ea9d1b8b51ad96ce674f5d`. PR pending. |
| 80 | 2026-04-24 | SIDEBAR COLLAPSE partial — CSS/HTML/hash only. Branch commit `bdc1fb6`. Token-paused. |
| 81 | 2026-04-24 | **SIDEBAR COLLAPSE shipped.** Branch commit `6d356cd`, deploy `69eaf518997b708751d871bf`. Readme §10 close-out discipline codified. |
| 82 | 2026-04-24 | **ABATEMENT BUILD partial: scraper shipped.** Branch commit `c4e71ef`. `scripts/scrape_abatements.py` + 9 Pecos hits (CoreWeave, Poolside, Silver Basin Digital, Greasewood II BESS, Bighorn Ridge Solar, Matterhorn). Reeves returned 0 (URL re-verify). 2 post-run regex tightenings. Stage split per §7.10: layer ship → Chat 83. NOT deployed. |

Full per-session detail in `WIP_LOG.md`.

---

## Prod status

- URL: https://lrp-tx-gis.netlify.app — requires real User-Agent on curl (`-A "Mozilla/5.0"`).
- Last published deploy: `69eaf518997b708751d871bf` on branch commit `6d356cd` (Chat 81, `refinement-sidebar-collapse`). **Chat 82 did not deploy.**
- Main HEAD will advance with Chat 82 close-out (this rewrite + WIP_LOG prepend).
- Auto-publish: unlocked.
- **Deploy path: Netlify MCP → CLI proxy.** REST-API dead.
- Layer set: **22 built clean** (Chat 83 will advance to 23 with `tax_abatements`).
- Prebuilt PMTiles (4): `parcels_pecos` 4.98 MB, `rrc_pipelines` 4.73 MB, `tiger_highways` 3.11 MB, `bts_rail` 2.16 MB.
- Sprite sheet: 5 icons @ 1x + 2x at `/sprite/sprite.png` + `sprite@2x.png`.
- Data-driven sizing live: `ercot_queue`, `solar`, `eia860_plants`, `eia860_battery`, `wind`; `substations`, `tpit_subs`, `tpit_lines`.
- UI state: sidebar collapsible (`#sb=1`); `parcels_pecos` sidebar-hidden; default-ON layers; default basemap = esri_imagery; default viewport = -102.9707/30.9112 z12.
- Sizing gaps (static fallback): `eia860_plants` 476/1367 null; `transmission` no voltage.
- **CDN warmup timing:** 45–75s post-deploy.

---

## Open backlog

**Standing watch item:** TCEQ diesel-genset NSR permits live only in CRPUB. Revisit only if TCEQ publishes bulk feed or operator authorizes scrape.

**Data-pipeline gaps (non-blocking):**
- `eia860_plants`: 476/1367 rows null `capacity_mw`/`technology`/`fuel`.
- `combined_points.csv` blank `operator` / `commissioned` on EIA point layers.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar.
- Reeves CivicEngage adapter returned 0 rows on first run — URL pattern or selector needs re-verify Chat 83 or Chat 85.

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
