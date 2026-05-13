# Refresh Automation — planning document (R26 P7, 2026-05-13)

**Status: PLANNING ONLY. No GitHub Action implementation in this session.**

This document inventories the project's data layers, their refresh
mechanisms, and a proposed GitHub Actions weekly schedule. Operator
sign-off required on the decisions in §7 before implementation.

---

## 1. Current state per layer

Refresh mechanism column values:
  - `auto-build`   — fetcher runs unconditionally on `python3 build.py`
                     (no separate trigger needed)
  - `trigger`      — explicit `refresh <name>` command per CLAUDE.md
                     (e.g. `refresh wells.`, `refresh permits.`)
  - `static`       — hand-curated; no refresh path needed
  - `prebuilt`     — `.pmtiles` already published, never rebuilt locally
  - `combined-csv` — sourced from `combined_points.csv` /
                     `combined_geoms.geojson`, refreshed by editing the
                     combined file directly (rare)

| Layer | Mechanism | Refresh script | Source cadence | Last refreshed | Recommended interval |
|---|---|---|---|---|---|
| wells_permian6 | trigger | scripts/fetch_rrc.py wells + scripts/parse_rrc.py wells | RRC MFT — weekly | 2026-05-13 | Weekly (Mon) |
| permits_permian6 | trigger | scripts/fetch_rrc.py permits + scripts/parse_rrc.py permits | RRC MFT — monthly EOM + Lat/Lon | 2026-05-13 | Monthly (first business day of month) |
| ercot_queue | trigger | scripts/geocode_ercot_queue.py | ERCOT GIS — monthly mid-month | 2026-04-25 | Monthly (mid-month) |
| eia860_plants | trigger | scripts/refresh_eia860.py | EIA-860 — annual (typically Feb-Mar) | 2026-04-28 | Annual (Mar) |
| eia860_battery | trigger | scripts/refresh_eia860.py | EIA-860 — annual | 2026-04-28 | Annual (Mar) |
| wind | trigger | scripts/refresh_uswtdb.py | USWTDB — quarterly | 2026-04-28 | Quarterly |
| solar | static (EIA-860 derived) | (refreshed alongside eia860) | Annual | 2026-04-28 | Annual |
| substations | trigger | (Overpass; no current script) | OSM — continuous | 2026-04-23 | Quarterly |
| transmission | combined-csv | (hand-edited) | HIFLD — annual | 2026-04-25 | Annual |
| tpit_subs / tpit_lines | trigger | (ERCOT TPIT XLSX scrape, not in repo) | ERCOT TPIT — monthly | 2026-04-25 | Monthly |
| rrc_pipelines | prebuilt | n/a | RRC — annual snapshot | 2019 baseline | (Acceptable per ARCH §11) |
| tceq_gas_turbines | trigger | scripts/refresh_tceq_gas_turbines.py | TCEQ — recurring filings | 2026-04-25 | Monthly |
| tax_abatements | trigger | scripts/scrape_ldad.py + scripts/scrape_abatements.py | LDAD — rolling | 2026-04-29 | Weekly (Sat after RRC) |
| fcc_fiber_coverage | trigger | scripts/refresh_fcc_fiber_coverage.py | FCC BDC — biannual | 2026-04-25 | Biannual |
| dc_anchors | trigger | scripts/refresh_dc_anchors.py | Hand-curated + sources | Continuous | Monthly review |
| counties / cities / county_labels / labels_hubs | static | n/a | Census TIGER (rare changes) | Persistent | Never (manual) |
| la_escalera / longfellow_ranch / gw_ranch / mpgcd_zone1 / waha_circle | static | n/a | Hand-placed | Persistent | Never |
| counterparty_assets | static (R2.5 Part 5) | n/a | Hand-placed APPROXIMATE | Persistent | Per-deal manual |
| parcels_pecos | prebuilt | n/a | StratMap TNRIS — annual | 2024 | Annual manual |
| tiger_highways / bts_rail | prebuilt | n/a | Census/BTS — rare | Persistent | Multi-year |
| caramba_north / solstice_substation | static | n/a | Hand-placed | Persistent | Never |
| hifld_ng_pipelines / hifld_crude_pipelines / hifld_hgl_pipelines / hifld_ng_processing | trigger | scripts/fetch_hifld.py (new in R26) | HIFLD/EIA — annual-ish per dataset | 2026-05-13 | Quarterly |

---

## 2. Proposed automation

### Workflow shape

A single GitHub Actions workflow file at `.github/workflows/weekly-refresh.yml`
with two jobs:
  1. **refresh-data** — checks out main, runs refresh scripts in
     dependency order, commits any data file deltas to a
     `refinement-weekly-refresh-<YYYY-MM-DD>` branch, pushes.
  2. **build-and-deploy** — depends on `refresh-data`; runs
     `python3 build.py` and `bash scripts/deploy.sh`. Gated by
     `errored == 0` check in build output.

### Refresh sequence (within job 1)

```
fetch_rrc.py wells       — weekly cadence anchor
parse_rrc.py wells
fetch_rrc.py permits     — monthly cadence, runs every week, skips
                           cached snapshots
parse_rrc.py permits
geocode_ercot_queue.py   — monthly source, weekly probe acceptable
scrape_abatements.py     — weekly probe (LDAD updates rolling)
fetch_hifld.py …         — quarterly source, monthly probe sufficient
refresh_eia860.py        — annual source, monthly probe sufficient
refresh_uswtdb.py        — quarterly probe
refresh_dc_anchors.py    — weekly review
```

### Failure handling

Each refresh step gated independently:
  - exit code != 0 → log + continue with next layer (do not abort
    pipeline; downstream layers may still refresh)
  - Build step gated on `errored == 0` in the build output (existing
    convention from scripts/audit.sh)
  - Deploy step gated on build success

### Notification on failure

Default proposal: GitHub Actions native notifications (email per
operator's GitHub notification settings). If the operator wants
out-of-band notification:
  - Webhook to Slack channel (requires SLACK_WEBHOOK_URL secret)
  - SMS via Twilio (requires Twilio creds)
  - SendGrid email (requires SENDGRID_API_KEY)

---

## 3. Per-layer publish cadence (verified)

| Layer | Source URL pattern | Publish cadence | Verified |
|---|---|---|---|
| wells (dbf900) | mft.rrc.texas.gov/link/b070ce28… | Weekly | 2026-05-13 |
| permits (daf420 EOM+LatLon) | mft.rrc.texas.gov/link/f5dfea9c… | Monthly | 2026-05-13 |
| permits (W-1 listings) | webapps.rrc.state.tx.us/DP/ | Daily/per-filing | 2026-05-13 |
| ercot_queue (GIS Report) | www.ercot.com/.../monthly-gis-reports/ | Monthly mid-month | 2026-04-25 |
| eia860 (annual ZIP) | eia.gov/electricity/data/eia860/ | Annual (Feb-Mar release) | 2026-02 |
| uswtdb (FeatureServer) | services.arcgis.com/.../USWTDB | Quarterly | 2026-04 |
| LDAD abatements | per-county commissioner court agendas | Rolling per-county | 2026-04-29 |
| HIFLD pipelines/refineries | services1.arcgis.com/Hp6G80…, services2.arcgis.com/FiaPA4ga… | Annual-ish (varies per dataset) | 2026-05-13 |
| HIFLD NG processing | services2.arcgis.com/ZOdjAzAQ… | Annual (EIA quarterly source) | 2026-05-13 |
| Comptroller Ch.312 | api.comptroller.texas.gov | Rolling | 2026-05-13 |
| TCEQ gas turbines | TCEQ turbine-lst.xlsx | Per-filing rolling | 2026-04-25 |
| FCC BDC fixed | broadbandmap.fcc.gov | Biannual (Jun / Dec) | 2026-04-25 |
| RRC PDQ Dump (production) | mft.rrc.texas.gov/link/1f5ddb8d… | Monthly (last Sat) | 2026-05-13 |

---

## 4. Recommended schedule (per Hanwha-thesis importance)

| Tier | Layers | Frequency | Action runner cron |
|---|---|---|---|
| Critical (current evidence) | wells_permian6, permits_permian6, ercot_queue | Weekly | Mon 06:00 UTC |
| Important (peer signals) | tax_abatements, eia860 layers, uswtdb | Weekly probe (most no-op) | Mon 06:30 UTC |
| Stable infra | hifld_*, fcc_fiber_coverage | Monthly | 1st-of-month 07:00 UTC |
| Annual+ | parcels_pecos, transmission, rrc_pipelines | Manual | n/a |

Single Monday-morning cron handles tiers 1+2; tier-3 monthly cron
handles HIFLD/FCC at month start.

---

## 5. Risk assessment

| Risk | Probability | Mitigation already in code |
|---|---|---|
| RRC ViewState / MFT URL change | Medium | scripts/fetch_rrc.py raises explicit error; pipeline fails fast |
| ERCOT GIS Report column rename | Medium | scripts/geocode_ercot_queue.py validates expected columns |
| ArcGIS FeatureServer URL move | Medium | scripts/fetch_hifld.py raises; pipeline fails one layer, continues others |
| EIA-860 file schema change | Low | refresh_eia860.py validates columns |
| Anti-scraping rate-limit kicks in | Medium | All scrapers use 1.5s+ throttle + retries |
| Build cardinality cap exceeded (>500K) | Low | build.py emits warning; tippecanoe handles via `--drop-densest-as-needed` |
| Deploy md5 polling timeout | Low | deploy.sh has built-in poll + retry |
| Netlify build minutes overrun | Low-Med | Plan budget — weekly + monthly run @ ~3-5 min each = ~20 min/mo |

**Existing safety net**: `scripts/audit.sh` + the `errored > 0` check in
`build.py` already prevent broken deploys. No new schema-validation
infra needed before launching the cron — existing validators are
sufficient for the first 90 days.

---

## 6. Estimated implementation effort

| Task | Estimate |
|---|---|
| Write `.github/workflows/weekly-refresh.yml` | 2 h |
| Verify each refresh script exits 0 on success / non-0 on failure | 1 h |
| Configure GitHub Actions secrets (NETLIFY_PAT, GITHUB_PAT, optional Slack webhook) | 30 min |
| First end-to-end dry run + iterate on flakes | 2-3 h |
| Document monitoring procedure for operator | 30 min |
| **Total** | **6-7 hours** |

Implementation requires the operator to:
  1. Add `NETLIFY_PAT` and `GITHUB_PAT` as repo secrets at
     https://github.com/10thMuses/lrp-tx-gis/settings/secrets/actions
  2. Decide on notification channel (default: GitHub email)
  3. Decide on Monday business-hours vs off-hours timing

---

## 7. Decision points (operator sign-off required)

1. **Refresh frequency tradeoff**
   - Option A: Weekly (proposed) — fresh data 3-7 days old, ~20 build minutes/mo
   - Option B: Daily — fresh data ≤1 day, ~90 build minutes/mo, more chance of mid-PR breaks
   - Option C: Bi-weekly — older data but lowest noise
   - **Recommendation: Option A (weekly).** Permian permit cadence is
     monthly, RRC wellbore is weekly, ERCOT queue is monthly. Weekly
     keeps the most-volatile layer (wells) current without daily-cron
     overhead.

2. **Notification mechanism**
   - Option A: GitHub Actions email (default, no setup)
   - Option B: Slack webhook (requires bot setup + secret)
   - Option C: Email via SendGrid (requires SENDGRID_API_KEY)
   - **Recommendation: Option A.** Sufficient for a 1-operator project.

3. **Texas business hours vs off-hours**
   - Mondays 06:00 UTC = 01:00 CDT (overnight Sun→Mon)
   - Mondays 12:00 UTC = 07:00 CDT (early morning)
   - **Recommendation: 06:00 UTC.** Operator wakes to a fresh deploy.
     RRC MFT is reliable overnight; Netlify CDN is global so deploy
     timing doesn't matter.

4. **Branch / merge model for refresh commits**
   - Option A: Auto-merge to main if `errored==0` (proposed)
   - Option B: PR per refresh, manual review
   - **Recommendation: Option A.** Refresh deltas are data-only; the
     `errored==0` gate is the protection mechanism. Manual review per
     weekly refresh would burn operator time on no-op deltas.

5. **What happens when a single layer's refresh fails?**
   - Option A: Continue with other layers; flag failure in commit
     message; deploy with stale layer (proposed)
   - Option B: Abort the whole pipeline; no deploy until manual fix
   - **Recommendation: Option A.** Stale-but-stable beats no-update.

---

## 8. Not implemented in this document

  - Actual `.github/workflows/weekly-refresh.yml` file
  - GitHub Actions secrets configuration
  - First end-to-end dry run

The user explicitly directed P7 to be planning-only. Implementation
sprint can pick this document up when operator gives sign-off on §7
decisions.
