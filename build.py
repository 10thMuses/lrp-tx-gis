#!/usr/bin/env python3
"""Build pipeline for the Texas Energy GIS Map.

Reads /mnt/project/layers.yaml. Supports two data-file patterns:

  1. COMBINED FILES (default for most layers):
       - combined_points.csv   — union of all point CSVs; `layer_id` column tags each row
       - combined_geoms.geojson — all line/polygon features; `layer_id` property tags each feature
     On build start we one-pass split each combined file into per-layer NDGeoJSON files
     in TMP. Each layer then tippecanoes from its pre-split file.

  2. STANDALONE FILES (heavy layers like parcels_pecos):
       - layers.yaml entry has `file: geoms_<name>.geojson`; build reads it directly.

Never materializes source data contents in-process beyond the bytes needed to stream
into tippecanoe's stdin (or to write per-layer NDGeoJSON during the initial split).

SUBCOMMANDS:
  python3 build.py                    — full build (default)
  python3 build.py merge <layer_id> <refresh_file>
                                       — swap <layer_id> rows/features in the combined
                                         file with contents of <refresh_file>.
                                         Output → /mnt/user-data/outputs/combined_*.{csv,geojson}
"""

import csv
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
TEMPLATE_FILE = ROOT / 'build_template.html'
TMP = Path('/tmp/gis_build')
SPLIT_DIR = TMP / 'split'
DIST = Path('/mnt/user-data/outputs/dist')
PROJECT = Path('/mnt/project')

COMBINED_CSV = 'combined_points.csv'
COMBINED_GJ = 'combined_geoms.geojson'

NUMERIC_KEYS = {'mw', 'capacity', 'capacity_mw', 'cap_kw', 'depth_ft',
                'year', 'plant_code', 'osm_id', 'acres'}

# Filter UI: cap distinct values for a categorical filter. Above this, the
# field is auto-demoted to text (substring match) so the UI stays usable.
CATEGORICAL_CAP = 100


def fnum(v):
    try:
        if v is None or v == '':
            return None
        x = float(v)
        return x if x == x else None
    except (TypeError, ValueError):
        return None


def resolve_source(file_rel):
    """Return absolute path in /mnt/project/ (flat) or subfolder fallback."""
    flat = PROJECT / file_rel
    if flat.exists():
        return flat
    if file_rel.startswith('points_'):
        alt = PROJECT / 'points' / file_rel[len('points_'):]
    elif file_rel.startswith('geoms_'):
        alt = PROJECT / 'geoms' / file_rel[len('geoms_'):]
    elif file_rel.startswith('deal_'):
        alt = PROJECT / 'deal' / file_rel[len('deal_'):]
    else:
        alt = None
    return alt if (alt and alt.exists()) else None


def _coerce_row_props(row):
    """Strip layer_id/lat/lon, drop blanks, coerce numeric columns. Returns dict."""
    props = {}
    for k, v in row.items():
        if k in ('lat', 'lon', 'layer_id'):
            continue
        if v is None or v == '':
            continue
        if k in NUMERIC_KEYS:
            num = fnum(v)
            props[k] = num if num is not None else v
        else:
            props[k] = v
    return props


def _flatten_coords(coords):
    """Recursively strip Z to keep 2D."""
    if isinstance(coords, (list, tuple)) and coords and isinstance(coords[0], (int, float)):
        return list(coords[:2])
    return [_flatten_coords(c) for c in coords]


# ---------- COMBINED-FILE SPLITTER (one pass → per-layer NDGeoJSON) ----------

def split_combined_csv(csv_path, out_dir):
    """Single pass through combined_points.csv → per-layer NDGeoJSON files
    in out_dir. Returns {layer_id: (n_total, n_written)}."""
    stats = {}  # layer_id -> [total, written]
    handles = {}  # layer_id -> open file handle
    try:
        with open(csv_path, newline='', encoding='utf-8') as fin:
            reader = csv.DictReader(fin)
            for row in reader:
                lid = row.get('layer_id') or ''
                if not lid:
                    continue
                st = stats.setdefault(lid, [0, 0])
                st[0] += 1
                lat = fnum(row.get('lat'))
                lon = fnum(row.get('lon'))
                if lat is None or lon is None:
                    continue
                if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                    continue
                props = _coerce_row_props(row)
                feat = {
                    'type': 'Feature',
                    'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
                    'properties': props,
                }
                fh = handles.get(lid)
                if fh is None:
                    fh = open(out_dir / f'{lid}.ndjson', 'w', encoding='utf-8')
                    handles[lid] = fh
                fh.write(json.dumps(feat, separators=(',', ':')))
                fh.write('\n')
                st[1] += 1
    finally:
        for fh in handles.values():
            fh.close()
    return {k: tuple(v) for k, v in stats.items()}


def split_combined_geojson(gj_path, out_dir):
    """One pass through combined_geoms.geojson → per-layer NDGeoJSON files
    in out_dir. Returns {layer_id: (n_total, n_written)}."""
    stats = {}
    handles = {}
    try:
        with open(gj_path, 'r', encoding='utf-8') as f:
            d = json.load(f)
        feats = d.get('features') or []
        for feat in feats:
            props = feat.get('properties') or {}
            lid = props.get('layer_id')
            if not lid:
                continue
            st = stats.setdefault(lid, [0, 0])
            st[0] += 1
            geom = feat.get('geometry')
            if not geom:
                continue
            try:
                geom['coordinates'] = _flatten_coords(geom.get('coordinates', []))
            except Exception:
                continue
            # Strip layer_id from output properties (internal tagging only)
            out_props = {k: v for k, v in props.items() if k != 'layer_id'}
            out_feat = {
                'type': 'Feature',
                'geometry': geom,
                'properties': out_props,
            }
            fh = handles.get(lid)
            if fh is None:
                fh = open(out_dir / f'{lid}.ndjson', 'w', encoding='utf-8')
                handles[lid] = fh
            fh.write(json.dumps(out_feat, separators=(',', ':')))
            fh.write('\n')
            st[1] += 1
    finally:
        for fh in handles.values():
            fh.close()
    return {k: tuple(v) for k, v in stats.items()}


# ---------- STANDALONE FILE CONVERTERS (same shape as before) ----------

def csv_to_ndgeojson(csv_path, out_path):
    n_total = 0
    n_written = 0
    with open(csv_path, newline='', encoding='utf-8') as fin, \
         open(out_path, 'w', encoding='utf-8') as fout:
        reader = csv.DictReader(fin)
        for row in reader:
            n_total += 1
            lat = fnum(row.get('lat'))
            lon = fnum(row.get('lon'))
            if lat is None or lon is None:
                continue
            if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                continue
            props = _coerce_row_props(row)
            feat = {
                'type': 'Feature',
                'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
                'properties': props,
            }
            fout.write(json.dumps(feat, separators=(',', ':')))
            fout.write('\n')
            n_written += 1
    return n_total, n_written


def geojson_to_ndgeojson(gj_path, out_path):
    n = 0
    with open(gj_path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    feats = d.get('features') or []
    with open(out_path, 'w', encoding='utf-8') as fout:
        for feat in feats:
            geom = feat.get('geometry')
            if not geom:
                continue
            try:
                geom['coordinates'] = _flatten_coords(geom.get('coordinates', []))
            except Exception:
                continue
            # Strip layer_id if present (defensive; standalone files usually don't have it)
            props = feat.get('properties') or {}
            if 'layer_id' in props:
                props = {k: v for k, v in props.items() if k != 'layer_id'}
                feat = dict(feat)
                feat['properties'] = props
            fout.write(json.dumps(feat, separators=(',', ':')))
            fout.write('\n')
            n += 1
    return n, n


def run_tippecanoe(nd_path, pmtiles_path, layer_id, extra_args):
    cmd = [
        'tippecanoe',
        '-fo', str(pmtiles_path),
        '-l', layer_id,
        '--read-parallel',
    ] + list(extra_args) + [str(nd_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f'tippecanoe failed for {layer_id}: {proc.stderr[:400]}')
    return proc.stderr


# ---------- PER-LAYER BUILD ----------

def build_layer(layer, report, split_stats):
    lid = layer['id']
    file_rel = layer.get('file', '')
    t0 = time.time()
    pm = DIST / 'tiles' / f'{lid}.pmtiles'
    pm.parent.mkdir(parents=True, exist_ok=True)

    # Prebuilt PMTiles: 3-tier resolution → dist/tiles/<id>.pmtiles
    #   tier 1: /mnt/project/<id>.pmtiles            (project knowledge or in-session cp)
    #   tier 2: /mnt/user-data/uploads/<id>.pmtiles  (operator session upload)
    #   tier 3: https://lrp-tx-gis.netlify.app/tiles/<id>.pmtiles  (current prod, self-sustaining)
    if layer.get('prebuilt'):
        src_project = PROJECT / f'{lid}.pmtiles'
        src_uploads = Path('/mnt/user-data/uploads') / f'{lid}.pmtiles'
        prod_url = f'https://lrp-tx-gis.netlify.app/tiles/{lid}.pmtiles'
        tier_used = None
        try:
            if src_project.exists():
                shutil.copy(src_project, pm)
                tier_used = 'project'
            elif src_uploads.exists():
                shutil.copy(src_uploads, pm)
                tier_used = 'uploads'
            else:
                import urllib.request
                req = urllib.request.Request(prod_url, headers={'User-Agent': 'lrp-build/1.0'})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    if resp.status != 200:
                        raise RuntimeError(f'HTTP {resp.status}')
                    pm.write_bytes(resp.read())
                tier_used = 'prod-url'
            sz = pm.stat().st_size
            if sz < 1024:
                report.append((lid, 0, 0, 'ERROR', f'prebuilt too small: {sz}B via {tier_used}'))
                return None
            report.append((lid, 0, 0, f'OK {sz//1024}KB',
                          f'prebuilt[{tier_used}] {time.time()-t0:.1f}s'))
            return {'id': lid, 'bytes': sz, 'features': layer.get('feature_count', 0)}
        except Exception as e:
            report.append((lid, 0, 0, 'ERROR', f'prebuilt: {str(e)[:80]}'))
            return None

    # Combined-file layer: use pre-split ndjson
    if file_rel in (COMBINED_CSV, COMBINED_GJ):
        nd = SPLIT_DIR / f'{lid}.ndjson'
        if not nd.exists():
            report.append((lid, 0, 0, 'MISSING',
                          f'no rows for {lid} in {file_rel}'))
            return None
        stats = split_stats.get(lid, (0, 0))
        n_total, n_written = stats
        try:
            run_tippecanoe(nd, pm, lid, layer.get('tippecanoe', ['-zg']))
            sz = pm.stat().st_size
            report.append((lid, n_total, n_written,
                          f'OK {sz//1024}KB', f'{time.time()-t0:.1f}s'))
            return {'id': lid, 'bytes': sz, 'features': n_written}
        except Exception as e:
            report.append((lid, n_total, n_written, 'ERROR', str(e)[:80]))
            return None

    # Standalone file layer
    src = resolve_source(file_rel)
    if src is None:
        report.append((lid, 0, 0, 'MISSING', file_rel))
        return None
    nd = TMP / f'{lid}.ndjson'
    try:
        if src.suffix.lower() == '.csv':
            n_total, n_written = csv_to_ndgeojson(src, nd)
        else:
            n_total, n_written = geojson_to_ndgeojson(src, nd)
        if n_written == 0:
            report.append((lid, n_total, 0, 'EMPTY', src.name))
            return None
        run_tippecanoe(nd, pm, lid, layer.get('tippecanoe', ['-zg']))
        sz = pm.stat().st_size
        report.append((lid, n_total, n_written,
                      f'OK {sz//1024}KB', f'{time.time()-t0:.1f}s'))
        return {'id': lid, 'bytes': sz, 'features': n_written}
    except Exception as e:
        report.append((lid, 0, 0, 'ERROR', str(e)[:80]))
        return None
    finally:
        if nd.exists():
            try: nd.unlink()
            except Exception: pass


# ---------- HTML + NETLIFY ----------

def compute_filter_stats(layers_config, split_dir):
    """Second pass over split ndjson to compute per-layer filter stats for
    any layer declaring `filterable_fields`. Returns:
        {layer_id: {field_name: {type, label, min?, max?, values?}}}
    Categorical fields exceeding CATEGORICAL_CAP distinct values are
    demoted to type='text' (values omitted).
    """
    result = {}
    for L in layers_config['layers']:
        spec = L.get('filterable_fields') or []
        if not spec:
            continue
        lid = L['id']
        nd = split_dir / f'{lid}.ndjson'
        if not nd.exists():
            continue
        # Per-field accumulators
        numeric = {}   # field -> [min, max]
        distinct = {}  # field -> set of string values
        declared = {}  # field -> (type, label)
        for s in spec:
            f = s['field']
            declared[f] = (s.get('type', 'text'), s.get('label', f))
            if s.get('type') == 'numeric':
                numeric[f] = [float('inf'), float('-inf')]
            elif s.get('type') == 'categorical':
                distinct[f] = set()
            # text: nothing to accumulate
        # Stream
        with open(nd, 'r', encoding='utf-8') as fin:
            for line in fin:
                try:
                    feat = json.loads(line)
                except Exception:
                    continue
                props = feat.get('properties') or {}
                for f in numeric:
                    v = props.get(f)
                    if v is None or v == '':
                        continue
                    num = fnum(v) if not isinstance(v, (int, float)) else v
                    if num is None:
                        continue
                    if num < numeric[f][0]: numeric[f][0] = num
                    if num > numeric[f][1]: numeric[f][1] = num
                for f in distinct:
                    v = props.get(f)
                    if v is None or v == '':
                        continue
                    if len(distinct[f]) >= CATEGORICAL_CAP + 1:
                        continue  # already over cap, no point collecting more
                    distinct[f].add(str(v))
        # Assemble per-layer output
        out = {}
        for f, (typ, label) in declared.items():
            entry = {'field': f, 'type': typ, 'label': label}
            if typ == 'numeric' and f in numeric:
                mn, mx = numeric[f]
                if mn <= mx:
                    entry['min'] = round(mn, 4)
                    entry['max'] = round(mx, 4)
                else:
                    # No data — skip this field
                    continue
            elif typ == 'categorical' and f in distinct:
                vals = distinct[f]
                if len(vals) == 0:
                    continue
                if len(vals) > CATEGORICAL_CAP:
                    # Demote to text
                    entry['type'] = 'text'
                else:
                    entry['values'] = sorted(vals)
            # text: no extra
            out[f] = entry
        if out:
            result[lid] = out
    return result


def render_html(layers_config, layer_stats, filter_stats=None):
    filter_stats = filter_stats or {}
    stats_by_id = {s['id']: s for s in layer_stats if s}
    clean = []
    for L in layers_config['layers']:
        if L['id'] not in stats_by_id:
            continue
        # Resolve filterable_fields against computed stats (preserve yaml order)
        ff = []
        fstats = filter_stats.get(L['id'], {})
        for s in (L.get('filterable_fields') or []):
            entry = fstats.get(s['field'])
            if entry is not None:
                ff.append(entry)
        clean.append({
            'id': L['id'],
            'label': L['label'],
            'group': L['group'],
            'geom': L['geom'],
            'color': L['color'],
            'default_on': L.get('default_on', False),
            'popup': L.get('popup', []),
            'min_zoom': L.get('min_zoom', 0),
            'radius': L.get('radius', 3),
            'fill_opacity': L.get('fill_opacity', 0.25),
            'features': stats_by_id[L['id']]['features'],
            'filterable_fields': ff,
        })
    registry_json = json.dumps(clean, separators=(',', ':'))
    tpl = TEMPLATE_FILE.read_text()
    out = tpl.replace('/*__LAYERS__*/', registry_json)
    (DIST / 'index.html').write_text(out)


def write_netlify_config():
    (DIST / '_headers').write_text(
        "/tiles/*\n"
        "  Access-Control-Allow-Origin: *\n"
        "  Cache-Control: public, max-age=3600, must-revalidate\n"
        "  Content-Type: application/octet-stream\n"
        "\n"
        "/*.pmtiles\n"
        "  Access-Control-Allow-Origin: *\n"
        "  Content-Type: application/octet-stream\n"
    )
    (DIST / '_redirects').write_text("/*    /index.html   200\n")


# ---------- MERGE SUBCOMMAND ----------

def merge_csv(combined_path, refresh_path, layer_id, out_path):
    """Swap layer_id rows in combined_points.csv with contents of refresh CSV.
    - If refresh has a layer_id column, values are honored (must all == layer_id).
    - If refresh lacks layer_id, it's injected with the target layer_id.
    - Output header is the union of existing combined header + refresh header,
      preserving existing column order and appending new columns at the end.
    """
    # Read combined header
    with open(combined_path, newline='', encoding='utf-8') as f:
        combined_header = next(csv.reader(f))
    # Read refresh header
    with open(refresh_path, newline='', encoding='utf-8') as f:
        refresh_header = next(csv.reader(f))

    # Build merged header
    merged_header = list(combined_header)
    for c in refresh_header:
        if c not in merged_header:
            merged_header.append(c)
    if 'layer_id' not in merged_header:
        merged_header.insert(0, 'layer_id')

    kept = 0
    removed = 0
    added = 0
    with open(out_path, 'w', newline='', encoding='utf-8') as fout:
        writer = csv.DictWriter(fout, fieldnames=merged_header, extrasaction='ignore')
        writer.writeheader()
        # Pass 1: keep non-target rows from combined
        with open(combined_path, newline='', encoding='utf-8') as fin:
            reader = csv.DictReader(fin)
            for row in reader:
                if row.get('layer_id') == layer_id:
                    removed += 1
                    continue
                writer.writerow(row)
                kept += 1
        # Pass 2: append refresh rows with layer_id tag
        with open(refresh_path, newline='', encoding='utf-8') as fin:
            reader = csv.DictReader(fin)
            for row in reader:
                row['layer_id'] = layer_id
                writer.writerow(row)
                added += 1
    return {'kept': kept, 'removed': removed, 'added': added,
            'columns': len(merged_header)}


def merge_geojson(combined_path, refresh_path, layer_id, out_path):
    """Swap layer_id features in combined_geoms.geojson with features from refresh GeoJSON."""
    with open(combined_path, 'r', encoding='utf-8') as f:
        combined = json.load(f)
    combined_feats = combined.get('features') or []
    # Remove target layer features
    kept = 0
    removed = 0
    keep_list = []
    for ft in combined_feats:
        props = ft.get('properties') or {}
        if props.get('layer_id') == layer_id:
            removed += 1
            continue
        keep_list.append(ft)
        kept += 1

    # Load refresh, tag with layer_id
    with open(refresh_path, 'r', encoding='utf-8') as f:
        refresh = json.load(f)
    refresh_feats = refresh.get('features') or []
    added = 0
    for ft in refresh_feats:
        props = ft.get('properties') or {}
        props['layer_id'] = layer_id
        ft['properties'] = props
        keep_list.append(ft)
        added += 1

    out = {'type': 'FeatureCollection', 'features': keep_list}
    with open(out_path, 'w', encoding='utf-8') as fout:
        json.dump(out, fout, separators=(',', ':'))
    return {'kept': kept, 'removed': removed, 'added': added,
            'total_features': len(keep_list)}


def cmd_merge(layer_id, refresh_filepath):
    """Entry point: python build.py merge <layer_id> <refresh_file>"""
    refresh_path = Path(refresh_filepath)
    if not refresh_path.exists():
        print(f'ERROR: refresh file not found: {refresh_filepath}')
        sys.exit(2)

    # Find layer in yaml to determine which combined file to target
    with open(ROOT / 'layers.yaml') as f:
        cfg = yaml.safe_load(f)
    layer = next((L for L in cfg['layers'] if L['id'] == layer_id), None)
    if layer is None:
        print(f'ERROR: layer_id not in layers.yaml: {layer_id}')
        sys.exit(2)

    target_combined = layer.get('file', '')
    if target_combined not in (COMBINED_CSV, COMBINED_GJ):
        print(f'ERROR: layer {layer_id} is not combined-file resident '
              f'(file={target_combined}). Merge applies only to combined layers.')
        sys.exit(2)

    combined_src = PROJECT / target_combined
    if not combined_src.exists():
        print(f'ERROR: combined file missing from project: {combined_src}')
        sys.exit(2)

    out_dir = Path('/mnt/user-data/outputs')
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / target_combined

    print(f'Merging layer_id={layer_id}')
    print(f'  combined:  {combined_src}')
    print(f'  refresh:   {refresh_path}')
    print(f'  output:    {out_path}')

    if target_combined == COMBINED_CSV:
        r = merge_csv(combined_src, refresh_path, layer_id, out_path)
        print(f'\n  rows kept:    {r["kept"]:,}')
        print(f'  rows removed: {r["removed"]:,} (old {layer_id})')
        print(f'  rows added:   {r["added"]:,} (new {layer_id})')
        print(f'  columns:      {r["columns"]}')
    else:
        r = merge_geojson(combined_src, refresh_path, layer_id, out_path)
        print(f'\n  features kept:    {r["kept"]:,}')
        print(f'  features removed: {r["removed"]:,} (old {layer_id})')
        print(f'  features added:   {r["added"]:,} (new {layer_id})')
        print(f'  total out:        {r["total_features"]:,}')

    sz = out_path.stat().st_size
    print(f'\n  output size: {sz/1e6:.2f} MB')
    print(f'\nDrop {out_path.name} into /mnt/project/ to replace the existing combined file.')


# ---------- MAIN (build) ----------

def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    if SPLIT_DIR.exists():
        shutil.rmtree(SPLIT_DIR)
    SPLIT_DIR.mkdir(parents=True, exist_ok=True)

    with open(ROOT / 'layers.yaml') as f:
        cfg = yaml.safe_load(f)

    # One-pass split of combined files (if present)
    split_stats = {}
    cc = PROJECT / COMBINED_CSV
    cg = PROJECT / COMBINED_GJ
    if cc.exists():
        print(f'Splitting {COMBINED_CSV} ...')
        s = split_combined_csv(cc, SPLIT_DIR)
        split_stats.update(s)
        print(f'  {sum(v[1] for v in s.values()):,} features across {len(s)} layers')
    if cg.exists():
        print(f'Splitting {COMBINED_GJ} ...')
        s = split_combined_geojson(cg, SPLIT_DIR)
        split_stats.update(s)
        print(f'  {sum(v[1] for v in s.values()):,} features across {len(s)} layers')

    report = []
    stats = []
    for layer in cfg['layers']:
        s = build_layer(layer, report, split_stats)
        if s:
            stats.append(s)

    filter_stats = compute_filter_stats(cfg, SPLIT_DIR)
    render_html(cfg, stats, filter_stats)
    write_netlify_config()

    print('\nBUILD REPORT')
    print(f"{'layer':<20} {'total':>8} {'kept':>8}  status")
    print('-' * 60)
    total_bytes = 0
    for lid, ntot, nkept, status, extra in report:
        print(f'{lid:<20} {ntot:>8} {nkept:>8}  {status}  {extra}')
    for pm in sorted((DIST / 'tiles').glob('*.pmtiles')):
        total_bytes += pm.stat().st_size
    built = sum(1 for r in report if r[3].startswith('OK'))
    missing = sum(1 for r in report if r[3] == 'MISSING')
    errored = sum(1 for r in report if r[3] == 'ERROR')
    print(f'\nbuilt={built}  missing={missing}  errored={errored}  '
          f'tiles_total={total_bytes//1024} KB')
    print(f'out: {DIST}/index.html')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'merge':
        if len(sys.argv) < 4:
            print('Usage: python build.py merge <layer_id> <refresh_file>')
            sys.exit(2)
        cmd_merge(sys.argv[2], sys.argv[3])
    else:
        main()
