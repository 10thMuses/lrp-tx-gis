# Caramba North OM — rebuild notes and delta vs. the July 2026 v4

Rebuilt 2026-08-19 from `scripts/build_caramba_om.py` + `scripts/caramba_om_data.py`.
Baseline: `Caramba_North_OM_PostNDA_Jul2026_v4.pdf` (built 2026-07-06, HeadlessChrome print).

The July v4 was never committed — no generator, no output, nothing in git history. This
rebuild reconstructs it from the repo's canonical layer data and commits the pipeline so the
next version is `python3 scripts/build_caramba_om.py`.

---

## 1. What is now derived rather than typed

Every figure in Sections 3, 4, 7 and 9 recomputes at build time from `combined_points.csv`,
`combined_geoms.geojson`, `data/wells_permian6.csv`, `data/well_prod_status.csv`,
`data/fracfocus/DisclosureList_1.csv`, and `data/datacenters/dc_anchors.json`.

The only hand-entered values are declared in `CONFIG` at the top of
`scripts/caramba_om_data.py` and are all counterparty-supplied indicative terms, labelled as
such in the document: acreage, the 47,418 AF/yr water permit, the Solstice and Waha
distances, and the Section 6 gas quote.

Methodology is inherited unchanged from the locked May-2026 study:

| Rule | Definition | Source |
|---|---|---|
| Genuine new drill | `completion_year` blank OR `completion_year >= spud_year` | RULE H, `outputs/reports/pecos_lock.py` |
| Shallow | `total_depth < 3000` ft | study |
| Marginal / end-of-life | lease trailing avg ≤ 125 Mcf/d gas AND ≤ 25 bbl/d oil | study |
| New-drill frack | FracFocus job year within −1…+2 yrs of wellbore spud **or** completion year | `outputs/reports/fracfocus_new_drill_only.py` |

Reproducing v4's numbers on the July data confirmed all four rules before any refresh was
applied.

---

## 2. Deltas caused by the data refresh

`data/wells_permian6.csv` re-fetched from RRC dbf900: **99,224 → 99,808 rows**.

| Figure | July v4 | 2026-08-19 | Cause |
|---|---|---|---|
| Pecos wellbore events since 2020 | 1,118 | 1,140 | new RRC rows |
| — genuine new drilling | 117 (10%) | 115 (10%) | reclassification, below |
| — rework / workover | 1,001 (90%) | 1,025 (90%) | new RRC rows |
| New-drill wells ≤ 2 mi | 0 | 0 | — |
| New-drill wells ≤ 5 mi | 0 | 0 | — |
| **New-drill wells ≤ 10 mi** | **3 (nearest 6.9 mi)** | **1 (nearest 9.37 mi)** | **see §3** |
| New-drill wells > 10 mi | 113 | 114 | new RRC rows |
| Non-plugged wellbores ≤ 10 mi | 291 | 298 | new RRC rows |
| Marginal / EOL ≤ 10 mi | 241 (83%) | 247 (83%) | share unchanged |
| Peer-county average new drill | ≈ 1,148 | 1,181 | Reagan 629→668, Reeves 1,044→1,053, Midland 1,487→1,569, Martin 1,685; Howard/Loving unchanged (static file) |
| FracFocus Pecos disclosures | 949 | 950 | one new filing |
| New-drill fracks 0–2 / 2–5 / 5–10 / 10–20 mi | 0 / 9 / 19 / 450 | 0 / 9 / 19 / 452 | new filings |
| New-drill fracks ≤ 20 mi | 478 | 480 | new filings |

Every Section 9 headline claim survives the refresh. The wellbore, production and fracturing
records still agree.

---

## 3. The one reclassification worth knowing about

v4 counted **3** new-drill wells within ten miles, nearest 6.94 mi — the two 2025 Mongoose
Energy "Viper" wells plus one 2020 well at 9.37 mi.

Since July the RRC has re-stamped the two Mongoose wells with **spud_year 2026 against
completion_year 2025**. RULE H excludes any wellbore whose completion precedes its spud,
because that pattern is the signature of a recompletion re-stamp on an old wellbore. Applied
literally, it now excludes two wells that are genuinely new.

The rule was not changed — changing a locked classification to preserve a headline is the
wrong move. Instead the document carries a **Classification note** in §9.4 disclosing all
three boundary cases (6.94 mi, 6.95 mi, 9.23 mi) with their spud and completion years, so a
reader comparing against the July vintage sees why the count moved.

**Open decision for the operator:** whether to amend RULE H to treat
`spud_year − completion_year <= 1` as a paperwork boundary rather than a re-stamp. That would
restore the count to 4 within ten miles (the three above plus the 2020 well) and is arguably
more faithful to the rule's intent — but it is a change to a locked definition that also feeds
the map filter, so it is not made here.

---

## 4. Deltas caused by a change of basis (not by new data)

**Section 4 named-project tables.** v4's footnote 7 sourced the named tables to the ERCOT
*April 2026 status report*, a file that is not in the repo. Its project grouping differs from
the `ercot_queue` layer: v4 showed 10 Pecos solar projects where the layer holds 16 rows, at
identical megawatts. The rebuild derives the named tables from the repo layer so the whole
section reconciles to one source. Capacity totals are unchanged to the megawatt:

| | July v4 | Rebuild |
|---|---|---|
| Pecos queue | 12.0 GW / 39 projects | 12,039 MW / 39 projects |
| Adjacent-county queue | 24.6 GW | 24,585 MW |
| Pecos operating solar | 13 plants · 2.2 GW | 13 plants · 2,178 MW |
| Pecos operating BESS | 6 · 500 MW | 6 · 505 MW |

**Pecos operating total: 3.4 GW → 3.2 GW.** v4 rolled operating wind up from the USWTDB
turbine layer (8 projects, 653 MW); the rebuild uses the EIA-860 plant record (5 plants,
542 MW) so that every operating-fleet figure sits on one basis. Both are defensible; the
EIA-860 basis is the one the rest of the table already used.

---

## 5. Two corrections to the July document

**a. "12,039 MW in the ERCOT queue within 20 miles."** This appears in the v4 executive
summary and in §4. The figure is correct but the geography is not: 12,039 MW / 39 projects is
the **Pecos County** queue. The true within-20-miles figure is **13 projects / 3,973 MW**. The
rebuild states the county figure and labels it as such.

**b. "More than 25 GW of announced data-center capacity in the immediate catchment."** The
rebuild reports **9.7 GW within 60 miles**, and lists Texas projects beyond that radius
separately and explicitly excluded from the headline. Two reasons for the gap, one of which is
a real data problem — see §6.

---

## 6. Known gaps — operator action needed

**a. `data/datacenters/dc_anchors.json` is stale and thin for the regional catchment.** It
holds 8 entries and only 2 within 60 miles (GW Ranch, Project Horizon); it was last compiled
2026-04-25. v4's §7 table listed four more regional projects that the register does not
carry: Chevron / Engine No. 1 West Texas Power Plant, the TPL + Bolt JV, LandBridge's Alpha
Digital Campus, and the Longfellow solar/wind/BESS cluster. They also appear as labels on
Exhibit 7.1 but have no record behind them. They were not added here — sourcing coordinates
and capacities by hand violates the no-hand-coded-features rule. Refreshing the register is
the single highest-value fix before this document goes to a buyer, because it is what moves
the headline from 9.7 GW back toward 25 GW.

**b. The ERCOT queue layer has not been refreshed since the March 2026 snapshot.** There is no
fetch script for it — `refresh_*.py` exists for EIA-860, USWTDB, TCEQ, FCC, and DC anchors,
but not for the ERCOT GIS Report. Section 4 is therefore five months stale. Every figure in it
is internally consistent and matches v4 exactly, which is itself the tell.

**c. Map exhibits are the July captures, not fresh ones.** `scripts/capture_om_exhibits.py`
is written, committed, and drives the live platform through the access gate with per-exhibit
viewport, layer set, and coordinate-anchored annotations — but Chromium has no network egress
from this sandbox (the proxy accepts curl and refuses the browser's TLS), so it could not run
here. The four exhibits were extracted from the v4 PDF at their original 3,200 px and carry
their real capture date, 2026-07-06, both in-image and in Appendix A.1. Running
`python3 scripts/capture_om_exhibits.py` on any machine with ordinary network access will
regenerate them at current layer state and write a `manifest.json` that the builder picks up
automatically.

---

## 7. Rebuild

```bash
python3 scripts/caramba_om_data.py --json /tmp/om_model.json   # inspect the derived model
python3 scripts/capture_om_exhibits.py                          # needs network; optional
python3 scripts/build_caramba_om.py                             # -> outputs/reports/*.pdf
python3 scripts/build_caramba_om.py --no-flags                  # suppress disclosure boxes
```

Output is 25 pages, matching v4's extent, with mixed portrait/landscape pages via CSS named
pages.
