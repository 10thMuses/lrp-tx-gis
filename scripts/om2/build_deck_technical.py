#!/usr/bin/env python3
"""Caramba North — Technical deck (system key: `technical`).

An engineering drawing set rather than a slide deck: numbered sheets, a title
block band across the top of every sheet carrying sheet number / section /
project / source / issue, a faint modular background grid, framed exhibit
plates sized to the exact aspect of the SVG they carry, and numbered tables
(TBL 04.1). Prose is converted to labelled callouts and table rows; IBM Plex
Mono carries every figure.

Facts, headline and subheading copy come from docs/redesign_content_brief.md
(§0-§4 binding). Distances are edge-to-edge: 15.5 mi (GW Ranch) and 19.3 mi
(Longfellow); the centroid figures appear only inside the §4 methodology note
on the final sheet.

    python3 scripts/om2/build_deck_technical.py
"""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import om_theme as T          # noqa: E402
import om_charts as C         # noqa: E402
import build_vector_maps as M  # noqa: E402

S = T.SYSTEMS["technical"]
INK, INK70, INK45, INK25, INK12 = S["ink"], S["ink70"], S["ink45"], S["ink25"], S["ink12"]
RULE = S["rule"]
BLUE, RED, GOLD = S["accent"], S["second"], S["third"]
PLATE_BG = "#FBFAF7"          # the exhibit plates' own paper (matches the SVGs)

OUT = T.REPO / "outputs" / "reports"
STEM = "Caramba-North-Deck-Technical"

TOTAL_SHEETS = 13

# ---------------------------------------------------------------------------
# Exhibit plumbing
# ---------------------------------------------------------------------------
_VB = re.compile(r'viewBox="0 0 ([\d.]+) ([\d.]+)"')


def ratio(name):
    """Aspect ratio of a built vector exhibit, so plates never letterbox."""
    s = (T.VEC / f"{name}.svg").read_text(encoding="utf-8")
    w, h = _VB.search(s).groups()
    return float(w) / float(h)


_UID = [0]


def uniq_ids(svg_text):
    """Namespace every element id in an inlined SVG.

    Every exhibit lands in ONE html document, and the corridor maps each carry
    a `<clipPath id="mapclip">`. Duplicate ids collapse: `url(#mapclip)` on the
    third map resolves to the FIRST map's clip rect, in the third map's own
    user units — which silently crops the later maps (this cost the corridor
    sheet its southern anchor). The shared exhibit files cannot be edited, so
    the ids are rewritten on the way in.
    """
    ids = set(re.findall(r'\sid="([^"]+)"', svg_text))
    if not ids:
        return svg_text
    _UID[0] += 1
    for i in ids:
        n = f"{i}-x{_UID[0]}"
        svg_text = (svg_text.replace(f'id="{i}"', f'id="{n}"')
                            .replace(f"url(#{i})", f"url(#{n})")
                            .replace(f'href="#{i}"', f'href="#{n}"'))
    return svg_text


def inline(svg_text):
    """Inline an in-memory SVG string the same way om_theme.svg() does."""
    s = re.sub(r'\s(width|height)="[\d.]+"', "", svg_text, count=2)
    s = s.replace("<svg ", '<svg preserveAspectRatio="xMidYMid meet" '
                  'style="width:100%;height:100%;display:block" ', 1)
    return uniq_ids(s)


def chart(fn, **kw):
    """Chart rendered transparent so it sits on the plate's own paper."""
    return inline(fn(dark=False, transparent=True, **kw))


def plate(inner, w, h, fig, caption, pad=0, bg=PLATE_BG):
    """A framed exhibit plate with a drafting-style figure caption beneath."""
    return f"""
<div style="width:{w}px">
  <div style="width:{w}px;height:{h}px;border:1px solid {RULE};background:{bg};
              padding:{pad}px;overflow:hidden">{inner}</div>
  <div class="m" style="margin-top:6px;font-size:9px;letter-spacing:.13em;
       color:{INK45};text-transform:uppercase">
    <span style="color:{BLUE};font-weight:600">{fig}</span>&nbsp;&nbsp;{caption}</div>
</div>"""


def exhibit(name, w=None, h=None, fig="", caption=""):
    r = ratio(name)
    if w is None:
        w = int(round(h * r))
    if h is None:
        h = int(round(w / r))
    return plate(uniq_ids(T.svg(name)), w, h, fig, caption)


_MAPDATA = None


def map_plate(w, h, fig, caption, **kw):
    """Corridor map generated in-memory at the plate's own pixel size.

    The prebuilt corridor SVGs are drawn at 900-1360 px and then scaled down
    into a plate, which shrinks their type with them. Rendering the same shared
    function at the plate's exact geometry keeps label type at full size and
    lets the sheet pick its own span. build_vector_maps.py is shared and is
    only ever called here, never edited.
    """
    global _MAPDATA
    if _MAPDATA is None:
        _MAPDATA = M.load()
    svg = M.map_corridor(_MAPDATA, width=w, height=h, dark=False,
                         show_rail=False, **kw)
    return plate(inline(svg), w, h, fig, caption)


def chart_plate(fn, w=None, h=None, fig="", caption="", src_w=None, src_h=None, **kw):
    """Charts are generated in-memory (transparent ground) at native size."""
    r = src_w / src_h
    if w is None:
        w = int(round(h * r))
    if h is None:
        h = int(round(w / r))
    return plate(chart(fn, **kw), w, h, fig, caption)


# ---------------------------------------------------------------------------
# Sheet shell
# ---------------------------------------------------------------------------
def cell(label, value, width=None, flex=False, mono_size=11.5, weight="500"):
    w = f"width:{width}px;" if width else ""
    f = "flex:1;min-width:0;" if flex else ""
    return f"""<div style="{w}{f}border-right:1px solid {RULE};padding:9px 12px 0;
     display:flex;flex-direction:column;justify-content:flex-start;overflow:hidden">
  <div class="m" style="font-size:7.6px;letter-spacing:.20em;color:{INK45};
       text-transform:uppercase;line-height:1">{label}</div>
  <div class="m" style="font-size:{mono_size}px;font-weight:{weight};color:{INK};
       margin-top:7px;line-height:1.25;letter-spacing:.02em;white-space:nowrap;
       overflow:hidden;text-overflow:ellipsis">{value}</div>
</div>"""


def sheet(no, section, project_line, source, body, issue="2026-08 · REV A"):
    tb = (
        cell("SHEET", f"{no:02d} <span style='color:{INK45};font-weight:400'>/ {TOTAL_SHEETS}</span>",
             width=104, mono_size=15, weight="600")
        + cell("SECTION", section, width=286)
        + cell("PROJECT", project_line, flex=True)
        + cell("SOURCE", source, width=330)
        + cell("ISSUE", issue, width=138)
    )
    # the last title-block cell drops its right border via .tb > div:last-child
    return f"""
<div class="page">
  <div class="grid"></div>
  <div class="frame">
    <div class="tb">{tb}</div>
    <div class="body">{body}</div>
    <div class="fb">
      <div>CARAMBA NORTH · OFFERING MEMORANDUM · CONFIDENTIAL — DISTRIBUTED UNDER NDA</div>
      <div>PECOS COUNTY, TEXAS</div>
      <div>SHEET {no:02d} OF {TOTAL_SHEETS}</div>
    </div>
  </div>
</div>"""


def head(title, sub, kicker=None):
    k = ""
    if kicker:
        k = (f'<div class="m" style="font-size:9px;letter-spacing:.20em;color:{BLUE};'
             f'text-transform:uppercase;margin-bottom:8px;font-weight:600">{kicker}</div>')
    return f"""
<div style="margin-bottom:14px">
  {k}
  <h2 class="d" style="font-size:25px;font-weight:600;letter-spacing:-0.35px;
      line-height:1.12;color:{INK}">{title}</h2>
  <div style="display:flex;gap:10px;margin-top:8px;align-items:flex-start">
    <div style="width:26px;height:2px;background:{BLUE};margin-top:8px;flex:none"></div>
    <p style="font-size:13.5px;line-height:1.42;color:{INK70};max-width:1080px">{sub}</p>
  </div>
</div>"""


# ---------------------------------------------------------------------------
# Content components
# ---------------------------------------------------------------------------
def tbl(num, title, cols, rows, note=None, width="100%", compact=False):
    """cols: list of (header, align, width|None). rows: list of lists (html ok)."""
    pv = "4.5px" if compact else "6px"
    ths = "".join(
        f'<th style="text-align:{a};padding:0 0 5px {14 if i else 0}px;'
        f'{"width:"+str(w)+"px;" if w else ""}border-bottom:1px solid {INK70};'
        f'font-family:{S["mono"]};font-size:8.2px;letter-spacing:.15em;'
        f'text-transform:uppercase;color:{INK45};font-weight:600;white-space:nowrap">{h}</th>'
        for i, (h, a, w) in enumerate(cols))
    trs = []
    for r in rows:
        tds = []
        for i, ((h, a, w), v) in enumerate(zip(cols, r)):
            mono = "" if a == "left" else f'font-family:{S["mono"]};font-variant-numeric:tabular-nums;'
            tds.append(f'<td style="text-align:{a};padding:{pv} 0 {pv} {14 if i else 0}px;'
                       f'border-bottom:1px solid {INK12};'
                       f'font-size:11.5px;line-height:1.3;color:{INK};{mono}">{v}</td>')
        trs.append("<tr>" + "".join(tds) + "</tr>")
    n = ""
    if note:
        n = (f'<div class="m" style="font-size:8.8px;line-height:1.45;color:{INK45};'
             f'margin-top:7px">{note}</div>')
    label = (f'<div class="m" style="font-size:9px;letter-spacing:.14em;'
             f'text-transform:uppercase;margin-bottom:7px;color:{INK45}">'
             f'<span style="color:{BLUE};font-weight:600">TBL {num}</span>'
             f'&nbsp;&nbsp;{title}</div>') if num else \
        '<div style="height:13px;margin-bottom:7px"></div>'
    return f"""
<div style="width:{width}">
  {label}
  <table style="width:100%">{"<thead><tr>" + ths + "</tr></thead>" if cols else ""}
  <tbody>{"".join(trs)}</tbody></table>
  {n}
</div>"""


def callout(idx, label, value, note="", color=None):
    color = color or BLUE
    return f"""
<div style="display:flex;gap:10px;padding:9px 0;border-top:1px solid {INK12}">
  <div class="m" style="width:20px;height:20px;flex:none;border:1px solid {color};
       color:{color};font-size:9px;font-weight:600;display:flex;align-items:center;
       justify-content:center;line-height:1">{idx}</div>
  <div style="min-width:0">
    <div class="m" style="font-size:8.4px;letter-spacing:.15em;text-transform:uppercase;
         color:{INK45}">{label}</div>
    <div class="m" style="font-size:16px;font-weight:600;color:{INK};margin-top:3px;
         letter-spacing:-0.2px">{value}</div>
    {f'<div style="font-size:10.8px;line-height:1.4;color:{INK70};margin-top:3px">{note}</div>' if note else ''}
  </div>
</div>"""


def keyfig(value, label, unit="", color=None):
    color = color or INK
    return f"""
<div style="flex:1;min-width:0;border-top:2px solid {BLUE};padding-top:8px">
  <div class="m" style="font-size:26px;font-weight:600;letter-spacing:-0.8px;
       color:{color};line-height:1">{value}<span style="font-size:12px;font-weight:500;
       color:{INK45};letter-spacing:0"> {unit}</span></div>
  <div class="m" style="font-size:8.4px;letter-spacing:.14em;text-transform:uppercase;
       color:{INK45};margin-top:7px;line-height:1.4">{label}</div>
</div>"""


def rail_title(t):
    return (f'<div class="m" style="font-size:9px;letter-spacing:.16em;'
            f'text-transform:uppercase;color:{INK45};margin-bottom:8px;'
            f'border-bottom:1px solid {INK25};padding-bottom:6px">{t}</div>')


def note_block(label, text, color=None):
    color = color or GOLD
    return f"""
<div style="border-left:2px solid {color};padding:2px 0 2px 11px">
  <div class="m" style="font-size:8.2px;letter-spacing:.16em;text-transform:uppercase;
       color:{INK45}">{label}</div>
  <div style="font-size:10.8px;line-height:1.45;color:{INK70};margin-top:4px">{text}</div>
</div>"""


# ===========================================================================
# SHEET 01 — TITLE SHEET
# ===========================================================================
INDEX = [
    ("01", "Title sheet — index, ring analysis"),
    ("02", "The property — 1,300 ac, I-10 frontage"),
    ("03", "Transmission — 765 kV terminus"),
    ("04", "Regional power cluster — fleet + queue"),
    ("05", "Water — Middle Pecos GCD rights"),
    ("06", "Natural gas — Waha basis, supply quote"),
    ("07", "Corridor + ring analysis"),
    ("08", "GW Ranch — 7.65 GW, 15.5 mi"),
    ("09", "Longfellow — phased generation, 19.3 mi"),
    ("10", "Queue and policy context"),
    ("11", "Subsurface activity — drilling record"),
    ("12", "Diligence platform — source register"),
    ("13", "Methodology and notices"),
]


def sheet01():
    rings = chart_plate(C.chart_rings, h=428, src_w=620, src_h=620,
                        fig="FIG 01.1",
                        caption="Operating + ERCOT-queued capacity by radius",
                        size=620)
    def idx_rows(items):
        return [[f'<span class="m" style="color:{BLUE};font-weight:600">{n}</span>', t]
                for n, t in items]
    idx_cols = [("SH", "left", 28), ("Section", "left", None)]
    body = f"""
<div style="display:flex;gap:34px;height:100%">
  <div style="flex:1;min-width:0;display:flex;flex-direction:column">
    <div class="m" style="font-size:9px;letter-spacing:.22em;color:{BLUE};
         text-transform:uppercase;font-weight:600">Offering memorandum · drawing set</div>
    <h1 class="d" style="font-size:44px;font-weight:600;letter-spacing:-1.4px;
        line-height:1.02;margin-top:12px;color:{INK}">Caramba North</h1>
    <div class="m" style="font-size:12.5px;letter-spacing:.05em;color:{INK70};
         margin-top:10px">1,300 ACRES · NORTH OF I-10 · PECOS COUNTY, TEXAS</div>
    <div style="display:flex;gap:10px;margin-top:16px;align-items:flex-start">
      <div style="width:26px;height:2px;background:{BLUE};margin-top:9px;flex:none"></div>
      <p style="font-size:14px;line-height:1.45;color:{INK70};max-width:640px">
        Two hyperscale-scale power projects — 7.65 GW and 2 GW — sit at 15.5 and
        19.3 miles on the same north–south line through this tract, inside a
        60-mile radius holding 32.7 GW of operating and queued capacity.</p>
    </div>
    <div style="display:flex;gap:22px;margin-top:22px">
      {keyfig("1,300", "Acres, max contiguous", "ac")}
      {keyfig("15", "Miles to 765 kV terminus", "mi")}
      {keyfig("47,418", "AF/yr water permitted", "")}
      {keyfig("32.7", "GW within 60 miles", "GW")}
    </div>
    <div style="margin-top:22px;display:flex;gap:32px">
      <div style="flex:1;min-width:0">
        {tbl("01.1", "Sheet index", idx_cols, idx_rows(INDEX[:7]), compact=True)}
      </div>
      <div style="flex:1;min-width:0">
        {tbl("", "", idx_cols, idx_rows(INDEX[7:]), compact=True)}
      </div>
    </div>
  </div>
  <div style="width:428px;flex:none;display:flex;flex-direction:column">
    {rings}
    <div style="margin-top:14px">
      {note_block("Bearing note",
                  "GW Ranch bears ~19° and Longfellow ~188° from the tract — the "
                  "property sits on the line between them, not off to one side.", BLUE)}
    </div>
  </div>
</div>"""
    return sheet(1, "00 TITLE SHEET", "CARAMBA NORTH · 1,300 AC · PECOS CO., TX",
                 "EIA-860 · ERCOT QUEUE · RRC · TCEQ", body)


# ===========================================================================
# SHEET 02 — THE PROPERTY
# ===========================================================================
def sheet02():
    ex = map_plate(724, 360, "FIG 02.1",
                   "Site setting — tract, I-10, Fort Stockton and the 765 kV terminus",
                   span_mi=30, anchors=0)
    rows = [
        ["Acreage", "1,300 ac max contiguous"],
        ["Position", "North side of I-10"],
        ["County", "Pecos County, Texas"],
        ["Services", "~5 mi to Fort Stockton"],
        ["Air access", "Regional airport, Fort Stockton"],
        ["Zoning", "No zoning ordinance in effect"],
        ["Permitted use", "Industrial / energy as of right"],
        ["ERCOT zone", "Far West weather zone"],
    ]
    body = head(
        "The property",
        "As-of-right industrial land inside the fastest-growing load pocket in "
        "ERCOT — this is a siting decision, not a rezoning story.",
        "2.1 Site parameters") + f"""
<div style="display:flex;gap:30px">
  <div style="flex:none">
    {ex}
    <div style="margin-top:16px;width:724px">
      {note_block("Reading this sheet set",
                  "Only the tract is drawn as a boundary — it is the set's one surveyed "
                  "polygon. The feature anchors are plotted on sheets 07 and 08 as "
                  "numbered site points, keyed in TBL 07.2; distances are measured from "
                  "the tract boundary (basis on sheet 13).", BLUE)}
    </div>
  </div>
  <div style="flex:1;min-width:0;display:flex;flex-direction:column">
    {tbl("02.1", "Site parameters",
         [("Parameter", "left", 128), ("Value", "left", None)], rows)}
    <div style="margin-top:16px">
      {callout("01", "Entitlement", "No zoning ordinance",
               "Industrial and energy use are permitted as of right; there is no "
               "rezoning or use-variance step on the critical path.")}
      {callout("02", "Load pocket", "Far West weather zone",
               "ERCOT's highest-growth large-load pocket by interconnection request "
               "volume.", RED)}
    </div>
  </div>
</div>"""
    return sheet(2, "2.1 THE PROPERTY", "CARAMBA NORTH · 1,300 AC · PECOS CO., TX",
                 "GIS TRACT LAYER · CENSUS TIGER · BTS", body)


# ===========================================================================
# SHEET 03 — TRANSMISSION
# ===========================================================================
SUBS = [("Fort Stockton Plant", "138 / 69 kV", 2.0),
        ("Airport", "138 kV", 3.3),
        ("Fort Stockton", "69 kV", 5.4),
        ("16th Street", "138 / 69 kV", 6.0),
        ("Northern Natural", "—", 7.0),
        ("Gomez", "—", 9.7),
        ("Solstice (AEP / CPS Energy)", "765 kV terminus", 15.0)]


def ladder(W=690):
    """CSS distance ladder — substations plotted on a 0-16 mile scale."""
    LEFT = 214
    span = W - LEFT - 76
    ticks = ""
    for mi in (0, 4, 8, 12, 16):
        x = LEFT + span * mi / 16
        ticks += (f'<div style="position:absolute;left:{x:.1f}px;top:26px;bottom:26px;'
                  f'width:1px;background:{INK12}"></div>'
                  f'<div class="m" style="position:absolute;left:{x:.1f}px;top:6px;'
                  f'transform:translateX(-50%);font-size:8.6px;color:{INK45}">{mi}</div>')
    rows = ""
    top = 42
    step = 44
    for i, (name, kv, mi) in enumerate(SUBS):
        y = top + i * step
        x = LEFT + span * mi / 16
        subject = mi == 15.0
        col = RED if subject else BLUE
        rows += f"""
<div style="position:absolute;left:14px;top:{y}px;width:{LEFT-28}px;text-align:right">
  <div style="font-size:11px;font-weight:{'600' if subject else '400'};color:{INK if subject else INK70};
       line-height:1.2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{name}</div>
  <div class="m" style="font-size:8.6px;color:{INK45};margin-top:2px">{kv}</div>
</div>
<div style="position:absolute;left:{LEFT}px;top:{y+9}px;width:{x-LEFT:.1f}px;height:1px;
     background:{INK25}"></div>
<div style="position:absolute;left:{x-3.5:.1f}px;top:{y+5.5}px;width:7px;height:7px;
     background:{col};border-radius:50%"></div>
<div class="m" style="position:absolute;left:{x+10:.1f}px;top:{y+2}px;font-size:11px;
     font-weight:{'600' if subject else '400'};color:{INK if subject else INK70}">{mi:.1f} mi</div>"""
    return (f'<div style="position:relative;width:{W}px;height:{top + len(SUBS)*step + 8}px;'
            f'font-family:{S["body"]}">'
            f'<div class="m" style="position:absolute;left:14px;top:6px;font-size:8.4px;'
            f'letter-spacing:.15em;color:{INK45};text-transform:uppercase">Miles from tract</div>'
            f'{ticks}{rows}</div>')


def sheet03():
    W = 690
    ex = plate(ladder(W), W, 358, "FIG 03.1",
               "Substation and 765 kV terminus distances from the tract boundary")
    body = head(
        "Transmission",
        "Fifteen miles from the delivery point of all three PUCT-approved 765 kV "
        "Permian import paths — the transmission decision was made upstream of this site.",
        "2.2 Transmission position") + f"""
<div style="display:flex;gap:30px">
  <div style="flex:none">
    {ex}
    <div style="display:flex;gap:20px;margin-top:16px;width:{W}px">
      {keyfig("6", "Substations within 10 mi", "")}
      {keyfig("2.0", "Miles to nearest substation", "mi")}
      {keyfig("15", "Miles to 765 kV terminus", "mi", RED)}
    </div>
  </div>
  <div style="flex:1;min-width:0">
    {tbl("03.1", "Approved 765 kV import path",
         [("Item", "left", 116), ("Record", "left", None)],
         [["Terminus", "Solstice Substation — AEP / CPS Energy"],
          ["Distance", "15 mi from tract boundary"],
          ["Paths", "Three PUCT-approved 765 kV Permian import lines"],
          ["Approval", "Apr 24, 2025"],
          ["Docket", "PBRP Docket No. 55718"]])}
    <div style="margin-top:18px">
      {tbl("03.2", "Planned grid upgrades (pipeline, not committed)",
           [("Category", "left", None), ("Count", "right", 74)],
           [["Substation upgrades tracked ERCOT-wide", "141"],
            ["Line upgrades tracked ERCOT-wide", "133"]],
           note="Source: ERCOT Transmission Planning Improvement Tool (TPIT). "
                "TPIT is the queue of planned upgrades; cite as pipeline context, "
                "not built or committed capacity.")}
    </div>
  </div>
</div>"""
    return sheet(3, "2.2 TRANSMISSION", "CARAMBA NORTH · 1,300 AC · PECOS CO., TX",
                 "HIFLD · PUCT DOCKET 55718 · ERCOT TPIT", body)


# ===========================================================================
# SHEET 04 — REGIONAL POWER CLUSTER
# ===========================================================================
def sheet04():
    ex = chart_plate(C.chart_power_mix, w=680, src_w=620, src_h=310,
                     fig="FIG 04.1",
                     caption="Pecos County operating capacity by technology, "
                             "with project counts")
    body = head(
        "Regional power cluster",
        "12,039 MW is already queued in Pecos County alone — before counting the "
        "two campuses on sheets 08 and 09 — against 3,226 MW operating today.",
        "2.3 Generation, operating and queued") + f"""
<div style="display:flex;gap:30px">
  <div style="flex:none">
    {ex}
    <div style="display:flex;gap:20px;margin-top:16px;width:680px">
      {keyfig("3,226", "MW operating, Pecos Co.", "MW")}
      {keyfig("12,039", "MW queued, Pecos Co.", "MW")}
      {keyfig("39", "Queued projects", "")}
    </div>
  </div>
  <div style="flex:1;min-width:0">
    {tbl("04.1", "Capacity by geography",
         [("Geography", "left", None), ("Operating", "right", 88), ("Queued", "right", 88)],
         [["Pecos County", "3,226 MW", "12,039 MW"],
          ["Adjacent six counties", "7,022 MW", "24,585 MW"],
          ["Within 20 mi of tract", "—", "3,973 MW"]],
         note="Adjacent counties: Reeves, Crane, Ward, Upton, Ector, Crockett. "
              "Within 20 mi: 13 queued projects.")}
    <div style="margin-top:16px">
      {tbl("04.2", "Pecos County operating fleet",
           [("Technology", "left", None), ("MW", "right", 78)],
           [["Solar", "2,178"], ["Wind", "542"],
            ["Storage (BESS)", "505"], ["Gas", "1"]],
           note="Tabulated form of FIG 04.1; project counts are carried on the "
                "figure. Gas is 1 MW across 1 project — below the resolution of "
                "the plotted bar.")}
    </div>
    <div style="margin-top:16px">
      {note_block("Nearest operating storage",
                  "St. Gall Energy Storage I — 103 MW BESS, 1.9 mi from the tract "
                  "boundary.", BLUE)}
    </div>
  </div>
</div>"""
    return sheet(4, "2.3 REGIONAL POWER CLUSTER", "CARAMBA NORTH · 1,300 AC · PECOS CO., TX",
                 "EIA-860 · ERCOT GIS REPORT (QUEUE)", body)


# ===========================================================================
# SHEET 05 — WATER
# ===========================================================================
def water_diagram():
    """Share block: permitted rights as ~2/3 of district industrial rights."""
    W, H = 660, 366
    bar_x, bar_y, bar_w, bar_h = 28, 138, W - 56, 88
    subj_w = bar_w * 2 / 3
    hatch = f"""
<svg style="position:absolute;left:0;top:0;width:{W}px;height:{H}px" xmlns="http://www.w3.org/2000/svg">
  <defs><pattern id="hx" width="7" height="7" patternUnits="userSpaceOnUse"
      patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="7" stroke="{INK45}" stroke-width="1" opacity="0.55"/></pattern></defs>
  <rect x="{bar_x + subj_w + 2:.1f}" y="{bar_y}" width="{bar_w - subj_w - 2:.1f}"
        height="{bar_h}" fill="url(#hx)" stroke="{INK25}" stroke-width="1"/>
</svg>"""
    return f"""
<div style="position:relative;width:{W}px;height:{H}px;font-family:{S['body']}">
  <div class="m" style="position:absolute;left:{bar_x}px;top:26px;font-size:8.6px;
       letter-spacing:.16em;text-transform:uppercase;color:{INK45}">
    Middle Pecos GCD — permitted industrial water rights</div>
  <div style="position:absolute;left:{bar_x}px;top:54px;width:{bar_w}px">
    <div class="m" style="font-size:34px;font-weight:600;letter-spacing:-1px;color:{BLUE};
         line-height:1">47,418<span style="font-size:14px;color:{INK45};font-weight:500">
         AF/yr</span>
      <span class="m" style="font-size:14px;color:{INK70};font-weight:500;
            letter-spacing:0;margin-left:14px">= 42.3 MGD</span></div>
  </div>
  {hatch}
  <div style="position:absolute;left:{bar_x}px;top:{bar_y}px;width:{subj_w:.1f}px;
       height:{bar_h}px;background:{BLUE}"></div>
  <div class="m" style="position:absolute;left:{bar_x + 14}px;top:{bar_y + 33}px;
       color:#FFFFFF;font-size:15px;font-weight:600;letter-spacing:.04em">
    ~2/3 — PERMITTED TO THIS POSITION</div>
  <div class="m" style="position:absolute;left:{bar_x + subj_w + 14:.1f}px;
       top:{bar_y + 35}px;color:{INK45};font-size:11px">BALANCE OF DISTRICT</div>
  <div style="position:absolute;left:{bar_x}px;top:{bar_y + bar_h + 22}px;
       width:{bar_w}px;display:flex;gap:26px">
    <div style="flex:1;border-top:1px solid {INK25};padding-top:8px">
      <div class="m" style="font-size:8.4px;letter-spacing:.15em;text-transform:uppercase;
           color:{INK45}">Source aquifer</div>
      <div style="font-size:11.5px;color:{INK};margin-top:4px;line-height:1.35">
        Edwards–Trinity (Plateau)</div>
    </div>
    <div style="flex:1;border-top:1px solid {INK25};padding-top:8px">
      <div class="m" style="font-size:8.4px;letter-spacing:.15em;text-transform:uppercase;
           color:{INK45}">Recharge record</div>
      <div style="font-size:11.5px;color:{INK};margin-top:4px;line-height:1.35">
        Held through the 1950s drought of record</div>
    </div>
    <div style="flex:1;border-top:1px solid {INK25};padding-top:8px">
      <div class="m" style="font-size:8.4px;letter-spacing:.15em;text-transform:uppercase;
           color:{INK45}">Location of rights</div>
      <div style="font-size:11.5px;color:{INK};margin-top:4px;line-height:1.35">
        Adjacent affiliated lands</div>
    </div>
  </div>
</div>"""


def sheet05():
    ex = plate(water_diagram(), 660, 366, "FIG 05.1",
               "Permitted industrial rights as a share of the district")
    body = head(
        "Water",
        "Roughly two-thirds of all Middle Pecos GCD industrial water rights are "
        "already permitted to this position — the water question is closed, not open.",
        "2.4 Water rights") + f"""
<div style="display:flex;gap:30px">
  <div style="flex:none">
    {ex}
    <div style="margin-top:16px;width:660px">
      {note_block("Rights basis",
                  "The permitted volume sits on adjacent affiliated lands and is "
                  "roughly two-thirds of all industrial water rights issued by the "
                  "Middle Pecos Groundwater Conservation District.", BLUE)}
    </div>
  </div>
  <div style="flex:1;min-width:0">
    {tbl("05.1", "Permitted volume and basis",
         [("Parameter", "left", 132), ("Value", "left", None)],
         [["Permitted volume", "47,418 AF/yr"],
          ["Daily equivalent", "42.3 MGD"],
          ["District share", "~2/3 of GCD industrial rights"],
          ["Aquifer", "Edwards–Trinity (Plateau)"],
          ["Holder", "Adjacent affiliated lands"],
          ["District", "Middle Pecos GCD"]])}
    <div style="margin-top:18px">
      {callout("01", "Status", "Permitted, not applied for",
               "The volume above is a granted permit position, not a pending "
               "application in a district queue.")}
      {callout("02", "Drought basis", "1950s drought of record",
               "Edwards–Trinity (Plateau) recharge held through the drought of "
               "record used for regional planning.", RED)}
    </div>
  </div>
</div>"""
    return sheet(5, "2.4 WATER", "CARAMBA NORTH · 1,300 AC · PECOS CO., TX",
                 "MIDDLE PECOS GCD · USGS", body)


# ===========================================================================
# SHEET 06 — NATURAL GAS
# ===========================================================================
def gas_schematic():
    W, H = 664, 268
    return f"""
<div style="position:relative;width:{W}px;height:{H}px;font-family:{S['body']}">
  <div style="position:absolute;left:26px;top:64px;width:{W-52}px;height:2px;
       background:{INK25}"></div>
  <div style="position:absolute;left:26px;top:46px;width:2px;height:38px;background:{GOLD}"></div>
  <div style="position:absolute;left:{W-28}px;top:46px;width:2px;height:38px;background:{RED}"></div>
  <div class="m" style="position:absolute;left:26px;top:22px;font-size:11.5px;
       font-weight:600;color:{INK}">WAHA HUB</div>
  <div class="m" style="position:absolute;left:26px;top:92px;font-size:8.6px;
       letter-spacing:.15em;color:{INK45};text-transform:uppercase">Pricing index</div>
  <div class="m" style="position:absolute;right:26px;top:22px;font-size:11.5px;
       font-weight:600;color:{INK};text-align:right">CARAMBA NORTH</div>
  <div class="m" style="position:absolute;right:26px;top:92px;font-size:8.6px;
       letter-spacing:.15em;color:{INK45};text-transform:uppercase;text-align:right">
    Delivery point</div>
  <div class="m" style="position:absolute;left:50%;top:40px;transform:translateX(-50%);
       background:{PLATE_BG};padding:0 12px;font-size:20px;font-weight:600;
       color:{BLUE};letter-spacing:-0.4px">20 mi</div>
  <div style="position:absolute;left:26px;top:158px;right:26px;display:flex;gap:20px">
    <div style="flex:1;border-top:2px solid {BLUE};padding-top:9px">
      <div class="m" style="font-size:21px;font-weight:600;color:{INK};letter-spacing:-0.5px">
        200,000</div>
      <div class="m" style="font-size:8.4px;letter-spacing:.14em;text-transform:uppercase;
           color:{INK45};margin-top:6px;line-height:1.4">MMBtu / day<br>indicative quote</div>
    </div>
    <div style="flex:1;border-top:2px solid {BLUE};padding-top:9px">
      <div class="m" style="font-size:21px;font-weight:600;color:{INK};letter-spacing:-0.5px">
        15 yr</div>
      <div class="m" style="font-size:8.4px;letter-spacing:.14em;text-transform:uppercase;
           color:{INK45};margin-top:6px;line-height:1.4">Term<br>Waha-index pricing</div>
    </div>
    <div style="flex:1;border-top:2px solid {BLUE};padding-top:9px">
      <div class="m" style="font-size:21px;font-weight:600;color:{INK};letter-spacing:-0.5px">
        $15–25M</div>
      <div class="m" style="font-size:8.4px;letter-spacing:.14em;text-transform:uppercase;
           color:{INK45};margin-top:6px;line-height:1.4">CIAC<br>contribution in aid</div>
    </div>
    <div style="flex:1;border-top:2px solid {BLUE};padding-top:9px">
      <div class="m" style="font-size:21px;font-weight:600;color:{INK};letter-spacing:-0.5px">
        9–15 mo</div>
      <div class="m" style="font-size:8.4px;letter-spacing:.14em;text-transform:uppercase;
           color:{INK45};margin-top:6px;line-height:1.4">Lead time<br>counterparty-supplied</div>
    </div>
  </div>
</div>"""


def sheet06():
    ex = plate(gas_schematic(), 664, 268, "FIG 06.1",
               "Indicative supply schematic — Waha hub to delivery point")
    body = head(
        "Natural gas",
        "A signable 15-year supply quote at Waha-index pricing sits 20 miles from "
        "the tract — the same structural basis discount now drawing behind-the-meter "
        "generation into this corridor.",
        "2.5 Gas supply") + f"""
<div style="display:flex;gap:30px">
  <div style="flex:none">
    {ex}
    <div style="margin-top:16px;width:664px">
      {note_block("Basis context",
                  "Waha prices at a structural discount to Henry Hub, with negative "
                  "prints recorded in 2024–2025 as the Matterhorn, Blackcomb, Hugh "
                  "Brinson and GCX pipelines rebalance Permian egress.")}
    </div>
  </div>
  <div style="flex:1;min-width:0">
    {tbl("06.1", "Indicative supply terms (counterparty-supplied)",
         [("Term", "left", 118), ("Value", "left", None)],
         [["Volume", "200,000 MMBtu/day"],
          ["Contract term", "15 years"],
          ["Pricing", "Waha-index"],
          ["CIAC", "$15–25M"],
          ["Lead time", "9–15 months"],
          ["Hub distance", "20 mi to Waha"]],
         note="Indicative and non-binding; supplied by the counterparty and subject "
              "to confirmation in diligence.")}
    <div style="margin-top:16px">
      {callout("01", "Egress build-out", "Four pipelines rebalancing",
               "Matterhorn, Blackcomb, Hugh Brinson and GCX are shifting Permian "
               "egress; the basis discount is the reason on-site generation is "
               "being sited here.", RED)}
    </div>
  </div>
</div>"""
    return sheet(6, "2.5 NATURAL GAS", "CARAMBA NORTH · 1,300 AC · PECOS CO., TX",
                 "COUNTERPARTY QUOTE · PUBLIC BASIS DATA", body)


# ===========================================================================
# SHEET 07 — CORRIDOR + RING ANALYSIS  (full-plate map sheet)
# ===========================================================================
def sheet07():
    ex = exhibit("corridor_wide_light", w=730, fig="FIG 07.1",
                 caption="Regional corridor — operating fleet, ERCOT queue "
                         "and the two numbered anchor sites")
    ring_rows = [["Within 15 mi", "0.5 GW"], ["Within 30 mi", "8.9 GW"],
                 ["Within 60 mi", "32.7 GW"], ["Within 100 mi", "53.5 GW"]]
    body = head(
        "Corridor and ring analysis",
        "32.7 GW of operating and queued capacity sits within 60 miles; Caramba "
        "North is inside that radius, not adjacent to it.",
        "2.6 Regional pipeline") + f"""
<div style="display:flex;gap:28px">
  <div style="flex:none">{ex}</div>
  <div style="flex:1;min-width:0">
    {tbl("07.1", "Cumulative capacity by radius",
         [("Radius", "left", None), ("Operating + queue", "right", 118)], ring_rows,
         note="Region-wide, computed from the same EIA-860 and ERCOT-queue layers "
              "used throughout; not county-bounded.")}
    <div style="margin-top:14px">
      {tbl("07.2", "The two feature anchors — map key",
           [("#", "left", 22), ("Project", "left", None),
            ("Distance", "right", 76), ("Bearing", "right", 68)],
           [['<span class="m" style="color:%s;font-weight:600">1</span>' % GOLD,
             f'<span style="color:{RED};font-weight:600">GW Ranch</span>',
             "15.5 mi", "~19°"],
            ['<span class="m" style="color:%s;font-weight:600">2</span>' % GOLD,
             f'<span style="color:{RED};font-weight:600">Longfellow</span>',
             "19.3 mi", "~188°"]],
           note="Numbers key the markers on FIG 07.1 and FIG 08.1. Distances are "
                "edge-to-edge from the tract boundary; each anchor is plotted at its "
                "disclosed site point — see sheet 13 for basis.")}
    </div>
    <div style="margin-top:14px">
      {note_block("Geometry",
                  "GW Ranch bears almost due north and Longfellow almost due south; "
                  "the tract sits between them on a single north–south axis.", BLUE)}
    </div>
    <div style="margin-top:12px">
      {note_block("Within 20 miles",
                  "3,973 MW across 13 ERCOT-queue projects, before either anchor "
                  "above is counted.", RED)}
    </div>
  </div>
</div>"""
    return sheet(7, "2.6 CORRIDOR + RINGS", "CARAMBA NORTH · 1,300 AC · PECOS CO., TX",
                 "EIA-860 · ERCOT QUEUE · HIFLD · TIGER", body)


# ===========================================================================
# SHEET 08 — GW RANCH
# ===========================================================================
def sheet08():
    ex = exhibit("corridor_bare_light", w=606, fig="FIG 08.1",
                 caption="GW Ranch (marker 1) relative to the tract — 15.5 mi, "
                         "bearing ~19°")
    body = head(
        "GW Ranch",
        "The largest air permit issued in the US this year — 7.65 GW — sits 15.5 "
        "miles up the same highway corridor, under construction rather than announced.",
        "2.6a Feature anchor · north") + f"""
<div style="display:flex;gap:30px">
  <div style="flex:none">{ex}</div>
  <div style="flex:1;min-width:0">
    <div style="display:flex;gap:18px;margin-bottom:16px">
      {keyfig("15.5", "Miles from tract", "mi", RED)}
      {keyfig("8,000", "Site acreage", "ac")}
      {keyfig("7.65", "GW air permit", "GW")}
    </div>
    {tbl("08.1", "Site and generation record",
         [("Parameter", "left", 122), ("Record", "left", None)],
         [["Site", "8,000 ac, Pecos County"],
          ["Ownership", "Amazon; disclosed Aug 2026"],
          ["Developer", "Pacifico Energy Group (plant operator)"],
          ["Generation", "35 gas turbines · 7.65 GW TCEQ air permit, Jan / Feb 2026"],
          ["Storage / solar", "1.8 GW battery; up to 750 MW solar"],
          ["Buildings", "3 × 189,000 sq ft (Gensler)"],
          ["Target completion", "Dec 2026"],
          ["Est. investment", "~$12B total project"],
          ["Status", "Under construction"]], compact=True)}
    <div style="margin-top:14px">
      {note_block("Permit classification",
                  "The 7.65 GW figure is a TCEQ <em>generation</em> air permit, not "
                  "an ERCOT interconnection queue position. No ERCOT filing has been "
                  "disclosed; the project is off-grid initially. See sheet 10 for the "
                  "state-level audit context this sits inside.")}
    </div>
  </div>
</div>"""
    return sheet(8, "2.6a GW RANCH", "GW RANCH · 8,000 AC · 15.5 MI FROM TRACT",
                 "TCEQ AIR PERMIT · PUBLIC REPORTING", body)


# ===========================================================================
# SHEET 09 — LONGFELLOW
# ===========================================================================
def phase_blocks():
    W, H = 660, 176
    n = 8
    gap = 8
    bw = (W - 40 - gap * (n - 1)) / n
    blocks = ""
    for i in range(n):
        x = 20 + i * (bw + gap)
        active = i == 0
        fill = GOLD if active else "none"
        col = INK if active else INK45
        blocks += f"""
<div style="position:absolute;left:{x:.1f}px;top:52px;width:{bw:.1f}px;height:56px;
     background:{fill};border:1px solid {GOLD if active else INK25}"></div>
<div class="m" style="position:absolute;left:{x:.1f}px;top:{52 + 20}px;width:{bw:.1f}px;
     text-align:center;font-size:11px;font-weight:600;color:{'#FFFFFF' if active else col}">
  {i+1}</div>
<div class="m" style="position:absolute;left:{x:.1f}px;top:116px;width:{bw:.1f}px;
     text-align:center;font-size:8.4px;color:{INK45}">250 MW</div>"""
    return f"""
<div style="position:relative;width:{W}px;height:{H}px;font-family:{S['body']}">
  <div class="m" style="position:absolute;left:20px;top:16px;font-size:8.6px;
       letter-spacing:.16em;text-transform:uppercase;color:{INK45}">
    Announced phasing — 8 phases × 250 MW = 2 GW</div>
  {blocks}
  <div class="m" style="position:absolute;left:20px;top:140px;font-size:9.6px;color:{INK70}">
    <span style="display:inline-block;width:9px;height:9px;background:{GOLD};
          margin-right:7px;vertical-align:-1px"></span>Phase-1 site work underway
    <span style="display:inline-block;width:9px;height:9px;border:1px solid {INK25};
          margin:0 7px 0 22px;vertical-align:-1px"></span>Planned, subsequent phases</div>
</div>"""


def sheet09():
    ph = plate(phase_blocks(), 660, 176, "FIG 09.1",
               "Announced phasing — 8 phases at 250 MW")
    mat = chart_plate(C.chart_maturity, w=620, src_w=560, src_h=190,
                      fig="FIG 09.2",
                      caption="Build status of the two anchors' combined 9,650 MW")
    body = head(
        "Longfellow",
        "A second phased gas-generation campus 19.3 miles south — the corridor's "
        "demand for on-site power is not one project deep.",
        "2.6b Feature anchor · south") + f"""
<div style="display:flex;gap:30px">
  <div style="flex:none">
    {ph}
    <div style="margin-top:14px">{mat}</div>
  </div>
  <div style="flex:1;min-width:0">
    {tbl("09.1", "Site and generation record",
         [("Parameter", "left", 122), ("Record", "left", None)],
         [["Site", "568 ac, Pecos County"],
          ["Distance", "19.3 mi from tract, edge-to-edge"],
          ["Announced", "Oct 2025 — 2 GW, 8 phases"],
          ["Phase size", "250 MW"],
          ["Generation", "On-site aero-derivative gas turbines"],
          ["Emissions", "SCR with carbon-capture capability"],
          ["Cooling", "Closed-loop, permitted non-potable groundwater"],
          ["Status", "Phase-1 site work underway"]])}
    <div style="margin-top:14px">
      {note_block("Permitting status",
                  "No confirmed ERCOT queue position and no TCEQ air-permit record "
                  "was found for this site as of Aug 2026. Stated as a fact about "
                  "the permitting record, not as commentary on the project.")}
    </div>
    <div style="margin-top:12px">
      {note_block("Location basis",
                  "Longfellow's own public materials describe the location as more "
                  "than 25 miles outside Fort Stockton; the 19.3 mi figure is measured "
                  "to the Caramba North tract boundary, not to Fort Stockton.", BLUE)}
    </div>
  </div>
</div>"""
    return sheet(9, "2.6b LONGFELLOW", "LONGFELLOW · 568 AC · 19.3 MI FROM TRACT",
                 "PUBLIC PROJECT MATERIALS · TCEQ / ERCOT", body)


# ===========================================================================
# SHEET 10 — QUEUE AND POLICY CONTEXT
# ===========================================================================
def sheet10():
    ex = chart_plate(C.chart_queue_growth, h=392, src_w=560, src_h=400,
                     fig="FIG 10.1",
                     caption="ERCOT large-load interconnection queue, GW pending")
    chrono = [
        ["End 2024", "63 GW", "Large-load queue baseline"],
        ["Nov 2025", "226 GW", "Nearly quadrupled in a year; ~77% data centers "
                               "targeting 2030 interconnection"],
        ["Aug 3, 2026", "—", "Gubernatorial directive to audit all ERCOT-queue data "
                             "centers; “Batch Zero” large-load review paused"],
        ["Aug 2026", "474 GW", "Statewide pending requests, ~90% data-center-driven"],
    ]
    body = head(
        "Queue and policy context",
        "The statewide backlog reached ~474 GW and triggered an audit and a "
        "queue-processing pause — the demand signal is large enough to have become "
        "a policy problem, which is a different claim than “this area is growing.”",
        "3.0 Macro framing") + f"""
<div style="display:flex;gap:30px">
  <div style="flex:none">{ex}</div>
  <div style="flex:1;min-width:0">
    {tbl("10.1", "Chronology",
         [("Date", "left", 92), ("Queue", "right", 68), ("Event", "left", None)],
         chrono,
         note="Sources: Latitude Media, “ERCOT's large load queue has nearly "
              "quadrupled in a single year” (Dec 3, 2025); Utility Dive, “Facing an "
              "estimated 474 GW of interconnection requests, Texas hits pause on "
              "data centers” (Aug 2026).")}
    <div style="margin-top:18px">
      {callout("01", "Scale reference", "5× record peak demand",
               "Gov. Abbott characterised the pending request volume as more than "
               "five times Texas' record peak demand.")}
      {callout("02", "Position", "Inside the radius",
               "The 32.7 GW within 60 miles of this tract sits inside the same "
               "state-level queue that produced the pause.", RED)}
    </div>
  </div>
</div>"""
    return sheet(10, "3.0 QUEUE + POLICY", "ERCOT LARGE-LOAD QUEUE · STATE OF TEXAS",
                 "PUBLIC REPORTING, DEC 2025 / AUG 2026", body)


# ===========================================================================
# SHEET 11 — SUBSURFACE
# ===========================================================================
def sheet11():
    ex = chart_plate(C.chart_peer_drilling, w=756, src_w=880, src_h=420,
                     fig="FIG 11.1",
                     caption="New-drill wellbore events since 2020, Pecos vs. peers")
    body = head(
        "Subsurface activity",
        "Pecos County records the lowest new-drill count of seven comparable Permian "
        "counties since 2020 — roughly 90% below the peer average.",
        "2.8 Drilling and wellbore record") + f"""
<div style="display:flex;gap:28px">
  <div style="flex:none">
    {ex}
    <div style="display:flex;gap:20px;margin-top:14px;width:756px">
      {keyfig("115", "New-drill events since 2020", "")}
      {keyfig("10%", "Share of 1,140 RRC events", "")}
      {keyfig("9.37", "Miles to nearest new drill", "mi", RED)}
    </div>
  </div>
  <div style="flex:1;min-width:0">
    {tbl("11.1", "New-drill wells by proximity ring",
         [("Ring", "left", None), ("Wells", "right", 62)],
         [["Within 2 mi", "0"], ["Within 5 mi", "0"], ["Within 10 mi", "1"],
          ["Beyond 10 mi", "114"]],
         note="Median distance beyond 10 mi: 19.9 mi; mean 20.9 mi. "
              "RRC dbf900 / W-1 records since 2020.")}
    <div style="margin-top:16px">
      {tbl("11.2", "Marginal / end-of-life share of non-plugged wellbores",
           [("Ring", "left", None), ("Marginal", "right", 78)],
           [["Within 2 mi", "60%"], ["Within 5 mi", "62%"], ["Within 10 mi", "83%"]],
           note="The closer ring is quieter than the wider one on both measures.")}
    </div>
  </div>
</div>"""
    return sheet(11, "2.8 SUBSURFACE", "PECOS COUNTY · RRC WELLBORE RECORD",
                 "RRC DBF900 / PRODUCTION / W-1 · FRACFOCUS", body)


# ===========================================================================
# SHEET 12 — DILIGENCE PLATFORM
# ===========================================================================
SOURCES = [
    ("ERCOT", "GIS Report · TPIT", "Queue, planned upgrades", "Monthly"),
    ("PUCT", "Dockets", "Approved transmission paths", "As filed"),
    ("EIA", "Form EIA-860", "Operating generation fleet", "Annual"),
    ("TCEQ", "Air permits", "Permitted generation", "As issued"),
    ("RRC", "dbf900 · production · W-1", "Wellbore and drilling record", "Weekly"),
    ("FracFocus", "Disclosure registry", "Completion record", "Weekly"),
    ("Middle Pecos GCD", "Permit register", "Water rights", "As issued"),
    ("HIFLD", "Transmission · substations", "Grid infrastructure", "Annual"),
    ("USGS", "Hydrogeology", "Aquifer extent", "Annual"),
    ("BTS · Census TIGER", "Roads · boundaries", "Highways, county lines", "Annual"),
]


def sheet12():
    rows = [[f'<span style="font-weight:500">{a}</span>', b, c,
             f'<span class="m" style="font-size:10.5px;color:{INK70}">{d}</span>']
            for a, b, c, d in SOURCES]
    ex = plate(tbl("12.1", "Source register — every layer traces to a cited dataset",
                   [("Publisher", "left", 150), ("Dataset", "left", 190),
                    ("What it carries", "left", None), ("Refresh", "left", 96)],
                   rows, compact=True),
               726, 344, "FIG 12.1",
               "Per-feature source attribution behind the GIS platform", pad=18)
    body = head(
        "Diligence platform",
        "Every figure on these sheets is independently re-derivable from a cited "
        "public dataset — this is a source register, not a broker's summary.",
        "2.7 Data provenance") + f"""
<div style="display:flex;gap:28px">
  <div style="flex:none">
    {ex}
    <div style="margin-top:16px;width:726px">
      {note_block("Re-derivability",
                  "Each feature in the platform carries a source popup naming the "
                  "dataset and vintage it was drawn from, so any figure on these "
                  "sheets can be traced back to the published record it came from.",
                  BLUE)}
    </div>
  </div>
  <div style="flex:1;min-width:0">
    {tbl("12.2", "Platform capability",
         [("Function", "left", 112), ("Detail", "left", None)],
         [["Filters", "County, depth, spud year, fuel, status"],
          ["Time", "Scrubber across the wellbore record"],
          ["Tools", "Measure, share, print"],
          ["Popups", "Per-feature source attribution"],
          ["Build", "Static, versioned"],
          ["Release", "Deployed bundle byte-verified"],
          ["Access", "Logged; credentials issued separately"]])}
    <div style="margin-top:16px">
      {note_block("Platform address",
                  "lrp-tx-gis.netlify.app — credentials issued to the deal team "
                  "separately from this document.", BLUE)}
    </div>
    <div style="margin-top:14px">
      {callout("01", "Refresh cadence", "Weekly / monthly / annual",
               "RRC weekly; ERCOT queue and TPIT monthly; EIA, USGS and OSM annually.")}
    </div>
  </div>
</div>"""
    return sheet(12, "2.7 DILIGENCE PLATFORM", "LRP-TX-GIS · STATIC VERSIONED BUILD",
                 "SEE SOURCE REGISTER, THIS SHEET", body)


# ===========================================================================
# SHEET 13 — METHODOLOGY AND NOTICES
# ===========================================================================
def distance_diagram():
    W, H = 604, 258
    return f"""
<div style="position:relative;width:{W}px;height:{H}px;font-family:{S['body']}">
  <div class="m" style="position:absolute;left:22px;top:14px;font-size:8.6px;
       letter-spacing:.16em;text-transform:uppercase;color:{INK45}">
    Measurement basis — edge-to-edge vs. centroid</div>
  <div style="position:absolute;left:22px;top:52px;width:118px;height:74px;
       border:1.5px solid {RED};background:rgba(176,58,46,0.06)"></div>
  <div class="m" style="position:absolute;left:22px;top:132px;width:118px;
       text-align:center;font-size:9px;color:{INK70}">TRACT (1,300 AC)</div>
  <div style="position:absolute;left:{22+59}px;top:{52+36}px;width:5px;height:5px;
       border-radius:50%;background:{INK45}"></div>
  <div style="position:absolute;left:{W-58}px;top:80px;width:9px;height:9px;
       border-radius:50%;background:{RED}"></div>
  <div class="m" style="position:absolute;right:22px;top:58px;font-size:9px;
       color:{INK70};text-align:right">ANCHOR SITE</div>
  <div style="position:absolute;left:140px;top:87px;width:{W-140-54}px;height:2px;
       background:{BLUE}"></div>
  <div class="m" style="position:absolute;left:150px;top:64px;font-size:10.5px;
       font-weight:600;color:{BLUE}">EDGE-TO-EDGE — USED THROUGHOUT</div>
  <div style="position:absolute;left:83px;top:98px;width:{W-83-54}px;height:0;
       border-top:1px dashed {INK45}"></div>
  <div class="m" style="position:absolute;left:150px;top:104px;font-size:10px;
       color:{INK45}">CENTROID — LONGER, NOT USED</div>
  <div style="position:absolute;left:22px;top:168px;right:22px;display:flex;gap:22px">
    <div style="flex:1;border-top:1px solid {INK25};padding-top:9px">
      <div class="m" style="font-size:8.4px;letter-spacing:.14em;text-transform:uppercase;
           color:{INK45}">GW Ranch</div>
      <div class="m" style="font-size:19px;font-weight:600;color:{INK};margin-top:5px">
        15.5 mi <span style="font-size:11px;color:{INK45};font-weight:400">
        (17.3 mi centroid)</span></div>
    </div>
    <div style="flex:1;border-top:1px solid {INK25};padding-top:9px">
      <div class="m" style="font-size:8.4px;letter-spacing:.14em;text-transform:uppercase;
           color:{INK45}">Longfellow</div>
      <div class="m" style="font-size:19px;font-weight:600;color:{INK};margin-top:5px">
        19.3 mi <span style="font-size:11px;color:{INK45};font-weight:400">
        (19.7 mi centroid)</span></div>
    </div>
  </div>
</div>"""


def sheet13():
    ex = plate(distance_diagram(), 604, 274, "FIG 13.1",
               "Distance measurement basis (§4)")
    body = head(
        "Methodology and notices",
        "Distances are measured edge-to-edge from the tract boundary; the centroid "
        "figures are longer and are used nowhere else in this set.",
        "4.0 Basis of measurement") + f"""
<div style="display:flex;gap:28px">
  <div style="flex:none">
    {ex}
    <div style="margin-top:14px;width:604px">
      {note_block("Distance methodology (§4)",
                  "Distances to GW Ranch and Longfellow are measured edge-to-edge: "
                  "from the nearest point on the Caramba North tract boundary to each "
                  "site's disclosed location, rather than centroid-to-centroid. This "
                  "is consistently shorter than a straight centroid measurement "
                  "because Caramba North's own tract has spatial extent. GW Ranch: "
                  "15.5 mi (vs. 17.3 mi centroid). Longfellow: 19.3 mi (vs. 19.7 mi "
                  "centroid) — Longfellow's own public site describes its location as "
                  "more than 25 miles outside Fort Stockton, consistent with the "
                  "longer figure; this distance should not be represented as shorter.",
                  BLUE)}
    </div>
  </div>
  <div style="flex:1;min-width:0">
    {tbl("13.1", "Source register — third-party reporting",
         [("Ref", "left", 34), ("Citation", "left", None)],
         [[f'<span class="m" style="color:{BLUE};font-weight:600">R1</span>',
           "Latitude Media, “ERCOT's large load queue has nearly quadrupled in a "
           "single year,” Dec 3, 2025."],
          [f'<span class="m" style="color:{BLUE};font-weight:600">R2</span>',
           "Utility Dive, “Facing an estimated 474 GW of interconnection requests, "
           "Texas hits pause on data centers,” Aug 2026."],
          [f'<span class="m" style="color:{BLUE};font-weight:600">R3</span>',
           "TCEQ air-permit record, GW Ranch, Jan / Feb 2026."],
          [f'<span class="m" style="color:{BLUE};font-weight:600">R4</span>',
           "PUCT PBRP Docket No. 55718, approved Apr 24, 2025."]])}
    <div style="margin-top:18px">
      <div class="m" style="font-size:9px;letter-spacing:.14em;text-transform:uppercase;
           color:{INK45};margin-bottom:8px">
        <span style="color:{BLUE};font-weight:600">NOTICE</span>&nbsp;&nbsp;Terms of distribution</div>
      <p style="font-size:11px;line-height:1.55;color:{INK70};border-top:1px solid {INK25};
         padding-top:10px">
        Confidential offering memorandum prepared for a limited number of prospective
        counterparties under non-disclosure agreement. This is not an offer to sell or
        a solicitation of an offer to buy securities. Information is preliminary and
        indicative, drawn from sources believed reliable but not independently verified
        by the issuer of this document. Public data is drawn from the sources registered
        on sheet 12; third-party transaction news is sourced to the public reporting
        cited above. Recipients should conduct their own diligence; the GIS platform
        referenced on sheet 12 is provided for that purpose.</p>
    </div>
  </div>
</div>"""
    return sheet(13, "4.0 METHODOLOGY + NOTICES", "CARAMBA NORTH · 1,300 AC · PECOS CO., TX",
                 "§4 DISTANCE BASIS · SOURCE REGISTER", body)


# ---------------------------------------------------------------------------
EXTRA_CSS = f"""
.grid {{ position:absolute; inset:0;
  background-image:
    linear-gradient(to right, rgba(74,84,95,0.11) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(74,84,95,0.11) 1px, transparent 1px),
    linear-gradient(to right, rgba(74,84,95,0.055) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(74,84,95,0.055) 1px, transparent 1px);
  background-size: 128px 128px, 128px 128px, 32px 32px, 32px 32px; }}
.frame {{ position:absolute; left:24px; top:24px; right:24px; bottom:24px;
  border:1px solid {RULE}; display:flex; flex-direction:column; }}
.tb, .fb {{ background:{S['paper']}; }}
.tb {{ height:66px; flex:none; display:flex; border-bottom:1px solid {RULE}; }}
.tb > div:last-child {{ border-right:none; }}
.body {{ flex:1; min-height:0; padding:18px 24px; overflow:hidden; }}
.fb {{ height:24px; flex:none; border-top:1px solid {RULE}; display:flex;
  align-items:center; justify-content:space-between; padding:0 14px;
  font-family:{S['mono']}; font-size:7.6px; letter-spacing:.16em; color:{INK45}; }}
em {{ font-style:italic; }}
"""


def main():
    pages = "\n".join([sheet01(), sheet02(), sheet03(), sheet04(), sheet05(),
                       sheet06(), sheet07(), sheet08(), sheet09(), sheet10(),
                       sheet11(), sheet12(), sheet13()])
    html = T.document("technical", pages, "landscape",
                      "Caramba North — Technical Drawing Set")
    html = html.replace("</style>", EXTRA_CSS + "\n</style>", 1)
    OUT.mkdir(parents=True, exist_ok=True)
    hp = OUT / f"{STEM}.html"
    hp.write_text(html, encoding="utf-8")
    print(f"html -> {hp.relative_to(T.REPO)}  ({hp.stat().st_size // 1024} KB)")
    T.render_pdf(str(hp), str(OUT / f"{STEM}.pdf"))


if __name__ == "__main__":
    main()
