# dc_anchors.json — schema and conventions

Curated index of large announced and under-construction Texas datacenter anchor projects, primarily AI/HPC oriented. Source feed for the Chat 99 layer build (`dc_anchors` layer in `layers.yaml` via custom loader). Hand-curated with source attribution; refresh cadence target weekly via the Chat 100 GitHub Actions cron with LLM-in-the-loop parser.

## Inclusion criteria

- Texas-sited datacenter campus, hyperscale or AI-anchored
- ≥100 MW announced capacity OR strategically material in its county (anchor tenant for a regional power buildout)
- Status ∈ {announced, permitted, under_construction, operational}; pure speculation/rumor excluded
- Excludes traditional colocation/enterprise-scale facilities below the threshold

## Top-level structure

```
{
  "schema_version": "1.0",
  "generated": "ISO date",
  "scope": "free text",
  "entries": [ <entry>, ... ]
}
```

## Entry schema

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | Slugified unique key, kebab-case, stable across refreshes. Used as the join key by the Chat 99 layer loader. |
| `name` | string | yes | Project display name, including parenthetical alternates where common (e.g. "Stargate Abilene (Project Ludicrous)"). |
| `developer` | string | yes | Lead developer. Multi-party deals expressed as "Developer (role); Operator (role); Tenant (role)". |
| `county` | string | yes | Texas county name without "County" suffix. Single county only — multi-county campuses pick the primary parcel county. |
| `lat` | number | yes | Decimal degrees, WGS84. May be null only if `coord_accuracy` is `county_centroid` and centroid not yet looked up; preferred to populate even at low precision. |
| `lon` | number | yes | Decimal degrees, WGS84. |
| `coord_accuracy` | enum | yes | One of `precise` (parcel-level, ≤500 m), `approximate` (right area, ≤10 km), `county_centroid` (county geometric centroid; rendering should reflect imprecision). |
| `status` | enum | yes | One of `announced` (publicly disclosed, no permits/site work), `permitted` (key permits issued, pre-construction), `under_construction` (active site work or partial commissioning), `operational` (any phase commissioned). |
| `capacity_mw_announced` | integer | yes | Total announced/permitted IT or generation capacity in MW. Distinguish in `power_source` whether the figure is generation or IT load when the two diverge materially. |
| `commissioned_target` | integer | nullable | Year of first power / first phase commissioning. Null if not publicly stated. |
| `power_source` | string | yes | Free text describing generation mix, grid connection, acreage, phasing, key counterparties. The "everything that doesn't fit a structured field" bucket. |
| `sources` | array | yes | ≥1 source per entry; ≥2 sources per non-trivial field is the aspirational target. |
| `single_source` | boolean | optional | Set `true` if entry rests on only one independent source. Default omitted (treated as multi-sourced). |

## Source object schema

```json
{
  "url": "https://...",
  "accessed": "YYYY-MM-DD",
  "claim": "What this URL substantiates."
}
```

Source quality preference (high → low):

1. Official permits (TCEQ air permits, county records, NRC filings)
2. SEC filings, Nasdaq disclosures, primary press releases from the developer
3. ERCOT INR filings, county economic-development records
4. Tier-1 trade press (DataCenterDynamics, Bloomberg, Reuters, FT, Texas Tribune, Inside Climate News)
5. Aggregator/secondary tech press (confirmation only)
6. Wikipedia / wiki-style aggregators (lowest tier; cross-check before relying)

## Data quality conventions

- **Capacity figures:** When announced campus capacity (e.g., 11 GW) materially exceeds permitted/contracted capacity (e.g., 6 GW permit + first 1 GW gas turbines acquired), record the announced full-buildout figure in `capacity_mw_announced` and use `power_source` to spell out the phasing reality. The Chat 99 layer renders a `capacity_mw_announced` symbology; the popup surfaces the phased breakdown.
- **Coordinate precision:** Mark `county_centroid` clearly. Chat 99's renderer treats centroids differently (lower-opacity marker, "approximate" badge in popup) so consumers don't mistake a centroid pin for a parcel.
- **Conflicting figures across sources:** Pick the most recent primary-source figure; note the variance in `power_source`. Example: GW Ranch reported as both "17 mi N of Fort Stockton" and "33 mi south of Fort Stockton" — use the more frequently cited figure and flag the conflict.
- **Project name aliases:** Project Matador = Fermi America HyperGrid = Advanced Energy and Intelligence Campus. Capture all aliases in `name` (parenthetical) for grep matching from external feeds.
- **Status transitions:** A project that has any phase operational is `operational`, even if the bulk of capacity is still under construction. Distinguish via `power_source` text.
- **Multi-tenant / co-located campuses:** Stargate Abilene and the adjacent Microsoft-Crusoe campus are recorded as separate entries despite sharing the Lancium Clean Campus footprint, because they have distinct power plants, lease counterparties, and capacities.
- **County conflict:** Project Matador has been variously reported as Amarillo (city), Carson County (TTU land near Pantex), and "the Texas Panhandle." The TTU-Pantex parcel is in Carson County; that's authoritative.

## Refresh cadence

Target: weekly, Mondays 06:00 UTC, via the Chat 100 GitHub Actions cron. Refresh strategy:

1. Re-fetch a curated set of news/press-release URL feeds (per-entry `sources[*].url` plus a watchlist of TX datacenter trade-press feeds).
2. LLM-in-the-loop parser proposes diffs against the current `dc_anchors.json` (status changes, capacity revisions, new entries). Diffs are surfaced as a PR for human review — never auto-merged.
3. New entries proposed by the parser are flagged with `single_source: true` until a second independent source is added on review.
4. `accessed` dates are bumped on confirmation that the source still substantiates the claim.

## Out-of-scope

- Crypto-only mining facilities (Hut 8, Riot Platforms etc.) without an explicit AI/HPC anchor
- Sub-100 MW colocation/enterprise sites
- International Stargate sites (UAE, UK, Norway, Argentina, etc.)
- Stargate sites outside Texas (Shackelford, Milam, Abilene are in scope; Ohio, Michigan, New Mexico, Wisconsin sites are not)
- Pure speculation without permit or developer announcement

## Versioning

`schema_version` follows semver. Breaking schema changes (field renames, type changes) bump major. Field additions bump minor. Bug-fix-only data refreshes do not bump schema_version.
