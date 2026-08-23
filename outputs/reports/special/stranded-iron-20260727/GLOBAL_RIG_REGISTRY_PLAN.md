# Global Rig Registry: schema, sourcing, and build sequence

Target: every mobile offshore drilling unit worldwide (~629 MODUs per NOV 2025 census: drillships, semisubs, jackups), engine-level detail per hull (make, model/series, cylinder config, kW, count, install year), plus status, stack location/duration, and valuation marks.

## Schema (shipped in global_rig_registry.db)

- `rigs`: identity, design, shipyard, delivery year, IMO, flag, class, status, stack location/since, never_worked flag
- `power_plants`: one row per engine group per rig; engine make/model (the SKU), count, kW mech/elec, generator make/model, voltage, fuel, `confidence` in {verified_primary, class_typical, nd}, source
- `valuations`: dated marks with basis and source
- `status_history`: event log (stacked, held_for_sale, sold, recycled)
- `sources`: full source registry with tier and cost

Seeded: 17 rigs (the full current cold-stack/disposal inventory), 13 plant rows (1 verified-primary: Ocean Rig Mylos, 42.0 MW electrical).

## Sourcing stack

### Tier 1: primary, free (build the spine here first)
1. **Owner rig spec sheets**: Transocean publishes per-rig PDFs listing main power to engine make/model/kW (this is where Mylos was verified). Valaris and Noble publish fleet matrices; power detail thinner.
2. **SEC EDGAR**: disposals, impairments, sale prices, financing terms. The distress layer.
3. **Equasis** (free registration): resolves every hull to an IMO number, flag, class society, ownership chain. IMO number is the join key for everything else.
4. **Class society registers** (free search): ABS Record, DNV Vessel Register, BV Fleet. Machinery survey records confirm engine builder and model per hull. This is the authoritative free path to engine make/series.
5. **IMO GISIS**: ship particulars.
6. **AIS** (MarineTraffic/VesselFinder freemium): independently verifies stack anchorage and idle duration from position history.

### Tier 2: recommended subscriptions (close the gaps at scale)
1. **Westwood RigLogix**: the canonical rig database. Specs, contracts, dayrates, stack durations, utilization. Its idle-fleet fields are the distress screen (172 idle units, 64 stacked 5+ years). Core subscription.
2. **S&P Global Sea-web Ships** (ex-IHS Ship Register): the machinery table. Engine builder, model, cylinder count, kW, build year, keyed by IMO number, for the entire world fleet. This is the single subscription that delivers "brand, make, series, SKU, age of engine" globally rather than rig-by-rig. Alternative: Clarksons World Fleet Register (adds sale-and-purchase comps).
3. **Esgian Rig Analytics + Rig Values**: the valuation marks quoted in trade press originate here. Needed to time bids against recycler parity.
4. Optional: Bassoe (cheap second valuation mark), S&P Petrodata RigPoint (overlaps RigLogix; pick one of the two).

### Tier 3: verification and comps
- Recycling transaction comps (Meltem+Scirocco $41M aggregate; Mistral $10M; Bora $14.5M) from owner disclosures and trade press.
- Shipbroker sale-and-purchase circulars (Fearnley Offshore, Clarksons) for live asking prices.

## Build sequence

1. **Week 1**: enumerate the fleet from RigLogix export (or free: NOV census + owner fleet lists). Assign rig_id, resolve IMO via Equasis. ~630 rows in `rigs`.
2. **Week 2**: bulk-pull machinery records via Sea-web export keyed on IMO. Populate `power_plants` with confidence=verified_primary where the register lists the engine, class_typical where inferred from sister ships.
3. **Week 3**: overlay status: owner FSRs (quarterly cadence) + AIS position history to date-stamp stacking. Populate `status_history`.
4. **Ongoing**: quarterly refresh on FSR publication; event-driven updates on 8-K disposals; Esgian marks into `valuations`.
5. **Screen**: the standing query is `status IN (cold_stacked, held_for_sale, retired) AND delivery_year >= 2009 AND kw_total_elec >= 30000`, ranked by $/kW at last mark less 30% non-drilling haircut.

## Known gaps in the seed

- IMO numbers: n/d pending Equasis pass.
- DSME 12000 and HuisDrill 12000 engine models: n/d pending class-register pull (DNV likely for Korean-built hulls).
- Enhanced Enterprise exact engine model/kW: n/d; owner spec sheets for stacked units are partially delisted; class records are the path.
- Jackup fleet excluded from seed (small plants, segment re-absorbing); add in Week 1 enumeration for completeness.
