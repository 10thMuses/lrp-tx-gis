import csv, json, math

REPO = "/home/andreahimmel/lrp-tx-gis"
gj = json.load(open(REPO + "/combined_geoms.geojson", encoding="utf-8"))
feats = gj.get("features", gj if isinstance(gj, list) else [])
car = next(f for f in feats if "caramba" in json.dumps(f.get("properties") or {}).lower())
g = car["geometry"]
rings = [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
pts = [p for r in rings for p in r]
cx = sum(p[0] for p in pts)/len(pts); cy = sum(p[1] for p in pts)/len(pts)
def mi(lo, la):
    dl = (la-cy)*69.0; do = (lo-cx)*69.0*math.cos(math.radians((la+cy)/2)); return math.hypot(dl, do)

W = []
for r in csv.DictReader(open(REPO + "/data/wells_permian6.csv", encoding="utf-8")):
    if (r.get("county_name") or "").strip() != "Pecos":
        continue
    try: td = float(r["total_depth"]) if r.get("total_depth") not in (None, "") else None
    except ValueError: td = None
    try: sy = int(float(r["spud_year"])) if r.get("spud_year") not in (None, "") else None
    except ValueError: sy = None
    try: lo = float(r["lon"]); la = float(r["lat"])
    except (TypeError, ValueError): lo = la = None
    if lo is None or sy is None:
        continue
    W.append((sy, td, mi(lo, la)))

RINGS = [2, 5, 10, 15]
YEARS = list(range(2015, 2027))
print("Pecos wells spudded by year, within distance of Caramba — count (shallow<3000 / deep>=3000 / unknown-depth)")
hdr = "year |" + "".join(" %-22s|" % ("<=%d mi" % m) for m in RINGS)
print(hdr)
for y in YEARS:
    cells = []
    for m in RINGS:
        grp = [w for w in W if w[0] == y and w[2] <= m]
        n = len(grp)
        sh = sum(1 for w in grp if w[1] is not None and w[1] < 3000)
        dp = sum(1 for w in grp if w[1] is not None and w[1] >= 3000)
        un = sum(1 for w in grp if w[1] is None)
        cells.append(" n=%-3d sh=%-3d dp=%-3d ?=%-2d|" % (n, sh, dp, un))
    print("%4d |%s" % (y, "".join(cells)))

print("\nAggregate spud >= 2020:")
for m in RINGS:
    grp = [w for w in W if w[0] >= 2020 and w[2] <= m]
    n = len(grp); sh = sum(1 for w in grp if w[1] is not None and w[1] < 3000)
    dp = sum(1 for w in grp if w[1] is not None and w[1] >= 3000)
    un = sum(1 for w in grp if w[1] is None)
    den = sh + dp
    print("  <=%2d mi: spudded>=2020 n=%d  shallow<3000=%d  deep>=3000=%d  unknown=%d  -> shallow share of depth-known = %s"
          % (m, n, sh, dp, un, ("%.0f%%" % (100*sh/den)) if den else "n/a"))

print("\nAggregate spud >= 2015:")
for m in RINGS:
    grp = [w for w in W if w[0] >= 2015 and w[2] <= m]
    n = len(grp); sh = sum(1 for w in grp if w[1] is not None and w[1] < 3000)
    dp = sum(1 for w in grp if w[1] is not None and w[1] >= 3000)
    den = sh + dp
    print("  <=%2d mi: n=%d shallow=%d deep=%d shallow_share=%s"
          % (m, n, sh, dp, ("%.0f%%" % (100*sh/den)) if den else "n/a"))
