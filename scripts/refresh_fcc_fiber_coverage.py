"""
FCC Fiber Coverage refresh — ArcGIS Living Atlas BDC, June 2025 vintage.

Source: ArcGIS Living Atlas FCC BDC FeatureServer, layer 5 (H3 res-8 hexes).
  https://services8.arcgis.com/peDZJliSvYims39Q/arcgis/rest/services/FCC_Broadband_Data_Collection_December_2024_View/FeatureServer/5
  (URL slug is legacy; service refreshed 2026-03-06; item title is "June 2025 BDC".)

Scope: 23-county Permian-focus footprint (Andrews, Borden, Brewster, Crane, Crockett, Culberson, Dawson, Ector, Fisher, Glasscock, Howard, Irion, Jeff Davis, Kent, Loving, Martin, Midland, Mitchell, Pecos, Reeves, Reagan, Schleicher, Scurry, Sterling, Sutton, Terrell, Tom Green, Upton, Ward, Winkler — all West-TX counties touching ERCOT Far West).
Filter: TotalBSLs > 0 within bbox -105.998,28.972,-100.115,32.525, then spatial-clip to county union.
Fields: GEOID, TotalBSLs, ServedBSLsFiber, UnderservedBSLsFiber, UnservedBSLsFiber, UniqueProvidersFiber.

Outputs:
- fcc_fiber_coverage.geojson  (repo root, build input)
- outputs/refresh/fcc_fiber_coverage_<date>.geojson  (archive)

Renamed properties:
- bsl_count, fiber_served_bsls, fiber_underserved_bsls, fiber_unserved_bsls,
  fiber_provider_count, as_of_date="2025-06-30"

Usage: python scripts/refresh_fcc_fiber_coverage.py
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

from shapely.geometry import shape
from shapely.ops import unary_union
from shapely.prepared import prep

ROOT = Path(__file__).resolve().parent.parent
COMBINED_GJ = ROOT / 'combined_geoms.geojson'
OUT_REPO = ROOT / 'fcc_fiber_coverage.geojson'
OUT_ARCHIVE_DIR = ROOT / 'outputs' / 'refresh'

FS_URL = ('https://services8.arcgis.com/peDZJliSvYims39Q/arcgis/rest/services/'
          'FCC_Broadband_Data_Collection_December_2024_View/FeatureServer/5/query')

BBOX = '-105.998,28.972,-100.115,32.525'
PAGE_SIZE = 2000
MAX_TRIES = 3
TIMEOUT = 30
AS_OF_DATE = '2025-06-30'

COUNTIES_23 = {
    'Andrews', 'Brewster', 'Crane', 'Crockett', 'Culberson', 'Ector',
    'Glasscock', 'Hudspeth', 'Irion', 'Jeff Davis', 'Loving', 'Martin',
    'Midland', 'Pecos', 'Presidio', 'Reagan', 'Reeves', 'Schleicher',
    'Sutton', 'Terrell', 'Upton', 'Ward', 'Winkler',
}

PROP_RENAME = {
    'TotalBSLs': 'bsl_count',
    'ServedBSLsFiber': 'fiber_served_bsls',
    'UnderservedBSLsFiber': 'fiber_underserved_bsls',
    'UnservedBSLsFiber': 'fiber_unserved_bsls',
    'UniqueProvidersFiber': 'fiber_provider_count',
}


def fetch_page(offset):
    """Fetch one page of hex features. Returns GeoJSON dict."""
    params = {
        'where': 'TotalBSLs > 0',
        'geometryType': 'esriGeometryEnvelope',
        'geometry': BBOX,
        'inSR': '4326',
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': 'GEOID,TotalBSLs,ServedBSLsFiber,UnderservedBSLsFiber,UnservedBSLsFiber,UniqueProvidersFiber',
        'outSR': '4326',
        'resultOffset': str(offset),
        'resultRecordCount': str(PAGE_SIZE),
        'f': 'geojson',
    }
    qs = urllib.parse.urlencode(params)
    url = f'{FS_URL}?{qs}'
    last_err = None
    for attempt in range(MAX_TRIES):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'LRP-TX-GIS/1.0'})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.loads(r.read())
        except Exception as e:
            last_err = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f'fetch_page offset={offset} failed after {MAX_TRIES} tries: {last_err}')


def load_county_union():
    """Build prepared union geometry of the 23-county set from combined_geoms."""
    if not COMBINED_GJ.exists():
        sys.exit(f'ERROR: {COMBINED_GJ} not found')
    with open(COMBINED_GJ, 'r', encoding='utf-8') as f:
        gj = json.load(f)
    matched = []
    seen = set()
    for feat in gj.get('features', []):
        p = feat.get('properties') or {}
        if p.get('layer_id') != 'counties':
            continue
        nm = (p.get('NAME') or p.get('name') or '').replace(' County', '').strip()
        if nm in COUNTIES_23 and nm not in seen:
            try:
                matched.append(shape(feat['geometry']))
                seen.add(nm)
            except Exception:
                continue
    missing = COUNTIES_23 - seen
    if missing:
        sys.exit(f'ERROR: missing counties in combined_geoms: {sorted(missing)}')
    print(f'County union built from {len(matched)} polygons')
    return prep(unary_union(matched))


def main():
    print('Loading 23-county union from combined_geoms.geojson...')
    union_prep = load_county_union()

    print(f'Paginating FCC BDC layer 5 (PAGE_SIZE={PAGE_SIZE})...')
    raw_features = []
    offset = 0
    while True:
        page = fetch_page(offset)
        feats = page.get('features') or []
        n = len(feats)
        print(f'  offset={offset:>5} got={n}')
        raw_features.extend(feats)
        if n < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    print(f'Total raw hex features in bbox: {len(raw_features)}')

    print('Spatial-clipping to 23-county union...')
    out_features = []
    skipped = 0
    for feat in raw_features:
        try:
            geom = shape(feat['geometry'])
        except Exception:
            skipped += 1
            continue
        if not union_prep.intersects(geom):
            skipped += 1
            continue
        src_props = feat.get('properties') or {}
        new_props = {}
        for src_key, dst_key in PROP_RENAME.items():
            v = src_props.get(src_key)
            new_props[dst_key] = v if v is not None else 0
        new_props['as_of_date'] = AS_OF_DATE
        out_features.append({
            'type': 'Feature',
            'geometry': feat['geometry'],
            'properties': new_props,
        })

    print(f'In-scope features: {len(out_features)} (skipped {skipped})')

    out_gj = {'type': 'FeatureCollection', 'features': out_features}
    OUT_REPO.write_text(json.dumps(out_gj))
    print(f'Wrote {OUT_REPO} ({OUT_REPO.stat().st_size:,} bytes)')

    OUT_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archive = OUT_ARCHIVE_DIR / f'fcc_fiber_coverage_{date.today().isoformat()}.geojson'
    archive.write_text(json.dumps(out_gj))
    print(f'Archived {archive}')


if __name__ == '__main__':
    main()
