"""Decisive check: do Pecos wells the dbo900 wellbore file calls <3,000 ft
actually carry a VERTICAL designation in the authoritative RRC W-1 Wellbore
Profile field? Join dbo900 (spud >= 2020) to W-1 by normalized API."""
import csv, collections, re

REPO = "/home/andreahimmel/lrp-tx-gis"

def apikey(s):
    d = re.sub(r"\D", "", s or "")
    # dbo900 = 42-371-38311 (10-ish digits incl state 42); W-1 = 371-38311.
    # Normalize to county(3)+unique(5) = last 8 digits.
    return d[-8:] if len(d) >= 8 else d

# W-1 authoritative profile by API (Pecos)
w1 = {}
for r in csv.DictReader(open(REPO + "/outputs/refresh/rrc_w1_permits.csv", encoding="utf-8", errors="replace")):
    if (r.get("county_name") or "").strip().upper() != "PECOS":
        continue
    k = apikey(r.get("api_no"))
    p = (r.get("wb_profile") or "").strip().lower()
    if k and p:
        # prefer an explicit horizontal/vertical over blank/dir if multiple
        if k not in w1 or (w1[k] not in ("horizontal", "vertical") and p in ("horizontal", "vertical")):
            w1[k] = p
print("W-1 Pecos APIs with a profile:", len(w1))

shallow = collections.Counter()
deep = collections.Counter()
sh_n = dp_n = sh_match = dp_match = 0
for r in csv.DictReader(open(REPO + "/data/wells_permian6.csv", encoding="utf-8")):
    if (r.get("county_name") or "").strip() != "Pecos":
        continue
    try:
        sy = int(float(r["spud_year"])) if r.get("spud_year") not in (None, "") else None
    except ValueError:
        sy = None
    if sy is None or sy < 2020:
        continue
    try:
        td = float(r["total_depth"]) if r.get("total_depth") not in (None, "") else None
    except ValueError:
        td = None
    if td is None:
        continue
    k = apikey(r.get("api_no"))
    prof = w1.get(k)
    if td < 3000:
        sh_n += 1
        if prof:
            sh_match += 1
            shallow[prof] += 1
    else:
        dp_n += 1
        if prof:
            dp_match += 1
            deep[prof] += 1

def pct(c):
    t = sum(c.values()) or 1
    H = sum(v for kk, v in c.items() if kk.startswith("h"))
    V = sum(v for kk, v in c.items() if kk.startswith("v"))
    return H, V, t, 100.0 * H / t, 100.0 * V / t

print("\n=== Pecos wells SPUD >=2020, dbo900 TD < 3,000 ft ===")
print("count=%d  matched to W-1 profile=%d (%.0f%%)" % (sh_n, sh_match, 100.0*sh_match/max(1, sh_n)))
H, V, t, hp, vp = pct(shallow)
print("  of matched: horizontal=%d (%.1f%%)  vertical=%d (%.1f%%)  raw=%s" % (H, hp, V, vp, dict(shallow)))

print("\n=== Pecos wells SPUD >=2020, dbo900 TD >= 3,000 ft ===")
print("count=%d  matched to W-1 profile=%d (%.0f%%)" % (dp_n, dp_match, 100.0*dp_match/max(1, dp_n)))
H, V, t, hp, vp = pct(deep)
print("  of matched: horizontal=%d (%.1f%%)  vertical=%d (%.1f%%)  raw=%s" % (H, hp, V, vp, dict(deep)))
