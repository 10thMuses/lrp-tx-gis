# Pacifico Energy — GW Ranch (Pecos County, TX) — Diligence Report

**Date:** June 12, 2026
**Prepared for:** Andrea Himmel, Land Resource Partners
**Subject:** GW Ranch power + data center campus, Pecos County — financing, capital stack, structure, land tenure, status, risks, differentiators
**Method:** Six parallel research tracks (~90 web sources, English + Japanese), cross-corroborated. Direct fetches of TCEQ, SEC EDGAR, Pecos CAD, Forbes, and county records were blocked from the research environment; those gaps are flagged and a manual verification playbook is included (§4). Every load-bearing claim is cited; developer claims are labeled as such.

---

## TL;DR

GW Ranch is the largest fully air-permitted power-for-AI campus in the US — 7.65 GW gas + 1.8 GW BESS + 750 MWac solar, fully off-grid (zero ERCOT/SB6/FERC exposure), on 8,000+ acres essentially on top of the Waha hub. The permit position, regulatory insulation, and gas logistics are genuinely best-in-class. But as of June 2026, **every commercial load-bearing element is undisclosed and unverified**: no named tenant, no named turbine OEM, no announced project financing, no confirmed groundbreaking, and land tenure (fee vs. option/lease) cannot be confirmed from public sources.

The capital stack behind the company is thinner than the marketing suggests. Pacifico is a **founder/family-controlled private company with no institutional sponsor at parent level** — the "backed by Goldman Sachs, Sumitomo, GE EFS, Shinsei, Dragon Capital" line maps to historical project- and fund-level relationships, not parent equity. The flagship monetization event that would seed the US pivot — Bank of America's sale of the Japanese solar platform — **publicly failed to clear**: KKR, Macquarie, and Copenhagen Infrastructure Partners all passed, the ask was cut ~70% (¥100bn → ¥30bn+), and no closing has been reported through June 2026. Forbes pegs GW Ranch's capital need at ~$12B; Pacifico's largest publicized US raise is $93M.

Until a turbine OEM, a financing close, or a creditworthy anchor lease lands, GW Ranch is an option on the Permian power thesis, not an executing project. The nearest analogs for permit-rich/tenant-poor off-grid campuses — Fermi (-80%+ post-IPO, class actions) and Poolside/CoreWeave Horizon in the same county (anchor lease terminated March 2026) — show where this model breaks: tenants and capital, not permits or gas. A second signal: Pacifico's other Texas project ("Fort Spunky," Hood County) had its concept plan revoked by commissioners in 2026 after a water-utility denial, and Pacifico is now suing the county.

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

The small/large turbine mix implies aeroderivative or recip bridging for the first GW with frame machines later — a common 2025-vintage structure for hitting an early first-power date while frame slots are scarce.

## 2. Company and project financing

### 2.1 Corporate structure and who actually stands behind Pacifico

Pacifico Energy Group: privately held holding company, HQ San Juan Capistrano, CA; founded 2009 by Nate (William) Franklin (UCLA Anderson MBA '08; ex-Edison Mission, ex-BP Solar director of solar development). Built its base as Japan's largest utility-scale solar developer via Pacifico Energy K.K. (Tokyo, est. 2012): 1,750+ MW developed, company-claimed $4–5B+ in cumulative equity/debt raised (unaudited).

**Ownership chain (the key clarity item):**

- The historical chain runs **Jamieson Group → Virginia Solar Group → Pacifico Energy K.K.** Business Wire releases from 2016 describe Pacifico Energy as "a subsidiary of Virginia Solar Group," and Virginia Solar Group as "an affiliate of the **Jamieson Group, a California-based oil & gas / real estate enterprise with annual revenues of over USD $800 million**" ([Business Wire Oct 11, 2016](https://www.businesswire.com/news/home/20161011005920/en/GE-Energy-Financial-Services-and-Virginia-Solar-Group-Commission-Mimasaka-Musashi-Solar-Project-in-Okayama-Prefecture-Japan); [Power Mag 2016](https://www.powermag.com/press-releases/ge-energy-financial-services-and-virginia-solar-group-commission-pacifico-energy-kumenan-mega-solar-plant-in-okayama-prefecture-japan/)). Franklin was a partner of Virginia Solar Group ([LinkedIn](https://www.linkedin.com/in/nate-franklin-b8362a4/)).
- Since a **July 11, 2022 shareholder change**, Pacifico Energy K.K. is owned **66.7% by "Pacifico Energy AM Holdings L.P."** and **33.3% by president/CEO Hiroki Matsuo** (松尾大樹) — the 33.3% was transferred *from* AM Holdings to Matsuo, i.e., a management equity grant, not outside capital ([AtPress July 2022](https://www.atpress.ne.jp/news/317649); [pacificoenergy.jp shareholder notice](https://www.pacificoenergy.jp/news/detail/%E3%83%91%E3%82%B7%E3%83%95%E3%82%A3%E3%82%B3%E3%83%BB%E3%82%A8%E3%83%8A%E3%82%B8%E3%83%BC-%E6%A0%AA%E4%B8%BB%E5%A4%89%E6%9B%B4%E3%81%AE%E3%81%8A%E7%9F%A5%E3%82%89%E3%81%9B/); corroborated by [Infralogic Oct 2024](https://ionanalytics.com/insights/infralogic/pacifico-energy-selling-japanese-solar-platform/)). Matsuo is an operator (ex-Toyota Tsusho, ex-Eurus Energy; Pacifico since 2013; president since June 2019), not a capital source.
- **AM Holdings L.P. is unregistered in any US state** (no OpenCorporates hit; the "L.P." suffix plus registry absence is consistent with a Cayman vehicle — unverified). Its GP/LP roster and beneficial owners are undisclosed. Inference, flagged as such: AM Holdings is the successor holding vehicle for the Franklin/Jamieson/Virginia Solar Group side of the chain.
- **Bottom line: founder/family-controlled, no institutional sponsor at parent level.** Institutional capital has only ever entered at project or fund level.

### 2.2 The Japan capital stack — how the platform was actually financed

**Project-level equity (strategics and GE):**
- **GE Energy Financial Services** was project-level equity co-investor (with Virginia Solar Group) in three Japan projects — Kumenan (majority stake), Hosoe (¥7.5bn commitment), Mimasaka Musashi — 2014–2016 ([GE News](https://www.ge.com/news/press-releases/ge-energy-financial-services-invests-japans-renewable-energy-power-market); [Business Wire Dec 2014](https://www.businesswire.com/news/home/20141210005230/en)). GE EFS never held equity in the Pacifico corporate entity. Disposition of GE's project stakes post-2018 is an open item.
- **Kansai Electric and ENEOS took 50/50 equity** in the Banshu project GK (~77 MWdc, COD Jan 2023) — project-level recycling to Japanese strategics ([Nikkei BP](https://project.nikkeibp.co.jp/ms/atcl/19/news/00001/01392/?ST=msb); [Kankyo Business](https://www.kankyo-business.jp/news/026925.php)).

**Project-level debt (Japanese banks, non-recourse):**
- Kumenan (32 MW): **¥11bn (~$101M) non-recourse from Bank of Tokyo-Mitsubishi UFJ and Chugoku Bank** — among the first international-standard non-recourse solar PF in Japan ([Business Wire May 2016](https://www.businesswire.com/news/home/20160516005413/en/GE-Energy-Financial-Services-Virginia-Solar-Group)).
- Hosoe (96.2 MW): **BTMU plus a 12-bank syndicate**; Kyushu Electric offtake ([Power Engineering](https://www.power-eng.com/renewables/gefs-virginia-solar-group-start-operations-at-japan-solar-power-plant/)). Setouchi Kirei (231 MW) closed at ~$1.1B with an $867M non-recourse syndicate loan ([Recharge](https://www.rechargenews.com/solar/870405/in-depth-ge-energy-financial-services-breaks-down-japan-barriers)).
- Shunan Nagaho: development-stage loan from **Bank of Yokohama** (Dec 2023) ([pacificoenergy.jp](https://www.pacificoenergy.jp/en/news/detail/20231226/)).
- Not found: any Mizuho, SMBC, SocGen, or Shinsei loan to a specific Pacifico project — the "Shinsei Bank" name in GW Ranch PRs has no traceable deal behind it in public sources.

**Asset-recycling funds (the sell-down machine):**
- **Fund I** (closed Sept 2017): **¥15.5bn (~$141M)** from Japanese institutional investors; 5 plants >100 MWdc; **Mitsubishi UFJ Morgan Stanley Securities sole placement agent** ([Business Wire Jan 2018](https://www.businesswire.com/news/home/20180131005563/en/Pacifico-Energy-Raises-15.5-Billion-Yen-Solar)).
- **Fund II** (Dec 2019): **¥29bn (~$266M)**; 5 plants >216 MWdc; **Nomura Securities and Goldman Sachs Japan co-placement agents** — Goldman's role was distribution, not principal ([Business Wire Dec 2019](https://www.businesswire.com/news/home/20191201005231/en/Pacifico-Energy-Raises-29-Billion-Yen-Solar); [pv magazine](https://www.pv-magazine.com/2019/12/03/pacifico-energy-raises-265-6m-with-new-pv-investment-fund-picks-up-35-mw-project-in-japan/)).
- Model confirmed by Japanese trade press: build, then transfer completed plants to its own private funds ("完工後はファンドに譲渡"). Individual LP identities were never disclosed. **No Fund III was ever raised** — consistent with the 2024 pivot to an outright platform sale.

**Offshore wind monetization:**
- **SSE Renewables paid $208M for 80%** of the Japan offshore wind platform (Oct/Nov 2021), **including $30M deferred consideration subject to conditions**; Pacifico retained 20% (SSE Pacifico JV, ~10 GW early-stage portfolio) ([Renewables Now](https://renewablesnow.com/news/sse-renewables-pacifico-set-up-japanese-offshore-wind-jv-759432/); [offshorewind.biz Nov 2021](https://www.offshorewind.biz/2021/11/01/sse-pacifico-emerges-in-japan/)). Caution: 4C Offshore lists the JV's Murakami–Tainai project as **cancelled**, consistent with broader Japan offshore wind distress (Mitsubishi exited three projects Aug 2025). Whether the $30M deferred was ever paid is unknown.

**BESS buildout (2023–2026):** first two grid BESS supported by a METI subsidy (2023); the Koganai BESS (COD Dec 9, 2025) was explicitly **"fully self-funded," subsidy-free merchant** — the 660 MW / 2.9 GWh-by-2030 program is riding on the K.K.'s own balance sheet, with no external lender or equity partner identified ([Business Wire Dec 8, 2025](https://www.businesswire.com/news/home/20251208564853/en/Pacifico-Energy-Commences-Operation-of-Grid-scale-Battery-Storage); [ESS News Dec 23, 2025](https://www.ess-news.com/2025/12/23/pacifico-energy-targets-2-9-gwh-of-bess-installations-in-japan-by-2030/)).

**Vietnam:** Dragon Capital is a project-level strategic partner on the 40 MWp Mui Ne solar plant only (non-recourse debt from Vietnam's OCB); no parent-level stake ([Business Wire Jun 2019](https://www.businesswire.com/news/home/20190623005057/en/Pacifico-Energy-Commences-Operation-of-a-40-MWp-Mui-Ne-Solar-Power-Plant-in-Vietnam)).

### 2.3 The failed platform sale — the impaired war chest

**Bank of America launched a sale of Pacifico Energy K.K. in late Sept 2024** — billed "USD 1bn-plus": 10 operating solar plants (317 MW), a 6.2 GW / 50-project pipeline, 2 GW BESS pipeline, SSE Pacifico carved out ([Infralogic Oct 2024](https://ionanalytics.com/insights/infralogic/pacifico-energy-selling-japanese-solar-platform/)). Then, per [Infralogic July 20, 2025 ("Infra managers walk away from Pacifico's Japan sale")](https://ionanalytics.com/insights/infralogic/infra-managers-walk-away-from-pacificos-japan-sale/):

- Initial bids missed expectations; the process stalled in early 2025.
- **KKR was interested but put off by price; Macquarie dropped out; Copenhagen Infrastructure Partners walked away in May 2025** on valuation gap.
- Pacifico originally wanted **~¥100bn (~$678M)** but, after reviving the process in May 2025, would "entertain offers above **¥30bn**" (~$200M) — a ~70% cut Infralogic attributes to "Pacifico's overly optimistic initial view of the value of its pipeline." BofA targeted final offers by Sept 2025.
- **No closing, buyer, or price has been reported through June 2026** (English or Japanese). Circumstantially, the platform was still operating independently under the Pacifico brand in Dec 2025 (self-funded BESS CODs and a 2030 growth target) — behavior inconsistent with a completed sale.

**Why it matters for GW Ranch:** the implicit equity story — recycle Japan proceeds into Texas — is impaired. Even a cleared sale at the reduced ask contributes ~$200M against a ~$12B build. And a publicly stalled sale process is itself a diligence datapoint on how the platform's pipeline value holds up under institutional scrutiny (KKR/Macquarie/CIP all looked and passed).

### 2.4 GW Ranch project financing — what's public

Zero disclosure: no company capex figure, no project-finance facility, no equity raise, **no SEC Form D found for any Pacifico US entity** (EDGAR-indexed search; direct full-text search blocked — re-check manually). External reference points: **Forbes (Feb 2026): "all he needs is the $12 billion to build it and the hyperscalers"** ([Forbes](https://x.com/Forbes/status/2025510977341632931)); 7.65 GW of gas capacity alone implies $12–19B at $1,500–2,500/kW before DC shells. The Pecos County abatement was reported against a "$5.5B"/"$6.4B" project value ([Fort Stockton Pioneer](https://www.fortstocktonpioneer.com/news/pecos-county-commissioners-approve-major-property-tax-relief-cemented-64-billion-data-center)) — likely a phase or DC-only figure. Franklin's Senate EPW response (Mar 2026) cites "$200B of AI supercomputers" supportable on site — demand-side framing, not capex.

**Read:** balance-sheet development funding (land, permitting, turbine deposits) from founder/family capital and recycled Asia proceeds, with construction capital intended as customer-anchored project finance once leases sign. The **Nov 2025 hire of Dhiraj Shangari as CFO / Head of Capital Markets & Investments** ([Pacifico news](https://www.pacificoenergy.com/news)) signals the raise is ahead, not behind. "Turbines secured" (Jan 2026 PR) implies funded deposits — but no OEM, count, or schedule has ever been disclosed. The "backed by Sumitomo, Goldman Sachs, GE EFS, Shinsei Bank, Dragon Capital" line in GW Ranch PRs maps to the historical project/fund relationships in §2.2 — **treat as marketing, not as a sponsor list**. US-side precedent: Pacifico Power's $93M 2024 financing (Sumitomo $40M tax equity, MUFG $29M debt, $24M ITC-transfer bridge) for 27 MW solar + 25 MWh BESS — three orders of magnitude below GW Ranch's need ([Business Wire Jun 2024](https://www.businesswire.com/news/home/20240627982661/en/)).

## 3. Land: owned or optioned?

**Unconfirmed — likely controlled, ownership unproven.** Across 16 months of PR, the project page, Forbes, and all coverage, Pacifico uses only possession-neutral language ("sited within 8,000+ acres," "build-ready land") — never "acquired/owns/optioned/leased." No seller, prior ranch name, or price reported; "GW" is gigawatt branding, so the deed/lease likely sits under an SPV against a differently-named ranch. The Chapter 312 abatement (approved Jan 12, 2026) is consistent with fee ownership but also covers leasehold improvements — not dispositive. Search-index sweeps of Pecos CAD, deed aggregators, and MPGCD filings return zero records tying "Pacifico"/"Pacifico GW LLC" to a parcel, deed, or water permit — weak evidence (poorly indexed databases), but it means there is no easy public confirmation of fee ownership.

## 4. Land-tenure verification playbook (~30 min manual)

| # | Step | What to do |
|---|---|---|
| 1 | Pecos CAD owner search (free) | [esearch.pecoscad.org](https://esearch.pecoscad.org/) → Property Search → Owner Name → "Pacifico", then "GW". If nothing: a 2024–25 purchase shows on the 2025/2026 roll — use the map search along Hwy 18 ~17 mi north of Fort Stockton and note the owner of the large tracts. That name is either the seller or the lessor. |
| 2 | TexasFile deed search (~$5–10) | [texasfile.com → Pecos County Clerk records](https://www.texasfile.com/search/texas/pecos-county/county-clerk-records/) → Grantee = "Pacifico", 2024-01-01 → today. A **warranty deed** = owned; a **memorandum of option/lease** = optioned/leased. Also run Grantee = the owner name from step 1. |
| 3 | Abatement agreement (best single document) | (a) Comptroller Chapter 312 registry — search "Pecos County" at [comptroller.texas.gov → tax abatements](https://comptroller.texas.gov/economy/development/prop-tax/abatements/); (b) TPIA request to the County Judge's office via [co.pecos.tx.us](https://www.co.pecos.tx.us/): "the tax abatement agreement and reinvestment zone designation approved by Commissioners Court on January 12, 2026, including the application and property description." The recitals state Pacifico's property interest verbatim. |
| 4 | Forbes profile + video | Forbes Feb 2026 (Amy Feldman; teased via [@Forbes](https://x.com/Forbes/status/2025510977341632931)) and ["This Daring Developer Wants To Power America's AI Future"](https://www.youtube.com/watch?v=5OMGS2pfKPs) — transcript-search "land," "bought," "lease." |
| 5 | Middle Pecos GCD (free + one call) | Scan [agendas/minutes](https://www.middlepecosgcd.org/agendas-and-minutes/) and [public notices](https://www.middlepecosgcd.org/public-notices/) 2024–26; faster, call the Fort Stockton district office — any non-exempt well application lists the **landowner of record**. |
| + | Bonus (free, 2 min) | [Comptroller franchise tax entity search](https://mycpa.cpa.state.tx.us/coa/) for "Pacifico GW LLC" — Texas registration, formation date, registered agent, officers, without SOSDirect fees. |

## 5. Status (June 2026) and milestone scorecard

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

**Upcoming milestones to watch (de-risking signals, in order of importance):** (1) creditworthy anchor lease/offtake; (2) project-finance close or Form D; (3) named turbine OEM with delivery schedule; (4) EPC award and visible groundbreaking; (5) confirmation/outcome of the Japan platform sale; (6) MPGCD filings or fiber route agreements. Each is falsifiable and near-term if H1 2027 first power is real.

**Pipeline note — Fort Spunky (Hood County).** Pacifico's second Texas project: a ~560–862-acre data center + power development near Granbury, requesting 100 MW from the grid and ~20,000 gal/day of water. The local water utility board denied its water request; Hood County commissioners then **revoked the previously-approved concept plan 3-2**, and Pacifico (via Husch Blackwell) **sued the county**, calling the revocation "unlawful and premature" and seeking ≥$250k ([Texas Scorecard](https://texasscorecard.com/local/hood-county-rejects-data-center-concept-plan/); [Hood County News](https://www.hcnews.com/stories/pacifico-demands-revocation-reversal,120041); [Texas Tribune via Salon, Jun 6, 2026](https://www.salon.com/2026/06/06/officials-powerless-to-stop-8-new-data-centers-that-could-transform-small-texas-county-partner/)). Datapoints: (a) GW Ranch is not the only US project; (b) Pacifico litigates local friction quickly; (c) grid-tied + water-dependent siting fails where GW Ranch's off-grid/dry-cooled design is precisely engineered not to.

## 6. Hurdles and risks

1. **Customer risk — the biggest hole.** No tenant after 10 months of marketing. Hyperscalers still publicly prefer grid-tied; remote Permian campuses attract credit-fragile AI tenants — the cautionary case is in the same county (CoreWeave terminated its 250 MW Project Horizon lease in March 2026 after Poolside's Series C failed). Counter-signals: Microsoft's reported 2,500 MW Reeves County DC (Apr 2026) and LandBridge/PowerBridge's 2 GW Waha campus validate the geography.
2. **Financing.** ~$12B+ needed vs. $93M largest disclosed US raise; no thermal track record; the Japan platform sale that would seed the equity publicly stalled at a ~70% valuation cut with KKR/Macquarie/CIP passing; Fermi's collapse has repriced the whole permit-rich/tenant-poor category.
3. **Turbines.** GE Vernova slots are 2029–2030, Siemens says 2030+; "secured" with no OEM contrasts with Fermi (600 MW publicized) and Crusoe (4.5 GW via Engine No. 1/GE Vernova JV). H1 2027 plausible only for an aero/recip bridge tranche; 7.65 GW by 2031 collides with slot math unless reservations predate the announcement.
4. **Labor/execution.** Pecos County pop. ~15k; peak construction competes with oilfield wages; solar developer building GW-scale thermal for the first time.
5. **Political tail.** Senate EPW minority letter (Mar 13, 2026, Whitehouse/Heinrich/Van Hollen) over the "largest air pollution permit in US history" — one of twelve projects probed; the 2027 Legislature could extend oversight to off-grid loads (utilities already lobbying on cost-shift from grid defection); any future ERCOT tie forfeits the SB6 exemption.
6. **Gas basis erosion.** Waha at -$7.15 records and 47 straight negative days into April 2026 is real today, but new takeaway in late 2026 relieves the glut — underwrite normalized basis, not -$5.
7. **Water.** Mitigated if dry cooling holds — but it costs capacity on 100°F+ days, and any drift toward evaporative cooling lands in the most water-litigious GCD in West Texas (Middle Pecos; Fort Stockton Holdings precedent). Fort Spunky shows what happens to Pacifico projects when water access is contested.

## 7. Differentiators and learnings

**Differentiators vs. the Texas GW-class set:**
- Largest single fully-permitted site in the US — one TCEQ permit covering 7.65 GW with claimed headroom to scale "without further regulatory approvals"
- Cleanest regulatory position in the class: zero ERCOT queue, zero SB6 curtailment exposure, zero FERC jurisdiction
- Sited essentially on top of Waha with a dedicated 1 Bcf/d lateral — a demand sink at the constrained hub needing no long-haul firm transport, with basis-distressed producers as natural supply counterparties
- 8,000+ contiguous, delineated, build-ready acres

**What it lacks vs. peers:** Stargate Abilene's tenant (OpenAI/Oracle) and $11.6B committed capital; Crusoe's and Fermi's disclosed turbine positions; Sailfish's DFW market proximity; Lancium's grid-interactive optionality.

**Competitive set snapshot (June 2026):**

| Project | Scale | Status | Model |
|---|---|---|---|
| GW Ranch (Pacifico, Pecos Co.) | 7.65 GW permitted; 5+ GW by 2031 | Permitted 1/2026; no tenant, no named OEM, no disclosed financing | Fully off-grid gas+BESS+solar |
| Stargate Abilene (Crusoe/Lancium/Oracle→OpenAI) | 1.2 GW campus; $11.6B raised; 4.5 GW gas JV | Phase 2 energizing mid-2026 | Grid-tied + BTM gas |
| Fermi "Matador" (Amarillo) | 11 GW HyperGrid; 6 GW gas | Stock -80%+ from IPO, class actions, tenant walkaway | Off-grid "power island" |
| Poolside/CoreWeave Horizon (Pecos Co.) | 2 GW | Anchor lease terminated 3/2026 | BTM Permian gas |
| LandBridge/PowerBridge Alpha (Reeves Co.) | 2 GW | First power 2027 | Co-located gas near Waha |
| Sailfish Comanche Circle (Hood Co.) | 5 GW / 2,600 acres | Phase 1 planned | Hybrid BTM + grid, metro-adjacent |
| Lancium (Abilene/Childress/Ft. Stockton) | 1.2 GW+ portfolio | Operating/expanding | Grid-interactive BTM |

**Learnings for LRP:**
1. **Permits are now the cheap, fast part.** A first-time thermal developer got the largest air permit in US history in ~5 months from public launch. TCEQ air permitting is not the moat; the moat is tenants, turbines, and capital — in that order.
2. **Sequencing inversion is the category's defining bet.** Pacifico (like Fermi, unlike Crusoe/Stargate) is building power first and marketing capacity second. The market has started pricing that bet: Fermi -80%+, CoreWeave/Poolside walkaway.
3. **Possession-neutral land language is a tell.** When a developer never says "owns" or "acquired" across 16 months of PR, assume optioned/staged control until county records prove otherwise.
4. **Marketing backer lists ≠ capital stacks.** "Backed by Goldman Sachs / Sumitomo / GE EFS" unpacked into placement agents, tax-equity buyers, and exited project co-investors. Always trace each name to the instrument, level (parent vs. project), and date.
5. **The abatement agreement is the best diligence document in any Texas county deal.** One open-records request beats weeks of press parsing — it names the real counterparty entity and recites the property interest.
6. **Off-grid is regulatory arbitrage with a legislative half-life.** Track the 2027 session for off-grid load oversight; it would reprice every BYOP campus in the state simultaneously.
7. **Failed sale processes are public-record stress tests.** KKR, Macquarie, and CIP looking at Pacifico's Japan pipeline and passing at -70% is the closest thing to an institutional mark on this sponsor's asset quality.

## 8. Source quality caveats

Sourcing on this project is dominated by Pacifico's own releases; trade press has been largely stenographic. Independently corroborated: the TCEQ permit and its emissions parameters (Inside Climate News / Texas Observer read the permit documents), the county abatement (Fort Stockton Pioneer), the Senate EPW letter, the Japan sale process (Infralogic, two reports), the 2022 shareholder structure (company notice + Infralogic), location/acreage, the Hood County revocation and lawsuit. Developer claims with no independent verification: "turbines secured," H1 2027 first power, "no external water," "five nines" reliability, "$5B raised," and the backer list as applied to GW Ranch. Single-source items: the Jamieson Group chain (2016 Business Wire + one Japanese profile), the Tesla Megapack BESS detail, the Murakami–Tainai cancellation. Pecos CAD, county deed records, MPGCD minutes, the abatement agreement text, SEC EDGAR full-text, and the full Forbes article could not be fetched from the research environment — §4 is the manual close-out path.
