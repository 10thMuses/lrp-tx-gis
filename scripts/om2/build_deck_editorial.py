#!/usr/bin/env python3
"""Caramba North — Editorial deck (system key: editorial).

A dark magazine special report: Instrument Serif set very large is the
dominant element, the insight subheading from the content brief usually IS
the headline, tables are replaced by two or three called-out numbers, and the
regional map runs full-bleed twice. Landscape, 14 pages.

Facts, headline/subheading copy and the §0 rules come from
docs/redesign_content_brief.md. Nothing here is invented.

    python3 scripts/om2/build_deck_editorial.py
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import om_theme as T  # noqa: E402

S = T.SYSTEMS["editorial"]
PAPER = S["paper"]
INK, INK70, INK45, INK25, INK12 = S["ink"], S["ink70"], S["ink45"], S["ink25"], S["ink12"]
RULE, PANEL = S["rule"], S["panel"]
RED, GOLD, BLUE = S["accent"], S["second"], S["third"]

PAD_X = 76
TOP = 92          # content box top
BOT = 76          # content box bottom offset
CW = T.SLIDE_W - 2 * PAD_X          # 1128
CH = T.SLIDE_H - TOP - BOT          # 552

_pages: list[str] = []


# ---------------------------------------------------------------------------
# page shells
# ---------------------------------------------------------------------------
def rails(section, folio):
    top = (f'<div style="position:absolute;left:{PAD_X}px;right:{PAD_X}px;top:36px;'
           f'display:flex;justify-content:space-between;align-items:baseline">'
           f'<div class="m" style="font-size:9.5px;letter-spacing:.24em;color:{INK45}">{section}</div>'
           f'<div class="m" style="font-size:9.5px;letter-spacing:.24em;color:{INK45}">'
           f'CARAMBA NORTH &middot; PECOS COUNTY, TEXAS</div></div>')
    bot = (f'<div style="position:absolute;left:{PAD_X}px;right:{PAD_X}px;bottom:32px;'
           f'border-top:1px solid {RULE};padding-top:9px;display:flex;'
           f'justify-content:space-between;align-items:baseline">'
           f'<div class="m" style="font-size:9.5px;letter-spacing:.2em;color:{INK45}">'
           f'LAND RESOURCE PARTNERS &middot; CONFIDENTIAL</div>'
           f'<div class="m" style="font-size:10.5px;color:{INK70}">{folio:02d}</div></div>')
    return top, bot


def page(section, folio, body):
    """Standard editorial page: rails top and bottom, one content box."""
    top, bot = rails(section, folio)
    return (f'<div class="page">{top}'
            f'<div style="position:absolute;left:{PAD_X}px;right:{PAD_X}px;top:{TOP}px;'
            f'bottom:{BOT}px;display:flex;flex-direction:column">{body}</div>{bot}</div>')


def raw_page(body):
    return f'<div class="page">{body}</div>'


# ---------------------------------------------------------------------------
# typographic components
# ---------------------------------------------------------------------------
def kicker(text, color=None, mt=0):
    return (f'<div class="m" style="font-size:10px;letter-spacing:.26em;'
            f'color:{color or INK70};margin-top:{mt}px">{text}</div>')


def headline(text, size=68, color=None, mt=16, lh=0.98, maxw=None):
    mw = f'max-width:{maxw}px;' if maxw else ''
    return (f'<h1 class="d" style="font-weight:400;font-size:{size}px;line-height:{lh};'
            f'letter-spacing:-0.015em;color:{color or INK};margin-top:{mt}px;{mw}">{text}</h1>')


def deck(text, size=24, mt=18, maxw=None, color=None):
    """The insight subheading — italic display, gold. Always a conclusion."""
    mw = f'max-width:{maxw}px;' if maxw else ''
    return (f'<p class="d" style="font-style:italic;font-weight:400;font-size:{size}px;'
            f'line-height:1.3;color:{color or GOLD};margin-top:{mt}px;{mw}">{text}</p>')


def body(text, size=14.5, mt=20, maxw=None, color=None, lh=1.62):
    mw = f'max-width:{maxw}px;' if maxw else ''
    return (f'<p style="font-size:{size}px;line-height:{lh};font-weight:300;'
            f'color:{color or INK70};margin-top:{mt}px;{mw}">{text}</p>')


def rule(mt=0, mb=0, color=None, w="100%"):
    return (f'<div style="width:{w};height:1px;background:{color or RULE};'
            f'margin-top:{mt}px;margin-bottom:{mb}px"></div>')


def bignum(value, unit, caption, size=76, color=None, cap_w=None):
    """One called-out number. Display face for the figure, mono for the unit."""
    cw = f'max-width:{cap_w}px;' if cap_w else ''
    return (
        f'<div style="flex:1;min-width:0">'
        f'<div style="height:1px;background:{INK25}"></div>'
        f'<div class="m" style="font-size:9.5px;letter-spacing:.22em;color:{INK45};'
        f'margin-top:12px">{unit}</div>'
        f'<div class="d" style="font-weight:400;font-size:{size}px;line-height:1;'
        f'letter-spacing:-0.02em;color:{color or INK};margin-top:8px">{value}</div>'
        f'<div style="font-size:12.5px;line-height:1.45;font-weight:300;color:{INK70};'
        f'margin-top:12px;{cw}">{caption}</div></div>')


def numrow(items, gap=44, mt=0):
    return (f'<div style="display:flex;gap:{gap}px;margin-top:{mt}px">'
            + "".join(items) + '</div>')


def chip(text, color=RED):
    return (f'<span class="m" style="display:inline-block;background:{color};color:#FFFFFF;'
            f'font-size:9.5px;letter-spacing:.18em;padding:4px 9px 3px;'
            f'vertical-align:middle">{text}</span>')


def keyline(n, name, meta, color=GOLD):
    """Numbered map-key entry, matching the 1/2/3 markers in the corridor SVGs."""
    return (
        f'<div style="display:flex;gap:12px;align-items:flex-start;margin-top:14px">'
        f'<div class="m" style="flex:none;width:19px;height:19px;border-radius:50%;'
        f'background:{color};color:{PAPER};font-size:10.5px;line-height:19px;'
        f'text-align:center">{n}</div>'
        f'<div style="min-width:0"><div style="font-size:14px;font-weight:500;color:{INK}">{name}</div>'
        f'<div class="m" style="font-size:10.5px;color:{INK45};margin-top:3px;'
        f'letter-spacing:.02em">{meta}</div></div></div>')


def note(text, mt=0, size=11, color=None):
    return (f'<p class="m" style="font-size:{size}px;line-height:1.6;color:{color or INK70};'
            f'margin-top:{mt}px">{text}</p>')


# ===========================================================================
# 01 — Cover
# ===========================================================================
cover_left = f"""
<div style="display:flex;flex-direction:column;height:100%">
  {kicker("CONFIDENTIAL OFFERING MEMORANDUM &middot; PREPARED UNDER NDA")}
  <h1 class="d" style="font-weight:400;font-size:116px;line-height:0.92;
      letter-spacing:-0.025em;color:{INK};margin-top:26px">Caramba<br>North</h1>
  <div style="height:1px;background:{RED};width:118px;margin-top:26px"></div>
  <p class="d" style="font-style:italic;font-weight:400;font-size:27px;line-height:1.28;
     color:{GOLD};margin-top:24px;max-width:470px">
     32.7 GW of operating and queued power sits within sixty miles. The corridor
     was built before this parcel was offered.</p>
  <div style="flex-grow:1"></div>
  <div class="m" style="font-size:11px;letter-spacing:.14em;color:{INK70};line-height:2">
     1,300 CONTIGUOUS ACRES &middot; NORTH OF I-10<br>
     PECOS COUNTY, TEXAS &middot; AUGUST 2026</div>
</div>"""

cover = raw_page(f"""
<div style="position:absolute;inset:0;display:flex;padding:64px {PAD_X}px 56px">
  <div style="width:494px;flex:none">{cover_left}</div>
  <div style="flex-grow:1"></div>
  <div style="width:600px;height:600px;flex:none;align-self:center">{T.svg("chart_rings_dark")}</div>
</div>
<div style="position:absolute;left:{PAD_X}px;right:{PAD_X}px;bottom:28px;
     border-top:1px solid {RULE};padding-top:9px;display:flex;justify-content:space-between">
  <div class="m" style="font-size:9.5px;letter-spacing:.2em;color:{INK45}">LAND RESOURCE PARTNERS</div>
  <div class="m" style="font-size:9.5px;letter-spacing:.2em;color:{INK45}">EDITORIAL EDITION</div>
</div>""")
_pages.append(cover)


# ===========================================================================
# 02 — The one idea
# ===========================================================================
p2 = page("01 &middot; POSITION", 2, f"""
{kicker("IF THERE ARE ONLY FIVE MINUTES")}
{headline("Not a land bet.<br>A position inside a corridor.", 72, mt=14, maxw=900)}
{deck("Two projects at hyperscale &mdash; 7.65 GW and 2 GW &mdash; sit on the same "
      "north&ndash;south line through the property, at 15.5 and 19.3 miles.", 25, mt=20, maxw=940)}
<div style="flex-grow:1"></div>
{numrow([
    bignum("1,300", "MAXIMUM CONTIGUOUS ACRES", "North side of I-10, five miles from Fort Stockton. "
           "No county zoning ordinance &mdash; industrial and energy use as of right.", 70),
    bignum("32.7 GW", "OPERATING + QUEUED, &le;60 MI", "Caramba North sits inside that radius, "
           "not adjacent to it. 53.5 GW within 100 miles.", 70),
    bignum("79.3%", "OF ANCHOR CAPACITY BUILDING", "Share of the two anchors&rsquo; combined announced "
           "megawatts already under construction rather than proposed.", 70),
], gap=42)}
{rule(mt=34, color=INK12)}
{body("Water and gas are already permitted rather than applied for: 47,418 AF/yr of Middle Pecos "
      "groundwater rights on adjacent affiliated lands, and an indicative 15-year, 200,000 MMBtu/day "
      "supply quote at Waha-index pricing. The site is fifteen miles from Solstice Substation, the "
      "western terminus of all three PUCT-approved 765 kV Permian import paths.", 14.5, mt=18, maxw=1050)}
""")
_pages.append(p2)


# ===========================================================================
# 03 — Full-bleed corridor map
# ===========================================================================
p3 = raw_page(f"""
<div style="position:absolute;left:500px;top:150px;width:801px;height:570px">
  {T.svg("corridor_bare_dark")}
</div>
<div style="position:absolute;left:{PAD_X}px;right:{PAD_X}px;top:40px">
  {kicker("02 &middot; THE CORRIDOR")}
  <div style="display:flex;align-items:flex-start;gap:44px;margin-top:10px">
    <h1 class="d" style="font-weight:400;font-size:58px;line-height:0.98;letter-spacing:-0.02em;
        color:{INK};flex:none;max-width:410px">The line runs<br>through the tract.</h1>
    <p class="d" style="font-style:italic;font-weight:400;font-size:21px;line-height:1.3;
       color:{GOLD};max-width:530px;padding-top:6px">
       GW Ranch sits almost due north of Caramba North and Longfellow almost due south &mdash;
       the property is on the line between them, not off to one side.</p>
  </div>
</div>
<div style="position:absolute;left:{PAD_X}px;top:232px;width:410px">
  {kicker("WHAT IS ON THE MAP")}
  <div style="margin-top:6px">
    {keyline(1, "GW Ranch", "15.5 mi north &middot; under construction")}
    {keyline(2, "Longfellow", "19.3 mi south &middot; phase-1 site work")}
  </div>
  <div style="font-size:12.5px;line-height:1.5;font-weight:300;color:{INK70};margin-top:16px">
    Both anchors are plotted at their disclosed site points. Caramba North is the only
    drawn boundary on the map &mdash; neither anchor&rsquo;s ranch parcel is outlined,
    because the disclosed locations are recorded as approximate.</div>
  <div style="height:1px;background:{INK25};margin-top:24px"></div>
  <div style="display:flex;gap:30px;margin-top:14px">
    <div><div class="m" style="font-size:9.5px;letter-spacing:.2em;color:{INK70}">&le;30 MI</div>
      <div class="d" style="font-size:40px;line-height:1.05;color:{INK};margin-top:4px">8.9 GW</div></div>
    <div><div class="m" style="font-size:9.5px;letter-spacing:.2em;color:{INK70}">&le;60 MI</div>
      <div class="d" style="font-size:40px;line-height:1.05;color:{INK};margin-top:4px">32.7 GW</div></div>
  </div>
  <div style="font-size:12.5px;line-height:1.5;font-weight:300;color:{INK70};margin-top:12px">
    Operating plus ERCOT-queued capacity, cumulative by radius from the tract. The dashed
    rings on the map are drawn at 10, 15 and 30 miles.</div>
</div>
<div style="position:absolute;left:{PAD_X}px;bottom:32px;right:{PAD_X}px;
     display:flex;justify-content:space-between;align-items:baseline">
  <span class="m" style="font-size:9.5px;letter-spacing:.22em;color:{INK45}">
    DRAWN FROM SOURCE GEOMETRY &mdash; HIFLD, ERCOT, PUCT, TIGER</span>
  <span class="m" style="font-size:10.5px;color:{INK70}">03</span>
</div>""")
_pages.append(p3)


# ===========================================================================
# 04 — Transmission
# ===========================================================================
subs = [("Fort Stockton Plant", "2.0 mi", "138/69 kV"),
        ("Airport", "3.3 mi", "138 kV"),
        ("Fort Stockton", "5.4 mi", "69 kV"),
        ("16th Street", "6.0 mi", "138/69 kV"),
        ("Northern Natural", "7.0 mi", "&mdash;"),
        ("Gomez", "9.7 mi", "&mdash;")]
sub_rows = "".join(
    f'<div style="display:flex;justify-content:space-between;align-items:baseline;'
    f'padding:9px 0;border-bottom:1px solid {INK12}">'
    f'<div style="font-size:14px;font-weight:400;color:{INK}">{n}</div>'
    f'<div style="display:flex;gap:26px">'
    f'<div class="m" style="font-size:12px;color:{INK45};width:96px;text-align:right;'
    f'white-space:nowrap">{kv}</div>'
    f'<div class="m" style="font-size:13px;color:{INK70};width:58px;text-align:right">{d}</div>'
    f'</div></div>' for n, d, kv in subs)

tpit_note = note("141 substation and 133 line upgrades are tracked ERCOT-wide under TPIT. "
                 "That is the queue of <em style='color:" + INK70 + "'>planned</em> grid work, "
                 "not built capacity &mdash; read it as pipeline context.", mt=10)

p4 = page("03 &middot; TRANSMISSION", 4, f"""
<div style="display:flex;gap:64px;height:100%">
  <div style="flex:1;min-width:0;display:flex;flex-direction:column">
    {kicker("TRANSMISSION")}
    {headline("The decision<br>was made upstream.", 66, mt=14)}
    {deck("Fifteen miles from the delivery point of all three approved 765 kV Permian "
          "import paths &mdash; the transmission question was settled above this site, "
          "not at it.", 23, mt=20, maxw=520)}
    <div style="flex-grow:1"></div>
    {numrow([
        bignum("15 mi", "TO SOLSTICE SUBSTATION", "AEP / CPS Energy. Western terminus of the "
               "PUCT-approved Permian import lines, approved 24 Apr 2025.", 58),
        bignum("6", "SUBSTATIONS WITHIN 10 MI", "The nearest is two miles out at 138/69 kV &mdash; "
               "local delivery exists before any new build.", 58),
    ], gap=40)}
  </div>
  <div style="width:432px;flex:none;display:flex;flex-direction:column">
    {kicker("LOCAL SUBSTATIONS WITHIN TEN MILES")}
    <div style="margin-top:14px;border-top:1px solid {INK25}">{sub_rows}</div>
    {note("PBRP Docket No. 55718 &middot; PUCT order 24 Apr 2025.", mt=20)}
    {tpit_note}
  </div>
</div>
""")
_pages.append(p4)


# ===========================================================================
# 05 — Water
# ===========================================================================
p5 = page("04 &middot; WATER", 5, f"""
{kicker("WATER")}
{headline("The water conversation<br>is closed, not open.", 70, mt=14, maxw=960)}
{deck("47,418 acre-feet per year &mdash; roughly two-thirds of every industrial water right "
      "the Middle Pecos Groundwater Conservation District has issued &mdash; is already permitted "
      "on adjacent affiliated lands.", 25, mt=20, maxw=980)}
<div style="flex-grow:1"></div>
{numrow([
    bignum("47,418", "ACRE-FEET PER YEAR, PERMITTED", "Held on adjacent affiliated lands rather than "
           "sought through a pending application.", 68),
    bignum("42.3", "MILLION GALLONS PER DAY", "The same right expressed at the rate a cooling load "
           "would actually draw it.", 68),
    bignum("&#8532;", "OF DISTRICT INDUSTRIAL RIGHTS", "Approximate share of all Middle Pecos GCD "
           "industrial water rights sitting in this position.", 68),
], gap=42)}
{rule(mt=32, color=INK12)}
{body("The source is the Edwards&ndash;Trinity (Plateau) aquifer, which held recharge through the "
      "1950s drought of record &mdash; the reference event West Texas water planning is still "
      "measured against.", 14.5, mt=18, maxw=1000)}
""")
_pages.append(p5)


# ===========================================================================
# 06 — Natural gas
# ===========================================================================
p6 = page("05 &middot; NATURAL GAS", 6, f"""
<div style="display:flex;gap:60px;height:100%">
  <div style="flex:1;min-width:0;display:flex;flex-direction:column">
    {kicker("NATURAL GAS")}
    {headline("A signable quote,<br>not an application.", 66, mt=14)}
    {deck("An indicative supply quote is in hand at Waha-index pricing &mdash; the same structural "
          "basis discount now drawing behind-the-meter generation into this corridor.", 23, mt=20,
          maxw=530)}
    <div style="flex-grow:1"></div>
    {numrow([
        bignum("200,000", "MMBTU PER DAY, INDICATIVE", "Counterparty-supplied terms: 15-year "
               "tenor, Waha-index pricing, CIAC $15&ndash;25M, 9&ndash;15 month lead time.", 54),
        bignum("20 mi", "TO THE WAHA HUB", "Close enough that the corridor&rsquo;s new generation "
               "is being sited against Waha basis rather than delivered gas.", 54),
    ], gap=38)}
  </div>
  <div style="width:400px;flex:none;display:flex;flex-direction:column;justify-content:flex-end">
    <div style="border-left:1px solid {INK25};padding-left:28px">
      {kicker("WHY THE BASIS HOLDS")}
      {body("Waha trades at a structural discount to Henry Hub, and printed negative through 2024 "
            "and 2025 as Matterhorn, Blackcomb, Hugh Brinson and GCX rebalanced Permian egress. "
            "Associated gas keeps arriving whether or not the pipe is there to move it.", 14, mt=16)}
      {body("That discount is the reason on-site generation pencils here at all &mdash; and the "
            "reason both anchor campuses in this corridor are being built around their own gas "
            "turbines rather than around a queue position.", 14, mt=14)}
      {note("Quote terms are counterparty-supplied and indicative, not committed.", mt=20)}
    </div>
  </div>
</div>
""")
_pages.append(p6)


# ===========================================================================
# 07 — The two anchors (wide map band)
# ===========================================================================
p7 = raw_page(f"""
<div style="position:absolute;left:0;top:172px;width:1280px;height:548px;overflow:hidden">
  <div style="width:1280px;height:651px;margin-top:-76px">{T.svg("corridor_wide_dark")}</div>
</div>
<div style="position:absolute;left:{PAD_X}px;right:{PAD_X}px;top:40px">
  {kicker("06 &middot; THE ANCHORS")}
  <div style="display:flex;gap:48px;margin-top:8px;align-items:flex-start">
    <h1 class="d" style="font-weight:400;font-size:52px;line-height:0.98;letter-spacing:-0.02em;
        color:{INK};flex:none;max-width:440px">Two anchors,<br>one line.</h1>
    <div style="flex:1;min-width:0">
      <p class="d" style="font-style:italic;font-weight:400;font-size:21px;line-height:1.3;
         color:{GOLD}">9,650 MW of announced capacity sits within twenty miles of the tract
         &mdash; and the larger share of it is already under construction.</p>
      <div style="display:flex;gap:36px;margin-top:14px;align-items:center">
        <div style="display:flex;gap:9px;align-items:center">
          <div class="m" style="flex:none;width:18px;height:18px;border-radius:50%;
               background:{GOLD};color:{PAPER};font-size:10px;line-height:18px;
               text-align:center">1</div>
          <div class="m" style="font-size:11px;color:{INK70};letter-spacing:.02em">
            GW RANCH &middot; 15.5 MI NORTH</div></div>
        <div style="display:flex;gap:9px;align-items:center">
          <div class="m" style="flex:none;width:18px;height:18px;border-radius:50%;
               background:{GOLD};color:{PAPER};font-size:10px;line-height:18px;
               text-align:center">2</div>
          <div class="m" style="font-size:11px;color:{INK70};letter-spacing:.02em">
            LONGFELLOW &middot; 19.3 MI SOUTH</div></div>
      </div>
    </div>
  </div>
</div>
<div style="position:absolute;right:{PAD_X}px;bottom:18px" class="m">
  <span style="font-size:10.5px;color:{INK70}">07</span>
</div>""")
_pages.append(p7)


# ===========================================================================
# 08 — GW Ranch
# ===========================================================================
p8 = page("07 &middot; ANCHOR I", 8, f"""
<div style="display:flex;gap:60px;height:100%">
  <div style="flex:1;min-width:0;display:flex;flex-direction:column">
    <div>{chip("GW RANCH")}<span class="m" style="font-size:10px;letter-spacing:.22em;
         color:{INK45};margin-left:14px">15.5 MI NORTH &middot; PECOS COUNTY</span></div>
    {headline("Under construction,<br>not announced.", 64, mt=18)}
    {deck("The largest air permit issued in the United States this year sits fifteen miles up the "
          "same highway corridor &mdash; and the buildings are already going up against a "
          "December 2026 target.", 23, mt=20, maxw=540)}
    <div style="flex-grow:1"></div>
    {numrow([
        bignum("7.65 GW", "TCEQ AIR PERMIT", "Issued Jan/Feb 2026 across 35 gas turbines, plus "
               "1.8 GW of battery storage and up to 750 MW of solar.", 54),
        bignum("8,000", "ACRE SITE", "Three 189,000 sq ft data-center buildings, Gensler design, "
               "roughly $300M each; ~$12B estimated total project investment.", 54),
    ], gap=38)}
  </div>
  <div style="width:398px;flex:none;display:flex;flex-direction:column;justify-content:flex-end">
    <div style="border-left:1px solid {INK25};padding-left:28px">
      {kicker("OWNERSHIP")}
      {body("Amazon disclosed ownership of the site in August 2026. Pacifico Energy Group, the "
            "prior owner, remains the power-plant developer and operator.", 14, mt=14)}
      {kicker("WHAT THE PERMIT IS &mdash; AND IS NOT", mt=24)}
      {body("The 7.65 GW figure is a TCEQ generation air permit, not an ERCOT interconnection "
            "queue position. No ERCOT filing has been disclosed and the project is off-grid "
            "initially. That distinction matters against the state-level queue context that "
            "follows.", 14, mt=14)}
      {note("TCEQ record locates the site &ldquo;~17 mi north of Fort Stockton on Highway 18&rdquo;; "
            "the 15.5 mi figure here is measured edge-to-edge from the Caramba North tract.", mt=20)}
    </div>
  </div>
</div>
""")
_pages.append(p8)


# ===========================================================================
# 09 — Longfellow + maturity
# ===========================================================================
p9 = page("08 &middot; ANCHOR II", 9, f"""
<div style="display:flex;gap:56px">
  <div style="flex:1;min-width:0">
    <div>{chip("LONGFELLOW")}<span class="m" style="font-size:10px;letter-spacing:.22em;
         color:{INK45};margin-left:14px">19.3 MI SOUTH &middot; PECOS COUNTY</span></div>
    {headline("The corridor&rsquo;s demand for<br>on-site power is not<br>one project deep.", 54, mt=18)}
  </div>
  <div style="width:452px;flex:none;padding-top:26px">
    {deck("A second phased gas-generation campus twenty miles south of the tract, built around "
          "its own turbines and its own permitted non-potable groundwater.", 22, mt=0)}
    {body("568 acres, announced October 2025 as a 2 GW campus in eight 250 MW phases. Planned "
          "on-site generation is aero-derivative turbines with SCR and carbon-capture capability; "
          "cooling is closed-loop on permitted non-potable groundwater. Phase-1 site work is "
          "underway, with the on-site generation build planned in phases.", 14, mt=16)}
    {note("No confirmed ERCOT queue position or TCEQ air-permit record was found for this site as "
          "of August 2026 &mdash; stated as a fact about permitting status. Longfellow&rsquo;s own "
          "public materials place it more than 25 miles outside Fort Stockton.", mt=14)}
  </div>
</div>
<div style="flex-grow:1"></div>
{rule(mt=0, mb=22, color=INK12)}
<div style="display:flex;gap:56px;align-items:flex-end">
  <div style="width:520px;flex:none">
    {kicker("PROJECT MATURITY")}
    <div style="width:520px;height:176px;margin-top:6px">{T.svg("chart_maturity_dark")}</div>
  </div>
  <div style="flex:1;min-width:0;padding-bottom:16px">
    <p class="d" style="font-style:italic;font-weight:400;font-size:27px;line-height:1.26;
       color:{INK};max-width:480px">The regional pipeline around this tract is
       majority-built, not majority-speculative.</p>
    {note("Share of 9,650 MW combined announced capacity across the two profiled anchors.", mt=16)}
  </div>
</div>
""")
_pages.append(p9)


# Pecos County operating fleet, drawn in HTML/CSS rather than via the shared
# chart_power_mix exhibit. The label collision that first forced this has been
# fixed upstream (the exhibit is now 620x310 with a reserved gutter), so this
# is now a typographic choice, not a workaround: at the 496px column this page
# allows, the SVG would render at 0.8 scale and its labels would fall below the
# 11px floor the rest of the deck holds. Same data, same chart spec — one
# recessive axis, thin marks, direct labels, identity never by color alone.
MIX = [("Solar", 2178, 13), ("Wind", 542, 5), ("Storage", 505, 6), ("Gas", 1, 1)]
_mixmax = max(v for _, v, _ in MIX)
mixbars = "".join(
    f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:13px">'
    f'<div style="flex:none;width:62px;font-size:12.5px;color:{INK70};text-align:right">{n}</div>'
    f'<div style="flex:1;min-width:0"><div style="width:{max(v / _mixmax * 100, 0.5):.1f}%;'
    f'height:15px;background:{BLUE};border-radius:0 3px 3px 0"></div></div>'
    f'<div class="m" style="flex:none;width:78px;font-size:12px;color:{INK};text-align:right">'
    f'{v:,} MW</div>'
    f'<div class="m" style="flex:none;width:54px;font-size:11px;color:{INK45};text-align:right">'
    f'{c} proj.</div></div>'
    for n, v, c in MIX)


# ===========================================================================
# 10 — Regional power cluster
# ===========================================================================
p10 = page("09 &middot; POWER CLUSTER", 10, f"""
<div style="display:flex;gap:60px;height:100%">
  <div style="flex:1;min-width:0;display:flex;flex-direction:column">
    {kicker("REGIONAL POWER CLUSTER")}
    {headline("Twelve gigawatts<br>are queued in this<br>county alone.", 62, mt=14)}
    {deck("And that is before counting either anchor campus &mdash; the county was already a "
          "generation county before the data centers arrived.", 22, mt=18, maxw=500)}
    <div style="flex-grow:1"></div>
    {numrow([
        bignum("12,039", "MW QUEUED &middot; PECOS COUNTY", "Across 39 ERCOT queue projects. "
               "3,973 MW of it sits within twenty miles of the tract.", 52),
        bignum("31,607", "MW QUEUED &middot; SIX ADJACENT", "Reeves, Crane, Ward, Upton, Ector and "
               "Crockett add 24,585 MW queued on 7,022 MW operating.", 52),
    ], gap=36)}
  </div>
  <div style="width:496px;flex:none;display:flex;flex-direction:column;justify-content:center">
    {kicker("PECOS COUNTY OPERATING CAPACITY")}
    <div style="margin-top:16px">{mixbars}</div>
    {note("Megawatts in service &middot; EIA-860. 3,226 MW operating today.", mt=14)}
    {rule(mt=26, mb=16, color=INK12)}
    {kicker("NEAREST OPERATING STORAGE")}
    <div style="display:flex;align-items:baseline;gap:14px;margin-top:10px">
      <div class="d" style="font-size:42px;line-height:1;color:{INK}">1.9 mi</div>
      <div style="font-size:13.5px;color:{INK70};font-weight:300">St. Gall Energy Storage I<br>
        <span class="m" style="font-size:11px;color:{INK45}">103 MW BESS &middot; operating</span></div>
    </div>
  </div>
</div>
""")
_pages.append(p10)


# ===========================================================================
# 11 — State queue context
# ===========================================================================
p11 = page("10 &middot; STATE CONTEXT", 11, f"""
<div style="display:flex;gap:64px;height:100%">
  <div style="flex:1;min-width:0;display:flex;flex-direction:column">
    {kicker("STATE-LEVEL CONTEXT")}
    {headline("The demand signal<br>became a policy<br>problem.", 64, mt=14)}
    {deck("ERCOT&rsquo;s large-load queue went from 63 GW to roughly 474 GW in twenty months, about "
          "90% of it data centers &mdash; large enough to trigger a state audit and a pause of the "
          "Batch Zero review.", 22, mt=18, maxw=520)}
    <div style="flex-grow:1"></div>
    {body("That is a different claim than &ldquo;this area is growing.&rdquo; The 32.7 GW around "
          "Caramba North sits inside a statewide queue that got big enough to create a regulatory "
          "problem. The distinction cuts both ways: it is why the corridor is real, and it is why a "
          "position with water and gas already permitted &mdash; rather than one more marginal "
          "interconnection request &mdash; is the safer place to stand.", 14.5, mt=0, maxw=520)}
    {note("Sources: Latitude Media, 3 Dec 2025; Utility Dive, Aug 2026. Full citations at the back.", mt=18)}
  </div>
  <div style="width:470px;flex:none;display:flex;flex-direction:column;justify-content:center">
    <div style="width:470px;height:336px">{T.svg("chart_queue_growth_dark")}</div>
    {rule(mt=22, mb=0, color=INK12)}
    {note("Gov. Abbott&rsquo;s 3 Aug 2026 directive orders an audit of all ERCOT-queue data centers "
          "and pauses the &ldquo;Batch Zero&rdquo; large-load review pending its outcome. The backlog "
          "he cites is more than five times the state&rsquo;s record peak demand.", mt=16, size=11.5)}
  </div>
</div>
""")
_pages.append(p11)


# ===========================================================================
# 12 — Subsurface
# ===========================================================================
p12 = page("11 &middot; SUBSURFACE", 12, f"""
{kicker("SUBSURFACE &amp; DRILLING ACTIVITY")}
<div style="display:flex;gap:52px;align-items:flex-start;margin-top:12px">
  <h1 class="d" style="font-weight:400;font-size:62px;line-height:0.98;letter-spacing:-0.02em;
      color:{INK};flex:none;max-width:440px">The quietest<br>of the seven.</h1>
  <p class="d" style="font-style:italic;font-weight:400;font-size:22px;line-height:1.3;
     color:{GOLD};max-width:600px;padding-top:6px">
     Pecos County recorded 115 new-drill wellbore events since 2020 against a peer average of
     1,181 &mdash; roughly 90% below &mdash; and not one of them fell within five miles of this tract.</p>
</div>
<div style="display:flex;gap:52px;margin-top:26px;flex-grow:1;min-height:0">
  <div style="width:752px;flex:none;height:359px">{T.svg("chart_peer_drilling_dark")}</div>
  <div style="flex:1;min-width:0;display:flex;flex-direction:column;justify-content:flex-start">
    <div style="display:flex;gap:26px">
      {bignum("0", "NEW DRILLS &le;5 MI", "Since 2020. The nearest is 9.37 miles out; beyond ten "
              "miles the median is 19.9 mi.", 62)}
      {bignum("83%", "MARGINAL &le;10 MI", "Share of non-plugged wellbores in end-of-life "
              "production &mdash; the near ring is quieter than the wide one.", 62)}
    </div>
    {note("115 new-drill events out of 1,140 total RRC wellbore events in the county since 2020 "
          "&mdash; a 10% new-drill share; the rest are workovers and reworks.", mt=26)}
  </div>
</div>
""")
_pages.append(p12)


# ===========================================================================
# 13 — What you are buying
# ===========================================================================
items = [
    ("Land", "1,300 contiguous acres, I-10 frontage, no zoning ordinance &mdash; industrial and "
             "energy use as of right, five miles from Fort Stockton services and its regional airport."),
    ("Transmission", "Fifteen miles from Solstice Substation, the western terminus of all three "
                     "PUCT-approved 765 kV Permian import paths; six substations inside ten miles."),
    ("Water", "47,418 AF/yr permitted on adjacent affiliated lands &mdash; about two-thirds of the "
              "district&rsquo;s industrial rights &mdash; from the Edwards&ndash;Trinity (Plateau) aquifer."),
    ("Gas", "An indicative 15-year, 200,000 MMBtu/day quote at Waha-index pricing, twenty miles "
            "from the hub."),
    ("Corridor", "9,650 MW announced within twenty miles, 79.3% of it under construction; "
                 "32.7 GW operating and queued within sixty."),
    ("Subsurface", "Zero new-drill wells within five miles since 2020, in the lowest-activity "
                   "county of seven comparable Permian peers."),
]
rows = "".join(
    f'<div style="display:flex;gap:24px;padding:11px 0;border-bottom:1px solid {INK12}">'
    f'<div class="m" style="flex:none;width:118px;font-size:10px;letter-spacing:.2em;'
    f'color:{GOLD};padding-top:4px">{k.upper()}</div>'
    f'<div style="font-size:13.5px;line-height:1.55;font-weight:300;color:{INK70}">{v}</div></div>'
    for k, v in items)

p13 = page("12 &middot; THE POSITION", 13, f"""
<div style="display:flex;gap:60px;height:100%">
  <div style="width:452px;flex:none;display:flex;flex-direction:column">
    {kicker("WHAT IS ACTUALLY BEING SOLD")}
    {headline("Permitted<br>adjacency.", 74, mt=14)}
    {deck("Everything the corridor needs next is already permitted here rather than applied for "
          "&mdash; which is the one thing a queue position cannot buy.", 22, mt=20)}
    <div style="flex-grow:1"></div>
    <div style="border-top:1px solid {INK25};padding-top:16px">
      {kicker("THE DILIGENCE PLATFORM")}
      {body("Every point, line and boundary behind these figures traces to a cited public dataset "
            "&mdash; ERCOT GIS Report and TPIT, PUCT, EIA-860, TCEQ, RRC, FracFocus, Middle Pecos "
            "GCD, HIFLD, USGS, BTS and Census TIGER &mdash; with per-feature source popups. "
            "Every figure here is independently re-derivable.", 13.5, mt=12)}
    </div>
  </div>
  <div style="flex:1;min-width:0;display:flex;flex-direction:column;justify-content:center">
    <div style="border-top:1px solid {INK25}">{rows}</div>
    {note("RRC refreshes weekly; ERCOT queue and TPIT monthly; EIA, USGS and OSM annually. "
          "Static, versioned build; deployed bundle byte-verified on release; access logged.", mt=18)}
  </div>
</div>
""")
_pages.append(p13)


# ===========================================================================
# 14 — Notes, method, sources
# ===========================================================================
p14 = page("13 &middot; NOTES", 14, f"""
{kicker("NOTES ON METHOD AND SOURCES")}
<div style="display:flex;gap:52px;align-items:flex-start;margin-top:12px">
  <h1 class="d" style="font-weight:400;font-size:56px;line-height:0.98;letter-spacing:-0.02em;
      color:{INK};flex:none;max-width:400px">How the numbers<br>were measured.</h1>
  <p class="d" style="font-style:italic;font-weight:400;font-size:21px;line-height:1.3;
     color:{GOLD};max-width:600px;padding-top:4px">
     Distances here are edge-to-edge from the tract boundary, which is the shorter and the more
     conservative of the two conventions to defend.</p>
</div>
<div style="display:flex;gap:52px;margin-top:32px;flex-grow:1;min-height:0">
  <div style="flex:1;min-width:0">
    {kicker("DISTANCE METHODOLOGY")}
    {body("Distances to GW Ranch and Longfellow are measured edge-to-edge: from the nearest point "
          "on the Caramba North tract boundary to each site&rsquo;s disclosed location, rather than "
          "centroid-to-centroid. Edge-to-edge is consistently shorter than a straight centroid "
          "measurement because Caramba North&rsquo;s own tract has spatial extent. GW Ranch: 15.5 mi "
          "(vs. 17.3 mi centroid). Longfellow: 19.3 mi (vs. 19.7 mi centroid) &mdash; Longfellow&rsquo;s "
          "own public site describes its location as more than 25 miles outside Fort Stockton, "
          "consistent with the longer figure; this distance should not be represented as shorter.",
          13.5, mt=12)}
    {kicker("PUBLIC REPORTING CITED", mt=24)}
    {note("Latitude Media, &ldquo;ERCOT&rsquo;s large load queue has nearly quadrupled in a single "
          "year&rdquo; (3 Dec 2025).", mt=10)}
    {note("Utility Dive, &ldquo;Facing an estimated 474 GW of interconnection requests, Texas hits "
          "pause on data centers&rdquo; (Aug 2026).", mt=6)}
    {note("PUCT Permian Basin Reliability Plan, Docket No. 55718, order of 24 Apr 2025.", mt=6)}
  </div>
  <div style="width:452px;flex:none;border-left:1px solid {INK25};padding-left:30px">
    {kicker("DATA SOURCES")}
    {note("ERCOT GIS Report and TPIT &middot; PUCT &middot; EIA-860 &middot; TCEQ &middot; RRC "
          "dbf900, production and W-1 &middot; FracFocus &middot; Middle Pecos GCD &middot; HIFLD "
          "&middot; USGS &middot; BTS &middot; Census TIGER.", mt=10)}
    {kicker("NOTICES", mt=26)}
    {body("Confidential offering memorandum prepared for a limited number of prospective "
          "counterparties under non-disclosure agreement. This is not an offer to sell or a "
          "solicitation of an offer to buy any security. Information is preliminary and indicative, "
          "drawn from sources believed reliable but not independently verified. Public data is "
          "drawn from the sources listed above; third-party transaction news is sourced to the "
          "public reporting cited in the companion source register. Gas supply terms are "
          "counterparty-supplied and indicative.", 12.5, mt=12, lh=1.6)}
  </div>
</div>
""")
_pages.append(p14)


# ---------------------------------------------------------------------------
def main():
    out = T.REPO / "outputs" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    html = T.document("editorial", "\n".join(_pages), "landscape",
                      "Caramba North — Editorial")
    hp = out / "Caramba-North-Deck-Editorial.html"
    hp.write_text(html, encoding="utf-8")
    print(f"html -> {hp.relative_to(T.REPO)}  ({hp.stat().st_size // 1024} KB, {len(_pages)} pages)")
    pp = out / "Caramba-North-Deck-Editorial.pdf"
    T.render_pdf(str(hp), str(pp))
    print(f"pdf  -> {pp.relative_to(T.REPO)}")


if __name__ == "__main__":
    main()
