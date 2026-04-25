# Chat 92 handoff — field expansion + wells hide

**Status at handoff:** branch `refinement-chat92-field-expansion-wells` has §1 fully merged into `combined_points.csv` AND a `build.py` fragility fix (§6 #15) committed. §1 popup yaml, §2 (tax_abatements popup rename) and §3 (wells min_zoom) not yet started. No build, no deploy, no merge to main.

**Last commits:**
- `8a396c2` — Chat 92 §1 partial: refresh-script + 2026-04-25 CSV
- (this commit) — §1 merge into combined_points.csv + merge_csv/merge_geojson temp+rename fix per §6 #15 + handoff rewrite

---

## What's done

- `scripts/refresh_tceq_gas_turbines.py` rewritten (Issued + Pending sheets, funnel_stage, ISO received-date in `zone`, num_units in `project`).
- `outputs/refresh/tceq_gas_turbines_2026-04-25.csv` — 13 rows, 13/13 geocoded.
- `combined_points.csv` merged: `tceq_gas_turbines` rows 6 → 13. Total rows 39,424 → 39,431. All 11 layers intact (verified by row-count audit pre + post). Columns 30 → 31.
- `build.py` patched: `merge_csv` and `merge_geojson` now write to `<out>.tmp` then `os.replace`, eliminating the read-modify-write data-wipe bug that triggered on first attempted merge this chat. Symmetric guard on `merge_geojson` per §6 #15 even though it was incidentally safe.

---

## What's next (resume scope)

### 1. layers.yaml edits — three layers in one pass

#### `tceq_gas_turbines` (around lines 350–374)

Replace `popup` and `filterable_fields`. Add `popup_labels` block. Order matters; preserve existing `id`, `file`, `geom`, `group`, `label`, `color`, `default_on`, `radius`, `tippecanoe`.

```yaml
  popup:
  - name
  - entity
  - county
  - capacity_mw
  - technology
  - manu
  - model
  - project
  - funnel_stage
  - zone
  - commissioned
  - plant_code
  popup_labels:
    name: Project
    entity: Company
    county: County
    capacity_mw: Project MW
    technology: Mode
    manu: Manufacturer
    model: Turbine model
    project: Number of CTs
    funnel_stage: Status
    zone: Received date
    commissioned: Issue date
    plant_code: Permit No.
  filterable_fields:
  - {field: county, type: categorical, label: County}
  - {field: technology, type: categorical, label: Mode}
  - {field: manu, type: categorical, label: Manufacturer}
  - {field: operator, type: categorical, label: Operator}
  - {field: funnel_stage, type: categorical, label: Status}
  - {field: capacity_mw, type: numeric, label: Project MW}
  - {field: year, type: numeric, label: Received year}
```

#### `tax_abatements` (around lines 411–455)

Schema stays locked (Chat 88 mapping in combined_points.csv unchanged — display-layer only). Replace `popup` + `popup_labels` + `filterable_fields`:

```yaml
  popup:
  - name
  - county
  - commissioned
  - technology
  - mw
  - capacity
  - use
  - sector
  - project
  - poi
  popup_labels:
    name: Applicant
    county: County
    commissioned: Approved date
    technology: Project type
    mw: Project MW
    capacity: Capex ($M)
    use: Abatement schedule
    sector: Taxing entities
    project: Reinvestment zone
    poi: Agenda URL
  filterable_fields:
  - {field: county, type: categorical, label: County}
  - {field: technology, type: categorical, label: Project type}
  - {field: commissioned, type: text, label: Approved date}
  - {field: mw, type: numeric, label: Project MW}
  - {field: capacity, type: numeric, label: Capex ($M)}
```

Drops from popup: `operator`, `entity`, `zone`, `cap_kw`, `status`. Drops from filters: `status`. Per Chat 92 spec.

**Filter type gap (flag in close-out backlog):** spec asked for `commissioned` as date-range filter; build system supports only numeric / categorical / text. Shipped as `text` (multi-select dropdown of distinct ISO dates — functional with 9 rows; not a true range slider). Backlog: implement `date_range` filter type (touches `build.py compute_filter_stats` + `build_template.html filterFieldControlHtml` + matching predicate).

#### `wells` (around lines 56–80)

Single-line: `min_zoom: 6` → `min_zoom: 10`. Do not touch tippecanoe flags. Memory-footprint primary fix. Fallback `hidden: true` only if memory still pressured post-deploy; not anticipated.

### 2. Build + deploy + verify

```bash
cd /home/claude/repo
python3 build.py 2>&1 | tail -20
# Verify final line: built=25 missing=0 errored=0
```

Then Netlify MCP `deploy-site` → CLI proxy → poll `state=ready` → 45s sleep → `curl -A "Mozilla/5.0"` GET on prod root + one tile → grep layer-id count = 25.

### 3. Commit + close-out

Commit message stub:

```
Chat 92 §1-§3: tceq popup expansion + tax_abatements popup rename + wells min_zoom raise + deploy

- layers.yaml: tceq_gas_turbines popup expanded to 12 fields with new
  popup_labels block; filterable_fields rebuilt to 7 incl. funnel_stage
  status filter and numeric capacity_mw + year. tax_abatements popup
  rename "Commissioned"→"Approved date"; popup field order matches Chat
  92 spec (10 fields); filters rebuilt to 5, status removed. wells
  min_zoom 6→10 to reduce statewide memory footprint.
- Layer count unchanged (25). Deploy <id>.
```

Then `bash scripts/close-out.sh refinement-chat92-field-expansion-wells <deploy-id>`.

---

## Carryforward flags

- **§6 #15 prose-rule was unenforced in code.** This chat hit the exact data-wipe pattern that rule describes. Now actually fixed in `build.py`. If a similar read-modify-write helper is added in future, the same guard pattern (temp path + `os.replace`) is required.
- **Filter type gap:** `date_range` filter type not implemented; `commissioned` filter on tax_abatements ships as text-multi-select. Add backlog entry in WIP_OPEN.md `## Open backlog` UI/UX section at close-out.
- **GITHUB_PAT leak (Chat 87):** still unrotated per operator override; valid until 2027-04-21.

---

## Session-open recipe

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
cd /home/claude && rm -rf repo 2>/dev/null
git clone -q https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git repo && cd repo
bash scripts/session-open.sh refinement-chat92-field-expansion-wells
apt-get install -y tippecanoe libcairo2 -q
pip install shapely pmtiles pyyaml cairosvg pandas requests openpyxl --break-system-packages -q
```

session-open.sh detects existing remote branch and checks it out per §10, then auto-prints this handoff.

**Do not call merge_csv again.** §1 merge is already in `combined_points.csv` on this branch. Pre/post audit confirms 39,431 rows / 11 layers / tceq_gas_turbines=13.
