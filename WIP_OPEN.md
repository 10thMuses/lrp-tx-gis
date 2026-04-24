# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per Readme §10: **`## Next chat`** = paste-ready for next shipping chat. **`## Sprint queue`** = N+2 and beyond.

---

## Next chat

**Chat 79 — UI POLISH v2.** Spec: `docs/refinement-sequence.md` §"Stage: UI POLISH v2". Bundle of four live-UI changes on `build_template.html` + `layers.yaml`: (1) filter inputs → dropdowns with auto-populate + multi-select (no free-text); (2) default open state (`caramba_north` / `counties` / `county_labels` / `cities` / `waha` ON, `esri_imagery` basemap, initial viewport zoomed to Caramba); (3) `ercot_queue` color split by `technology` (gas/solar/wind/battery/other); (4) hide `parcels_pecos` (default-off + remove from sidebar, data file retained). Branch: `refinement-ui-polish-v2`. No data-pipeline changes. Main HEAD `f334601`. Prod live on deploy `69ea83a786cf7142db291f87` (22 layers, MW-driven sizing on `eia860_plants` included).

**Credential:** `NETLIFY_PAT=nfp_h3iY48jurPAn57KcUzaCKGNccw5gXR1z9ac5` and `GITHUB_PAT=...` supplied in `/mnt/project/CREDENTIALS.md`. If container is fresh and `CREDENTIALS.md` is missing them, operator pastes `NETLIFY_PAT=...` at top of resume prompt.

### Session open (single block)

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
cd /home/claude && rm -rf repo 2>/dev/null; git clone -q https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git repo && cd repo
git config user.email "claude@lrp.local" && git config user.name "Claude (LRP GIS)"
git checkout -b refinement-ui-polish-v2
apt-get install -y tippecanoe libcairo2 -q
pip install shapely pmtiles pyyaml cairosvg pandas openpyxl --break-system-packages -q
```

### UI POLISH v2 — task execution order

1. **Hide `parcels_pecos`** (simplest; fast acceptance gate). In `layers.yaml` set `default_on: false` and add sidebar-omit flag per template convention. Data file stays.
2. **Default open state** — edit `build_template.html` initial state constants: ON layers list, basemap = `esri_imagery`, viewport coords = Caramba centroid with appropriate zoom (check `caramba_north` geometry in `combined_geoms.geojson` for centroid).
3. **`ercot_queue` color split by `technology`** — swap static color for `['match', ['get', 'technology'], ...]` expression. Gas codes (GT/CC/IC/ST) → gas color; PV → solar color; WT → wind color; BA → battery color; OT/null → neutral. Colors consistent with existing `solar`, `wind`, `eia860_battery` layer colors.
4. **Dropdown filter UI** — all text-input filters → `<select>` elements populated from unique values in layer data. Categorical: multi-select. Numeric/date: range pickers (unchanged). Build step extracts unique values per categorical field and injects into template.

### Build + deploy

```bash
python build.py
# gate: built=22, errored=0

PAT=$(grep '^NETLIFY_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
SITE=01b53b80-687e-4641-b088-115b7d5ef638
cd /mnt/user-data/outputs/dist && zip -qr /tmp/d.zip .
RESP=$(curl -s -X POST -H "Authorization: Bearer $PAT" -H "Content-Type: application/zip" \
  --data-binary @/tmp/d.zip "https://api.netlify.com/api/v1/sites/$SITE/deploys")
DEPLOY_ID=$(echo "$RESP" | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")

# Poll until ready, then sleep 90 for CDN warmup
i=0; while [ $i -lt 30 ]; do i=$((i+1))
  STATE=$(curl -s -H "Authorization: Bearer $PAT" \
    "https://api.netlify.com/api/v1/sites/$SITE/deploys/$DEPLOY_ID" \
    | python3 -c "import sys,json;print(json.load(sys.stdin).get('state','?'))")
  [ "$STATE" = "ready" ] && break; [ "$STATE" = "error" ] && break; sleep 6
done
sleep 90
curl -sI -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | head -3
curl -s -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | grep -oE '"id":[ ]*"[a-z0-9_]+"' | sort -u | wc -l  # expect 22
```

### PR + close-out

Per `docs/refinement-sequence.md` §universal-rules: open PR against `main` with task list + files changed in body, do not merge. Operator merges.

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
git push "https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git" refinement-ui-polish-v2
# open PR via gh CLI or GitHub API
```

Update `WIP_OPEN.md` `## Next chat` → promote Chat 80 (SIDEBAR COLLAPSE) after merge. Append `WIP_LOG.md` entry for Chat 79.

---

## Sprint queue

### Chat 80 — SIDEBAR COLLAPSE

**Spec:** `docs/refinement-sequence.md` §"Stage: SIDEBAR COLLAPSE". Small live-UI change: collapsible left sidebar with `«` / `»` toggle, map resize on transition, URL-hash state persistence, mobile + desktop parity. Branch: `refinement-sidebar-collapse`. Depends on nothing — can run after UI POLISH v2 merges, or parallel if diff surface doesn't conflict.

---

### Chat 81+ — Tax abatement BUILD

**Approved scope:** `docs/refinement-abatement-spec.md` §12 (locked 2026-04-23). Both standalone layer + facility annotation; all 23 counties with Trans-Pecos → Permian-core → peripheral sequencing; PDFs skipped; 2025+2026 filings only; Comptroller Ch. 312 spreadsheet manual-quarterly ingest; dedup by `(county, applicant_normalized, reinvestment_zone)`; weekly GitHub Actions; alerting deferred.

**Stage split:** DISCOVERY closed (spec committed). BUILD unblocked after UI POLISH v2 merges. Independent track otherwise.

---

## Current workstream

MW-driven sizing on `eia860_plants` shipped Chat 78. SIZING_RULES now covers 8 layers (`ercot_queue`, `solar`, `eia860_plants`, `eia860_battery`, `wind`, `substations`, `tpit_subs`, `tpit_lines`). 476/1367 EIA-860 plants with null `capacity_mw` fall back cleanly to `L.radius: 6` via existing `['<=', _sizingVal(rule), 0]` guard — no zero-sized markers.

Next: UI POLISH v2 bundle (Chat 79). Abatement BUILD unblocked on independent track after UI POLISH merges.

---

## Recent sessions

| Chat | Date | Outcome |
|---:|---|---|
| 70 | 2026-04-22 | Token-efficiency sweep (doc-only). |
| 71 | 2026-04-22 | Stage 3 closed + Stage 4 SIZING+WATERMARK shipped. Merges `ebe5634` + `026eff2`. Prod `69e96a36`. |
| 72 | 2026-04-23 | TCEQ REFRESH recon + data pull. 6 records geocoded. `tceq_pws`/`tceq_pbr`/`tceq_nsr_pending` scoped out. |
| 73 | 2026-04-23 | TCEQ refresh branch merged to main — `ea7e39d`. |
| 74 | 2026-04-23 | TCEQ data/config + EIA-860 research committed — `4292bf2`, `3aada1c`. Build deferred. |
| 75 | 2026-04-23 | Abatement discovery spec + multi-chat refinement rules — `92d25c72`. TCEQ built locally clean. Stopped pre-deploy. |
| 75b | 2026-04-23 | **TCEQ SHIP complete.** Deploy `69ea32c7d3733641c9a1bb7c`. 21→22 layers. Readme §2 ban-ship-it rule `939ff16`. |
| 76 | 2026-04-23 | **UI polish shipped.** 10 label/layout tweaks — `a379539`. Live on prod. |
| 77 | 2026-04-23 | **EIA-860 enrichment shipped.** 891/1367 plants enriched + `capacity_mw` coalesce — commit `9d40df4`, deploy `69ea73f92acb1109e87b4ddc`. Deploy path migrated to Netlify REST API after MCP proxy 503s. |
| 78 | 2026-04-23 | **MW-driven sizing on `eia860_plants` shipped.** Single SIZING_RULES entry + `L.radius: 6` fallback — commit `f334601`, deploy `69ea83a786cf7142db291f87`. 22 layers unchanged. |

Full per-session detail in `WIP_LOG.md`.

---

## Prod status

- URL: https://lrp-tx-gis.netlify.app — **requires real User-Agent on curl** (default `curl/x.y.z` UA returns 503; use `-A "Mozilla/5.0"`). See `docs/settled.md` §Data sources.
- Last published deploy: `69ea83a786cf7142db291f87` on commit `f334601` (Chat 78).
- Main HEAD: `f334601`.
- Auto-publish: unlocked.
- **Deploy path:** Netlify REST API via `NETLIFY_PAT`. MCP proxy path deprecated for this site.
- Layer set: 22 built clean.
- Prebuilt PMTiles (4): `parcels_pecos` 4.98 MB, `rrc_pipelines` 4.73 MB, `tiger_highways` 3.11 MB, `bts_rail` 2.16 MB.
- Sprite sheet: 5 icons @ 1x + 2x at `/sprite/sprite.png` + `sprite@2x.png`.
- Data-driven sizing live: `ercot_queue`, `solar`, `eia860_plants`, `eia860_battery`, `wind` (`capacity_mw`); `substations`, `tpit_subs`, `tpit_lines` (kV).
- Sizing gaps (static fallback): `eia860_plants` 476/1367 null `capacity_mw` → radius 6 fallback; `transmission` no voltage in geoms.
- **CDN warmup timing:** Standard post-deploy `sleep 90` per Chat 77 observation.
- **Container-egress caveat (Chat 78):** Close-out observed container egress proxy returning 503 "DNS cache overflow" on all `lrp-tx-gis.netlify.app` curl requests while Netlify API calls succeeded. Root 200 reconfirmation deferred; deploy `state=ready` confirmed via API. Not a prod issue.

---

## Open backlog

**Standing watch item:** TCEQ diesel-genset NSR permits live only in CRPUB (not in `turbine-lst.xlsx`). Gap for data-center backup-power intelligence. Revisit only if TCEQ publishes bulk feed or operator authorizes CRPUB scrape.

**Data-pipeline gaps (non-blocking):**
- `eia860_plants`: 476/1367 rows still null on `capacity_mw`/`technology`/`fuel`. Chat 78 UI fallback handles cleanly; data fix requires plants not in EIA-860 Form 2024 (small / retired / non-utility-scale).
- `combined_points.csv` blank `operator` / `commissioned` on EIA point layers — filter UI provides leverage post-Chat-79; out of scope unless prioritized.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar. Low priority.

**Infrastructure:**
- **Netlify MCP proxy blocker:** Proxy-based deploy path returning 503 on upload. REST API is canonical path. Watch: if REST API begins failing, re-check MCP proxy, then escalate to Netlify support.

**Permanently excluded / settled:**
- `rrc_wells_permian`, `tceq_pws`, `tceq_pbr`, `tceq_nsr_pending` — see `docs/settled.md` §"Scoped-out data sources" and §"Data sources".

**UI/UX backlog (unscheduled):**
- **Mobile-friendly map.** Responsive breakpoints, touch-friendly controls, pinch-zoom tuning, measure tool + print-to-PDF mobile usability, popup sizing. Candidate for promotion into `docs/refinement-sequence.md` after UI POLISH v2.

**Other (non-GIS):**
- Grid Wire Vol. 7.
- Tier 2 water availability assessments, cluster intelligence sheets, Excel returns model.

---

## GitHub sync — live

Repo: `github.com/10thMuses/lrp-tx-gis`. Authority: `main` = canonical. Working dir: `/home/claude/repo/`. Protocol: `Readme.md` §7 + `docs/principles.md` §5.
