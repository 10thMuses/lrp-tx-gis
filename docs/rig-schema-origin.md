# `rig` schema — origin and status

## What this is

`supabase/migrations/*_rig_schema_baseline.sql` is a structure-only baseline
for a Postgres schema named `rig`: an offshore drilling-rig / distressed-asset
intelligence data model — rigs, corporate ownership, contracts, component
inventories, distress scoring, valuations, comparable transactions, and a
handful of analytical views over all of it (fleet status, tier-A power
inventory, harvest/scrap economics, distress ranking).

## How it got here

The `rig` schema was discovered live inside a Postgres database that belongs
to a different, unrelated application (a social-club member app), sharing
that app's Supabase project. It appears to have been built there by mistake
— roughly 100 migrations were applied directly against that live database
between 2026-07-28 and 2026-08-01, with no source control anywhere: none of
those migrations ever existed in any git repository. The schema's business
content (rig fleet data, corporate entities named after real offshore
drilling contractors) has nothing to do with that app.

That other project's owner confirmed this is unrelated and decided:

> "move but do not delete that as it is an unrelated project. it should be
> in a different repo."

This repo (`lrp-tx-gis`) was identified as the correct home.

## What "move" means here

**Only the schema definition moved. The data did not.**

- The baseline migration in this repo captures structure only: tables,
  columns, types, constraints, indexes, views, functions, and triggers —
  reconstructed from a live, read-only introspection of the schema as it
  stood on 2026-08-23 (`information_schema` / `pg_catalog`, plus
  `pg_get_viewdef` / `pg_get_functiondef` / `pg_get_triggerdef` for view,
  function, and trigger bodies).
- The underlying rows — roughly 380 rig records and 51 corporate-entity
  records, plus the contents of every other table — were **not** copied or
  exported anywhere. As of this writing they still live only in the
  original shared Supabase project, per the explicit "do not delete"
  instruction above.
- This repo has no Supabase project of its own yet. The migration file
  documents the schema for whenever one is provisioned, and serves as an
  audit-quality record in the meantime.
- The 100 historical migrations that were applied live were never
  committed anywhere, so replaying them here under fabricated dates would
  misrepresent this repo's history. A single clean baseline capturing the
  current live structure is the more honest record.

## Reconciling structure vs. history

The baseline was validated by applying it to a scratch Postgres 16 database
(with the `pgcrypto`, `pg_trgm`, `btree_gist`, and `postgis` extensions it
depends on) and confirming: all 37 tables, 11 views, 4 functions, and 4
triggers create without error; every view queries cleanly; the `rig_code`
auto-numbering default and the `fn_audit()` audit-log trigger both fire as
expected on insert; and Row Level Security — enabled with zero policies on
every table, exactly as found live — blocks all row access outside the
table owner, even for a role granted explicit table-level `SELECT`.

## Provenance

Filed and tracked as `10th-muses-app` founder-intake item
`1a4cdd8b-604c-4d1c-987a-9f33d541f5c3`. That item's `admin_notes` carry the
original discovery investigation and the decision to relocate the schema
here.

## Status going forward

This repo is now the source of truth for the `rig` **schema**. If/when this
project gets its own Supabase (or other Postgres) instance, or if the
underlying data is ever formally migrated over, that's a separate, explicit
follow-up — not implied by this commit.
