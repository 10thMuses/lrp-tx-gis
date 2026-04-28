"""
Chat 111: Extend `county_labels` from 46 (West Texas) to all 254 Texas counties.

Source: TIGER 2024 county polygons (Census), filtered STATEFP=='48'.
Position: representative_point() per shapely (handles concave shapes — e.g.,
counties wrapped around water bodies or lobed by river meanders — better than
centroid, which can land outside the polygon).

Replaces (not dedupes) existing county_labels features in combined_geoms.geojson.
Atomic write via temp + os.replace, per OPERATING.md §6.15.
"""
import io
import json
import os
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

import shapefile  # pyshp
from shapely.geometry import shape

REPO = Path(__file__).resolve().parent.parent
COMBINED = REPO / "combined_geoms.geojson"
WORK = REPO / "outputs" / "refresh"
WORK.mkdir(parents=True, exist_ok=True)
TIGER_URL = "https://www2.census.gov/geo/tiger/TIGER2024/COUNTY/tl_2024_us_county.zip"
ZIP_PATH = WORK / "tl_2024_us_county.zip"


def fetch_with_retry(url, dest, attempts=5, sleep=10):
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
            return
        except Exception as e:
            if i == attempts - 1:
                raise
            print(f"  fetch attempt {i+1} failed: {e}; retry in {sleep}s")
            time.sleep(sleep)


def main():
    if not ZIP_PATH.exists() or ZIP_PATH.stat().st_size < 100_000:
        print(f"[fetch] {TIGER_URL}")
        fetch_with_retry(TIGER_URL, ZIP_PATH)
    print(f"[fetch] zip size {ZIP_PATH.stat().st_size:,} B")

    # pyshp can read directly from in-memory shp/dbf/shx — extract via zipfile
    with zipfile.ZipFile(ZIP_PATH) as zf:
        names = zf.namelist()
        shp_name = next(n for n in names if n.endswith(".shp"))
        base = shp_name[:-4]
        shp_buf = io.BytesIO(zf.read(base + ".shp"))
        dbf_buf = io.BytesIO(zf.read(base + ".dbf"))
        shx_buf = io.BytesIO(zf.read(base + ".shx"))

    new_features = []
    skipped = 0
    with shapefile.Reader(shp=shp_buf, dbf=dbf_buf, shx=shx_buf) as r:
        fields = [f[0] for f in r.fields[1:]]  # drop deletion flag
        i_state = fields.index("STATEFP")
        i_name = fields.index("NAME")
        for sr in r.iterShapeRecords():
            rec = sr.record
            if rec[i_state] != "48":
                skipped += 1
                continue
            geom = shape(sr.shape.__geo_interface__)
            if geom.is_empty or not geom.is_valid:
                geom = geom.buffer(0)
            pt = geom.representative_point()
            name = rec[i_name]
            new_features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [round(pt.x, 6), round(pt.y, 6)]},
                "properties": {"layer_id": "county_labels", "name": f"{name} County"},
            })

    print(f"[tiger] non-Texas skipped: {skipped}; Texas counties: {len(new_features)}")
    if len(new_features) < 254:
        print(f"FATAL: expected 254 Texas counties, got {len(new_features)}", file=sys.stderr)
        sys.exit(1)

    # Read combined, filter, append, atomic write
    with open(COMBINED) as f:
        data = json.load(f)
    before = len(data["features"])
    kept = [f for f in data["features"] if f.get("properties", {}).get("layer_id") != "county_labels"]
    dropped = before - len(kept)
    kept.extend(new_features)
    data["features"] = kept

    tmp = COMBINED.with_suffix(".geojson.tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, separators=(",", ":"))
    os.replace(tmp, COMBINED)
    print(f"[combined] dropped {dropped} old county_labels; appended {len(new_features)} new; total features {len(kept)}")


if __name__ == "__main__":
    main()
