"""Render a REAL geographic map of OXY infrastructure across the Permian / West Texas.

County outlines come from the repo's combined_geoms (Census TIGER, layer_id=counties);
the Permian pipeline grid from data/hifld/* (HIFLD/EIA) as faint context; OXY assets
are plotted with precise coords where known (data/oxy/oxy_assets.geojson) or at the
county centroid (computed from the real county polygon) for county-attributed assets.
Geometry is streamed to a PNG, never printed. Dark theme to match the deck.

Usage: python3 scripts/build_oxy_map.py [assets.json]
"""
import json, os, sys, math, collections
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Polygon as MplPoly
from matplotlib.lines import Line2D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "reports", "oxy_permian_map.png")

def rings(geom):
    t = geom["type"]; c = geom["coordinates"]
    if t == "Polygon": return [c[0]]
    if t == "MultiPolygon": return [p[0] for p in c]
    return []

def lines(geom):
    t = geom["type"]; c = geom["coordinates"]
    if t == "LineString": return [c]
    if t == "MultiLineString": return list(c)
    return []

# ---- counties ----
gj = json.load(open(os.path.join(ROOT, "combined_geoms.geojson"), encoding="utf-8"))
counties = [f for f in gj["features"] if (f.get("properties") or {}).get("layer_id") == "counties"]
cent = {}  # county NAME (upper, no 'County') -> centroid
allx, ally = [], []
for f in counties:
    nm = (f["properties"].get("NAME") or "").replace(" County", "").strip().upper()
    xs, ys = [], []
    for r in rings(f["geometry"]):
        for x, y in r:
            xs.append(x); ys.append(y)
    if xs:
        cent[nm] = (sum(xs)/len(xs), sum(ys)/len(ys)); allx += xs; ally += ys

xmin, xmax = min(allx), max(allx); ymin, ymax = min(ally), max(ally)

# ---- figure ----
coslat = math.cos(math.radians((ymin+ymax)/2))
fig_w = 9.0
fig_h = fig_w * ((ymax-ymin) / ((xmax-xmin)*coslat))
fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=150)
fig.patch.set_facecolor("#0b1220"); ax.set_facecolor("#0b1220")
ax.set_aspect(1/coslat)

# pipelines (context)
for fn, col in [("data/hifld/hifld_ng_pipelines.geojson", "#3a4660"),
                ("data/hifld/hifld_crude_pipelines.geojson", "#4a3550"),
                ("data/hifld/hifld_hgl_pipelines.geojson", "#3a4660")]:
    p = os.path.join(ROOT, fn)
    if not os.path.exists(p): continue
    d = json.load(open(p, encoding="utf-8"))
    for ft in d.get("features", []):
        for ln in lines(ft.get("geometry") or {}):
            xs = [pt[0] for pt in ln]; ys = [pt[1] for pt in ln]
            ax.plot(xs, ys, color=col, lw=0.6, alpha=0.55, zorder=1)

# counties
for f in counties:
    for r in rings(f["geometry"]):
        ax.add_patch(MplPoly(r, closed=True, fill=False, edgecolor="#33405c", lw=0.7, zorder=2))
    cx, cy = cent[(f["properties"].get("NAME") or "").replace(" County","").strip().upper()]
    ax.text(cx, cy, (f["properties"].get("NAME") or "").replace(" County","").upper(),
            color="#54618099", fontsize=4.4, ha="center", va="center", zorder=2)

# ---- assets ----
STYLE = {  # type -> (color, marker, size, label)
    "gas":   ("#f59e0b", "^", 90, "Gas processing / CO₂"),
    "power": ("#fbbf24", "o", 80, "Power / solar"),
    "netpower": ("#ef4444", "s", 95, "NET Power (planned)"),
    "dac":   ("#fb7185", "D", 80, "DAC / CO₂ capture"),
    "water": ("#2dd4bf", "P", 100, "Water / recycling"),
    "sub":   ("#38bdf8", "o", 32, "OXY substations"),
}
def load_assets(path):
    if path and os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    # default: from oxy_assets.geojson, typed by name
    g = json.load(open(os.path.join(ROOT, "data/oxy/oxy_assets.geojson"), encoding="utf-8"))
    out = []
    for ft in g["features"]:
        lon, lat = ft["geometry"]["coordinates"][:2]; n = ft["properties"]["name"].lower()
        if "block 31" in n or "wasson" in n or "century" in n: t = "gas"
        elif "goldsmith" in n or "santa garcias" in n: t = "power"
        else: t = "sub"
        out.append({"name": ft["properties"]["name"], "lon": lon, "lat": lat, "type": t,
                    "label": ft["properties"]["name"].split(" - ")[0]})
    return out

assets = load_assets(sys.argv[1] if len(sys.argv) > 1 else None)
cc = collections.Counter(); skipped = []; keyrows = []; num = 0
for a in assets:
    lon, lat = a.get("lon"), a.get("lat")
    if lon is None and a.get("county"):
        co = a["county"].upper(); c = cent.get(co)
        if not c:
            skipped.append(f"{a.get('name')} [county {co} not in map]"); continue
        k = cc[co]; cc[co] += 1
        if k:  # spiral successive same-county assets off the centroid
            ang = k * 2.39996; r = 0.17
            lon = c[0] + r*math.cos(ang)/coslat; lat = c[1] + r*math.sin(ang)
        else:
            lon, lat = c
    if lon is None:
        skipped.append(f"{a.get('name')} [no location]"); continue
    if not (xmin-0.1 <= lon <= xmax+0.1 and ymin-0.1 <= lat <= ymax+0.1):
        skipped.append(f"{a.get('name')} [out of Permian-TX extent]"); continue
    col, mk, sz, _ = STYLE.get(a.get("type", "gas"), STYLE["gas"])
    ax.scatter([lon], [lat], c=col, marker=mk, s=sz, edgecolors="#0b1220", linewidths=0.9, zorder=5)
    if a.get("type") != "sub":
        num += 1
        ax.annotate(str(num), (lon, lat), xytext=(6, 5), textcoords="offset points",
                    color="#ffffff", fontsize=8, fontweight="bold", zorder=7,
                    path_effects=[pe.withStroke(linewidth=2.6, foreground=col)])
        keyrows.append({"n": num, "label": a.get("label") or a.get("name"), "type": a.get("type")})
if skipped:
    print("NOTE — not on Permian-TX map (shown in text / separate region):")
    for s in skipped: print("   -", s)
json.dump(keyrows, open(os.path.join(ROOT, "outputs", "reports", "oxy_map_key.json"), "w"), indent=1, ensure_ascii=False)
print("KEY:", " · ".join(f"{r['n']}={r['label']}" for r in keyrows))

ax.set_xlim(xmin-0.15, xmax+0.15); ax.set_ylim(ymin-0.15, ymax+0.15)
ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_visible(False)
# legend
present = []
seen=set()
for a in assets:
    t=a.get("type","gas")
    if t in STYLE and t not in seen:
        seen.add(t); col,mk,sz,lab=STYLE[t]
        present.append(Line2D([0],[0],marker=mk,color="none",markerfacecolor=col,
                              markeredgecolor="#0b1220",markersize=9,label=lab))
leg=ax.legend(handles=present, loc="lower left", frameon=False, fontsize=7.5, labelcolor="#cbd5e1")
ax.set_title("OXY infrastructure — Permian Basin / West Texas",
             color="#f8fafc", fontsize=12, fontweight="bold", loc="left", pad=8)
fig.text(0.012, 0.012, "Counties: Census TIGER · pipeline grid (context): HIFLD/EIA · OXY assets: LRP map + OXY filings",
         color="#56657d", fontsize=5.5)
plt.subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.03)
fig.savefig(OUT, facecolor=fig.get_facecolor(), dpi=150)
print("wrote", OUT, "·", len([a for a in assets]), "assets ·", os.path.getsize(OUT), "bytes")
