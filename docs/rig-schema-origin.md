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

**UPDATE (2026-08-24): both schema and data have now moved.** The founder's
explicit go-ahead — *"create a new su[per]base project for this if that is
the most efficient way, without any content or data or process loss"* — was
carried out in a follow-up session:

- A new, dedicated Supabase project was created: **`rhglbwoxuzgwoptycspc`**
  (project name `lrp-tx-gis-rig`), unrelated to and unconnected from the
  10th-muses-app project.
- This repo's baseline migration (below) was applied to that new project
  and verified structurally identical to the source: 37/37 tables, 11/11
  views, 4/4 functions, 4 triggers, 20/20 enums, and the same zero-policy
  RLS posture on every table (including the 3 tables —
  `power_cost_benchmark`, `indicator_normalisation`,
  `indicator_applicability` — that have RLS OFF in the source, matched
  exactly rather than "corrected").
- All data — **7,031 rows across 36 populated tables** — was copied from
  the original shared project into the new one and independently
  verified: a table-by-table row-count match (source vs. target, all 36
  non-empty tables exact), a matching aggregate total (7031 = 7031), and
  content-level spot checks (server-side `jsonb` equality, not eyeballed)
  across `rig`, `corporate_entity`, and the text-heavy `rig_valuation`
  table. Source was re-verified unchanged (still 7031 rows) after the
  copy — nothing was moved *out* of the original project, only copied.
- Per the founder's explicit "do not delete" instruction, **the original
  data in the shared 10th-muses-app Supabase project (`xvlpperttnedsduscgnq`)
  was left fully in place** — this was a copy, not a cutover. The `rig`
  schema now exists live, with identical data, in both projects.
- The original discovery/decision context below (schema-only, no project
  yet) describes the state as of 2026-08-23, one day before the data copy;
  kept for the historical record rather than rewritten.

Original schema-only note (2026-08-23, superseded by the above for the
data question, still accurate for how the baseline migration was built):

- The baseline migration in this repo captures structure only: tables,
  columns, types, constraints, indexes, views, functions, and triggers —
  reconstructed from a live, read-only introspection of the schema as it
  stood on 2026-08-23 (`information_schema` / `pg_catalog`, plus
  `pg_get_viewdef` / `pg_get_functiondef` / `pg_get_triggerdef` for view,
  function, and trigger bodies).
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

This repo is the source of truth for the `rig` schema's **definition**. The
live, running instance of both schema and data now lives in the dedicated
Supabase project `rhglbwoxuzgwoptycspc` (see above) — this repo's migration
file is what defines that project's structure going forward; any future
schema change to the rig data model should land here first, the same way
any other Supabase-backed repo's migrations work.
