# Chat 76 handoff — UI polish retry

State: main `8da2b0f` (Chat 75b close-out). Prior Chat 76 attempt was staged+build-verified but never committed; container reset wiped it. Re-do from scratch. No code in the repo has moved. Prod still `69ea32c7d3733641c9a1bb7c`, 22 layers.

Scope source of truth: `WIP_OPEN.md` §Next chat. Item 4 is deferred to Chat 78. 10 tweaks execute.

Operator ordering override (binding): **edits → `python build.py` → `git commit` + `git push` FIRST → then deploy.** Do not trade the commit for a deploy attempt. If Netlify returns 503 after 45s warm-up, that becomes Chat 76b — commit already landed.

Target final commit message: `Chat 76: UI polish — 10 label/layout tweaks (item 4 deferred to Chat 78)`.

---

## Session open

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
cd /home/claude && rm -rf repo 2>/dev/null; git clone -q https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git repo && cd repo
git config user.email "claude@lrp.local" && git config user.name "Claude (LRP GIS)"
apt-get install -y tippecanoe libcairo2 -q
pip install shapely pmtiles pyyaml cairosvg --break-system-packages -q
```

**Delete this handoff doc as part of your edit batch** — per Readme §7.7 it is removed before the close-out commit lands. `git rm docs/_chat76_handoff.md` goes into the same commit.

---

## Line map (verified against `8da2b0f` — do not re-grep)

`layers.yaml` — 22 layers. `label:` line numbers:

| # | Line | Current label | Group |
|---|---|---|---|
| a | 6 | `Counties (outline)` | Reference |
| b | 19 | `Cities` | Reference |
| c | 31 | `Caramba North (1,681 ac)` | Land & Deal |
| d | 45 | `MPGCD Zone 1 (approx.)` | Water & Regulatory |
| e | 60 | `TWDB wells` | Water & Regulatory |
| f | 85 | `EIA-860 plants` | Generation |
| g | 104 | `Battery storage (EIA-860)` | Generation |
| h | 125 | `Wind turbines (USWTDB)` | Generation |
| i | 152 | `Solar plants (EIA-860)` | Generation |
| j | 171 | `"Transmission \u2265100 kV"` | Transmission & Grid |
| k | 188 | `Substations (OSM)` | Transmission & Grid |
| l | 208 | `Substation Upgrades` | Transmission & Grid |
| m | 227 | `Transmission Upgrades` | Transmission & Grid |
| n | 242 | `ERCOT GIR queue` | Projects |
| o | 276 | `Pecos County parcels` | Land & Deal |
| p | 292 | `Natural gas hubs` | Reference |
| q | 305 | `County labels` | Reference |
| r | 318 | `"RRC pipelines (\u226520\" transmission)"` | Pipelines |
| s | 331 | `TCEQ gas turbines` | Permits |
| t | 356 | `Highways (Interstate + US)` | Reference |
| u | 366 | `Rail (main lines)` | Reference |
| v | 377 | `Water mains (approximate)` | Water & Regulatory |

`build_template.html`:

- Line 75: `.filter-multi` CSS (max-height 96px scroll box) — target of item 1.
- Lines 527–531: `filter-multi` render in `filterFieldControlHtml()` (categorical branch) — target of item 1.
- Line 371 and lines 404–420: `geom === 'label'` render path — extension site for item 7 marker.
- Line 715: `GROUP_ORDER` array — target of item 6.
- Lines 427–435 + 474–477: visibility / filter handlers — add `__marker` branch mirroring `__icon` for item 7.

`combined_geoms.geojson`: WAHA hub feature confirmed single point at `[-103.183, 31.215]`, `layer_id: labels_hubs`, `source_date: 2026-04-21`. No change needed — the circle renders from the same feature, no data rewrite.

---

## Exact edits

### Item 2 — title-case (combined with items 3, 5, 7–11 below so each label line is edited once)

Final label text by line number. Lines not listed do not change (already title-case, single word, or intentional lowercase SI unit):

| Line | New value |
|---|---|
| 6 | `Counties (Outline)` |
| 45 | `Groundwater District Management Zone 1` (item 10) |
| 60 | `Groundwater Wells (TWDB)` (item 9) |
| 85 | `Power Plants (EIA-860)` (item 5) |
| 104 | `Battery Storage (EIA-860)` |
| 125 | `Wind Turbines (USWTDB)` |
| 152 | `Solar Farms (EIA-860)` (item 3) |
| 242 | `ERCOT Interconnect Queue (as of 2026-04-21)` (item 8) |
| 276 | `Pecos County Parcels` |
| 292 | `WAHA Natural Gas Hub` (item 7 — text) |
| 305 | `County Labels` |
| 318 | `Oil & Gas Pipelines (>20", RRC)` (item 11) |
| 331 | `TCEQ Gas Turbines` |
| 366 | `Rail (Main Lines)` |
| 377 | `Water Mains (Approximate)` |

Intentional non-changes: line 19 `Cities`, line 31 `Caramba North (1,681 ac)` (ac = acre unit), line 171 `Transmission ≥100 kV` (kV is an SI unit, always lowercase k), line 188 `Substations (OSM)`, lines 208/227 already title-case, line 356 `Highways (Interstate + US)` already title-case.

Item 11 note: operator spec is `Oil & Gas Pipelines (>20", RRC)` — the `>` replaces `≥` and the inline `"` needs YAML escaping. Use double-quoted scalar: `label: "Oil & Gas Pipelines (>20\", RRC)"`.

Item 8 vintage note: `2026-04-21` matches WAHA's `source_date` in `combined_geoms.geojson` and aligns with Chat 40 (last ERCOT pull). If operator supplies a different vintage in the chat prompt, use that instead. Commit message unchanged either way.

### Item 6 — group ordering

`build_template.html` line 715. Current:
```js
const GROUP_ORDER = ['Land & Deal', 'Water & Regulatory', 'Generation', 'Transmission & Grid', 'Pipelines', 'Permits', 'Projects', 'Reference'];
```
New:
```js
const GROUP_ORDER = ['Land & Deal', 'Generation', 'Transmission & Grid', 'Pipelines', 'Permits', 'Projects', 'Reference', 'Water & Regulatory'];
```

### Item 7 — WAHA circle marker on `labels_hubs`

Two-part change.

**yaml** (`layers.yaml` labels_hubs block, around lines 288–300): add `show_marker: true` key. The layer stays `geom: label` — the marker is an additive companion layer.

**template** (`build_template.html`):

1. After the `geom === 'label'` symbol layer is added (around line 380), add a sibling circle layer when `L.show_marker` is truthy:

```js
if (L.geom === 'label' && L.show_marker) {
  map.addLayer({
    id: `${lyrId}__marker`,
    type: 'circle',
    source: srcId,
    'source-layer': L.id,
    minzoom: L.min_zoom || 0,
    paint: {
      'circle-radius': 6,
      'circle-color': L.color,
      'circle-stroke-width': 2,
      'circle-stroke-color': '#ffffff',
    },
    layout: { visibility: L.default_on ? 'visible' : 'none' },
  }, lyrId);  // beneath the text symbol
}
```

2. `setLayerVisibility` (around lines 427–435) — add `__marker` branch:
```js
if (L.geom === 'label' && L.show_marker) {
  try { map.setLayoutProperty(`lyr_${L.id}__marker`, 'visibility', v); } catch (e) {}
}
```

3. `setLayerFilter` (around lines 474–477) — add:
```js
if (L.geom === 'label' && L.show_marker) { try { map.setFilter(`lyr_${L.id}__marker`, expr); } catch (e) {} }
```

No order-dependency with the symbol layer because the `before` arg in `addLayer` inserts the circle below the existing symbol.

### Item 1 — filter dropdowns (collapse vertical footprint)

Interpretation: the `.filter-multi` scrollable checkbox box (always-visible 96px max-height) becomes a disclosure widget. Closed state shows `<label> (N selected)` as a one-line summary; open state shows the existing checkbox list.

**CSS** (`build_template.html`, line 75 block). Replace:
```css
.filter-multi { max-height: 96px; overflow-y: auto; border: 1px solid var(--border); border-radius: 4px; padding: 3px 6px; background: #fff; }
```
with:
```css
.filter-multi { border: 1px solid var(--border); border-radius: 4px; background: #fff; }
.filter-multi > summary { cursor: pointer; padding: 3px 6px; font-size: 11px; user-select: none; list-style: none; }
.filter-multi > summary::-webkit-details-marker { display: none; }
.filter-multi > summary::before { content: "▸"; display: inline-block; width: 10px; color: var(--muted); }
.filter-multi[open] > summary::before { content: "▾"; }
.filter-multi > .filter-multi-body { max-height: 96px; overflow-y: auto; padding: 3px 6px; border-top: 1px solid var(--border); }
```

**JS** (`build_template.html`, lines 527–531). Replace the categorical return block:
```js
const lis = vals.map(v => `<label><input type="checkbox" value="${escapeHtml(v)}" ${selected.has(v) ? 'checked' : ''}> ${escapeHtml(v)}</label>`).join('');
return `<div class="filter-field" data-field="${f.field}" data-type="categorical">
  <span class="filter-field-label">${escapeHtml(f.label)} (${vals.length})</span>
  <div class="filter-multi">${lis}</div>
</div>`;
```
with:
```js
const lis = vals.map(v => `<label><input type="checkbox" value="${escapeHtml(v)}" ${selected.has(v) ? 'checked' : ''}> ${escapeHtml(v)}</label>`).join('');
const selCount = selected.size;
const summaryTxt = selCount > 0 ? `${escapeHtml(f.label)} — ${selCount} selected` : `${escapeHtml(f.label)} (${vals.length})`;
return `<div class="filter-field" data-field="${f.field}" data-type="categorical">
  <details class="filter-multi"${selCount > 0 ? ' open' : ''}>
    <summary>${summaryTxt}</summary>
    <div class="filter-multi-body">${lis}</div>
  </details>
</div>`;
```

Change is additive — `<details>` is native HTML, no JS event rebinding needed. The checkbox event handler at line 571 (`panel.querySelectorAll('input[type=checkbox]')`) still matches the inputs because they're still descendants of the filter-field. No filter-logic changes.

---

## Execution order (operator override — binding)

1. `git rm docs/_chat76_handoff.md` (delete this file first)
2. Apply edits: `layers.yaml` (15 label lines + 1 `show_marker: true` key) and `build_template.html` (CSS block, filter JS, GROUP_ORDER line, label-marker render/visibility/filter additions).
3. `python build.py` — gate: `built=22, errored=0`.
4. `git add -A && git commit -m "Chat 76: UI polish — 10 label/layout tweaks (item 4 deferred to Chat 78)" && git push`
5. **Stop if push fails.** Resolve before any deploy attempt. No deploy retries burn budget that should be spent ensuring the commit is safe.
6. Netlify MCP deploy from `/mnt/user-data/outputs/dist/`. `sleep 45`. Curl verify with `-A "Mozilla/5.0"`.
7. If deploy ready → full close-out (update `WIP_OPEN.md` `## Next chat` to Chat 77, copy Chat 77 spec forward from current `## Sprint queue`; append `WIP_LOG.md` entry for Chat 76).
8. If deploy 503 persists past 45s warm-up window → commit the close-out with Chat 76b as Next chat = "deploy retry only, no code changes". Commit already landed in step 4 so no code loss.

---

## Known ERCOT vintage open item

Tweak 8 needs a source date for the label. No vintage field exists on `ercot_queue` rows in `combined_points.csv` or any doc in the repo. Default chosen: `2026-04-21` (matches the WAHA hub `source_date` in `combined_geoms.geojson`, which was the last ERCOT pull per WIP_LOG Chat 40). Operator can override in the chat prompt. If overridden, substitute literally in the label text at line 242 — no other edits change.
