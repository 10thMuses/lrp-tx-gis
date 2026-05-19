import csv, collections, re

REPO = "/home/andreahimmel/lrp-tx-gis"

def apikey(s):
    d = re.sub(r"\D", "", s or "")
    return d[-8:] if len(d) >= 8 else d

# oil/gas from dbo900 wells (permit file has none)
og_by_api = {}
for r in csv.DictReader(open(REPO + "/data/wells_permian6.csv", encoding="utf-8")):
    if (r.get("county_name") or "").strip() != "Pecos":
        continue
    k = apikey(r.get("api_no")); o = (r.get("oil_gas") or "").strip().upper()
    if k and o and k not in og_by_api:
        og_by_api[k] = o

rows = []
for r in csv.DictReader(open(REPO + "/outputs/refresh/rrc_w1_permits.csv", encoding="utf-8", errors="replace")):
    if (r.get("county_name") or "").strip().upper() != "PECOS":
        continue
    try:
        yc = int(float(r.get("year_chunk") or 0))
    except ValueError:
        yc = 0
    if yc < 2020:
        continue
    try:
        td = float(r["total_depth"]) if r.get("total_depth") not in (None, "") else None
    except ValueError:
        td = None
    rows.append({
        "op": (r.get("operator_name") or "").strip(),
        "prof": (r.get("wb_profile") or "").strip().lower(),
        "purpose": (r.get("filing_purpose") or "").strip(),
        "status": (r.get("status") or "").strip(),
        "amended": (r.get("is_amended") or "").strip(),
        "td": td,
        "og": og_by_api.get(apikey(r.get("api_no"))),
    })

N = len(rows)
print("Pecos W-1 permits, year_chunk>=2020:", N)

def dist(label, key, top=8):
    c = collections.Counter(key(x) for x in rows)
    print("\n%s:" % label)
    for k, v in c.most_common(top):
        print("  %4d  %5.1f%%  %s" % (v, 100.0*v/N, k if k != "" else "(blank)"))

def depth_bucket(x):
    t = x["td"]
    if t is None: return "(no depth)"
    if t < 3000: return "<3,000 ft"
    if t < 10000: return "3,000-9,999 ft"
    return ">=10,000 ft"

dist("By wellbore profile", lambda x: x["prof"])
dist("By filing purpose", lambda x: x["purpose"])
dist("By status (current queue)", lambda x: x["status"])
dist("By depth bucket (permit total_depth - weak proxy)", depth_bucket)
ogc = collections.Counter(x["og"] for x in rows if x["og"])
matched = sum(ogc.values())
print("\nBy oil/gas target (joined from wells file; matched %d of %d = %.0f%%):" % (matched, N, 100.0*matched/N))
for k, v in ogc.most_common():
    lab = {"O": "Oil", "G": "Gas"}.get(k, k)
    print("  %4d  %5.1f%% of matched  %s" % (v, 100.0*v/max(1, matched), lab))

print("\n=== TOP 8 OPERATORS x dimensions ===")
opc = collections.Counter(x["op"] for x in rows)
for op, tot in opc.most_common(8):
    sub = [x for x in rows if x["op"] == op]
    H = sum(1 for x in sub if x["prof"].startswith("h"))
    V = sum(1 for x in sub if x["prof"].startswith("v"))
    sh = sum(1 for x in sub if x["td"] is not None and x["td"] < 3000)
    dp = sum(1 for x in sub if x["td"] is not None and x["td"] >= 10000)
    appr = sum(1 for x in sub if x["status"].lower().startswith("appr"))
    purp = collections.Counter(x["purpose"] for x in sub).most_common(1)
    og = collections.Counter(x["og"] for x in sub if x["og"])
    print("\n%s  (n=%d, %.1f%% of all)" % (op, tot, 100.0*tot/N))
    print("  profile: H=%d V=%d (%.0f%% H)" % (H, V, 100.0*H/max(1, H+V)))
    print("  depth: <3k=%d  >=10k=%d  (of %d w/depth)" % (sh, dp, sum(1 for x in sub if x["td"] is not None)))
    print("  status approved: %d (%.0f%%)   top purpose: %s   oil/gas matched: %s"
          % (appr, 100.0*appr/tot, (purp[0][0] if purp else "-"),
             dict({"O": "Oil", "G": "Gas"}.get(k, k) for k in []) or {("Oil" if k=="O" else "Gas" if k=="G" else k): v for k, v in og.items()}))
