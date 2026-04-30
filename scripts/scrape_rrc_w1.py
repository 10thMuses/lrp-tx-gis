#!/usr/bin/env python3
"""
RRC W-1 Drilling Permit Application scraper.

Source: https://webapps.rrc.state.tx.us/DP/initializePublicQueryAction.do
        Public W-1 Search Results — JSP form-driven query, no auth required.
        Cookie-bound session preserves query state across pagination GETs.

Scope: 11 Permian-relevant counties, all years 1976-present (RRC drilling permit
       data starts 1976 per the agency's own statement).

Counties (district 08 unless noted):
    PECOS=371, REEVES=389, WARD=475, LOVING=301, WINKLER=495,
    CULBERSON=109 (district 7C), CRANE=103, UPTON=461, REAGAN=383,
    CROCKETT=105 (district 7C), TERRELL=443 (district 7C)

Strategy:
    1. POST query (county + year) to /DP/publicQuerySearchAction.do
    2. If response says "exceeds the maximum records allowed", fall back to
       monthly chunks for that year. Cap empirically lies between 569 and
       2,411 (Loving 2020 = 569 OK; Pecos 10y = 2,411 blocked).
    3. Otherwise, parse first 20 results, then GET
       /DP/changeQueryPageAction.do?pager.offset=N for N=20,40,... until
       a page returns fewer than 20 rows.

Output: outputs/refresh/rrc_w1_permits.csv (atomic write per §6.15).
        Checkpoint: outputs/refresh/rrc_w1_checkpoint.json — resume-capable.
        Each row carries county_code, year for downstream aggregation.

Listing-page columns (no lat/lon — coords on detail page only, deferred
to a follow-on chat per scope split):

    permit_no       ← Status # (e.g. 854220)
    api_no          ← API No (e.g. 301-34562)
    status          ← Current Queue (Approved | Withdrawn | Cancelled | ...)
    approved_date   ← Status Date "Approved MM/DD/YYYY"
    submitted_date  ← Status Date "Submitted MM/DD/YYYY"
    operator_name   ← Operator Name
    operator_no     ← Operator Number (in parens)
    lease_name      ← Lease Name
    well_no         ← Well #
    district        ← Dist.
    county_name     ← County
    county_code     ← (added) numeric county code 001..507
    wb_profile      ← Wellbore Profile (Horizontal | Vertical | ...)
    filing_purpose  ← Filing Purpose (New Drill | Recompletion | ...)
    is_amended      ← Amend (Yes | No)
    total_depth     ← Total Depth (ft)
    univ_doc_no     ← detail-page link's univDocNo param
    detail_url      ← /DP/drillDownQueryAction.do?...&univDocNo=...

Hard rules respected:
    §6.1 No source-data file read into context. CSV streamed via DictWriter.
    §6.2 No fetch during build. This is the refresh path.
    §6.5 One layer/county/year failure never aborts the run. Try/except per chunk.
    §6.15 Atomic in-place writes via temp + os.replace.
    §11   No `view` of large result HTML — direct regex parse, never load file via
          shell tools.

Throttle: 1.5s between HTTP requests (configurable via THROTTLE_SECS).
Retry: 3 attempts per request with 10s sleep on failure.
"""

import csv
import datetime
import json
import os
import re
import sys
import time
import urllib.parse
from html import unescape
from html.parser import HTMLParser

import requests

# ============================================================================
# Config
# ============================================================================

BASE = "https://webapps.rrc.state.tx.us/DP"
INIT_URL = f"{BASE}/initializePublicQueryAction.do"
PAGE_URL = f"{BASE}/changeQueryPageAction.do"
SORT_URL = f"{BASE}/changeQuerySortOrderAction.do"
# Sorting by API number stabilizes pagination — without it, the result set
# rebuilds on each request with an unstable sort, causing overlapping/missed
# rows during sequential walking. Empirically: 461/569 captured without sort,
# 569/569 with sort applied. (Discovered 2026-04-30.)
SORT_KEY = "sortApiNumber"

# (name, county_code, district)
TARGETS = [
    ("PECOS",     "371", "08"),
    ("REEVES",    "389", "08"),
    ("WARD",      "475", "08"),
    ("LOVING",    "301", "08"),
    ("WINKLER",   "495", "08"),
    ("CRANE",     "103", "08"),
    ("UPTON",     "461", "08"),
    ("REAGAN",    "383", "08"),
    ("CULBERSON", "109", "7C"),
    ("CROCKETT",  "105", "7C"),
    ("TERRELL",   "443", "7C"),
]

START_YEAR = 1976  # RRC drilling permit data origin
END_YEAR = 2026

THROTTLE_SECS = 1.5
RETRY_ATTEMPTS = 3
RETRY_SLEEP = 10
HTTP_TIMEOUT = 90

UA = "Mozilla/5.0 (compatible; lrp-tx-gis research scraper; contact andrea@landresourcepartners.com)"

OUT_CSV = "outputs/refresh/rrc_w1_permits.csv"
OUT_COUNTS = "outputs/refresh/rrc_w1_counts.csv"
CHECKPOINT = "outputs/refresh/rrc_w1_checkpoint.json"
COUNTS_CHECKPOINT = "outputs/refresh/rrc_w1_counts_checkpoint.json"

CSV_FIELDS = [
    "permit_no", "api_no", "status",
    "approved_date", "submitted_date",
    "operator_name", "operator_no",
    "lease_name", "well_no",
    "district", "county_name", "county_code",
    "wb_profile", "filing_purpose",
    "is_amended", "total_depth",
    "univ_doc_no", "detail_url",
    "year_chunk",  # the (county, year[, month]) chunk this row was fetched in
]

# ============================================================================
# HTTP / session
# ============================================================================

def make_session():
    """Fresh session — gets cookies + jsessionid-bound action URL."""
    s = requests.Session()
    s.headers["User-Agent"] = UA
    return s


def fetch_init_action_url(session):
    """Fetch the form page; return the jsessionid-bound POST action URL."""
    for attempt in range(RETRY_ATTEMPTS):
        try:
            r = session.get(INIT_URL, timeout=HTTP_TIMEOUT)
            if r.status_code == 200:
                m = re.search(r'action="(/DP/publicQuerySearchAction\.do[^"]*)"', r.text)
                if m:
                    return m.group(1)
            print(f"  init attempt {attempt+1}: HTTP {r.status_code}")
        except Exception as e:
            print(f"  init attempt {attempt+1} error: {e}")
        time.sleep(RETRY_SLEEP)
    raise RuntimeError("could not fetch init form")


# ============================================================================
# HTML row parser
# ============================================================================

# Each result row in the listing is a series of <td> cells inside a <tr>.
# Empirically: status_date, status_no, api_no, operator (name + number),
# lease_name (link → detail), well_no, district, county, wb_profile, filing,
# amend, total_depth, stacked_lateral_parent, current_queue.
#
# Strategy: extract all <tr> blocks containing a `drillDownQueryAction.do`
# link (those are real result rows). For each, pull cell text in order, then
# parse the structured sub-fields.

ROW_BLOCK_RE = re.compile(
    r"<tr[^>]*>(?P<body>(?:(?!<tr[^>]*>).)*?drillDownQueryAction\.do.*?)</tr>",
    re.DOTALL | re.IGNORECASE,
)
DETAIL_LINK_RE = re.compile(
    r'href="(/DP/drillDownQueryAction\.do\?[^"]+)"[^>]*>([^<]+)</a>',
    re.IGNORECASE,
)
UNIV_DOC_RE = re.compile(r"univDocNo=(\d+)", re.IGNORECASE)
APPROVED_RE = re.compile(r"Approved\s*(\d{2}/\d{2}/\d{4})")
SUBMITTED_RE = re.compile(r"Submitted\s*(\d{2}/\d{2}/\d{4})")
OPERATOR_RE = re.compile(r"^(.*?)\s*\((\d+)\)\s*$")
# Counts are formatted "1 - 20 of <strong>569</strong> results" with tags
# and &nbsp; interleaved. Match against tag-stripped + whitespace-normalized text.
COUNT_RE = re.compile(r"of\s+(\d[\d,]*)\s+results?", re.IGNORECASE)
EXCEEDS_RE = re.compile(r"exceeds the maximum records allowed", re.IGNORECASE)

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def cell_text(html_chunk):
    """Strip tags, unescape, collapse whitespace."""
    txt = TAG_RE.sub(" ", html_chunk)
    txt = unescape(txt)
    return WS_RE.sub(" ", txt).strip()


def parse_listing_page(html, county_name, county_code, year_chunk):
    """Yield row dicts from one listing page. Filters out the per-page
    'Click on lease name for detailed permit information' instructional row
    that matches the same `<tr>` structure but has no permit number."""
    rows = []
    for m in ROW_BLOCK_RE.finditer(html):
        body = m.group("body")
        # extract all td chunks
        tds = re.findall(r"<td[^>]*>(.*?)</td>", body, re.DOTALL | re.IGNORECASE)
        if not tds:
            continue

        # detail link → univ_doc_no, lease_name
        detail_url = ""
        univ_doc_no = ""
        lease_name = ""
        link_match = DETAIL_LINK_RE.search(body)
        if link_match:
            detail_url = link_match.group(1)
            lease_name = unescape(link_match.group(2)).strip()
            udn_match = UNIV_DOC_RE.search(detail_url)
            if udn_match:
                univ_doc_no = udn_match.group(1)

        # extract cell texts
        cells = [cell_text(td) for td in tds]

        def get(idx):
            return cells[idx] if idx < len(cells) else ""

        permit_no = get(1)
        # Skip the per-page instructional row (no real permit_no)
        if not permit_no.isdigit():
            continue

        status_date_cell = get(0)
        approved_match = APPROVED_RE.search(status_date_cell)
        submitted_match = SUBMITTED_RE.search(status_date_cell)
        approved_date = approved_match.group(1) if approved_match else ""
        submitted_date = submitted_match.group(1) if submitted_match else ""

        operator_cell = get(3)
        op_name = operator_cell
        op_no = ""
        op_match = OPERATOR_RE.match(operator_cell)
        if op_match:
            op_name = op_match.group(1).strip()
            op_no = op_match.group(2).strip()

        # detail_url is page-relative — make absolute
        if detail_url and detail_url.startswith("/"):
            detail_url_abs = "https://webapps.rrc.state.tx.us" + detail_url
        else:
            detail_url_abs = detail_url

        rows.append({
            "permit_no": permit_no,
            "api_no": get(2),
            "status": get(13),
            "approved_date": approved_date,
            "submitted_date": submitted_date,
            "operator_name": op_name,
            "operator_no": op_no,
            "lease_name": lease_name,
            "well_no": get(5),
            "district": get(6),
            "county_name": get(7) or county_name,
            "county_code": county_code,
            "wb_profile": get(8),
            "filing_purpose": get(9),
            "is_amended": get(10),
            "total_depth": get(11),
            "univ_doc_no": univ_doc_no,
            "detail_url": detail_url_abs,
            "year_chunk": year_chunk,
        })
    return rows


def parse_total_count(html):
    """Return total result count, or None if not found."""
    if EXCEEDS_RE.search(html):
        return "EXCEEDS"
    # Tag-strip + collapse whitespace before matching (count text is broken
    # across <strong> tags and &nbsp; entities in raw HTML).
    flat = WS_RE.sub(" ", unescape(TAG_RE.sub(" ", html)))
    m = COUNT_RE.search(flat)
    if m:
        return int(m.group(1).replace(",", ""))
    if "No Matches Found" in flat:
        return 0
    return None


# ============================================================================
# Query execution
# ============================================================================

def post_query(session, action_url, district, county_code, start_date, end_date):
    """POST one search query. Returns the response text."""
    payload = {
        "submit": "Submit",
        "districtNames": district,
        "countyNames": county_code,
        "approvedStart": start_date,
        "approvedEnd": end_date,
    }
    for attempt in range(RETRY_ATTEMPTS):
        try:
            r = session.post(
                "https://webapps.rrc.state.tx.us" + action_url,
                data=payload,
                timeout=HTTP_TIMEOUT,
            )
            if r.status_code == 200:
                return r.text
            print(f"      POST attempt {attempt+1}: HTTP {r.status_code}")
        except Exception as e:
            print(f"      POST attempt {attempt+1} error: {e}")
        time.sleep(RETRY_SLEEP)
    return None


def get_page(session, offset):
    """GET a paginated result page."""
    url = f"{PAGE_URL}?pager.offset={offset}"
    for attempt in range(RETRY_ATTEMPTS):
        try:
            r = session.get(url, timeout=HTTP_TIMEOUT)
            if r.status_code == 200:
                return r.text
            print(f"      GET pg attempt {attempt+1}: HTTP {r.status_code}")
        except Exception as e:
            print(f"      GET pg attempt {attempt+1} error: {e}")
        time.sleep(RETRY_SLEEP)
    return None


def scrape_chunk(county_name, county_code, district, start_date, end_date, year_chunk_label):
    """Scrape one (county, date-range) chunk. Returns list of row dicts or
    the sentinel ['EXCEEDS'] if the cap was hit (caller should subdivide)."""
    session = make_session()
    action_url = fetch_init_action_url(session)
    time.sleep(THROTTLE_SECS)

    html = post_query(session, action_url, district, county_code, start_date, end_date)
    if html is None:
        print(f"    [{county_name} {year_chunk_label}] FETCH_FAILED")
        return None

    total = parse_total_count(html)
    if total == "EXCEEDS":
        return ["EXCEEDS"]
    if total is None:
        # 0 results case — page may not show a count
        if "No Matches Found" in html or "0 results" in html:
            return []
        print(f"    [{county_name} {year_chunk_label}] could not parse count")
        return []

    print(f"    [{county_name} {year_chunk_label}] {total} results")
    if total == 0:
        return []

    # Apply API-number sort — stabilizes pagination across sequential GETs.
    time.sleep(THROTTLE_SECS)
    for attempt in range(RETRY_ATTEMPTS):
        try:
            sr = session.get(f"{SORT_URL}?order={SORT_KEY}", timeout=HTTP_TIMEOUT)
            if sr.status_code == 200:
                break
        except Exception as e:
            print(f"      sort attempt {attempt+1} error: {e}")
        time.sleep(RETRY_SLEEP)
    else:
        print(f"    [{county_name} {year_chunk_label}] sort FETCH_FAILED — pagination may be incomplete")
        sr = None

    # Page 0 (first page after sort)
    if sr is not None and sr.status_code == 200:
        rows = parse_listing_page(sr.text, county_name, county_code, year_chunk_label)
    else:
        rows = parse_listing_page(html, county_name, county_code, year_chunk_label)
    # Dedupe by univ_doc_no — that's the per-status-event unique key. permit_no
    # repeats across status events (initial approval + amendments + reissuances)
    # so cannot be used as dedup key. The reported `total` from the listing
    # counts events, not unique permits — so we aggregate to permits downstream.
    seen = {r["univ_doc_no"] for r in rows if r["univ_doc_no"]}

    # Paginate. Loop until either: (a) all `total` events covered, or (b) a
    # page returns 0 new events.
    offset = 20
    while len(seen) < total:
        time.sleep(THROTTLE_SECS)
        page_html = get_page(session, offset)
        if page_html is None:
            print(f"    [{county_name} {year_chunk_label}] page offset={offset} FETCH_FAILED — partial result ({len(seen)}/{total})")
            break
        page_rows = parse_listing_page(page_html, county_name, county_code, year_chunk_label)
        new_rows = [r for r in page_rows if r["univ_doc_no"] and r["univ_doc_no"] not in seen]
        if not new_rows:
            print(f"    [{county_name} {year_chunk_label}] no new events at offset={offset}; stopping ({len(seen)}/{total})")
            break
        rows.extend(new_rows)
        seen.update(r["univ_doc_no"] for r in new_rows)
        offset += 20

    if len(seen) < total:
        print(f"    [{county_name} {year_chunk_label}] WARNING: captured {len(seen)} events of {total} reported")
    return rows


def scrape_county_year(county_name, county_code, district, year):
    """Full event-level scrape of one (county, year). Falls back to monthly
    chunks if the year exceeds the listing cap."""
    label = f"{year}"
    start = f"01/01/{year}"
    end = f"12/31/{year}"
    result = scrape_chunk(county_name, county_code, district, start, end, label)
    if result == ["EXCEEDS"]:
        print(f"    [{county_name} {year}] cap hit — falling back to monthly")
        rows = []
        for month in range(1, 13):
            mday = {1:31,2:29 if year%4==0 and (year%100!=0 or year%400==0) else 28,
                    3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}[month]
            mstart = f"{month:02d}/01/{year}"
            mend = f"{month:02d}/{mday:02d}/{year}"
            time.sleep(THROTTLE_SECS)
            mresult = scrape_chunk(county_name, county_code, district, mstart, mend, f"{year}-{month:02d}")
            if mresult == ["EXCEEDS"]:
                print(f"      [{county_name} {year}-{month:02d}] MONTHLY cap also exceeded — skipped")
                continue
            if mresult is None:
                continue
            rows.extend(mresult)
        return rows
    return result or []


def scrape_count_only(county_name, county_code, district, start_date, end_date, label):
    """Counts-only — POST query, return (count, status). Fast path for the
    density choropleth: we don't need event rows, just totals.

    Returns dict {count: int, status: 'ok'|'exceeds'|'fail'} or None on hard fail.
    """
    session = make_session()
    action_url = fetch_init_action_url(session)
    time.sleep(THROTTLE_SECS)
    html = post_query(session, action_url, district, county_code, start_date, end_date)
    if html is None:
        return None
    total = parse_total_count(html)
    if total == "EXCEEDS":
        return {"count": None, "status": "exceeds"}
    if total is None:
        return {"count": 0, "status": "ok"}  # treat unparseable as 0
    return {"count": total, "status": "ok"}


def scrape_county_year_counts_only(county_name, county_code, district, year):
    """Counts-only year scrape with monthly fallback if year exceeds cap."""
    label = f"{year}"
    start = f"01/01/{year}"
    end = f"12/31/{year}"
    result = scrape_count_only(county_name, county_code, district, start, end, label)
    if result is None:
        return [{"county_name": county_name, "county_code": county_code,
                 "district": district, "year": year, "month": "",
                 "count": "", "status": "fail"}]
    if result["status"] == "ok":
        return [{"county_name": county_name, "county_code": county_code,
                 "district": district, "year": year, "month": "",
                 "count": result["count"], "status": "ok"}]
    # Cap exceeded — subdivide monthly
    print(f"    [{county_name} {year}] cap hit — falling back to monthly")
    out = []
    for month in range(1, 13):
        mday = {1:31,2:29 if year%4==0 and (year%100!=0 or year%400==0) else 28,
                3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}[month]
        mstart = f"{month:02d}/01/{year}"
        mend = f"{month:02d}/{mday:02d}/{year}"
        time.sleep(THROTTLE_SECS)
        mresult = scrape_count_only(county_name, county_code, district, mstart, mend, f"{year}-{month:02d}")
        if mresult is None:
            out.append({"county_name": county_name, "county_code": county_code,
                        "district": district, "year": year, "month": month,
                        "count": "", "status": "fail"})
            continue
        out.append({"county_name": county_name, "county_code": county_code,
                    "district": district, "year": year, "month": month,
                    "count": mresult["count"] if mresult["status"] == "ok" else "",
                    "status": mresult["status"]})
    return out


def append_count_rows(rows):
    if not rows:
        return
    new_file = not os.path.exists(OUT_COUNTS)
    fields = ["county_name", "county_code", "district", "year", "month", "count", "status"]
    tmp = OUT_COUNTS + ".tmp"
    existing = []
    if not new_file:
        with open(OUT_COUNTS) as f:
            existing = list(csv.DictReader(f))
    with open(tmp, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in existing:
            writer.writerow({k: r.get(k, "") for k in fields})
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fields})
    os.replace(tmp, OUT_COUNTS)


def main_counts_only():
    os.makedirs("outputs/refresh", exist_ok=True)
    state = {"completed": []}
    if os.path.exists(COUNTS_CHECKPOINT):
        with open(COUNTS_CHECKPOINT) as f:
            state = json.load(f)
    completed = set(tuple(c) for c in state["completed"])

    yr_start = START_YEAR
    yr_end = END_YEAR
    print(f"=== RRC W-1 counts-only: {len(TARGETS)} counties × {yr_start}-{yr_end} ===")
    for (cname, ccode, district) in TARGETS:
        for year in range(yr_start, yr_end + 1):
            key = (cname, year)
            if key in completed:
                continue
            try:
                rows = scrape_county_year_counts_only(cname, ccode, district, year)
                append_count_rows(rows)
                state["completed"].append(list(key))
                tmp = COUNTS_CHECKPOINT + ".tmp"
                with open(tmp, "w") as f:
                    json.dump(state, f)
                os.replace(tmp, COUNTS_CHECKPOINT)
                cnt = sum(int(r["count"]) for r in rows if r.get("count") not in ("", None))
                print(f"  [{cname} {year}] {cnt}")
            except Exception as e:
                print(f"  [{cname} {year}] ERROR {e}")
                continue
    print("=== counts-only scrape complete ===")
    """Scrape one (county, year). Falls back to monthly if cap exceeded."""
    label = f"{year}"
    start = f"01/01/{year}"
    end = f"12/31/{year}"
    result = scrape_chunk(county_name, county_code, district, start, end, label)
    if result == ["EXCEEDS"]:
        print(f"    [{county_name} {year}] cap hit — falling back to monthly")
        rows = []
        for month in range(1, 13):
            month_end_day = {1:31,2:29 if year%4==0 and (year%100!=0 or year%400==0) else 28,
                             3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}[month]
            mlabel = f"{year}-{month:02d}"
            mstart = f"{month:02d}/01/{year}"
            mend = f"{month:02d}/{month_end_day:02d}/{year}"
            time.sleep(THROTTLE_SECS)
            mresult = scrape_chunk(county_name, county_code, district, mstart, mend, mlabel)
            if mresult == ["EXCEEDS"]:
                # If even monthly hits cap, log and skip — doesn't happen in this universe
                print(f"      [{county_name} {mlabel}] MONTHLY cap also exceeded — skipped")
                continue
            if mresult is None:
                continue
            rows.extend(mresult)
        return rows
    return result or []


# ============================================================================
# Checkpoint + write
# ============================================================================

def load_checkpoint():
    if os.path.exists(CHECKPOINT):
        with open(CHECKPOINT) as f:
            return json.load(f)
    return {"completed": []}


def save_checkpoint(state):
    tmp = CHECKPOINT + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, CHECKPOINT)


def append_rows(rows):
    """Append rows to OUT_CSV atomically. If file doesn't exist, write header."""
    if not rows:
        return
    new_file = not os.path.exists(OUT_CSV)
    tmp = OUT_CSV + ".tmp"
    # read existing, then write all to tmp
    existing = []
    if not new_file:
        with open(OUT_CSV) as f:
            reader = csv.DictReader(f)
            existing = list(reader)
    with open(tmp, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in existing:
            writer.writerow({k: r.get(k, "") for k in CSV_FIELDS})
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in CSV_FIELDS})
    os.replace(tmp, OUT_CSV)


# ============================================================================
# Main
# ============================================================================

def main():
    os.makedirs("outputs/refresh", exist_ok=True)
    state = load_checkpoint()
    completed = set(tuple(c) for c in state["completed"])

    # Allow CLI override: scrape_rrc_w1.py <county> <year_start> <year_end>
    targets = TARGETS
    yr_start = START_YEAR
    yr_end = END_YEAR
    if len(sys.argv) >= 2 and sys.argv[1] != "all":
        targets = [t for t in TARGETS if t[0].upper() == sys.argv[1].upper()]
        if not targets:
            print(f"unknown county: {sys.argv[1]}")
            sys.exit(1)
    if len(sys.argv) >= 3:
        yr_start = int(sys.argv[2])
    if len(sys.argv) >= 4:
        yr_end = int(sys.argv[3])

    print(f"=== RRC W-1 scrape: {len(targets)} counties × {yr_start}-{yr_end} ===")

    for (cname, ccode, district) in targets:
        print(f"\n[{cname}] district {district}, county_code {ccode}")
        for year in range(yr_start, yr_end + 1):
            key = (cname, year)
            if key in completed:
                continue
            try:
                rows = scrape_county_year(cname, ccode, district, year)
                if rows is None:
                    print(f"  {year}: SKIPPED (fetch failed)")
                    continue
                append_rows(rows)
                state["completed"].append(list(key))
                save_checkpoint(state)
                file_total = (sum(1 for _ in open(OUT_CSV)) - 1) if os.path.exists(OUT_CSV) else 0
                print(f"  {year}: +{len(rows)} rows (total file {file_total})")
            except Exception as e:
                print(f"  {year}: ERROR {e}")
                continue

    print("\n=== scrape complete ===")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "counts":
        main_counts_only()
    else:
        main()
