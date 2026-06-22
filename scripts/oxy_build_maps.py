"""Generate every map used in the OXY dossier, writing PNGs + a key JSON.

Reads the shared asset list from oxy_assets_data.py, then renders six big maps
via oxy_maps.render() — each carrying a Caramba North reference marker:
  overview, caramba (50-mi proximity), midstream, water, power, dac.

Run: python3 scripts/oxy_build_maps.py
"""
import os, json
import oxy_maps
from oxy_assets_data import ASSETS, CARAMBA, SUBSTATIONS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RPT = os.path.join(ROOT, "outputs", "reports")
os.makedirs(RPT, exist_ok=True)
ALL = ["gas", "power", "netpower", "dac", "water"]

def map_assets(types, include_subs=True, coords_only=False):
    """Renderer-ready dicts for assets of the given types (+ optional subs).
    coords_only keeps only precisely-located assets (proximity map)."""
    out = []
    for a in ASSETS:
        if a["type"] not in types or not a.get("on_map", True):
            continue
        if "lon" in a:
            out.append({"name": a["name"], "label": a["map_label"], "type": a["type"],
                        "lon": a["lon"], "lat": a["lat"]})
        elif not coords_only:
            out.append({"name": a["name"], "label": a["map_label"], "type": a["type"],
                        "county": a["county"]})
    if include_subs:
        out += SUBSTATIONS
    return out

def main():
    ctx = oxy_maps.load_context(ROOT)
    keys = {}

    keys["overview"] = oxy_maps.render(
        map_assets(ALL), os.path.join(RPT, "oxy_map_overview.png"),
        "OXY infrastructure across the Permian / West Texas", ctx, caramba=CARAMBA)

    keys["caramba"] = oxy_maps.render(
        map_assets(ALL, include_subs=False, coords_only=True),
        os.path.join(RPT, "oxy_map_caramba.png"),
        "OXY assets within 50 miles of Caramba North", ctx,
        center=CARAMBA, radius_mi=50, caramba=CARAMBA)

    keys["midstream"] = oxy_maps.render(
        map_assets(["gas"]), os.path.join(RPT, "oxy_map_midstream.png"),
        "Midstream, pipelines & gas processing", ctx, caramba=CARAMBA)

    keys["water"] = oxy_maps.render(
        map_assets(["water"]), os.path.join(RPT, "oxy_map_water.png"),
        "Water — produced-water recycling & desalination", ctx, caramba=CARAMBA)

    keys["power"] = oxy_maps.render(
        map_assets(["power", "netpower"]), os.path.join(RPT, "oxy_map_power.png"),
        "Power generation & NET Power", ctx, caramba=CARAMBA)

    keys["dac"] = oxy_maps.render(
        map_assets(["dac", "power", "netpower"], include_subs=False),
        os.path.join(RPT, "oxy_map_dac.png"),
        "Carbon capture — the Odessa low-carbon cluster", ctx, caramba=CARAMBA)

    json.dump(keys, open(os.path.join(RPT, "oxy_map_keys.json"), "w"), indent=1, ensure_ascii=False)
    for k, rows in keys.items():
        print(f"{k:10s} {len(rows)} numbered")

if __name__ == "__main__":
    main()
