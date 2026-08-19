#!/usr/bin/env python3
"""Derive every numeric figure in the Caramba North post-NDA Offering
Memorandum from the repo's canonical layer data.

Nothing in the rendered document is hand-typed except counterparty-supplied
indicative terms (Sections 5 and 6), which are declared in CONFIG below and
labelled as such in the document.

Methodology is inherited from the locked May-2026 study:
  - genuine new drill  == completion_year blank OR completion_year >= spud_year
                          (RULE H, outputs/reports/pecos_lock.py)
  - shallow            == total_depth < 3000 ft
  - marginal / EOL     == lease trailing avg <= 125 Mcf/d gas AND <= 25 bbl/d oil
  - distances          == straight line from tract centroid, 69 mi/deg lat

Usage:
    python3 scripts/caramba_om_data.py            # pretty-print the model
    python3 scripts/caramba_om_data.py --json out.json
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import math
import os
import re
import sys
from pathlib import Path

REPO = Path(os.environ.get("LRP_PROJECT_DIR", Path(__file__).resolve().parent.parent))

# --------------------------------------------------------------------------
# CONFIG — counterparty-supplied indicative terms and settled framing.
# These are the only non-derived values in the document.
# --------------------------------------------------------------------------
CONFIG = {
    "acres_max": 1300,
    "water_af_yr": 47418,
    "water_mgd": 42.3,
    "solstice_miles": 15,
    "waha_miles": 20,
    "gas_quote_mmbtu_d": 200000,
    "gas_quote_term_years": 15,
    "gas_ciac_musd": "15–25",
    "gas_lead_months": "9–15",
    "adjacent_counties": ["Reeves", "Crane", "Ward", "Upton", "Ector", "Crockett"],
    "peer_counties": ["Reagan", "Howard", "Reeves", "Loving", "Midland", "Martin"],
    "marginal_gas_mcf_d": 125.0,
    "marginal_oil_bbl_d": 25.0,
    "shallow_ft": 3000.0,
}

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def pint(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def pflt(v):
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def norm_county(v: str) -> str:
    return (v or "").upper().replace(" COUNTY", "").strip()


def load_points(layer_ids):
    """Stream combined_points.csv, keeping only the requested layers."""
    want = set(layer_ids)
    out = collections.defaultdict(list)
    with open(REPO / "combined_points.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["layer_id"] in want:
                out[r["layer_id"]].append(r)
    return out


def tract_geometry():
    with open(REPO / "combined_geoms.geojson", encoding="utf-8") as f:
        gj = json.load(f)
    feats = gj.get("features", gj)
    car = next(
        f for f in feats
        if (f.get("properties") or {}).get("layer_id") == "caramba_north"
    )
    g = car["geometry"]
    rings = ([g["coordinates"][0]] if g["type"] == "Polygon"
             else [p[0] for p in g["coordinates"]])
    pts = [p for r in rings for p in r]
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    return rings, cx, cy


RINGS, CX, CY = tract_geometry()


def miles(lon, lat):
    return math.hypot((lat - CY) * 69.0,
                      (lon - CX) * 69.0 * math.cos(math.radians((lat + CY) / 2)))


def in_tract(lon, lat):
    """Ray-casting point-in-polygon against the tract rings."""
    inside = False
    for ring in RINGS:
        n = len(ring)
        j = n - 1
        for i in range(n):
            xi, yi = ring[i][0], ring[i][1]
            xj, yj = ring[j][0], ring[j][1]
            if (yi > lat) != (yj > lat):
                xint = (xj - xi) * (lat - yi) / (yj - yi) + xi
                if lon < xint:
                    inside = not inside
            j = i
    return inside


def apikey(s):
    """RRC API8 = county code (3) + unique (5). Sources carry a leading state
    code 42 and, in FracFocus, a trailing 4-digit sidetrack suffix."""
    d = re.sub(r"\D", "", s or "")
    if len(d) >= 10 and d.startswith("42"):
        return d[2:10]
    return d[:8] if len(d) >= 8 else None


# --------------------------------------------------------------------------
# Section 3 — transmission
# --------------------------------------------------------------------------
def section3(pts):
    with open(REPO / "combined_geoms.geojson", encoding="utf-8") as f:
        gj = json.load(f)
    feats = gj.get("features", gj)
    tpit_lines = sum(1 for ft in feats
                     if (ft.get("properties") or {}).get("layer_id") == "tpit_lines")
    subs = []
    for r in pts["substations"]:
        lat, lon = pflt(r["lat"]), pflt(r["lon"])
        if lat is None or lon is None:
            continue
        d = miles(lon, lat)
        if d <= 12 and r.get("name"):
            subs.append({"name": r["name"], "miles": round(d, 1),
                         "voltage": r.get("voltage") or ""})
    subs.sort(key=lambda x: x["miles"])
    return {
        "tpit_substation_upgrades": len(pts["tpit_subs"]),
        "tpit_line_projects": tpit_lines,
        "local_substations": subs[:6],
    }


# --------------------------------------------------------------------------
# Section 4 — regional power cluster
# --------------------------------------------------------------------------
TECH_LABEL = {"PV": "Solar", "WT": "Wind", "BA": "BESS",
              "IC": "Gas", "GT": "Gas", "CC": "Gas", "ST": "Gas"}


def _eia_tech(t):
    if t == "Solar Photovoltaic":
        return "Solar"
    if t == "Onshore Wind Turbine":
        return "Wind"
    if t == "Batteries":
        return "BESS"
    if t.startswith("Natural Gas") or t in ("Petroleum Liquids",):
        return "Gas"
    return None


def _operating(pts, counties):
    """Operating fleet, EIA-860 basis, deduped to plant level."""
    out = collections.defaultdict(lambda: {"projects": {}, "mw": 0.0})
    for r in pts["eia860_plants"]:
        if norm_county(r["county"]) not in counties:
            continue
        tech = _eia_tech(r.get("technology") or "")
        if not tech:
            continue
        mw = pflt(r.get("capacity_mw")) or 0.0
        key = r.get("plant_code") or r["name"]
        e = out[tech]
        e["projects"].setdefault(key, {"name": r["name"], "mw": 0.0})
        e["projects"][key]["mw"] += mw
        e["mw"] += mw
    return out


def _queue(pts, counties):
    out = collections.defaultdict(lambda: {"projects": {}, "mw": 0.0})
    for r in pts["ercot_queue"]:
        if norm_county(r["county"]) not in counties:
            continue
        tech = TECH_LABEL.get(r.get("technology") or "", "Other")
        mw = pflt(r.get("mw")) or 0.0
        key = (r.get("name") or "").strip()
        e = out[tech]
        e["projects"].setdefault(key, {"name": key, "mw": 0.0})
        e["projects"][key]["mw"] += mw
        e["mw"] += mw
    return out


def _fmt_group(g, top_n=12):
    rows = []
    for tech in ("Solar", "Wind", "BESS", "Gas"):
        e = g.get(tech)
        if not e:
            rows.append({"tech": tech, "count": 0, "mw": 0.0, "named": []})
            continue
        named = sorted(e["projects"].values(), key=lambda p: -p["mw"])
        rows.append({
            "tech": tech,
            "count": len(named),
            "mw": round(e["mw"]),
            "named": [{"name": p["name"], "mw": round(p["mw"])}
                      for p in named[:top_n]],
            "more": max(0, len(named) - top_n),
        })
    return rows


def section4(pts):
    pecos = {"PECOS"}
    adj = {c.upper() for c in CONFIG["adjacent_counties"]}

    op_p, q_p = _operating(pts, pecos), _queue(pts, pecos)
    op_a, q_a = _operating(pts, adj), _queue(pts, adj)

    # proximity markers: operating storage / solar near the tract
    markers = []
    for lid, label in (("eia860_battery", "BESS"), ("solar", "Solar")):
        for r in pts.get(lid, []):
            lat, lon = pflt(r["lat"]), pflt(r["lon"])
            if lat is None or lon is None:
                continue
            d = miles(lon, lat)
            if d <= 20:
                markers.append({"name": r["name"], "kind": label,
                                "miles": round(d, 1),
                                "mw": round(pflt(r.get("capacity_mw")) or 0.0)})
    markers.sort(key=lambda x: x["miles"])

    within20 = [r for r in pts["ercot_queue"]
                if pflt(r["lat"]) is not None
                and miles(float(r["lon"]), float(r["lat"])) <= 20]

    return {
        "pecos_operating": _fmt_group(op_p),
        "pecos_queue": _fmt_group(q_p),
        "adjacent_operating": _fmt_group(op_a),
        "adjacent_queue": _fmt_group(q_a),
        "pecos_operating_total_mw": round(sum(e["mw"] for e in op_p.values())),
        "pecos_queue_total_mw": round(sum(e["mw"] for e in q_p.values())),
        "adjacent_operating_total_mw": round(sum(e["mw"] for e in op_a.values())),
        "adjacent_queue_total_mw": round(sum(e["mw"] for e in q_a.values())),
        "pecos_queue_projects": sum(len(e["projects"]) for e in q_p.values()),
        "queue_within_20mi_projects": len(within20),
        "queue_within_20mi_mw": round(sum(pflt(r["mw"]) or 0.0 for r in within20)),
        "proximity_markers": markers[:8],
    }


# --------------------------------------------------------------------------
# Section 7 — data-center pipeline
# --------------------------------------------------------------------------
def section7():
    p = REPO / "data" / "datacenters" / "dc_anchors.json"
    with open(p, encoding="utf-8") as f:
        raw = json.load(f)
    entries = raw.get("entries", raw.get("features", []))
    out = []
    for e in entries:
        pr = e.get("properties", e) or {}
        srcs = pr.get("sources") or []
        out.append({
            "id": pr.get("id"),
            "name": pr.get("name"),
            "developer": pr.get("developer"),
            "county": pr.get("county"),
            "capacity_mw": pr.get("capacity_mw_announced"),
            "status": (pr.get("status") or "").replace("_", " "),
            "detail": pr.get("power_source"),
            "lat": pr.get("lat"),
            "lon": pr.get("lon"),
            "coord_accuracy": pr.get("coord_accuracy"),
            "miles": (round(miles(pr["lon"], pr["lat"]), 1)
                      if pr.get("lat") and pr.get("lon") else None),
            "source_url": srcs[0].get("url") if srcs else None,
        })
    out.sort(key=lambda x: -(x["capacity_mw"] or 0))
    total = sum(x["capacity_mw"] or 0 for x in out)
    LOCAL_MI = 60
    local = [x for x in out if x["miles"] is not None and x["miles"] <= LOCAL_MI]
    other = [x for x in out if x not in local]
    local_mw = sum(x["capacity_mw"] or 0 for x in local)
    return {"anchors": out, "count": len(out),
            "local": local, "other": other, "local_radius_mi": LOCAL_MI,
            "local_mw": local_mw, "local_gw": round(local_mw / 1000.0, 1),
            "total_mw": total, "total_gw": round(total / 1000.0, 1),
            "generated": raw.get("generated")}


# --------------------------------------------------------------------------
# Section 9 — subsurface and drilling activity
# --------------------------------------------------------------------------
def load_wells():
    out = []
    for name in ("wells_permian6.csv", "wells_howard_loving.csv"):
        p = REPO / "data" / name
        if not p.exists():
            continue
        with open(p, newline="", encoding="utf-8") as f:
            out.extend(csv.DictReader(f))
    return out or None


def is_new_drill(r):
    sy = pint(r.get("spud_year"))
    if sy is None:
        return False
    cy = pint(r.get("completion_year"))
    return cy is None or cy >= sy


def section9(wells):
    if wells is None:
        return {"available": False}
    SHALLOW = CONFIG["shallow_ft"]

    for r in wells:
        lat, lon = pflt(r.get("lat")), pflt(r.get("lon"))
        r["_m"] = miles(lon, lat) if (lat is not None and lon is not None) else None

    pecos = [r for r in wells if (r.get("county_name") or "").strip() == "Pecos"]

    # --- 9.1 on the tract itself
    tract = []
    for r in pecos:
        lat, lon = pflt(r.get("lat")), pflt(r.get("lon"))
        if lat is None or lon is None or not in_tract(lon, lat):
            continue
        tract.append({
            "depth_ft": pflt(r.get("total_depth")),
            "spud_year": pint(r.get("spud_year")),
            "plugged": (r.get("plug_flag") or "").strip().upper() in ("Y", "1", "TRUE"),
            "active": (r.get("active_flag") or "").strip().upper() in ("Y", "1", "TRUE"),
            "oil_gas": (r.get("oil_gas") or "").strip(),
        })
    tract = [t for t in tract if t["depth_ft"] is not None]
    tract.sort(key=lambda t: t["depth_ft"])

    # --- 9.2 wellbore-record events since 2020, Pecos
    ev = [r for r in pecos if (pint(r.get("spud_year")) or 0) >= 2020]
    nd_events = [r for r in ev if is_new_drill(r)]
    events = {
        "total": len(ev),
        "new_drill": len(nd_events),
        "rework": len(ev) - len(nd_events),
        "new_drill_pct": round(100.0 * len(nd_events) / len(ev)) if ev else 0,
    }

    # --- 9.3 proximity of all wellbores
    def near(radius):
        return [r for r in wells if r["_m"] is not None and r["_m"] <= radius]

    w1, w2 = near(1), near(2)
    shallow2 = [r for r in w2
                if (pflt(r.get("total_depth")) or 1e9) < SHALLOW
                and pint(r.get("spud_year")) is not None]
    shallow2.sort(key=lambda r: pint(r["spud_year"]))
    nonplugged_shallow2 = sorted(
        [r for r in shallow2
         if (r.get("plug_flag") or "").strip().upper() not in ("Y", "1", "TRUE")],
        key=lambda r: r["_m"])
    proximity = {
        "wellbores_within_1mi": len(w1),
        "shallow_within_1mi": sum(1 for r in w1
                                  if (pflt(r.get("total_depth")) or 1e9) < SHALLOW),
        "wellbores_within_2mi": len(w2),
        "shallow_within_2mi": len(shallow2),
        "shallow_spud_min": pint(shallow2[0]["spud_year"]) if shallow2 else None,
        "shallow_spud_max": pint(shallow2[-1]["spud_year"]) if shallow2 else None,
        "most_recent_spud_within_2mi": max(
            [pint(r.get("spud_year")) for r in w2 if pint(r.get("spud_year"))],
            default=None),
        "nearest_nonplugged_shallow": [
            {"miles": round(r["_m"], 2), "spud_year": pint(r.get("spud_year")),
             "depth_ft": pflt(r.get("total_depth"))}
            for r in nonplugged_shallow2[:2]],
    }

    # --- 9.4 new drilling since 2020 by distance and depth (Pecos)
    nd = [r for r in pecos
          if (pint(r.get("spud_year")) or 0) >= 2020 and is_new_drill(r)
          and r["_m"] is not None]
    bands = {}
    for label, lo, hi in (("≤ 2 mi", 0, 2), ("≤ 5 mi", 0, 5), ("≤ 10 mi", 0, 10)):
        sel = [r for r in nd if r["_m"] <= hi]
        bands[label] = {
            "count": len(sel),
            "shallow": sum(1 for r in sel
                           if (pflt(r.get("total_depth")) or 1e9) < SHALLOW),
            "nearest": round(min((r["_m"] for r in sel), default=0), 2) if sel else None,
        }
    far = [r for r in nd if r["_m"] > 10]
    fm = sorted(r["_m"] for r in far)
    depth_bands = collections.Counter()
    for r in far:
        d = pflt(r.get("total_depth"))
        if d is None:
            continue
        if d < 3000:
            depth_bands["< 3,000 ft (shallow)"] += 1
        elif d < 5000:
            depth_bands["3,000 – 4,999 ft"] += 1
        elif d < 10000:
            depth_bands["5,000 – 9,999 ft"] += 1
        else:
            depth_bands["≥ 10,000 ft"] += 1
    # RULE H boundary cases: wellbores whose completion_year is exactly one year
    # before a >=2020 spud_year. These are new wells whose paperwork crossed a
    # year boundary, not decades-old recompletions, but RULE H excludes them.
    boundary = []
    for r in pecos:
        sy, cy = pint(r.get("spud_year")), pint(r.get("completion_year"))
        if sy is None or cy is None or sy < 2020 or r["_m"] is None:
            continue
        if 0 < sy - cy <= 1 and r["_m"] <= 10:
            boundary.append({"miles": round(r["_m"], 2), "spud_year": sy,
                             "completion_year": cy,
                             "depth_ft": pflt(r.get("total_depth"))})
    boundary.sort(key=lambda x: x["miles"])

    newdrill = {
        "bands": bands,
        "rule_h_boundary_within_10mi": boundary,
        "beyond_10mi": {
            "count": len(far),
            "median_mi": round(fm[len(fm) // 2], 1) if fm else None,
            "mean_mi": round(sum(fm) / len(fm), 1) if fm else None,
            "max_mi": round(fm[-1], 1) if fm else None,
        },
        "depth_bands": dict(depth_bands),
        "county_total": len(nd),
    }

    # --- 9.5 peer-county comparison
    peers = {}
    for c in ["Pecos"] + CONFIG["peer_counties"]:
        cr = [r for r in wells if (r.get("county_name") or "").strip() == c]
        s20 = [r for r in cr if (pint(r.get("spud_year")) or 0) >= 2020]
        ndc = [r for r in s20 if is_new_drill(r)]
        peers[c] = {
            "new_drill": len(ndc),
            "shallow": sum(1 for r in ndc
                           if (pflt(r.get("total_depth")) or 1e9) < SHALLOW),
        }
    others = [v["new_drill"] for k, v in peers.items() if k != "Pecos"]
    comparison = {
        "counties": peers,
        "peer_average": round(sum(others) / len(others)) if others else None,
    }

    # --- 9.6 production status near the tract
    prod = production(wells)

    # --- 9.7 FracFocus
    frac = fracfocus(wells)

    return {
        "available": True,
        "tract_wellbores": tract,
        "events": events,
        "proximity": proximity,
        "new_drilling": newdrill,
        "comparison": comparison,
        "production": prod,
        "fracfocus": frac,
    }


def production(wells):
    p = REPO / "data" / "well_prod_status.csv"
    if not p.exists():
        return {"available": False}
    status = {}
    with open(p, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            status[r["api8"]] = (pflt(r.get("gas_mcf_d")) or 0.0,
                                 pflt(r.get("oil_bbl_d")) or 0.0)
    G, O = CONFIG["marginal_gas_mcf_d"], CONFIG["marginal_oil_bbl_d"]
    out = {}
    for radius in (2, 5, 10):
        sel = [r for r in wells
               if r["_m"] is not None and r["_m"] <= radius
               and (r.get("plug_flag") or "").strip().upper() not in ("Y", "1", "TRUE")
               and is_new_drill(r)]
        matched = marginal = 0
        for r in sel:
            k = apikey(r.get("api_no"))
            if k is None or k not in status:
                continue
            matched += 1
            g, o = status[k]
            if g <= G and o <= O:
                marginal += 1
        out[f"≤ {radius} mi"] = {
            "nonplugged": len(sel),
            "matched": matched,
            "marginal": marginal,
            "marginal_pct": round(100.0 * marginal / len(sel)) if sel else 0,
        }
    # vintage of the 10-mile population
    v = collections.Counter()
    for r in wells:
        if r["_m"] is None or r["_m"] > 10:
            continue
        if (r.get("plug_flag") or "").strip().upper() in ("Y", "1", "TRUE"):
            continue
        if not is_new_drill(r):
            continue
        sy = pint(r.get("spud_year"))
        if sy:
            v[f"{(sy // 10) * 10}s"] += 1
    return {"available": True, "radii": out, "vintage": dict(sorted(v.items()))}


def _ff_year(v):
    """FracFocus JobStartDate is 'M/D/YYYY h:mm:ss AM'."""
    m = re.search(r"/(\d{4})\b", v or "")
    if m:
        return int(m.group(1))
    m = re.match(r"\s*(\d{4})-", v or "")
    return int(m.group(1)) if m else None


def api10(s):
    """state(2) + county(3) + unique(5). The join key used by the locked
    FracFocus cross-reference (outputs/reports/fracfocus_new_drill_only.py)."""
    d = re.sub(r"\D", "", s or "")
    return d[:10] if len(d) >= 10 else d


def fracfocus(wells):
    """Cross-reference Texas FracFocus disclosures against the RRC wellbore
    record to isolate NEW-DRILL fracks (a frack performed at the original
    completion of a newly drilled wellbore), excluding re-fracs.

    Classification is the locked rule: the job year must fall within -1 to +2
    years of EITHER the wellbore's completion year or its spud year. Matching
    on completion year as well as spud year is what makes the rule robust to
    RRC re-stamping, which moves spud_year on existing wellbores.
    """
    p = REPO / "data" / "fracfocus" / "DisclosureList_1.csv"
    if not p.exists():
        return {"available": False}

    wb = {}
    for r in wells:
        a = api10(r.get("api_no"))
        if a:
            wb[a] = (pint(r.get("spud_year")), pint(r.get("completion_year")))

    def classify(api, year):
        rec = wb.get(api)
        if rec is None or year is None:
            return "unmatched"
        sy, cy = rec
        if cy is not None and -1 <= year - cy <= 2:
            return "new-drill"
        if sy is not None:
            if -1 <= year - sy <= 2:
                return "new-drill"
            if year - sy > 2:
                return "re-frac"
        if cy is not None and (year > cy + 2 or year < cy - 1):
            return "re-frac"
        return "unmatched"

    BANDS = (("0 – 2 mi", 0, 2), ("2 – 5 mi", 2, 5),
             ("5 – 10 mi", 5, 10), ("10 – 20 mi", 10, 20))
    bands = {b[0]: {"count": 0, "latest": None} for b in BANDS}
    total_pecos = 0
    per_year = collections.Counter()
    operators = collections.Counter()

    with open(p, newline="", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            st = (r.get("StateName") or "").strip().lower()
            cnty = (r.get("CountyName") or "").strip().lower()
            a = api10(r.get("APINumber"))
            if st != "texas" or cnty != "pecos":
                if not (a and a[2:5] == "371"):
                    continue
            total_pecos += 1
            lat, lon = pflt(r.get("Latitude")), pflt(r.get("Longitude"))
            if lat is None or lon is None:
                continue
            d = miles(lon, lat)
            if d > 20:
                continue
            yr = _ff_year(r.get("JobStartDate")) or _ff_year(r.get("JobEndDate"))
            if classify(a, yr) != "new-drill":
                continue
            for label, lo, hi in BANDS:
                if (d <= hi) if lo == 0 else (lo < d <= hi):
                    b = bands[label]
                    b["count"] += 1
                    if yr and (b["latest"] is None or yr > b["latest"]):
                        b["latest"] = yr
                    break
            if yr:
                per_year[yr] += 1
            op = (r.get("OperatorName") or "").strip()
            if op:
                operators[op] += 1

    return {
        "available": True,
        "pecos_disclosures": total_pecos,
        "bands": bands,
        "within_20mi_total": sum(v["count"] for v in bands.values()),
        "per_year": dict(sorted(per_year.items())),
        "top_operators": operators.most_common(5),
    }


# --------------------------------------------------------------------------
def build():
    pts = load_points(["ercot_queue", "eia860_plants", "eia860_battery",
                       "solar", "wind", "substations", "tpit_subs"])
    wells = load_wells()
    return {
        "config": CONFIG,
        "tract_centroid": {"lat": round(CY, 4), "lon": round(CX, 4)},
        "section3": section3(pts),
        "section4": section4(pts),
        "section7": section7(),
        "section9": section9(wells),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="write the model to this path")
    a = ap.parse_args()
    model = build()
    if a.json:
        Path(a.json).write_text(json.dumps(model, indent=2), encoding="utf-8")
        print(f"wrote {a.json}")
    else:
        print(json.dumps(model, indent=2)[:12000])
