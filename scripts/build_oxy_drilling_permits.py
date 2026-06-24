# -*- coding: utf-8 -*-
"""Build the OXY drilling-permits layer (RRC W-1) from EOM master+lat/lon files.

Streams the cached RRC "Drilling Permit EOM + Lat/Lon" snapshots
(data/rrc_raw/daf420.dat.*), keeps only permits whose operator name matches
OXY / Occidental, and emits one Point feature per permit (surface lat/lon from
the file's location record — every coordinate is operator-reported and public,
satisfying hard rule 3). De-duplicated by permit number across snapshots.

Operator scope (RRC P-5 entities, confirmed): OXY USA INC. (#630591),
OCCIDENTAL PERMIAN LTD (#617544), OXY USA WTP LP, OXY USA EOR LLC. The regex
\b(OXY|OCCIDENTAL)\b captures all OXY upstream filers; OxyChem/Oxy Vinyls do not
file drilling permits so no chemical-side false positives appear.

Dual record-format support (verified empirically on the cached snapshots):
  * 2018-2023 snapshots use master record id "0108"; location records are
    26-byte "14"/"15" lines.
  * 2024-2026 snapshots use master record id "0109"; location records grew to
    27/28-byte "14"/"15" lines. permit_no (4:14), county_fips (11:14),
    submit_date (58:66) and operator (66:98) sit at identical offsets in both;
    approve_date shifted 120->119. lat/lon are range-anchored regex-extracted
    from the location record, so the parse is robust to the 1-2 byte growth.

County names come from the sourced Census-TIGER county polygons in
combined_geoms.geojson (GEOID last 3 = county FIPS); a small Census-FIPS
reference covers Permian counties outside the map's AOI. Nothing is hand-placed.

Output (atomic write): data/oxy/oxy_drilling_permits.geojson
Run: python3 scripts/build_oxy_drilling_permits.py
"""
import os, re, json, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "rrc_raw")
OXYDIR = os.path.join(ROOT, "data", "oxy")

OXY_OP = re.compile(r"\b(OXY|OCCIDENTAL)\b", re.I)
DATE_RE = re.compile(rb"(20[12][0-9])(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])")
# Texas surface coords: lat 25.8-36.5, lon -106.7..-93.5. Range-anchored so the
# two fields can never be confused and stray digits can't false-match.
LAT_RE = re.compile(rb"(?<!\d)(2[5-9]|3[0-6])\.\d{6,7}")
LON_RE = re.compile(rb"-?(9[3-9]|10[0-6])\.\d{6,7}")

# Permian-region county FIPS outside the 46-county map AOI (US Census FIPS,
# public reference — used only when the TIGER derivation has no polygon).
FIPS_FALLBACK = {"501": "Yoakum", "263": "Kent", "305": "Lynn", "079": "Cochran",
                 "445": "Terry", "169": "Garza", "033": "Borden", "003": "Andrews"}


def texas_fips_names():
    out = dict(FIPS_FALLBACK)
    gj = json.load(open(os.path.join(ROOT, "combined_geoms.geojson"), encoding="utf-8"))
    for f in gj["features"]:
        p = f.get("properties") or {}
        if p.get("layer_id") != "counties":
            continue
        name = (p.get("NAME") or "").replace(" County", "").strip()
        geoid = str(p.get("GEOID") or "")
        fips3 = geoid[-3:] if len(geoid) >= 3 else ""
        if name and fips3.isdigit():
            out[fips3] = name           # TIGER (sourced) overrides fallback
    return out


def parse_date_field(line, *offsets):
    for o in offsets:
        s = line[o:o + 8]
        if DATE_RE.fullmatch(s):
            return f"{s[:4].decode()}-{s[4:6].decode()}-{s[6:8].decode()}"
    return ""


def parse_master(line):
    return {
        "permit_no": line[4:14].decode("ascii", "replace").strip(),
        "county_fips": line[11:14].decode("ascii", "replace"),
        "lease_name": line[14:46].decode("ascii", "replace").strip(),
        "well_no": line[50:54].decode("ascii", "replace").strip().lstrip("0"),
        "operator_name": line[66:98].decode("ascii", "replace").strip(),
        "district": line[112:114].decode("ascii", "replace").strip(),
        "submitted_date": parse_date_field(line, 58),
        "approved_date": parse_date_field(line, 120, 119),
    }


def parse_loc(line):
    lat_m = LAT_RE.search(line)
    lon_m = LON_RE.search(line)
    lat = float(lat_m.group(0)) if lat_m else None
    lon = -abs(float(lon_m.group(0))) if lon_m else None
    if lat is not None and not (25.8 <= lat <= 36.6):
        lat = None
    if lon is not None and not (-106.7 <= lon <= -93.4):
        lon = None
    return lat, lon


def iter_oxy(path):
    cur = lat = lon = None

    def emit():
        if cur is None or not OXY_OP.search(cur.get("operator_name", "")):
            return None
        if lat is None or lon is None:
            return None
        return (cur, lat, lon)

    with open(path, "rb") as f:
        for raw in f:
            line = raw.rstrip(b"\r\n")
            if len(line) < 4:
                continue
            k = line[:4]
            if k in (b"0108", b"0109"):
                got = emit()
                if got:
                    yield got
                cur = parse_master(line)
                lat = lon = None
            elif line[:2] in (b"14", b"15") and 26 <= len(line) <= 28:
                la, lo = parse_loc(line)
                if lat is None and la is not None:
                    lat = la
                if lon is None and lo is not None:
                    lon = lo
        got = emit()
        if got:
            yield got


def main():
    fips = texas_fips_names()
    snaps = sorted(glob.glob(os.path.join(RAW, "daf420.dat.*")))
    if not snaps:
        raise SystemExit("ERROR: no daf420.dat.* in data/rrc_raw — run "
                         "`python3 scripts/fetch_rrc.py permits` first")

    seen = {}
    raw_total = 0
    for snap in snaps:
        tag = snap.rsplit(".", 1)[-1]
        n = 0
        for m, lat, lon in iter_oxy(snap):
            raw_total += 1
            n += 1
            pno = m["permit_no"].strip()
            cfips = m.get("county_fips", "")
            pyear = (m["approved_date"] or m["submitted_date"] or "")[:4]
            props = {
                "permit_no": pno, "operator": m["operator_name"],
                "lease": m["lease_name"], "well_no": m["well_no"],
                "county": fips.get(cfips, ""), "county_fips": cfips,
                "district": m["district"], "approved_date": m["approved_date"],
                "submitted_date": m["submitted_date"], "permit_year": pyear,
                "source": "RRC Drilling Permit Master+Lat/Lon (daf420 EOM); operator-reported surface coords",
                "accuracy": "precise (RRC operator-reported)",
            }
            feat = {"type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
                    "properties": props}
            seen[pno or f"_{tag}_{n}"] = feat        # latest snapshot wins on dup
        print(f"  {os.path.basename(snap):24s} OXY permits: {n}")

    feats = list(seen.values())
    years = sorted(y for y in (f["properties"]["permit_year"] for f in feats) if y)
    fc = {"type": "FeatureCollection",
          "metadata": {"layer": "oxy_drilling_permits", "feature_count": len(feats),
                       "coverage": (f"RRC approved drilling permits {years[0]}-{years[-1]}"
                                    if years else "RRC approved drilling permits"),
                       "note": "OXY/Occidental RRC W-1 drilling permits (daf420 EOM master+lat/lon); "
                               "operator-reported surface coordinates; de-duplicated by permit_no."},
          "features": feats}
    os.makedirs(OXYDIR, exist_ok=True)
    out = os.path.join(OXYDIR, "oxy_drilling_permits.geojson")
    tmp = out + ".tmp"
    json.dump(fc, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, out)

    ops, cnts, yrs = {}, {}, {}
    for f in feats:
        p = f["properties"]
        ops[p["operator"]] = ops.get(p["operator"], 0) + 1
        c = p["county"] or p["county_fips"]
        cnts[c] = cnts.get(c, 0) + 1
        y = (p["approved_date"] or p["submitted_date"] or "")[:4]
        yrs[y] = yrs.get(y, 0) + 1
    print(f"\noxy_drilling_permits  {len(feats)} unique permits ({raw_total} raw / {len(snaps)} snapshots)")
    print("  operators:", dict(sorted(ops.items(), key=lambda x: -x[1])))
    print("  counties :", dict(sorted(cnts.items(), key=lambda x: -x[1])))
    print("  by year  :", dict(sorted(yrs.items())))


if __name__ == "__main__":
    main()
