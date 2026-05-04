#!/usr/bin/env python3
"""
RRC Drilling Permit Master + Trailer (with lat/lon) — refresh.

Source: https://mft.rrc.texas.gov/link/f5dfea9c-bb39-4a5e-a44e-fb522e088cba
        End-of-Month File. ASCII fixed-width. Multi-segment record format
        per oga049m manual. Cumulates lifetime since 1976.

Schema (oga049m, July 14 2004):
    Bytes 1-2 = RRC-TAPE-RECORD-ID. Each segment-type-keyed record carries:
        01 DAROOT     — application status root. Has county code, lease name,
                        district, operator name, status flag, permit no., issue date.
        02 DAPERMIT   — permit master. Issued permits only (subset of root). Has
                        well no., total depth, type-application code, received
                        date, issued date, amended date, extended date, spud date.
        14 DAW999A1   — GIS surface coordinates (one per permit).
        15 DAW999B1   — GIS bottom-hole coordinates.
        (03-13 omitted — field/restriction/check-register data not used here.)

DAROOT (record id "01") field offsets (1-indexed positions per oga049m):
        3-11   DA-PRIMARY-KEY     (status# 7 + sequence# 2)
        12-14  DA-COUNTY-CODE     (3-digit FIPS-like RRC code; 371 = Pecos)
        15-46  DA-LEASE-NAME      (32 chars)
        47-48  DA-DISTRICT        (2 digits; 08 / 7C for Permian)
        49-54  DA-OPERATOR-NUMBER (6 digits)
        67-98  DA-OPERATOR-NAME   (32 chars)
        101    DA-STATUS-OF-APP-FLAG  (P/A/W/D/E/C/O/X/Z; A = Approved)
        113-119  DA-PERMIT        (7-digit issued-permit no.)
        120-127  DA-ISSUE-DATE    (CCYYMMDD)

DAPERMIT (record id "02") field offsets:
        Note: oga049m page II.13 declares two `RRC-TAPE-RECORD-ID PIC X(02)`
        markers (POS 1 and POS 3) on this segment. Treated as 4-byte header;
        the segment proper begins at byte 5 per the printed POS column.
        5-11   DA-PERMIT-NUMBER       (7 digits)
        12-13  DA-PERMIT-SEQUENCE-NUMBER (2 digits)
        14-16  DA-PERMIT-COUNTY-CODE  (3 digits)
        17-48  DA-PERMIT-LEASE-NAME   (32 chars)
        49-50  DA-PERMIT-DISTRICT     (2 digits)
        51-56  DA-PERMIT-WELL-NUMBER  (6 chars)
        57-61  DA-PERMIT-TOTAL-DEPTH  (5 digits)
        62-67  DA-PERMIT-OPERATOR-NUMBER (6 digits)
        68-69  DA-TYPE-APPLICATION    (2 digits; 01=Drill, 12=Drill-Horizontal,
                                       08=Sidetrack, 13=Sidetrack-Horizontal,
                                       07=Re-Enter, 02-04=Deepen/Plug-Back, ...)
        132-139  DA-PERMIT-ISSUED-DATE  (CCYYMMDD)

DAW999A1 (record id "14") field offsets:
        3-14   DA-SURF-LOC-LONGITUDE  PIC 9(5)V9(7)  — 5 int + 7 fractional,
                                                       implied decimal at byte 8.
                                                       SOURCE IS POSITIVE; flip
                                                       sign for Texas (W of GMT).
        15-26  DA-SURF-LOC-LATITUDE   PIC 9(5)V9(7)

Datum: NAD27. Per oga049m: "coordinates do not necessarily represent a true
geographic location and are subject to change upon maintenance to the RRC's
survey boundaries." Repo convention is WGS84 — converted via pyproj.Transformer
EPSG:4267 → EPSG:4326. Conversion offset in Permian basin is ~10-15m,
within the source's own advertised precision.

Permian-county scope (per WIP_OPEN.md sprint context, matches scrape_rrc_w1.py):
    PECOS=371, REEVES=389, WARD=475, LOVING=301, WINKLER=495,
    CULBERSON=109, CRANE=103, UPTON=461, REAGAN=383, CROCKETT=105, TERRELL=443

Output: combined_points.csv 31-column schema, layer_id="drilling_permits".
        outputs/refresh/drilling_permits_<date>.csv (atomic write per §6.15).

Permit status filter: only "A" (Approved) rows surfaced as points. The Master
file alone has Approved permits; the Root segment carries the status flag and
must be joined by primary key to the Type-14 GIS record.

Hard rules respected:
    §6.1  No source-data file read into model context. Stream-parse only.
    §6.2  No fetch during build. This is the refresh path.
    §6.5  Try/except per record-type dispatcher; one bad row never aborts.
    §6.15 Atomic temp-file + os.replace.

Usage:
    python3 scripts/refresh_rrc_drilling_permits.py [--out outputs/refresh]
                                                    [--source URL_OR_PATH]

Exit codes:
    0  CSV written non-empty
    1  fetch failed (logged FETCH_FAILED, no partial output)
    2  parse failed (no permits joined; check schema drift)
"""
import argparse
import csv
import os
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

UA = "LRP-TX-GIS/1.0 (refinement-rrc-drilling-permits)"
SOURCE_URL = "https://mft.rrc.texas.gov/link/f5dfea9c-bb39-4a5e-a44e-fb522e088cba"

# combined_points.csv 31-column canonical schema (matches refresh_eia860 / refresh_uswtdb)
SCHEMA = [
    "layer_id", "lat", "lon", "name", "plant_code", "county", "technology",
    "capacity", "sector", "inr", "fuel", "mw", "zone", "poi", "entity",
    "funnel_stage", "group", "under_construction", "commissioned",
    "capacity_mw", "operator", "voltage", "osm_id", "depth_ft", "use",
    "aquifer", "project", "manu", "model", "cap_kw", "year",
]

# 11 Permian counties — RRC numeric county codes per oga049m Section III
PERMIAN_COUNTIES = {
    "371": "PECOS",
    "389": "REEVES",
    "475": "WARD",
    "301": "LOVING",
    "495": "WINKLER",
    "109": "CULBERSON",
    "103": "CRANE",
    "461": "UPTON",
    "383": "REAGAN",
    "105": "CROCKETT",
    "443": "TERRELL",
}

# DA-TYPE-APPLICATION code → human label (oga049m II.16)
TYPE_APPL = {
    "01": "Drill",
    "02": "Deepen-below-casing",
    "03": "Deepen-within-casing",
    "04": "Plug-back",
    "05": "Other",
    "06": "Amended-drill",
    "07": "Re-enter",
    "08": "Sidetrack",
    "09": "Field-transfer",
    "10": "Amended-pre-1977",
    "11": "Drill-direct-sidetrack",
    "12": "Drill-horizontal",
    "13": "Sidetrack-horizontal",
    "14": "Recompletion",
    "15": "Reclass",
}

# Texas geographic envelope (filter sanity bounds; same as refresh_uswtdb)
TX_LAT_MIN, TX_LAT_MAX = 25.0, 37.0
TX_LON_MIN, TX_LON_MAX = -107.0, -93.0


def fetch_with_retry(url, attempts=5, sleep=10):
    """Standard OPERATING.md §8 helper. Returns response bytes or raises last."""
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": UA, "Accept": "*/*"},
            )
            with urllib.request.urlopen(req, timeout=600) as r:
                return r.read()
        except Exception as e:
            last = e
            sys.stderr.write(f"[fetch-retry {i+1}/{attempts}] {url}: {e}\n")
            time.sleep(sleep)
    raise last


def stream_records(blob_bytes):
    """Yield (record_id, raw_line) tuples. Splits on CRLF/LF; handles short lines.

    Records are line-delimited in the public release (not the original 510-byte
    fixed-block tape format described in oga049m §I.3). Each line begins with
    the 2-byte RRC-TAPE-RECORD-ID. Empty lines and lines shorter than 2 bytes
    are skipped silently.
    """
    text = blob_bytes.decode("latin-1", errors="replace")
    for raw in text.splitlines():
        if len(raw) < 2:
            continue
        yield raw[:2], raw


def parse_implied_decimal(s, int_digits=5, frac_digits=7):
    """PIC 9(5)V9(7) → float. Whitespace/non-numeric → None."""
    s = s.strip()
    if not s or not s.replace("0", "").strip(" .") and s.strip("0 ") == "":
        return None
    if not s.replace(".", "").isdigit():
        # Strip non-numeric (e.g. embedded spaces in malformed records)
        digits = "".join(c for c in s if c.isdigit())
        if len(digits) < int_digits + frac_digits:
            return None
        s = digits[: int_digits + frac_digits]
    if len(s) < int_digits + frac_digits:
        s = s.zfill(int_digits + frac_digits)
    try:
        int_part = int(s[:int_digits])
        frac_part = int(s[int_digits : int_digits + frac_digits])
        return int_part + frac_part / (10 ** frac_digits)
    except ValueError:
        return None


def parse_root(line):
    """Type 01 DAROOT. Returns dict of joinable fields or None on parse error.

    Positions are 1-indexed per oga049m; Python slicing is 0-indexed half-open.
    """
    try:
        return {
            "primary_key": line[2:11].strip(),                 # 3-11 (9 chars)
            "county_code": line[11:14].strip(),                # 12-14
            "lease_name": line[14:46].strip(),                 # 15-46
            "district": line[46:48].strip(),                   # 47-48
            "operator_name": line[66:98].strip(),              # 67-98
            "status_flag": line[100:101] if len(line) > 100 else "",  # 101
            "permit_no": line[112:119].strip().lstrip("0"),    # 113-119
            "issue_date": line[119:127].strip(),               # 120-127 (CCYYMMDD)
        }
    except (IndexError, ValueError):
        return None


def parse_permit(line):
    """Type 02 DAPERMIT. 4-byte header per oga049m page II.13 anomaly
    (`RRC-TAPE-RECORD-ID PIC X(02)` declared at both POS 1 and POS 3); segment
    proper begins at byte 5."""
    try:
        return {
            "primary_key": line[4:13].strip(),                 # 5-13 (permit# 7 + seq 2)
            "well_number": line[50:56].strip(),                # 51-56
            "total_depth": line[56:61].strip().lstrip("0"),    # 57-61
            "type_appl": line[67:69].strip(),                  # 68-69
            "issued_date": line[131:139].strip(),              # 132-139
        }
    except (IndexError, ValueError):
        return None


def parse_gis_surface(line):
    """Type 14 DAW999A1. Returns (primary_key, lat, lon) in NAD27 or None.

    Source layout (post-record-id):
        bytes 3-14:  longitude (12 chars, implied decimal 5.7), POSITIVE in source
        bytes 15-26: latitude (12 chars, implied decimal 5.7)

    The Type 14 record key on the public ASCII feed: empirical tests are
    required to confirm whether the primary-key field follows the record id
    (as in DAROOT) or whether the join is positional (one Type 14 per
    immediately-preceding DAROOT/DAPERMIT block). oga049m page II.75 declares
    the segment WORKING-STORAGE without explicitly listing a key field. We
    extract the 9-byte field at bytes 27-35 if present and treat it as the
    candidate primary key; if absent, the caller falls back to positional
    nearest-preceding-root joining.
    """
    try:
        lon_raw = line[2:14]
        lat_raw = line[14:26]
        lon = parse_implied_decimal(lon_raw)
        lat = parse_implied_decimal(lat_raw)
        # Optional trailing primary key (some tape variants append it for join)
        pk_raw = line[26:35].strip() if len(line) >= 35 else ""
        pk = pk_raw if pk_raw.isdigit() and len(pk_raw) == 9 else ""
        if lat is None or lon is None:
            return None
        return {"primary_key": pk, "lat": lat, "lon": -lon}  # sign-flip for TX
    except (IndexError, ValueError):
        return None


def nad27_to_wgs84(lat, lon):
    """NAD27 (EPSG:4267) → WGS84 (EPSG:4326). Uses pyproj if available; falls
    back to identity (~12m offset in W. Texas) with a one-time warning."""
    global _TRANSFORMER
    try:
        return _TRANSFORMER.transform(lon, lat)[::-1]  # transformer returns (x, y)
    except NameError:
        try:
            from pyproj import Transformer
            _TRANSFORMER = Transformer.from_crs("EPSG:4267", "EPSG:4326", always_xy=True)
            return _TRANSFORMER.transform(lon, lat)[::-1]
        except Exception as e:
            sys.stderr.write(f"[warn] pyproj unavailable ({e}); using NAD27 coords as WGS84 (~12m offset)\n")
            _TRANSFORMER = None
            return lat, lon
    except Exception:
        return lat, lon


def empty_row():
    return {col: "" for col in SCHEMA}


def yyyymmdd_to_iso(s):
    """8-digit CCYYMMDD → 'YYYY-MM-DD'. Empty/zero → ''."""
    s = s.strip()
    if len(s) != 8 or not s.isdigit() or s == "00000000":
        return ""
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}"


def yyyymmdd_to_year(s):
    """8-digit CCYYMMDD → 'YYYY' int as string. Empty/zero → ''."""
    s = s.strip()
    if len(s) != 8 or not s.isdigit() or s == "00000000":
        return ""
    return s[:4]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="outputs/refresh")
    ap.add_argument("--source", default=SOURCE_URL,
                    help="URL or local file path. Useful for re-runs against a cached blob.")
    ap.add_argument("--limit-records", type=int, default=0,
                    help="Stop after N records. 0 = no limit. Smoke-test aid.")
    args = ap.parse_args()

    today = date.today().isoformat()

    # --- Fetch ---------------------------------------------------------------
    if args.source.startswith("http://") or args.source.startswith("https://"):
        sys.stderr.write(f"[fetch] {args.source}\n")
        try:
            blob = fetch_with_retry(args.source)
        except Exception as e:
            sys.stderr.write(f"FETCH_FAILED: {e}\n")
            return 1
    else:
        sys.stderr.write(f"[read-local] {args.source}\n")
        try:
            with open(args.source, "rb") as f:
                blob = f.read()
        except OSError as e:
            sys.stderr.write(f"FETCH_FAILED (local): {e}\n")
            return 1

    # If response is a zip, extract the single inner ASCII file
    if blob[:4] == b"PK\x03\x04":
        import io
        import zipfile
        try:
            with zipfile.ZipFile(io.BytesIO(blob)) as zf:
                names = zf.namelist()
                if not names:
                    sys.stderr.write("FETCH_FAILED: empty zip\n")
                    return 1
                # Heuristic: largest member is the data file
                target = max(names, key=lambda n: zf.getinfo(n).file_size)
                sys.stderr.write(f"[zip] extracting {target} ({zf.getinfo(target).file_size:,} bytes)\n")
                blob = zf.read(target)
        except zipfile.BadZipFile as e:
            sys.stderr.write(f"FETCH_FAILED: bad zip ({e})\n")
            return 1

    sys.stderr.write(f"[fetched] {len(blob):,} bytes\n")

    # --- Pass 1: scan all records, retain only Permian roots & their permits ---
    roots = {}     # primary_key -> root dict, Permian only, status='A'
    permits = {}   # primary_key -> permit dict, joined later
    gis_keyed = {}    # primary_key -> (lat_nad27, lon_nad27)
    gis_positional = []  # [(file_offset_index, lat, lon), ...] for fallback joining
    last_root_pk = None
    n_total = n_root = n_permit = n_gis = 0

    for record_id, line in stream_records(blob):
        n_total += 1
        if args.limit_records and n_total > args.limit_records:
            break
        try:
            if record_id == "01":
                r = parse_root(line)
                if r is None:
                    continue
                n_root += 1
                # Permian filter: drop everything else immediately to bound memory.
                if r["county_code"] not in PERMIAN_COUNTIES:
                    last_root_pk = None
                    continue
                # Status filter: only Approved permits become points
                if r["status_flag"] != "A":
                    last_root_pk = None
                    continue
                roots[r["primary_key"]] = r
                last_root_pk = r["primary_key"]
            elif record_id == "02":
                p = parse_permit(line)
                if p is None:
                    continue
                n_permit += 1
                if p["primary_key"] in roots:
                    permits[p["primary_key"]] = p
            elif record_id == "14":
                g = parse_gis_surface(line)
                if g is None:
                    continue
                n_gis += 1
                if g["primary_key"] and g["primary_key"] in roots:
                    gis_keyed[g["primary_key"]] = (g["lat"], g["lon"])
                elif last_root_pk is not None:
                    # Positional fallback: associate with the most recently
                    # seen Permian-Approved root. oga049m segment hierarchy
                    # places DAW999A1 directly below DAROOT (page I.2 tree).
                    gis_keyed.setdefault(last_root_pk, (g["lat"], g["lon"]))
        except Exception as e:
            sys.stderr.write(f"[parse-warn] line at offset {n_total}: {e}\n")
            continue

    sys.stderr.write(
        f"[scanned] total={n_total:,} roots={n_root:,} permits={n_permit:,} gis={n_gis:,}\n"
        f"[permian] roots_kept={len(roots):,} gis_joined={len(gis_keyed):,}\n"
    )

    if not roots:
        sys.stderr.write("ERROR: 0 Permian Approved roots found — schema drift suspected.\n")
        return 2

    if not gis_keyed:
        sys.stderr.write("ERROR: 0 Permian permits joined to GIS coords — schema drift on Type 14.\n")
        return 2

    # --- Build output rows ---------------------------------------------------
    out_rows = []
    skipped_oob = 0
    for pk, root in roots.items():
        coords = gis_keyed.get(pk)
        if coords is None:
            continue
        lat_nad27, lon_nad27 = coords
        lat, lon = nad27_to_wgs84(lat_nad27, lon_nad27)

        # Sanity: must fall within Texas envelope post-conversion
        if not (TX_LAT_MIN < lat < TX_LAT_MAX and TX_LON_MIN < lon < TX_LON_MAX):
            skipped_oob += 1
            continue

        permit = permits.get(pk, {})
        county_name = PERMIAN_COUNTIES.get(root["county_code"], "")
        type_appl_label = TYPE_APPL.get(permit.get("type_appl", ""), "") if permit else ""

        row = empty_row()
        row.update({
            "layer_id": "drilling_permits",
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "name": root["lease_name"],                  # Lease name = popup title
            "plant_code": root["permit_no"] or pk,        # Permit # for popup
            "county": county_name,
            "operator": root["operator_name"],
            "technology": type_appl_label,                # "Drill", "Drill-horizontal", etc.
            "depth_ft": permit.get("total_depth", "") if permit else "",
            "commissioned": yyyymmdd_to_iso(
                permit.get("issued_date", "") if permit else root["issue_date"]
            ),
            "year": yyyymmdd_to_year(
                permit.get("issued_date", "") if permit else root["issue_date"]
            ),
            "project": permit.get("well_number", "") if permit else "",  # well # in popup
            "zone": root["district"],                     # RRC district
            "funnel_stage": "Approved",
        })
        out_rows.append(row)

    sys.stderr.write(
        f"[built] rows={len(out_rows):,} skipped_oob={skipped_oob:,}\n"
    )

    if not out_rows:
        sys.stderr.write("ERROR: 0 rows after sanity filtering\n")
        return 2

    # --- Write atomically ----------------------------------------------------
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"drilling_permits_{today}.csv"
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")

    with open(tmp_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SCHEMA)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    os.replace(tmp_path, out_path)

    sys.stderr.write(f"[wrote] {out_path} ({len(out_rows):,} rows)\n")
    print(f"OK drilling_permits={len(out_rows)} src={args.source}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
