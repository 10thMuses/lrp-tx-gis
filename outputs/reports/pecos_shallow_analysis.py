import csv, json, math, statistics, collections

REPO = "/home/andreahimmel/lrp-tx-gis"

# ---- 1. Caramba North polygon + centroid ---------------------------------
gj = json.load(open(REPO + "/combined_geoms.geojson", encoding="utf-8"))
feats = gj.get("features", gj if isinstance(gj, list) else [])
caramba = None
for f in feats:
    p = f.get("properties") or {}
    blob = json.dumps(p).lower()
    if "caramba" in blob:
        caramba = f
        break

def rings(geom):
    if not geom:
        return []
    t = geom.get("type"); c = geom.get("coordinates")
    if t == "Polygon":
        return [c[0]]
    if t == "MultiPolygon":
        return [poly[0] for poly in c]
    return []

car_rings = rings(caramba.get("geometry")) if caramba else []
pts = [pt for r in car_rings for pt in r]
cx = sum(p[0] for p in pts) / len(pts)
cy = sum(p[1] for p in pts) / len(pts)
print("Caramba feature found:", bool(caramba), "centroid=(%.5f, %.5f)" % (cx, cy),
      "rings=", len(car_rings), "verts=", len(pts))

def pip(lon, lat, ring):
    inside = False
    n = len(ring); j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi):
            inside = not inside
        j = i
    return inside

def in_caramba(lon, lat):
    return any(pip(lon, lat, r) for r in car_rings)

def miles(lon, lat):
    dlat = (lat - cy) * 69.0
    dlon = (lon - cx) * 69.0 * math.cos(math.radians((lat + cy) / 2))
    return math.hypot(dlat, dlon)

# ---- 2. Load Pecos wells -------------------------------------------------
rows = []
with open(REPO + "/data/wells_permian6.csv", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        if (r.get("county_name") or "").strip() != "Pecos":
            continue
        try:
            td = float(r["total_depth"]) if r.get("total_depth") not in (None, "") else None
        except ValueError:
            td = None
        try:
            sy = int(float(r["spud_year"])) if r.get("spud_year") not in (None, "") else None
        except ValueError:
            sy = None
        try:
            lon = float(r["lon"]); lat = float(r["lat"])
        except (ValueError, TypeError):
            lon = lat = None
        rows.append({"td": td, "sy": sy, "plug": (r.get("plug_flag") or "").strip().upper(),
                     "og": (r.get("oil_gas") or "").strip().upper(),
                     "role": (r.get("county_role") or "").strip(),
                     "lon": lon, "lat": lat})

n_all = len(rows)
SH = 3000
shallow = [r for r in rows if r["td"] is not None and r["td"] < SH]
with_depth = [r for r in rows if r["td"] is not None]
print("\n=== PECOS COUNTY WELLS ===")
print("total Pecos wells:", n_all)
print("with a recorded total depth:", len(with_depth))
print("shallow (<%d ft):" % SH, len(shallow),
      "= %.1f%% of depth-recorded" % (100*len(shallow)/max(1,len(with_depth))))
print("very shallow (<2000 ft):", sum(1 for r in with_depth if r["td"] < 2000))
print("<=3000 ft:", sum(1 for r in with_depth if r["td"] <= 3000))

# ---- 3. Shallow drilling over time (era) ---------------------------------
def era(y):
    if y is None: return "unknown"
    if y < 1974: return "pre-1974"
    if y < 1984: return "1974-1983"
    if y < 1994: return "1984-1993"
    if y < 2000: return "1994-1999"
    if y < 2005: return "2000-2004"
    if y < 2010: return "2005-2009"
    if y < 2015: return "2010-2014"
    if y < 2020: return "2015-2019"
    return "2020+"

order = ["pre-1974","1974-1983","1984-1993","1994-1999","2000-2004","2005-2009","2010-2014","2015-2019","2020+","unknown"]
sh_era = collections.Counter(era(r["sy"]) for r in shallow)
print("\n=== SHALLOW (<%d ft) PECOS SPUDS BY ERA ===" % SH)
for k in order:
    if sh_era.get(k): print("  %-10s %5d" % (k, sh_era[k]))
yrs = [r["sy"] for r in shallow if r["sy"] is not None]
print("most-recent shallow spud year:", max(yrs) if yrs else None)
for cut in (2000, 2010, 2015, 2020, 2024):
    print("  shallow spudded >= %d:" % cut, sum(1 for y in yrs if y >= cut))

# ---- 4. Plug status of shallow ------------------------------------------
sh_plug = collections.Counter(r["plug"] for r in shallow)
print("\n=== SHALLOW PECOS PLUG STATUS ===")
print("  plugged/abandoned (Y):", sh_plug.get("Y", 0),
      "= %.1f%%" % (100*sh_plug.get("Y",0)/max(1,len(shallow))))
print("  active/other (N/blank):", len(shallow) - sh_plug.get("Y", 0))

# ---- 5. Modern Pecos drilling depth profile ------------------------------
print("\n=== PECOS DRILLING DEPTH PROFILE BY ERA (is modern drilling shallow?) ===")
for k in order:
    grp = [r for r in with_depth if era(r["sy"]) == k]
    if not grp: continue
    md = statistics.median(r["td"] for r in grp)
    sh = sum(1 for r in grp if r["td"] < SH)
    deep = sum(1 for r in grp if r["td"] >= 10000)
    print("  %-10s n=%5d  median_depth=%6.0f ft  <%d=%4.1f%%  >=10k=%4.1f%%"
          % (k, len(grp), md, SH, 100*sh/len(grp), 100*deep/len(grp)))

# ---- 6. Proximity to Caramba --------------------------------------------
geo = [r for r in rows if r["lon"] is not None]
def ring_stats(maxmi):
    sel = [r for r in geo if miles(r["lon"], r["lat"]) <= maxmi]
    seld = [r for r in sel if r["td"] is not None]
    shal = [r for r in seld if r["td"] < SH]
    shal_recent = [r for r in shal if r["sy"] and r["sy"] >= 2015]
    shal_plug = sum(1 for r in shal if r["plug"] == "Y")
    md = statistics.median(r["td"] for r in seld) if seld else None
    return dict(n=len(sel), withd=len(seld), shallow=len(shal),
                shallow_recent2015=len(shal_recent), shallow_plugged=shal_plug,
                median_depth=md,
                shallow_years=sorted(set(r["sy"] for r in shal if r["sy"])) )

print("\n=== PROXIMITY TO CARAMBA NORTH (data-center site) ===")
inpoly = [r for r in geo if in_caramba(r["lon"], r["lat"])]
ip_d = [r for r in inpoly if r["td"] is not None]
print("wells INSIDE the Caramba tract:", len(inpoly),
      " of which <%d ft: %d" % (SH, sum(1 for r in ip_d if r["td"] < SH)),
      " depths:", sorted(round(r["td"]) for r in ip_d) if ip_d else [])
for mi in (1, 2, 5, 10):
    s = ring_stats(mi)
    yrs = s["shallow_years"]
    print(" <= %2d mi: wells=%4d  shallow<%d=%3d  shallow_spud>=2015=%2d  shallow_plugged=%3d  median_depth=%s  shallow_yrs[min..max]=%s"
          % (mi, s["n"], SH, s["shallow"], s["shallow_recent2015"], s["shallow_plugged"],
             ("%.0f" % s["median_depth"]) if s["median_depth"] else "NA",
             ("%d..%d" % (yrs[0], yrs[-1])) if yrs else "none"))

# nearest shallow well to Caramba
shg = [(miles(r["lon"], r["lat"]), r) for r in geo if r["td"] is not None and r["td"] < SH]
shg.sort(key=lambda t: t[0])
print("\nNearest shallow (<%d ft) wells to Caramba centroid:" % SH)
for dmi, r in shg[:8]:
    print("  %.2f mi  depth=%5.0f ft  spud=%s  plug=%s  oilgas=%s"
          % (dmi, r["td"], r["sy"], r["plug"] or "-", r["og"] or "-"))
# recency of any shallow within 5 mi
near5 = [r for r in geo if r["td"] is not None and r["td"] < SH and miles(r["lon"], r["lat"]) <= 5]
ny = sorted(r["sy"] for r in near5 if r["sy"])
print("shallow <=5 mi count=%d  spud-year range=%s  spud>=2010=%d  spud>=2020=%d"
      % (len(near5), ("%d..%d" % (ny[0], ny[-1]) if ny else "none"),
         sum(1 for y in ny if y >= 2010), sum(1 for y in ny if y >= 2020)))
