# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per Readme §10: **`## Next chat`** holds paste-ready instructions for the immediately-next shipping chat (rewritten every close-out). **`## Sprint queue`** holds the forward plan for chats beyond that (updated as plans firm up or change). Operator's per-chat prompt collapses to `Resume.` — all state needed is here.

---

## Next chat

**Chat 75b — TCEQ SHIP (deploy + close-out).** Main HEAD `92d25c72`. Prod unchanged since Chat 71 (`69e96a36`, 21 layers). Chat 75 landed abatement-discovery spec + multi-chat rules (`92d25c72`) and rebuilt locally clean (22 layers, `errored=0`, `tceq_gas_turbines=6`) then stopped pre-deploy per operator direction. Chat 75b rebuilds in fresh container, deploys, and lands close-out docs.

### Session open (single block)

```bash
cd /home/claude && git clone https://github_pat_<see CREDENTIALS.md>@github.com/10thMuses/lrp-tx-gis.git && cd lrp-tx-gis
apt-get install -y tippecanoe libcairo2 -q
pip install shapely pmtiles pyyaml cairosvg --break-system-packages -q
grep -c '^tceq_gas_turbines,' combined_points.csv   # expect 6
grep -c 'Permits' layers.yaml build_template.html   # both 1
```

### Build

```bash
python build.py
```

Gate: 22 layers, `errored=0`, `tceq_gas_turbines feature_count=6` (confirmed clean in Chat 75 — re-verify in fresh container).

### Deploy

Netlify MCP from `/mnt/user-data/outputs/dist/`. Sleep 45. Curl 200 on prod URL. Layer spot-check: one `tceq_gas_turbines` tile endpoint.

### Doc edits (post-deploy)

1. **`docs/settled.md`** — append under `## Data sources`:

   ```
   **TCEQ sources closed 2026-04-23.** `tceq_pws` dropped (HTTP 400 on original endpoint, operator decision). `tceq_pbr` scoped out (CRPUB HTML-scrape, same failure class as RRC MFT — see scoped-out block). `tceq_nsr_pending` scoped out for same reason. Nominatim fallback accepted for Census geocoder zero-match (1.1s throttle).
   ```

2. **`WIP_OPEN.md`** — rewrite `## Next chat` to Chat 76 UI-polish (spec already in `## Sprint queue` §Chat 76, copy forward). Update `## Prod status`: new deploy ID, layer count `21 → 22`. Remove `tceq_pws`, `tceq_pbr`, `tceq_nsr_pending` from `## Open backlog` (now settled). Append rows to `## Recent sessions` for Chats 73, 74, 75, 75b.

3. **`WIP_LOG.md`** — append entries for Chats 73 (TCEQ branch merge), 74 (TCEQ data/config + EIA-860 research), 75 (abatement spec + rules + TCEQ build, no deploy), 75b (TCEQ deploy + close-out). Each with SHA + deploy ID where applicable.

### Commit + push

```bash
git add -A
git commit -m "Chat 75b: ship TCEQ gas turbines (21→22 layers) + close-out docs"
git push
```

### Budget note

Chat 75 split off to preserve budget headroom for deploy + docs. Deploy is the priority — if docs consume budget, ship deploy + commit + push first, split docs to a 75c doc-only close-out. Do NOT attempt Chat 76 (UI polish) or Chat 77 (EIA-860) in this chat.


---

## Sprint queue

### Chat 76 — UI polish (data-independent)

10 labeling/layout tweaks. Item 4 blocks on Chat 77 — defer to Chat 78.

1. Sidebar filters → dropdown checkboxes (collapse vertical footprint)
2. Title-case all multi-word layer labels
3. "Solar Plants" → "Solar Farms"
4. **DEFER to Chat 78** — semantic icons keyed to fuel/technology; requires EIA-860 enrichment
5. "EIA-860 plants" → "Power Plants (EIA-860)"
6. Water & Regulatory group → bottom of sidebar (after Reference)
7. "Natural gas hub" → "WAHA Natural Gas Hub" + circle marker on point
8. "ERCOT GIR queue" → "ERCOT Interconnect Queue (as of <source date>)" — vintage from ERCOT xlsx timestamp
9. "TWDB wells" → "Groundwater Wells (TWDB)"
10. "MPGCD Management Zone" → "Groundwater District Management Zone 1"
11. "RRC pipelines (≥20\" transmission)" → `Oil & Gas Pipelines (>20", RRC)`

### Chat 77 — EIA-860 enrichment + capacity coalesce

**Part A — `eia860_plants` enrichment.** Populates 891/1367 rows (65.2%); 476 stay blank.

```bash
curl -sL -A 'Mozilla/5.0' \
  -H 'Referer: https://www.eia.gov/electricity/data/eia860/' \
  -o eia860_2024.zip \
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

**Stage split:** DISCOVERY is doc-only and effectively closed by the spec commit. BUILD gated on operator sign-off against spec §9. Independent track — slots anywhere after Chat 75; not blocked by TCEQ / EIA-860 / UI sprints.

---

## Current workstream

TCEQ MERGE in flight across Chats 72–75. Chat 72 pulled bulk data (`turbine-lst.xlsx` v2026.4.3, 6 rows, 23-county West TX, Received ≥ 2020, 6/6 geocoded via Nominatim fallback). Chat 73 merged refresh branch to main (`ea7e39d`). Chat 74 appended data to `combined_points.csv`, added layer to `layers.yaml` under new "Permits" group + EIA-860 research — deferred build on budget. Chat 75 ships.

Parallel-safe after Chat 75: UI polish (Chat 76), EIA-860 enrichment (Chat 77), abatement scraper (Chat 79+).

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

Full per-session detail in `WIP_LOG.md`.

---

## Prod status

- URL: https://lrp-tx-gis.netlify.app
- Last published deploy: `69e96a36b4de5c3af264ab27` (Chat 71, Stage 4 Sizing + Watermark). **Unchanged across Chats 72–74.**
- Main HEAD: `3aada1c`.
- Auto-publish: unlocked.
- Layer set: 21 built clean at last deploy. TCEQ data + config on main but unbuilt → Chat 75 brings to 22.
- Prebuilt PMTiles (4): parcels_pecos 4.98 MB, rrc_pipelines 4.73 MB, tiger_highways 3.11 MB, bts_rail 2.16 MB.
- Sprite sheet: 5 icons @ 1x + 2x at `/sprite/sprite.png` + `sprite@2x.png`.
- Data-driven sizing live: `ercot_queue`, `solar`, `eia860_battery`, `wind` (MW), `substations`, `tpit_subs`, `tpit_lines` (kV).
- Sizing gaps (static fallback): `eia860_plants` (capacity_mw blank 1367/1367 — Chat 77 fixes), `transmission` (no voltage in geoms).

---

## Open backlog

**Standing watch item:** TCEQ diesel-genset NSR permits live only in CRPUB (not in `turbine-lst.xlsx`). Gap for data-center backup-power intelligence if that becomes a use case. Revisit only if TCEQ publishes bulk feed or operator authorizes CRPUB scrape.

**Deferred sources (indefinite):**
- `tceq_nsr_pending` — no bulk source; CRPUB HTML-scrape authorization declined.

**Data-pipeline gaps (non-blocking, addressed by queued chats):**
- `eia860_plants` capacity_mw / technology / fuel — Chat 77.
- `combined_points.csv` blank `operator` / `commissioned` on EIA point layers — filter UI provides leverage; out of scope unless prioritized.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar. Low priority.

**Permanently excluded:**
- `rrc_wells_permian` — see `docs/settled.md` §"Scoped-out data sources".
- `tceq_pws`, `tceq_pbr` — entries land in `docs/settled.md` as part of Chat 75 close-out.

**Other (non-GIS):**
- Grid Wire Vol. 7.
- Tier 2 water availability assessments, cluster intelligence sheets, Excel returns model.

---

## GitHub sync — live

Repo: `github.com/10thMuses/lrp-tx-gis`. Authority: `main` = canonical. Working dir: `/home/claude/repo/`. Protocol: `Readme.md` §7 + `docs/principles.md` §5.
