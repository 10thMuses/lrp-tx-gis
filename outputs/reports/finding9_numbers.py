#!/usr/bin/env python3
"""Derive exact Finding 9 numbers from the BUILT wells layer.

Reads the post-filter genuine-new-drill ndjson the build fed to tippecanoe
(/tmp/gis_build/split/wells_permian6.ndjson) so counts match the deployed map
exactly (recompletions excluded, min_spud_year applied, well_status set).
Centroid + miles() mirror outputs/reports/pecos_caramba_vicinity.py so the
ring counts are consistent with Findings 1-6.
"""
import json, math, csv

REPO = "/home/andreahimmel/lrp-tx-gis"
ND = "/tmp/gis_build/split/wells_permian6.ndjson"

# --- Caramba centroid (same method as pecos_caramba_vicinity.py) ---
gj = json.load(open(REPO + "/combined_geoms.geojson", encoding="utf-8"))
feats = gj.get("features", gj if isinstance(gj, list) else [])
caramba = next((f for f in feats if "caramba" in json.dumps(f.get("properties") or {}).lower()), None)
g = caramba["geometry"]
car_rings = [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
pts = [pt for r in car_rings for pt in r]
cx = sum(p[0] for p in pts) / len(pts)
cy = sum(p[1] for p in pts) / len(pts)


def miles(lon, lat):
    dlat = (lat - cy) * 69.0
    dlon = (lon - cx) * 69.0 * math.cos(math.radians((lat + cy) / 2))
    return math.hypot(dlat, dlon)


# --- production lookup (same csv build.py joined) ---
prod = {}
with open(REPO + "/data/well_prod_status.csv", newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        a = (r.get("api8") or "").strip()
        try:
            prod[a] = (float(r.get("gas_mcf_d") or 0), float(r.get("oil_bbl_d") or 0))
        except ValueError:
            pass

import re
def api8(s):
    d = re.sub(r"\D", "", s or "")
    return d[-8:] if len(d) >= 8 else d

GAS, OIL = 125.0, 150.0

tot = plug = nolong = active = unmatched_np = 0
rings = {2: [], 5: [], 10: []}
near_producers = []

with open(ND, encoding="utf-8") as fh:
    for line in fh:
        try:
            o = json.loads(line)
        except Exception:
            continue
        p = o.get("properties") or {}
        st = p.get("well_status")
        tot += 1
        if st == "Plugged":
            plug += 1
        elif st == "Inactive - no longer producing":
            nolong += 1
        else:
            active += 1
        geom = o.get("geometry") or {}
        c = geom.get("coordinates") or [None, None]
        try:
            lon, lat = float(c[0]), float(c[1])
        except Exception:
            continue
        mi = miles(lon, lat)
        rec = prod.get(api8(p.get("api_no")))
        is_np = st != "Plugged"
        matched = rec is not None
        if is_np and not matched:
            unmatched_np += 1
        producing = is_np and matched and not (rec[0] < GAS and rec[1] < OIL)
        for R in (2, 5, 10):
            if mi <= R:
                rings[R].append((mi, st, matched, producing, rec, p.get("api_no")))
        if mi <= 10 and producing:
            near_producers.append((mi, p.get("api_no"), rec, p.get("oil_gas"), p.get("spud_year"), p.get("total_depth")))

print(f"centroid lon={cx:.5f} lat={cy:.5f}")
print(f"LAYER TOTAL (genuine-new-drill, map population): {tot:,}")
print(f"  Plugged:                      {plug:,}")
print(f"  Inactive - no longer producing:{nolong:,}")
print(f"  Active:                       {active:,}")
print(f"  (non-plugged unmatched, kept Active): {unmatched_np:,}")
print()
for R in (2, 5, 10):
    rr = rings[R]
    np_ = [x for x in rr if x[1] != "Plugged"]
    npm = [x for x in np_ if x[2]]
    prod_ = [x for x in np_ if x[3]]
    nol = [x for x in np_ if x[2] and not x[3]]
    pl = [x for x in rr if x[1] == "Plugged"]
    print(f"<= {R} mi: total={len(rr)}  plugged={len(pl)}  non-plugged={len(np_)}  "
          f"matched={len(npm)}  STILL PRODUCING={len(prod_)}  no-longer={len(nol)}")
print()
print("STILL-PRODUCING wells within 10 mi (mi, api, gas_mcfd, oil_bbld, og, spud, depth):")
for mi, api, rec, og, sy, td in sorted(near_producers):
    print(f"  {mi:5.2f} mi  api={api}  gas={rec[0]:.1f} Mcf/d  oil={rec[1]:.1f} bbl/d  og={og}  spud={sy}  depth={td}")
