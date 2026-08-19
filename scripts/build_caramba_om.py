#!/usr/bin/env python3
"""Build the Caramba North post-NDA Offering Memorandum.

Every figure is derived at build time by scripts/caramba_om_data.py from the
repo's canonical layer data; map exhibits come from
scripts/capture_om_exhibits.py. Rendering is HTML -> headless Chromium print.

    python3 scripts/build_caramba_om.py
    python3 scripts/build_caramba_om.py --html-only --out /tmp/om.html
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import caramba_om_data as D  # noqa: E402

EXHIBIT_DIR = REPO / "outputs" / "reports" / "om_exhibits"
CHROME_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
    "/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome",
]

E = html.escape


def fmt(n, unit=""):
    if n is None:
        return "—"
    if isinstance(n, float):
        n = round(n)
    return f"{n:,}{unit}"


def gw(mw):
    return f"{mw / 1000.0:.1f} GW" if mw and mw >= 1000 else f"{fmt(mw)} MW"


def img_data_uri(path: Path):
    if not path.exists():
        alt = path.with_suffix(".jpg" if path.suffix.lower() == ".png" else ".png")
        if not alt.exists():
            return None
        path = alt
    mime = "image/jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


# --------------------------------------------------------------------------
CSS = """
@page { size: letter portrait; margin: 0.72in 0.78in 0.62in; }
@page exhibit { size: letter landscape; margin: 0.42in 0.45in; }
* { box-sizing: border-box; }
body { font-family: Helvetica, Arial, sans-serif; font-size: 9.6pt; line-height: 1.44;
       color: #16202e; margin: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
h1, h2, h3, h4 { margin: 0; font-weight: 700; }
.page { page-break-after: always; }
.page:last-child { page-break-after: auto; }
.exhibit-page { page: exhibit; page-break-after: always; }

.eyebrow { font-size: 7.6pt; font-weight: 700; letter-spacing: .19em; text-transform: uppercase;
           color: #b91c1c; margin-bottom: 7px; }
.eyebrow.muted { color: #64748b; }
h2.sec { font-size: 16.5pt; line-height: 1.22; color: #0f1b2d; margin-bottom: 12px; letter-spacing: -.01em; }
.lede { border-left: 3px solid #b91c1c; padding: 2px 0 2px 14px; margin: 0 0 16px;
        font-size: 10.2pt; line-height: 1.55; color: #24354c; }
h3.sub { font-size: 10.4pt; margin: 20px 0 8px; color: #0f1b2d; }
p { margin: 0 0 9px; }
sup { font-size: 6.6pt; color: #b91c1c; font-weight: 700; }

table { width: 100%; border-collapse: collapse; margin: 8px 0 14px; font-size: 8.9pt; }
th { text-align: left; font-size: 7.4pt; letter-spacing: .11em; text-transform: uppercase;
     color: #475569; background: #f1f5f9; padding: 6px 9px; border-bottom: 1px solid #cbd5e1;
     font-weight: 700; }
td { padding: 6px 9px; border-bottom: 1px solid #e2e8f0; vertical-align: top; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
tr.total td { font-weight: 700; background: #fef2f2; border-bottom: 1px solid #fecaca; }
.note { font-size: 7.8pt; color: #64748b; line-height: 1.45; margin: -6px 0 14px; }

.stats { display: flex; gap: 0; border-top: 1.5px solid #16202e; border-bottom: 1.5px solid #16202e;
         margin: 16px 0 18px; }
.stats div { flex: 1; padding: 11px 10px 12px; border-right: 1px solid #e2e8f0; }
.stats div:last-child { border-right: 0; }
.stats .v { font-size: 14pt; font-weight: 700; color: #0f1b2d; line-height: 1.1;
            white-space: nowrap; }
.stats .k { font-size: 6.5pt; letter-spacing: .1em; text-transform: uppercase; color: #64748b;
            margin-top: 5px; line-height: 1.3; }

.cover { padding-top: 1.1in; }
.cover .rule { height: 7px; background: #0f1b2d; margin-bottom: 26px; }
.cover h1 { font-size: 44pt; line-height: 1.02; letter-spacing: -.025em; color: #0f1b2d; }
.cover .tag { font-size: 13pt; color: #24354c; margin-top: 16px; line-height: 1.35; }
.cover .geo { font-size: 8.4pt; letter-spacing: .16em; text-transform: uppercase; color: #475569;
              margin-top: 12px; }
.cover { display: flex; flex-direction: column; height: 9.16in; }
.cover .spacer { flex: 1 1 auto; }
.cover .foot { display: flex; justify-content: space-between; gap: 24px; font-size: 8pt;
               color: #475569; border-top: 1px solid #cbd5e1; padding-top: 8px; }

.toc a, .toc { text-decoration: none; color: inherit; }
.toc .row { display: flex; gap: 14px; align-items: baseline; padding: 7px 0;
            border-bottom: 1px solid #e2e8f0; }
.toc .n { flex: 0 0 26px; font-weight: 700; color: #b91c1c; font-size: 8.4pt; }
.toc .t { font-weight: 700; font-size: 10pt; color: #0f1b2d; }
.toc .row.appx .n, .toc .row.appx .t { color: #64748b; font-weight: 400; }
.toc .row.appx .n { font-weight: 700; }

.exhibit-page { display: flex; flex-direction: column; height: 7.62in; overflow: hidden; }
.exhibit-page .plate { flex: 0 1 auto; min-height: 0; border: 1px solid #cbd5e1;
                       background-repeat: no-repeat; background-position: center center;
                       background-size: cover; width: 100%; }
.exhibit-page .cap { font-size: 8.2pt; color: #475569; margin: 4px 0 8px; line-height: 1.4; }
.exhibit-page h2 { font-size: 14pt; color: #0f1b2d; margin-bottom: 3px; }
.takeaway { border-left: 3px solid #b91c1c; padding: 5px 0 5px 12px; margin-top: 9px;
            font-size: 8.6pt; line-height: 1.45; color: #24354c; }

.bars .bar { display: flex; align-items: center; gap: 9px; margin: 4px 0; font-size: 8.6pt; }
.bars .lab { flex: 0 0 118px; text-align: right; color: #24354c; }
.bars .track { flex: 1; background: #f1f5f9; height: 13px; position: relative; }
.bars .fill { background: #b91c1c; height: 100%; }
.bars .fill.alt { background: #94a3b8; }
.bars .val { flex: 0 0 96px; font-size: 8.2pt; color: #475569; font-variant-numeric: tabular-nums; }

.cols { column-count: 2; column-gap: 26px; }
.duo { display: flex; gap: 22px; align-items: flex-start; }
.duo > div { flex: 1; min-width: 0; }
.keep { break-inside: avoid; page-break-inside: avoid; }
.mini { font-size: 8.6pt; }
.mini .grp { break-inside: avoid; page-break-inside: avoid; }
.mini .h { font-size: 7.4pt; letter-spacing: .11em; text-transform: uppercase; color: #b91c1c;
           font-weight: 700; margin: 0 0 6px; }
.mini .grp + .grp { margin-top: 13px; }
.mini .row { display: flex; justify-content: space-between; gap: 10px; padding: 3.5px 0;
             border-bottom: 1px solid #eef2f7; }
.mini .row .mw { color: #475569; font-variant-numeric: tabular-nums; white-space: nowrap; }

.bottomline { border: 1.5px solid #b91c1c; background: #fef7f7; padding: 16px 18px; margin-top: 20px; }
.bottomline .k { font-size: 7.4pt; letter-spacing: .16em; text-transform: uppercase; color: #b91c1c;
                 font-weight: 700; margin-bottom: 8px; }
.bottomline p { font-size: 11pt; line-height: 1.42; color: #0f1b2d; font-weight: 700; margin: 0 0 8px; }
.bottomline .src { font-size: 7.8pt; color: #64748b; font-weight: 400; line-height: 1.45; margin: 0; }

.notice { font-size: 7.9pt; line-height: 1.5; color: #24354c; text-align: justify; }
.flag { background: #fffbeb; border: 1px solid #fcd34d; padding: 9px 12px; font-size: 8.3pt;
        color: #78350f; margin: 10px 0 14px; line-height: 1.45; }
"""


# --------------------------------------------------------------------------
def render(m, exhibits, stamp, include_flags):
    s4, s9, s3, s7 = m["section4"], m["section9"], m["section3"], m["section7"]
    C = m["config"]
    ex = {e["id"]: e for e in exhibits}
    out = []
    w = out.append

    def exhibit(eid):
        e = ex.get(eid)
        if not e:
            return
        uri = img_data_uri(EXHIBIT_DIR / e["file"])
        if not uri:
            return
        ar = e.get("aspect") or "16/9"
        w(f'''<section class="exhibit-page">
  <div class="eyebrow">{E(e["eyebrow"])}</div>
  <h2>{E(e["title"])}</h2>
  <div class="cap">{E(e["subtitle"])}</div>
  <div class="plate" style="background-image:url({uri});aspect-ratio:{ar}"></div>
  <div class="takeaway"><b>Takeaway —</b> {E(e["takeaway"])}</div>
</section>''')

    # ---------------- cover
    q = s4["pecos_queue_total_mw"]
    w(f'''<section class="page cover">
  <div class="rule"></div>
  <div class="eyebrow">Strictly Confidential · Offering Memorandum · Post-NDA</div>
  <h1>CARAMBA<br>NORTH</h1>
  <div class="tag">Up to {C["acres_max"]:,} contiguous acres of powered land on the ERCOT 765&nbsp;kV backbone</div>
  <div class="geo">Pecos County, Texas · Far West ERCOT · Permian Basin · I-10 Corridor</div>
  <div class="stats">
    <div><div class="v">{C["acres_max"]:,}</div><div class="k">Contiguous acres (up to)</div></div>
    <div><div class="v">{C["water_af_yr"]:,}</div><div class="k">AF/yr permitted water rights</div></div>
    <div><div class="v">{C["solstice_miles"]} mi</div><div class="k">To 765 kV Solstice substation</div></div>
    <div><div class="v">{C["waha_miles"]} mi</div><div class="k">To Waha natural gas hub</div></div>
    <div><div class="v">{gw(q)}</div><div class="k">ERCOT queue, Pecos Co.</div></div>
    <div><div class="v">{s9["new_drilling"]["bands"]["≤ 5 mi"]["count"]}</div>
         <div class="k">New-drill wells within 5 mi since 2020</div></div>
  </div>
  <div class="spacer"></div>
  <div class="foot">
    <div>Prepared by Land Resource Partners · Interactive diligence platform: lrp-tx-gis.netlify.app</div>
    <div>{stamp} · Data compendium for the buyer data room</div>
  </div>
</section>''')

    # ---------------- TOC
    toc = [("01", "Executive Summary"), ("02", "The Property"),
           ("03", "Transmission — the 765 kV Grid Anchor &amp; Planned Upgrades"),
           ("04", "Regional Power Cluster — Operating Fleet &amp; ERCOT Queue, Named Projects"),
           ("05", "Water Rights at Institutional Scale"), ("06", "Waha-Basis Natural Gas"),
           ("07", "Regional Data Center Pipeline"), ("08", "The Diligence Platform"),
           ("09", "Subsurface &amp; Drilling Activity — the Vibration Record")]
    appx = [("A.1", "GIS Platform — Access &amp; Navigation"),
            ("A.2", "Footnotes, References &amp; Sources"), ("A.3", "Important Notices")]
    rows = "".join(f'<div class="row"><div class="n">{n}</div><div class="t">{t}</div></div>'
                   for n, t in toc)
    rows += "".join(f'<div class="row appx"><div class="n">{n}</div><div class="t">{t}</div></div>'
                    for n, t in appx)
    w(f'''<section class="page toc">
  <div class="eyebrow muted">Contents</div>
  <h2 class="sec">Table of Contents</h2>
  {rows}
</section>''')

    # ---------------- 01 executive summary
    nd10 = s9["new_drilling"]["bands"]["≤ 10 mi"]
    pillars = [
        ("Structural power cost",
         "Waha-basis natural gas at a structural discount to Henry Hub, with recurring negative "
         "prints in 2024–2025 as Matterhorn, Blackcomb, Hugh Brinson, and GCX expansions rebalance "
         "basin egress.<sup>A.2</sup>"),
        ("765 kV transmission anchor",
         f"AEP Solstice Substation {C['solstice_miles']} miles north — the western terminus of the "
         "three PUCT-approved 765 kV Permian import paths under the Permian Basin Reliability "
         "Plan.<sup>1,2,3</sup>"),
        ("Water rights at institutional scale",
         f"{C['water_af_yr']:,} AF/yr (~{C['water_mgd']} MGD) permitted on adjacent affiliated lands "
         "— nearly two-thirds of total Middle Pecos GCD rights — from the Edwards-Trinity (Plateau) "
         "aquifer, whose recharge record held through the 1950s drought of record.<sup>10</sup>"),
        ("Demand already on the ground",
         f"{fmt(s4['pecos_queue_total_mw'])} MW in the ERCOT queue in Pecos County across "
         f"{s4['pecos_queue_projects']} projects; Pecos and adjacent counties host "
         f"{s7['local_gw']} GW of announced hyperscale and large-load capacity within {s7['local_radius_mi']} miles.<sup>7,8</sup>"),
        ("As-of-right development",
         "Unincorporated Pecos County has no zoning ordinance — no use districts, density limits, "
         "height restrictions, or setbacks. Industrial and energy uses are permitted as of right "
         "with no discretionary land-use review."),
    ]
    prows = "".join(
        f'<tr><td class="num">{i+1}</td><td><b>{t}</b></td><td>{b}</td></tr>'
        for i, (t, b) in enumerate(pillars))
    w(f'''<section class="page">
  <div class="eyebrow">01 · Executive Summary</div>
  <h2 class="sec">A powered-land site at the intersection of transmission, water, gas, and proven hyperscale demand</h2>
  <div class="lede">Caramba North is an up-to-{C["acres_max"]:,}-acre contiguous site on the north side of
    Interstate 10 in Pecos County, Texas — the Far West weather zone of ERCOT, the highest-growth
    large-load pocket in North America. The site combines a 765 kV transmission anchor
    {C["solstice_miles"]} miles north, permitted groundwater at institutional scale on adjacent
    affiliated lands, Waha-basis natural gas {C["waha_miles"]} miles away, and a surrounding project
    pipeline of more than {s7["total_gw"]} GW of announced data-center and large-load capacity. Its
    subsurface record is unusually clean: no new-drill well lies within five miles, and no new-drill
    hydraulic-fracturing job has ever been filed within two miles.</div>
  <h3 class="sub">Five pillars of the opportunity</h3>
  <table><thead><tr><th class="num">#</th><th>Pillar</th><th>Substance</th></tr></thead>
    <tbody>{prows}</tbody></table>
  <h3 class="sub">What this document is</h3>
  <p>This Memorandum is the post-NDA data compendium for the Caramba North data room. Each section
    opens with the conclusion the data supports, followed by the data itself — including named-project
    detail for the operating fleet and interconnection queue (Section 4) and the full drilling-activity
    study of the tract and its ten-mile radius (Section 9). Every figure derives from the public
    sources registered in Appendix A.2 or from counterparty-supplied indicative terms identified as
    such, and every mapped feature is independently verifiable on the companion GIS platform
    (Section 8, Appendix A.1). Map exhibits are captured directly from that platform.</p>
</section>''')

    # ---------------- 02 the property
    w(f'''<section class="page">
  <div class="eyebrow">02 · The Property</div>
  <h2 class="sec">Contiguous interstate-frontage acreage with rail, fiber, and municipal services within five miles</h2>
  <div class="lede">The Property comprises up to {C["acres_max"]:,} contiguous acres on the north side of
    Interstate 10, approximately five miles west of Fort Stockton (tract centroid
    {m["tract_centroid"]["lat"]}° N, {abs(m["tract_centroid"]["lon"])}° W). It carries direct interstate
    frontage, proximity to the Union Pacific Sunset Route rail line, and long-haul fiber along the I-10
    corridor. Fort Stockton provides municipal services and a regional airport within approximately five
    miles. The Property is offered to accommodate a range of institutional counterparty structures —
    hyperscale data-center development, large-load industrial siting, or combined-cycle generation with
    co-located storage and renewables.</div>
  <h3 class="sub">Site fundamentals</h3>
  <table><thead><tr><th>Attribute</th><th>Detail</th></tr></thead><tbody>
    <tr><td>Size / configuration</td><td>Up to {C["acres_max"]:,} contiguous acres, north side of I-10</td></tr>
    <tr><td>Access</td><td>Direct interstate frontage; Union Pacific Sunset Route proximate; long-haul fiber along the I-10 corridor</td></tr>
    <tr><td>Municipal services</td><td>Fort Stockton (~5 mi): municipal services, regional airport</td></tr>
    <tr><td>Land-use regime</td><td>Unincorporated Pecos County — no zoning ordinance; industrial and energy uses as of right; no discretionary land-use review</td></tr>
    <tr><td>Groundwater regulation</td><td>Middle Pecos Groundwater Conservation District (see Section 5)</td></tr>
    <tr><td>ERCOT position</td><td>Far West weather zone — highest-growth large-load pocket in ERCOT<sup>4</sup></td></tr>
  </tbody></table>
</section>''')
    exhibit("2.1")

    # ---------------- 03 transmission
    subs = ", ".join(f"{s['name'].replace(' Substation','')} ({s['miles']} mi)"
                     for s in s3["local_substations"][:4])
    w(f'''<section class="page">
  <div class="eyebrow">03 · Transmission</div>
  <h2 class="sec">Fifteen miles from the western terminus of ERCOT's 765 kV import backbone — inside an active grid-upgrade corridor</h2>
  <div class="lede">AEP's Solstice Substation, {C["solstice_miles"]} miles north of the Property, is the
    western terminus of the three PUCT-approved 765 kV Permian import paths — the largest transmission
    program in ERCOT history, approved April 24, 2025 under the Permian Basin Reliability Plan. Multiple
    138 kV substations sit within seven miles of the site, and ERCOT's Transmission Project Information
    Tracking (TPIT) shows a dense program of planned line and substation upgrades across Pecos County and
    its neighbors. The Property is positioned to interconnect into a grid pocket that regulators have
    already committed to reinforcing at extra-high voltage.<sup>1,2,3</sup></div>
  <table><thead><tr><th>Element</th><th>Detail</th></tr></thead><tbody>
    <tr><td>765 kV PUCT approval</td><td>Three import paths approved April 24, 2025 (Permian Basin Reliability Plan, Project No. 55718)<sup>1</sup></td></tr>
    <tr><td>Solstice Substation</td><td>AEP / CPS Energy; western terminus of the three 765 kV paths; {C["solstice_miles"]} mi north of the Property</td></tr>
    <tr><td>Howard–Solstice line</td><td>~300–370 miles to San Antonio; AEP / CPS Energy; CCN routing in progress (PUCT Docket 59366)<sup>2</sup></td></tr>
    <tr><td>Local substations</td><td>{E(subs)}</td></tr>
    <tr><td>Planned upgrades (TPIT)</td><td>{s3["tpit_substation_upgrades"]} planned substation upgrades and {s3["tpit_line_projects"]} planned transmission projects tracked ERCOT-wide, refreshed monthly; the regional concentration is shown in Exhibit 3.1</td></tr>
    <tr><td>Planning basis</td><td>ERCOT Permian Basin Reliability Plan Study (July 2024); PBRP approved September 2024<sup>3</sup></td></tr>
  </tbody></table>
</section>''')
    exhibit("3.1")

    # ---------------- 04 regional power cluster
    def grp_rows(op, qu):
        rows = ""
        for o, qq in zip(op, qu):
            rows += (f'<tr><td>{o["tech"]}</td>'
                     f'<td class="num">{o["count"]} · {gw(o["mw"])}</td>'
                     f'<td class="num">{qq["count"]} · {gw(qq["mw"])}</td></tr>')
        return rows

    def named(group):
        blocks = ""
        for g in group:
            if not g["count"]:
                continue
            shown = [x for x in g["named"] if (x["mw"] or 0) >= 5]
            if not shown:
                blocks += (f'<div class="grp"><div class="h">{g["tech"]}</div>'
                           f'<div class="row"><span>No utility-scale {g["tech"].lower()} '
                           f'capacity recorded</span><span class="mw"></span></div></div>')
                continue
            rows = "".join(
                f'<div class="row"><span>{E(x["name"])}</span>'
                f'<span class="mw">{fmt(x["mw"])} MW</span></div>' for x in shown)
            dropped = g.get("more", 0) + (len(g["named"]) - len(shown))
            more = (f'<div class="row"><span>+{dropped} more</span><span class="mw"></span></div>'
                    if dropped else "")
            noun = "project" if g["count"] == 1 else "projects"
            blocks += (f'<div class="grp"><div class="h">{g["tech"]} · {g["count"]} {noun} · '
                       f'{gw(g["mw"])}</div>{rows}{more}</div>')
        return f'<div class="mini cols">{blocks}</div>'

    pop, pq = s4["pecos_operating"], s4["pecos_queue"]
    aop, aq = s4["adjacent_operating"], s4["adjacent_queue"]
    w(f'''<section class="page">
  <div class="eyebrow">04 · Regional Power Cluster</div>
  <h2 class="sec">Embedded in the densest renewable generation cluster in ERCOT, with {gw(s4["pecos_queue_total_mw"])} queued in Pecos County</h2>
  <div class="lede">Pecos County is the number-one solar-producing county in Texas —
    {pop[0]["count"]} operating plants totalling {gw(pop[0]["mw"])} — and the ERCOT
    generator-interconnection queue in the county totals {fmt(s4["pecos_queue_total_mw"])} MW across
    {s4["pecos_queue_projects"]} projects. Operating storage is already on the ground at the site's
    doorstep. Named-project detail for the operating fleet and the queue follows in 4.2–4.5.<sup>5,6,7</sup></div>

  <h3 class="sub">4.1 &nbsp;Operating fleet and queue, by county group</h3>
  <table>
    <thead><tr><th>Technology</th><th class="num">Pecos County — operating</th><th class="num">Pecos County — ERCOT queue</th></tr></thead>
    <tbody>{grp_rows(pop, pq)}
      <tr class="total"><td>Total</td><td class="num">{gw(s4["pecos_operating_total_mw"])}</td><td class="num">{gw(s4["pecos_queue_total_mw"])}</td></tr></tbody>
  </table>
  <table>
    <thead><tr><th>Technology</th><th class="num">Adjacent counties — operating</th><th class="num">Adjacent counties — ERCOT queue</th></tr></thead>
    <tbody>{grp_rows(aop, aq)}
      <tr class="total"><td>Total</td><td class="num">{gw(s4["adjacent_operating_total_mw"])}</td><td class="num">{gw(s4["adjacent_queue_total_mw"])}</td></tr></tbody>
  </table>
  <div class="note">Adjacent counties: {", ".join(C["adjacent_counties"])}. Operating fleet on an
    EIA-860 plant basis; queue on an ERCOT Generator Interconnection Status Report basis, one row per
    interconnection request, grouped by project name. Sources: ERCOT GIS Report; EIA-860;
    USGS/LBNL USWTDB.<sup>6,7</sup></div>

  <h3 class="sub">Selected proximity markers</h3>
  <table><thead><tr><th>Asset</th><th class="num">Distance</th><th class="num">Capacity</th></tr></thead><tbody>
    {"".join(f'<tr><td>{E(x["name"])} ({x["kind"]})</td><td class="num">{x["miles"]} mi</td><td class="num">{fmt(x["mw"])} MW</td></tr>' for x in s4["proximity_markers"])}
  </tbody></table>
</section>

<section class="page">
  <h3 class="sub" style="margin-top:0">4.2 &nbsp;Operating fleet, Pecos County — {gw(s4["pecos_operating_total_mw"])} across {sum(g["count"] for g in pop)} plants</h3>
  {named(pop)}
</section>

<section class="page">
  <h3 class="sub" style="margin-top:0">4.3 &nbsp;ERCOT queue, Pecos County — {gw(s4["pecos_queue_total_mw"])} queued, {s4["pecos_queue_total_mw"] / max(s4["pecos_operating_total_mw"], 1):.1f}× the operating base</h3>
  {named(pq)}
</section>

<section class="page">
  <h3 class="sub" style="margin-top:0">4.4 &nbsp;Operating fleet, adjacent counties — {gw(s4["adjacent_operating_total_mw"])}</h3>
  {named(aop)}
</section>

<section class="page">
  <h3 class="sub" style="margin-top:0">4.5 &nbsp;ERCOT queue, adjacent counties — {gw(s4["adjacent_queue_total_mw"])}, skewed to storage and firm gas</h3>
  {named(aq)}
</section>''')
    exhibit("4.1")

    # ---------------- 05 water / 06 gas
    w(f'''<section class="page">
  <div class="eyebrow">05 · Water</div>
  <h2 class="sec">Permitted groundwater at a scale few competing sites can document</h2>
  <div class="lede">An affiliated party holds permits for {C["water_af_yr"]:,} acre-feet per year
    (~{C["water_mgd"]} million gallons per day) on adjacent lands — nearly two-thirds of the total
    permitted rights in the Middle Pecos Groundwater Conservation District. The source is the
    Edwards-Trinity (Plateau) aquifer, recharged from the mountains to the south, with an annual
    recharge record that held through the 1950s drought of record. The permit base is designated for
    industrial use and is sufficient for combined-cycle cooling and hyperscale data-center
    loads.<sup>10</sup></div>
  <table><thead><tr><th>Element</th><th>Detail</th></tr></thead><tbody>
    <tr><td>Permitted volume</td><td>{C["water_af_yr"]:,} AF/yr (~{C["water_mgd"]} MGD) on adjacent affiliated lands — ≈ two-thirds of total district rights</td></tr>
    <tr><td>Groundwater district</td><td>Middle Pecos GCD (MPGCD)<sup>10</sup></td></tr>
    <tr><td>Aquifer source</td><td>Edwards-Trinity (Plateau); recharge from southern mountains</td></tr>
    <tr><td>Drought resilience</td><td>Well-established annual recharge record; held through the 1950s drought of record</td></tr>
    <tr><td>Permitted use profile</td><td>Industrial; sufficient for combined-cycle cooling and hyperscale data-center loads</td></tr>
  </tbody></table>

  <div class="eyebrow" style="margin-top:26px">06 · Natural Gas</div>
  <h2 class="sec">Twenty miles from Waha, with an indicative long-term supply quote in hand</h2>
  <div class="lede">The Property sits approximately {C["waha_miles"]} miles from the Waha hub, the West
    Texas gas pricing and delivery point that has traded at a structural discount to Henry Hub —
    including recurring negative prints through 2024–2025 — as Matterhorn, Blackcomb, Hugh Brinson, and
    the GCX expansion rebalance basin takeaway. An indicative supply quote has been secured for
    {C["gas_quote_mmbtu_d"]:,} MMBtu per day on a {C["gas_quote_term_years"]}-year term at Waha-index
    pricing, with contribution-in-aid-of-construction of ${C["gas_ciac_musd"]} million and a build lead
    time of {C["gas_lead_months"]} months.</div>
  <table><thead><tr><th>Element</th><th>Detail</th></tr></thead><tbody>
    <tr><td>Indicative supply quote</td><td>{C["gas_quote_mmbtu_d"]:,} MMBtu/day · {C["gas_quote_term_years"]}-year term · Waha-index pricing (counterparty-supplied indicative terms)</td></tr>
    <tr><td>CIAC / lead time</td><td>${C["gas_ciac_musd"]} million; {C["gas_lead_months"]} months from counterparty</td></tr>
    <tr><td>Basis dynamic</td><td>Structural discount vs. Henry Hub; recurring negative prints 2024–2025</td></tr>
    <tr><td>Takeaway expansion</td><td>Matterhorn in service; Blackcomb, Hugh Brinson, GCX expansion in the pipeline</td></tr>
  </tbody></table>
</section>''')

    # ---------------- 07 data center pipeline
    def anchor_row(a):
        prox = E(a["county"] or "—")
        if a.get("miles") is not None:
            prox += f' · ~{a["miles"]} mi'
        return (f'<tr><td><b>{E(a["name"] or "")}</b></td><td>{E(a["developer"] or "—")}</td>'
                f'<td class="num">{gw(a["capacity_mw"])}</td><td>{prox}</td>'
                f'<td>{E((a["status"] or "").title())}</td></tr>')

    local_rows = "".join(anchor_row(a) for a in s7["local"])
    other_rows = "".join(anchor_row(a) for a in s7["other"])
    other_block = ""
    if s7["other"]:
        other_gw = round((s7["total_mw"] - s7["local_mw"]) / 1000.0, 1)
        other_block = f'''
  <h3 class="sub">Elsewhere in Texas — context, not catchment</h3>
  <p>The register also tracks {len(s7["other"])} announced Texas campuses outside the regional
    catchment, totalling {other_gw} GW. They are listed for market context and are <b>not</b> included
    in the {s7["local_gw"]} GW figure above.</p>
  <table><thead><tr><th>Project</th><th>Sponsor</th><th class="num">Capacity</th><th>County · distance</th><th>Status</th></tr></thead>
    <tbody>{other_rows}</tbody></table>'''

    w(f'''<section class="page">
  <div class="eyebrow">07 · Regional Data Center Pipeline</div>
  <h2 class="sec">Announced hyperscale and large-load capacity inside {s7["local_radius_mi"]} miles totals {s7["local_gw"]} GW</h2>
  <div class="lede">Pecos and Reeves counties are emerging as the Permian Basin's gigawatt-scale AI
    computing corridor. The announced campuses within {s7["local_radius_mi"]} miles of the Property —
    sponsors including Pacifico Energy and Poolside/CoreWeave — target {s7["local_gw"]} GW between them,
    the nearest inside twenty miles. Each validates the same siting logic the Property offers: cheap
    Waha gas, big flat land, groundwater, and a reinforced grid.<sup>8,9</sup></div>
  <h3 class="sub">Announced projects within {s7["local_radius_mi"]} miles</h3>
  <table><thead><tr><th>Project</th><th>Sponsor</th><th class="num">Capacity</th><th>County · distance</th><th>Status</th></tr></thead>
    <tbody>{local_rows}</tbody></table>
  {other_block}
  <div class="note">Anchor register compiled from corporate announcements, TCEQ air permits, ERCOT queue
    entries, and county tax-abatement filings; last compiled {E(s7.get("generated") or "—")}. Distances
    are straight-line from the tract centroid. Coordinates marked approximate in the register are
    anchored to the nearest public reference where sponsors have not disclosed a location. The register
    covers announced or under-construction Texas campuses at or above roughly 100 MW; it is not a
    complete census of regional load.</div>
</section>''')

    exhibit("7.1")

    # ---------------- 08 platform
    w(f'''<section class="page">
  <div class="eyebrow">08 · The Diligence Platform</div>
  <h2 class="sec">Every figure in this Memorandum is independently verifiable, feature by feature</h2>
  <div class="lede">The data behind this Memorandum lives on a password-protected interactive GIS
    platform carrying the Property boundary, the regional generation fleet and ERCOT queue, transmission
    and planned upgrades, midstream networks, the announced campus land positions, permits and tax
    abatements, and the complete wellbore record used in Section 9. Layers refresh on
    weekly-to-monthly cadences from the primary sources registered in Appendix A.2, every feature carries
    its source citation in its popup, and map states can be shared as URLs that reproduce exact views,
    layers, and filters. The map exhibits in this Memorandum were captured directly from the platform.
    Access credentials and a navigation guide are provided in Appendix A.1.</div>
  <table><thead><tr><th>Property of the platform</th><th>Why it matters for diligence</th></tr></thead><tbody>
    <tr><td>Source-cited features</td><td>Every point, line, and boundary traces to a cited public dataset; per-feature citations in popups. Nothing is hand-placed except labeled reference toponyms; the single approximated boundary (the groundwater management zone) is disclosed as such.</td></tr>
    <tr><td>Refresh discipline</td><td>RRC wells/permits and abatements weekly; ERCOT queue and TPIT monthly; EIA/USGS/OSM annually on release.</td></tr>
    <tr><td>Analytical tooling</td><td>Field-level filters (wells by county/depth/spud year; queue by fuel/capacity/status), pre-built analytical views with exportable statistics, a time scrubber animating the drilling record by year, and measure/share/print tools.</td></tr>
    <tr><td>Reproducibility</td><td>Static, versioned build; the deployed bundle is byte-verified against the build on every release. Access is logged.</td></tr>
  </tbody></table>
</section>''')

    # ---------------- 09 subsurface
    ev, px, ndd, cmp_, pr, ff = (s9["events"], s9["proximity"], s9["new_drilling"],
                                 s9["comparison"], s9["production"], s9["fracfocus"])
    b2, b5, b10 = ndd["bands"]["≤ 2 mi"], ndd["bands"]["≤ 5 mi"], ndd["bands"]["≤ 10 mi"]
    p10 = pr["radii"]["≤ 10 mi"]
    tract_rows = "".join(
        f'<tr><td class="num">{fmt(t["depth_ft"])}</td><td class="num">{t["spud_year"]}</td>'
        f'<td>{"Plugged &amp; abandoned" if t["plugged"] else ("Active" if t["active"] else "Not plugged")}</td>'
        f'<td>{"Gas" if t["oil_gas"] == "G" else "Oil"}</td></tr>' for t in s9["tract_wellbores"])
    bd = ndd.get("rule_h_boundary_within_10mi") or []
    if include_flags and bd:
        detail = "; ".join(
            f'{b["miles"]} mi, spud {b["spud_year"]}, completion {b["completion_year"]}, '
            f'{fmt(b["depth_ft"])} ft' for b in bd)
        boundary_flag = (
            f'<div class="flag"><b>Classification note —</b> {len(bd)} wellbore(s) within ten miles '
            f'carry a completion year exactly one year before a 2020-or-later spud year ({detail}). '
            f'The locked recompletion filter excludes them from the new-drill counts above. They are '
            f'disclosed here because a reader comparing against an earlier vintage of this study will '
            f'see them counted as new drills.</div>')
    else:
        boundary_flag = ""

    peer_max = max(v["new_drill"] for v in cmp_["counties"].values()) or 1
    bars = "".join(
        f'<div class="bar"><div class="lab">{E(c)}{" (site county)" if c == "Pecos" else ""}</div>'
        f'<div class="track"><div class="fill{"" if c == "Pecos" else " alt"}" '
        f'style="width:{100.0 * v["new_drill"] / peer_max:.1f}%"></div></div>'
        f'<div class="val">{fmt(v["new_drill"])} ({v["shallow"]} shallow)</div></div>'
        for c, v in sorted(cmp_["counties"].items(), key=lambda kv: kv[1]["new_drill"]))
    ffrows = "".join(
        f'<tr><td>{band}</td><td class="num">{v["count"]}</td>'
        f'<td class="num">{v["latest"] or "— none, ever"}</td></tr>'
        for band, v in ff["bands"].items())
    w(f'''<section class="page">
  <div class="eyebrow">09 · Subsurface &amp; Drilling Activity</div>
  <h2 class="sec">No new drilling is occurring at or near the site — and the public record proves it three independent ways</h2>
  <div class="lede">This section reproduces the drilling-activity study of the tract and its ten-mile
    radius, prepared as vibration-context due diligence for data-center development. Counting only
    genuine new wells — wellbore records with recompletion re-stamps excluded — no new-drill well lies
    within five miles of the tract, only {b10["count"]} sit within ten miles across 2020–present, and
    the public hydraulic-fracturing disclosure record shows no new-drill frack within two miles, ever.
    The wellbore record, the production record, and the fracturing disclosure record each independently
    support the same conclusion.<sup>11,12,13</sup></div>
  <div class="stats">
    <div><div class="v">{b2["count"]}</div><div class="k">New-drill wells within 2 mi since 2020</div></div>
    <div><div class="v">{b5["count"]}</div><div class="k">New-drill wells within 5 mi since 2020</div></div>
    <div><div class="v">{b10["count"]}</div><div class="k">New-drill wells within 10 mi{f" — nearest {b10['nearest']} mi" if b10["nearest"] else ""}</div></div>
    <div><div class="v">{ff["bands"]["0 – 2 mi"]["count"]}</div><div class="k">New-drill fracks within 2 mi, ever</div></div>
    <div><div class="v">{px["shallow_spud_max"]}</div><div class="k">Most recent shallow spud within 2 mi</div></div>
    <div><div class="v">{ev["new_drill_pct"]}%</div><div class="k">Share of 2020+ Pecos wellbore events that are new drilling</div></div>
  </div>

  <h3 class="sub">9.1 &nbsp;On the tract itself: legacy completions, no modern shallow drilling</h3>
  <p>The wellbores recorded inside the tract boundary are decades-old completions. The table below is the
    complete record.</p>
  <table><thead><tr><th class="num">Depth (ft)</th><th class="num">Spud year</th><th>Status</th><th>Oil / gas</th></tr></thead>
    <tbody>{tract_rows}</tbody></table>

  <h3 class="sub">9.2 &nbsp;Pecos "drilling activity" is ~{100 - ev["new_drill_pct"]}% rework of existing wells, not new drilling</h3>
  <p>The Railroad Commission of Texas maintains a master wellbore database (dbf900) in which every
    drilling, completion, and workover event is logged against a unique API well number. Tracing every
    Pecos wellbore with any recorded activity since 2020: of {fmt(ev["total"])} wellbore-record events,
    only ≈ {ev["new_drill_pct"]}% ({ev["new_drill"]}) are genuine new drilling. The remaining
    ≈ {100 - ev["new_drill_pct"]}% ({fmt(ev["rework"])}) are recompletion or workover events on existing
    wellbores. A workover rig on an existing bore is not the drilling-and-fracturing activity associated
    with ground vibration, and the program is not near the site.<sup>11</sup></p>

</section>

<section class="page">
  <h3 class="sub" style="margin-top:0">9.3 &nbsp;Proximity: drilling near the tract ended over two decades ago</h3>
  <p>Within one mile — {px["wellbores_within_1mi"]} wellbores of any depth;
    {px["shallow_within_1mi"] or "none"} shallow (&lt; 3,000 ft). Within two miles — of
    {px["wellbores_within_2mi"]} wellbores, the {px["shallow_within_2mi"]} shallow wells were spudded
    {px["shallow_spud_min"]}–{px["shallow_spud_max"]}; most are plugged and abandoned. The nearest
    non-plugged shallow wells were spudded
    {" and ".join(f"{n['spud_year']} ({n['miles']} mi)" for n in px["nearest_nonplugged_shallow"])} —
    decades-old completions, not active drilling.</p>
</section>

  <h3 class="sub">9.4 &nbsp;New drilling since 2020, by distance and depth</h3>
  <p>Counting only genuine new wells drilled in Pecos since 2020 (recompletion re-stamps excluded), the
    activity is deep and remote. The {fmt(ndd["beyond_10mi"]["count"])} new wells beyond ten miles sit at
    a median distance of ≈ {ndd["beyond_10mi"]["median_mi"]} miles (max
    {ndd["beyond_10mi"]["max_mi"]}), and the great majority are deep — the modern Permian
    unconventional program.</p>
  <div class="duo">
    <div><table><thead><tr><th>Radius</th><th class="num">New-drill wells, spudded ≥ 2020</th></tr></thead><tbody>
      <tr><td>≤ 2 mi</td><td class="num">{b2["count"]}</td></tr>
      <tr><td>≤ 5 mi</td><td class="num">{b5["count"]}</td></tr>
      <tr><td>≤ 10 mi</td><td class="num">{b10["count"]}{f' (nearest ≈ {b10["nearest"]} mi)' if b10["nearest"] else ""}</td></tr>
      <tr><td>&gt; 10 mi</td><td class="num">{fmt(ndd["beyond_10mi"]["count"])} (median {ndd["beyond_10mi"]["median_mi"]} mi, max {ndd["beyond_10mi"]["max_mi"]} mi)</td></tr>
      <tr class="total"><td>County-wide total</td><td class="num">{fmt(ndd["county_total"])}</td></tr>
    </tbody></table></div>
    <div><table><thead><tr><th>Depth band (wells &gt; 10 mi)</th><th class="num">Wells</th><th class="num">Share</th></tr></thead><tbody>
      {"".join(f'<tr><td>{k}</td><td class="num">{v}</td><td class="num">{100.0 * v / max(sum(ndd["depth_bands"].values()), 1):.0f}%</td></tr>' for k, v in ndd["depth_bands"].items())}
    </tbody></table></div>
  </div>
  {boundary_flag}

  <h3 class="sub">9.5 &nbsp;County-wide, Pecos has a fraction of the new drilling of its peers</h3>
  <p>On the same genuine-new-drill basis, Pecos — at ≈ 4,700 square miles — has dramatically less new
    drilling than comparable Permian counties. Its {cmp_["counties"]["Pecos"]["new_drill"]} new wells
    since 2020 are a small fraction of the comparable-county average
    (≈ {fmt(cmp_["peer_average"])}). Genuine new shallow drilling is negligible in every county.<sup>11</sup></p>
  <div class="bars">{bars}</div>
  <div class="note">New-drill wells spudded since 2020 (shallow &lt; 3,000 ft in parentheses). RRC dbf900,
    genuine-new-drill basis. Howard and Loving lie outside the six-county sale-area set and are included
    only to broaden the comparison.</div>
</section>

<section class="page">
  <h3 class="sub">9.6 &nbsp;Production near the site is decades-old completions — {p10["marginal_pct"]}% marginal or end-of-life</h3>
  <p>Every well was additionally cross-referenced against the Railroad Commission's production records,
    joined by API number. A well is treated as "marginal or end-of-life" when its trailing-average output
    is at or below {fmt(C["marginal_gas_mcf_d"])} Mcf/day of gas and at or below
    {fmt(C["marginal_oil_bbl_d"])} bbl/day of oil — a strict marginal-well threshold.<sup>12</sup></p>
  <p>Of the {fmt(p10["nonplugged"])} non-plugged wellbores within ten miles of the tract,
    {fmt(p10["marginal"])} (≈ {p10["marginal_pct"]}%) are marginal or end-of-life. These are not new
    drilling: they are decades-old completions that have depleted over 30–60 years of production. The
    vintage distribution makes the point.</p>
  <table><thead><tr><th>Radius</th><th class="num">Non-plugged wellbores</th><th class="num">Marginal / end-of-life</th><th class="num">Share</th></tr></thead><tbody>
    {"".join(f'<tr><td>{k}</td><td class="num">{fmt(v["nonplugged"])}</td><td class="num">{fmt(v["marginal"])}</td><td class="num">{v["marginal_pct"]}%</td></tr>' for k, v in pr["radii"].items())}
  </tbody></table>
  <div class="bars">{"".join(f'<div class="bar"><div class="lab">{k}</div><div class="track"><div class="fill alt" style="width:{100.0 * v / max(pr["vintage"].values()):.1f}%"></div></div><div class="val">{v}</div></div>' for k, v in pr["vintage"].items())}</div>
  <div class="note">Spud-decade distribution of the non-plugged wellbores within ten miles.</div>

  <h3 class="sub">9.7 &nbsp;The public fracking record independently confirms the wellbore record</h3>
  <p>The Texas FracFocus disclosure database is the public record of every hydraulic-fracturing job filed
    in Texas since 2011. Every Pecos County disclosure ({fmt(ff["pecos_disclosures"])} in total) was
    cross-referenced against the RRC wellbore record by API number to exclude re-fracs on existing wells;
    the figures below are confirmed new-drill fracks only — a frack performed at the original completion
    of a newly drilled wellbore.<sup>13</sup></p>
  <table><thead><tr><th>Distance band from tract</th><th class="num">New-drill fracks (2011–present)</th><th class="num">Most recent</th></tr></thead>
    <tbody>{ffrows}</tbody></table>
  <p>No new-drill hydraulic-fracturing job has ever been performed within two miles of the tract. The
    broader Permian program does exist — {fmt(ff["within_20mi_total"])} new-drill fracks within twenty
    miles since 2011, dominated by the deep-horizontal unconventional players
    ({", ".join(f"{E(o)} {n}" for o, n in ff["top_operators"][:3])}) — but it is concentrated outside the
    ten-mile buffer, almost entirely at unconventional depths.</p>

  <div class="bottomline keep">
    <div class="k">Bottom line — Section 9</div>
    <p>Whether the question is framed as shallow drilling, hydraulic fracturing, or new drilling of any
      kind, three independent public records point the same way: it is not happening at or near this site.</p>
    <p class="src">Wellbore record (RRC dbf900) · production record (RRC, API-matched) · fracturing
      disclosures (FracFocus, API-cross-referenced). Method detail and thresholds are stated in-line
      above; sources in Appendix A.2.</p>
  </div>
</section>''')

    # ---------------- appendices
    footnotes = [
        ("1", "PUCT Order approving three 765 kV import paths, April 24, 2025 — Permian Basin Reliability Plan, Project No. 55718. interchange.puc.texas.gov (No. 55718)"),
        ("2", "AEP Texas / CPS Energy, Howard–Solstice Transmission Line Project; PUCT Docket 59366. interchange.puc.texas.gov (No. 59366)"),
        ("3", "ERCOT Permian Basin Reliability Plan Study, July 2024; PBRP approved September 2024. ercot.com/gridinfo/planning"),
        ("4", "ERCOT Long-Term Load Forecast. ercot.com/gridinfo/load/forecast"),
        ("5", "Apex Clean Energy disclosures, Pecos Flats project area. apexcleanenergy.com"),
        ("6", "EIA Form 860; USGS/LBNL U.S. Wind Turbine Database; project-level GIS analysis. eia.gov/electricity/data/eia860"),
        ("7", "ERCOT GIS Report of projects in the Generator Interconnection Queue. ercot.com/gridinfo/resource"),
        ("8", "TCEQ Air Permit filings; sponsor press releases, 2025–2026. tceq.texas.gov/permitting/air"),
        ("9", "ERCOT Generator Interconnection Queue entries, Longfellow cluster, Pecos County."),
        ("10", "Middle Pecos Groundwater Conservation District — permit registry and district rules. middlepecosgcd.org"),
        ("11", "Railroad Commission of Texas, dbf900 Full Wellbore ASCII master file (weekly release), genuine-new-drill basis: every event tagged to a unique API number; recompletion/workover re-stamps excluded. rrc.texas.gov"),
        ("12", "RRC production records joined by API number. Marginal threshold: ≤ 125 Mcf/d gas AND ≤ 25 bbl/d oil, trailing average. webapps.rrc.texas.gov/PDQ"),
        ("13", "FracFocus Chemical Disclosure Registry, Texas disclosures 2011–present, API-cross-referenced against the RRC wellbore record to isolate new-drill fracks. fracfocus.org"),
    ]
    register = [
        ("County / highway reference", "U.S. Census TIGER/Line 2023", "Static", "census.gov"),
        ("Rail", "BTS North American Rail Network", "Static", "geodata.bts.gov"),
        ("Plants, batteries, solar", "EIA-860 annual + generator detail", "Annual", "eia.gov"),
        ("Wind turbines", "USGS/LBNL U.S. Wind Turbine Database", "Annual", "eerscmap.usgs.gov/uswtdb"),
        ("Transmission; NG/crude/NGL pipelines; processing", "EIA U.S. Energy Atlas (HIFLD)", "Annual", "atlas.eia.gov"),
        ("Substations", "OpenStreetMap", "Annual", "openstreetmap.org"),
        ("Interconnection queue", "ERCOT GIS Report", "Monthly", "ercot.com/gridinfo/resource"),
        ("Planned grid upgrades", "ERCOT TPIT", "Monthly", "ercot.com/gridinfo/transmission"),
        ("Wellbore &amp; permit record", "RRC public datasets (dbf900, W-1)", "Weekly", "rrc.texas.gov"),
        ("Large-diameter pipelines", "RRC digital pipeline data", "Annual", "rrc.texas.gov/pipeline-safety"),
        ("Air permits", "TCEQ air permitting records", "Annual", "tceq.texas.gov/permitting/air"),
        ("Tax abatements (Ch. 381/312)", "County commissioners-court records (compiled)", "Weekly", "County clerk agendas"),
        ("Groundwater district", "Middle Pecos GCD (zone boundary approximate, disclosed)", "On publication", "middlepecosgcd.org"),
    ]
    exlist = "".join(
        f'<tr><td>Exhibit {e["id"]}</td><td>{E(e["title"])}</td><td>{E(e["captured"])}</td></tr>'
        for e in exhibits)
    w(f'''<section class="page">
  <div class="eyebrow muted">Appendix A.1</div>
  <h2 class="sec">GIS Platform — Access &amp; Navigation</h2>
  <table><thead><tr><th>Access</th><th>Detail</th></tr></thead><tbody>
    <tr><td>URL</td><td>https://lrp-tx-gis.netlify.app</td></tr>
    <tr><td>Login</td><td>Business email + access password (issued to the deal team separately)</td></tr>
    <tr><td>Notes</td><td>No installation; desktop Chrome/Edge/Safari recommended. Sessions persist per browser. Access is logged; credentials are for the deal team only.</td></tr>
  </tbody></table>
  <h3 class="sub">Layout</h3>
  <p><b>Left sidebar</b> — layer groups with individual on/off toggles and live feature counts. High-density
    layers activate as you zoom in. <b>Top bar</b> — Measure (distance/area), Reset (default view), Share
    (copies a URL capturing your exact view, layers, and filters — the standard way to circulate a specific
    exhibit), Print (landscape print/PDF). <b>Basemaps</b> — Esri World Imagery (default), Carto Light (best
    for dense layer work). <b>Popups</b> — click any feature for its attributes with source and as-of date.</p>
  <h3 class="sub">Analysis tools</h3>
  <p><b>Filters</b> — wells by county/depth/spud year; the ERCOT queue by fuel/capacity/status; permits by
    operator. <b>Views</b> — pre-built analytical views of the drilling record with exportable summary
    statistics. <b>Time scrubber</b> — animates the well record by year.</p>
  <h3 class="sub">Exhibit provenance</h3>
  <table><thead><tr><th>Exhibit</th><th>Title</th><th>Captured</th></tr></thead><tbody>{exlist}</tbody></table>
</section>

<section class="page">
  <div class="eyebrow muted">Appendix A.2</div>
  <h2 class="sec">Footnotes, References &amp; Sources</h2>
  <h3 class="sub">Numbered footnotes</h3>
  <table><thead><tr><th class="num">#</th><th>Reference</th></tr></thead><tbody>
    {"".join(f'<tr><td class="num">{n}</td><td>{t}</td></tr>' for n, t in footnotes)}
  </tbody></table>
  <h3 class="sub">General source register (GIS platform layers)</h3>
  <table><thead><tr><th>Domain</th><th>Source</th><th>Cadence</th><th>Link</th></tr></thead><tbody>
    {"".join(f'<tr><td>{d}</td><td>{s}</td><td>{c}</td><td>{l}</td></tr>' for d, s, c, l in register)}
  </tbody></table>
  <div class="note">Distances stated in this Memorandum are straight-line from the tract centroid unless
    labeled otherwise. Map exhibits were captured from the companion GIS platform on the dates shown in
    Appendix A.1. Every figure in Sections 3, 4, 7 and 9 is derived programmatically from the layer data
    at build time; the indicative gas terms in Section 6 and the permitted water volume in Section 5 are
    counterparty-supplied and identified as such. Compiled {stamp}.</div>
</section>

<section class="page">
  <div class="eyebrow muted">Appendix A.3</div>
  <h2 class="sec">Important Notices</h2>
  <div class="notice">
  <p>This Confidential Offering Memorandum (the "Memorandum") has been prepared solely for the use of a
    limited number of prospective counterparties, under executed non-disclosure agreement, in connection
    with the potential acquisition of, or investment in, the Caramba North property (the "Property"). The
    Memorandum contains proprietary data of Harvest Energy, LLC and is delivered on a strictly confidential
    basis. By accepting this Memorandum, the recipient agrees that it will not be reproduced or distributed,
    in whole or in part, to any other person, and that the information contained herein will be used solely
    for the purpose of evaluating the potential transaction described.</p>
  <p>This Memorandum does not constitute an offer to sell or a solicitation of an offer to buy any security
    or interest. Any such offer or solicitation will be made only by means of definitive transaction
    documents and in compliance with applicable law. The information contained in this Memorandum is
    preliminary and indicative, has been compiled from sources believed to be reliable, and is subject to
    revision, correction, completion, and update without notice. No representation or warranty, express or
    implied, is made as to the accuracy or completeness of any information set forth herein.</p>
  <p>Public data referenced in this Memorandum is drawn from ERCOT, the Public Utility Commission of Texas,
    the U.S. Energy Information Administration, the Texas Commission on Environmental Quality, the Railroad
    Commission of Texas, the FracFocus Chemical Disclosure Registry, the Middle Pecos Groundwater
    Conservation District, HIFLD, USGS, BTS, and U.S. Census TIGER, supplemented by project-level GIS
    analysis and counterparty-supplied indicative terms. Distances stated are straight-line from property
    boundary or centroid, as labeled. Forward-looking statements are subject to risks, uncertainties, and
    assumptions.</p>
  <p>Recipients should conduct their own independent investigation and analysis of the Property, the
    transaction, and the matters referred to in this Memorandum, including consultation with their own
    legal, tax, accounting, engineering, and other professional advisors. Any and all liability for
    representations or warranties, express or implied, contained in, or for omissions from, this Memorandum
    or any other written or oral communications transmitted to a prospective counterparty in the course of
    its evaluation of the transaction is expressly disclaimed.</p>
  </div>
</section>''')

    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<title>Caramba North — Confidential Offering Memorandum (Post-NDA)</title>'
            f'<style>{CSS}</style></head><body>{"".join(out)}</body></html>')


def find_chrome():
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
    raise SystemExit("no Chromium binary found for PDF rendering")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="outputs/reports/Caramba-North-OM-PostNDA.pdf")
    ap.add_argument("--html-only", action="store_true")
    ap.add_argument("--stamp", default=date.today().isoformat())
    ap.add_argument("--no-flags", action="store_true",
                    help="omit methodology/classification disclosure boxes")
    a = ap.parse_args()

    model = D.build()
    mpath = EXHIBIT_DIR / "manifest.json"
    if mpath.exists():
        exhibits = json.loads(mpath.read_text())
    else:
        exhibits = [
            {"id": "2.1", "file": "exhibit_2_1_site-setting.png", "captured": "2026-07-06", "aspect": "2400/1500",
             "eyebrow": "EXHIBIT 2.1 · PECOS COUNTY, TEXAS",
             "title": "The site: contiguous, interstate-front, five miles from Fort Stockton",
             "subtitle": "Aerial view of the Caramba North tract (green boundary) on the north side of Interstate 10, with Fort Stockton and its municipal services to the east.",
             "takeaway": "The tract is a single contiguous block with direct I-10 frontage and town services five miles away."},
            {"id": "3.1", "file": "exhibit_3_1_planned-grid-upgrades.png", "captured": "2026-07-06", "aspect": "2400/1374",
             "eyebrow": "EXHIBIT 3.1 · CARAMBA NORTH CORRIDOR",
             "title": "Planned grid upgrades only (ERCOT TPIT) — the Solstice hub circled, the site beside it",
             "subtitle": "Planned transmission upgrades and planned substation upgrades only — no existing infrastructure shown.",
             "takeaway": "The planned-upgrade program radiates from the circled Solstice terminus on the site's doorstep."},
            {"id": "4.1", "file": "exhibit_4_1_generation-cluster.png", "captured": "2026-07-06", "aspect": "2400/1374",
             "eyebrow": "EXHIBIT 4.1 · PECOS COUNTY AND NEIGHBORING COUNTIES",
             "title": "The operating fleet and the interconnection queue, on one map",
             "subtitle": "Operating generation with the ERCOT generator-interconnection queue over the same footprint.",
             "takeaway": "The site sits inside the densest operating renewable cluster in ERCOT."},
            {"id": "7.1", "file": "exhibit_7_1_datacenter-pipeline.png", "captured": "2026-07-06", "aspect": "2400/1374",
             "eyebrow": "EXHIBIT 7.1 · PECOS AND REEVES COUNTIES",
             "title": "The announced data-center and large-load projects surrounding the site",
             "subtitle": "Campus land positions plus labeled callouts for announced projects.",
             "takeaway": "Gigawatt-scale sponsors have taken positions on every side of the site."},
        ]

    doc = render(model, exhibits, a.stamp, include_flags=not a.no_flags)
    out = REPO / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    hpath = out.with_suffix(".html")
    hpath.write_text(doc, encoding="utf-8")
    print(f"html  -> {hpath.relative_to(REPO)}  ({len(doc) // 1024} KB)")
    if a.html_only:
        return

    subprocess.run([find_chrome(), "--headless", "--no-sandbox", "--disable-gpu",
                    "--no-pdf-header-footer", f"--print-to-pdf={out}", hpath.as_uri()],
                   check=True, capture_output=True)
    print(f"pdf   -> {out.relative_to(REPO)}  ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
