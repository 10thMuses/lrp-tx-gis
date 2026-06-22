"""Generate every map used in the OXY dossier, writing PNGs + a key JSON.

Reads the shared asset list from oxy_assets_data.py (single source of truth for
both maps and report), then renders six maps via oxy_maps.render():
  overview, caramba (50-mi proximity), midstream, water, power, dac.

Run: python3 scripts/oxy_build_maps.py
"""
import os, json
import oxy_maps
from oxy_assets_data import ASSETS, CARAMBA, SUBSTATIONS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RPT = os.path.join(ROOT, "outputs", "reports")
os.makedirs(RPT, exist_ok=True)

def map_assets(types, include_subs=True, coords_only=False):
    """Return renderer-ready dicts for assets of the given types (+ optional subs).

    coords_only=True keeps only assets with precise lon/lat — used for the
    proximity map so county-centroid placement can't imply false nearness.
    """
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

ALL = ["gas", "power", "netpower", "dac", "water"]

def main():
    ctx = oxy_maps.load_context(ROOT)
    keys = {}

    keys["overview"] = oxy_maps.render(
        map_assets(ALL), os.path.join(RPT, "oxy_map_overview.png"),
        "OXY infrastructure across the Permian / West Texas", ctx,
        subtitle="Owned & affiliated assets · numbered to the key at right")

    keys["caramba"] = oxy_maps.render(
        map_assets(ALL, include_subs=False, coords_only=True),
        os.path.join(RPT, "oxy_map_caramba.png"),
        "OXY assets within 50 miles of Caramba North", ctx,
        center=CARAMBA, radius_mi=50, fig_w=8.0,
        subtitle="Pecos County · green ring = 50-mile radius from the Williams tract")

    keys["midstream"] = oxy_maps.render(
        map_assets(["gas"]), os.path.join(RPT, "oxy_map_midstream.png"),
        "Midstream, pipelines & gas processing", ctx,
        subtitle="OXY-owned CO₂ / gas-processing assets + WES processing")

    keys["water"] = oxy_maps.render(
        map_assets(["water"]), os.path.join(RPT, "oxy_map_water.png"),
        "Water — produced-water recycling & desalination", ctx,
        subtitle="OXY & Western Midstream water assets")

    keys["power"] = oxy_maps.render(
        map_assets(["power", "netpower"]), os.path.join(RPT, "oxy_map_power.png"),
        "Power generation & NET Power", ctx,
        subtitle="Solar OXY powers its operations with + the NET Power gas-to-power site")

    keys["dac"] = oxy_maps.render(
        map_assets(["dac", "power", "netpower"], include_subs=False),
        os.path.join(RPT, "oxy_map_dac.png"),
        "Carbon capture — the Odessa low-carbon cluster", ctx,
        subtitle="STRATOS direct-air-capture + co-located solar & NET Power (Ector Co.)")

    json.dump(keys, open(os.path.join(RPT, "oxy_map_keys.json"), "w"),
              indent=1, ensure_ascii=False)
    for k, rows in keys.items():
        print(f"{k:10s} {len(rows)} numbered")

if __name__ == "__main__":
    main()
