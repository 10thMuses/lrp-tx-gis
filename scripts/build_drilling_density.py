"""Build the drilling_permit_density layer features.

Reads:
  outputs/refresh/rrc_w1_counts.csv   (Chat 123 scrape)
  combined_geoms.geojson              (counties layer for geometry)

Writes:
  combined_geoms.geojson              (atomic in-place; appends 11 new features
                                       with layer_id=drilling_permit_density,
                                       drops any pre-existing rows of that layer)

Idempotent. Re-runnable without duplication.

Density windows: all-time (1976-2026), 20-yr (2006+), 10-yr (2016+), 5-yr (2021+).
Area: WGS84 geodesic, pyproj.Geod.polygon_area_perimeter; multipolygons summed.
"""
from __future__ import annotations

import csv
import datetime
import json
import os
import sys
from collections import defaultdict

from pyproj import Geod

CSV_PATH = "outputs/refresh/rrc_w1_counts.csv"
GEOMS_PATH = "combined_geoms.geojson"
LAYER_ID = "drilling_permit_density"
SOURCE_LABEL = "RRC W-1 Public Query"

# 11 Permian counties (matches the Chat 122 scraper TARGETS)
TARGET_COUNTIES = [
    "PECOS", "REEVES", "WARD", "LOVING", "WINKLER",
    "CULBERSON", "CRANE", "UPTON", "REAGAN", "CROCKETT", "TERRELL",
]

# Window definitions: (suffix, start_year_inclusive)
WINDOWS = [
    ("all", 1976),
    ("20yr", 2006),
    ("10yr", 2016),
    ("5yr", 2021),
]

GEOD = Geod(ellps="WGS84")
SQM_PER_SQMI = 2589988.110336


def aggregate_counts(csv_path: str) -> dict:
    """Returns {COUNTY: {'all': int, '20yr': int, '10yr': int, '5yr': int}}."""
    out = {c: {w[0]: 0 for w in WINDOWS} for c in TARGET_COUNTIES}
    with open(csv_path) as f:
        for r in csv.DictReader(f):
            if r.get("status") != "ok":
                continue
            cnt = r.get("count")
            if cnt in (None, ""):
                continue
            try:
                cnt = int(cnt)
                year = int(r["year"])
            except (TypeError, ValueError):
                continue
            cn = r["county_name"].upper()
            if cn not in out:
                continue
            for suffix, start in WINDOWS:
                if year >= start:
                    out[cn][suffix] += cnt
    return out


def polygon_area_sqmi(geom: dict) -> float:
    """Sum geodesic area across all rings of a Polygon or MultiPolygon (WGS84)."""
    t = geom.get("type")
    if t == "Polygon":
        polys = [geom["coordinates"]]
    elif t == "MultiPolygon":
        polys = geom["coordinates"]
    else:
        raise ValueError(f"unsupported geom type {t}")
    total_sqm = 0.0
    for poly in polys:
        # poly is [outer_ring, hole1, hole2, ...]; we treat the absolute area
        # of the outer ring and subtract holes
        outer = poly[0]
        lons = [p[0] for p in outer]
        lats = [p[1] for p in outer]
        area, _ = GEOD.polygon_area_perimeter(lons, lats)
        total_sqm += abs(area)
        for hole in poly[1:]:
            hlons = [p[0] for p in hole]
            hlats = [p[1] for p in hole]
            harea, _ = GEOD.polygon_area_perimeter(hlons, hlats)
            total_sqm -= abs(harea)
    return total_sqm / SQM_PER_SQMI


def round4(v: float) -> float:
    return round(v, 4)


def main():
    if not os.path.exists(CSV_PATH):
        sys.exit(f"missing {CSV_PATH}")
    if not os.path.exists(GEOMS_PATH):
        sys.exit(f"missing {GEOMS_PATH}")

    counts = aggregate_counts(CSV_PATH)

    with open(GEOMS_PATH) as f:
        gj = json.load(f)

    # Find the 11 county polygons; key by NAME (with " County" suffix stripped)
    norm = lambda s: (s or "").replace(" County", "").strip().upper()
    county_geoms = {}
    for ft in gj["features"]:
        props = ft.get("properties") or {}
        if props.get("layer_id") != "counties":
            continue
        name = norm(props.get("NAME"))
        if name in counts:
            county_geoms[name] = ft

    missing = [c for c in TARGET_COUNTIES if c not in county_geoms]
    if missing:
        sys.exit(f"missing county geometries in combined_geoms.geojson: {missing}")

    today = datetime.date.today().isoformat()
    new_features = []
    summary = []
    for cn in TARGET_COUNTIES:
        src_ft = county_geoms[cn]
        geom = src_ft["geometry"]
        area_sqmi = polygon_area_sqmi(geom)
        c = counts[cn]
        density = {w[0]: (c[w[0]] / area_sqmi) if area_sqmi > 0 else 0.0 for w in WINDOWS}
        props = {
            "layer_id": LAYER_ID,
            "county": cn.title(),
            "geoid": (src_ft.get("properties") or {}).get("GEOID"),
            "area_sqmi": round(area_sqmi, 1),
            "permit_count_all": c["all"],
            "permit_count_20yr": c["20yr"],
            "permit_count_10yr": c["10yr"],
            "permit_count_5yr": c["5yr"],
            "permits_per_sqmi_all": round4(density["all"]),
            "permits_per_sqmi_20yr": round4(density["20yr"]),
            "permits_per_sqmi_10yr": round4(density["10yr"]),
            "permits_per_sqmi_5yr": round4(density["5yr"]),
            "source": SOURCE_LABEL,
            "source_date": today,
        }
        new_features.append({"type": "Feature", "geometry": geom, "properties": props})
        summary.append((cn, area_sqmi, c, density))

    # Drop any prior drilling_permit_density features (idempotency); keep everything else
    kept = [
        ft for ft in gj["features"]
        if (ft.get("properties") or {}).get("layer_id") != LAYER_ID
    ]
    gj["features"] = kept + new_features

    # Atomic write per OPERATING.md §6.15
    tmp = GEOMS_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(gj, f, separators=(",", ":"))
    os.replace(tmp, GEOMS_PATH)

    # Summary print — density ranking (20-yr)
    print(f"=== drilling_permit_density built: {len(new_features)} features ===")
    print(f"{'County':<11} {'area_sqmi':>10} {'all':>8} {'20yr':>8} {'10yr':>8} {'5yr':>8} "
          f"{'pps_all':>10} {'pps_20yr':>10} {'pps_10yr':>10} {'pps_5yr':>10}")
    for cn, area, c, d in sorted(summary, key=lambda r: -r[3]["20yr"]):
        print(f"{cn:<11} {area:>10.1f} {c['all']:>8} {c['20yr']:>8} {c['10yr']:>8} {c['5yr']:>8} "
              f"{d['all']:>10.3f} {d['20yr']:>10.3f} {d['10yr']:>10.3f} {d['5yr']:>10.3f}")


if __name__ == "__main__":
    main()
