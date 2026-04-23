# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per Readme §10: **`## Next chat`** holds paste-ready instructions for the immediately-next shipping chat (rewritten every close-out). **`## Sprint queue`** holds the forward plan for chats beyond that (updated as plans firm up or change). Operator's per-chat prompt collapses to `Resume.` — all state needed is here.

---

## Next chat

**Chat 75 — TCEQ SHIP.** Main HEAD `3aada1c`. Prod unchanged since Chat 71 (`69e96a36`). Chat 73 merged TCEQ branch (`ea7e39d`); Chat 74 landed TCEQ data/config (`4292bf2`) + EIA-860 research notes (`3aada1c`) but deferred build. Chat 75 = build, deploy, ship + three short doc edits.

### Session open (single block)

```bash
cd /home/claude && git clone https://github_pat_<see CREDENTIALS.md>@github.com/10thMuses/lrp-tx-gis.git && cd lrp-tx-gis
apt-get install -y tippecanoe libcairo2 -q
pip install shapely pmtiles pyyaml cairosvg --break-system-packages -q
grep -c '^tceq_gas_turbines,' combined_points.csv   # expect 6
grep -c 'Permits' layers.yaml build_template.html   # both 1
```

Side task post-ship: `build.py` now imports `build_sprite.py` which requires `cairosvg`. Add `cairosvg` to Readme session-open install list.

### Build

```bash
python build.py
```

Gate: 22 layers, `errored=0`, `tceq_gas_turbines feature_count=6`.

### Deploy

Netlify MCP from `/mnt/user-data/outputs/dist/`. Sleep 45. Curl 200.

### Doc edits

1. **`docs/settled.md`** — append under "Data sources":

   ```
   ### TCEQ sources closed 2026-04-23
   - tceq_pws: dropped (HTTP 400, operator decision)
   - tceq_pbr: scoped out (CRPUB HTML-scrape, RRC-MFT analog preferred)
   - Nominatim fallback accepted for Census zero-match (1.1s throttle)
   ```

2. **`WIP_OPEN.md`** — rewrite `## Next chat` with Chat 76 UI-polish instructions (see Sprint queue §Chat 76); update `## Prod status` deploy ID + layer count `21 → 22`; remove `tceq_pws`/`tceq_pbr` from `## Open backlog` (now settled); append row to `## Recent sessions`.

3. **`WIP_LOG.md`** — append entries for Chats 73, 74, 75 with SHAs + deploy ID + layer delta.

### Commit + push

```bash
git add -A
git commit -m "Chat 75: ship TCEQ gas turbines (21→22 layers)"
git push
```

### Budget escape

If build/deploy consumes budget: ship TCEQ, commit, push, STOP. Roll doc edits (1–3) into a Chat 75b doc-only close-out. Do NOT attempt UI-polish (Chat 76) or EIA-860 (Chat 77) in this chat.

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

Partial work from concurrent Chat 74 research track — **NOT committed.** Reconstruct from this spec.

**Architecture:**
- Per-county adapter pattern. 2/5 tested: Pecos (WordPress), Reeves (CivicEngage). 3 stubbed (Ward, Culberson, Ector) — URL patterns unverified.
- Keyword taxonomies ready: `KW_ABATEMENT`, `KW_PROJECT_RENEWABLE`, `KW_PROJECT_DC`, `KW_PROJECT_GAS`, `KW_DEVELOPERS`, `KW_LOADS`.
- Tested helpers: `classify()`, `extract_zone()`, `extract_capacity()`, `parse_meeting_date()`.
- **Known bug:** `extract_applicant()` missing `flags=re.I` in both regex searches.

**Live hits confirmed during discovery:**

| County | Hit | Date |
|---|---|---|
| Pecos | Longfellow Renewable Energy Reinvestment Zone | 1/13/2025 |
| Pecos | Poolside Inc. Ch. 312 abatement (AI compute, not solar) | 11/10/2025 agenda |
| Pecos | Apex Clean Energy donation signal | 11/10/2025 |
| Reeves | Pecos Power Plant LLC — 226 MW natgas recips, $150–200M | 6/13/2025 notice |

**Settled regulatory context (do not re-litigate):**
- Ch. 313 expired 12/31/2022
- Ch. 403 / JETI Act (eff 1/1/2024) explicitly excludes renewables
- Active abatement mechanisms for renewables: Ch. 312 + Ch. 381
- Leading-indicator hierarchy: lease signing (private) → ERCOT queue → reinvestment zone creation (commissioners court) → abatement application + 30-day notice → executed → Comptroller Ch. 312 filing
- Commissioners court agendas = real leading signal
- Comptroller Ch. 312 DB: JS-loaded (static fetch fails) + multi-month lag — not usable as primary source

**Chat 79 tasks:**
1. Reconstruct `scripts/scrape_abatements.py` from this spec
2. Apply `re.I` fix to `extract_applicant()`
3. Verify Ward, Culberson, Ector agenda URL patterns
4. Commit script + add `.github/workflows/abatement-scrape.yml` (weekly cron)
5. Run full 5-county scan, commit first CSV to `data/abatements/`
6. Close refinement item #5 discovery phase in `WIP_OPEN.md`
7. Layer build (geocode RZs + applicant parcels → `tax_abatements` layer) = separate future chat

Independent track — can slot anywhere after Chat 75; not blocked by TCEQ / EIA-860 / UI sprints.

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
