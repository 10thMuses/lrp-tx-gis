#!/usr/bin/env python3
"""Extract Howard (FIPS 227) + Loving (301) wellbores from the local
data/rrc_raw/dbf900.txt.gz using the existing parse_rrc parser, then compute
genuine-new-drill-since-2020 counts on the same RULE H basis as memo Finding 8
(completion_year blank or >= spud_year; spud_year >= 2020; shallow < 3,000 ft)."""
import csv, sys, importlib.util
from pathlib import Path

ROOT = Path("/home/andreahimmel/lrp-tx-gis")
spec = importlib.util.spec_from_file_location("parse_rrc", ROOT / "scripts" / "parse_rrc.py")
pr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pr)

# Re-scope the parser to Howard + Loving only.
pr.COUNTIES = {"227": "Howard", "301": "Loving"}
try:
    pr.SUBJECT_COUNTY_FIPS = frozenset()
    pr.PEER_COUNTY_FIPS = frozenset()
except Exception:
    pass

SRC = ROOT / "data" / "rrc_raw" / "dbf900.txt.gz"
DST = ROOT / "data" / "wells_howard_loving.csv"
print(f"parsing {SRC} -> {DST} (Howard 227 + Loving 301)...", file=sys.stderr)
res = pr.parse_wellbore(SRC, DST)
print("parse result:", res, file=sys.stderr)

def pint(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None

agg = {}
for r in csv.DictReader(open(DST, encoding="utf-8")):
    c = (r.get("county_name") or "").strip()
    sy = pint(r.get("spud_year"))
    cyr = pint(r.get("completion_year"))
    a = agg.setdefault(c, {"total": 0, "nd": 0, "nd_shallow": 0})
    a["total"] += 1
    if sy is not None and sy >= 2020 and (cyr is None or cyr >= sy):
        a["nd"] += 1
        try:
            td = float(r["total_depth"]) if r.get("total_depth") not in (None, "") else None
        except ValueError:
            td = None
        if td is not None and td < 3000:
            a["nd_shallow"] += 1

print("\n=== Howard / Loving — genuine new-drill since 2020 (RULE H) ===")
for c in ("Howard", "Loving"):
    a = agg.get(c, {"total": 0, "nd": 0, "nd_shallow": 0})
    print(f"  {c:8s} total_wellbores={a['total']:6d}  new-drill>=2020={a['nd']:5d}  of which shallow<3000={a['nd_shallow']:4d}")
