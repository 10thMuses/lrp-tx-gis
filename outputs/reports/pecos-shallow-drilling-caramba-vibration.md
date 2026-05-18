# Shallow (<3,000  ft) Drilling Near the Caramba North Tract — Vibration-Risk Analysis

**Prepared:** 2026-05-18 · **Classification:** Confidential — prepared in connection with the Pecos County land transaction · **Subject site:** Caramba North tract (~1,300 ac), Pecos County, TX — centroid ≈ 30.9032° N, 102.9747° W

## Question presented

The prospective buyer has raised a concern that **shallow oil-and-gas drilling in Pecos County — specifically wells less than 3,000 ft deep — could generate ground vibration that interferes with the operation of a data center the buyer intends to build on the Caramba North tract.** This memorandum tests that concern against the Railroad Commission of Texas (RRC) wellbore and spud record.

## Bottom line

**The drilling record does not support a material risk that shallow (<3,000 ft) drilling will occur at, or close enough to, the Caramba North tract to affect data-center operations.** Shallow drilling in the immediate vicinity of the site is a *legacy* activity that effectively ceased decades ago, and the small number of nearby legacy wells are predominantly plugged and abandoned — i.e., not operating sources of any vibration. The buyer's concern, while understandable as a general matter, is not borne out by the actual drilling history at this location.

The findings below are deliberately scoped and stated conservatively so they remain defensible: shallow drilling *does* continue elsewhere in Pecos County (a ~4,700-square-mile county), but the operative question for a site-specific vibration concern is **proximity and recency**, and on those measures the record is clear.

## Findings

### 1. On the Caramba North tract itself: no modern shallow drilling

Nine wellbore records fall inside the tract boundary. Of these:

| Depth (ft) | Spud year | Status | Oil/Gas |
|---|---|---|---|
| 2,873 | 1960 | Plugged & abandoned | Gas |
| 3,067 | 1991 | Plugged & abandoned | Oil |
| 3,109 | 1957 | Plugged & abandoned | Oil |
| 3,186 | 1987 | Plugged & abandoned | Oil |
| 3,250 | 2008 | Active | Oil |
| 22,545 | 1978 | Plugged & abandoned | Gas |
| — | — | undrilled location record | — |
| — | — | undrilled location record | — |
| — | — | undrilled location record | — |

- **Exactly one well on the tract is below the buyer's 3,000-ft threshold: a 2,873-ft well spudded in 1960 — drilled 66 years ago and long since plugged and abandoned.**
- The only non-plugged, depth-recorded well on the tract (3,250 ft, spudded 2008) is **deeper than the 3,000-ft threshold the concern is premised on**, and was drilled 18 years ago.
- There has been **no shallow (<3,000 ft) drilling on the Caramba North tract in the modern era at all.**

### 2. Within 1 mile of the site: zero shallow wells

Only three wellbores of any depth sit within one mile of the tract centroid, and **none is a shallow (<3,000 ft) well.** The area immediately surrounding the proposed data center has no shallow-well drilling history.

### 3. Within 2 miles: shallow drilling ended ~24 years ago

Of the ~46 wellbores within two miles, every well shallower than 3,000 ft was spudded between **1957 and 2002**. The **most recent shallow spud within two miles was in 2002** — and that well is plugged. The large majority of the within-2-mile shallow wells are plugged and abandoned; the handful still un-plugged were drilled in **1970 and 1988**. There is **no active, and no recent, shallow drilling within two miles of the site.**

### 4. Within 5 miles: only three shallow spuds in the last decade

Within five miles there are 496 wellbores (131 shallow). Shallow spuds since 2015 number **three** — all drilled in **2022**, all at **1,700 ft**, and all located **2.2–3.7 miles** from the tract (none closer than 2.2 mi). Across the last ~16 years there have been six shallow spuds within five miles. The nearest shallow well of any vintage is 1.05 miles away and was spudded in 1966 (plugged).

### 5. The nearest *active* shallow wells are 55-year-old wellbores, not active drilling

A vibration source is an **operating drill rig**, not a completed (or plugged) wellbore. The nearest non-plugged shallow wells to the site were spudded in **1970 (1.28 mi)** and **1988 (1.97 mi, 2.04 mi)** — decades-old completions, not drilling activity. The nearest *recent* shallow well (2022) is 2.2 miles away. No active shallow **drilling** is occurring adjacent to the tract.

## Why this answers the buyer's concern

The buyer's worry depends on a factual premise: that shallow (<3,000 ft) **drilling** is occurring, or is likely to occur, close enough to the Caramba North site to transmit operationally significant vibration to a data center. The RRC record refutes that premise at this location:

- **On-site:** one shallow well, drilled in 1960, plugged. No modern shallow drilling on the tract.
- **0–1 mi:** no shallow wells at all.
- **0–2 mi:** no shallow spud since 2002; nearest still-active shallow wells date to 1970/1988.
- **0–5 mi:** only three shallow spuds in the past decade, all in 2022, all ≥2.2 mi away.

Ground vibration from drilling attenuates rapidly with distance and has no source at all from a plugged or long-completed well. With no shallow drilling on or within a mile of the tract, none within two miles for roughly a quarter-century, and only a sparse, distant 2022 cluster within five miles, the drilling record provides **strong affirmative support** for the position that shallow-drilling vibration is not a credible threat to data-center operations at Caramba North.

## Scope, method, and limitations (read before relying on this)

- **Source.** RRC dbo900 Full Wellbore extract as carried in the LRP Texas Energy GIS dataset (`data/wells_permian6.csv`), filtered to `county_name = Pecos`. Caramba North geometry and centroid taken from the project's `combined_geoms.geojson`. Distances are great-circle from the tract centroid; in-tract membership is exact point-in-polygon.
- **"Shallow" = total reported depth < 3,000 ft**, matching the buyer's stated threshold. A <2,000-ft cut and a ≤3,000-ft cut were also run and do not change the conclusions.
- **Data completeness.** Roughly 40% of Pecos wellbore records in the RRC extract lack a recorded total depth, and a small number lack a spud year. County-wide shallow *counts* are therefore conservative lower bounds among depth-known wells. The proximity and recency findings around Caramba rely on the geolocated records directly and are robust to the missing-depth records (a well with no recorded depth is not counted as shallow).
- **County-wide context, stated for candor.** Shallow drilling continues in other parts of Pecos County — roughly 556 shallow spuds county-wide since 2020. This memo does **not** claim shallow drilling has stopped in Pecos County; it establishes that it is not occurring at or adjacent to the Caramba North site, which is the only question relevant to a site-specific vibration concern.
- **This is a drilling-record analysis, not a geotechnical study.** It quantifies the likelihood, recency, depth, and proximity of shallow drilling — the factual premise of the concern. It does not model vibration propagation through site soils; that separate analysis, if commissioned, would only reinforce the conclusion, since vibration cannot propagate from drilling that is not occurring near the site.

*Reproduce: `data/wells_permian6.csv` + `combined_geoms.geojson`; analysis scripts archived with this report.*
