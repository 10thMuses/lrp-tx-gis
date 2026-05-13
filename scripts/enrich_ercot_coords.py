#!/usr/bin/env python3
"""
R2.5 Part 3 — ercot_queue precise-coord upgrade via abatement cross-reference.

Reads `combined_points.csv` in place. For each `ercot_queue` row whose
`coords_source` is `county_centroid`/blank, fuzzy-matches the row's
name/entity/operator against `tax_abatements` rows in the same county.
On match, lifts the abatement's lat/lon onto the ercot row and tags
`coords_source = abatement_match`.

Atomic temp + os.replace. Idempotent: running twice produces no diff.

Limitations:
  - Only the abatement source is used (per the existing `abate_index`).
  - FERC EQR + PUC CCN cross-references are documented in the R2.5 Part 3
    decision-log entry but not implemented — they require per-project
    manual filings lookup (~4-8 h for the 6-county scope's 43 imprecise
    rows).
  - This script does NOT touch any other layer's rows.

Trigger:
    python3 scripts/enrich_ercot_coords.py
    python3 build.py    # rebuild PMTiles
"""
from __future__ import annotations

import csv
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SCOPE = {"pecos", "reeves", "ward", "midland", "martin", "reagan"}

CORP_RE = re.compile(
    r"\b(l\.?l\.?c\.?|inc\.?|lp|ltd|corp|corporation|company|co\.?|l\.?p\.?)\b",
    re.IGNORECASE,
)
NONWORD = re.compile(r"[^a-z0-9]+")


def norm(s: str | None) -> set[str]:
    if not s:
        return set()
    s = s.lower()
    s = CORP_RE.sub(" ", s)
    s = NONWORD.sub(" ", s)
    return set(t for t in s.split() if len(t) > 1)


def main() -> int:
    src = ROOT / "combined_points.csv"
    if not src.exists():
        print(f"ERROR: {src} missing")
        return 2

    # Read every row; build abatement index per county.
    rows = []
    with open(src, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        for r in reader:
            rows.append(r)

    abate_by_county: dict[str, list[tuple[set[str], str, str, str]]] = {}
    for r in rows:
        if r.get("layer_id") != "tax_abatements":
            continue
        c = (r.get("county") or "").lower().strip()
        if c not in SCOPE:
            continue
        lat = r.get("lat") or ""
        lon = r.get("lon") or ""
        if not lat or not lon:
            continue
        for k in ("name", "operator"):
            applicant = r.get(k)
            if not applicant:
                continue
            toks = norm(applicant)
            if not toks:
                continue
            abate_by_county.setdefault(c, []).append((toks, applicant, lat, lon))

    # Walk ercot_queue rows; upgrade where match found.
    n_upgraded = 0
    n_already_precise = 0
    n_in_scope = 0
    for r in rows:
        if r.get("layer_id") != "ercot_queue":
            continue
        c = (r.get("county") or "").lower().strip()
        if c not in SCOPE:
            continue
        n_in_scope += 1
        cs = (r.get("coords_source") or "").strip()
        if cs and cs not in ("county_centroid", "unknown"):
            n_already_precise += 1
            continue
        # Build query token sets
        for v in (r.get("name"), r.get("entity"), r.get("operator")):
            q = norm(v)
            if not q:
                continue
            for (a_toks, a_applicant, a_lat, a_lon) in abate_by_county.get(c, []):
                if not a_toks:
                    continue
                if q <= a_toks or a_toks <= q:
                    r["lat"] = a_lat
                    r["lon"] = a_lon
                    r["coords_source"] = "abatement_match"
                    n_upgraded += 1
                    print(f"  upgrade [{c}] {r.get('name')!r} -> via {a_applicant!r}")
                    break
            if r.get("coords_source") == "abatement_match":
                break

    print(f"\nin-scope ercot_queue: {n_in_scope}")
    print(f"already precise (eia/uswtdb/tpit/substation): {n_already_precise}")
    print(f"upgraded this run: {n_upgraded}")

    if n_upgraded == 0:
        print("No changes.")
        return 0

    # Atomic write back
    tmp = src.with_suffix(".csv.tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    os.replace(tmp, src)
    print(f"wrote {src} (+{n_upgraded} ercot rows upgraded)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
