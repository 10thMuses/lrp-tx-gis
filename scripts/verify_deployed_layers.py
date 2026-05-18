#!/usr/bin/env python3
"""Verify the live production map: every layer in layers.yaml is actually
deployed as a non-empty PMTiles tileset, and report feature counts.

Per-layer prebuilt tiles live at  <base>/tiles/<layer_id>.pmtiles  (build.py
tier-3 resolution: https://lrp-tx-gis.netlify.app/tiles/<id>.pmtiles). This
reads each tileset's tilestats metadata via HTTP range requests — no full
download — using the same `pmtiles.reader` path build.py uses locally.

Intended uses:
  1. Ad-hoc audit: `python3 scripts/verify_deployed_layers.py`
  2. Auto-update guardrail: run AFTER build, BEFORE the deploy is accepted.
     Exit code is the gate.

Exit codes:
  0  every layers.yaml layer is live with count > 0
  1  one or more layers MISSING (404 / unreadable) or ZERO-count
  2  could not load layers.yaml or no layers found (harness error)

Hard rules respected: no source-data file read into context (only PMTiles
metadata, which is aggregate counts, never feature rows); read-only.
"""
import argparse
import gzip
import io
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

import yaml

DEFAULT_BASE = "https://lrp-tx-gis.netlify.app"
ROOT = Path(__file__).resolve().parent.parent
UA = "LRP-TX-GIS/1.0 (verify_deployed_layers)"


def http_range(url, offset, length, timeout=30, attempts=3):
    """Fetch bytes [offset, offset+length) via an HTTP Range request."""
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": UA,
                         "Range": f"bytes={offset}-{offset + length - 1}"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise FileNotFoundError(url)
            last = e
        except Exception as e:
            last = e
    raise last


def read_tilestats_counts(url):
    """Return {layer_name: count} from a remote PMTiles' tilestats metadata.

    Uses python-pmtiles with an HTTP-range byte source so only the header +
    metadata block transfer (typically a few KB), never the tile body.
    Falls back to a manual v3-header metadata parse if the lib API differs.
    """
    try:
        from pmtiles.reader import Reader
        reader = Reader(lambda off, ln: http_range(url, off, ln))
        md = reader.metadata()
    except FileNotFoundError:
        raise
    except Exception:
        # Manual PMTiles v3 fallback: 127-byte header; metadata offset/len at
        # fixed little-endian positions (offset@byte 26 u64, length@byte 34 u64).
        head = http_range(url, 0, 127)
        if head[:7] != b"PMTiles":
            raise ValueError(f"not a PMTiles file: {url}")
        import struct
        md_off = struct.unpack_from("<Q", head, 26)[0]
        md_len = struct.unpack_from("<Q", head, 34)[0]
        raw = http_range(url, md_off, md_len)
        try:
            raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
        except OSError:
            pass
        md = json.loads(raw)
    ts = md.get("tilestats") or {}
    layers = ts.get("layers") or []
    return {l.get("layer_name", f"layer{i}"): int(l.get("count", 0))
            for i, l in enumerate(layers)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE,
                    help="Deployed site origin (default: production).")
    ap.add_argument("--layers", default=str(ROOT / "layers.yaml"))
    ap.add_argument("--quiet", action="store_true",
                    help="Only print the summary + failures (for cron).")
    args = ap.parse_args()

    try:
        cfg = yaml.safe_load(open(args.layers))
        layer_ids = [d["id"] for d in cfg["layers"]]
    except Exception as e:
        print(f"FATAL: cannot load {args.layers}: {e}", file=sys.stderr)
        return 2
    if not layer_ids:
        print("FATAL: no layers in config", file=sys.stderr)
        return 2

    missing, empty, ok = [], [], []
    rows = []
    for lid in layer_ids:
        url = f"{args.base}/tiles/{lid}.pmtiles"
        try:
            counts = read_tilestats_counts(url)
            total = sum(counts.values())
            if total <= 0:
                empty.append(lid)
                rows.append((lid, "EMPTY", 0))
            else:
                ok.append(lid)
                rows.append((lid, "live", total))
        except FileNotFoundError:
            missing.append(lid)
            rows.append((lid, "MISSING (404)", 0))
        except Exception as e:
            missing.append(lid)
            rows.append((lid, f"ERROR {type(e).__name__}", 0))

    if not args.quiet:
        w = max(len(r[0]) for r in rows)
        print(f"\nProd layer verification — {args.base}/tiles/")
        print("-" * (w + 30))
        for lid, status, n in rows:
            flag = "  " if status == "live" else "!!"
            print(f"{flag} {lid:<{w}}  {status:<16} {n:>10,}" if n else
                  f"{flag} {lid:<{w}}  {status}")
        print("-" * (w + 30))

    total_feat = sum(n for _, s, n in rows if s == "live")
    print(f"\n{len(ok)}/{len(layer_ids)} layers live · "
          f"{total_feat:,} total features · "
          f"missing={len(missing)} empty={len(empty)}")
    if missing:
        print(f"MISSING: {', '.join(missing)}")
    if empty:
        print(f"EMPTY:   {', '.join(empty)}")

    return 0 if not missing and not empty else 1


if __name__ == "__main__":
    sys.exit(main())
