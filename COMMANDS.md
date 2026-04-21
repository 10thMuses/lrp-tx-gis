# GIS Map — Command Reference

Exact messages to send Claude for every GIS operation. Copy-paste.

---

## 1. EVERYDAY TRIGGERS

### Build only (no deploy)
```
build.
```
Sanity-check before pushing live.

### Build + deploy to preview
```
build. deploy to preview.
```

### Build + deploy to production
```
build. deploy to prod.
```
Publishes to `https://lrp-tx-gis.netlify.app`.

### Re-deploy existing build
```
deploy to prod.
```
No rebuild.

### Password-protect
```
password-protect with <password>.
```

### Remove password
```
remove password.
```

### Resume a handed-off state
```
resume.
```
Reads `WIP_OPEN.md` "Next chat" block and executes.

---

## 2. REFRESH + MERGE EXISTING LAYERS

Post-chat-34 refactor: most layers live inside `combined_points.csv` or `combined_geoms.geojson`. Refresh + merge is a two-trigger sequence.

### Refresh a single layer
```
refresh ercot_queue.
```
Claude fetches, writes `outputs/refresh/points_ercot_queue.csv`.

### Merge refreshed file into combined
```
merge ercot_queue from outputs/refresh/points_ercot_queue.csv.
```
Claude runs `python3 build.py merge ercot_queue outputs/refresh/points_ercot_queue.csv`, which swaps ercot_queue rows inside `combined_points.csv`, writes updated combined file to `outputs/`.

### Refresh + merge + deploy (one-shot, when feasible within budget)
```
refresh ercot_queue. merge. build. deploy to prod.
```
Fits only if refresh is quick (≤4 calls). Otherwise split.

### Common cadences

**Monthly:**
```
refresh ercot_queue. merge. build. deploy to prod.
```

**Quarterly:**
```
refresh wells, substations.
```
(Then separate merge + build chats.)

**Annual:**
```
refresh eia860_plants, eia860_battery, wind, solar, transmission, pipelines.
```

---

## 3. ADDING PENDING LAYERS

### Batch 3b — Pecos parcels (standalone)

Already refreshed. To add + deploy:
```
add layer parcels_pecos from outputs/refresh with min_zoom 11. build. deploy to prod.
```

### Batch 4 — TCEQ permits

**Chat A:**
```
refresh tceq_permits. Scrape TCEQ CRPUB for active air/water permits in Pecos, Reeves, Ward, Winkler, Ector counties. Geocode via Census Geocoder batch endpoint. Skip non-geocodable (log). Canonical schema + permit_no, program, issue_date, facility, county. Return row count + geocode hit rate.
```

**Chat B:**
```
merge points_tceq_permits.csv.
add layer tceq_permits from outputs/refresh. build. deploy to prod.
```

### Batch 5 — Data center sites

**Manual first:** compile `dc_sites_source.csv` with `name, address_or_county, capacity_mw, developer, status, source_url, announce_date`. Upload to project.

**Chat A:**
```
refresh dc_sites. Read /mnt/project/dc_sites_source.csv, geocode address-only via Census Geocoder, county-only falls to centroid (flag APPROXIMATE). Write points_dc_sites.csv.
```

**Chat B:**
```
merge points_dc_sites.csv.
add layer dc_sites from outputs/refresh. build. deploy to prod.
```

---

## 4. UX / STYLING TWEAKS

All through `layers.yaml` edits. One chat.

### Change a layer's color
```
change caramba_north color to #7c2d12. build. deploy to prod.
```

### Change default-on
```
make caramba_north, caramba_south, mpgcd_zone1 default on. all others default off. build. deploy to prod.
```

### Change min_zoom
```
set wind min_zoom to 8. build. deploy to prod.
```

### Change popup fields
```
for ercot_queue popup, show name, fuel, technology, mw, county, entity, funnel_stage, commissioned. build. deploy to prod.
```

### Change point size
```
make eia860_battery radius 6. build. deploy to prod.
```

### Rename sidebar label
```
rename ercot_queue label to "ERCOT GIR queue (Apr 2026)". build. deploy to prod.
```

### Change sidebar group
```
move tpit_subs and tpit_lines to a new group called Transmission Planning. build. deploy to prod.
```

### Add a feature filter UI
```
add a filter dropdown on ercot_queue sidebar entry to filter by fuel. options from the data. build. deploy to prod.
```

---

## 5. DIAGNOSTICS / TROUBLESHOOTING

### Something renders wrong
```
the transmission layer is missing features south of I-10. diagnose.
```

### See current layers.yaml
```
show me layers.yaml.
```

### See last build report
```
show me the last build report.
```

### Force a clean rebuild
```
clean rebuild. deploy to prod.
```

### Live site looks stale
Hard refresh browser. If still stale after 1 hour:
```
bump cache-busting on tiles. build. deploy to prod.
```

---

## 6. GRID WIRE STATIC EXPORT

### Screenshot of specific view
```
capture a screenshot of the map centered on Pecos County (lon -103.0 lat 30.9, zoom 9) with layers caramba_north, caramba_south, mpgcd_zone1, wells, ercot_queue on. 1600x1000 png.
```

---

## 7. ACCESS CONTROL

### Current: link-only, no password.

### Password-protect
```
password-protect with <password>.
```

### Counterparty-specific branch preview
```
create a branch preview called <name> with only these layers visible: caramba_north, caramba_south, mpgcd_zone1, ercot_queue, transmission. build. deploy to that branch.
```

---

## 8. SAFETY RAILS

Per `GIS_SPEC.md §1`, Claude will refuse without asking:
- Fabricate coordinates, rows, or geometry when sources don't exist
- Re-digitize from PDFs when a vector source exists
- Deploy to prod if build report shows `errored > 0`
- Delete project files

Everything else executes without asking.

---

## 9. SESSION PROTOCOL

### Budget declaration

Every code-shipping chat's second silent step (after pre-flight `ls /mnt/project/`) is budget declaration. Ceilings in `GIS_SPEC.md §12`. Circuit breakers enforce abort before over-run.

### Interstitial cadence

Feature chats N alternate with hardening chats N.5. Every chat's close-out declares N.5 scope (or null declaration). See `GIS_SPEC.md §14`.

### Handoff quality gate

Every handoff to `WIP_OPEN.md` "Next chat" passes three rules: facts pre-resolved, verification tier matches blast radius, budget realism with line items. See `GIS_SPEC.md §15`.

### Self-correction

If operator catches a protocol violation, the correction becomes a rules-doc amendment in the same chat. Banned phrases → `PROJECT_INSTRUCTIONS.md` and `GIS_SPEC.md §13`. New high-risk categories → §15 Rule 2. Red-flag handoff phrases → §15 Rule 1. Committed in the same close-out, not deferred.

---

## 10. WHAT CLAUDE DOES WITHOUT ASKING

Reference list. If Claude asks about any of these, flag it — protocol violation.

**Data & layers:**
- Choose tippecanoe flags for a new layer (based on feature density)
- Choose color from the palette within the right group
- Choose `default_on: false` for new layers by default
- Choose `min_zoom` based on feature density (>5k features = min_zoom 7+)
- Choose popup fields from available columns (up to 6 most informative)
- Add a §9 fragility entry when a source misbehaves
- Skip a broken source, log, continue with other layers

**Build & deploy:**
- Install tippecanoe if missing
- Vendor `pmtiles.js` into `dist/` on every build
- Write `_headers` and `_redirects`
- Run Netlify MCP deploy + proxy bash + verification curl as one chain
- Present `dist/index.html` + URL at close-out

**Docs & protocol:**
- Append to `SESSION_LOG.md` at close-out
- Update `WIP_OPEN.md` "Recent sessions"
- Declare N.5 scope (or null declaration)
- Commit protocol amendments when a correction lands
- Increment chat number in memory

**Refresh & merge:**
- Retry AGOL fetches per §9
- Skip and log on 5-retry failure
- Route numeric fields through `fnum()`
- Simplify line/polygon per layer's canonical tolerance
- Round coordinates to 4 decimals

**Judgment calls Claude states at close-out but does not ask upfront:**
- Which of two tippecanoe flag sets produces better tile compression
- Whether a layer warrants standalone vs. combined storage (size > 5 MB → standalone)
- Whether a new source failure warrants §9 entry (always yes if failure consumed a retry)
- Whether a correction from operator warrants rules-doc amendment (default yes)

---

## QUICK-REFERENCE CARD

| I want to... | Send Claude |
|---|---|
| Monthly ERCOT pull + deploy | `refresh ercot_queue. merge. build. deploy to prod.` |
| Push a styling tweak | describe + `build. deploy to prod.` |
| Add a pending batch | `refresh <layer>.` then next chat `merge. add layer. build. deploy.` |
| Lock down the site | `password-protect with <pw>.` |
| Resume a handed-off state | `resume.` |
| Recover from a bad state | `clean rebuild. deploy to prod.` |
