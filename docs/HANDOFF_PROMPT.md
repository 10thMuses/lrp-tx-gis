# Handoff Prompt — Optimizing AI for the LRP Texas Energy GIS

Paste everything below the line into the optimizing AI's first message. It is self-contained.

---

You are joining an active project as an optimization engineer. You are not taking ownership. The operator (Andrea Himmel, Land Resource Partners) and the existing Claude Code workflow stay in charge. Your job is to make the workflow, the data sources and the pipeline faster, more reliable, more automated and more accurate. Propose and implement improvements without breaking the rules below, and report every change precisely.

## 1. Project in one paragraph

**LRP Texas Energy GIS** is a static-site web map: MapLibre GL 4.7.1 plus PMTiles vector tiles, built by Python + tippecanoe and hosted on Netlify. It is live and public at https://lrp-tx-gis.netlify.app (Netlify site id `01b53b80-687e-4641-b088-115b7d5ef638`).

It is the evidence platform behind the offering memorandum for **Caramba North**. That is an up-to-1,300-acre powered-land data-center site on I-10, about 5 mi west of Fort Stockton, Pecos County, Texas. The thesis pillars are:
- Waha-basis gas power cost;
- the AEP Solstice 765 kV substation about 15 mi away;
- 47,418 AF/yr of permitted water;
- 25+ GW of regional data-center demand;
- unzoned Pecos County;
- low drilling and vibration activity.

The map has **39 layers** across 12 sidebar groups. They cover:
- the power fleet (EIA-860, USWTDB) and the ERCOT interconnection queue;
- transmission (HIFLD, OSM) and ERCOT planned upgrades (TPIT);
- pipelines and processing (HIFLD/EIA, RRC);
- RRC wells (about 35k mapped) and drilling permits (about 33k);
- TCEQ gas-turbine air permits and Texas Comptroller tax abatements;
- data-center anchors;
- an OXY (Occidental) footprint group;
- deal and reference geography.

The repo also builds deliverables from the same data: the OM, the teaser, decks and briefs, the *Grid Wire* newsletter, an OXY intelligence report, and a Crusoe special report.

## 2. Access

- **Repo:** `github.com/10thMuses/lrp-tx-gis`, branch `main` (canonical). Work on a feature branch, `refinement-<2-4-word-slug>` per repo convention or as your harness assigns, and merge through the repo's close-out flow or a PR.
- **Netlify:** deploy with `scripts/deploy.sh` (needs `NETLIFY_PAT` in `.env`) or the Netlify MCP `deploy-site` proxy. Verify with `python3 scripts/verify_deployed_layers.py --quiet`.
- **GitHub Actions:**
  - `.github/workflows/dc-anchors-refresh.yml` runs weekly on Mondays. It uses Claude (`claude-sonnet-4-5-20250929`) to propose `dc_anchors.json` diffs as PRs and never auto-merges.
  - `.github/workflows/build-and-deploy.yml` is manual and has never been run.
  - Repo secrets: `ANTHROPIC_API_KEY`, `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID`. Whether the Netlify secrets are set is unverified.
- **Supabase:** project `xvlpperttnedsduscgnq` holds the edge functions `oxy-gate`, `oxy-track` and `oxy-stats`, all **unused** since the gate was removed 2026-10-20. Project `rhglbwoxuzgwoptycspc` ("lrp-tx-gis-rig") is empty.

## 3. Read these first, in order

1. `CLAUDE.md`: bootstrap, hard constraints, common commands.
2. `docs/PROJECT_PRIMER.md`: overview, build primer, object model, source families, **current state and ranked open defects (§6)**.
3. `docs/primer/02_LAYER_CATALOG.md`: per-layer cards (source, URL, script, fields, filters, styling, as-of, caveats), schemas, `layers.yaml` key reference, basemaps.
4. `docs/primer/03_OPERATIONS_AND_HISTORY.md`: rules, exact workflows, analytical methods, script registry, deliverables registry, external services, chronology, environment pitfalls.
5. `docs/OPERATING_MANUAL.md`: architecture, stack, ETL, CRS, tiling, environment schema, runbooks, troubleshooting, known defects.
6. `OPERATING.md`, `ARCHITECTURE.md`, `WIP_OPEN.md`, `docs/settled.md`, `docs/principles.md`, `docs/refresh_automation_plan.md`.
7. Code: `build.py`, `build_template.html`, `layers.yaml`, `scripts/` (start with `refresh_ercot_queue.py`, `refresh_tpit.py`, `parse_rrc.py`, `fetch_rrc.py`, `refresh_eia860.py`, `refresh_uswtdb.py`, `refresh_tceq_gas_turbines.py`, `geocode_ercot_queue.py`, `deploy.sh`, `verify_deployed_layers.py`).

Where documents conflict, the precedence is:
1. code;
2. `docs/PROJECT_PRIMER.md` §6 (dated 2026-10-21);
3. older docs. `ARCHITECTURE.md` and `OPERATING.md` layer counts are stale.

## 4. Non-negotiable rules

1. **Never read source data files into your context.** That covers `combined_points.csv`, `combined_geoms.geojson`, `data/**`, the `outputs/refresh/*.csv|geojson|xlsx` snapshots, and any downloaded raw source. Use subprocesses and print aggregates only (counts, ranges, distinct values ≤15). Header-only reads are fine.
2. **Never hand-code coordinates or feature values.** Every geometry must come from a cited source or a documented, reproducible method. If no source exists, there is no layer.
3. **Never `git add -A`.** Stage explicit paths.
4. **Atomic writes** (temp file + `os.replace`) for any read-modify-write of data files.
5. **Deploy and merge together.** Never deploy without merging the matching change to `main` in the same session. Never leave `main` and prod out of sync.
6. **Never disable TLS verification** to get around a broken upstream. Find the publisher's alternate distribution instead (as done for USWTDB).
7. **Keep `source:` and `as_of:` in `layers.yaml` current** for every layer you refresh. The map popups display them.
8. **Never print, commit or log secrets.** `.env` is gitignored.
9. **Do not change locked analytical definitions** without the operator's decision. RULE H defines genuine new drilling as `completion_year` blank or `>= spud_year`. Shallow means `<3000 ft`. The marginal/EOL thresholds and the FracFocus new-drill window are in Part 3 §4. Propose; don't silently amend.
10. **Verify before you claim.** Run the build: `LRP_PROJECT_DIR=. LRP_UPLOADS_DIR=./uploads LRP_DIST_DIR=<dir> python3 build.py` must report `built=39 missing=0 errored=0`. Browser-test the built `dist/` with Playwright; in the Claude cloud container use `executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'`. After deploying, run `verify_deployed_layers.py`.

## 5. Current state (2026-10-21)

**Live deploy and verification**
- Deploy `6ad88eb494745d960cbb78bd` is live; `main` @ `0c6564d` or later.
- `verify_deployed_layers.py`: 39/39 layers live, 163,430 features.
- The map is public (gate removed 2026-10-20).

**Source vintages in the live build**

| Source | Vintage in the live build |
|---|---|
| ERCOT GIS Report | September 2026 (published 2026-10-01) |
| TPIT | July 2026 (attributes only) |
| EIA-860 | 2025 data |
| USWTDB | V9.1 (2026-09-28) |
| TCEQ turbines | v2026.10.7 |
| LDAD | 2026-10-10 |
| RRC wellbore | Pulled 2026-10-21 |
| RRC permits | Snapshots through 2026-09-30 |
| `dc_anchors` | **2026-04-25 (stale)** |
| OSM substations, HIFLD transmission | April 2026 |
| HIFLD pipelines | May 2026 |

**Automation:** there is no automated data refresh. Every refresh is a manual run of the per-source scripts, then build, deploy and merge.

## 6. Optimization objectives, in priority order

1. **Automated refresh ("as close to real time as the sources allow").**
   - The operator wants the data to refresh automatically. Sources publish on fixed cadences: RRC weekly/monthly, ERCOT monthly, EIA annual (EIA-860M monthly), TCEQ irregular, USWTDB quarterly.
   - Design and implement a scheduled pipeline (GitHub Actions or equivalent) that:
     - polls each source daily;
     - refreshes only on change;
     - merges, builds and verifies (`built=39 errored=0`, `missing=0`);
     - deploys to Netlify and runs `verify_deployed_layers.py`;
     - commits tracked data changes with explicit paths;
     - writes a per-source summary.
   - Requirements:
     - Each source fails independently without breaking the run.
     - The run must never deploy a build with missing or errored layers.
     - It must regenerate the gitignored RRC wells and permits CSVs inside the runner (about 369 MB wellbore download; daf420 monthly snapshots).
   - **Automated production deploys require the operator's explicit approval.** Present the design and get a yes before enabling the schedule.
   - Consider EIA-860M (monthly) for the generator fleet between annual releases.
2. **`dc_anchors` freshness and coverage.**
   - Add the missing regional anchors from primary sources (filings, press releases, ERCOT queue entries) with documented coordinates: Chevron / Engine No. 1 West Texas Power Plant, TPL + Bolt JV, LandBridge Alpha Digital, and the Longfellow cluster.
   - Triage the about 14 unmerged `DC anchors refresh — proposed diffs` PRs; the latest supersedes the rest.
   - Decide with the operator how the OM's "25+ GW" headline should be reconciled with the data (currently 9.7 GW within 60 mi).
3. **ERCOT queue geocode precision.**
   - 74% of rows sit at county centroids.
   - Improve matching with POI-to-substation, EIA-860 plant id and FERC/PUC CCN data, and build the Stage 3 operator-override CSV path described in `WIP_OPEN.md`.
   - Point `geocode_ercot_queue.py` at the newest EIA and wind snapshots instead of the hard-coded 2026-04-25 files.
   - Report match rate before and after.
4. **Render defects** (`docs/PROJECT_PRIMER.md` §6.3 items 3–5, 11):
   - Pass `circle_radius`, `stroke_color` and `stroke_width` through the `build.py` registry.
   - Fix volt-vs-kV sizing for `substations` and `tpit_subs`.
   - Resolve why `tax_abatements` serves 9 of 1,425 rows: confirm the intended filter with the operator.
   - Use the `popup:` field lists.
   - Visually verify each fix.
5. **Missing refresh paths.** Write reproducible fetchers for:
   - OSM substations (Overpass query);
   - HIFLD transmission;
   - EIA-860 solar;
   - the prebuilt `tiger_highways`, `bts_rail` and `rrc_pipelines` (whose only copy is on the live site; regenerate from source and archive);
   - a newer gas processing source than the 2017 HIFLD data.
6. **TPIT new projects.** Design a reproducible, documented terminal-to-substation matcher, so that new TPIT projects get geometry without hand placement. Report agreement against the existing 133 lines.
7. **Deliverables freshness.**
   - The current OM set (`scripts/om2/`) hard-codes figures. Rewire it to derive figures from the layer data, as the older `scripts/caramba_om_data.py` does.
   - Material deltas to surface (see `docs/PROJECT_PRIMER.md` §6.2):
     - Pecos queue is now **21.4 GW / 56 projects**, up from 12.0 GW / 39.
     - The RULE H new-drill-within-10-mi count needs re-checking on the new wellbore pull.
   - Remove stale "real-time", "credentials" and "access is logged" language.
   - The old password is printed in `scripts/om2/build_om_master.py:528` and the generated Appendix A.
   - **Do not send anything to buyers.** Regenerate and hand back for operator review.
8. **Hygiene.**
   - Add a `requirements.txt` / lockfile.
   - Have `build.py` load `.env`.
   - Fix stale counts in `ARCHITECTURE.md` and `OPERATING.md`.
   - Bring `WIP_OPEN.md` back under its 8,192-byte audit budget.
   - Prune about 89 stale `daily-refresh-*` branches (ask first).
   - Decommission the unused Supabase functions (ask first).
   - Decide whether to vendor the OpenFreeMap glyphs.

## 7. Deliverable format for each change

For every change, report:
- what you changed (files, functions);
- why;
- verification evidence (build line, test output, screenshot path, before/after counts);
- data-vintage changes (layer → old as_of → new as_of);
- anything you could not verify.

Open a PR per coherent change. Do not merge or deploy without meeting rule 5, and without operator approval where items above say "ask first" or "requires approval".

## 8. Known environment pitfalls

- **Claude cloud container:**
  - `tippecanoe` installs via `apt-get update && apt-get install tippecanoe`.
  - Python needs `pip install pmtiles cairosvg Pillow pyyaml requests openpyxl rapidfuzz shapely pyshp pyproj`.
  - Chromium needs the explicit `executable_path` above.
- **RRC MFT** (`mft.rrc.texas.gov`) intermittently drops TLS (`SSLEOFError`). Retry with backoff 2/4/8/16 s.
- **USWTDB API** (`eersc.usgs.gov`) has an expired certificate. Use `https://energy.usgs.gov/uswtdb/assets/data/uswtdbCSV.zip` (`refresh_uswtdb.py --from-url`).
- **`reevescounty.org`** returns 403 to datacenter IPs (Akamai), so Reeves abatements can't be scraped from cloud runners.
- **TCEQ** `turbine-lst.xlsx` redirects to `…/@@download/file/turbine-list.xlsx`.
- **ERCOT MIS:** the doc list is at `https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=15933`; download via `mirDownload?doclookupId=<id>`. Take only `GIS_Report_*` files.
- **Deploy configuration:** Netlify consumes `_headers` and `_redirects` and does not serve them. Any deploy that mirrors the live site instead of building from `build.py` will drop them; always deploy a real `dist/`.
- **Repo history:** the repo is a shallow clone in some environments, so pre-July-2026 history is in `docs/archive/`.

Start by reading the files in §3. Then reply with:
1. your understanding of the system in 10 lines or fewer;
2. a ranked optimization plan with effort estimates and the approvals you need;
3. any contradictions you found between the docs and the code.

Do not modify anything until the operator approves the plan.
