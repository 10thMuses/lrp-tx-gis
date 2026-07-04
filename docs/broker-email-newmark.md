# Broker introduction email — Newmark investment sales

Draft v1 · 2026-07-04 · Send from andrea@abhcm.com. Placeholders in [brackets].
Companion deliverables: map polish (in progress), PDF deep-dive (on hold, pending
prior-session presentation retrieval).

---

**To:** [Broker name], Newmark
**From:** Andrea Himmel, Land Resource Partners
**Subject:** Caramba North — Pecos County, TX | Diligence platform access ahead of engagement

---

[First name],

Ahead of formalizing the investment-sales engagement, I want to put the full
diligence picture in front of your team on day one. We have built a
purpose-built GIS platform covering the Caramba North site — approximately 1,300
acres in Pecos County, Texas — and the energy-infrastructure context that drives
its value: proximate generation, transmission, midstream, water, hyperscale
land precedents, and two decades of permitting and drilling activity across the
surrounding six-county Permian corridor.

The platform is live, password-protected, and current — core layers refresh on
weekly-to-monthly cadences from primary public sources (EIA, ERCOT, RRC, TCEQ,
Census, USGS). Access credentials and a navigation guide are below my
signature.

**What the map covers, in brief:**

- **The site and its immediate context.** The Caramba North boundary, county
  and municipal reference, interstate/US highway and mainline rail corridors,
  the Waha natural-gas hub, the AEP Solstice substation, and the Middle Pecos
  Groundwater Conservation District's Management Zone 1.
- **The Occidental footprint.** Seven layers compiled from public filings
  mapping OXY's regional position: power and NET Power assets, midstream and
  processing, ERCOT interconnection-queue entries, TCEQ air permits, water
  infrastructure, carbon-management infrastructure, and 294 RRC drilling
  permits filed 2020–2026.
- **Hyperscale precedent.** The three announced large-scale power/data-center
  land campuses in the immediate area — La Escalera Ranch (Apex Clean Energy),
  Longfellow Ranch, and GW Ranch (Pacifico Energy) — mapped as boundaries for
  direct comparison to the site.
- **Power and grid.** Every EIA-860 registered plant, battery installation,
  solar farm, and USGS-inventoried wind turbine in scope; transmission at
  ≥100 kV; substations; and ERCOT's planned transmission and substation
  upgrades (TPIT), which indicate where grid capacity is being built next.
- **Midstream.** Natural gas, crude trunk, and NGL pipelines (EIA/HIFLD), gas
  processing plants, and RRC large-diameter (>20") pipeline routes.
- **The development pipeline.** The active ERCOT interconnection queue
  (~1,800 positions, sized by capacity) and announced data-center anchors of
  100 MW or greater.
- **Permitting, incentives, and drilling history.** TCEQ gas-turbine air
  permits; ~29,000 RRC W-1 drilling permits (2018–present) across the
  six-county corridor; approved local tax abatements (Ch. 381/312) from
  commissioners-court records; and the full spud-well record — roughly 99,000
  wells, 1964 to present — filterable by county, depth, and era, with
  exportable summary statistics.

Each feature on the map traces to a cited public dataset; nothing is
hand-placed except labeled reference toponyms, and the one approximated
boundary (the groundwater management zone) is disclosed as such. Sources and
refresh cadences are itemized below.

Suggested next step: a 45-minute working session where I walk your team
through the platform and the sale thesis, after which we will circulate the
deep-dive deck. [Proposed windows / scheduling link.]

Looking forward to working together on this.

Best regards,

**Andrea Himmel**
Land Resource Partners
andrea@abhcm.com · [phone]

---
---

## Appendix A — Access

| | |
|---|---|
| **URL** | https://lrp-tx-gis.netlify.app |
| **Login** | Your business email + access password |
| **Password** | `LRP-Permian-2026` |
| **Access policy** | Confidential; credentials are for the Newmark deal team only. Access is logged. Sessions persist per browser; no install required. Desktop Chrome/Edge/Safari recommended. |

## Appendix B — Navigating the map

**Layout.** Left sidebar: layer groups with individual toggles and live feature
counts. Top bar: **Measure** (distance/area), **Reset** (default view),
**Share** (copies a URL capturing your exact view, layers, and filters — use it
to circulate specific exhibits within your team), **Print** (landscape
print/PDF). Basemap picker at the bottom of the sidebar (Esri World Imagery is
the default; Carto Light is best for dense layer work; NAIP aerial for
site-level detail).

**Layers.** Toggle any layer on/off; groups are organized by theme (Reference,
OXY footprint, Local Focal Points, Hyperscale Campuses, Power Generation,
Transmission & Grid, Energy Infrastructure, Projects, Pipelines, Permits,
Wells). Some high-density layers activate as you zoom in. Click any feature
for a popup with its attributes, source, and as-of date.

**Filters.** Layers with a filter icon support field-level filtering — e.g.,
wells by county/depth/spud year, the ERCOT queue by fuel/capacity/status,
permits by operator. The **Views** dropdown at the top of the sidebar loads
pre-built analytical views of the drilling record. A time scrubber animates
well history by year.

**Suggested starting points** (links restore the exact view after login):

1. **Site overview** (default view): https://lrp-tx-gis.netlify.app
2. **Regional power & grid:** https://lrp-tx-gis.netlify.app/#lat=31.1500&lon=-102.9000&zoom=8&layers=counties,county_labels,cities,tiger_highways,caramba_north,eia860_plants,eia860_battery,solar,transmission,substations,ercot_queue,dc_anchors&base=carto_light
3. **OXY & midstream:** https://lrp-tx-gis.netlify.app/#lat=31.0000&lon=-103.0000&zoom=9&layers=counties,county_labels,cities,caramba_north,oxy_power,oxy_midstream,oxy_carbon,oxy_water,oxy_ercot,hifld_ng_pipelines,rrc_pipelines&base=carto_light
4. **Permitting & drilling activity:** https://lrp-tx-gis.netlify.app/#lat=31.0000&lon=-103.0000&zoom=9&layers=counties,county_labels,caramba_north,permits_permian6,tax_abatements,wells_permian6&base=carto_light

## Appendix C — Data sources & refresh cadence

| Domain | Source | Cadence | Link |
|---|---|---|---|
| County / highway reference | U.S. Census TIGER/Line 2023 | Static | https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html |
| Rail | BTS North American Rail Network | Static | https://geodata.bts.gov |
| Power plants, batteries, solar | EIA-860 (annual + generator detail) | Annual | https://www.eia.gov/electricity/data/eia860/ |
| Wind turbines | USGS/LBNL U.S. Wind Turbine Database | Annual | https://eerscmap.usgs.gov/uswtdb/ |
| Transmission ≥100 kV; NG/crude/NGL pipelines; gas processing | EIA U.S. Energy Atlas (HIFLD) | Annual | https://atlas.eia.gov |
| Substations | OpenStreetMap | Annual | https://www.openstreetmap.org |
| Interconnection queue | ERCOT GIS Report | Monthly | https://www.ercot.com/gridinfo/resource |
| Planned grid upgrades | ERCOT Transmission Project Information Tracking (TPIT) | Monthly | https://www.ercot.com/gridinfo/transmission |
| Drilling permits (W-1) & wellbore record | Railroad Commission of Texas — public datasets & permit query | Weekly | https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/ |
| Large-diameter pipelines | RRC digital pipeline data | Annual | https://www.rrc.texas.gov/pipeline-safety/ |
| Air permits (gas turbines; OXY facilities) | TCEQ air permitting records | Annual | https://www.tceq.texas.gov/permitting/air |
| Tax abatements (Ch. 381/312) | County commissioners-court records (compiled) | Weekly | County clerk agendas; compilation available on request |
| Groundwater district zone | Middle Pecos GCD (boundary approximate, disclosed) | On publication | https://www.middlepecosgcd.org |
| OXY footprint layers | Compiled from RRC, TCEQ, ERCOT, and public company disclosures | With source layers | Per-feature source citations in popups |

*Confidentiality: this platform and its contents are provided solely for
evaluation of the referenced engagement and may not be redistributed without
Land Resource Partners' written consent.*
