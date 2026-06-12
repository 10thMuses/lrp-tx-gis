# Pacifico Energy — GW Ranch (Pecos County, TX) — Diligence Memo

**Date:** June 12, 2026
**Prepared for:** Andrea Himmel, Land Resource Partners
**Subject:** GW Ranch power + data center campus, Pecos County — financing, structure, land tenure, status, risks, differentiators
**Method:** Five parallel research tracks (~70 web sources, English + Japanese), cross-corroborated. Direct fetches of TCEQ, SEC EDGAR, Pecos CAD, and county records were blocked from this environment; those gaps are flagged. Every load-bearing claim is cited; developer claims are labeled as such.

---

## TL;DR

GW Ranch is the largest fully air-permitted power-for-AI campus in the US — 7.65 GW gas + 1.8 GW BESS + 750 MWac solar, fully off-grid (zero ERCOT/SB6/FERC exposure), on 8,000+ acres essentially on top of the Waha hub. The permit position, regulatory insulation, and gas logistics are genuinely best-in-class. But as of June 2026, **every commercial load-bearing element is undisclosed and unverified**: no named tenant, no named turbine OEM, no announced project financing, no confirmed groundbreaking, and land tenure (fee vs. option/lease) cannot be confirmed from public sources. Forbes pegs the capital need at ~$12B, and Pacifico's largest publicized US raise to date is ~$93M. Until a turbine OEM, a project-finance close, or a creditworthy anchor lease lands, GW Ranch is an option on the Permian power thesis, not an executing project. The nearest analogs for permit-rich/tenant-poor off-grid campuses — Fermi (-80%+ post-IPO, class actions) and Poolside/CoreWeave Horizon in the same county (anchor lease terminated March 2026) — show exactly where this model breaks: tenants and capital, not permits or gas.

---

## 1. Project structure

| Element | Detail | Source |
|---|---|---|
| Generation | 7.65 GW gas turbines (mix of small + large frames) + 1.8 GW BESS + 750 MWac solar | TCEQ permit coverage: [DCD Jan 2026](https://www.datacenterdynamics.com/en/news/pacifico-secures-765gw-air-permit-for-gw-ranch-project-in-west-texas/), [Turbomachinery Mag](https://www.turbomachinerymag.com/view/pacifico-energy-obtains-air-permit-for-gw-ranch-project-in-texas) |
| Grid status | Fully islanded private grid, "completely unconnected to ERCOT" — deliberate bypass of interconnection queue and PUCT/SB6 | [Power Engineering Aug 2025](https://www.power-eng.com/onsite-power/pacifico-energy-plans-5-gw-off-grid-facility-in-texas-for-hyperscale-data-centers/), [EnergyTech](https://www.energytech.com/data-center-power/article/55311675/pacifico-unveils-5-gw-off-grid-texas-power-for-data-centers) |
| Site | 8,000+ acres (Forbes: 8,400), Hwy 18 ~17 mi north of Fort Stockton | [TCEQ notice 181033](https://www.tceq.texas.gov/downloads/permitting/air/bilingual/pending-permit-notices/181033-pls-english.pdf), [Big Bend Sentinel Feb 4, 2026](https://bigbendsentinel.com/2026/02/04/massive-ai-data-center-coming-to-pecos-county/), [KCBD Feb 1, 2026](https://www.kcbd.com/2026/02/01/texas-approves-largest-permitted-data-center-campus-us/) |
| Gas | Multiple laterals incl. dedicated 15-mile, 1 Bcf/d pipeline to Waha; full-build burn ~1–2 Bcf/d (4–7% of 2025 Permian output) | [Businesswire Jan 26, 2026](https://www.businesswire.com/news/home/20260126236053/en/Pacifico-Energy-Secures-7.65-GW-Power-Generation-Permit-for-GW-Ranch-Project), [Texas Tribune Feb 2, 2026](https://www.texastribune.org/2026/02/02/texas-permian-basin-power-plant-project-data-centers/) |
| Business model | "Bring-your-own-power" / powered campus: Pacifico builds generation + private utility grid, co-locates customer data centers behind the fence. Lease vs. build-to-suit mechanics undisclosed. | [RCR Tech](https://rcrtech.com/ai-infrastructure/7-65-gw-ranch-is-biggest-byop-project-in-u-s/), Franklin quotes in Jan 2026 PR |
| Entities | Project SPV: **Pacifico GW LLC** (TCEQ applicant; same San Juan Capistrano address as parent). TCEQ regulated entity RN112259775, notice 181033. Parent: Pacifico Energy Group (private, founder-led). | [TCEQ pending permit notice](https://www.tceq.texas.gov/downloads/permitting/air/bilingual/pending-permit-notices/181033-napd-english.pdf) |
| Phasing | First power Q1/H1 2027 → 1 GW 2028 → 5+ GW by 2031 | Jan 2026 PR |
| Water | Developer claims "no major external water sources" — air-cooled, with combustion water recovery feeding DC cooling (marketing claim, mechanism unverified) | [Big Bend Sentinel](https://bigbendsentinel.com/2026/02/04/massive-ai-data-center-coming-to-pecos-county/) (VP Constantyn Gieskes quote) |
| Fiber | No disclosed provider or route | — |

Note the small/large turbine mix implies aeroderivative or recip bridging for the first GW with frame machines later — a common 2025-vintage structure for hitting an early first-power date while frame slots are scarce.

## 2. Company and project financing

**Company.** Pacifico Energy Group: privately held holding company, HQ San Juan Capistrano, CA; founded 2009 by Nate (William) Franklin (UCLA Anderson MBA '08; ex-Edison Mission, ex-BP Solar director of solar development). Built its base as Japan's largest utility-scale solar developer via Pacifico Energy K.K. (Tokyo, est. 2012): 1,750+ MW developed, claims $4–5B+ in cumulative equity/debt raised. The capital model has been **develop → sell down → recycle**:

- GE Energy Financial Services equity in early Japan solar (Hosoe, Kumenan, Setouchi Kirei — the latter ~$1.1B with $867M non-recourse syndicate loan) ([GE](https://www.ge.com/news/press-releases/ge-energy-financial-services-invests-japans-renewable-energy-power-market), [Recharge](https://www.rechargenews.com/solar/870405/in-depth-ge-energy-financial-services-breaks-down-japan-barriers))
- $141M solar fund (2018) and ¥29B (~$264M) Fund II (2019, Goldman Sachs Japan co-placement) buying stakes in its own operating plants ([Businesswire Dec 2019](https://www.businesswire.com/news/home/20191201005231/en/))
- SSE Renewables paid ~$208M for 80% of the Japan offshore wind platform (May 2021) ([CityAM](https://www.cityam.com/sse-renewables-jumps-into-japanese-offshore-wind-with-208m-stake/))
- **Bank of America was running a sale of the entire Pacifico Energy K.K. platform at $1B+ as of Oct 2024** — first-round bids due end-2024, SSE JV carved out. **No closing or buyer has been publicly reported as of June 2026.** This is the single biggest determinant of Pacifico's equity firepower for GW Ranch. ([Infralogic Oct 2024](https://ionanalytics.com/insights/infralogic/pacifico-energy-selling-japanese-solar-platform/))
- US distributed arm (Pacifico Power): $93M total 2024 financing (Sumitomo $40M tax equity, MUFG $29M debt, $24M ITC-transfer bridge) for 27 MW solar + 25 MWh BESS — its largest publicized US raise ([Businesswire Jun 2024](https://www.businesswire.com/news/home/20240627982661/en/))

The "backed by Sumitomo, Goldman Sachs, GE EFS, Shinsei Bank, Dragon Capital" line in GW Ranch PRs maps to these **historical project/fund relationships**, not confirmed equity in Pacifico Energy Group or in GW Ranch itself. Treat as marketing.

**Project.** Zero public disclosure: no capex figure from the company, no project-finance facility, no equity raise, no SEC Form D for any Pacifico US entity (EDGAR-indexed search; direct full-text search blocked — re-check manually). External reference points: **Forbes (Feb 2026): "all he needs is the $12 billion to build it and the hyperscalers"** ([Forbes](https://x.com/Forbes/status/2025510977341632931)); 7.65 GW of gas capacity alone implies $12–19B at $1,500–2,500/kW before DC shells. The Pecos County abatement was reported against a "$5.5B" / "$6.4B" project value ([Fort Stockton Pioneer](https://www.fortstocktonpioneer.com/news/pecos-county-commissioners-approve-major-property-tax-relief-cemented-64-billion-data-center)) — likely a phase or DC-only figure; doesn't bracket full buildout. Franklin's Senate EPW response (Mar 2026) cites "$200B of AI supercomputers" supportable on site — demand-side framing, not capex.

**Read:** balance-sheet development funding (land, permitting, deposits) from recycled Asia proceeds, with construction capital intended to come via customer-anchored project finance once offtake/leases sign. The November 2025 hire of **Dhiraj Shangari as CFO / Head of Capital Markets & Investments** ([Pacifico news](https://www.pacificoenergy.com/news)) signals the raise is ahead, not behind. "Turbines secured" (Jan 2026 PR) implies meaningful deposits already funded — but no OEM, count, or schedule has ever been disclosed.

## 3. Land: owned or optioned?

**Unconfirmed — likely controlled, ownership unproven.** Across both PRs, the project page, Forbes, and all local/trade coverage, Pacifico uses only possession-neutral language: "sited within 8,000+ acres," "over 8,000 acres of build-ready land." No instance of "acquired," "purchased," "owns," "optioned," or "leased" was found. No seller, prior ranch name, or consideration has been reported; "GW" is gigawatt branding, not a historic ranch name, so the underlying deed/lease likely sits under an SPV against a differently-named ranch. The Chapter 312 abatement (approved Jan 12, 2026) is consistent with fee ownership but can equally cover leasehold improvements — not dispositive.

**Fastest paths to settle it** (all blocked from this sandbox, ~30 min manual work):
1. esearch.pecoscad.org owner search: "Pacifico," "Pacifico GW LLC"
2. TexasFile grantee search, Pecos County, "Pacifico," 2024–2026
3. Open-records request for the Jan 12, 2026 abatement agreement — names the counterparty entity and recites the property interest
4. Full Forbes Feb 2026 profile + video ("This Daring Developer Wants To Power America's AI Future") — most likely public source to state tenure
5. Middle Pecos GCD permit applications — any non-exempt well application lists the landowner of record

## 4. Status (June 2026) and milestone scorecard

| Milestone | Status |
|---|---|
| TCEQ air permit (7.65 GW) | ✅ Issued ~Jan 26, 2026 — largest US power-gen air permit; ~5 months from public launch. Authorizes 12,000+ tpy criteria pollutants, up to 33 Mt/yr CO2e. No contested-case hearing or lawsuit found. |
| County tax abatement | ✅ Approved Jan 12, 2026 (+200-unit workforce housing) |
| Land delineation | ✅ "All site delineations complete" (developer claim, Jan 2026) |
| Turbines | ⚠️ "Secured" per PR — no OEM, count, or delivery schedule ever disclosed |
| Groundbreaking / construction | ❌ Not confirmed. "Construction can start Q1 2026" — Q1 passed with no reported site work; GEM lists pre-construction; Pacifico still presenting to Commissioners Court May 11, 2026 |
| EPC contractor | ❌ None announced |
| Anchor tenant | ❌ None announced, 10 months post-launch |
| Project financing | ❌ None announced |
| ERCOT queue | N/A by design (off-grid) |
| Timeline drift | Full buildout slipped 2030 → 2031 between Aug 2025 and Jan 2026; first power softened Q1 → H1 2027 within weeks |

**Upcoming milestones to watch (de-risking signals, in rough order of importance):** (1) creditworthy anchor lease/offtake; (2) project-finance close or Form D; (3) named turbine OEM with delivery schedule; (4) EPC award and visible groundbreaking; (5) confirmation the Pacifico Energy K.K. sale closed (funds the equity check); (6) MPGCD filings or fiber route agreements. Each is falsifiable and near-term if the H1 2027 first-power date is real.

## 5. Hurdles and risks

1. **Customer risk — the biggest hole.** No tenant after 16 months of development and 10 months of marketing. Hyperscalers still publicly prefer grid-tied sites; remote Permian campuses disproportionately attract credit-fragile AI tenants. The cautionary case is in the same county: Poolside/CoreWeave "Project Horizon" (2 GW, Longfellow Ranch) lost its anchor when CoreWeave terminated its 250 MW lease in March 2026 after Poolside's $2B Series C failed. Counter-signal: Microsoft's reported 2,500 MW "Pecos Data Center" in neighboring Reeves County (Apr 2026) and LandBridge/PowerBridge's 2 GW Alpha campus near Waha validate the geography.
2. **Financing risk.** ~$12B+ needed; largest disclosed US raise to date is $93M; no thermal track record; the Japan platform sale that presumably funds the equity is unconfirmed. Fermi's post-IPO collapse (-80%+, securities class actions, tenant walkaway) has repriced the permit-rich/tenant-poor off-grid category and will weigh on any GW Ranch raise.
3. **Turbine reality vs. claim.** GE Vernova slots are 2029–2030; Siemens says new orders deliver 2030+. "Secured" with no OEM named contrasts with Fermi (600 MW turbines publicized) and Crusoe (4.5 GW via Engine No. 1/GE Vernova JV). H1 2027 first power is plausible only for an aeroderivative/recip bridge tranche; 7.65 GW by 2031 collides with OEM slot math unless reservations predate the announcement.
4. **Execution/labor.** Pecos County pop. ~15k; peak construction (thousands of workers per Abilene comps) competes with oilfield wages. Solar developer building GW-scale thermal for the first time.
5. **Political/regulatory tail.** Senate EPW minority letter (Mar 13, 2026, Whitehouse/Heinrich/Van Hollen) targeting the "largest air pollution permit in US history" — one of twelve projects probed. The 2027 Texas Legislature could extend oversight to off-grid loads (utilities already lobbying on cost-shift from grid defection). Any future ERCOT tie forfeits the exemption and drops the project into the SB6 queue.
6. **Gas basis erosion.** The Waha thesis (negative 47 consecutive days into April 2026; -$7.15 record) is real today, but new takeaway in late 2026 relieves the glut; underwrite normalized basis, not -$5.
7. **Water.** Mitigated if the air-cooled design holds — but dry cooling costs efficiency on 100°F+ days, and any drift toward evaporative cooling lands in the most water-litigious GCD in West Texas (Middle Pecos; Fort Stockton Holdings precedent).

## 6. Differentiators and learnings

**Differentiators vs. the Texas GW-class set:**
- Largest single fully-permitted site in the US — one TCEQ permit covering 7.65 GW with claimed headroom to scale "without further regulatory approvals"
- Cleanest regulatory position in the class: zero ERCOT queue, zero SB6 curtailment exposure, zero FERC jurisdiction
- Sited essentially on top of Waha with a dedicated 1 Bcf/d lateral — a demand sink at the constrained hub needing no long-haul firm transport, with producers desperate to avoid negative realizations as natural supply counterparties
- 8,000+ contiguous, delineated, build-ready acres

**What it lacks vs. peers:** Stargate Abilene's tenant (OpenAI/Oracle) and $11.6B committed capital; Crusoe's and Fermi's disclosed turbine positions; Sailfish's DFW market proximity; Lancium's grid-interactive optionality.

**Learnings for LRP:**
1. **Permits are now the cheap, fast part.** A first-time thermal developer got the largest air permit in US history in ~5 months from public launch. TCEQ air permitting is not the moat; the moat is tenants, turbines, and capital — in that order.
2. **Sequencing inversion is the category's defining bet.** Pacifico (like Fermi, unlike Crusoe/Stargate) is building power first and marketing capacity second. The market has started pricing that bet: Fermi -80%+, CoreWeave/Poolside walkaway. Land + permit + gas is an option premium, not a project.
3. **Possession-neutral land language is a tell.** When a developer never says "owns" or "acquired" across 16 months of PR, assume optioned/staged control until county records prove otherwise — directly relevant to how LRP reads other Permian campus announcements.
4. **The abatement agreement is the best diligence document in any Texas county deal.** It names the real counterparty entity and recites the property interest — an open-records request beats weeks of press parsing.
5. **Off-grid is a regulatory arbitrage with a legislative half-life.** Worth tracking the 2027 session for off-grid load oversight; it would reprice every BYOP campus in the state simultaneously.

## 7. Source quality caveats

Sourcing on this project is dominated by Pacifico's own releases; trade press has been largely stenographic. Independently corroborated: the TCEQ permit and its emissions parameters (Inside Climate News / Texas Observer read the permit documents), the county abatement (Fort Stockton Pioneer), the Senate EPW letter, location/acreage. Developer claims with no independent verification: "turbines secured," H1 2027 first power, "no external water," "five nines" reliability, and the historical-investor backing as it applies to GW Ranch. Pecos CAD, county deed records, MPGCD minutes, the abatement agreement text, and SEC EDGAR full-text could not be fetched from this environment — the land-tenure and Form D checks above are the highest-value manual follow-ups.
