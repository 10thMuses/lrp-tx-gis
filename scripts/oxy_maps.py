# -*- coding: utf-8 -*-
"""Parameterized light-theme map renderer for the OXY infrastructure dossier.

Big, business-legible PNG maps on a WHITE background with dark geographic
context (county outlines + labels, Interstate/US highways, city labels), large
numbered OXY-asset markers, and a Caramba North reference marker on EVERY map so
each asset group is shown relative to the Williams tract.

Public API:
  ctx = load_context(root)
  render(assets, out_path, title, ctx, caramba=(lon,lat), **opts)

`assets` is a list of dicts: {name, label, type, lon?/lat? or county?}.
Returns the numbered key rows so the report can print a matching legend.
"""
import os, json, math, csv, collections
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Polygon as MplPoly, Circle
from matplotlib.lines import Line2D

MI_PER_DEG_LAT = 69.0

# Asset marker styling — large, high-contrast on white. (color, marker, size, legend label)
STYLE = {
    "gas":      ("#b45309", "^", 140, "Gas processing / CO₂"),
    "power":    ("#ca8a04", "o", 130, "Power / solar"),
    "netpower": ("#dc2626", "s", 150, "NET Power (planned)"),
    "dac":      ("#db2777", "D", 130, "DAC / CO₂ capture"),
    "water":    ("#0891b2", "P", 165, "Water / recycling"),
    "sub":      ("#2563eb", "o", 55, "OXY substations"),
}

def _rings(geom):
    t = geom["type"]; c = geom["coordinates"]
    if t == "Polygon": return [c[0]]
    if t == "MultiPolygon": return [p[0] for p in c]
    return []

def _lines(geom):
    t = geom["type"]; c = geom["coordinates"]
    if t == "LineString": return [c]
    if t == "MultiLineString": return list(c)
    return []

def load_context(root):
    gj = json.load(open(os.path.join(root, "combined_geoms.geojson"), encoding="utf-8"))
    counties = [f for f in gj["features"] if (f.get("properties") or {}).get("layer_id") == "counties"]
    cent = {}
    for f in counties:
        nm = (f["properties"].get("NAME") or "").replace(" County", "").strip().upper()
        xs, ys = [], []
        for r in _rings(f["geometry"]):
            for x, y in r:
                xs.append(x); ys.append(y)
        if xs:
            cent[nm] = (sum(xs) / len(xs), sum(ys) / len(ys))
    highways = []
    hw = os.path.join(root, "data/tiger/primary_roads_wtx.geojson")
    if os.path.exists(hw):
        d = json.load(open(hw, encoding="utf-8"))
        for ft in d.get("features", []):
            nm = (ft.get("properties") or {}).get("name") or ""
            for ln in _lines(ft.get("geometry") or {}):
                highways.append((nm, ln))
    pipelines = []
    for fn in ("data/hifld/hifld_ng_pipelines.geojson", "data/hifld/hifld_crude_pipelines.geojson",
               "data/hifld/hifld_hgl_pipelines.geojson"):
        p = os.path.join(root, fn)
        if not os.path.exists(p): continue
        d = json.load(open(p, encoding="utf-8"))
        for ft in d.get("features", []):
            for ln in _lines(ft.get("geometry") or {}):
                pipelines.append(ln)
    cities = []
    cp = os.path.join(root, "combined_points.csv")
    if os.path.exists(cp):
        with open(cp, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("layer_id") != "cities":
                    continue
                try:
                    cities.append((row.get("name") or "", float(row["lon"]), float(row["lat"])))
                except (KeyError, ValueError, TypeError):
                    pass
    return {"counties": counties, "cent": cent, "highways": highways,
            "pipelines": pipelines, "cities": cities}

def _norm_hwy(nm):
    return (nm or "").replace("I- ", "I-").strip()

def _resolve_xy(a, cent, used):
    lon, lat = a.get("lon"), a.get("lat")
    if lon is not None and lat is not None:
        return float(lon), float(lat)
    co = (a.get("county") or "").upper()
    c = cent.get(co)
    if not c:
        return None, None
    k = used[co]; used[co] += 1
    if k == 0:
        return c
    ang = k * 2.39996; r = 0.16
    return c[0] + r * math.cos(ang), c[1] + r * math.sin(ang)

def render(assets, out_path, title, ctx, extent=None, center=None,
           radius_mi=None, caramba=None, number=True, fig_w=11.0):
    cent = ctx["cent"]
    coords, used = [], collections.Counter()
    for a in assets:
        coords.append(_resolve_xy(a, cent, used))

    # ---- determine extent (always include Caramba North when given) ----
    if center and radius_mi:
        clon, clat = center
        dlat = radius_mi / MI_PER_DEG_LAT
        dlon = dlat / math.cos(math.radians(clat))
        pad = 1.16
        xmin, xmax = clon - dlon * pad, clon + dlon * pad
        ymin, ymax = clat - dlat * pad, clat + dlat * pad
    elif extent:
        xmin, xmax, ymin, ymax = extent
    else:
        pts = [c for c, a in zip(coords, assets)
               if c[0] is not None and a.get("type") != "sub"]
        if not pts:
            pts = [c for c in coords if c[0] is not None]
        if caramba:
            pts = pts + [caramba]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        spanx = (max(xs) - min(xs)) * 1.28 + 0.18
        spany = (max(ys) - min(ys)) * 1.28 + 0.18
        spanx = max(spanx, 1.5); spany = max(spany, 1.05)
        cl0 = math.cos(math.radians(cy))
        ageo = (spanx * cl0) / spany
        if ageo < 0.82:
            spanx = 0.82 * spany / cl0
        elif ageo > 1.7:
            spany = (spanx * cl0) / 1.7
        xmin, xmax = cx - spanx / 2, cx + spanx / 2
        ymin, ymax = cy - spany / 2, cy + spany / 2

    coslat = math.cos(math.radians((ymin + ymax) / 2))
    fig_h = fig_w * ((ymax - ymin) / ((xmax - xmin) * coslat))
    fig, ax = plt.subplots(figsize=(fig_w, max(fig_h, 4.0)), dpi=200)
    fig.patch.set_facecolor("#ffffff"); ax.set_facecolor("#ffffff")
    ax.set_aspect(1 / coslat)

    def invis(lon, lat):
        return not (xmin <= lon <= xmax and ymin <= lat <= ymax)

    # counties
    for f in ctx["counties"]:
        nm = (f["properties"].get("NAME") or "").replace(" County", "").strip().upper()
        c = cent.get(nm)
        for r in _rings(f["geometry"]):
            ax.add_patch(MplPoly(r, closed=True, fill=False, edgecolor="#9fb0c3", lw=1.0, zorder=2))
        if c is not None and not invis(*c):
            ax.text(c[0], c[1], nm.title(), color="#475569", fontsize=10.0,
                    ha="center", va="center", zorder=3, alpha=0.9)

    # pipelines (faint)
    for ln in ctx["pipelines"]:
        ax.plot([p[0] for p in ln], [p[1] for p in ln], color="#e3e8ef", lw=0.7, alpha=0.8, zorder=1)

    # highways (dark, labeled interstates)
    label_done = set()
    for nm, ln in ctx["highways"]:
        ax.plot([p[0] for p in ln], [p[1] for p in ln], color="#8a98ab", lw=1.7, alpha=0.95, zorder=2)
        n = _norm_hwy(nm)
        if n.startswith("I-") and n not in label_done:
            mids = [(x, y) for x, y in ln if xmin < x < xmax and ymin < y < ymax]
            if mids:
                mx, my = mids[len(mids) // 2]
                ax.text(mx, my, n, color="#334155", fontsize=9.0, fontweight="bold",
                        ha="center", va="center", zorder=4,
                        path_effects=[pe.withStroke(linewidth=3.0, foreground="#ffffff")],
                        bbox=dict(boxstyle="round,pad=0.15", fc="#ffffff", ec="#cbd5e1", lw=0.6, alpha=0.9))
                label_done.add(n)

    # cities
    for nm, lon, lat in ctx["cities"]:
        if invis(lon, lat): continue
        ax.scatter([lon], [lat], c="#334155", marker="o", s=16, zorder=4, edgecolors="none")
        ax.text(lon, lat + (ymax - ymin) * 0.012, nm, color="#334155", fontsize=8.5,
                ha="center", va="bottom", zorder=4,
                path_effects=[pe.withStroke(linewidth=2.4, foreground="#ffffff")])

    # proximity ring
    if center and radius_mi:
        clon, clat = center
        dlat = radius_mi / MI_PER_DEG_LAT
        th = [i * math.pi / 90 for i in range(181)]
        rx = dlat / math.cos(math.radians(clat))
        ax.add_patch(Circle((clon, clat), dlat, fill=True, facecolor="#22c55e", alpha=0.06, zorder=1))
        ax.plot([clon + rx * math.cos(t) for t in th], [clat + dlat * math.sin(t) for t in th],
                color="#16a34a", lw=1.8, ls="--", alpha=0.9, zorder=4)

    # Caramba North reference marker (on every map)
    if caramba and not invis(*caramba):
        ax.scatter([caramba[0]], [caramba[1]], marker="*", s=460, c="#16a34a",
                   edgecolors="#ffffff", linewidths=1.4, zorder=10)
        ax.annotate("Caramba North\n(Williams)", (caramba[0], caramba[1]),
                    xytext=(0, -18), textcoords="offset points", ha="center", va="top",
                    color="#15803d", fontsize=9.5, fontweight="bold", zorder=10,
                    path_effects=[pe.withStroke(linewidth=3.0, foreground="#ffffff")])

    # OXY assets
    keyrows = []; num = 0
    for a, (lon, lat) in zip(assets, coords):
        if lon is None or invis(lon, lat):
            continue
        col, mk, sz, _ = STYLE.get(a.get("type", "gas"), STYLE["gas"])
        within = None
        if center and radius_mi:
            clon, clat = center
            dmi = math.hypot((lon - clon) * math.cos(math.radians(clat)), lat - clat) * MI_PER_DEG_LAT
            within = dmi <= radius_mi
        ax.scatter([lon], [lat], c=col, marker=mk, s=sz, edgecolors="#ffffff", linewidths=1.3, zorder=6)
        if number and a.get("type") != "sub":
            num += 1
            ax.annotate(str(num), (lon, lat), xytext=(8, 6), textcoords="offset points",
                        color=col, fontsize=12.0, fontweight="bold", zorder=9,
                        path_effects=[pe.withStroke(linewidth=3.4, foreground="#ffffff")])
            keyrows.append({"n": num, "label": a.get("label") or a.get("name"),
                            "type": a.get("type"), "within": within})

    ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor("#cbd5e1")

    present, seen = [], set()
    for a in assets:
        t = a.get("type", "gas")
        if t in STYLE and t not in seen:
            seen.add(t); col, mk, sz, lab = STYLE[t]
            present.append(Line2D([0], [0], marker=mk, color="none", markerfacecolor=col,
                                  markeredgecolor="#475569", markersize=11, label=lab))
    if caramba:
        present.append(Line2D([0], [0], marker="*", color="none", markerfacecolor="#16a34a",
                              markeredgecolor="#ffffff", markersize=15, label="Caramba North (Williams)"))
    if present:
        ax.legend(handles=present, loc="lower left", frameon=True, framealpha=0.93,
                  edgecolor="#cbd5e1", facecolor="#ffffff", fontsize=9.5, labelcolor="#334155")

    ax.set_title(title, color="#0f172a", fontsize=15.5, fontweight="bold", loc="left", pad=7)
    fig.text(0.012, 0.010, "Counties & roads: Census TIGER · pipelines (context): HIFLD/EIA · OXY assets: OXY filings + public facility databases",
             color="#94a3b8", fontsize=6.5)
    plt.subplots_adjust(left=0.008, right=0.992, top=0.95, bottom=0.035)
    fig.savefig(out_path, facecolor="#ffffff", dpi=200)
    plt.close(fig)
    return keyrows
