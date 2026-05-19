"""Operators of wells SPUDDED in Pecos since 2020. The dbo900 wellbore file has
no operator field, so join spudded wells -> RRC W-1 permit record by normalized
API (county3+unique5 = last 8 digits)."""
import csv, collections, json, math, re

REPO = "/home/andreahimmel/lrp-tx-gis"

def apikey(s):
    d = re.sub(r"\D", "", s or "")
    return d[-8:] if len(d) >= 8 else d

# Caramba centroid for the within-10-mi cut
gj = json.load(open(REPO + "/combined_geoms.geojson", encoding="utf-8"))
feats = gj.get("features", gj)
car = next(f for f in feats if "caramba" in json.dumps(f.get("properties") or {}).lower())
g = car["geometry"]
rings = [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
pts = [p for r in rings for p in r]
cx = sum(p[0] for p in pts)/len(pts); cy = sum(p[1] for p in pts)/len(pts)
def miles(lo, la):
    return math.hypot((la-cy)*69.0, (lo-cx)*69.0*math.cos(math.radians((la+cy)/2)))

# api -> operator from W-1 (comprehensive Pecos scrape); fallback permits file
op = {}
for r in csv.DictReader(open(REPO + "/outputs/refresh/rrc_w1_permits.csv", encoding="utf-8", errors="replace")):
    if (r.get("county_name") or "").strip().upper() != "PECOS":
        continue
    k = apikey(r.get("api_no")); o = (r.get("operator_name") or "").strip()
    if k and o and k not in op:
        op[k] = o
for r in csv.DictReader(open(REPO + "/data/permits_permian6.csv", encoding="utf-8")):
    if (r.get("county_name") or "").strip() != "Pecos":
        continue
    k = apikey(r.get("api_no")); o = (r.get("operator_name") or "").strip()
    if k and o and k not in op:
        op[k] = o
print("operator lookup size (Pecos):", len(op))

allc = collections.Counter(); nearc = collections.Counter()
n = near = matched = nearmatched = 0
for r in csv.DictReader(open(REPO + "/data/wells_permian6.csv", encoding="utf-8")):
    if (r.get("county_name") or "").strip() != "Pecos":
        continue
    try:
        sy = int(float(r["spud_year"])) if r.get("spud_year") not in (None, "") else None
    except ValueError:
        sy = None
    if sy is None or sy < 2020:
        continue
    n += 1
    o = op.get(apikey(r.get("api_no")))
    if o:
        matched += 1
        allc[o] += 1
    try:
        d = miles(float(r["lon"]), float(r["lat"]))
    except (TypeError, ValueError):
        d = None
    if d is not None and d <= 10:
        near += 1
        if o:
            nearmatched += 1
            nearc[o] += 1

print("\n=== PECOS wells SPUDDED >= 2020 ===")
print("total=%d  operator matched=%d (%.0f%%)" % (n, matched, 100.0*matched/max(1, n)))
print("Top operators (of matched):")
for o, c in allc.most_common(15):
    print("  %5d  %5.1f%%  %s" % (c, 100.0*c/max(1, matched), o))

print("\n=== Within 10 mi of Caramba (spud >= 2020) ===")
print("total=%d  operator matched=%d" % (near, nearmatched))
for o, c in nearc.most_common(12):
    print("  %3d  %s" % (c, o))
