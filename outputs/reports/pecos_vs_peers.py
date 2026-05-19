import csv, collections, statistics

REPO = "/home/andreahimmel/lrp-tx-gis"
SUBJ = "Pecos"
OTHER5 = ["Reeves", "Ward", "Midland", "Martin", "Reagan"]
ALL6 = [SUBJ] + OTHER5

# --- Wells spudded >= 2020 by county; shallow <3000 share ---
w_cnt = collections.Counter()
w_sh = collections.Counter()
for r in csv.DictReader(open(REPO + "/data/wells_permian6.csv", encoding="utf-8")):
    c = (r.get("county_name") or "").strip()
    if c not in ALL6:
        continue
    try:
        sy = int(float(r["spud_year"])) if r.get("spud_year") not in (None, "") else None
    except ValueError:
        sy = None
    if sy is None or sy < 2020:
        continue
    w_cnt[c] += 1
    try:
        td = float(r["total_depth"]) if r.get("total_depth") not in (None, "") else None
    except ValueError:
        td = None
    if td is not None and td < 3000:
        w_sh[c] += 1

print("=== WELLS SPUDDED >= 2020 (by county) ===")
print("%-9s %8s %8s %8s" % ("county", "wells", "shal<3k", "shal%"))
for c in ALL6:
    n = w_cnt[c]; s = w_sh[c]
    print("%-9s %8d %8d %7.0f%%" % (c, n, s, (100*s/n if n else 0)))
o_w = [w_cnt[c] for c in OTHER5]
o_shpct = [(100*w_sh[c]/w_cnt[c] if w_cnt[c] else 0) for c in OTHER5]
print("-- other5 avg wells/county = %.0f  (range %d-%d)" % (statistics.mean(o_w), min(o_w), max(o_w)))
print("-- other5 avg shallow%% = %.0f%%" % statistics.mean(o_shpct))
print("-- PECOS wells=%d  shallow%%=%.0f%%" % (w_cnt[SUBJ], 100*w_sh[SUBJ]/w_cnt[SUBJ]))

# --- Authoritative W-1 wellbore profile >= 2020 by county ---
prof = {c: collections.Counter() for c in ALL6}
cov = {c: collections.Counter() for c in ALL6}
try:
    for r in csv.DictReader(open(REPO + "/outputs/refresh/rrc_w1_permits.csv", encoding="utf-8", errors="replace")):
        c = (r.get("county_name") or "").strip().title()
        if c not in ALL6:
            continue
        try:
            yc = int(float(r.get("year_chunk") or 0))
        except ValueError:
            yc = 0
        cov[c][yc] += 1
        if yc >= 2020:
            prof[c][(r.get("wb_profile") or "").strip().lower()] += 1
    print("\n=== W-1 WELLBORE PROFILE >= 2020 (authoritative) ===")
    print("%-9s %7s %7s %7s %7s" % ("county", "permits", "horiz", "vert", "horiz%"))
    hpcts = {}
    for c in ALL6:
        p = prof[c]
        H = sum(v for k, v in p.items() if k.startswith("h"))
        V = sum(v for k, v in p.items() if k.startswith("v"))
        tot = sum(p.values())
        hp = (100*H/tot if tot else 0)
        hpcts[c] = hp
        yrs = sorted(y for y in cov[c] if y)
        print("%-9s %7d %7d %7d %6.0f%%   yr_coverage=%s..%s" % (
            c, tot, H, V, hp, (yrs[0] if yrs else "-"), (yrs[-1] if yrs else "-")))
    o_hp = [hpcts[c] for c in OTHER5]
    print("-- other5 avg horizontal%% = %.0f%%   PECOS = %.0f%%" % (statistics.mean(o_hp), hpcts[SUBJ]))
except FileNotFoundError:
    print("W-1 file not found")
