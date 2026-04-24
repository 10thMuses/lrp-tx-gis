# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per Readme §10: **`## Next chat`** = paste-ready for next shipping chat. **`## Sprint queue`** = N+2 and beyond.

---

## Next chat

**Chat 85 — ABATEMENT ANNOTATION + FILTER UI.** Chat 84 deployed the `tax_abatements` layer (8 features, 23 layers live) and merged `refinement-abatement-build` into `main`. Feature branch deleted from origin.

**This chat's scope (unblocked, ready to execute):**

Per spec §12.1 (locked): join `tax_abatements` hits to `eia860_plants`, `ercot_queue`, `solar`, `wind`, `eia860_battery`, and future `dc_sites` by fuzzy applicant name + county + approximate coordinates. Single pass, no iterative refinement. Surface matched `abatement_*` fields in popups of the matched facilities. Add filter UI controls for `technology` / `commissioned` / `status` on the `tax_abatements` layer.

Re-include the Matterhorn row skipped Chat 83 (no meeting date captured — resolve via agenda PDF re-scrape or operator-provided date). Account for column-mapping caveats in §Prod status below when writing join keys and filter predicates.

### Session open (single block)

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
cd /home/claude && rm -rf repo 2>/dev/null
git clone -q https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git repo && cd repo
git config user.email "claude@lrp.local" && git config user.name "Claude (LRP GIS)"
git checkout -b refinement-abatement-annotate origin/main
apt-get install -y tippecanoe libcairo2 -q
pip install shapely pmtiles pyyaml cairosvg pandas --break-system-packages -q
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

### Close-out (NON-NEGOTIABLE, per Readme §10)

Simplified 3-action rule:

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
git push "https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git" refinement-abatement-annotate
# then on main:
git checkout main && git pull --rebase origin main
# rewrite WIP_OPEN.md §Next chat → Chat 86 per §Sprint queue; update §Prod status
git commit -am "Chat 85 close-out" && git push
```

No `WIP_LOG.md` append. No `## Recent sessions` row. Both sections removed Chat 83a.

**Merge to main.** `GITHUB_PAT` can push to main directly. Merge feature branch locally via `git merge --no-ff origin/<branch>` and push, then `git push --delete origin <branch>` to clean up. No PR step needed. (Per Chat 84a: prior "operator merge" rule is obsolete — PAT lacked PR-creation scope, not merge-to-main capability.)

---

## Sprint queue

### Chat 86 — ABATEMENT COUNTY EXPANSION (21 unverified adapters)

Per spec §12.2 sequencing: Trans-Pecos (Brewster, Culberson, Hudspeth, Jeff Davis, Presidio, Terrell) → Permian-core (Andrews, Ector, Glasscock, Loving, Martin, Midland, Ward, Winkler) → peripheral (Crane, Crockett, Irion, Reagan, Schleicher, Sutton, Upton). Per spec §12.3 PDF-only counties dropped; flag in deliverable. URL research + adapter write per county; estimate 3–5 counties per chat given adapter pattern overhead.

### Chat 87 — ABATEMENT WEEKLY CRON

`.github/workflows/abatement-scrape.yml`. Cron weekly Monday 06:00 UTC. Commit diff to `data/abatements/abatement_hits_latest.csv` + rolling history. Alerting deferred per §12.8.

### Chat 88+ — Mobile-friendly map

UI/UX stage. Responsive breakpoints, touch-friendly controls, pinch-zoom tuning, measure tool + print-to-PDF mobile usability, popup sizing. Candidate for promotion into `docs/refinement-sequence.md`.

### Outstanding merges (operator)

- `refinement-ui-polish-v2` → `main` (Chat 79). Prod reflects via deploy `69ea9d1b8b51ad96ce674f5d`. Cleanup only.
- `refinement-sidebar-collapse` → `main` (Chat 81). Prod reflects via deploy `69eaf518997b708751d871bf`. Cleanup only.

(Note Chat 84a: `refinement-abatement-build` was merged directly to `main` by Claude via PAT push — no operator step required. Direct-merge pattern now standard; see §Close-out above. The two entries above are residual and can be cleaned up by operator or folded into a future Claude direct-merge.)

### Operator data ask (spec §12.5, non-blocking)

Comptroller Ch. 312 abatement registry spreadsheet — manual quarterly download from `comptroller.texas.gov`. Authoritative statewide baseline + backstop for county scrape failure. Can land Chat 86 or later. Drop in `/mnt/user-data/uploads/` when downloaded.

---

## Prod status

- URL: https://lrp-tx-gis.netlify.app — requires real User-Agent on curl (`-A "Mozilla/5.0"`).
- Last published deploy: `69eb6ae6583299e28d48965e` (Chat 84, `refinement-abatement-build`, 2026-04-24). State=ready, CDN-verified, 23 layer ids live.
- Main HEAD includes `refinement-abatement-build` as of Chat 84a (merge commit `78754f6`). Feature branch deleted from origin.
- Auto-publish: unlocked.
- **Deploy path: Netlify MCP → CLI proxy.** REST-API dead.
- Layer set: **23 built clean** (advanced from 22 with `tax_abatements` Chat 84).
- Prebuilt PMTiles (4): `parcels_pecos` 4.98 MB, `rrc_pipelines` 4.73 MB, `tiger_highways` 3.11 MB, `bts_rail` 2.16 MB.
- Sprite sheet: 5 icons @ 1x + 2x at `/sprite/sprite.png` + `sprite@2x.png`.
- Data-driven sizing live: `ercot_queue`, `solar`, `eia860_plants`, `eia860_battery`, `wind`; `substations`, `tpit_subs`, `tpit_lines`.
- UI state: sidebar collapsible (`#sb=1`); `parcels_pecos` sidebar-hidden; default-ON layers; default basemap = esri_imagery; default viewport = -102.9707/30.9112 z12.
- Sizing gaps (static fallback): `eia860_plants` 476/1367 null; `transmission` no voltage.
- **CDN warmup timing:** 45–75s post-deploy.

### Abatement layer notes (Chat 83–84)

- 8 features live. All geocoded to **county centroid only** — no sub-county spatial precision. Do not represent as true point locations.
- **Column-mapping caveats** (schema constraint — `combined_points.csv` has fixed columns):
  - `agenda_url` stored in the `poi` column.
  - `flags` stored in the `funnel_stage` column.
  - `applicant` stored in `operator`; `status` in `funnel_stage` (shares column with flags); `reinvestment_zone` in `project`; `project_type` in `technology`; `meeting_date` in `commissioned`.
- **Silver Basin Digital row** has `technology=abatement_other` (not a canonical project_type). Filter via `project=` (reinvestment zone) rather than `technology=` to isolate canonical project-type categories.
- **Matterhorn row dropped Chat 83** — no meeting date captured. Re-include Chat 85 after agenda PDF re-scrape or operator-provided date.

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
