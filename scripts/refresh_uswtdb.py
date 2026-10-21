"""
USWTDB refresh — produces wind_<date>.csv.

Source: https://eersc.usgs.gov/api/uswtdb/v1/turbines (PostgREST).
No auth. Geographic filter: `t_state=eq.TX`. Pagination via Range/limit; the
endpoint caps single responses at 1000 rows so we paginate by `case_id`.

Schema match: outputs follow `combined_points.csv` 31-column layout. Wind has
no operator field in USWTDB (p_owner was deprecated); `operator` stays blank
and is filled from the project layer when available downstream.

`capacity_mw` is computed from `t_cap` (kW) per Chat 75 coalesce convention.

Alternate source (file release, valid TLS cert) -- use when eersc.usgs.gov's
cert is expired. Do NOT disable TLS verification; use one of:
    python scripts/refresh_uswtdb.py --from-file path/to/uswtdb_V9_1_YYYYMMDD.csv   (or the .zip)
    python scripts/refresh_uswtdb.py --from-url https://energy.usgs.gov/uswtdb/assets/data/uswtdbCSV.zip
The file release carries the same column names as the API (t_state, t_county,
p_year, t_cap, xlong, ylat, ...); only t_state == TX rows are kept.

Usage:
    python scripts/refresh_uswtdb.py [--out outputs/refresh] [--from-file F | --from-url U]

Exit codes:
    0  CSV written non-empty
    1  fetch failed (logged FETCH_FAILED, no partial output)
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

UA = "LRP-TX-GIS/1.0 (refinement-uswtdb-refresh)"
BASE = "https://eersc.usgs.gov/api/uswtdb/v1/turbines"
PAGE = 1000

SCHEMA = [
    "layer_id", "lat", "lon", "name", "plant_code", "county", "technology",
    "capacity", "sector", "inr", "fuel", "mw", "zone", "poi", "entity",
    "funnel_stage", "group", "under_construction", "commissioned",
    "capacity_mw", "operator", "voltage", "osm_id", "depth_ft", "use",
    "aquifer", "project", "manu", "model", "cap_kw", "year",
]


def fetch_with_retry(url, attempts=5, sleep=10):
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception as e:
            last = e
            sys.stderr.write(f"[fetch-retry {i+1}/{attempts}] {url}: {e}\n")
            time.sleep(sleep)
    raise last


def fetch_all_tx():
    """Paginate by case_id ascending. PostgREST default sort isn't guaranteed,
    so explicit `order=case_id.asc` and cursor on last seen case_id."""
    all_rows = []
    last_id = None
    while True:
        params = [
            "t_state=eq.TX",
            f"limit={PAGE}",
            "order=case_id.asc",
        ]
        if last_id is not None:
            params.append(f"case_id=gt.{last_id}")
        url = f"{BASE}?{'&'.join(params)}"
        blob = fetch_with_retry(url)
        page = json.loads(blob.decode("utf-8"))
        if not page:
            break
        all_rows.extend(page)
        last_id = page[-1].get("case_id")
        sys.stderr.write(f"[uswtdb] fetched {len(all_rows)} (cursor case_id={last_id})\n")
        if len(page) < PAGE:
            break
    return all_rows


def load_tx_from_file(path):
    """Read TX turbines from a USWTDB file release (.csv or .zip containing one)."""
    import io
    import zipfile
    p = Path(path)
    if p.suffix.lower() == ".zip":
        with zipfile.ZipFile(p) as z:
            names = [n for n in z.namelist() if n.lower().endswith(".csv")]
            if not names:
                raise RuntimeError(f"no .csv inside {p}")
            raw = z.read(names[0])
            src = names[0]
    else:
        raw = p.read_bytes()
        src = p.name
    sys.stderr.write(f"[uswtdb] reading file release {src}\n")
    rd = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    rows = [r for r in rd if (r.get("t_state") or "").strip().upper() == "TX"]
    # Match API ordering (case_id asc)
    rows.sort(key=lambda r: int(r["case_id"]) if (r.get("case_id") or "").isdigit() else 0)
    return rows


def download_to_tmp(url):
    """Download a file release over normal (verified) TLS to a temp file."""
    import tempfile
    blob = fetch_with_retry(url)
    suffix = ".zip" if url.lower().endswith(".zip") else ".csv"
    fd, tmp = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as f:
        f.write(blob)
    sys.stderr.write(f"[uswtdb] downloaded {len(blob)} bytes from {url}\n")
    return tmp


def empty_row():
    return {col: "" for col in SCHEMA}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="outputs/refresh")
    ap.add_argument("--from-file", help="USWTDB file release (.csv or .zip); skips the API")
    ap.add_argument("--from-url", help="URL of a USWTDB file release (.csv/.zip) with a valid TLS cert; skips the API")
    args = ap.parse_args()

    today = date.today().isoformat()

    try:
        if args.from_file:
            turbines = load_tx_from_file(args.from_file)
        elif args.from_url:
            turbines = load_tx_from_file(download_to_tmp(args.from_url))
        else:
            turbines = fetch_all_tx()
    except Exception as e:
        sys.stderr.write(f"FETCH_FAILED: {e}\n")
        return 1

    if not turbines:
        sys.stderr.write("ERROR: USWTDB returned 0 TX turbines\n")
        return 1

    out_rows = []
    for t in turbines:
        try:
            lat = float(t.get("ylat")) if t.get("ylat") is not None else None
            lon = float(t.get("xlong")) if t.get("xlong") is not None else None
        except (TypeError, ValueError):
            lat = lon = None
        if lat is None or lon is None:
            continue
        if not (25.0 < lat < 37.0 and -107.0 < lon < -93.0):
            continue

        cap_kw = t.get("t_cap")
        try:
            cap_kw_f = float(cap_kw) if cap_kw not in (None, "") else None
        except (TypeError, ValueError):
            cap_kw_f = None
        capacity_mw = round(cap_kw_f / 1000.0, 3) if cap_kw_f else ""

        row = empty_row()
        row.update({
            "layer_id": "wind",
            "lat": lat, "lon": lon,
            "county": str(t.get("t_county") or "").strip().upper(),
            "commissioned": str(t.get("p_year") or "").strip(),
            "capacity_mw": capacity_mw,
            "project": str(t.get("p_name") or "").strip(),
            "manu": str(t.get("t_manu") or "").strip(),
            "model": str(t.get("t_model") or "").strip(),
            "cap_kw": cap_kw_f if cap_kw_f is not None else "",
            "year": str(t.get("p_year") or "").strip(),
        })
        out_rows.append(row)

    out_path = Path(args.out) / f"wind_{today}.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SCHEMA)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    sys.stderr.write(f"[wrote] {out_path} ({len(out_rows)} rows)\n")

    if not out_rows:
        sys.stderr.write("ERROR: wind_*.csv empty after filtering\n")
        return 1
    src = args.from_file or args.from_url or f"{BASE}?t_state=eq.TX"
    print(f"OK wind={len(out_rows)} src={src}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
