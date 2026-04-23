# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per Readme §10: **`## Next chat`** holds paste-ready instructions for the immediately-next shipping chat (rewritten every close-out). **`## Sprint queue`** holds the forward plan for chats beyond that (updated as plans firm up or change). Operator's per-chat prompt collapses to `Resume.` — all state needed is here.

---

## Next chat

**Chat 77 — EIA-860 enrichment + capacity coalesce.** Data-pipeline refresh. Populates `capacity_mw`/`technology`/`fuel` on `eia860_plants` (891/1367 rows, 65.2%) from EIA-860 Form 2024, and unifies capacity column naming across all generation layers. `layers.yaml` popup additions. Layer count unchanged (22). Main HEAD `a379539` (Chat 76 UI polish shipped). Prod live on `a379539`.

### Session open (single block)

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
cd /home/claude && rm -rf repo 2>/dev/null; git clone -q https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git repo && cd repo
git config user.email "claude@lrp.local" && git config user.name "Claude (LRP GIS)"
apt-get install -y tippecanoe libcairo2 -q
pip install shapely pmtiles pyyaml cairosvg pandas openpyxl --break-system-packages -q
```

### Part A — `eia860_plants` enrichment

```bash
curl -sL -A 'Mozilla/5.0' \
  -H 'Referer: https://www.eia.gov/electricity/data/eia860/' \
  -o /tmp/eia860_2024.zip \
  'https://www.eia.gov/electricity/data/eia860/xls/eia8602024.zip'
unzip -p /tmp/eia860_2024.zip '3_1_Generator_Y2024.xlsx' > /tmp/gen.xlsx
```

- `pd.read_excel('/tmp/gen.xlsx', sheet_name='Operable', skiprows=1)` — verify sheet name on first read, fall back to first sheet.
- Filter `Status == 'OP'`.
- Groupby `Plant Code`:
  - `capacity_mw = sum(Nameplate Capacity (MW))`
  - `technology = mode(Technology)`
  - `fuel_code = mode(Energy Source 1)`
- Fuel code map: `NG→Natural gas, WAT→Hydro, NUC→Nuclear, SUB/BIT/LIG→Coal, DFO→Oil, SUN→Solar, WND→Wind, MWH→Battery`. Unknown codes → null (don't invent).
- Left-join on `plant_code` for `layer_id == 'eia860_plants'` rows in `combined_points.csv`. Write back to same file.

### Part B — capacity column coalesce (all layers)

| Layer | Source col | Transform |
|---|---|---|
| `eia860_battery` | `capacity` | → `capacity_mw` (already MW) |
| `ercot_queue` | `mw` | → `capacity_mw` |
| `wind` | `cap_kw` | `/ 1000` → `capacity_mw` |
| `solar`, `tceq_gas_turbines` | already `capacity_mw` | — |

Retain source columns for provenance (don't drop `mw`, `cap_kw`, `capacity`). Update `layers.yaml` popups:
- `ercot_queue`: swap popup field `mw` → `capacity_mw`
- `eia860_battery`, `wind`: add `capacity_mw`
- `eia860_plants`: add `capacity_mw`, `technology`, `fuel`

**Expected coverage post-enrichment:** `eia860_plants` 891/1367, `eia860_battery` 133/133, `ercot_queue` 1708/1778, `solar` 180/180, `wind` 19269/19464, `tceq_gas_turbines` 6/6. Total ~22,187 rows.

### Sizing re-audit

Confirm `SIZING_RULES` in `build_template.html` still correct after field renames. `ercot_queue` sizing expression currently reads `mw` — must swap to `capacity_mw`. `wind` sizing reads `cap_kw` — swap to `capacity_mw` (and rescale: 3→15px maps to new MW range ~0–5 instead of 0–5000).

### Build + deploy

```bash
python build.py
# gate: built=22, errored=0
```

Netlify MCP from `/mnt/user-data/outputs/dist/`. Sleep 45. Curl verify with real UA (`-A "Mozilla/5.0"`).

### Commit + push + close-out

```bash
git add -A
git commit -m "Chat 77: EIA-860 enrichment (891/1367 plants) + capacity_mw coalesce"
git push
```

Update `WIP_OPEN.md` `## Next chat` to Chat 78 (promote from `## Sprint queue`). Append `WIP_LOG.md` entry for Chat 77. Capture Netlify `deployId` from MCP call for the Prod status block.

---

## Sprint queue

### Chat 78 — Semantic icons (unblocked by Chat 77)

- Icon routing by `fuel` field on `eia860_plants` (data-driven icon-image expression: Solar→sun, Wind→windmill, Natural gas→flame, Nuclear→atom, Coal→coal, Oil→oil-barrel, Hydro→water, Battery→battery).
- Icon routing by `technology` field on `ercot_queue` (same mapping, technology-keyed).
- Layer-level icon for single-fuel layers: `solar`→sun, `wind`→windmill, `eia860_battery`→battery, `tceq_gas_turbines`→flame.
- Sprite sheet extension: audit existing 5 icons, add missing (atom, coal, oil-barrel, water, flame) via `build_sprite.py` + cairosvg. Commit `sprite/sprite.png` + `@2x` + `.json` manifests.
- MW-driven sizing re-audit: `eia860_plants` now has MW for 891/1367 → data-driven sizing on those, static fallback for 476 unmatched (expression: `['case', ['>', ['get','capacity_mw'], 0], sizingExpr, static]`).

### Chat 79+ — Tax abatement scraper (refinement item #5)

**Spec:** `docs/refinement-abatement-spec.md` (committed 2026-04-23). Regulatory context, leading-indicator hierarchy, keyword taxonomy, `extract_applicant()` regex with both `re.I` + `\b` fixes, field catalog, schema Options A/B, county adapter status (2 validated, 3 stubbed, 18 TODO), 4 live hits, 8 BUILD-gate open questions.

**Stage split:** DISCOVERY is doc-only and effectively closed by the spec commit. BUILD gated on operator sign-off against spec §9. Independent track — slots anywhere after Chat 75b; not blocked by UI / EIA-860 / icon sprints.

---

## Current workstream

UI polish complete and in prod (Chat 76). 22 layers live with title-cased labels, collapsible filter dropdowns, WAHA circle marker, reordered sidebar groups.

Next: EIA-860 enrichment (Chat 77), semantic icons (Chat 78 after 77), tax abatement scraper (Chat 79+, independent track).

---

## Recent sessions

| Chat | Date | Outcome |
|---:|---|---|
| 69 | 2026-04-22 | Stage 3 Visual Overhaul — recon only. |
| 70 | 2026-04-22 | Token-efficiency sweep (doc-only). |
| 71 | 2026-04-22 | Stage 3 closed + Stage 4 SIZING+WATERMARK shipped. Merges `ebe5634` + `026eff2`. Prod `69e96a36`. |
| 72 | 2026-04-23 | TCEQ REFRESH recon + data pull. 6 records geocoded. `tceq_pws`/`tceq_pbr`/`tceq_nsr_pending` scoped out. |
| 73 | 2026-04-23 | TCEQ refresh branch merged to main — `ea7e39d`. |
| 74 | 2026-04-23 | TCEQ data/config + EIA-860 research committed — `4292bf2`, `3aada1c`. Build deferred. |
| 75 | 2026-04-23 | Abatement discovery spec + multi-chat refinement rules — `92d25c72`. TCEQ built locally clean. Stopped pre-deploy. |
| 75b | 2026-04-23 | **TCEQ SHIP complete.** Deploy `69ea32c7d3733641c9a1bb7c`. 21→22 layers. Readme §2 ban-ship-it rule `939ff16`. Close-out docs landed in same chat. |
| 76 | 2026-04-23 | **UI polish shipped.** 10 label/layout tweaks — `a379539`. Live on prod. Close-out docs landed in follow-up chat. |

Full per-session detail in `WIP_LOG.md`.

---

## Prod status

- URL: https://lrp-tx-gis.netlify.app — **requires real User-Agent on curl** (default `curl/x.y.z` UA returns 503; use `-A "Mozilla/5.0"`). See `docs/settled.md` §Data sources.
- Last published deploy: live on commit `a379539` (Chat 76 UI polish). Netlify `deployId` not captured in-session; Netlify API requires auth to retrieve.
- Main HEAD: `a379539`.
- Auto-publish: unlocked.
- Layer set: 22 built clean. All labels title-cased with vintage-tagged ERCOT queue; filter dropdowns collapsible; WAHA hub has circle marker; `Water & Regulatory` at bottom of sidebar.
- Prebuilt PMTiles (4): parcels_pecos 4.98 MB, rrc_pipelines 4.73 MB, tiger_highways 3.11 MB, bts_rail 2.16 MB.
- Sprite sheet: 5 icons @ 1x + 2x at `/sprite/sprite.png` + `sprite@2x.png`.
- Data-driven sizing live: `ercot_queue`, `solar`, `eia860_battery`, `wind` (MW), `substations`, `tpit_subs`, `tpit_lines` (kV). **Note:** Chat 77 will rename source fields to `capacity_mw`; sizing expressions in `build_template.html` must swap `mw`→`capacity_mw` and `cap_kw`→`capacity_mw` same chat.
- Sizing gaps (static fallback): `eia860_plants` (capacity_mw blank 1367/1367 — Chat 77 fixes 891 of them), `transmission` (no voltage in geoms).

---

## Open backlog

**Standing watch item:** TCEQ diesel-genset NSR permits live only in CRPUB (not in `turbine-lst.xlsx`). Gap for data-center backup-power intelligence if that becomes a use case. Revisit only if TCEQ publishes bulk feed or operator authorizes CRPUB scrape.

**Data-pipeline gaps (non-blocking, addressed by queued chats):**
- `eia860_plants` capacity_mw / technology / fuel — Chat 77.
- `combined_points.csv` blank `operator` / `commissioned` on EIA point layers — filter UI provides leverage; out of scope unless prioritized.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar. Low priority.

**Permanently excluded / settled:**
- `rrc_wells_permian`, `tceq_pws`, `tceq_pbr`, `tceq_nsr_pending` — see `docs/settled.md` §"Scoped-out data sources" and §"Data sources".

**Other (non-GIS):**
- Grid Wire Vol. 7.
- Tier 2 water availability assessments, cluster intelligence sheets, Excel returns model.

---

## GitHub sync — live

Repo: `github.com/10thMuses/lrp-tx-gis`. Authority: `main` = canonical. Working dir: `/home/claude/repo/`. Protocol: `Readme.md` §7 + `docs/principles.md` §5.
