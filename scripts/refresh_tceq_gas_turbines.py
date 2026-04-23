"""
TCEQ gas-turbine refresh.

Source: https://www.tceq.texas.gov/downloads/permitting/air/memos/turbine-lst.xlsx
Scope: 23-county West Texas, Received date >= 2020, Issued sheet only (active).
Output: outputs/refresh/tceq_gas_turbines_<date>.csv (combined_points.csv schema).
Geocoding: Census Public_AR_Current one-line geocoder, City+TX precision.

Usage: python scripts/refresh_tceq_gas_turbines.py
"""
import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

import openpyxl

SOURCE_URL = "https://www.tceq.texas.gov/downloads/permitting/air/memos/turbine-lst.xlsx"
GEOCODER = "https://nominatim.openstreetmap.org/search?q={q}&format=json&limit=1&countrycodes=us"
UA = "LRP-TX-GIS/1.0 (refinement-tceq-refresh)"

COUNTIES_23 = {
    "ANDREWS", "BREWSTER", "CRANE", "CROCKETT", "CULBERSON", "ECTOR",
    "GLASSCOCK", "HUDSPETH", "IRION", "JEFF DAVIS", "LOVING", "MARTIN",
    "MIDLAND", "PECOS", "PRESIDIO", "REAGAN", "REEVES", "SCHLEICHER",
    "SUTTON", "TERRELL", "UPTON", "WARD", "WINKLER",
}

# combined_points.csv schema (header row)
SCHEMA = [
    "layer_id", "lat", "lon", "name", "plant_code", "county", "technology",
    "capacity", "sector", "inr", "fuel", "mw", "zone", "poi", "entity",
    "funnel_stage", "group", "under_construction", "commissioned",
    "capacity_mw", "operator", "voltage", "osm_id", "depth_ft", "use",
    "aquifer", "project", "manu", "model", "cap_kw", "year",
]


def received_year(v):
    """Extract earliest year from Received cell. Handles dates and 'renew X/Y/Z...' text."""
    if v is None:
        return None
    if hasattr(v, "year"):
        return v.year
    s = str(v)
    # Find all dates in the string
    years = re.findall(r"\b(19|20)(\d{2})\b", s)
    if years:
        return min(int(a + b) for a, b in years)
    return None


def geocode(city, county):
    """City, County, TX → (lat, lon) via Nominatim. None on miss."""
    q1 = f"{city}, {county} County, Texas, USA"
    q2 = f"{city}, Texas, USA"
    for q in (q1, q2):
        url = GEOCODER.format(q=urllib.parse.quote(q))
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.load(r)
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception as e:
            print(f"  geocode error for '{q}': {e}", file=sys.stderr)
    return None, None


def extract_manu(model):
    """Extract manufacturer token from turbine-model string."""
    if not model:
        return ""
    m = str(model).strip()
    lower = m.lower()
    for token, name in [
        ("siemens", "Siemens"), ("ge ", "GE"), ("ge h-", "GE"), ("ge f", "GE"),
        ("ge 7", "GE"), ("ge lm", "GE"), ("ge tm", "GE"), ("tm2500", "GE"),
        ("r-r", "Rolls-Royce"), ("rolls", "Rolls-Royce"),
        ("solar ", "Solar Turbines"), ("mhi", "Mitsubishi"),
        ("mitsubishi", "Mitsubishi"), ("pratt", "Pratt & Whitney"),
    ]:
        if token in lower:
            return name
    return m.split()[0] if m else ""


def main():
    src = Path("outputs/refresh/turbine-lst_2026-04-23.xlsx")
    if not src.exists():
        src = Path("/tmp/turbine-lst.xlsx")
    wb = openpyxl.load_workbook(src, data_only=True)
    ws = wb["Issued Turbine Air Permits"]

    # Rows start at 6 (header at 5)
    rows = [r for r in ws.iter_rows(min_row=6, values_only=True) if r[0]]
    total = len(rows)
    print(f"Issued-sheet non-empty rows: {total}")

    in_county = [r for r in rows if (r[7] or "").strip().upper() in COUNTIES_23]
    print(f"In 23-county scope: {len(in_county)}")

    kept = []
    for r in in_county:
        y = received_year(r[3])
        if y is None or y < 2020:
            continue
        kept.append(r)
    print(f"Post-date filter (Received year >= 2020): {len(kept)}")

    out_rows = []
    for r in kept:
        permit_no = str(r[0] or "").strip()
        received = r[3]
        issue = r[4]
        company = (r[5] or "").strip()
        city = (r[6] or "").strip()
        county = (r[7] or "").strip().title()
        model = (r[8] or "").strip()
        n_cts = r[9]
        mw_per = r[10]
        project_mw = r[11]
        mode = (r[15] or "").strip()

        y = received_year(received)
        print(f"  [{permit_no}] {company} | {city}, {county} | geocoding...")
        lat, lon = geocode(city, county)
        time.sleep(1.1)  # Nominatim ToS: 1 req/sec max

        row = {k: "" for k in SCHEMA}
        row.update({
            "layer_id": "tceq_gas_turbines",
            "lat": f"{lat:.6f}" if lat else "",
            "lon": f"{lon:.6f}" if lon else "",
            "name": f"{company} ({permit_no})",
            "plant_code": permit_no,
            "county": county,
            "technology": f"Gas turbine {mode}".strip(),
            "fuel": "natural_gas",
            "mw": project_mw if project_mw is not None else "",
            "entity": company,
            "commissioned": (
                issue.strftime("%Y-%m-%d") if hasattr(issue, "strftime") else (str(issue) if issue else "")
            ),
            "capacity_mw": project_mw if project_mw is not None else "",
            "operator": company,
            "manu": extract_manu(model),
            "model": model,
            "year": y if y else "",
        })
        out_rows.append(row)

    today = date.today().isoformat()
    out_path = Path(f"outputs/refresh/tceq_gas_turbines_{today}.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SCHEMA)
        w.writeheader()
        w.writerows(out_rows)
    print(f"\nWrote {len(out_rows)} rows → {out_path}")
    geocoded = sum(1 for r in out_rows if r["lat"])
    print(f"Geocoded: {geocoded}/{len(out_rows)}")
    return len(out_rows), geocoded


if __name__ == "__main__":
    n, g = main()
    sys.exit(0 if n > 0 and g == n else 1)
