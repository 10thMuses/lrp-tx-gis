# RRC W-1 drilling-permit code mapping (empirical)

Source: forensic byte-position analysis of `daf420.dat.MM-DD-YYYY` (RRC
"Drilling Permit EOM + Lat/Lon" monthly snapshots from the GoAnywhere
MFT endpoint). RRC has not published a record layout for the daf420 file
series; everything below was derived from the January 2018 snapshot's
1,474 master records (`0108`-prefixed 212-byte lines) plus 1,484 detail
records (`0208`-prefixed 510-byte lines).

## Record-key prefixes (first 4 bytes of every line)

| Prefix | Length (b) | Count / monthly file | Purpose                                                                       |
|--------|-----------:|---------------------:|-------------------------------------------------------------------------------|
| `0108` | 212        | ~1,474               | **Master record** — one per permit. Contains permit id, lease, operator, dates, district, profile, filing-purpose code. |
| `0208` | 510        | ~1,484               | **Detail record** — one per permit. Contains total_depth, survey, distances. |
| `0X..` | 50/52/72   | varies               | Sub-records (perforations, casings, supplementary metadata).                 |
| `08XX` | 87         | ~23K                 | Free-text remarks (4 lines per permit explaining SWR 3.13 compliance).       |
| `14`   | 26         | 1,484                | WGS84 lat/lon — primary location.                                            |
| `15`   | 26         | 1,484                | WGS84 lat/lon — duplicate (likely BHL vs SHL or NAD27 vs WGS84 datum).       |

A permit "block" begins with a `0108` line and ends at the next `0108`
line or end-of-file. Multiple sub-records belong to the same permit.

## Master record (212 bytes) field positions

| Bytes (0-indexed) | Field                    | Notes                                                             |
|------------------:|--------------------------|-------------------------------------------------------------------|
| 0–3               | record_key               | constant "0108"                                                   |
| 4–13              | permit_master_id (10c)   | last 3 digits = **county FIPS** (✓ verified on 6-county scope)    |
| 11–13             | county_fips (3c)         | slice within permit_master_id                                     |
| 14–45             | lease_name (32c, padded) | e.g., "KING, E. F.", "UNIVERSITY UE A"                            |
| 50–53             | well_no (4c, approx)     | uncertain; appears at this position but encoding varies           |
| 58–65             | submitted_date           | YYYYMMDD                                                          |
| 66–97             | operator_name (32c)      | full company name, space-padded                                   |
| 100               | status_flag              | uniformly "A" in EOM file → all rows are approved permits         |
| 112–113           | district                 | 2-digit RRC district (08, 8A, 7C, etc.)                           |
| 120–127           | approved_date            | YYYYMMDD                                                          |
| 155–169 (window)  | wellbore_profile         | substring "HL" → horizontal; absence → vertical (≤1% horizontal)  |
| 182               | filing_purpose code      | X (63%), E (18%), P (12%), 3 (6%) — see code mapping below        |

## Detail record (510 bytes) field positions

| Bytes (0-indexed) | Field         | Notes                                                                  |
|------------------:|---------------|------------------------------------------------------------------------|
| 0–3               | record_key    | constant "0208"                                                        |
| 4–13              | permit_id     | matches master id (join key)                                           |
| 14–45             | lease_name    | mirrors master                                                         |
| 322–331           | total_depth   | 10-digit zero-padded depth in **feet**                                 |
| 332–339           | sub_depth     | 7-digit related depth (plug-back / KOP) — not exposed on the map      |

## Filing-purpose codes at master byte 182

**Empirical distribution (Jan 2018 snapshot, n = 1,474):**

| Code | Count | Share | Tentative meaning (UNVERIFIED — RRC has not published a key)             |
|------|------:|------:|----------------------------------------------------------------------------|
| `X`  |   936 | 63.6% | Most likely **New Drill** / production well — the dominant category.      |
| `E`  |   259 | 17.6% | Possibly **Exploration** / wildcat — or another secondary purpose.        |
| `P`  |   178 | 12.1% | Unknown — possibly **Plug-back** or pre-existing infrastructure.          |
| `3`  |    95 |  6.4% | Numeric code; likely a special filing class.                              |
| ` `  |     6 |  0.4% | Blank — no code assigned.                                                 |

### Round 2 R2-2 implication

The Round-2 spec asks for "production-purpose only — exclude injection,
disposal, plugging, recompletion, re-entry, water, observation."

The EOM+LatLon file itself is **already filtered by RRC to drilling
permits** (filename prefix `daf420` is the W-1 drilling permit series).
Injection (Form W-14) and disposal permits are distributed through
separate file series (UIC database, `uic_manual_uia010_3116.pdf` layout),
so they do not appear in this file.

Within the drilling-permit population, the X/E/P/3 codes at byte 182
likely segment into purpose categories. Without official documentation
mapping these letters to canonical W-1 purpose names ("New Drill",
"Recompletion", "Re-entry", "Field Transfer", "Amend"), we expose the
raw code as `filing_purpose` in the popup and let the operator filter.
Defaulting to "X-only" approximates "new-drill / production-purpose"
but should be operator-validated before being used in a defensible
demonstration.

## Oil vs. gas determination

**No reliable single-byte indicator found** at any tested master-record
position. Texas RRC distinguishes oil and gas permits via lease-number
context (oil leases vs gas wells), not via a flag on the W-1 application.
Operators file a single permit and the well becomes oil or gas based on
the producing horizon, declared after drilling.

For map purposes (R2-5 color scheme), `oil_gas` is set to `"unknown"`
at the parser stage. Once filed wells are completed, the well's oil/gas
classification is recoverable from the **dbf900 wellbore database**
(WBCOMPL segment, byte 3: 'O' = oil key, blank → gas key). Future
enhancement: post-join `permits_permian6` to `wells_permian6` on
`(county_fips, lease_name, well_no)` to inherit oil/gas tagging from
completed wells.

## Coordinate encoding (`14` / `15` lines, 26 bytes)

Position 0–1: record key (`14` or `15`).
Position 2–13: longitude, 12-char zoned-decimal `[ -]DDD.DDDDDDD` —
  Texas longitudes always negative; either signed or absolute magnitude.
Position 14–15: two spaces (separator).
Position 16–25: latitude, 10-char `DD.DDDDDDD`.

The `14` and `15` lines appear to be the same point in different datum
encodings (likely NAD27 vs WGS84). The parser takes the first non-null
of each.

## Verified against
- 11 county FIPS codes in 11-county scope (R1) — all matched against
  Texas Census TIGER county codes.
- 6 county FIPS codes in 6-county rescope — all present in the file with
  reasonable cardinality (30–135 permits per month per county).
- 3 specific permits hand-decoded (REED 500 ft, KING E.F. 4,822 ft,
  UNIVERSITY UE A 4,982 ft horizontal) — all fields parsed correctly.
