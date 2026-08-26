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
# Page 1 — the land itself. The property is the asset; the corridor around it
# is corroboration, and it comes second (page 2).
# ---------------------------------------------------------------------------
def attr(k, v):
    return (f'<div style="display:flex;justify-content:space-between;gap:14px;'
            f'padding:6.5px 0;border-bottom:1px solid {S["ink12"]}">'
            f'<span style="font-size:12.5px;color:{INK70};line-height:1.3">{k}</span>'
            f'<span class="m" style="font-size:12px;font-weight:500;color:{INK};'
            f'text-align:right;white-space:nowrap">{v}</span></div>')


def p1():
    body = f"""
<div style="display:flex;justify-content:space-between;align-items:baseline">
  <div style="display:flex;align-items:center;gap:11px">
    <div style="width:9px;height:9px;background:{RED}"></div>
    <div class="m" style="font-size:11.5px;letter-spacing:.19em;color:{BLUE};font-weight:600">
      CARAMBA NORTH &nbsp;·&nbsp; PECOS COUNTY, TEXAS</div>
  </div>
  <div class="m" style="font-size:10.5px;letter-spacing:.12em;color:{INK45}">
    PRE-NDA SUMMARY</div>
</div>
<div style="height:1px;background:{INK};margin:15px 0 26px"></div>

<div style="display:flex;gap:44px;flex:1;min-height:0">

  <div style="width:560px;flex:none;display:flex;flex-direction:column">
    {hero("1,300", "ACRES", 116)}
    <div class="d" style="font-size:26px;font-weight:500;line-height:1.26;
                          letter-spacing:-0.02em;margin-top:18px;max-width:548px">
      contiguous, on Interstate&nbsp;10, with
      <span style="color:{RED}">47,418 acre-feet a year</span> of permitted water,
      long-haul fiber at the boundary, and no zoning to clear.
    </div>
    <div style="font-size:13.5px;line-height:1.58;color:{INK70};margin-top:15px;max-width:548px">
      A single block of land with the things a large power or data-center project
      normally spends years assembling &mdash; already in place, and permitted rather
      than applied for.
    </div>

    <div style="margin-top:20px">
      {attr("Size and configuration", "Up to 1,300 contiguous acres")}
      {attr("Frontage", "Direct Interstate 10 frontage")}
      {attr("Long-haul fiber", "Along the I-10 corridor")}
      {attr("Rail", "Union Pacific Sunset Route")}
      {attr("Town, services, regional airport", "~5 miles")}
      {attr("Zoning", "None — industrial and energy as of right")}
    </div>
  </div>

  <div style="flex:1;min-width:0;display:flex;flex-direction:column">
    <div style="border:1px solid {RULE};background:#fff;overflow:hidden;
                aspect-ratio:1180/600">
      {T.svg("corridor_prenda_wide_light")}
    </div>

    <div class="m" style="font-size:9px;letter-spacing:.14em;color:{INK45};font-weight:600;
                          margin-top:16px;padding-bottom:7px;border-bottom:1px solid {INK}">
      WATER &mdash; THE PART THAT IS HARDEST TO REPLICATE</div>
    <div style="display:flex;align-items:baseline;gap:11px;margin-top:12px">
      <div class="d" style="font-size:34px;font-weight:600;letter-spacing:-0.03em;
                            line-height:1;color:{INK}">47,418</div>
      <div class="m" style="font-size:10.5px;letter-spacing:.1em;color:{INK45};line-height:1.5">
        ACRE-FEET PER YEAR<br>&asymp; 42 MILLION GALLONS A DAY</div>
    </div>
    <div style="font-size:12.5px;line-height:1.52;color:{INK70};margin-top:11px">
      Permitted on adjacent affiliated land &mdash; roughly
      <strong style="color:{INK};font-weight:600">two-thirds of every industrial water
      right</strong> the local groundwater district has issued, at a volume that supports
      large-scale cooling.
    </div>
    <div style="background:{PANEL};border-left:3px solid {BLUE};padding:11px 13px;margin-top:11px">
      <div style="font-size:11.8px;line-height:1.48;color:#2A323B">
        The Edwards&ndash;Trinity aquifer here is refilled each year by runoff from the
        mountains to the south, rather than drawn from a reservoir that only depletes.
        Its recharge record held through the 1950s drought of record.
      </div>
    </div>
  </div>
</div>
{footer(1)}"""
    return page(body)


# ---------------------------------------------------------------------------
# Page 2 — power: what the site can reach, and what is already being built
# around it. Corroboration for page 1, not the lead.
# ---------------------------------------------------------------------------
def p2():
    body = f"""
<div style="display:flex;justify-content:space-between;align-items:baseline">
  <div class="m" style="font-size:11.5px;letter-spacing:.19em;color:{BLUE};font-weight:600">
    POWER &mdash; ON THE SITE AND AROUND IT</div>
  <div class="m" style="font-size:10.5px;letter-spacing:.12em;color:{INK45}">
    CARAMBA NORTH &nbsp;·&nbsp; PRE-NDA SUMMARY</div>
</div>
<div style="height:1px;background:{INK};margin:15px 0 22px"></div>

<div class="d" style="font-size:26px;font-weight:500;letter-spacing:-0.02em;
                      line-height:1.22;max-width:1090px">
  Grid access, fuel for on-site generation, and
  <span style="color:{RED}">9.65 GW of hyperscale capacity</span> going in within
  19.3 miles.
</div>
<div class="d" style="font-size:15.5px;font-style:italic;color:{RED};margin-top:9px;
                      max-width:1020px;line-height:1.4">
  The developers already building here reached the same conclusion about this corridor,
  with their own capital.
</div>

<div style="display:flex;gap:38px;margin-top:22px;flex:1;min-height:0">

  <div style="flex:1;min-width:0;display:flex;flex-direction:column">
    <div class="m" style="font-size:9.5px;letter-spacing:.15em;color:{BLUE};font-weight:600;
                          padding-bottom:8px;border-bottom:1px solid {INK}">
      A PLACE ON THE GRID</div>
    <div style="display:flex;align-items:baseline;gap:11px;margin-top:13px">
      <div class="d" style="font-size:34px;font-weight:600;letter-spacing:-0.03em;
                            line-height:1;color:{INK}">15</div>
      <div class="m" style="font-size:10.5px;letter-spacing:.1em;color:{INK45};line-height:1.5">
        MILES TO THE 765 kV<br>IMPORT TERMINUS</div>
    </div>
    <div style="font-size:12.5px;line-height:1.5;color:{INK70};margin-top:12px">
      Fifteen miles from where all three approved 765&nbsp;kV import lines land &mdash;
      the largest transmission program in the grid operator&rsquo;s history, approved and
      being built. Three substations sit within seven miles.
    </div>
  </div>

  <div style="flex:1;min-width:0;display:flex;flex-direction:column">
    <div class="m" style="font-size:9.5px;letter-spacing:.15em;color:{BLUE};font-weight:600;
                          padding-bottom:8px;border-bottom:1px solid {INK}">
      FUEL FOR ON-SITE POWER</div>
    <div style="display:flex;align-items:baseline;gap:11px;margin-top:13px">
      <div class="d" style="font-size:34px;font-weight:600;letter-spacing:-0.03em;
                            line-height:1;color:{INK}">20</div>
      <div class="m" style="font-size:10.5px;letter-spacing:.1em;color:{INK45};line-height:1.5">
        MILES TO THE<br>WAHA GAS HUB</div>
    </div>
    <div style="font-size:12.5px;line-height:1.5;color:{INK70};margin-top:12px">
      West Texas gas trades below the national benchmark &mdash; at times below zero. That
      is why the campuses nearby are building their own generation rather than waiting for
      grid power.
    </div>
    <div style="margin-top:11px">
      {attr("Indicative supply quote", "200,000 MMBtu/day")}
      {attr("Term", "15 years, at the hub price")}
      {attr("Utility build contribution", "$15–25 million")}
    </div>
  </div>

  <div style="flex:1.05;min-width:0;display:flex;flex-direction:column">
    <div class="m" style="font-size:9.5px;letter-spacing:.15em;color:{BLUE};font-weight:600;
                          padding-bottom:8px;border-bottom:1px solid {INK}">
      WHAT IS ALREADY BEING BUILT</div>
    <div style="display:flex;align-items:baseline;gap:11px;margin-top:13px">
      <div class="d" style="font-size:34px;font-weight:600;letter-spacing:-0.03em;
                            line-height:1;color:{INK}">9.65</div>
      <div class="m" style="font-size:10.5px;letter-spacing:.1em;color:{INK45};line-height:1.5">
        GW ANNOUNCED WITHIN<br>19.3 MILES</div>
    </div>
    <div style="font-size:12.5px;line-height:1.5;color:{INK70};margin-top:12px">
      7.65&nbsp;GW of it already under construction. Both campuses sit on the same
      north&ndash;south line through the property.
    </div>
    <div style="display:flex;flex-direction:column;gap:9px;margin-top:12px">
      {keyrow("1", "Amazon — 7.65 GW", "15.5 mi · under construction · 35 gas turbines", RED, star=True)}
      {keyrow("2", "Second announced campus", "19.3 mi · site work underway · 2 GW planned gas", GOLD)}
    </div>
    <div class="m" style="font-size:9px;color:{INK45};margin-top:10px;line-height:1.5">
      Counterparty site names withheld pre-NDA.
    </div>
  </div>
</div>

<div style="display:flex;gap:38px;align-items:stretch;margin-top:22px">
  <div style="flex:1;background:{PANEL};border-left:3px solid {RED};padding:12px 15px">
    <div class="m" style="font-size:9px;letter-spacing:.14em;color:{RED};font-weight:600;
                          margin-bottom:6px">WHY IT IS HAPPENING HERE, NOW</div>
    <div style="font-size:11.8px;line-height:1.48;color:#2A323B">
      Requests to connect large new loads to the Texas grid grew from 63&nbsp;GW at the end
      of 2024 to roughly 474&nbsp;GW by August 2026, about 90% of it data centres &mdash;
      enough that the state paused new reviews pending an audit. The capacity already
      permitted and building around this property is outside that queue.
    </div>
  </div>
  <div style="width:326px;flex:none">
    <div class="m" style="font-size:9px;letter-spacing:.14em;color:{INK45};font-weight:600;
                          padding-bottom:7px;border-bottom:1px solid {INK}">AVAILABLE UNDER NDA</div>
    <div style="font-size:11.5px;line-height:1.52;color:{INK70};margin-top:9px">
      Counterparty names, water and transmission documentation, indicative gas terms, and
      logged access to the diligence platform behind this summary &mdash; where every figure
      here can be checked against its public source.
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
