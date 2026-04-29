#!/usr/bin/env python3
"""
Merge a Comptroller LDAD refresh CSV + commissioner-court seed into combined_points.csv.

Per WIP_OPEN Chat 121 (supersedes Chat 118):
  - Drop only tax_abatements rows where `coords_source = ldad_county_centroid`.
    Non-centroid tax_abatements rows (commissioner_court seed, future overrides)
    are preserved across refreshes.
  - Load `data/abatements_court_seed.csv` (9 Pecos/Reeves rows from Chat 83
    commissioner-court intel). Each seed row carries `coords_source = commissioner_court`.
  - Append LDAD-scraped rows under the same layer_id, deduping any whose
    (county, name lower-cased exact) collides with a seed row — seed wins
    (curated coords > county centroid).
  - Coerce `1900-01-01` → '' on commissioned/year for scraped rows. The LDAD
    open-data API returns `1900-01-01` as an unknown-date placeholder, which
    poisons date_range filter min bound.
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
SEED_PATH = REPO / "data" / "abatements_court_seed.csv"

LAYER_ID = "tax_abatements"
LDAD_CENTROID_TAG = "ldad_county_centroid"
UNKNOWN_DATE_PLACEHOLDER = "1900-01-01"


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
    if commissioned == UNKNOWN_DATE_PLACEHOLDER:
        commissioned = ""
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
    if not SEED_PATH.exists():
        print(f"[transform_ldad] ERROR: seed CSV not found: {SEED_PATH}", file=sys.stderr)
        return 2

    print(f"[transform_ldad] refresh: {refresh_path.relative_to(REPO)}")
    print(f"[transform_ldad] seed:    {SEED_PATH.relative_to(REPO)}")
    print(f"[transform_ldad] target:  {COMBINED_POINTS.relative_to(REPO)}")

    # Read refresh CSV in full (small file — ~1,500 rows).
    with open(refresh_path, encoding="utf-8") as f:
        refresh_rows = list(csv.DictReader(f))
    print(f"[transform_ldad] refresh rows loaded: {len(refresh_rows)}")

    # Read commissioner-court seed.
    with open(SEED_PATH, encoding="utf-8") as f:
        seed_rows = list(csv.DictReader(f))
    print(f"[transform_ldad] seed rows loaded:    {len(seed_rows)}")

    # Stream combined_points.csv: drop ONLY tax_abatements rows whose
    # coords_source == ldad_county_centroid; preserve everything else.
    # Then append seed rows + scraped rows (de-duped against seed).
    # §6.15 atomic via temp + os.replace.
    seed_keys = {
        (
            (r.get("county", "") or "").strip().lower(),
            (r.get("name", "") or "").strip().lower(),
        )
        for r in seed_rows
    }

    tmp_path = COMBINED_POINTS.with_suffix(COMBINED_POINTS.suffix + ".tmp")
    dropped_centroid = 0
    preserved_layer = 0
    kept_other = 0
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
                if (row.get("coords_source") or "").strip() == LDAD_CENTROID_TAG:
                    dropped_centroid += 1
                    continue
                # Preserve non-centroid tax_abatements (court seed reload re-emits
                # them below; skip here to avoid duplication on reruns).
                preserved_layer += 1
                continue
            writer.writerow(row)
            kept_other += 1

        # Append seed rows (canonical court overlay).
        appended_seed = 0
        for s in seed_rows:
            seed_out = {col: s.get(col, "") for col in header}
            writer.writerow(seed_out)
            appended_seed += 1

        # Append scraped LDAD rows, deduping any whose (county, name) collides
        # with the seed — seed wins because it has curated coords.
        appended_ldad = 0
        skipped_overlap = 0
        for rec in refresh_rows:
            point_row = to_point_row(rec, header)
            key = (
                (point_row.get("county") or "").strip().lower(),
                (point_row.get("name") or "").strip().lower(),
            )
            if key in seed_keys:
                skipped_overlap += 1
                continue
            writer.writerow(point_row)
            appended_ldad += 1

    os.replace(tmp_path, COMBINED_POINTS)

    total_layer_after = appended_seed + appended_ldad
    total_layer_before = dropped_centroid + preserved_layer
    print(
        f"[transform_ldad] dropped {dropped_centroid} prior {LAYER_ID} centroid rows; "
        f"superseded {preserved_layer} prior non-centroid rows (re-emitted from seed); "
        f"kept {kept_other} other-layer rows"
    )
    print(
        f"[transform_ldad] appended seed={appended_seed} ldad={appended_ldad} "
        f"(skipped_seed_overlap={skipped_overlap})"
    )
    print(
        f"[transform_ldad] before={total_layer_before}  after={total_layer_after}  "
        f"delta={total_layer_after - total_layer_before:+d}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
