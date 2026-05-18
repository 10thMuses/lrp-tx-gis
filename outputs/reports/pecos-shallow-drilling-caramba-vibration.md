# Shallow (<3,000 ft) Oil-and-Gas Drilling at and Near the Caramba North Tract — Historical and Recent Record

**Prepared:** 2026-05-18 · **Subject site:** Caramba North tract (~1,300 ac), Pecos County, TX — centroid ≈ 30.9032° N, 102.9747° W · **Classification:** Confidential

## Purpose

This memorandum summarizes the historical and recent record of shallow oil-and-gas drilling — wells less than 3,000 ft total depth — at and in the vicinity of the Caramba North tract, drawn from the Railroad Commission of Texas (RRC) wellbore and drilling-permit records. It is provided as factual context for evaluating potential ground-vibration considerations for a data-center development on the site.

## Summary of findings

Shallow (<3,000 ft) drilling at and around the Caramba North tract is a legacy activity that has effectively ceased in the immediate vicinity of the site. No well of any kind has been spudded within two miles of the tract since 2020; no shallow well within two miles since 2002; and the few nearby legacy shallow wells are predominantly plugged and abandoned. Drilling does continue across Pecos County, but it is concentrated well away from the site — about 83% of the wells spudded county-wide since 2020 are more than fifteen miles from the tract (median ≈ 30 miles), and no drilling permit has been filed within ten miles of the tract since 2020. That modern activity is, per the Railroad Commission's wellbore-profile record, overwhelmingly **horizontal, deep** development — roughly 87% of Pecos drilling permits since 2020 — not shallow vertical drilling, and in any case it is not occurring at or adjacent to the site.

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

### 6. County-wide context — recent activity is concentrated away from the site

Since 2020, **1,117 wells were spudded across Pecos County (~4,700 sq mi)**. Their distribution relative to the tract is decisive: **none within two miles, 8 within five miles, 23 within ten miles, and 190 within fifteen miles; the remaining 927 — about 83% — are more than fifteen miles away, at a median distance of roughly thirty miles.** The drilling-permit record agrees: only 27 permits of any kind sit within ten miles of the tract, and **none has been filed within ten miles since 2020** — permitted activity since 2020 appears only in the ten-to-fifteen-mile band and beyond. Recent drilling in the county is real, but it is not occurring at or adjacent to the Caramba North site.

### 7. Modern drilling is predominantly horizontal — and not at the site

Shallow vertical drilling is the activity at issue. The Railroad Commission's W-1 **Wellbore Profile** field shows that modern drilling in Pecos County is the opposite of that: of roughly 900 drilling permits issued in the county since 2020, **about 87% are horizontal and only ~12% vertical.** Modern development in this part of the Permian/Delaware Basin is deep horizontal drilling, not shallow vertical work. Shallow (<3,000 ft) vertical drilling of the kind at issue is, in this county, largely a **historical** activity (Findings 1–5), and the modern horizontal program — like all recent drilling — is concentrated well away from the tract (Finding 6). *(Total-depth values in the permit extract are not a reliable proxy for orientation; the figures here come from the RRC Wellbore Profile field directly — see limitations.)*

## Scope, method, and limitations (read before relying on this)

- **Source.** Proximity, recency, and plug-status findings: RRC dbo900 Full Wellbore extract and the carried drilling-permit dataset (`data/wells_permian6.csv`, `data/permits_permian6.csv`), filtered to `county_name = Pecos`. Orientation finding: a direct scrape of the RRC public W-1 drilling-permit system for Pecos, 2020–present, carrying the agency's own "Wellbore Profile" field (`outputs/refresh/rrc_w1_permits.csv`). Caramba North geometry and centroid from `combined_geoms.geojson`. Distances are great-circle from the tract centroid; in-tract membership is exact point-in-polygon.
- **"Shallow" = total reported depth < 3,000 ft.** A < 2,000-ft cut and a ≤ 3,000-ft cut were also run and do not change the conclusions.
- **Well orientation.** Orientation figures are taken directly from the Railroad Commission's W-1 **"Wellbore Profile"** field (Horizontal | Vertical | Directional), retrieved from the agency's public drilling-permit system; for Pecos permits since 2020 this field is populated for essentially all records (n ≈ 900). **Total-depth values in these extracts are not a reliable proxy for orientation** — the permit extract places a large majority of clearly-horizontal permits below 3,000 ft — so no depth-based orientation inference is used in this memorandum; the profile field is used directly. The RRC dbo900 wellbore (drilled-well) extract used for the proximity and recency findings does not carry an orientation field, but those findings (location, spud year, plug status) do not depend on orientation.
- **Data completeness.** Roughly 40% of Pecos wellbore records in the RRC extract lack a recorded total depth, and a small number lack a spud year. County-wide shallow *counts* are therefore conservative lower bounds among depth-known wells. The proximity and recency findings rely on the geolocated records directly and are robust to the missing-depth records (a well with no recorded depth is not counted as shallow).
- **Drilling-record analysis, not a geotechnical study.** This memorandum quantifies the location, depth, recency, and status of drilling at and near the site. It does not model vibration propagation through site soils; that is a separate engineering analysis.

*Reproduce: `data/wells_permian6.csv`, `data/permits_permian6.csv`, `outputs/refresh/rrc_w1_permits.csv` (RRC W-1 Wellbore Profile scrape, Pecos 2020–present), `combined_geoms.geojson`; analysis scripts archived with this report.*
