# Shallow (<3,000 ft) Oil-and-Gas Drilling at and Near the Caramba North Tract — Historical and Recent Record

**Prepared:** 2026-05-18 · **Subject site:** Caramba North tract (~1,300 ac), Pecos County, TX — centroid ≈ 30.9032° N, 102.9747° W · **Classification:** Confidential

## Purpose

This memorandum summarizes the historical and recent record of shallow oil-and-gas drilling — wells less than 3,000 ft total depth — at and in the vicinity of the Caramba North tract, drawn from the Railroad Commission of Texas (RRC) wellbore and drilling-permit records. It is provided as factual context for evaluating potential ground-vibration considerations for a data-center development on the site.

## Summary of findings

Shallow (<3,000 ft) drilling at and around the Caramba North tract is a legacy activity that has effectively ceased in the immediate vicinity of the site. There is no shallow well within one mile of the tract; no shallow well has been spudded within two miles since 2002; and the few nearby legacy wells are predominantly plugged and abandoned. Shallow drilling does continue elsewhere in Pecos County, but it is concentrated well away from the site — of the shallow wells spudded county-wide since 2020, roughly 98% are more than fifteen miles from the tract, at a median distance of about sixty miles. Separately, the wells at issue (under 3,000 ft) are, by the depth structure of the Permian/Delaware Basin, conventional vertical wellbores; modern horizontal development targets deep producing benches several thousand feet below, not shallow intervals. About half of all Pecos drilling since 2020 is, by depth, this kind of shallow vertical activity — and that half is concentrated far from the site.

## Findings

### 1. On the Caramba North tract

The shallowest wellbores recorded inside the tract boundary:

| Depth (ft) | Spud year | Status | Oil/Gas |
|---|---|---|---|
| 2,873 | 1960 | Plugged &amp; abandoned | Gas |
| 3,067 | 1991 | Plugged &amp; abandoned | Oil |
| 3,109 | 1957 | Plugged &amp; abandoned | Oil |
| 3,186 | 1987 | Plugged &amp; abandoned | Oil |
| 3,250 | 2008 | Active | Oil |

Only one well on the tract lies below 3,000 ft — a 2,873-ft well spudded in 1960 and long since plugged and abandoned. The only active well on the tract (3,250 ft, spudded 2008) is deeper than 3,000 ft. There has been no shallow (<3,000 ft) drilling on the tract in the modern era. *(The remaining tract records are a single deep 22,545-ft wellbore and permitted-but-undrilled location entries.)*

### 2. Within 1 mile — no shallow wells

Three wellbores of any depth lie within one mile of the tract; **none is shallow (<3,000 ft).**

### 3. Within 2 miles — shallow drilling ended roughly 24 years ago

Of about 46 wellbores within two miles, the ten shallow wells were spudded between 1960 and 2002. The most recent shallow spud within two miles was in 2002, and most of these wells are plugged and abandoned. No shallow well has been spudded within two miles in roughly a quarter-century.

### 4. Within 5, 10, and 15 miles

| Radius | Wells (all depths) | Shallow (<3,000 ft) | Shallow spudded ≥ 2020 | Of shallow, plugged | Shallow spud-year range |
|---|---|---|---|---|---|
| ≤ 5 mi | 496 | 131 | 3 | 88 | 1954–2022 |
| ≤ 10 mi | 1,152 | 239 | 7 | 148 | 1953–2025 |
| ≤ 15 mi | 1,757 | 268 | 14 | 166 | 1953–2025 |

Recent (post-2015) shallow wells appear only beyond about two miles. The nearest recent shallow well is 2.2 miles from the tract (2022). Within five miles, only three shallow wells have been drilled since 2015.

### 5. The nearest active wells are decades-old completions

The nearest non-plugged shallow wells were spudded in 1970 (1.28 mi) and 1988 (1.97 mi) — decades-old completions, not active drilling. A ground-vibration source is an operating drill rig; a plugged or long-completed wellbore is not. No active shallow drilling is occurring adjacent to the tract.

### 6. County-wide context — and how much of it is definitionally vertical

Since 2020, **1,117 wells were spudded in Pecos County (~4,700 sq mi)**, with a recorded depth for all but one. Of those, **556 — 49.8% — are under 3,000 ft and are therefore, by the depth structure of the basin, vertical wells.** (Under a 5,000-ft threshold the figure is 50.8%; only 11 of these recent wells fall between 3,000 and 5,000 ft, so the cutoff barely changes the count — see Finding 7.) In other words, **roughly half of all drilling in Pecos County since 2020 is definitionally vertical, shallow activity**, and the other half is deep development.

Those 556 shallow vertical wells are the county-wide population most relevant here, and they are concentrated well away from the site: **only 7 are within ten miles of the Caramba North tract and 14 within fifteen miles; the remaining 542 (~98%) are more than fifteen miles away, at a median distance of roughly sixty miles.** The RRC drilling-permit record points the same way: only 27 permits of any kind sit within ten miles of the tract, and none has been filed within ten miles since 2020.

### 7. The shallow wells at issue are vertical, not horizontal

Modern high-intensity drilling — and the ground vibration associated with it — is a feature of long-lateral **horizontal** wells, which in the Permian/Delaware Basin target deep producing benches. Pecos drilling since 2020 falls into two cleanly separated depth populations: a **shallow group at roughly 1,000–3,000 ft (≈50% of wells — conventional vertical)** and a **deep group at roughly 7,000–15,000 ft (≈50% — consistent with horizontal development)**. Almost nothing is drilled between them — only 11 of 1,116 recent wells fall between 3,000 and 5,000 ft — so a 3,000-ft cutoff and a 5,000-ft cutoff identify essentially the same vertical population. Horizontal laterals are not targeted at these shallow intervals. The sub-3,000-ft (equivalently, sub-5,000-ft) wells that are the subject of this memorandum are therefore, by the depth structure of the basin, **conventional vertical wellbores** — a fundamentally lower-intensity activity than the deep horizontal development that characterizes modern drilling. *(See limitations for the basis of this characterization and the status of an explicit profile field.)*

## Scope, method, and limitations (read before relying on this)

- **Source.** RRC dbo900 Full Wellbore extract and RRC W-1 drilling-permit extract, as carried in the LRP Texas Energy GIS dataset (`data/wells_permian6.csv`, `data/permits_permian6.csv`), filtered to `county_name = Pecos`. Caramba North geometry and centroid taken from `combined_geoms.geojson`. Distances are great-circle from the tract centroid; in-tract membership is exact point-in-polygon.
- **"Shallow" = total reported depth < 3,000 ft.** A < 2,000-ft cut and a ≤ 3,000-ft cut were also run and do not change the conclusions.
- **Well orientation.** The RRC wellbore (drilled-well) extract does **not** record a vertical/horizontal designation. The drilling-permit extract nominally carries a wellbore-profile field, but it is derived by a text/byte heuristic that yields an implausible ~50/50 split and is **not relied on here.** Orientation is instead inferred from total depth — a directly recorded field — plus well-established basin geology: in the Permian/Delaware Basin, horizontal development targets producing benches thousands of feet below 5,000 ft, drilled with mile-plus laterals, whereas wells at or under 3,000 ft (and, here, under 5,000 ft) are conventional vertical wellbores. This inference is unusually robust at this location because the Pecos depth record since 2020 is **strongly bimodal** — a shallow ~1,000–3,000-ft mode and a deep ~7,000–15,000-ft mode, with only 11 of 1,116 wells in between — so the conclusion does not depend on the exact cutoff. Depth coverage for the 2020-and-later wells is essentially complete (1,116 of 1,117), so the percentages in Findings 6–7 are not affected by the missing-depth issue noted below. A definitive, well-by-well horizontal/vertical tally would require re-scraping the RRC W-1 "Wellbore Profile" field directly — a separate data task.
- **Data completeness.** Roughly 40% of Pecos wellbore records in the RRC extract lack a recorded total depth, and a small number lack a spud year. County-wide shallow *counts* are therefore conservative lower bounds among depth-known wells. The proximity and recency findings rely on the geolocated records directly and are robust to the missing-depth records (a well with no recorded depth is not counted as shallow).
- **Drilling-record analysis, not a geotechnical study.** This memorandum quantifies the location, depth, recency, and status of drilling at and near the site. It does not model vibration propagation through site soils; that is a separate engineering analysis.

*Reproduce: `data/wells_permian6.csv`, `data/permits_permian6.csv`, `combined_geoms.geojson`; analysis scripts archived with this report (`pecos_shallow_analysis.py`, `pecos_caramba_vicinity.py`, `pecos_v2_rings_permits.py`, `pecos_vertical_share.py`).*
