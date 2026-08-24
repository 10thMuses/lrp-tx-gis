#!/usr/bin/env python3
"""Caramba North — Minimal Executive deck (system D, key `minimal`).

One idea per page. A single oversized Archivo figure or statement carries
each page; one heading and one conclusion-subheading sit under it; at most
one small stat row OR one exhibit. Everything else is negative space.

Twelve landscape pages, 1280x720, white ground, near-black ink. Four pages
carry an exhibit (rings, corridor, maturity, peer drilling); the other eight
are type only.

Every page is a flex column with the footer pushed down by `margin-top:auto`,
and every exhibit sits in a `flex:1; min-height:0` box — so an exhibit can
only ever shrink to fit, never overrun the fixed 1280x720 page box (where
`overflow:hidden` would silently clip it).

    python3 scripts/om2/build_deck_minimal.py
"""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import om_theme as T  # noqa: E402

REPO = T.REPO
OUT = REPO / "outputs" / "reports"
STEM = "Caramba-North-Deck-Minimal"

INK = "#0B0D0F"
INK70 = "#5C666F"
INK45 = "#9AA0A6"
INK25 = "#D6D9DC"
RULE = "#E3E5E8"
RED = "#B03A2E"
GOLD = "#C08A10"

TOTAL_PAGES = 12
PAD = "56px 80px 34px"


# ---------------------------------------------------------------------------
# Exhibits. The shared vector files are drawn on the warm institutional paper
# (#FBFAF7) in its ink (#12181F); this deck's ground is pure white, so the
# inlined markup is re-grounded on the way in. The source files are untouched.
# ---------------------------------------------------------------------------
def vec(name, viewbox=None):
    s = T.svg(name)
    s = (s.replace("#FBFAF7", "#FFFFFF")
          .replace("#12181F", INK)
          .replace("#F4F6F7", "#FFFFFF"))
    if viewbox:
        # corridor_wide draws its scale bar and third callout just below its
        # declared viewBox; widening the box brings them inside the frame.
        s = re.sub(r'viewBox="[^"]*"', f'viewBox="{viewbox}"', s, count=1)
    return s


def exhibit(name, viewbox=None, max_w=None, top=0, align="center",
            justify="center"):
    """An exhibit that fills the remaining page height and cannot overflow."""
    cap = f"max-width:{max_w}px;" if max_w else ""
    return (f'<div style="flex:1 1 auto;min-height:0;position:relative;'
            f'margin-top:{top}px">'
            f'<div style="position:absolute;inset:0;display:flex;'
            f'justify-content:{justify};align-items:{align}">'
            f'<div style="width:100%;height:100%;{cap}">'
            f'{vec(name, viewbox)}</div></div></div>')


# ---------------------------------------------------------------------------
# Page furniture
# ---------------------------------------------------------------------------
def eyebrow(text, mark=False):
    dot = (f'<span style="display:inline-block;width:26px;height:3px;'
           f'background:{RED};vertical-align:middle;margin-right:14px;'
           f'position:relative;top:-2px"></span>') if mark else ""
    return (f'<div class="m" style="flex:0 0 auto;font-size:11px;'
            f'letter-spacing:.24em;text-transform:uppercase;color:{INK45};'
            f'font-weight:500">{dot}{text}</div>')


def footer(n, push=True):
    top = "auto" if push else "24px"
    return (f'<div style="flex:0 0 auto;margin-top:{top};padding-top:12px;'
            f'border-top:1px solid {RULE};display:flex;'
            f'justify-content:space-between;align-items:flex-end">'
            f'<div class="m" style="font-size:10px;letter-spacing:.2em;'
            f'color:{INK45}">CARAMBA NORTH &middot; PECOS COUNTY, TEXAS</div>'
            f'<div class="m" style="font-size:10px;letter-spacing:.2em;'
            f'color:{INK45}">{n:02d} / {TOTAL_PAGES}</div></div>')


def hero(number, unit=None, size=150):
    u = ""
    if unit:
        u = (f'<span class="d" style="font-size:{size*0.26:.0f}px;font-weight:500;'
             f'letter-spacing:-0.01em;color:{INK45};margin-left:{size*0.10:.0f}px">'
             f'{unit}</span>')
    return (f'<div class="d" style="font-size:{size}px;font-weight:600;'
            f'letter-spacing:-0.045em;line-height:0.94;color:{INK};'
            f'white-space:nowrap">{number}{u}</div>')


def heading(text, size=34, width=980, top=26):
    return (f'<div class="d" style="font-size:{size}px;font-weight:500;'
            f'letter-spacing:-0.022em;line-height:1.18;color:{INK};'
            f'max-width:{width}px;margin-top:{top}px">{text}</div>')


def subhead(text, size=19, width=860, top=16):
    return (f'<div style="font-size:{size}px;font-weight:400;line-height:1.55;'
            f'color:{INK70};max-width:{width}px;margin-top:{top}px">{text}</div>')


def note(text, width=880, top=22):
    return (f'<div class="m" style="font-size:10.5px;line-height:1.6;'
            f'color:{INK45};max-width:{width}px;margin-top:{top}px">{text}</div>')


def statrow(items, top=44, width=1120):
    cells = []
    for value, label in items:
        cells.append(
            f'<div style="flex:1;border-top:1px solid {INK25};padding-top:14px">'
            f'<div class="d" style="font-size:25px;font-weight:600;'
            f'letter-spacing:-0.03em;color:{INK};line-height:1.1">{value}</div>'
            f'<div class="m" style="font-size:10.5px;letter-spacing:.14em;'
            f'text-transform:uppercase;color:{INK45};margin-top:8px;'
            f'line-height:1.5">{label}</div></div>')
    return (f'<div style="display:flex;gap:46px;margin-top:{top}px;'
            f'max-width:{width}px">{"".join(cells)}</div>')


def page(n, body, pad=PAD, show_footer=True, footer_push=True):
    return (f'<div class="page" style="padding:{pad};display:flex;'
            f'flex-direction:column">{body}'
            f'{footer(n, footer_push) if show_footer else ""}</div>')


def textpage(n, eb, hero_html, head_html, sub_html, extra="", mark=False):
    """The default page: eyebrow up top, the hero block vertically centred."""
    return page(n, (
        f'{eyebrow(eb, mark)}'
        f'<div style="flex:1 1 auto;min-height:0;display:flex;'
        f'flex-direction:column;justify-content:center">'
        f'{hero_html}{head_html}{sub_html}{extra}</div>'))


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def p01_cover():
    body = f"""
    {eyebrow("Confidential offering memorandum &middot; August 2026")}
    <div style="flex:1 1 auto;min-height:0;display:flex;flex-direction:column;
         justify-content:center">
      <div class="d" style="font-size:118px;font-weight:600;letter-spacing:-0.05em;
           line-height:0.92;color:{INK}">Caramba North</div>
      <div style="width:88px;height:4px;background:{RED};margin-top:38px"></div>
      <div class="d" style="font-size:27px;font-weight:400;line-height:1.42;
           color:{INK70};max-width:880px;margin-top:34px;letter-spacing:-0.012em">
        1,300 acres on I&#8209;10 in Pecos County, Texas &mdash; inside a power and
        data&#8209;center corridor where 79.3% of nearby announced capacity is
        already under construction.</div>
    </div>
    <div style="flex:0 0 auto;margin-top:auto;padding-top:16px;
         border-top:1px solid {RULE};display:flex;justify-content:space-between">
      <div class="m" style="font-size:11px;letter-spacing:.2em;color:{INK45}">
        1,300 ACRES &middot; NO ZONING ORDINANCE &middot; I-10 FRONTAGE</div>
      <div class="m" style="font-size:11px;letter-spacing:.2em;color:{INK45}">
        EXECUTIVE SUMMARY &middot; {TOTAL_PAGES} PAGES</div>
    </div>"""
    return page(1, body, pad="56px 80px 42px", show_footer=False)


def p02_property():
    return textpage(
        2, "01 &middot; The property",
        hero("1,300", "acres", 152),
        heading("Contiguous, on the north side of I&#8209;10, with no zoning "
                "ordinance in force.", 34, 940),
        subhead("Industrial and energy use is as&#8209;of&#8209;right. What "
                "governs the schedule here is construction, not entitlement."),
        statrow([("&asymp;5 mi", "Fort Stockton, services and airport"),
                 ("I-10", "Direct frontage, north side"),
                 ("Far West", "ERCOT's highest load-growth zone")],
                top=46),
        mark=True)


def p03_region():
    body = f"""
    {eyebrow("02 &middot; The region")}
    <div style="position:absolute;left:80px;top:176px;width:566px">
      {hero("32.7", "GW", 132)}
      {heading("of operating and ERCOT&#8209;queued capacity sits within "
               "60 miles.", 31, 540)}
      {subhead("Caramba North is inside that radius, not adjacent to it: "
               "0.5 GW within 15 miles, 8.9 GW within 30, 53.5 GW within 100.",
               18, 520)}
    </div>
    <div style="position:absolute;right:76px;top:92px;width:544px;height:544px">
      {vec("chart_rings_light")}
    </div>"""
    return page(3, body)


def p04_gwranch():
    return textpage(
        4, "03 &middot; GW Ranch",
        hero("15.5", "mi", 152),
        heading("to a 7.65&nbsp;GW generation site that is under construction, "
                "not announced.", 34, 980),
        subhead("GW Ranch: 8,000 acres, 35 gas turbines, 1.8&nbsp;GW of battery "
                "storage and up to 750&nbsp;MW of solar. Its TCEQ air permit is "
                "the largest issued in the US this year, and three "
                "189,000&nbsp;sq&nbsp;ft data&#8209;center buildings are targeted "
                "for December 2026.", 18, 920),
        statrow([("7.65 GW", "TCEQ air permit, issued Jan 2026"),
                 ("&asymp;$12B", "Estimated project investment"),
                 ("Dec 2026", "Targeted completion, first buildings")],
                top=38)
        + note("The 7.65&nbsp;GW figure is a TCEQ generation air permit, not an "
               "ERCOT interconnection queue position; the project is off&#8209;grid "
               "initially and no ERCOT filing has been disclosed. Distance is "
               "edge&#8209;to&#8209;edge from the tract boundary.", 940, 20),
        mark=True)


def p05_corridor():
    # The rail-less corridor variants carry exactly two numbered markers, both
    # plotted on the anchors' disclosed site points; only the subject tract is
    # drawn as a polygon. The key says nothing the map does not show.
    key_items = [
        (RED, "CARAMBA NORTH", "1,300 acres, I-10 frontage"),
        (GOLD, "1 &nbsp;GW RANCH", "15.5 mi north, under construction"),
        (GOLD, "2 &nbsp;LONGFELLOW", "19.3 mi south, phase-1 site work"),
    ]
    rows = "".join(
        f'<div style="display:flex;gap:9px;align-items:baseline;margin-top:7px">'
        f'<span style="flex:0 0 auto;width:8px;height:8px;background:{c};'
        f'border-radius:1px;position:relative;top:-1px"></span>'
        f'<span class="m" style="font-size:9.5px;letter-spacing:.13em;'
        f'color:{INK};font-weight:600">{name}</span>'
        f'<span class="m" style="font-size:9.5px;color:{INK45};'
        f'letter-spacing:.04em">{sub}</span></div>'
        for c, name, sub in key_items)

    body = f"""
    <div style="flex:0 0 auto;display:flex;gap:52px;align-items:flex-start">
      <div style="flex:1;min-width:0">
        {eyebrow("04 &middot; The corridor", True)}
        <div class="d" style="font-size:33px;font-weight:500;letter-spacing:-0.024em;
             line-height:1.16;color:{INK};margin-top:16px;max-width:790px">
          The corridor runs through the property, not past it.</div>
        <div style="font-size:16.5px;line-height:1.5;color:{INK70};margin-top:10px;
             max-width:790px">
          GW Ranch sits 15.5 miles north, Longfellow 19.3 miles south &mdash;
          Caramba North is on the line between them.</div>
      </div>
      <div style="flex:0 0 auto;width:326px;padding-top:2px">
        <div class="m" style="font-size:9.5px;letter-spacing:.22em;color:{INK45};
             font-weight:600">KEY &nbsp;&middot;&nbsp; 05 / {TOTAL_PAGES}</div>
        {rows}
        <div class="m" style="font-size:9px;line-height:1.55;color:{INK45};
             margin-top:11px;letter-spacing:.04em">
          Markers plot each anchor's disclosed site point; rings are 15 and 30
          miles from the tract.</div>
      </div>
    </div>
    {exhibit("corridor_wide_light", top=12)}"""
    return page(5, body, pad="40px 58px 18px", show_footer=False)


def p06_maturity():
    body = f"""
    {eyebrow("05 &middot; Build status", True)}
    <div style="flex:0 0 auto;margin-top:34px">
      {hero("79.3%", None, 118)}
      {heading("of nearby announced capacity is already under construction.",
               31, 880, 22)}
      {subhead("Of the 9,650&nbsp;MW announced at the two campuses within 20 "
               "miles, 7,650&nbsp;MW is being built now; the remaining 20.7% is "
               "in planned or phase&#8209;1 status.", 18, 840, 14)}
    </div>
    {exhibit("chart_maturity_light", max_w=660, top=18, justify="flex-start")}"""
    return page(6, body)


def p07_transmission():
    return textpage(
        7, "06 &middot; Transmission",
        hero("15", "mi", 152),
        heading("to the western terminus of all three approved 765&nbsp;kV "
                "Permian import paths.", 34, 940),
        subhead("The transmission decision was made upstream of this site: the "
                "PUCT approved the routes on April 24, 2025 (PBRP Docket "
                "No.&nbsp;55718), and they land at Solstice Substation.", 18, 880),
        statrow([("6", "Substations within 10 miles"),
                 ("2.0 mi", "Fort Stockton Plant, 138/69 kV"),
                 ("141 + 133", "Substation and line upgrades in TPIT")],
                top=40)
        + note("TPIT upgrades are the ERCOT&#8209;wide queue of planned grid work "
               "&mdash; pipeline context, not committed capacity.", 880, 20))


def p08_water():
    return textpage(
        8, "07 &middot; Water",
        hero("47,418", "AF/yr", 140),
        heading("already permitted on adjacent affiliated lands &mdash; "
                "42.3&nbsp;MGD.", 34, 900),
        subhead("That is roughly two&#8209;thirds of all Middle Pecos GCD "
                "industrial water rights. The water question here is closed, "
                "not open.", 19, 840),
        note("Source: Edwards&ndash;Trinity (Plateau) aquifer; recharge held "
             "through the 1950s drought of record.", 860, 30),
        mark=True)


def p09_gas():
    return textpage(
        9, "08 &middot; Natural gas",
        hero("200,000", "MMBtu/d", 132),
        heading("quoted for a 15&#8209;year term at Waha&#8209;index pricing.", 34, 900),
        subhead("The site is 20 miles from the Waha hub and an indicative supply "
                "quote is in hand: CIAC of $15&ndash;25M, 9&ndash;15 month lead "
                "time. Waha's structural discount to Henry Hub &mdash; negative "
                "prints through 2024&ndash;2025 as Matterhorn, Blackcomb, Hugh "
                "Brinson and GCX rebalance Permian egress &mdash; is the same "
                "economics drawing on&#8209;site generation into this corridor.",
                18, 900),
        note("Quote is counterparty&#8209;supplied and indicative, not a "
             "contract.", 880, 22),
        mark=True)


def p10_queue():
    return textpage(
        10, "09 &middot; State context",
        hero("474", "GW", 152),
        heading("of pending interconnection requests &mdash; enough to stop the "
                "queue.", 34, 900),
        subhead("ERCOT's large&#8209;load queue went from 63&nbsp;GW at the end "
                "of 2024 to 226&nbsp;GW in November 2025 to roughly "
                "474&nbsp;GW by August 2026, about 90% of it data&#8209;center "
                "driven. On August 3, 2026 the governor directed an audit of "
                "queued data centers and the Batch&nbsp;Zero large&#8209;load "
                "review was paused pending it.", 18, 900),
        note("Public reporting: Latitude Media, Dec 3 2025; Utility Dive, Aug 2026.",
             880, 24))


def p11_drilling():
    body = f"""
    {eyebrow("10 &middot; Subsurface")}
    <div style="flex:0 0 auto;display:flex;gap:52px;align-items:flex-start;
         margin-top:26px">
      <div style="flex:0 0 auto">{hero("115", None, 108)}</div>
      <div style="flex:1;min-width:0;padding-top:4px">
        <div class="d" style="font-size:26px;font-weight:500;letter-spacing:-0.022em;
             line-height:1.2;color:{INK}">
          new&#8209;drill wells in Pecos County since 2020, against a peer average
          of 1,181.</div>
        <div style="font-size:16.5px;line-height:1.5;color:{INK70};margin-top:11px">
          The lowest of seven comparable Permian counties, roughly 90% below the
          peer average &mdash; and zero new&#8209;drill wells within five miles of
          the tract.</div>
      </div>
    </div>
    {exhibit("chart_peer_drilling_light", max_w=1000, top=20)}"""
    return page(11, body)


def p12_colophon():
    body = f"""
    {eyebrow("11 &middot; Diligence")}
    <div style="flex:0 0 auto;margin-top:44px">
      <div class="d" style="font-size:52px;font-weight:500;letter-spacing:-0.032em;
           line-height:1.12;color:{INK};max-width:1000px">
        Every figure in this document is re&#8209;derivable from a cited public
        source.</div>
      {subhead("The underlying GIS platform traces each point, line and boundary "
               "to ERCOT, PUCT, EIA&#8209;860, TCEQ, RRC, FracFocus, Middle Pecos "
               "GCD, HIFLD, USGS, BTS and Census TIGER, with per&#8209;feature "
               "source popups. RRC refreshes weekly; the ERCOT queue and TPIT "
               "monthly. Access is credentialed and logged.", 19, 940, 22)}
    </div>
    <div style="flex:0 0 auto;margin-top:auto;display:flex;gap:64px">
      <div style="flex:1;border-top:1px solid {INK25};padding-top:12px">
        <div class="m" style="font-size:10px;letter-spacing:.2em;color:{INK45};
             font-weight:600">DISTANCE METHODOLOGY</div>
        <div style="font-size:11.5px;line-height:1.6;color:{INK70};margin-top:8px">
          Distances to GW Ranch and Longfellow are measured edge&#8209;to&#8209;edge:
          from the nearest point on the Caramba North tract boundary to each site's
          disclosed location, rather than centroid&#8209;to&#8209;centroid. This is
          consistently shorter than a straight centroid measurement because the
          tract has spatial extent. GW Ranch: 15.5 mi (vs. 17.3 mi centroid).
          Longfellow: 19.3 mi (vs. 19.7 mi centroid) &mdash; Longfellow's own public
          materials describe its location as more than 25 miles outside Fort
          Stockton, consistent with the longer figure; this distance should not be
          represented as shorter.</div>
      </div>
      <div style="flex:1;border-top:1px solid {INK25};padding-top:12px">
        <div class="m" style="font-size:10px;letter-spacing:.2em;color:{INK45};
             font-weight:600">NOTICES</div>
        <div style="font-size:11.5px;line-height:1.6;color:{INK70};margin-top:8px">
          Confidential offering memorandum prepared for a limited number of
          prospective counterparties under NDA. Not an offer to sell or a
          solicitation of an offer to buy securities. Information is preliminary
          and indicative, drawn from sources believed reliable; public data is
          drawn from the sources listed above and third&#8209;party transaction
          news is sourced to the public reporting cited in the companion source
          register.</div>
      </div>
    </div>"""
    return page(12, body, footer_push=False)


PAGES = [p01_cover, p02_property, p03_region, p04_gwranch, p05_corridor,
         p06_maturity, p07_transmission, p08_water, p09_gas, p10_queue,
         p11_drilling, p12_colophon]


def main():
    # The vector exhibits set type in IBM Plex Sans/Mono; this system embeds
    # Archivo + Plex Mono only, so the sans face is added for the exhibits.
    extra_fonts = f"<style>{T.font_css('plexsans')}</style>"
    pages_html = extra_fonts + "\n".join(fn() for fn in PAGES)
    html = T.document("minimal", pages_html, "landscape",
                      "Caramba North — Executive Summary")
    OUT.mkdir(parents=True, exist_ok=True)
    html_path = OUT / f"{STEM}.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"html -> {html_path.relative_to(REPO)} "
          f"({html_path.stat().st_size // 1024} KB, {len(PAGES)} pages)")
    T.render_pdf(str(html_path), str(OUT / f"{STEM}.pdf"))


if __name__ == "__main__":
    main()
