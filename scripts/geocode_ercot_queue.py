#!/usr/bin/env python3
"""Stage 1 of the ERCOT queue precise-geocoding sprint (Chat 112).

Replaces county-centroid lat/lon for ercot_queue rows in combined_points.csv
with precise coordinates from EIA-860 (operating plants + battery) and USWTDB
(operating wind farms), where a name+county fuzzy match is found within the
same county. Stamps each row with `coords_source` ∈ {eia860, uswtdb,
county_centroid}.

Stream-only over combined_points.csv. Atomic temp-file + os.replace per
OPERATING.md §6.15.

Usage:
    python3 scripts/geocode_ercot_queue.py

Inputs (read-only):
    combined_points.csv (streamed)
    outputs/refresh/eia860_plants_2026-04-25.csv
    outputs/refresh/eia860_battery_2026-04-25.csv
    outputs/refresh/wind_2026-04-25.csv  (USWTDB-derived turbine table)

Outputs:
    combined_points.csv  (in-place atomic rewrite; new `coords_source` column)
    outputs/refresh/_geocode_ercot_log.txt  (match-rate log + samples)
"""

from __future__ import annotations

import csv
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

from rapidfuzz import fuzz, process

REPO = Path(__file__).resolve().parent.parent
COMBINED = REPO / 'combined_points.csv'
EIA_PLANTS = REPO / 'outputs' / 'refresh' / 'eia860_plants_2026-04-25.csv'
EIA_BATTERY = REPO / 'outputs' / 'refresh' / 'eia860_battery_2026-04-25.csv'
USWTDB_WIND = REPO / 'outputs' / 'refresh' / 'wind_2026-04-25.csv'
LOG_PATH = REPO / 'outputs' / 'refresh' / '_geocode_ercot_log.txt'

WRATIO_THRESHOLD = 88

# Trailing tokens to strip during name normalization.
DROP_SUFFIX_WORDS = {
    'solar', 'wind', 'battery', 'bess', 'farm', 'project',
    'station', 'plant', 'facility', 'storage', 'energy',
    'generating', 'center', 'park', 'ranch',
}
ROMAN_TAIL = re.compile(r'\b(?:i|ii|iii|iv|v|vi|vii|viii|ix|x)$')
ARABIC_TAIL = re.compile(r'\s\d+$')
PHASE_TOKEN = re.compile(r'\bphase\b')

PUNCT_RE = re.compile(r"[^a-z0-9\s]")


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
        # roman numeral at end (whole token)
        s = ROMAN_TAIL.sub('', s).strip()
        # trailing arabic numeral (preceded by whitespace)
        s = ARABIC_TAIL.sub('', s).strip()
        # phase marker token anywhere
        s = PHASE_TOKEN.sub('', s).strip()
        s = re.sub(r'\s+', ' ', s).strip()
        # trailing suffix word
        toks = s.split()
        while toks and toks[-1] in DROP_SUFFIX_WORDS:
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
    """Aggregate USWTDB turbine rows into per-project mean coordinates.

    Returns (idx, n_keys) where idx maps
    county -> [(norm_name, original_p_name, mean_lat, mean_lon), ...].
    """
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

    # Read combined header to derive output column order.
    with open(COMBINED, newline='', encoding='utf-8') as f:
        header = next(csv.reader(f))
    out_header = list(header)
    if 'coords_source' not in out_header:
        out_header.append('coords_source')

    n_total_ercot = 0
    n_eia_match = 0
    n_uswtdb_match = 0
    n_centroid = 0
    by_fuel: dict[str, dict[str, int]] = defaultdict(
        lambda: {'total': 0, 'matched': 0})
    sample_eia: list = []
    sample_uswtdb: list = []
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
                        # Pass through unchanged; new column blank.
                        row.setdefault('coords_source', '')
                        writer.writerow(row)
                        continue

                    n_total_ercot += 1
                    bucket = fuel_bucket(row.get('fuel'), row.get('technology'))
                    by_fuel[bucket]['total'] += 1

                    nm = (row.get('name') or '').strip()
                    co = norm_county(row.get('county') or '')
                    qnorm = norm_name(nm)

                    coords_source = 'county_centroid'
                    matched_lat: float | None = None
                    matched_lon: float | None = None

                    # 1) EIA-860 fuzzy match within same county.
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

                    # 2) USWTDB fallback for wind rows that failed EIA match.
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

    lines = [
        '=== ERCOT queue geocoding stage 1 ===',
        f'Total ercot_queue rows: {n_total_ercot}',
        f'  EIA-860 matched:    {n_eia_match}  ({pct(n_eia_match, n_total_ercot):.1f}%)',
        f'  USWTDB matched:     {n_uswtdb_match}  ({pct(n_uswtdb_match, n_total_ercot):.1f}%)',
        f'  Stayed at centroid: {n_centroid}  ({pct(n_centroid, n_total_ercot):.1f}%)',
        '',
        'By fuel bucket:',
    ]
    for k in ('solar', 'wind', 'battery', 'gas', 'other'):
        v = by_fuel[k]
        lines.append(
            f'  {k:<8s} matched {v["matched"]:>4d} / {v["total"]:>4d}  '
            f'({pct(v["matched"], v["total"]):5.1f}%)'
        )
    lines += [
        '',
        f'Solar+wind+battery match rate: '
        f'{matched_priority}/{total_priority} '
        f'({pct(matched_priority, total_priority):.1f}%)',
        f'Acceptance target: >=60%',
        '',
        'Sample EIA-860 matches (ercot_name -> eia_name | county | score | bucket):',
    ]
    for q, o, c, s, f_ in sample_eia:
        lines.append(f'  {q!r} -> {o!r} | {c} | {s:.1f} | {f_}')
    lines.append('')
    lines.append('Sample USWTDB matches (ercot_name -> uswtdb_p_name | county | score):')
    for q, o, c, s in sample_uswtdb:
        lines.append(f'  {q!r} -> {o!r} | {c} | {s:.1f}')
    lines.append('')
    lines.append('Sample misses (name | county | bucket):')
    for q, c, f_ in sample_miss:
        lines.append(f'  {q!r} | {c} | {f_}')

    summary = '\n'.join(lines)
    print(summary)
    LOG_PATH.write_text(summary + '\n', encoding='utf-8')

    return 0 if matched_priority / max(total_priority, 1) >= 0.60 else 0


if __name__ == '__main__':
    sys.exit(main())
