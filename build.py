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

from build_sprite import build_sprite_sheet

ROOT = Path(__file__).parent
SPRITE_SRC = Path(__file__).parent / 'sprite'
TEMPLATE_FILE = ROOT / 'build_template.html'
TMP = Path('/tmp/gis_build')
SPLIT_DIR = TMP / 'split'
DIST = Path('/mnt/user-data/outputs/dist')
PROJECT = Path('/mnt/project')

COMBINED_CSV = 'combined_points.csv'
COMBINED_GJ = 'combined_geoms.geojson'

NUMERIC_KEYS = {'mw', 'capacity', 'capacity_mw', 'cap_kw', 'depth_ft',
                'year', 'plant_code', 'osm_id', 'acres'}

# Filter UI: cap distinct values for a categorical (or text) filter. Above this,
# the field is auto-demoted to plain text (substring match) so the UI stays
# usable. Raised from 100 → 2000 for UI POLISH v2: text fields now render as
# searchable multi-select dropdowns, so we want values populated whenever
# feasible (plant names, operators, projects).
CATEGORICAL_CAP = 2000

# Tax-abatement annotation (Chat 85). Target layers whose rows receive
# `abatement_*` properties when their name/entity/operator/project fuzzy-matches
# a tax_abatements applicant in the same county. Single pass, no iterative
# refinement. Status values `zone_creation` / `relationship_signal` are excluded
# from the join — they are not true abatement applicants.
ABATEMENT_TARGET_LAYERS = frozenset({
    'eia860_plants', 'ercot_queue', 'solar', 'wind', 'eia860_battery',
})

# Corporate-suffix pattern for applicant-name normalization.
import re as _re
_CORP_SUFFIX = _re.compile(
    r'\b(l\.?l\.?c\.?|inc\.?|lp|ltd|corp|corporation|company|co\.?|l\.?p\.?)\b',
    _re.IGNORECASE,
)
_NONWORD = _re.compile(r'[^a-z0-9]+')


def _normalize_applicant(s):
    """Lowercase, drop corporate suffixes, drop punctuation, collapse whitespace."""
    if not s:
        return ''
    s = str(s).lower()
    s = _CORP_SUFFIX.sub(' ', s)
    s = _NONWORD.sub(' ', s)
    return ' '.join(s.split())


def _name_fuzzy_match(applicant_norm, candidate_strs):
    """Token-set match: applicant tokens vs each candidate's normalized tokens.
    Strict subset-match rule — one side's non-empty token set must be fully
    contained in the other's. This catches legal-entity matches (e.g.
    `pecos power plant` == `pecos power plant`) but rejects generic-token
    coincidences (`ii`+`bess` overlap between unrelated projects).
    The earlier `≥2 token overlap` fallback was removed Chat 85 after producing
    3 false positives (Elk Ridge Solar, Longfellow BESS II, Sherbino II BESS SLF).
    """
    if not applicant_norm:
        return False
    atoks = set(applicant_norm.split())
    if not atoks:
        return False
    for c in candidate_strs:
        ctoks = set(_normalize_applicant(c).split())
        if not ctoks:
            continue
        if atoks <= ctoks or ctoks <= atoks:
            return True
    return False


def build_abatement_index(csv_path):
    """Scan tax_abatements rows → list of (county_lower, applicant_norm, meta).
    Skips zone_creation and relationship_signal rows (not applicants)."""
    idx = []
    if not csv_path.exists():
        return idx
    with open(csv_path, newline='', encoding='utf-8') as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            if row.get('layer_id') != 'tax_abatements':
                continue
            county = (row.get('county') or '').strip()
            applicant = (row.get('operator') or row.get('name') or '').strip()
            if not county or not applicant:
                continue
            fs_raw = row.get('funnel_stage') or ''
            status = fs_raw.split('|', 1)[0] if fs_raw else ''
            if status in ('zone_creation', 'relationship_signal'):
                continue
            idx.append((
                county.lower(),
                _normalize_applicant(applicant),
                {
                    'abatement_applicant': applicant,
                    'abatement_meeting_date': row.get('commissioned') or '',
                    'abatement_status': status,
                    'abatement_project_type': row.get('technology') or '',
                    'abatement_reinvestment_zone': row.get('project') or '',
                    'abatement_flags': fs_raw,
                    'abatement_agenda_url': row.get('poi') or '',
                },
            ))
    return idx


def _annotate_facility_with_abatement(lid, props, abate_index):
    """If lid is a target facility layer AND props match an abatement entry by
    (county, applicant-fuzzy-name), merge abatement_* fields into props. First
    match wins; no iterative refinement. Returns props."""
    if lid not in ABATEMENT_TARGET_LAYERS or not abate_index:
        return props
    county_l = str(props.get('county') or '').strip().lower()
    if not county_l:
        return props
    candidates = []
    for k in ('name', 'entity', 'operator', 'project'):
        v = props.get(k)
        if v:
            candidates.append(v)
    if not candidates:
        return props
    for abate_county, abate_applicant_norm, abate_meta in abate_index:
        if abate_county != county_l:
            continue
        if _name_fuzzy_match(abate_applicant_norm, candidates):
            for k, v in abate_meta.items():
                if v:
                    props[k] = v
            return props
    return props


def fnum(v):
    try:
        if v is None or v == '':
            return None
        x = float(v)
        return x if x == x else None
    except (TypeError, ValueError):
        return None


def resolve_source(file_rel):
    """Return absolute path in /mnt/project/ (flat), subfolder fallback,
    or repo ROOT (GitHub-as-canonical-source fallback for files not synced
    into project knowledge — the canonical source is the cloned repo)."""
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
    if alt and alt.exists():
        return alt
    repo_path = ROOT / file_rel
    return repo_path if repo_path.exists() else None


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

def split_combined_csv(csv_path, out_dir, abate_index=None):
    """Single pass through combined_points.csv → per-layer NDGeoJSON files
    in out_dir. Returns {layer_id: (n_total, n_written)}.

    If `abate_index` is provided, facility rows in ABATEMENT_TARGET_LAYERS
    are annotated with abatement_* properties on match. tax_abatements rows
    get a derived `status` property (first token of funnel_stage)."""
    stats = {}  # layer_id -> [total, written]
    handles = {}  # layer_id -> open file handle
    annotated = 0  # count of facility rows annotated
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
                # Derive `status` for tax_abatements rows (funnel_stage first token)
                if lid == 'tax_abatements':
                    fs = props.get('funnel_stage')
                    if fs:
                        props['status'] = str(fs).split('|', 1)[0]
                # Annotate facility rows with matched abatement fields
                if abate_index and lid in ABATEMENT_TARGET_LAYERS:
                    before = 'abatement_applicant' in props
                    _annotate_facility_with_abatement(lid, props, abate_index)
                    if not before and 'abatement_applicant' in props:
                        annotated += 1
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
    if abate_index:
        print(f'  abatement annotations applied: {annotated}')
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
                # Range-chunked fetch with retry. Full-file GETs intermittently
                # return 503 ('DNS cache overflow') from the container egress proxy
                # for large files; Range requests go through a different code path
                # on Netlify edge and succeed reliably once the file is cached.
                import urllib.request, urllib.error
                CHUNK = 8 * 1024 * 1024  # 8 MB
                MAX_TRIES = 5
                # Probe size via HEAD with retry
                total = None
                for attempt in range(MAX_TRIES):
                    try:
                        req = urllib.request.Request(prod_url, method='HEAD',
                                                     headers={'User-Agent': 'Mozilla/5.0 (lrp-build)'})
                        with urllib.request.urlopen(req, timeout=30) as r:
                            total = int(r.headers.get('Content-Length', '0'))
                        if total:
                            break
                    except (urllib.error.HTTPError, urllib.error.URLError, OSError):
                        pass
                    time.sleep(2 ** attempt)
                if not total:
                    raise RuntimeError('HEAD probe failed')
                # Chunked Range fetch
                with open(pm, 'wb') as out:
                    start = 0
                    while start < total:
                        end = min(start + CHUNK - 1, total - 1)
                        last_err = None
                        got = False
                        for attempt in range(MAX_TRIES):
                            try:
                                req = urllib.request.Request(
                                    prod_url,
                                    headers={'User-Agent': 'Mozilla/5.0 (lrp-build)',
                                             'Range': f'bytes={start}-{end}'})
                                with urllib.request.urlopen(req, timeout=60) as resp:
                                    if resp.status not in (200, 206):
                                        raise RuntimeError(f'HTTP {resp.status}')
                                    out.write(resp.read())
                                got = True
                                break
                            except Exception as ex:
                                last_err = ex
                                time.sleep(2 ** attempt)
                        if not got:
                            raise RuntimeError(f'range {start}-{end}: {last_err}')
                        start = end + 1
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
            elif s.get('type') == 'text':
                # UI POLISH v2: text fields auto-populate as searchable
                # multi-select dropdowns when distinct count fits under cap.
                # Collect values same as categorical; fall back to plain text
                # input only when distinct > CATEGORICAL_CAP.
                distinct[f] = set()
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
            elif typ == 'text' and f in distinct:
                # UI POLISH v2: promote to categorical (multi-select dropdown)
                # when distinct values fit under cap; else keep as plain text.
                vals = distinct[f]
                if len(vals) == 0:
                    continue
                if len(vals) <= CATEGORICAL_CAP:
                    entry['type'] = 'categorical'
                    entry['values'] = sorted(vals)
                # else: keep as text, no values (template shows plain input)
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
            'sidebar_omit': L.get('sidebar_omit', False),
            'popup': L.get('popup', []),
            'popup_labels': L.get('popup_labels', {}),
            'description': L.get('description', ''),
            'min_zoom': L.get('min_zoom', 0),
            'radius': L.get('radius', 3),
            'fill_opacity': L.get('fill_opacity', 0.25),
            'line_width': L.get('line_width', 2),
            'color_steps': L.get('color_steps'),
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
    # §6 #15: write to temp path + atomic rename. If out_path == combined_path,
    # opening out_path in 'w' before the source read would truncate it to zero.
    tmp_path = str(out_path) + '.tmp'
    with open(tmp_path, 'w', newline='', encoding='utf-8') as fout:
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
    os.replace(tmp_path, out_path)
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
    # §6 #15: symmetric guard. merge_geojson currently happens to be safe
    # (full-load before write), but the rule mandates temp+rename for any
    # read-modify-write helper to prevent regression.
    tmp_path = str(out_path) + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as fout:
        json.dump(out, fout, separators=(',', ':'))
    os.replace(tmp_path, out_path)
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

    # Regenerate sprite into repo-root sprite/ (committed) and mirror to DIST
    # so Netlify serves /sprite/sprite* alongside tiles.
    n_icons = build_sprite_sheet(SPRITE_SRC)
    dist_sprite = DIST / 'sprite'
    if dist_sprite.exists():
        shutil.rmtree(dist_sprite)
    shutil.copytree(SPRITE_SRC, dist_sprite)
    print(f'Sprite: {n_icons} icons @ 1x + 2x → {SPRITE_SRC}/ + {dist_sprite}/')

    with open(ROOT / 'layers.yaml') as f:
        cfg = yaml.safe_load(f)

    # One-pass split of combined files (if present)
    split_stats = {}
    cc = ROOT / COMBINED_CSV
    cg = ROOT / COMBINED_GJ
    # Pre-scan tax_abatements rows for fuzzy-join annotation step.
    abate_index = build_abatement_index(cc) if cc.exists() else []
    if abate_index:
        print(f'Abatement index: {len(abate_index)} applicants for fuzzy-join')
    if cc.exists():
        print(f'Splitting {COMBINED_CSV} ...')
        s = split_combined_csv(cc, SPLIT_DIR, abate_index=abate_index)
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
