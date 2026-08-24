#!/usr/bin/env python3
"""Caramba North — Technical Snapshot (condensed portrait document).

The data-room counterpart to the prose Executive Brief: same facts, opposite
treatment. Table- and stat-grid-driven, minimal prose, every figure set in
IBM Plex Mono so columns align down the page. Each section opens with a
banded header row carrying its insight subheading (brief §0 rule 2).

System: brief_tech — IBM Plex Sans + IBM Plex Mono, cool ground #F4F6F7,
blue #0E6E9C leading; red #B03A2E reserved for the subject site and the two
feature anchors.

    python3 scripts/om2/build_brief_technical.py
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import om_theme as T  # noqa: E402

S = T.SYSTEMS["brief_tech"]
BLUE, RED, GOLD = S["accent"], S["second"], S["third"]
INK, INK70, INK45, RULE = S["ink"], S["ink70"], S["ink45"], S["rule"]
PAPER, PANEL = S["paper"], S["panel"]
W, H = T.PAGE_W, T.PAGE_H
PAD_X, PAD_T, PAD_B = 46, 40, 34
CW = W - 2 * PAD_X          # 724 content width

OUT = T.REPO / "outputs" / "reports"
STEM = "Caramba-North-Brief-Technical"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def X(name, w, h):
    """Exhibit in a panel card, sized to its own aspect ratio so nothing
    letterboxes. The vector exhibits carry the warm deck ground baked in;
    recolour it to this system's panel so the card reads as one surface."""
    inner = T.svg(name).replace("#FBFAF7", PANEL)
    return (f'<div class="exh" style="width:{w}px;height:{h}px">{inner}</div>')


def band(num, name, sub, color=BLUE):
    return (f'<div class="band" style="background:{color}">'
            f'<div class="bn m">{num}</div>'
            f'<div class="bx"><div class="bl m">{name}</div>'
            f'<div class="bs">{sub}</div></div></div>')


def tbl(rows, widths, klass=""):
    """rows: list of tuples of cell strings; a cell may be prefixed 'm|' to
    set it in mono, or 'k|' for the recessive key column."""
    cols = "".join(f'<col style="width:{x}">' for x in widths)
    body = []
    for r in rows:
        tds = []
        for c in r:
            cls = ""
            if c.startswith("m|"):
                cls, c = "m num", c[2:]
            elif c.startswith("k|"):
                cls, c = "k", c[2:]
            tds.append(f'<td class="{cls}">{c}</td>')
        body.append("<tr>" + "".join(tds) + "</tr>")
    return (f'<table class="t {klass}">{cols}<tbody>'
            + "".join(body) + "</tbody></table>")


def hrow(cells, widths):
    cols = "".join(f'<col style="width:{x}">' for x in widths)
    ths = "".join(f'<th>{c}</th>' for c in cells)
    return f'<table class="t hd">{cols}<thead><tr>{ths}</tr></thead></table>'


def page(inner, n, running):
    return (f'<div class="page">'
            f'<div class="run"><span class="m">CARAMBA NORTH · TECHNICAL SNAPSHOT</span>'
            f'<span class="m">{running}</span></div>'
            f'<div class="body">{inner}</div>'
            f'<div class="foot"><span class="m">PECOS COUNTY, TEXAS · AUGUST 2026 · CONFIDENTIAL</span>'
            f'<span class="m">{n} / 6</span></div></div>')


CSS = f"""
<style>
.page {{ position:relative; }}
.body {{ position:absolute; left:{PAD_X}px; right:{PAD_X}px; top:{PAD_T}px;
         bottom:{PAD_B}px; }}
.run {{ position:absolute; left:{PAD_X}px; right:{PAD_X}px; top:16px;
        display:flex; justify-content:space-between; font-size:7.6px;
        letter-spacing:.16em; color:{INK45}; }}
.foot {{ position:absolute; left:{PAD_X}px; right:{PAD_X}px; bottom:14px;
         display:flex; justify-content:space-between; font-size:7.6px;
         letter-spacing:.14em; color:{INK45};
         border-top:1px solid {RULE}; padding-top:6px; }}

/* --- section band: the insight subheading IS the table header row ------- */
.band {{ display:flex; align-items:stretch; color:#fff; margin-bottom:0; }}
.bn {{ width:34px; flex:none; display:flex; align-items:center;
       justify-content:center; font-size:11px; font-weight:600;
       background:rgba(0,0,0,.18); }}
.bx {{ padding:6px 10px 7px; }}
.bl {{ font-size:8.4px; letter-spacing:.19em; opacity:.82; }}
.bs {{ font-size:11.4px; line-height:1.32; font-weight:500; margin-top:2px; }}

/* --- tables ------------------------------------------------------------- */
table.t {{ border-collapse:collapse; width:100%; table-layout:fixed;
           background:{PANEL}; }}
table.t td, table.t th {{ border-bottom:1px solid {RULE}; padding:4.6px 8px;
           font-size:9.6px; line-height:1.34; vertical-align:top;
           text-align:left; }}
table.t td.k {{ color:{INK70}; }}
table.t td.num {{ color:{INK}; font-weight:500; }}
table.t.hd th {{ font-family:{S['mono']}; font-size:7.8px; letter-spacing:.14em;
           color:{INK45}; text-transform:uppercase; padding:5px 8px 4px;
           border-bottom:1px solid {INK45}; font-weight:400; }}
table.t tr:last-child td {{ border-bottom:1px solid {RULE}; }}
.tw {{ border-left:1px solid {RULE}; border-right:1px solid {RULE}; }}

/* --- exhibits ----------------------------------------------------------- */
.exh {{ background:{PANEL}; border:1px solid {RULE}; overflow:hidden; }}
.cap {{ font-size:7.8px; letter-spacing:.13em; color:{INK45};
        margin-top:4px; }}

/* --- kpi strip ---------------------------------------------------------- */
.kpi {{ display:flex; gap:6px; }}
.kt {{ flex:1; min-width:0; background:{PANEL}; border:1px solid {RULE};
       border-top:2.5px solid {BLUE}; padding:7px 8px 8px; }}
.kt.r {{ border-top-color:{RED}; }}
.kv {{ font-size:21px; font-weight:600; letter-spacing:-.015em;
       line-height:1; color:{INK}; }}
.ku {{ font-size:8.2px; color:{INK70}; font-weight:400; margin-top:3px;
       letter-spacing:.06em; }}
.kl {{ font-size:7.4px; letter-spacing:.1em; color:{INK45}; margin-top:7px;
       line-height:1.42; text-transform:uppercase;
       border-top:1px solid {RULE}; padding-top:6px; }}

/* --- map key ------------------------------------------------------------ */
.key {{ display:flex; gap:12px; margin-top:7px; }}
.ki {{ flex:1; min-width:0; font-size:8.6px; line-height:1.4; color:{INK70};
       display:flex; gap:6px; align-items:flex-start; }}
.kn {{ flex:none; width:13px; height:13px; border-radius:50%;
       background:{GOLD}; color:#fff; font-size:8px; font-weight:600;
       display:flex; align-items:center; justify-content:center;
       margin-top:.5px; }}
.ki b {{ color:{INK}; font-weight:600; }}
.legend {{ display:flex; gap:16px; flex-wrap:wrap; margin-top:7px;
       font-size:8px; letter-spacing:.06em; color:{INK45};
       border-top:1px solid {RULE}; padding-top:6px; }}
.sw {{ display:inline-block; width:9px; height:9px; margin-right:5px;
       vertical-align:-1px; }}

/* --- stat tiles (wide) -------------------------------------------------- */
.st3 {{ display:flex; gap:10px; }}
.s3 {{ flex:1; background:{PANEL}; border:1px solid {RULE};
       border-left:3px solid {RED}; padding:8px 11px 9px; }}
.s3 .v {{ font-size:22px; font-weight:600; line-height:1; color:{INK};
       letter-spacing:-.015em; }}
.s3 .l {{ font-size:7.6px; letter-spacing:.12em; color:{INK45}; margin-top:6px;
       text-transform:uppercase; line-height:1.4; }}
.idx {{ display:flex; gap:14px; }}

/* --- corridor timeline (HTML/CSS, no new SVG) --------------------------- */
.tl {{ display:flex; gap:0; margin-top:9px; }}
.tn {{ flex:1; min-width:0; padding-right:12px; position:relative; }}
.tn .dot {{ width:9px; height:9px; border-radius:50%; background:{BLUE};
       position:relative; z-index:2; }}
.tn.done .dot {{ background:{BLUE}; }}
.tn.fut .dot {{ background:{PANEL}; border:2px solid {INK45}; }}
.tn .bar {{ position:absolute; left:0; right:0; top:4px; height:1.5px;
       background:{RULE}; z-index:1; }}
.tn:last-child .bar {{ right:auto; width:9px; }}
.tn .dt {{ font-size:8.6px; letter-spacing:.1em; color:{BLUE}; margin-top:8px;
       font-weight:600; }}
.tn.fut .dt {{ color:{INK45}; }}
.tn .tx {{ font-size:9px; line-height:1.4; color:{INK70}; margin-top:3px;
       padding-right:6px; }}
.tn .tx b {{ color:{INK}; font-weight:600; }}
.idx table td {{ padding:3.4px 7px; font-size:8.8px; }}

/* --- notes / callouts --------------------------------------------------- */
.note {{ background:{PANEL}; border:1px solid {RULE};
         border-left:2.5px solid {GOLD}; padding:8px 11px;
         font-size:9.3px; line-height:1.45; color:{INK70}; }}
.note b {{ color:{INK}; font-weight:600; }}
.note .h {{ font-size:7.8px; letter-spacing:.16em; color:{INK45};
            margin-bottom:4px; }}
.two {{ display:flex; gap:16px; align-items:flex-start; }}
.col {{ flex:1; min-width:0; }}
h2.st {{ font-size:9px; letter-spacing:.2em; color:{BLUE}; font-weight:600;
         margin:0 0 2px; }}
.stsub {{ font-size:9.6px; line-height:1.35; color:{INK70}; margin:0 0 6px;
         max-width:640px; }}
</style>
"""



# ---------------------------------------------------------------------------
# page 1 — masthead, KPI strip, ring analysis, macro context, contents
# ---------------------------------------------------------------------------
KPI = [
    ("1,300", "acres", "Max contiguous tract, I-10 north side", 0),
    ("32.7", "GW", "Operating + queued within 60 mi", 0),
    ("15.5", "miles", "To GW Ranch — 7.65 GW air permit", 1),
    ("19.3", "miles", "To Longfellow — 2 GW planned campus", 1),
    ("47,418", "AF / yr", "Permitted water — 42.3 MGD", 0),
    ("115", "wells", "New-drill since 2020 — 90% below peer avg", 0),
]
kpi_html = "".join(
    f'<div class="kt{" r" if r else ""}"><div class="kv m">{v}</div>'
    f'<div class="ku m">{u}</div><div class="kl m">{l}</div></div>'
    for v, u, l, r in KPI)

ring_tbl = hrow(["Radius from tract", "Operating + queued"], ["58%", "42%"]) + tbl([
    ("k|≤ 15 mi", "m|0.5 GW"),
    ("k|≤ 30 mi", "m|8.9 GW"),
    ("k|≤ 60 mi", "m|32.7 GW"),
    ("k|≤ 100 mi", "m|53.5 GW"),
], ["58%", "42%"], "tw")

IDX = [
    [("01", "Regional power gravity · ring analysis", "1"),
     ("02", "The property", "2"),
     ("03", "Transmission", "2"),
     ("04", "Regional power cluster", "3")],
    [("05", "Water", "2"),
     ("06", "Natural gas", "2"),
     ("07", "Regional pipeline", "4"),
     ("7A/7B", "GW Ranch · Longfellow", "4")],
    [("08", "Subsurface and drilling activity", "5"),
     ("09", "The diligence platform", "5"),
     ("10", "Distance methodology", "6"),
     ("11", "Notices", "6"),
     ("12", "Source register", "6")],
]
idx_html = "".join(
    '<div class="col">' + tbl([(f"m|{a}", f"k|{b}", f"m|{c}") for a, b, c in g],
                              ["17%", "72%", "11%"], "tw") + "</div>"
    for g in IDX)

p1 = f"""
<div style="display:flex;justify-content:space-between;align-items:flex-end">
  <div>
    <div class="m" style="font-size:8.6px;letter-spacing:.24em;color:{BLUE}">
      TECHNICAL SNAPSHOT · DATA-ROOM REFERENCE</div>
    <h1 class="d" style="font-size:38px;font-weight:600;letter-spacing:-.02em;
        line-height:1;margin-top:9px">Caramba North</h1>
  </div>
  <div class="m" style="font-size:8.4px;letter-spacing:.13em;color:{INK45};
       text-align:right;line-height:1.7">
    PECOS COUNTY, TEXAS<br>FORT STOCKTON · ERCOT FAR WEST<br>AUGUST 2026 EDITION</div>
</div>
<div style="border-top:2px solid {INK};margin:11px 0 10px"></div>
<p style="font-size:11.6px;line-height:1.5;color:{INK};max-width:648px">
  A 1,300-acre as-of-right industrial tract on the north-south line between two
  hyperscale-scale power campuses — 7.65 GW at 15.5 miles and a 2 GW phased
  build at 19.3 miles — inside a 60-mile radius carrying 32.7 GW of operating
  and queued capacity, with water and gas already permitted rather than
  applied for.</p>

<div class="kpi" style="margin-top:13px">{kpi_html}</div>

<div style="margin-top:15px">
{band("01", "REGIONAL POWER GRAVITY · RING ANALYSIS",
      "32.7 GW of operating and queued capacity sits within 60 miles; "
      "Caramba North is inside the radius, not adjacent to it.")}
</div>
<div class="two" style="margin-top:10px">
  <div style="flex:none">{X("chart_rings_light", 392, 392)}
    <div class="cap m">CUMULATIVE OPERATING + ERCOT-QUEUE CAPACITY BY RADIUS</div>
  </div>
  <div class="col">
    {ring_tbl}
    <div class="note" style="margin-top:10px">
      <div class="h m">BEARING</div>
      GW Ranch bears <b>~19°</b> and Longfellow <b>~188°</b> from the tract —
      the property sits on the north-south line between them, not off to one
      side of the corridor.</div>
    <div class="note" style="margin-top:8px;border-left-color:{BLUE}">
      <div class="h m">BASIS</div>
      Region-wide operating capacity (EIA-860) plus ERCOT interconnection-queue
      capacity, computed on radius from the tract boundary — not county-bounded,
      and not limited to the two profiled anchors.</div>
    <div class="note" style="margin-top:8px;border-left-color:{RED}">
      <div class="h m">STATE CONTEXT · PUBLIC REPORTING, DEC 2025 / AUG 2026</div>
      ERCOT's large-load queue grew from <b>63 GW</b> (year-end 2024) to
      <b>226 GW</b> (Nov 2025) and reached roughly <b>474 GW</b> of pending
      requests by Aug 2026, approximately <b>90% data-center-driven</b>. An
      Aug 3, 2026 directive ordered an audit of all ERCOT-queue data centers and
      paused the "Batch Zero" large-load review.</div>
  </div>
</div>

<h2 class="st m" style="margin-top:16px">CONTENTS</h2>
<p class="stsub">Twelve sections; every figure resolves to the source register on page 6.</p>
<div class="idx">{idx_html}</div>
"""

# ---------------------------------------------------------------------------
# page 2 — property, transmission, water, gas
# ---------------------------------------------------------------------------
prop = hrow(["Attribute", "Value", "Basis"], ["24%", "30%", "46%"]) + tbl([
    ("k|Contiguous area", "m|1,300 acres", "Maximum contiguous assemblage"),
    ("k|Location", "m|I-10 north side", "Pecos County, Texas"),
    ("k|Services", "m|~5 mi", "Fort Stockton — services and regional airport"),
    ("k|Entitlement", "m|No zoning ordinance", "Industrial and energy use as of right; no rezoning path required"),
    ("k|ERCOT zone", "m|Far West", "Highest-growth large-load weather zone in ERCOT"),
], ["24%", "30%", "46%"], "tw")

trans = hrow(["Attribute", "Value", "Basis"], ["24%", "30%", "46%"]) + tbl([
    ("k|Solstice Substation", "m|15 mi", "Western terminus of three PUCT-approved 765 kV Permian import paths"),
    ("k|Approval", "m|Apr 24, 2025", "PUCT PBRP Docket No. 55718"),
    ("k|Substations ≤ 10 mi", "m|6", "Listed below — 138 kV and 69 kV local network"),
    ("k|Nearest substation", "m|2.0 mi", "Fort Stockton Plant, 138/69 kV"),
    ("k|TPIT upgrade queue", "m|141 sub / 133 line", "ERCOT-wide <i>planned</i> upgrades; pipeline context, not committed capacity"),
], ["24%", "30%", "46%"], "tw")

subs = hrow(["Substation", "Distance", "Voltage", "Substation", "Distance", "Voltage"],
            ["21%", "8%", "14%", "22%", "8%", "14%"]) + tbl([
    ("k|Fort Stockton Plant", "m|2.0 mi", "m|138 / 69 kV", "k|16th Street", "m|6.0 mi", "m|138 / 69 kV"),
    ("k|Airport", "m|3.3 mi", "m|138 kV", "k|Northern Natural", "m|7.0 mi", "m|—"),
    ("k|Fort Stockton", "m|5.4 mi", "m|69 kV", "k|Gomez", "m|9.7 mi", "m|—"),
], ["21%", "8%", "14%", "22%", "8%", "14%"], "tw")

water = hrow(["Attribute", "Value"], ["46%", "54%"]) + tbl([
    ("k|Permitted volume", "m|47,418 AF/yr · 42.3 MGD"),
    ("k|Share of district industrial rights", "m|≈ two-thirds"),
    ("k|Permit position", "Adjacent affiliated lands"),
    ("k|Source aquifer", "Edwards-Trinity (Plateau)"),
    ("k|Drought-of-record behaviour", "Recharge held through the 1950s"),
], ["46%", "54%"], "tw")

gas = hrow(["Attribute", "Value"], ["46%", "54%"]) + tbl([
    ("k|Waha hub distance", "m|20 mi"),
    ("k|Indicative supply quote", "m|200,000 MMBtu/day"),
    ("k|Term / pricing", "m|15 years · Waha index"),
    ("k|CIAC", "m|$15 – 25 M"),
    ("k|Lead time", "m|9 – 15 months"),
], ["46%", "54%"], "tw")

p2 = f"""
{band("02", "THE PROPERTY",
      "As-of-right industrial land inside the fastest-growing load pocket in "
      "ERCOT — not a rezoning story.")}
{prop}

<div style="margin-top:16px">
{band("03", "TRANSMISSION",
      "Fifteen miles from the delivery point of all three approved 765 kV "
      "Permian import lines — the transmission decision is already made, "
      "upstream of this site.")}
</div>
{trans}
<h2 class="st m" style="margin-top:12px">LOCAL SUBSTATIONS WITHIN TEN MILES</h2>
<p class="stsub">Six substations sit inside ten miles and the nearest is two —
the local distribution network is already in place, not a greenfield extension.</p>
{subs}

<div class="two" style="margin-top:16px">
  <div class="col">
    {band("05", "WATER",
          "Two-thirds of the district's industrial water rights are already "
          "permitted to this position — the water conversation is closed, not "
          "open.")}
    {water}
  </div>
  <div class="col">
    {band("06", "NATURAL GAS",
          "A signable 15-year gas quote at Waha basis — the same structural "
          "discount now drawing behind-the-meter generation into this "
          "corridor.")}
    {gas}
  </div>
</div>
<div class="note" style="margin-top:11px">
  <div class="h m">GAS BASIS CONTEXT</div>
  Waha prices at a structural discount to Henry Hub, with negative prints
  recorded in 2024–2025 as the Matterhorn, Blackcomb, Hugh Brinson and GCX
  pipelines rebalance Permian egress. Supply terms above are a
  counterparty-supplied indicative quote, not a binding offer.</div>

<div class="two" style="margin-top:11px">
  <div class="col"><div class="note" style="border-left-color:{BLUE}">
    <div class="h m">WHAT THE 765 KV APPROVAL MEANS HERE</div>
    The Permian import build is a decision already taken upstream of this tract:
    three paths approved, terminating 15 miles away. The site does not need a new
    line to be approved — it needs to be near one that already is.</div></div>
  <div class="col"><div class="note">
    <div class="h m">READING THE TPIT COLUMN</div>
    141 substation and 133 line upgrades are tracked ERCOT-wide in the
    Transmission Planning Improvement Tool. These are <b>planned</b> upgrades,
    not built capacity, and are cited here as pipeline context only.</div></div>
</div>
"""

# ---------------------------------------------------------------------------
# page 3 — regional power cluster + corridor geometry
# ---------------------------------------------------------------------------
cluster = hrow(["Measure", "Capacity", "Detail"], ["30%", "23%", "47%"]) + tbl([
    ("k|Operating, Pecos County", "m|3,226 MW", "Solar 2,178 MW (13) · Wind 542 MW (5) · BESS 505 MW (6) · Gas 1 MW (1)"),
    ("k|ERCOT queue, Pecos County", "m|12,039 MW", "39 projects in this county alone"),
    ("k|Operating, six adjacent counties", "m|7,022 MW", "Reeves, Crane, Ward, Upton, Ector, Crockett"),
    ("k|Queued, six adjacent counties", "m|24,585 MW", "Same six-county ring"),
    ("k|Queued within 20 mi", "m|3,973 MW", "13 projects"),
    ("k|Nearest operating storage", "m|103 MW", "St. Gall Energy Storage I — 1.9 mi, BESS"),
], ["30%", "23%", "47%"], "tw")

key_html = f"""
<div class="key" style="flex-direction:column;gap:9px;margin-top:0">
  <div class="ki"><span class="kn">1</span><span><b>GW Ranch</b> — 15.5 mi
    north · 7.65 GW TCEQ air permit · under construction (§7A)</span></div>
  <div class="ki"><span class="kn">2</span><span><b>Longfellow</b> — 19.3 mi
    south · 2 GW planned on-site gas generation · phase-1 site work (§7B)</span></div>
</div>
<div class="legend m" style="flex-direction:column;gap:5px">
  <span><span class="sw" style="background:{RED}"></span>Subject tract (surveyed)</span>
  <span><span class="sw" style="background:{GOLD};border-radius:50%"></span>Anchor site point</span>
  <span><span class="sw" style="background:{INK45}"></span>Transmission (HIFLD)</span>
  <span><span class="sw" style="background:{BLUE};border-radius:50%"></span>ERCOT queue</span>
  <span><span class="sw" style="border:1px dashed {INK45}"></span>Rings at 10 / 15 / 30 mi</span>
</div>
<div style="font-size:8px;line-height:1.45;color:{INK45};margin-top:7px">
  Markers 1 and 2 are plotted at each anchor's disclosed site point. The
  distances quoted are edge-to-edge from the Caramba North tract boundary, which
  is shorter than the plotted point-to-point spacing (methodology, §10).</div>"""

p3 = f"""
{band("04", "REGIONAL POWER CLUSTER",
      "12 GW is already queued in this county alone — before counting the two "
      "hyperscale-scale campuses profiled on the next page.")}
{cluster}
<div class="two" style="margin-top:11px">
  <div style="flex:none">{X("chart_power_mix_light", 380, 190)}
    <div class="cap m">PECOS COUNTY OPERATING CAPACITY BY TECHNOLOGY</div></div>
  <div class="col">
    <div class="note" style="border-left-color:{BLUE}">
      <div class="h m">COMPOSITION OF THE OPERATING FLEET</div>
      The operating base is intermittent and storage-weighted — 2,178 MW solar,
      542 MW wind, 505 MW BESS and 1 MW of gas. The queue is what changes that
      mix: <b>12,039 MW</b> filed in Pecos County and <b>24,585 MW</b> across the
      six adjacent counties, of which <b>3,973 MW</b> sits within 20 miles of the
      tract. Nearest operating storage is 1.9 miles from the boundary.</div>
  </div>
</div>

<h2 class="st m" style="margin-top:15px">CORRIDOR GEOMETRY — TRACT, ANCHORS, TRANSMISSION AND QUEUE</h2>
<p class="stsub">The tract, both anchors, the 765 kV terminus and the bulk of the
queued capacity all fall inside a thirty-mile frame, on one north-south line.</p>
<div class="two">
  <div style="flex:none">{X("corridor_bare_light", 520, 370)}</div>
  <div class="col">{key_html}</div>
</div>
"""

# ---------------------------------------------------------------------------
# page 4 — the regional pipeline and the two anchors
# ---------------------------------------------------------------------------
S3 = [("9.65 GW", "Combined announced · two anchors"),
      ("79.3%", "GW Ranch · under construction"),
      ("20.7%", "Longfellow · planned, phase 1")]
s3_html = "".join(f'<div class="s3"><div class="v m">{v}</div>'
                  f'<div class="l m">{l}</div></div>' for v, l in S3)

gw = hrow(["Attribute", "Value"], ["37%", "63%"]) + tbl([
    ("k|Distance from tract", "m|15.5 mi — edge-to-edge"),
    ("k|Site", "m|8,000 acres, Pecos County"),
    ("k|Ownership", "Amazon, disclosed Aug 2026; Pacifico Energy Group remains power-plant developer/operator"),
    ("k|Generation", "m|35 gas turbines · 7.65 GW"),
    ("k|Permit", "TCEQ air permit issued Jan/Feb 2026 — largest in the US"),
    ("k|Storage and solar", "m|1.8 GW BESS · up to 750 MW solar"),
    ("k|Buildings", "m|3 × 189,000 sq ft"),
    ("k|Design / cost", "Gensler; ≈ $300 M each; ≈ $12 B total project"),
    ("k|Target completion", "m|Dec 2026"),
    ("k|Status", "Under construction"),
], ["37%", "63%"], "tw")

lf = hrow(["Attribute", "Value"], ["37%", "63%"]) + tbl([
    ("k|Distance from tract", "m|19.3 mi — edge-to-edge"),
    ("k|Site", "m|568 acres, Pecos County"),
    ("k|Announced", "Oct 2025 — 2 GW across 8 phases"),
    ("k|Phase size", "m|250 MW"),
    ("k|Generation planned", "On-site natural gas: aero-derivative turbines with SCR and carbon-capture capability"),
    ("k|Cooling", "Closed-loop on permitted non-potable groundwater"),
    ("k|Status", "Phase-1 site work underway; on-site generation build planned in phases"),
    ("k|Permitting record", "No confirmed ERCOT queue position or TCEQ air-permit record found as of Aug 2026"),
    ("k|Location note", "Public materials describe the site as more than 25 mi outside Fort Stockton"),
], ["37%", "63%"], "tw")

p4 = f"""
{band("07", "REGIONAL DATA-CENTER AND POWER PIPELINE",
      "79.3% of the two anchors' combined announced capacity is already under "
      "construction — the regional pipeline is majority-built, not "
      "majority-speculative.")}
<div class="st3" style="margin-top:11px">{s3_html}</div>
<div class="two" style="margin-top:12px">
  <div style="flex:none;width:380px">{X("chart_maturity_light", 380, 129)}
    <div class="cap m">COMBINED ANNOUNCED MW, BY BUILD STATUS</div>
    <div class="note" style="margin-top:10px;border-left-color:{RED}">
      <div class="h m">PERMIT vs. QUEUE — READ CAREFULLY</div>
      The 7.65 GW figure at GW Ranch is a TCEQ <b>generation air permit</b>, not
      an ERCOT interconnection queue position. No ERCOT filing has been disclosed
      and the project is off-grid initially.</div></div>
  <div class="col">
    <div class="note" style="border-left-color:{BLUE}">
      <div class="h m">WHY THIS MATTERS TO THIS TRACT</div>
      Both anchors are being built around on-site generation rather than a grid
      interconnection award — the same water, gas and land conditions that made
      that possible at 15.5 and 19.3 miles apply to this tract.</div>
    <div class="note" style="margin-top:9px">
      <div class="h m">WHAT THE 9.65 GW DOES NOT INCLUDE</div>
      This figure counts only the two profiled anchors. The ring analysis in §01
      counts all operating and ERCOT-queued capacity by radius regardless of
      developer — <b>0.5 GW</b> within 15 mi, <b>8.9 GW</b> within 30 mi and
      <b>32.7 GW</b> within 60 mi.</div>
  </div>
</div>

<div class="two" style="margin-top:14px">
  <div class="col">
    {band("7A", "GW RANCH", "The largest air permit issued in the US this year "
          "sits fifteen miles up the same highway corridor — under "
          "construction, not announced.", RED)}
    {gw}
  </div>
  <div class="col">
    {band("7B", "LONGFELLOW", "A second phased gas-generation campus twenty "
          "miles south — the corridor's demand for on-site power is not one "
          "project deep.", RED)}
    {lf}
  </div>
</div>

<h2 class="st m" style="margin-top:16px">CORRIDOR TIMELINE</h2>
<p class="stsub">Four of the five dated milestones in this corridor have already
occurred; the fifth is a completion target, not an approval.</p>
<div class="tl">
  <div class="tn done"><div class="bar"></div><div class="dot"></div>
    <div class="dt m">APR 2025</div>
    <div class="tx">PUCT approves three 765 kV Permian import paths —
      <b>Docket 55718</b></div></div>
  <div class="tn done"><div class="bar"></div><div class="dot"></div>
    <div class="dt m">OCT 2025</div>
    <div class="tx"><b>Longfellow</b> announced — 2 GW across eight
      250 MW phases</div></div>
  <div class="tn done"><div class="bar"></div><div class="dot"></div>
    <div class="dt m">JAN / FEB 2026</div>
    <div class="tx"><b>GW Ranch</b> TCEQ air permit issued — 7.65 GW,
      largest in the US</div></div>
  <div class="tn done"><div class="bar"></div><div class="dot"></div>
    <div class="dt m">AUG 2026</div>
    <div class="tx">GW Ranch ownership disclosed; Longfellow
      <b>phase-1 site work underway</b></div></div>
  <div class="tn fut"><div class="bar"></div><div class="dot"></div>
    <div class="dt m">DEC 2026</div>
    <div class="tx">GW Ranch three-building <b>targeted completion</b></div></div>
</div>
"""

# ---------------------------------------------------------------------------
# page 5 — subsurface + diligence platform
# ---------------------------------------------------------------------------
sub_rings = hrow(["Ring from tract boundary", "New-drill wells since 2020", "Detail"],
                 ["30%", "26%", "44%"]) + tbl([
    ("k|≤ 2 mi", "m|0", "No new-drill wellbore events recorded"),
    ("k|≤ 5 mi", "m|0", "No new-drill wellbore events recorded"),
    ("k|≤ 10 mi", "m|1", "Single event at 9.37 mi"),
    ("k|> 10 mi", "m|114", "Median 19.9 mi · mean 20.9 mi"),
    ("k|Pecos County total", "m|115", "Of 1,140 RRC events — 10% new-drill, 90% workover / rework"),
], ["30%", "26%", "44%"], "tw")

peers = hrow(["Wellbore condition within each ring", "≤ 2 mi", "≤ 5 mi", "≤ 10 mi"],
             ["52%", "16%", "16%", "16%"]) + tbl([
    ("k|Share of non-plugged wellbores in marginal or end-of-life production",
     "m|60%", "m|62%", "m|83%"),
], ["52%", "16%", "16%", "16%"], "tw")

plat = hrow(["Attribute", "Specification"], ["24%", "76%"]) + tbl([
    ("k|Data lineage", "Every point, line and boundary traces to a cited public dataset; per-feature source popups"),
    ("k|Source datasets", "ERCOT GIS Report / TPIT · PUCT · EIA-860 · TCEQ · RRC dbf900, production, W-1 · FracFocus · Middle Pecos GCD · HIFLD · USGS · BTS · Census TIGER"),
    ("k|Refresh cadence", "RRC weekly · ERCOT queue and TPIT monthly · EIA, USGS, OSM annually"),
    ("k|Query tools", "Filters by county, depth, spud year, fuel and status; time scrubber; measure, share and print"),
    ("k|Build and access", "Static versioned build; deployed bundle byte-verified on release; access logged"),
    ("k|URL", "m|lrp-tx-gis.netlify.app — credentials issued to the deal team separately"),
], ["24%", "76%"], "tw")

p5 = f"""
{band("08", "SUBSURFACE AND DRILLING ACTIVITY",
      "Pecos County has the lowest new-drilling count of seven comparable "
      "Permian counties since 2020 — a 90%-below-peer-average level of "
      "activity, not merely quiet.")}
<div style="margin-top:10px">{X("chart_peer_drilling_light", 724, 346)}
  <div class="cap m">NEW-DRILL WELLBORE EVENTS SINCE 2020 — PECOS vs. SIX PEER PERMIAN COUNTIES · RRC dbf900</div></div>

<h2 class="st m" style="margin-top:14px">ACTIVITY BY RING FROM THE TRACT BOUNDARY</h2>
<p class="stsub">No new-drill wellbore has been recorded within five miles of the
tract since 2020, and only one within ten.</p>
{sub_rings}
<div style="margin-top:10px">{peers}</div>

<div style="margin-top:16px">
{band("09", "THE DILIGENCE PLATFORM",
      "Every figure in this document is independently re-derivable from a "
      "cited public source — this is not a broker's summary.")}
</div>
{plat}
"""

# ---------------------------------------------------------------------------
# page 6 — methodology, notices, source register, figure register
# ---------------------------------------------------------------------------
srcs = hrow(["Item", "Source"], ["27%", "73%"]) + tbl([
    ("k|GIS layer lineage", "ERCOT GIS Report and TPIT; PUCT; EIA-860; TCEQ; RRC dbf900, production and W-1; FracFocus; Middle Pecos GCD; HIFLD; USGS; BTS; Census TIGER"),
    ("k|Transmission approval", "PUCT Permian Basin Reliability Plan, Docket No. 55718 — approved Apr 24, 2025"),
    ("k|Planned grid upgrades", "ERCOT Transmission Planning Improvement Tool (TPIT), monthly refresh"),
    ("k|Operating generation", "EIA-860 plant and capacity records"),
    ("k|Queued generation", "ERCOT interconnection queue, monthly refresh"),
    ("k|GW Ranch air permit", "TCEQ air-permit record, issued Jan/Feb 2026"),
    ("k|GW Ranch ownership and campus detail", "Public reporting, Aug 2026"),
    ("k|Longfellow site detail", "Project public materials and public reporting, Oct 2025 – Aug 2026"),
    ("k|ERCOT queue growth", "Latitude Media, “ERCOT's large load queue has nearly quadrupled in a single year,” Dec 3, 2025"),
    ("k|Queue pause and audit", "Utility Dive, “Facing an estimated 474 GW of interconnection requests, Texas hits pause on data centers,” Aug 2026"),
    ("k|Water rights", "Middle Pecos Groundwater Conservation District permit records"),
    ("k|Gas supply terms", "Counterparty-supplied indicative quote — not a binding offer"),
    ("k|Wellbore activity", "Railroad Commission of Texas dbf900, production and W-1 records; weekly refresh"),
], ["27%", "73%"], "tw")

figs = hrow(["Figure", "Page", "Derived from"], ["30%", "8%", "62%"]) + tbl([
    ("k|Cumulative capacity by radius", "m|1", "EIA-860 operating capacity + ERCOT queue, radius from tract boundary"),
    ("k|Pecos County operating capacity by technology", "m|3", "EIA-860 plant records, Pecos County"),
    ("k|Corridor geometry", "m|3", "Surveyed tract boundary, disclosed anchor site points, HIFLD transmission, ERCOT queue, Census TIGER highways"),
    ("k|Combined announced MW by build status", "m|4", "GW Ranch 7,650 MW under construction; Longfellow 2,000 MW planned"),
    ("k|New-drill wellbore events since 2020", "m|5", "RRC dbf900 new-drill events, seven Permian counties"),
], ["30%", "8%", "62%"], "tw")

p6 = f"""
{band("10", "DISTANCE METHODOLOGY",
      "Distances here are measured edge-to-edge — the shorter and the more "
      "defensible of the two conventions, stated rather than assumed.")}
<div class="note" style="margin-top:10px;border-left-color:{BLUE}">
  Distances to GW Ranch and Longfellow are measured edge-to-edge: from the
  nearest point on the Caramba North tract boundary to each site's disclosed
  location, rather than centroid-to-centroid. Edge-to-edge is consistently
  shorter than a straight centroid measurement because the Caramba North tract
  has spatial extent of its own.
  <div style="margin-top:7px">
  <b>GW Ranch — 15.5 mi</b> edge-to-edge (17.3 mi centroid-to-centroid).<br>
  <b>Longfellow — 19.3 mi</b> edge-to-edge (19.7 mi centroid-to-centroid).
  </div>
  <div style="margin-top:7px">
  Longfellow's own public materials describe its location as more than 25 miles
  outside of Fort Stockton, which is consistent with the longer figure; this
  distance should not be represented as shorter. The TCEQ record for GW Ranch
  locates that site approximately 17 miles north of Fort Stockton on Highway 18.
  </div>
</div>

<div style="margin-top:15px">
{band("11", "NOTICES",
      "This document is an indicative technical summary issued under NDA — it "
      "is not an offer, and the figures are preliminary.")}
</div>
<div class="note" style="margin-top:10px;border-left-color:{RED}">
  Confidential offering memorandum prepared for a limited number of prospective
  counterparties under non-disclosure agreement. This is not an offer to sell or
  a solicitation of an offer to buy any security. Information is preliminary and
  indicative, drawn from sources believed to be reliable but not independently
  verified by the issuer. Public data is drawn from the datasets listed in the
  diligence-platform section and the source register below. Third-party
  transaction and permitting news is sourced to the public reporting cited in
  that register. Recipients should conduct their own diligence.</div>

<div style="margin-top:15px">
{band("12", "SOURCE REGISTER",
      "Every number above resolves to one of the rows below — public dataset, "
      "regulatory docket or cited report.")}
</div>
{srcs}
<h2 class="st m" style="margin-top:13px">FIGURE REGISTER</h2>
<p class="stsub">Each exhibit is reproducible from the layers named below.</p>
{figs}
"""

# ---------------------------------------------------------------------------
pages = "".join([
    CSS,
    page(p1, 1, "01 · POSITION"),
    page(p2, 2, "02–03, 05–06 · PROPERTY, TRANSMISSION, WATER, GAS"),
    page(p3, 3, "04 · REGIONAL POWER CLUSTER"),
    page(p4, 4, "07 · REGIONAL PIPELINE"),
    page(p5, 5, "08–09 · SUBSURFACE AND PLATFORM"),
    page(p6, 6, "10–12 · METHODOLOGY, NOTICES, SOURCES"),
])

html = T.document("brief_tech", pages, "portrait",
                  "Caramba North — Technical Snapshot")
OUT.mkdir(parents=True, exist_ok=True)
hp = OUT / f"{STEM}.html"
hp.write_text(html, encoding="utf-8")
print("html", hp, hp.stat().st_size // 1024, "KB")
T.render_pdf(str(hp), str(OUT / f"{STEM}.pdf"), "portrait")
print("pdf ", OUT / f"{STEM}.pdf")
