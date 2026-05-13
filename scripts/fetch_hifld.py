#!/usr/bin/env python3
"""Generic HIFLD / ArcGIS FeatureServer fetcher.

Queries a FeatureServer layer for a bounding box, paginates through all
results, and writes a single GeoJSON FeatureCollection. Output goes to
data/hifld/<slug>.geojson and is consumed by layers.yaml entries.

Usage:
    python3 scripts/fetch_hifld.py <slug> <featureserver_url>

The script is invoked once per HIFLD layer; layers.yaml points each
layer at the resulting .geojson file via `file:`.

6-county Permian bbox is hard-coded. Adjust HIFLD_BBOX if the scope
changes.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# 6-county Permian bbox (W, S, E, N) — Pecos/Reeves/Ward/Midland/Martin/Reagan.
# Generous padding so cross-county pipelines/lines aren't clipped at edges.
HIFLD_BBOX = (-104.0, 30.0, -101.0, 32.6)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "hifld"


def query_layer(url: str, bbox: tuple) -> dict:
    """Query a FeatureServer layer URL, paginating until exhausted.

    Returns a GeoJSON FeatureCollection (dict).
    """
    feats: list[dict] = []
    offset = 0
    page_size = 1000
    while True:
        params = {
            "f": "geojson",
            "where": "1=1",
            "outFields": "*",
            "geometry": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
            "geometryType": "esriGeometryEnvelope",
            "spatialRel": "esriSpatialRelIntersects",
            "inSR": "4326",
            "outSR": "4326",
            "resultOffset": str(offset),
            "resultRecordCount": str(page_size),
        }
        q = url + "/query?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(q, headers={"User-Agent": "lrp-tx-gis/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        page = data.get("features", []) or []
        feats.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
        time.sleep(0.25)
    return {"type": "FeatureCollection", "features": feats}


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: fetch_hifld.py <slug> <featureserver_layer_url>", file=sys.stderr)
        return 2
    slug, url = sys.argv[1], sys.argv[2]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dst = OUT_DIR / f"{slug}.geojson"
    tmp = dst.with_suffix(".geojson.tmp")

    print(f"=== fetch hifld: {slug} ===")
    print(f"  url:  {url}")
    print(f"  bbox: {HIFLD_BBOX}")
    fc = query_layer(url, HIFLD_BBOX)
    n = len(fc["features"])
    print(f"  features fetched: {n}")
    with open(tmp, "w") as f:
        json.dump(fc, f)
    tmp.replace(dst)
    size_kb = dst.stat().st_size / 1024
    print(f"  wrote: {dst} ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
