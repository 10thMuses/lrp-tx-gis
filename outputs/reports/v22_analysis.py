#!/usr/bin/env python3
"""v22 supporting analysis — answers advisor's questions for the memo restructure.

1) Wellbore-based actual-drilled vs recompletion-restamp ratio in Pecos since 2020.
2) Of the 116 genuine-new-drill wellbores in Pecos with spud >= 2020:
   - Within / beyond 10 mi of Caramba centroid.
   - For the beyond-10-mi cohort: median distance + depth distribution.
3) Spud-year distribution of the 291 non-plugged wellbores within 10 mi of
   Caramba (post-recompletion-restamp filter, in the wells_permian6 layer),
   to explain why 83% are marginal/end-of-life under the strict threshold.
"""
import csv, json, math, statistics
from collections import Counter
from pathlib import Path

REPO = Path("/home/andreahimmel/lrp-tx-gis")
CSV = REPO / "data" / "wells_permian6.csv"
ND  = Path("/tmp/gis_build/split/wells_permian6.ndjson")

# Caramba centroid (same method as pecos_caramba_vicinity.py).
gj = json.load(open(REPO / "combined_geoms.geojson", encoding="utf-8"))
feats = gj.get("features", gj if isinstance(gj, list) else [])
caramba = next((f for f in feats if "caramba" in json.dumps(f.get("properties") or {}).lower()), None)
g = caramba["geometry"]
car_rings = [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
pts = [pt for r in car_rings for pt in r]
CX = sum(p[0] for p in pts) / len(pts)
CY = sum(p[1] for p in pts) / len(pts)

def miles(lon, lat):
    dlat = (lat - CY) * 69.0
    dlon = (lon - CX) * 69.0 * math.cos(math.radians((lat + CY) / 2))
    return math.hypot(dlat, dlon)


def parse_int(s):
    try:
        return int(float(s)) if s not in (None, "") else None
    except Exception:
        return None


def parse_float(s):
    try:
        return float(s) if s not in (None, "") else None
    except Exception:
        return None


# ---------- (1) Pecos since-2020 wellbore record: actual drilling vs restamps ----------
n_total_pecos_post2020 = 0
n_genuine_new = 0
n_restamp = 0
n_unknown = 0
genuine_by_year = Counter()
restamp_by_year = Counter()

# Track for (2): the 116 genuine new wells (Pecos, completion>=spud, spud>=2020)
g116 = []  # list of dicts

with open(CSV, encoding="utf-8") as fh:
    rd = csv.DictReader(fh)
    for r in rd:
        if (r.get("county_name") or "").strip() != "Pecos":
            continue
        sy = parse_int(r.get("spud_year"))
        cy = parse_int(r.get("completion_year"))
        # since-2020 set: spud_year >= 2020 OR completion_year >= 2020
        in_post2020 = (sy is not None and sy >= 2020) or (cy is not None and cy >= 2020)
        if in_post2020:
            n_total_pecos_post2020 += 1
            if sy is not None and cy is not None:
                if cy >= sy:
                    n_genuine_new += 1
                    genuine_by_year[sy if sy >= 2020 else cy] += 1
                else:
                    n_restamp += 1
                    restamp_by_year[max(sy, cy)] += 1
            else:
                n_unknown += 1
        # For (2): the 116 cohort (spud>=2020 + completion>=spud)
        if sy is not None and sy >= 2020 and cy is not None and cy >= sy:
            lon = parse_float(r.get("lon")); lat = parse_float(r.get("lat"))
            td = parse_float(r.get("total_depth"))
            if lon is not None and lat is not None:
                g116.append(dict(api=r.get("api_no"), sy=sy, td=td,
                                 mi=miles(lon, lat), plug=(r.get("plug_flag") or "").strip().upper()))

print("=== (1) PECOS WELLBORE RECORDS SINCE 2020 ===")
print(f"  Total records (spud OR completion >= 2020): {n_total_pecos_post2020:,}")
print(f"    Genuine new (completion >= spud):         {n_genuine_new:,}  ({100*n_genuine_new/max(n_total_pecos_post2020,1):.1f}%)")
print(f"    Recompletion restamps (completion < spud):{n_restamp:,}  ({100*n_restamp/max(n_total_pecos_post2020,1):.1f}%)")
print(f"    Missing one or both dates:                {n_unknown:,}")
print()
print("=== (2) THE 116 GENUINE NEW WELLS IN PECOS (spud>=2020, completion>=spud) ===")
print(f"  Total: {len(g116)}")
near = [w for w in g116 if w["mi"] <= 10]
far  = [w for w in g116 if w["mi"] > 10]
print(f"    Within 10 mi of Caramba: {len(near)}  (depths: {sorted([int(w['td']) for w in near if w['td']])})  miles: {sorted([round(w['mi'],2) for w in near])}")
print(f"    Beyond 10 mi:            {len(far)}")
if far:
    dists = [w["mi"] for w in far]
    depths = [w["td"] for w in far if w["td"] is not None]
    print(f"      Median distance: {statistics.median(dists):.2f} mi")
    print(f"      Mean distance:   {statistics.mean(dists):.2f} mi")
    print(f"      Min / Max:       {min(dists):.2f} / {max(dists):.2f} mi")
    if depths:
        print(f"      Median depth:    {statistics.median(depths):,.0f} ft")
        print(f"      Mean depth:      {statistics.mean(depths):,.0f} ft")
        # depth bands
        b_shallow = sum(1 for d in depths if d < 3000)
        b_3_5 = sum(1 for d in depths if 3000 <= d < 5000)
        b_5_10 = sum(1 for d in depths if 5000 <= d < 10000)
        b_10p = sum(1 for d in depths if d >= 10000)
        print(f"      Depth bands (n={len(depths)} with depth on record):")
        print(f"        <3,000 ft:        {b_shallow}")
        print(f"        3,000-4,999 ft:   {b_3_5}")
        print(f"        5,000-9,999 ft:   {b_5_10}")
        print(f"        >=10,000 ft:      {b_10p}")
        print(f"      Missing depth:      {len(far) - len(depths)}")

# ---------- (3) Spud-year distribution of 291 within-10 non-plugged wellbores ----------
print()
print("=== (3) SPUD-YEAR DISTRIBUTION OF 291 NON-PLUGGED WELLBORES WITHIN 10 MI OF CARAMBA ===")
print("    (from the built wells_permian6 ndjson -- recompletion restamps already excluded)")
if ND.exists():
    decades = Counter()
    by_status = Counter()
    with open(ND, encoding="utf-8") as fh:
        for line in fh:
            try:
                o = json.loads(line)
            except Exception:
                continue
            p = o.get("properties") or {}
            geom = o.get("geometry") or {}
            c = geom.get("coordinates") or [None, None]
            try:
                lon, lat = float(c[0]), float(c[1])
            except Exception:
                continue
            mi = miles(lon, lat)
            if mi > 10:
                continue
            is_plug = str(p.get("plug_flag") or "").strip().upper() == "Y"
            if is_plug:
                continue
            sy = parse_int(p.get("spud_year"))
            st = p.get("well_status") or "Active"
            by_status[st] += 1
            if sy is not None:
                dec = (sy // 10) * 10
                decades[dec] += 1
    total = sum(by_status.values())
    print(f"    Total non-plugged within 10 mi: {total}")
    for st, n in by_status.most_common():
        print(f"      {st}: {n}  ({100*n/max(total,1):.1f}%)")
    print(f"    By spud decade:")
    for d in sorted(decades):
        print(f"      {d}s: {decades[d]}")
else:
    print("    (ndjson not present)")
