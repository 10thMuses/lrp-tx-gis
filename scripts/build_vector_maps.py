#!/usr/bin/env python3
"""Render the OM map exhibits as clean vector SVG from real GIS geometry.

Replaces the previous approach (crops of a rendered MapLibre screenshot,
which carried the basemap's own type, its baked-in labels, and no control
over weight, color, or callout placement). Everything here is drawn from
outputs/reports/om_exhibits/map_geometry.json — the repo's canonical layer
geometry — so type, line weight, label placement and color are controlled,
and the output is resolution-independent.

Site positions (Caramba North, GW Ranch, Longfellow, La Escalera) are real
polygon boundaries from the layer data, not points and not hand-placed.

    python3 scripts/extract_map_geometry.py     # first — refresh geometry
    python3 scripts/build_vector_maps.py
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

REPO = Path(os.environ.get("LRP_PROJECT_DIR", Path(__file__).resolve().parent.parent))
GEOM = REPO / "outputs" / "reports" / "om_exhibits" / "map_geometry.json"
OUT_DIR = REPO / "outputs" / "reports" / "om_exhibits" / "vector"

FONT = "IBM Plex Sans, Helvetica Neue, Arial, sans-serif"
MONO = "IBM Plex Mono, SFMono-Regular, Consolas, monospace"

# --- palette: one ink family, one accent, one grid tone ---------------------
LIGHT = dict(
    paper="#FBFAF7", ink="#12181F", ink70="#4A545F", ink45="#8A939D",
    ink25="#C5CBD1", ink12="#E4E7EA", grid="#0E6E9C", accent="#B03A2E",
    gold="#C08A10", tractfill="#B03A2E",
)
DARK = dict(
    paper="#0E141A", ink="#E8EDF2", ink70="#9BA8B6", ink45="#6B7885",
    ink25="#333F4B", ink12="#1C252E", grid="#0E6E9C", accent="#B03A2E",
    gold="#C08A10", tractfill="#B03A2E",
)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


class Projection:
    """Equirectangular, aspect-corrected. Accurate at this extent (~100 mi)."""

    def __init__(self, center, span_mi, width, height, pad=0):
        cx, cy = center
        self.center, self.width, self.height = center, width, height
        self.kx = math.cos(math.radians(cy))
        iw, ih = width - 2 * pad, height - 2 * pad
        # scale so `span_mi` spans the SHORTER inner dimension
        self.scale = min(iw, ih) / (span_mi / 69.0)
        self.cxpx, self.cypx = width / 2, height / 2
        self.cx, self.cy = cx, cy

    def __call__(self, lon, lat):
        x = self.cxpx + (lon - self.cx) * self.kx * self.scale
        y = self.cypx - (lat - self.cy) * self.scale
        return x, y

    def mi(self, mi):
        return mi / 69.0 * self.scale


def star_path(cx, cy, r_out, points=5, ratio=0.4):
    """A five-point star as an SVG path.

    Used to mark the one anchor that carries the most weight in the story.
    Kept small and thin-stroked deliberately: it should read as a different
    KIND of marker at a glance, not as a louder one.
    """
    import math
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_out * ratio
        th = math.radians(-90 + i * 180.0 / points)
        pts.append(f"{cx + r * math.cos(th):.2f},{cy + r * math.sin(th):.2f}")
    return "M" + " L".join(pts) + " Z"


def path_d(proj, coords, close=False):
    if not coords:
        return ""
    pts = [proj(c[0], c[1]) for c in coords]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return d + " Z" if close else d


def load():
    with open(GEOM, encoding="utf-8") as f:
        data = json.load(f)
    # ring analysis rides along so the map can carry its own analytical payload
    try:
        import sys
        sys.path.insert(0, str(REPO / "scripts"))
        import build_insight_pack as IP
        data["rings"] = IP.build().get("ring_analysis", [])
    except Exception:
        data["rings"] = []
    return data


def poly_centroid(ring):
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def clip_visible(proj, coords, w, h, slack=200):
    """Cheap reject: keep a line only if any vertex lands near the canvas."""
    for c in coords:
        x, y = proj(c[0], c[1])
        if -slack <= x <= w + slack and -slack <= y <= h + slack:
            return True
    return False


# ---------------------------------------------------------------------------
# Callout labels — boxes in the gutters with elbow leaders
# ---------------------------------------------------------------------------
def layout_callouts(cands, width, height, box_h, top=24, gap=12):
    """cands: list of dicts with x, y, side. Assigns ly without overlap."""
    for side in ("l", "r"):
        col = sorted([c for c in cands if c["side"] == side], key=lambda c: c["y"])
        cursor = top
        for c in col:
            ly = max(c["y"] - box_h / 2, cursor)
            c["ly"] = ly
            cursor = ly + box_h + gap
        overflow = cursor - gap - (height - top)
        if overflow > 0 and col:
            for i, c in enumerate(col):
                c["ly"] -= overflow * (i + 1) / len(col)
    return cands


def callout(o, c, side, width, box_w, box_h, P, title, sub, color, num=None):
    """Draw one gutter callout box + elbow leader to its point."""
    bx = 18 if side == "l" else width - 18 - box_w
    by = c["ly"]
    mid_y = by + box_h / 2
    # elbow leader: box edge -> horizontal run -> diagonal to point
    ex = bx + box_w + 10 if side == "l" else bx - 10
    run = ex + 34 if side == "l" else ex - 34
    o.append(f'<path d="M{ex:.1f},{mid_y:.1f} L{run:.1f},{mid_y:.1f} L{c["x"]:.1f},{c["y"]:.1f}" '
             f'fill="none" stroke="{color}" stroke-width="1.2" opacity="0.75" '
             f'stroke-linejoin="round" stroke-linecap="round"/>')
    o.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{box_w}" height="{box_h}" rx="2" '
             f'fill="{P["paper"]}" stroke="{color}" stroke-width="1.4"/>')
    tx = bx + 12
    if num is not None:
        o.append(f'<circle cx="{bx+15:.1f}" cy="{by+16:.1f}" r="9" fill="{color}"/>')
        o.append(f'<text x="{bx+15:.1f}" y="{by+16:.1f}" font-family="{MONO}" font-size="11" '
                 f'font-weight="600" fill="{P["paper"]}" text-anchor="middle" '
                 f'dominant-baseline="central">{num}</text>')
        tx = bx + 30
    o.append(f'<text x="{tx:.1f}" y="{by+20:.1f}" font-family="{FONT}" font-size="14.5" '
             f'font-weight="600" fill="{P["ink"]}" letter-spacing="-0.1">{esc(title)}</text>')
    for i, line in enumerate(sub):
        o.append(f'<text x="{tx:.1f}" y="{by+38+i*15:.1f}" font-family="{MONO}" font-size="11.5" '
                 f'fill="{P["ink70"]}" letter-spacing="0.02">{esc(line)}</text>')


# ---------------------------------------------------------------------------
# Shared chrome: scale bar, north arrow, rings
# ---------------------------------------------------------------------------
def scale_bar(o, proj, P, x, y, miles=10):
    px = proj.mi(miles)
    o.append(f'<g>')
    o.append(f'<path d="M{x},{y} L{x},{y+7} M{x},{y+3.5} L{x+px:.1f},{y+3.5} '
             f'M{x+px:.1f},{y} L{x+px:.1f},{y+7}" stroke="{P["ink70"]}" stroke-width="1.3" fill="none"/>')
    o.append(f'<text x="{x+px/2:.1f}" y="{y-6:.1f}" font-family="{MONO}" font-size="10.5" '
             f'fill="{P["ink70"]}" text-anchor="middle" letter-spacing="0.08">{miles} MI</text>')
    o.append('</g>')


def north_arrow(o, P, x, y):
    o.append(f'<g><path d="M{x},{y+16} L{x},{y-6}" stroke="{P["ink45"]}" stroke-width="1.3"/>'
             f'<path d="M{x-4.5},{y+1} L{x},{y-8} L{x+4.5},{y+1} Z" fill="{P["ink45"]}"/>'
             f'<text x="{x}" y="{y+29}" font-family="{MONO}" font-size="10.5" fill="{P["ink45"]}" '
             f'text-anchor="middle" letter-spacing="0.08">N</text></g>')


def rings(o, proj, P, radii, center_px, label_angle_deg=48):
    cx, cy = center_px
    for r in radii:
        rp = proj.mi(r)
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rp:.1f}" fill="none" '
                 f'stroke="{P["ink25"]}" stroke-width="1" stroke-dasharray="3 4"/>')
        th = math.radians(label_angle_deg)
        lx, ly = cx + rp * math.sin(th), cy - rp * math.cos(th)
        o.append(f'<rect x="{lx-19:.1f}" y="{ly-9:.1f}" width="38" height="17" rx="2" '
                 f'fill="{P["paper"]}" opacity="0.92"/>')
        o.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-family="{MONO}" font-size="10.5" '
                 f'fill="{P["ink45"]}" text-anchor="middle" dominant-baseline="central" '
                 f'letter-spacing="0.05">{r} MI</text>')


# ---------------------------------------------------------------------------
# MAP 1 — Corridor: the tract, the two anchors, the grid, I-10
# ---------------------------------------------------------------------------
def map_corridor(data, width=1360, height=860, dark=False, span_mi=54, rail_w=330,
                 show_rail=True, show_rings=True, anchors=3, pre_nda=False):
    """Map on the left, a numbered callout RAIL on the right.

    The rail is what makes this readable: numbered markers sit on the map,
    their full text lives in a fixed column that can never collide with the
    geometry or with another label.
    """
    P = DARK if dark else LIGHT
    W, H = width, height
    if not show_rail:
        rail_w = 0
    MW = W - rail_w          # map width
    proj = Projection(data["center"], span_mi, MW, H)
    o = []
    a = o.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    a(f'<rect width="{W}" height="{H}" fill="{P["paper"]}"/>')
    # Unique per instance: two corridor SVGs inlined in one HTML document
    # both declaring id="mapclip" makes url(#mapclip) resolve to the first,
    # clipping the second map by the wrong rect and silently dropping
    # markers. Key the id to this variant's own geometry.
    clip_id = f"mapclip_{int(W)}x{int(H)}_{int(span_mi)}_{'d' if dark else 'l'}_{anchors}"
    a(f'<defs><clipPath id="{clip_id}"><rect x="0" y="0" width="{MW}" height="{H}"/></clipPath></defs>')
    a(f'<g clip-path="url(#{clip_id})">')

    # county boundaries
    a(f'<g stroke="{P["ink25"]}" stroke-width="1" fill="none">')
    for f in data["geoms"].get("counties", []):
        if "point" in f or not clip_visible(proj, f["coords"], MW, H):
            continue
        a(f'<path d="{path_d(proj, f["coords"], close=True)}"/>')
    a('</g>')

    # transmission — grid texture, deliberately quiet
    a(f'<g stroke="{P["grid"]}" stroke-width="1" fill="none" opacity="0.32">')
    for f in data["geoms"].get("transmission", []):
        if "point" in f or not clip_visible(proj, f["coords"], MW, H):
            continue
        a(f'<path d="{path_d(proj, f["coords"])}"/>')
    a('</g>')

    # substations — density ticks
    a(f'<g fill="{P["grid"]}" opacity="0.45">')
    for p in data["points"].get("substations", []):
        x, y = proj(p["lon"], p["lat"])
        if -20 <= x <= MW + 20 and -20 <= y <= H + 20:
            a(f'<rect x="{x-1.7:.1f}" y="{y-1.7:.1f}" width="3.4" height="3.4"/>')
    a('</g>')

    # ERCOT queue — the pipeline as a field of rings
    a(f'<g fill="none" stroke="{P["gold"]}" stroke-width="1.1" opacity="0.55">')
    for p in data["points"].get("ercot_queue", []):
        x, y = proj(p["lon"], p["lat"])
        if -20 <= x <= MW + 20 and -20 <= y <= H + 20:
            a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3"/>')
    a('</g>')

    # highways — I-10 carries real weight, it is the site's frontage
    i10_path = None
    for f in data["geoms"].get("highways", []):
        if "point" in f or not clip_visible(proj, f["coords"], MW, H):
            continue
        nm = (f.get("name") or "").replace(" ", "")
        i10 = "I-10" in nm
        d = path_d(proj, f["coords"])
        a(f'<path d="{d}" fill="none" '
          f'stroke="{P["ink70"] if i10 else P["ink45"]}" stroke-width="{4.5 if i10 else 1.4}" '
          f'opacity="{0.92 if i10 else 0.38}" stroke-linecap="round" stroke-linejoin="round"/>')
        if i10:
            a(f'<path d="{d}" fill="none" stroke="{P["paper"]}" '
              f'stroke-width="1.2" opacity="0.6" stroke-dasharray="11 11"/>')
            i10_path = f["coords"]

    # distance rings
    center_px = proj(*data["center"])
    rings(o, proj, P, [15, 30], center_px, label_angle_deg=214)

    # --- site polygons ------------------------------------------------------
    def site_poly(key, color, fill_op=0.16, sw=2.0, dash=None):
        for f in data["geoms"].get(key, []):
            if "point" in f:
                continue
            da = f' stroke-dasharray="{dash}"' if dash else ""
            a(f'<path d="{path_d(proj, f["coords"], close=True)}" fill="{color}" '
              f'fill-opacity="{fill_op}" stroke="{color}" stroke-width="{sw}" '
              f'stroke-linejoin="round"{da}/>')

    # Only the subject tract is drawn from survey geometry. The gw_ranch /
    # longfellow_ranch / la_escalera layers are APPROXIMATE whole-ranch
    # outlines, and neither anchor's disclosed site point falls inside its
    # own ranch polygon (both are flagged coord_accuracy=approximate in
    # dc_anchors.json). Drawing outline and marker together would assert a
    # spatial relationship the data does not support, so the anchors are
    # shown as located markers only — which is also what every distance
    # figure in the OM is actually measured to.
    site_poly("caramba_south", P["accent"], 0.09, 1.5, dash="5 4")

    # the subject tract, drawn last and loudest, with a halo so it reads small
    for ring in data["tract"]:
        d = path_d(proj, ring, close=True)
        a(f'<path d="{d}" fill="none" stroke="{P["accent"]}" stroke-width="11" '
          f'opacity="0.16" stroke-linejoin="round"/>')
        a(f'<path d="{d}" fill="{P["accent"]}" fill-opacity="0.34" '
          f'stroke="{P["accent"]}" stroke-width="2.6" stroke-linejoin="round"/>')

    # Fort Stockton
    for c in data["points"].get("cities", []):
        if c["name"] != "Fort Stockton":
            continue
        x, y = proj(c["lon"], c["lat"])
        a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6" fill="{P["ink70"]}"/>')
        a(f'<text x="{x:.1f}" y="{y+20:.1f}" font-family="{FONT}" font-size="13" '
          f'font-weight="500" fill="{P["ink70"]}" text-anchor="middle">Fort Stockton</text>')

    # Solstice substation
    for f in data["geoms"].get("solstice_substation", []):
        if "point" not in f:
            continue
        x, y = proj(*f["point"])
        a(f'<rect x="{x-5.5:.1f}" y="{y-5.5:.1f}" width="11" height="11" fill="{P["paper"]}" '
          f'stroke="{P["grid"]}" stroke-width="2.4"/>')
        a(f'<text x="{x:.1f}" y="{y-14:.1f}" font-family="{MONO}" font-size="11" '
          f'font-weight="500" fill="{P["grid"]}" text-anchor="middle" '
          f'letter-spacing="0.06">SOLSTICE 765 kV</text>')

    # I-10 inline label
    if i10_path:
        mid = i10_path[len(i10_path) // 2]
        x, y = proj(mid[0], mid[1])
        if 40 < x < MW - 60:
            a(f'<rect x="{x-30:.1f}" y="{y-30:.1f}" width="60" height="19" rx="2" '
              f'fill="{P["paper"]}" opacity="0.9"/>')
            a(f'<text x="{x:.1f}" y="{y-16:.1f}" font-family="{MONO}" font-size="11.5" '
              f'font-weight="600" fill="{P["ink70"]}" text-anchor="middle" '
              f'letter-spacing="0.08">I-10</text>')

    # --- numbered markers on the map ---------------------------------------
    dist = data.get("distances", {})
    if pre_nda:
        # Pre-NDA variant: counterparty site names are withheld. Amazon's
        # ownership is public reporting, so the operator is named while its
        # site is not; the other positions are described by what they are.
        entries = [
            ("tract", "CARAMBA NORTH", ["1,300 contiguous acres · as-of-right",
                                        "I-10 frontage · 5 mi to Fort Stockton"], P["accent"], None),
            ("gw_ranch", "Amazon — 7.65 GW", [
                f'{dist.get("gw_ranch_mi", 15.5)} mi · under construction',
                "TCEQ air permit · 35 gas turbines"], P["accent"], "1"),
            ("longfellow_ranch", "Second announced campus", [
                f'{dist.get("longfellow_mi", 19.3)} mi · phase-1 site work',
                "2 GW planned on-site gas generation"], P["gold"], "2"),
            ("la_escalera", "Wind + solar + hydrogen", [
                "3.3 GW announced position",
                "same catchment"], P["gold"], "3"),
        ][:anchors + 1]
    else:
        entries = [
            ("tract", "CARAMBA NORTH", ["1,300 contiguous acres · as-of-right",
                                        "I-10 frontage · 5 mi to Fort Stockton"], P["accent"], None),
            ("gw_ranch", "GW Ranch", [f'{dist.get("gw_ranch_mi", 15.5)} mi · under construction',
                                      "7.65 GW TCEQ air permit · Amazon"], P["accent"], "1"),
            ("longfellow_ranch", "Longfellow", [f'{dist.get("longfellow_mi", 19.3)} mi · phase-1 site work',
                                                "2 GW planned on-site gas generation"], P["gold"], "2"),
            ("la_escalera", "La Escalera Ranch", ["Apex Clean Energy — Pecos Flat",
                                                  "3.3 GW wind + solar + hydrogen"], P["gold"], "3"),
        ][:anchors + 1]

    # Disclosed site coordinates, keyed to the ranch-polygon layer they sit in.
    # These are the same points every distance figure in the OM is measured to.
    anchor_pt = {}
    for _an in data.get("dc_anchors", []):
        if _an.get("id") == "gw-ranch-pacifico-pecos":
            anchor_pt["gw_ranch"] = (_an["lon"], _an["lat"])
        elif _an.get("id") == "project-horizon-poolside-coreweave":
            anchor_pt["longfellow_ranch"] = (_an["lon"], _an["lat"])

    marks = []
    for key, title, sub, color, num in entries:
        if key == "tract":
            x, y = center_px
        elif key in anchor_pt:
            x, y = proj(*anchor_pt[key])
        else:
            polys = [f for f in data["geoms"].get(key, []) if "point" not in f]
            if not polys:
                continue
            lon, lat = poly_centroid(polys[0]["coords"])
            x, y = proj(lon, lat)
        marks.append(dict(x=x, y=y, title=title, sub=sub, color=color, num=num,
                          star=(key == "gw_ranch")))
        if num is not None:
            # The Amazon site is the single most consequential fact on this
            # map, so it gets a star as well as its number -- a different
            # mark, not a bigger one.
            if key == "gw_ranch":
                a(f'<path d="{star_path(x, y - 25, 9.5)}" fill="{color}" '
                  f'stroke="{P["paper"]}" stroke-width="1.6" stroke-linejoin="round"/>')
            a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="{color}" '
              f'stroke="{P["paper"]}" stroke-width="2.5"/>')
            a(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{MONO}" font-size="13" '
              f'font-weight="600" fill="{P["paper"]}" text-anchor="middle" '
              f'dominant-baseline="central">{num}</text>')

    # chrome
    scale_bar(o, proj, P, 30, H - 36, 10)
    north_arrow(o, P, MW - 40, 44)

    a('</g>')  # end map clip

    if not show_rail:
        a('</svg>')
        return "\n".join(o)

    # --- rail ---------------------------------------------------------------
    rx = MW
    a(f'<rect x="{rx}" y="0" width="{rail_w}" height="{H}" fill="{P["paper"]}"/>')
    a(f'<line x1="{rx}" y1="0" x2="{rx}" y2="{H}" stroke="{P["ink25"]}" stroke-width="1"/>')

    px = rx + 30
    y = 56
    a(f'<text x="{px}" y="{y}" font-family="{MONO}" font-size="11" font-weight="600" '
      f'fill="{P["ink45"]}" letter-spacing="0.14">REGIONAL POWER CORRIDOR</text>')
    y += 30
    a(f'<line x1="{px}" y1="{y-12}" x2="{W-30}" y2="{y-12}" stroke="{P["ink25"]}" stroke-width="1"/>')

    for m in marks:
        y += 16
        if m["num"] is not None:
            if m.get("star"):
                a(f'<path d="{star_path(px + 11, y - 26, 8)}" fill="{m["color"]}"/>')
            a(f'<circle cx="{px+11}" cy="{y-4}" r="11" fill="{m["color"]}"/>')
            a(f'<text x="{px+11}" y="{y-4}" font-family="{MONO}" font-size="12" font-weight="600" '
              f'fill="{P["paper"]}" text-anchor="middle" dominant-baseline="central">{m["num"]}</text>')
        else:
            a(f'<rect x="{px+3}" y="{y-12}" width="16" height="16" fill="{m["color"]}" '
              f'fill-opacity="0.34" stroke="{m["color"]}" stroke-width="2"/>')
        a(f'<text x="{px+32}" y="{y}" font-family="{FONT}" font-size="16" font-weight="600" '
          f'fill="{P["ink"]}" letter-spacing="-0.15">{esc(m["title"])}</text>')
        y += 21
        for line in m["sub"]:
            a(f'<text x="{px+32}" y="{y}" font-family="{MONO}" font-size="11.5" '
              f'fill="{P["ink70"]}" letter-spacing="0.01">{esc(line)}</text>')
            y += 16
        y += 12

    # ring-analysis stat block — the analytical payload of the map
    ring_rows = data.get("rings") or []
    if ring_rows:
        y = max(y + 10, H - 400)
        a(f'<line x1="{px}" y1="{y}" x2="{W-30}" y2="{y}" stroke="{P["ink25"]}" stroke-width="1"/>')
        y += 22
        a(f'<text x="{px}" y="{y}" font-family="{MONO}" font-size="10.5" font-weight="600" '
          f'fill="{P["ink45"]}" letter-spacing="0.14">OPERATING + ERCOT QUEUE</text>')
        y += 8
        for row in ring_rows:
            y += 26
            a(f'<text x="{px}" y="{y}" font-family="{MONO}" font-size="12" '
              f'fill="{P["ink45"]}">{row["radius_mi"]} mi</text>')
            a(f'<text x="{W-30}" y="{y}" font-family="{FONT}" font-size="18" font-weight="600" '
              f'fill="{P["ink"]}" text-anchor="end" letter-spacing="-0.3">'
              f'{row["total_gw"]:.1f} GW</text>')
            a(f'<line x1="{px+52}" y1="{y-4}" x2="{W-104}" y2="{y-4}" stroke="{P["ink25"]}" '
              f'stroke-width="1" stroke-dasharray="1 3"/>')

    # legend in the rail
    y = H - 168
    a(f'<line x1="{px}" y1="{y}" x2="{W-30}" y2="{y}" stroke="{P["ink25"]}" stroke-width="1"/>')
    y += 22
    a(f'<text x="{px}" y="{y}" font-family="{MONO}" font-size="10.5" font-weight="600" '
      f'fill="{P["ink45"]}" letter-spacing="0.14">LEGEND</text>')
    y += 20
    legend = [(P["grid"], "line", "Transmission line (HIFLD)"),
              (P["grid"], "sq", "Substation"),
              (P["gold"], "ring", "ERCOT interconnection queue"),
              (P["ink70"], "road", "Interstate 10"),
              (P["ink25"], "dash", "Distance ring from tract")]
    for col, kind, lab in legend:
        if kind == "line":
            a(f'<path d="M{px},{y-4} L{px+20},{y-4}" stroke="{col}" stroke-width="1.6" opacity="0.75"/>')
        elif kind == "sq":
            a(f'<rect x="{px+7}" y="{y-8}" width="7" height="7" fill="{col}" opacity="0.75"/>')
        elif kind == "ring":
            a(f'<circle cx="{px+10}" cy="{y-4}" r="3.6" fill="none" stroke="{col}" stroke-width="1.3"/>')
        elif kind == "road":
            a(f'<path d="M{px},{y-4} L{px+20},{y-4}" stroke="{col}" stroke-width="3.6" opacity="0.9"/>')
        else:
            a(f'<path d="M{px},{y-4} L{px+20},{y-4}" stroke="{col}" stroke-width="1.2" '
              f'stroke-dasharray="3 4"/>')
        a(f'<text x="{px+30}" y="{y}" font-family="{MONO}" font-size="10.5" '
          f'fill="{P["ink45"]}">{esc(lab)}</text>')
        y += 17

    a('</svg>')
    return "\n".join(o)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = load()
    for dark, name in ((False, "corridor_light"), (True, "corridor_dark")):
        svg = map_corridor(data, dark=dark)
        (OUT_DIR / f"{name}.svg").write_text(svg, encoding="utf-8")
        print(f"  {name}.svg  ({len(svg)//1024} KB)")
    # bare variants (no rail) for in-slide use, where the slide supplies the copy.
    # Two aspects so the map fills its container instead of letterboxing:
    # "bare" for tall/square slots, "wide" for full-width slots.
    for dark, name in ((False, "corridor_bare_light"), (True, "corridor_bare_dark")):
        svg = map_corridor(data, width=900, height=640, dark=dark,
                           span_mi=52, show_rail=False, anchors=2)
        (OUT_DIR / f"{name}.svg").write_text(svg, encoding="utf-8")
        print(f"  {name}.svg  ({len(svg)//1024} KB)")
    for dark, name in ((False, "corridor_prenda_light"),):
        svg = map_corridor(data, width=1360, height=860, dark=dark, span_mi=54,
                           anchors=3, pre_nda=True)
        (OUT_DIR / f"{name}.svg").write_text(svg, encoding="utf-8")
        print(f"  {name}.svg  ({len(svg)//1024} KB)")
    for dark, name in ((False, "corridor_prenda_wide_light"),):
        svg = map_corridor(data, width=1180, height=600, dark=dark, span_mi=46,
                           show_rail=False, anchors=2, pre_nda=True)
        (OUT_DIR / f"{name}.svg").write_text(svg, encoding="utf-8")
        print(f"  {name}.svg  ({len(svg)//1024} KB)")
    for dark, name in ((False, "corridor_wide_light"), (True, "corridor_wide_dark")):
        svg = map_corridor(data, width=1180, height=600, dark=dark,
                           span_mi=46, show_rail=False, anchors=2)
        (OUT_DIR / f"{name}.svg").write_text(svg, encoding="utf-8")
        print(f"  {name}.svg  ({len(svg)//1024} KB)")
    print(f"maps -> {OUT_DIR.relative_to(REPO)}")


if __name__ == "__main__":
    main()
