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

Cardinality target: 6-county Permian rescope yields ~60-90k rows out of ~750k
statewide (subject: Pecos/Reeves/Ward; peer: Midland/Martin/Reagan).
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

# 6-county Permian scope. FIPS county codes (3 digits), state code 48.
# Matches WB-API-CNTY field in WBROOT records.
#
# Subject counties (sale area):       Pecos · Reeves · Ward
# Active Permian peer counties:       Midland · Martin · Reagan
#
# Rationale (per 2026-05-13 rescope, decision-logged in WIP_OPEN.md):
# tight sale-area-vs-boom-area contrast for the Hanwha legal defense.
COUNTIES = {
    "317": "Martin",
    "329": "Midland",
    "371": "Pecos",
    "383": "Reagan",
    "389": "Reeves",
    "475": "Ward",
}

SUBJECT_COUNTY_FIPS = frozenset({"371", "389", "475"})   # Pecos, Reeves, Ward
PEER_COUNTY_FIPS = frozenset({"317", "329", "383"})      # Martin, Midland, Reagan

# Segment keys (from wba091 §1.2)
SEG_WBROOT = "01"
SEG_WBCOMPL = "02"
SEG_WBNEWLOC = "13"

CSV_FIELDS = [
    "layer_id",
    "api_no", "county_fips", "county_name", "county_role", "district",
    "well_no", "lease_no", "oil_gas",
    "total_depth", "completion_date", "completion_year",
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
        # R2-3: numeric year for time-series filters/scrubber
        try:
            yr = int(f"{cent}{yy}")
            if 1900 <= yr <= 2030:
                acc["completion_year"] = str(yr)
        except ValueError:
            pass
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
    """Emit acc as a row if county is in scope AND well is not plugged.

    R2-1: include only wells with status ∈ {active, drilling}. In dbf900
    wells are completed wellbores (drilling-in-progress lives in the
    permits layer, not here), so 'drilling' is never observed. The remaining
    discriminant is plug_flag: 'N' = not plugged (active by default),
    'Y' = plugged / abandoned / P&A (excluded). Rationale + before/after
    cardinality logged in WIP_OPEN.md decision log."""
    cnty = acc.get("county_fips", "")
    if cnty not in COUNTIES:
        return False
    if not acc.get("api_no"):
        return False
    # R2-1 hard filter: exclude plugged / abandoned / P&A wells.
    plug = acc.get("plug_flag", "")
    if plug == "Y":
        return False
    row = {f: acc.get(f, "") for f in CSV_FIELDS}
    row["layer_id"] = "wells_permian6"
    row["county_name"] = COUNTIES[cnty]
    row["county_role"] = "subject" if cnty in SUBJECT_COUNTY_FIPS else "peer"
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


PERMIT_FIELDS = [
    "layer_id",
    "permit_no", "status_no", "api_no",
    "county_fips", "county_name", "county_role", "district",
    "lease_name", "well_no",
    "operator_name",
    "submitted_date", "approved_date",
    "permit_year",
    "status",
    "wellbore_profile",     # horizontal | vertical
    "filing_purpose",       # raw 1-char code (P/X/E/...) — populated only when present
    "oil_gas",              # oil | gas | unknown — derived from filing_purpose if recognizable
    "total_depth",
    "lat", "lon",
]


# Master record (212b, prefix 0108) byte positions (1-indexed in wba091-style;
# decoded here as Python slices). Verified empirically on the
# daf420.dat.01-31-2018 monthly snapshot.
M_RECKEY = slice(0, 4)             # "0108"
M_PERMIT_ID = slice(4, 14)         # 10-digit permit/status master id
M_COUNTY_FIPS = slice(11, 14)      # last 3 digits of master id = Texas county FIPS
M_LEASE_NAME = slice(14, 46)       # 32 chars, space-padded
M_WELL_NO = slice(50, 54)          # 4 chars
M_SUBMIT_DATE = slice(58, 66)      # YYYYMMDD
M_OPERATOR = slice(66, 98)         # 32 chars, space-padded
M_STATUS_FLAG = slice(100, 101)    # A=Approved etc. (uniform 'A' in EOM file — all approved)
M_DISTRICT = slice(112, 114)       # 2-digit RRC district
M_APPROVE_DATE = slice(120, 128)   # YYYYMMDD
# Wellbore profile: in 9/1474 records the literal "HL" appears at position 160.
# The position-160 byte alone is a poor signal — many records carry "H " or
# other 2-char codes there. We search a small window for the exact "HL"
# substring and fall back to "vertical" when absent (the dominant case).
M_PROFILE_WINDOW = slice(155, 170)
M_FILING_PURPOSE = slice(182, 183)     # X (63%), E (18%), P (12%), 3 (6%)

# Location record (26b, prefix '14' or '15'): WGS84 lat/lon
LOC_LON = slice(2, 14)             # signed 12-char "DDD.DDDDDDD" or " -DD.DDDDDDD" (TX always negative)
LOC_LAT = slice(16, 26)            # "DD.DDDDDDD"

PERMIT_STATUS_MAP = {
    "A": "approved",
    "X": "cancelled",
    "W": "withdrawn",
    "E": "expired",
    "D": "denied",
    "P": "pending",
    "S": "submitted",
}

# Loose mapping from filing_purpose codes seen in samples → an oil/gas
# best-guess. Refined empirically; rows that come back as 'unknown' get
# carried with that label rather than dropped (R2-2's filter is applied
# downstream in the build layer config).
FILING_TO_OG = {
    "O": "oil",
    "G": "gas",
    "P": "production-other",
    # Less-frequent / less-known codes left as None so they surface as 'unknown'.
}


def parse_date(raw: bytes) -> str:
    s = raw.decode("ascii", errors="replace").strip()
    if len(s) == 8 and s.isdigit() and s != "00000000":
        return f"{s[:4]}-{s[4:6]}-{s[6:]}"
    return ""


def parse_master(line: bytes) -> dict:
    permit_id = line[M_PERMIT_ID].decode("ascii", errors="replace")
    county_fips = line[M_COUNTY_FIPS].decode("ascii", errors="replace")
    status_no = permit_id[:7] if len(permit_id) >= 7 else permit_id
    lease_name = line[M_LEASE_NAME].decode("ascii", errors="replace").strip()
    well_no = line[M_WELL_NO].decode("ascii", errors="replace").strip().lstrip("0")
    submit_date = parse_date(line[M_SUBMIT_DATE])
    approve_date = parse_date(line[M_APPROVE_DATE])
    operator = line[M_OPERATOR].decode("ascii", errors="replace").strip()
    status_flag = line[M_STATUS_FLAG].decode("ascii", errors="replace").strip()
    district = line[M_DISTRICT].decode("ascii", errors="replace").strip()
    # Wellbore profile heuristic: byte 160 carries the wellbore-type letter.
    # 'H' (~48% of records) → horizontal; everything else → vertical/directional/blank.
    # The literal substring "HL" appears only in ~9/1474 records — a much rarer
    # special-class marker not the primary horizontal indicator.
    profile_byte = chr(line[160]) if len(line) > 160 else ' '
    wellbore_profile = "horizontal" if profile_byte == "H" else "vertical"
    filing_purpose = line[M_FILING_PURPOSE].decode("ascii", errors="replace").strip()
    oil_gas = FILING_TO_OG.get(filing_purpose, "unknown")
    status = PERMIT_STATUS_MAP.get(status_flag, status_flag.lower() or "unknown")
    permit_year = submit_date[:4] if submit_date else (approve_date[:4] if approve_date else "")
    return {
        "permit_no": permit_id,
        "status_no": status_no,
        "county_fips": county_fips,
        "lease_name": lease_name,
        "well_no": well_no,
        "submitted_date": submit_date,
        "approved_date": approve_date,
        "operator_name": operator,
        "status": status,
        "district": district,
        "wellbore_profile": wellbore_profile,
        "filing_purpose": filing_purpose,
        "oil_gas": oil_gas,
        "permit_year": permit_year,
    }


def parse_loc(line: bytes) -> tuple[float | None, float | None]:
    """Decode WGS84 lon (signed) + lat from a 26-byte 14/15-prefixed line."""
    if len(line) != 26:
        return None, None
    lon_s = line[LOC_LON].decode("ascii", errors="replace").strip()
    lat_s = line[LOC_LAT].decode("ascii", errors="replace").strip()
    try:
        lon = float(lon_s)
    except ValueError:
        lon = None
    try:
        lat = float(lat_s)
    except ValueError:
        lat = None
    # Texas longitude is always negative; the file stores either signed
    # ("-103.4567890") or unsigned magnitudes — normalize to negative.
    if lon is not None:
        lon = -abs(lon)
    return lat, lon


# total_depth lives at bytes 322-331 of the 510-byte detail record (10-char
# zero-padded depth in feet). Verified empirically across 3 known permits
# (KING E.F. = 4822, UNIVERSITY UE A = 4982, REED = 500). The 7-digit field
# at 332-339 is a related sub-depth (plug-back / penetration) that we don't
# expose on the map.
D_TOTAL_DEPTH = slice(322, 332)

def extract_total_depth(detail_line: bytes) -> str:
    """Return zero-padded total_depth as int-string, or '' if unparseable or 0."""
    if len(detail_line) < 332:
        return ""
    raw = detail_line[D_TOTAL_DEPTH].decode("ascii", errors="replace")
    if not raw.isdigit():
        return ""
    v = int(raw)
    if v <= 0 or v > 50000:
        return ""
    return str(v)


def parse_permits(src: Path, dst: Path) -> dict:
    """Stream-parse daf420.dat (one EOM monthly snapshot) → permits CSV.
    Atomic temp+replace."""
    tmp = dst.with_suffix(dst.suffix + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)

    counts = {
        "lines_total": 0,
        "permits_seen": 0,
        "permits_in_scope": 0,
        "permits_no_latlon": 0,
        "permits_no_depth": 0,
        "rows_written": 0,
    }

    with open(src, "rb") as f_in, open(tmp, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=PERMIT_FIELDS)
        writer.writeheader()

        # Block state
        cur_master = None
        cur_detail = None
        cur_lat = None
        cur_lon = None

        def flush_block():
            if cur_master is None:
                return
            counts["permits_seen"] += 1
            cnty = cur_master.get("county_fips", "")
            if cnty not in COUNTIES:
                return
            counts["permits_in_scope"] += 1
            depth = extract_total_depth(cur_detail) if cur_detail else ""
            if not depth:
                counts["permits_no_depth"] += 1
                return  # R2-2: exclude null total_depth at the data layer
            if cur_lat is None or cur_lon is None:
                counts["permits_no_latlon"] += 1
                return
            row = {f: "" for f in PERMIT_FIELDS}
            row.update(cur_master)
            row["layer_id"] = "permits_permian6"
            row["county_name"] = COUNTIES[cnty]
            row["county_role"] = "subject" if cnty in SUBJECT_COUNTY_FIPS else "peer"
            row["api_no"] = f"42-{cnty}-{cur_master['status_no'][-5:]}" if cur_master.get("status_no") else ""
            row["total_depth"] = depth
            row["lat"] = f"{cur_lat:.6f}"
            row["lon"] = f"{cur_lon:.6f}"
            writer.writerow(row)
            counts["rows_written"] += 1

        for raw_line in f_in:
            counts["lines_total"] += 1
            line = raw_line.rstrip(b"\r\n")
            if len(line) < 4:
                continue
            key4 = line[:4]
            if key4 == b"0108":
                # New permit boundary — flush prior block first
                flush_block()
                cur_master = parse_master(line)
                cur_detail = None
                cur_lat = None
                cur_lon = None
            elif key4 == b"0208":
                cur_detail = line
            elif len(line) == 26 and line[:2] in (b"14", b"15"):
                lat, lon = parse_loc(line)
                # Prefer first non-null lat/lon (14 vs 15 are usually same coords)
                if cur_lat is None and lat is not None:
                    cur_lat = lat
                if cur_lon is None and lon is not None:
                    cur_lon = lon
        # Final flush
        flush_block()

    os.replace(tmp, dst)
    return counts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", choices=["wells", "permits", "all"], default="all", nargs="?")
    args = ap.parse_args()

    if args.target in ("wells", "all"):
        src = RAW / "dbf900.txt.gz"
        if not src.exists():
            print(f"ERROR: {src} not found — run `python3 scripts/fetch_rrc.py wells` first")
            return 2
        dst = ROOT / "data" / "wells_permian6.csv"
        print(f"=== parse wells: {src.name} → {dst} ===")
        counts = parse_wellbore(src, dst)
        for k, v in counts.items():
            print(f"  {k}: {v:,}")
        size_mb = dst.stat().st_size / (1024 * 1024)
        print(f"  output: {size_mb:.2f} MB")

    if args.target in ("permits", "all"):
        # Glob all EOM monthly snapshots cached under data/rrc_raw/.
        # fetch_rrc.py downloads the latest only; if the operator pre-pulled
        # a backfill set, we iterate them all here.
        src_dir = RAW
        snapshots = sorted(src_dir.glob("daf420.dat.*"))
        if not snapshots:
            print(f"ERROR: no daf420.dat.* snapshots in {src_dir} — "
                  f"run `python3 scripts/fetch_rrc.py permits` first")
            return 2
        dst = ROOT / "data" / "permits_permian6.csv"
        agg_counts = {
            "lines_total": 0, "permits_seen": 0, "permits_in_scope": 0,
            "permits_no_latlon": 0, "permits_no_depth": 0, "rows_written": 0,
        }
        # Multi-file aggregation: parse each into a temp CSV, then concatenate.
        # Easier approach: parse first, then append for subsequent.
        for i, snap in enumerate(snapshots):
            print(f"=== parse permits [{i+1}/{len(snapshots)}]: {snap.name} ===")
            if i == 0:
                c = parse_permits(snap, dst)
            else:
                # Append mode — parse to temp, then concatenate without header.
                tmp_dst = dst.with_suffix(".append.tmp.csv")
                c = parse_permits(snap, tmp_dst)
                with open(tmp_dst) as f_in, open(dst, "a") as f_out:
                    next(f_in)  # skip header
                    f_out.writelines(f_in)
                tmp_dst.unlink()
            for k, v in c.items():
                agg_counts[k] += v
        print(f"\n=== permits aggregate ===")
        for k, v in agg_counts.items():
            print(f"  {k}: {v:,}")
        size_mb = dst.stat().st_size / (1024 * 1024)
        print(f"  output: {size_mb:.2f} MB ({dst})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
