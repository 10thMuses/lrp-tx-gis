#!/usr/bin/env python3
"""Cross-check the FracFocus disclosure registry against the Caramba North
tract: every hydraulic-fracturing job ever filed in Pecos County (Texas), with
distance to Caramba centroid, depth, operator, year. Filter rings: <=2, <=5,
<=10, <=20 miles.
"""
import csv, json, math, statistics
from collections import Counter
from datetime import datetime
from pathlib import Path

REPO = Path("/home/andreahimmel/lrp-tx-gis")
FF   = REPO / "data" / "fracfocus" / "DisclosureList_1.csv"

# Caramba centroid (same method as v22_analysis.py)
gj = json.load(open(REPO / "combined_geoms.geojson", encoding="utf-8"))
feats = gj.get("features", gj if isinstance(gj, list) else [])
caramba = next((f for f in feats if "caramba" in json.dumps(f.get("properties") or {}).lower()), None)
g = caramba["geometry"]
car_rings = [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
pts = [pt for r in car_rings for pt in r]
CX = sum(p[0] for p in pts) / len(pts)
CY = sum(p[1] for p in pts) / len(pts)


def miles(lon, lat):
    dlat = (lat - CY) * 69.0
    dlon = (lon - CX) * 69.0 * math.cos(math.radians((lat + CY) / 2))
    return math.hypot(dlat, dlon)


def f(s):
    try:
        return float(s) if s not in (None, "") else None
    except Exception:
        return None


def parse_date(s):
    if not s:
        return None
    for fmt in ("%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except Exception:
            pass
    return None


# --- read + filter to Texas/Pecos ---
pecos = []
tx_pecos_county_codes = {"371"}  # Pecos County FIPS-3
with open(FF, encoding="utf-8", errors="replace") as fh:
    rd = csv.DictReader(fh)
    for r in rd:
        st = (r.get("StateName") or "").strip().lower()
        cnty = (r.get("CountyName") or "").strip().lower()
        if st != "texas" or cnty != "pecos":
            # Some entries may have blank CountyName but valid API. Try API county code.
            api = (r.get("APINumber") or "").strip()
            digits = "".join(c for c in api if c.isdigit())
            if not (len(digits) >= 5 and digits[2:5] in tx_pecos_county_codes):
                continue
        lat = f(r.get("Latitude")); lon = f(r.get("Longitude"))
        if lat is None or lon is None:
            continue
        dt = parse_date(r.get("JobStartDate") or "") or parse_date(r.get("JobEndDate") or "")
        tvd = f(r.get("TVD"))
        pecos.append(dict(
            id=r.get("DisclosureId"),
            api=r.get("APINumber"),
            op=r.get("OperatorName"),
            well=r.get("WellName"),
            lat=lat, lon=lon,
            mi=miles(lon, lat),
            tvd=tvd,
            dt=dt,
            year=(dt.year if dt else None),
        ))

print(f"=== TOTAL FRACFOCUS DISCLOSURES IN PECOS COUNTY, TEXAS ===")
print(f"  All time:          {len(pecos):,}")
years = Counter([p["year"] for p in pecos if p["year"]])
print(f"  Year range:        {min(years)} – {max(years)}  (most recent = {max(years)})")
print()
print(f"=== ANNUAL VOLUME (last 10 years) ===")
for yr in sorted(years)[-12:]:
    print(f"    {yr}: {years[yr]}")

print()
print(f"=== BY DISTANCE FROM CARAMBA CENTROID ({CX:.5f}, {CY:.5f}) ===")
rings = [2, 5, 10, 20]
for R in rings:
    inside = [p for p in pecos if p["mi"] <= R]
    print(f"  <= {R:>2} mi: {len(inside)}  disclosures")
    if inside:
        recent = max((p["year"] for p in inside if p["year"]), default=None)
        oldest = min((p["year"] for p in inside if p["year"]), default=None)
        tvds = [p["tvd"] for p in inside if p["tvd"] and p["tvd"] > 0]
        print(f"            most recent year: {recent}    oldest: {oldest}")
        if tvds:
            print(f"            TVD median: {statistics.median(tvds):,.0f} ft    min/max: {min(tvds):,.0f} / {max(tvds):,.0f}")
        ops = Counter([p["op"] for p in inside])
        print(f"            operators (top 5): " + "; ".join(f"{o} ({n})" for o, n in ops.most_common(5)))

print()
print(f"=== EVERY DISCLOSURE WITHIN 10 MI (sorted by distance) ===")
near = sorted([p for p in pecos if p["mi"] <= 10], key=lambda p: p["mi"])
for p in near:
    yr = p["year"] or "??"
    tvd = f"{p['tvd']:,.0f} ft" if p["tvd"] else "TVD —"
    print(f"  {p['mi']:5.2f} mi  {yr}  {tvd:>12}  {p['op'] or '?'}   well={p['well'] or '?'}   api={p['api']}")
