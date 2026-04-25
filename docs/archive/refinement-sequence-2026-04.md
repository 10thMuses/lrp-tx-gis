# Map Refinement Sequence

Planned discrete shipping chats to refine the GIS map post-Hanwha delivery. Each stage is a separate chat.

Integrates the 10M-port operating protocol: natural-language prompts, `Readme.md` + `WIP_OPEN.md` as source of truth, no `CURRENT TASK:` framing, clone-edit-push per `Readme.md` §7.

Refinement uses a **branch + PR workflow**, not direct-to-main. Sequence is explicitly scoped per `docs/settled.md` §"GitHub sync" — PR workflow allowed when sequenced work benefits from reviewable diffs.

---

## Universal rules for every refinement chat

1. **First action: clone repo.** Per `Readme.md` §7. Read `Readme.md` (source of truth) and `WIP_OPEN.md` (active state) before any other action.
2. **Create a stage-named branch.** Pattern: `refinement-<stage-slug>`. Example: `refinement-filter-ui`, `refinement-bug-sweep`, `refinement-visual-overhaul`.
3. **Work on the branch only.** Commit frequently with clear messages.
4. **Open a PR at end of chat.** Do not merge. Do not deploy to prod. Operator merges and deploys manually.
5. **Stay in stage scope.** Do not touch files outside the stage's assigned tasks.
6. **If blocked by genuine ambiguity, stop and ask** per `Readme.md` §2 acceptable-asks list. Otherwise pick the most plausible interpretation and flag the assumption.
7. **Do not assume empty data fields mean anything specific.** Only act on affirmative evidence.
8. **PR description is the handoff.** Per `Readme.md` §10 — handoff content in the PR body, not as a separate upload. Include: files changed, decisions made, anything the next stage needs to know.
9. **WIP_OPEN.md update + WIP_LOG.md entry as final action.** Per `Readme.md` §7 rule 3.

Trigger phrases (`build.`, `refresh <layer>.`, `add layer...`) remain valid invocations for ad-hoc work outside this sequence. Refinement stages use natural-language triggers instead (examples in stage specs below).

---

## Stage dependency map

```
FILTER UI (foundation) ──┬──► BUG SWEEP ──► VISUAL OVERHAUL ──► SIZING + WATERMARK ──┬──► ABATEMENT BUILD
                         │                                                            │
                         ├──► ABATEMENT DISCOVERY ────────────────────────────────────┘
                         │
                         ├──► DC RESEARCH ──► DC BUILD ──► DC AUTO-REFRESH
                         │
                         └──► TCEQ REFRESH ──► TCEQ MERGE
```

Parallel-safe after FILTER UI merges: ABATEMENT DISCOVERY, DC RESEARCH, TCEQ REFRESH.
Sequential main track: FILTER UI → BUG SWEEP → VISUAL OVERHAUL → SIZING + WATERMARK.
Build stages (ABATEMENT BUILD, DC BUILD) require SIZING + WATERMARK merged so visual conventions are locked.

---

## Stage specs

### Stage: FILTER UI (foundation)

**Branch:** `refinement-filter-ui`
**Depends on:** nothing
**Blocks:** everything else

Tasks:

1. Inspect current `layers.yaml` and build pipeline. Confirm understanding of layer inventory and config structure.
2. Build generic per-layer filter UI:
   - Dropdown per layer; user picks any field in that layer's data
   - Numeric fields → range slider or min/max input
   - Categorical fields → multi-select
   - Date fields → date range
   - Clear/reset control per layer
   - Works across ALL active layers; not hardcoded per layer
   - YAML flag: `filterable_fields:` per layer specifies which fields surface in the UI
3. Piggyback yaml tweaks (same files touched, cheap to bundle):
   - Remove Caramba South layer entirely
   - Reorder TPIT substation popup — voltage before owner
   - Adjust `min_zoom` / `max_zoom` on road, county, highway labels so labels appear at more zoom levels (both zoomed in and out)
   - Expand popup/label templates across ALL layers to surface every available data field
4. Do NOT touch: icons, colors, sizing, sprite sheet, watermark, measure tool, Waha, Pecos parcels. Those are later stages.

Deliverables: PR with filter UI + 4 yaml tweaks.

---

### Stage: BUG SWEEP

**Branch:** `refinement-bug-sweep`
**Depends on:** FILTER UI merged
**Blocks:** VISUAL OVERHAUL

Tasks:

1. **Waha gas hub** — diagnose why not showing; fix.
2. **Pecos County parcels layer** — diagnose why nothing renders; fix. If data file is broken, document and propose solution before rebuilding.
3. **Measure tool closes when user clicks a popup.** Fix state interaction so measure tool persists through popup clicks.

Deliverables: PR with three bug fixes, root cause documented per bug.

---

### Stage: VISUAL OVERHAUL

**Branch:** `refinement-visual-overhaul`
**Depends on:** BUG SWEEP merged
**Blocks:** SIZING + WATERMARK

Tasks:

1. **Contrast + color separation across all layers.**
   - Distinct colors for transmission vs. pipelines vs. upgrades (currently similar blues are ambiguous)
   - Larger icons/dots with prominent halos
   - Higher contrast at all zoom levels
   - Iterate if first pass insufficient
2. **Semantic icons via new/updated sprite sheet:**
   - Solar → yellow sun
   - Wind → windmill
   - Battery storage → battery
   - Any other energy-type layers with intuitive icons
3. Update sprite sheet assets and references.

Deliverables: PR with new palette, updated sprite sheet, layer style changes. No brand/license constraints on icon sources.

---

### Stage: SIZING + WATERMARK

**Branch:** `refinement-sizing-watermark`
**Depends on:** VISUAL OVERHAUL merged
**Blocks:** ABATEMENT BUILD, DC BUILD

Tasks:

1. **Data-driven icon sizing.**
   - Scale icon size by MW (power plants, ERCOT queue, data centers) or kV (substations, transmission)
   - Relative scaling, not absolute
   - Audit which layers have clean power fields; apply sizing only to those. Flag gaps — do not guess.
2. **Confidential watermark.**
   - Text: `CONFIDENTIAL — [date]`
   - Position: bottom corner
   - Opacity: visible, not too translucent (~70%)
   - Applied to on-map view AND print exports (same treatment)

Deliverables: PR with sizing expressions and watermark implementation.

---

### Stage: UI POLISH v2

**Branch:** `refinement-ui-polish-v2`
**Depends on:** nothing (live-UI layer only)
**Blocks:** nothing

Tasks:

1. **Filter UI — dropdowns with auto-populate + multi-select.** All text-input filters replaced with dropdowns populated from unique values present in each layer's data. Categorical fields: multi-select. Numeric/date fields: range pickers (unchanged). No free-text entry.
2. **Default map open state.**
   - Layers ON by default: `caramba_north`, `counties` (outline), `county_labels`, `cities`, `waha`
   - Basemap: `esri_imagery` (satellite)
   - Initial viewport: zoomed to Caramba / project area (exact lat/lon/zoom set in build step)
3. **ercot_queue — fuel-type color split.** Currently single-color. Split by technology code: gas (GT/CC/IC/ST → gas color), solar (PV → solar color), wind (WT → wind color), battery (BA → battery color), other (OT → neutral). Colors consistent with other layers' conventions for the same fuels.
4. **Hide `parcels_pecos` layer.** Default-off and remove from sidebar, or gate behind a hidden flag. Data file stays in repo for future re-enable.

Deliverables: PR with UI changes. No data-pipeline changes.

---

### Stage: SIDEBAR COLLAPSE

**Branch:** `refinement-sidebar-collapse`
**Depends on:** nothing (live-UI layer only)
**Blocks:** nothing

Tasks:

1. **Toggle control.** Add a toggle button anchored to the sidebar's right edge (top-right corner of sidebar). Renders `«` when sidebar is expanded, `»` when collapsed. Accessible target size on mobile (minimum 44×44 px hit area).
2. **Collapse behavior.** On toggle, sidebar slides out of view (negative `transform: translateX` or `width: 0` via CSS transition, ~200ms). Map container expands to full viewport width. MapLibre `map.resize()` fires on transition end so tiles reflow.
3. **Expand behavior.** Reverse of collapse. Map resizes back. Sidebar contents retain prior scroll position and filter state.
4. **Mobile parity.** Same control, same chevron convention. On mobile the sidebar overlays the map (rather than sitting adjacent), so collapse returns full-screen map.
5. **State persistence.** Sidebar open/collapsed state serialized into URL hash alongside existing viewport state. Reloading or sharing the URL preserves the collapsed view.

Deliverables: PR with `build_template.html` CSS + JS changes only. No `layers.yaml`, no data-pipeline, no build.py changes.

---

### Stage: ABATEMENT DISCOVERY (parallel-safe after FILTER UI)

**Spec:** `docs/refinement-abatement-spec.md` — authoritative. Regulatory corrections (Ch. 313 expired, JETI excludes renewables, Ch. 312+381 are active mechanisms), keyword taxonomy, regex, field catalog, schema options, county adapter status, live hits, BUILD-gate open questions. Task list below is historical scope only.

**Branch:** `refinement-abatement-discovery`
**Depends on:** FILTER UI merged
**Blocks:** ABATEMENT BUILD

Tasks:

1. Pull **Chapter 312 Central Registry** (Texas Comptroller) — active county/city tax abatements.
2. Pull **legacy Chapter 313 database** — grandfathered school district agreements.
3. Ignore **JETI (Chapter 403)** — renewables are explicitly excluded from JETI.
4. **Scope filter: 23-county West Texas set** — Andrews, Brewster, Crane, Crockett, Culberson, Ector, Glasscock, Hudspeth, Irion, Jeff Davis, Loving, Martin, Midland, Pecos, Presidio, Reagan, Reeves, Schleicher, Sutton, Terrell, Upton, Ward, Winkler.
5. **Time filter:** filings 2020 through present.
6. **Status filter:** unexpired only.
   - Expired = explicit termination date in past, OR start date + term length computes to past date
   - Empty/missing expiration fields → treat as active
7. Catalog all available data fields from source.
8. Propose layer schema + popup spec.
9. Produce discovery doc for operator approval — no code changes.

Deliverables: Markdown doc in PR with field catalog, schema proposal, example records, and open questions. Approval gate before ABATEMENT BUILD.

---

### Stage: ABATEMENT BUILD

**Approved scope:** `docs/refinement-abatement-spec.md` §12 (locked 2026-04-23).

**Branch:** `refinement-abatement-build`
**Depends on:** ABATEMENT DISCOVERY approved AND SIZING + WATERMARK merged

Tasks:

1. Build renewable abatement layer per approved schema.
2. Default view: last 2 years of filings.
3. Toggle control: change time range (user-selectable).
4. Popup shows all catalogued fields.
5. Layer participates in generic filter UI from FILTER UI stage.
6. Size/color consistent with VISUAL OVERHAUL + SIZING + WATERMARK conventions.

Deliverables: PR with new layer, data file, and filter integration.

---

### Stage: DC RESEARCH (parallel-safe after FILTER UI)

**Branch:** `refinement-dc-research`
**Depends on:** FILTER UI merged
**Blocks:** DC BUILD

Tasks:

1. Research announced, planned, rumored, and reported data center projects across all 23 West Texas counties.
2. Known anchors: **Longfellow/Poolside AI** (Pecos County), **Stargate** (Abilene area), **Project Matador/Fermi**.
3. Per project, capture:
   - Project name
   - Location (county, coordinates if available)
   - Total power (MW)
   - Announcement date
   - Expected completion date
   - Owner / operator / developer
   - Tenant(s) if announced
   - Source(s) + confidence level (announced vs. rumored)
4. Produce structured data file (JSON or GeoJSON) for handoff to DC BUILD.

Deliverables: Research doc + structured data file. No layer build.

---

### Stage: DC BUILD

**Branch:** `refinement-dc-build`
**Depends on:** DC RESEARCH data file AND SIZING + WATERMARK merged

Tasks:

1. Build data center layer from DC RESEARCH data file.
2. Scale icon size by total MW.
3. Visual treatment consistent with VISUAL OVERHAUL + SIZING + WATERMARK conventions.
4. Popup shows all fields.
5. Layer participates in generic filter UI.
6. Include `confidence_level` as a filterable field.

Deliverables: PR with new layer + data file.

---

### Stage: DC AUTO-REFRESH

**Branch:** `refinement-dc-automation`
**Depends on:** DC BUILD merged

Tasks:

1. Build GitHub Actions workflow at `.github/workflows/dc-refresh.yml`:
   - Runs weekly on schedule
   - Monitors news sources for West Texas data center announcements
   - Parses into structured records matching DC RESEARCH schema
   - Commits data file updates automatically
2. Use LLM-in-the-loop for news parsing (Anthropic API, API key as GitHub secret).
3. Include dry-run mode for testing.
4. Log changes per run; open PR instead of direct commit if the workflow detects material changes.

Deliverables: PR with workflow file, scraper/parser scripts, documentation on setup (secrets, manual trigger, failure handling).

---

### Stage: TCEQ REFRESH (parallel-safe after FILTER UI)

**Branch:** `refinement-tceq-refresh`
**Depends on:** FILTER UI merged
**Blocks:** TCEQ MERGE

Tasks:

1. Refresh TCEQ data from source (CRPUB scrape + Census geocoder per manual-CSV pattern; fossil/emissions scope only per `docs/settled.md`).
2. Update data file in `outputs/refresh/`; do not change layer styling yet.
3. Document source URL, refresh date, record count delta.

Deliverables: PR with updated data file + changelog.

---

### Stage: TCEQ MERGE

**Branch:** `refinement-tceq-merge`
**Depends on:** TCEQ REFRESH merged

Tasks:

1. Merge TCEQ layers (`tceq_nsr`, `tceq_pbr`, `tceq_gas_turbines`) into `combined_points.csv` (drop-and-append by `layer_id`).
2. Add 3 layers to `layers.yaml` under new "Permits" sidebar group.
3. Color family distinct from water.
4. Each layer declares `filterable_fields`: `date_filed` (date), `permit_type` (category), `status` (category), `company` (text).

Deliverables: PR with merged layer config and data.

---

## Opening message template

For each stage, operator sends one message to open the chat. Natural language is fine; no required structure. Example invocations:

- `start filter ui stage`
- `start bug sweep`
- `run visual overhaul`
- `begin abatement discovery`
- `do the dc research stage`
- `kick off tceq refresh`

Claude's protocol (silent, per `Readme.md` §5 and §6):

1. Classify prompt → shipping task (stage name matches a spec above)
2. Clone repo → read `Readme.md` + `WIP_OPEN.md` → find stage spec in `docs/refinement-sequence.md`
3. Create stage branch
4. Execute tasks end-to-end
5. Open PR with handoff content in description
6. Update `WIP_OPEN.md` + append entry to `WIP_LOG.md` as final action
7. Final response reports PR URL

If a stage's dependencies aren't merged yet, Claude flags and stops — per `Readme.md` §2 acceptable-asks list rule 5 (factual input only operator has).

---

## Close-out

Refinement sequence complete when all stages are merged to main and deployed to prod. Sequence doc can be archived at that point (move to `docs/archive/refinement-sequence-closed.md`), or retained as reference for future refinement cycles.
