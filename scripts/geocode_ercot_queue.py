#!/usr/bin/env python3
"""ERCOT queue precise-geocoding pipeline (Chats 112 + 113).

Replaces county-centroid lat/lon for ercot_queue rows in combined_points.csv
with precise coordinates from cascading sources, stamping each row with a
provenance label in the new `coords_source` column. Stages run in order; later
stages only operate on rows still at `coords_source = county_centroid`.

Stage 1 (Chat 112)
  eia860          EIA-860 operating-plant + battery name+county fuzzy match
  uswtdb          USWTDB wind-farm name+county fuzzy match (wind rows only)

Stage 2 (Chat 113) — POI-proximity geocoding via the queue row's declared POI
substation. WIP_OPEN named TPIT explicitly but set a 60% match-rate target the
141-row TPIT layer alone cannot meet. Per OPERATING.md §7 ambiguity rule, the
plausible interpretation is "use available substation POI sources", of which
the OSM-derived `substations` layer (1,637 rows) is the broader companion.
Both stamp distinct provenance.
  tpit_poi        TPIT planned-upgrade substation match (same-county fuzzy
                  WRatio >= 88). TPIT carries no county column; counties are
                  derived per row via TIGER 2024 point-in-polygon.
  substation_poi  Same matching kernel against the OSM `substations` layer.
                  Counties also derived via TIGER point-in-polygon.
  dc_anchors      Anchor-tenant alias match against ercot_queue
                  `entity`/`name`, constrained to the same county as the
                  dc_anchors entry. Snaps to anchor centroid.

Stream-only over combined_points.csv. Atomic temp-file + os.replace per
OPERATING.md §6.15.

Usage:
    python3 scripts/geocode_ercot_queue.py

Inputs (read-only):
    combined_points.csv (streamed; supplies ercot_queue + tpit_subs + substations)
    outputs/refresh/eia860_plants_2026-04-25.csv
    outputs/refresh/eia860_battery_2026-04-25.csv
    outputs/refresh/wind_2026-04-25.csv
    data/datacenters/dc_anchors.json
    outputs/refresh/tl_2024_us_county.zip  (auto-fetched if absent; gitignored)

Outputs:
    combined_points.csv  (in-place atomic rewrite; `coords_source` column)
    outputs/refresh/_geocode_ercot_log.txt  (append-mode run log)
"""

from __future__ import annotations

import csv
import io
import json
import os
import re
import sys
import time
import urllib.request
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from rapidfuzz import fuzz, process

import shapefile  # pyshp
from shapely.geometry import Point, shape
from shapely.strtree import STRtree

REPO = Path(__file__).resolve().parent.parent
COMBINED = REPO / 'combined_points.csv'
EIA_PLANTS = REPO / 'outputs' / 'refresh' / 'eia860_plants_2026-04-25.csv'
EIA_BATTERY = REPO / 'outputs' / 'refresh' / 'eia860_battery_2026-04-25.csv'
USWTDB_WIND = REPO / 'outputs' / 'refresh' / 'wind_2026-04-25.csv'
DC_ANCHORS_JSON = REPO / 'data' / 'datacenters' / 'dc_anchors.json'
TIGER_URL = (
    'https://www2.census.gov/geo/tiger/TIGER2024/COUNTY/tl_2024_us_county.zip'
)
TIGER_ZIP = REPO / 'outputs' / 'refresh' / 'tl_2024_us_county.zip'
LOG_PATH = REPO / 'outputs' / 'refresh' / '_geocode_ercot_log.txt'

WRATIO_THRESHOLD = 88

# Trailing tokens to strip during generic project-name normalization.
DROP_SUFFIX_WORDS = {
    'solar', 'wind', 'battery', 'bess', 'farm', 'project',
    'station', 'plant', 'facility', 'storage', 'energy',
    'generating', 'center', 'park', 'ranch',
}
# Additional tail tokens to strip when normalizing substation / POI names.
SUBSTATION_DROP_TAIL = {
    'substation', 'subsation', 'sub', 'switch', 'switchyard', 'switchgear',
    'tap', 'line', 'interchange', 'sw', 'ss', 'county',
}
ROMAN_TAIL = re.compile(r'\b(?:i|ii|iii|iv|v|vi|vii|viii|ix|x)$')
ARABIC_TAIL = re.compile(r'\s\d+$')
PHASE_TOKEN = re.compile(r'\bphase\b')
PUNCT_RE = re.compile(r"[^a-z0-9\s]")
# Voltage tokens: "138kv", "345kv", "138 kv", lone "kv".
VOLTAGE_NUM_KV_RE = re.compile(r'\b\d+\s*kv\b')
LONE_KV_RE = re.compile(r'\bkv\b')


def norm_name(s: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace, drop trailing
    suffix tokens (solar/wind/farm/etc., phase markers, roman/arabic numerals).
    """
    if not s:
        return ''
    s = s.lower()
    s = PUNCT_RE.sub(' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    while True:
        before = s
        s = ROMAN_TAIL.sub('', s).strip()
        s = ARABIC_TAIL.sub('', s).strip()
        s = PHASE_TOKEN.sub('', s).strip()
        s = re.sub(r'\s+', ' ', s).strip()
        toks = s.split()
        while toks and toks[-1] in DROP_SUFFIX_WORDS:
            toks.pop()
        s = ' '.join(toks)
        if s == before:
            break
    return s


def norm_substation_name(s: str) -> str:
    """Normalize a substation or queue-POI name. Same base treatment as
    `norm_name` plus: strip voltage tokens (e.g. '138kV', '345kV', bare 'kv')
    and strip substation-specific tail tokens (substation/sub/switch/tap/etc.).
    """
    if not s:
        return ''
    s = s.lower()
    s = PUNCT_RE.sub(' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    s = VOLTAGE_NUM_KV_RE.sub(' ', s)
    s = LONE_KV_RE.sub(' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    while True:
        before = s
        s = ROMAN_TAIL.sub('', s).strip()
        s = ARABIC_TAIL.sub('', s).strip()
        s = PHASE_TOKEN.sub('', s).strip()
        s = re.sub(r'\s+', ' ', s).strip()
        toks = s.split()
        while toks and (
            toks[-1] in DROP_SUFFIX_WORDS or toks[-1] in SUBSTATION_DROP_TAIL
        ):
            toks.pop()
        s = ' '.join(toks)
        if s == before:
            break
    return s


def norm_county(s: str) -> str:
    """Uppercase, strip ' COUNTY' suffix, strip whitespace."""
    if not s:
        return ''
    s = s.upper().strip()
    if s.endswith(' COUNTY'):
        s = s[:-len(' COUNTY')].strip()
    return s


def fnum(v):
    if v is None or v == '':
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Stage 1: EIA-860 + USWTDB indexes
# ---------------------------------------------------------------------------

def build_eia_index() -> tuple[dict, int, int]:
    """Index EIA-860 plants + battery records.

    Returns (idx, n_plants, n_battery) where idx maps
    county -> [(norm_name, original_name, lat, lon), ...].
    """
    idx: dict[str, list] = defaultdict(list)
    n_plants = 0
    n_battery = 0
    sources = [(EIA_PLANTS, 'plants'), (EIA_BATTERY, 'battery')]
    for path, label in sources:
        if not path.exists():
            print(f'  warning: missing {path}', file=sys.stderr)
            continue
        with open(path, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                lat = fnum(row.get('lat'))
                lon = fnum(row.get('lon'))
                nm = (row.get('name') or '').strip()
                co = norm_county(row.get('county') or '')
                if not nm or not co or lat is None or lon is None:
                    continue
                norm = norm_name(nm)
                if not norm:
                    continue
                idx[co].append((norm, nm, lat, lon))
                if label == 'plants':
                    n_plants += 1
                else:
                    n_battery += 1
    return idx, n_plants, n_battery


def build_uswtdb_index() -> tuple[dict, int]:
    """Aggregate USWTDB turbine rows into per-project mean coordinates."""
    if not USWTDB_WIND.exists():
        print(f'  warning: missing {USWTDB_WIND}', file=sys.stderr)
        return defaultdict(list), 0
    agg: dict[tuple[str, str], dict] = {}
    with open(USWTDB_WIND, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            lat = fnum(row.get('lat'))
            lon = fnum(row.get('lon'))
            p = (row.get('project') or '').strip()
            co = norm_county(row.get('county') or '')
            if not p or not co or lat is None or lon is None:
                continue
            key = (p, co)
            slot = agg.setdefault(
                key, {'lat_sum': 0.0, 'lon_sum': 0.0, 'n': 0})
            slot['lat_sum'] += lat
            slot['lon_sum'] += lon
            slot['n'] += 1
    idx: dict[str, list] = defaultdict(list)
    for (p, co), v in agg.items():
        n = v['n']
        if n == 0:
            continue
        norm = norm_name(p)
        if not norm:
            continue
        idx[co].append((norm, p, v['lat_sum'] / n, v['lon_sum'] / n))
    return idx, len(agg)


# ---------------------------------------------------------------------------
# Stage 2 helpers: TIGER county derivation + per-layer substation indexing
# ---------------------------------------------------------------------------

def fetch_with_retry(
    url: str, dest: Path, attempts: int = 5, sleep: int = 10
) -> None:
    """Download `url` to `dest` with retry. No-op if dest already >=100 KB."""
    if dest.exists() and dest.stat().st_size >= 100_000:
        return
    last_err: Exception | None = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(
                url, headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=120) as r, \
                    open(dest, 'wb') as f:
                while True:
                    chunk = r.read(64 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
            return
        except Exception as e:
            last_err = e
            if i == attempts - 1:
                raise
            print(
                f'  fetch attempt {i+1} failed: {e}; retry in {sleep}s',
                file=sys.stderr,
            )
            time.sleep(sleep)
    raise RuntimeError(f'fetch failed: {last_err}')


def build_tx_county_polys() -> tuple[STRtree, list, list]:
    """Fetch TIGER 2024 county polygons; return (tree, polys, names) for TX.

    polys[i] is a shapely polygon for Texas county i. names[i] is the uppercase
    county name (no ' COUNTY' suffix). tree is an STRtree over polys for fast
    point-in-polygon candidate lookup.
    """
    fetch_with_retry(TIGER_URL, TIGER_ZIP)
    with zipfile.ZipFile(TIGER_ZIP) as zf:
        members = zf.namelist()
        shp_name = next(n for n in members if n.endswith('.shp'))
        base = shp_name[:-4]
        shp_buf = io.BytesIO(zf.read(base + '.shp'))
        dbf_buf = io.BytesIO(zf.read(base + '.dbf'))
        shx_buf = io.BytesIO(zf.read(base + '.shx'))
    polys: list = []
    names: list[str] = []
    with shapefile.Reader(shp=shp_buf, dbf=dbf_buf, shx=shx_buf) as r:
        fields = [f[0] for f in r.fields[1:]]
        i_state = fields.index('STATEFP')
        i_name = fields.index('NAME')
        for sr in r.iterShapeRecords():
            if sr.record[i_state] != '48':
                continue
            geom = shape(sr.shape.__geo_interface__)
            if geom.is_empty or not geom.is_valid:
                geom = geom.buffer(0)
            polys.append(geom)
            names.append(str(sr.record[i_name]).upper())
    tree = STRtree(polys)
    return tree, polys, names


def derive_county(
    lat: float, lon: float, tree: STRtree, polys: list, names: list[str]
) -> str:
    """Return uppercase county name (no ' COUNTY' suffix) for a (lat, lon)
    point, or empty string if the point falls outside all TX county polygons.
    """
    pt = Point(lon, lat)
    cand = tree.query(pt)
    for i in cand:
        if polys[i].contains(pt):
            return names[i]
    return ''


def build_substation_index_from_layer(
    layer_id: str,
    tree: STRtree,
    polys: list,
    county_names: list[str],
) -> tuple[dict, int, int, int]:
    """Stream `combined_points.csv` for rows matching `layer_id`, derive each
    row's county via TIGER point-in-polygon, and index by county.

    Returns (idx, n_seen, n_indexed, n_no_county) where idx maps
    county -> [(norm_substation_name, original_name, lat, lon), ...].
    Rows with no name, no coords, or outside all TX county polygons are dropped.
    """
    idx: dict[str, list] = defaultdict(list)
    n_seen = 0
    n_indexed = 0
    n_no_county = 0
    with open(COMBINED, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row.get('layer_id') != layer_id:
                continue
            n_seen += 1
            lat = fnum(row.get('lat'))
            lon = fnum(row.get('lon'))
            nm = (row.get('name') or '').strip()
            if lat is None or lon is None or not nm:
                continue
            co = derive_county(lat, lon, tree, polys, county_names)
            if not co:
                n_no_county += 1
                continue
            norm = norm_substation_name(nm)
            if not norm:
                continue
            idx[co].append((norm, nm, lat, lon))
            n_indexed += 1
    return idx, n_seen, n_indexed, n_no_county


# Curated anchor-tenant aliases per dc_anchors entry. Whole-word case-insensitive
# substring match against ercot_queue `entity` + `name`. Generic terms
# ('Oracle', 'OpenAI', bare 'meta') are deliberately excluded — they would
# false-match unrelated queue rows. Same-county filter (in matching) further
# constrains snaps to the anchor's own county.
DC_ANCHOR_ALIASES: dict[str, list[str]] = {
    'Project Horizon': ['coreweave', 'poolside'],
    'Stargate Abilene (Project Ludicrous, Lancium Clean Campus)': ['lancium'],
    'Microsoft–Crusoe Abilene Campus (adjacent to Stargate)': [
        'crusoe', 'microsoft',
    ],
    'Project Matador (Advanced Energy and Intelligence Campus)': [
        'fermi america',
    ],
    'GW Ranch': ['pacifico'],
    'Stargate Frontier Campus': ['vantage', 'voltagrid'],
    'Stargate Milam County (SoftBank/SB Energy)': ['sb energy', 'softbank'],
    'Meta Temple Data Center': ['meta platforms', 'polmer'],
}


def build_dc_anchors_index() -> tuple[dict, int]:
    """Build a county-keyed dc_anchors index.

    Returns (idx, n_indexed) where idx maps
    county -> [(compiled_alias_re, lat, lon, anchor_name), ...].
    """
    if not DC_ANCHORS_JSON.exists():
        print(f'  warning: missing {DC_ANCHORS_JSON}', file=sys.stderr)
        return defaultdict(list), 0
    with open(DC_ANCHORS_JSON, encoding='utf-8') as f:
        j = json.load(f)
    idx: dict[str, list] = defaultdict(list)
    n_indexed = 0
    for entry in j.get('entries', []):
        nm = (entry.get('name') or '').strip()
        co = norm_county(entry.get('county') or '')
        lat = fnum(entry.get('lat'))
        lon = fnum(entry.get('lon'))
        if not nm or not co or lat is None or lon is None:
            continue
        aliases = DC_ANCHOR_ALIASES.get(nm)
        if not aliases:
            continue
        pattern = (
            r'(?i)\b(?:'
            + '|'.join(re.escape(a) for a in aliases)
            + r')\b'
        )
        idx[co].append((re.compile(pattern), lat, lon, nm))
        n_indexed += 1
    return idx, n_indexed


# ---------------------------------------------------------------------------
# Shared matchers
# ---------------------------------------------------------------------------

def best_match(query_norm: str, candidates: list):
    """Return (lat, lon, original, score) or None if best WRatio < threshold."""
    if not candidates or not query_norm:
        return None
    pool = [c[0] for c in candidates]
    res = process.extractOne(query_norm, pool, scorer=fuzz.WRatio)
    if res is None:
        return None
    _, score, idx = res
    if score < WRATIO_THRESHOLD:
        return None
    _, original, lat, lon = candidates[idx]
    return lat, lon, original, score


def fuel_bucket(fuel: str, tech: str) -> str:
    fuel = (fuel or '').strip().upper()
    tech = (tech or '').strip().upper()
    if fuel == 'SOL':
        return 'solar'
    if fuel == 'WIN':
        return 'wind'
    if fuel == 'OTH' and tech == 'BA':
        return 'battery'
    if fuel == 'GAS':
        return 'gas'
    return 'other'


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main() -> int:
    print('Loading EIA-860 index...', file=sys.stderr)
    eia_idx, n_plants, n_battery = build_eia_index()
    eia_total = sum(len(v) for v in eia_idx.values())
    print(
        f'  EIA-860: {n_plants} plant rows + {n_battery} battery rows '
        f'-> {eia_total} indexed across {len(eia_idx)} counties',
        file=sys.stderr,
    )

    print('Loading USWTDB index...', file=sys.stderr)
    uswtdb_idx, n_uswtdb_keys = build_uswtdb_index()
    uswtdb_total = sum(len(v) for v in uswtdb_idx.values())
    print(
        f'  USWTDB: {n_uswtdb_keys} (project, county) groups '
        f'-> {uswtdb_total} indexed across {len(uswtdb_idx)} counties',
        file=sys.stderr,
    )

    print('Loading TIGER 2024 TX county polygons...', file=sys.stderr)
    tree, polys, county_names = build_tx_county_polys()
    print(f'  {len(polys)} TX county polygons loaded', file=sys.stderr)

    print('Building TPIT substation index...', file=sys.stderr)
    tpit_idx, tpit_seen, tpit_indexed, tpit_no_co = (
        build_substation_index_from_layer(
            'tpit_subs', tree, polys, county_names
        )
    )
    print(
        f'  TPIT: {tpit_seen} rows seen, {tpit_indexed} indexed, '
        f'{tpit_no_co} no-county; {len(tpit_idx)} counties covered',
        file=sys.stderr,
    )

    print('Building OSM substations index...', file=sys.stderr)
    osm_idx, osm_seen, osm_indexed, osm_no_co = (
        build_substation_index_from_layer(
            'substations', tree, polys, county_names
        )
    )
    print(
        f'  OSM substations: {osm_seen} rows seen, {osm_indexed} indexed, '
        f'{osm_no_co} no-county; {len(osm_idx)} counties covered',
        file=sys.stderr,
    )

    print('Loading dc_anchors index...', file=sys.stderr)
    dc_idx, n_dc_indexed = build_dc_anchors_index()
    print(
        f'  dc_anchors: {n_dc_indexed} entries indexed '
        f'across {len(dc_idx)} counties',
        file=sys.stderr,
    )

    # Read combined header to derive output column order.
    with open(COMBINED, newline='', encoding='utf-8') as f:
        header = next(csv.reader(f))
    out_header = list(header)
    if 'coords_source' not in out_header:
        out_header.append('coords_source')

    n_total_ercot = 0
    n_eia_match = 0
    n_uswtdb_match = 0
    n_tpit_match = 0
    n_osm_match = 0
    n_dc_match = 0
    n_centroid = 0
    by_fuel: dict[str, dict[str, int]] = defaultdict(
        lambda: {'total': 0, 'matched': 0})
    sample_eia: list = []
    sample_uswtdb: list = []
    sample_tpit: list = []
    sample_osm: list = []
    sample_dc: list = []
    sample_miss: list = []

    tmp_path = COMBINED.with_suffix(COMBINED.suffix + '.tmp')
    try:
        with open(tmp_path, 'w', newline='', encoding='utf-8') as fout:
            writer = csv.DictWriter(
                fout, fieldnames=out_header,
                extrasaction='ignore', lineterminator='\n',
            )
            writer.writeheader()
            with open(COMBINED, newline='', encoding='utf-8') as fin:
                for row in csv.DictReader(fin):
                    lid = row.get('layer_id') or ''
                    if lid != 'ercot_queue':
                        # Pass through unchanged; ensure column exists.
                        row.setdefault('coords_source', '')
                        writer.writerow(row)
                        continue

                    n_total_ercot += 1
                    bucket = fuel_bucket(
                        row.get('fuel'), row.get('technology')
                    )
                    by_fuel[bucket]['total'] += 1

                    nm = (row.get('name') or '').strip()
                    co = norm_county(row.get('county') or '')
                    qnorm = norm_name(nm)
                    poi_field = (row.get('poi') or '').strip()
                    poi_norm = norm_substation_name(poi_field)

                    coords_source = 'county_centroid'
                    matched_lat: float | None = None
                    matched_lon: float | None = None

                    # --- Stage 1.a: EIA-860 fuzzy match within same county.
                    if qnorm and co and co in eia_idx:
                        m = best_match(qnorm, eia_idx[co])
                        if m is not None:
                            matched_lat, matched_lon, orig, score = m
                            coords_source = 'eia860'
                            n_eia_match += 1
                            by_fuel[bucket]['matched'] += 1
                            if len(sample_eia) < 6:
                                sample_eia.append(
                                    (nm, orig, co, score, bucket))

                    # --- Stage 1.b: USWTDB fallback for wind rows missed above.
                    if (matched_lat is None and bucket == 'wind'
                            and qnorm and co and co in uswtdb_idx):
                        m = best_match(qnorm, uswtdb_idx[co])
                        if m is not None:
                            matched_lat, matched_lon, orig, score = m
                            coords_source = 'uswtdb'
                            n_uswtdb_match += 1
                            by_fuel[bucket]['matched'] += 1
                            if len(sample_uswtdb) < 6:
                                sample_uswtdb.append((nm, orig, co, score))

                    # --- Stage 2.a: TPIT POI proximity (same county).
                    if (matched_lat is None and poi_norm
                            and co and co in tpit_idx):
                        m = best_match(poi_norm, tpit_idx[co])
                        if m is not None:
                            matched_lat, matched_lon, orig, score = m
                            coords_source = 'tpit_poi'
                            n_tpit_match += 1
                            by_fuel[bucket]['matched'] += 1
                            if len(sample_tpit) < 6:
                                sample_tpit.append(
                                    (poi_field, orig, co, score, bucket))

                    # --- Stage 2.b: OSM substations POI proximity (same county).
                    if (matched_lat is None and poi_norm
                            and co and co in osm_idx):
                        m = best_match(poi_norm, osm_idx[co])
                        if m is not None:
                            matched_lat, matched_lon, orig, score = m
                            coords_source = 'substation_poi'
                            n_osm_match += 1
                            by_fuel[bucket]['matched'] += 1
                            if len(sample_osm) < 6:
                                sample_osm.append(
                                    (poi_field, orig, co, score, bucket))

                    # --- Stage 2.c: dc_anchors exact-alias match (same county).
                    if matched_lat is None and co and co in dc_idx:
                        haystack = (
                            (row.get('entity') or '') + ' '
                            + (row.get('name') or '')
                        )
                        for pat, alat, alon, aname in dc_idx[co]:
                            if pat.search(haystack):
                                matched_lat = alat
                                matched_lon = alon
                                coords_source = 'dc_anchors'
                                n_dc_match += 1
                                by_fuel[bucket]['matched'] += 1
                                if len(sample_dc) < 6:
                                    sample_dc.append(
                                        (nm, row.get('entity', ''),
                                         aname, co, bucket))
                                break

                    if matched_lat is not None and matched_lon is not None:
                        row['lat'] = f'{matched_lat:.6f}'
                        row['lon'] = f'{matched_lon:.6f}'
                    else:
                        n_centroid += 1
                        if len(sample_miss) < 6:
                            sample_miss.append((nm, co, bucket))

                    row['coords_source'] = coords_source
                    writer.writerow(row)
        os.replace(tmp_path, COMBINED)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise

    def pct(a: int, b: int) -> float:
        return (100.0 * a / b) if b else 0.0

    matched_priority = (
        by_fuel['solar']['matched']
        + by_fuel['wind']['matched']
        + by_fuel['battery']['matched']
    )
    total_priority = (
        by_fuel['solar']['total']
        + by_fuel['wind']['total']
        + by_fuel['battery']['total']
    )

    ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    n_matched_total = (
        n_eia_match + n_uswtdb_match
        + n_tpit_match + n_osm_match + n_dc_match
    )

    lines = [
        '',
        '=== ERCOT queue geocoding pipeline (Stage 1 + Stage 2) ===',
        f'run_at: {ts}',
        f'Total ercot_queue rows: {n_total_ercot}',
        f'  Stage 1 EIA-860 matched:        {n_eia_match}  '
        f'({pct(n_eia_match, n_total_ercot):.1f}%)',
        f'  Stage 1 USWTDB matched:         {n_uswtdb_match}  '
        f'({pct(n_uswtdb_match, n_total_ercot):.1f}%)',
        f'  Stage 2 TPIT POI matched:       {n_tpit_match}  '
        f'({pct(n_tpit_match, n_total_ercot):.1f}%)',
        f'  Stage 2 OSM-substation matched: {n_osm_match}  '
        f'({pct(n_osm_match, n_total_ercot):.1f}%)',
        f'  Stage 2 dc_anchors match:       {n_dc_match}  '
        f'({pct(n_dc_match, n_total_ercot):.1f}%)',
        f'  Total non-centroid:             {n_matched_total}  '
        f'({pct(n_matched_total, n_total_ercot):.1f}%)',
        f'  Stayed at centroid:             {n_centroid}  '
        f'({pct(n_centroid, n_total_ercot):.1f}%)',
        '',
        'By fuel bucket (matched / total):',
    ]
    for k in ('solar', 'wind', 'battery', 'gas', 'other'):
        v = by_fuel[k]
        lines.append(
            f'  {k:<8s} {v["matched"]:>4d} / {v["total"]:>4d}  '
            f'({pct(v["matched"], v["total"]):5.1f}%)'
        )
    lines += [
        '',
        f'Solar+wind+battery match rate: '
        f'{matched_priority}/{total_priority} '
        f'({pct(matched_priority, total_priority):.1f}%)',
        'Acceptance target: >=60% (solar+wind+battery non-centroid)',
        '',
        'Sample EIA-860 matches '
        '(ercot_name -> eia_name | county | score | bucket):',
    ]
    for q, o, c, s, b in sample_eia:
        lines.append(f'  {q!r} -> {o!r} | {c} | {s:.1f} | {b}')
    lines.append('')
    lines.append(
        'Sample USWTDB matches '
        '(ercot_name -> uswtdb_p_name | county | score):'
    )
    for q, o, c, s in sample_uswtdb:
        lines.append(f'  {q!r} -> {o!r} | {c} | {s:.1f}')
    lines.append('')
    lines.append(
        'Sample TPIT POI matches '
        '(ercot_poi -> tpit_name | county | score | bucket):'
    )
    for q, o, c, s, b in sample_tpit:
        lines.append(f'  {q!r} -> {o!r} | {c} | {s:.1f} | {b}')
    lines.append('')
    lines.append(
        'Sample OSM-substation matches '
        '(ercot_poi -> osm_name | county | score | bucket):'
    )
    for q, o, c, s, b in sample_osm:
        lines.append(f'  {q!r} -> {o!r} | {c} | {s:.1f} | {b}')
    lines.append('')
    lines.append(
        'Sample dc_anchors matches '
        '(ercot_name | entity -> anchor | county | bucket):'
    )
    for nm, ent, aname, co, b in sample_dc:
        lines.append(f'  {nm!r} | {ent!r} -> {aname!r} | {co} | {b}')
    lines.append('')
    lines.append('Sample misses (name | county | bucket):')
    for q, c, b in sample_miss:
        lines.append(f'  {q!r} | {c} | {b}')
    lines.append('')

    summary = '\n'.join(lines)
    print(summary)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(summary + '\n')

    return 0


if __name__ == '__main__':
    sys.exit(main())
