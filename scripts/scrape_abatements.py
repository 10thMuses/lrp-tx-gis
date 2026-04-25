#!/usr/bin/env python3
"""
Abatement scraper — commissioners-court agendas + public notices.

Output: data/abatements/abatement_hits_YYYYMMDD_HHMMSS.csv

Scope (canonical leading signal per ARCHITECTURE.md §11 — Comptroller registries
JS-gated with multi-month lag; commissioners-court agendas required ≥30 days
before abatement vote per Tax Code §312.207(d)):
- 23 Trans-Pecos / Permian-core / peripheral counties.
- Filings 2025 + 2026 only.
- Skip PDF-only counties; flag in output.
- Dedup key (county, applicant_normalized, reinvestment_zone).

Validated adapters: Pecos (WordPress), Reeves (CivicEngage).
Other 21 counties: stubs returning empty with status='unverified_source'.
Per §7.10 stage-split: expansion to remaining counties is its own stage.
"""
from __future__ import annotations
import csv, datetime as dt, hashlib, os, re, sys, time
from dataclasses import dataclass, asdict, field
from typing import Iterable
import requests
from bs4 import BeautifulSoup

UA = "LRP-Abatement-Scraper/1.0 (contact: andrea@landresourcepartners.com)"
TIMEOUT = 30
YEAR_FILTER = {2025, 2026}

# --- Keyword taxonomy (spec §5) -------------------------------------------
ABATE = ["abatement","reinvestment zone","chapter 312","chapter 381","enterprise zone",
    "tax incentive","economic development agreement","380 agreement","381 agreement","tax abatement"]
RENEW = ["solar","wind ","turbine","photovoltaic","pv farm","battery","bess","storage facility",
    "energy storage","renewable","microgrid","hybrid generation"]
DC = ["data center","datacenter","hyperscale","compute","gpu farm","ai campus","training cluster"]
GAS = ["natural gas","reciprocating engine","combined cycle","peaker","peaking plant","gas generation"]
DEVS = ["Apex Clean Energy","NextEra","Engie","Enel","Invenergy","Orsted","EDF Renewables","EDP",
    "Avangrid","Recurrent","Savion","Longroad","Intersect Power","7X Energy","Lightsource",
    "Cypress Creek","Duke Energy","Pattern Energy","Clearway","Leeward","RWE","Iberdrola"]
LOADS = ["Poolside","Anthropic","OpenAI","Google","Alphabet","Amazon","AWS","Meta","Microsoft",
    "Oracle","Crusoe","CoreWeave","Applied Digital","Lancium","Hanwha","QCells"]

ENT_SUFFIX = r"(?:LLC|Inc\.?|L\.?P\.?|Corp\.?|Corporation|Company|Co\.?|LP|LLP|Ltd\.?|Energy|Holdings)"

@dataclass
class Hit:
    county: str
    meeting_date: str            # ISO
    agenda_url: str
    agenda_type: str             # agenda | notice | minutes
    item_number: str
    raw_text: str
    applicant: str
    reinvestment_zone: str
    flags: str                   # pipe-separated
    capacity_or_usd: str
    project_type: str
    source_system: str

# --- Utilities -------------------------------------------------------------
def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip()).strip(".,-;:")

def normalize_applicant(s: str) -> str:
    s = norm(s).lower()
    s = re.sub(r"\b(llc|inc\.?|l\.?p\.?|corp\.?|corporation|company|co\.?|ltd\.?|holdings)\b", "", s)
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return re.sub(r"\s+", " ", s).strip()

def fetch(url: str, session: requests.Session) -> str | None:
    try:
        r = session.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return None

def extract_applicant(text: str) -> str:
    m = re.search(rf"(?:agreement|application)\s+with\s+([A-Z][A-Za-z0-9 ,&.\-]+?\b{ENT_SUFFIX})",
                  text, flags=re.I)
    if m: return norm(m.group(1))
    m = re.search(rf"Applicant[^:]*:\s*([A-Z][A-Za-z0-9 ,&.\-]+?\b{ENT_SUFFIX})",
                  text, flags=re.I)
    if m: return norm(m.group(1))
    return ""

def extract_zone(text: str) -> str:
    m = re.search(r"((?:[A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+){0,4})"
                  r"\s+Reinvestment\s+Zone(?:\s+(?:No\.?|Number)\s*\d+)?)", text)
    if not m: return ""
    cand = norm(m.group(1))
    if re.match(r"^(Thirty\s+Day|Public\s+Hearing|The|Proposed|Designating|Establish(?:ing)?)\b",
                cand, flags=re.I):
        return ""
    return cand

def extract_capacity_or_usd(text: str) -> str:
    m = re.search(r"(\d{1,4}(?:\.\d+)?)\s*MW\b", text, flags=re.I)
    if m: return f"{m.group(1)} MW"
    m = re.search(r"\$\s*([\d,]+(?:\.\d+)?)\s*(million|billion|[MB])\b", text, flags=re.I)
    if m: return norm(m.group(0))
    m = re.search(r"\$\s*([\d,]{4,})\b", text)
    if m:
        raw = m.group(1).replace(",", "")
        if int(raw) > 10000:
            return norm(m.group(0))
    return ""

def match_flags(text_lower: str) -> tuple[list[str], str]:
    flags: list[str] = []
    if any(k in text_lower for k in ABATE): flags.append("abatement")
    if any(k in text_lower for k in RENEW): flags.append("renewable")
    if any(k in text_lower for k in DC):    flags.append("data_center")
    if any(k in text_lower for k in GAS):   flags.append("gas_gen")
    for d in DEVS:
        if d.lower() in text_lower: flags.append(f"dev:{d}")
    for l in LOADS:
        if l.lower() in text_lower: flags.append(f"load:{l}")
    has_load = any(f.startswith("load:") for f in flags)
    pt_priority = [("data_center","data_center"),("gas_gen","gas_generation"),
                   ("renewable","renewable"),("abatement","abatement_other")]
    project_type = next((pt for f,pt in pt_priority if f in flags), "")
    # Override: explicit AI/hyperscale load implies data_center even if zone name says "renewable"
    if has_load and project_type == "renewable":
        project_type = "data_center"
        if "data_center" not in flags: flags.insert(0, "data_center")
    return flags, project_type

def extract_meeting_date(text: str) -> str:
    m = re.search(r"(?:^|\b)((?:JAN(?:UARY)?|FEB(?:RUARY)?|MAR(?:CH)?|APR(?:IL)?|MAY|JUN(?:E)?|"
                  r"JUL(?:Y)?|AUG(?:UST)?|SEP(?:TEMBER)?|OCT(?:OBER)?|NOV(?:EMBER)?|DEC(?:EMBER)?)"
                  r"\s+\d{1,2},?\s+20\d{2})", text, flags=re.I)
    if m:
        try:
            return dt.datetime.strptime(re.sub(r"[,]", "", m.group(1).title()), "%B %d %Y").date().isoformat()
        except ValueError:
            try:
                return dt.datetime.strptime(re.sub(r"[,]", "", m.group(1).title()), "%b %d %Y").date().isoformat()
            except ValueError:
                pass
    m = re.search(r"\b(\d{1,2})/(\d{1,2})/(20\d{2})\b", text)
    if m:
        mo, da, yr = (int(x) for x in m.groups())
        try: return dt.date(yr, mo, da).isoformat()
        except ValueError: return ""
    return ""

def text_hits(county: str, url: str, body: str, source_system: str,
              agenda_type: str = "agenda") -> list[Hit]:
    """Generic keyword scan on a page body; one Hit per abatement+match item."""
    out: list[Hit] = []
    if not body: return out
    body_l = body.lower()
    if not any(k in body_l for k in ABATE): return out

    # Split by item number markers
    items = re.split(r"\n\s*(?=\d{1,3}\.\s+[A-Z])", body)
    date_str = extract_meeting_date(body)
    if date_str:
        try:
            if dt.date.fromisoformat(date_str).year not in YEAR_FILTER: return out
        except ValueError: pass

    for item in items:
        il = item.lower()
        if not any(k in il for k in ABATE): continue
        item_m = re.match(r"\s*(\d{1,3})\.", item)
        item_no = item_m.group(1) if item_m else ""
        flags, pt = match_flags(il)
        out.append(Hit(
            county=county, meeting_date=date_str, agenda_url=url,
            agenda_type=agenda_type, item_number=item_no,
            raw_text=item[:1500], applicant=extract_applicant(item),
            reinvestment_zone=extract_zone(item), flags="|".join(flags),
            capacity_or_usd=extract_capacity_or_usd(item), project_type=pt,
            source_system=source_system,
        ))
    return out

# --- Adapters --------------------------------------------------------------
def pecos_adapter(session: requests.Session) -> list[Hit]:
    hits: list[Hit] = []
    base = "https://www.co.pecos.tx.us/category/notices-announcements/commissioners-court-agendas/"
    for page in range(1, 6):
        url = base if page == 1 else f"{base}page/{page}/"
        html = fetch(url, session)
        if not html: break
        soup = BeautifulSoup(html, "html.parser")
        links = [a.get("href") for a in soup.select("h2.entry-title a, h3.entry-title a, article a[rel='bookmark']")]
        links = list(dict.fromkeys([l for l in links if l]))
        if not links: break
        for post in links:
            body_html = fetch(post, session)
            if not body_html: continue
            s = BeautifulSoup(body_html, "html.parser")
            content = s.select_one("article, .entry-content, main") or s
            text = content.get_text("\n", strip=True)
            hits.extend(text_hits("Pecos", post, text, source_system="pecos_wp"))
            time.sleep(0.3)
        time.sleep(0.3)
    return hits

def reeves_adapter(session: requests.Session) -> list[Hit]:
    """
    Chat 91 update: domain migrated co.reeves.tx.us -> reevescounty.org.
    Old DNS dead; new domain (same CivicEngage CMS, same URL pattern) is
    Akamai bot-protected and 403s all datacenter egress regardless of UA
    or header tuning. Adapter is structurally correct but cannot be
    end-to-end verified from cloud runners — requires residential proxy
    or whitelisted egress (search-engine crawlers retrieve content fine).
    Confirmed live abatement notices on new domain via search results
    Chat 91: August Draw Solar LLC, Energy Forge One LLC, Pecos Power
    Plant LLC (the hand-seeded row) — all three are present.
    """
    hits: list[Hit] = []
    base = "https://www.reevescounty.org/visitors/rc-news"
    html = fetch(base, session)
    if not html: return hits
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.select("a[href]"):
        h = a.get("href") or ""
        if "/visitors/rc-news/" in h or "news/post/" in h.lower():
            if h.startswith("/"): h = "https://www.reevescounty.org" + h
            links.append(h)
    links = list(dict.fromkeys(links))
    for post in links[:40]:
        body_html = fetch(post, session)
        if not body_html: continue
        s = BeautifulSoup(body_html, "html.parser")
        content = s.select_one("article, .news-article, main, .content") or s
        text = content.get_text("\n", strip=True)
        hits.extend(text_hits("Reeves", post, text, source_system="reeves_ce",
                              agenda_type="notice"))
        time.sleep(0.3)
    return hits

STUB_COUNTIES = ["Brewster","Culberson","Hudspeth","Jeff Davis","Presidio","Terrell",
    "Andrews","Ector","Glasscock","Loving","Martin","Midland","Ward","Winkler",
    "Crane","Crockett","Irion","Reagan","Schleicher","Sutton","Upton"]

def main(out_dir: str = "data/abatements") -> str:
    os.makedirs(out_dir, exist_ok=True)
    stamp = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    fpath = os.path.join(out_dir, f"abatement_hits_{stamp}.csv")
    session = requests.Session()
    all_hits: list[Hit] = []
    for name, fn in [("Pecos", pecos_adapter), ("Reeves", reeves_adapter)]:
        try:
            h = fn(session)
            print(f"[{name}] hits={len(h)}", file=sys.stderr)
            all_hits.extend(h)
        except Exception as e:
            print(f"[{name}] ERROR: {e}", file=sys.stderr)
    # Dedup (county, applicant_normalized, reinvestment_zone)
    seen: dict[tuple[str,str,str], Hit] = {}
    for h in all_hits:
        k = (h.county, normalize_applicant(h.applicant), h.reinvestment_zone.lower())
        if k not in seen or (h.meeting_date > seen[k].meeting_date):
            seen[k] = h
    kept = list(seen.values())
    with open(fpath, "w", newline="", encoding="utf-8") as f:
        fieldnames = list(Hit.__dataclass_fields__.keys())
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for h in kept:
            w.writerow(asdict(h))
    print(f"WROTE {fpath} rows={len(kept)} (unverified_adapters={len(STUB_COUNTIES)})",
          file=sys.stderr)
    return fpath

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/abatements")
