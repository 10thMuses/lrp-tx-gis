# Sprint plan

Detailed task breakdowns for multi-step Sprint queue items. Created on demand
per `OPERATING.md §10`; each section deletes when the sprint item ships and
its detail is no longer load-bearing.

`WIP_OPEN.md` carries one-paragraph pointers; deep detail lives here.

---

## FIELD EXPANSION + WELLS HIDE

Bundled `layers.yaml` + refresh-script maintenance chat. No layer-count change (stays at 25). One chat.

1. **`tceq_gas_turbines` extend refresh** — `scripts/refresh_tceq_gas_turbines.py` captures 13 of ~18 source columns. Add: full `received_date` (ISO; only `year` captured today), TCEQ `permit_no` (distinct from INR which is in `plant_code`), `num_units`, permit `status`. Map via abatement-style overload (ARCHITECTURE.md §4): `inr` ← permit_no, `funnel_stage` ← permit status, `zone` ← received_date ISO, `project` ← num_units. Add to popup + `filterable_fields` (numeric on `mw`, `year`; categorical on `technology`, `manu`, `operator`, `county`, `funnel_stage`).

2. **`tax_abatements` popup/filter rename** — display layer only; Chat 88 schema stays locked. Rename `commissioned` label "Commissioned" → "Approved date". Popup field order: `name` (Applicant), `county`, `commissioned` (Approved date), `technology` (Project type), `mw` (Project MW), `capacity` (Capex $M), `use` (Abatement schedule), `sector` (Taxing entities), `project` (Reinvestment zone), `poi` (Agenda URL). `filterable_fields`: county, technology, commissioned (date range), mw, capacity. No status in popup or filters. Technology filter set: natural_gas, gas_peaker, solar, wind, battery, renewable_other.

3. **`wells` hide** — current state: `default_on: false`, `min_zoom: 6`, thousands of statewide features. Primary: raise `min_zoom: 10`. Fallback: flag entry with `hidden: true` and skip sidebar render in `build_template.html`. Do NOT delete PMTiles.

---

## ABATEMENT PERMIAN-CORE + PERIPHERAL

Permian-core (Andrews, Ector, Glasscock, Loving, Martin, Midland, Ward, Winkler) → peripheral (Crane, Crockett, Irion, Reagan, Schleicher, Sutton, Upton). PDF-only counties dropped. 4–6 chats.

**Constraint:** any county on the same CivicEngage CMS hosting platform now used by Reeves (`reevescounty.org`) is Akamai bot-protected from datacenter egress; adapter URL fixes are correct but cannot be verified from cloud runners until residential-proxy or whitelisted egress is provisioned.

---

## POWER PLANT DATA REFRESH + POPUP REDESIGN

Re-pull EIA-860 (plants, battery) + USWTDB (wind) to fill blank operator/commissioned/technology/fuel/capacity_mw. Rewrite popup templates for `eia860_plants`, `eia860_battery`, `solar`, `wind`, `ercot_queue`: DROP sector; ADD commissioned/COD date, operator, capacity_mw, fuel/technology. Filter UI reflects same fields.

---

## DC RESEARCH → DC BUILD → DC AUTO-REFRESH (3-chat sub-sequence)

Research anchors: Longfellow/Poolside (Pecos), Stargate (Abilene), Project Matador/Fermi. Capture per-project: name, county, coords, MW, announcement date, completion date, owner/operator/developer, tenant, source, confidence level. Deliver structured data file → layer build → GitHub Actions weekly refresh with LLM-in-the-loop parser.
