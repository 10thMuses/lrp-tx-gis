"""Chat 109b consolidation:
- Reposition WAHA from Reeves into Pecos (31.155, -103.105)
- Append longfellow_ranch + gw_ranch polygons (la_escalera already exists)
- All atomic per OPERATING §6.15.
"""
import json, os, tempfile

SRC = "combined_geoms.geojson"
WAHA_LON, WAHA_LAT = -103.105, 31.155  # Pecos County, near actual WAHA hub infra

# Longfellow Ranch — Mitchell family ~350k ac southern Pecos/Terrell/Brewster.
# 33.5 mi south of Fort Stockton (operator-authoritative ranch website).
LONGFELLOW_RING = [
    [-102.860, 30.510],
    [-102.700, 30.530],
    [-102.520, 30.500],
    [-102.430, 30.420],
    [-102.435, 30.300],
    [-102.490, 30.180],
    [-102.620, 30.105],
    [-102.770, 30.135],
    [-102.860, 30.230],
    [-102.890, 30.355],
    [-102.870, 30.450],
    [-102.860, 30.510],
]

# GW Ranch (Pacifico) — ~8,000+ ac on Hwy 18, ~17 mi N of Fort Stockton, Pecos Co.
GW_RANCH_RING = [
    [-102.870, 31.155],
    [-102.815, 31.155],
    [-102.810, 31.105],
    [-102.870, 31.105],
    [-102.870, 31.155],
]

with open(SRC) as f:
    gj = json.load(f)

waha_circle_n = waha_label_n = 0
out = []
existing_ids = set()
for feat in gj["features"]:
    p = feat.get("properties") or {}
    lid = p.get("layer_id")
    existing_ids.add(lid)
    if lid == "waha_circle":
        feat["geometry"] = {"type": "Point", "coordinates": [WAHA_LON, WAHA_LAT]}
        p["name"] = "WAHA"; feat["properties"] = p
        waha_circle_n += 1
    elif lid == "labels_hubs":
        feat["geometry"] = {"type": "Point", "coordinates": [WAHA_LON, WAHA_LAT]}
        p["name"] = "WAHA"; feat["properties"] = p
        waha_label_n += 1
    out.append(feat)

# Add new layers only if not already present (idempotent)
if "longfellow_ranch" not in existing_ids:
    out.append({
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [LONGFELLOW_RING]},
        "properties": {
            "layer_id": "longfellow_ranch",
            "name": "Longfellow Ranch",
            "owner": "Mitchell Family / Riata / Mitchell Group",
            "developer": "Poolside (Project Horizon) — anchor tenant CoreWeave",
            "campus": "Hyperscale DC & Power Campus",
            "capacity": "2 GW (announced); behind-the-meter aero-derivative gas + battery",
            "county": "Pecos / Terrell / Brewster",
            "ACCURACY": "APPROXIMATE — ranch boundary digitized from public references; project area is a sub-portion",
            "source": "Poolside Project Horizon announcement (2025-10); Longfellow Ranches public materials",
            "source_date": "2026-04-27"
        }
    })
if "gw_ranch" not in existing_ids:
    out.append({
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [GW_RANCH_RING]},
        "properties": {
            "layer_id": "gw_ranch",
            "name": "GW Ranch",
            "developer": "Pacifico Energy",
            "campus": "Hyperscale DC & Power Campus",
            "capacity": "Up to 7.65 GW gas turbines + 1.8 GW battery + 750 MWac solar (TCEQ air permit)",
            "status": "Permitted; first power Q1 2027; 1 GW online 2028; 5+ GW by 2031",
            "grid": "Off-grid / private (no ERCOT interconnect)",
            "county": "Pecos",
            "ACCURACY": "APPROXIMATE — campus footprint approximated from public reporting (Hwy 18, ~17 mi N of Fort Stockton)",
            "source": "Pacifico Energy GW Ranch press materials; TCEQ permit; Texas Tribune / DCD / Big Bend Sentinel reporting",
            "source_date": "2026-04-27"
        }
    })

gj["features"] = out

fd, tmp = tempfile.mkstemp(prefix=".combined_geoms.", suffix=".geojson", dir=".")
try:
    with os.fdopen(fd, "w") as f:
        json.dump(gj, f, separators=(",", ":"))
    os.replace(tmp, SRC)
except Exception:
    if os.path.exists(tmp): os.unlink(tmp)
    raise

print(f"WAHA repositioned (circle×{waha_circle_n}, label×{waha_label_n}) -> Pecos County @ ({WAHA_LAT}, {WAHA_LON})")
print(f"longfellow_ranch present: {'longfellow_ranch' in existing_ids or 'now appended'}")
print(f"gw_ranch present: {'gw_ranch' in existing_ids or 'now appended'}")
print(f"total features: {len(out)}")
