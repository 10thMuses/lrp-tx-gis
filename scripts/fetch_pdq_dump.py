#!/usr/bin/env python3
"""Download the RRC Production Data Query (PDQ) bulk dump via GoAnywhere MFT.

Source: https://mft.rrc.texas.gov/link/1f5ddb8d-329a-4459-b7f8-177b4f5ee60d
File:   PDQ_DSV.zip (~3.44 GB compressed)
Update cadence: "Last Saturday each month" per RRC.

Streams to data/rrc_raw/PDQ_DSV.zip via atomic temp+os.replace. Reuses
the GoAnywhere PrimeFaces protocol from scripts/fetch_rrc.py.

Hard rules respected:
  - CLAUDE.md §3.1: streams to disk, never reads source data into memory.
  - CLAUDE.md §3.4: atomic in-place writes via temp + os.replace.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

# Reuse the GoAnywhere primitives from fetch_rrc.py
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_rrc import (  # noqa: E402
    THROTTLE_SECS,
    download_row,
    get_folder,
    list_files,
    make_session,
)

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "rrc_raw"
PDQ_UUID = "1f5ddb8d-329a-4459-b7f8-177b4f5ee60d"


def main() -> int:
    out = RAW_DIR / "PDQ_DSV.zip"
    if out.exists() and "--force" not in sys.argv:
        size_gb = out.stat().st_size / (1024**3)
        print(f"  cached: {out.name} ({size_gb:.2f} GB)")
        return 0
    print(f"  fetching {out.name} (~3.44 GB compressed) ...")
    session = make_session()
    html, vs = get_folder(session, PDQ_UUID)
    files = list_files(html)
    target_row = None
    for ri, name, size in files:
        if name == "PDQ_DSV.zip":
            target_row = ri
            print(f"    row {ri}: {name} ({size})")
            break
    if target_row is None:
        print("ERROR: PDQ_DSV.zip not found in folder", file=sys.stderr)
        return 2
    time.sleep(THROTTLE_SECS)
    n = download_row(session, vs, target_row, out)
    print(f"    wrote {n} bytes ({n / (1024**3):.2f} GB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
