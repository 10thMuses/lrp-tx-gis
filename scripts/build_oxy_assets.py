"""Build data/oxy/oxy_assets.geojson — a curated OXY/Occidental footprint overlay
for the Caramba North / OXY partnership view.

Every coordinate is EXTRACTED from an existing, already-sourced layer in this repo
(combined_points.csv rows from ERCOT/EIA-860/OSM; data/hifld/hifld_ng_processing.geojson
from EIA-757). No coordinate or feature value is hand-coded — only the editorial
category/relevance labels are added here (same pattern as layer descriptions in
layers.yaml). Atomic write via os.replace.

Run: python3 scripts/build_oxy_assets.py
"""
import csv, json, os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PTS = os.path.join(ROOT, "combined_points.csv")
HIFLD = os.path.join(ROOT, "data", "hifld", "hifld_ng_processing.geojson")
OUT = os.path.join(ROOT, "data", "oxy", "oxy_assets.geojson")

# Curated assets: (source_layer_id, name-match, exact?, category, relevance note).
# name-match is compared case-insensitively; exact=False => substring.
SPECS = [
    ("substations", "Century Plant Substation", True, "Substation (OXY-operated)",
     "138 kV substation at OXY's Century cryogenic gas/CO2 plant — OXY grid infrastructure in Pecos County."),
    ("substations", "Oxy Cogdell Substation", True, "Substation (OXY-operated)",
     "OXY-operated 69 kV substation; Cogdell/Kelly-Snyder CO2-EOR area."),
    ("substations", "OXY North Cowden Substation", True, "Substation (OXY field)",
     "138 kV; North Cowden Unit (Ector Co.) OXY field operations."),
    ("substations", "Oxy South Curtis Ranch Substation", True, "Substation (OXY field)",
     "138 kV; co-located with OXY's South Curtis Ranch produced-water recycling facility."),
    ("substations", "Oxy Welch Substation", True, "Substation (OXY field)",
     "69 kV; OXY Welch field operations."),
    ("solar", "Goldsmith", False, "Solar — operating (OXY)",
     "Oxy Renewable Energy Goldsmith solar farm (Ector Co.) powering OXY Permian operations."),
    ("eia860_plants", "Wasson CO2 Removal Plant", True, "Gas turbine / CO2-EOR (CCS lineage)",
     "Occidental Permian Ltd — Wasson/Denver Unit CO2-EOR, the franchise behind OXY's CCS credibility."),
    ("ercot_queue", "Santa Garcias Solar", True, "Solar — ERCOT queue (OXY)",
     "265 MW solar, developer Oxy Renewable Energy LLC (Kleberg Co.) — co-located with the 1PointFive South Texas DAC hub."),
]

def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def main():
    feats = []
    seen = set()
    # --- points from combined_points.csv ---
    with open(PTS, encoding="utf-8", errors="replace") as f:
        rows = list(csv.DictReader(f))
    for layer_id, nm, exact, category, note in SPECS:
        hit = None
        for r in rows:
            if (r.get("layer_id") or "").strip() != layer_id:
                continue
            name = (r.get("name") or "").strip()
            ok = (name.lower() == nm.lower()) if exact else (nm.lower() in name.lower())
            if ok:
                hit = r
                break
        if not hit:
            print(f"WARN: no match for {layer_id} / {nm!r}", file=sys.stderr)
            continue
        lat, lon = num(hit.get("lat")), num(hit.get("lon"))
        if lat is None or lon is None:
            print(f"WARN: {nm} matched but missing coords", file=sys.stderr)
            continue
        key = (round(lat, 5), round(lon, 5))
        if key in seen:
            continue
        seen.add(key)
        props = {
            "name": (hit.get("name") or "").strip(),
            "category": category,
            "operator": (hit.get("operator") or hit.get("entity") or "").strip() or "Occidental (OXY)",
            "county": (hit.get("county") or "").strip(),
            "capacity_mw": (hit.get("capacity_mw") or hit.get("mw") or "").strip(),
            "detail": (hit.get("voltage") or "").strip(),
            "source_layer": layer_id,
            "source": "LRP map layer (ERCOT/EIA-860/OSM) — see ARCHITECTURE.md",
            "relevance": note,
        }
        feats.append({"type": "Feature",
                      "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
                      "properties": props})

    # --- Block 31 gas plant from HIFLD/EIA NG-processing ---
    with open(HIFLD, encoding="utf-8") as f:
        gj = json.load(f)
    for ft in gj.get("features", []):
        p = ft.get("properties") or {}
        if "block 31" in str(p.get("Plant_Name", "")).lower() and "oxy" in str(p.get("Owner", "")).lower():
            lon, lat = ft["geometry"]["coordinates"][:2]
            feats.append({"type": "Feature",
                          "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
                          "properties": {
                              "name": p.get("Plant_Name", "Block 31 Plant"),
                              "category": "Gas processing (OXY)",
                              "operator": "Oxy",
                              "county": p.get("County", "Crane"),
                              "capacity_mw": "",
                              "detail": f"{p.get('Cap_MMcfd','')} MMcfd",
                              "source_layer": "hifld_ng_processing",
                              "source": "HIFLD/EIA-757 Natural Gas Processing Plant Survey",
                              "relevance": "OXY-owned gas processing plant in Crane County, abutting Pecos.",
                          }})
            break

    fc = {"type": "FeatureCollection",
          "metadata": {"layer": "oxy_assets",
                       "note": "Curated OXY/Occidental footprint; coordinates extracted from existing sourced LRP map layers.",
                       "feature_count": len(feats)},
          "features": feats}

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(OUT), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fout:
        json.dump(fc, fout, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    print(f"wrote {OUT} with {len(feats)} features")
    for ft in feats:
        c = ft["properties"]
        print(f"  - {c['name']} | {c['category']} | {c.get('county','')} | {ft['geometry']['coordinates']}")

if __name__ == "__main__":
    main()
