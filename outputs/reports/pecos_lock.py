"""Lock canonical numbers under RULE H (genuine new drill = completion_year
blank OR completion_year >= spud_year). Per-county, spud_year >= 2020."""
import csv, json, math, collections

REPO = "/home/andreahimmel/lrp-tx-gis"
gj = json.load(open(REPO + "/combined_geoms.geojson", encoding="utf-8")); feats = gj.get("features", gj)
car = next(f for f in feats if "caramba" in json.dumps(f.get("properties") or {}).lower())
g = car["geometry"]; rg = [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
pp = [p for r in rg for p in r]; cx = sum(p[0] for p in pp)/len(pp); cy = sum(p[1] for p in pp)/len(pp)
def miles(lo, la): return math.hypot((la-cy)*69.0, (lo-cx)*69.0*math.cos(math.radians((la+cy)/2)))
def pint(v):
    try: return int(float(v))
    except (TypeError, ValueError): return None
def pflt(v):
    try: return float(v) if v not in (None, "") else None
    except (TypeError, ValueError): return None

rows = list(csv.DictReader(open(REPO + "/data/wells_permian6.csv", encoding="utf-8")))
COUNTIES = ["Pecos", "Reeves", "Ward", "Midland", "Martin", "Reagan"]

def is_new_drill(r):
    sy = pint(r.get("spud_year"))
    if sy is None: return False
    cyr = pint(r.get("completion_year"))
    return cyr is None or cyr >= sy

print("=== Per-county GENUINE NEW DRILL (completion>=spud), spud_year >= 2020 ===")
print("%-9s %8s %10s %9s %8s" % ("county", "all>=20", "newdrill", "shallow<3k", "deep>=3k"))
per = {}
for c in COUNTIES:
    cr = [r for r in rows if (r.get("county_name") or "").strip() == c]
    s20 = [r for r in cr if (pint(r.get("spud_year")) or 0) >= 2020]
    nd = [r for r in s20 if is_new_drill(r)]
    ndd = [r for r in nd if pflt(r.get("total_depth")) is not None]
    sh = sum(1 for r in ndd if pflt(r.get("total_depth")) < 3000)
    dp = sum(1 for r in ndd if pflt(r.get("total_depth")) >= 3000)
    per[c] = dict(all20=len(s20), nd=len(nd), sh=sh, dp=dp)
    print("%-9s %8d %10d %9d %8d" % (c, len(s20), len(nd), sh, dp))

oth = [c for c in COUNTIES if c != "Pecos"]
avg_nd = sum(per[c]["nd"] for c in oth)/len(oth)
avg_sh = sum(per[c]["sh"] for c in oth)/len(oth)
print("\nPECOS new-drill since 2020: %d  (shallow %d, deep %d)" % (per["Pecos"]["nd"], per["Pecos"]["sh"], per["Pecos"]["dp"]))
print("Other-5 avg new-drill since 2020: %.0f  (avg shallow %.0f)" % (avg_nd, avg_sh))
print("Martin specifically: new-drill %d (shallow %d, deep %d)" % (per["Martin"]["nd"], per["Martin"]["sh"], per["Martin"]["dp"]))

# Pecos proximity (locked)
pe = [r for r in rows if (r.get("county_name") or "").strip() == "Pecos"]
ndp = [r for r in pe if (pint(r.get("spud_year")) or 0) >= 2020 and is_new_drill(r)]
g = []
for r in ndp:
    try: g.append((miles(float(r["lon"]), float(r["lat"])), r))
    except (TypeError, ValueError): pass
print("\nPECOS new-drill proximity: <=2mi=%d  <=5mi=%d  <=10mi=%d" %
      (sum(1 for m, _ in g if m <= 2), sum(1 for m, _ in g if m <= 5), sum(1 for m, _ in g if m <= 10)))
for m, r in sorted([x for x in g if x[0] <= 10]):
    print("   %.2f mi  spud=%s depth=%s completion=%s" % (m, r.get("spud_year"), r.get("total_depth"), r.get("completion_year")))
print("nearest new-drill: %.2f mi" % min(m for m, _ in g))

# map-filter impact (all years, all 6 counties): drop where completion<spud
print("\n=== MAP FILTER impact (drop rows where completion_year < spud_year) ===")
for c in COUNTIES:
    cr = [r for r in rows if (r.get("county_name") or "").strip() == c]
    drop = sum(1 for r in cr if (pint(r.get("spud_year")) is not None and pint(r.get("completion_year")) is not None and pint(r.get("completion_year")) < pint(r.get("spud_year"))))
    print("  %-9s total=%6d  dropped=%6d  kept=%6d" % (c, len(cr), drop, len(cr)-drop))
tot = len(rows); drop = sum(1 for r in rows if (pint(r.get("spud_year")) is not None and pint(r.get("completion_year")) is not None and pint(r.get("completion_year")) < pint(r.get("spud_year"))))
print("  ALL 6     total=%6d  dropped=%6d  kept=%6d" % (tot, drop, tot-drop))
