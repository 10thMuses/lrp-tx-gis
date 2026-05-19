"""Two candidate canonical 'genuine new drill' rules, exact numbers, so the
memo + map can standardize on one reproducible definition.

RULE H (well-level, buyer-reproducible from the public wells file alone, county-
uniform, also powers the map filter): a wellbore is a genuine new drill iff
completion_year is blank OR completion_year >= spud_year (i.e., not an old well
re-stamped with a recent spud date by recompletion/re-entry).

RULE W (authoritative but Pecos-only, needs our W-1 scrape): API has a W-1
'New Drill' filing purpose."""
import csv, json, math, re, collections

REPO = "/home/andreahimmel/lrp-tx-gis"
def apikey(s):
    d = re.sub(r"\D", "", s or ""); return d[-8:] if len(d) >= 8 else d
gj = json.load(open(REPO + "/combined_geoms.geojson", encoding="utf-8")); feats = gj.get("features", gj)
car = next(f for f in feats if "caramba" in json.dumps(f.get("properties") or {}).lower())
g = car["geometry"]; rg = [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
pp = [p for r in rg for p in r]; cx = sum(p[0] for p in pp)/len(pp); cy = sum(p[1] for p in pp)/len(pp)
def miles(lo, la): return math.hypot((la-cy)*69.0, (lo-cx)*69.0*math.cos(math.radians((la+cy)/2)))

def pint(v):
    try: return int(float(v))
    except (TypeError, ValueError): return None

rows = list(csv.DictReader(open(REPO + "/data/wells_permian6.csv", encoding="utf-8")))

def ruleH(r):
    sy = pint(r.get("spud_year")); cyr = pint(r.get("completion_year"))
    if sy is None: return False
    return cyr is None or cyr >= sy   # keep = genuine new drill

print("=== RULE H (completion>=spud or blank), all 6 counties ===")
for c in ["Pecos", "Reeves", "Ward", "Midland", "Martin", "Reagan"]:
    cr = [r for r in rows if (r.get("county_name") or "").strip() == c]
    keep = [r for r in cr if ruleH(r)]
    print("  %-8s total=%6d  keep(new-drill)=%6d  dropped(recompletion/re-stamp)=%6d (%.1f%%)"
          % (c, len(cr), len(keep), len(cr)-len(keep), 100.0*(len(cr)-len(keep))/max(1, len(cr))))

pe = [r for r in rows if (r.get("county_name") or "").strip() == "Pecos"]
def stats(label, pool):
    s20 = [r for r in pool if (pint(r.get("spud_year")) or 0) >= 2020]
    def mi(r):
        try: return miles(float(r["lon"]), float(r["lat"]))
        except (TypeError, ValueError): return None
    g = [(mi(r), r) for r in s20 if mi(r) is not None]
    def ring(d): return sum(1 for m, _ in g if m <= d)
    sh = sum(1 for r in s20 if (lambda t: t is not None and t < 3000)(_to(r)))
    near = sorted([m for m, _ in g])
    print("  [%s] Pecos spud>=2020 n=%d  <=2mi=%d  <=5mi=%d  <=10mi=%d  shallow<3000=%d  nearest=%s"
          % (label, len(s20), ring(2), ring(5), ring(10), sh,
             ("%.2f" % near[0]) if near else "n/a"))
    w10 = sorted([(m, r) for m, r in g if m <= 10])
    for m, r in w10:
        print("      %.2f mi  spud=%s depth=%s completion=%s" %
              (m, r.get("spud_year"), r.get("total_depth"), r.get("completion_year")))

def _to(r):
    try: return float(r["total_depth"]) if r.get("total_depth") not in (None, "") else None
    except ValueError: return None

print("\n=== Pecos new-drill proximity under each rule ===")
stats("ALL spud>=2020 (no exclusion)", pe)
stats("RULE H new-drill", [r for r in pe if ruleH(r)])

# RULE W
nd_apis = set()
for r in csv.DictReader(open(REPO + "/outputs/refresh/rrc_w1_permits.csv", encoding="utf-8", errors="replace")):
    if (r.get("county_name") or "").strip().upper() == "PECOS" and (r.get("filing_purpose") or "").strip().lower().startswith("new drill"):
        k = apikey(r.get("api_no"))
        if k: nd_apis.add(k)
stats("RULE W (W-1 New Drill API)", [r for r in pe if apikey(r.get("api_no")) in nd_apis])
