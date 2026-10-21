-- ============================================================================
-- rig schema baseline
-- ============================================================================
-- Reconstructed structure-only baseline of the "rig" schema, an offshore
-- drilling-rig / distressed-asset intelligence data model that was built
-- and run directly against a Supabase project shared with an unrelated
-- application (10th Muses), with no source control (100 migrations applied
-- live between 2026-07-28 and 2026-08-01, none ever committed anywhere).
--
-- This file recreates the CURRENT structure captured live on 2026-08-23 via
-- read-only introspection (information_schema / pg_catalog / pg_get_viewdef
-- / pg_get_functiondef / pg_get_triggerdef) directly against that project.
-- It is a clean baseline, not a replay of the 100 historical migrations --
-- those never existed in git, so faking their dates would be less honest
-- than starting version control from the structure as it exists today.
--
-- SCHEMA ONLY. No data. As of this writing the ~380 rig rows and 51
-- corporate_entity rows (plus all other table contents) still live ONLY in
-- the original shared Supabase project -- nothing was copied or moved, per
-- an explicit "do not delete" instruction from that project's owner. See
-- docs/rig-schema-origin.md for full provenance and status.
--
-- Source objects captured: 37 base tables, 11 views, 4 functions, 3
-- triggers, 20 enum types, 4 sequences, 156 table constraints (PK/FK/UNIQUE
-- /CHECK/EXCLUDE), 29 non-constraint indexes. Row Level Security was
-- enabled (and mostly FORCEd) on every table with ZERO policies defined,
-- and ZERO grants existed beyond the implicit table-owner privileges -- i.e.
-- the schema was already locked down to anything but a superuser/owner
-- connection. That posture is reproduced verbatim below.
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS rig;

-- Extensions the live schema depends on (uuid defaults, trigram name
-- search, exclusion constraints over daterange, and rig position geography).
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE EXTENSION IF NOT EXISTS postgis;

-- ----------------------------------------------------------------------------
-- Enum types
-- ----------------------------------------------------------------------------

CREATE TYPE rig.component_tier AS ENUM ('A_power_electrical', 'B_industrial_mechanical', 'C_marine_propulsion', 'D_drilling_subsea', 'E_hull_steel');
CREATE TYPE rig.condition_grade AS ENUM ('as_new', 'good', 'fair', 'poor', 'non_functional', 'unknown');
CREATE TYPE rig.confidence AS ENUM ('verified', 'high', 'medium', 'low', 'unverified');
CREATE TYPE rig.conversion_target AS ENUM ('fpso', 'fso', 'accommodation', 'wind_installation', 'energy_storage', 'aquaculture', 'other');
CREATE TYPE rig.data_era AS ENUM ('live', 'post_2000', 'pre_2000', 'pre_1984');
CREATE TYPE rig.distress_domain AS ENUM ('financial', 'technical', 'commercial', 'regulatory');
CREATE TYPE rig.emissions_gate AS ENUM ('us_permittable_as_is', 'us_permittable_with_scr', 'us_nonroad_or_temporary', 'non_us_only', 'not_permittable', 'unassessed');
CREATE TYPE rig.event_type AS ENUM ('contract_award', 'contract_start', 'contract_end', 'contract_extension', 'contract_suspension', 'contract_resumption', 'sps_survey', 'class_renewal', 'class_suspension', 'class_withdrawal', 'shipyard_entry', 'shipyard_exit', 'reactivation', 'stacking', 'sale', 'bareboat_charter', 'name_change', 'reflag', 'incident', 'scrapping', 'conversion', 'newbuild_order', 'delivery', 'other');
CREATE TYPE rig.extraction_difficulty AS ENUM ('craneable', 'partial_cut', 'major_cut', 'not_extractable', 'unassessed');
CREATE TYPE rig.fuel_capability AS ENUM ('diesel_only', 'hfo', 'dual_fuel_gas', 'gas_only', 'methanol', 'convertible_to_gas', 'unknown');
CREATE TYPE rig.identifier_type AS ENUM ('imo', 'mmsi', 'call_sign', 'abs_class_no', 'dnv_id', 'lr_no', 'bv_no', 'ccs_no', 'classnk_no', 'rina_no', 'hull_no', 'yard_no', 'official_no', 'contractor_internal', 'petrodata_id', 'other');
CREATE TYPE rig.lifecycle_state AS ENUM ('ordered', 'under_construction', 'delivered', 'active', 'warm_stacked', 'cold_stacked', 'in_shipyard', 'suspended', 'scrapped', 'converted', 'total_loss', 'sold_out_of_segment', 'unknown');
CREATE TYPE rig.oem_lifecycle AS ENUM ('in_production', 'superseded_supported', 'discontinued_supported', 'discontinued_unsupported', 'unknown');
CREATE TYPE rig.preservation_state AS ENUM ('operating', 'preserved_active', 'preserved_lapsed', 'unpreserved_stacked', 'cannibalised', 'unknown');
CREATE TYPE rig.rating_basis AS ENUM ('standby', 'prime', 'continuous', 'peak_shaving', 'unknown');
CREATE TYPE rig.redeployment_class AS ENUM ('tier_a', 'tier_b', 'tier_c', 'tier_d', 'unassessed');
CREATE TYPE rig.station_keeping AS ENUM ('moored', 'dp2', 'dp3', 'moored_dp_assist', 'unknown');
CREATE TYPE rig.txn_type AS ENUM ('rig_sale', 'rig_sale_distressed', 'auction', 'fleet_transfer', 'scrap_sale', 'conversion_sale', 'component_sale', 'genset_used_market', 'newbuild_order', 'bareboat', 'charter');
CREATE TYPE rig.unit_class AS ENUM ('drillship', 'semisub', 'semi_tender', 'barge_tender', 'jackup_he', 'jackup_benign', 'intervention_semi', 'accommodation_semi', 'mopu', 'drilling_barge', 'unknown');
CREATE TYPE rig.valuation_case AS ENUM ('going_concern', 'rig_sale_comp', 'conversion', 'component_harvest', 'scrap_floor');

-- ----------------------------------------------------------------------------
-- Sequences (referenced by column defaults below)
-- ----------------------------------------------------------------------------

CREATE SEQUENCE IF NOT EXISTS rig.alert_event_alert_id_seq;
CREATE SEQUENCE IF NOT EXISTS rig.audit_log_audit_id_seq;
CREATE SEQUENCE IF NOT EXISTS rig.rig_code_seq;
CREATE SEQUENCE IF NOT EXISTS rig.rig_position_position_id_seq;

-- ----------------------------------------------------------------------------
-- Tables (dependency order)
-- ----------------------------------------------------------------------------

CREATE TABLE rig.source (
    source_id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_key text NOT NULL,
    source_name text NOT NULL,
    source_type text NOT NULL,
    is_licensed boolean DEFAULT false NOT NULL,
    redistribution_ok boolean DEFAULT false NOT NULL,
    base_url text,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT source_pkey PRIMARY KEY (source_id)
);

CREATE TABLE rig.source_precedence (
    source_id uuid NOT NULL,
    field_domain text NOT NULL,
    rank integer NOT NULL,
    CONSTRAINT source_precedence_pkey PRIMARY KEY (source_id, field_domain)
);

CREATE TABLE rig.source_record (
    source_record_id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_id uuid NOT NULL,
    retrieved_at timestamp with time zone NOT NULL,
    document_ref text,
    document_url text,
    document_hash text,
    era rig.data_era DEFAULT 'live'::rig.data_era NOT NULL,
    extraction_method text,
    reviewed_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    document_date date,
    CONSTRAINT source_record_pkey PRIMARY KEY (source_record_id)
);

CREATE TABLE rig.rig_design (
    design_id uuid DEFAULT gen_random_uuid() NOT NULL,
    designer text NOT NULL,
    design_series text NOT NULL,
    design_variant text,
    generation text,
    CONSTRAINT rig_design_pkey PRIMARY KEY (design_id)
);

CREATE TABLE rig.corporate_entity (
    entity_id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_key text NOT NULL,
    legal_name text NOT NULL,
    short_name text,
    entity_type text NOT NULL,
    domicile text,
    listing text,
    is_public boolean DEFAULT false NOT NULL,
    parent_entity_id uuid,
    status text DEFAULT 'active'::text NOT NULL,
    notes text,
    source_record_id uuid,
    confidence rig.confidence DEFAULT 'medium'::rig.confidence NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT corporate_entity_pkey PRIMARY KEY (entity_id)
);

CREATE TABLE rig.rig (
    rig_id uuid DEFAULT gen_random_uuid() NOT NULL,
    canonical_name text NOT NULL,
    unit_class rig.unit_class NOT NULL,
    core_scope boolean NOT NULL,
    design_id uuid,
    builder_yard text,
    builder_country text,
    hull_number text,
    keel_laid_date date,
    delivery_date date,
    original_owner text,
    jackup_he_criteria_met integer,
    jackup_he_rationale text,
    source_record_id uuid,
    confidence rig.confidence DEFAULT 'medium'::rig.confidence NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    rig_code text DEFAULT ('RIG-'::text || lpad((nextval('rig.rig_code_seq'::regclass))::text, 6, '0'::text)),
    delivery_year integer,
    CONSTRAINT rig_pkey PRIMARY KEY (rig_id)
);

CREATE TABLE rig.component_type (
    component_type_id uuid DEFAULT gen_random_uuid() NOT NULL,
    tier rig.component_tier NOT NULL,
    type_key text NOT NULL,
    display_name text NOT NULL,
    default_redeploy rig.redeployment_class DEFAULT 'unassessed'::rig.redeployment_class NOT NULL,
    rating_unit text,
    notes text,
    CONSTRAINT component_type_pkey PRIMARY KEY (component_type_id)
);

CREATE TABLE rig.engine_family (
    engine_family_id uuid DEFAULT gen_random_uuid() NOT NULL,
    oem text NOT NULL,
    family text NOT NULL,
    bore_stroke_mm text,
    rpm_nominal integer,
    kw_per_cyl_nominal numeric,
    cyl_configs text,
    imo_tier_typical text,
    fuel rig.fuel_capability DEFAULT 'unknown'::rig.fuel_capability NOT NULL,
    gas_conversion_avail boolean,
    lifecycle rig.oem_lifecycle DEFAULT 'unknown'::rig.oem_lifecycle NOT NULL,
    parts_availability text,
    land_power_precedent boolean DEFAULT false NOT NULL,
    notes text,
    CONSTRAINT engine_family_pkey PRIMARY KEY (engine_family_id)
);

CREATE TABLE rig.distress_indicator_def (
    indicator_id uuid DEFAULT gen_random_uuid() NOT NULL,
    domain rig.distress_domain NOT NULL,
    indicator_key text NOT NULL,
    description text NOT NULL,
    weight numeric NOT NULL,
    polarity integer NOT NULL,
    scale_note text,
    CONSTRAINT distress_indicator_def_pkey PRIMARY KEY (indicator_id)
);

CREATE TABLE rig.rig_capability (
    capability_id uuid DEFAULT gen_random_uuid() NOT NULL,
    rig_id uuid NOT NULL,
    valid_period daterange NOT NULL,
    max_water_depth_m numeric,
    max_water_depth_raw text,
    max_drill_depth_m numeric,
    max_drill_depth_raw text,
    loa_m numeric,
    beam_m numeric,
    depth_m numeric,
    operating_draft_m numeric,
    displacement_t numeric,
    variable_deckload_t numeric,
    station_keeping rig.station_keeping,
    thruster_count integer,
    installed_power_kw numeric,
    hookload_kn numeric,
    derrick_type text,
    dual_activity boolean,
    mud_pump_count integer,
    mud_pump_total_hp numeric,
    mud_system_volume_m3 numeric,
    riser_length_m numeric,
    riser_od_in numeric,
    bop_count integer,
    bop_pressure_rating_psi integer,
    bop_ram_count integer,
    mpd_capable boolean,
    managed_pressure_note text,
    accommodation_berths integer,
    helideck_rating text,
    moonpool_dimensions text,
    source_record_id uuid,
    confidence rig.confidence DEFAULT 'medium'::rig.confidence NOT NULL,
    hookload_raw text,
    CONSTRAINT rig_capability_pkey PRIMARY KEY (capability_id)
);

CREATE TABLE rig.rig_component (
    component_id uuid DEFAULT gen_random_uuid() NOT NULL,
    rig_id uuid NOT NULL,
    component_type_id uuid NOT NULL,
    parent_component_id uuid,
    engine_family_id uuid,
    make text,
    model_series text,
    model_variant text,
    sku text,
    serial_number text,
    quantity integer DEFAULT 1 NOT NULL,
    rating_value numeric,
    rating_unit text,
    rating_raw text,
    output_kw numeric,
    rpm integer,
    frequency_hz integer,
    voltage_kv numeric,
    phase_config text,
    manufacture_year integer,
    install_date date,
    install_date_precision text,
    removal_date date,
    is_original_equipment boolean,
    operating_hours numeric,
    operating_hours_asof date,
    hours_source_type text,
    condition rig.condition_grade DEFAULT 'unknown'::rig.condition_grade NOT NULL,
    preservation rig.preservation_state DEFAULT 'unknown'::rig.preservation_state NOT NULL,
    last_overhaul_date date,
    overhaul_interval_hours numeric,
    maintenance_history_ref text,
    fuel rig.fuel_capability DEFAULT 'unknown'::rig.fuel_capability NOT NULL,
    imo_tier text,
    epa_gate rig.emissions_gate DEFAULT 'unassessed'::rig.emissions_gate NOT NULL,
    epa_gate_note text,
    redeploy_class rig.redeployment_class DEFAULT 'unassessed'::rig.redeployment_class NOT NULL,
    extraction rig.extraction_difficulty DEFAULT 'unassessed'::rig.extraction_difficulty NOT NULL,
    extraction_cost_usd numeric,
    dry_weight_t numeric,
    footprint_m2 numeric,
    oem_lifecycle_status rig.oem_lifecycle DEFAULT 'unknown'::rig.oem_lifecycle NOT NULL,
    parts_availability text,
    oem_new_price_usd numeric,
    oem_price_asof date,
    est_recovery_value_usd numeric,
    recovery_value_method text,
    notes text,
    source_record_id uuid,
    confidence rig.confidence DEFAULT 'medium'::rig.confidence NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT rig_component_pkey PRIMARY KEY (component_id)
);

CREATE TABLE rig.rig_contract (
    contract_id uuid DEFAULT gen_random_uuid() NOT NULL,
    rig_id uuid NOT NULL,
    operator text,
    contractor text,
    country text,
    block_or_field text,
    contract_period daterange,
    dayrate_usd numeric,
    dayrate_is_estimate boolean DEFAULT false NOT NULL,
    contract_value_usd numeric,
    scope_note text,
    source_record_id uuid,
    confidence rig.confidence DEFAULT 'medium'::rig.confidence NOT NULL,
    content_hash text NOT NULL,
    superseded_by_source_record_id uuid,
    country_iso2 character(2),
    CONSTRAINT rig_contract_pkey PRIMARY KEY (contract_id)
);

CREATE TABLE rig.rig_distress_observation (
    observation_id uuid DEFAULT gen_random_uuid() NOT NULL,
    rig_id uuid NOT NULL,
    indicator_id uuid NOT NULL,
    observed_on date NOT NULL,
    raw_value numeric,
    normalised_score numeric,
    note text,
    source_record_id uuid,
    confidence rig.confidence DEFAULT 'medium'::rig.confidence NOT NULL,
    CONSTRAINT rig_distress_observation_pkey PRIMARY KEY (observation_id)
);

CREATE TABLE rig.rig_event (
    event_id uuid DEFAULT gen_random_uuid() NOT NULL,
    rig_id uuid NOT NULL,
    event_type rig.event_type NOT NULL,
    event_date date,
    event_date_precision text,
    counterparty text,
    country text,
    detail jsonb,
    source_record_id uuid,
    confidence rig.confidence DEFAULT 'medium'::rig.confidence NOT NULL,
    content_hash text NOT NULL,
    superseded_by_source_record_id uuid,
    CONSTRAINT rig_event_pkey PRIMARY KEY (event_id)
);

CREATE TABLE rig.rig_exit (
    rig_id uuid NOT NULL,
    exit_state rig.lifecycle_state NOT NULL,
    exit_date date,
    exit_date_precision text,
    exit_location text,
    converted_to text,
    source_record_id uuid,
    confidence rig.confidence DEFAULT 'medium'::rig.confidence NOT NULL,
    CONSTRAINT rig_exit_pkey PRIMARY KEY (rig_id)
);

CREATE TABLE rig.rig_identifier (
    rig_identifier_id uuid DEFAULT gen_random_uuid() NOT NULL,
    rig_id uuid NOT NULL,
    id_type rig.identifier_type NOT NULL,
    id_value text NOT NULL,
    valid_from date,
    valid_to date,
    source_record_id uuid,
    confidence rig.confidence DEFAULT 'high'::rig.confidence NOT NULL,
    CONSTRAINT rig_identifier_pkey PRIMARY KEY (rig_identifier_id)
);

CREATE TABLE rig.rig_name_alias (
    alias_id uuid DEFAULT gen_random_uuid() NOT NULL,
    rig_id uuid NOT NULL,
    name text NOT NULL,
    valid_from date,
    valid_to date,
    source_record_id uuid,
    CONSTRAINT rig_name_alias_pkey PRIMARY KEY (alias_id)
);

CREATE TABLE rig.rig_opportunity_score (
    score_id uuid DEFAULT gen_random_uuid() NOT NULL,
    rig_id uuid NOT NULL,
    scored_on date NOT NULL,
    distress_score numeric,
    component_value_score numeric,
    permittability_score numeric,
    extraction_score numeric,
    composite_score numeric,
    input_coverage_pct numeric,
    model_version text NOT NULL,
    note text,
    CONSTRAINT rig_opportunity_score_pkey PRIMARY KEY (score_id)
);

CREATE TABLE rig.rig_ownership (
    rig_ownership_id uuid DEFAULT gen_random_uuid() NOT NULL,
    rig_id uuid NOT NULL,
    entity_id uuid NOT NULL,
    role text DEFAULT 'beneficial_owner'::text NOT NULL,
    valid_period daterange NOT NULL,
    ownership_pct numeric,
    source_record_id uuid,
    confidence rig.confidence DEFAULT 'medium'::rig.confidence NOT NULL,
    CONSTRAINT rig_ownership_pkey PRIMARY KEY (rig_ownership_id)
);

CREATE TABLE rig.rig_position (
    position_id bigint DEFAULT nextval('rig.rig_position_position_id_seq'::regclass) NOT NULL,
    rig_id uuid NOT NULL,
    observed_at timestamp with time zone NOT NULL,
    geom geography(Point,4326) NOT NULL,
    sog_knots numeric,
    nav_status text,
    source_record_id uuid,
    CONSTRAINT rig_position_pkey PRIMARY KEY (position_id)
);

CREATE TABLE rig.rig_registry (
    registry_id uuid DEFAULT gen_random_uuid() NOT NULL,
    rig_id uuid NOT NULL,
    valid_period daterange NOT NULL,
    rig_name text,
    registered_owner text,
    beneficial_owner text,
    operator text,
    ism_manager text,
    flag_state text,
    port_of_registry text,
    class_society text,
    class_notations text,
    gross_tonnage numeric,
    source_record_id uuid,
    confidence rig.confidence DEFAULT 'medium'::rig.confidence NOT NULL,
    creditor_controlled boolean DEFAULT false NOT NULL,
    controlling_creditor text,
    CONSTRAINT rig_registry_pkey PRIMARY KEY (registry_id)
);

CREATE TABLE rig.rig_scrap_basis (
    rig_id uuid NOT NULL,
    lightship_ldt numeric,
    ldt_is_estimated boolean DEFAULT true NOT NULL,
    ldt_method text,
    ferrous_t numeric,
    non_ferrous_t numeric,
    copper_t numeric,
    hazmat_inventory_ref text,
    hkc_compliant_yard_req boolean,
    tow_origin_port text,
    est_tow_cost_usd numeric,
    est_yard_cost_usd numeric,
    source_record_id uuid,
    confidence rig.confidence DEFAULT 'low'::rig.confidence NOT NULL,
    CONSTRAINT rig_scrap_basis_pkey PRIMARY KEY (rig_id)
);

CREATE TABLE rig.rig_status_period (
    status_period_id uuid DEFAULT gen_random_uuid() NOT NULL,
    rig_id uuid NOT NULL,
    state rig.lifecycle_state NOT NULL,
    valid_period daterange NOT NULL,
    location_country text,
    location_note text,
    source_record_id uuid,
    confidence rig.confidence DEFAULT 'medium'::rig.confidence NOT NULL,
    location_country_iso2 character(2),
    CONSTRAINT rig_status_period_pkey PRIMARY KEY (status_period_id)
);

CREATE TABLE rig.rig_valuation (
    valuation_id uuid DEFAULT gen_random_uuid() NOT NULL,
    rig_id uuid NOT NULL,
    case_type rig.valuation_case NOT NULL,
    valued_on date NOT NULL,
    low_usd numeric,
    mid_usd numeric,
    high_usd numeric,
    currency text DEFAULT 'USD'::text NOT NULL,
    contract_ebitda_usd numeric,
    discount_rate_pct numeric,
    reactivation_capex_usd numeric,
    survey_capex_usd numeric,
    conversion_target rig.conversion_target,
    time_to_sale_months integer,
    time_discount_pct numeric,
    method_note text NOT NULL,
    key_assumptions jsonb,
    comp_set_exists boolean DEFAULT false NOT NULL,
    comp_count integer,
    model_version text NOT NULL,
    prepared_by text,
    source_record_id uuid,
    confidence rig.confidence DEFAULT 'low'::rig.confidence NOT NULL,
    CONSTRAINT rig_valuation_pkey PRIMARY KEY (valuation_id)
);

CREATE TABLE rig.comparable_transaction (
    txn_id uuid DEFAULT gen_random_uuid() NOT NULL,
    txn_type rig.txn_type NOT NULL,
    txn_date date,
    txn_date_precision text,
    rig_id uuid,
    asset_description text NOT NULL,
    seller text,
    buyer text,
    price_usd numeric,
    price_is_reported boolean DEFAULT false NOT NULL,
    ldt numeric,
    usd_per_ldt numeric,
    usd_per_kw numeric,
    distressed_process text,
    jurisdiction text,
    source_record_id uuid,
    confidence rig.confidence DEFAULT 'medium'::rig.confidence NOT NULL,
    CONSTRAINT comparable_transaction_pkey PRIMARY KEY (txn_id)
);

CREATE TABLE rig.corporate_event (
    corporate_event_id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_id uuid NOT NULL,
    counterparty_entity_id uuid,
    event_type text NOT NULL,
    event_date date,
    event_date_precision text DEFAULT 'day'::text,
    consideration_usd numeric,
    detail jsonb,
    fleet_impact_note text,
    source_record_id uuid,
    confidence rig.confidence DEFAULT 'medium'::rig.confidence NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT corporate_event_pkey PRIMARY KEY (corporate_event_id)
);

CREATE TABLE rig.field_conflict (
    conflict_id uuid DEFAULT gen_random_uuid() NOT NULL,
    rig_id uuid NOT NULL,
    table_name text NOT NULL,
    field_name text NOT NULL,
    accepted_value text,
    accepted_source uuid,
    rejected_value text,
    rejected_source uuid,
    resolution_rule text,
    resolved_by text,
    detected_at timestamp with time zone DEFAULT now() NOT NULL,
    reviewed boolean DEFAULT false NOT NULL,
    CONSTRAINT field_conflict_pkey PRIMARY KEY (conflict_id)
);

CREATE TABLE rig.harvest_buildup (
    buildup_id uuid DEFAULT gen_random_uuid() NOT NULL,
    valuation_id uuid NOT NULL,
    component_id uuid,
    line_label text NOT NULL,
    gross_recovery_usd numeric,
    extraction_cost_usd numeric,
    testing_cost_usd numeric,
    refurb_cost_usd numeric,
    aftertreatment_cost_usd numeric,
    logistics_cost_usd numeric,
    holding_months integer,
    time_discount_usd numeric,
    net_recovery_usd numeric,
    note text,
    CONSTRAINT harvest_buildup_pkey PRIMARY KEY (buildup_id)
);

CREATE TABLE rig.indicator_applicability (
    indicator_id uuid NOT NULL,
    model_version text NOT NULL,
    unit_class rig.unit_class NOT NULL,
    state_condition text,
    CONSTRAINT indicator_applicability_pkey PRIMARY KEY (indicator_id, model_version, unit_class)
);

CREATE TABLE rig.indicator_normalisation (
    indicator_id uuid NOT NULL,
    model_version text NOT NULL,
    curve text NOT NULL,
    cap numeric,
    unit text,
    ordinal_map jsonb,
    is_provisional boolean DEFAULT false NOT NULL,
    note text,
    CONSTRAINT indicator_normalisation_pkey PRIMARY KEY (indicator_id, model_version)
);

CREATE TABLE rig.power_cost_benchmark (
    benchmark_id uuid DEFAULT gen_random_uuid() NOT NULL,
    model_version text NOT NULL,
    benchmark_key text NOT NULL,
    technology text NOT NULL,
    basis text NOT NULL,
    input_kind text DEFAULT 'model_input'::text NOT NULL,
    usd_per_kw numeric NOT NULL,
    usd_per_kw_low numeric,
    usd_per_kw_high numeric,
    dollar_basis text NOT NULL,
    source_usd_per_kw numeric,
    source_dollar_year text,
    escalation_series text,
    escalation_factor numeric,
    equipment_share numeric,
    derivation_note text NOT NULL,
    is_adopted boolean DEFAULT false NOT NULL,
    source_record_id uuid NOT NULL,
    confidence rig.confidence DEFAULT 'medium'::rig.confidence NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT power_cost_benchmark_pkey PRIMARY KEY (benchmark_id)
);

CREATE TABLE rig.repurposing_assessment (
    assessment_id uuid DEFAULT gen_random_uuid() NOT NULL,
    component_id uuid NOT NULL,
    target_application text NOT NULL,
    target_market text,
    assessed_on date NOT NULL,
    gate_emissions boolean,
    gate_frequency boolean,
    gate_voltage boolean,
    gate_duty_cycle boolean,
    gate_extraction boolean,
    gate_oem_support boolean,
    gate_fuel_supply boolean,
    all_gates_pass boolean GENERATED ALWAYS AS (COALESCE(gate_emissions, false) AND COALESCE(gate_frequency, false) AND COALESCE(gate_voltage, false) AND COALESCE(gate_duty_cycle, false) AND COALESCE(gate_extraction, false) AND COALESCE(gate_oem_support, false) AND COALESCE(gate_fuel_supply, false)) STORED,
    basis_original rig.rating_basis,
    basis_target rig.rating_basis,
    derate_factor numeric,
    derated_output_kw numeric,
    fuel_conversion_path text,
    fuel_conversion_cost_usd numeric,
    aftertreatment_scope text,
    balance_of_plant_scope text,
    footprint_m2 numeric,
    install_weight_t numeric,
    retrofit_cost_usd numeric,
    lead_time_weeks integer,
    blocking_issue text,
    note text,
    source_record_id uuid,
    confidence rig.confidence DEFAULT 'low'::rig.confidence NOT NULL,
    CONSTRAINT repurposing_assessment_pkey PRIMARY KEY (assessment_id)
);

CREATE TABLE rig.watchlist (
    watchlist_id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    owner text,
    criteria jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT watchlist_pkey PRIMARY KEY (watchlist_id)
);

CREATE TABLE rig.watchlist_rig (
    watchlist_id uuid NOT NULL,
    rig_id uuid NOT NULL,
    added_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT watchlist_rig_pkey PRIMARY KEY (watchlist_id, rig_id)
);

CREATE TABLE rig.alert_rule (
    rule_id uuid DEFAULT gen_random_uuid() NOT NULL,
    rule_key text NOT NULL,
    description text NOT NULL,
    trigger_sql text NOT NULL,
    channel text DEFAULT 'email'::text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    CONSTRAINT alert_rule_pkey PRIMARY KEY (rule_id)
);

CREATE TABLE rig.alert_event (
    alert_id bigint DEFAULT nextval('rig.alert_event_alert_id_seq'::regclass) NOT NULL,
    rule_id uuid NOT NULL,
    rig_id uuid,
    fired_at timestamp with time zone DEFAULT now() NOT NULL,
    payload jsonb,
    acknowledged boolean DEFAULT false NOT NULL,
    CONSTRAINT alert_event_pkey PRIMARY KEY (alert_id)
);

CREATE TABLE rig.audit_log (
    audit_id bigint DEFAULT nextval('rig.audit_log_audit_id_seq'::regclass) NOT NULL,
    table_name text NOT NULL,
    row_pk text NOT NULL,
    operation text NOT NULL,
    old_value jsonb,
    new_value jsonb,
    actor text DEFAULT CURRENT_USER NOT NULL,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT audit_log_pkey PRIMARY KEY (audit_id)
);
-- ----------------------------------------------------------------------------
-- Constraints (FK / UNIQUE / CHECK / EXCLUDE) added after all tables exist
-- ----------------------------------------------------------------------------

ALTER TABLE rig.source ADD CONSTRAINT source_source_key_key UNIQUE (source_key);
ALTER TABLE rig.source_precedence ADD CONSTRAINT source_precedence_source_id_fkey FOREIGN KEY (source_id) REFERENCES rig.source(source_id) ON DELETE CASCADE;
ALTER TABLE rig.source_record ADD CONSTRAINT source_record_source_id_fkey FOREIGN KEY (source_id) REFERENCES rig.source(source_id);
ALTER TABLE rig.rig_design ADD CONSTRAINT rig_design_designer_design_series_design_variant_key UNIQUE (designer, design_series, design_variant);
ALTER TABLE rig.corporate_entity ADD CONSTRAINT corporate_entity_status_check CHECK ((status = ANY (ARRAY['active'::text, 'acquired'::text, 'dissolved'::text, 'in_insolvency'::text])));
ALTER TABLE rig.corporate_entity ADD CONSTRAINT corporate_entity_type_check CHECK ((entity_type = ANY (ARRAY['public_company'::text, 'private_company'::text, 'jv'::text, 'state_owned'::text, 'subsidiary'::text, 'creditor_vehicle'::text])));
ALTER TABLE rig.corporate_entity ADD CONSTRAINT corporate_entity_parent_entity_id_fkey FOREIGN KEY (parent_entity_id) REFERENCES rig.corporate_entity(entity_id);
ALTER TABLE rig.corporate_entity ADD CONSTRAINT corporate_entity_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.corporate_entity ADD CONSTRAINT corporate_entity_entity_key_key UNIQUE (entity_key);
ALTER TABLE rig.rig ADD CONSTRAINT he_jackup_needs_rationale CHECK (((unit_class <> 'jackup_he'::rig.unit_class) OR (jackup_he_criteria_met IS NOT NULL)));
ALTER TABLE rig.rig ADD CONSTRAINT rig_jackup_he_criteria_met_check CHECK (((jackup_he_criteria_met >= 0) AND (jackup_he_criteria_met <= 4)));
ALTER TABLE rig.rig ADD CONSTRAINT rig_design_id_fkey FOREIGN KEY (design_id) REFERENCES rig.rig_design(design_id);
ALTER TABLE rig.rig ADD CONSTRAINT rig_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.rig ADD CONSTRAINT rig_canonical_name_key UNIQUE (canonical_name);
ALTER TABLE rig.rig ADD CONSTRAINT rig_rig_code_key UNIQUE (rig_code);
ALTER TABLE rig.component_type ADD CONSTRAINT component_type_type_key_key UNIQUE (type_key);
ALTER TABLE rig.engine_family ADD CONSTRAINT engine_family_oem_family_key UNIQUE (oem, family);
ALTER TABLE rig.distress_indicator_def ADD CONSTRAINT distress_indicator_def_polarity_check CHECK ((polarity = ANY (ARRAY['-1'::integer, 1])));
ALTER TABLE rig.distress_indicator_def ADD CONSTRAINT distress_indicator_def_weight_check CHECK ((weight >= (0)::numeric));
ALTER TABLE rig.distress_indicator_def ADD CONSTRAINT distress_indicator_def_indicator_key_key UNIQUE (indicator_key);
ALTER TABLE rig.rig_capability ADD CONSTRAINT rig_capability_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id) ON DELETE CASCADE;
ALTER TABLE rig.rig_capability ADD CONSTRAINT rig_capability_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.rig_capability ADD CONSTRAINT rig_capability_rig_id_valid_period_excl EXCLUDE USING gist (rig_id WITH =, valid_period WITH &&);
ALTER TABLE rig.rig_component ADD CONSTRAINT hours_need_source CHECK (((operating_hours IS NULL) OR (hours_source_type IS NOT NULL)));
ALTER TABLE rig.rig_component ADD CONSTRAINT no_self_parent CHECK ((parent_component_id IS DISTINCT FROM component_id));
ALTER TABLE rig.rig_component ADD CONSTRAINT rig_component_frequency_hz_check CHECK ((frequency_hz = ANY (ARRAY[50, 60])));
ALTER TABLE rig.rig_component ADD CONSTRAINT rig_component_install_date_precision_check CHECK ((install_date_precision = ANY (ARRAY['day'::text, 'month'::text, 'quarter'::text, 'year'::text, 'unknown'::text])));
ALTER TABLE rig.rig_component ADD CONSTRAINT rig_component_component_type_id_fkey FOREIGN KEY (component_type_id) REFERENCES rig.component_type(component_type_id);
ALTER TABLE rig.rig_component ADD CONSTRAINT rig_component_engine_family_id_fkey FOREIGN KEY (engine_family_id) REFERENCES rig.engine_family(engine_family_id);
ALTER TABLE rig.rig_component ADD CONSTRAINT rig_component_parent_component_id_fkey FOREIGN KEY (parent_component_id) REFERENCES rig.rig_component(component_id);
ALTER TABLE rig.rig_component ADD CONSTRAINT rig_component_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id) ON DELETE CASCADE;
ALTER TABLE rig.rig_component ADD CONSTRAINT rig_component_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.rig_contract ADD CONSTRAINT rig_contract_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id) ON DELETE CASCADE;
ALTER TABLE rig.rig_contract ADD CONSTRAINT rig_contract_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.rig_contract ADD CONSTRAINT rig_contract_superseded_by_source_record_id_fkey FOREIGN KEY (superseded_by_source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.rig_distress_observation ADD CONSTRAINT rig_distress_observation_normalised_score_check CHECK (((normalised_score >= (0)::numeric) AND (normalised_score <= (1)::numeric)));
ALTER TABLE rig.rig_distress_observation ADD CONSTRAINT rig_distress_observation_indicator_id_fkey FOREIGN KEY (indicator_id) REFERENCES rig.distress_indicator_def(indicator_id);
ALTER TABLE rig.rig_distress_observation ADD CONSTRAINT rig_distress_observation_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id) ON DELETE CASCADE;
ALTER TABLE rig.rig_distress_observation ADD CONSTRAINT rig_distress_observation_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.rig_distress_observation ADD CONSTRAINT rig_distress_observation_rig_id_indicator_id_observed_on_key UNIQUE (rig_id, indicator_id, observed_on);
ALTER TABLE rig.rig_event ADD CONSTRAINT rig_event_event_date_precision_check CHECK ((event_date_precision = ANY (ARRAY['day'::text, 'month'::text, 'quarter'::text, 'year'::text, 'unknown'::text])));
ALTER TABLE rig.rig_event ADD CONSTRAINT rig_event_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id) ON DELETE CASCADE;
ALTER TABLE rig.rig_event ADD CONSTRAINT rig_event_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.rig_event ADD CONSTRAINT rig_event_superseded_by_source_record_id_fkey FOREIGN KEY (superseded_by_source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.rig_exit ADD CONSTRAINT rig_exit_exit_date_precision_check CHECK ((exit_date_precision = ANY (ARRAY['day'::text, 'month'::text, 'quarter'::text, 'year'::text, 'unknown'::text])));
ALTER TABLE rig.rig_exit ADD CONSTRAINT rig_exit_exit_state_check CHECK ((exit_state = ANY (ARRAY['scrapped'::rig.lifecycle_state, 'converted'::rig.lifecycle_state, 'total_loss'::rig.lifecycle_state, 'sold_out_of_segment'::rig.lifecycle_state])));
ALTER TABLE rig.rig_exit ADD CONSTRAINT rig_exit_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id) ON DELETE CASCADE;
ALTER TABLE rig.rig_exit ADD CONSTRAINT rig_exit_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.rig_identifier ADD CONSTRAINT rig_identifier_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id) ON DELETE CASCADE;
ALTER TABLE rig.rig_identifier ADD CONSTRAINT rig_identifier_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.rig_identifier ADD CONSTRAINT rig_identifier_id_type_id_value_rig_id_key UNIQUE (id_type, id_value, rig_id);
ALTER TABLE rig.rig_name_alias ADD CONSTRAINT rig_name_alias_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id) ON DELETE CASCADE;
ALTER TABLE rig.rig_name_alias ADD CONSTRAINT rig_name_alias_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.rig_opportunity_score ADD CONSTRAINT rig_opportunity_score_component_value_score_check CHECK (((component_value_score >= (0)::numeric) AND (component_value_score <= (100)::numeric)));
ALTER TABLE rig.rig_opportunity_score ADD CONSTRAINT rig_opportunity_score_composite_score_check CHECK (((composite_score >= (0)::numeric) AND (composite_score <= (100)::numeric)));
ALTER TABLE rig.rig_opportunity_score ADD CONSTRAINT rig_opportunity_score_distress_score_check CHECK (((distress_score >= (0)::numeric) AND (distress_score <= (100)::numeric)));
ALTER TABLE rig.rig_opportunity_score ADD CONSTRAINT rig_opportunity_score_extraction_score_check CHECK (((extraction_score >= (0)::numeric) AND (extraction_score <= (100)::numeric)));
ALTER TABLE rig.rig_opportunity_score ADD CONSTRAINT rig_opportunity_score_input_coverage_pct_check CHECK (((input_coverage_pct >= (0)::numeric) AND (input_coverage_pct <= (100)::numeric)));
ALTER TABLE rig.rig_opportunity_score ADD CONSTRAINT rig_opportunity_score_permittability_score_check CHECK (((permittability_score >= (0)::numeric) AND (permittability_score <= (100)::numeric)));
ALTER TABLE rig.rig_opportunity_score ADD CONSTRAINT rig_opportunity_score_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id) ON DELETE CASCADE;
ALTER TABLE rig.rig_opportunity_score ADD CONSTRAINT rig_opportunity_score_rig_id_scored_on_model_version_key UNIQUE (rig_id, scored_on, model_version);
ALTER TABLE rig.rig_ownership ADD CONSTRAINT rig_ownership_role_check CHECK ((role = ANY (ARRAY['beneficial_owner'::text, 'registered_owner'::text, 'bareboat_charterer'::text, 'manager'::text, 'operator'::text])));
ALTER TABLE rig.rig_ownership ADD CONSTRAINT rig_ownership_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES rig.corporate_entity(entity_id);
ALTER TABLE rig.rig_ownership ADD CONSTRAINT rig_ownership_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id) ON DELETE CASCADE;
ALTER TABLE rig.rig_ownership ADD CONSTRAINT rig_ownership_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.rig_ownership ADD CONSTRAINT rig_ownership_rig_id_role_valid_period_excl EXCLUDE USING gist (rig_id WITH =, role WITH =, valid_period WITH &&);
ALTER TABLE rig.rig_position ADD CONSTRAINT rig_position_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id) ON DELETE CASCADE;
ALTER TABLE rig.rig_position ADD CONSTRAINT rig_position_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.rig_registry ADD CONSTRAINT rig_registry_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id) ON DELETE CASCADE;
ALTER TABLE rig.rig_registry ADD CONSTRAINT rig_registry_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.rig_registry ADD CONSTRAINT rig_registry_rig_id_valid_period_excl EXCLUDE USING gist (rig_id WITH =, valid_period WITH &&);
ALTER TABLE rig.rig_scrap_basis ADD CONSTRAINT rig_scrap_basis_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id) ON DELETE CASCADE;
ALTER TABLE rig.rig_scrap_basis ADD CONSTRAINT rig_scrap_basis_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.rig_status_period ADD CONSTRAINT rig_status_period_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id) ON DELETE CASCADE;
ALTER TABLE rig.rig_status_period ADD CONSTRAINT rig_status_period_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.rig_status_period ADD CONSTRAINT rig_status_period_rig_id_valid_period_excl EXCLUDE USING gist (rig_id WITH =, valid_period WITH &&);
ALTER TABLE rig.rig_valuation ADD CONSTRAINT rig_valuation_check CHECK (((low_usd IS NULL) OR (mid_usd IS NULL) OR (low_usd <= mid_usd)));
ALTER TABLE rig.rig_valuation ADD CONSTRAINT rig_valuation_check1 CHECK (((mid_usd IS NULL) OR (high_usd IS NULL) OR (mid_usd <= high_usd)));
ALTER TABLE rig.rig_valuation ADD CONSTRAINT rig_valuation_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id) ON DELETE CASCADE;
ALTER TABLE rig.rig_valuation ADD CONSTRAINT rig_valuation_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.rig_valuation ADD CONSTRAINT rig_valuation_rig_id_case_type_valued_on_model_version_key UNIQUE (rig_id, case_type, valued_on, model_version);
ALTER TABLE rig.comparable_transaction ADD CONSTRAINT comparable_transaction_txn_date_precision_check CHECK ((txn_date_precision = ANY (ARRAY['day'::text, 'month'::text, 'quarter'::text, 'year'::text, 'unknown'::text])));
ALTER TABLE rig.comparable_transaction ADD CONSTRAINT comparable_transaction_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id);
ALTER TABLE rig.comparable_transaction ADD CONSTRAINT comparable_transaction_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.corporate_event ADD CONSTRAINT corporate_event_event_date_precision_check CHECK ((event_date_precision = ANY (ARRAY['day'::text, 'month'::text, 'quarter'::text, 'year'::text, 'unknown'::text])));
ALTER TABLE rig.corporate_event ADD CONSTRAINT corporate_event_counterparty_entity_id_fkey FOREIGN KEY (counterparty_entity_id) REFERENCES rig.corporate_entity(entity_id);
ALTER TABLE rig.corporate_event ADD CONSTRAINT corporate_event_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES rig.corporate_entity(entity_id) ON DELETE CASCADE;
ALTER TABLE rig.corporate_event ADD CONSTRAINT corporate_event_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.field_conflict ADD CONSTRAINT field_conflict_accepted_source_fkey FOREIGN KEY (accepted_source) REFERENCES rig.source(source_id);
ALTER TABLE rig.field_conflict ADD CONSTRAINT field_conflict_rejected_source_fkey FOREIGN KEY (rejected_source) REFERENCES rig.source(source_id);
ALTER TABLE rig.field_conflict ADD CONSTRAINT field_conflict_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id) ON DELETE CASCADE;
ALTER TABLE rig.harvest_buildup ADD CONSTRAINT harvest_buildup_component_id_fkey FOREIGN KEY (component_id) REFERENCES rig.rig_component(component_id);
ALTER TABLE rig.harvest_buildup ADD CONSTRAINT harvest_buildup_valuation_id_fkey FOREIGN KEY (valuation_id) REFERENCES rig.rig_valuation(valuation_id) ON DELETE CASCADE;
ALTER TABLE rig.indicator_applicability ADD CONSTRAINT indicator_applicability_state_condition_check CHECK ((state_condition = ANY (ARRAY['stacked'::text, 'cold_stacked'::text])));
ALTER TABLE rig.indicator_applicability ADD CONSTRAINT indicator_applicability_indicator_id_fkey FOREIGN KEY (indicator_id) REFERENCES rig.distress_indicator_def(indicator_id);
ALTER TABLE rig.indicator_normalisation ADD CONSTRAINT indicator_normalisation_cap_check CHECK (((cap IS NULL) OR (cap > (0)::numeric)));
ALTER TABLE rig.indicator_normalisation ADD CONSTRAINT indicator_normalisation_check CHECK (((curve <> 'linear_capped'::text) OR (cap IS NOT NULL)));
ALTER TABLE rig.indicator_normalisation ADD CONSTRAINT indicator_normalisation_check1 CHECK (((curve <> 'ordinal'::text) OR (ordinal_map IS NOT NULL)));
ALTER TABLE rig.indicator_normalisation ADD CONSTRAINT indicator_normalisation_curve_check CHECK ((curve = ANY (ARRAY['linear_capped'::text, 'ordinal'::text, 'binary'::text])));
ALTER TABLE rig.indicator_normalisation ADD CONSTRAINT indicator_normalisation_indicator_id_fkey FOREIGN KEY (indicator_id) REFERENCES rig.distress_indicator_def(indicator_id);
ALTER TABLE rig.power_cost_benchmark ADD CONSTRAINT power_cost_benchmark_band CHECK (((usd_per_kw_low IS NULL) OR (usd_per_kw_high IS NULL) OR ((usd_per_kw_low <= usd_per_kw) AND (usd_per_kw <= usd_per_kw_high))));
ALTER TABLE rig.power_cost_benchmark ADD CONSTRAINT power_cost_benchmark_basis_check CHECK ((basis = ANY (ARRAY['installed_plant'::text, 'prime_equipment'::text, 'all_equipment'::text])));
ALTER TABLE rig.power_cost_benchmark ADD CONSTRAINT power_cost_benchmark_equipment_share_check CHECK (((equipment_share > (0)::numeric) AND (equipment_share <= (1)::numeric)));
ALTER TABLE rig.power_cost_benchmark ADD CONSTRAINT power_cost_benchmark_escalation_factor_check CHECK ((escalation_factor > (0)::numeric));
ALTER TABLE rig.power_cost_benchmark ADD CONSTRAINT power_cost_benchmark_input_kind_check CHECK ((input_kind = 'model_input'::text));
ALTER TABLE rig.power_cost_benchmark ADD CONSTRAINT power_cost_benchmark_source_usd_per_kw_check CHECK ((source_usd_per_kw > (0)::numeric));
ALTER TABLE rig.power_cost_benchmark ADD CONSTRAINT power_cost_benchmark_usd_per_kw_check CHECK ((usd_per_kw > (0)::numeric));
ALTER TABLE rig.power_cost_benchmark ADD CONSTRAINT power_cost_benchmark_usd_per_kw_high_check CHECK ((usd_per_kw_high > (0)::numeric));
ALTER TABLE rig.power_cost_benchmark ADD CONSTRAINT power_cost_benchmark_usd_per_kw_low_check CHECK ((usd_per_kw_low > (0)::numeric));
ALTER TABLE rig.power_cost_benchmark ADD CONSTRAINT power_cost_benchmark_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.power_cost_benchmark ADD CONSTRAINT power_cost_benchmark_nk UNIQUE (model_version, benchmark_key);
ALTER TABLE rig.repurposing_assessment ADD CONSTRAINT repurposing_assessment_derate_factor_check CHECK (((derate_factor > (0)::numeric) AND (derate_factor <= 1.5)));
ALTER TABLE rig.repurposing_assessment ADD CONSTRAINT repurposing_assessment_component_id_fkey FOREIGN KEY (component_id) REFERENCES rig.rig_component(component_id) ON DELETE CASCADE;
ALTER TABLE rig.repurposing_assessment ADD CONSTRAINT repurposing_assessment_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES rig.source_record(source_record_id);
ALTER TABLE rig.watchlist_rig ADD CONSTRAINT watchlist_rig_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id) ON DELETE CASCADE;
ALTER TABLE rig.watchlist_rig ADD CONSTRAINT watchlist_rig_watchlist_id_fkey FOREIGN KEY (watchlist_id) REFERENCES rig.watchlist(watchlist_id) ON DELETE CASCADE;
ALTER TABLE rig.alert_rule ADD CONSTRAINT alert_rule_rule_key_key UNIQUE (rule_key);
ALTER TABLE rig.alert_event ADD CONSTRAINT alert_event_rig_id_fkey FOREIGN KEY (rig_id) REFERENCES rig.rig(rig_id);
ALTER TABLE rig.alert_event ADD CONSTRAINT alert_event_rule_id_fkey FOREIGN KEY (rule_id) REFERENCES rig.alert_rule(rule_id);

-- ----------------------------------------------------------------------------
-- Indexes (excludes those already created implicitly by PK/UNIQUE constraints)
-- ----------------------------------------------------------------------------

CREATE INDEX idx_alert_unack ON rig.alert_event USING btree (fired_at DESC) WHERE (NOT acknowledged);
CREATE INDEX idx_comp_txn ON rig.comparable_transaction USING btree (txn_type, txn_date DESC);
CREATE INDEX idx_component_type_tier ON rig.component_type USING btree (tier);
CREATE INDEX corporate_event_entity_id_event_date_idx ON rig.corporate_event USING btree (entity_id, event_date);
CREATE INDEX idx_conflict_unreviewed ON rig.field_conflict USING btree (detected_at DESC) WHERE (NOT reviewed);
CREATE INDEX idx_repurpose_pass ON rig.repurposing_assessment USING btree (target_application) WHERE all_gates_pass;
CREATE INDEX idx_rig_class ON rig.rig USING btree (unit_class) WHERE core_scope;
CREATE INDEX idx_rig_name_trgm ON rig.rig USING gin (canonical_name gin_trgm_ops);
CREATE INDEX idx_component_makemodel ON rig.rig_component USING btree (make, model_series);
CREATE INDEX idx_component_permit ON rig.rig_component USING btree (epa_gate) WHERE (epa_gate = ANY (ARRAY['us_permittable_as_is'::rig.emissions_gate, 'us_permittable_with_scr'::rig.emissions_gate, 'us_nonroad_or_temporary'::rig.emissions_gate]));
CREATE INDEX idx_component_rig ON rig.rig_component USING btree (rig_id);
CREATE INDEX idx_component_tier_a ON rig.rig_component USING btree (rig_id) WHERE (redeploy_class = 'tier_a'::rig.redeployment_class);
CREATE INDEX idx_component_type ON rig.rig_component USING btree (component_type_id);
CREATE INDEX idx_contract_period ON rig.rig_contract USING gist (contract_period);
CREATE INDEX idx_contract_rig ON rig.rig_contract USING btree (rig_id);
CREATE UNIQUE INDEX rig_contract_nk ON rig.rig_contract USING btree (rig_id, content_hash);
CREATE INDEX idx_event_rig_date ON rig.rig_event USING btree (rig_id, event_date DESC);
CREATE INDEX idx_event_type ON rig.rig_event USING btree (event_type, event_date DESC);
CREATE UNIQUE INDEX rig_event_nk ON rig.rig_event USING btree (rig_id, content_hash);
CREATE UNIQUE INDEX idx_imo_unique ON rig.rig_identifier USING btree (id_value) WHERE (id_type = 'imo'::rig.identifier_type);
CREATE INDEX idx_rig_identifier_lookup ON rig.rig_identifier USING btree (id_type, id_value);
CREATE INDEX idx_alias_trgm ON rig.rig_name_alias USING gin (name gin_trgm_ops);
CREATE INDEX idx_opp_score ON rig.rig_opportunity_score USING btree (composite_score DESC, scored_on DESC);
CREATE INDEX rig_ownership_entity_id_idx ON rig.rig_ownership USING btree (entity_id);
CREATE INDEX idx_position_geom ON rig.rig_position USING gist (geom);
CREATE INDEX idx_position_rig_time ON rig.rig_position USING btree (rig_id, observed_at DESC);
CREATE INDEX idx_status_current ON rig.rig_status_period USING btree (rig_id) WHERE upper_inf(valid_period);
CREATE INDEX idx_valuation_rig_case ON rig.rig_valuation USING btree (rig_id, case_type, valued_on DESC);
CREATE INDEX idx_source_record_source ON rig.source_record USING btree (source_id, retrieved_at DESC);

-- ----------------------------------------------------------------------------
-- Views (dependency order)
-- ----------------------------------------------------------------------------

CREATE OR REPLACE VIEW rig.v_rig_tier_a_power AS
WITH tier_a AS (
         SELECT c.rig_id,
            c.component_id,
            c.parent_component_id,
            c.quantity,
            c.output_kw,
            ct.type_key
           FROM (rig.rig_component c
             JOIN rig.component_type ct ON ((ct.component_type_id = c.component_type_id)))
          WHERE ((ct.tier = 'A_power_electrical'::rig.component_tier) AND (c.removal_date IS NULL))
        ), superseded AS (
         SELECT DISTINCT a.parent_component_id AS component_id
           FROM tier_a a
          WHERE ((a.parent_component_id IS NOT NULL) AND (a.output_kw IS NOT NULL))
        ), counted AS (
         SELECT t.rig_id,
            t.component_id,
            t.parent_component_id,
            t.quantity,
            t.output_kw,
            t.type_key,
            (s.component_id IS NOT NULL) AS is_superseded
           FROM (tier_a t
             LEFT JOIN superseded s ON ((s.component_id = t.component_id)))
        )
 SELECT rig_id,
    sum(((quantity)::numeric * output_kw)) FILTER (WHERE (NOT is_superseded)) AS tier_a_kw,
    count(*) AS tier_a_rows,
    count(*) FILTER (WHERE ((NOT is_superseded) AND (output_kw IS NOT NULL))) AS tier_a_rated_rows,
    sum(((quantity)::numeric * output_kw)) FILTER (WHERE is_superseded) AS double_count_avoided_kw,
        CASE
            WHEN (sum(((quantity)::numeric * output_kw)) FILTER (WHERE (NOT is_superseded)) IS NULL) THEN 'no rating recorded'::text
            WHEN (bool_or(((NOT is_superseded) AND (output_kw IS NOT NULL) AND (type_key = ANY (ARRAY['generator'::text, 'emergency_genset'::text])))) AND bool_or(((NOT is_superseded) AND (output_kw IS NOT NULL) AND (type_key = ANY (ARRAY['main_engine'::text, 'aux_engine'::text]))))) THEN 'mixed: electrical where an alternator is rated, mechanical elsewhere'::text
            WHEN bool_or(((NOT is_superseded) AND (output_kw IS NOT NULL) AND (type_key = ANY (ARRAY['main_engine'::text, 'aux_engine'::text])))) THEN 'mechanical (prime-mover rating; no rated alternator recorded)'::text
            ELSE 'electrical (alternator / genset rating)'::text
        END AS tier_a_kw_basis
   FROM counted
  GROUP BY rig_id;

CREATE OR REPLACE VIEW rig.coverage_by_era_class AS
 SELECT r.unit_class,
    sr.era,
    count(DISTINCT r.rig_id) AS rig_count,
    round(((100.0 * (count(DISTINCT c.rig_id))::numeric) / (NULLIF(count(DISTINCT r.rig_id), 0))::numeric), 1) AS pct_with_capability
   FROM ((rig.rig r
     LEFT JOIN rig.source_record sr ON ((sr.source_record_id = r.source_record_id)))
     LEFT JOIN rig.rig_capability c ON ((c.rig_id = r.rig_id)))
  GROUP BY r.unit_class, sr.era;

CREATE OR REPLACE VIEW rig.qa_implausible AS
 SELECT c.rig_id,
    r.canonical_name,
    'installed_power vs thruster_count'::text AS issue
   FROM (rig.rig_capability c
     JOIN rig.rig r USING (rig_id))
  WHERE ((c.thruster_count > 0) AND (c.installed_power_kw IS NOT NULL) AND (((c.installed_power_kw / (c.thruster_count)::numeric) < (800)::numeric) OR ((c.installed_power_kw / (c.thruster_count)::numeric) > (12000)::numeric)))
UNION ALL
 SELECT c.rig_id,
    r.canonical_name,
    'vdl exceeds displacement'::text AS issue
   FROM (rig.rig_capability c
     JOIN rig.rig r USING (rig_id))
  WHERE ((c.variable_deckload_t IS NOT NULL) AND (c.displacement_t IS NOT NULL) AND (c.variable_deckload_t > (c.displacement_t * 0.5)))
UNION ALL
 SELECT c.rig_id,
    r.canonical_name,
    'water depth exceeds plausible range for unit_class'::text AS issue
   FROM (rig.rig_capability c
     JOIN rig.rig r USING (rig_id))
  WHERE ((r.unit_class = 'jackup_he'::rig.unit_class) AND (c.max_water_depth_m > (200)::numeric))
UNION ALL
 SELECT r.rig_id,
    r.canonical_name,
    'delivery date precedes keel laid'::text AS issue
   FROM rig.rig r
  WHERE ((r.delivery_date IS NOT NULL) AND (r.keel_laid_date IS NOT NULL) AND (r.delivery_date < r.keel_laid_date));

CREATE OR REPLACE VIEW rig.v_fleet_current AS
 SELECT r.rig_id,
    r.canonical_name,
    r.unit_class,
    r.core_scope,
    d.designer,
    d.design_series,
    d.generation,
    reg.operator,
    reg.flag_state,
    reg.class_society,
    sp.state,
    sp.location_country,
    cap.max_water_depth_m,
    cap.station_keeping,
    cap.installed_power_kw
   FROM ((((rig.rig r
     LEFT JOIN rig.rig_design d ON ((d.design_id = r.design_id)))
     LEFT JOIN rig.rig_registry reg ON (((reg.rig_id = r.rig_id) AND upper_inf(reg.valid_period))))
     LEFT JOIN rig.rig_status_period sp ON (((sp.rig_id = r.rig_id) AND upper_inf(sp.valid_period))))
     LEFT JOIN rig.rig_capability cap ON (((cap.rig_id = r.rig_id) AND upper_inf(cap.valid_period))))
  WHERE (NOT (EXISTS ( SELECT 1
           FROM rig.rig_exit e
          WHERE (e.rig_id = r.rig_id))));

CREATE OR REPLACE VIEW rig.v_harvest_data_gaps AS
 SELECT r.unit_class,
    count(DISTINCT r.rig_id) AS rigs,
    round(((100.0 * (count(DISTINCT
        CASE
            WHEN (ct.tier = 'A_power_electrical'::rig.component_tier) THEN r.rig_id
            ELSE NULL::uuid
        END))::numeric) / (NULLIF(count(DISTINCT r.rig_id), 0))::numeric), 1) AS pct_with_power_inventory,
    round(((100.0 * (count(DISTINCT
        CASE
            WHEN (c.operating_hours IS NOT NULL) THEN r.rig_id
            ELSE NULL::uuid
        END))::numeric) / (NULLIF(count(DISTINCT r.rig_id), 0))::numeric), 1) AS pct_with_any_hours,
    round(((100.0 * (count(DISTINCT
        CASE
            WHEN (c.condition <> 'unknown'::rig.condition_grade) THEN r.rig_id
            ELSE NULL::uuid
        END))::numeric) / (NULLIF(count(DISTINCT r.rig_id), 0))::numeric), 1) AS pct_with_condition,
    round(((100.0 * (count(DISTINCT
        CASE
            WHEN (c.epa_gate <> 'unassessed'::rig.emissions_gate) THEN r.rig_id
            ELSE NULL::uuid
        END))::numeric) / (NULLIF(count(DISTINCT r.rig_id), 0))::numeric), 1) AS pct_emissions_assessed,
    round(((100.0 * (count(DISTINCT
        CASE
            WHEN (c.serial_number IS NOT NULL) THEN r.rig_id
            ELSE NULL::uuid
        END))::numeric) / (NULLIF(count(DISTINCT r.rig_id), 0))::numeric), 1) AS pct_with_serials
   FROM ((rig.rig r
     LEFT JOIN rig.rig_component c ON ((c.rig_id = r.rig_id)))
     LEFT JOIN rig.component_type ct ON ((ct.component_type_id = c.component_type_id)))
  GROUP BY r.unit_class;

CREATE OR REPLACE VIEW rig.v_scrap_per_kw AS
WITH class_power AS (
         SELECT r.unit_class,
            count(*) AS n_rigs_with_kw,
            round((percentile_cont((0.5)::double precision) WITHIN GROUP (ORDER BY ((p.tier_a_kw)::double precision)))::numeric) AS median_tier_a_kw,
            round(min(p.tier_a_kw)) AS min_tier_a_kw,
            round(max(p.tier_a_kw)) AS max_tier_a_kw
           FROM (rig.v_rig_tier_a_power p
             JOIN rig.rig r USING (rig_id))
          WHERE (p.tier_a_kw IS NOT NULL)
          GROUP BY r.unit_class
        ), deals AS (
         SELECT v.deal,
            v.unit_class,
            v.units,
            v.total_usd,
            v.per_unit_usd,
            v.process,
            v.txn_date
           FROM ( VALUES ('Transocean 6 UDW floaters'::text,'drillship'::text,6,(71000000)::numeric,(11833333)::numeric,'recycling'::text,'2025-12-31'::date), ('Discoverer India'::text,'drillship'::text,1,14000000,14000000,'recycling'::text,'2026-01-01'::date), ('Pacific Scirocco'::text,'drillship'::text,1,15600000,15600000,'going concern'::text,'2025-06-01'::date), ('Valaris DPS-3/5/6 (net)'::text,'semisub'::text,3,7800000,2600000,'recycling'::text,'2025-04-01'::date), ('Valaris DPS-3/5/6 (gross cash)'::text,'semisub'::text,3,10000000,3333333,'recycling'::text,'2025-04-01'::date), ('Ocean Apex (1976 built)'::text,'semisub'::text,1,5100000,5100000,'distressed'::text,'2026-07-01'::date), ('Deepsea Bollsta (incl. backlog)'::text,'semisub'::text,1,480000000,480000000,'going concern'::text,'2025-12-15'::date), ('Valaris 102 + 145'::text,'jackup_benign'::text,2,500000,250000,'recycling'::text,'2025-12-01'::date), ('Valaris 75'::text,'jackup_benign'::text,1,23800000,23800000,'going concern'::text,'2025-01-01'::date), ('Valaris 247 (premium)'::text,'jackup_benign'::text,1,103900000,103900000,'going concern'::text,'2025-08-01'::date), ('Noble Resolve (agreed)'::text,'jackup_benign'::text,1,64000000,64000000,'going concern'::text,'2026-04-01'::date)) v(deal, unit_class, units, total_usd, per_unit_usd, process, txn_date)
        )
 SELECT d.deal,
    d.unit_class,
    d.process,
    d.txn_date,
    d.units,
    d.total_usd,
    d.per_unit_usd,
    c.median_tier_a_kw,
    round((d.per_unit_usd / NULLIF(c.median_tier_a_kw, (0)::numeric)), 0) AS implied_usd_per_kw,
    c.n_rigs_with_kw AS kw_sample_size,
    c.min_tier_a_kw,
    c.max_tier_a_kw,
    ((('CLASS-MEDIAN DENOMINATOR, not this unit''s own installed power. The kW comes from '::text || c.n_rigs_with_kw) || ' OTHER rigs of the same unit_class that carry component-level ratings '::text) || '(sister-unit generalisation, par.17, flagged medium). The transacted unit''s own installed power is NOT known.'::text) AS kw_basis_caveat
   FROM (deals d
     LEFT JOIN class_power c ON ((c.unit_class = (d.unit_class)::rig.unit_class)))
  ORDER BY d.unit_class, d.process, d.per_unit_usd;

CREATE OR REPLACE VIEW rig.v_power_arbitrage AS
WITH b AS (
         SELECT power_cost_benchmark.usd_per_kw,
            power_cost_benchmark.usd_per_kw_low,
            power_cost_benchmark.usd_per_kw_high,
            power_cost_benchmark.model_version,
            power_cost_benchmark.dollar_basis
           FROM rig.power_cost_benchmark
          WHERE (power_cost_benchmark.is_adopted AND (power_cost_benchmark.basis = 'prime_equipment'::text))
          ORDER BY power_cost_benchmark.model_version DESC
         LIMIT 1
        )
 SELECT v.deal,
    v.unit_class,
    v.process,
    v.txn_date,
    v.units,
    v.total_usd,
    v.per_unit_usd,
    v.median_tier_a_kw,
    v.kw_sample_size,
    round(v.implied_usd_per_kw) AS acq_usd_per_kw,
    b.usd_per_kw AS new_equip_usd_per_kw,
    b.dollar_basis AS benchmark_dollar_basis,
    b.model_version AS benchmark_version,
    round(((100.0 * v.implied_usd_per_kw) / b.usd_per_kw), 1) AS pct_of_new_equipment,
    round((b.usd_per_kw / v.implied_usd_per_kw), 2) AS discount_to_new_x,
    (v.implied_usd_per_kw < b.usd_per_kw) AS below_new_equipment_cost,
    v.kw_basis_caveat
   FROM (rig.v_scrap_per_kw v
     CROSS JOIN b)
  WHERE (v.implied_usd_per_kw IS NOT NULL);

CREATE OR REPLACE VIEW rig.v_power_replacement_cost AS
WITH b AS (
         SELECT power_cost_benchmark.usd_per_kw,
            power_cost_benchmark.usd_per_kw_low,
            power_cost_benchmark.usd_per_kw_high,
            power_cost_benchmark.dollar_basis,
            power_cost_benchmark.model_version
           FROM rig.power_cost_benchmark
          WHERE (power_cost_benchmark.is_adopted AND (power_cost_benchmark.basis = 'prime_equipment'::text))
          ORDER BY power_cost_benchmark.model_version DESC
         LIMIT 1
        )
 SELECT r.rig_id,
    r.canonical_name,
    r.unit_class,
    r.core_scope,
    p.tier_a_kw,
    p.tier_a_kw_basis,
    b.model_version AS benchmark_version,
    b.dollar_basis,
    b.usd_per_kw AS benchmark_usd_per_kw,
    round((p.tier_a_kw * b.usd_per_kw)) AS replacement_cost_usd,
    round((p.tier_a_kw * b.usd_per_kw_low)) AS replacement_cost_low_usd,
    round((p.tier_a_kw * b.usd_per_kw_high)) AS replacement_cost_high_usd,
    x.exit_state,
    s.state AS current_state
   FROM ((((rig.rig r
     JOIN rig.v_rig_tier_a_power p ON (((p.rig_id = r.rig_id) AND (p.tier_a_kw > (0)::numeric))))
     CROSS JOIN b)
     LEFT JOIN rig.rig_exit x ON ((x.rig_id = r.rig_id)))
     LEFT JOIN rig.rig_status_period s ON (((s.rig_id = r.rig_id) AND upper_inf(s.valid_period))));

CREATE OR REPLACE VIEW rig.v_harvest_targets AS
 SELECT r.rig_id,
    r.canonical_name,
    r.unit_class,
    d.design_series,
    r.delivery_date,
    sp.state,
    sp.location_country,
    os.composite_score,
    os.distress_score,
    os.permittability_score,
    os.input_coverage_pct,
    hv.mid_usd AS harvest_value_mid_usd,
    sv.mid_usd AS scrap_floor_mid_usd,
    (hv.mid_usd - COALESCE(sv.mid_usd, (0)::numeric)) AS harvest_premium_over_scrap_usd,
    pw.tier_a_kw,
    pw.tier_a_kw_basis,
    pw.double_count_avoided_kw,
    agg.tier_a_units,
    agg.pct_hours_known
   FROM (((((((rig.rig r
     LEFT JOIN rig.rig_design d ON ((d.design_id = r.design_id)))
     LEFT JOIN rig.rig_status_period sp ON (((sp.rig_id = r.rig_id) AND upper_inf(sp.valid_period))))
     LEFT JOIN rig.v_rig_tier_a_power pw ON ((pw.rig_id = r.rig_id)))
     LEFT JOIN LATERAL ( SELECT o.distress_score,
            o.component_value_score,
            o.permittability_score,
            o.extraction_score,
            o.composite_score,
            o.input_coverage_pct,
            o.model_version,
            o.note
           FROM rig.rig_opportunity_score o
          WHERE (o.rig_id = r.rig_id)
          ORDER BY o.scored_on DESC
         LIMIT 1) os ON (true))
     LEFT JOIN LATERAL ( SELECT v.mid_usd
           FROM rig.rig_valuation v
          WHERE ((v.rig_id = r.rig_id) AND (v.case_type = 'component_harvest'::rig.valuation_case))
          ORDER BY v.valued_on DESC
         LIMIT 1) hv ON (true))
     LEFT JOIN LATERAL ( SELECT v.mid_usd
           FROM rig.rig_valuation v
          WHERE ((v.rig_id = r.rig_id) AND (v.case_type = 'scrap_floor'::rig.valuation_case))
          ORDER BY v.valued_on DESC
         LIMIT 1) sv ON (true))
     LEFT JOIN LATERAL ( SELECT count(*) AS tier_a_units,
            round(((100.0 * (count(c.operating_hours))::numeric) / (NULLIF(count(*), 0))::numeric), 1) AS pct_hours_known
           FROM (rig.rig_component c
             JOIN rig.component_type ct ON ((ct.component_type_id = c.component_type_id)))
          WHERE ((c.rig_id = r.rig_id) AND (ct.tier = 'A_power_electrical'::rig.component_tier) AND (c.removal_date IS NULL))) agg ON (true))
  WHERE ((sp.state = ANY (ARRAY['cold_stacked'::rig.lifecycle_state, 'warm_stacked'::rig.lifecycle_state, 'under_construction'::rig.lifecycle_state, 'unknown'::rig.lifecycle_state])) OR (EXISTS ( SELECT 1
           FROM rig.rig_exit e
          WHERE ((e.rig_id = r.rig_id) AND (e.exit_state = ANY (ARRAY['scrapped'::rig.lifecycle_state, 'sold_out_of_segment'::rig.lifecycle_state]))))));

CREATE OR REPLACE VIEW rig.v_distress_ranking AS
 SELECT r.rig_id,
    r.canonical_name,
    r.unit_class,
    r.core_scope,
    sp.state,
    e.short_name AS beneficial_owner,
    o.distress_score,
    o.input_coverage_pct,
    round(LEAST(1.0, (o.input_coverage_pct / 40.0)), 4) AS coverage_confidence,
    round((o.distress_score * LEAST(1.0, (o.input_coverage_pct / 40.0))), 2) AS screen_rank_score,
    ( SELECT count(DISTINCT ob.indicator_id) AS count
           FROM rig.rig_distress_observation ob
          WHERE ((ob.rig_id = r.rig_id) AND (ob.raw_value IS NOT NULL))) AS indicators_observed,
    (o.input_coverage_pct >= (40)::numeric) AS rankable,
        CASE
            WHEN (o.input_coverage_pct >= (40)::numeric) THEN 'rankable'::text
            WHEN (o.input_coverage_pct >= (20)::numeric) THEN 'indicative only -- below the 40% coverage floor'::text
            ELSE 'not rankable -- coverage under 20%, the score is a mean of one or two observations'::text
        END AS evidence_grade,
    p.tier_a_kw,
    p.tier_a_kw_basis,
    o.composite_score,
    o.model_version,
    o.scored_on
   FROM (((((rig.rig_opportunity_score o
     JOIN rig.rig r USING (rig_id))
     LEFT JOIN rig.rig_status_period sp ON (((sp.rig_id = r.rig_id) AND (CURRENT_DATE <@ sp.valid_period))))
     LEFT JOIN rig.v_rig_tier_a_power p ON ((p.rig_id = r.rig_id)))
     LEFT JOIN rig.rig_ownership own ON (((own.rig_id = r.rig_id) AND (own.role = 'beneficial_owner'::text) AND (CURRENT_DATE <@ own.valid_period))))
     LEFT JOIN rig.corporate_entity e ON ((e.entity_id = own.entity_id)))
  WHERE ((o.model_version = 'v2'::text) AND (o.scored_on = ( SELECT max(o2.scored_on) AS max
           FROM rig.rig_opportunity_score o2
          WHERE ((o2.rig_id = o.rig_id) AND (o2.model_version = 'v2'::text)))))
  ORDER BY (o.distress_score * LEAST(1.0, (o.input_coverage_pct / 40.0))) DESC, o.input_coverage_pct DESC;

CREATE OR REPLACE VIEW rig.v_tier_a_inventory AS
 SELECT r.rig_id,
    r.canonical_name,
    r.unit_class,
    sp.state AS lifecycle_state,
    sp.location_country,
    "left"((ct.tier)::text, 1) AS tier_letter,
    ct.display_name AS component_type,
    c.component_id,
    c.make,
    c.model_series,
    c.sku,
    c.quantity,
    c.output_kw,
    ((c.quantity)::numeric * c.output_kw) AS aggregate_kw,
    c.frequency_hz,
    c.voltage_kv,
    c.rpm,
    c.fuel,
    c.imo_tier,
    c.epa_gate,
    c.condition,
    c.preservation,
    c.operating_hours,
    c.hours_source_type,
    c.extraction,
    c.oem_lifecycle_status,
    c.parts_availability,
    c.est_recovery_value_usd
   FROM (((rig.rig r
     JOIN rig.rig_component c ON ((c.rig_id = r.rig_id)))
     JOIN rig.component_type ct ON ((ct.component_type_id = c.component_type_id)))
     LEFT JOIN rig.rig_status_period sp ON (((sp.rig_id = r.rig_id) AND upper_inf(sp.valid_period))))
  WHERE ((ct.tier = 'A_power_electrical'::rig.component_tier) AND (c.removal_date IS NULL));

-- ----------------------------------------------------------------------------
-- Functions
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION rig.fn_normalise_indicator(p_indicator_id uuid, p_raw numeric, p_model_version text DEFAULT 'v1'::text)
 RETURNS numeric
 LANGUAGE sql
 STABLE
AS $function$
  SELECT CASE
    WHEN p_raw IS NULL THEN NULL
    WHEN n.curve = 'binary'        THEN CASE WHEN p_raw = 0 THEN 0.0 ELSE 1.0 END
    WHEN n.curve = 'linear_capped' THEN round(least(greatest(p_raw, 0) / n.cap, 1.0), 4)
    WHEN n.curve = 'ordinal'       THEN (n.ordinal_map ->> (round(p_raw)::int)::text)::numeric
  END
  FROM rig.indicator_normalisation n
  WHERE n.indicator_id = p_indicator_id AND n.model_version = p_model_version;
$function$;

CREATE OR REPLACE FUNCTION rig.fn_distress_score(p_rig_id uuid, p_model_version text DEFAULT 'v1'::text)
 RETURNS TABLE(distress_score numeric, input_coverage_pct numeric, indicators integer, observed_weight numeric, applicable_weight numeric)
 LANGUAGE sql
 STABLE
AS $function$
  WITH me AS (
    SELECT r.rig_id, r.unit_class,
           (SELECT sp.state FROM rig.rig_status_period sp
             WHERE sp.rig_id = r.rig_id AND current_date <@ sp.valid_period LIMIT 1) AS state
    FROM rig.rig r WHERE r.rig_id = p_rig_id
  ),
  latest AS (
    SELECT DISTINCT ON (o.indicator_id)
           o.indicator_id,
           rig.fn_normalise_indicator(o.indicator_id, o.raw_value, p_model_version) AS ns
    FROM rig.rig_distress_observation o
    WHERE o.rig_id = p_rig_id AND o.raw_value IS NOT NULL
    ORDER BY o.indicator_id, o.observed_on DESC
  ),
  obs AS (
    SELECT sum(l.ns * d.weight) AS num, sum(d.weight) AS den, count(*)::int AS n
    FROM latest l JOIN rig.distress_indicator_def d USING (indicator_id)
    WHERE l.ns IS NOT NULL
  ),
  applicable AS (
    SELECT sum(d.weight) AS tot
    FROM rig.indicator_applicability a
    JOIN rig.distress_indicator_def d USING (indicator_id)
    CROSS JOIN me
    WHERE a.model_version = p_model_version
      AND a.unit_class = me.unit_class
      AND (a.state_condition IS NULL
           OR me.state IS NULL
           OR me.state = 'unknown'
           OR (a.state_condition = 'stacked'      AND me.state IN ('cold_stacked','warm_stacked'))
           OR (a.state_condition = 'cold_stacked' AND me.state = 'cold_stacked'))
  ),
  extra AS (
    SELECT coalesce(sum(d.weight), 0) AS tot
    FROM latest l JOIN rig.distress_indicator_def d USING (indicator_id)
    CROSS JOIN me
    WHERE l.ns IS NOT NULL
      AND NOT EXISTS (
        SELECT 1 FROM rig.indicator_applicability a
        WHERE a.indicator_id = l.indicator_id
          AND a.model_version = p_model_version
          AND a.unit_class = me.unit_class
          AND (a.state_condition IS NULL
               OR me.state IS NULL
               OR me.state = 'unknown'
               OR (a.state_condition = 'stacked'      AND me.state IN ('cold_stacked','warm_stacked'))
               OR (a.state_condition = 'cold_stacked' AND me.state = 'cold_stacked')))
  )
  SELECT round(100 * obs.num / nullif(obs.den, 0), 2),
         round(100 * obs.den / nullif(applicable.tot + extra.tot, 0), 2),
         coalesce(obs.n, 0),
         obs.den,
         applicable.tot + extra.tot
  FROM obs, applicable, extra;
$function$;

CREATE OR REPLACE FUNCTION rig.fn_audit()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  INSERT INTO rig.audit_log (table_name, row_pk, operation, old_value, new_value)
  VALUES (
    TG_TABLE_NAME,
    COALESCE(NEW.*::text, OLD.*::text),
    TG_OP,
    CASE WHEN TG_OP IN ('UPDATE','DELETE') THEN to_jsonb(OLD) END,
    CASE WHEN TG_OP IN ('INSERT','UPDATE') THEN to_jsonb(NEW) END
  );
  RETURN COALESCE(NEW, OLD);
END $function$;

CREATE OR REPLACE FUNCTION rig.fn_rig_code_immutable()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  IF NEW.rig_code IS DISTINCT FROM OLD.rig_code THEN
    RAISE EXCEPTION 'rig_code is immutable (rig_id=%)', OLD.rig_id;
  END IF;
  RETURN NEW;
END $function$;

-- ----------------------------------------------------------------------------
-- Triggers
-- ----------------------------------------------------------------------------

CREATE TRIGGER trg_audit_rig AFTER INSERT OR DELETE OR UPDATE ON rig.rig FOR EACH ROW EXECUTE FUNCTION rig.fn_audit();
CREATE TRIGGER trg_rig_code_immutable BEFORE UPDATE ON rig.rig FOR EACH ROW EXECUTE FUNCTION rig.fn_rig_code_immutable();
CREATE TRIGGER trg_audit_capability AFTER INSERT OR DELETE OR UPDATE ON rig.rig_capability FOR EACH ROW EXECUTE FUNCTION rig.fn_audit();
CREATE TRIGGER trg_audit_component AFTER INSERT OR DELETE OR UPDATE ON rig.rig_component FOR EACH ROW EXECUTE FUNCTION rig.fn_audit();

-- ----------------------------------------------------------------------------
-- Row Level Security
-- ----------------------------------------------------------------------------
-- Reproduced exactly as found live: RLS is enabled (most tables also
-- FORCEd) with ZERO policies defined anywhere in the schema, and zero
-- grants exist beyond the implicit table-owner privileges. That combination
-- blocks all access via PostgREST/anon/authenticated roles by construction
-- -- there is nothing to relax here; add policies deliberately if/when this
-- schema is served through Supabase's API layer.

ALTER TABLE rig.source ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.source FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.source_precedence ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.source_precedence FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.source_record ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.source_record FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_design ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_design FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.corporate_entity ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.component_type ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.component_type FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.engine_family ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.engine_family FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.distress_indicator_def ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.distress_indicator_def FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_capability ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_capability FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_component ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_component FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_contract ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_contract FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_distress_observation ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_distress_observation FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_event FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_exit ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_exit FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_identifier ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_identifier FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_name_alias ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_name_alias FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_opportunity_score ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_opportunity_score FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_ownership ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_position ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_position FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_registry FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_scrap_basis ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_scrap_basis FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_status_period ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_status_period FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_valuation ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.rig_valuation FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.comparable_transaction ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.comparable_transaction FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.corporate_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.field_conflict ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.field_conflict FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.harvest_buildup ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.harvest_buildup FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.repurposing_assessment ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.repurposing_assessment FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.watchlist ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.watchlist FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.watchlist_rig ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.watchlist_rig FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.alert_rule ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.alert_rule FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.alert_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.alert_event FORCE ROW LEVEL SECURITY;
ALTER TABLE rig.audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig.audit_log FORCE ROW LEVEL SECURITY;
-- power_cost_benchmark, indicator_normalisation, indicator_applicability
-- had RLS OFF entirely on the live database (owner/superuser-only access
-- was still enforced by the absence of any anon/authenticated grant).
