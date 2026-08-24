#!/usr/bin/env python3
"""Vector chart exhibits for the Caramba North OM redesign.

All output is standalone SVG, drawn to one spec so the whole document set
reads as a single system. Palette is the validated categorical triple
(see docs/redesign_content_brief.md §5a) — it passes the dataviz six checks
against both the light (#FBFAF7) and dark (#0E141A) surfaces.

Chart rules applied throughout: one axis, thin marks with 4px rounded
data-ends anchored to the baseline, a 2px surface gap between adjacent
fills, recessive grid/axes, selective direct labels (never a number on
every point), and identity never carried by color alone.

    python3 scripts/om2/om_charts.py        # writes outputs/.../vector/
"""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(os.environ.get("LRP_PROJECT_DIR", Path(__file__).resolve().parent.parent.parent))
OUT_DIR = REPO / "outputs" / "reports" / "om_exhibits" / "vector"

SANS = "IBM Plex Sans, Helvetica Neue, Arial, sans-serif"
MONO = "IBM Plex Mono, SFMono-Regular, Consolas, monospace"

# Validated categorical palette — passes lightness, chroma, CVD separation,
# normal-vision floor and contrast on BOTH surfaces.
RED, GOLD, BLUE = "#B03A2E", "#C08A10", "#0E6E9C"

LIGHT = dict(paper="#FBFAF7", ink="#12181F", ink70="#4A545F",
             ink45="#8A939D", ink25="#C5CBD1", ink12="#E7E9EC")
DARK = dict(paper="#0E141A", ink="#E8EDF2", ink70="#9BA8B6",
            ink45="#6B7885", ink25="#333F4B", ink12="#1C252E")


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def head(w, h, P, transparent=False):
    bg = "none" if transparent else P["paper"]
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
            f'<rect width="{w}" height="{h}" fill="{bg}"/>']


def txt(o, x, y, s, size=12, fill="#12181F", font=SANS, weight="400",
        anchor="start", ls="0", baseline=None, style="", halo=None):
    b = f' dominant-baseline="{baseline}"' if baseline else ""
    st = f' font-style="{style}"' if style else ""
    # NOTE: no paint-order halo — support is uneven across SVG rasterizers
    # (it silently strokes OVER the glyphs in some), so collisions are solved
    # by placement and by drawing reference rules beneath the marks instead.
    h = ""
    o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" '
             f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
             f'letter-spacing="{ls}"{b}{st}{h}>{esc(s)}</text>')


def bar(o, x, y, w, h, fill, r=4, horizontal=True):
    """Bar with rounded data-end only; the baseline end stays square."""
    if w <= 0 or h <= 0:
        return
    if horizontal:
        r = min(r, w, h / 2)
        o.append(f'<path d="M{x:.1f},{y:.1f} H{x+w-r:.1f} Q{x+w:.1f},{y:.1f} {x+w:.1f},{y+r:.1f} '
                 f'V{y+h-r:.1f} Q{x+w:.1f},{y+h:.1f} {x+w-r:.1f},{y+h:.1f} H{x:.1f} Z" fill="{fill}"/>')
    else:
        r = min(r, h, w / 2)
        o.append(f'<path d="M{x:.1f},{y+h:.1f} V{y+r:.1f} Q{x:.1f},{y:.1f} {x+r:.1f},{y:.1f} '
                 f'H{x+w-r:.1f} Q{x+w:.1f},{y:.1f} {x+w:.1f},{y+r:.1f} V{y+h:.1f} Z" fill="{fill}"/>')


# ===========================================================================
# 1. Peer-county new-drill comparison — the flagship subsurface stat.
#    One hue + emphasis (not categorical): Pecos is the subject, peers recede.
# ===========================================================================
PEERS = [("Martin", 1685), ("Midland", 1569), ("Loving", 1121), ("Reeves", 1053),
         ("Howard", 990), ("Reagan", 668), ("Pecos", 115)]


def chart_peer_drilling(dark=False, w=880, h=420, transparent=False):
    P = DARK if dark else LIGHT
    o = head(w, h, P, transparent)
    L, R, T = 108, 76, 62
    plot_w = w - L - R
    vmax = max(v for _, v in PEERS)
    rows = len(PEERS)
    gap = 9
    bh = (h - T - 54 - gap * (rows - 1)) / rows

    txt(o, L, 26, "New-drill wellbore events since 2020", 15.5, P["ink"], SANS, "600", ls="-0.1")
    txt(o, L, 45, "Pecos County vs. six comparable Permian counties · RRC dbf900",
        11.5, P["ink45"], MONO)

    peer_avg = sum(v for n, v in PEERS if n != "Pecos") / (len(PEERS) - 1)
    ax = L + plot_w * peer_avg / vmax
    o.append(f'<path d="M{ax:.1f},{T-8:.1f} V{T + rows*(bh+gap) - gap + 6:.1f}" '
             f'stroke="{P["ink45"]}" stroke-width="1.2" stroke-dasharray="4 4"/>')
    txt(o, ax, T - 14, f"peer avg {peer_avg:,.0f}", 10.5, P["ink45"], MONO, anchor="middle")

    for i, (name, v) in enumerate(PEERS):
        y = T + i * (bh + gap)
        subject = name == "Pecos"
        fill = RED if subject else P["ink25"]
        bw = plot_w * v / vmax
        bar(o, L, y, bw, bh, fill)
        # if this bar ends within a label-width of the peer-average rule,
        # the rule would strike through the value; push the label past it
        label_x = L + bw + 10
        if abs(label_x - ax) < 46 or (label_x < ax < label_x + 46):
            label_x = ax + 12
        txt(o, L - 12, y + bh / 2, name, 12.5, P["ink"] if subject else P["ink70"],
            SANS, "600" if subject else "400", anchor="end", baseline="central")
        txt(o, label_x, y + bh / 2, f"{v:,}", 12.5,
            P["ink"] if subject else P["ink70"], MONO,
            "600" if subject else "400", baseline="central")

    txt(o, L, h - 22, "Pecos is the lowest of the seven — roughly 90% below the peer average.",
        12, P["ink70"], SANS, "500")
    o.append("</svg>")
    return "\n".join(o)


# ===========================================================================
# 2. ERCOT large-load queue growth. One series -> no legend, title names it.
# ===========================================================================
QUEUE = [("End 2024", 63), ("Nov 2025", 226), ("Aug 2026", 474)]


def chart_queue_growth(dark=False, w=560, h=400, transparent=False):
    P = DARK if dark else LIGHT
    o = head(w, h, P, transparent)
    L, R, T, B = 58, 34, 74, 74
    plot_w, plot_h = w - L - R, h - T - B
    vmax = 500
    n = len(QUEUE)
    slot = plot_w / n
    bw = min(74, slot * 0.5)

    txt(o, L - 20, 26, "ERCOT large-load interconnection queue", 15.5, P["ink"], SANS, "600", ls="-0.1")
    txt(o, L - 20, 45, "Gigawatts of pending requests · public reporting", 11.5, P["ink45"], MONO)

    for gv in (0, 125, 250, 375, 500):
        gy = T + plot_h - plot_h * gv / vmax
        o.append(f'<path d="M{L},{gy:.1f} H{w-R}" stroke="{P["ink12"]}" stroke-width="1"/>')
        txt(o, L - 10, gy, f"{gv}", 10.5, P["ink45"], MONO, anchor="end", baseline="central")

    for i, (label, v) in enumerate(QUEUE):
        cx = L + slot * (i + 0.5)
        bh = plot_h * v / vmax
        y = T + plot_h - bh
        bar(o, cx - bw / 2, y, bw, bh, RED if i == n - 1 else P["ink25"], horizontal=False)
        txt(o, cx, y - 11, f"{v}", 21, P["ink"] if i == n - 1 else P["ink70"], SANS,
            "600", anchor="middle", ls="-0.3")
        txt(o, cx, T + plot_h + 20, label, 11.5, P["ink70"], MONO, anchor="middle")

    o.append(f'<path d="M{L},{T+plot_h} H{w-R}" stroke="{P["ink45"]}" stroke-width="1.2"/>')
    txt(o, L - 20, h - 26, "~90% of the Aug 2026 backlog is data-center-driven —", 11.5, P["ink70"], SANS)
    txt(o, L - 20, h - 11, "large enough to trigger a state audit and a queue pause.", 11.5, P["ink70"], SANS)
    o.append("</svg>")
    return "\n".join(o)


# ===========================================================================
# 3. Ring / power-gravity diagram — cumulative capacity by radius.
#    Radial, because the data IS radial (distance bands from one point).
# ===========================================================================
RINGS = [(15, 0.48), (30, 8.9), (60, 32.72), (100, 53.5)]
# true bearings from the tract centroid (deg) — the north/south symmetry
SITES = [("GW RANCH", 19, 17.3, "15.5 mi"), ("LONGFELLOW", 188, 19.7, "19.3 mi")]


def chart_rings(dark=False, size=620, transparent=False):
    """Radial, because the data is radial: distance bands from one point.

    Radius uses a SQRT scale, not linear. On a linear scale the 15- and
    30-mile rings collapse against the centre and their labels collide with
    the site markers; sqrt spaces the bands evenly and keeps the inner rings
    legible without misstating any distance (the ring labels carry the
    numbers).
    """
    import math
    P = DARK if dark else LIGHT
    o = head(size, size, P, transparent)
    cx, cy = size / 2 + 26, size / 2 + 14
    rmax = size / 2 - 84
    vmax = 100.0

    def rad(mi):
        return rmax * math.sqrt(mi / vmax)

    # rings, outermost first so inner strokes stay crisp
    for r, gw in RINGS:
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rad(r):.1f}" fill="none" '
                 f'stroke="{P["ink25"]}" stroke-width="1" stroke-dasharray="3 5"/>')

    # radial axis due WEST — clear of both site markers, which sit N and S.
    # Only the SHORT radius ticks live on the axis; the capacity values go in
    # a corner table, because four value labels crowd together near the
    # centre no matter how the rings are scaled.
    for r, gw in RINGS:
        lx, ly = cx - rad(r), cy
        o.append(f'<path d="M{lx:.1f},{ly-6:.1f} V{ly+6:.1f}" stroke="{P["ink45"]}" '
                 f'stroke-width="1.2"/>')
        lab = f"{r} mi" if r == RINGS[0][0] else f"{r}"
        txt(o, lx, ly + 20, lab, 10.5, P["ink45"], MONO, anchor="middle")

    # capacity table, upper right
    tx0, ty0 = size - 172, 96
    txt(o, tx0, ty0 - 14, "CUMULATIVE", 9.5, P["ink45"], MONO, "600", ls="0.14")
    o.append(f'<path d="M{tx0},{ty0-6} H{size-24}" stroke="{P["ink25"]}" stroke-width="1"/>')
    for i, (r, gw) in enumerate(RINGS):
        yy = ty0 + 20 + i * 25
        txt(o, tx0, yy, f"{r} mi", 11, P["ink45"], MONO, baseline="central")
        txt(o, size - 24, yy, f"{gw:.1f} GW", 15, P["ink"], SANS, "600",
            anchor="end", baseline="central", ls="-0.2")

    o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7.5" fill="{RED}"/>')
    txt(o, cx + 14, cy + 4, "CARAMBA NORTH", 11.5, P["ink"], SANS, "600",
        ls="0.06")

    for name, bearing, dist, label in SITES:
        th = math.radians(bearing)
        rr = rad(dist)
        x, y = cx + rr * math.sin(th), cy - rr * math.cos(th)
        o.append(f'<path d="M{cx:.1f},{cy:.1f} L{x:.1f},{y:.1f}" stroke="{GOLD}" '
                 f'stroke-width="1.2" stroke-dasharray="3 3" opacity="0.75"/>')
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="{P["paper"]}" '
                 f'stroke="{GOLD}" stroke-width="2.6"/>')
        up = math.cos(th) >= 0
        ly = y - 16 if up else y + 26
        txt(o, x, ly, name, 11.5, P["ink"], SANS, "600", anchor="middle",
            ls="0.05")
        txt(o, x, ly + (-15 if up else 15), label, 11, P["ink70"], MONO,
            anchor="middle")

    txt(o, 22, 28, "Operating + ERCOT-queued capacity by radius", 14.5, P["ink"],
        SANS, "600", ls="-0.1")
    txt(o, 22, 46, "Cumulative, region-wide · EIA-860 + ERCOT queue", 11, P["ink45"], MONO)
    txt(o, 22, size - 16,
        "GW Ranch sits due north, Longfellow due south — the site is on the line between them.",
        11, P["ink70"], SANS)
    o.append("</svg>")
    return "\n".join(o)


# ===========================================================================
# 4. Project maturity — one stacked bar, 2 segments, 2px surface gap.
# ===========================================================================
def chart_maturity(dark=False, w=560, h=190, transparent=False):
    P = DARK if dark else LIGHT
    o = head(w, h, P, transparent)
    L, R, T, bh = 30, 30, 74, 46
    plot_w = w - L - R
    segs = [("Under construction", 79.3, RED, "GW Ranch · 7,650 MW"),
            ("Planned / phase 1", 20.7, GOLD, "Longfellow · 2,000 MW")]

    txt(o, L, 26, "Announced capacity within 20 miles, by build status", 15, P["ink"], SANS, "600", ls="-0.1")
    txt(o, L, 45, "Share of 9,650 MW combined announced", 11.5, P["ink45"], MONO)

    x = L
    for i, (name, pct, col, _) in enumerate(segs):
        sw = plot_w * pct / 100
        if i:
            x += 2  # 2px surface gap between adjacent fills
            sw -= 2
        r = 4 if i == len(segs) - 1 else 0
        if r:
            bar(o, x, T, sw, bh, col, r=4)
        else:
            o.append(f'<rect x="{x:.1f}" y="{T}" width="{sw:.1f}" height="{bh}" fill="{col}"/>')
        txt(o, x + 12, T + bh / 2, f"{pct}%", 18, "#FFFFFF", SANS, "600", baseline="central", ls="-0.2")
        x += sw

    ly = T + bh + 30
    lx = L
    for name, pct, col, sub in segs:
        o.append(f'<rect x="{lx}" y="{ly-9}" width="10" height="10" rx="2" fill="{col}"/>')
        txt(o, lx + 17, ly, name, 12, P["ink"], SANS, "500", baseline="central")
        txt(o, lx + 17, ly + 16, sub, 10.5, P["ink45"], MONO, baseline="central")
        lx += 250
    o.append("</svg>")
    return "\n".join(o)


# ===========================================================================
# 5. Pecos County operating capacity by technology.
# ===========================================================================
MIX = [("Solar", 2178, 13), ("Wind", 542, 5), ("Storage", 505, 6), ("Gas", 1, 1)]


def chart_power_mix(dark=False, w=620, h=310, transparent=False):
    """Operating capacity by technology.

    The project-count column sits in its own reserved gutter, and the bar
    track stops short of it — otherwise the value label on the longest bar
    (Solar, the max) runs straight into the count.
    """
    P = DARK if dark else LIGHT
    o = head(w, h, P, transparent)
    L, R, T = 92, 132, 74
    VALUE_W = 78          # reserved for the "N,NNN MW" label after the bar
    plot_w = w - L - R - VALUE_W
    vmax = max(v for _, v, _ in MIX)
    gap, rows = 11, len(MIX)
    bh = (h - T - 46 - gap * (rows - 1)) / rows

    txt(o, L - 62, 26, "Pecos County operating capacity", 15.5, P["ink"], SANS, "600", ls="-0.1")
    txt(o, L - 62, 45, "Megawatts in service · EIA-860", 11.5, P["ink45"], MONO)

    for i, (name, v, n) in enumerate(MIX):
        y = T + i * (bh + gap)
        bw = max(plot_w * v / vmax, 2)
        bar(o, L, y, bw, bh, BLUE)
        txt(o, L - 12, y + bh / 2, name, 12.5, P["ink70"], SANS, anchor="end", baseline="central")
        txt(o, L + bw + 10, y + bh / 2, f"{v:,} MW", 12, P["ink"], MONO, "500", baseline="central")
        txt(o, w - 24, y + bh / 2, f"{n} proj.", 11, P["ink45"], MONO, anchor="end", baseline="central")

    txt(o, L - 62, h - 16, "3,226 MW operating today; 12,039 MW queued in this county alone.",
        11.5, P["ink70"], SANS, "500")
    o.append("</svg>")
    return "\n".join(o)


CHARTS = {
    "chart_peer_drilling": chart_peer_drilling,
    "chart_queue_growth": chart_queue_growth,
    "chart_rings": chart_rings,
    "chart_maturity": chart_maturity,
    "chart_power_mix": chart_power_mix,
}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, fn in CHARTS.items():
        for dark, suffix in ((False, "light"), (True, "dark")):
            svg = fn(dark=dark)
            path = OUT_DIR / f"{name}_{suffix}.svg"
            path.write_text(svg, encoding="utf-8")
        print(f"  {name}_{{light,dark}}.svg")
    print(f"charts -> {OUT_DIR.relative_to(REPO)}")


if __name__ == "__main__":
    main()
