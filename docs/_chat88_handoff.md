# Chat 88 handoff — ABATEMENT REFACTOR

Written by prior Chat (resume session) that consumed budget on recon only, no edits shipped. This doc is authoritative; do not re-verify line numbers or file structure. Apply edits directly.

## State at handoff

- Branch `refinement-chat88-abatement-refactor` exists locally on prior Claude's container only — has NOT been pushed. Next chat creates it fresh on clone.
- No edits shipped to any file. Recon only.
- Layer count baseline: 24. No change this chat.
- Prod: `69ebb64823c1c470e0c6f0b1` (Chat 87 bugfix). Unchanged.

## Recon findings (authoritative, do not re-verify)

### layers.yaml — tax_abatements block is lines 411-436

Current state:

```yaml
- id: tax_abatements            # line 411
  file: combined_points.csv
  geom: point
  group: Permits
  label: Tax Abatements          # line 415 — rename target
  color: '#dc2626'
  default_on: false
  radius: 4
  popup:                          # line 419 — reorder + expand
  - name
  - operator
  - county
  - commissioned
  - status
  - project
  - technology
  - capacity_mw
  - poi
  filterable_fields:             # line 429 — prune to technology + status
  - {field: county, type: categorical, label: County}
  - {field: technology, type: categorical, label: Project Type}
  - {field: status, type: categorical, label: Status}
  - {field: commissioned, type: text, label: Meeting Date}
  tippecanoe:
  - -Z0
  - -z14
```

### build.py render_html serializer is lines 633-648

Current layer-dict fields serialized. Missing: `description`, `popup_labels`. Add both to dict (uses `L.get(...)` with safe defaults).

### build_template.html — two patch sites

- `featurePopupHtml()` at line 785–800. The rows-loop at line 791 renders `<td class="k">${k}</td>` using the CSV column name. Change to use `L.popup_labels?.[k] || k` so the display label overrides.
- Popup header needs description line. Insert after title (line 797) conditional on `L.description`.
- Sidebar label at line 857–862. Add `title="${escapeHtml(L.description || '')}"` to the `<label class="layer">` opening tag for tooltip-on-hover.

### combined_points.csv — tax_abatements rows are 39465-39473 (9 rows)

Column order (from line 1 header, 31 columns):
`layer_id,lat,lon,name,plant_code,county,technology,capacity,sector,inr,fuel,mw,zone,poi,entity,funnel_stage,group,under_construction,commissioned,capacity_mw,operator,voltage,osm_id,depth_ft,use,aquifer,project,manu,model,cap_kw,year`

Spec data available for back-populate (from `docs/refinement-abatement-spec.md:138`):
- **Pecos Power Plant LLC** (Reeves, 2025-06-13, line 39471): `mw=226` (already set in column 22/osm_id column — WAIT, check — osm_id is col 23, mw is col 12. Re-verify before editing). Spec says 226 MW, $150-200M. Set `capacity=150-200` (capex in $M).
- **Matterhorn Express Pipeline LLC** (Pecos, 2022-07-25, line 39473): flags say `capex:50M`. Set `capacity=50`. `year=2022` per meeting-date proxy (spec PDF not fetched per task 7 skip rule).

Other 7 rows: no back-populate data available.

**Note on line 39471 current state:** osm_id column (col 23) already has `226` — that is the MW value stored in the wrong column, or column-count miscount. Prior Claude did not verify this. Next chat must `awk -F, 'NR==1||$1=="tax_abatements"{print NR,$0}' combined_points.csv` to confirm column positions before edit, then fix if misalignment found.

## Execution plan (do these in order)

1. **Session open:** clone fresh, create branch.
2. **Verify CSV column alignment** for line 39471 (osm_id=226 anomaly). If columns drifted, halt and diagnose. If intentional data placement, move 226 to `mw` column.
3. **Patch layers.yaml:411-436** — new label, add `description` key, reorder popup list, add `popup_labels` map, prune filterable_fields to technology + status.
4. **Patch build.py** — add `'description': L.get('description', '')` and `'popup_labels': L.get('popup_labels', {})` to serializer dict at line 645.
5. **Patch build_template.html** — popup label override at line 791, description header in popup, sidebar `title` attribute at line 857.
6. **Edit combined_points.csv** — back-populate Pecos Power Plant LLC + Matterhorn only.
7. **Build + deploy + verify** per `WIP_OPEN.md §Deploy pattern`. Expect 24 layers, `errored=0`.
8. **Close-out** per `WIP_OPEN.md §Close-out`: merge branch, delete branch, promote Chat 89 brief, delete this handoff doc, push.

## Proposed popup_labels map for tax_abatements

```yaml
popup_labels:
  operator: applicant
  entity: developer
  commissioned: meeting date
  project: reinvestment zone
  technology: project type
  mw: project MW
  capacity: capex ($M)
  zone: abatement term (yrs)
  use: abatement schedule
  year: announcement year
  cap_kw: jobs commitment
  sector: taxing entities
  poi: agenda URL
  funnel_stage: flags
```

## Proposed popup order per spec §Chat 88 task 5

```yaml
popup:
- name
- operator
- entity
- county
- technology
- mw
- capacity
- zone
- use
- cap_kw
- project
- sector
- status
- poi
```

## Proposed description text

"County-level property tax abatements for new or expanded facilities. Chapter 312 reinvestment zones and Local Development Agreements (HB 5 / SB 1340 successors to the sunsetted Ch.313)."

## Scoping warning for next chat

Chat 88 has 7 distinct tasks across yaml, build.py, template, CSV. Per Readme §7.10 this may be two stages. If execution reveals the template patch requires more than a single-line change (e.g., popup-labels map requires broader refactor to honor across non-tax_abatements layers), split: ship yaml + CSV back-populate + filter changes in this chat; defer description/popup-label template work to Chat 88b.
