#!/usr/bin/env python3
"""
RRC bulk-download fetcher via GoAnywhere PrimeFaces.

Bulk endpoint: https://mft.rrc.texas.gov/link/<UUID> renders a PrimeFaces
folder-browser XHTML page. Each file in the folder is a row in a JSF
DataTable; clicking submits the form with `fileTable:<row>:j_id_2f` plus the
session ViewState. The server then streams the file as application/force-download.

Protocol (validated 2026-05-13):
  1. GET landing page → harvest JSESSIONID cookie + javax.faces.ViewState
  2. POST to /webclient/godrive/PublicGoDrive.xhtml with:
       fileTable_selection=
       fileList_SUBMIT=1
       javax.faces.ViewState=<from step 1>
       fileTable:<row>:j_id_2f=fileTable:<row>:j_id_2f
       fileList=fileList
  3. Stream response to data/rrc_raw/<filename> via atomic temp+replace.

Sources downloaded:
  - dbf900.txt.gz       — Full Wellbore (ASCII fixed-width, 247-byte records,
                          28 segments keyed by 2-byte record-ID prefix).
                          Layout: docs/rrc_layouts/wba091_well-bore-database.pdf.
                          (~366 MB compressed, ~1.97 GB uncompressed.)
  - dp_*_pending_<ts>.txt — Drilling Permits Pending: 11 pipe-delimited TXT
                          files per snapshot, foreign-keyed by API_SEQUENCE_NUMBER.
                          Layout: docs/rrc_layouts/pendingdrillingpermits.pdf.
                          Latest snapshot only.

Hard rules respected:
  - CLAUDE.md §3.1: never reads source data into context. All download is
    streamed to disk via requests.iter_content + atomic os.replace.
  - CLAUDE.md §3.4: atomic in-place writes (tmp + os.replace).
  - OPERATING.md §2 / banned phrases: no recap. Single CLI: `python3 scripts/fetch_rrc.py [wells|permits|all]`.

Idempotent: skips files already cached unless --force.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "rrc_raw"

UA = (
    "Mozilla/5.0 (compatible; lrp-tx-gis research; "
    "contact andrea@landresourcepartners.com)"
)
THROTTLE_SECS = 1.5
HTTP_TIMEOUT = 600  # 10 min for large file streams
CHUNK = 65536

# MFT folder UUIDs.
WELLBORE_UUID = "b070ce28-5c58-4fe2-9eb7-8b70befb7af9"  # Full Wellbore folder
PENDING_UUID = "0ad92a65-4212-49a1-98a7-d667a55fb497"   # Drilling Permits Pending folder

POST_URL = "https://mft.rrc.texas.gov/webclient/godrive/PublicGoDrive.xhtml"

VIEWSTATE_RE = re.compile(
    r'name="javax\.faces\.ViewState[^"]*"[^>]*value="([^"]+)"'
)
ROW_RE = re.compile(
    r'<tr[^>]*data-ri="(\d+)"[^>]*>(.*?)</tr>', re.DOTALL
)
CELL_RE = re.compile(r'<td[^>]*>(.*?)</td>', re.DOTALL)
TAG_RE = re.compile(r'<[^>]+>')
WS_RE = re.compile(r'\s+')


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = UA
    return s


def get_folder(session: requests.Session, uuid: str) -> tuple[str, str]:
    """GET the folder landing page. Return (html, view_state)."""
    url = f"https://mft.rrc.texas.gov/link/{uuid}"
    r = session.get(url, timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    m = VIEWSTATE_RE.search(r.text)
    if not m:
        raise RuntimeError(f"could not find ViewState on {url}")
    return r.text, m.group(1)


def list_files(html: str) -> list[tuple[int, str, str]]:
    """Parse rendered rows. Yield (row_index, filename, size_str)."""
    out: list[tuple[int, str, str]] = []
    for m in ROW_RE.finditer(html):
        ri = int(m.group(1))
        cells = CELL_RE.findall(m.group(2))
        texts = [
            WS_RE.sub(" ", TAG_RE.sub(" ", c)).strip() for c in cells
        ]
        # Empirical column layout: [icon, sel, name, modified, size, ...]
        name = texts[2] if len(texts) > 2 else ""
        size = texts[4] if len(texts) > 4 else ""
        if not name:
            continue
        out.append((ri, name, size))
    return out


def download_row(
    session: requests.Session,
    view_state: str,
    row_index: int,
    out_path: Path,
) -> int:
    """POST the row download and stream to out_path atomically.
    Returns bytes written."""
    payload = {
        "fileTable_selection": "",
        "fileList_SUBMIT": "1",
        "javax.faces.ViewState": view_state,
        f"fileTable:{row_index}:j_id_2f": f"fileTable:{row_index}:j_id_2f",
        "fileList": "fileList",
    }
    r = session.post(POST_URL, data=payload, timeout=HTTP_TIMEOUT, stream=True)
    r.raise_for_status()
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with open(tmp, "wb") as f:
        for chunk in r.iter_content(chunk_size=CHUNK):
            f.write(chunk)
            written += len(chunk)
    r.close()
    os.replace(tmp, out_path)
    return written


def fetch_wellbore(force: bool = False) -> Path:
    """Download dbf900.txt.gz to data/rrc_raw/. Idempotent."""
    out = RAW_DIR / "dbf900.txt.gz"
    if out.exists() and not force:
        size_mb = out.stat().st_size / (1024 * 1024)
        print(f"  cached: {out.name} ({size_mb:.1f} MB)")
        return out
    print(f"  fetching {out.name} (~366 MB) ...")
    session = make_session()
    html, vs = get_folder(session, WELLBORE_UUID)
    files = list_files(html)
    target_row = None
    for ri, name, size in files:
        if name == "dbf900.txt.gz":
            target_row = ri
            print(f"    row {ri}: {name} ({size})")
            break
    if target_row is None:
        raise RuntimeError("dbf900.txt.gz not found in wellbore folder")
    time.sleep(THROTTLE_SECS)
    n = download_row(session, vs, target_row, out)
    print(f"    wrote {n} bytes ({n/(1024*1024):.1f} MB)")
    return out


def fetch_pending_latest(force: bool = False) -> Path:
    """Download the most recent Pending snapshot (all 11 dp_* files).
    Returns the directory containing them."""
    out_dir = RAW_DIR / "pending_latest"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"  fetching latest Pending snapshot to {out_dir} ...")
    session = make_session()
    html, vs = get_folder(session, PENDING_UUID)
    files = list_files(html)
    if not files:
        raise RuntimeError("no files in Pending folder")

    # Extract timestamps and group by snapshot. Filename pattern:
    #   dp_<name>_pending_<YYYYMMDDhhmmss>.txt
    snapshots: dict[str, list[tuple[int, str]]] = {}
    snap_re = re.compile(r"_pending_(\d{14})\.txt$")
    for ri, name, _sz in files:
        m = snap_re.search(name)
        if m:
            snapshots.setdefault(m.group(1), []).append((ri, name))
    if not snapshots:
        raise RuntimeError("no _pending_<ts> files found")
    latest_ts = max(snapshots)
    rows = snapshots[latest_ts]
    print(f"    latest snapshot: {latest_ts}  ({len(rows)} files)")
    for ri, name in rows:
        out_path = out_dir / name
        if out_path.exists() and not force:
            print(f"      cached: {name}")
            continue
        time.sleep(THROTTLE_SECS)
        # Re-fetch ViewState per request — the JSF view may invalidate
        # after each submission. Cheap belt-and-suspenders.
        html2, vs2 = get_folder(session, PENDING_UUID)
        n = download_row(session, vs2, ri, out_path)
        print(f"      {name}: {n/1024:.1f} KB")
    # Write a manifest noting which snapshot is current
    (out_dir / "_snapshot_ts.txt").write_text(latest_ts + "\n")
    return out_dir


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", choices=["wells", "permits", "all"], default="all", nargs="?")
    ap.add_argument("--force", action="store_true",
                    help="re-download even if cached")
    args = ap.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"=== RRC fetch ({args.target}) ===")
    if args.target in ("wells", "all"):
        fetch_wellbore(force=args.force)
    if args.target in ("permits", "all"):
        fetch_pending_latest(force=args.force)
    print("=== fetch complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
