# -*- coding: utf-8 -*-
"""Single source of truth for the OXY dossier: asset list (business-language) +
geography. Imported by oxy_build_maps.py (to plot) and build_oxy_report.py (to
write the report), so the maps and the text can never drift apart.

Each asset carries: section, type, status, location (lon/lat OR county), a short
map_label, a plain-English one-liner, standardized business `rows`, a `jv`
relevance note (angled at a hyperscale data-center joint venture), and `src`
footnote text (where the raw facility-database IDs now live).
"""

CARAMBA = (-102.9747, 30.9032)  # Caramba North centroid (Pecos Co.) — Census TIGER stream

# OXY-named field substations (plotted small/unnumbered for orientation).
SUBSTATIONS = [
    {"name": "North Cowden substation", "label": "North Cowden", "type": "sub", "lon": -102.51677, "lat": 32.006051},
    {"name": "South Curtis Ranch substation", "label": "S. Curtis Ranch", "type": "sub", "lon": -102.159612, "lat": 32.129845},
    {"name": "Welch substation", "label": "Welch", "type": "sub", "lon": -102.13773, "lat": 32.896391},
    {"name": "Cogdell substation", "label": "Cogdell", "type": "sub", "lon": -100.886409, "lat": 32.942344},
]

ASSETS = [
    # ===================== MIDSTREAM / GAS / CO2 =====================
    {
        "section": "midstream", "type": "gas", "status": "existing",
        "name": "Century gas & CO₂ plant", "map_label": "Century plant (Pecos)",
        "lon": -102.5809, "lat": 30.6075, "on_map": True,
        "one": "A billion-dollar plant in Pecos County that strips carbon dioxide out of natural gas and ships it off for oilfield use — the closest large OXY facility to Caramba North.",
        "rows": [
            ("Where", "Pecos County, Texas — near Gardendale, about 31 miles from Caramba North."),
            ("What it does", "Cleans high-CO₂ natural gas, separating the CO₂ so the gas can be sold and the CO₂ can be reused to push more oil out of older fields."),
            ("Scale", "Handles up to 800 million cubic feet of gas a day and captures roughly 8.4 million tonnes of CO₂ a year — the largest industrial carbon-capture site in North America."),
            ("Who controls it", "Built and run day-to-day by SandRidge; OXY funded it (~$1.1 billion) and takes all the captured CO₂. One report says OXY sold the plant itself in 2022 but still takes the carbon and operates the export pipeline."),
        ],
        "jv": "The single nearest piece of major OXY infrastructure to the Williams land. Its captured-CO₂ stream and the pipeline it feeds are exactly the carbon-handling backbone a gas-powered data center would need to make low-emission power claims.",
        "src": "Century gas/CO₂ plant — EPA Greenhouse Gas Reporting Program facility 1004301; CO₂ export pipeline PHMSA operator ID 31502; TCEQ regulated entity RN105567218 (air account 85488). Sources: Oil & Gas Journal (start-up); SandRidge release, 30 Jun 2008; MIT Sequestration database; PHMSA. “800 MMcf/d” is gas-treating capacity; “~450 MMcf/d” is the CO₂ export rate.",
    },
    {
        "section": "midstream", "type": "gas", "status": "existing",
        "name": "Block 31 plant & CO₂ flood", "map_label": "Block 31 (Crane)",
        "lon": -102.4623, "lat": 31.4415, "on_map": True,
        "one": "An OXY-operated oil field and small gas plant in Crane County that has used CO₂ to coax out extra oil since the 1950s — the second-closest OXY asset to Caramba North.",
        "rows": [
            ("Where", "Crane County, Texas — about 48 miles from Caramba North."),
            ("What it does", "Injects CO₂ into an old oil reservoir to recover more oil, and processes the gas that comes back up."),
            ("Scale", "A modest 41 million cubic feet a day of gas processing; about 344 wells; roughly 7,500 barrels of oil and 730 million cubic feet of gas in a recent month."),
            ("Who controls it", "100% owned and operated by OXY."),
        ],
        "jv": "Shows OXY's operating presence stretches to within ~50 miles of Caramba North. A fully-instrumented, OXY-run site that anchors the company's footprint on the Williams side of the basin.",
        "src": "Block 31 — EPA GHGRP facility 1001132 (115,965 t CO₂e, 2023); EIA-757 plant NGPP480657 (41 MMcf/d); Texas RRC operator #630591; TCEQ RN100223569, NSR permit 73238, Title V FOP 547; CO₂ injected under Class II UIC. Sources: EPA Envirofacts; EIA-757; RRC; TCEQ.",
    },
    {
        "section": "midstream", "type": "gas", "status": "existing",
        "name": "Wasson / Denver Unit CO₂ field", "map_label": "Wasson CO₂-EOR",
        "lon": -102.7569, "lat": 33.0099, "on_map": True,
        "one": "The world's largest CO₂-enhanced oil project, and the demand center that makes OXY's whole CO₂ network worth building.",
        "rows": [
            ("Where", "Gaines and Yoakum Counties, Texas (about 130 miles north of Caramba North)."),
            ("What it does", "Injects huge volumes of CO₂ underground to recover oil — and, in doing so, permanently stores much of that CO₂, which is independently measured and verified."),
            ("Scale", "About 420 million cubic feet of CO₂ injected per day across ~27,000 acres. It permanently stored 3.7 million tonnes of CO₂ in 2023 and has injected ~213 million tonnes over its life."),
            ("Who controls it", "Owned and operated by OXY (Occidental Permian)."),
        ],
        "jv": "Proof that OXY can permanently and verifiably store CO₂ at massive scale — the credibility behind any “carbon-managed” power offering. It holds the U.S.'s first-ever government-approved CO₂ storage-monitoring plan.",
        "src": "Wasson / Denver Unit — EPA GHGRP facility 1011767; EPA Subpart RR monitoring plan 1011767-1 approved 27 Dec 2015 (first ever), amended 1011767-2 (2023); 3,669,743 t net stored 2023; ~212.8 Mt cumulative; RRC field #95397, operator #617544; co-located CO₂-removal plant GHGRP 1002629, TCEQ Title V O553; Denver Unit recovery plant TCEQ O3051. Sources: EPA Envirofacts; RRC; Oil & Gas Journal EOR surveys.",
    },
    {
        "section": "midstream", "type": "gas", "status": "existing",
        "name": "Denver City CO₂ hub", "map_label": "Denver City hub",
        "county": "GAINES", "on_map": True,
        "one": "The Grand Central Station of West Texas carbon dioxide — where OXY's CO₂ supply lines meet and get routed to its oil fields.",
        "rows": [
            ("Where", "Gaines / Yoakum Counties, Texas (Denver City area)."),
            ("What it does", "Collects CO₂ from multiple long-distance pipelines and distributes it to OXY's enhanced-oil-recovery fields."),
            ("Scale", "Where pipelines carrying well over 1.5 billion cubic feet of CO₂ a day converge."),
            ("Who controls it", "A shared interconnection point; OXY is one of the main users drawing CO₂ from it."),
        ],
        "jv": "The routing node that ties OXY's owned CO₂ sources to demand. Useful context for understanding how flexibly OXY could direct captured carbon toward a new use such as a power-plus-storage campus.",
        "src": "Denver City hub — convergence of the Cortez (~1.5 Bcf/d), Bravo (382 MMcf/d) and Century lines. Sources: Kinder Morgan CO₂ operations; Oil & Gas Journal.",
    },
    {
        "section": "midstream", "type": "gas", "status": "existing",
        "name": "Western Midstream (WES) — the gas, crude & water engine", "map_label": "Western Midstream",
        "county": "REEVES", "on_map": False,
        "one": "The separately-listed pipeline company OXY controls and relies on to gather and process most of its Permian gas, oil and water.",
        "rows": [
            ("Where", "Across the Delaware Basin (West Texas + southeast New Mexico)."),
            ("What it does", "Gathers, processes and moves natural gas, crude oil and produced water for OXY and others — the physical plumbing beneath OXY's production."),
            ("Scale", "Gas-processing capacity scaling toward ~2,490 million cubic feet a day; supplied roughly 60% of WES's revenue in 2025."),
            ("Who controls it", "OXY owns about 39.5% and controls WES through the general partner. OXY has explored selling the entire stake (~$20 billion) but no sale has closed."),
        ],
        "jv": "The most flexible part of OXY's toolkit: WES could contract to gather and deliver the natural gas that fuels a behind-the-meter power plant, and handle the water, without OXY having to build anything new.",
        "src": "Western Midstream Partners (NYSE: WES) — OXY interest ~39.5% (stepped down from ~41.9% after a 3 Feb 2026 unit redemption and Delaware contract reset). Sources: WES 2025 10-K (18 Feb 2026); SEC 13D/A & 8-K (Jan–Feb 2026); Hart Energy.",
    },
    {
        "section": "midstream", "type": "gas", "status": "existing",
        "name": "WES Delaware (DBM) gas processing", "map_label": "WES DBM processing",
        "county": "REEVES", "on_map": True,
        "one": "OXY-affiliated gas-processing plants in the heart of the Delaware Basin that turn raw wellhead gas into pipeline-ready product.",
        "rows": [
            ("Where", "Culberson, Loving, Reeves and Ward Counties (TX) and Eddy/Lea (NM)."),
            ("What it does", "Removes liquids and impurities from raw natural gas so it can be sold or burned for power."),
            ("Scale", "A five-plant complex (including the Mentone and North Loving trains) totaling roughly 1,600+ million cubic feet a day and still growing."),
            ("Who controls it", "Owned by Western Midstream, which OXY controls."),
        ],
        "jv": "Physical processing capacity already sitting in the Delaware Basin — the supply side of any deal to dedicate gas to on-site power generation.",
        "src": "WES Delaware Basin Midstream (DBM): Mentone III (300 MMcf/d), North Loving I (250) / II (300, ~2027), Ramsey (~500). Sources: WES 2025 10-K; WES investor materials.",
    },
    {
        "section": "midstream", "type": "gas", "status": "planned",
        "name": "Athena gas-processing plant", "map_label": "Athena plant (2026)",
        "county": "MIDLAND", "on_map": True,
        "one": "A new processing plant being built to handle OXY's Midland-Basin gas after OXY sold the gathering lines that feed it.",
        "rows": [
            ("Where", "Midland Basin, Texas."),
            ("What it does", "Processes the natural gas OXY produces in the Midland Basin under a long-term agreement."),
            ("Scale", "300 million cubic feet a day of gas and 40,000 barrels a day of natural-gas liquids."),
            ("Who controls it", "Built and owned by Enterprise Products; OXY is a committed customer. Expected online late 2026."),
        ],
        "jv": "Confirms OXY's Midland gas has guaranteed processing capacity — relevant if a campus were sited on the Midland side rather than near Pecos.",
        "src": "Athena cryogenic plant (Enterprise Products), in-service Q4-2026. Sources: Enterprise/BusinessWire (6 Aug 2025); Oil & Gas Journal.",
    },
    {
        "section": "midstream", "type": "gas", "status": "existing",
        "name": "Bravo Dome CO₂ field & pipeline", "map_label": "Bravo Dome (NM)",
        "county": "", "on_map": False,
        "one": "OXY's own natural source of nearly-pure carbon dioxide in New Mexico, with a pipeline that carries it to the Denver City hub.",
        "rows": [
            ("Where", "Northeast New Mexico, feeding a 218-mile pipeline to Denver City, Texas."),
            ("What it does", "Produces naturally-occurring CO₂ (98–99% pure) and pipes it to OXY's Texas oil fields."),
            ("Scale", "About 300 million cubic feet a day of CO₂; the pipeline moves up to 382 million cubic feet a day."),
            ("Who controls it", "OXY operates the field and pipeline (with minority partners)."),
        ],
        "jv": "The part of OXY's CO₂ supply it actually owns (as opposed to buys). Demonstrates OXY controls carbon supply end-to-end — source, pipeline and storage.",
        "src": "Bravo Dome CO₂ Gas Unit (NM OCD facility OGRID 16696); Bravo Pipeline 218 mi · 20-in · 382 MMcf/d, in service 1984. Sources: NM OCD; Kinder Morgan 10-Ks; IPCC SRCCS.",
    },
    {
        "section": "midstream", "type": "gas", "status": "existing",
        "name": "Cortez Pipeline — OXY is a customer, not the owner", "map_label": "Cortez (KM-owned)",
        "county": "", "on_map": False,
        "one": "The largest CO₂ pipeline in the U.S. — frequently mis-attributed to OXY, but actually owned by Kinder Morgan and ExxonMobil. OXY just buys capacity on it.",
        "rows": [
            ("Where", "Southwest Colorado to Denver City, Texas (~500 miles)."),
            ("What it does", "Carries naturally-occurring CO₂ from Colorado to the West Texas oil fields."),
            ("Scale", "About 1.5 billion cubic feet a day — roughly 80% of all CO₂ used for Permian oil recovery."),
            ("Who controls it", "Kinder Morgan (~50%, operator) and ExxonMobil (~37%). OXY owns no part of it and is only a shipper."),
        ],
        "jv": "Included to correct a common error: OXY does not own this line. It matters only as a reminder to verify which CO₂ assets OXY actually controls before relying on them.",
        "src": "Cortez Pipeline Co.: Kinder Morgan ~50% / ExxonMobil ~37% / Cortez Vickers ~13%; PHMSA operator KM CO2 Co. LLC, OPID 31555. Sources: Oil & Gas Journal; Kinder Morgan CO₂.",
    },
    {
        "section": "midstream", "type": "gas", "status": "divested",
        "name": "Midland gas gathering (sold to Enterprise)", "map_label": "Midland gathering (sold)",
        "county": "", "on_map": False,
        "one": "Gathering pipelines OXY sold in 2025 to pay down debt, converting itself from owner to customer.",
        "rows": [
            ("Where", "Four Midland-Basin counties, Texas (~73,000-acre dedication)."),
            ("What it does", "Gathered raw gas from OXY's Midland wells (now feeds the Enterprise/Athena system)."),
            ("Scale", "About 200 miles of gathering lines serving 1,000+ drilling locations."),
            ("Who controls it", "Sold to Enterprise Products for $580 million in August 2025; OXY stayed on as a committed shipper."),
        ],
        "jv": "Signals OXY's current strategy — sell midstream for cash, keep the production. A partner should expect OXY to prefer contracting for services over owning new pipe.",
        "src": "Sold to Enterprise for $580M cash, debt-free; signed 6 Aug, closed 22 Aug 2025. Sources: Enterprise/BusinessWire; Rigzone.",
    },

    # ===================== WATER =====================
    {
        "section": "water", "type": "water", "status": "existing",
        "name": "South Curtis Ranch water recycling", "map_label": "S. Curtis Ranch recycle",
        "county": "MIDLAND", "on_map": True,
        "one": "OXY's flagship Midland-Basin facility for cleaning and reusing the salty water that comes up with oil, instead of using fresh water.",
        "rows": [
            ("Where", "Midland Basin, Texas."),
            ("What it does", "Treats “produced water” (the brine that surfaces with oil) so it can be reused, cutting fresh-water demand."),
            ("Scale", "Has treated and reused more than 50 million barrels of water since 2021 (the partnership behind it passed ~97 million barrels by early 2026)."),
            ("Who controls it", "OXY, in a long-running partnership with Select Water Solutions."),
        ],
        "jv": "Demonstrates OXY can move and treat large volumes of non-fresh water — the capability a water-hungry data center needs for cooling without competing for scarce drinking water.",
        "src": "South Curtis Ranch — operational since Mar 2021; >50 MM bbl reused by May 2024. Daily capacity not disclosed. Sources: Select Water Solutions releases (2024).",
    },
    {
        "section": "water", "type": "water", "status": "demonstration",
        "name": "Produced-water desalination pilot", "map_label": "WES desal pilot",
        "county": "REEVES", "on_map": True,
        "one": "A working pilot that turns oilfield brine into clean fresh water — the early-stage technology most relevant to supplying data-center cooling water.",
        "rows": [
            ("Where", "Reeves County, Texas (near Red Bluff Reservoir)."),
            ("What it does", "Desalinates produced water, producing reclaimed fresh water suitable for cooling, irrigation or discharge."),
            ("Scale", "Takes in 2,000 barrels a day and yields about 1,000 barrels a day of fresh water — ten times the size of the 2023 first pilot."),
            ("Who controls it", "Run through Western Midstream's industry joint program; started up June 2026."),
        ],
        "jv": "The clearest line of sight to a sustainable cooling-water supply. If scaled, desalinated produced water could let a campus run cooling without drawing down West Texas aquifers — a major permitting and community advantage.",
        "src": "WES “JIP 2” desalination pilot — started up 17 Jun 2026; 2,000 bbl/d in → ~1,000 bbl/d fresh. Permian produced water is hypersaline (~120,000+ mg/L). Sources: WES release (17 Jun 2026); Texas Produced Water Consortium.",
    },
    {
        "section": "water", "type": "water", "status": "planned",
        "name": "Pathfinder produced-water pipeline", "map_label": "Pathfinder PW (2027)",
        "county": "LOVING", "on_map": True,
        "one": "A large new water pipeline being built to move produced water across the Delaware Basin for reuse and disposal.",
        "rows": [
            ("Where", "Eastern Loving County, Texas."),
            ("What it does", "Moves large volumes of produced water for recycling and managed disposal."),
            ("Scale", "42 miles of 30-inch pipe carrying more than 800,000 barrels a day."),
            ("Who controls it", "Western Midstream; targeted in service 1 January 2027."),
        ],
        "jv": "Adds dedicated, high-volume water-transport capacity. Relevant to siting a campus where cooling-water supply and wastewater handling both need to scale.",
        "src": "WES Pathfinder pipeline — 42 mi · 30-in · >800 Mbbl/d; in-service 1 Jan 2027. Sources: WES investor materials.",
    },
    {
        "section": "water", "type": "water", "status": "existing",
        "name": "Aris produced-water network (via WES)", "map_label": "Aris PW network",
        "county": "", "on_map": False,
        "one": "A recently-acquired, basin-spanning water system that makes OXY's affiliate one of the biggest water handlers in the Permian.",
        "rows": [
            ("Where", "Loving, Reeves and Ward Counties (TX) and Eddy/Lea (NM)."),
            ("What it does", "Gathers, recycles and disposes of produced water across a 625,000-acre dedication."),
            ("Scale", "Handles ~1.8 million barrels a day over ~830 miles of pipe, with ~1.5 million barrels a day of recycling capacity."),
            ("Who controls it", "Western Midstream (acquired October 2025)."),
        ],
        "jv": "The scale here is the point: OXY's affiliate already operates one of the region's largest water platforms, so cooling-water and wastewater logistics for a campus would not start from scratch.",
        "src": "Aris Water Solutions acquired by WES, closed 15 Oct 2025; ~1,812 Mbbl/d handling, ~830 mi, ~1,560 Mbbl/d recycle. Sources: WES release; Hart Energy.",
    },
    {
        "section": "water", "type": "water", "status": "planned",
        "name": "TerraLithium (lithium from brine) — California-only, for now", "map_label": "TerraLithium (CA)",
        "county": "", "on_map": False,
        "one": "OXY's technology for pulling battery-grade lithium out of salty water — promising, but so far only deployed in California, not Texas.",
        "rows": [
            ("Where", "Imperial Valley, California (not the Permian)."),
            ("What it does", "Extracts lithium from brine without evaporation ponds — effectively an advanced brine-treatment process."),
            ("Scale", "Capacity and start-up date not disclosed."),
            ("Who controls it", "OXY, in a 50/50 venture with Berkshire Hathaway Energy."),
        ],
        "jv": "Included for completeness and to mark a boundary: there is no announced Texas produced-water lithium project. Treat Permian “water-to-lithium” as strategic intent, not an asset.",
        "src": "TerraLithium (wholly-owned OXY) + BHE Renewables 50/50 JV announced 25 Jun 2024; California geothermal brine only. Sources: OXY release & Reuters (Jun 2024).",
    },

    # ===================== POWER =====================
    {
        "section": "power", "type": "netpower", "status": "planned",
        "name": "NET Power — clean gas-to-power plant", "map_label": "NET Power (Ector)",
        "county": "ECTOR", "on_map": True,
        "one": "OXY's most strategically important asset for a data center: a natural-gas power plant designed to capture nearly all of its own carbon dioxide, built near Odessa.",
        "rows": [
            ("Where", "Ector County, near Odessa, Texas — on land OXY leases."),
            ("What it does", "Generates electricity from natural gas while capturing ~97% of the CO₂ automatically, using almost no water for cooling."),
            ("Scale", "The first commercial plant was re-scoped in 2026 from 300 to 80 megawatts; a proven demonstration plant has run near Houston since 2018."),
            ("Who controls it", "OXY is the largest shareholder of NET Power (~46%) and provides the site, the CO₂ handling and a power off-take."),
        ],
        "jv": "This is the template. A NET Power plant delivers firm, 24/7, low-emission power behind the meter — skipping the multi-year grid-connection queue that is the biggest schedule risk for any AI campus, with the carbon already captured. The clearest path to a co-developed, carbon-managed, gas-powered data center.",
        "src": "NET Power (NYSE: NPWR), OXY ~46.46% via OLCV. Site near Odessa (Ector Co.), lease Q1-2024. 9 Mar 2026 update: paused the 300 MW Allam-cycle design, re-scoped to 80 MW (Siemens turbines + Entropy capture); final investment decision targeted 2H-2026, operations ~2029. No named hyperscaler is yet attached to the plant — the data-center fit is the thesis, not a signed contract. Sources: NET Power Q4/YE-2025 update; POWER Magazine; E&E News.",
    },
    {
        "section": "power", "type": "power", "status": "existing",
        "name": "Goldsmith Solar", "map_label": "Goldsmith Solar 16 MW",
        "lon": -102.6337, "lat": 32.0015, "on_map": True,
        "one": "A small OXY solar farm near Odessa that powers its own oilfield operations — proof OXY builds generation to serve its own load.",
        "rows": [
            ("Where", "Ector County, Texas."),
            ("What it does", "Generates solar power used directly to run OXY's enhanced-oil-recovery equipment."),
            ("Scale", "16 megawatts, about 174,000 panels; operating since October 2019 under a 12-year power agreement."),
            ("Who controls it", "OXY is the power off-taker (third-party owned/built)."),
        ],
        "jv": "A working example of OXY arranging dedicated, behind-the-meter renewable power for its own use — the same contracting muscle a campus would need for on-site solar.",
        "src": "Goldsmith Solar — EIA plant 63388; 16.8 MW; commercial Oct 2019. Sources: OXY release (Oct 2019); EIA-860.",
    },
    {
        "section": "power", "type": "power", "status": "planned",
        "name": "STRATOS dedicated solar", "map_label": "STRATOS solar",
        "county": "ECTOR", "on_map": True,
        "one": "A large solar project contracted to power OXY's flagship carbon-capture plant near Odessa.",
        "rows": [
            ("Where", "Ector County area, Texas."),
            ("What it does", "Supplies renewable electricity to run the STRATOS direct-air-capture plant."),
            ("Scale", "Up to 500 megawatts (DC), with ~145 megawatts contracted to STRATOS."),
            ("Who controls it", "Owned/built by Origis; OXY is the power customer."),
        ],
        "jv": "Shows OXY can line up several hundred megawatts of dedicated renewable supply in the Odessa area — directly relevant to powering a co-located campus cleanly.",
        "src": "STRATOS dedicated solar (Origis Energy); ~500 MWdc, ~145 MW to STRATOS. Sources: Origis/OXY releases.",
    },
    {
        "section": "power", "type": "power", "status": "planned",
        "name": "Santa Garcias Solar", "map_label": "Santa Garcias (S. TX)",
        "county": "", "on_map": False,
        "one": "A larger OXY-linked solar project in South Texas, awaiting grid connection.",
        "rows": [
            ("Where", "Kleberg County, South Texas (off the Permian map)."),
            ("What it does", "Will supply renewable power, tied to OXY's South Texas carbon-capture ambitions."),
            ("Scale", "265 megawatts."),
            ("Who controls it", "OXY-linked; grid-interconnection agreement reached February 2026, operation slipped toward 2029."),
        ],
        "jv": "Evidence of OXY's appetite to build utility-scale renewables, though this one is far from Pecos County.",
        "src": "Santa Garcias Solar — 265 MW (Kleberg Co.); interconnection agreement Feb 2026; COD ~Jan 2029. Sources: ERCOT queue; OXY.",
    },

    # ===================== DAC / CARBON CAPTURE =====================
    {
        "section": "dac", "type": "dac", "status": "construction",
        "name": "STRATOS — direct air capture plant", "map_label": "STRATOS DAC (Ector)",
        "county": "ECTOR", "on_map": True,
        "one": "The world's largest plant designed to pull CO₂ straight out of the open air — OXY's showcase carbon-removal facility near Odessa.",
        "rows": [
            ("Where", "Ector County, near Odessa, Texas."),
            ("What it does", "Removes CO₂ directly from the atmosphere and stores it underground, generating carbon-removal credits."),
            ("Scale", "Designed for up to 500,000 tonnes of CO₂ a year; cost ~$1.3 billion; targeted online in 2026."),
            ("Who controls it", "OXY's 1PointFive subsidiary, with a ~$550 million investment from BlackRock."),
        ],
        "jv": "Gives a partner a turnkey way to offset a gas-powered campus's emissions and market it as carbon-neutral — but the credits are expensive, so treat this as a premium add-on, not a low-cost solution.",
        "src": "STRATOS — EPA Class VI storage permits issued 7 Apr 2025; up to 500,000 t/yr; ~$1.3B; BlackRock ~$550M JV. Sources: 1PointFive releases; EPA.",
    },
    {
        "section": "dac", "type": "dac", "status": "planned",
        "name": "King Ranch / South Texas carbon-storage hub", "map_label": "King Ranch hub (S. TX)",
        "county": "", "on_map": False,
        "one": "A much larger carbon-capture-and-storage hub OXY is developing in South Texas, backed by a major federal grant.",
        "rows": [
            ("Where", "Kleberg County, South Texas (off the Permian map)."),
            ("What it does", "Will capture and permanently store CO₂ at regional scale."),
            ("Scale", "Starting at 500,000 tonnes a year, with potential to reach tens of millions; up to $500 million in U.S. Department of Energy support."),
            ("Who controls it", "OXY's 1PointFive, with potential investment from ADNOC/XRG; still pre-construction."),
        ],
        "jv": "Signals OXY's long-term ambition in carbon storage, but it is far from Pecos County and years from operating — context, not a near-term lever for a Permian campus.",
        "src": "South Texas DAC hub / King Ranch (Kleberg Co.) — DOE award up to $500M (Sep 2024); RRC Kleberg Sequestration Hub. Sources: DOE; 1PointFive.",
    },
    {
        "section": "dac", "type": "dac", "status": "existing",
        "name": "1PointFive carbon-removal sales", "map_label": "CDR offtake (context)",
        "county": "", "on_map": False,
        "one": "OXY's track record selling carbon-removal credits to blue-chip buyers — evidence there is a real market for the offsets a campus could use.",
        "rows": [
            ("Where", "Corporate (buyers worldwide)."),
            ("What it does", "Sells verified carbon-removal credits from OXY's capture plants."),
            ("Scale", "Includes a 500,000-tonne deal with Microsoft (2024), 250,000 with Amazon, 400,000 with Airbus, plus JPMorgan, ANA and others."),
            ("Who controls it", "OXY's 1PointFive."),
        ],
        "jv": "Shows hyperscalers (notably Microsoft and Amazon) already buy OXY's carbon removal — a natural commercial bridge to the same companies as data-center tenants.",
        "src": "Verified 1PointFive carbon-removal offtake: Microsoft 500k t (Jul 2024); Amazon 250k (Sep 2023); Airbus 400k (Mar 2022); plus JPMorgan, ANA, TD, BCG and others. “Net-zero oil” deals (e.g. SK) excluded. Sources: 1PointFive releases.",
    },
]
