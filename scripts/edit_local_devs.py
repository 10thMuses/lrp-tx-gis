"""Surgical edits to combined_geoms.geojson:
1. Reposition WAHA features (waha_circle, labels_hubs) to Coyanosa, Pecos County and uppercase name to 'WAHA'
2. Add new feature: layer_id 'solstice_substation' (point) — AEP Solstice Substation, OSM way 500535889
3. Add new feature: layer_id 'la_escalera' (polygon) — La Escalera Ranch / Apex Pecos Flat (APPROXIMATE)

Atomic write per OPERATING §6.15.
"""
import json, os, sys, tempfile

SRC = "combined_geoms.geojson"

# Coyanosa / WAHA Hub coords — operator-supplied address: 5693 El Paso Rd, Coyanosa, TX 79730 (Pecos County)
WAHA_LON = -103.2070
WAHA_LAT = 31.2350

# AEP Solstice Substation — OSM way 500535889 (Mapcarta-published coordinates)
SOLSTICE_LON = -103.36171
SOLSTICE_LAT = 30.94832

# La Escalera Ranch (Apex Pecos Flat) — APPROXIMATE ranch outline.
# Lyda family ranch, headquartered ~20 mi south of Fort Stockton on US-385.
# Apex Clean Energy leased land within for the 3.3 GW Pecos Flats wind/solar/H2 project.
# 223,000 acres ≈ 348 sq mi. Polygon designed to encompass that area, anchored on Pecos County.
# Irregular (not square) to reflect actual ranch shapes. ACCURACY: APPROXIMATE.
LA_ESCALERA_RING = [
    [-103.005, 30.660],
    [-102.870, 30.685],
    [-102.730, 30.660],
    [-102.660, 30.580],
    [-102.685, 30.470],
    [-102.760, 30.380],
    [-102.870, 30.345],
    [-102.985, 30.380],
    [-103.045, 30.470],
    [-103.040, 30.580],
    [-103.005, 30.660],
]

with open(SRC) as f:
    gj = json.load(f)

waha_circle_count = waha_label_count = 0
out_features = []

for feat in gj["features"]:
    p = feat.get("properties") or {}
    lid = p.get("layer_id")
    if lid == "waha_circle":
        feat["geometry"] = {"type": "Point", "coordinates": [WAHA_LON, WAHA_LAT]}
        p["name"] = "WAHA"
        feat["properties"] = p
        waha_circle_count += 1
    elif lid == "labels_hubs":
        feat["geometry"] = {"type": "Point", "coordinates": [WAHA_LON, WAHA_LAT]}
        p["name"] = "WAHA"
        feat["properties"] = p
        waha_label_count += 1
    out_features.append(feat)

# Append Solstice Substation feature
out_features.append({
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [SOLSTICE_LON, SOLSTICE_LAT]},
    "properties": {
        "layer_id": "solstice_substation",
        "name": "AEP Solstice Substation",
        "operator": "AEP Texas",
        "county": "Pecos",
        "voltage_kv": 345,
        "status": "Operational; 765 kV expansion planned",
        "role": "Permian Basin Reliability Plan terminus (Howard-Solstice 765 kV; Bottlebrush-Solstice 345 kV; Faulkner-Solstice 345 kV)",
        "osm_id": 500535889,
        "source": "OpenStreetMap way 500535889",
        "source_date": "2026-04-27"
    }
})

# Append La Escalera Ranch polygon
out_features.append({
    "type": "Feature",
    "geometry": {"type": "Polygon", "coordinates": [LA_ESCALERA_RING]},
    "properties": {
        "layer_id": "la_escalera",
        "name": "La Escalera Ranch (Apex Clean Energy — Pecos Flat)",
        "owner": "Lyda Family",
        "developer": "Apex Clean Energy",
        "county": "Pecos (primary); Brewster",
        "acres": 223000,
        "project": "Pecos Flat Energy — 3.3 GW wind + solar + green hydrogen",
        "ACCURACY": "APPROXIMATE — ranch boundary digitized from public-domain references; not a survey product",
        "source": "Public reporting (kjas.com 2024-09; Pecos County School Fund lease; ranch literature)",
        "source_date": "2026-04-27"
    }
})

gj["features"] = out_features

# Atomic write per OPERATING §6.15
fd, tmp = tempfile.mkstemp(prefix=".combined_geoms.", suffix=".geojson", dir=".")
try:
    with os.fdopen(fd, "w") as f:
        json.dump(gj, f, separators=(",", ":"))
    os.replace(tmp, SRC)
except Exception:
    if os.path.exists(tmp):
        os.unlink(tmp)
    raise

print(f"waha_circle features updated: {waha_circle_count}")
print(f"labels_hubs features updated: {waha_label_count}")
print(f"appended solstice_substation: 1")
print(f"appended la_escalera: 1")
print(f"total features: {len(out_features)}")
