#!/usr/bin/env python3
"""Derive additional regional-power "insight" analytics beyond the core OM
data model (caramba_om_data.py), for the redesigned marketing materials.

Everything here is computed from data already loaded/sourced by
caramba_om_data.py — no hand-coded coordinates or feature values, per repo
convention. This module adds three things the base model doesn't compute:

  1. Ring-radius cumulative capacity (operating + ERCOT queue), region-wide
     (not county-bounded), at 15 / 30 / 60 mile bands from the Caramba
     North tract centroid — the "power gravity" curve.
  2. Project-maturity mix among the local (<=60mi) data-center anchors —
     how much of the announced capacity is already under construction vs.
     merely announced/seeking a tenant.
  3. Edge-to-edge (tract-boundary-to-site) distances for the two feature
     anchors (GW Ranch, Longfellow/Project Horizon), which run measurably
     shorter than the centroid-to-point figures used elsewhere, since the
     Caramba North tract itself has spatial extent.

Usage:
    python3 scripts/build_insight_pack.py --json /tmp/om_insights.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import caramba_om_data as D  # noqa: E402

RING_BANDS_MI = [15, 30, 60, 100]
TECH_LABEL = D.TECH_LABEL


def _miles_xy(lon1, lat1, lon2, lat2):
    return math.hypot((lat2 - lat1) * 69.0,
                       (lon2 - lon1) * 69.0 * math.cos(math.radians((lat1 + lat2) / 2)))


def _point_to_segment(px, py, ax, ay, bx, by):
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    ab2 = abx * abx + aby * aby
    t = 0 if ab2 == 0 else max(0, min(1, (apx * abx + apy * aby) / ab2))
    return ax + t * abx, ay + t * aby


def boundary_distance_mi(target_lon, target_lat):
    """Nearest-edge distance, in miles, from the Caramba North tract
    boundary (D.RINGS) to an external point — not centroid-to-point."""
    best = 1e18
    for ring in D.RINGS:
        n = len(ring)
        for i in range(n):
            ax, ay = ring[i]
            bx, by = ring[(i + 1) % n]
            qx, qy = _point_to_segment(target_lon, target_lat, ax, ay, bx, by)
            d = _miles_xy(target_lon, target_lat, qx, qy)
            best = min(best, d)
    return round(best, 1)


def ring_analysis(pts):
    """Cumulative operating + ERCOT-queue capacity within each radius band,
    region-wide (all counties in the point layers, not just Pecos/adjacent)."""
    bands = {b: {"operating_mw": 0.0, "queue_mw": 0.0,
                 "operating_projects": set(), "queue_projects": set()} for b in RING_BANDS_MI}

    for r in pts["eia860_plants"]:
        lat, lon = D.pflt(r["lat"]), D.pflt(r["lon"])
        if lat is None or lon is None:
            continue
        tech = D._eia_tech(r.get("technology") or "")
        if not tech:
            continue
        d = D.miles(lon, lat)
        mw = D.pflt(r.get("capacity_mw")) or 0.0
        key = r.get("plant_code") or r["name"]
        for b in RING_BANDS_MI:
            if d <= b:
                bands[b]["operating_mw"] += mw
                bands[b]["operating_projects"].add(key)

    for r in pts["ercot_queue"]:
        lat, lon = D.pflt(r["lat"]), D.pflt(r["lon"])
        if lat is None or lon is None:
            continue
        d = D.miles(lon, lat)
        mw = D.pflt(r.get("mw")) or 0.0
        key = (r.get("name") or "").strip() or id(r)
        for b in RING_BANDS_MI:
            if d <= b:
                bands[b]["queue_mw"] += mw
                bands[b]["queue_projects"].add(key)

    out = []
    for b in RING_BANDS_MI:
        e = bands[b]
        out.append({
            "radius_mi": b,
            "operating_mw": round(e["operating_mw"]),
            "operating_gw": round(e["operating_mw"] / 1000, 2),
            "operating_project_count": len(e["operating_projects"]),
            "queue_mw": round(e["queue_mw"]),
            "queue_gw": round(e["queue_mw"] / 1000, 2),
            "queue_project_count": len(e["queue_projects"]),
            "total_gw": round((e["operating_mw"] + e["queue_mw"]) / 1000, 2),
        })
    return out


def project_maturity(section7):
    anchors = [a for a in section7["anchors"] if a["miles"] is not None and a["miles"] <= section7["local_radius_mi"]]
    buckets = {}
    for a in anchors:
        status = (a.get("status") or "unspecified").strip().lower()
        if "under construction" in status:
            key = "under_construction"
        elif "operat" in status:
            key = "operating"
        elif "seeking" in status or "tenant" in status:
            key = "seeking_tenant"
        else:
            key = "announced_permitted"
        b = buckets.setdefault(key, {"count": 0, "mw": 0})
        b["count"] += 1
        b["mw"] += a.get("capacity_mw") or 0
    total_mw = sum(b["mw"] for b in buckets.values()) or 1
    for b in buckets.values():
        b["pct_of_local_mw"] = round(100 * b["mw"] / total_mw, 1)
    return buckets


def build(out_path=None):
    pts = D.load_points(["ercot_queue", "eia860_plants", "eia860_battery", "solar", "substations"])
    model = D.build()
    section7 = model["section7"]

    gw_ranch = next(a for a in section7["anchors"] if a["id"] == "gw-ranch-pacifico-pecos")
    longfellow = next(a for a in section7["anchors"] if a["id"] == "project-horizon-poolside-coreweave")

    result = {
        "ring_analysis": ring_analysis(pts),
        "project_maturity": project_maturity(section7),
        "distances_edge_to_edge": {
            "gw_ranch_mi": boundary_distance_mi(gw_ranch["lon"], gw_ranch["lat"]),
            "gw_ranch_centroid_mi": gw_ranch["miles"],
            "longfellow_mi": boundary_distance_mi(longfellow["lon"], longfellow["lat"]),
            "longfellow_centroid_mi": longfellow["miles"],
            "note": ("Edge-to-edge = nearest point on the Caramba North tract boundary to the "
                     "site's disclosed/reported location, vs. centroid-to-point used elsewhere. "
                     "Longfellow/Project Horizon's own site (projecthorizon-tx.com) states "
                     "the location is 'more than 25 miles outside of Fort Stockton' -- consistent "
                     "with the longer figure here; do not round this down."),
        },
    }
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"wrote {out_path}")
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    args = ap.parse_args()
    r = build(args.json)
    print(json.dumps(r, indent=2)[:2000])
