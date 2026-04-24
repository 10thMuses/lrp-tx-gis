# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per Readme §10: **`## Next chat`** = paste-ready for next shipping chat. **`## Sprint queue`** = N+2 and beyond.

---

## Next chat

**Chat 82 — ABATEMENT BUILD.** SIDEBAR COLLAPSE shipped Chat 81 on branch `refinement-sidebar-collapse` (branch HEAD `6d356cd`, prod deploy `69eaf518997b708751d871bf`, 22 layers, feature verified live). PR against `main` pending operator merge (PAT scope still blocks auto-open). Chat 79 PR (`refinement-ui-polish-v2`) also still pending — both are independent of Chat 82.

**Approved scope:** `docs/refinement-abatement-spec.md` §12 (locked 2026-04-23). Both standalone layer + facility annotation; all 23 counties with Trans-Pecos → Permian-core → peripheral sequencing; PDFs skipped; 2025+2026 filings only; Comptroller Ch. 312 spreadsheet manual-quarterly ingest; dedup by `(county, applicant_normalized, reinvestment_zone)`; weekly GitHub Actions; alerting deferred.

Stage split: DISCOVERY closed (spec committed Chat 75). BUILD is this chat.

### Session open (single block)

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
cd /home/claude && rm -rf repo 2>/dev/null
git clone -q https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git repo && cd repo
git config user.email "claude@lrp.local" && git config user.name "Claude (LRP GIS)"
git checkout -b refinement-abatement-build
apt-get install -y tippecanoe libcairo2 -q
pip install shapely pmtiles pyyaml cairosvg pandas openpyxl requests --break-system-packages -q
cat docs/refinement-abatement-spec.md   # §12 is authoritative scope
```

### Deploy pattern (CANONICAL — confirmed Chat 81)

`NETLIFY_PAT=` line was removed from `CREDENTIALS.md` in a prior edit. **REST-API deploy path is DEAD.** Only working deploy path is Netlify MCP → CLI proxy:

1. Call `Netlify:netlify-deploy-services-updater` MCP tool with `{operation: "deploy-site", params: {siteId: "01b53b80-687e-4641-b088-115b7d5ef638"}}` → returns a `--proxy-path` URL (one-time token, single use).
2. `cd /mnt/user-data/outputs/dist && npx -y @netlify/mcp@latest --site-id 01b53b80-687e-4641-b088-115b7d5ef638 --proxy-path "<URL>" --no-wait` — returns `{"deployId": "...", "buildId": "..."}` on stdout.
3. Poll state via `Netlify:netlify-deploy-services-reader` `get-deploy-for-site` tool until `state=ready`.
4. `sleep 45` for CDN warm-up (503 at 30s is normal; 503 at 75s requires a retry).
5. Curl-verify: `curl -sI -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/` → HTTP 200; `curl -s -A "Mozilla/5.0" ... | grep -oE '"id":[ ]*"[a-z0-9_]+"' | sort -u | wc -l` → 22 (or 23 if abatement ships as standalone layer).

### PR + close-out (NON-NEGOTIABLE, regardless of deploy outcome)

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
git push "https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git" refinement-abatement-build
```

Then on `main`:
- Rewrite `## Next chat` → promote next stage.
- Append `WIP_LOG.md` entry for Chat 82.
- `git commit -am "Chat 82 close-out" && git push` to main.

**Token-budget rule (codified Chat 81, see Readme §10 Close-out discipline):** stop active work at ~65% of token budget. Reserve remaining 35% for blocker recovery plus the four non-optional close-out actions: (a) push feature branch to origin, (b) rewrite WIP_OPEN `## Next chat`, (c) prepend WIP_LOG entry, (d) commit both to main and push.

### Known constraint (carried from Chat 79)

`GITHUB_PAT` in `CREDENTIALS.md` lacks PR-creation scope — returns `403 Resource not accessible by personal access token`. Branch push works; PR must be opened by operator via GitHub UI. Revisit PAT scopes if persistent blocker.

---

## Sprint queue

### Chat 83+ — Mobile-friendly map

UI/UX stage. Responsive breakpoints, touch-friendly controls, pinch-zoom tuning, measure tool + print-to-PDF mobile usability, popup sizing. Candidate for promotion into `docs/refinement-sequence.md` when abatement BUILD concludes.

### Outstanding PR merges (operator)

- `refinement-ui-polish-v2` → `main` (Chat 79). No functional dependency — prod already reflects via deploy `69ea9d1b8b51ad96ce674f5d`. Cleanup only.
- `refinement-sidebar-collapse` → `main` (Chat 81). No functional dependency — prod reflects via deploy `69eaf518997b708751d871bf`. Cleanup only.

---

## Current workstream

SIDEBAR COLLAPSE shipped Chat 81 — three-edit bundle on `build_template.html` wiring the toggle button (CSS + HTML were applied Chat 80 pre-pause): init `sidebarCollapsed` from `#sb=1` hash before map construction; `syncHash` serializes `sb` into URL; `sb-toggle` click handler fires `map.resize()` on `transitionend` with 260ms fallback. Prod deploy `69eaf518997b708751d871bf` on branch commit `6d356cd`. PR `refinement-sidebar-collapse` → `main` pending operator merge.

Next: ABATEMENT BUILD (Chat 82).

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
| 79 | 2026-04-23 | **UI POLISH v2 shipped.** Branch commit `c8ff838`, deploy `69ea9d1b8b51ad96ce674f5d`. PR pending merge. |
| 80 | 2026-04-24 | SIDEBAR COLLAPSE partial — CSS + HTML + writeHash-serialization only. Branch commit `bdc1fb6`, pushed. Token-limit paused before JS wiring. Not deployed. |
| 81 | 2026-04-24 | **SIDEBAR COLLAPSE shipped.** JS wiring completed on top of Chat 80 commit — branch commit `6d356cd`, deploy `69eaf518997b708751d871bf`. Deploy path restored to Netlify MCP proxy (REST API dead — `NETLIFY_PAT` absent from creds). PR pending operator merge. Mid-chat operator correction: close-out must happen even when deploy is blocked — branch push + WIP_OPEN rewrite + WIP_LOG append + main push are non-optional. |

Full per-session detail in `WIP_LOG.md`.

---

## Prod status

- URL: https://lrp-tx-gis.netlify.app — **requires real User-Agent on curl** (default `curl/x.y.z` UA returns 503; use `-A "Mozilla/5.0"`). See `docs/settled.md` §Data sources.
- Last published deploy: `69eaf518997b708751d871bf` on branch commit `6d356cd` (Chat 81, branch `refinement-sidebar-collapse`).
- Main HEAD: `0831052` (will advance one commit with Chat 81 close-out — this rewrite + WIP_LOG entries).
- Auto-publish: unlocked.
- **Deploy path: Netlify MCP → CLI proxy.** REST-API path is dead (no `NETLIFY_PAT` in `CREDENTIALS.md`). See `## Next chat` §Deploy pattern for the 5-step procedure. Confirmed working Chat 81.
- Layer set: 22 built clean.
- Prebuilt PMTiles (4): `parcels_pecos` 4.98 MB, `rrc_pipelines` 4.73 MB, `tiger_highways` 3.11 MB, `bts_rail` 2.16 MB.
- Sprite sheet: 5 icons @ 1x + 2x at `/sprite/sprite.png` + `sprite@2x.png`.
- Data-driven sizing live: `ercot_queue`, `solar`, `eia860_plants`, `eia860_battery`, `wind` (`capacity_mw`); `substations`, `tpit_subs`, `tpit_lines` (kV).
- UI state live (Chat 81): sidebar collapsible via `«`/`»` button at top-left of map (44×44), keyboard-accessible, state persists in URL hash `#sb=1`, transitions 220ms, mobile overlays sidebar as 280px drawer.
- UI state live (Chat 79): `parcels_pecos` sidebar-hidden; default-ON = caramba_north/counties/county_labels/cities/waha; default basemap = esri_imagery; default viewport = -102.9707/30.9112 z12; `ercot_queue` per-technology color; categorical filters auto-promoted to searchable multi-select dropdowns.
- Sizing gaps (static fallback): `eia860_plants` 476/1367 null `capacity_mw` → radius 6 fallback; `transmission` no voltage in geoms.
- **CDN warmup timing:** 45–75s post-deploy. 503 at 30s is normal; 503 at 75s retry.

---

## Open backlog

**Standing watch item:** TCEQ diesel-genset NSR permits live only in CRPUB (not in `turbine-lst.xlsx`). Gap for data-center backup-power intelligence. Revisit only if TCEQ publishes bulk feed or operator authorizes CRPUB scrape.

**Data-pipeline gaps (non-blocking):**
- `eia860_plants`: 476/1367 rows still null on `capacity_mw`/`technology`/`fuel`.
- `combined_points.csv` blank `operator` / `commissioned` on EIA point layers.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar. Low priority.

**Infrastructure:**
- **Credential state (Chat 81 discovery):** `NETLIFY_PAT=` line is absent from `CREDENTIALS.md`. The `## Active credentials` table says "Managed by Netlify MCP" — accurate. REST-API deploys no longer possible; Netlify MCP proxy path is canonical.
- **GitHub PAT scope (Chat 79):** Current `GITHUB_PAT` can push branches but returns 403 on PR-creation endpoint. Operator opens PRs via GitHub UI.

**Permanently excluded / settled:**
- `rrc_wells_permian`, `tceq_pws`, `tceq_pbr`, `tceq_nsr_pending` — see `docs/settled.md` §"Scoped-out data sources" and §"Data sources".

**UI/UX backlog (unscheduled):**
- **Mobile-friendly map.** Responsive breakpoints, touch-friendly controls, pinch-zoom tuning, measure tool + print-to-PDF mobile usability, popup sizing. Candidate for promotion into `docs/refinement-sequence.md` after ABATEMENT BUILD.

**Other (non-GIS):**
- Grid Wire Vol. 7.
- Tier 2 water availability assessments, cluster intelligence sheets, Excel returns model.

---

## GitHub sync — live

Repo: `github.com/10thMuses/lrp-tx-gis`. Authority: `main` = canonical. Working dir: `/home/claude/repo/`. Protocol: `Readme.md` §7 + `docs/principles.md` §5.
