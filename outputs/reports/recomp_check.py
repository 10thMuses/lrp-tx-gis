"""Does excluding recompletions change things?
(1) W-1 Pecos >=2020: filing_purpose distribution overall + top operators.
(2) Wells spudded >=2020 (dbo900) joined by API to W-1 filing_purpose:
    are spud-based counts new-drills, or contaminated by recompletions?
(3) Re-derive proximity + shallow numbers for NEW-DRILL-only."""
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

# ---- (1) W-1 filing_purpose ----
purp_all = collections.Counter()
op_purp = collections.defaultdict(collections.Counter)
# api -> set of purposes (any New Drill?)
api_purposes = collections.defaultdict(set)
for r in csv.DictReader(open(REPO + "/outputs/refresh/rrc_w1_permits.csv", encoding="utf-8", errors="replace")):
    if (r.get("county_name") or "").strip().upper() != "PECOS":
        continue
    try:
        yc = int(float(r.get("year_chunk") or 0))
    except ValueError:
        yc = 0
    fp = (r.get("filing_purpose") or "").strip()
    k = apikey(r.get("api_no"))
    if k:
        api_purposes[k].add(fp.lower())
    if yc < 2020:
        continue
    purp_all[fp or "(blank)"] += 1
    op_purp[(r.get("operator_name") or "").strip()][fp or "(blank)"] += 1

tot = sum(purp_all.values())
print("=== W-1 Pecos permits >=2020: filing_purpose (n=%d) ===" % tot)
for p, c in purp_all.most_common():
    print("  %-28s %5d  %5.1f%%" % (p, c, 100.0*c/tot))

print("\n=== filing_purpose split for top operators (>=2020) ===")
for o, _ in collections.Counter({k: sum(v.values()) for k, v in op_purp.items()}).most_common(6):
    s = op_purp[o]; t = sum(s.values())
    nd = sum(v for k, v in s.items() if "new" in k.lower())
    rc = sum(v for k, v in s.items() if "recomp" in k.lower() or "re-comp" in k.lower())
    re_ = sum(v for k, v in s.items() if "enter" in k.lower())
    print("  %-30s tot=%4d  NewDrill=%4d  Recomp=%4d  Reenter=%4d  other=%d"
          % (o[:30], t, nd, rc, re_, t-nd-rc-re_))

def is_newdrill(k):
    ps = api_purposes.get(k, set())
    if not ps: return None  # unmatched
    return any("new" in p for p in ps)

# ---- (2)/(3) wells spudded >=2020 joined to purpose ----
cls = collections.Counter()
tot20 = nd20 = 0
near2 = near10 = nd_near2 = nd_near10 = 0
sh = nd_sh = 0
for r in csv.DictReader(open(REPO + "/data/wells_permian6.csv", encoding="utf-8")):
    if (r.get("county_name") or "").strip() != "Pecos":
        continue
    try:
        sy = int(float(r["spud_year"])) if r.get("spud_year") not in (None, "") else None
    except ValueError:
        sy = None
    if sy is None or sy < 2020:
        continue
    tot20 += 1
    k = apikey(r.get("api_no"))
    nd = is_newdrill(k)
    cls["new-drill" if nd else ("recomp/other-only" if nd is False else "unmatched")] += 1
    try:
        td = float(r["total_depth"]) if r.get("total_depth") not in (None, "") else None
    except ValueError:
        td = None
    try:
        d = miles(float(r["lon"]), float(r["lat"]))
    except (TypeError, ValueError):
        d = None
    isnd = (nd is True)
    if isnd:
        nd20 += 1
    if td is not None and td < 3000:
        sh += 1
        if isnd: nd_sh += 1
    if d is not None and d <= 2:
        near2 += 1
        if isnd: nd_near2 += 1
    if d is not None and d <= 10:
        near10 += 1
        if isnd: nd_near10 += 1

print("\n=== Wells with dbo900 spud_year >=2020 (Pecos), classified via W-1 permit purpose ===")
for kk, v in cls.most_common():
    print("  %-20s %4d  (%4.1f%%)" % (kk, v, 100.0*v/tot20))
print("\nProximity / depth: ALL spud>=2020  vs  NEW-DRILL-only")
print("  total          : %4d  ->  %4d" % (tot20, nd20))
print("  within 2 mi    : %4d  ->  %4d" % (near2, nd_near2))
print("  within 10 mi   : %4d  ->  %4d" % (near10, nd_near10))
print("  shallow <3000  : %4d  ->  %4d" % (sh, nd_sh))
