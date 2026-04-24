"""Transform abatement scraper hits into combined_points.csv rows + patch layers.yaml.

Per WIP_OPEN Chat 83 scope. Idempotent: skips append if tax_abatements rows
already present, skips yaml patch if tax_abatements id already declared.
"""
from __future__ import annotations

import csv
import io
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
HITS_CSV = ROOT / "data/abatements/abatement_hits_20260424_092810.csv"
POINTS_CSV = ROOT / "combined_points.csv"
LAYERS_YAML = ROOT / "layers.yaml"

# 23 county centroids from WIP_OPEN
CENTROIDS = {
    "Andrews": (-102.636000, 32.304500),
    "Brewster": (-103.084723, 29.816000),
    "Crane": (-102.540085, 31.490500),
    "Crockett": (-101.378010, 30.694000),
    "Culberson": (-104.488588, 31.552500),
    "Ector": (-102.543000, 31.876500),
    "Glasscock": (-101.522000, 31.868500),
    "Hudspeth": (-105.406975, 31.303000),
    "Irion": (-100.981238, 31.305500),
    "Jeff Davis": (-104.130042, 30.931000),
    "Loving": (-103.569579, 31.820500),
    "Martin": (-101.951510, 32.304500),
    "Midland": (-102.031250, 31.869000),
    "Pecos": (-102.666594, 30.727000),
    "Presidio": (-104.238482, 29.942500),
    "Reagan": (-101.524747, 31.366000),
    "Reeves": (-103.645106, 31.381500),
    "Schleicher": (-100.538514, 30.901500),
    "Sutton": (-100.538000, 30.500000),
    "Terrell": (-102.162869, 30.165000),
    "Upton": (-102.042750, 31.364000),
    "Ward": (-103.126510, 31.466000),
    "Winkler": (-103.063837, 31.830500),
}

# Points CSV schema (header row)
POINT_COLS = [
    "layer_id", "lat", "lon", "name", "plant_code", "county", "technology",
    "capacity", "sector", "inr", "fuel", "mw", "zone", "poi", "entity",
    "funnel_stage", "group", "under_construction", "commissioned",
    "capacity_mw", "operator", "voltage", "osm_id", "depth_ft", "use",
    "aquifer", "project", "manu", "model", "cap_kw", "year",
]

# §7 seed rows not captured by scrape (per WIP_OPEN Chat 83 scope)
SEED_ROWS = [
    {
        "county": "Pecos",
        "meeting_date": "2025-01-13",
        "applicant": "",
        "reinvestment_zone": "Longfellow Renewable Energy Reinvestment Zone",
        "project_type": "reinvestment_zone_creation",
        "agenda_url": "",
        "flags": "zone_creation",
        "capacity_mw": "",
        "note": "Longfellow RE RIZ established by resolution",
    },
    {
        "county": "Reeves",
        "meeting_date": "2025-06-13",
        "applicant": "Pecos Power Plant LLC",
        "reinvestment_zone": "Enterprise Zone §312.2011",
        "project_type": "natural_gas",
        "agenda_url": "",
        "flags": "abatement|gas|capex:150-200M",
        "capacity_mw": "226",
        "note": "226 MW natgas, $150-200M capex",
    },
    {
        "county": "Pecos",
        "meeting_date": "2025-11-10",
        "applicant": "Apex Clean Energy",
        "reinvestment_zone": "",
        "project_type": "donation",
        "agenda_url": "",
        "flags": "relationship_signal",
        "capacity_mw": "",
        "note": "Donation to Pecos County — relationship signal, not a filing",
    },
]


def clean_zone(z: str) -> str:
    if not z:
        return ""
    z = re.sub(r"^\s*located within the\s+", "", z, flags=re.I)
    z = re.sub(r"\s+Established on .*$", "", z, flags=re.I)
    return z.strip()


def project_type_override(applicant: str, raw_type: str, raw_text: str) -> str:
    """Matterhorn = gas turbines despite 'Solar' trademark."""
    blob = (applicant + " " + raw_text).lower()
    if "matterhorn" in blob and "solar titan" in blob:
        return "natural_gas"
    return raw_type


def load_hits() -> list[dict]:
    rows = []
    with open(HITS_CSV, encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            # Drop noise: generic zone-establishment rows with blank applicant
            # project_type=abatement_other. (Actual abatement rows retained.)
            if not r.get("applicant", "").strip():
                if r.get("project_type") == "abatement_other":
                    continue
                # Row with no applicant and no useful project_type — drop
                if not r.get("project_type"):
                    continue
            # Drop Matterhorn (no date, incomplete record for Chat 83 ship;
            # can be re-included Chat 85 with cleaner scrape)
            if "matterhorn" in r.get("applicant", "").lower() and not r.get("meeting_date"):
                continue
            rows.append(r)
    return rows


def to_point_row(county: str, meeting_date: str, applicant: str, zone: str,
                 project_type: str, agenda_url: str, flags: str,
                 capacity_mw: str, note: str = "") -> dict:
    lon, lat = CENTROIDS.get(county, (None, None))
    if lon is None:
        return None
    # name = applicant if present, else derive from zone or note
    name = applicant or zone or note or f"{county} abatement {meeting_date}"
    row = {c: "" for c in POINT_COLS}
    row["layer_id"] = "tax_abatements"
    row["lat"] = f"{lat:.6f}"
    row["lon"] = f"{lon:.6f}"
    row["name"] = name
    row["county"] = county
    row["technology"] = project_type
    row["operator"] = applicant
    row["commissioned"] = meeting_date
    row["project"] = clean_zone(zone)
    row["capacity_mw"] = capacity_mw
    row["poi"] = agenda_url  # agenda_url stored in poi (schema constraint)
    row["funnel_stage"] = flags
    row["group"] = "Permits"
    return row


def already_present() -> bool:
    """Idempotent guard: check if tax_abatements rows already in points CSV."""
    with open(POINTS_CSV, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            if line.startswith("tax_abatements,"):
                return True
            if i > 100_000:  # safety
                break
    # Tail check (in case append happened at end)
    with open(POINTS_CSV, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 50_000))
        tail = f.read().decode("utf-8", errors="ignore")
    return "tax_abatements," in tail


def append_rows(rows: list[dict]) -> int:
    # Append only — never read full file (per §9.1)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=POINT_COLS, lineterminator="\n")
    for r in rows:
        w.writerow(r)
    data = buf.getvalue()
    with open(POINTS_CSV, "a", encoding="utf-8") as f:
        f.write(data)
    return len(rows)


YAML_BLOCK = """- id: tax_abatements
  file: combined_points.csv
  geom: point
  group: Permits
  label: Tax Abatements
  color: '#dc2626'
  default_on: false
  radius: 4
  popup:
  - name
  - operator
  - county
  - commissioned
  - project
  - technology
  - capacity_mw
  - poi
  filterable_fields:
  - {field: county, type: categorical, label: County}
  - {field: technology, type: categorical, label: Project Type}
  - {field: commissioned, type: text, label: Meeting Date}
  tippecanoe:
  - -Z0
  - -z14
"""


def patch_yaml() -> bool:
    text = LAYERS_YAML.read_text()
    if "- id: tax_abatements" in text:
        return False
    # Ensure trailing newline then append block
    if not text.endswith("\n"):
        text += "\n"
    text += YAML_BLOCK
    LAYERS_YAML.write_text(text)
    return True


def main():
    if already_present():
        print("ABORT: tax_abatements rows already present in combined_points.csv")
        sys.exit(1)

    hits = load_hits()
    print(f"Loaded {len(hits)} filtered hits")

    rows = []
    for h in hits:
        pr = to_point_row(
            county=h["county"],
            meeting_date=h.get("meeting_date", ""),
            applicant=h.get("applicant", ""),
            zone=h.get("reinvestment_zone", ""),
            project_type=project_type_override(
                h.get("applicant", ""), h.get("project_type", ""), h.get("raw_text", "")
            ),
            agenda_url=h.get("agenda_url", ""),
            flags=h.get("flags", ""),
            capacity_mw="",
        )
        if pr:
            rows.append(pr)
    for s in SEED_ROWS:
        pr = to_point_row(
            county=s["county"],
            meeting_date=s["meeting_date"],
            applicant=s["applicant"],
            zone=s["reinvestment_zone"],
            project_type=s["project_type"],
            agenda_url=s["agenda_url"],
            flags=s["flags"],
            capacity_mw=s["capacity_mw"],
            note=s["note"],
        )
        if pr:
            rows.append(pr)

    n = append_rows(rows)
    print(f"Appended {n} tax_abatement rows to combined_points.csv")

    patched = patch_yaml()
    print(f"layers.yaml patched: {patched}")


if __name__ == "__main__":
    main()
