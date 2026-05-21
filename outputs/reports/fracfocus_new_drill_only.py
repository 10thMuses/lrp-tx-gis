#!/usr/bin/env python3
"""Cross-reference each FracFocus disclosure within 20 mi of Caramba against
the dbf900 wellbore record (by API) to filter to NEW-DRILL fracks only.

Classification per disclosure:
  - "new-drill frack" : the FracFocus job is the original completion of a
    genuine-new-drill wellbore (i.e., the wellbore record has
    completion_year >= spud_year, AND the FracFocus job date is within
    ~24 months of the wellbore's spud_date).
  - "re-frac" : everything else (re-stamp records; or FracFocus date well
    after original completion -> re-frac on existing well).

This is the conservative interpretation: it ONLY counts fracks that
correspond to drilling a new wellbore. Re-fracs of existing wells are
excluded, per advisor.
"""
import csv, json, math, statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path("/home/andreahimmel/lrp-tx-gis")
FF   = REPO / "data" / "fracfocus" / "DisclosureList_1.csv"
WB   = REPO / "data" / "wells_permian6.csv"

# Caramba centroid
gj = json.load(open(REPO / "combined_geoms.geojson", encoding="utf-8"))
feats = gj.get("features", gj if isinstance(gj, list) else [])
caramba = next((f for f in feats if "caramba" in json.dumps(f.get("properties") or {}).lower()), None)
g = caramba["geometry"]
car_rings = [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
pts = [pt for r in car_rings for pt in r]
CX = sum(p[0] for p in pts) / len(pts); CY = sum(p[1] for p in pts) / len(pts)


def miles(lon, lat):
    dlat = (lat - CY) * 69.0
    dlon = (lon - CX) * 69.0 * math.cos(math.radians((lat + CY) / 2))
    return math.hypot(dlat, dlon)


def f(s):
    try: return float(s) if s not in (None, "") else None
    except: return None


def parse_int(s):
    try: return int(float(s)) if s not in (None, "") else None
    except: return None


def parse_date(s):
    if not s: return None
    for fmt in ("%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try: return datetime.strptime(s.strip(), fmt)
        except: pass
    return None


def api8(s):
    """Normalize an API number to 'state(2)+county(3)+unique(5)' = 10 digits."""
    digits = "".join(c for c in (s or "") if c.isdigit())
    return digits[:10] if len(digits) >= 10 else digits


# --- Index wellbore record by 10-digit API ---
wb_idx = {}  # api10 -> dict(spud_y, comp_y, td, plug)
with open(WB, encoding="utf-8") as fh:
    rd = csv.DictReader(fh)
    for r in rd:
        a = api8(r.get("api_no"))
        if not a: continue
        wb_idx[a] = dict(
            spud_y=parse_int(r.get("spud_year")),
            comp_y=parse_int(r.get("completion_year")),
            spud_d=parse_date(r.get("spud_date") or ""),
            comp_d=parse_date(r.get("completion_date") or ""),
            td=f(r.get("total_depth")),
            plug=(r.get("plug_flag") or "").strip().upper(),
        )

# --- Read FracFocus disclosures in Pecos ---
disc = []
with open(FF, encoding="utf-8", errors="replace") as fh:
    rd = csv.DictReader(fh)
    for r in rd:
        st = (r.get("StateName") or "").strip().lower()
        cnty = (r.get("CountyName") or "").strip().lower()
        api = (r.get("APINumber") or "").strip()
        a10 = api8(api)
        if st != "texas" or cnty != "pecos":
            if not (a10 and a10[2:5] == "371"):
                continue
        lat = f(r.get("Latitude")); lon = f(r.get("Longitude"))
        if lat is None or lon is None: continue
        dt = parse_date(r.get("JobStartDate") or "") or parse_date(r.get("JobEndDate") or "")
        disc.append(dict(
            api=a10, op=r.get("OperatorName"), well=r.get("WellName"),
            lat=lat, lon=lon, mi=miles(lon, lat),
            tvd=f(r.get("TVD")), dt=dt, year=(dt.year if dt else None),
        ))

# --- Classify each disclosure ---
NEW = "new-drill"
REFRAC = "re-frac"
UNMATCHED = "unmatched"

def classify(d):
    """Match the FracFocus job date against EITHER the wellbore spud date OR
    the wellbore completion date. The frack is a "new-drill frack" iff it falls
    near the original spud/completion of the wellbore (within -1 to +2 years).
    A re-stamped wellbore can still have its ORIGINAL frack appear at the
    original completion_year (which is the earlier of spud/completion in
    re-stamp records) -- those are new-drill fracks, not re-fracs."""
    wb = wb_idx.get(d["api"])
    if wb is None:
        return UNMATCHED, "wellbore not in dbf900"
    sy, cy = wb["spud_y"], wb["comp_y"]
    if d["year"] is None:
        return UNMATCHED, "no FracFocus date"
    # Match against completion_year (original frack at original completion).
    if cy is not None:
        delta_c = d["year"] - cy
        if -1 <= delta_c <= 2:
            return NEW, f"frack at original completion (completion {cy}, frack {d['year']})"
    # Match against spud_year (covers genuine-new-drill records where spud == completion).
    if sy is not None:
        delta_s = d["year"] - sy
        if -1 <= delta_s <= 2:
            return NEW, f"frack near spud (spud {sy}, frack {d['year']})"
        if delta_s > 2:
            return REFRAC, f"re-frac ({delta_s}y after spud {sy}, frack {d['year']})"
    if cy is not None and d["year"] > cy + 2:
        return REFRAC, f"re-frac ({d['year']-cy}y after original completion {cy})"
    if cy is not None and d["year"] < cy - 1:
        return REFRAC, f"frack before completion -- data error or duplicate ({d['year']} vs completion {cy})"
    return UNMATCHED, "ambiguous"

for d in disc:
    d["cls"], d["why"] = classify(d)

# --- Report ring counts by classification ---
RINGS = [(0, 2), (2, 5), (5, 10), (10, 20)]
print(f"=== FRACFOCUS DISCLOSURES IN PECOS, BY RING + CLASSIFICATION ===")
print(f"  Total disclosures pulled:         {len(disc):,}")
print(f"  Classification overall: ", Counter(d['cls'] for d in disc))
print()
for lo, hi in RINGS:
    band = [d for d in disc if lo < d["mi"] <= hi if hi != 20 or d["mi"] <= 20]
    # ring 0-2 is inclusive at 0:
    if lo == 0:
        band = [d for d in disc if d["mi"] <= hi]
    else:
        band = [d for d in disc if lo < d["mi"] <= hi]
    nd = [d for d in band if d["cls"] == NEW]
    rf = [d for d in band if d["cls"] == REFRAC]
    un = [d for d in band if d["cls"] == UNMATCHED]
    print(f"  {lo}–{hi} mi: total={len(band):3d}  new-drill={len(nd):3d}  re-frac={len(rf):3d}  unmatched={len(un):3d}")
    if nd:
        recent_nd = max((x['year'] for x in nd if x['year']), default=None)
        print(f"            new-drill: most recent year = {recent_nd}; operators: " + ", ".join(f"{op} ({n})" for op, n in Counter(x['op'] for x in nd).most_common(5)))

print()
print(f"=== EVERY DISCLOSURE WITHIN 10 MI -- classified ===")
near = sorted([d for d in disc if d["mi"] <= 10], key=lambda d: d["mi"])
for d in near:
    yr = d["year"] or "??"
    tvd = f"{d['tvd']:,.0f} ft" if d["tvd"] else "TVD —"
    print(f"  {d['mi']:5.2f} mi  {yr}  {tvd:>10}  [{d['cls']}]  {d['op'] or '?'}   well={d['well'] or '?'}   api={d['api']}   why={d['why']}")
