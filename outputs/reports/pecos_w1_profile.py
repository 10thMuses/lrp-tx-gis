"""Pecos drilling-permit orientation since 2020, from the authoritative RRC W-1
'Wellbore Profile' field (outputs/refresh/rrc_w1_permits.csv, produced by
scripts/scrape_rrc_w1.py PECOS 2020 <year>). Year is the `year_chunk` column.

Finding: modern Pecos drilling is ~87% horizontal / ~12% vertical — the permit
`total_depth` value is NOT a reliable orientation proxy (it places a majority of
clearly-horizontal permits below 3,000 ft), so orientation is read from the
Wellbore Profile field directly, not inferred from depth."""
import csv, collections

SRC = "/home/andreahimmel/lrp-tx-gis/outputs/refresh/rrc_w1_permits.csv"
prof = collections.Counter()
yrs = collections.Counter()
shal_v = shal_h = deep_v = deep_h = 0
n = 0
for r in csv.DictReader(open(SRC, encoding="utf-8", errors="replace")):
    if (r.get("county_name") or "").strip().upper() != "PECOS":
        continue
    try:
        yc = int(float(r.get("year_chunk") or 0))
    except ValueError:
        yc = 0
    if yc < 2020:
        continue
    n += 1
    yrs[yc] += 1
    p = (r.get("wb_profile") or "").strip().lower()
    prof[p] += 1
    try:
        td = float(r["total_depth"]) if r.get("total_depth") not in (None, "") else None
    except ValueError:
        td = None
    if td is not None:
        if td < 3000:
            if p.startswith("h"): shal_h += 1
            elif p.startswith("v"): shal_v += 1
        if td >= 10000:
            if p.startswith("h"): deep_h += 1
            elif p.startswith("v"): deep_v += 1

tot = sum(prof.values()) or 1
H = sum(v for k, v in prof.items() if k.startswith("h"))
V = sum(v for k, v in prof.items() if k.startswith("v"))
print("PECOS W-1 permits, year_chunk >= 2020:", n)
print("by year:", dict(sorted(yrs.items())))
print("by wb_profile:", dict(prof.most_common()))
print("HORIZONTAL = %d (%.1f%%)   VERTICAL = %d (%.1f%%)   other = %d"
      % (H, 100*H/tot, V, 100*V/tot, tot - H - V))
print("depth-vs-profile sanity (why depth is not an orientation proxy):")
print("  <3000 ft: vertical=%d  horizontal=%d" % (shal_v, shal_h))
print("  >=10000 ft: vertical=%d  horizontal=%d" % (deep_v, deep_h))
