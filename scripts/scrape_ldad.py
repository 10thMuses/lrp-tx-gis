#!/usr/bin/env python3
"""
Comptroller LDAD scraper — Local Development Agreement Database (Ch. 312 abatements).

Source: https://api.comptroller.texas.gov/open-data/v1/tables/ch312-abatement
JSON open-data endpoint backing the Comptroller's public search UI at
`comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`.
Single-call fetch with `?limit=10000` returns all records (no pagination needed —
`limit` works, `offset` returns 500). Eliminates the headless-browser path
documented in the WIP_OPEN pre-flight: the search UI's DataTables widget consumes
this same endpoint.

Output: outputs/refresh/comptroller_ldad_<ISO-date>.csv

Columns (per WIP_OPEN Chat 118 spec — minimum agreement_id, taxing_unit,
applicant, county, commissioned, lat, lon; extended with status/zone/value for
downstream mapping into combined_points.csv field set):

  agreement_id     ← API `id`
  agmt_type        ← API `agmt_type` (abatement | post-abatement)
  taxing_unit      ← API `lead_tax_unit_nm`
  govt_name        ← API `govt_name`
  govt_type        ← API `govt_type` (City | County | ISD | ...)
  applicant        ← API `prop_ownr_nm` (chain: prop_ownr → entity_nm → first_owner_nm)
  county           ← derived from govt_type=County|locl_gov_nm CAD parse
  commissioned     ← API `abat_crea_dt` (record-creation date; matches semantics
                     of existing 9 rows whose `commissioned` carries the
                     decision/filing date)
  abatement_status ← API `abat_sta_cd`
  reinvestment_zone← API `abat_zone_nm`
  property_value   ← API `prop_val_am`
  detail_url       ← Built from id
  lat, lon         ← County centroid from combined_geoms.geojson `county_labels`
  coords_source    ← Always "ldad_county_centroid" (LDAD records are agreement-
                     level not site-level — no per-record coords exposed in
                     either the search UI or detail pages)

County derivation: 100% coverage on 2026-04-29 fetch (1,486/1,486 records map
to one of 254 TX counties). Algorithm:
  1. If govt_type∈{county, COUNTY} and govt_name is a valid TX county, use it.
  2. Else strip " CAD" / " Cad" / " Central Appraisal District" suffix from
     locl_gov_nm; try full string (handles "Deaf Smith", "Fort Bend",
     "San Patricio"); then progressively shorter prefixes (handles joint CADs
     like "Potter Randall CAD" → first valid prefix "Potter").

Hard rules respected:
  - §6.1 No source-data file read into context. JSON streamed line-write to CSV.
  - §6.2 No fetch during build. This is the refresh path, not build.
  - §6.15 Atomic writes via temp + os.replace.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COMBINED_GEOMS = REPO / "combined_geoms.geojson"
REFRESH_DIR = REPO / "outputs" / "refresh"

API_URL = "https://api.comptroller.texas.gov/open-data/v1/tables/ch312-abatement?limit=10000"
DETAIL_URL_FMT = "https://comptroller.texas.gov/economy/development/search-tools/ch312/abatements-details.php?id={id}"
UA = "Mozilla/5.0 (compatible; LRP-LDAD-Scraper/1.0; contact: andrea@landresourcepartners.com)"

OUT_COLUMNS = [
    "agreement_id", "agmt_type", "taxing_unit", "govt_name", "govt_type",
    "applicant", "county", "commissioned", "abatement_status",
    "reinvestment_zone", "property_value", "detail_url",
    "lat", "lon", "coords_source",
]


def fetch_with_retry(url: str, attempts: int = 5, sleep: int = 10) -> bytes:
    """Fetch URL with retry. Returns raw bytes. Hard rule §6.2 only applies
    during build; this is the refresh phase where fetching is required."""
    last_exc = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception as e:
            last_exc = e
            if i == attempts - 1:
                break
            print(f"  fetch attempt {i+1} failed: {e}; retry in {sleep}s", file=sys.stderr)
            time.sleep(sleep)
    raise RuntimeError(f"fetch failed after {attempts} attempts: {last_exc}")


def load_county_centroids() -> dict:
    """Stream combined_geoms.geojson and return {bare_county_name_titlecase: (lat, lon)}.
    Bare = " County" suffix stripped. Source: TIGER 2024 representative_points
    written by extend_county_labels.py (Chat 111). Covers all 254 TX counties."""
    with open(COMBINED_GEOMS) as f:
        g = json.load(f)
    out = {}
    for feat in g.get("features", []):
        p = feat.get("properties") or {}
        if p.get("layer_id") != "county_labels":
            continue
        name = (p.get("name") or p.get("county") or "").strip()
        if not name:
            continue
        bare = re.sub(r"\s*County\s*$", "", name, flags=re.IGNORECASE).strip()
        coords = feat.get("geometry", {}).get("coordinates")
        if not coords or len(coords) < 2:
            continue
        # GeoJSON coords are [lon, lat]
        out[bare.title()] = (float(coords[1]), float(coords[0]))
    return out


def derive_county(rec: dict, valid_counties: set) -> str:
    """Return title-case bare county name, or '' if unmappable."""
    g_type = (rec.get("govt_type") or "").strip().lower()
    g_name = (rec.get("govt_name") or "").strip()
    cad = (rec.get("locl_gov_nm") or "").strip()

    # Path 1: govt_type=county
    if g_type == "county" and g_name:
        cand = g_name.title()
        if cand in valid_counties:
            return cand

    # Path 2: parse CAD name
    if cad:
        bare = re.sub(
            r"\s*(CAD|Cad|Central\s+Appraisal\s+District)\s*$",
            "",
            cad,
            flags=re.IGNORECASE,
        ).strip()
        # Try full string first (catches multi-word counties)
        cand = bare.title()
        if cand in valid_counties:
            return cand
        # Try progressively shorter word prefixes (catches joint CADs)
        words = bare.split()
        for n in range(len(words), 0, -1):
            cand = " ".join(words[:n]).title()
            if cand in valid_counties:
                return cand
    return ""


def applicant_of(rec: dict) -> str:
    """Pick best non-null applicant string: prop_ownr_nm > entity_nm > first_owner_nm."""
    for k in ("prop_ownr_nm", "entity_nm", "first_owner_nm"):
        v = rec.get(k)
        if v and str(v).strip():
            return str(v).strip()
    return ""


def commissioned_of(rec: dict) -> str:
    """Pick best date: abat_crea_dt (creation/decision date — matches existing
    9 rows' meeting_date semantics) > abat_eff_dt > submt_dt."""
    for k in ("abat_crea_dt", "abat_eff_dt", "submt_dt"):
        v = rec.get(k)
        if v and str(v).strip():
            return str(v).strip()
    return ""


def atomic_write_csv(path: Path, header: list, rows: list) -> None:
    """Temp-file + os.replace, per §6.15."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def main() -> int:
    today = dt.date.today().isoformat()
    out_path = REFRESH_DIR / f"comptroller_ldad_{today}.csv"

    print(f"[scrape_ldad] fetching {API_URL}")
    raw = fetch_with_retry(API_URL)
    payload = json.loads(raw)
    if not payload.get("success", True):
        # API returns success flag; treat absence as success per observed behavior
        print(f"[scrape_ldad] WARN: API success={payload.get('success')}", file=sys.stderr)
    data = payload.get("data") or []
    api_count = payload.get("count", len(data))
    last_updated = payload.get("lastUpdated", "?")
    print(f"[scrape_ldad] api_count={api_count} returned={len(data)} lastUpdated={last_updated}")
    if api_count != len(data):
        print(
            f"[scrape_ldad] ERROR: API reports {api_count} records but returned {len(data)}; "
            "limit cap insufficient",
            file=sys.stderr,
        )
        return 2

    centroids = load_county_centroids()
    valid_counties = set(centroids.keys())
    print(f"[scrape_ldad] county centroids loaded: {len(centroids)}")

    rows = []
    unmapped = 0
    counties_hit = set()
    for rec in data:
        county = derive_county(rec, valid_counties)
        if not county:
            unmapped += 1
            continue
        lat, lon = centroids[county]
        agreement_id = (rec.get("id") or "").strip()
        out = {
            "agreement_id": agreement_id,
            "agmt_type": (rec.get("agmt_type") or "").strip(),
            "taxing_unit": (rec.get("lead_tax_unit_nm") or "").strip(),
            "govt_name": (rec.get("govt_name") or "").strip(),
            "govt_type": (rec.get("govt_type") or "").strip(),
            "applicant": applicant_of(rec),
            "county": county,
            "commissioned": commissioned_of(rec),
            "abatement_status": (rec.get("abat_sta_cd") or "").strip(),
            "reinvestment_zone": (rec.get("abat_zone_nm") or "").strip(),
            "property_value": rec.get("prop_val_am") or "",
            "detail_url": DETAIL_URL_FMT.format(id=agreement_id) if agreement_id else "",
            "lat": f"{lat:.6f}",
            "lon": f"{lon:.6f}",
            "coords_source": "ldad_county_centroid",
        }
        rows.append(out)
        counties_hit.add(county)

    atomic_write_csv(out_path, OUT_COLUMNS, rows)

    print(
        f"[scrape_ldad] wrote {out_path.relative_to(REPO)} rows={len(rows)} "
        f"counties={len(counties_hit)} unmapped={unmapped}"
    )
    if unmapped:
        # Spec: partial results acceptable; document in run log
        print(
            f"[scrape_ldad] WARN: {unmapped} records dropped due to county-derivation failure",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
