# LRP Texas Energy GIS Map — Project Handbook

Complete operating manual for the LRP Texas Energy GIS Map: what it is, where every
byte comes from, how to build it, how to ship it, how to change it, and how to move
it from a personal account to a team account.

**Live map:** https://lrp-tx-gis.netlify.app
**Repo:** https://github.com/10thMuses/lrp-tx-gis
**Written:** 2026-08-18 · against `main` @ `0fae6a2`

---

## Who this is for

Three audiences, in priority order:

1. **The person executing the account migration.** Start at
   [`00-MIGRATION-RUNBOOK.md`](00-MIGRATION-RUNBOOK.md). Nothing else is required
   reading first.
2. **A new operator/engineer inheriting the project.** Read
   [`01-PROJECT-OVERVIEW.md`](01-PROJECT-OVERVIEW.md) →
   [`03-BUILD-PIPELINE.md`](03-BUILD-PIPELINE.md) →
   [`04-OPERATIONS-RUNBOOK.md`](04-OPERATIONS-RUNBOOK.md). That is enough to build
   and deploy safely.
3. **A team member who just needs to look at the map or pull data out of it.**
   [`01-PROJECT-OVERVIEW.md §7`](01-PROJECT-OVERVIEW.md#7-using-the-map-no-code)
   and [`06-ACCOUNTS-AND-ACCESS.md`](06-ACCOUNTS-AND-ACCESS.md).

---

## Contents

| Doc | Covers |
|---|---|
| [`00-MIGRATION-RUNBOOK.md`](00-MIGRATION-RUNBOOK.md) | **Personal → team account migration.** Ordered, reversible steps for GitHub, Netlify, secrets, PATs, the Claude cron, and the pre-migration cleanup. Includes what deliberately should *not* move. |
| [`01-PROJECT-OVERVIEW.md`](01-PROJECT-OVERVIEW.md) | What the map is and why. Stack, architecture, repo map, design decisions that are settled, how to use the map as a non-engineer. |
| [`02-DATA-SOURCES.md`](02-DATA-SOURCES.md) | **Exhaustive input inventory.** Every one of the 39 layers: upstream source, URL, licence/terms, refresh cadence, scope filters, known assumptions and their blast radius, fragility notes. |
| [`03-BUILD-PIPELINE.md`](03-BUILD-PIPELINE.md) | Inputs → outputs. `layers.yaml` schema, `combined_*` file schemas, `build.py` stage-by-stage, tippecanoe invocation, derived/annotated fields, what lands in `dist/`. |
| [`04-OPERATIONS-RUNBOOK.md`](04-OPERATIONS-RUNBOOK.md) | Day-to-day. Environment setup, refresh commands per layer, build, deploy, verify, close-out, audit, and a symptom-indexed troubleshooting table. |
| [`05-EDITING-THE-MAP.md`](05-EDITING-THE-MAP.md) | How to change things. Add a layer, recolour, add a filter, edit a popup, change defaults, edit the frontend, add an icon, add a basemap. With worked examples. |
| [`06-ACCOUNTS-AND-ACCESS.md`](06-ACCOUNTS-AND-ACCESS.md) | Every account, credential, secret, endpoint and share link. Who needs what. Rotation procedure. |
| [`07-AUTOMATION.md`](07-AUTOMATION.md) | The two GitHub Actions workflows and the Claude scheduled Routine — including the **full daily-refresh contract prompt**, which until now lived only inside the cron config and not in the repo. |
| [`08-ROADMAP-AND-GAPS.md`](08-ROADMAP-AND-GAPS.md) | Known drift, open backlog, scoped-out sources and the conditions that would reopen them, and a prioritised improvement list. |

---

## The five things that will bite you

Condensed from `OPERATING.md §3`. Full context in
[`04-OPERATIONS-RUNBOOK.md §8`](04-OPERATIONS-RUNBOOK.md#8-hard-rules).

1. **Never read source data files into context.** No `cat`/`head`/`open` of
   `combined_points.csv`, `combined_geoms.geojson`, `data/fracfocus/DisclosureList_1.csv`,
   or any layer source. Stream them through subprocesses. They are up to 60 MB.
2. **Never `git add -A`.** Always stage explicit paths. `dist/`, `.env`, `__pycache__/`
   and gitignored probe artifacts are one careless commit away from `main`.
3. **Never hand-code coordinates or feature values.** Every point traces to a public
   dataset cited in [`02-DATA-SOURCES.md`](02-DATA-SOURCES.md). Two layers
   (`mpgcd_zone1`, `waha_circle`) are documented exceptions and are labelled APPROXIMATE.
4. **Atomic writes only** for any read-modify-write helper — `os.replace(tmp, final)`,
   never `open(path, 'w')` mid-process.
5. **Deploy and merge are one unit.** `scripts/ship.sh` enforces it. A deploy without
   its merge leaves prod ahead of `main` with no record of what shipped.

---

## Conventions used in this handbook

- Commands assume you are at the repo root with `.env` populated.
- `<ANGLE_BRACKETS>` mark values you must substitute.
- Facts are stated against the repo as of 2026-08-18. Where a repo doc disagrees with
  the code, the code wins and the discrepancy is flagged in
  [`08-ROADMAP-AND-GAPS.md §1`](08-ROADMAP-AND-GAPS.md#1-documentation-drift-found-2026-08-18).
