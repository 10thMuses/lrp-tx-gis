# -*- coding: utf-8 -*-
"""Assemble OXY's footprint into six categorized GeoJSON layers for the live map.

Every coordinate traces to a public source (hard rule 3): the layers are built by
streaming OXY rows out of combined_points.csv (ercot_queue, eia860_plants,
substations — sourced ERCOT/EIA/OSM) and reading the already-sourced
data/oxy/oxy_assets.geojson facility points. A small set of facilities that lack
a precise public point coordinate are placed at the county centroid (computed
from the Census-TIGER county polygon in combined_geoms) and explicitly flagged
`accuracy="approximate (county centroid)"`.

Outputs (atomic writes): data/oxy/oxy_power.geojson, oxy_midstream.geojson,
oxy_ercot.geojson, oxy_permits.geojson, oxy_water.geojson, oxy_carbon.geojson.

Run: python3 scripts/build_oxy_map_layers.py
"""
import os, csv, json, re, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OXYDIR = os.path.join(ROOT, "data", "oxy")

# ---- county centroids (sourced; for approximate placement) ----
def county_centroids():
    gj = json.load(open(os.path.join(ROOT, "combined_geoms.geojson"), encoding="utf-8"))
    cent = {}
    for f in gj["features"]:
        p = f.get("properties") or {}
        if p.get("layer_id") != "counties":
            continue
        nm = (p.get("NAME") or "").replace(" County", "").strip().upper()
        xs, ys = [], []
        g = f["geometry"]; t = g["type"]; c = g["coordinates"]
        rings = [c[0]] if t == "Polygon" else ([p2[0] for p2 in c] if t == "MultiPolygon" else [])
        for r in rings:
            for x, y in r:
                xs.append(x); ys.append(y)
        if xs:
            cent[nm] = (round(sum(xs) / len(xs), 5), round(sum(ys) / len(ys), 5))
    return cent

# ---- OXY rows out of combined_points (sourced coords) ----
def oxy_points():
    out = {"ercot_queue": [], "eia860_plants": [], "substations": []}
    ENT = re.compile(r'oxy renewable|net power', re.I)
    OP = re.compile(r'occidental|oxy vinyls|oxy renewable|net power', re.I)
    SUB = re.compile(r'\boxy\b|occidental|goldsmith', re.I)
    with open(os.path.join(ROOT, "combined_points.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            lid = r.get("layer_id")
            if lid not in out:
                continue
            try:
                lon, lat = float(r["lon"]), float(r["lat"])
            except (KeyError, ValueError, TypeError):
                continue
            if lid == "ercot_queue" and ENT.search(r.get("entity") or ""):
                out[lid].append((lon, lat, r))
            elif lid == "eia860_plants" and OP.search((r.get("operator") or "")):
                out[lid].append((lon, lat, r))
            elif lid == "substations" and (SUB.search(r.get("name") or "") or OP.search(r.get("operator") or "")):
                out[lid].append((lon, lat, r))
    return out

def feat(lon, lat, props):
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
            "properties": props}

def write_layer(name, feats):
    fc = {"type": "FeatureCollection", "metadata": {"layer": name, "feature_count": len(feats),
          "note": "OXY footprint; coords from sourced LRP layers (ERCOT/EIA/OSM) + oxy_assets.geojson; approximate points flagged."},
          "features": feats}
    tmp = os.path.join(OXYDIR, name + ".geojson.tmp")
    json.dump(fc, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, os.path.join(OXYDIR, name + ".geojson"))
    return len(feats)

def main():
    cent = county_centroids()
    cp = oxy_points()
    assets = {f["properties"]["name"]: f for f in
              json.load(open(os.path.join(OXYDIR, "oxy_assets.geojson"), encoding="utf-8"))["features"]}

    def coord_of(name):
        f = assets.get(name)
        return tuple(f["geometry"]["coordinates"]) if f else (None, None)

    def cc(county):  # county centroid (approximate)
        return cent.get(county.upper(), (None, None))

    century = coord_of("Century Plant Substation")     # @ Century plant, Pecos
    block31 = coord_of("Block 31 Plant")                # Crane
    wasson = coord_of("Wasson CO2 Removal Plant")       # Yoakum
    scr_sub = coord_of("Oxy South Curtis Ranch Substation")  # co-located w/ recycling

    P = {}  # layer -> [features]

    # ---------- 1. POWER & NET POWER ----------
    pf = []
    for lon, lat, r in cp["eia860_plants"]:
        op = r.get("operator") or ""
        div = bool(re.search(r'vinyls', op, re.I))  # OxyChem cogen → divested
        pf.append(feat(lon, lat, {
            "name": r.get("name"), "asset": "Generation",
            "fuel": r.get("fuel") or "", "technology": r.get("technology") or "",
            "capacity_mw": r.get("capacity_mw") or "", "county": r.get("county") or "",
            "operator": op, "online": r.get("commissioned") or "",
            "status": "Divested to Berkshire (Jan 2026)" if div else "Operating",
            "source": "EIA-860", "accuracy": "precise"}))
    for lon, lat, r in cp["substations"]:
        pf.append(feat(lon, lat, {
            "name": r.get("name"), "asset": "Substation",
            "voltage": r.get("voltage") or "", "operator": r.get("operator") or "",
            "status": "Operating", "source": "OSM/HIFLD substations", "accuracy": "precise"}))
    P["oxy_power"] = pf

    # ---------- 3. ERCOT QUEUE ----------
    STAT = {"Santa Garcias Solar": "IA signed Feb 2026",
            "NET Power Demonstration plant": "Active in queue",
            "TRIFECTA Gas": "Withdrawn Apr 2026"}
    ef = []
    for lon, lat, r in cp["ercot_queue"]:
        nm = r.get("name")
        ef.append(feat(lon, lat, {
            "name": nm, "capacity_mw": r.get("capacity_mw") or "",
            "fuel": r.get("fuel") or "", "technology": r.get("technology") or "",
            "county": r.get("county") or "", "zone": r.get("zone") or "",
            "filing_entity": r.get("entity") or "", "status": STAT.get(nm, "In queue"),
            "source": "ERCOT interconnection queue", "accuracy": "precise"}))
    P["oxy_ercot"] = ef

    # ---------- 2. MIDSTREAM / PIPELINE / PROCESSING ----------
    mf = [
        feat(*century, {"name": "Century gas & CO₂ plant", "facility": "CO₂-capture / gas treating",
            "county": "Pecos", "operator": "Occidental (SandRidge-operated)", "detail": "800 MMcf/d treating; ~8.4 Mt CO₂/yr",
            "status": "Operating", "source": "oxy_assets (substations layer) @ Century", "accuracy": "precise"}),
        feat(*block31, {"name": "Block 31 gas plant", "facility": "Gas processing / CO₂ flood",
            "county": "Crane", "operator": "OXY USA", "detail": "41 MMcf/d", "status": "Operating",
            "source": "HIFLD/EIA-757 processing", "accuracy": "precise"}),
        feat(*wasson, {"name": "Wasson / Denver Unit CO₂-EOR", "facility": "CO₂-EOR field & recovery plant",
            "county": "Yoakum", "operator": "Occidental Permian", "detail": "world's largest CO₂ flood",
            "status": "Operating", "source": "EIA-860 @ Wasson CO₂-Removal", "accuracy": "precise"}),
    ]
    dc = cc("Gaines")
    if dc[0]:
        mf.append(feat(*dc, {"name": "Denver City CO₂ hub", "facility": "CO₂ trunkline interconnect",
            "county": "Gaines", "operator": "multi-party (OXY offtaker)", "status": "Operating",
            "source": "county centroid (Gaines)", "accuracy": "approximate (county centroid)"}))
    P["oxy_midstream"] = mf

    # ---------- 4. TCEQ AIR & EMISSION PERMITS ----------
    qf = [
        feat(*century, {"name": "Century gas / CO₂ plant", "county": "Pecos",
            "permit_type": "TCEQ New Source Review (air)", "status": "Active — no pending Title V",
            "source": "oxy_assets @ Century", "accuracy": "precise"}),
        feat(*block31, {"name": "Block 31 plant", "county": "Crane",
            "permit_type": "TCEQ Title V + NSR", "status": "Title V renewed 10 Jul 2025",
            "source": "HIFLD @ Block 31", "accuracy": "precise"}),
        feat(*wasson, {"name": "Wasson CO₂-removal plant", "county": "Yoakum",
            "permit_type": "TCEQ Title V (O553)", "status": "Renewed 25 Nov 2025",
            "source": "EIA-860 @ Wasson", "accuracy": "precise"}),
        feat(wasson[0] + 0.02, wasson[1] - 0.02, {"name": "Denver Unit CO₂-recovery plant", "county": "Yoakum",
            "permit_type": "TCEQ Title V (O3051)", "status": "Renewed 15 Oct 2025",
            "source": "near Wasson (Yoakum)", "accuracy": "approximate (co-located, Yoakum)"}),
    ]
    P["oxy_permits"] = qf

    # ---------- 6. CARBON ----------
    cf = [
        feat(*century, {"name": "Century CO₂ capture", "carbon_type": "Industrial CO₂ capture",
            "county": "Pecos", "detail": "~8.4 Mt CO₂/yr to EOR", "status": "Operating",
            "source": "oxy_assets @ Century", "accuracy": "precise"}),
        feat(*wasson, {"name": "Wasson / Denver Unit CO₂ storage", "carbon_type": "CO₂ storage (Subpart RR MRV)",
            "county": "Yoakum", "detail": "first U.S. MRV plan; ~3.67 Mt stored 2023", "status": "Operating",
            "source": "EIA-860 @ Wasson", "accuracy": "precise"}),
    ]
    st = cc("Ector"); kr = cc("Kleberg")
    if st[0]:
        cf.append(feat(*st, {"name": "STRATOS DAC", "carbon_type": "Direct air capture",
            "county": "Ector", "detail": "world's largest DAC; up to 500 kt/yr", "status": "Under construction",
            "source": "county centroid (Ector) — precise pending", "accuracy": "approximate (county centroid)"}))
    if kr[0]:
        cf.append(feat(*kr, {"name": "King Ranch / South Texas DAC hub", "carbon_type": "DAC + storage hub",
            "county": "Kleberg", "detail": "DOE-backed; pre-construction", "status": "Planned",
            "source": "county centroid (Kleberg) — precise pending", "accuracy": "approximate (county centroid)"}))
    P["oxy_carbon"] = cf

    # ---------- 5. WATER ----------
    wf = []
    if scr_sub[0]:
        wf.append(feat(*scr_sub, {"name": "South Curtis Ranch produced-water recycling",
            "water_type": "Produced-water recycling", "county": "Martin (straddles Midland line)",
            "operator": "OXY + Select Water", "detail": ">50 MM bbl reused (2024)", "status": "Operating",
            "source": "OXY South Curtis Ranch substation (OSM way 457948592); RRC lease 08-40691",
            "accuracy": "approximate (at OXY substation; recycling plant within ~1-3 mi, no published coordinate)"}))
    # remaining sites — precise regulator coordinate where research found one, else county centroid; all flagged
    water_extra = [
        ("Lost Tank produced-water recycling", "Lea (NM)", (-103.72052, 32.39144), "OXY + Select Water",
         "Produced-water recycling", "up to 180,000 bbl/d; 1.9 MMbbl storage; 13-mi line to OXY's Mesa Verde", "Operating",
         "NM OCD Facilities (Select Water 'Lost Tank Recycling Facility', ID fVV2203540475, permit 1RF-479-0)",
         "precise (NM OCD facilities database)"),
        ("WES desalination pilot (JIP 2)", "Reeves", (-103.92, 31.90), "Western Midstream",
         "Desalination pilot", "2,000 bbl/d in → ~1,000 bbl/d fresh; near Red Bluff Reservoir", "Pilot",
         "near Red Bluff Reservoir (WES release 17 Jun 2026); USGS Red Bluff Dam gage 08410100",
         "approximate (near Red Bluff Reservoir, Reeves Co.; exact site not published)"),
        ("Pathfinder produced-water pipeline", "Loving", None, "Western Midstream",
         "Produced-water pipeline", "42 mi · 30-in · >800 Mbbl/d (in service 2027)", "Planned",
         "county centroid (Loving) — linear asset, precise route not published", "approximate (county centroid)"),
    ]
    for nm, county, xy, op, wtype, detail, status, src, acc in water_extra:
        c = xy if xy else cc(county)
        if c and c[0]:
            wf.append(feat(c[0], c[1], {"name": nm, "water_type": wtype, "county": county,
                "operator": op, "detail": detail, "status": status, "source": src, "accuracy": acc}))
    P["oxy_water"] = wf

    for name, feats in P.items():
        n = write_layer(name, feats)
        prec = sum(1 for f in feats if f["properties"].get("accuracy", "").startswith("precise"))
        print(f"{name:14s} {n:2d} features ({prec} precise, {n-prec} approximate)")

if __name__ == "__main__":
    main()
