# ABATEMENT DISCOVERY — Spec

Companion to `docs/refinement-sequence.md` §137. Authoritative discovery-stage spec. Replaces the handoff-doc pattern for this stage. BUILD-stage work gated on operator sign-off at §Open questions below.

---

## 1. Regulatory context (do not re-litigate)

- **Ch. 313 expired 12/31/2022.** Grandfathered agreements still report; no new filings.
- **Ch. 403 / JETI Act (eff 1/1/2024) explicitly excludes renewables.** Statute bars "non-dispatchable electric generation facility or electric energy storage facility." Solar, wind, standalone BESS out of scope.
- **Ch. 312 is the active mechanism for renewables** (city/county). **Ch. 381** parallels for county economic-development agreements.
- **Comptroller Ch. 312 search tool is JavaScript-gated.** `comptroller.texas.gov/economy/development/search-tools/ch312/abatements-simple.php` static-fetches "Error Loading Page." Same failure mode as RRC MFT (see `settled.md` §Scoped-out). Plus multi-month reporting lag. Unusable as primary source.
- **Commissioners-court agendas + public-notices pages are the real leading indicator.** Tax Code §312.207(d) requires ≥30 days public notice before abatement vote, including applicant, site description, anticipated improvements, estimated cost.

---

## 2. Leading-indicator hierarchy

| Signal | Public | Lead to COD | Source |
|---|---|---|---|
| Land lease signed | No | 3–7 yr | Private; sometimes CAD deed records |
| ERCOT queue entry | Yes | 2–5 yr | ERCOT GIS Report (monthly) |
| Reinvestment zone creation (§312.201/401) | Yes | 1–3 yr | County commissioners court resolution |
| Abatement application + 30-day notice | Yes | 1–2 yr | County agenda + public notices |
| Agreement executed | Yes | 12–18 mo | Comptroller Ch. 312 (lagged) |
| Construction permits | Yes | 6–12 mo | RRC, TCEQ CRPUB |

Commissioners-court scraping = earliest public committed-capital signal with material detail.

---

## 3. Data sources ranked

1. **County commissioners-court agendas** — primary feed. 30-day statutory notice, per-item detail.
2. **County public-notices pages** — same sites, separate archive. Catches reinvestment-zone notices ahead of agenda vote.
3. **Comptroller Ch. 312 Abatement Registry** — historical baseline only; manual one-time spreadsheet download acceptable.
4. **Comptroller Local Development Agreements DB (380/381/312 union)** — skipped. No material uplift over #1, same JS-gating.
5. **Comptroller Ch. 313 Biennial Reports** — legacy pipeline for grandfathered renewables (~2/3 of pre-2023 cohort). Static HTML, scrapable. Useful for 2018–2022 backfill.

---

## 4. County adapter status (23-county scope per §137)

| Status | Counties | Site pattern |
|---|---|---|
| **Validated** | Pecos | WordPress `/category/notices-announcements/commissioners-court-agendas/`, paginated, ~18-mo archive |
| **Validated** | Reeves | CivicEngage `/visitors/rc-news`, news-post pattern |
| Stubbed (unverified) | Culberson, Ector, Ward | Placeholder URLs — must verify before use. Ward = PDF minutes at `/page/ward.Court.Minutes` |
| TODO | Andrews, Brewster, Crane, Crockett, Glasscock, Hudspeth, Irion, Jeff Davis, Loving, Martin, Midland, Presidio, Reagan, Schleicher, Sutton, Terrell, Upton, Winkler | Unknown |

---

## 5. Scraper spec

Per-county adapter pattern. Dependencies: `requests`, `beautifulsoup4`. Output: `data/abatements/abatement_hits_YYYYMMDD_HHMMSS.csv`.

Each adapter implements:

1. `enumerate_agenda_urls()` → yields `(url, title)` from paginated index
2. `parse_agenda(url, html)` → returns `list[Hit]` of keyword-matched items

### Keyword taxonomy (lowercase substring match on normalized text)

- **Abatement markers:** `abatement`, `reinvestment zone`, `chapter 312`, `chapter 381`, `enterprise zone`, `tax incentive`, `economic development agreement`, `380 agreement`, `381 agreement`, `tax abatement`
- **Renewable project markers:** `solar`, `wind ` (trailing space to avoid `winding`), `turbine`, `photovoltaic`, `pv farm`, `battery`, `bess`, `storage facility`, `energy storage`, `renewable`, `microgrid`, `hybrid generation`
- **Data-center markers:** `data center`, `datacenter`, `hyperscale`, `compute`, `gpu farm`, `ai campus`, `training cluster`
- **Gas-generation markers:** `natural gas`, `reciprocating engine`, `combined cycle`, `peaker`, `peaking plant`, `gas generation`
- **Developer list:** Apex Clean Energy, NextEra, Engie, Enel, Invenergy, Orsted, EDF Renewables, EDP, Avangrid, Recurrent, Savion, Longroad, Intersect Power, 7X Energy, Lightsource, Cypress Creek, Duke Energy, Pattern Energy, Clearway, Leeward, RWE, Iberdrola
- **AI / hyperscale load list:** Poolside, Anthropic, OpenAI, Google/Alphabet, Amazon/AWS, Meta, Microsoft, Oracle, Crusoe, CoreWeave, Applied Digital, Lancium, Hanwha, QCells

### Critical regex: `extract_applicant()` — needs BOTH fixes

`re.I` flag AND `\b` word boundary before the entity group. Without `\b`, "Co" in "Pecos" matches the `Co.` corporation suffix and truncates "Pecos Power Plant LLC" to "Peco":

```python
def extract_applicant(text: str) -> str:
    ent = r"(?:LLC|Inc\.?|L\.?P\.?|Corp\.?|Corporation|Company|Co\.?|LP|LLP|Ltd\.?|Energy|Holdings)"
    m = re.search(
        rf"(?:agreement|application)\s+with\s+([A-Z][A-Za-z0-9 ,&.\-]+?\b{ent})",
        text, flags=re.I,
    )
    if m:
        return norm(m.group(1))
    m = re.search(
        rf"Applicant[^:]*:\s*([A-Z][A-Za-z0-9 ,&.\-]+?\b{ent})",
        text, flags=re.I,
    )
    if m:
        return norm(m.group(1))
    return ""
```

Accepted tradeoff: `Energy` in entity suffix early-stops on "NextEra Energy Resources LLC" → captures "NextEra Energy." Downstream SOS / Regrid resolves to full legal name.

---

## 6. Field catalog

### High-reliability direct extraction

| Field | Type | Source pattern |
|---|---|---|
| `county` | string | Hard-coded per adapter |
| `meeting_date` | ISO date | "MONDAY, NOVEMBER 10, 2025" or "11/10/2025" |
| `agenda_url` | URL | Canonical post URL |
| `agenda_type` | enum | `agenda` \| `notice` \| `minutes` |
| `item_number` | string | "26." prefix in numbered agenda |
| `raw_text` | string | Item body, ≤ 1500 chars |
| `applicant` | string | Per §5 regex |
| `reinvestment_zone` | string | "\<X\> Reinvestment Zone" regex |
| `flags` | pipe-separated | `abatement`, `renewable`, `data_center`, `gas_gen`, `dev:<name>`, `load:<name>` |

### Medium-reliability (~70% hit rate)

| Field | Notes |
|---|---|
| `capacity_or_usd` | "226 MW" or "$150,000,000" best-effort |
| `project_type` | Derived from keyword flags; empty for pure zone creations |

### Deferred to BUILD stage

| Field | Rationale |
|---|---|
| `latitude`, `longitude` | Notices reference exhibit-map PDFs; geocoding needs CAD parcel cross-ref or manual extraction |
| `parcel_id` | CAD lookup by applicant name |
| `abatement_pct`, `abatement_years` | Often absent from public notice; requires minutes or executed agreement |
| `status` | `proposed` / `approved` / `executed` / `terminated` — requires cross-meeting tracking |

---

## 7. Live hits confirmed during discovery (2026-04-23)

| County | Hit | Date | Note |
|---|---|---|---|
| Pecos | Longfellow Renewable Energy Reinvestment Zone | 2025-01-13 | Zone name references renewables; first abatement within was a data-center load — pattern: renewable-branded zones hosting co-located compute |
| Pecos | Poolside Inc. Ch. 312 abatement | 2025-11-10 agenda item #26 | AI code-assistant compute company. Despite zone name, data-center filing, not solar |
| Pecos | Apex Clean Energy donation to Precinct 2 (Rooney Park trees) | 2025-11-10 item #17 | Relationship signal, not a filing. Expect Apex abatement within 12–18 mo |
| Reeves | Pecos Power Plant LLC — 30-day notice | 2025-06-13 | 226 MW natgas reciprocating engines; $150–200M; Enterprise Zone (Gov Code Ch. 2303, treated as reinvestment zone per §312.2011) |

---

## 8. Schema proposal — BUILD stage

### Option A (recommended): standalone `tax_abatements` layer

Own columns, own sidebar toggle, independent time-series playback. Extra columns beyond standard `layer_id`, `lat`, `lon`, `name`:

```
county, meeting_date, status, agenda_url, applicant,
reinvestment_zone, project_type, capacity_or_usd,
developer_parent, load_customer, notice_date,
agreement_executed_date, abatement_pct, abatement_years,
raw_text, source_system
```

Where `status` ∈ `zone_proposed`, `zone_created`, `application_pending`, `hearing_scheduled`, `agreement_approved`, `agreement_executed`, `terminated`, `expired`.

Mapping to existing `combined_points.csv` schema: `layer_id=tax_abatements`, `capacity_mw` from parsed `capacity_or_usd`, `operator=applicant`, `funnel_stage=status`, `project=reinvestment_zone`. Existing columns `inr`, `poi`, `zone`, `entity` can absorb abatement fields without extension.

### Option B: annotation on existing layers

Join abatement flag to `ercot_queue`, `solar`, `wind`, future `data_centers`. Later enhancement, not mutually exclusive with A.

---

## 9. Open questions — BUILD approval gate

1. **Layer scope:** Option A standalone vs. Option B annotation vs. both?
2. **County coverage:** all 23 at once, or phased (5 Permian-core + 18 rollout)? Cost: ~1 day per CivicEngage/WordPress county, ~2–3 days custom/PDF-only.
3. **PDF parsing:** `pdfminer.six` (text PDFs), Tesseract OCR (scans, slower), or skip PDF-only counties with low historical volume?
4. **Historical backfill depth:** spec §137 says 2020–present; archives only go ~18 mo. Open Records requests + Wayback crawls needed for 2020. Is 18-mo trailing OK for BUILD with backfill as Phase 2?
5. **Comptroller Ch. 312 spreadsheet:** manual quarterly download (~20 min) vs. Playwright automation (~2 hr build)? Recommend manual.
6. **Deduplication:** one abatement appears in zone notice → abatement notice → agenda vote → minutes → Comptroller registry. Recommend dedup key `(county, applicant_normalized, reinvestment_zone)`, preserve sighting dates as array, status = latest.
7. **GitHub Actions cadence:** weekly (captures 30-day notices cleanly) vs. monthly (risks missing time-sensitive). Recommend weekly.
8. **Alerting:** push new hits to Grid Wire or separate operator feed? Out of scope for BUILD; defer.

---

## 10. Recommended BUILD sequence (gated on §9 answers)

Assuming Option A / 5-county Phase 1 / `pdfminer.six`:

1. Build `scripts/scrape_abatements.py` from adapter pattern above. Apply both regex fixes (`re.I` + `\b`).
2. Complete Ward / Culberson / Ector adapters with PDF text extraction.
3. Run 5-county scan, commit `data/abatements/abatement_hits_<date>.csv`.
4. Geocode: CAD parcel centroid via applicant-name lookup; fallback to reinvestment-zone centroid from exhibit maps (manual first pass); fallback to county centroid via `county_labels` join.
5. Transform to `combined_points.csv` schema, append rows.
6. Add `tax_abatements` entry to `layers.yaml`. Icon from sprite sheet. Respect VISUAL OVERHAUL + SIZING+WATERMARK conventions.
7. Build + deploy per `principles.md` acceptance protocol.
8. Wire filter UI controls for `project_type`, `status`, `meeting_date` range.
9. Add `.github/workflows/abatement-scrape.yml` weekly cron + diff alerting.

---

## 11. Scope explicitly out

- **Local Development Agreements Database (Ch. 380/381/312 union)** — not materially better than commissioners-court scrape for leading-indicator value, JS-gated anyway.
- **TCEQ NSR diesel-genset permits** — already tracked in `docs/settled.md`; separate data-center backup-power intelligence surface, not an abatement signal.
