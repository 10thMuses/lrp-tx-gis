# Chat 92 handoff — field expansion + wells hide

**Status at handoff:** branch `refinement-chat92-field-expansion-wells` has §1 partial committed (refresh-script + 2026-04-25 CSV). §2 (tax_abatements popup rename) and §3 (wells min_zoom) not yet started. No build, no deploy, no merge to main.

**Last commit:** `8a396c2` — "Chat 92 §1 partial: tceq_gas_turbines refresh-script field expansion + 2026-04-25 refresh output"

---

## What's done

- Refresh script `scripts/refresh_tceq_gas_turbines.py` rewritten:
  - Reads both Issued + Pending sheets (was Issued only).
  - `funnel_stage` taxonomy: `issued` / `renewed` / `modified` / `pending`, derived from sheet name + Received-cell text prefix.
  - Received-date ISO populated in `zone` (was year-only via `year` column; `year` still populated for backward compat).
  - `num_units` populated in `project`.
  - `plant_code` keeps Permit No. — **no INR mapping added** per Chat 92 confirmation (source has no separate INR column; only "Permit No.", PSD, GHG Permit No.; first is the TCEQ NSR permit number, the others are federal companion permits).
- Refresh output committed: `outputs/refresh/tceq_gas_turbines_2026-04-25.csv`. 13 rows (was 6). Status breakdown: 6 issued, 3 renewed, 4 pending. 13/13 geocoded via Nominatim City+County+TX.

---

## What's next (resume scope)

### 1. Merge refreshed CSV into combined_points.csv

`build.py merge` resolves source from `/mnt/project/combined_points.csv` (read-only) and writes output to `/mnt/user-data/outputs/`. Under the repo-as-source-of-truth model the repo-local file at `/home/claude/repo/combined_points.csv` is canonical. Bypass the CLI subcommand and call `merge_csv()` directly:

```python
import sys
sys.path.insert(0, '/home/claude/repo')
from build import merge_csv
r = merge_csv(
    '/home/claude/repo/combined_points.csv',
    '/home/claude/repo/outputs/refresh/tceq_gas_turbines_2026-04-25.csv',
    'tceq_gas_turbines',
    '/home/claude/repo/combined_points.csv'  # in-place
)
print(r)
```

Verify: pre-merge row count for layer_id=tceq_gas_turbines should be 6; post-merge should be 13. No other layer rows touched.

### 2. layers.yaml edits

#### `tceq_gas_turbines` (lines 350–374)

Replace popup + filterable_fields. Order matters; preserve existing `id`, `file`, `geom`, `group`, `label`, `color`, `default_on`, `radius`, `tippecanoe`. New popup + popup_labels + filterable_fields:

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

Spec asked for filters on `mw` (numeric) and `technology` (categorical). `mw` and `capacity_mw` hold the same value (project MW); used `capacity_mw` for the filter for consistency with EIA layers. `technology` value strings are e.g. "Gas turbine SC" / "Gas turbine CC" — the categorical filter populates from the data automatically.

#### `tax_abatements` (lines 411–455)

Per Chat 92 spec §2, popup label rename + filter rebuild. **Schema stays locked** (Chat 88 mapping in combined_points.csv unchanged — these are display-layer-only edits).

New popup + popup_labels + filterable_fields:

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

**Filter type gap (flag in close-out):** spec called for `commissioned` as a "date range" filter, but build system supports only `numeric` / `categorical` / `text`. Shipped as `text`, which auto-populates as multi-select dropdown of distinct ISO dates (functional with 9 rows; not a true range slider). Add to backlog: implement `date_range` filter type (touches `build.py compute_filter_stats` + `build_template.html` filterFieldControlHtml + matching predicate). Operator unblocked acceptance pre-emptively.

Drop `entity`, `zone`, `cap_kw`, `status` from popup. Drop `status` from filters. Per spec: "no `status` in popup or filters."

#### `wells` (lines 56–80)

Single-line change: `min_zoom: 6` → `min_zoom: 10`. Do not touch tippecanoe flags or anything else. Memory-footprint primary fix. Fallback (`hidden: true`) only if memory still pressured after deploy; not anticipated.

### 3. Build + deploy + verify

Standard pattern from §Next chat / §Deploy pattern:

```bash
cd /home/claude/repo
python3 build.py 2>&1 | tail -20
# Verify build report shows 25 layers, errored=0
```

Then Netlify MCP → CLI proxy → poll → 45s sleep → curl GET → grep for layer ids → expect 25.

### 4. Commit + close-out

Commit message stub:

```
Chat 92 §2-§3: tax_abatements popup rename + wells min_zoom raise + tceq merge + deploy

- combined_points.csv: tceq_gas_turbines rows refreshed 6→13 (Pending sheet
  added, status taxonomy populated, full received-date ISO + num_units
  captured).
- layers.yaml: tceq_gas_turbines popup expanded to 12 fields with new
  popup_labels; filterable_fields rebuilt to 7 fields including funnel_stage
  status filter and numeric capacity_mw + year. tax_abatements popup
  rename "Commissioned" → "Approved date"; popup field order matches
  Chat 92 spec; filters rebuilt to 5 fields, status removed. wells
  min_zoom 6 → 10 to reduce statewide memory footprint.
- Layer count unchanged (25). Deploy <id>.
```

Then standard close-out per WIP_OPEN.md `## Next chat → ## Close-out` block (fetch / checkout main / merge --no-ff / rewrite WIP_OPEN.md / push / delete remote branch).

---

## Carryforward flags

- **Filter type gap:** date_range filter type not implemented; `commissioned` filter on tax_abatements ships as text-multi-select. Add backlog entry in WIP_OPEN.md `## Open backlog` UI/UX section at close-out.
- **GITHUB_PAT leak:** still unrotated per operator override; valid until 2027-04-21. Flag again at close-out.

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

session-open.sh will detect the existing remote branch and check it out (Readme §10), then auto-print this handoff doc per §9.7.
