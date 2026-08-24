#!/usr/bin/env python3
"""Caramba North — Institutional deck (system: `institutional`).

The "everything" version: 17 landscape pages, dense stat tiles, real tables,
hairline rules. Newsreader carries the headings, Public Sans the body, IBM
Plex Mono every figure and label so numbers align down a column.

Facts, headings and subheadings come from docs/redesign_content_brief.md
(§0-§4 binding). Nothing here is invented.

Two exhibits are drawn in HTML/CSS rather than pulled from om_charts:
the substation distance profile (p. 05) does not exist as an SVG, and the
operating-capacity bars (p. 06) are drawn here because at this page's 490px
column the shared `chart_power_mix_*` exhibit has to run at 0.79x and its
labels are set in IBM Plex Sans, which is not one of this system's three
faces — the HTML version carries the deck's own Public Sans / Plex Mono at
the deck's own sizes, and its four fixed label columns cannot collide at any
scale. (The label overprint that originally forced the substitution has since
been fixed upstream; the substitution is kept on typographic grounds.)

The shared exhibits ask for IBM Plex Sans in their label stacks, so that face
is embedded here alongside the three system faces. Without it Chromium
substitutes Liberation Sans — an Arial clone, which PART II rules out.

    python3 scripts/om2/build_deck_institutional.py
"""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import om_theme as T  # noqa: E402

S = T.SYSTEMS["institutional"]
W, H = T.SLIDE_W, T.SLIDE_H

PAPER = S["paper"]          # #FBFAF7
INK = S["ink"]              # #12181F
INK70 = S["ink70"]
INK45 = S["ink45"]
INK25 = S["ink25"]
RULE = S["rule"]            # #D9D4CB
PANEL = S["panel"]          # #F2EEE6
RED = S["accent"]           # reserved: subject site + the two feature anchors
GOLD = S["second"]
BLUE = S["third"]           # the institutional lead accent (rules, eyebrows)
SUBINK = "#39434E"          # italic subheading ink

PAD = 68                    # left/right margin
CW = W - 2 * PAD            # 1144 content width
BODY_TOP = 190
BODY_H = 474

TOTAL_PAGES = 17


# ---------------------------------------------------------------------------
_SVG_SEQ = [0]


def vsvg(name):
    """Inline a vector exhibit with its internal ids namespaced to this copy.

    `om_theme.svg()` inlines the SVG markup verbatim, and every corridor map
    declares its clip rect with the same id, `mapclip`. Two maps in one
    document therefore share one id, and `url(#mapclip)` resolves to whichever
    appeared first: on p. 09 the 1360x860 regional map was being clipped by
    p. 04's 900x640 rect, silently discarding the Longfellow and La Escalera
    markers and the eastern third of the map. Rewriting every id per instance
    keeps the two apart. Harmless for the chart exhibits, which carry no ids.
    """
    out = T.svg(name)
    _SVG_SEQ[0] += 1
    tag = f"i{_SVG_SEQ[0]}"
    for ident in sorted(set(re.findall(r'id="([^"]+)"', out)), key=len, reverse=True):
        out = (out.replace(f'id="{ident}"', f'id="{ident}-{tag}"')
                  .replace(f"url(#{ident})", f"url(#{ident}-{tag})")
                  .replace(f'href="#{ident}"', f'href="#{ident}-{tag}"'))
    return out


# The shared SVG exhibits label themselves in IBM Plex Sans. It is not one of
# the three institutional faces, so it is embedded only for them; without it
# Chromium falls back to Liberation Sans (Arial), which PART II bans.
EXHIBIT_FONT_CSS = "<style>\n" + T.font_css("plexsans") + "\n</style>\n"

# ---------------------------------------------------------------------------
CSS = f"""
<style>
.eyebrow {{ font-size:9.5px; letter-spacing:.22em; text-transform:uppercase;
  color:{INK45}; font-variant-numeric:tabular-nums; }}
.eyebrow b {{ color:{BLUE}; font-weight:500; }}
.h {{ font-size:34px; font-weight:500; line-height:1.08; letter-spacing:-.005em; }}
.sub {{ font-style:italic; font-size:17.5px; line-height:1.34; color:{SUBINK}; }}
.rule {{ height:1px; background:{RULE}; }}
.rule-k {{ height:1px; background:{INK}; }}
.lbl {{ font-size:8.8px; letter-spacing:.15em; text-transform:uppercase; color:{INK45}; }}
.val {{ font-size:27px; font-weight:600; line-height:1; color:{INK}; letter-spacing:-.02em; }}
.val-s {{ font-size:20px; font-weight:600; line-height:1; color:{INK}; letter-spacing:-.01em; }}
.note {{ font-size:10.5px; line-height:1.4; color:{INK70}; }}
.p {{ font-size:12.4px; line-height:1.62; color:#242C35; }}
.p b {{ font-weight:600; color:{INK}; }}
.tile {{ border-top:1px solid {INK}; padding-top:9px; }}
.tile .lbl {{ margin-bottom:7px; }}
.tile .note {{ margin-top:6px; }}
table.t {{ border-collapse:collapse; width:100%; }}
table.t th {{ font-family:{S['mono']}; font-size:8.6px; letter-spacing:.14em;
  text-transform:uppercase; color:{INK45}; text-align:left; font-weight:500;
  padding:0 0 6px 0; border-bottom:1px solid {INK}; }}
table.t td {{ font-size:11.8px; line-height:1.4; color:#242C35; padding:7px 0;
  border-bottom:1px solid {RULE}; vertical-align:top; }}
table.t.tall td {{ padding:11px 0; }}
table.t tr:last-child td {{ border-bottom:none; }}
table.t td.k {{ font-family:{S['mono']}; font-size:10.5px; letter-spacing:.03em;
  color:{INK45}; text-transform:uppercase; }}
table.t td.n {{ font-family:{S['mono']}; font-variant-numeric:tabular-nums;
  font-size:11.6px; color:{INK}; font-weight:500; }}
table.t td.r {{ text-align:right; }}
table.t tr.tot td {{ border-top:1px solid {INK}; border-bottom:none;
  font-weight:600; color:{INK}; padding-top:7px; }}
.cap {{ font-size:9.2px; letter-spacing:.06em; color:{INK45}; line-height:1.45; }}
.panel {{ background:{PANEL}; padding:16px 18px; }}
.chip {{ display:inline-block; font-size:9.4px; letter-spacing:.1em;
  text-transform:uppercase; color:{INK70}; border:1px solid {RULE};
  padding:4px 9px; margin:0 5px 5px 0; }}
.kicker {{ font-size:9.5px; letter-spacing:.18em; text-transform:uppercase;
  color:{BLUE}; font-weight:500; }}
.kicker-r {{ color:{RED}; }}
.fnote {{ font-size:9px; line-height:1.5; color:{INK45}; }}
.ftr {{ position:absolute; left:{PAD}px; right:{PAD}px; bottom:34px; }}
.ftr .row {{ display:flex; justify-content:space-between; margin-top:7px;
  font-size:8.6px; letter-spacing:.14em; text-transform:uppercase; color:{INK45}; }}
.xtitle {{ font-size:13px; font-weight:600; color:{INK}; letter-spacing:-.01em; }}
.xsub {{ font-size:9.6px; letter-spacing:.06em; color:{INK45}; margin-top:3px; }}
.brow {{ display:flex; align-items:center; }}
.track {{ position:relative; height:22px; }}
.fill {{ position:absolute; left:0; top:0; height:22px; }}
</style>
"""


# ---------------------------------------------------------------------------
def page(num, section, title, sub, body, body_top=BODY_TOP, body_h=BODY_H,
         head_top=50, title_size=34, ftr_bottom=34):
    rule_y = body_top - 18
    return f"""
<div class="page">
  <div style="position:absolute;left:{PAD}px;top:{head_top}px;width:{CW}px">
    <div class="m eyebrow" style="display:flex;justify-content:space-between">
      <span><b>{num:02d}</b>&nbsp;&nbsp;/&nbsp;&nbsp;{section}</span>
      <span>Caramba North &nbsp;·&nbsp; Pecos County, Texas</span>
    </div>
  </div>
  <div style="position:absolute;left:{PAD}px;top:{head_top + 26}px;width:{CW}px">
    <div class="d h" style="font-size:{title_size}px">{title}</div>
  </div>
  <div style="position:absolute;left:{PAD}px;top:{head_top + 26 + title_size + 12}px;width:940px">
    <div class="d sub">{sub}</div>
  </div>
  <div class="rule" style="position:absolute;left:{PAD}px;top:{rule_y}px;width:{CW}px"></div>
  <div style="position:absolute;left:{PAD}px;top:{body_top}px;width:{CW}px;height:{body_h}px;overflow:hidden">
    {body}
  </div>
  <div class="ftr" style="bottom:{ftr_bottom}px">
    <div class="rule"></div>
    <div class="m row">
      <span>Caramba North &nbsp;—&nbsp; Confidential Offering Memorandum</span>
      <span>{section}</span>
      <span>{num:02d}&nbsp;/&nbsp;{TOTAL_PAGES}</span>
    </div>
  </div>
</div>"""


def tile(label, value, note="", vclass="val", w=None):
    width = f"width:{w}px;" if w else "flex:1;min-width:0;"
    n = f'<div class="note">{note}</div>' if note else ""
    return (f'<div class="tile" style="{width}">'
            f'<div class="m lbl">{label}</div>'
            f'<div class="m {vclass}">{value}</div>{n}</div>')


def table(headers, rows, widths=None, total_row=None, cls=""):
    cols = ""
    if widths:
        cols = "<colgroup>" + "".join(f'<col style="width:{x}">' for x in widths) + "</colgroup>"
    th_parts = []
    for h in headers:
        align = ' style="text-align:right"' if h.startswith("~") else ""
        th_parts.append("<th%s>%s</th>" % (align, h.lstrip("~")))
    th = "".join(th_parts)
    body = ""
    for r in rows:
        tds = ""
        for cell in r:
            txt, c = (cell if isinstance(cell, tuple) else (cell, ""))
            tds += f'<td class="{c}">{txt}</td>'
        body += f"<tr>{tds}</tr>"
    if total_row:
        tds = ""
        for cell in total_row:
            txt, c = (cell if isinstance(cell, tuple) else (cell, ""))
            tds += f'<td class="{c}">{txt}</td>'
        body += f'<tr class="tot">{tds}</tr>'
    return (f'<table class="t {cls}">{cols}<thead><tr>{th}</tr></thead>'
            f'<tbody>{body}</tbody></table>')


def exhibit(name, w, h, caption=None):
    cap = f'<div class="m cap" style="margin-top:8px;width:{w}px">{caption}</div>' if caption else ""
    return (f'<div><div style="width:{w}px;height:{h}px;overflow:hidden">'
            f'{vsvg(name)}</div>{cap}</div>')


# ---------------------------------------------------------------------------
# Two HTML/CSS exhibits (see module docstring for why).
# ---------------------------------------------------------------------------
def bar_chart(title, subtitle, rows, maxv, note, label_w=64, track_w=252,
              val_w=80, right_w=62, barcol=BLUE):
    """rows: (label, bar_value, value_text, right_text). Labels never collide:
    every element sits in its own fixed column."""
    out = []
    for label, v, vtext, rtext in rows:
        frac = max(v / maxv, 0.004)
        out.append(f"""
<div class="brow" style="margin-top:14px">
  <div class="m" style="width:{label_w}px;font-size:10px;color:{INK70};text-align:right;
       padding-right:10px">{label}</div>
  <div class="track" style="width:{track_w}px;background:{PANEL}">
    <div class="fill" style="width:{frac * 100:.2f}%;background:{barcol}"></div>
  </div>
  <div class="m" style="width:{val_w}px;font-size:11.5px;font-weight:600;color:{INK};
       padding-left:10px">{vtext}</div>
  <div class="m" style="width:{right_w}px;font-size:9.6px;color:{INK45};
       text-align:right">{rtext}</div>
</div>""")
    return f"""
<div>
  <div class="xtitle">{title}</div>
  <div class="m xsub">{subtitle}</div>
  {''.join(out)}
  <div class="note" style="margin-top:16px">{note}</div>
</div>"""


def distance_profile(rows, maxmi, width=612, name_w=148, track_w=252,
                     dist_w=66, right_w=88):
    """rows: (name, miles, right_text, emphasis) — a scaled distance strip."""
    ticks = ""
    for mi in (0, 5, 10, 15):
        x = mi / maxmi * track_w
        ticks += (f'<div style="position:absolute;left:{x:.1f}px;top:0;width:1px;'
                  f'height:6px;background:{INK25}"></div>'
                  f'<div class="m" style="position:absolute;left:{x:.1f}px;top:8px;'
                  f'font-size:8px;color:{INK45};transform:translateX(-50%)">{mi}</div>')
    head = f"""
<div class="brow" style="margin-bottom:22px">
  <div style="width:{name_w}px"></div>
  <div style="width:{track_w}px;position:relative;height:20px">{ticks}
    <div class="m" style="position:absolute;right:-30px;top:8px;font-size:8px;
         color:{INK45}">MILES</div></div>
  <div style="width:{dist_w}px"></div><div style="width:{right_w}px"></div>
</div>"""
    out = []
    for nm, mi, rtext, emph in rows:
        col = BLUE if emph else INK70
        frac = mi / maxmi
        out.append(f"""
<div class="brow" style="height:30px;border-bottom:1px solid {RULE}">
  <div class="m" style="width:{name_w}px;font-size:10.2px;color:{INK if emph else INK70};
       font-weight:{600 if emph else 400};padding-right:10px">{nm}</div>
  <div style="width:{track_w}px;position:relative;height:12px">
    <div style="position:absolute;left:0;top:5.5px;width:{track_w}px;height:1px;
         background:{RULE}"></div>
    <div style="position:absolute;left:0;top:5.5px;width:{frac * track_w:.1f}px;height:1px;
         background:{col}"></div>
    <div style="position:absolute;left:{frac * track_w - 3:.1f}px;top:3px;width:7px;
         height:7px;background:{col}"></div>
  </div>
  <div class="m" style="width:{dist_w}px;font-size:10.8px;font-weight:600;color:{INK};
       text-align:right">{mi:.1f} mi</div>
  <div class="m" style="width:{right_w}px;font-size:10px;color:{INK70};
       text-align:right">{rtext}</div>
</div>""")
    return f'<div style="width:{width}px">{head}{"".join(out)}</div>'


# ===========================================================================
# 01 — Cover
# ===========================================================================
def p01():
    left = f"""
<div style="width:614px">
  <div class="m" style="font-size:9.5px;letter-spacing:.24em;text-transform:uppercase;color:{RED}">
    Confidential Offering Memorandum</div>
  <div class="rule-k" style="margin:14px 0 26px"></div>
  <div class="d" style="font-size:82px;font-weight:500;line-height:.98;letter-spacing:-.02em">
    Caramba<br>North</div>
  <div class="m" style="font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:{INK70};margin-top:24px">
    1,300 contiguous acres &nbsp;·&nbsp; north side of I-10 &nbsp;·&nbsp; Pecos County, Texas</div>
  <div class="d sub" style="font-size:20px;margin-top:22px;width:592px">
    A 1,300-acre parcel inside an already-forming power and data-center corridor:
    32.7 GW of operating and queued capacity within 60 miles, and two
    hyperscale-scale campuses on the same north–south line through the property
    at 15.5 and 19.3 miles.</div>
  <div class="rule" style="margin:30px 0 0"></div>
  <div style="display:flex;gap:20px;margin-top:16px">
    {tile("Within 60 mi", "32.7 GW", "operating + ERCOT queue", "val-s")}
    {tile("Permitted water", "47,418", "AF/yr &nbsp;(42.3 MGD)", "val-s")}
    {tile("To Solstice", "15 mi", "765 kV import terminus", "val-s")}
    {tile("To Waha hub", "20 mi", "gas supply quote in hand", "val-s")}
  </div>
</div>"""
    right = f"""
<div style="width:470px;padding-top:6px">
  {exhibit("chart_rings_light", 470, 470)}
  <div class="m cap" style="margin-top:10px">
    Exhibit A &nbsp;·&nbsp; Cumulative operating + ERCOT-queued capacity by radius
    from the tract. Region-wide, not county-bounded.</div>
</div>"""
    return f"""
<div class="page">
  <div style="position:absolute;left:{PAD}px;top:64px;width:{CW}px;display:flex;
              gap:60px;align-items:flex-start">{left}{right}</div>
  <div class="ftr">
    <div class="rule"></div>
    <div class="m row">
      <span>Prepared for a limited number of prospective counterparties under NDA</span>
      <span>August 2026</span>
      <span>01&nbsp;/&nbsp;{TOTAL_PAGES}</span>
    </div>
  </div>
</div>"""


# ===========================================================================
# 02 — Contents
# ===========================================================================
CONTENTS = [
    ("03", "Positioning", "The corridor makes the case before the parcel does."),
    ("04", "The Property", "As-of-right industrial land; no rezoning path required."),
    ("05", "Transmission", "Fifteen miles from the 765 kV import terminus."),
    ("06", "Regional Power Cluster", "3,226 MW operating and 12,039 MW queued in-county."),
    ("07", "Water", "47,418 AF/yr permitted — two-thirds of district rights."),
    ("08", "Natural Gas", "A 15-year indicative quote at Waha index pricing."),
    ("09", "The Regional Pipeline", "Named large-load projects sit on one axis."),
    ("10", "Ring Analysis", "0.5 / 8.9 / 32.7 / 53.5 GW at 15 / 30 / 60 / 100 mi."),
    ("11", "GW Ranch", "7.65 GW air permit, under construction, 15.5 mi north."),
    ("12", "Longfellow", "Phased on-site gas generation, 19.3 miles south."),
    ("13", "ERCOT Queue Context", "A 474 GW backlog that triggered a state audit."),
    ("14", "Subsurface & Drilling", "Lowest new-drill count of seven Permian counties."),
    ("15", "The Diligence Platform", "Every figure traces to a cited public dataset."),
    ("16", "Methodology & Sources", "Distances are edge-to-edge; here is the arithmetic."),
    ("17", "Notices", "Preliminary and indicative; circulated under NDA."),
]


def p02():
    def row(n, t, d):
        return f"""
<div style="display:flex;gap:16px;padding:9px 0;border-bottom:1px solid {RULE}">
  <div class="m" style="width:26px;font-size:10.5px;color:{BLUE};padding-top:3px">{n}</div>
  <div style="flex:1;min-width:0">
    <div class="d" style="font-size:15px;font-weight:500;line-height:1.2">{t}</div>
    <div class="note" style="margin-top:2px">{d}</div>
  </div>
</div>"""
    colA = "".join(row(*r) for r in CONTENTS[:8])
    colB = "".join(row(*r) for r in CONTENTS[8:])

    def kv(k, v):
        return f"""
<div style="display:flex;justify-content:space-between;border-top:1px solid {RULE};
     padding:7px 0">
  <span class="m" style="font-size:8.8px;letter-spacing:.14em;text-transform:uppercase;
        color:{INK45}">{k}</span>
  <span class="m" style="font-size:10.5px;font-weight:600;color:{INK}">{v}</span>
</div>"""
    body = f"""
<div style="display:flex;gap:27px">
  <div style="width:420px">{colA}</div>
  <div style="width:420px">{colB}</div>
  <div style="width:250px">
    <div class="panel">
      <div class="m kicker">How to read this</div>
      <div class="p" style="margin-top:8px;font-size:11.4px;line-height:1.58">
        Every heading carries a one-sentence conclusion beneath it. Figures set in mono
        come from the GIS data model described on page 15 and are re-derivable from
        cited public sources. Distances to the two feature anchors are edge-to-edge from
        the tract boundary — see page 16.</div>
    </div>
    <div style="margin-top:20px">
      {kv("Pages", "17")}
      {kv("Exhibits", "8")}
      {kv("Data as of", "Aug 2026")}
      {kv("Distribution", "NDA only")}
    </div>
  </div>
</div>"""
    return page(2, "Contents", "Contents",
                "Ordered from the region's numbers inward to the site's — the corridor "
                "makes the case before the parcel does.", body)


# ===========================================================================
# 03 — Positioning
# ===========================================================================
def p03():
    body = f"""
<div style="display:flex;gap:40px">
  <div style="width:660px">
    <div class="d" style="font-size:24px;line-height:1.34;font-weight:400">
      Caramba North is not a speculative land bet. It is a 1,300-acre parcel sitting
      inside an already-forming power and data-center corridor — with water and gas
      on contract-ready terms, not applications.</div>
    <div class="rule" style="margin:22px 0 18px"></div>
    <div style="display:flex;gap:32px">
      <div style="flex:1">
        <div class="m kicker">What the region carries</div>
        <div class="p" style="margin-top:8px">
          Two hyperscale-scale projects — <b>7.65 GW</b> and <b>2 GW</b> announced —
          sit on the same north–south line through the property at <b>15.5</b> and
          <b>19.3</b> miles. Around them, <b>32.7 GW</b> of operating and ERCOT-queued
          capacity sits within 60 miles, in the state's highest-growth large-load
          pocket.</div>
      </div>
      <div style="flex:1">
        <div class="m kicker">What the site carries</div>
        <div class="p" style="margin-top:8px">
          A transmission, water and gas position that is already permitted rather than
          proposed: 15 miles from the western terminus of three PUCT-approved 765 kV
          import paths, <b>47,418 AF/yr</b> of permitted groundwater on adjacent
          affiliated lands, and an indicative <b>15-year</b> gas supply quote at Waha
          index pricing.</div>
      </div>
    </div>
    <div class="rule" style="margin:18px 0 16px"></div>
    <div class="p">
      The state-level context is the frame, not the pitch: Texas' interconnection
      backlog reached roughly <b>474 GW</b> of pending requests, about 90% data-center
      driven, large enough to trigger a gubernatorial audit and a pause of the
      large-load review process in August 2026. Caramba North is positioned to benefit
      from the same infrastructure buildout without carrying the exposure of being the
      marginal, unproven project inside that queue.</div>
  </div>
  <div style="width:444px">
    {tile("Operating + queued within 60 miles", "32.7 GW", "region-wide; EIA-860 operating fleet plus ERCOT interconnection queue")}
    <div style="height:20px"></div>
    {tile("Queued in Pecos County alone", "12,039 MW", "39 projects, before counting the two feature anchors")}
    <div style="height:20px"></div>
    {tile("Announced capacity under construction", "79.3%", "of the two profiled anchors' combined announced MW")}
    <div style="height:20px"></div>
    {tile("New-drill wells within 5 miles since 2020", "0", "one within 10 miles, at 9.37 mi")}
  </div>
</div>"""
    return page(3, "Positioning", "Positioning",
                "Two hyperscale-scale campuses sit on the same north–south line through "
                "this property at 15.5 and 19.3 miles; the water and gas behind it are "
                "permitted, not applied for.", body)


# ===========================================================================
# 04 — The Property
# ===========================================================================
def p04():
    tbl = table(
        ["Attribute", "Detail"],
        [
            [("Acreage", "k"), "1,300 acres maximum contiguous"],
            [("Location", "k"), "North side of Interstate 10, Pecos County, Texas"],
            [("Nearest city", "k"), "≈ 5 miles from Fort Stockton — services and regional airport"],
            [("Zoning", "k"), "No county zoning ordinance; industrial and energy use as of right"],
            [("ERCOT zone", "k"), "Far West weather zone — the highest-growth large-load pocket in ERCOT"],
            [("Transmission", "k"), "15 miles to Solstice Substation; six substations within 10 miles (p. 05)"],
            [("Water", "k"), "47,418 AF/yr permitted on adjacent affiliated lands (p. 07)"],
            [("Gas", "k"), "20 miles to the Waha hub; indicative 15-year supply quote (p. 08)"],
        ],
        widths=["118px", "auto"], cls="tall")

    # Key matches the map exactly: `corridor_bare_*` carries the subject tract
    # as a drawn boundary and exactly two numbered anchor markers — GW Ranch
    # north, Longfellow south. La Escalera appears only on the rail variant
    # used on p. 09, so it is not listed here.
    def key(mark, nm, d):
        return (f'{mark}'
                f'<span class="m" style="font-size:8.6px;letter-spacing:.09em;'
                f'text-transform:uppercase;color:{INK};margin-left:5px">{nm}</span>'
                f'<span class="m" style="font-size:8.6px;color:{INK45};margin-left:4px;'
                f'margin-right:16px">{d}</span>')

    swatch = (f'<span style="display:inline-block;width:8px;height:8px;'
              f'background:{RED};opacity:.34;border:1.5px solid {RED};'
              f'vertical-align:-1px"></span>')

    def numdot(n):
        return (f'<span class="m" style="display:inline-block;width:12px;height:12px;'
                f'border-radius:50%;background:{GOLD};color:{PAPER};font-size:8px;'
                f'font-weight:600;line-height:12px;text-align:center;'
                f'vertical-align:-2px">{n}</span>')

    keyrow = (f'<div style="margin-top:9px;border-top:1px solid {RULE};padding-top:8px;'
              f'white-space:nowrap">'
              + key(swatch, "Caramba North", "subject tract")
              + key(numdot(1), "GW Ranch", "15.5 mi N")
              + key(numdot(2), "Longfellow", "19.3 mi S") + "</div>")
    body = f"""
<div style="display:flex;gap:34px">
  <div style="width:548px">
    {tbl}
    <div class="rule" style="margin:18px 0 14px"></div>
    <div style="display:flex;gap:18px">
      {tile("Max contiguous", "1,300 ac", "", "val-s")}
      {tile("To Fort Stockton", "≈ 5 mi", "", "val-s")}
      {tile("Zoning", "None", "", "val-s")}
      {tile("Weather zone", "Far West", "", "val-s")}
    </div>
  </div>
  <div style="width:562px">
    <div style="width:562px;height:400px;overflow:hidden">{vsvg("corridor_bare_light")}</div>
    {keyrow}
    <div class="m cap" style="margin-top:7px;width:562px">
      Exhibit B &nbsp;·&nbsp; Site setting — tract, anchors, transmission, I-10.
      Anchors are markers at their disclosed site coordinates; only the subject
      position is drawn as a boundary.</div>
  </div>
</div>"""
    return page(4, "The Property", "The Property",
                "As-of-right industrial land inside the fastest-growing load pocket in "
                "ERCOT — this is not a rezoning story.", body)


# ===========================================================================
# 05 — Transmission
# ===========================================================================
def p05():
    prof = distance_profile([
        ("Fort Stockton Plant", 2.0, "138 / 69 kV", False),
        ("Airport", 3.3, "138 kV", False),
        ("Fort Stockton", 5.4, "69 kV", False),
        ("16th Street", 6.0, "138 / 69 kV", False),
        ("Northern Natural", 7.0, "—", False),
        ("Gomez", 9.7, "—", False),
        ("Solstice", 15.0, "765 kV", True),
    ], maxmi=16.0, width=612)
    body = f"""
<div style="display:flex;gap:44px">
  <div style="width:612px">
    <div class="xtitle">Substations by distance from the tract</div>
    <div class="m xsub">Six local substations inside 10 miles; the 765 kV import
      terminus at 15</div>
    <div style="height:16px"></div>
    {prof}
    <div class="m cap" style="margin-top:12px">
      Exhibit C &nbsp;·&nbsp; Distance profile, tract boundary to each substation.
      Solstice set apart in blue: it is the delivery point, not a local tap.</div>
    <div class="rule" style="margin:22px 0 14px"></div>
    <div style="display:flex;gap:22px">
      {tile("Nearest substation", "2.0 mi", "Fort Stockton Plant, 138 / 69 kV", "val-s")}
      {tile("Inside 10 miles", "6", "local substations", "val-s")}
      {tile("Highest voltage nearby", "765 kV", "at Solstice, 15 miles", "val-s")}
    </div>
  </div>
  <div style="width:488px">
    <div class="panel">
      <div class="m kicker">Solstice Substation — 15 miles</div>
      <div class="p" style="margin-top:8px">
        Western terminus of three 765 kV Permian import paths approved by the PUCT on
        <b>April 24, 2025</b> (PBRP Docket No. 55718), developed by AEP and CPS Energy.
        The decision to move bulk power into this part of the Permian is already made,
        upstream of the site.</div>
    </div>
    <div style="display:flex;gap:20px;margin-top:22px">
      {tile("To Solstice", "15 mi", "765 kV import terminus", "val-s")}
      {tile("Approved paths", "3", "PUCT, Apr 24 2025", "val-s")}
    </div>
    <div style="display:flex;gap:20px;margin-top:22px">
      {tile("TPIT substations", "141", "planned upgrades, ERCOT-wide", "val-s")}
      {tile("TPIT lines", "133", "planned upgrades, ERCOT-wide", "val-s")}
    </div>
    <div class="rule" style="margin:22px 0 12px"></div>
    <div class="fnote">
      TPIT (Transmission Planning Improvement Tool) counts are the queue of
      <i>planned</i> ERCOT-wide grid upgrades, not built capacity — cited here as
      pipeline context only. Substation distances are straight-line from the tract
      boundary; voltages as recorded in the HIFLD and ERCOT layers.</div>
  </div>
</div>"""
    return page(5, "Transmission", "Transmission",
                "Fifteen miles from the delivery point of all three approved 765 kV "
                "Permian import lines — the transmission decision is already made, "
                "upstream of this site.", body)


# ===========================================================================
# 06 — Regional Power Cluster
# ===========================================================================
def p06():
    chart = bar_chart(
        "Pecos County operating capacity",
        "Megawatts in service · EIA-860",
        [("Solar", 2178, "2,178 MW", "13 proj."),
         ("Wind", 542, "542 MW", "5 proj."),
         ("Storage", 505, "505 MW", "6 proj."),
         ("Gas", 1, "1 MW", "1 proj.")],
        maxv=2178,
        note="3,226 MW operating today; 12,039 MW queued in this county alone.")
    op = table(
        ["Pecos County — operating", "~MW", "~Projects"],
        [
            ["Solar", ("2,178", "n r"), ("13", "n r")],
            ["Wind", ("542", "n r"), ("5", "n r")],
            ["Battery storage", ("505", "n r"), ("6", "n r")],
            ["Gas", ("1", "n r"), ("1", "n r")],
        ],
        widths=["auto", "80px", "80px"], cls="tall",
        total_row=[("Total operating", ""), ("3,226", "n r"), ("25", "n r")])
    q = table(
        ["Queue and adjacent counties", "~MW", "~Projects"],
        [
            ["Pecos County — ERCOT queue", ("12,039", "n r"), ("39", "n r")],
            ["Adjacent six counties — operating", ("7,022", "n r"), ("—", "n r")],
            ["Adjacent six counties — queued", ("24,585", "n r"), ("—", "n r")],
            ["Within 20 miles of the tract — queued", ("3,973", "n r"), ("13", "n r")],
        ],
        widths=["auto", "80px", "80px"], cls="tall")
    body = f"""
<div style="display:flex;gap:44px">
  <div style="width:490px">
    {chart}
    <div class="m cap" style="margin-top:10px">
      Exhibit D &nbsp;·&nbsp; Pecos County operating capacity by technology (EIA-860).</div>
    <div class="rule" style="margin:18px 0 14px"></div>
    <div style="display:flex;gap:20px">
      {tile("Nearest operating storage", "1.9 mi", "St. Gall Energy Storage I", "val-s")}
      {tile("Its rating", "103 MW", "battery storage", "val-s")}
    </div>
    <div class="rule" style="margin:20px 0 12px"></div>
    <div class="fnote">
      Operating capacity is the in-service EIA-860 fleet for Pecos County. The county's
      ERCOT queue is 3.7× its operating fleet before either feature anchor is counted;
      neither anchor appears in the queue totals on this page.</div>
  </div>
  <div style="width:610px">
    {op}
    <div style="height:26px"></div>
    {q}
    <div class="fnote" style="margin-top:14px">
      Adjacent six counties: Reeves, Crane, Ward, Upton, Ector and Crockett. Queue
      figures are ERCOT interconnection-queue positions, not committed capacity;
      operating figures are the EIA-860 fleet.</div>
  </div>
</div>"""
    return page(6, "Regional Power Cluster", "Regional Power Cluster",
                "12 GW is already queued in this county alone — before counting either "
                "of the two hyperscale campuses profiled on pages 11 and 12.", body)


# ===========================================================================
# 07 — Water
# ===========================================================================
def p07():
    bar = f"""
<div style="margin-top:8px">
  <div style="display:flex;height:34px;border:1px solid {RULE}">
    <div style="width:66.6%;background:{BLUE}"></div>
    <div style="flex:1;background:{PANEL}"></div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:8px">
    <div class="m" style="font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:{BLUE}">
      ≈ two-thirds — permitted to this position</div>
    <div class="m" style="font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:{INK45}">
      remainder of district industrial rights</div>
  </div>
</div>"""
    tbl = table(
        ["Parameter", "Detail"],
        [
            [("Permitted volume", "k"), "47,418 acre-feet per year — 42.3 million gallons per day"],
            [("Held on", "k"), "Adjacent affiliated lands, permitted through the Middle Pecos GCD"],
            [("District share", "k"), "Roughly two-thirds of all Middle Pecos GCD industrial water rights"],
            [("Source", "k"), "Edwards-Trinity (Plateau) aquifer"],
            [("Recharge record", "k"), "Held through the 1950s drought of record"],
        ],
        widths=["148px", "auto"], cls="tall")
    body = f"""
<div style="display:flex;gap:40px">
  <div style="width:600px">
    {tbl}
    <div class="rule" style="margin:22px 0 16px"></div>
    <div class="m kicker">Share of Middle Pecos GCD industrial water rights</div>
    {bar}
    <div class="fnote" style="margin-top:18px">
      Volumes are permitted rights held on adjacent affiliated lands, recorded with the
      Middle Pecos Groundwater Conservation District. The Edwards-Trinity (Plateau)
      aquifer is the producing source.</div>
  </div>
  <div style="width:504px">
    {tile("Permitted", "47,418 AF/yr", "acre-feet per year, Middle Pecos GCD")}
    <div style="height:24px"></div>
    {tile("Equivalent", "42.3 MGD", "million gallons per day")}
    <div style="height:24px"></div>
    {tile("Aquifer", "Edwards-Trinity", "Plateau; recharge held through the 1950s drought of record")}
    <div style="height:28px"></div>
    <div class="panel">
      <div class="p">
        The water conversation on this position is closed rather than open: the volume
        is permitted, not applied for, and it represents roughly two-thirds of the
        district's total industrial allocation. Closed-loop cooling on permitted
        non-potable groundwater is already the regional design pattern — see page 12.</div>
    </div>
  </div>
</div>"""
    return page(7, "Water", "Water",
                "Two-thirds of the district's industrial water rights are already "
                "permitted to this position — the water conversation is closed, "
                "not open.", body)


# ===========================================================================
# 08 — Natural Gas
# ===========================================================================
def p08():
    tbl = table(
        ["Parameter", "Quoted term"],
        [
            [("Volume", "k"), ("200,000 MMBtu / day", "n")],
            [("Tenor", "k"), ("15 years", "n")],
            [("Pricing", "k"), ("Waha index", "n")],
            [("CIAC", "k"), ("$15–25 million", "n")],
            [("Lead time", "k"), ("9–15 months", "n")],
            [("Distance to hub", "k"), ("20 miles to Waha", "n")],
        ],
        widths=["150px", "auto"], cls="tall")
    body = f"""
<div style="display:flex;gap:40px">
  <div style="width:520px">
    <div class="m kicker">Indicative supply quote — terms in hand</div>
    <div style="height:12px"></div>
    {tbl}
    <div class="fnote" style="margin-top:14px">
      Terms above are counterparty-supplied and indicative, not a binding offer.</div>
    <div class="rule" style="margin:22px 0 16px"></div>
    <div style="display:flex;gap:22px">
      {tile("To Waha hub", "20 mi", "", "val-s")}
      {tile("Quoted volume", "200 MMcf/d", "order of magnitude", "val-s")}
      {tile("Quoted tenor", "15 yr", "", "val-s")}
    </div>
  </div>
  <div style="width:584px">
    <div class="m kicker">Basis context</div>
    <div class="p" style="margin-top:8px">
      Waha trades at a structural discount to Henry Hub, with negative prints recorded
      in 2024 and 2025 as Permian egress rebalances. That basis is the same economic
      signal now drawing behind-the-meter generation into this corridor — including the
      two campuses profiled on pages 11 and 12, both of which plan on-site gas
      generation rather than grid supply.</div>
    <div style="height:16px"></div>
    <div class="m kicker">Egress projects rebalancing Permian basis</div>
    <div style="margin-top:10px">
      <span class="m chip">Matterhorn</span><span class="m chip">Blackcomb</span>
      <span class="m chip">Hugh Brinson</span><span class="m chip">GCX</span>
    </div>
    <div class="rule" style="margin:18px 0 16px"></div>
    <div class="m kicker">Schedule-critical variables</div>
    <div class="p" style="margin-top:8px">
      The CIAC range of <b>$15–25 million</b> and the <b>9–15 month</b> lead time are
      the two schedule-critical terms in the fuel path; both are quoted, so they can be
      diligenced rather than estimated.</div>
    <div style="height:20px"></div>
    <div class="panel">
      <div class="p">
        A signable 15-year quote at Waha index pricing is a different asset than a
        pipeline interconnect study. It converts the fuel question from a development
        risk into a commercial term, at a hub 20 miles away.</div>
    </div>
  </div>
</div>"""
    return page(8, "Natural Gas", "Natural Gas",
                "A signable 15-year gas quote at Waha basis — the same structural "
                "discount now drawing behind-the-meter generation into this corridor.",
                body)


# ===========================================================================
# 09 — The Regional Pipeline (large map)
# ===========================================================================
def p09():
    left = f"""
<div style="width:270px">
  <div class="p" style="font-size:11.8px">
    The named large-load and generation projects in this corridor do not sit scattered
    across the basin. They line up along the I-10 / Highway 18 axis that runs through
    the property, with the two feature anchors due north and due south of it.</div>
  <div class="rule" style="margin:16px 0 14px"></div>
  {tile("Queued within 20 miles", "3,973 MW", "13 ERCOT-queue projects", "val-s")}
  <div style="height:18px"></div>
  {tile("Nearest operating storage", "1.9 mi", "St. Gall Energy Storage I — 103 MW", "val-s")}
  <div style="height:18px"></div>
  {tile("Anchor bearings", "19° / 188°", "GW Ranch north, Longfellow south", "val-s")}
  <div class="fnote" style="margin-top:16px">
    Exhibit E &nbsp;·&nbsp; Regional map with callout rail. Geometry drawn from the GIS
    layers described on page 15: the Caramba North tract, HIFLD transmission, the ERCOT
    queue and TIGER highways. The two feature anchors are plotted as markers at their
    disclosed site coordinates — the same points every distance in this document is
    measured to — and the subject position is the only boundary drawn.</div>
</div>"""
    body = f"""
<div style="display:flex;gap:44px;align-items:flex-start">
  {left}
  <div style="width:830px;height:525px;overflow:hidden">{vsvg("corridor_light")}</div>
</div>"""
    return page(9, "The Regional Pipeline", "The Regional Pipeline",
                "The named large-load projects in this corridor sit on one axis through "
                "the property — the site is inside the formation, not adjacent to it.",
                body, body_top=150, body_h=552, head_top=32, title_size=28,
                ftr_bottom=18)


# ===========================================================================
# 10 — Ring Analysis
# ===========================================================================
def p10():
    rings = table(
        ["Radius from tract", "~Operating + queued", "~Increment"],
        [
            [("≤ 15 miles", "k"), ("0.5 GW", "n r"), ("—", "n r")],
            [("≤ 30 miles", "k"), ("8.9 GW", "n r"), ("+8.4", "n r")],
            [("≤ 60 miles", "k"), ("32.7 GW", "n r"), ("+23.8", "n r")],
            [("≤ 100 miles", "k"), ("53.5 GW", "n r"), ("+20.8", "n r")],
        ],
        widths=["auto", "140px", "100px"])
    body = f"""
<div style="display:flex;gap:34px;align-items:flex-start">
  <div style="width:430px">
    <div style="width:430px;height:430px;overflow:hidden">{vsvg("chart_rings_light")}</div>
    <div class="m cap" style="margin-top:6px;width:430px">
      Exhibit A &nbsp;·&nbsp; Cumulative capacity by radius, with the two anchors plotted
      at true bearing and distance from the tract.</div>
  </div>
  <div style="width:670px">
    {rings}
    <div class="fnote" style="margin-top:9px">
      Region-wide totals computed from the same EIA-860 operating fleet and ERCOT
      interconnection-queue layers used throughout; not county-bounded. Increments are
      the additional capacity captured by each successive ring. GW Ranch bears ≈19°
      (almost due north) and Longfellow ≈188° (almost due south) from the tract, so the
      property sits on the line between them rather than off to one side.</div>
    <div class="rule" style="margin:18px 0 14px"></div>
    <div class="m kicker">Maturity of the two feature anchors</div>
    <div style="width:500px;height:170px;overflow:hidden;margin-top:8px">
      {vsvg("chart_maturity_light")}</div>
    <div class="fnote" style="margin-top:8px">
      Exhibit F &nbsp;·&nbsp; 79.3% of the two anchors' combined announced MW is under
      construction; 20.7% is in planned / phase-1 status — the regional pipeline is
      majority-built, not majority-speculative.</div>
  </div>
</div>"""
    return page(10, "Ring Analysis", "Ring Analysis",
                "Capacity compounds with radius — 0.5 GW at 15 miles, 32.7 GW at 60, "
                "53.5 GW at 100 — and the tract sits at the centre of that gradient.",
                body)


# ===========================================================================
# 11 — GW Ranch
# ===========================================================================
def p11():
    tbl = table(
        ["Item", "Detail"],
        [
            [("Site", "k"), "8,000 acres, Pecos County"],
            [("Distance", "k"), "≈ 15.5 miles from the Caramba North tract boundary, edge-to-edge"],
            [("Ownership", "k"), "Amazon — ownership disclosed August 2026"],
            [("Developer", "k"), "Pacifico Energy Group remains power-plant developer and operator"],
            [("Generation", "k"), "35 gas turbines; 7.65 GW TCEQ air permit issued Jan / Feb 2026 — the largest in the US"],
            [("Storage", "k"), "1.8 GW battery storage"],
            [("Solar", "k"), "Up to 750 MW"],
            [("Buildings", "k"), "Three data-center buildings of 189,000 sq ft each (Gensler design), ≈ $300M each"],
            [("Target completion", "k"), "December 2026"],
            [("Investment", "k"), "≈ $12 billion estimated total project investment"],
            [("Status", "k"), "Under construction"],
        ],
        widths=["150px", "auto"])
    body = f"""
<div style="display:flex;gap:34px">
  <div style="width:648px">
    {tbl}
    <div class="fnote" style="margin-top:14px">
      TCEQ's own record locates the site "~17 mi north of Fort Stockton on Highway 18" —
      a measurement from the town. The 15.5-mile figure above is measured from the
      Caramba North tract boundary; see page 16.</div>
  </div>
  <div style="width:462px">
    <div style="display:flex;gap:20px">
      {tile("Distance", "15.5 mi", "edge-to-edge, due north (≈19°)", "val-s")}
      {tile("Air permit", "7.65 GW", "TCEQ, issued Jan / Feb 2026", "val-s")}
    </div>
    <div style="height:22px"></div>
    <div style="display:flex;gap:20px">
      {tile("Site", "8,000 ac", "Pecos County", "val-s")}
      {tile("Turbines", "35", "natural gas", "val-s")}
    </div>
    <div style="height:22px"></div>
    <div style="display:flex;gap:20px">
      {tile("Storage", "1.8 GW", "battery", "val-s")}
      {tile("Solar", "750 MW", "up to", "val-s")}
    </div>
    <div style="height:24px"></div>
    <div class="panel">
      <div class="m kicker kicker-r">Clarification to retain</div>
      <div class="p" style="margin-top:8px">
        The 7.65 GW figure is a TCEQ <b>generation air permit</b>, not an ERCOT
        interconnection-queue position. Amazon has not disclosed an ERCOT filing and the
        project is off-grid initially. That distinction matters against the state-level
        queue context on page 13.</div>
    </div>
  </div>
</div>"""
    return page(11, "GW Ranch", "GW Ranch",
                "The largest air permit issued in the US this year sits fifteen miles up "
                "the same highway corridor — under construction, not announced.", body)


# ===========================================================================
# 12 — Longfellow
# ===========================================================================
def p12():
    tbl = table(
        ["Item", "Detail"],
        [
            [("Site", "k"), "568 acres, Pecos County"],
            [("Distance", "k"), "≈ 19.3 miles from the Caramba North tract boundary, edge-to-edge"],
            [("Announced", "k"), "October 2025 — a 2 GW campus in 8 phases of 250 MW each"],
            [("Generation", "k"), "On-site natural gas planned: aero-derivative turbines with SCR and carbon-capture capability"],
            [("Cooling", "k"), "Closed-loop, on permitted non-potable groundwater"],
            [("Status", "k"), "Phase-1 site work underway; on-site generation build planned in phases"],
            [("Permitting", "k"), "No confirmed ERCOT queue position or TCEQ air-permit record found for this site as of August 2026"],
        ],
        widths=["150px", "auto"], cls="tall")
    body = f"""
<div style="display:flex;gap:34px">
  <div style="width:648px">
    {tbl}
    <div class="rule" style="margin:20px 0 14px"></div>
    <div class="fnote">
      Longfellow's own public materials describe the location as "more than 25 miles
      outside of Fort Stockton." The 19.3-mile figure above is measured to the Caramba
      North tract boundary, which lies north of Fort Stockton — the two statements are
      consistent, and this distance should not be represented as shorter. See the
      methodology note on page 16. The permitting line is a statement of record status
      as searched, not a comment on the project.</div>
  </div>
  <div style="width:462px">
    <div style="display:flex;gap:20px">
      {tile("Distance", "19.3 mi", "edge-to-edge, due south (≈188°)", "val-s")}
      {tile("Site", "568 ac", "Pecos County", "val-s")}
    </div>
    <div style="height:22px"></div>
    <div style="display:flex;gap:20px">
      {tile("Announced", "2 GW", "October 2025", "val-s")}
      {tile("Phasing", "8 × 250 MW", "as announced", "val-s")}
    </div>
    <div style="height:24px"></div>
    <div class="panel">
      <div class="m kicker kicker-r">Why it belongs in this document</div>
      <div class="p" style="margin-top:8px">
        Read purely as infrastructure, Longfellow is the second phased gas-generation
        campus inside twenty miles. It establishes that demand for on-site power in this
        corridor is not one project deep, and that closed-loop cooling on permitted
        non-potable groundwater is the regional design pattern — the same water position
        described on page 7.</div>
    </div>
    <div style="height:20px"></div>
    <div class="rule"></div>
    <div class="fnote" style="margin-top:10px">
      Site dimensions and phasing as announced publicly in October 2025; generation and
      cooling design as described in the project's own public materials; permitting
      status as searched in August 2026.</div>
  </div>
</div>"""
    return page(12, "Longfellow", "Longfellow",
                "A second phased gas-generation campus twenty miles south — the "
                "corridor's demand for on-site power isn't one project deep.", body)


# ===========================================================================
# 13 — ERCOT queue context
# ===========================================================================
def p13():
    body = f"""
<div style="display:flex;gap:40px">
  <div style="width:480px">
    <div style="width:480px;height:343px;overflow:hidden">{vsvg("chart_queue_growth_light")}</div>
    <div class="m cap" style="margin-top:8px">
      Exhibit G &nbsp;·&nbsp; ERCOT interconnection queue, 2024 → 2026 (public reporting).</div>
    <div style="display:flex;gap:22px;margin-top:20px">
      {tile("Of the Nov 2025 queue", "77%", "data centers targeting 2030 interconnection", "val-s")}
      {tile("Of the Aug 2026 backlog", "≈ 90%", "data-center driven", "val-s")}
    </div>
  </div>
  <div style="width:624px">
    <div class="m kicker">What happened</div>
    <div class="p" style="margin-top:8px">
      ERCOT's large-load interconnection queue grew from <b>63 GW</b> at the end of 2024
      to <b>226 GW</b> by November 2025 — nearly quadrupling in a year — with roughly
      <b>77%</b> of that load being data centers targeting 2030 interconnection. By
      August 2026 the statewide backlog of pending requests reached approximately
      <b>474 GW</b>, about <b>90%</b> data-center driven: more than five times the state's
      record peak demand, per Governor Abbott.</div>
    <div style="height:16px"></div>
    <div class="m kicker">What it triggered</div>
    <div class="p" style="margin-top:8px">
      An August 3, 2026 directive to audit all ERCOT-queue data centers, and a pause of
      the "Batch Zero" large-load review process pending that audit.</div>
    <div class="rule" style="margin:18px 0 14px"></div>
    <div class="m kicker">Why it frames this site</div>
    <div class="p" style="margin-top:8px">
      The 32.7 GW around Caramba North sits inside a state-level queue large enough to
      have created a policy problem. That is a different and more testable claim than
      "this area is growing." It also sharpens the distinction on page 11: GW Ranch is
      permitted through TCEQ and off-grid initially, so its capacity does not depend on
      the queue that is now paused.</div>
    <div class="rule" style="margin:18px 0 12px"></div>
    <div class="fnote">
      Sources: Latitude Media, "ERCOT's large load queue has nearly quadrupled in a single
      year," December 3, 2025. Utility Dive, "Facing an estimated 474 GW of interconnection
      requests, Texas hits pause on data centers," August 2026.</div>
  </div>
</div>"""
    return page(13, "ERCOT Queue Context", "ERCOT Queue Context",
                "The statewide backlog reached roughly 474 GW and triggered a "
                "queue-processing pause — the demand signal is large enough to have "
                "created a policy problem.", body)


# ===========================================================================
# 14 — Subsurface & drilling
# ===========================================================================
def p14():
    prox = table(
        ["Proximity to tract", "~New drills"],
        [
            [("Within 2 miles", "k"), ("0", "n r")],
            [("Within 5 miles", "k"), ("0", "n r")],
            [("Within 10 miles", "k"), ("1", "n r")],
            [("Beyond 10 miles", "k"), ("114", "n r")],
        ],
        widths=["auto", "80px"])
    body = f"""
<div>
  <div style="display:flex;gap:20px">
    {tile("New-drill events, Pecos County since 2020", "115", "of 1,140 total RRC wellbore events", "val-s")}
    {tile("New-drill share of RRC activity", "10%", "the other 90% are workovers and reworks", "val-s")}
    {tile("Peer-county average", "1,181", "six comparable Permian counties", "val-s")}
    {tile("Pecos vs. peer average", "≈ 90% below", "lowest of all seven counties", "val-s")}
  </div>
  <div style="height:20px"></div>
  <div style="display:flex;gap:30px;align-items:flex-start">
    <div style="width:730px">
      <div style="width:730px;height:348px;overflow:hidden">{vsvg("chart_peer_drilling_light")}</div>
      <div class="m cap" style="margin-top:6px">
        Exhibit H &nbsp;·&nbsp; New-drill wellbore events since 2020 — Pecos County
        against six comparable Permian counties (RRC dbf900).</div>
    </div>
    <div style="width:384px">
      {prox}
      <div class="fnote" style="margin-top:10px">
        Nearest new-drill well since 2020 is 9.37 miles away. Beyond 10 miles the median
        distance is 19.9 miles and the mean 20.9 miles.</div>
      <div class="rule" style="margin:16px 0 12px"></div>
      <div class="m kicker">Well status inside 10 miles</div>
      <div class="p" style="margin-top:7px">
        <b>83%</b> of non-plugged wellbores within 10 miles are marginal or end-of-life
        production, against 60% at ≤2 miles and 62% at ≤5 miles — the closer ring is
        quieter still.</div>
    </div>
  </div>
</div>"""
    return page(14, "Subsurface & Drilling", "Subsurface &amp; Drilling Activity",
                "Pecos County has the lowest new-drilling count of seven comparable "
                "Permian counties since 2020 — roughly 90% below the peer average.", body)


# ===========================================================================
# 15 — The Diligence Platform
# ===========================================================================
def p15():
    src = table(
        ["Dataset", "Publisher / series"],
        [
            [("Interconnection", "k"), "ERCOT GIS Report; ERCOT TPIT"],
            [("Transmission siting", "k"), "PUCT dockets"],
            [("Generating fleet", "k"), "EIA-860"],
            [("Air permits", "k"), "TCEQ"],
            [("Wells & permits", "k"), "RRC dbf900, production records, W-1"],
            [("Completions", "k"), "FracFocus"],
            [("Groundwater", "k"), "Middle Pecos GCD"],
            [("Infrastructure", "k"), "HIFLD; USGS; BTS; Census TIGER"],
        ],
        widths=["160px", "auto"], cls="tall")
    cadence = table(
        ["Layer", "~Refresh"],
        [
            [("RRC wells and permits", "k"), ("Weekly", "n r")],
            [("ERCOT queue and TPIT", "k"), ("Monthly", "n r")],
            [("EIA / USGS / OSM", "k"), ("Annually", "n r")],
        ],
        widths=["auto", "100px"])
    body = f"""
<div style="display:flex;gap:34px">
  <div style="width:560px">
    {src}
    <div class="fnote" style="margin-top:12px">
      Every point, line and boundary in the platform carries a per-feature source popup
      naming its dataset, so any figure in this document can be traced back to the
      record it came from.</div>
  </div>
  <div style="width:550px">
    {cadence}
    <div style="height:24px"></div>
    <div class="m kicker">Working tools</div>
    <div class="p" style="margin-top:8px">
      Filters by county, depth, spud year, fuel and status; a time scrubber; and
      measure, share and print tools. The build is static and versioned, the deployed
      bundle is byte-verified on release, and access is logged.</div>
    <div class="rule" style="margin:20px 0 16px"></div>
    <div style="display:flex;gap:20px">
      {tile("Build", "Static", "versioned, byte-verified", "val-s")}
      {tile("Access", "Logged", "credentials issued separately", "val-s")}
    </div>
    <div style="height:20px"></div>
    <div class="panel">
      <div class="m" style="font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:{INK45}">
        Platform</div>
      <div class="m" style="font-size:17px;font-weight:600;margin-top:6px;color:{INK}">
        lrp-tx-gis.netlify.app</div>
      <div class="note" style="margin-top:6px">
        Credentials issued to the deal team separately.</div>
    </div>
  </div>
</div>"""
    return page(15, "The Diligence Platform", "The Diligence Platform",
                "Every figure in this document is independently re-derivable from a "
                "cited public source — this isn't a broker's summary.", body)


# ===========================================================================
# 16 — Methodology & sources
# ===========================================================================
def p16():
    dist = table(
        ["Site", "~Edge-to-edge", "~Centroid-to-centroid"],
        [
            [("GW Ranch", "k"), ("15.5 mi", "n r"), ("17.3 mi", "n r")],
            [("Longfellow", "k"), ("19.3 mi", "n r"), ("19.7 mi", "n r")],
        ],
        widths=["auto", "130px", "180px"], cls="tall")
    body = f"""
<div style="display:flex;gap:40px">
  <div style="width:604px">
    <div class="m kicker">Distance methodology</div>
    <div class="p" style="margin-top:8px">
      Distances to GW Ranch and Longfellow are measured <b>edge-to-edge</b>: from the
      nearest point on the Caramba North tract boundary to each site's disclosed
      location, rather than centroid-to-centroid. Edge-to-edge is consistently the
      shorter of the two because the Caramba North tract has its own spatial extent.
      The edge-to-edge figures are the ones used everywhere else in this document; the
      centroid figures appear here and nowhere else.</div>
    <div style="height:18px"></div>
    {dist}
    <div class="fnote" style="margin-top:14px">
      Longfellow's own public site describes its location as more than 25 miles outside
      Fort Stockton, which is consistent with the longer of these figures; that distance
      should not be represented as shorter. The TCEQ record for GW Ranch places it
      "~17 mi north of Fort Stockton on Highway 18" — a measurement from the town, not
      from this tract.</div>
    <div class="rule" style="margin:20px 0 14px"></div>
    <div class="m kicker">Vintage</div>
    <div class="p" style="margin-top:8px">
      All figures are stated as of August 2026, on the refresh cadence set out on
      page 15.</div>
  </div>
  <div style="width:504px">
    <div class="m kicker">Cited third-party reporting</div>
    <div style="height:12px"></div>
    <div class="p" style="border-top:1px solid {RULE};padding-top:12px">
      Latitude Media, "ERCOT's large load queue has nearly quadrupled in a single year,"
      December 3, 2025.</div>
    <div class="p" style="border-top:1px solid {RULE};padding-top:12px;margin-top:12px">
      Utility Dive, "Facing an estimated 474 GW of interconnection requests, Texas hits
      pause on data centers," August 2026.</div>
    <div class="rule" style="margin:22px 0 16px"></div>
    <div class="m kicker">Other source classes</div>
    <div class="p" style="margin-top:8px">
      TCEQ air-permit records for the GW Ranch generation permit; PUCT PBRP Docket No.
      55718 for the 765 kV import approvals; Middle Pecos GCD for permitted groundwater;
      RRC dbf900 and W-1 records for wellbore activity. Public-data figures drawn from
      the GIS model on page 15 carry their citation in the platform's per-feature source
      popups.</div>
    <div style="height:22px"></div>
    <div class="panel">
      <div class="p">
        Where a figure is not in the GIS data model — ERCOT queue-growth totals, TCEQ
        permit language, news items — the source class is named at the point of use.</div>
    </div>
  </div>
</div>"""
    return page(16, "Methodology & Sources", "Methodology &amp; Sources",
                "Distances here are edge-to-edge from the tract boundary — shorter than "
                "centroid-to-centroid, and stated in full so the figures can be checked.",
                body)


# ===========================================================================
# 17 — Notices
# ===========================================================================
def p17():
    clauses = [
        ("Confidentiality",
         "This memorandum is confidential and has been prepared for a limited number of "
         "prospective counterparties under a non-disclosure agreement. It may not be "
         "reproduced or distributed, in whole or in part, without prior written consent."),
        ("No offer",
         "This memorandum is not an offer to sell, nor a solicitation of an offer to buy, "
         "any security or interest. No agreement or obligation arises from its delivery or "
         "from any discussion it prompts."),
        ("Preliminary information",
         "The information here is preliminary and indicative. It has been drawn from "
         "sources believed to be reliable, but no representation or warranty, express or "
         "implied, is made as to its accuracy or completeness. Indicative commercial terms, "
         "including the gas supply quote on page 8, are counterparty-supplied and subject "
         "to change."),
        ("Public data",
         "Public data reproduced in this memorandum is drawn from the datasets listed on "
         "page 15 and is re-derivable from those sources. Third-party transaction and "
         "policy reporting is sourced to the public reporting cited on page 16 and in the "
         "companion source register."),
        ("Forward-looking statements",
         "Statements regarding planned capacity, construction timing, permitting status "
         "and regional development reflect information available as of August 2026 and are "
         "subject to change without notice."),
    ]
    rows = ""
    for i, (h, t) in enumerate(clauses, 1):
        rows += f"""
<div style="display:flex;gap:18px;padding:15px 0;border-top:1px solid {RULE}">
  <div class="m" style="width:26px;font-size:10px;color:{BLUE};padding-top:2px">{i:02d}</div>
  <div class="m" style="width:190px;font-size:9.5px;letter-spacing:.14em;
       text-transform:uppercase;color:{INK};padding-top:2px">{h}</div>
  <div style="flex:1;min-width:0"><div class="p">{t}</div></div>
</div>"""
    body = f"""
<div style="width:1010px">{rows}
  <div style="border-top:1px solid {INK};margin-top:16px;padding-top:16px;
       display:flex;justify-content:space-between">
    <div class="m" style="font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:{INK45}">
      Caramba North &nbsp;·&nbsp; Pecos County, Texas</div>
    <div class="m" style="font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:{INK45}">
      Confidential Offering Memorandum &nbsp;·&nbsp; August 2026</div>
  </div>
</div>"""
    return page(17, "Notices", "Notices",
                "This memorandum is preliminary and indicative, circulated under NDA to a "
                "limited number of counterparties — read the clauses below as binding on "
                "its use.", body)


# ===========================================================================
def main():
    pages = [p01(), p02(), p03(), p04(), p05(), p06(), p07(), p08(), p09(),
             p10(), p11(), p12(), p13(), p14(), p15(), p16(), p17()]
    assert len(pages) == TOTAL_PAGES, len(pages)
    html = T.document("institutional",
                      EXHIBIT_FONT_CSS + CSS + "\n".join(pages), "landscape",
                      "Caramba North — Institutional")
    out = T.REPO / "outputs" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    stem = out / "Caramba-North-Deck-Institutional"
    stem.with_suffix(".html").write_text(html, encoding="utf-8")
    print("html", stem.with_suffix(".html"),
          stem.with_suffix(".html").stat().st_size // 1024, "KB")
    T.render_pdf(str(stem.with_suffix(".html")), str(stem.with_suffix(".pdf")))
    print("pdf ", stem.with_suffix(".pdf"))


if __name__ == "__main__":
    main()
