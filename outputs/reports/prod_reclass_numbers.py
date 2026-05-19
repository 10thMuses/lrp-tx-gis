"""Corrected production-reclassification numbers at gas<125 Mcf/d AND oil<150
bbl/d, from existing data/lease_status.csv (no PDQ re-parse). County-wide and
near the Caramba North tract."""
import csv, json, math

REPO = "/home/andreahimmel/lrp-tx-gis"
GAS, OIL = 125.0, 150.0

# Caramba centroid
gj = json.load(open(REPO + "/combined_geoms.geojson", encoding="utf-8")); feats = gj.get("features", gj)
car = next(f for f in feats if "caramba" in json.dumps(f.get("properties") or {}).lower())
g = car["geometry"]; rg = [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
pp = [p for r in rg for p in r]; cx = sum(p[0] for p in pp)/len(pp); cy = sum(p[1] for p in pp)/len(pp)
def miles(lo, la): return math.hypot((la-cy)*69.0, (lo-cx)*69.0*math.cos(math.radians((la+cy)/2)))

st = {}
for r in csv.DictReader(open(REPO + "/data/lease_status.csv", encoding="utf-8")):
    k = ((r["oil_gas"] or "").strip().upper()[:1], (r["district"] or "").strip().lstrip("0"), (r["lease_no"] or "").strip().lstrip("0"))
    st[k] = (float(r["gas_mcf_d"] or 0), float(r["oil_bbl_d"] or 0))

def pint(v):
    try: return int(float(v))
    except: return None

tot = plugged = active_unmatched = producing = nolong = 0
near = {2: [0, 0], 5: [0, 0], 10: [0, 0]}  # dist -> [no_longer, producing] among matched non-plugged
for r in csv.DictReader(open(REPO + "/data/wells_permian6.csv", encoding="utf-8")):
    sy = pint(r.get("spud_year")); cyr = pint(r.get("completion_year"))
    if sy is None or sy < 1964:
        continue
    if cyr is not None and cyr < sy:   # recompletion re-stamp (excluded from map)
        continue
    tot += 1
    if (r.get("plug_flag") or "").strip().upper() == "Y":
        plugged += 1
        continue
    k = ((r.get("oil_gas") or "").strip().upper()[:1], (r.get("district") or "").strip().lstrip("0"), (r.get("lease_no") or "").strip().lstrip("0"))
    rec = st.get(k)
    if rec is None:
        active_unmatched += 1
        cls = None
    else:
        gmd, obd = rec
        if gmd < GAS and obd < OIL:
            nolong += 1; cls = "no"
        else:
            producing += 1; cls = "prod"
    if rec is not None:
        try:
            d = miles(float(r["lon"]), float(r["lat"]))
            for R in (2, 5, 10):
                if d <= R:
                    near[R][0 if cls == "no" else 1] += 1
        except (TypeError, ValueError):
            pass

print(f"genuine new-drill wells (1964+, recompletions excluded): {tot}")
print(f"  Plugged: {plugged}")
print(f"  Non-plugged matched, NO LONGER producing (gas<{GAS:.0f} & oil<{OIL:.0f}): {nolong}")
print(f"  Non-plugged matched, still producing: {producing}")
print(f"  Non-plugged unmatched (stay Active, unverified): {active_unmatched}")
print(f"  => Active total (producing + unmatched): {producing + active_unmatched}")
print("Near Caramba (matched non-plugged wells)  [no-longer / still-producing]:")
for R in (2, 5, 10):
    print(f"  within {R:2d} mi: no-longer={near[R][0]}  producing={near[R][1]}")
