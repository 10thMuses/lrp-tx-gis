import csv, json, math

REPO = "/home/andreahimmel/lrp-tx-gis"
gj = json.load(open(REPO + "/combined_geoms.geojson", encoding="utf-8"))
feats = gj.get("features", gj if isinstance(gj, list) else [])
caramba = next((f for f in feats if "caramba" in json.dumps(f.get("properties") or {}).lower()), None)
g = caramba["geometry"]
car_rings = [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
pts = [pt for r in car_rings for pt in r]
cx = sum(p[0] for p in pts)/len(pts); cy = sum(p[1] for p in pts)/len(pts)

def pip(lon, lat, ring):
    inside = False; n = len(ring); j = n-1
    for i in range(n):
        xi,yi = ring[i][0],ring[i][1]; xj,yj = ring[j][0],ring[j][1]
        if ((yi>lat)!=(yj>lat)) and (lon < (xj-xi)*(lat-yi)/((yj-yi) or 1e-12)+xi): inside = not inside
        j = i
    return inside
def in_car(lon,lat): return any(pip(lon,lat,r) for r in car_rings)
def miles(lon,lat):
    dlat=(lat-cy)*69.0; dlon=(lon-cx)*69.0*math.cos(math.radians((lat+cy)/2)); return math.hypot(dlat,dlon)

rows=[]
with open(REPO+"/data/wells_permian6.csv",encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        if (r.get("county_name") or "").strip()!="Pecos": continue
        try: td=float(r["total_depth"]) if r.get("total_depth") not in (None,"") else None
        except: td=None
        try: sy=int(float(r["spud_year"])) if r.get("spud_year") not in (None,"") else None
        except: sy=None
        try: lon=float(r["lon"]); lat=float(r["lat"])
        except: lon=lat=None
        if lon is None: continue
        rows.append(dict(td=td,sy=sy,plug=(r.get("plug_flag") or "").strip().upper(),
                         og=(r.get("oil_gas") or "").strip().upper(),api=r.get("api_no"),
                         lon=lon,lat=lat,mi=miles(lon,lat),inc=in_car(lon,lat)))

print("WELLS INSIDE CARAMBA TRACT:")
for r in sorted([x for x in rows if x["inc"]],key=lambda x:(x["td"] or 9e9)):
    print("  depth=%s spud=%s plug=%s og=%s api=%s" % (r["td"],r["sy"],r["plug"] or "-",r["og"] or "-",r["api"]))

print("\nALL WELLS <=2 mi (any depth), nearest first:")
for r in sorted([x for x in rows if x["mi"]<=2],key=lambda x:x["mi"]):
    print("  %.2f mi depth=%s spud=%s plug=%s og=%s" % (r["mi"],r["td"],r["sy"],r["plug"] or "-",r["og"] or "-"))

print("\nSHALLOW (<3000) spud>=2015 within 5 mi:")
for r in sorted([x for x in rows if x["td"] is not None and x["td"]<3000 and x["sy"] and x["sy"]>=2015 and x["mi"]<=5],key=lambda x:x["mi"]):
    print("  %.2f mi depth=%.0f spud=%d plug=%s og=%s" % (r["mi"],r["td"],r["sy"],r["plug"] or "-",r["og"] or "-"))

# data completeness: shallow with no spud year
sh=[x for x in rows if x["td"] is not None and x["td"]<3000]
print("\nshallow total(geo)=%d  no-spud-year=%d  active(N/blank)&recent>=2010=%d"
      % (len(sh), sum(1 for x in sh if x["sy"] is None),
         sum(1 for x in sh if x["plug"]!="Y" and x["sy"] and x["sy"]>=2010)))
# nearest ACTIVE shallow + nearest ANY active well
act=[x for x in rows if x["plug"]!="Y"]
acts=[x for x in act if x["td"] is not None and x["td"]<3000]
acts.sort(key=lambda x:x["mi"])
print("nearest ACTIVE shallow wells:", [(round(x['mi'],2),x['td'],x['sy']) for x in acts[:5]])
