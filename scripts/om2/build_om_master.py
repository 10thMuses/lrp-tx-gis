#!/usr/bin/env python3
"""Caramba North — the merged offering memorandum (`Caramba-North-OM.html/.pdf`).

One book, two parts, one type system.

  PART I  — the Institutional deck, unchanged in substance, renumbered, with
            four full-bleed statement pages borrowed from the Minimal deck's
            idiom dropped in as section openers, and an appendix divider.
  PART II — the Technical drawing set, re-set as Appendix A (sheets A-01 to
            A-13) on the book's own warm paper, with the drafting grid removed.

Nothing here rewrites content. The two source builders are imported and their
page functions called; this module only renumbers, re-grounds and composes.

How the re-grounding works: both builders read their palette out of
`om_theme.SYSTEMS[...]` into module globals at import, and their page
functions read those globals at call time. So mutating `TECH.RULE` (etc.)
before calling `TECH.sheet01()` changes what that sheet emits. Two things are
baked at import and are therefore re-authored here rather than imported:
`TECH.EXTRA_CSS` (which carries the `.grid` rule and the cool paper) and the
literal `<div class="grid"></div>` every technical sheet emits.

The whole document is wrapped with `T.document("institutional", ...)`, so
`class="d"` resolves to Newsreader and unclassed body copy to Public Sans
throughout — the appendix picks up the book's faces while its tables, figure
captions and title blocks stay IBM Plex Mono. That is what binds Appendix A to
the body instead of letting it read as a second deck.

    python3 scripts/om2/build_om_master.py
"""
from __future__ import annotations

import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import om_theme as T                    # noqa: E402
import build_deck_institutional as INST  # noqa: E402
import build_deck_technical as TECH      # noqa: E402

W, H = T.SLIDE_W, T.SLIDE_H
S = T.SYSTEMS["institutional"]

PAPER = S["paper"]          # #FBFAF7 warm — the book's one paper
INK = S["ink"]
INK70 = S["ink70"]
INK45 = S["ink45"]
INK25 = S["ink25"]
RULE = S["rule"]            # #D9D4CB
PANEL = S["panel"]
RED = S["accent"]           # reserved: subject site + the two feature anchors
BLUE = S["third"]           # institutional lead accent, and technical's accent
SUBINK = "#39434E"

PAD = INST.PAD              # 68
CW = INST.CW                # 1144

STEM = "Caramba-North-OM"

# ---------------------------------------------------------------------------
# PART I structure. Original institutional page -> its page in this book.
# The four statement pages are section openers: each sits immediately before
# the page that develops its number.
# ---------------------------------------------------------------------------
BODY_PAGES = 22             # 01-22; Appendix A then runs A-01 - A-13
APPENDIX_SHEETS = 13

PAGE_MAP = {
    1: 1,    # cover
    2: 2,    # contents (re-authored below)
    3: 3,    # positioning
    4: 4,    # the property
    5: 5,    # transmission
    6: 6,    # regional power cluster
    #        7  = STATEMENT  47,418 AF/yr
    7: 8,    # water
    8: 9,    # natural gas
    9: 10,   # the regional pipeline
    #        11 = STATEMENT  32.7 GW
    10: 12,  # ring analysis
    #        13 = STATEMENT  79.3%
    11: 14,  # GW Ranch
    12: 15,  # Longfellow
    13: 16,  # ERCOT queue context
    #        17 = STATEMENT  115
    14: 18,  # subsurface & drilling
    15: 19,  # the diligence platform
    16: 20,  # methodology & sources
    17: 21,  # notices
    #        22 = APPENDIX DIVIDER
}


# ---------------------------------------------------------------------------
# Extra CSS. Institutional's own CSS ships as-is (INST.CSS); the technical
# frame CSS is re-authored: no `.grid`, and the title/footer bands take the
# book's warm paper instead of technical's cool #F4F6F7.
# ---------------------------------------------------------------------------
APPENDIX_CSS = f"""
<style>
.frame {{ position:absolute; left:24px; top:24px; right:24px; bottom:24px;
  border:1px solid {RULE}; display:flex; flex-direction:column; }}
.tb, .fb {{ background:{PAPER}; }}
.tb {{ height:66px; flex:none; display:flex; border-bottom:1px solid {RULE}; }}
.tb > div:last-child {{ border-right:none; }}
.body {{ flex:1; min-height:0; padding:18px 24px; overflow:hidden; }}
.fb {{ height:24px; flex:none; border-top:1px solid {RULE}; display:flex;
  align-items:center; justify-content:space-between; padding:0 14px;
  font-family:{S['mono']}; font-size:7.6px; letter-spacing:.16em;
  color:{TECH.INK45}; }}
em {{ font-style:italic; }}
.stmt-hero {{ font-weight:500; letter-spacing:-0.035em; line-height:0.94;
  color:{INK}; white-space:nowrap; }}
.stmt-line {{ font-weight:400; letter-spacing:-0.015em; line-height:1.24;
  color:{INK}; }}
</style>
"""


# ===========================================================================
# PART I — statement pages (Minimal's idiom, institutional's type)
# ===========================================================================
def footer(num, section, total=BODY_PAGES):
    return f"""
  <div class="ftr">
    <div class="rule"></div>
    <div class="m row">
      <span>Caramba North &nbsp;—&nbsp; Confidential Offering Memorandum</span>
      <span>{section}</span>
      <span>{num:02d}&nbsp;/&nbsp;{total}</span>
    </div>
  </div>"""


def eyebrow(num, section):
    return f"""
  <div style="position:absolute;left:{PAD}px;top:50px;width:{CW}px">
    <div class="m eyebrow" style="display:flex;justify-content:space-between">
      <span><b>{num:02d}</b>&nbsp;&nbsp;/&nbsp;&nbsp;{section}</span>
      <span>Caramba North &nbsp;·&nbsp; Pecos County, Texas</span>
    </div>
  </div>"""


def statement(num, section, number, unit, line, note, hero_size=150,
              line_size=31, line_w=920):
    """One number, one sentence, one qualifier, and the rest of the page empty.

    Borrowed wholesale from `build_deck_minimal.hero()` / `textpage()`: the
    oversized figure carries the page and nothing competes with it. Re-set in
    Newsreader / Public Sans / Plex Mono on warm paper, so it reads as a
    section opener inside this book rather than as a page from another deck.
    """
    u = ""
    if unit:
        u = (f'<span class="d" style="font-size:{hero_size * 0.24:.0f}px;'
             f'font-weight:500;letter-spacing:-0.01em;color:{INK45};'
             f'margin-left:{hero_size * 0.09:.0f}px">{unit}</span>')
    return f"""
<div class="page">
{eyebrow(num, section)}
  <div style="position:absolute;left:{PAD}px;top:172px;width:{CW}px">
    <div style="width:38px;height:3px;background:{BLUE}"></div>
    <div class="d stmt-hero" style="font-size:{hero_size}px;margin-top:36px">
      {number}{u}</div>
    <div class="d stmt-line" style="font-size:{line_size}px;margin-top:36px;
         max-width:{line_w}px">{line}</div>
    <div class="m" style="font-size:10.5px;line-height:1.62;color:{INK45};
         max-width:760px;margin-top:28px">{note}</div>
  </div>
{footer(num, section)}
</div>"""


def p07_statement_water():
    return statement(
        7, "Water", "47,418", "AF/yr",
        "of permitted groundwater sit on adjacent affiliated lands &mdash; "
        "roughly two-thirds of all the industrial water rights the "
        "Middle Pecos district has issued.",
        "42.3 million gallons per day, drawn from the Edwards-Trinity "
        "(Plateau) aquifer, whose recharge held through the 1950s drought of "
        "record. Detail follows on page 08.")


def p11_statement_rings():
    return statement(
        11, "Ring Analysis", "32.7", "GW",
        "of operating and ERCOT-queued capacity sits within sixty miles "
        "of the tract. Caramba North is inside that radius, not adjacent to it.",
        "0.5 GW within 15 miles &nbsp;·&nbsp; 8.9 GW within 30 &nbsp;·&nbsp; "
        "53.5 GW within 100. Region-wide, computed from the EIA-860 "
        "operating fleet plus the ERCOT interconnection queue &mdash; not "
        "county-bounded. Detail follows on page 12.")


def p13_statement_maturity():
    return statement(
        13, "Project Maturity", "79.3", "%",
        "of the two anchor campuses&rsquo; combined announced capacity is "
        "already under construction &mdash; the pipeline on this axis is "
        "majority-built, not majority-proposed.",
        "GW Ranch: 7.65 GW permitted, under construction, 15.5 mi north. "
        "Longfellow: 2 GW announced, phase-1 site work underway, 19.3 mi "
        "south. Both distances edge-to-edge from the tract "
        "boundary; basis on page 20.")


def p17_statement_drilling():
    return statement(
        17, "Subsurface", "115", "",
        "new-drill wellbore events in Pecos County since 2020, against a "
        "1,181 average across six comparable Permian counties.",
        "Lowest of all seven by a wide margin &mdash; roughly 90% below the "
        "peer average. Zero new-drill wells within five miles of the "
        "tract; one within ten, at 9.37 miles. RRC wellbore records. Detail "
        "follows on page 18.")


# ===========================================================================
# 22 — Appendix divider
# ===========================================================================
def p22_divider():
    return f"""
<div class="page">
{eyebrow(22, "Appendix A")}
  <div style="position:absolute;left:{PAD}px;top:196px;width:{CW}px">
    <div style="width:38px;height:3px;background:{BLUE}"></div>
    <div class="d" style="font-size:78px;font-weight:500;letter-spacing:-0.03em;
         line-height:1;color:{INK};margin-top:36px">Appendix A</div>
    <div class="d" style="font-size:34px;font-weight:400;letter-spacing:-0.02em;
         line-height:1.2;color:{INK70};margin-top:16px">Technical Drawing Set</div>
    <div class="d sub" style="font-size:19px;margin-top:26px;max-width:860px">
      The same facts as the body, re-set at drawing-set density:
      thirteen numbered sheets, each with its own title block, numbered tables
      and framed figure plates.</div>
    <div class="rule" style="margin-top:34px;width:860px"></div>
    <div class="m" style="font-size:10px;letter-spacing:.2em;text-transform:uppercase;
         color:{INK45};margin-top:14px">
      Sheets A-01 &nbsp;&ndash;&nbsp; A-13 &nbsp;·&nbsp;
      Source register and distance basis on sheet A-13</div>
  </div>
{footer(22, "Appendix A")}
</div>"""


# ===========================================================================
# 02 — Contents (re-authored: this book has two parts, not one)
# ===========================================================================
PART_I = [
    ("03", "Positioning", "The corridor makes the case before the parcel does."),
    ("04", "The Property", "As-of-right industrial land; no rezoning path required."),
    ("05", "Transmission", "Fifteen miles from the 765 kV import terminus."),
    ("06", "Regional Power Cluster", "3,226 MW operating and 12,039 MW queued in-county."),
    ("07", "Water", "47,418 AF/yr permitted — two-thirds of district rights."),
    ("09", "Natural Gas", "A 15-year indicative quote at Waha index pricing."),
    ("10", "The Regional Pipeline", "Named large-load projects sit on one axis."),
    ("11", "Ring Analysis", "0.5 / 8.9 / 32.7 / 53.5 GW at 15 / 30 / 60 / 100 mi."),
    ("13", "GW Ranch", "7.65 GW air permit, under construction, 15.5 mi north."),
    ("15", "Longfellow", "Phased on-site gas generation, 19.3 miles south."),
    ("16", "ERCOT Queue Context", "A 474 GW backlog that triggered a state audit."),
    ("17", "Subsurface &amp; Drilling", "Lowest new-drill count of seven Permian counties."),
    ("19", "The Diligence Platform", "Every figure traces to a cited public dataset."),
    ("20", "Methodology &amp; Sources", "Distances are edge-to-edge; here is the arithmetic."),
    ("21", "Notices", "Preliminary and indicative; circulated under NDA."),
    ("22", "Appendix A", "Technical drawing set — sheets A-01 through A-13."),
]

PART_II = [
    ("A-01", "Title sheet — index, ring analysis"),
    ("A-02", "The property — 1,300 ac, I-10 frontage"),
    ("A-03", "Transmission — 765 kV terminus"),
    ("A-04", "Regional power cluster — fleet + queue"),
    ("A-05", "Water — Middle Pecos GCD rights"),
    ("A-06", "Natural gas — Waha basis, supply quote"),
    ("A-07", "Corridor + ring analysis"),
    ("A-08", "GW Ranch — 7.65 GW, 15.5 mi"),
    ("A-09", "Longfellow — phased generation, 19.3 mi"),
    ("A-10", "Queue and policy context"),
    ("A-11", "Subsurface activity — drilling record"),
    ("A-12", "Diligence platform — source register"),
    ("A-13", "Methodology and notices"),
]


def contents_page():
    def row(n, t, d):
        return f"""
<div style="display:flex;gap:14px;padding:7.5px 0;border-bottom:1px solid {RULE}">
  <div class="m" style="width:24px;font-size:10.5px;color:{BLUE};padding-top:3px">{n}</div>
  <div style="flex:1;min-width:0">
    <div class="d" style="font-size:14.5px;font-weight:500;line-height:1.2">{t}</div>
    <div class="note" style="margin-top:1px;font-size:10px">{d}</div>
  </div>
</div>"""

    def srow(n, t):
        return f"""
<div style="display:flex;gap:12px;padding:5.5px 0;border-bottom:1px solid {RULE}">
  <div class="m" style="width:36px;font-size:9.6px;color:{BLUE};font-weight:500">{n}</div>
  <div class="m" style="flex:1;min-width:0;font-size:9.6px;color:{INK70};
       line-height:1.25">{t}</div>
</div>"""

    def parthead(kicker, title):
        return f"""
<div style="margin-bottom:10px">
  <div class="m kicker">{kicker}</div>
  <div class="d" style="font-size:16px;font-weight:500;margin-top:5px;
       line-height:1.15">{title}</div>
  <div class="rule-k" style="margin-top:8px"></div>
</div>"""

    colA = "".join(row(*r) for r in PART_I[:8])
    colB = "".join(row(*r) for r in PART_I[8:])
    colC = "".join(srow(*r) for r in PART_II)

    body = f"""
<div style="display:flex;gap:26px">
  <div style="width:376px">
    {parthead("Part I &nbsp;·&nbsp; pages 01&ndash;22", "Memorandum")}
    {colA}
  </div>
  <div style="width:376px">
    <div style="height:56px"></div>
    {colB}
  </div>
  <div style="width:314px">
    {parthead("Part II &nbsp;·&nbsp; sheets A-01&ndash;A-13", "Appendix A &nbsp;—&nbsp; Technical Drawing Set")}
    {colC}
    <div class="fnote" style="margin-top:12px;line-height:1.55">
      Four pages in Part I carry a single figure and one sentence; each opens the
      section that develops it. Figures set in mono come from the GIS data model
      described on page 19. Distances to the two anchors are edge-to-edge from the
      tract boundary — see page 20.</div>
  </div>
</div>"""
    return INST.page(
        2, "Contents", "Contents",
        "Ordered from the region's numbers inward to the site's, then the same "
        "record again at drawing-set density — the corridor makes the case "
        "before the parcel does.", body)


# ===========================================================================
# PART II — Appendix A: the technical sheets, re-grounded and renumbered
# ===========================================================================
def _sheet_appendix(no, section, project_line, source, body,
                    issue="2026-08 · REV A"):
    """`TECH.sheet()` with A-numbering and no drafting grid.

    Same title block, same footer band, same frame — only the sheet label and
    the ground change. Technical's own `sheet()` is replaced with this before
    any sheet function is called, so every sheet picks it up.
    """
    lbl = f"A-{no:02d}"
    tot = f"A-{APPENDIX_SHEETS:02d}"
    tb = (
        TECH.cell("SHEET",
                  f"{lbl} <span style='color:{TECH.INK45};font-weight:400'>/ {tot}</span>",
                  width=152, mono_size=15, weight="600")
        + TECH.cell("SECTION", section, width=248)
        + TECH.cell("PROJECT", project_line, flex=True)
        + TECH.cell("SOURCE", source, width=330)
        + TECH.cell("ISSUE", issue, width=138)
    )
    return f"""
<div class="page">
  <div class="frame">
    <div class="tb">{tb}</div>
    <div class="body">{body}</div>
    <div class="fb">
      <div>CARAMBA NORTH · OFFERING MEMORANDUM · CONFIDENTIAL — DISTRIBUTED UNDER NDA</div>
      <div>PECOS COUNTY, TEXAS</div>
      <div>APPENDIX A · {lbl} / {tot}</div>
    </div>
  </div>
</div>"""


# a lowercase "sheet 07" / "sheets 08 and 09" in running copy — the title
# blocks and footer bands are uppercase, so this can never touch them.
_SHEETREF = re.compile(r'\bsheets?\s+\d{2}(?:\s+and\s+\d{2})?\b')


def _fix_sheet_refs(html):
    def sub(m):
        return re.sub(r'(\d{2})', r'A-\1', m.group(0))
    return _SHEETREF.sub(sub, html)


def build_appendix():
    # Re-ground: warm hairlines instead of technical's cool ones, so the frame
    # and the plate borders sit correctly on the book's paper. Read at call
    # time by every technical helper, so this must precede the sheet calls.
    TECH.RULE = RULE
    TECH.INK25 = INK25
    TECH.INK12 = S["ink12"]
    TECH.sheet = _sheet_appendix
    TECH.INDEX = [(f"A-{n}", t) for n, t in TECH.INDEX]

    sheets = [getattr(TECH, f"sheet{i:02d}")() for i in range(1, 14)]
    html = "\n".join(sheets)
    # technical emits a literal grid div per sheet; the appendix runs clean
    html = html.replace('<div class="grid"></div>', "")
    # one paper for the whole book
    html = html.replace("#F4F6F7", PAPER)
    return _fix_sheet_refs(html)


# ===========================================================================
# PART I — body, renumbered
# ===========================================================================
_PAGEREF = re.compile(r'\b(pages|page|p\.)\s+(\d{1,2})(\s+and\s+(\d{1,2}))?\b')


def _fix_page_refs(html):
    """Cross-references in running copy follow the renumbering."""
    def one(tok):
        n = PAGE_MAP.get(int(tok), int(tok))
        return f"{n:02d}" if len(tok) == 2 and tok[0] == "0" else str(n)

    def sub(m):
        word, a, b = m.group(1), m.group(2), m.group(4)
        out = f"{word} {one(a)}"
        if b:
            out += f" and {one(b)}"
        return out
    return _PAGEREF.sub(sub, html)


def build_body():
    INST.TOTAL_PAGES = BODY_PAGES
    orig_page = INST.page
    INST.page = lambda num, *a, **kw: orig_page(PAGE_MAP[num], *a, **kw)
    try:
        # only the imported pages carry the old numbering in their copy;
        # the pages authored in this module are already written in the new
        # scheme and must not be run through the map a second time.
        pages = {n: _fix_page_refs(getattr(INST, f"p{n:02d}")())
                 for n in range(1, 18)}
    finally:
        INST.page = orig_page

    ordered = [
        pages[1],                   # 01 cover
        contents_page(),            # 02 contents (replaces INST.p02)
        pages[3],                   # 03 positioning
        pages[4],                   # 04 the property
        pages[5],                   # 05 transmission
        pages[6],                   # 06 regional power cluster
        p07_statement_water(),      # 07 *
        pages[7],                   # 08 water
        pages[8],                   # 09 natural gas
        pages[9],                   # 10 the regional pipeline
        p11_statement_rings(),      # 11 *
        pages[10],                  # 12 ring analysis
        p13_statement_maturity(),   # 13 *
        pages[11],                  # 14 GW Ranch
        pages[12],                  # 15 Longfellow
        pages[13],                  # 16 ERCOT queue context
        p17_statement_drilling(),   # 17 *
        pages[14],                  # 18 subsurface & drilling
        pages[15],                  # 19 the diligence platform
        pages[16],                  # 20 methodology & sources
        pages[17],                  # 21 notices
        p22_divider(),              # 22 appendix divider
    ]
    assert len(ordered) == BODY_PAGES, len(ordered)
    return "\n".join(ordered)


# ===========================================================================
def main():
    body = build_body()
    appendix = build_appendix()
    pages = body + "\n" + appendix

    html = T.document("institutional",
                      INST.EXHIBIT_FONT_CSS + INST.CSS + APPENDIX_CSS + pages,
                      "landscape", "Caramba North — Offering Memorandum")

    out = T.REPO / "outputs" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    stem = out / STEM
    hp = stem.with_suffix(".html")
    hp.write_text(html, encoding="utf-8")
    n = html.count('<div class="page">')
    print(f"html -> {hp.relative_to(T.REPO)}  ({hp.stat().st_size // 1024} KB, "
          f"{n} pages: {BODY_PAGES} body + {APPENDIX_SHEETS} appendix)")
    T.render_pdf(str(hp), str(stem.with_suffix(".pdf")))
    print(f"pdf  -> {stem.with_suffix('.pdf').relative_to(T.REPO)}")


if __name__ == "__main__":
    main()
