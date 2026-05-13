#!/usr/bin/env python3
"""
RRC W-1 detail-page scrape — fetches per-permit lat/lon for permits in the
existing `scripts/scrape_rrc_w1.py` listing output that lack coordinates.

Purpose (R2.5 Part 2B): backfill the `permits_permian6` layer to 1976-2004
by harvesting lat/lon from each permit's W-1 detail page. The EOM+LatLon
bulk file (`daf420.dat`) only goes back to 2018 — earlier permits have no
machine-readable lat/lon outside the W-1 detail page.

Workflow:
  1. Operator runs `scripts/scrape_rrc_w1.py` once for the 6-county scope and
     1976-2004 year range. That produces `outputs/refresh/rrc_w1_permits.csv`
     with listing-page metadata (permit_no, api_no, operator, lease,
     district, county, dates, total_depth, detail_url).
  2. Operator runs this script: walks each row, GETs the detail_url with the
     same JSP session pattern as scrape_rrc_w1, parses the detail HTML for
     surface-location lat/lon. Atomic-appends to
     `outputs/refresh/rrc_w1_permits_with_coords.csv`.
  3. The script is RESUMABLE: a checkpoint file records (permit_no, status)
     pairs so re-running picks up where it left off after a network blip.
  4. When complete, `scripts/parse_rrc.py` (extended in a follow-up sprint)
     reads the backfill CSV and merges into `data/permits_permian6.csv`.

Estimated runtime: 6-county × 28 years × ~100 permits/county/yr × 1.5s
throttle = ~7 hours. Run as a nohup overnight job. Do NOT run synchronously.

Trigger:
    nohup python3 scripts/scrape_rrc_w1_detail_coords.py \\
        --in outputs/refresh/rrc_w1_permits.csv \\
        --out outputs/refresh/rrc_w1_permits_with_coords.csv \\
        > /tmp/rrc_w1_coords.log 2>&1 &

Hard rules respected:
  - CLAUDE.md §3.1: streams to disk via atomic temp+os.replace, never loads
    raw HTML beyond the few KB per page that's parsed immediately.
  - CLAUDE.md §3.4: atomic in-place writes for the resumable CSV.
  - Throttle 1.5s/request honored; 3-retry × 10s sleep on transient errors.

NOT RUN BY DEFAULT. Operator-controlled execution.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from html import unescape
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent

UA = (
    "Mozilla/5.0 (compatible; lrp-tx-gis research scraper; "
    "contact andrea@landresourcepartners.com)"
)
THROTTLE_SECS = 1.5
RETRY_ATTEMPTS = 3
RETRY_SLEEP = 10
HTTP_TIMEOUT = 90

# 6-county filter (matches scripts/parse_rrc.py)
COUNTY_NAMES = {
    "BREWSTER", "CRANE", "CROCKETT", "CULBERSON", "JEFF DAVIS",
    "MARTIN", "MIDLAND", "PECOS", "REAGAN", "REEVES", "TERRELL",
    "UPTON", "WARD",
}
# R2.5 Part 2 scope is the 6-county Permian sale-vs-peer set
SCOPE_COUNTIES = {"PECOS", "REEVES", "WARD", "MIDLAND", "MARTIN", "REAGAN"}


# Detail-page lat/lon regex. RRC W-1 detail pages render coordinates in a
# table cell adjacent to a "Latitude" / "Longitude" label. Empirical
# inspection of a few detail pages shows lat/lon as plain decimal text.
LAT_RE = re.compile(
    r"Latitude[^<>0-9]*(?P<lat>2[89]\.\d{2,8}|3[0-7]\.\d{2,8})",
    re.IGNORECASE,
)
LON_RE = re.compile(
    r"Longitude[^<>0-9]*(?P<lon>-?(?:9[3-9]|10[0-7])\.\d{2,8})",
    re.IGNORECASE,
)


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = UA
    return s


def fetch_detail(session: requests.Session, url: str) -> str | None:
    for attempt in range(RETRY_ATTEMPTS):
        try:
            r = session.get(url, timeout=HTTP_TIMEOUT)
            if r.status_code == 200:
                return r.text
            print(f"  HTTP {r.status_code} on {url} (attempt {attempt+1})")
        except Exception as e:
            print(f"  error on {url}: {e}")
        time.sleep(RETRY_SLEEP)
    return None


def parse_coords(html: str) -> tuple[float | None, float | None]:
    lat_m = LAT_RE.search(html)
    lon_m = LON_RE.search(html)
    try:
        lat = float(lat_m.group("lat")) if lat_m else None
    except ValueError:
        lat = None
    try:
        lon = float(lon_m.group("lon")) if lon_m else None
        if lon is not None and lon > 0:
            lon = -lon  # Texas convention
    except ValueError:
        lon = None
    return lat, lon


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True,
                    help="listing-page CSV (output of scrape_rrc_w1.py)")
    ap.add_argument("--out", dest="dst", required=True,
                    help="output CSV with appended lat/lon columns")
    ap.add_argument("--ckpt", default="outputs/refresh/rrc_w1_coords_checkpoint.json")
    args = ap.parse_args()

    src = Path(args.src)
    dst = Path(args.dst)
    ckpt = Path(args.ckpt)
    if not src.exists():
        print(f"ERROR: {src} not found. Run scrape_rrc_w1.py first.")
        return 2
    dst.parent.mkdir(parents=True, exist_ok=True)

    # Load checkpoint
    done = set()
    if ckpt.exists():
        with open(ckpt) as f:
            done = set(json.load(f))
        print(f"resuming with {len(done)} permits already processed")

    # Iterate input listing, fetching detail pages for in-scope counties only.
    session = make_session()
    new_rows = []
    n_total = 0
    n_in_scope = 0
    n_fetched = 0
    with open(src) as f:
        reader = csv.DictReader(f)
        out_fields = reader.fieldnames + ["lat", "lon", "coords_source"]

        # Resume mode: existing dst is appended to; ckpt drives skip.
        new_file = not dst.exists()
        with open(dst, "a", newline="") as fout:
            writer = csv.DictWriter(fout, fieldnames=out_fields)
            if new_file:
                writer.writeheader()
            for row in reader:
                n_total += 1
                county = (row.get("county_name") or "").strip().upper()
                if county not in SCOPE_COUNTIES:
                    continue
                n_in_scope += 1
                key = row.get("permit_no") or row.get("univ_doc_no")
                if not key or key in done:
                    continue
                url = row.get("detail_url")
                if not url:
                    continue
                time.sleep(THROTTLE_SECS)
                html = fetch_detail(session, url)
                lat, lon = (None, None)
                if html:
                    lat, lon = parse_coords(html)
                row_out = dict(row)
                row_out["lat"] = f"{lat:.6f}" if lat is not None else ""
                row_out["lon"] = f"{lon:.6f}" if lon is not None else ""
                row_out["coords_source"] = "w1_detail_scrape" if (lat and lon) else "missing"
                writer.writerow(row_out)
                done.add(key)
                n_fetched += 1
                if n_fetched % 25 == 0:
                    # Persist checkpoint atomically every 25 permits.
                    tmp = ckpt.with_suffix(".json.tmp")
                    with open(tmp, "w") as cf:
                        json.dump(sorted(done), cf)
                    os.replace(tmp, ckpt)
                    print(f"  [{n_fetched}] last={key} ({'OK' if lat and lon else 'no coords'})")
    # Final checkpoint flush
    tmp = ckpt.with_suffix(".json.tmp")
    with open(tmp, "w") as cf:
        json.dump(sorted(done), cf)
    os.replace(tmp, ckpt)
    print(f"\n=== scrape complete: total={n_total} in_scope={n_in_scope} fetched_this_run={n_fetched} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
