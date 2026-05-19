"""Canonical reconciliation: reproduce the user's corrected memo numbers from
RRC data, and emit the per-API new-drill classification used to filter the map.

Definition (matches memo): a Pecos wellbore is a GENUINE NEW DRILL iff the RRC
W-1 permit record carries filing_purpose 'New Drill' for that API. Recompletions
and re-entries are excluded."""
import csv, collections, json, math, re, statistics

REPO = "/home/andreahimmel/lrp-tx-gis"

def apikey(s):
    d = re.sub(r"\D", "", s or "")
    return d[-8:] if len(d) >= 8 else d

# Caramba centroid
gj = json.load(open(REPO + "/combined_geoms.geojson", encoding="utf-8"))
feats = gj.get("features", gj)
car = next(f for f in feats if "caramba" in json.dumps(f.get("properties") or {}).lower())
g = car["geometry"]; rings = [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
pts = [p for r in rings for p in r]; cx = sum(p[0] for p in pts)/len(pts); cy = sum(p[1] for p in pts)/len(pts)
def miles(lo, la): return math.hypot((la-cy)*69.0, (lo-cx)*69.0*math.cos(math.radians((la+cy)/2)))

# ---- A. Pecos W-1 permits since 2020: New Drill vs Recompletion ----
permits = []
for r in csv.DictReader(open(REPO + "/outputs/refresh/rrc_w1_permits.csv", encoding="utf-8", errors="replace")):
    if (r.get("county_name") or "").strip().upper() != "PECOS":
        continue
    try: yc = int(float(r.get("year_chunk") or 0))
    except ValueError: yc = 0
    if yc < 2020:
        continue
    permits.append({
        "api": apikey(r.get("api_no")),
        "purpose": (r.get("filing_purpose") or "").strip().lower(),
        "op": (r.get("operator_name") or "").strip(),
    })
P = len(permits)
nd = [p for p in permits if p["purpose"].startswith("new drill")]
rc = [p for p in permits if "recompl" in p["purpose"]]
oth = [p for p in permits if p not in nd and p not in rc]
print("=== A. Pecos W-1 permits since 2020 ===")
print("total=%d  NewDrill=%d (%.1f%%)  Recompletion=%d (%.1f%%)  other=%d" %
      (P, len(nd), 100.0*len(nd)/P, len(rc), 100.0*len(rc)/P, len(oth)))
km = sum(1 for p in rc if p["op"].upper().startswith("KINDER MORGAN"))
print("Recompletions by Kinder Morgan: %d / %d = %.1f%%" % (km, len(rc), 100.0*km/max(1, len(rc))))
nd_ops = collections.Counter(p["op"] for p in nd)
print("New-drill operators (top 6 of %d permits):" % len(nd))
for o, c in nd_ops.most_common(6):
    print("  %4d  %5.1f%%  %s" % (c, 100.0*c/len(nd), o))

# set of APIs that have a New Drill permit (genuine new drill)
nd_apis = {p["api"] for p in nd if p["api"]}
rc_apis = {p["api"] for p in rc if p["api"]}

# ---- B. Join to wells (Pecos) ----
wells = []
for r in csv.DictReader(open(REPO + "/data/wells_permian6.csv", encoding="utf-8")):
    if (r.get("county_name") or "").strip() != "Pecos":
        continue
    try: sy = int(float(r["spud_year"])) if r.get("spud_year") not in (None, "") else None
    except ValueError: sy = None
    try: td = float(r["total_depth"]) if r.get("total_depth") not in (None, "") else None
    except ValueError: td = None
    try: lo = float(r["lon"]); la = float(r["lat"]); mi = miles(lo, la)
    except (TypeError, ValueError): mi = None
    wells.append({"api": apikey(r.get("api_no")), "sy": sy, "td": td, "mi": mi})

nd_wells = [w for w in wells if w["api"] in nd_apis and w["sy"] is not None and w["sy"] >= 2020]
print("\n=== B. Genuine NEW-DRILL wells (NewDrill permit) spud_year>=2020, Pecos ===")
print("count=%d" % len(nd_wells))
wd = [w for w in nd_wells if w["td"] is not None]
deep = sum(1 for w in wd if w["td"] >= 3000); sh = sum(1 for w in wd if w["td"] < 3000)
print("  with depth=%d  deep>=3000=%d (%.1f%%)  shallow<3000=%d" %
      (len(wd), deep, 100.0*deep/max(1, len(wd)), sh))
geo = [w for w in nd_wells if w["mi"] is not None]
for d in (2, 5, 10):
    print("  within %2d mi: %d" % (d, sum(1 for w in geo if w["mi"] <= d)))
near10 = sorted((w for w in geo if w["mi"] <= 10), key=lambda w: w["mi"])
print("  the within-10mi new-drill wells:")
for w in near10:
    print("    %.2f mi  spud=%s  depth=%s" % (w["mi"], w["sy"], w["td"]))
if geo:
    print("  nearest new-drill well: %.2f mi" % min(w["mi"] for w in geo))

# ---- C. wells-CSV-only heuristic for the MAP filter (county-uniform) ----
print("\n=== C. MAP filter heuristic (completion vs spud), all 6 counties ===")
rows = list(csv.DictReader(open(REPO + "/data/wells_permian6.csv", encoding="utf-8")))
def parse_int(v):
    try: return int(float(v))
    except (TypeError, ValueError): return None
by_cty = collections.Counter(); drop_by_cty = collections.Counter()
agree = dis = 0
for r in rows:
    c = (r.get("county_name") or "").strip()
    by_cty[c] += 1
    sy = parse_int(r.get("spud_year")); cyr = parse_int(r.get("completion_year"))
    # heuristic recompletion/re-stamp: completion strictly before spud (impossible for new drill)
    is_restamp = (sy is not None and cyr is not None and cyr < sy)
    if is_restamp:
        drop_by_cty[c] += 1
    # agreement vs W-1 NewDrill flag (Pecos only, spud>=2020)
    if c == "Pecos" and sy is not None and sy >= 2020:
        k = apikey(r.get("api_no"))
        wnd = k in nd_apis
        hkeep = not is_restamp
        if wnd == hkeep: agree += 1
        else: dis += 1
print("rows total=%d" % len(rows))
for c in ["Pecos", "Reeves", "Ward", "Midland", "Martin", "Reagan"]:
    print("  %-8s total=%6d  completion<spud (re-stamp) =%5d (%.1f%%)" %
          (c, by_cty[c], drop_by_cty[c], 100.0*drop_by_cty[c]/max(1, by_cty[c])))
print("Pecos spud>=2020: heuristic(keep if completion>=spud or no completion) vs W-1 NewDrill -> agree=%d disagree=%d (%.0f%% agree)"
      % (agree, dis, 100.0*agree/max(1, agree+dis)))
