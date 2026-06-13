# Stargate Abilene / Lancium Clean Campus — Counterparty Diligence Memorandum

**1.2 GW operational AI data center campus (Crusoe / Oracle / OpenAI), Taylor County, Texas — project structure, land position, capital stack, ownership, status, risk**
**Prepared June 13, 2026 · Land Resource Partners · Internal and counterparty-restricted circulation · Not investment advice**

---

## I. Executive Summary

**The opposite profile to a speculative permit play: this one is built, leased, capitalized, and running — and it still broke once.** The Abilene campus (Lancium Clean Campus; "Stargate I") is the most de-risked gigawatt-scale AI campus in the United States — live since September 2025, ~$15B of committed capital, hybrid grid-plus-gas power, and multiple investment-grade hyperscalers competing for capacity. It is also the live case study in how single-counterparty AI data center risk transmits to lenders: in March 2026 the Oracle/OpenAI expansion lease collapsed, Nvidia paid Crusoe a $150M deposit to backstop the dropped block and recruit a replacement, Microsoft stepped in on the adjacent capacity, and a winter storm had already knocked buildings offline for days. If this is the strong case for the sector, the tenantless tier (GW Ranch, Fermi) is far more exposed.

**Structure: a project-finance real-estate deal wearing a "Stargate" label.** The single most-confused fact in public coverage: **the $500B Stargate JV does not own or finance Abilene.** The campus is owned by a Crusoe / Blue Owl Capital / Primary Digital Infrastructure JV, ground-leased from landowner Lancium, and net-leased to Oracle, which buys ~$40B of Nvidia GPUs and resells cloud capacity to OpenAI. "Stargate I" is retroactive branding on a pre-existing Crusoe/Oracle deal. Crusoe CEO Chase Lochmiller, on record: *"Our customer is Oracle. OpenAI is Oracle's customer."*

**Capital is real and senior-debt-heavy, ring-fenced against the Oracle lease.** ~$15B committed at the site: roughly **$9.6B JPMorgan construction debt + ~$5B Crusoe/Blue Owl equity**, plus Lancium's $600M campus debt. The debt is reportedly non-recourse, secured by the campus assets and the 15-year Oracle lease — classic project finance "like a merchant plant with a long-term offtake." Blue Owl holds the controlling equity; Crusoe is the minority operator.

**Verdict: a financed, operating, multi-tenant asset whose tail risk is demand volatility, not site control.** The binding constraint here is the inverse of the spec plays: not "can they find a tenant," but whether OpenAI's offtake — against ~$20B ARR and a reset ~$600B (from ~$1.4T) compute pledge — holds up enough to keep Oracle paying rent that backs JPMorgan's loan. Oracle's own credit is the transmission cable: ~14–16% GPU-rental margins, 5-year CDS that hit a record ~198 bps in March 2026, a Jan 2026 bondholder lawsuit, and an RPO backlog heavily concentrated in the OpenAI contract. The asset is sound; the counterparty chain above it is where the risk lives.

## II. Project Structure

| Attribute | Finding | Source |
|---|---|---|
| Project name(s) | Lancium Clean Campus / "Stargate I" / Crusoe Abilene; dev codenames "Project Artemis" (2021 origin), "Project Radiance" (Mar 2025 expansion), "Longhorn Data Center" (TCEQ air permit) | Crusoe; Develop Abilene; TCEQ |
| Location | 5502 Spinks Rd, **north/NW** Abilene, Taylor County, TX (Spinks/Summerhill/Old Anson/FM 2404 — not south/I-20) | datacentermap; KTXS |
| Scale | 8 buildings, ~4M sq ft, **1.2 GW**, up to **450,000 Nvidia GB200** (each building up to 50,000 GB200 NVL72 on one fabric) | Crusoe/GlobeNewswire (Mar 18, 2025); DCD |
| Power — hybrid | **1.2 GW ERCOT grid interconnect** (held by Lancium, AEP/ERCOT-approved) + **~360 MW behind-the-meter gas** + battery storage (reported ~1 GW/4 GWh) + on/adjacent **265.5 MW Goodnight Wind Farm** | Lancium; gridstatus; ESIG |
| On-site gas | TCEQ Standard Permit ("Longhorn," approved Jan 22, 2025): ~360 MW across **10 simple-cycle turbines** (5× Solar Titan 350 + 5× GE LM2500, SCR-equipped). Broader Crusoe fleet: 29 GE Vernova LM2500XPRESS (~1 GW), Parker Hannifin >1 GW, PROENERGY 13× PE6000 | TCEQ Reg. 177263; lanin/Substack; DCD |
| Cooling | Direct-to-chip liquid cooling, **closed-loop, zero-evaporation** (air-cooled chillers; no cooling towers) | Crusoe; Lancium |
| Compute stack | Crusoe builds/owns shells + power; Oracle (OCI) installs/owns GPUs and operates cloud; OpenAI consumes. Build-to-suit / powered-shell-plus | DCD; constructionreviewonline |
| Entities | Land: **Lancium Abilene LLC**. Buildings: **Crusoe / Blue Owl / Primary Digital Infrastructure JV**. Lessee: Oracle. TCEQ entity "Longhorn Data Center" | Comptroller Ch.312 id 000017852; BusinessWire |

**Angle.** The power configuration is the structural opposite of the off-grid Permian plays (GW Ranch, Fermi). Abilene is **grid-tied first, gas-bridged second**: it took an ERCOT interconnect (the thing GW Ranch was built to avoid) and added ~360 MW of on-site simple-cycle gas as fast-start bridge/firming while the grid and the six-building Phase 2 came up. That choice buys grid backup and avoided a multi-year wait only because Lancium had pioneered the ERCOT Controllable Load Resource model and already held the interconnect — but it also drops the grid-connected load squarely into the ERCOT large-load queue and SB6 regime (§VI). The cooling design (closed-loop, air-cooled) is a genuine, deliberate water-risk mitigation given Abilene's stressed reservoirs.

## III. Land Position — Resolved (ground lease, not fee)

Unlike a speculative site where tenure is the central unknown, the Abilene chain is fully established and is a **ground lease, not a sale**:

**Lancium Abilene LLC (fee owner + master developer) → Crusoe (ground-leases ~90 acres; builds & owns the buildings + brings power) → Oracle (15-year net lease of the facilities) → OpenAI (end user via Oracle cloud).**

- **Owner:** Lancium Abilene LLC (subsidiary of Houston-based Lancium LLC) owns the campus and remains master developer as of 2026; Crusoe did **not** buy the land. Lancium's role "begins and ends with finding the land and providing the power infrastructure." (Develop Abilene, Nov 19, 2024; KTXS, 2026)
- **Acreage:** ~875 acres in the executed Chapter 312 legal description; ~1,045–1,100 acres total Lancium holdings (the variance is abated parcel vs. total footprint). Crusoe ground-leases ~90 acres within it. (Comptroller Ch.312 id 000017852; datacentermap)
- **Lancium background:** founded 2017 by **Michael McNamara (CEO) and Dr. Raymond Cline** (note: not "Grimstad," a common misattribution). "Clean Campus" model = load sited at congested wind/solar nodes, ramped as an ERCOT Controllable Load Resource. Other sites: Fort Stockton (first campus, operating) and Childress (>1 GW interconnect approved). (BearBox v. Lancium, CAFC 23-1922, Jan 13, 2025; PRNewswire)
- **Lancium capital:** Hanwha Solutions led a ~$150M round (~$100M Hanwha) in Nov 2021; Blackstone reported to have invested ~$500M in Nov 2024 toward ~5 GW of West Texas buildout (Bloomberg; one structural source could not independently confirm a current Blackstone stake — treat as reported); ~$600M debt closed Oct 16, 2025 (Santander sole structuring bank, Cantor advisor). (Hanwha; Bloomberg; Lancium/PRNewswire)
- **Incentives:** City of Abilene Chapter 312 abatement, Reinvestment Zone RZ21-1, **85% for 10 years**, effective 2031–2044, min investment $2.4B (Crusoe committed up to ~$3.5B), **357 new jobs at ~$57,600**. **Abilene ISD granted no abatement** (collects on 100% of value). No JETI (Ch. 403) school value-limitation agreement found — likely none. Projected ~$22.6M/yr city + ~$18M/yr county property tax across all 8 buildings. (Big Country Homepage; Develop Abilene; Comptroller)
- **Water:** City of Abilene allocated up to **500 gal/min**; closed-loop initial fill ~1M gal/building; actual draw reported ~20 gal/min (<5% of allocation) as of April 2026. No separate raw-water/groundwater contract identified. (Big Country Homepage; Inside Climate News, Apr 2026)

**Could not be verified from primary records (CAD/deed access blocked):** Taylor County CAD recorded parcel value, deed instrument numbers, prior landowner, and purchase price. A direct taylor-cad.org owner search ("Lancium Abilene LLC") or title pull would settle these; they are not load-bearing given the abatement and press record already establish ownership and the lease chain.

## IV. Ownership and Capital Stack

### The "who owns / who pays / who bears risk" map

| Layer | Owner | Instrument | Pays → | Bears |
|---|---|---|---|---|
| Land + substations | **Lancium Abilene LLC** (fee / master dev) | Ground lease to Crusoe; $600M campus debt | Receives ground rent | Land / power / interconnect risk |
| Buildings + shells | **Crusoe + Blue Owl RE + Primary Digital JV** (Blue Owl controlling equity; Crusoe minority + operator) | $3.4B → ~$15B JV; "forward takeout" SPV | Ground rent → Lancium; debt service → JPMorgan | Real-estate risk (cushioned by Oracle net lease) |
| Building debt | **JPMorgan** (~$9.6B incl. $2.3B Phase-1 + $7.1B Phase-2) | Senior, ring-fenced at SPV, secured by lease; reportedly non-recourse | Receives debt service | Senior credit vs. Oracle lease |
| Building lease | **Oracle** (lessee, ~15 yr) | Rent → JV | Rent → JV | Tenant credit + occupancy |
| GPUs / IT | **Oracle** (~400–450k GB200, ~$40B) | Buys chips; leases compute to OpenAI | Pays Nvidia | GPU capex + obsolescence |
| Cloud compute | **OpenAI** (customer) | OCI contract (~$300B / ~$60B-yr from 2027) | Pays Oracle | Demand / offtake |
| Program equity | **Stargate LLC** (OpenAI ~40 / SoftBank ~40 / Oracle / MGX) | Separate $500B program pledge | Funds *other* sites | Does **not** own Abilene |

### Site-level capital (the real, financed number)

- **~$15B committed at Abilene I**, built up as: **Phase 1** — $3.4B JV (Oct 15, 2024; Crusoe/Blue Owl/Primary Digital), with a **$2.3B JPMorgan construction loan** (Newmark-brokered, ~Jan 2025); **Phase 2** — additional **$11.6B debt+equity** (May 2025), expanding the JV to ~$15B for the full 8-building/1.2 GW campus, including a **$7.1B JPMorgan tranche**. Sacra's breakdown: ~$9.6B JPMorgan debt + ~$5B Crusoe/Blue Owl equity. Plus **Lancium's $600M** campus debt (Oct 2025). (BusinessWire; Bloomberg; DCD; Sacra, Apr 27, 2026)
- **Risk structure (important):** the debt is ring-fenced at the SPV, secured by the campus and the 15-year Oracle lease, and reportedly **non-recourse** to Crusoe/Blue Owl. JPMorgan underwrote against the Oracle lease, not Crusoe. If Oracle stops paying, the lenders take "a giant empty hyperscale shell." OpenAI's *partners* (Oracle, Crusoe, Blue Owl, SoftBank) carry ~$100B of associated debt; OpenAI itself bears none. (electroneconomics; Sherwood/FT)

### Crusoe Energy (developer/operator)

- Founded **2018** by **Chase Lochmiller (CEO) and Cully Cavness (President)**; origin was "Digital Flare Mitigation" — flare-gas-powered Bitcoin mining — pivoted to AI cloud 2023–24. **Sold the legacy bitcoin/flare-gas business to NYDIG (Mar 25, 2025)** (~425 modular DCs, ~250–270 MW, ~55% of 2024 revenue) to become a pure-play AI infra developer. (CNBC; Sacra)
- **Equity:** Series D Dec 2024, $600M @ **~$2.8B** (Founders Fund led; **Nvidia, Fidelity, Mubadala, Valor, Ribbit** participated); Series E Oct 2025, $1.375B @ **>$10B** (Mubadala Capital + Valor co-led). ~$3.9B equity raised since founding. Additional debt: Brookfield $750M, Upper90 $225M, Victory Park $175M. (Sacra, Apr 27, 2026) *Note: the "~$35B valuation" sometimes cited is CoreWeave's IPO benchmark, not Crusoe's — Crusoe is ~$10B.*

### Blue Owl Capital (controlling equity)

- Lead/controlling equity via its Real Estate platform, with Primary Digital Infrastructure (CIO Bill Stein, ex-Digital Realty CEO); Crusoe is minority + operator. **Exact Abilene equity split is undisclosed** — do not assume the 80/20 split from Blue Owl's separate ~$27B Meta Hyperion JV. Risk-discipline signal: Blue Owl **walked away from funding Oracle's ~$10B Michigan (Saline Township) site** in Dec 2025 over unfavorable lease terms — it underwrites to lease quality, not Oracle's name. (Global Data Center Hub; DCD)

### The $500B Stargate LLC (program equity — not the Abilene owner)

- Announced at the White House Jan 21–22, 2025: **$500B over four years, $100B immediate**; reported equity SoftBank ~40% / OpenAI ~40% / Oracle ~$7B / MGX (Abu Dhabi) ~$7B; SoftBank financial lead (Masa Son chairman), OpenAI operational lead. Scoped up Sept 2025 to ~7 GW / >$400B over three years across new sites (Shackelford/Vantage, Milam, Doña Ana NM, Lordstown OH, Michigan). **This equity funds new greenfield sites, not Abilene's title.** (OpenAI; TechCrunch; S&P Global)

**Angle.** This is a fundamentally bankable structure — senior bank debt sized against a 15-year investment-grade-adjacent lease, controlling institutional equity (Blue Owl), and an operator (Crusoe) with skin in the game but no balance-sheet dependence on it. That is exactly why it got built while the off-grid spec plays did not. The fragility is not in the layer cake's construction; it is that **every layer's cash flow ultimately rests on OpenAI's ability to pay Oracle**, and OpenAI is pre-profit with commitments far ahead of revenue. The non-recourse ring-fence protects Crusoe/Blue Owl's *other* assets, not the building's value if the offtake fails.

## V. Status and Milestones

| Item | Status (June 2026) |
|---|---|
| Groundbreaking | June 2024 (Lancium broke ground on the broader campus Nov 2022) |
| Phase 1 live | **Verified.** Two buildings (~980k sq ft, 200+ MW critical IT) energized and live on OCI for OpenAI **Sept 30, 2025**; first Nvidia GB200 racks delivered June 2025 |
| Compute delivered | **GPT-5.5 reportedly trained on-site** — a concrete capacity-delivered datapoint (OpenAI). "Hundreds of thousands of GPUs operational" is aggregate marketing, not an independently verified live count |
| Buildout | 8th (final) building **topped off Nov 2025**; ~**4 of 8 buildings operational** mid-2026 ("most complete Stargate site"); full 1.2 GW guidance **slipped from mid-2026 → end-2026/Q1 2027** |
| On-site gas | TCEQ "Longhorn" permit approved Jan 22, 2025 (~360 MW); permit **modified to raise run hours 5,880 → 8,760 (continuous)** — i.e., baseload, not pure backup |
| Reliability event | **Winter weather in early 2026 damaged liquid-cooling equipment, taking several buildings offline for days** — a contributing factor in the expansion pullback |
| Expansion **reversal** | **Mar 2026:** Oracle/OpenAI **dropped the planned ~600–700 MW Abilene expansion** (financing terms + OpenAI's shifting demand + reliability + a decision not to mix Blackwell with next-gen Vera Rubin). Existing 1.2 GW unaffected. Oracle disputes the "cancellation" framing |
| Backfill | **Nvidia paid Crusoe a ~$150M deposit** to hold the dropped block and recruited **Meta** (to keep the site Nvidia, not AMD); **Microsoft** announced a **separate adjacent 900 MW campus** (Mar 27, 2026; 20-yr lease; first building ~mid-2027) → ~2.1 GW total Abilene footprint, now multi-tenant |
| Financing posture | Lancium CEO McNamara (Apr 2026): campus "fully financed long-term," Oracle 15-yr + Microsoft 20-yr tenants |
| Labor | ~5,000–9,000 peak workers; 24/7 build; Abilene housing strain (rents +~$1,000/yr); one resident hospitalized after being struck by a construction truck. No confirmed on-site worker fatality (two nearby data-center deaths — Haskell, Medina counties — are different projects) |

**Next 12–24 month milestones to watch:** full 1.2 GW / 8-building energization (Q1 2027 guidance); Microsoft 900 MW campus first power (mid-2027); resolution of the Meta-vs-Microsoft backfill; Oracle credit trajectory (CDS, ratings, the bondholder suit); OpenAI's next funding round and whether its ~$600B compute reset holds; SoftBank liquidity.

## VI. Risk Register

| Risk | Rating | Substance |
|---|---|---|
| Counterparty / offtake concentration | HIGH | The whole stack rests on OpenAI → Oracle → JV → JPMorgan. JPMorgan debt is reportedly non-recourse, secured by the Oracle lease; "if Oracle stops paying, the lender takes an empty shell." **This risk partly fired in Mar 2026** when the expansion lease collapsed and needed an Nvidia deposit + Microsoft/Meta backfill. Banks had already hit single-counterparty (Oracle) exposure limits; JPMorgan struggled for months to syndicate |
| OpenAI affordability | HIGH | ~$1.4T in compute commitments over 8 years (Altman, late 2025), **reset toward ~$600B by 2030** (Feb 2026), against ~$13–20B revenue / ~$20B ARR and ~$9B+ net loss; HSBC: not cash-flow positive by 2030, needs ~$207B more capital. Oracle deal alone ~$60B/yr from 2027 |
| Oracle credit (the transmission cable) | HIGH/MED | ~14–16% GPU-rental gross margin (a ~$100M operating loss renting Blackwell, per internal docs); 5-yr **CDS hit a record ~198 bps Mar 2026** (>2008 peak), then eased after a $50B raise plan; **Moody's Baa2 / S&P BBB, both negative outlook** (outlook, not a downgrade); $18B (Sept 2025) + $25B (Feb 2026) bonds; **bondholder lawsuit Jan 15, 2026** alleging non-disclosure of a $38B DC debt facility; RPO ~$638B (Q4 FY26) heavily concentrated in the OpenAI contract |
| Circular / vendor financing | MED | Nvidia is simultaneously a Crusoe equity investor, Oracle's GPU vendor, and put a $150M deposit into Crusoe; AMD guaranteed a $300M Crusoe chip-loan lease-back; Nvidia's "$100B" OpenAI commitment was walked back to ~$30B and called "never a commitment" (Feb 2026). Bernstein/Bloomberg/The Register flag round-tripping. Burry alleged hyperscaler depreciation understatement (note: his "$1.1B short" is misreported; actual premium ~$9.2M) |
| ERCOT / SB6 | MED | Grid-connected ~1.2 GW load sits in an ERCOT large-load queue that ballooned ~300% in 2025 to ~226 GW. **SB6 (June 2025)** imposes remote-disconnect + mandatory curtailment on >75 MW loads interconnected after Dec 31, 2025 — Phase 1 may be partly grandfathered, but **expansion capacity falls under the curtailment regime**. NERC flagged large-load voltage ride-through risk |
| Reliability | MED | The winter-2026 cooling outage demonstrated the failure mode; firm on-site gas + battery mitigate but the liquid-cooling system itself proved weather-vulnerable |
| Power economics | LOW/MED | Favorable: Waha gas went negative for a record streak in Feb 2026; on-site simple-cycle beats waiting in the queue. But ERCOT West is congestion/curtailment-heavy, and SB6 curtailment caps the grid leg's firmness |
| Air / environmental | MED | "Longhorn" gas permit run-hours raised to continuous (8,760) undercuts the "backup only" narrative (~1.6M tons GHG, 14 tons HAPs/yr); "Save Abilene" opposition; Texas Observer health coverage. Milder than peers (Meta Hyperion, xAI Colossus face lawsuits) |
| Water | LOW | Air-cooled closed-loop = genuinely low draw (~20 gpm vs. 500 gpm allocation). Context is stressed (Abilene reservoirs declining, city bought 2.5B gal from Possum Kingdom Feb 2025) but not a binding constraint for this design |
| Crusoe execution | MED | ~7-year-old company valued as a hyperscaler but operating as a leveraged "build-and-flip" developer (~$30B capex to 2030, ~$18B from selling stakes in its own projects). **Pushed off its own 1.8 GW Wyoming "Project Jade" by Google over cost/timetable concerns** — the sharpest execution datapoint |
| SoftBank liquidity | MED | Funded its $22.5B tranche but is strained: sold its entire Nvidia stake ($5.83B, Nov 2025), $40B bridge due Mar 2027, S&P negative, ~98% return concentration in OpenAI. "If OpenAI fails to deliver, there could easily be a liquidity crunch at SoftBank" |
| Stargate JV dysfunction | LOW (for Abilene) | The $500B JV reportedly stalled ~15 months with no staff and no JV-built sites; OpenAI now calls "Stargate" an umbrella term and prefers to lease. Low *direct* impact on Abilene (separately financed) but a negative signal on the program narrative |

## VII. Differentiators and Vulnerabilities

**What makes Abilene the strong case in the cohort**

- **It is actually built and running** — Phase 1 live since Sept 2025, GPT-5.5 trained on-site, ~half of 8 buildings operational. No peer GW-scale campus is further along.
- **Capitalized with senior bank debt against a long lease** — the bankable structure (JPMorgan + Blue Owl + 15-yr Oracle lease) that tenantless plays cannot replicate.
- **Multiple investment-grade-adjacent tenants competing for capacity** — Oracle, Microsoft, and Nvidia-via-Meta all wanted the site; tenant *churn*, not tenant *absence*, is the issue.
- **Hybrid power with a pioneer interconnect** — Lancium's ERCOT CLR model delivered a 1.2 GW grid tie plus ~360 MW fast-start gas, avoiding both the pure-queue wait and the pure-off-grid reliability bet.
- **Air-cooled, near-zero-water design** — a real de-risking in drought-stressed West Texas.

**Where Abilene is vulnerable**

- **Demand-side, not supply-side.** The risk is OpenAI's offtake durability transmitting through Oracle's thin margins and stretched credit to non-recourse lenders — a chain that already snapped once on the expansion.
- **Counterparty churn cost.** When the anchor lease dropped, it took an Nvidia deposit and months of re-leasing to backfill — capacity got re-tenanted, but not seamlessly.
- **SB6 curtailment on grid-connected expansion capacity**, and a demonstrated cooling-reliability failure mode.
- **Operator concentration risk in Crusoe**, a young, highly leveraged build-and-flip developer that has already been removed from one of its own flagship campuses.

**Competitive set (June 2026)**

| Campus | Scale | Status / signal | De-risking |
|---|---|---|---|
| **Stargate Abilene** (Crusoe) | 1.2 GW live | Expansion lease collapsed Mar 2026; Microsoft/Nvidia-Meta backfill; winter cooling outage | **Best**: live, ~$15B capitalized, multi-tenant, grid+gas |
| **Fermi America** (Amarillo) | 11 GW planned | Stock **−81%**; tenant pulled $150M (Dec 2025); CEO+CFO out; securities class actions | Weak: speculative, no firm anchor |
| **Pacifico GW Ranch** (Pecos) | 7.65 GW permitted, off-grid | **No named tenant, no financing, no land title disclosed** | Weakest: tenantless option |
| **Poolside / CoreWeave Horizon** (Pecos) | 2 GW | **Collapsed Mar–Apr 2026** (CoreWeave terminated anchor after Poolside's raise failed); courting Google | Failed |
| **Microsoft Reeves County** | ~2,500 MW | Microsoft canceled ~200 MW of US leases (demand-caution signal) | Mixed |
| **Meta Hyperion** (Louisiana) | 5 GW | Strong tenant; 10 gas plants; heavy ratepayer/enviro backlash (UCS: up to $90B damages) | Strong tenant, enviro/ratepayer risk |
| **xAI Colossus** (Memphis) | — | Strong tenant; NAACP/SELC/Earthjustice suit over 27 unpermitted turbines; EJ/legal risk | Strong tenant, severe enviro/legal risk |

## VIII. Falsification Conditions

- **On "most de-risked / bankable":** an Oracle credit downgrade (not just outlook) plus a failed syndication or a covenant breach on the JPMorgan facility; or OpenAI defaulting/restructuring its Oracle cloud contract; or Blue Owl writing down its Abilene equity. Any one would move this from "de-risked operating asset" toward the distressed tier.
- **On "demand is the binding constraint, not the asset":** sustained OpenAI ARR growth covering the ~$60B/yr Oracle obligation, plus Microsoft's 900 MW reaching FID/first power on schedule, would refute the demand-fragility thesis and confirm the asset is durably tenanted.
- **On "Abilene ≠ Stargate JV":** any disclosure that Stargate LLC equity actually capitalized the Abilene real estate (rather than Crusoe/Blue Owl/JPMorgan) would change the ownership analysis — none found to date.
- **On the bear base case:** triggers confirming it are an Oracle ratings downgrade, an OpenAI funding miss or down round, a SoftBank liquidity event, or a second reliability outage at scale. De-risking triggers: a clean Microsoft FID, OpenAI Q4 2026 IPO at/above the ~$850B mark, and Oracle CDS normalizing.

## IX. Action Items and Decision Thresholds

| # | Action | Window | Decision threshold |
|---|---|---|---|
| 1 | Pull Taylor County CAD ("Lancium Abilene LLC") + deed records to confirm fee owner, recorded value, prior owner | 0–30 days | Confirms the only unverified land item; not load-bearing (lease chain already established) |
| 2 | Pull the JPMorgan facility terms / any rated tranches and the Oracle lease structure (recourse, covenants, term, rent) | 0–60 days | Recourse + covenant package defines lender (and any successor-owner) exposure if OpenAI/Oracle falter |
| 3 | Track Oracle credit weekly: CDS, Moody's/S&P actions, the Jan 2026 bondholder suit, RPO concentration disclosures | Ongoing | A downgrade (not outlook) or suit progress is the leading indicator of stress transmitting to the asset |
| 4 | Monitor OpenAI funding/IPO and the $600B compute reset vs. actual ARR; SoftBank liquidity | Ongoing | Funding miss / down round / SoftBank event = demand-side bear case confirming |
| 5 | Confirm Microsoft 900 MW campus reaches FID + first power (~mid-2027) and resolve Meta-vs-Microsoft backfill | 30–180 days | Clean multi-tenant FID = durable demand; further slippage = churn risk persisting |
| 6 | Watch SB6 rule (PUCT, due Dec 31, 2026) for curtailment treatment of the grid-connected expansion capacity | 90–365 days | Heavy curtailment obligation reprices the grid leg's firmness |
| 7 | If engaging directly: as comps for any LRP West Texas land/power position, treat Abilene as the "tenanted + grid + gas" benchmark; the value premium is the lease, not the dirt | Standing | — |

## X. Caveats and Undisclosed-Items Register

- **Undisclosed:** exact Crusoe/Blue Owl/Primary Digital equity split at Abilene; precise Oracle lease NPV and recourse terms; Lancium's current Blackstone ownership %; Taylor CAD recorded value/prior owner/deed numbers; final Meta-vs-Microsoft tenancy of the backfilled capacity.
- **Corrections to common misreporting:** the **$500B Stargate JV does not own/finance Abilene** (Crusoe/Blue Owl/Lancium do; Oracle leases it); the **"~$30B"** figure is the *annual* OpenAI→Oracle cloud run-rate (the deal is ~$300B / ~$60B-yr from 2027), **not** the building lease; **Crusoe is ~$10B** (the "~$35B" is CoreWeave's IPO benchmark); **Oracle issued two bonds** ($18B Sept 2025 + $25B Feb 2026); **Lancium's backer is Hanwha** (not DataBank); **Lancium co-founders are McNamara + Cline** (not Grimstad); **Vantage's Frontier (Shackelford County) is a separate Stargate site** and owns no part of Abilene I; **Burry's "$1.1B short"** reflects ~$9.2M of actual premium; **Oracle has a "negative outlook," not a downgrade**; the **Haskell/Medina worker fatalities are different projects**, not Abilene.
- **Numbers that moved:** Nvidia's "$100B" OpenAI commitment → ~$30B, called non-binding (Feb 2026); OpenAI's "$1.4T" compute framing → ~$600B (Feb 2026); the Abilene expansion went from "doubling to ~2 GW for OpenAI" to "cancelled, backfilled by a separate 900 MW Microsoft campus."
- **Site naming:** Abilene is north/NW (Spinks Rd), not south/I-20.
- **Method:** primary-domain fetches (Bloomberg, FT, The Information, CNBC, Oracle, OpenAI, Crusoe, Lancium, county CAD) were network-blocked during research; findings rest on search-indexed extracts of those primary pages plus corroborating outlets and the directly-read Sacra Crusoe equity report (Apr 27, 2026). Highest-stakes Bloomberg/FT/The Information figures should be confirmed against live URLs before external citation. Nothing herein is investment advice or an offer to transact.

**Sources:** OpenAI (Stargate announcement Jan 2025; five new sites Sept 2025; compute-infrastructure posts); Crusoe newsroom (200 MW Jul 2024; 1.2 GW/Project Radiance Mar 18, 2025; live Sept 30, 2025; Microsoft 900 MW Mar 27, 2026; GE Vernova orders); Lancium (Jul 2024; Mar 2025; $600M debt Oct 16, 2025); BusinessWire ($3.4B JV Oct 15, 2024); Bloomberg ($7.1B JPMorgan loan May 2025; Oracle CDS Mar 2026; Microsoft lease Mar 27, 2026; SoftBank); DCD (extensive — financing, GPU counts, expansion reversal, Oracle margins/RPO, turbines); Sacra Crusoe report (Apr 27, 2026); Newmark/Commercial Observer (Phase-1 loan); Comptroller Ch.312 id 000017852; Develop Abilene / Texas EDC; TCEQ "Longhorn" Std Permit Reg. 177263 (Jan 22, 2025); ESIG/Lancium grid presentation; Utility Dive / ERCOT / NERC (queue, SB6, ride-through); Perkins Coie / McGuireWoods (SB6); Texas Observer / Save Abilene (air); Inside Climate News / Austin Chronicle / Texas Tribune (water); Big Country Homepage / KTXS / Time / ENR (local, labor, abatement); Fortune / CNBC / The Register / Bloomberg / HSBC / Moody's (circular-financing, OpenAI burn, Oracle credit); BearBox v. Lancium CAFC 23-1922 (founders); SEC filings (Oracle $18B/$25B notes; AMD 8-K); CNBC/NYDIG (Crusoe bitcoin divestiture); Blockspace/DCD (Crusoe Wyoming removal). English-language sourcing. Nothing herein is investment advice or an offer to transact.
