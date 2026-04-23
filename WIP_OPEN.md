# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per Readme §10: **`## Next chat

**Chat 78 — MW-driven sizing on `eia860_plants`.** Sprite/icon routing and ERCOT technology-code expansion cut from scope by operator 2026-04-23. Single change: add `capacity_mw`-driven sizing expression with fallback for the ~495 plants where `fuel`/`capacity_mw` are null. Layer count unchanged (22). Main HEAD `c4ba863`. Prod live on deploy `69ea73f92acb1109e87b4ddc`.

**Credential:** `NETLIFY_PAT=nfp_h3iY48jurPAn57KcUzaCKGNccw5gXR1z9ac5` (supplied by operator Chat 78 prep). Operator to paste into project's `CREDENTIALS.md` when UI edit path becomes available; until then, paste the same line at top of resume prompt so session-open `grep` path works.

### Session open (single block)

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
cd /home/claude && rm -rf repo 2>/dev/null; git clone -q https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git repo && cd repo
git config user.email "claude@lrp.local" && git config user.name "Claude (LRP GIS)"
apt-get install -y tippecanoe libcairo2 -q
pip install shapely pmtiles pyyaml cairosvg pandas openpyxl --break-system-packages -q
```

### MW-driven sizing on `eia860_plants`

Add one line to `SIZING_RULES` in `build_template.html`:

```js
eia860_plants: { field: 'capacity_mw', mode: 'mw' }
```

Existing `mw` mode applies to both `circle-radius` and `icon-size` via existing helper functions — no new mode needed. The existing `['<=', _sizingVal(rule), 0]` guard handles null/0 rows by falling back to `L.radius || 4` (functionally equivalent to spec's `coalesce`+`>0` case expression). Set `L.radius: 6` on `eia860_plants` in `layers.yaml` if not already present, to match spec's fallback radius.

**MW distribution confirmed (Chat 78 prep, n=891 enriched):** min 1.0, p10 1.2, p50 100, p90 501, p99 1694, max 4008. Existing `mw` interpolation stops `(0→3, 50→5, 200→7, 500→9.5, 1000→12, 2000→15)` fit cleanly — no retuning needed.

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

### Commit + push + close-out

```bash
git add -A
git commit -m "Chat 78: MW-driven sizing on eia860_plants"
git push
```

Update `WIP_OPEN.md` `## Next chat` → promote Chat 79 (UI POLISH v2). Append `WIP_LOG.md` entry for Chat 78.

---

## Sprint queue

### Chat 79 — UI POLISH v2

**Spec:** `docs/refinement-sequence.md` §"Stage: UI POLISH v2". Bundle of four live-UI tweaks: (1) filter inputs → dropdowns with auto-populate + multi-select; (2) default open state (caramba_north / counties / county_labels / cities / waha ON, `esri_imagery` basemap, zoom to Caramba); (3) `ercot_queue` fuel-type color split (gas / solar / wind / battery / other); (4) hide `parcels_pecos` layer.

**Dependencies:** none. Operates on `build_template.html` + `layers.yaml` only.

### Chat 80+ — Tax abatement BUILD

**Approved scope:** `docs/refinement-abatement-spec.md` §12 (locked 2026-04-23). Both standalone layer + facility annotation; all 23 counties with Trans-Pecos → Permian-core → peripheral sequencing; PDFs skipped; 2025+2026 filings only; Comptroller Ch. 312 spreadsheet manual-quarterly ingest; dedup by `(county, applicant_normalized, reinvestment_zone)`; weekly GitHub Actions; alerting deferred.

**Stage split:** DISCOVERY closed (spec committed). BUILD unblocked. Independent track — not blocked by Chat 78 or Chat 79.

---

## Current workstream

Data enrichment complete and in prod (Chat 77). EIA-860 matched 891/1367 plants with capacity/technology/fuel; capacity column unified to `capacity_mw` across all generation layers; sizing expressions on `ercot_queue` and `wind` swapped to unified field.

Next: semantic icons + MW-driven plant sizing (Chat 78), tax abatement scraper (Chat 79+, independent track).

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
| 77 | 2026-04-23 | **EIA-860 enrichment shipped.** 891/1367 plants enriched + `capacity_mw` coalesce — commit `9d40df4`, deploy `69ea73f92acb1109e87b4ddc`. Deploy path migrated to Netlify REST API + `NETLIFY_PAT` after MCP proxy 503s blocked two deploy attempts. |

Full per-session detail in `WIP_LOG.md`.

---

## Prod status

- URL: https://lrp-tx-gis.netlify.app — **requires real User-Agent on curl** (default `curl/x.y.z` UA returns 503; use `-A "Mozilla/5.0"`). See `docs/settled.md` §Data sources.
- Last published deploy: `69ea73f92acb1109e87b4ddc` on commit `9d40df4` (Chat 77).
- Main HEAD: `9d40df4`.
- Auto-publish: unlocked.
- **Deploy path:** Netlify REST API via `NETLIFY_PAT`. Netlify MCP proxy returned 503 on two consecutive chats (77 + resume) despite Netlify platform being fully operational on `netlifystatus.com`. MCP proxy path effectively deprecated for this site; REST API is canonical going forward. See Chat 77 entry in `WIP_LOG.md` for failure detail.
- Layer set: 22 built clean. All 10 Chat 76 label/layout tweaks + Chat 77 popup additions (`capacity_mw`, `technology`, `fuel` on `eia860_plants`; `capacity_mw` on `ercot_queue` / `eia860_battery` / `wind`).
- Prebuilt PMTiles (4): parcels_pecos 4.98 MB, rrc_pipelines 4.73 MB, tiger_highways 3.11 MB, bts_rail 2.16 MB.
- Sprite sheet: 5 icons @ 1x + 2x at `/sprite/sprite.png` + `sprite@2x.png`. Chat 78 extends to 10 icons.
- Data-driven sizing live: `ercot_queue` (`capacity_mw`), `solar` (`capacity_mw`), `eia860_battery` (`capacity_mw`), `wind` (`capacity_mw`), `substations`, `tpit_subs`, `tpit_lines` (kV).
- Sizing gaps (static fallback): `eia860_plants` (476/1367 still blank post-Chat-77 — Chat 78 adds conditional expression), `transmission` (no voltage in geoms).
- **CDN warmup timing:** Chat 77 observed ~90s for edges to clear 503 after deploy `state=ready`. Prior norm was 45s. Standard post-deploy `sleep 90` recommended going forward.

---

## Open backlog

**Standing watch item:** TCEQ diesel-genset NSR permits live only in CRPUB (not in `turbine-lst.xlsx`). Gap for data-center backup-power intelligence if that becomes a use case. Revisit only if TCEQ publishes bulk feed or operator authorizes CRPUB scrape.

**Data-pipeline gaps (non-blocking):**
- `eia860_plants`: 476/1367 rows still blank on `capacity_mw`/`technology`/`fuel` post-Chat-77. EIA-860 Form 2024 matched 891/1367; remainder are plants not in EIA-860 (small / retired / not utility-scale). Chat 78 handles UI via conditional sizing + fallback icon.
- `combined_points.csv` blank `operator` / `commissioned` on EIA point layers — filter UI provides leverage; out of scope unless prioritized.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar. Low priority.

**Infrastructure:**
- **Netlify MCP proxy blocker:** Proxy-based deploy path (`npx @netlify/mcp@latest --proxy-path`) returning 503 on upload despite platform operational. Migrated to REST API for Chat 77. Watch: if REST API begins failing similarly, check MCP proxy again in case it has recovered, then escalate to Netlify support if neither works.

**Permanently excluded / settled:**
- `rrc_wells_permian`, `tceq_pws`, `tceq_pbr`, `tceq_nsr_pending` — see `docs/settled.md` §"Scoped-out data sources" and §"Data sources".

**UI/UX backlog (unscheduled):**
- **Mobile-friendly map.** Responsive breakpoints for sidebar (collapsible drawer on narrow viewports), touch-friendly control sizing, pinch-zoom/pan tuning for MapLibre, measure tool + print-to-PDF usability on mobile, popup sizing on small screens. Scope TBD — candidate for promotion into `docs/refinement-sequence.md` as a standalone stage after Chat 78.

**Other (non-GIS):**
- Grid Wire Vol. 7.
- Tier 2 water availability assessments, cluster intelligence sheets, Excel returns model.

---

## GitHub sync — live

Repo: `github.com/10thMuses/lrp-tx-gis`. Authority: `main` = canonical. Working dir: `/home/claude/repo/`. Protocol: `Readme.md` §7 + `docs/principles.md` §5.
