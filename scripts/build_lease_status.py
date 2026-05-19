#!/usr/bin/env python3
"""Precompute per-lease trailing production from the RRC PDQ bulk dump, so the
map build can reclassify "active" wells that are effectively no longer
producing.

Rule (set by the owner's advisor): take the trailing 6 full months of PDQ
production for each lease; if the average **natural gas** rate is below
125 Mcf/day (= 125,000 cubic feet/day) AND average oil is below 150 bbl/day,
the wells on that lease are flagged "no longer producing." Both the gas-only
count and the gas+oil count are reported.

RRC reports production at the LEASE level (oil) and lease/gas-well level (gas);
PDQ's finest grain is (oil_gas, district, lease) x cycle-month. Wells join to a
lease via wells_permian6.csv (oil_gas, district, lease_no).

Output: data/lease_status.csv  (small, committed, auditable)
  columns: oil_gas,district,lease_no,gas_mcf_d,oil_bbl_d,window,months_present
"""
import calendar, csv, io, os, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "rrc_raw" / "PDQ_DSV.zip"
OUT = ROOT / "data" / "lease_status.csv"
DELIM = "}"
SCOPE = {"PECOS", "REEVES", "WARD", "MIDLAND", "MARTIN", "REAGAN"}
TRAIL_MONTHS = 6
GAS_THRESH_MCFD = 125.0      # 125,000 cf/day
OIL_GUARD_BPD = 150.0        # oil also below this/day to count as no-longer-producing


def stream_dsv(z, name):
    with z.open(name) as raw:
        text = io.TextIOWrapper(raw, encoding="utf-8", errors="replace")
        header = text.readline().rstrip("\r\n").split(DELIM)
        for line in text:
            line = line.rstrip("\r\n")
            if not line:
                continue
            vals = line.split(DELIM)
            if len(vals) < len(header):
                vals += [""] * (len(header) - len(vals))
            yield dict(zip(header, vals[: len(header)]))


def f(s):
    try:
        return float(s or 0)
    except ValueError:
        return 0.0


def main():
    if not RAW.exists():
        print(f"ERROR: {RAW} not found (run scripts/fetch_pdq_dump.py)", file=sys.stderr)
        return 2
    with zipfile.ZipFile(RAW, "r") as z:
        cmap = {}
        for r in stream_dsv(z, "GP_COUNTY_DATA_TABLE.dsv"):
            no = (r.get("COUNTY_NO") or "").strip()
            if no:
                cmap[no] = (r.get("COUNTY_NAME") or "").strip().upper()
        scope_nos = {no for no, nm in cmap.items() if nm in SCOPE}
        print("scope county_nos:", sorted(scope_nos), file=sys.stderr)

        # (og,dist,lease) -> {ym: [gas_mcf, oil_bbl]}
        lease = {}
        allyms = set()
        n = 0
        for r in stream_dsv(z, "OG_COUNTY_LEASE_CYCLE_DATA_TABLE.dsv"):
            if (r.get("COUNTY_NO") or "").strip() not in scope_nos:
                continue
            ym = (r.get("CYCLE_YEAR_MONTH") or "").strip()
            if len(ym) < 6:
                continue
            n += 1
            og = (r.get("OIL_GAS_CODE") or "").strip()
            dist = (r.get("DISTRICT_NO") or "").strip()
            lno = (r.get("LEASE_NO") or "").strip()
            gas = f(r.get("CNTY_LSE_GAS_PROD_VOL")) + f(r.get("CNTY_LSE_CSGD_PROD_VOL"))
            oil = f(r.get("CNTY_LSE_OIL_PROD_VOL")) + f(r.get("CNTY_LSE_COND_PROD_VOL"))
            d = lease.setdefault((og, dist, lno), {})
            cur = d.get(ym)
            if cur:
                cur[0] += gas; cur[1] += oil
            else:
                d[ym] = [gas, oil]
            allyms.add(ym)
        print(f"scanned {n:,} in-scope lease-months; {len(lease):,} leases", file=sys.stderr)

    yms = sorted(allyms)
    window = yms[-TRAIL_MONTHS:]
    win_days = 0
    for ym in window:
        try:
            y, m = int(ym[:4]), int(ym[4:6])
            win_days += calendar.monthrange(y, m)[1]
        except ValueError:
            win_days += 30
    win_days = win_days or 1
    print(f"trailing window: {window[0]}..{window[-1]} ({win_days} days)", file=sys.stderr)

    below_gas = below_both = 0
    rows = []
    for (og, dist, lno), d in lease.items():
        g = sum(d.get(ym, [0, 0])[0] for ym in window)
        o = sum(d.get(ym, [0, 0])[1] for ym in window)
        gmd = g / win_days
        obd = o / win_days
        present = sum(1 for ym in window if ym in d)
        if gmd < GAS_THRESH_MCFD:
            below_gas += 1
            if obd < OIL_GUARD_BPD:
                below_both += 1
        rows.append((og, dist, lno, round(gmd, 2), round(obd, 2), f"{window[0]}-{window[-1]}", present))

    tmp = str(OUT) + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["oil_gas", "district", "lease_no", "gas_mcf_d", "oil_bbl_d", "window", "months_present"])
        w.writerows(rows)
    os.replace(tmp, OUT)
    print(f"wrote {OUT} ({len(rows):,} leases)", file=sys.stderr)
    print(f"leases below {GAS_THRESH_MCFD:.0f} Mcf/d gas: {below_gas:,}", file=sys.stderr)
    print(f"  of those also below {OIL_GUARD_BPD:.0f} bbl/d oil (=> 'no longer producing'): {below_both:,}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
