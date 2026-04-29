#!/usr/bin/env python3
"""
Merge a Comptroller LDAD refresh CSV into combined_points.csv.

Per WIP_OPEN Chat 118:
  - Drop existing tax_abatements rows from combined_points.csv.
  - Append LDAD rows under the same layer_id.
  - Atomic write via temp + os.replace (§6.15).
  - No schema change to tax_abatements field set beyond what's already present.

Field mapping (LDAD CSV column → combined_points.csv column):
  agreement_id     → inr            (generic identifier slot, already in schema)
  agmt_type        → (folded into funnel_stage)
  taxing_unit      → entity
  applicant        → operator
  county           → county
  commissioned     → commissioned
  abatement_status → (folded into funnel_stage)
  reinvestment_zone→ project
  property_value   → (dropped — combined_points has no money field; preserved
                     in refresh CSV for downstream queries)
  detail_url       → poi             (existing 9 rows already use poi for URLs)
  lat, lon         → lat, lon
  coords_source    → coords_source

Derived combined_points fields:
  layer_id   = "tax_abatements"
  name       = applicant or reinvestment_zone or f"{county} abatement {agreement_id}"
  funnel_stage = "{agmt_type}|{status_lower}" (e.g., "abatement|expired")
  group      = "Permits"
  year       = first 4 chars of commissioned (or blank)
  All other columns (plant_code, technology, capacity, sector, fuel, mw, zone,
  under_construction, capacity_mw, voltage, osm_id, depth_ft, use, aquifer,
  manu, model, cap_kw) are left blank — LDAD is not energy-typed.

Idempotent: re-running with the same refresh CSV produces the same combined_points.

Usage:
  python3 scripts/transform_ldad.py outputs/refresh/comptroller_ldad_<date>.csv

Or with no arg — picks the most recent comptroller_ldad_*.csv in outputs/refresh/.
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COMBINED_POINTS = REPO / "combined_points.csv"
REFRESH_DIR = REPO / "outputs" / "refresh"

LAYER_ID = "tax_abatements"


def latest_refresh() -> Path:
    candidates = sorted(REFRESH_DIR.glob("comptroller_ldad_*.csv"))
    if not candidates:
        print("[transform_ldad] ERROR: no comptroller_ldad_*.csv in outputs/refresh/", file=sys.stderr)
        sys.exit(2)
    return candidates[-1]


def to_point_row(rec: dict, header: list) -> dict:
    """Map a refresh-CSV record to a combined_points row keyed by `header`."""
    row = {col: "" for col in header}
    agreement_id = (rec.get("agreement_id") or "").strip()
    applicant = (rec.get("applicant") or "").strip()
    zone = (rec.get("reinvestment_zone") or "").strip()
    county = (rec.get("county") or "").strip()
    agmt_type = (rec.get("agmt_type") or "").strip()
    status = (rec.get("abatement_status") or "").strip().lower()
    commissioned = (rec.get("commissioned") or "").strip()
    year = commissioned[:4] if commissioned and len(commissioned) >= 4 else ""

    funnel_parts = [p for p in (agmt_type, status) if p]
    funnel = "|".join(funnel_parts)

    name = applicant or zone or (f"{county} abatement {agreement_id}".strip() if county else agreement_id)

    row["layer_id"] = LAYER_ID
    row["lat"] = rec.get("lat", "")
    row["lon"] = rec.get("lon", "")
    row["name"] = name
    row["county"] = county
    row["inr"] = agreement_id
    row["poi"] = rec.get("detail_url", "")
    row["entity"] = rec.get("taxing_unit", "")
    row["funnel_stage"] = funnel
    row["group"] = "Permits"
    row["commissioned"] = commissioned
    row["operator"] = applicant
    row["project"] = zone
    row["year"] = year
    row["coords_source"] = rec.get("coords_source", "ldad_county_centroid")
    return row


def main() -> int:
    if len(sys.argv) > 1:
        refresh_path = Path(sys.argv[1])
        if not refresh_path.is_absolute():
            refresh_path = REPO / refresh_path
    else:
        refresh_path = latest_refresh()

    if not refresh_path.exists():
        print(f"[transform_ldad] ERROR: refresh CSV not found: {refresh_path}", file=sys.stderr)
        return 2

    print(f"[transform_ldad] refresh: {refresh_path.relative_to(REPO)}")
    print(f"[transform_ldad] target:  {COMBINED_POINTS.relative_to(REPO)}")

    # Read refresh CSV in full (small file — 1,486 rows).
    with open(refresh_path, encoding="utf-8") as f:
        refresh_rows = list(csv.DictReader(f))
    print(f"[transform_ldad] refresh rows loaded: {len(refresh_rows)}")

    # Stream combined_points.csv: drop layer rows, write everything else,
    # then append new layer rows. §6.15 atomic via temp + os.replace.
    tmp_path = COMBINED_POINTS.with_suffix(COMBINED_POINTS.suffix + ".tmp")
    before_layer_count = 0
    kept = 0
    with open(COMBINED_POINTS, encoding="utf-8") as src, \
         open(tmp_path, "w", newline="", encoding="utf-8") as dst:
        reader = csv.DictReader(src)
        header = reader.fieldnames
        if not header:
            print("[transform_ldad] ERROR: combined_points.csv has no header", file=sys.stderr)
            return 2
        writer = csv.DictWriter(dst, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        for row in reader:
            if row.get("layer_id") == LAYER_ID:
                before_layer_count += 1
                continue
            writer.writerow(row)
            kept += 1

        # Append new layer rows
        appended = 0
        for rec in refresh_rows:
            point_row = to_point_row(rec, header)
            writer.writerow(point_row)
            appended += 1

    os.replace(tmp_path, COMBINED_POINTS)

    print(
        f"[transform_ldad] dropped {before_layer_count} prior {LAYER_ID} rows; "
        f"kept {kept} other rows; appended {appended} new {LAYER_ID} rows"
    )
    print(f"[transform_ldad] before={before_layer_count}  after={appended}  delta={appended - before_layer_count:+d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
