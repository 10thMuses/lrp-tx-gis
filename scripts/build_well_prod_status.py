#!/usr/bin/env python3
"""Build an API-level production-status lookup using RRC's authoritative
API->lease crosswalk (OG_WELL_COMPLETION_DATA_TABLE in PDQ_DSV.zip), so the
map can reclassify wells by *API* instead of guessing the wellbore file's
lease_no formatting (which only matched ~31% of wells).

Reuses the already-computed data/lease_status.csv (per-lease trailing-6-month
gas/oil from PDQ OG_COUNTY_LEASE_CYCLE). For every well completion this:
  API (county+unique, 8 digits)  ->  (oil_gas, district, lease_no)  ->  lease_status

Output: data/well_prod_status.csv  (api8, gas_mcf_d, oil_bbl_d)
"""
import csv, io, os, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "rrc_raw" / "PDQ_DSV.zip"
LEASE_STATUS = ROOT / "data" / "lease_status.csv"
OUT = ROOT / "data" / "well_prod_status.csv"
DELIM = "}"
TABLE = "OG_WELL_COMPLETION_DATA_TABLE.dsv"
# 6-county Permian API county codes (same FIPS as parse_rrc COUNTIES).
SCOPE_CNTY = {"317", "329", "371", "383", "389", "475"}


def stream_dsv(z, name):
    with z.open(name) as raw:
        text = io.TextIOWrapper(raw, encoding="utf-8", errors="replace")
        header = text.readline().rstrip("\r\n").split(DELIM)
        idx = {h: i for i, h in enumerate(header)}
        for line in text:
            line = line.rstrip("\r\n")
            if not line:
                continue
            v = line.split(DELIM)
            if len(v) < len(header):
                v += [""] * (len(header) - len(v))
            yield v, idx


def main():
    if not RAW.exists() or not LEASE_STATUS.exists():
        print("ERROR: need PDQ_DSV.zip and data/lease_status.csv", file=sys.stderr)
        return 2

    lease = {}
    for r in csv.DictReader(open(LEASE_STATUS, encoding="utf-8")):
        k = ((r["oil_gas"] or "").strip().upper()[:1],
             (r["district"] or "").strip().lstrip("0"),
             (r["lease_no"] or "").strip().lstrip("0"))
        try:
            lease[k] = (float(r["gas_mcf_d"] or 0), float(r["oil_bbl_d"] or 0))
        except ValueError:
            pass
    print(f"lease_status rows: {len(lease):,}", file=sys.stderr)

    api_prod = {}
    n = scoped = mapped = 0
    with zipfile.ZipFile(RAW, "r") as z:
        for v, idx in stream_dsv(z, TABLE):
            n += 1
            cc = (v[idx["API_COUNTY_CODE"]] or "").strip()
            if cc.lstrip("0").zfill(3) not in SCOPE_CNTY and cc not in SCOPE_CNTY:
                continue
            scoped += 1
            uniq = (v[idx["API_UNIQUE_NO"]] or "").strip()
            api8 = cc.zfill(3) + uniq.zfill(5)
            k = ((v[idx["OIL_GAS_CODE"]] or "").strip().upper()[:1],
                 (v[idx["DISTRICT_NO"]] or "").strip().lstrip("0"),
                 (v[idx["LEASE_NO"]] or "").strip().lstrip("0"))
            rec = lease.get(k)
            if rec is not None:
                # keep the lowest-gas (most conservative "still producing"
                # evidence) if an API has multiple completion rows.
                cur = api_prod.get(api8)
                if cur is None or rec[0] < cur[0]:
                    api_prod[api8] = rec
                mapped += 1
    print(f"completion rows: {n:,}  in-scope: {scoped:,}  api->lease->status: {len(api_prod):,} APIs", file=sys.stderr)

    tmp = str(OUT) + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["api8", "gas_mcf_d", "oil_bbl_d"])
        for a, (g, o) in api_prod.items():
            w.writerow([a, round(g, 2), round(o, 2)])
    os.replace(tmp, OUT)
    print(f"wrote {OUT} ({len(api_prod):,} APIs)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
