# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per Readme §10: **`## Next chat`** holds paste-ready instructions for the immediately-next shipping chat (rewritten every close-out). **`## Sprint queue`** holds the forward plan for chats beyond that (updated as plans firm up or change). Operator's per-chat prompt collapses to `Resume.` — all state needed is here.

---

## Next chat

**Chat 76 — UI polish (data-independent).** 10 labeling/layout tweaks. Item 4 defers to Chat 78 (requires EIA-860 enrichment from Chat 77). All tweaks are yaml/template only — no data pipeline changes, no new layers, no schema changes. Main HEAD `939ff16` (Readme §2 ban-ship-it rule shipped Chat 75b). Prod `69ea32c7d3733641c9a1bb7c`, 22 layers.

### Session open (single block)

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
cd /home/claude && rm -rf repo 2>/dev/null; git clone -q https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git repo && cd repo
git config user.email "claude@lrp.local" && git config user.name "Claude (LRP GIS)"
apt-get install -y tippecanoe libcairo2 -q
pip install shapely pmtiles pyyaml cairosvg --break-system-packages -q
```

### Tweaks (yaml + template)

1. Sidebar filters → dropdown checkboxes (collapse vertical footprint).
2. Title-case all multi-word layer labels.
3. `"Solar Plants"` → `"Solar Farms"`.
4. **DEFER to Chat 78** — semantic icons keyed to fuel/technology; requires EIA-860 enrichment.
5. `"EIA-860 plants"` → `"Power Plants (EIA-860)"`.
6. Water & Regulatory group → bottom of sidebar (after Reference).
7. `"Natural gas hub"` → `"WAHA Natural Gas Hub"` + circle marker on point.
8. `"ERCOT GIR queue"` → `"ERCOT Interconnect Queue (as of <source date>)"` — vintage from ERCOT xlsx timestamp.
9. `"TWDB wells"` → `"Groundwater Wells (TWDB)"`.
10. `"MPGCD Management Zone"` → `"Groundwater District Management Zone 1"`.
11. `"RRC pipelines (≥20\" transmission)"` → `Oil & Gas Pipelines (>20", RRC)`.

### Build + deploy

```bash
python build.py
# gate: built=22, errored=0
```

Netlify MCP from `/mnt/user-data/outputs/dist/`. Sleep 45. Curl verify with real UA (`-A "Mozilla/5.0"`) — default curl UA returns 503 per `docs/settled.md`.

### Commit + push + close-out

```bash
git add -A
git commit -m "Chat 76: UI polish — 10 label/layout tweaks (item 4 deferred to Chat 78)"
git push
```

Update `WIP_OPEN.md` `## Next chat` to Chat 77 (EIA-860 enrichment — spec already in `## Sprint queue` §Chat 77, copy forward). Append `WIP_LOG.md` entry for Chat 76.

---

## Sprint queue

### Chat 77 — EIA-860 enrichment + capacity coalesce

**Part A — `eia860_plants` enrichment.** Populates 891/1367 rows (65.2%); 476 stay blank.

```bash
curl -sL -A 'Mozilla/5.0' \\
  -H 'Referer: https://www.eia.gov/electricity/data/eia860/' \\
  -o eia860_2024.zip \\
  'https://www.eia.gov/electricity/data/eia860/xls/eia8602024.zip'
```

- Extract `3_1_Generator_Y2024.xlsx`
- `pd.read_excel(..., skiprows=1)`, filter `Status == 'OP'`
- Groupby `Plant Code`: `sum(Nameplate Capacity (MW))`, `mode(Technology)`, `mode(Energy Source 1)` → fuel_code
- Fuel map: `NG→Natural gas, WAT→Hydro, NUC→Nuclear, SUB/BIT/LIG→Coal, DFO→Oil, SUN→Solar, WND→Wind, MWH→Battery`
- Left-join on `plant_code` for `layer_id='eia860_plants'` rows

**Part B — capacity column coalesce (all layers).**

| Layer | Source col | Transform |
|---|---|---|
| `eia860_battery` | `capacity` | → `capacity_mw` (already MW) |
| `ercot_queue` | `mw` | → `capacity_mw` |
| `wind` | `cap_kw` | `/ 1000` → `capacity_mw` |
| `solar`, `tceq_gas_turbines` | already `capacity_mw` | — |

Retain source columns for provenance. Update `layers.yaml` popups: `ercot_queue` swap `mw`→`capacity_mw`; `eia860_battery`/`wind` add `capacity_mw`; `eia860_plants` add `capacity_mw`, `technology`, `fuel`.

**Post-enrichment capacity_mw coverage:** `eia860_plants` 891/1367, `eia860_battery` 133/133, `ercot_queue` 1708/1778, `solar` 180/180, `wind` 19269/19464, `tceq_gas_turbines` 6/6. Total ~22,187 rows.

Build, deploy, commit, push. Layer count unchanged (22).

### Chat 78 — Semantic icons (unblocked by Chat 77)

- Icon routing by fuel field on `eia860_plants`, `ercot_queue`
- Layer-level icon for single-fuel: `solar`→sun, `wind`→windmill, `eia860_battery`→battery, `tceq_gas_turbines`→flame
- MW-driven sizing re-audit: `eia860_plants` now has MW for 891/1367 → data-driven sizing on those, static fallback for 476 unmatched

### Chat 79+ — Tax abatement scraper (refinement item #5)

**Spec:** `docs/refinement-abatement-spec.md` (committed 2026-04-23). Regulatory context, leading-indicator hierarchy, keyword taxonomy, `extract_applicant()` regex with both `re.I` + `\b` fixes, field catalog, schema Options A/B, county adapter status (2 validated, 3 stubbed, 18 TODO), 4 live hits, 8 BUILD-gate open questions.

**Stage split:** DISCOVERY is doc-only and effectively closed by the spec commit. BUILD gated on operator sign-off against spec §9. Independent track — slots anywhere after Chat 75b; not blocked by UI / EIA-860 / icon sprints.

---

## Current workstream

TCEQ MERGE complete and in prod (Chats 72–75b). `tceq_gas_turbines` layer live under "Permits" sidebar group with 6 features across 23-county West-TX scope. 22 layers total. Prod deployId `69ea32c7d3733641c9a1bb7c`.

Next: UI polish (Chat 76), EIA-860 enrichment (Chat 77), semantic icons (Chat 78 after 77), tax abatement scraper (Chat 79+, independent track).

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

Full per-session detail in `WIP_LOG.md`.

---

## Prod status

- URL: https://lrp-tx-gis.netlify.app — **requires real User-Agent on curl** (default `curl/x.y.z` UA returns 503; use `-A "Mozilla/5.0"`). See `docs/settled.md` §Data sources.
- Last published deploy: `69ea32c7d3733641c9a1bb7c` (Chat 75b, TCEQ gas turbines).
- Main HEAD: `939ff16`.
- Auto-publish: unlocked.
- Layer set: 22 built clean. `tceq_gas_turbines` (6 features) live under "Permits" sidebar group.
- Prebuilt PMTiles (4): parcels_pecos 4.98 MB, rrc_pipelines 4.73 MB, tiger_highways 3.11 MB, bts_rail 2.16 MB.
- Sprite sheet: 5 icons @ 1x + 2x at `/sprite/sprite.png` + `sprite@2x.png`.
- Data-driven sizing live: `ercot_queue`, `solar`, `eia860_battery`, `wind` (MW), `substations`, `tpit_subs`, `tpit_lines` (kV).
- Sizing gaps (static fallback): `eia860_plants` (capacity_mw blank 1367/1367 — Chat 77 fixes), `transmission` (no voltage in geoms).

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
