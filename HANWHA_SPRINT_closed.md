# HANWHA_SPRINT.md — CLOSED 2026-04-21 16:37 EDT (12:37 EST)

**Status:** DELIVERED — ~5.5 hrs ahead of 6:00 PM EST deadline.
**Hanwha URL:** https://lrp-tx-gis.netlify.app (open, no password per sprint decision).
**Final prod deploy:** `69e7a7859da0044dc5b0f714`, 22 layers, 17.5 MB total tiles, 0 errored.

---

## Delivered

- 22 layers live (up from 17 at sprint start). New additions: parcels_pecos (Chat 41), rrc_pipelines, tiger_highways, bts_rail, water_mains_approx, labels_hubs (Waha).
- ERCOT queue popup enrichment (Chat 41): MW / fuel / commissioning / funnel stage / county / zone / entity.
- Planned Upgrade styling (Chat 44): amber "PLANNED UPGRADE" badge prefix on tpit_subs + tpit_lines popups with kV + expected completion + project fields.
- Custom icons (Chat 44): sun/wind/battery/flame/droplet emoji overlays for solar/wind/battery/plants/wells from zoom 9+, white 2px halo.
- Measure tool (Chat 44): distance miles + area acres, polygon close on double-click.
- Print-to-PDF (Chat 44): landscape, LRP-branded header strip, dated, scale bar preserved, chrome hidden.
- 5 basemaps (Chat 44): Carto Light / Esri Streets / Esri Imagery / OpenFreeMap / NAIP.
- Share-view hash state with base + layers + center + zoom preserved.

---

## Deferred post-sprint (from Chat 43 FETCH_FAILED + Chat 44 descope)

- rrc_wells_permian — endpoint moved, requires discovery chat.
- tceq_gas_turbines — no public GIS endpoint, manual-CSV pattern required.
- tceq_nsr_pending — same.
- tceq_pbr — same.
- tceq_pws — endpoint schema-shifted, alternative discovery required.

Reason for descope vs. sprint draft scope: Chat 43 refresh batch returned 5 FETCH_FAILED across these sources. Rather than extend sprint, the 4 successful refreshes + display polish were prioritized to hit the deadline. Deferred sources are independent add-ons; can be added post-Hanwha without disrupting the delivered map.

---

## Archival

This file can be archived or deleted. Backlog items promoted to `WIP_OPEN.md`.
