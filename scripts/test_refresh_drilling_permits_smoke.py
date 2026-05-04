#!/usr/bin/env python3
"""Synthetic-fixture smoke test for refresh_rrc_drilling_permits.py.

Builds a tiny multi-segment ASCII blob mirroring oga049m record layout:
- 2 DAROOT records (01): one Pecos-Approved, one non-Permian (filtered)
- 1 DAPERMIT record (02) for the Pecos root
- 1 DAW999A1 record (14) for the Pecos root, positional join

Exercises:
    parse_implied_decimal (PIC 9(5)V9(7))
    parse_root, parse_permit, parse_gis_surface
    Permian county filter
    Status-flag filter (only "A" Approved)
    Positional GIS-to-root join via last_root_pk
    NAD27 → WGS84 conversion (pyproj path)
    Sign-flip of longitude for Texas
    31-column SCHEMA emission
    Atomic temp-file rename
"""
import importlib.util
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "refresh_drill", REPO / "scripts" / "refresh_rrc_drilling_permits.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def _root(primary_key, county_code, status, permit_no, issue_date,
          lease="WILDCAT 1", district="08", operator="ACME OIL CO"):
    """Build an 01 DAROOT record. Bytes 1-2 = '01'. POS columns 1-indexed.
    Pad to at least byte 127 for DA-ISSUE-DATE access."""
    line = ["01"]                                  # 1-2
    line.append(primary_key.zfill(9))              # 3-11 DA-PRIMARY-KEY
    line.append(county_code.zfill(3))              # 12-14
    line.append(lease.ljust(32)[:32])              # 15-46 lease name
    line.append(district.zfill(2))                 # 47-48 district
    line.append("123456")                          # 49-54 operator number
    line.append(" " * 12)                          # 55-66 (CONVERTED-DATE + DATE-APP-RECEIVED)
    line.append(operator.ljust(32)[:32])           # 67-98 operator name
    line.append(" ")                               # 99 filler
    line.append(" ")                               # 100 HB1407 flag
    line.append(status)                            # 101 status flag
    line.append(" " * 11)                          # 102-112 problem flags
    line.append(permit_no.zfill(7))                # 113-119
    line.append(issue_date)                        # 120-127 CCYYMMDD
    return "".join(line)


def _permit(primary_key, well_number, total_depth, type_appl, issued_date):
    """Build an 02 DAPERMIT record with the documented 4-byte header anomaly."""
    line = ["02", "02"]                            # 1-2 + 3-4 (oga049m page II.13 anomaly)
    line.append(primary_key.zfill(9))              # 5-13 PERMIT-NUMBER + SEQUENCE
    line.append("371")                             # 14-16 county
    line.append("WILDCAT 1".ljust(32)[:32])        # 17-48 lease
    line.append("08")                              # 49-50 district
    line.append(well_number.ljust(6)[:6])          # 51-56 well number
    line.append(total_depth.zfill(5))              # 57-61 total depth
    line.append("123456")                          # 62-67 operator number
    line.append(type_appl.zfill(2))                # 68-69 type-application
    line.append(" " * 62)                          # 70-131 padding (other / address / dates)
    line.append(issued_date)                       # 132-139 issued date
    return "".join(line)


def _gis(longitude_pos, latitude_pos, primary_key=""):
    """Build a 14 DAW999A1 record. Lon/lat as PIC 9(5)V9(7) — 12 chars each.
    Source longitude is positive (gets sign-flipped on parse)."""
    line = ["14"]                                  # 1-2
    line.append(f"{int(longitude_pos * 10**7):012d}")   # 3-14 longitude
    line.append(f"{int(latitude_pos * 10**7):012d}")    # 15-26 latitude
    if primary_key:
        line.append(primary_key.zfill(9))          # 27-35 (optional trailing key)
    return "".join(line)


def make_fixture():
    """Synthetic blob: 1 Permian Approved permit with full GIS, plus noise."""
    records = [
        # Permian Approved permit — should produce one output row
        _root("100000001", "371", "A", "8500001", "20200615",
              lease="JONES STATE A", operator="PIONEER NATURAL"),
        _permit("100000001", "1H", "12500", "12", "20200615"),  # horizontal drill
        _gis(longitude_pos=103.4567890, latitude_pos=30.8765432),  # Pecos County area

        # Non-Permian root — filtered out
        _root("100000002", "001", "A", "8500002", "20200616"),  # Anderson County
        _gis(longitude_pos=95.0000000, latitude_pos=31.5000000),

        # Permian but non-Approved — filtered out
        _root("100000003", "389", "W", "8500003", "20200617"),  # Reeves Withdrawn
        _gis(longitude_pos=103.5000000, latitude_pos=31.4000000),

        # Permian Approved — but no GIS record (should be silently dropped)
        _root("100000004", "475", "A", "8500004", "20200618"),  # Ward, Approved, no coords
    ]
    return ("\n".join(records) + "\n").encode("latin-1")


def run():
    fixture = make_fixture()
    sys.stderr.write(f"[fixture] {len(fixture)} bytes, {fixture.count(b'\\n')} records\n")

    tmpdir = tempfile.mkdtemp(prefix="rrc-smoke-")
    try:
        fixture_path = Path(tmpdir) / "fixture.bin"
        fixture_path.write_bytes(fixture)
        out_dir = Path(tmpdir) / "refresh"

        # Run the script's main() with --source pointing at the fixture
        argv_save = sys.argv[:]
        sys.argv = [
            "refresh_rrc_drilling_permits.py",
            "--source", str(fixture_path),
            "--out", str(out_dir),
        ]
        try:
            rc = mod.main()
        finally:
            sys.argv = argv_save

        assert rc == 0, f"main() returned {rc}, expected 0"

        # Find the written CSV
        csvs = list(out_dir.glob("drilling_permits_*.csv"))
        assert len(csvs) == 1, f"expected 1 CSV, found {len(csvs)}: {csvs}"
        csv_path = csvs[0]

        # Verify contents
        import csv as csv_mod
        with open(csv_path) as f:
            rows = list(csv_mod.DictReader(f))

        assert len(rows) == 1, (
            f"expected exactly 1 row (only Pecos-Approved-with-GIS), got {len(rows)}: {rows}"
        )
        row = rows[0]

        # Schema check — all 31 columns present
        assert set(row.keys()) == set(mod.SCHEMA), (
            f"schema mismatch: {set(row.keys()) ^ set(mod.SCHEMA)}"
        )

        # Field-by-field assertions
        assert row["layer_id"] == "drilling_permits"
        assert row["county"] == "PECOS"
        assert row["funnel_stage"] == "Approved"
        assert row["technology"] == "Drill-horizontal", f"type-appl: {row['technology']}"
        assert row["operator"] == "PIONEER NATURAL"
        assert row["plant_code"] == "8500001"
        assert row["project"] == "1H"
        assert row["depth_ft"] == "12500"
        assert row["zone"] == "08"
        assert row["commissioned"] == "2020-06-15"
        assert row["year"] == "2020"

        # Coordinate checks
        lat = float(row["lat"])
        lon = float(row["lon"])
        # NAD27 (30.876, -103.456) → WGS84 should shift roughly +0.00001 lat, -0.00001 lon
        # in the Permian basin. Accept anywhere within 0.01° of the source coord.
        assert abs(lat - 30.876543) < 0.01, f"lat drift: {lat}"
        assert abs(lon - (-103.456789)) < 0.01, f"lon drift: {lon} (expected sign-flip)"
        assert lon < 0, f"longitude must be negative for Texas, got {lon}"

        sys.stderr.write(f"[pass] 1 row written, lat={lat}, lon={lon}\n")
        sys.stderr.write(f"[pass] all field assertions held\n")
        print("SMOKE OK")
        return 0

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(run())
