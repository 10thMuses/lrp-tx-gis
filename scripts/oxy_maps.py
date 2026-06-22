"""Parameterized light-theme map renderer for the OXY infrastructure dossier.

Produces clean, business-legible PNG maps on a WHITE background with dark
geographic context (county outlines + labels, Interstate/US highways, city
labels) and small, numbered OXY-asset markers. One renderer drives every map
in the report:

  * an overview map of all OXY assets across the Permian / West Texas,
  * a proximity map centred on the Williams family's Caramba North tract
    (Pecos County) with a 50-mile radius ring, and
  * one map per asset-type section (midstream, water, power, DAC).

Geographic sources (all public, all streamed — never printed):
  * counties .......... combined_geoms.geojson (Census TIGER)
  * highways .......... data/tiger/primary_roads_wtx.geojson (Census TIGER 2023 primary roads)
  * pipeline context .. data/hifld/*.geojson (HIFLD / EIA)
  * cities ............ combined_points.csv (layer_id=cities)

Public API:
  ctx = load_context(root)
  render(assets, out_path, title, ctx, **opts)

`assets` is a list of dicts: {name, label, type, n?, lon?/lat? or county?}.
Asset `type` keys map to STYLE below. Returns the list of numbered key rows
[{n,label,type,within?}] so the report can print a matching legend.
"""
import os, json, math, csv, collections
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Polygon as MplPoly, Circle
from matplotlib.lines import Line2D

MI_PER_DEG_LAT = 69.0

# Asset marker styling — small, high-contrast on white. (color, marker, size, legend label)
STYLE = {
    "gas":      ("#b45309", "^", 70, "Gas processing / CO₂"),
    "power":    ("#ca8a04", "o", 64, "Power / solar"),
    "netpower": ("#dc2626", "s", 74, "NET Power (planned)"),
    "dac":      ("#db2777", "D", 64, "DAC / CO₂ capture"),
    "water":    ("#0891b2", "P", 80, "Water / recycling"),
    "sub":      ("#2563eb", "o", 30, "OXY substations"),
}

# ---------- geometry helpers ----------
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

# ---------- context loader (read once, reuse for every map) ----------
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
    for fn in ("data/hifld/hifld_ng_pipelines.geojson",
               "data/hifld/hifld_crude_pipelines.geojson",
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
    nm = (nm or "").replace("I- ", "I-").strip()
    return nm

def _resolve_xy(a, cent, used):
    """Return (lon, lat) for an asset: explicit coords, else county centroid
    with a deterministic spiral offset when several assets share a county."""
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

# ---------- main renderer ----------
def render(assets, out_path, title, ctx, extent=None, center=None,
           radius_mi=None, subtitle=None, number=True, fig_w=9.0):
    cent = ctx["cent"]
    coords, used = [], collections.Counter()
    for a in assets:
        lon, lat = _resolve_xy(a, cent, used)
        coords.append((lon, lat))

    # ---- determine extent ----
    if center and radius_mi:
        clon, clat = center
        dlat = radius_mi / MI_PER_DEG_LAT
        dlon = dlat / math.cos(math.radians(clat))
        pad = 1.18
        xmin, xmax = clon - dlon * pad, clon + dlon * pad
        ymin, ymax = clat - dlat * pad, clat + dlat * pad
    elif extent:
        xmin, xmax, ymin, ymax = extent
    else:  # fit to the PRIMARY (non-substation) assets; subs decorate, don't drive extent
        pts = [c for c, a in zip(coords, assets)
               if c[0] is not None and a.get("type") != "sub"]
        if not pts:
            pts = [c for c in coords if c[0] is not None]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        spanx = (max(xs) - min(xs)) * 1.5 + 0.25
        spany = (max(ys) - min(ys)) * 1.5 + 0.25
        # minimum window so a tight cluster still gets county context
        spanx = max(spanx, 1.6); spany = max(spany, 1.15)
        # clamp geographic aspect so a few near-coincident points can't make a
        # grotesquely tall/narrow map
        cl0 = math.cos(math.radians(cy))
        ageo = (spanx * cl0) / spany
        if ageo < 0.85:
            spanx = 0.85 * spany / cl0
        elif ageo > 1.7:
            spany = (spanx * cl0) / 1.7
        xmin, xmax = cx - spanx / 2, cx + spanx / 2
        ymin, ymax = cy - spany / 2, cy + spany / 2

    coslat = math.cos(math.radians((ymin + ymax) / 2))
    fig_h = fig_w * ((ymax - ymin) / ((xmax - xmin) * coslat))
    fig, ax = plt.subplots(figsize=(fig_w, max(fig_h, 3.2)), dpi=170)
    fig.patch.set_facecolor("#ffffff"); ax.set_facecolor("#ffffff")
    ax.set_aspect(1 / coslat)

    def invis(lon, lat):
        return not (xmin <= lon <= xmax and ymin <= lat <= ymax)

    # ---- counties (outline + dark label) ----
    for f in ctx["counties"]:
        nm = (f["properties"].get("NAME") or "").replace(" County", "").strip().upper()
        c = cent.get(nm)
        if c is None or invis(*c):
            # still draw outline if it overlaps the window
            pass
        for r in _rings(f["geometry"]):
            ax.add_patch(MplPoly(r, closed=True, fill=False, edgecolor="#9fb0c3",
                                 lw=0.8, zorder=2))
        if c is not None and not invis(*c):
            ax.text(c[0], c[1], nm.title(), color="#475569", fontsize=6.4,
                    ha="center", va="center", zorder=3, alpha=0.9)

    # ---- pipeline context (very faint) ----
    for ln in ctx["pipelines"]:
        xs = [p[0] for p in ln]; ys = [p[1] for p in ln]
        ax.plot(xs, ys, color="#e3e8ef", lw=0.6, alpha=0.8, zorder=1)

    # ---- highways (dark, labeled interstates) ----
    label_done = set()
    for nm, ln in ctx["highways"]:
        xs = [p[0] for p in ln]; ys = [p[1] for p in ln]
        ax.plot(xs, ys, color="#94a3b8", lw=1.3, alpha=0.95, zorder=2)
        n = _norm_hwy(nm)
        if n.startswith("I-") and n not in label_done:
            mids = [(x, y) for x, y in ln if xmin < x < xmax and ymin < y < ymax]
            if mids:
                mx, my = mids[len(mids) // 2]
                ax.text(mx, my, n, color="#334155", fontsize=6.0, fontweight="bold",
                        ha="center", va="center", zorder=4,
                        path_effects=[pe.withStroke(linewidth=2.4, foreground="#ffffff")],
                        bbox=dict(boxstyle="round,pad=0.1", fc="#ffffff", ec="#cbd5e1", lw=0.5, alpha=0.85))
                label_done.add(n)

    # ---- cities (orientation) ----
    for nm, lon, lat in ctx["cities"]:
        if invis(lon, lat): continue
        ax.scatter([lon], [lat], c="#334155", marker="o", s=9, zorder=4, edgecolors="none")
        ax.text(lon, lat + (ymax - ymin) * 0.012, nm, color="#334155", fontsize=5.6,
                ha="center", va="bottom", zorder=4,
                path_effects=[pe.withStroke(linewidth=2.0, foreground="#ffffff")])

    # ---- proximity ring ----
    if center and radius_mi:
        clon, clat = center
        dlat = radius_mi / MI_PER_DEG_LAT
        ax.add_patch(Circle((clon, clat), dlat, transform=ax.transData, fill=True,
                            facecolor="#22c55e", alpha=0.06, zorder=1))
        # ring as ellipse via many points (aspect handles lon scaling)
        th = [i * math.pi / 90 for i in range(181)]
        rx = dlat / math.cos(math.radians(clat))
        ax.plot([clon + rx * math.cos(t) for t in th],
                [clat + dlat * math.sin(t) for t in th],
                color="#16a34a", lw=1.4, ls="--", alpha=0.9, zorder=4)
        ax.scatter([clon], [clat], marker="*", s=340, c="#16a34a",
                   edgecolors="#ffffff", linewidths=1.2, zorder=8)
        ax.annotate("Caramba North\n(Williams)", (clon, clat),
                    xytext=(0, -16), textcoords="offset points", ha="center", va="top",
                    color="#15803d", fontsize=7.0, fontweight="bold", zorder=8,
                    path_effects=[pe.withStroke(linewidth=2.6, foreground="#ffffff")])

    # ---- OXY assets ----
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
        ax.scatter([lon], [lat], c=col, marker=mk, s=sz, edgecolors="#ffffff",
                   linewidths=1.0, zorder=6)
        if number and a.get("type") != "sub":
            num += 1
            ax.annotate(str(num), (lon, lat), xytext=(6, 4), textcoords="offset points",
                        color=col, fontsize=8.0, fontweight="bold", zorder=9,
                        path_effects=[pe.withStroke(linewidth=2.6, foreground="#ffffff")])
            keyrows.append({"n": num, "label": a.get("label") or a.get("name"),
                            "type": a.get("type"), "within": within})

    ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor("#e2e8f0")

    # ---- legend (asset types present) ----
    present, seen = [], set()
    for a in assets:
        t = a.get("type", "gas")
        if t in STYLE and t not in seen:
            seen.add(t); col, mk, sz, lab = STYLE[t]
            present.append(Line2D([0], [0], marker=mk, color="none", markerfacecolor=col,
                                  markeredgecolor="#475569", markersize=8, label=lab))
    if present:
        ax.legend(handles=present, loc="lower left", frameon=True, framealpha=0.92,
                  edgecolor="#e2e8f0", facecolor="#ffffff", fontsize=7.0, labelcolor="#334155")

    ax.set_title(title, color="#0f172a", fontsize=12.5, fontweight="bold", loc="left", pad=6)
    fig.text(0.012, 0.012, "Counties & roads: Census TIGER · pipelines (context): HIFLD/EIA · OXY assets: OXY filings + public facility databases",
             color="#94a3b8", fontsize=5.0)
    plt.subplots_adjust(left=0.01, right=0.99, top=0.94, bottom=0.04)
    fig.savefig(out_path, facecolor="#ffffff", dpi=170)
    plt.close(fig)
    return keyrows
