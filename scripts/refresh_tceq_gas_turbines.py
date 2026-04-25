"""
TCEQ gas-turbine refresh.

Source: https://www.tceq.texas.gov/downloads/permitting/air/memos/turbine-lst.xlsx
Sheets read: "Issued Turbine Air Permits", "Pending Turbine Air Permits".
Scope: 23-county West Texas, most-recent received year >= 2020.
Output: outputs/refresh/tceq_gas_turbines_<date>.csv (combined_points.csv schema).
Geocoding: OpenStreetMap Nominatim, City+County+TX precision.

Field expansion (Chat 92): full received_date ISO -> `zone`, num_units -> `project`,
permit status -> `funnel_stage`. plant_code keeps Permit No. (no separate INR
column exists in the source; confirmed Chat 92 recon).

Status taxonomy:
  issued    - Issued sheet, datetime Received cell
  renewed   - Issued sheet, Received cell starts with "renew" (most-recent date used)
  modified  - Issued sheet, Received cell starts with "upgraded"
  pending   - Pending sheet

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

DATE_RE = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{2}|\d{4})\b")


def _norm_year(y):
    """Two-digit year -> 4-digit. <=29 -> 20xx, else 19xx."""
    yi = int(y)
    if yi < 100:
        return 2000 + yi if yi <= 29 else 1900 + yi
    return yi


def parse_dates(cell):
    """Parse a Received or Issue cell; returns list of date strings (ISO),
    most-recent first. Handles datetime cells and 'renew M/D/YY M/D/YYYY' strings."""
    if cell is None:
        return []
    if hasattr(cell, "strftime"):
        return [cell.strftime("%Y-%m-%d")]
    s = str(cell).strip()
    if not s:
        return []
    found = []
    for m, d, y in DATE_RE.findall(s):
        try:
            yr = _norm_year(y)
            dt = date(yr, int(m), int(d))
            found.append(dt)
        except (ValueError, TypeError):
            continue
    found.sort(reverse=True)
    return [dt.isoformat() for dt in found]


def derive_status(received_cell, sheet_name):
    """Return one of {issued, renewed, modified, pending} per Chat 92 taxonomy."""
    if "Pending" in sheet_name:
        return "pending"
    if isinstance(received_cell, str):
        prefix = received_cell.strip().lower()
        if prefix.startswith("renew"):
            return "renewed"
        if prefix.startswith("upgraded") or prefix.startswith("amend") or prefix.startswith("modif"):
            return "modified"
    return "issued"


def geocode(city, county):
    """City, County, TX -> (lat, lon) via Nominatim. None on miss."""
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


def process_sheet(ws, sheet_name):
    """Return list of (row_tuple, status, received_iso, issue_iso, recv_year)
    for in-county rows passing the date filter."""
    out = []
    for r in ws.iter_rows(min_row=6, values_only=True):
        if not r[0]:
            continue
        county = (r[7] or "").strip().upper()
        if county not in COUNTIES_23:
            continue
        status = derive_status(r[3], sheet_name)
        recv_dates = parse_dates(r[3])
        issue_dates = parse_dates(r[4])
        recv_iso = recv_dates[0] if recv_dates else ""
        issue_iso = issue_dates[0] if issue_dates else ""
        recv_year = int(recv_iso[:4]) if recv_iso else None
        if recv_year is None or recv_year < 2020:
            continue
        out.append((r, status, recv_iso, issue_iso, recv_year))
    return out


def main():
    src = Path("outputs/refresh/turbine-lst_2026-04-23.xlsx")
    if not src.exists():
        src = Path("/tmp/turbine-lst.xlsx")
    wb = openpyxl.load_workbook(src, data_only=True)

    issued = process_sheet(wb["Issued Turbine Air Permits"], "Issued Turbine Air Permits")
    pending = process_sheet(wb["Pending Turbine Air Permits"], "Pending Turbine Air Permits")
    print(f"Issued in-county post-2020: {len(issued)}")
    print(f"Pending in-county post-2020: {len(pending)}")

    status_counts = {}
    for _r, s, _ri, _ii, _y in issued + pending:
        status_counts[s] = status_counts.get(s, 0) + 1
    print(f"Status breakdown: {status_counts}")

    out_rows = []
    for r, status, recv_iso, issue_iso, recv_year in issued + pending:
        permit_no = str(r[0] or "").strip()
        company = (r[5] or "").strip()
        city = (r[6] or "").strip()
        county = (r[7] or "").strip().title()
        model = (r[8] or "").strip()
        n_cts = r[9]
        project_mw = r[11]
        mode = (r[15] or "").strip()

        print(f"  [{permit_no}] {company} | {city}, {county} | {status} | geocoding...")
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
            "zone": recv_iso,
            "entity": company,
            "funnel_stage": status,
            "commissioned": issue_iso,
            "capacity_mw": project_mw if project_mw is not None else "",
            "operator": company,
            "project": str(n_cts) if n_cts is not None else "",
            "manu": extract_manu(model),
            "model": model,
            "year": recv_year if recv_year else "",
        })
        out_rows.append(row)

    today = date.today().isoformat()
    out_path = Path(f"outputs/refresh/tceq_gas_turbines_{today}.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SCHEMA)
        w.writeheader()
        w.writerows(out_rows)
    print(f"\nWrote {len(out_rows)} rows -> {out_path}")
    geocoded = sum(1 for r in out_rows if r["lat"])
    print(f"Geocoded: {geocoded}/{len(out_rows)}")
    return len(out_rows), geocoded


if __name__ == "__main__":
    n, g = main()
    sys.exit(0 if n > 0 and g == n else 1)
