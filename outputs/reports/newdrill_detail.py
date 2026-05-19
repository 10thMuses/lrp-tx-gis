import csv, collections, json, math, re
REPO = "/home/andreahimmel/lrp-tx-gis"
def apikey(s):
    d = re.sub(r"\D", "", s or ""); return d[-8:] if len(d) >= 8 else d
gj = json.load(open(REPO + "/combined_geoms.geojson", encoding="utf-8"))
feats = gj.get("features", gj)
car = next(f for f in feats if "caramba" in json.dumps(f.get("properties") or {}).lower())
g = car["geometry"]
rings = [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
pts = [p for r in rings for p in r]
cx = sum(p[0] for p in pts)/len(pts); cy = sum(p[1] for p in pts)/len(pts)
def miles(lo, la): return math.hypot((la-cy)*69.0, (lo-cx)*69.0*math.cos(math.radians((la+cy)/2)))

# W-1: per api -> purposes; per-permit (>=2020) operator/purpose/depth
api_nd = {}            # api -> True if any New Drill, False if only recomp/reenter, absent=unmatched
nd_ops = collections.Counter(); rc_ops = collections.Counter()
nd_depth = collections.Counter()
for r in csv.DictReader(open(REPO + "/outputs/refresh/rrc_w1_permits.csv", encoding="utf-8", errors="replace")):
    if (r.get("county_name") or "").strip().upper() != "PECOS":
        continue
    k = apikey(r.get("api_no")); fp = (r.get("filing_purpose") or "").strip().lower()
    if k:
        if "new" in fp:
            api_nd[k] = True
        elif k not in api_nd:
            api_nd[k] = False
    try:
        yc = int(float(r.get("year_chunk") or 0))
    except ValueError:
        yc = 0
    if yc < 2020:
        continue
    op = (r.get("operator_name") or "").strip()
    try:
        td = float(r["total_depth"]) if r.get("total_depth") not in (None, "") else None
    except ValueError:
        td = None
    if "new" in fp:
        nd_ops[op] += 1
        b = "<3000" if (td is not None and td < 3000) else (">=3000" if td is not None else "?")
        nd_depth[b] += 1
    elif "recomp" in fp:
        rc_ops[op] += 1

print("=== NEW-DRILL permits Pecos >=2020: top operators ===")
ndtot = sum(nd_ops.values())
for o, c in nd_ops.most_common(8):
    print("  %4d  %5.1f%%  %s" % (c, 100.0*c/ndtot, o))
print("  new-drill depth split:", dict(nd_depth), " (n=%d)" % ndtot)
print("\n=== RECOMPLETION permits Pecos >=2020: top operators ===")
rctot = sum(rc_ops.values())
for o, c in rc_ops.most_common(5):
    print("  %4d  %5.1f%%  %s" % (c, 100.0*c/rctot, o))

# spud>=2020 wells, new-drill only
W = []
for r in csv.DictReader(open(REPO + "/data/wells_permian6.csv", encoding="utf-8")):
    if (r.get("county_name") or "").strip() != "Pecos":
        continue
    try:
        sy = int(float(r["spud_year"])) if r.get("spud_year") not in (None, "") else None
    except ValueError:
        sy = None
    if sy is None or sy < 2020:
        continue
    k = apikey(r.get("api_no"))
    try:
        td = float(r["total_depth"]) if r.get("total_depth") not in (None, "") else None
    except ValueError:
        td = None
    try:
        d = miles(float(r["lon"]), float(r["lat"]))
    except (TypeError, ValueError):
        d = None
    W.append((sy, td, d, api_nd.get(k), k))

nd = [w for w in W if w[3] is True]
print("\n=== Spud>=2020 NEW-DRILL-only (Pecos) ===")
print("  total new-drill        : %d" % len(nd))
for mi in (2, 5, 10):
    s = [w for w in nd if w[2] is not None and w[2] <= mi]
    print("  within %2d mi           : %d  (shallow<3k=%d, deep=%d)"
          % (mi, len(s), sum(1 for w in s if w[1] is not None and w[1] < 3000),
             sum(1 for w in s if w[1] is not None and w[1] >= 3000)))
sh = sum(1 for w in nd if w[1] is not None and w[1] < 3000)
print("  shallow<3k / deep      : %d / %d" % (sh, sum(1 for w in nd if w[1] is not None and w[1] >= 3000)))
print("\n  the new-drill wells within 10 mi (yr, depth, dist mi):")
for w in sorted([w for w in nd if w[2] is not None and w[2] <= 10], key=lambda x: x[2]):
    print("    %d  %s ft  %.2f mi" % (w[0], int(w[1]) if w[1] else "?", w[2]))
