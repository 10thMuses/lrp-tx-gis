"""Are the 'wells spudded since 2020' genuine NEW drills, or are recompletions /
re-entries inflating the count? Two independent tests:
  (A) wells-file internal sanity: completion_year vs spud_year
  (B) join to W-1 permits by API: does the well have a 'New Drill' permit, and
      do its permits predate 2020 (=> old wellbore re-entered)?
Then recompute the headline numbers on the genuine-new-drill subset."""
import csv, collections, json, math, re, statistics

REPO = "/home/andreahimmel/lrp-tx-gis"

def apikey(s):
    d = re.sub(r"\D", "", s or "")
    return d[-8:] if len(d) >= 8 else d

gj = json.load(open(REPO + "/combined_geoms.geojson", encoding="utf-8"))
feats = gj.get("features", gj)
car = next(f for f in feats if "caramba" in json.dumps(f.get("properties") or {}).lower())
g = car["geometry"]; rings = [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
pts = [p for r in rings for p in r]; cx = sum(p[0] for p in pts)/len(pts); cy = sum(p[1] for p in pts)/len(pts)
def miles(lo, la): return math.hypot((la-cy)*69.0, (lo-cx)*69.0*math.cos(math.radians((la+cy)/2)))

# W-1 permits by API: list of (purpose, year)
permw = collections.defaultdict(list)
for r in csv.DictReader(open(REPO + "/outputs/refresh/rrc_w1_permits.csv", encoding="utf-8", errors="replace")):
    if (r.get("county_name") or "").strip().upper() != "PECOS":
        continue
    k = apikey(r.get("api_no"))
    try: yc = int(float(r.get("year_chunk") or 0))
    except ValueError: yc = 0
    permw[k].append(((r.get("filing_purpose") or "").strip().lower(), yc))

W = []
for r in csv.DictReader(open(REPO + "/data/wells_permian6.csv", encoding="utf-8")):
    if (r.get("county_name") or "").strip() != "Pecos":
        continue
    try: sy = int(float(r["spud_year"])) if r.get("spud_year") not in (None, "") else None
    except ValueError: sy = None
    try: cy_ = int(float(r["completion_year"])) if r.get("completion_year") not in (None, "") else None
    except ValueError: cy_ = None
    try: td = float(r["total_depth"]) if r.get("total_depth") not in (None, "") else None
    except ValueError: td = None
    try: lo = float(r["lon"]); la = float(r["lat"]); mi = miles(lo, la)
    except (TypeError, ValueError): mi = None
    W.append({"k": apikey(r.get("api_no")), "sy": sy, "cy": cy_, "td": td, "mi": mi})

s20 = [w for w in W if w["sy"] is not None and w["sy"] >= 2020]
N = len(s20)
print("Pecos wells with spud_year >= 2020:", N)

# (A) completion_year sanity
have_cy = [w for w in s20 if w["cy"] is not None]
comp_before_spud = sum(1 for w in have_cy if w["cy"] < w["sy"])
comp_pre2015 = sum(1 for w in have_cy if w["cy"] < 2015)
comp_pre2000 = sum(1 for w in have_cy if w["cy"] < 2000)
print("\n(A) completion_year sanity (of %d with a completion_year):" % len(have_cy))
print("  completion BEFORE spud (impossible for a new drill): %d (%.0f%%)" % (comp_before_spud, 100.0*comp_before_spud/max(1,len(have_cy))))
print("  completion < 2015 while 'spud' >= 2020: %d (%.0f%%)" % (comp_pre2015, 100.0*comp_pre2015/max(1,len(have_cy))))
print("  completion < 2000 while 'spud' >= 2020: %d" % comp_pre2000)
print("  s20 wells with NO completion_year: %d" % (N - len(have_cy)))

# (B) permit join
matched = nd = only_recomp = old_perm = 0
for w in s20:
    ps = permw.get(w["k"])
    if not ps:
        continue
    matched += 1
    purposes = [p for p, y in ps]
    yrs = [y for p, y in ps if y]
    if any(p.startswith("new drill") for p in purposes):
        nd += 1
    elif all(("recompl" in p or "reenter" in p or "reclass" in p or "field transfer" in p or p == "") for p in purposes):
        only_recomp += 1
    if yrs and min(yrs) < 2018:
        old_perm += 1
print("\n(B) W-1 permit join (of %d s20 wells, %d matched a permit):" % (N, matched))
print("  has a 'New Drill' permit: %d (%.0f%% of matched)" % (nd, 100.0*nd/max(1,matched)))
print("  only recompletion/reenter/other (no New Drill): %d (%.0f%% of matched)" % (only_recomp, 100.0*only_recomp/max(1,matched)))
print("  has a permit dated before 2018 (=> pre-existing wellbore): %d (%.0f%% of matched)" % (old_perm, 100.0*old_perm/max(1,matched)))

# Genuine new drill subset: completion not absurdly old AND (New Drill permit OR unmatched-but-consistent)
def is_genuine(w):
    if w["cy"] is not None and w["cy"] < 2015:
        return False  # completed long before the claimed 2020+ spud
    ps = permw.get(w["k"])
    if ps:
        purposes = [p for p, y in ps]
        if any(p.startswith("new drill") for p in purposes):
            return True
        if all(("recompl" in p or "reenter" in p or "reclass" in p or "field transfer" in p or p == "") for p in purposes):
            return False
    return True  # no contradicting evidence

gen = [w for w in s20 if is_genuine(w)]
print("\n=== RECOMPUTE on genuine-new-drill subset ===")
print("genuine new-drill wells spud>=2020: %d  (was %d; excluded %d = %.0f%%)" % (len(gen), N, N-len(gen), 100.0*(N-len(gen))/N))
for label, pool in (("ALL spud>=2020", s20), ("GENUINE new-drill", gen)):
    g = [w for w in pool if w["mi"] is not None]
    def r(d): return sum(1 for w in g if w["mi"] <= d)
    sh = sum(1 for w in pool if w["td"] is not None and w["td"] < 3000)
    print("  [%s] n=%d  <=2mi=%d  <=5mi=%d  <=10mi=%d  shallow<3000=%d" % (label, len(pool), r(2), r(5), r(10), sh))
