#!/usr/bin/env python3
"""
RRC dbf900 wellbore parser → 11-county Permian CSV.

Source layout: docs/rrc_layouts/wba091_well-bore-database.pdf

dbf900.txt.gz is a stream of CRLF-delimited variable-length lines. Each line
is one segment record with trailing fillers stripped. The first two bytes
of each record carry the segment key (RRC-TAPE-RECORD-ID). Segments belonging
to the same wellbore appear in adjacent lines, beginning with a key=01
(WBROOT) record that marks the well-bore boundary.

This parser walks the file line-by-line, maintains a per-well accumulator,
and flushes one CSV row per wellbore whose API county code is in the 11-county
Permian scope.

Segments consumed (rest skipped):

  01 WBROOT     county, well-unique, district, original completion date,
                total depth, newest drilling permit number, plug flag.
  02 WBCOMPL    oil-or-gas code, lease number, well number, active/inactive.
  13 WBNEWLOC   WGS84 latitude, WGS84 longitude (PIC S9(3)V9(7), DISPLAY).

PIC S9(3)V9(7) DISPLAY decode: 10 ASCII bytes total. The 10 digits represent
3 integer + 7 implied-decimal digits. Sign is overpunched on the trailing
digit per IBM zoned-decimal convention:
    '0'..'9' → +digit (unsigned positive)
    '{' or 'A'..'I' → +0..+9 (signed positive)
    '}' or 'J'..'R' → -0..-9 (signed negative)
Some RRC variants emit a leading ASCII '-' instead — handled defensively.

Hard rules respected:
  - CLAUDE.md §3.1: streams gzip → text via gzip.open(); no full-file load.
  - CLAUDE.md §3.4: atomic temp+os.replace on output CSV.

Output CSV columns:
  layer_id, api_no, county_fips, county_name, district, well_no,
  lease_no, oil_gas, total_depth, completion_date, newest_permit_no,
  plug_flag, active_flag, lat, lon

Cardinality target: ~30-40k rows for 11 Permian counties out of ~750k statewide.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "rrc_raw"

# 11-county Permian scope. FIPS county codes (3 digits), state code 48.
# Matches WB-API-CNTY field in WBROOT records.
COUNTIES = {
    "043": "Brewster",
    "103": "Crane",
    "105": "Crockett",
    "109": "Culberson",
    "243": "Jeff Davis",
    "371": "Pecos",
    "383": "Reagan",
    "389": "Reeves",
    "443": "Terrell",
    "461": "Upton",
    "475": "Ward",
}

# Segment keys (from wba091 §1.2)
SEG_WBROOT = "01"
SEG_WBCOMPL = "02"
SEG_WBNEWLOC = "13"

CSV_FIELDS = [
    "layer_id",
    "api_no", "county_fips", "county_name", "district",
    "well_no", "lease_no", "oil_gas",
    "total_depth", "completion_date",
    "newest_permit_no", "plug_flag", "active_flag",
    "lat", "lon",
]

# Zoned-decimal sign overpunch (IBM EBCDIC convention, also used in RRC ASCII
# DISPLAY format files when the source is converted from mainframe tape).
OVERPUNCH_POS = {ord("{"): "0"} | {ord(c): str(i + 1) for i, c in enumerate("ABCDEFGHI")}
OVERPUNCH_NEG = {ord("}"): "0"} | {ord(c): str(i + 1) for i, c in enumerate("JKLMNOPQR")}


def decode_signed_zoned(raw: bytes) -> float | None:
    """Decode a PIC S9(3)V9(7) DISPLAY field. 10 ASCII bytes in, decimal out."""
    if len(raw) < 10:
        return None
    # Strip ASCII whitespace defensively
    s = raw.decode("ascii", errors="replace").rstrip()
    if not s or s.strip(" 0") == "":
        return None
    sign = 1
    # Variant 1: ASCII leading '-' followed by digits
    if s.startswith("-"):
        sign = -1
        digits = s[1:].lstrip()
    else:
        digits = s
    # Variant 2: trailing overpunched digit
    if digits and not digits[-1].isdigit():
        last_byte = ord(digits[-1])
        if last_byte in OVERPUNCH_NEG:
            sign = -1
            digits = digits[:-1] + OVERPUNCH_NEG[last_byte]
        elif last_byte in OVERPUNCH_POS:
            digits = digits[:-1] + OVERPUNCH_POS[last_byte]
    if not digits.isdigit():
        return None
    if len(digits) < 10:
        digits = digits.zfill(10)
    # 3 integer + 7 fractional
    int_part = digits[:3].lstrip("0") or "0"
    frac_part = digits[3:10]
    try:
        return sign * float(f"{int_part}.{frac_part}")
    except ValueError:
        return None


def parse_int(raw: bytes) -> int | None:
    s = raw.decode("ascii", errors="replace").strip()
    if not s or not s.lstrip("0").isdigit():
        if s.isdigit():
            return int(s)
        return None
    return int(s)


def parse_text(raw: bytes) -> str:
    return raw.decode("ascii", errors="replace").rstrip()


def slice_at(line: bytes, start1: int, length: int) -> bytes:
    """Slice using 1-indexed COBOL position. Returns b'' if line too short."""
    i = start1 - 1
    if i < 0 or i >= len(line):
        return b""
    return line[i:i + length]


def parse_wbroot(line: bytes, acc: dict) -> None:
    """Extract fields from WBROOT record (key=01).
    Positions are 1-indexed from the wba091 layout."""
    api_cnty = parse_text(slice_at(line, 3, 3))
    api_unique = parse_text(slice_at(line, 6, 5))
    district = parse_text(slice_at(line, 15, 2))
    # WB-ORIG-COMPL date: CC at pos 21 (2), YY at 23 (2), MM 25 (2), DD 27 (2)
    cent = parse_text(slice_at(line, 21, 2))
    yy = parse_text(slice_at(line, 23, 2))
    mm = parse_text(slice_at(line, 25, 2))
    dd = parse_text(slice_at(line, 27, 2))
    total_depth = parse_text(slice_at(line, 29, 5)).lstrip("0") or ""
    newest_permit = parse_text(slice_at(line, 81, 6)).lstrip("0") or ""
    plug_flag = parse_text(slice_at(line, 91, 1))

    acc["county_fips"] = api_cnty
    acc["api_no"] = f"42-{api_cnty}-{api_unique}" if api_cnty and api_unique else ""
    acc["district"] = district
    if cent.isdigit() and yy.isdigit() and mm.isdigit() and dd.isdigit() and int(cent) > 0:
        acc["completion_date"] = f"{cent}{yy}-{mm}-{dd}"
    acc["total_depth"] = total_depth
    acc["newest_permit_no"] = newest_permit
    acc["plug_flag"] = plug_flag


def parse_wbcompl(line: bytes, acc: dict) -> None:
    """Extract from WBCOMPL (key=02). First-seen wins per well."""
    if acc.get("_wbcompl_seen"):
        return
    acc["_wbcompl_seen"] = True
    oil_code = parse_text(slice_at(line, 3, 1))
    oil_lse = parse_text(slice_at(line, 6, 5)).lstrip("0") or ""
    oil_well = parse_text(slice_at(line, 11, 6))
    gas_well = parse_text(slice_at(line, 19, 6))
    active = parse_text(slice_at(line, 46, 1))
    acc["oil_gas"] = oil_code
    acc["lease_no"] = oil_lse
    acc["well_no"] = oil_well or gas_well
    acc["active_flag"] = active


def parse_wbnewloc(line: bytes, acc: dict) -> None:
    """Extract WGS84 lat/lon from WBNEWLOC (key=13).

    RRC encodes both fields as zoned-decimal magnitudes — the sign overpunch
    consistently registers as positive. Texas is north + west of the equator/
    prime meridian, so we keep lat positive and force lon negative.
    """
    lat = decode_signed_zoned(slice_at(line, 133, 10))
    lon_mag = decode_signed_zoned(slice_at(line, 143, 10))
    if lat is not None and 25.0 < abs(lat) < 38.0:
        acc["lat"] = f"{abs(lat):.6f}"
    if lon_mag is not None and 93.0 < abs(lon_mag) < 107.5:
        acc["lon"] = f"{-abs(lon_mag):.6f}"


def flush(acc: dict, writer: csv.DictWriter) -> bool:
    """Emit acc as a row if county is in scope. Returns True if written."""
    cnty = acc.get("county_fips", "")
    if cnty not in COUNTIES:
        return False
    if not acc.get("api_no"):
        return False
    row = {f: acc.get(f, "") for f in CSV_FIELDS}
    row["layer_id"] = "wells_pecos11"
    row["county_name"] = COUNTIES[cnty]
    writer.writerow(row)
    return True


def parse_wellbore(src: Path, dst: Path) -> dict:
    """Stream-parse dbf900.txt.gz → CSV at dst. Atomic temp+replace."""
    tmp = dst.with_suffix(dst.suffix + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)

    counts = {
        "lines_total": 0,
        "wbroot_seen": 0,
        "wbnewloc_seen": 0,
        "rows_written": 0,
        "wells_in_scope_no_latlon": 0,
    }
    acc: dict = {}

    with gzip.open(src, "rb") as f_in, open(tmp, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for raw_line in f_in:
            counts["lines_total"] += 1
            line = raw_line.rstrip(b"\r\n")
            if len(line) < 2:
                continue
            key = line[:2].decode("ascii", errors="replace")
            if key == SEG_WBROOT:
                # Boundary: flush previous accumulator if any
                if acc:
                    if acc.get("county_fips") in COUNTIES:
                        if "lat" not in acc or "lon" not in acc:
                            counts["wells_in_scope_no_latlon"] += 1
                    if flush(acc, writer):
                        counts["rows_written"] += 1
                acc = {}
                counts["wbroot_seen"] += 1
                parse_wbroot(line, acc)
            elif key == SEG_WBCOMPL:
                if acc:
                    parse_wbcompl(line, acc)
            elif key == SEG_WBNEWLOC:
                counts["wbnewloc_seen"] += 1
                if acc:
                    parse_wbnewloc(line, acc)
            # else: skip segment

        # Final flush
        if acc:
            if acc.get("county_fips") in COUNTIES:
                if "lat" not in acc or "lon" not in acc:
                    counts["wells_in_scope_no_latlon"] += 1
            if flush(acc, writer):
                counts["rows_written"] += 1

    os.replace(tmp, dst)
    return counts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", choices=["wells", "all"], default="all", nargs="?")
    args = ap.parse_args()

    if args.target in ("wells", "all"):
        src = RAW / "dbf900.txt.gz"
        if not src.exists():
            print(f"ERROR: {src} not found — run `python3 scripts/fetch_rrc.py wells` first")
            return 2
        dst = ROOT / "data" / "wells_pecos11.csv"
        print(f"=== parse wells: {src.name} → {dst} ===")
        counts = parse_wellbore(src, dst)
        for k, v in counts.items():
            print(f"  {k}: {v:,}")
        size_mb = dst.stat().st_size / (1024 * 1024)
        print(f"  output: {size_mb:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
