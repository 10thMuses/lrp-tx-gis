#!/usr/bin/env python3
"""Extract a compact vector-geometry bundle for the OM map exhibits.

The previous OM exhibits were crops of a rendered MapLibre screenshot — a
raster, with the basemap's own baked-in labels and no control over type,
weight, or callout placement. This script instead pulls the REAL geometry
out of the repo's canonical layers and emits a small JSON bundle that the
exhibit builders draw as clean vector SVG: full control of typography,
label placement, line weight, and color, at any output resolution.

Streams the combined layer files (never materializes them in full) and
clips everything to a bounding box around Caramba North.

    python3 scripts/extract_map_geometry.py --out outputs/reports/om_exhibits/map_geometry.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

REPO = Path(os.environ.get("LRP_PROJECT_DIR", Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(REPO / "scripts"))

import caramba_om_data as D  # noqa: E402

# Bounding box around the site, wide enough to hold every anchor plus context.
# ~1.9 deg lon x ~1.35 deg lat -> roughly 105 x 93 miles at this latitude.
BBOX = (-103.75, 30.35, -101.85, 31.70)  # (west, south, east, north)


def in_bbox(lon, lat, bbox=BBOX):
    w, s, e, n = bbox
    return w <= lon <= e and s <= lat <= n


def seg_in_bbox(coords, bbox=BBOX):
    """Keep a line if any vertex falls inside the box."""
    return any(in_bbox(c[0], c[1], bbox) for c in coords)


def rdp(points, epsilon):
    """Ramer-Douglas-Peucker simplify, so line work stays light in the SVG."""
    if len(points) < 3:
        return points
    dmax, index = 0.0, 0
    x1, y1 = points[0]
    x2, y2 = points[-1]
    for i in range(1, len(points) - 1):
        x0, y0 = points[i]
        den = math.hypot(x2 - x1, y2 - y1)
        d = abs((x2 - x1) * (y1 - y0) - (x1 - x0) * (y2 - y1)) / den if den else 0.0
        if d > dmax:
            dmax, index = d, i
    if dmax > epsilon:
        return rdp(points[:index + 1], epsilon)[:-1] + rdp(points[index:], epsilon)
    return [points[0], points[-1]]


def r6(coords):
    return [[round(c[0], 5), round(c[1], 5)] for c in coords]


def stream_geoms(layer_ids, simplify=0.004):
    """Stream combined_geoms.geojson, keeping only in-box features."""
    want = set(layer_ids)
    out = {k: [] for k in want}
    with open(REPO / "combined_geoms.geojson", encoding="utf-8") as f:
        gj = json.load(f)
    for feat in gj.get("features", gj):
        props = feat.get("properties") or {}
        lid = props.get("layer_id")
        if lid not in want:
            continue
        g = feat.get("geometry") or {}
        gtype, coords = g.get("type"), g.get("coordinates")
        if not coords:
            continue
        parts = []
        if gtype == "Point":
            if in_bbox(coords[0], coords[1]):
                out[lid].append({"point": [round(coords[0], 5), round(coords[1], 5)],
                                 "name": props.get("name") or ""})
            continue
        if gtype == "LineString":
            parts = [coords]
        elif gtype == "MultiLineString":
            parts = coords
        elif gtype == "Polygon":
            parts = coords
        elif gtype == "MultiPolygon":
            parts = [ring for poly in coords for ring in poly]
        for part in parts:
            part = [c for c in part if len(c) >= 2]
            if len(part) < 2 or not seg_in_bbox(part):
                continue
            simp = rdp([[c[0], c[1]] for c in part], simplify) if simplify else part
            if len(simp) >= 2:
                out[lid].append({"coords": r6(simp), "name": props.get("name") or ""})
    return out


def stream_points(layer_ids):
    """Stream combined_points.csv, keeping only in-box points of these layers."""
    import csv
    csv.field_size_limit(min(sys.maxsize, 2 ** 31 - 1))
    want = set(layer_ids)
    out = {k: [] for k in want}
    with open(REPO / "combined_points.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["layer_id"] not in want:
                continue
            try:
                lon, lat = float(r["lon"]), float(r["lat"])
            except (TypeError, ValueError):
                continue
            if not in_bbox(lon, lat):
                continue
            out[r["layer_id"]].append({
                "name": (r.get("name") or "").strip(),
                "lon": round(lon, 5), "lat": round(lat, 5),
                "mi": round(D.miles(lon, lat), 1),
                "operator": (r.get("operator") or "").strip(),
                "technology": (r.get("technology") or "").strip(),
                "capacity": (r.get("capacity_mw") or r.get("capacity") or "").strip(),
            })
    return out


def highways():
    """Primary roads (Interstate / US / State) from the standalone TIGER cut.

    tiger_highways is a prebuilt PMTiles layer with no vector source in the
    combined files, so read the TIGER extract it was built from instead.
    """
    path = REPO / "data" / "tiger" / "primary_roads_wtx.geojson"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        gj = json.load(f)
    out = []
    for feat in gj.get("features", gj):
        name = ((feat.get("properties") or {}).get("name") or "").strip()
        g = feat.get("geometry") or {}
        gtype, coords = g.get("type"), g.get("coordinates")
        parts = [coords] if gtype == "LineString" else (coords if gtype == "MultiLineString" else [])
        for part in parts:
            part = [c for c in part if len(c) >= 2]
            if len(part) < 2 or not seg_in_bbox(part):
                continue
            simp = rdp([[c[0], c[1]] for c in part], 0.003)
            if len(simp) >= 2:
                out.append({"coords": r6(simp), "name": name})
    return out


def dc_anchors():
    """Data-center / large-load anchors, from the tracked anchor file."""
    path = REPO / "data" / "datacenters" / "dc_anchors.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    items = raw.get("entries", raw) if isinstance(raw, dict) else raw
    out = []
    for a in items:
        if not isinstance(a, dict):
            continue
        lon, lat = a.get("lon"), a.get("lat")
        if lon is None or lat is None:
            continue
        out.append({
            "id": a.get("id"), "name": a.get("name"),
            "lon": round(float(lon), 5), "lat": round(float(lat), 5),
            "mi": round(D.miles(float(lon), float(lat)), 1),
            "status": a.get("status"), "mw": a.get("capacity_mw_announced"),
            "county": a.get("county"),
            "coord_accuracy": a.get("coord_accuracy"),
        })
    return out


def build():
    geoms = stream_geoms(
        ["counties", "transmission", "tpit_lines"],
        simplify=0.004,
    )
    geoms["highways"] = highways()
    # Named site / feature polygons — real boundaries, not points. These are
    # what let the maps show GW Ranch, Longfellow and the Solstice substation
    # as actual land positions relative to the tract.
    # No simplification: these are small, few, and their shape IS the content.
    sites = stream_geoms(
        ["gw_ranch", "longfellow_ranch", "la_escalera", "caramba_south",
         "solstice_substation", "waha_circle", "mpgcd_zone1", "water_mains_approx"],
        simplify=0,
    )
    geoms.update(sites)
    tract = [r6(ring) for ring in D.RINGS]
    pts = stream_points(["substations", "tpit_subs", "cities", "labels_hubs",
                         "eia860_plants", "ercot_queue", "waha_circle"])
    ins = {}
    try:
        import build_insight_pack as IP
        ins = IP.build().get("distances_edge_to_edge", {})
    except Exception:
        pass
    return {
        "bbox": list(BBOX),
        "center": [round(D.CX, 5), round(D.CY, 5)],
        "tract": tract,
        "geoms": geoms,
        "points": pts,
        "dc_anchors": dc_anchors(),
        "distances": ins,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="outputs/reports/om_exhibits/map_geometry.json")
    args = ap.parse_args()
    data = build()
    out = REPO / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))
    os.replace(tmp, out)
    counts = {k: len(v) for k, v in data["geoms"].items()}
    pcounts = {k: len(v) for k, v in data["points"].items()}
    print(f"geometry -> {out.relative_to(REPO)}")
    print(f"  lines   {counts}")
    print(f"  points  {pcounts}")
    print(f"  anchors {len(data['dc_anchors'])}  tract rings {len(data['tract'])}")


if __name__ == "__main__":
    main()
