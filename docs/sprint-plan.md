# Sprint plan

Active multi-chat plan. Referenced from `WIP_OPEN.md` §Next chat + §Sprint queue.

Covers Chat 87–91. When the last chat in this file ships, delete the file
and start a new one. Chats beyond 91 (Permian-core abatement, power-plant
refresh, DC sub-sequence, etc.) remain in `WIP_OPEN.md` §Sprint queue as
short pointers until they enter the active 5-chat window.

---

## Maintenance discipline (per `Readme.md` §10)

Each shipping chat's close-out re-reads the downstream chat briefs below.
If the just-completed work changed a downstream chat's assumptions — file
layout, dep versions, layer count baseline, discovered regression, new
backlog item, schema change, deprecated source — edit the affected brief
before committing close-out. A close-out that pushes a stale brief forward
is the same silent-regression class as Chat 85's stale-ref merge.

Promotion rule: `WIP_OPEN.md` §Next chat carries the full brief for the
immediately-next chat inline (paste-ready). `§Sprint queue` carries
one-paragraph summaries with pointers into this doc. On close-out, the
executing chat deletes its own section here, promotes the next chat's
full brief into `§Next chat`, and shortens the new §Sprint queue entry
for the chat it just removed.

---

## Chat 88 — ABATEMENT REFACTOR (no new data)

Schema refactor on the existing 9-row `tax_abatements` layer. No new
scrapes this chat. No layer count change.

### Tasks

1. **Label rename.** `layers.yaml` tax_abatements
   `label: "Tax Abatements"` → `"Property Tax Abatements (Ch.312 /
   LDAD, new or expansion)"`. If sidebar truncation is ugly, keep
   concise version and add full text to popup header or tooltip.

2. **Sidebar tooltip / popup header.** Add description: "County-level
   property tax abatements for new or expanded facilities. Chapter
   312 reinvestment zones and Local Development Agreements (HB 5 /
   SB 1340 successors to the sunsetted Ch.313)." Implementation:
   new `description` key in `layers.yaml` per-layer, template
   renders it as popup-header text or sidebar `title` attribute.
   Requires template patch — inspect existing popup builder before
   editing to avoid schema collision.

3. **Drop meeting-date filter.** Remove
   `{field: commissioned, type: text, label: Meeting Date}` from
   tax_abatements `filterable_fields`. Leave `commissioned` column
   populated (for back-compat with existing 9 rows) but not
   user-facing.

4. **Column remapping — new fields.** Additive to Chat 85 mapping;
   columns exist in CSV schema but were unpopulated.

   | CSV column  | Abatement field          |
   |-------------|--------------------------|
   | `mw`        | project MW               |
   | `capacity`  | capex ($M)               |
   | `zone`      | abatement term (yrs)     |
   | `use`       | abatement schedule       |
   | `year`      | announcement year        |
   | `entity`    | developer                |
   | `cap_kw`    | jobs commitment          |
   | `sector`    | taxing entities          |

   Preserved Chat 85 mappings (unchanged): `poi`=agenda_url,
   `funnel_stage`=flags (status derived at build time),
   `operator`=applicant, `project`=reinvestment_zone,
   `technology`=project_type, `commissioned`=meeting_date.

5. **Popup order.** name, operator, entity, county, technology, mw,
   capacity, zone, use, cap_kw, project, sector, status, poi.
   Update `layers.yaml` tax_abatements `popup` list accordingly.

6. **Filter UI.** `filterable_fields`: technology, status only.
   Drop county, commissioned. No other filters.

7. **Back-populate Chat 85's 9 rows** where spec data supports the
   new fields. Matterhorn row (meeting date 2022-07-25): recover
   `year` (announcement year) from the agenda PDF if possible. If
   not recoverable, skip and note in §Abatement layer notes.

### Acceptance

- Layer count: 24 (unchanged).
- tax_abatements label, popup, filter UI reflect new schema.
- 9 existing rows still render, with new fields populated where
  spec data available.
- Build report `errored == 0`; dropped-features <5%.

### Close-out

Deploy → merge branch `refinement-chat88-abatement-refactor` →
delete branch → promote Chat 89 brief to §Next chat → remove Chat
88 section here → push.

---

## Chat 89 — ABATEMENT TRANS-PECOS EXPANSION

County scraping wave. Single-pass; 0-hit counties logged and
flagged, no retry.

### Tasks

1. **Scrape 6 Trans-Pecos counties:** Brewster, Culberson, Hudspeth,
   Jeff Davis, Presidio, Terrell. Reuse Chat 82–84 scraper
   framework (CivicEngage/CivicPlus adapters first, bespoke sites
   second). PDF-only counties drop per spec §12.3 and flag.

2. **Technology filter:** include only `natural_gas`, `gas_peaker`,
   `solar`, `wind`, `battery`, `renewable_other`. Exclude
   `data_center` (deferred to DC sub-sequence), industrial, other
   non-energy. Silver Basin Digital stays under existing
   `technology=abatement_other`.

3. **Schema:** use Chat 88's new column mapping (not Chat 85's).
   Mapping is locked by the time this chat runs.

4. **Merge adapter outputs into `combined_points.csv`** under
   `layer_id=tax_abatements`. Geocode to county centroid only — no
   sub-county precision.

5. **Reeves deferred.** Reeves is Permian-core, adapter regression
   from Chat 82 still open. Handled in Chat 91 §Reeves re-verify,
   not here.

### Acceptance

- Layer count: 24 (unchanged).
- tax_abatements feature count grows from 9 by whatever 6 counties
  yield. Counterfactual estimate: 0–10 hits total (rural,
  low-commercial). Completeness is the criterion, not volume.
- 0-hit counties flagged in `§Abatement layer notes` with
  adapter-type noted (so future chats know whether selector
  regression is likely).

### Close-out

Deploy → merge → delete branch → promote Chat 90 brief to §Next
chat → remove Chat 89 section here → push.

---

## Chat 90 — FCC FIBER COVERAGE

New layer. Ship-priority item from prior chat-86 brief.

### Tasks

1. **Source:** FCC BDC Texas fixed-availability CSV, most recent
   as-of. Download: https://broadbandmap.fcc.gov/data-download/
   nationwide-data (By State → Texas → Fixed Broadband). Backup
   source if UI blocks download: ArcGIS Living Atlas "FCC Broadband
   Data Collection" hosted feature service.

2. **Filter:** `technology_code=50` (FTTP), `low_latency=1`.

3. **Spatial join:** BSL coords to 23-county TIGER polygons already
   in `combined_geoms.geojson`. Drop rows outside the 23-county
   scope.

4. **H3 aggregation.** `pip install h3 --break-system-packages`.
   Resolution 8 (~0.74 km²). If h3-py compile-fails, fallback:
   shapely hexbin at ~1 km pitch. Per hex, compute:
   - `fiber_provider_count`
   - `max_down_mbps`, `max_up_mbps`
   - `providers` (comma-delim, alphabetical, cap 5)
   - `bsl_count`
   - `as_of_date`

5. **Render.** New yaml entry `fcc_fiber_coverage`. Geom=fill.
   3-bin choropleth on `max_down_mbps`: ≥1000 / 100–999 / <100.
   Cyan palette. `default_on: false`. Popup: all six aggregate
   fields.

6. **Friction budget.** CSV is 100+ MB. Use pandas chunked read.
   If h3 install fails, fall back to shapely hexbin same-chat, do
   not reschedule.

### Acceptance

- Layer count: 24 → 25.
- Fiber hex layer renders across 23 counties.
- Popup shows aggregate fields.
- Choropleth bins render visibly distinct.

### Close-out

Deploy → merge → delete branch → promote Chat 91 brief to §Next
chat → remove Chat 90 section here → push.

---

## Chat 91 — BEAD FIBER PLANNED + REEVES ADAPTER RE-VERIFY

Conditional new layer + deferred adapter fix.

### Tasks

1. **BEAD fiber planned layer (conditional).**
   - Primary: TX Comptroller BDO BEAD map / awards list
     (https://comptroller.texas.gov/programs/broadband/).
   - Fallback 1: NTIA Middle Mile award list, Texas subset.
   - Fallback 2: NTIA National Broadband Funding Map.
   - Fields: `subgrantee`, `award_amount`, `county_list` or
     polygon, `announced_date`, `target_completion`, `technology`,
     speed commitment.
   - Render: polygon if available, else county centroid. Cyan
     family, darker shade or dashed stroke than Chat 90's layer.
   - **Ship rule:** if no downloadable source in 30 min, drop the
     layer entirely, log in §Open backlog, proceed to §2 below.

2. **Reeves CivicEngage adapter re-verify.** Chat 82 regression:
   adapter returned 0 hits on first run; Pecos Power Plant LLC
   Reeves abatement was hand-seeded from spec §8. Re-run adapter,
   confirm it reproduces the hand-seeded row. If still 0 hits,
   diagnose selector / URL pattern. If adapter works, run it
   against all Permian-core counties that share the CivicEngage
   CMS (log which).

### Acceptance

- Layer count: 25 → 26 if §1 ships, 25 if dropped.
- Reeves adapter either reproduces Pecos Power Plant row OR
  produces a diagnostic note in `§Open backlog` identifying the
  failure mode.
- `docs/sprint-plan.md` is deleted at close-out (last chat in
  sprint); a new one may be created for the next 5-chat window.

### Close-out

Deploy → merge → delete branch → update `WIP_OPEN.md` §Next chat
to whatever follows (Chat 92 = Permian-core abatement wave, per
current sprint queue) → delete `docs/sprint-plan.md` → push.
