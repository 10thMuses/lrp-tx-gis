import csv, statistics, collections

REPO = "/home/andreahimmel/lrp-tx-gis"
W = []
for r in csv.DictReader(open(REPO + "/data/wells_permian6.csv", encoding="utf-8")):
    if (r.get("county_name") or "").strip() != "Pecos":
        continue
    try:
        td = float(r["total_depth"]) if r.get("total_depth") not in (None, "") else None
    except ValueError:
        td = None
    try:
        sy = int(float(r["spud_year"])) if r.get("spud_year") not in (None, "") else None
    except ValueError:
        sy = None
    W.append((sy, td))

def block(label, rows):
    n = len(rows)
    wd = [t for s, t in rows if t is not None]
    lt3 = sum(1 for t in wd if t < 3000)
    lt5 = sum(1 for t in wd if t < 5000)
    ge10 = sum(1 for t in wd if t >= 10000)
    print("\n=== %s ===" % label)
    print("wells: %d   with recorded depth: %d   (no depth: %d)" % (n, len(wd), n - len(wd)))
    if wd:
        print("  <3000 ft : %d  = %.1f%% of depth-recorded   (definitionally vertical @3k)" % (lt3, 100*lt3/len(wd)))
        print("  <5000 ft : %d  = %.1f%% of depth-recorded   (definitionally vertical @5k)" % (lt5, 100*lt5/len(wd)))
        print("  >=5000ft : %d  = %.1f%%" % (len(wd)-lt5, 100*(len(wd)-lt5)/len(wd)))
        print("  >=10000ft: %d  = %.1f%%" % (ge10, 100*ge10/len(wd)))
        print("  median depth (depth-recorded): %.0f ft" % statistics.median(wd))
        # also express vs ALL wells (incl. no-depth) as a conservative lower bound
        print("  <3000 as %% of ALL %s wells (incl. no-depth): %.1f%%" % (label.split()[0], 100*lt3/n))
        print("  <5000 as %% of ALL wells: %.1f%%" % (100*lt5/n))

block("PECOS spud >= 2020", [(s, t) for s, t in W if s and s >= 2020])
block("PECOS spud >= 2015", [(s, t) for s, t in W if s and s >= 2015])
block("PECOS all years", W)

# depth histogram for >=2020 to sanity-check the 3k vs 5k line
wd20 = sorted(t for s, t in W if s and s >= 2020 and t is not None)
import bisect
edges = [1000, 2000, 3000, 4000, 5000, 7000, 10000, 15000, 30000]
print("\nPECOS >=2020 depth histogram (depth-recorded n=%d):" % len(wd20))
prev = 0
for e in edges:
    c = bisect.bisect_left(wd20, e) - bisect.bisect_left(wd20, prev)
    print("  %6d-%6d ft : %4d" % (prev, e, c))
    prev = e
print("  %6d+        ft : %4d" % (prev, len(wd20) - bisect.bisect_left(wd20, prev)))
