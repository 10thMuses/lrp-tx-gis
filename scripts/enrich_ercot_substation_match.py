#!/usr/bin/env python3
"""R26 P6: ercot_queue precise-coord upgrade via OSM substation name match.

For each ercot_queue row in 6-county Permian scope whose coords_source is
`county_centroid`, `unknown`, or blank, extract substation names from
the row's `zone` (POI) text field, fuzzy-match against the OSM
substations layer in the same county neighborhood, and lift the
substation's lat/lon onto the ercot row with coords_source =
`substation_match` and tag = `precise`.

The `zone` field commonly contains strings like:
  "Tap 138 kV Yucca Drive Switch (bus# 1009) - Sand Tank (bus# 11197)"
  "TNJACKRBT1 138kV"
  "11098 SLKSW – 60404 SOLSTICE Ckt 1"
  "#38455 HOLIDAY SUB TNP - #38450 SOAPTREE TNP"

This script extracts substation tokens (uppercase short codes, "X
SUBSTATION", "X SUB", "X SWITCH") and matches them against the OSM
substation names within the county. Idempotent: re-running produces no
diff when no new sources land.

Atomic temp + os.replace.
"""
from __future__ import annotations

import csv
import math
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SCOPE = {"pecos", "reeves", "ward", "midland", "martin", "reagan"}
COUNTY_BBOX = (-104.0, 30.0, -101.0, 32.6)

# Substation-token extractor: catches "X Substation", "X Sub", "X Switch",
# "X SWSTA", "XYZW1" (5+ char alphanumeric all-caps), or hash-prefixed
# numeric tags like "#11098 SLKSW".
TOKEN_RE = re.compile(
    r"(?:#\d+\s+)?([A-Z][A-Z0-9_]{3,30})(?:\s+(?:SUB(?:STATION)?|SWITCH|SUBSTATION|SWSTA|SS))?",
    re.IGNORECASE,
)
WORD_RE = re.compile(r"[A-Za-z0-9_]+")
STOP = {
    "TAP", "BUS", "CKT", "TNP", "KV", "138KV", "345KV", "69KV", "TIE",
    "TO", "FROM", "AT", "THE", "AND", "OR", "STATION", "SUBSTATION",
    "SWITCH", "SWITCHING", "SWSTA", "SUB", "SS", "POI", "POD", "INC", "CO", "LLC",
    "LP", "MW", "GAS", "SOL", "BA", "GT", "IC", "OTH", "ENERGY", "POWER",
    "PROJECT", "PLANT", "FARM", "WIND", "SOLAR", "BESS", "STORAGE",
    "WEST", "EAST", "NORTH", "SOUTH", "TX", "TEXAS", "PERMIAN", "BASIN",
    # Generic location nouns — too common to discriminate substations
    "FIELD", "RANCH", "CREEK", "LAKE", "MOUNTAIN", "RIVER", "VALLEY",
    "DRIVE", "ROAD", "ROUTE", "AVENUE", "STREET", "PARK", "TANK",
    # County names — would match every substation in that county
    "PECOS", "REEVES", "WARD", "MIDLAND", "MARTIN", "REAGAN", "COUNTY",
}

CSV_PATH = ROOT / "combined_points.csv"


def haversine_mi(a_lat, a_lon, b_lat, b_lon) -> float:
    R = 3958.756
    lat1, lat2 = math.radians(a_lat), math.radians(b_lat)
    dlat = lat2 - lat1
    dlon = math.radians(b_lon - a_lon)
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def normalize(s: str) -> set[str]:
    if not s:
        return set()
    s = s.upper()
    out = set()
    for w in WORD_RE.findall(s):
        if len(w) >= 4 and w not in STOP and not w.isdigit():
            out.add(w)
    return out


def main() -> int:
    if not CSV_PATH.exists():
        print(f"ERROR: {CSV_PATH} missing")
        return 2

    rows: list[dict] = []
    fields: list[str] = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        fields = list(r.fieldnames or [])
        for row in r:
            rows.append(row)

    # Build substation index — global within 6-county bbox.
    sub_index: list[tuple[set[str], str, float, float]] = []
    token_freq: dict[str, int] = {}
    for r in rows:
        if r.get("layer_id") != "substations":
            continue
        try:
            lat = float(r.get("lat") or "")
            lon = float(r.get("lon") or "")
        except ValueError:
            continue
        if not (COUNTY_BBOX[1] <= lat <= COUNTY_BBOX[3]
                and COUNTY_BBOX[0] <= lon <= COUNTY_BBOX[2]):
            continue
        name = (r.get("name") or "").strip()
        if not name:
            continue
        tokens = normalize(name)
        if not tokens:
            continue
        sub_index.append((tokens, name, lat, lon))
        for t in tokens:
            token_freq[t] = token_freq.get(t, 0) + 1
    print(f"  substation candidates (6-county bbox, named): {len(sub_index)}")
    # Discriminating tokens = appear in ≤2 substations. Ambiguous tokens
    # (frequency ≥3) cannot serve as a sole match key.
    discriminating = {t for t, c in token_freq.items() if c <= 2}

    n_upgraded = 0
    n_skipped_already_precise = 0
    n_in_scope = 0
    n_no_match = 0
    upgrade_detail: list[tuple[str, str, str, float, float]] = []

    for r in rows:
        if r.get("layer_id") != "ercot_queue":
            continue
        c = (r.get("county") or "").lower().strip()
        if c not in SCOPE:
            continue
        n_in_scope += 1
        cs = (r.get("coords_source") or "").strip()
        if cs and cs not in ("county_centroid", "unknown", ""):
            n_skipped_already_precise += 1
            continue
        zone_text = (r.get("zone") or "")
        poi_text = (r.get("poi") or "")
        haystack = f"{zone_text} {poi_text}"
        ercot_tokens = normalize(haystack)
        if not ercot_tokens:
            n_no_match += 1
            continue
        try:
            cur_lat = float(r.get("lat") or "")
            cur_lon = float(r.get("lon") or "")
        except ValueError:
            cur_lat = cur_lon = None
        best = None
        best_score = 0
        for sub_toks, sub_name, sub_lat, sub_lon in sub_index:
            overlap = ercot_tokens & sub_toks
            if not overlap:
                continue
            # Require ≥1 discriminating token (≤2-substation frequency) AND
            # ≥7 chars or digit-bearing, OR ≥2 distinct ≥5-char discriminating
            # token overlap. This excludes generic words shared across many
            # substations (SPRINGS appears in 3+ → ambiguous).
            strong = [t for t in overlap
                      if t in discriminating
                      and (len(t) >= 7 or any(d.isdigit() for d in t))]
            multi_overlap = [t for t in overlap
                             if t in discriminating and len(t) >= 5]
            if not strong and len(multi_overlap) < 2:
                continue
            score = sum(len(t) for t in strong) + (10 * (len(multi_overlap) - 1) if len(multi_overlap) >= 2 else 0)
            # Geographic plausibility: substation must be within 30 mi of
            # the existing county-centroid position (sanity gate).
            if cur_lat is not None and cur_lon is not None:
                if haversine_mi(cur_lat, cur_lon, sub_lat, sub_lon) > 30:
                    continue
            if score > best_score:
                best = (sub_name, sub_lat, sub_lon, overlap)
                best_score = score
        if best:
            sub_name, sub_lat, sub_lon, overlap = best
            r["lat"] = f"{sub_lat:.6f}"
            r["lon"] = f"{sub_lon:.6f}"
            r["coords_source"] = "substation_match"
            n_upgraded += 1
            upgrade_detail.append((r.get("name", ""), sub_name, ",".join(sorted(overlap)), sub_lat, sub_lon))
        else:
            n_no_match += 1

    # Atomic write.
    tmp = CSV_PATH.with_suffix(".csv.tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow(row)
    os.replace(tmp, CSV_PATH)

    print(f"  ercot_queue rows in 6-county scope:    {n_in_scope}")
    print(f"  already precise (skipped):             {n_skipped_already_precise}")
    print(f"  upgraded to substation_match:          {n_upgraded}")
    print(f"  no substation match found:             {n_no_match}")
    if upgrade_detail:
        print("\n  upgrades:")
        for ercot_name, sub_name, tokens, lat, lon in upgrade_detail:
            print(f"    {ercot_name[:40]:40} → {sub_name[:30]:30}  via [{tokens[:30]}]  ({lat:.4f},{lon:.4f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
