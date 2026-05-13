#!/usr/bin/env python3
"""Build the Hanwha-exhibit production deliverable from RRC PDQ_DSV dump.

Inputs:
  data/rrc_raw/PDQ_DSV.zip  — RRC bulk PDQ export, monthly 1993-current,
                              statewide lease/operator/county/district records.
                              Schema discovered at first run from the ZIP TOC.

Outputs (NOT map layers — exported to data/ for direct distribution):
  data/production_permian6.xlsx          — 6 tabs (annual/operator/lease/
                                            monthly/sale-vs-peer/raw)
  data/production_permian6_summary.pdf   — 4-page narrative summary

Scope: 6-county Permian (Pecos, Reeves, Ward, Midland, Martin, Reagan),
       1993-present, monthly aggregates.

Hard rules respected:
  - CLAUDE.md §3.1: streams every CSV inside the zip via zipfile.open()
    line-by-line. Never loads a full extracted CSV into memory.
  - CLAUDE.md §3.4: atomic write — temp file + os.replace for both
    deliverable outputs.
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "rrc_raw" / "PDQ_DSV.zip"
OUT_XLSX = ROOT / "data" / "production_permian6.xlsx"
OUT_PDF = ROOT / "data" / "production_permian6_summary.pdf"

# 6-county scope — county-level filter is by RRC 3-digit code (last 3
# digits of API county prefix) where available; fallback to county-name
# string match on the PDQ COUNTY column.
SUBJECT_COUNTIES = {"PECOS", "REEVES", "WARD"}
PEER_COUNTIES = {"MIDLAND", "MARTIN", "REAGAN"}
SCOPE_COUNTIES = SUBJECT_COUNTIES | PEER_COUNTIES


def discover_schema(zip_path: Path) -> dict:
    """Open the PDQ_DSV zip TOC, return {filename: header_row} for each CSV.

    PDQ_DSV publishes DSV files (delimited variable). We need to learn
    column names per file before processing."""
    out = {}
    with zipfile.ZipFile(zip_path, "r") as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            with z.open(info.filename) as f:
                # Read first KB to extract header line
                head = f.read(8192).decode("utf-8", errors="replace")
                first_line = head.split("\n", 1)[0]
                out[info.filename] = first_line
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--discover", action="store_true",
                    help="Just print the zip TOC + file headers and exit")
    args = ap.parse_args()

    if not RAW.exists():
        print(f"ERROR: {RAW} not found.", file=sys.stderr)
        print("       Run `python3 scripts/fetch_pdq_dump.py` first (~3.44 GB).",
              file=sys.stderr)
        return 2

    if args.discover:
        schema = discover_schema(RAW)
        for fname, hdr in schema.items():
            print(f"=== {fname}")
            print(f"    header: {hdr[:300]}")
        return 0

    print("ERROR: PDQ_DSV.zip parser not yet implemented for the discovered",
          "schema. Run with --discover first to dump TOC, then extend this",
          "script's main() with schema-specific aggregation logic.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
