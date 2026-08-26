#!/usr/bin/env python3
"""Pre-NDA two-page teaser for Caramba North.

This is the first thing an investor sees, and the only job of these two
pages is to make the site impossible to dismiss on a first read. It works
by stating what is already built and permitted around the property, in
figures, and getting out of the way. No promotional language: the facts
are the argument.

DISCLOSURE POSTURE (pre-NDA):
  - Caramba North is named. It is our own position.
  - Amazon is named, and its capacity figure used, because its ownership
    of the neighbouring site was disclosed in public reporting (Aug 2026).
    Its SITE is not named.
  - The second campus and the wind/solar/hydrogen position are described
    by what they are, never by their ranch or developer names.
  - Maps use the corridor_prenda_* variants, whose rails carry the same
    aliases. Do not substitute the post-NDA exhibits here.

    python3 scripts/om2/build_teaser_prenda.py
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import om_theme as T  # noqa: E402

S = T.SYSTEMS["institutional"]
W, H = T.SLIDE_W, T.SLIDE_H
PAPER, INK, INK70, INK45 = S["paper"], S["ink"], S["ink70"], S["ink45"]
INK25, RULE, PANEL = S["ink25"], S["rule"], S["panel"]
RED, GOLD, BLUE = S["accent"], S["second"], S["third"]

OUT = T.REPO / "outputs" / "reports"
STEM = "Caramba-North-Teaser-PreNDA"
PAD = 66


def hero(number, unit=None, size=132, color=None):
    u = ""
    if unit:
        u = (f'<span class="d" style="font-size:{size*0.27:.0f}px;font-weight:500;'
             f'letter-spacing:-0.01em;color:{INK45};margin-left:{size*0.09:.0f}px">{unit}</span>')
    return (f'<div class="d" style="font-size:{size}px;font-weight:600;'
            f'letter-spacing:-0.045em;line-height:0.92;color:{color or INK};'
            f'white-space:nowrap">{number}{u}</div>')


def keyrow(mark, title, sub, color, star=False):
    """One line of the map key. Drawn in HTML so the type is the page's own,
    not the exhibit's internal 10px labels."""
    if star:
        # the map draws a star ABOVE the numbered badge for this anchor, so the
        # key carries both marks in the same order the reader sees them
        dot = (f'<div style="width:15px;height:15px;border-radius:50%;background:{color};'
               f'flex:none;display:flex;align-items:center;justify-content:center">'
               f'<span class="m" style="font-size:9px;font-weight:600;color:{PAPER}">'
               f'{mark}</span></div>') if mark else ""
        badge = (f'<div style="display:flex;align-items:center;gap:5px;flex:none;'
                 f'margin-top:2px"><svg viewBox="0 0 20 20" style="width:14px;height:14px">'
                 f'<path d="M10 1.4 L12.4 7.2 L18.6 7.7 L13.9 11.8 '
                 f'L15.4 17.9 L10 14.6 L4.6 17.9 L6.1 11.8 L1.4 7.7 L7.6 7.2 Z" '
                 f'fill="{color}"/></svg>{dot}</div>')
    elif mark:
        badge = (f'<div style="width:15px;height:15px;border-radius:50%;background:{color};'
                 f'flex:none;margin-top:2px;display:flex;align-items:center;'
                 f'justify-content:center"><span class="m" style="font-size:9px;'
                 f'font-weight:600;color:{PAPER}">{mark}</span></div>')
    else:
        badge = (f'<div style="width:15px;height:15px;flex:none;margin-top:2px;'
                 f'background:{color}29;border:1.5px solid {color}"></div>')
    return (f'<div style="display:flex;gap:9px;align-items:flex-start">{badge}'
            f'<div style="min-width:0"><div style="font-size:12.5px;font-weight:600;'
            f'color:{INK};line-height:1.3">{title}</div>'
            f'<div class="m" style="font-size:10px;color:{INK45};line-height:1.5;'
            f'margin-top:2px">{sub}</div></div></div>')


def statrow(items, top=34, gap=40, border=True):
    cells = []
    for value, label in items:
        bt = f"border-top:1px solid {INK25};padding-top:13px;" if border else ""
        cells.append(
            f'<div style="flex:1;min-width:0;{bt}">'
            f'<div class="d" style="font-size:27px;font-weight:600;letter-spacing:-0.03em;'
            f'color:{INK};line-height:1.08">{value}</div>'
            f'<div class="m" style="font-size:9.5px;letter-spacing:.13em;'
            f'text-transform:uppercase;color:{INK45};margin-top:8px;line-height:1.55">{label}</div>'
            f'</div>')
    return f'<div style="display:flex;gap:{gap}px;margin-top:{top}px">{"".join(cells)}</div>'


def footer(n):
    return (f'<div style="position:absolute;left:{PAD}px;right:{PAD}px;bottom:32px">'
            f'<div style="height:1px;background:{RULE}"></div>'
            f'<div class="m" style="display:flex;justify-content:space-between;'
            f'font-size:9.5px;letter-spacing:.12em;color:{INK45};padding-top:10px">'
            f'<span>CARAMBA NORTH &nbsp;·&nbsp; PECOS COUNTY, TEXAS</span>'
            f'<span>PRE-NDA SUMMARY &nbsp;·&nbsp; AUGUST 2026</span>'
            f'<span>{n} / 2</span></div></div>')


def page(body):
    return (f'<div class="page" style="padding:{PAD}px {PAD}px 92px;position:relative;'
            f'display:flex;flex-direction:column">{body}</div>')


# ---------------------------------------------------------------------------
# Page 1 — the one fact that should stop the reader
# ---------------------------------------------------------------------------
def p1():
    body = f"""
<div style="display:flex;justify-content:space-between;align-items:baseline">
  <div style="display:flex;align-items:center;gap:11px">
    <div style="width:9px;height:9px;background:{RED}"></div>
    <div class="m" style="font-size:11.5px;letter-spacing:.19em;color:{BLUE};font-weight:600">
      CARAMBA NORTH &nbsp;·&nbsp; 1,300 ACRES &nbsp;·&nbsp; PECOS COUNTY, TEXAS</div>
  </div>
  <div class="m" style="font-size:10.5px;letter-spacing:.12em;color:{INK45}">
    PRE-NDA SUMMARY</div>
</div>
<div style="height:1px;background:{INK};margin:16px 0 34px"></div>

<div style="display:flex;gap:46px;flex:1;min-height:0">

  <div style="width:566px;flex:none;display:flex;flex-direction:column">
    {hero("9.65", "GW", 128)}
    <div class="d" style="font-size:29px;font-weight:500;line-height:1.24;
                          letter-spacing:-0.02em;margin-top:22px;max-width:580px">
      of announced hyperscale capacity sits within
      <span style="color:{RED}">19.3 miles</span> of the property &mdash;
      7.65&nbsp;GW of it already under construction.
    </div>
    <div style="font-size:15px;line-height:1.62;color:{INK70};margin-top:20px;max-width:566px">
      Two campuses sit on the same north&ndash;south line through the tract. The larger is
      Amazon-owned and building now under the largest generation air permit issued in
      the United States this year. The site is 1,300 contiguous acres on Interstate&nbsp;10
      with no zoning ordinance to clear.
    </div>

    {statrow([("15.5 mi", "to the Amazon site &mdash; under construction"),
              ("19.3 mi", "to a second announced campus"),
              ("32.7 GW", "operating + queued within 60 mi")])}
  </div>

  <div style="flex:1;min-width:0;display:flex;flex-direction:column">
    <div style="border:1px solid {RULE};background:#fff;overflow:hidden;
                aspect-ratio:1180/600">
      {T.svg("corridor_prenda_wide_light")}
    </div>
    <div style="display:flex;flex-direction:column;gap:11px;margin-top:16px">
      {keyrow(None, "Caramba North", "1,300 contiguous acres · I-10 frontage · no zoning", RED)}
      {keyrow("1", "Amazon — 7.65 GW", "15.5 mi · under construction · TCEQ air permit", RED, star=True)}
      {keyrow("2", "Second announced campus", "19.3 mi · phase-1 site work · 2 GW planned on-site gas", GOLD)}
    </div>
    <div class="m" style="font-size:9.5px;color:{INK45};margin-top:14px;line-height:1.55">
      Counterparty site names withheld pre-NDA. Distances measured edge-to-edge
      from the tract boundary to each site&rsquo;s disclosed location.
    </div>
  </div>
</div>
{footer(1)}"""
    return page(body)


# ---------------------------------------------------------------------------
# Page 2 — why this parcel and not the next one
# ---------------------------------------------------------------------------
def block(title, sub, rows):
    r = "".join(
        f'<div style="display:flex;justify-content:space-between;gap:16px;'
        f'padding:9px 0;border-bottom:1px solid {S["ink12"]}">'
        f'<span style="font-size:13px;color:{INK70};line-height:1.35">{k}</span>'
        f'<span class="m" style="font-size:12.5px;font-weight:500;color:{INK};'
        f'text-align:right;white-space:nowrap">{v}</span></div>'
        for k, v in rows)
    return f"""
<div style="flex:1;min-width:0;display:flex;flex-direction:column">
  <div class="m" style="font-size:9.5px;letter-spacing:.15em;color:{BLUE};
                        font-weight:600;padding-bottom:8px;border-bottom:1px solid {INK}">
    {title}</div>
  <div class="d" style="font-size:15px;font-style:italic;color:{RED};
                        margin:13px 0 8px;line-height:1.4">{sub}</div>
  <div>{r}</div>
</div>"""


def p2():
    body = f"""
<div style="display:flex;justify-content:space-between;align-items:baseline">
  <div class="m" style="font-size:11.5px;letter-spacing:.19em;color:{BLUE};font-weight:600">
    WHY THIS PARCEL</div>
  <div class="m" style="font-size:10.5px;letter-spacing:.12em;color:{INK45}">
    CARAMBA NORTH &nbsp;·&nbsp; PRE-NDA SUMMARY</div>
</div>
<div style="height:1px;background:{INK};margin:16px 0 26px"></div>

<div class="d" style="font-size:30px;font-weight:500;letter-spacing:-0.02em;
                      line-height:1.2;max-width:1090px">
  The power, water and gas positions are permitted, not proposed.
</div>
<div class="d" style="font-size:18px;font-style:italic;color:{RED};margin-top:11px;
                      max-width:1010px;line-height:1.45">
  The constraint that stops most large-load sites &mdash; interconnection, water, or
  fuel &mdash; is already resolved here, and the corridor around it is being built by
  someone else&rsquo;s capital.
</div>

<div style="display:flex;gap:44px;margin-top:30px;flex:1;min-height:0">
  {block("TRANSMISSION", "Fifteen miles from the delivery point of all three approved 765 kV Permian import lines.", [
      ("Distance to 765 kV import terminus", "15 mi"),
      ("PUCT approval", "Docket 55718"),
      ("Substations within 10 miles", "6"),
      ("ERCOT weather zone", "Far West"),
  ])}
  {block("WATER &amp; NATURAL GAS", "Two-thirds of the district&rsquo;s industrial water rights are already permitted to this position.", [
      ("Permitted water, adjacent lands", "47,418 AF/yr"),
      ("Equivalent", "42.3 MGD"),
      ("Distance to Waha gas hub", "20 mi"),
      ("Indicative supply quote in hand", "200,000 MMBtu/d"),
  ])}
  {block("SITE &amp; SUBSURFACE", "Pecos County has the lowest new-drilling count of seven comparable Permian counties since 2020.", [
      ("Max contiguous acreage", "1,300 ac"),
      ("Zoning", "None &mdash; as-of-right"),
      ("New-drill events since 2020", "115"),
      ("Peer-county average", "1,181"),
  ])}
</div>

<div style="display:flex;gap:44px;align-items:flex-end;margin-top:22px">
  <div style="flex:1;background:{PANEL};border-left:3px solid {RED};padding:15px 18px">
    <div class="m" style="font-size:9.5px;letter-spacing:.14em;color:{RED};
                          font-weight:600;margin-bottom:7px">STATE CONTEXT</div>
    <div style="font-size:13px;line-height:1.55;color:#2A323B">
      ERCOT&rsquo;s large-load queue grew from 63&nbsp;GW at the end of 2024 to roughly
      474&nbsp;GW of pending requests by August 2026, about 90% data-center-driven &mdash;
      enough to trigger a state audit and a pause on new large-load review. The capacity
      already permitted and under construction around this site sits outside that queue.
    </div>
  </div>
  <div style="width:352px;flex:none">
    <div class="m" style="font-size:9.5px;letter-spacing:.14em;color:{INK45};
                          font-weight:600;padding-bottom:8px;border-bottom:1px solid {INK}">
      AVAILABLE UNDER NDA</div>
    <div style="font-size:12.5px;line-height:1.62;color:{INK70};margin-top:11px">
      Counterparty names and site boundaries, the full transmission and water
      documentation, indicative gas terms, and the underlying GIS platform &mdash; every
      figure above is re-derivable from cited public data.
    </div>
  </div>
</div>
{footer(2)}"""
    return page(body)


def main():
    html = T.document("institutional", p1() + "\n" + p2(), "landscape",
                      "Caramba North — Pre-NDA Summary")
    OUT.mkdir(parents=True, exist_ok=True)
    hp = OUT / f"{STEM}.html"
    hp.write_text(html, encoding="utf-8")
    print(f"html -> {hp.relative_to(T.REPO)}  ({hp.stat().st_size // 1024} KB)")
    T.render_pdf(str(hp), str(OUT / f"{STEM}.pdf"))


if __name__ == "__main__":
    main()
