"""Rebuild the OXY report with ONE DEEP PROFILE PER ASSET for sections 4-7.

Post-processor: regenerates the v2 base (keeps the financials/Berkshire/map/team/
caveats sections), then swaps the region between the <!-- 4 MIDSTREAM --> and
<!-- 8 TEAM --> markers with per-asset profiles, and injects asset CSS.

Run: python3 scripts/build_oxy_report_v3.py   (writes HTML; render PDF separately)
"""
import subprocess, re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RPT = os.path.join(ROOT, "outputs", "reports")
V2 = os.path.join(ROOT, "scripts", "build_oxy_report_v2.py")
SRCHTML = os.path.join(RPT, "oxy-intelligence-report.html")
OUT = os.path.join(RPT, "oxy-intelligence-report.html")  # overwrite in place

subprocess.run(["python3", V2], check=True)
html = open(SRCHTML, encoding="utf-8").read()

def chip(s):
    s = s.upper()
    if s.startswith("EXIST"): return '<span class="tag ex">existing</span>'
    if s.startswith("PLAN") or s.startswith("PERMIT"): return '<span class="tag pl">planned</span>'
    if s.startswith("DEMO"): return '<span class="tag pl">demonstration</span>'
    return '<span class="tag dv">divested</span>'

def A(name, tag, fields, narr, src, tall=False):
    rows = "".join(f'<div class="f"><span class="fl">{k}</span><span class="fv">{v}</span></div>' for k, v in fields if v)
    cls = "asset" + (" tall" if tall else "")
    return (f'<div class="{cls}"><h3>{name} {chip(tag)}</h3>{rows}'
            f'<p class="an">{narr}</p><p class="src">Sources: {src}</p></div>')

SEC_ACCENT = {"fin":("#0f766e","#ecfdf5"),"bk":("#6d28d9","#f5f3ff"),"map":("#b45309","#fffbeb"),
              "mid":("#b91c1c","#fef2f2"),"wat":("#0369a1","#eff6ff"),"pow":("#c2410c","#fff7ed"),
              "dac":("#15803d","#f0fdf4"),"team":("#7e22ce","#faf5ff"),"cav":("#9a3412","#fef6f3")}
def keyfind(key, bullets):
    a, bg = SEC_ACCENT[key]
    lis = "".join(f"<li>{b}</li>" for b in bullets)
    return (f'<div class="keyfind" style="--kfc:{a};background:{bg};border-left-color:{a};">'
            f'<div class="kh">Key findings</div><ul>{lis}</ul></div>')

# ---------------- SECTION 4 — MIDSTREAM, PIPELINES & PROCESSING ----------------
S4 = '<div class="sec brk"><span class="secnum">SECTION 4</span><h2>Midstream, pipelines &amp; gas processing</h2>'
S4 += keyfind("mid", [
 "<b>Century (Pecos)</b> is the largest single-source industrial CO₂-capture plant in North America — 800 MMcf/d, ~8.4 Mt CO₂/yr — anchoring the Denver City CO₂ grid.",
 "<b>Cortez Pipeline is Kinder Morgan-owned</b> — OXY is a shipper, not an owner; OXY owns the parallel Bravo Dome / Bravo system.",
 "OXY sold its Midland gas gathering to Enterprise ($580M, 2025) — owner becomes shipper; the Athena plant (Q4'26) processes its gas.",
 "Western Midstream (OXY <b>~39.5%</b>, GP control) is the retained gas/crude/water engine; a full ~$20B WES exit was explored but not done."])
S4 += ('<p class="lead" style="margin-top:6pt">OXY is the Permian\'s #1 CO₂-EOR operator, and its owned midstream is built around CO₂: the Century capture complex, the Bravo source/pipeline, and the Denver City hub that feeds its EOR floods. For gas, crude and produced water OXY now works largely through a controlling ~39.5% interest in Western Midstream (WES), having sold its conventional Midland gathering to Enterprise in 2025. Each asset is profiled below.</p>')

S4 += A("Century gas/CO₂ plant", "existing",
 [("Location","Pecos Co., TX — Gardendale area, ~NW of McCamey/Fort Stockton"),
  ("Owner / op","Built &amp; gas-operated by SandRidge (2008 contract); OXY funded construction (~$1.1B) and historically owned the CO₂-handling facilities. One source reports OXY sold the plant in Jan 2022 (~$200M, Mitchell-group buyer) and now takes the captured CO₂ as offtaker — VERIFY. OXY (Occidental Permian Ltd) operates the CO₂ takeaway line, PHMSA OPID 31502"),
  ("Capacity","800 MMcf/d inlet treating (2 trains); nameplate capture 8.4 Mt CO₂/yr (Train 1 = 5.0, Train 2 = 3.4); ~450 MMcf/d CO₂ takeaway via a ~160-mi, 24-in line to Denver City"),
  ("In-service","Century I ~Sep–Nov 2010; Century II late 2012"),
  ("Throughput","Processes high-CO₂ Val Verde gas; OXY takes 100% of separated CO₂ for EOR; historically underutilized (&lt;800 kt/yr 2018–22, often one train); SandRidge keeps/sells the methane (~350 MMcf/d gross)"),
  ("Status","EXISTING"),
  ("Emissions / GHGRP","EPA GHGRP facility 1004301 (30.6104, −102.5794), Subparts C + PP + W. The plant's *reported* CO₂e is small (~6 kt/yr combustion) because under Subpart PP the separated CO₂ is logged as a supplied product, not a stack emission — so GHGRP understates the ~Mt-scale CO₂ Century actually captures"),
  ("Regulatory","EPA GHGRP 1004301; captured CO₂ routed to OXY's Subpart-RR MRV-covered EOR units (Wasson). TCEQ regulated entity RN105567218, air account / program ID 85488 (the specific NSR permit number is gated behind TCEQ Central Registry); EIA-757 plant ID not publicly exposed for this CO₂-treating site"),
  ("Role","Largest single-source industrial CO₂-capture facility in North America; the anthropogenic leg of OXY's Denver City CO₂ grid")],
 "The flagship in-county asset: a billion-dollar CO₂-capture/gas-treating complex in Pecos County (EPA GHGRP 1004301). OXY funded and long owned the CO₂ facilities; a reported 2022 plant sale shifted OXY's role toward CO₂ offtake, though OXY still operates the takeaway pipeline (OPID 31502).",
 "EPA Envirofacts GHGRP (facility 1004301); Oil &amp; Gas Journal (start-up); SandRidge release 30 Jun 2008; MIT Sequestration; energyconnects (2022 sale — single source); PHMSA (OPID 31502). ‘800 MMcf/d’ = inlet treating; ‘~450 MMcf/d’ = CO₂ takeaway.")

S4 += A("Block 31 gas plant &amp; (Devonian) CO₂-flood unit", "existing",
 [("Location","Crane Co., TX — 1501 FM 1601, ~5 mi N of Crane (~31.647°N, 102.529°W)"),
  ("Owner / op","OXY USA Inc. (RRC operator P-5 #630591); 100% Occidental. Middle-Devonian chert miscible CO₂ flood; first miscible injection 1952"),
  ("Capacity","Gas plant 41 MMcf/d inlet (~100% utilization), 550-Btu inlet (CO₂/inert-rich) — EIA-757 plant NGPP480657"),
  ("Production","~7,504 bbl oil + 733,278 Mcf gas (Feb 2026); 344 wells; ~17.0 MM bbl cumulative since 1993"),
  ("Emissions","EPA GHGRP facility 1001132 — 115,965 t CO₂e (2023); Subpart C (~91k t) + Subpart W (~25k t)"),
  ("Regulatory","CO₂ injected under Class II UIC (Texas RRC), not Class VI; TCEQ RN100223569, NSR Permit 73238 (in renewal), Title V FOP 547"),
  ("Status","EXISTING"),
  ("Role","OXY-operated CO₂-flood field + processing one county from Pecos — a fully-instrumented example of OXY's legacy Permian CO₂-EOR footprint")],
 "Previously the thinnest profile, now fully resolved through the public facility databases: EIA-757 capacity (41 MMcf/d), EPA GHGRP emissions (115,965 t CO₂e, 2023), RRC production (344 wells), and the TCEQ/UIC permit stack — a 1952-vintage Devonian CO₂ flood OXY still operates.",
 "EPA Envirofacts GHGRP (facility 1001132); EIA-757 (NGPP480657); RRC PDQ / shalexp (Block 31 Unit; OXY P-5 630591); TCEQ Permit 73238 notice (2025).")

S4 += A("Wasson field / Denver Unit CO₂-EOR &amp; CO₂-removal plant", "existing",
 [("Location","Wasson (San Andres) field — Gaines/Yoakum Cos., TX; Denver Unit ~27,000 ac"),
  ("Owner / op","Occidental Permian Ltd (RRC operator #617544); Wasson San Andres = RRC field #95397"),
  ("Capacity","CO₂ injection ~420 MMcf/d (~200 MMcf/d purchased + ~220 recycled); the world's largest CO₂-EOR project"),
  ("In-service","Tertiary CO₂ flood began 1984 on completion of the Cortez line; CO₂-removal/recompression plant ~1988"),
  ("GHGRP / MRV","EPA GHGRP facility 1011767 (Denver Unit). Subpart RR MRV plan 1011767-1 approved 27 Dec 2015 — EPA's first-ever approved CO₂-EOR MRV plan — amended 1011767-2 on 20 Jul 2023. 2023 net CO₂ sequestered 3,669,743 mt; cumulative CO₂ injected ~212.8 MMt. Co-located Wasson CO₂-removal/recompression plant = GHGRP 1002629 (~136,530 mt, 2023), TCEQ Title V O553 / RN100226687; the Denver Unit CO₂-recovery plant holds TCEQ Title V O3051 / RN102413861"),
  ("Throughput","Decades of CO₂ flood; supplied via the Denver City hub from McElmo Dome (Cortez) and Bravo Dome (Bravo)"),
  ("Status","EXISTING; the Denver Unit is the flagship of OXY's Subpart-RR MRV-covered EOR units (with South Plains, Hobbs NM and the new Brown Pelican / STRATOS hub). The Seminole San Andres Unit, GHGRP 1009861, now reports under a Hess parent — consistent with OXY's 2023 divestiture of that field"),
  ("Role","OXY's anchor EOR sink and the demand center that justifies the entire Denver City CO₂ grid")],
 "The Denver Unit (EPA GHGRP 1011767) is the reason the CO₂ network exists: ~27,000 acres of San Andres flood, ~3.67 MMt net-sequestered in 2023 and ~212.8 MMt injected cumulatively, the original 1984 destination for McElmo Dome CO₂ and holder of EPA's first-ever approved MRV plan.",
 "EPA Envirofacts GHGRP (facility 1011767, MRV plans 1011767-1 / -2; plant 1002629); EPA Wasson San Andres MRV report (2023); RRC (field #95397, operator #617544); TCEQ Central Registry (O553 / RN100226687; O3051 / RN102413861); GEM CO₂-EOR; Oil &amp; Gas Journal EOR surveys.")

S4 += A("Denver City CO₂ hub", "existing",
 [("Location","Gaines/Yoakum Cos., TX (Denver City)"),
  ("Owner / op","Hub where multiple CO₂ trunklines interconnect; OXY is a primary offtaker"),
  ("Capacity","Convergence of Cortez (~1.5 Bcf/d), Bravo (382 MMcf/d) and Century takeaway"),
  ("Status","EXISTING"),
  ("Role","The distribution nexus from which OXY draws CO₂ to its Permian EOR floods (Denver Unit, Slaughter, Cogdell, Seminole)")],
 "Not a single OXY-owned asset but the grid node that ties OXY's CO₂ supply (Cortez purchases + owned Bravo + owned Century capture) to its EOR demand.",
 "Kinder Morgan CO₂ operations; GEM; Oil &amp; Gas Journal.")

S4 += A("Bravo Dome CO₂ field", "existing",
 [("Location","Harding/Union (&amp; Quay) Cos., NE New Mexico — ~800k–1M-acre unit (NM OCD ‘Bravo Dome Carbon Dioxide Gas Unit’; facility OGRID 16696)"),
  ("Owner / op","OXY USA Inc. operator (since ~2000, ex-BP Amoco); Kinder Morgan CO₂ ~11% non-op; XTO WI not separately disclosed"),
  ("Reservoir","Tubb sandstone (~1,900–2,950 ft), Cimarron Anhydrite seal; documented sub-hydrostatic depletion"),
  ("Resource","98–99% CO₂; recoverable &gt;10 Tcf (1989 est.); Bravo Dome unit ~801 Bcf recoverable; ~626 Bcf cumulative by YE1989"),
  ("Production","~300 MMcf/d (2012); ~272 wells (1989), reported up to ~627 recently; CO₂ found 1916, commercial 1982–83"),
  ("Status","EXISTING long-life depletion asset"),
  ("Role","OXY's owned, operated natural-CO₂ supply feeding the Bravo Pipeline to Denver City — the equity counterweight to its purchased Cortez volumes")],
 "Fully resolved from NM OCD + literature: OXY operates the ~800k-acre Bravo Dome unit (Kinder Morgan ~11% non-op), a 98–99%-pure Tubb-sandstone CO₂ field producing ~300 MMcf/d into the Bravo line — the original natural-CO₂ leg of OXY's Permian EOR supply.",
 "NM OCD imaging (Bravo Dome CO₂ Gas Unit; OGRID 16696); AAPG #91004 (Broadhead 1991); Kinder Morgan 10-Ks; GEM; PNAS 2014.")

S4 += A("Bravo Pipeline (CO₂)", "existing",
 [("Location","Bravo Dome, NM → Denver City hub, TX; deliveries to Wasson (Yoakum) &amp; Slaughter (Cochran/Hockley)"),
  ("Owner / op","Operator ‘Bravo Pipeline Company’ / ‘OXY Bravo Pipeline’ (Occidental); co-owned Occidental Permian + Kinder Morgan CO₂ + XTO — split not publicly disclosed; PHMSA OPID gated (not found)"),
  ("Capacity","218 mi · 20-in · 382 MMcf/d (≈7.3 Mt CO₂/yr), delivered ~1,800–1,900 psi"),
  ("In-service","1984 (orig. BP Amoco → Occidental ~2000)"),
  ("Safety","One PHMSA incident on record: 28 Jun 2004, Levelland TX (3,608 bbl, no injuries)"),
  ("Status","EXISTING"),
  ("Role","OXY's owned CO₂ trunkline — distinct from the Kinder Morgan-controlled Cortez line")],
 "OXY's owned CO₂ trunkline (operated since ~2000), parallel to Cortez: 218 mi of 20-inch pipe at 382 MMcf/d from Bravo Dome to Denver City. The exact ownership split and PHMSA OPID are not public.",
 "Kinder Morgan CO₂; IPCC SRCCS Ch.4 (1984, 7.3 Mt); PHMSA incident 271436; GEM.")

S4 += A("Cortez Pipeline (CO₂) — OXY is a shipper, not an owner", "existing",
 [("Location","McElmo Dome (Montezuma Co., CO) &amp; Doe Canyon (Dolores Co.) → Denver City, TX — three states"),
  ("Owner / op","Cortez Pipeline Co.: Kinder Morgan ~50% (operator), ExxonMobil ~37%, Cortez Vickers ~13%. OXY owns NO equity. PHMSA operator KM CO2 Co. LLC, OPID 31555"),
  ("Capacity","~500–505 mi (1983 build spec) · 30-in · ~1.5 Bcf/d — the largest CO₂ pipeline in the U.S., ~80% of Permian-EOR CO₂"),
  ("In-service","1984"),
  ("OXY role","Downstream CO₂ buyer/shipper-customer at Denver City for its Denver Unit flood; OXY also acquired the Doe Canyon source via a 2007 BP swap"),
  ("Regulatory","CO₂ common carrier (outside FERC NGA ratemaking); McElmo Dome royalty class actions settled Sep 2001. PHMSA operator ID not retrieved"),
  ("Status","EXISTING; KM pursuing CCUS tie-ins (Red Cedar / Southern Ute) that could feed captured CO₂ into the network")],
 "A common point of confusion, corrected here: Cortez is Kinder Morgan-operated and OXY holds no equity — OXY draws McElmo Dome CO₂ off it as a customer at Denver City, while owning the parallel Bravo system. OXY-specific Cortez offtake volumes are not disclosed.",
 "Oil &amp; Gas Journal (1983 build; 2000 Shell–KM sale); Kinder Morgan CO₂; Four Corners Free Press; Shell Cortez Pipeline Co. v. Shores (Tex. App. 2004); DOE QER 2015.")

S4 += A("Midland-Basin gas gathering → Enterprise Products", "divested",
 [("Location","Four Midland-Basin counties, TX (~73,000-acre dedication; counties not named in releases)"),
  ("Owner / op","SOLD to Enterprise Products (‘Enterprise Midland Basin Midstream LLC’); OXY now a shipper"),
  ("Capacity","~200 mi gathering; &gt;1,000 drilling locations"),
  ("Transaction","$580M cash, debt-free — signed 6 Aug 2025, closed 22 Aug 2025; OXY signed a long-term G&amp;P agreement keeping its gas dedicated to Enterprise"),
  ("Status","DIVESTED"),
  ("Role","Deleveraging move (post-CrownRock): OXY converted owned gathering to a fee-based service relationship while retaining processing certainty via the new Athena plant")],
 "The clearest recent example of OXY shedding conventional midstream to cut debt while locking in long-term gas takeaway — owner becomes customer.",
 "Enterprise/BusinessWire 6 Aug 2025; Rigzone 27 Aug 2025; OGJ.")

S4 += A("Athena cryogenic gas plant (Enterprise-built; processes OXY gas)", "planned",
 [("Location","Midland Basin — TCEQ permit places it ‘NW of Garden City’ (Glasscock Co. seat); a secondary source tags Midland Co. (Newberry complex straddles the line)"),
  ("Owner / op","Enterprise Products (wholly owned; ‘Enterprise Midland Basin Midstream LLC’). OXY is a customer, not an owner"),
  ("Capacity","300 MMcf/d processing; up to 40,000 bbl/d NGL extraction. Lifts EPD Midland totals to 2.2 Bcf/d / 310,000 bbl/d NGL"),
  ("In-service","Q4 2026 (reaffirmed Q1-2026); under construction"),
  ("Cost","No standalone figure; folded into EPD growth capex ($2.2–2.5B for 2026)"),
  ("Regulatory","TCEQ Air Standard Permit No. 181847 (Project 399233), approved 14 Oct 2025"),
  ("Status","PLANNED / under construction"),
  ("Role","Processes OXY's dedicated Midland gas under the long-term agreement signed with the $580M gathering sale")],
 "The processing counterpart to the Enterprise gathering sale: OXY's associated gas flows here under a long-term deal, securing takeaway without OXY owning the plant.",
 "Enterprise/BusinessWire 6 Aug 2025; TCEQ permit (OilGasLeads, Oct 2025); EPD Q1-2026 slides 28 Apr 2026; Rigzone.")

S4 += A("Western Midstream (WES) — Delaware Basin gas G&amp;P system", "existing",
 [("Location","Culberson/Loving/Reeves/Ward Cos., TX; Eddy/Lea Cos., NM"),
  ("Owner / op","OXY owns ~39.5% of WES (38.3% LP + 2.2% GP) and controls it via its wholly-owned general partner; WES operates independently and is not consolidated"),
  ("Capacity","West Texas (Delaware) complex ~2.09 Bcf/d (YE2024) → &gt;2.75 Bcf/d after acquisitions — a 5-plant complex"),
  ("Plants","Mentone Train III 300 MMcf/d (Loving, Q4 2023); North Loving I 250 (Loving, Feb 2025) + II 300 (Q2 2027); Ramsey complex ~500 (Reeves; ex-Nuevo Midstream, 2014)"),
  ("Status","EXISTING / EXPANDING"),
  ("Ownership history","Inherited via Anadarko (2019, ~55%); cut below 50% in 2020; 19.5M units sold Aug 2024 (~$697M); 15.3M units redeemed Feb 2026 (~$610M). OXY explored a full ~$20B WES exit (JPMorgan) — not consummated"),
  ("Role","OXY's principal retained midstream engine for gas, crude and produced water in the Delaware")],
 "The single biggest nuance in OXY's midstream: it no longer owns ~half of WES. The current figure is ~39.5% total / 38.3% of common units (Feb-2026 13D/A), but OXY still controls WES through the GP. A full sale remains possible.",
 "WES FY2025 10-K (filed Feb 2026); SEC 13D/A (Jan 21 &amp; Feb 5 2026); WES Q4-2025 slides (18 Feb 2026); Reuters (Feb 2024 sale exploration).")

S4 += A("WES North Loving gas plant + Train II", "existing",
 [("Location","Loving Co., TX (Delaware Basin)"),
  ("Owner / op","Western Midstream (OXY ~39.5%)"),
  ("Capacity","North Loving I 250 MMcf/d (in service late-Feb 2025) + Train II 300 MMcf/d (targeted early Q2 2027 → ~2.5 Bcf/d base)"),
  ("Status","EXISTING (250) + PLANNED (300)"),
  ("Role","Incremental Delaware processing capacity for WES/OXY's growing Loving/Reeves gas")],
 "A concrete near-term WES expansion: 250 MMcf/d live, another 300 MMcf/d in 2027 — part of the ~$850M–$1.0B 2026 WES program funding North Loving II and Pathfinder.",
 "NGI; PB Oil &amp; Gas Magazine; WES Q1-2026 slides.")
S4 += '</div>'

# ---------------- SECTION 5 — WATER ----------------
S5 = '<div class="sec brk"><span class="secnum">SECTION 5</span><h2>Water infrastructure</h2>'
S5 += keyfind("wat", [
 "Recycling with Select Water — <b>South Curtis Ranch (Martin Co.)</b> and <b>Lost Tank (Lea Co., NM; up to 180k bbl/d)</b> each ~97 MM bbl recycled by Q1'26.",
 "WES/Aris ($2.0B EV, closed Oct 2025) made WES the #2 Permian water midstream; the OXY-anchored Pathfinder pipeline (&gt;800 Mbbl/d) lands 2027.",
 "<b>OXY is not a named partner in the WES desalination JIP</b> — its only tie is its ~40% ownership of WES.",
 "TerraLithium DLE is <b>California-only</b> (demonstration); no announced Permian produced-water lithium asset."])
S5 += ('<p class="lead" style="margin-top:6pt">The Permian produced &gt;20 MMbbl/d of water in 2024 (~3.5:1 water-to-oil), heading past 26 MMbbl/d by 2030. OXY\'s own total volume is not disclosed; its water runs through (a) a named Select Water recycling partnership and (b) Western Midstream\'s large produced-water system (incl. Aris). Seismicity-driven disposal curtailment is the structural push toward recycling and, increasingly, desalination. Each asset below.</p>')

S5 += A("South Curtis Ranch produced-water recycling facility", "existing",
 [("Location","Martin Co., TX (Midland Basin)"),
  ("Owner / op","Select Water Solutions (NYSE: WTTR) owns/operates; OXY is the anchor producer/customer (Oxy Midland Basin)"),
  ("Capacity","Facility-specific bbl/d not disclosed (Select flagship sites ‘process hundreds of thousands of bbl/d’)"),
  ("In-service","March 2021"),
  ("Throughput","&gt;50 MM bbl treated &amp; reused by May 2024 → 97 MM bbl by Q1-2026 (Select reports South Curtis Ranch and Lost Tank at 97 MM each)"),
  ("Status","EXISTING"),
  ("Role","Recycles produced water back into OXY completions to displace freshwater in the Midland Basin")],
 "OXY's flagship Midland recycling site — a direct hedge against disposal curtailment, cycling tens of millions of barrels back into frac operations. Daily capacity is undisclosed; Select confirms the Martin County location.",
 "Select Water Solutions releases 20 May 2024 &amp; 28 Apr 2026; Martin Co. confirmed in Select 12 Feb 2025 release; Hart Energy.")

S5 += A("Lost Tank produced-water recycling facility", "existing",
 [("Location","Lea Co., NM (Delaware Basin)"),
  ("Owner / op","OXY facility with Select Water Solutions"),
  ("Capacity","Up to ~180,000 bbl/d; 1.9 MM bbl storage; 13-mi pipeline to OXY's ‘Mesa Verde’ development"),
  ("In-service","2022"),
  ("Throughput","50 MM bbl recycled by Sept 2024"),
  ("Status","EXISTING"),
  ("Role","Serves OXY's northern-Delaware Mesa Verde operated area with recycled completion water")],
 "OXY's largest disclosed recycling capacity (up to 180k bbl/d), purpose-built to feed the Mesa Verde development via a dedicated 13-mile line.",
 "Select Water Solutions release Sept 2024; selectwater.com.")

S5 += A("WES produced-water desalination pilots (JIP 1 &amp; JIP 2)", "existing",
 [("Location","Reeves Co., TX (near Red Bluff Reservoir)"),
  ("Owner / op","Operated by Western Midstream; JIP partners are Chevron, ConocoPhillips, Devon &amp; ExxonMobil. OXY is NOT a named JIP sponsor — the tie is OXY's ~40% ownership of WES"),
  ("Capacity","JIP 2: 2,000 bbl/d feed → ~1,000 bbl/d reclaimed freshwater (10× JIP 1)"),
  ("In-service","JIP 2 started up 17 Jun 2026; JIP 1 ran from 2023 (24 months, 50,000+ data points)"),
  ("Technology","‘Multi-barrier / high-recovery membrane’ train (pre-treatment → desalination → post-treatment); specific vendors/TDS not disclosed"),
  ("Status","EXISTING (pilot); CEO: ‘meaningfully closer to WES's first commercial-scale facility’"),
  ("Role","The closest thing OXY has (via WES) to commercial produced-water desalination — end-uses cited include power-plant/data-center cooling, irrigation, surface discharge")],
 "OXY's exposure to Permian produced-water desalination is indirect — through its ~40% stake in WES, which runs this joint-industry pilot with four other majors. OXY is not itself a named JIP partner. The program is the bridge to a first commercial-scale desal facility.",
 "WES release 17 Jun 2026; SEC EDGAR full-text (desal/JIP appear only in WES M&amp;A exhibits, not periodic filings); WES Q1-2026 call; TxPWC 2024.")

S5 += A("WES / Aris produced-water system", "existing",
 [("Location","Lea/Eddy Cos., NM; Loving/Reeves/Ward Cos., TX"),
  ("Owner / op","Western Midstream (OXY ~39.5%), via the Aris Water Solutions acquisition"),
  ("Capacity","1,812 Mbbl/d handling; 830 mi water pipeline; 1,560 Mbbl/d recycling; 625,000 dedicated acres (+ McNeill Ranch pore space)"),
  ("Transaction","~$2.0B enterprise value ($1.5B equity); 0.625 WES units or $25.00 cash/share, cash capped $415M, ~26.6M units; announced 6 Aug 2025, closed 15 Oct 2025"),
  ("Status","EXISTING"),
  ("Throughput","Drove WES produced-water throughput to ~2,795 Mbbl/d in Q1-2026 (+140% YoY)"),
  ("Role","Makes WES (and thus OXY) the #2 Permian produced-water midstream operator, with beneficial-reuse/desal and iodine-mineral capability")],
 "The transformational water deal: a $2B bolt-on that roughly doubled WES's water platform and added desalination/beneficial-reuse expertise — OXY participates through its ~39.5% WES interest.",
 "WES releases 6 Aug &amp; 15 Oct 2025; WES FY2025 10-K; Bluefield Research; RBN Energy.")

S5 += A("WES Pathfinder produced-water pipeline", "planned",
 [("Location","Eastern Loving Co., TX (Delaware Basin)"),
  ("Owner / op","Western Midstream (OXY ~39.5%); OXY is the anchor shipper"),
  ("Capacity","42 mi · 30-in steel · &gt;800 Mbbl/d (analyst-cited expansion ceiling ~1.2 MMbbl/d); +280 Mbbl/d gathering; +220 Mbbl/d disposal via 9 new SWDs"),
  ("In-service","Sanctioned 26 Feb 2025; in-service moved to Q1 2027 (from 1 Jan 2027)"),
  ("Cost","Standalone restated to ~$300–350M (from ~$400–450M incl. gathering+SWDs); ~half of WES's 2026 capital program with North Loving II"),
  ("Anchor","OXY firm: up to 280 Mbbl/d gathering + 220 Mbbl/d disposal, on minimum-volume commitments"),
  ("Status","PLANNED / sanctioned"),
  ("Role","Moves water out of the high-pore-pressure Delaware core to underutilized shallower disposal — a seismicity-driven egress solution OXY anchors")],
 "A sanctioned, OXY-anchored water trunkline addressing the binding constraint in the Delaware: induced-seismicity limits on deep disposal. OXY's firm MVCs underwrite it.",
 "WES release 26 Feb 2025; SEC 8-K EX-99.2; East Daley Analytics 20 Mar 2025; WES Q1-2026 slides.")

S5 += A("TerraLithium direct-lithium-extraction (DLE)", "demonstration",
 [("Location","Brawley / Imperial Valley (Salton Sea), Imperial Co., CALIFORNIA — not the Permian"),
  ("Owner / op","TerraLithium = wholly-owned OXY subsidiary (DLE IP, ex-Simbol via OXY's 2022 All-American Lithium buy); JV with BHE Renewables (Berkshire Hathaway Energy)"),
  ("Capacity","Demo: ‘99%+ capture efficiency’ of LiCl from geothermal brine. Commercial-plant tonnage (t LCE/yr) NOT disclosed"),
  ("JV","Announced 4 June 2024 (NOT June 25); JV structure / equity split NOT publicly disclosed (the ‘50/50’ characterization is not in primary sources); financial terms not disclosed. Commercial plants to be built/owned/operated by BHE; tech licensed beyond Imperial Valley"),
  ("Resource","BHE operates 10 Imperial Valley geothermal plants (345 MW, 50,000 gal/min brine); DOE/LBNL estimate 4.1–18 M t LCE region-wide (‘Lithium Valley’)"),
  ("Status","DEMONSTRATION (pilot operating in Brawley); commercial plant planned, no FID/date/capacity disclosed"),
  ("Role","A brine-treatment-adjacent capability; OXY frames Permian produced-water lithium as strategic intent only — no announced Permian DLE asset")],
 "Important scope boundary: all concrete TerraLithium activity is California geothermal brine, at demonstration stage. The widely-repeated ‘50/50 JV, June 25 2024’ is wrong — it is a jointly-formed venture announced June 4 2024 with an undisclosed split.",
 "OXY release 4 Jun 2024; terralithium.com; Reuters/Mining-Technology; LBNL (Dec 2023); CA Gov. office. (Integrity note: a PDF auto-summary hallucinated quotes; only cross-corroborated wire text used.)")
S5 += '</div>'

# ---------------- SECTION 6 — POWER ----------------
S6 = '<div class="sec brk"><span class="secnum">SECTION 6</span><h2>Power generation &amp; the NET Power program</h2>'
S6 += keyfind("pow", [
 "OXY is mainly a power <b>consumer</b>; owned generation is thin — Goldsmith 16 MW operating, Santa Garcias 265 MW planned ~2029.",
 "<b>NET Power (OXY 46.46%): the Odessa flagship was re-scoped (Mar 2026) from a 300 MW Allam-cycle plant to an 80 MW Siemens + Entropy capture plant</b>; FID 2H'26, COD ~2029.",
 "The ‘CCS-on-gas for data centers’ template is real in concept but has <b>no named hyperscaler offtake</b>."])
S6 += ('<p class="lead" style="margin-top:6pt">OXY is mainly a large power consumer — CO₂-EOR compression and DAC are electricity-intensive — and builds decarbonized self-supply: solar for its own operations, plus a controlling-influence equity stake in NET Power (carbon-capture-on-gas). The OxyChem cogeneration left with the Jan-2026 sale. Each asset below.</p>')

S6 += A("Goldsmith Solar facility", "existing",
 [("Location","Ector Co., TX (near Goldsmith)"),
  ("Owner / op","Oxy Renewable Energy LLC — EIA-860 plant code 63388; ERCOT INR 19INR0184 (filed 30 Jan 2019)"),
  ("Capacity","16.8 MW nameplate; ~174,000 First Solar thin-film panels; ~120 acres"),
  ("In-service","Built 2019; initial operation Apr 2020"),
  ("Contract","Long-term PPA (OLCV / First Solar / Macquarie GIG)"),
  ("Status","EXISTING — OXY's only EIA-coded operating generator"),
  ("Role","Powers OXY EOR operations and eliminates &gt;20,000 t CO₂/yr — OXY's first owned utility-scale solar")],
 "Small but strategically symbolic: OXY's first solar farm, built to power its own Permian EOR rather than for merchant sale.",
 "OXY release (Oct 2019); EIA-860; Power Technology.")

S6 += A("Santa Garcias Solar", "planned",
 [("Location","Kleberg Co., TX (South Texas)"),
  ("Owner / op","Oxy Renewable Energy LLC (developer) — ERCOT INR 26INR0143"),
  ("Capacity","265 MW"),
  ("In-service","Interconnection agreement Feb 2026; COD slipped to ~31 Jan 2029"),
  ("Status","PLANNED (ERCOT queue)"),
  ("Role","Sited in the same county as the 1PointFive South Texas DAC hub — almost certainly the hub's clean-power source")],
 "OXY's largest renewable project — a 265 MW solar build in South Texas, co-located with the King Ranch DAC hub and very likely intended to power it.",
 "ERCOT interconnection queue; LRP map data (developer = Oxy Renewable Energy LLC).")

S6 += A("STRATOS dedicated solar — ‘Swift Air’ (Origis)", "existing",
 [("Location","Ector Co., TX"),
  ("Owner / op","Origis Energy develops &amp; owns; OXY is the OFFTAKER (not owner) — so it carries Origis, not Oxy, EIA/ERCOT IDs"),
  ("Capacity","500 MW DC across 3 phases (~145–167 MW each); ~145 MW dedicated to STRATOS"),
  ("In-service","Completed Feb 2026 (final phase)"),
  ("Status","EXISTING"),
  ("Role","Provides low-carbon power to the STRATOS DAC plant, lowering its lifecycle emissions")],
 "Dedicated renewable supply for STRATOS — but owned by Origis, with OXY only as offtaker. The 500 MW-DC ‘Swift Air’ portfolio (3 phases) finished in Feb 2026; DAC's power-intensity is why each plant is paired with contracted solar.",
 "Origis Energy (‘Swift Air’); Solar Power World (Feb 2026); PV-Tech.")

S6 += A("NET Power (NYSE: NPWR) — Allam-cycle carbon-capture-on-gas; OXY owns 46.46%", "planned",
 [("Tech","Allam-Fetvedt cycle: oxy-combustion of natural gas with a supercritical-CO₂ working fluid → ~97% inherent CO₂ capture at pipeline pressure, near-zero air emissions, air-cooled / very low water (fundamentally unlike post-combustion amine capture)"),
  ("Demo","La Porte, TX (Harris Co.) — 50 MWth; first fire 2018; first ERCOT grid sync 16 Nov 2021"),
  ("First plant","‘Project Permian’ / SN1 on an OXY-leased site near Odessa (Ector Co.): originally ~300 MWe Allam (Baker Hughes turboexpander, Air Liquide ASU, Zachry FEED); OXY provides site lease (Q1-2024), CO₂ offtake for EOR/sequestration, and power offtake"),
  ("Cost / schedule","Escalated ~$750–950M → ~$1B (Nov 2023) → $1.7–2.0B+ (2025); slipped from 2026"),
  ("2026 PIVOT","Per the YE-2025 update (~9 Mar 2026), NET Power PAUSED the 300 MW Allam design and re-scoped the same Odessa site to ~80 MW using Siemens gas turbines + Entropy post-combustion capture (PCC) — i.e. a conventional turbine with bolt-on amine capture, not the inherent-capture Allam cycle. FID targeted 2H-2026; COD ~early 2029"),
  ("Corporate","Public via Rice Acquisition Corp. II SPAC (June 2023; ~$1.5B EV). OXY (via OLCV) is the largest shareholder at 46.46% (+$250M follow-on); 8 Rivers ~22%, Constellation, Baker Hughes"),
  ("Data-center thesis","A NET Power-style plant = firm, 24/7, low-/zero-emission gas baseload with CO₂ captured for sequestration/EOR, air-cooled, behind-the-meter, fast red-state siting — the profile AI data centers seek. CAVEAT: no primary statement pairs the Odessa plant with a NAMED hyperscaler; the data-center link is the category thesis, not a signed offtake"),
  ("Status","PLANNED (re-scoped); Allam-cycle commercialization deferred, not cancelled")],
 "The centerpiece of OXY's power-plus-CCS strategy and its most-changed story: as of March 2026 the flagship Odessa plant is no longer a 300 MW Allam-cycle unit but an 80 MW Siemens+Entropy PCC plant. OXY's 46.46% stake, host site and CO₂-offtake role persist; the ‘CCS-on-gas for data centers’ template is real in concept but has no named hyperscaler contract yet.",
 "NET Power YE-2025 business update (9 Mar 2026); RONI/NPWR merger S-4 (June 2023); POWER Magazine; E&amp;E News; Energy Intelligence (46.46%).", tall=True)

S6 += A("OxyChem cogeneration (divested)", "divested",
 [("Location","Wichita, KS &amp; Taft, LA (non-Permian)"),
  ("Owner / op","Left OXY with the OxyChem sale to Berkshire Hathaway (closed 2 Jan 2026)"),
  ("Status","DIVESTED"),
  ("Role","Historical OXY cogeneration; recorded here for completeness — no longer an OXY power asset")],
 "Included only to be complete: the two OxyChem cogeneration plants transferred to Berkshire with the $9.7B chemicals sale and are no longer OXY's.",
 "OXY/Berkshire OxyChem releases (Oct 2025 / Jan 2026).")
S6 += '</div>'

# ---------------- SECTION 7 — DAC ----------------
S7 = '<div class="sec brk"><span class="secnum">SECTION 7</span><h2>Carbon capture (1PointFive) — assets &amp; economics</h2>'
S7 += keyfind("dac", [
 "<b>DAC is barely economic</b> — ~$400–600/t cost vs ≤$180/t 45Q credit; subsidy- and premium-buyer-dependent.",
 "STRATOS (Ector) is the world's largest DAC — 500k t/yr, ~$1.3B, BlackRock $550M JV, EPA Class VI permits Apr 2025; commissioning 2026.",
 "Verified 1PointFive CDR buyers led by <b>Microsoft (500k t)</b> and Amazon (250k t); SK Trading excluded (net-zero oil, not removal)."])
S7 += ('<p class="lead" style="margin-top:6pt">Right-sized: direct air capture is barely economic today — subsidy- and premium-buyer-dependent — so it is profiled but not emphasized. 1PointFive is OXY\'s wholly-owned DAC subsidiary (built on Carbon Engineering technology, acquired ~$1.1B, closed Nov 2023).</p>')

S7 += A("STRATOS DAC plant + Brown Pelican Class VI wells", "planned",
 [("Location","Ector Co., TX — Shoe Bar Ranch, ~20 mi SW of Odessa (Notrees); 65-acre plant footprint"),
  ("Owner / op","1PointFive (OXY) + BlackRock JV ($550M ≈ 40% of the ~$1.3B JV); EPC Worley; technology Carbon Engineering"),
  ("Capacity","Up to 500,000 t CO₂/yr (2×250k modules) — the world's largest DAC; ~$1.3B"),
  ("Sequestration","Brown Pelican CCS — RRC Class VI UIC Permit 55294 (Dist. 08); EPA docket EPA-R06-OW-2024-0410, wells R6-TX-135-C6-0001/-0002/-0003 (CCS1–3); Lower San Andres saline, 4,402–5,177' TVD; 8.5 Mt over 12 yr"),
  ("Permits","EPA Class VI issued 7 Apr 2025 (first-ever for a DAC project); Subpart RR MRV plan approved 15 Jul 2025; RRC primacy 16 Oct 2025"),
  ("In-service","Phase 1 final startup + Phase 2 commissioning Q2-2026 (slipped from mid-2025); ramping through 2026"),
  ("Status","PLANNED / commissioning"),
  ("Role","OXY's DAC flagship and the proof case for the 70-plant-by-2035 ambition")],
 "The world's largest DAC plant, commissioning in 2026 with the first-ever DAC Class VI permits (RRC #55294; 3 saline wells in the Lower San Andres). Per-tonne cost is undisclosed and, like all DAC, depends on 45Q + premium buyers.",
 "RRC Class VI list &amp; Oxy Brown Pelican fact sheet; EPA permit release 7 Apr 2025; EPA Subpart RR approval 15 Jul 2025; Bloomberg (BlackRock JV); OGJ/RBN (2026 ramp).")

S7 += A("South Texas DAC Hub / King Ranch", "permitted",
 [("Location","Kleberg Co., TX (King Ranch lease)"),
  ("Owner / op","1PointFive / Kleberg Sequestration Hub, LLC (OXY)"),
  ("Capacity","~106,000 leased pore-space acres; ~3 Bt estimated saline storage; first plant 500k → 1M t/yr; hub potential ~30M t/yr"),
  ("Sequestration","RRC Class VI applicant Kleberg Sequestration Hub LLC — Tracking #58220 (Dist. 04); Frio saline; 6 wells, 6,302–9,638' TVD; status ‘Pending RAD Response’ (filed 19 Nov 2024)"),
  ("Funding","DOE Regional DAC Hub award up to $500M ($50M initial, expandable to $650M; Sept 2024); ADNOC/XRG framework — up to $500M for a 500k t/yr plant (May 2025)"),
  ("Status","PERMITTING / pre-construction (Class VI pending RAD response)"),
  ("Role","OXY's multi-megatonne sequestration build-out; likely powered by the co-located 265 MW Santa Garcias solar")],
 "The hub behind OXY's DAC scale ambition — DOE- and ADNOC-backed, ~3 Bt storage, with a 6-well Frio Class VI application (RRC #58220) pending. Still pre-construction.",
 "RRC Class VI list (#58220); DOE OCED award 12 Sep 2024; OXY/XRG release (May 2025); 1PointFive.")

S7 += ('<div class="kbox"><div class="h">1PointFive DAC economics &amp; verified CDR offtake</div>'
 '<p style="font-size:8.6pt;margin-bottom:5pt">DAC costs ~$385–690/t today (WRI avg ~$490/t). 45Q pays $180/t (DAC+saline), $130/t (DAC+EOR), $85/t (point-source). Voluntary durable-CDR runs ~$200–350/t. The ~$220–420/t gap closes only by stacking 45Q with top-of-market voluntary buyers — hence "barely economic." Verified 1PointFive CDR buyers: '
 '<b>Microsoft 500,000 t</b> (Jul 2024), <b>Amazon 250,000 t</b> (Sep 2023), <b>Airbus 400,000 t</b> (Mar 2022), JPMorganChase 50,000 t (Jun 2025), All Nippon Airways 30,000 t, TD 27,500 t, BCG 21,000 t, Palo Alto Networks 10,000 t, Bain 9,000 t, plus AT&amp;T · Trafigura · Astros · NYK (undisclosed). '
 '<b>SK Trading is excluded</b> — it is a "net-zero oil" deal, not carbon removal.</p>'
 '<p class="src">Sources: 1PointFive releases; WRI/IEA DAC cost estimates; World Oil (Microsoft).</p></div>')
S7 += '</div>'

PERASSET = S4 + S5 + S6 + S7

# asset CSS
ASSET_CSS = """
.asset{border:.8pt solid var(--rule);border-radius:5pt;padding:8pt 11pt;margin:7pt 0;break-inside:avoid;background:#fcfdfe;}
.asset.tall{break-inside:auto;}
.asset h3{margin:0 0 5pt;font-size:11.3pt;line-height:1.18;}
.asset .f{display:flex;gap:8pt;margin-bottom:1.6pt;}
.asset .fl{flex:none;width:64pt;font-size:6.6pt;font-weight:800;text-transform:uppercase;letter-spacing:.3pt;color:#6b7a89;padding-top:1.4pt;line-height:1.2;}
.asset .fv{flex:1;font-size:8.5pt;line-height:1.34;}
.asset .an{font-size:8.6pt;line-height:1.42;margin:5pt 0 3pt;color:#27323d;}
.asset .src{font-size:6.8pt;color:var(--faint);margin:0;line-height:1.3;}
.keyfind{border-left:4pt solid #b91c1c;border-radius:0 6pt 6pt 0;padding:8pt 13pt 7pt;margin:7pt 0 11pt;break-inside:avoid;}
.keyfind .kh{font-size:7.3pt;font-weight:900;letter-spacing:1.7pt;text-transform:uppercase;color:var(--kfc,#b91c1c);margin-bottom:4pt;}
.keyfind ul{margin:0;list-style:none;}
.keyfind li{position:relative;padding-left:12pt;margin-bottom:2.8pt;font-size:8.5pt;line-height:1.36;color:#27323d;}
.keyfind li:before{content:"▸";position:absolute;left:1pt;top:.2pt;color:var(--kfc,#b91c1c);font-size:7.5pt;}
.keyfind li b{color:#0d1620;font-weight:700;}
"""

# inject CSS + swap sections
html = html.replace(".two{display:flex;gap:12pt;}", ".two{display:flex;gap:12pt;}\n" + ASSET_CSS, 1)
html = re.sub(r"<!-- 4 MIDSTREAM -->.*?<!-- 8 TEAM -->",
              "<!-- 4 MIDSTREAM -->\n" + PERASSET + "\n<!-- 8 TEAM -->", html, flags=re.S)
# correct the WES figure retained in the §9 caveats
html = html.replace("~41.9% (YE-2025), not", "~39.5% (Feb-2026), not").replace("is 41.9% not", "is ~39.5% not")

# Key Findings boxes for the kept v2 sections (1, 2, 3, 8, 9)
for h2, key, bullets in [
 ('<h2>OXY at a glance — financials</h2>', "fin", [
   "Net debt roughly halved — ~$24.0B (FY24) → <b>~$11.9B (Q1'26)</b>; principal debt $13.3B, target $10B.",
   "FY2025 operating cash flow $10.5B, free cash flow $4.1B; <b>FY2026 capex guided $5.5–5.9B</b>.",
   "Fitch upgraded OXY to BBB (investment grade), Feb 2026; OxyChem sold to Berkshire ($9.7B) → three segments."]),
 ('<h2>The Berkshire Hathaway financing relationship</h2>', "bk", [
   "$10B 8% preferred: <b>only ~$1.5B redeemed</b> (all 2023); ~$8.5B remains (~$680M/yr); redemption deferred to <b>Aug 2029</b>.",
   "Berkshire holds 83.86M warrants at $59.624 (unexercised) + ~27% common; FERC-cleared to acquire up to 50%.",
   "Buffett (2023 letter): ‘no interest in purchasing or managing Occidental’; calls DAC economics ‘yet to be proven’."]),
 ('<h2>OXY infrastructure map — Permian / West Texas</h2>', "map", [
   "13 OXY/affiliated assets plotted on real Permian county geography over the regional pipeline grid.",
   "Off-map OXY assets: Santa Garcias solar &amp; King Ranch DAC hub (S. Texas), Bravo Dome (NE NM), Lost Tank (Lea NM), TerraLithium (CA)."]),
 ('<h2>Key personnel — profiles</h2>', "team", [
   "All three contacts are Land/commercial: <b>Woest</b> (Surface Land), <b>Cranfill</b> (BD — US Onshore &amp; Carbon Mgmt, UT Austin), <b>Noto</b> (Land Team Lead, ex-OLCV).",
   "Public-source only; LinkedIn/ZoomInfo block automated access, so credentials/timelines are flagged, not fabricated."]),
 ('<h2>Caveats, data gaps &amp; verification flags</h2>', "cav", [
   "Superseded figures: NET Power Odessa is <b>80 MW</b> (not 300 MW Allam); WES stake <b>~39.5%</b> (not 49%); Cortez is not an OXY asset.",
   "TerraLithium is California-only; DAC is barely economic; the $10B Berkshire preferred is largely un-redeemed.",
   "Several figures are genuinely not disclosed (flagged in-text); EPA/EDGAR blocked automated fetch — confirm against primary filings."]),
]:
    html = html.replace(h2, h2 + keyfind(key, bullets), 1)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("wrote", OUT, "·", len(html), "bytes ·", PERASSET.count('class="asset'), "asset profiles")
