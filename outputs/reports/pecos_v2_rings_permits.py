import csv, json, math, statistics, collections

REPO = "/home/andreahimmel/lrp-tx-gis"
gj = json.load(open(REPO + "/combined_geoms.geojson", encoding="utf-8"))
feats = gj.get("features", gj if isinstance(gj, list) else [])
caramba = next((f for f in feats if "caramba" in json.dumps(f.get("properties") or {}).lower()), None)
g = caramba["geometry"]
car_rings = [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
pts = [pt for r in car_rings for pt in r]
cx = sum(p[0] for p in pts)/len(pts); cy = sum(p[1] for p in pts)/len(pts)

def pip(lon, lat, ring):
    inside=False; n=len(ring); j=n-1
    for i in range(n):
        xi,yi=ring[i][0],ring[i][1]; xj,yj=ring[j][0],ring[j][1]
        if ((yi>lat)!=(yj>lat)) and (lon<(xj-xi)*(lat-yi)/((yj-yi) or 1e-12)+xi): inside=not inside
        j=i
    return inside
def in_car(lon,lat): return any(pip(lon,lat,r) for r in car_rings)
def miles(lon,lat):
    dlat=(lat-cy)*69.0; dlon=(lon-cx)*69.0*math.cos(math.radians((lat+cy)/2)); return math.hypot(dlat,dlon)

# ---------- WELLS ----------
W=[]
for r in csv.DictReader(open(REPO+"/data/wells_permian6.csv",encoding="utf-8")):
    if (r.get("county_name") or "").strip()!="Pecos": continue
    try: td=float(r["total_depth"]) if r.get("total_depth") not in (None,"") else None
    except: td=None
    try: sy=int(float(r["spud_year"])) if r.get("spud_year") not in (None,"") else None
    except: sy=None
    try: lon=float(r["lon"]); lat=float(r["lat"])
    except: lon=lat=None
    W.append(dict(td=td,sy=sy,plug=(r.get("plug_flag") or "").strip().upper(),lon=lon,lat=lat,
                  mi=(miles(lon,lat) if lon is not None else None)))
SH=3000
print("PECOS wells total=%d  geo=%d  shallow<3000=%d"%(len(W),sum(1 for x in W if x['mi'] is not None),
      sum(1 for x in W if x['td'] is not None and x['td']<SH)))

print("\n=== WELLS — RINGS FROM CARAMBA ===")
for mi in (1,2,5,10,15):
    sel=[x for x in W if x['mi'] is not None and x['mi']<=mi]
    sd=[x for x in sel if x['td'] is not None]
    sh=[x for x in sd if x['td']<SH]
    yrs=sorted(x['sy'] for x in sh if x['sy'])
    print(" <=%2dmi wells=%4d shallow=%3d sh_spud>=2015=%2d sh_spud>=2020=%2d sh_plugged=%3d sh_yr=%s med_depth=%s"
          %(mi,len(sel),len(sh),sum(1 for y in yrs if y>=2015),sum(1 for y in yrs if y>=2020),
            sum(1 for x in sh if x['plug']=='Y'),
            ("%d..%d"%(yrs[0],yrs[-1]) if yrs else "none"),
            ("%.0f"%statistics.median(x['td'] for x in sd) if sd else "NA")))

# county-wide shallow spuds >=2020 and their distance distribution
sh2020=[x for x in W if x['td'] is not None and x['td']<SH and x['sy'] and x['sy']>=2020]
geo2020=[x for x in sh2020 if x['mi'] is not None]
print("\n=== COUNTY-WIDE SHALLOW(<3000) SPUDS >=2020 ===")
print("count=%d  geolocated=%d"%(len(sh2020),len(geo2020)))
for mi in (5,10,15):
    print("  within %2d mi of Caramba: %d"%(mi,sum(1 for x in geo2020 if x['mi']<=mi)))
print("  OUTSIDE 10 mi: %d   OUTSIDE 15 mi: %d"%(sum(1 for x in geo2020 if x['mi']>10),
      sum(1 for x in geo2020 if x['mi']>15)))
d=[x['mi'] for x in geo2020]
print("  nearest such well to Caramba: %.1f mi   median distance: %.0f mi"%(min(d),statistics.median(d)))

# ---------- PERMITS (wellbore_profile) ----------
P=[]
for r in csv.DictReader(open(REPO+"/data/permits_permian6.csv",encoding="utf-8")):
    if (r.get("county_name") or "").strip()!="Pecos": continue
    try: td=float(r["total_depth"]) if r.get("total_depth") not in (None,"") else None
    except: td=None
    try: py=int(float(r["permit_year"])) if r.get("permit_year") not in (None,"") else None
    except: py=None
    try: lon=float(r["lon"]); lat=float(r["lat"])
    except: lon=lat=None
    P.append(dict(td=td,py=py,prof=(r.get("wellbore_profile") or "").strip().lower(),lon=lon,lat=lat,
                  mi=(miles(lon,lat) if lon is not None else None)))
print("\n=== PECOS DRILLING PERMITS — PROFILE x DEPTH ===")
print("total Pecos permits=%d"%len(P))
pd=[x for x in P if x['td'] is not None]
sh=[x for x in pd if x['td']<SH]
dp=[x for x in pd if x['td']>=10000]
print("permits with depth=%d  shallow<3000=%d  deep>=10000=%d"%(len(pd),len(sh),len(dp)))
for lab,grp in (("<3000 ft",sh),(">=10000 ft",dp),("ALL w/depth",pd)):
    v=sum(1 for x in grp if x['prof']=='vertical'); h=sum(1 for x in grp if x['prof']=='horizontal')
    print("  %-12s n=%5d  vertical=%5d (%.1f%%)  horizontal=%5d (%.1f%%)"
          %(lab,len(grp),v,100*v/max(1,len(grp)),h,100*h/max(1,len(grp))))
hz=[x['td'] for x in pd if x['prof']=='horizontal']
vt=[x['td'] for x in pd if x['prof']=='vertical']
print("  median depth: horizontal=%.0f ft  vertical=%.0f ft"%(statistics.median(hz),statistics.median(vt)))
print("  horizontal permits with depth <3000 ft: %d (%.2f%% of horizontals)"
      %(sum(1 for x in pd if x['prof']=='horizontal' and x['td']<SH),
        100*sum(1 for x in pd if x['prof']=='horizontal' and x['td']<SH)/max(1,len(hz))))

print("\n=== PERMITS NEAR CARAMBA (profile/depth/recency) ===")
for mi in (5,10,15):
    sel=[x for x in P if x['mi'] is not None and x['mi']<=mi]
    seld=[x for x in sel if x['td'] is not None]
    shv=[x for x in seld if x['td']<SH and x['prof']=='vertical']
    shh=[x for x in seld if x['td']<SH and x['prof']=='horizontal']
    rec=[x for x in sel if x['py'] and x['py']>=2020]
    recsh=[x for x in rec if x['td'] is not None and x['td']<SH]
    print(" <=%2dmi permits=%4d  shallow_vert=%3d  shallow_horiz=%3d  permits>=2020=%4d  shallow_permits>=2020=%2d"
          %(mi,len(sel),len(shv),len(shh),len(rec),len(recsh)))
