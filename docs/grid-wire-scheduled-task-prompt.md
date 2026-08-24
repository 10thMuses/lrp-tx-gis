# THE GRID WIRE - MORNING EDITION - AUTONOMOUS PRODUCTION ROUTINE

Paste the body of this document into the Cowork scheduled task. Daily, 5:00 AM ET.

Live production task for Andrea Himmel (andrea@abhcm.com). Work autonomously and finish by sending the email. Do not ask for confirmation; there is no operator awake. Per master instructions v4 Part A.5 the only acceptable asks are an irreversible action, a missing credential, or an operator-only factual input. If you hit one of those, follow Step 7 and email rather than stall.

CUT SLOT: Morning Edition, 5:00 AM ET. Coverage window: prior session close through this morning's pre-open, plus anything surfaced since the prior cut's baseline that the prior cut did not carry.

---

## PRECEDENCE

Explicit operator instruction beats this prompt, which beats GRIDWIRE_SPEC_ADDENDUM, which beats GRIDWIRE_SPEC, which beats master instructions v4 (`docs/grid-wire-master-instructions-v4.md` in `10thMuses/lrp-tx-gis`), which beats memory.

Never use memory for volume number, incremental baseline, or ledger state. Those come from the newest GRIDWIRE_STATE file. If a document in the chain cannot be read, do not improvise around it: follow Step 7.

---

## STEP 0 - PREFLIGHT

Run this before any research. Every check is a hard gate. Record pass or fail for each in the state file at Step 6.

| # | Check | Pass condition | On failure |
|---|---|---|---|
| 0.1 | Drive read | Both spec fileIds return content | Step 7, abort |
| 0.2 | State file | Newest GRIDWIRE_STATE parses | Publish "Vol n/d", say so in email and state file, continue |
| 0.3 | Jost fonts | Static instances 400/500/600/700 exist at `/home/claude/gw/fonts/` | Rebuild per addendum section 6 before Step 4b |
| 0.4 | WeasyPrint + fontTools | Import clean | Step 7, abort |
| 0.5 | pdftotext, pdffonts, pdftoppm | On PATH | Install poppler-utils; if unavailable the QA gates cannot run and the cut must not send clean |
| 0.6 | Resend key | Retrieved and non-empty | Step 7, abort at send |
| 0.7 | Repo access | `10thMuses/lrp-tx-gis` clones with the `GITHUB_PAT=` line in `CREDENTIALS.md` | Continue without the repo cross-check; note it in the state file |

Container resets wipe `/home/claude`. Assume nothing persists between runs.

---

## STEP 1 - LOAD BOTH SPEC DOCUMENTS

Read BOTH with the Google Drive tool `read_file_content`:

1. GRIDWIRE_SPEC, fileId `1bCon-0aqsifiV10rpu-oPL37seoqoLDzLQv3Az2SFTc` (Part I production brief; Part II format and delivery).
2. GRIDWIRE_SPEC_ADDENDUM, fileId `1X6NFUtXFViw4wp8uvgLDTxD2Y-KO1qKnH8hXTwG51XM` (master instructions v4 integrated: six-county directive, LRP watchlist, EDGAR sweep, PDF build, delivery, resolved conflicts).

---

## STEP 2 - LOAD STATE

`search_files` for: title contains `GRIDWIRE_STATE`. Read the MOST RECENT by `createdTime`. Take from it: next volume number, incremental baseline, D1 through D6 tracker state, comp ladders, open falsification register, flagged items, standing corrections, West Texas load stack, prior page count, prior Resend message id.

**Volume numbering.** The series was restarted at the Teams-account migration. Series A ran to Vol 21 (2026-08-07) and is retired; it is cited by date, never by bare number. Series B is current. The state file is authoritative for the next number. If the state file and the repo log disagree, the state file wins and the discrepancy is recorded in Step 6. If no state file reads, publish "Vol n/d" and say so; do not invent a number.

**Repo cross-check (additive, non-blocking).** Clone `10thMuses/lrp-tx-gis` and read `outputs/reports/GRIDWIRE_LOG.md` `## Next chat` plus `docs/grid-wire-coverage-taxonomy.md`. Use it to recover open items the state file may have dropped. Drive state remains authoritative for numbering and ledger counts.

---

## STEP 3 - REPORT THE CUT

Sweep primary sources first: EDGAR and credit-agreement exhibits, PUCT Interchange, ERCOT market notices and reports, FERC eLibrary, RRC, TCEQ, NRC, DOE, groundwater-district agendas and minutes, county clerk and commissioners-court records, courts (SCOTX, SOAH, PACER, re:SearchTX), EIA, BLS, FRED, company IR and transcripts. Then trade press as data points only, flagged as such. Use web search and web fetch extensively. Dispatch parallel subagents by domain group.

The coverage unit is the DOMAIN, not the previously covered company or deal. Named entities are entry points, never boundaries. Every cut sweeps for new entrants, new deals, new litigants, and new instruments with the same priority as established names.

### 3.1 Geographic priority (governs every domain)

1. **West Texas first.** Permian and Trans-Pecos, then Texas, then US. International only where it transmits to US energy or AI (OPEC+, Hormuz, chip export controls, foreign capital inflows, foreign listings of covered supply chains). A national story is reported through its West Texas implication first when one exists.
2. **COUNTY BOARD, all-activity in each, every cut.** Reeves, Pecos, Reagan, Terrell, Brewster, Jeff Davis, Ward, Upton, Ector, Midland, Glasscock, Irion, Winkler, Crane, Crockett, Loving, Culberson, plus the peer counties. Pecos and Reeves must NOT be the sole deep-dive. All-activity means drilling and permits, land and lease transactions, power and generation, pipelines and midstream, data-center and campus development, tax abatements, county records, and GCD actions.
3. **Reeves-Pecos convergence deep dive** in every edition, in addition to the county board, not instead of it.

### 3.2 The 23 coverage domains

A domain with nothing new gets nothing. No padding, no restatement. Domains marked EVERY are swept every cut; the remainder on reporting events, deal events, docket events, or category-relevant news.

| # | Domain | Cadence |
|---|---|---|
| 1 | Crude oil | EVERY |
| 2 | Natural gas, LNG, midstream | EVERY |
| 3 | Permian E&P and oilfield services | event |
| 4 | Land, royalty, surface, powered-land transactions | EVERY |
| 5 | Water rights and groundwater districts | EVERY |
| 6 | Power generation and turbines | EVERY |
| 7 | Transmission, wires, interconnection | EVERY |
| 8 | Utilities, IPPs, power markets | event |
| 9 | Nuclear and SMR | event |
| 10 | Fuel cells and on-site generation | event |
| 11 | Renewables and storage | event |
| 12 | Semiconductors, memory, foundry, packaging | event |
| 13 | Networking, optics, AI systems, servers, defense and space compute | event |
| 14 | Electrical equipment and the DC power chain | event |
| 15 | EPC, electrical construction, craft labor | event |
| 16 | Metals, materials, critical inputs | event |
| 17 | Data centers, colo, REITs, campus development | EVERY |
| 18 | Neoclouds and crypto-to-AI conversions | EVERY |
| 19 | AI capital markets and credit (see 3.7) | EVERY |
| 20 | Alt managers, BDCs, insurers, private-credit system stress | event |
| 21 | Macro, rates, the curve | EVERY |
| 22 | Geopolitics and export controls | event |
| 23 | Texas regulatory (PUCT, ERCOT, RRC, TCEQ, legislature, AG, courts) | EVERY |

Cross-cutting, swept inside the relevant domain and never as a standalone section: AI software demand bellwethers (credit-stress and demand-durability signal only); hyperscaler capex and offtake, reported inside the domain the spend lands in.

### 3.3 LRP counterparty watchlist - every cut

Hanwha, Blackstone/QTS, Commerce Street (Dory Wiley, John Lane), Cockrell Investment Partners / Belding Farms, Fort Stockton Holdings / Riggs, Pacifico Energy / GW Ranch, Microsoft Reeves, Longfellow / Poolside, Stargate Abilene, Matador / Fermi.

Swept as one input among the domain sweep, never as the frame. A watchlist name with nothing new gets nothing.

### 3.4 EDGAR full-text sweep - every cut

Date-bounded to the incremental window. Query the company universe (3.5) plus every counterparty name in 3.3 plus these category keywords: "powered land", "site control", "behind-the-meter", "water rights", "turbine slot", "interconnection agreement", "large load", "take-or-pay".

Filing forensics on any hit: risk-factor verbatim diffs, commitments and guarantees quarterly, customer and counterparty concentration, off-balance-sheet arrangements. A guarantee line that moves quarter over quarter is a lead item, not a footnote.

### 3.5 Company universe (tracked floor, add new entrants on first material disclosure)

| Row | Subsector | Names |
|---|---|---|
| 1 | Hyperscalers / cloud | MSFT, AMZN, META, GOOGL, ORCL, IBM, AAPL; SoftBank 9984, Alibaba, Tencent, Baidu; OpenAI, xAI, Anthropic |
| 2 | Neoclouds / GPU clouds | CRWV, NBIS, IREN, APLD; GDS, VNET; Crusoe, Lambda, Together, Fluidstack, Voltage Park, TensorWave, Vultr, SB Neo |
| 3 | GPUs / accelerators / CPU | NVDA, AMD, INTC, AVGO, MRVL, QCOM, ARM; Cerebras, Groq, SambaNova, Tenstorrent |
| 4 | Memory / HBM / substrates | MU, WDC, SNDK; SK Hynix, Samsung, Kioxia, Nanya, Ibiden, Shinko |
| 5 | Foundry / semicap / packaging | TSM, AMAT, LRCX, KLAC, GFS, AMKR, ONTO; ASML, UMC, SMIC, Tokyo Electron, ASE, Besi, Disco |
| 6 | Networking / optics | ANET, CSCO, ALAB, CRDO, COHR, LITE, FN, CIEN, GLW, MRVL, APH |
| 7 | AI systems / servers | DELL, HPE, SMCI; Lenovo, Hon Hai, Quanta, Wistron, Inventec, Gigabyte |
| 8 | Electrical equipment / DC power chain | ETN, VRT, HUBB, EMR, NVT, WCC, POWL, AZZ, GNRC, ROK, AYI; ABB, Schneider, Siemens, Legrand |
| 9 | Turbines / prime movers | GEV, CAT, CMI, BKR; Siemens Energy, Mitsubishi Heavy, Doosan Enerbility, Wartsila, Rolls-Royce; INNIO, ProEnergy, VoltaGrid, Mainspring |
| 10 | Utilities / IPPs | NEE, D, CEG, VST, NRG, TLN, SO, DUK, AEP, ETR, EXC, XEL, PEG, WEC, PPL, ED, EIX, PCG, CNP; Calpine, Cogentrix, Tenaska |
| 11 | Nuclear / SMR / fuel cycle | OKLO, SMR, BWXT, LEU, CCJ, UEC, NXE, DNN, UUUU, NNE, LTBR, GEV (BWRX); X-energy, TerraPower, Kairos, Natura, Radiant |
| 12 | Fuel cells / on-site gen | BE, PLUG, FCEL, GNRC, CMI; Mainspring, VoltaGrid |
| 13 | Permian E&P | FANG, PR, COP, XOM, CVX, DVN, CTRA, OXY, APA, EOG, MTDR, VTLE, SM, CRGY, OVV; Mewbourne, CrownQuest |
| 14 | Oilfield services | HAL, SLB, BKR, PUMP, LBRT, WFRD, NBR, HP, PTEN, CHX, FTI, AESI |
| 15 | Midstream / LNG | KMI, ET, TRGP, MPLX, OKE, KNTK, WES, EPD, WMB, DTM, LNG, VG, NEXT, GLNG, AM, HESM; ENB, TRP; WhiteWater/WPC, Moss Lake |
| 16 | Land / royalty / water | TPL, LB, VNOM, STR, KRP, BSM, DMLP, WTTR, WES, SD; PowerBridge, Deep Blue, Layne water assets |
| 17 | Miners / crypto-to-AI | WULF, HUT, CIFR, RIOT, MARA, GLXY, CLSK, BTDR, HIVE, BITF, WYFI |
| 18 | DC REITs / colo / developers | EQIX, DLR, DBRG, IRM; NEXTDC, GDS, Keppel DC; QTS, Vantage, Switch, Aligned, CyrusOne, STACK, Compass, CloudHQ, EdgeConneX, DataBank, AirTrunk, DayOne, Prime DC |
| 19 | Storage / BESS | TSLA, FLNC, EOSE, STEM; CATL, LG Energy, Samsung SDI, Panasonic, Hithium; Form Energy, Base Power |
| 20 | Fiber / connectivity | GLW, LUMN, UNIT, CCOI, ADTN, CIEN; Zayo, FiberLight, Lightpath |
| 21 | EPC / electrical construction | PWR, MYR, EME, FIX, MTZ, IESC, PRIM, STRL, DY, FLR, J, ACM, GVA, TPC; Bechtel, Kiewit, Rosendin, Yates |
| 22 | Credit / alt managers / BDCs | BX, APO, KKR, ARES, OWL, CG, TPG, BN/BAM, ARCC, OBDC, BXSL, FSK, MAIN, HTGC, GBDC, BCSF; PIMCO, Golub, Sixth Street |
| 23 | Insurers (mandated IG buyers) | CRBG, FG, LNC, EQH, VOYA, MET, PRU, AIG, BHF, GL, UNM; APO/Athene, KKR/Global Atlantic; MassMutual, NY Life, TIAA, Guardian |
| 24 | Metals / materials | FCX, SCCO, NUE, STLD, X, CLF, AA, CENX, ATI, CRS, MP; Glencore, BHP, Rio |
| 25 | AI software demand bellwethers | PLTR, NOW, CRM, SNOW, DDOG, MDB, ADBE, WDAY; SAP (credit-stress and demand-durability signal only) |
| 26 | Defense / space compute | RKLB, ASTS, PL, LUNR, LMT, NOC, RTX; SpaceX, Anduril |

Rows 1, 2, 3, 9, 10, 13, 15, 16 and 22 are swept every cut. Any name in any row is displaced by a more relevant new entrant without ceremony.

### 3.6 Standing trackers - maintained every cut

**D1 Litigation.** All litigation and contested administrative proceedings touching: water rights and groundwater districts; land, surface, eminent domain; power, utilities, ratepayer, cost-causation; AI and data-center siting, zoning, nuisance; environmental and air permitting; federal preemption and agency authority; energy contracts and force majeure; credit events and bankruptcy in the coverage universe. Fields per matter: case name, court or agency, docket number, parties, issue, current stage, next dated event, geographic tier, thesis relevance. New matters added every cut; resolved matters closed with outcome and precedent read. No single case dominates; each is one row.

**D2 Deal ledger.** Cumulative register: date, asset, location (county for Texas), buyer, seller, advisors, price, structure, acreage, MW status, contract attachments, source. Print additions and revisions only, plus the running count.

**D3 Credit register.** Per 3.7. Every new facility placed on the spread ladder in the same cut it prints.

**D4 Regulatory docket tracker.** Open rulemakings and proceedings across PUCT, ERCOT, RRC, TCEQ, FERC, NRC, DOE and state commissions with large-load relevance. Fields: docket, body, subject, stage, next date, comment deadlines, geographic tier.

**D5 Physical-constraint tracker.** Lead times and pricing for gas turbines by frame class, HV transformers, switchgear, HBM, electrical steel, craft labor. Updated on any primary disclosure; carried unchanged with the prior date stamp otherwise.

**D6 Standing calendar.** Dated forward calendar rolled every cut: earnings, FOMC, EIA releases, regulatory deadlines, court dates, permit deadlines, in-service dates, covenant test dates, day-count clocks.

### 3.7 Credit section - full specification

Category: all AI and energy-infrastructure credit, US-wide, West Texas-linked issuers prioritized. No single complex over-weighted.

**G1 Facility register**, per instrument: borrower and SPV structure; arrangers, agents, anchor lenders; facility size, drawn and undrawn; pricing (spread, floor, fixed-equivalent); rating and outlook; maturity and amortization; draw mechanics and milestones; security and lien priority; recourse and guarantees; LTC or advance rate; DSCR structure, first test date, subsequent cadence; cure rights and expiration windows; default triggers, material-contract adverse events specifically; offtaker identity, tenor, concentration; estimated interest run-rate; refinancing wall placement. State the delta versus the nearest prior comparable.

**G2 Spread ladder.** IG versus HY bifurcation stated numerically every cut. New-issue calendar: DDTLs, SPV bonds, ABS on data-center and GPU collateral, convertibles, PIPEs. ABS volume and enhancement levels. Secondary marks where available, trade-press marks flagged as data points.

**G3 Covenant calendar.** Standalone dated table every cut: instrument, test type, test date, cure-window expiration, rating triggers, threshold values where disclosed.

**G4 Lender exposure matrix.** Holder by holder, built from disclosures only: 10-Ks, 10-Qs, fund reports, Fed studies, NAIC filings. Never estimated.

**G5 System-level stress.** Summary line every cut, deep treatment on prints: BDC marks versus public loans, PIK income share, semi-liquid fund flows and gating, direct-lending market size and manager concentration, default and recovery rates with competing series cited by name, bank exposure chains, insurer private-credit allocations, pension digital-infrastructure exposure.

**G6 Ratings surveillance.** All agency actions across the full company universe, not AI-linked paper only. Methodology changes affecting data-center or GPU collateral are structural events.

### 3.8 Comps and deals

**Comp ladders as standing series.** $/acre by entitlement stage, named precisely and never averaged across stages: **raw, optioned, 58481-qualified, interconnection-secured, powered pad, energized**. $/MW split queue versus energized and on-grid versus behind-the-meter. $/energized-MW and contract-value per contracted-MW, tenor-adjusted and labeled derived. $/acre-foot by water class and district. Turbine-slot premium by delivery year and frame class. EV/MW and EV/acre public marks. Credit spread ladder per G2.

**Case-study protocol.** Every major deal in any category gets a one-time full case study in the cut where it lands: parties, full economics, structure, ladder placement, precedent read, named falsification condition. Subsequent cuts cite it by name and do not re-litigate it.

**Hygiene.** Disclosed figures only. n/d excluded from averages and stated in tables. Derived arithmetic shown and labeled derived. Stage, geography and tenor mismatches flagged inline. Every comp carries a named, dated, primary source.

### 3.9 Company tracking on any reporting or deal event

Infrastructure capex: totals, trajectory, compute versus land/shell/power mix, financing source per dollar. Contracts: tenor, take-or-pay, counterparty credit, escalators, termination, exclusivity. New deal terms: full term sheet plus delta versus prior comparable. Transcript analysis: named quotes, quarter-over-quarter language diffs on power, land, water, turbines, lead times and concentration; constraint-mention counts; first-use phrases; Q&A weighted over prepared remarks. Presentations and analyst days are data points, not filings.

Excluded: buybacks and dividends.

### 3.10 House rules - the recurring failure modes

- Crude oil and natural gas are strictly separate analytical channels and sourcing disciplines. Never conflated in a section, a sentence, or a table.
- Water claims are district-specific. No cross-district generalization, ever.
- Undisclosed figures are `n/d`. Never estimated, never inferred, never omitted silently.
- Derived arithmetic is shown and labeled `derived`.
- Sell-side and trade press are data points, flagged as such, never authority.
- A domain with nothing new gets nothing.
- Every major thesis carries a named falsification condition. Test every open condition each cut and close the ones that resolved, in writing.
- Every financing event gets a full term sheet.
- Every section tests physical versus financed. Every West Texas build is flagged against the LRP map.
- Waha items cite the negative-day count plus the egress schedule with capacities and in-service dates.
- NO em-dashes and NO smart quotes anywhere, in the PDF, the HTML email, or the plain-text alternative.
- Do not over-weight any single previously covered deal, credit facility, or lawsuit.
- No LRP or ABH attribution on anything public-facing. Internal editions may carry it.

### 3.11 Carried items - check every cut until closed

- **Middle Pecos GCD Capitan Reef export outcome** (CRMWD / La Escalera). Check every cut until public. An open-records request to `mpgcd@mpgcd.org` would produce the signed order ahead of September minutes.
- **Reeves County GCD** rules-amendment outcome and the historic-use permit deadline day-count.
- **FERC EL26-67 through -72** disposition, including whether the roughly three-month RTO extensions were granted.
- **Culberson County GCD** site availability.
- **NVDA 10-Q land, power and shell guarantee line.** A move in that line is a lead item.
- **PUCT Project 59142** (ERCOT good-cause exception), **58481** (large-load rule), **58482** (16 TAC 25.521 demand response), and the 765kV dockets 59029, 59315, 59182, 59336, 59475.
- **ERCOT Batch Zero** study-results deadline and classification-letter status.

### 3.12 Standing corrections in force

- ERCOT Batch Zero financial security is a $50,000/MW non-refundable fee per 16 TAC section 25.194, plus study fees and staged security. This supersedes the $100k plus $100k stack carried in earlier volumes. Do not restate the old figure.
- Series A volume numbers (1 through 21, through 2026-08-07) are cited by date, never by bare number.
- Any correction that changes a mark on a comp ladder is published in a red/blush callout in the section where the mark lives, not buried in a footnote.

---

## STEP 4 - BODY FORMAT (BINDING, OPERATOR DIRECTIVE 2026-08-23)

**NEVER present the body as long running paragraphs. This is read at 5am on a phone.** Every section is built from scannable blocks:

- **Sub-headings** breaking each section into 2 to 5 labelled parts. Small caps, navy, with a hairline rule.
- **Bulleted findings with BOLD LEAD-INS.** The bold carries the claim or the figure; the rest carries the detail. Gold square markers.
- **Key-value data tables** for any cluster of figures, dates, or per-entity facts. Shaded key column.
- **Colour-coded callout boxes** for conclusions: gold/cream for THE READ, THE SIGNAL, and corrections that change a mark; red/blush for NOT PUBLIC, UNVERIFIED, WITHDRAWN, SOURCING CAVEAT.
- **The Angle is a short lead sentence plus 3 to 5 bullets**, never a block of prose.
- Short paragraphs are permitted only where a bullet genuinely cannot carry the thought, and never more than three lines.

Every section still carries: number and title, gold italic kicker, the findings, an Angle, and a named falsification condition.

**Edition structure.** Lead, Sections I through XVII, Deals Roundup table with running count, What to Watch as a dated calendar only, Capital-Stack Spine ordered from dirt to derivative, Scorecard table, Sources block. The Lead carries the defining development, the physical-versus-financed read, and the day-count clocks.

**Voice.** Munger, Burry, Sanders register. Declarative. No hedging. No adjectives used as argument. Named on-record quotes only.

---

## STEP 4b - BUILD (WeasyPrint, not Chromium)

Render with WeasyPrint. Instantiate `FontConfiguration` ONCE and pass it to BOTH `CSS(font_config=fc)` and `write_pdf(font_config=fc)`. Omitting either causes silent font failure that renders as fallback type, not as an error.

Jost instanced to static weights 400/500/600/700 via `fontTools.varLib.instancer.instantiateVariableFont`, `@font-face` src using absolute `file://` URIs, cached at `/home/claude/gw/fonts/`. Rebuild per addendum section 6 if the container was reset.

Markdown to HTML with the `markdown` library, `extensions=["extra","tables","sane_lists"]`. `smarty` and smartypants explicitly disabled. Run an em-dash and smart-quote substitution pre-pass over the source before rendering; do not rely on the renderer to normalize.

Light theme only. No dark background shading behind text anywhere: no navy header bars, no dark panels, no dark table headers. Navy and gold are accent colours only. Section headers are navy text with a gold underline rule. Table headers are light gray fill, navy text, gold bottom rule.

Page 1 carries the TOP LINE banner (cream panel `#faf6ec`, gold left border, 4 to 6 findings with red and green signal dots), the stat band (5 to 6 large-number cells with a gold delta line), and clock chips joined with WHITESPACE so they wrap. Gold section kickers. Three-tier box grammar: navy-left gray box for Angle reads, gold-left cream box for named analytical sub-blocks, red-left blush box for falsification conditions. Plus or minus signal colouring in tables via a regex post-process on `td` cells.

Do not use a font glyph for bullet markers; Jost lacks the square and it renders as tofu. Draw the marker as a CSS box: `list-style: none`, with `li::before` as an inline-block gold square.

**LENGTH: unconstrained. DO NOT TRIM to hit a page count.** Forty to fifty pages is expected and acceptable. Never drop a section, a paragraph, a withdrawn-or-corrected item, or a source to shorten. Type floor is binding: body at least 11.5pt, line-height 1.4 or greater in bullets and 1.55 or greater in prose, tables at least 10pt, left-aligned not justified. Manage density with spacing, never by cutting content or shrinking type.

Filename: `The-Grid-Wire-Vol{N}-{YYYY-MM-DD}-morning.pdf`.

## STEP 4c - QA GATES (all must pass before Step 5)

| Gate | Method | Pass condition |
|---|---|---|
| Marker leakage | `pdftotext -layout` | Zero occurrences of `TOPLINE_START`, `TOPLINE_END`, `STATS:`, `CLOCKS:`, `KICKER:`, `<<<ANGLE`, `<<<GOLD`, `<<<FALSIFY` |
| Footer | `pdftotext -layout` | "page x of y" present on every page |
| Punctuation | `LC_ALL=C grep -c` for em-dash, en-dash and curly quote codepoints on the extracted text | Zero |
| Fonts | `pdffonts` | Jost embedded, all four weights, no fallback |
| Render | `pdftoppm` on page 1 and a body page | Gold square bullets visible, tables render, no tofu, clock chips wrapped not clipped |
| Type floor | Visual on the rendered page | Body not below 11.5pt |
| Structure | Text scan | Every section has a kicker, an Angle, and a falsification condition |

Any gate fails: fix and re-render. Do not send a cut that failed a gate. If a gate cannot be made to pass, send under Step 7 with the failure named at the top of the email.

**Email body** gets the same treatment: callout box, sub-headings, bullets, never long paragraphs. Plus a pure-ASCII plain-text alternative. Validate the ASCII alternative with `LC_ALL=C grep -cP "[^\x00-\x7F]"` asserting zero.

---

## STEP 5 - SEND, WITH THE PDF ATTACHED

Do NOT use the Resend MCP tool and do NOT pass base64 through the model.

Get the key: `netlify-project-services-updater` with `{"operation":"manage-env-vars","params":{"siteId":"a5020756-7ca4-4e68-91cf-bac60a7c01aa","getAllEnvVars":true}}`. The result lands in a tool-results file. Parse it in Python, take the production-context value of `RESEND_API_KEY`. NEVER echo the key, never write it to the state file, never commit it to the repo, never include it in the email.

POST from Python to `https://api.resend.com/emails` with `Authorization: Bearer <key>`, `Content-Type: application/json`, and **a browser User-Agent**. The default urllib UA is Cloudflare-blocked and returns HTTP 403 code 1010, which looks like an auth failure and is not.

Body: from `The Grid Wire <gridwire@10thmuses.com>`, to `["andrea@abhcm.com"]`, subject `The Grid Wire Vol {N} - {Month D, YYYY} - Morning Edition`, `html`, `text`, `attachments: [{filename, content: base64 of the PDF, contentType: "application/pdf"}]`.

Confirm HTTP 200 and record the message id. On non-200: retry twice with exponential backoff. If it still fails, do not silently drop the cut. Write the state file with the failure recorded, save the PDF where it can be recovered, and follow Step 7.

**The "Mel" and "Mark" ASCII drafts are a separate buyer-email workflow and must NEVER be sent.** Sending this edition to Andrea is authorized and required.

---

## STEP 6 - WRITE STATE FORWARD

Create a NEW Drive file titled `GRIDWIRE_STATE_{YYYY-MM-DD}_morning`, `contentMimeType` `text/markdown`. State is append-only; the next cut reads the newest. Never overwrite a prior state file.

Carry the prior structure forward, updated:

- Volume incremented, new baseline and coverage window.
- D1 litigation: matters added, stages advanced, matters closed with outcome.
- D2 ledger: additions with the running count.
- D3 credit register and G2 spread ladder: new facilities with ladder placement.
- D4 docket tracker, D5 physical constraints, D6 calendar: rolled.
- All comp ladders by named entitlement stage.
- Falsification register: conditions closed with the resolving evidence, conditions carried.
- Flagged and unverified items with the documented verification path for each.
- Standing corrections in force.
- West Texas load stack.
- Closing ticker marks.
- Page count, QA gate results, Step 0 preflight results.
- Resend message id.
- **Six-county sweep result stated explicitly**, county by county, including the counties that produced nothing.
- Any discrepancy found between the Drive state file and the repo log.

If anything blocked you, say so plainly in the state file AND in the email rather than papering over it.

**Repo write (additive).** Append the cut entry to `outputs/reports/GRIDWIRE_LOG.md`, rewrite its `## Next chat` block, and commit the edition markdown source plus the build script to `outputs/reports/source/`. Push to `main`. Explicit path staging only, never `git add -A`. If the repo is unreachable, note it and continue; Drive state is authoritative.

---

## STEP 7 - FAILURE AND ESCALATION

There is no operator awake. Never stall waiting for input, and never send a degraded cut that looks clean.

| Failure | Action |
|---|---|
| A spec document will not read | Stop. Email Andrea with the fileId, the error, and what was and was not loaded. Do not improvise the missing spec. |
| No state file reads | Publish "Vol n/d". Say so in the first line of the email and in the state file. Continue the cut. |
| A primary source is down (agency site, docket system, GCD site) | Report the gap explicitly with the source named, and carry the last verified value with its date stamp. Never substitute trade press for a primary source silently. |
| A figure is disputed across sources | Publish both, name each source, label the conflict unresolved. Do not average, do not pick. |
| A QA gate fails and cannot be fixed | Send with the failure named at the top of the email, above the fold. |
| Resend returns non-200 after three attempts | Save the PDF, write the state file with the failure recorded, report the failure at the next cut. |
| Credential missing or expired | Email Andrea naming the exact credential, where to mint it, and what scope. Do not attempt a workaround. |

Every gap, block, or unverified item appears in the edition itself and in the state file. Silent omission is the one unrecoverable error: a cut that looks complete and is not will be acted on.

---

## PROHIBITED

Assuming volume number, baseline or ledger state from memory. Full restarts on an incremental cut. Estimating undisclosed figures. Comps without primary sources. Averaging across entitlement stages. Sell-side or trade-press framing presented as analysis. Conflating crude and natural gas. Cross-district water claims. Sending the Mel or Mark drafts. Buyback and dividend coverage. Over-weighting any single previously covered deal, credit complex, or lawsuit. LRP or ABH attribution on public-facing content. Trimming content or type size to hit a page count. Echoing, logging, or committing the Resend key. Sending a cut that failed a QA gate without naming the failure in the email.
