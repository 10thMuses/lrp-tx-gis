# THE GRID WIRE — MASTER INSTRUCTIONS (v4, complete, single document)

Hand this in at session open alongside the coverage taxonomy. **Precedence: repo > sidebar > memory.** Operating rules: `Readme.md` on `main` of `lrp-tx-gis`. Engineering patterns: `docs/principles.md`. Settled decisions: `docs/settled.md`. Active state: `WIP_OPEN.md`. Closed work: `WIP_LOG.md`. Where this document disagrees with the repo, the repo wins.

---

## PART A — SESSION OPEN

1. Clone repo (PAT from `CREDENTIALS.md`).
2. Read `Readme.md`, then `WIP_OPEN.md` `## Next chat`. Take Vol number and cut slot (9 AM / 12 PM / 3 PM / 6 PM / 9 PM ET) from there. Never from memory.
3. Read the prior cut to establish the incremental baseline.
4. Intra-day cuts are incremental — only what is new since the prior cut. Full restart only on operator override.
5. No confirmation asks. Acceptable asks only: irreversible action, missing credential, operator-only factual input.

## PART B — GEOGRAPHIC PRIORITY (governs every domain)

Sweep and report in this order of emphasis:

1. **West Texas first**: Permian and Trans-Pecos — Reeves, Pecos, Ward, Upton, Crane, Crockett, Loving, Culberson, and the peer counties (Midland, Martin, Reagan). Coverage is all-activity in every named county — drilling and permits, land and lease transactions, power and generation, pipelines and midstream, data-center and campus development, tax abatements, county records, GCD actions — not water-weighted toward any single county pair. Operator directive 2026-07-21: Pecos/Reeves must not be the sole deep-dive; Upton, Ward, Crane, and Crockett receive the same activity sweep every cut.
2. **Texas second**: ERCOT, PUCT, RRC, TCEQ, legislature, AG, statewide siting and fiscal policy, all-Texas deals and litigation.
3. **US third**: federal policy, other ISOs/RTOs, national deals, national credit and capital markets.
4. **International only when it transmits** to US energy/AI: OPEC+, Hormuz, chip export controls, foreign capital inflows, foreign listings of covered supply chains.

A national story is reported through its West Texas implication first when one exists.

## PART C — SWEEP ROUTINE (category-based, not name-based)

The coverage unit is the **category**, not the previously studied company or deal. Named entities are entry points, never boundaries. Every cut sweeps for **new entrants, new deals, new litigants, and new instruments** in each category with the same priority as established names. Over-emphasis on previously covered items (any single credit complex, any single conversion deal, any single lawsuit) is a defect.

1. Sweep all 23 taxonomy domains per `grid-wire-coverage-taxonomy.md`. Sub-sector granularity is the floor.
2. Incremental rule: a domain with nothing new gets nothing. No padding, no restatement.
3. Search order: primary sources first (EDGAR + credit-agreement exhibits, EIA, RRC, TCEQ, PUCT/ERCOT dockets, FERC, NRC, GCD agendas, courts/PACER/re:SearchTX, county records, company IR, transcripts), then trade press for data points only, flagged.
4. Per-cut filing sweep: EDGAR full-text on the company universe + counterparty names + category keywords (powered land, site control, behind-the-meter, water rights, turbine slot), date-bounded to the incremental window; PUCT open projects touching large loads; ERCOT market notices; GCD agendas (Reeves, Middle Pecos, and adjacent districts); new docket filings across all trackers (Part D).
5. LRP counterparty names (Hanwha, Blackstone/QTS, Commerce Street, Cockrell/Belding, Fort Stockton Holdings/Riggs, Pacifico/GW Ranch, Microsoft Reeves, Longfellow/Poolside, Stargate Abilene, Matador/Fermi) swept every cut — as one input among the category sweep, not the frame.
6. Reeves–Pecos convergence deep dive in every edition.

## PART D — STANDING TRACKERS (maintained every cut, category-level)

### D1. Litigation tracker
Covers all litigation and contested administrative proceedings relating to: water rights and groundwater districts; land, surface, and eminent domain; power, utilities, ratepayer, and cost-causation; AI and data-center siting, zoning, and nuisance; environmental and air permitting; federal preemption and agency authority; energy contracts and force majeure; credit events and bankruptcy in the coverage universe. Fields per matter: case name, court/agency, docket number, parties, issue, current stage, next dated event, geographic tier (WTX/TX/US), thesis relevance. New matters added every cut; resolved matters closed with outcome and precedent read. No single case dominates; each is one row.

### D2. Deal ledger
Cumulative register of every transaction in the coverage universe: date, asset, location (county for TX), buyer, seller, advisors, price, structure, acreage, MW status, contract attachments, source. Each cut prints additions and revisions only, plus row count.

### D3. Credit register
Every AI/energy-infrastructure financing on record, per Part G. New facilities placed on the spread ladder in the same cut they print.

### D4. Regulatory docket tracker
Open rulemakings and proceedings across PUCT, ERCOT, RRC, TCEQ, FERC, NRC, DOE, and state commissions with large-load relevance. Fields: docket, body, subject, stage, next date, comment deadlines, geographic tier.

### D5. Physical-constraint tracker
Lead times and pricing for: gas turbines by frame class, HV transformers, switchgear, HBM, electrical steel, craft labor. Updated on any primary disclosure.

### D6. Standing calendar
Dated forward calendar rolled every cut: earnings, FOMC, EIA releases, regulatory deadlines, court dates, permit deadlines, in-service dates, covenant test dates, day-count clocks (Reeves GCD Sep 1 2026 and successors).

## PART E — COMPANY UNIVERSE

Names are the tracked floor; add any new public entrant to the relevant row on first material disclosure.

| # | Subsector | US listed | Foreign listed | Private / watch |
|---|---|---|---|---|
| 1 | Hyperscalers / cloud | MSFT, AMZN, META, GOOGL, ORCL, IBM, AAPL | SoftBank 9984, Alibaba, Tencent, Baidu | OpenAI, xAI, Anthropic |
| 2 | Neoclouds / GPU clouds | CRWV, NBIS, IREN, APLD | GDS, VNET | Crusoe, Lambda, Together, Fluidstack, Voltage Park, TensorWave, Vultr, SB Neo |
| 3 | GPUs / accelerators / CPU | NVDA, AMD, INTC, AVGO, MRVL, QCOM, ARM | — | Cerebras, Groq, SambaNova, Tenstorrent |
| 4 | Memory / HBM / substrates | MU, WDC, SNDK | SK Hynix, Samsung, Kioxia, Nanya, Ibiden, Shinko | — |
| 5 | Foundry / semicap / packaging | TSM, AMAT, LRCX, KLAC, GFS, AMKR, ONTO | ASML, UMC, SMIC, Tokyo Electron, ASE, Besi, Disco | — |
| 6 | Networking / optics | ANET, CSCO, ALAB, CRDO, COHR, LITE, FN, CIEN, GLW, MRVL, APH | — | — |
| 7 | AI systems / servers | DELL, HPE, SMCI | Lenovo, Hon Hai, Quanta, Wistron, Inventec, Gigabyte | — |
| 8 | Electrical equipment / DC power chain | ETN, VRT, HUBB, EMR, NVT, WCC, POWL, AZZ, GNRC, ROK, AYI | ABB, Schneider, Siemens, Legrand | — |
| 9 | Turbines / prime movers | GEV, CAT, CMI, BKR | Siemens Energy, Mitsubishi Heavy, Doosan Enerbility, Wärtsilä, Rolls-Royce | INNIO, ProEnergy, VoltaGrid, Mainspring |
| 10 | Utilities / IPPs | NEE, D, CEG, VST, NRG, TLN, SO, DUK, AEP, ETR, EXC, XEL, PEG, WEC, PPL, ED, EIX, PCG, CNP (Texas wires) | — | Calpine, Cogentrix, Tenaska |
| 11 | Nuclear / SMR / fuel cycle | OKLO, SMR, BWXT, LEU, CCJ, UEC, NXE, DNN, UUUU, NNE, LTBR, GEV (BWRX) | — | X-energy, TerraPower, Kairos, Natura, Radiant |
| 12 | Fuel cells / on-site gen | BE, PLUG, FCEL, GNRC, CMI | — | Mainspring, VoltaGrid |
| 13 | Permian E&P | FANG, PR, COP, XOM, CVX, DVN, CTRA, OXY, APA, EOG, MTDR, VTLE, SM, CRGY, OVV | — | Mewbourne, CrownQuest, Endeavor legacy |
| 14 | Oilfield services | HAL, SLB, BKR, PUMP, LBRT, WFRD, NBR, HP, PTEN, CHX, FTI, AESI | — | — |
| 15 | Midstream / LNG | KMI, ET, TRGP, MPLX, OKE, KNTK, WES, EPD, WMB, DTM, LNG, VG, NEXT, GLNG, AM, HESM | ENB, TRP | WhiteWater/WPC, Moss Lake |
| 16 | Land / royalty / water | TPL, LB, VNOM, STR, KRP, BSM, DMLP, WTTR, ARIS-legacy (WES), SD | — | PowerBridge, Deep Blue, Layne water assets |
| 17 | Miners / crypto-to-AI | WULF, HUT, CIFR, RIOT, MARA, GLXY, CLSK, BTDR, HIVE, BITF, WYFI | — | — |
| 18 | DC REITs / colo / developers | EQIX, DLR, DBRG, IRM (data centers) | NEXTDC, GDS, Keppel DC | QTS, Vantage, Switch, Aligned, CyrusOne, STACK, Compass, CloudHQ, EdgeConneX, DataBank, AirTrunk, DayOne, Prime DC |
| 19 | Storage / BESS | TSLA, FLNC, EOSE, STEM | CATL, LG Energy, Samsung SDI, Panasonic, Hithium | Form Energy, Base Power |
| 20 | Fiber / connectivity | GLW, LUMN, UNIT, CCOI, ADTN, CIEN | — | Zayo, FiberLight, Lightpath |
| 21 | EPC / electrical construction | PWR, MYR, EME, FIX, MTZ, IESC, PRIM, STRL, DY, FLR, J, ACM, GVA, TPC | — | Bechtel, Kiewit, Rosendin, Yates |
| 22 | Credit / alt managers / BDCs | BX, APO, KKR, ARES, OWL, CG, TPG, BN/BAM, ARCC, OBDC, BXSL, FSK, MAIN, HTGC, GBDC, BCSF | — | PIMCO, Golub, Sixth Street |
| 23 | Insurers (mandated IG buyers) | CRBG, FG, LNC, EQH, VOYA, MET, PRU, AIG, BHF, GL, UNM; APO/Athene, KKR/Global Atlantic | — | MassMutual, NY Life, TIAA, Guardian |
| 24 | Metals / materials | FCX, SCCO, NUE, STLD, X, CLF, AA, CENX, ATI, CRS, MP | Glencore, BHP, Rio | — |
| 25 | AI software demand bellwethers | PLTR, NOW, CRM, SNOW, DDOG, MDB, ORCL-apps, ADBE, WDAY | SAP | — (tracked as credit-stress and demand-durability signal only) |
| 26 | Defense / space compute | RKLB, ASTS, PL, LUNR, LMT, NOC, RTX | — | SpaceX, Anduril |

Sweep rule: rows 1–3, 9, 10, 13, 15, 16, 22 every cut; remainder on reporting events, deal events, or category-relevant news. Any name in any row is displaced by a more relevant new entrant without ceremony.

## PART F — COMPANY TRACKING (theme-based)

Per covered name on any reporting or deal event: infrastructure capex (totals, trajectory, compute vs land/shell/power mix, financing source per dollar); contracts and underlying agreements (tenor, take-or-pay, counterparty credit, escalators, termination, exclusivity); new deal terms (full term sheet + delta vs prior comparable); transcript analysis (named quotes, QoQ language diffs on power/land/water/turbines/lead times/concentration, constraint-mention counts, first-use phrases, Q&A over prepared remarks); presentation/analyst-day analysis (deck-before-filing metrics are data points); filing forensics (risk-factor verbatim diffs, commitments/guarantees quarterly, concentration, off-BS arrangements). Excluded: buybacks, dividends.

## PART G — CREDIT SECTION (full specification)

Category: all AI/energy-infrastructure credit, US-wide, West Texas–linked issuers prioritized. No single complex over-weighted; the tracked set expands to every material issuer.

### G1. Facility register (per instrument, standing surveillance)
Required data points: borrower and SPV structure; arrangers, agents, anchor lenders; facility size, drawn/undrawn; pricing (spread, floor, fixed-equivalent); rating and outlook; maturity and amortization; draw mechanics and milestones; security and lien priority; recourse and guarantees; LTC/advance rate; DSCR structure, first test date, subsequent test cadence; cure rights and expiration windows; default triggers (material-contract adverse events specifically); offtaker identity, tenor, and concentration; estimated interest burden run-rate; refinancing wall placement. Every new facility placed on the spread ladder in the same cut, delta vs the nearest prior comparable stated.

### G2. Spread ladder and market structure
IG vs HY bifurcation stated numerically on every update. HY/IG index spreads for DC and energy issuers. New-issue calendar: DDTLs, SPV bonds, ABS (data-center and GPU collateral), convertibles, PIPEs. ABS issuance volume and enhancement levels. Secondary marks on tracked paper when available; trade-press marks used, flagged as data points.

### G3. Covenant calendar
Standalone dated table every cut: instrument, test type, test date, cure window expiration, rating triggers, threshold values where disclosed.

### G4. Lender exposure matrix
Holder-by-holder exposure (managers, banks, insurers) built from disclosures only — 10-Ks/10-Qs, fund reports, Fed studies, NAIC filings. Never estimated.

### G5. System-level stress
Every cut, summary line; deep treatment on prints: BDC marks vs public loans, PIK income share, semi-liquid fund flows and gating (BCRED-class), direct-lending market size and manager concentration, default and recovery rates (competing series cited by name), bank exposure chains, insurer private-credit allocations, pension digital-infra exposure. AI as simultaneous borrower stress (software disruption — Row 25 watch) and asset origination.

### G6. Ratings surveillance
All agency actions across the full company universe, not AI-linked paper only. Methodology changes affecting data-center or GPU collateral treated as structural events.

## PART H — COMPS & DEALS

1. Comp ladders as standing series: $/acre by entitlement stage (raw → optioned → 58481-qualified → interconnection-secured → powered pad → energized; never averaged across stages); $/MW (queue vs energized, on-grid vs BTM); $/energized-MW and contract-value/contracted-MW (tenor-adjusted, derived); $/acre-foot by water class and district; turbine-slot premium by delivery year and frame class; EV/MW and EV/acre public marks; credit spread ladder (G2).
2. Case-study protocol: every major deal in any category gets a one-time full case study in the cut where it lands — parties, full economics, structure, ladder placement, precedent read, falsification condition. Subsequent comps cite by name. The case-study file is category-complete, not limited to previously studied transactions.
3. Hygiene: disclosed only; n/d excluded from averages and stated in tables; derived arithmetic shown and labeled; stage/geography/tenor mismatches flagged inline; every comp carries a named, dated, primary source.

## PART I — ANALYTICAL RULES

1. Crude and natural gas: separate channels, always.
2. Primary sources carry authority. Sell-side/trade press = data points only, flagged.
3. n/d for undisclosed; never estimate; derived labeled `derived`.
4. Named falsification condition on every major thesis.
5. Waha items cite negative-day count + egress schedule with capacities and in-service dates.
6. Water claims district-specific. No cross-district generalization.
7. Every financing event: full term sheet.
8. Every section tests physical-vs-financed. Every West Texas build flagged against the LRP map.

## PART J — STRUCTURE, VOICE, OUTPUT

1. Structure: Lead + I–XVII + scorecard + sources per repo/current WIP state. Each section: primary-source data points, named counterparties, term-sheet detail, an Angle, falsification conditions. Lead = defining development + physical-vs-financed read + day-count clocks. Deals Roundup = table. What to Watch = dated calendar only.
2. Voice: Munger/Burry/Sanders register. Declarative. No hedging, no adjectives-as-argument, no em-dashes, no smart quotes. Named on-record quotes only.
3. PDF: WeasyPrint; Jost instanced static weights 400/500/600/700 via fontTools; FontConfiguration threaded to both CSS() and write_pdf(); absolute file:// font paths; text.parse_math=False for matplotlib; navy palette; pdftoppm QA.
4. Emails: two plain-ASCII drafts (Mel, Mark), draft-only, never sent. Mark = Mel with first salutation swapped. Normalization: substitution dict → NFKD → ASCII encode/decode → assert ord<128 → verify `LC_ALL=C grep -cP "[^\x00-\x7F]"` = 0.
5. Deliver PDF + both drafts to outputs.

## PART K — SESSION CLOSE

1. Record cut outcomes per repo protocol (`WIP_LOG.md`); update `WIP_OPEN.md` `## Next chat`.
2. Nothing chat-specific cached in memory. State lives in the repo.

## PART L — PROHIBITED

Assuming Vol/baseline/repo state from memory. Full restarts on incremental cuts. Estimating undisclosed figures. Comps without primary sources. Averaging across entitlement stages. Sell-side framing as analysis. Conflating crude and gas. Cross-district water claims. Sending email drafts. Buyback/dividend coverage. Over-weighting any single previously covered deal, credit complex, or lawsuit at the expense of the category. LRP/ABH attribution on public content — public byline is "Andrea Himmel of LAND · The Grid Wire".

---

## ADDENDUM (repo-side, 2026-07-08): PDF format spec v2 — executive-scannable layout

Adopted with Vol. 18 full edition on operator direction ("highlighting, shading, colors; salient points and headlines quickly"). Standing for all future cuts, layered on Part J.3:

- **TOP LINE banner** (page 1): navy-filled box, gold header, 4-6 one-line findings with red (claim-layer stress) / green (input-layer confirmation) signal dots.
- **Stat band** (page 1): 5-6 large-number cells (price, yield, day-count, $/MW figures) with gold delta line.
- **Clock chips**: dated day-count chips under the stat band, rolled every cut.
- **Section kickers**: one-line gold salient headline under every section header.
- **Section headers**: navy-filled band, white text, gold left accent.
- **Box grammar**: navy-left/gray box = Angle reads; gold-left/cream box = named analytical sub-blocks (ladders, decision trees, previews); red-left/blush box = falsification conditions.
- **Signal coloring**: +x% / +bps green, -x% / -bps red inside all tables (regex post-process on td cells).
- Build: markdown -> post-process (TOPLINE/STATS/CLOCKS markers, KICKER lines, box classes, td colorizer) -> WeasyPrint. Markers live in the cut's source md; the build script strips them. QA: pdftotext for marker leakage plus pdftoppm page render.
- Reference implementation: the Vol. 18 build (`build_pdf18v2.py` pattern, recorded in WIP_LOG Vol. 18 entry).
