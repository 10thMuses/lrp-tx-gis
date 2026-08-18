# 08 — Roadmap, Gaps and Known Drift

What is stale, what is broken, what is blocked, and what is worth building next.
Verified against the repo on 2026-08-18 at `main` @ `0fae6a2`.

---

## 1. Documentation drift (found 2026-08-18)

Where the repo's own docs disagree with the code. **The code is authoritative.** These
are cheap to fix and each one has already misled someone.

| # | Location | Says | Reality | Impact |
|---|---|---|---|---|
| 1 | `ARCHITECTURE.md §5` | "**32 layers** total live in prod" | `layers.yaml` has **39**; the last deploy shipped 39 | Anyone using the doc as an acceptance target will pass a broken build |
| 2 | `OPERATING.md §5.1` | Build clean = "**26 entries → 24 display layers**" | 39 entries | Same — this is the stated acceptance criterion and it is wrong |
| 3 | `ARCHITECTURE.md §5` catalog | Lists `aquifers`, `wells` (TWDB groundwater), `pipelines`, `parcels_pecos`, `fcc_fiber_coverage` | **None are in `layers.yaml`** | Five documented layers that do not exist |
| 4 | `ARCHITECTURE.md §5` catalog | Omits 17 live layers: all 7 `oxy_*`, `la_escalera`, `longfellow_ranch`, `gw_ranch`, `solstice_substation`, 4 × `hifld_*`, `dc_anchors`, `county_labels` | They are live | Nearly half the map is undocumented in the canonical catalog |
| 5 | `ARCHITECTURE.md §2` | "All files flat at repo root. No subfolders for data files." | `data/` has 7 subfolders holding 13 layer sources | The stated layout convention is no longer followed |
| 6 | `ARCHITECTURE.md §11` | `permits_permian6` is **scoped out** — layout unavailable | The layer **shipped** and carries 28,842 permits | Contradicted two sections earlier in the same file |
| 7 | `OPERATING.md §4` | `parse_rrc.py wells` writes `data/wells_pecos11.csv` | Writes `data/wells_permian6.csv` | Wrong path in the canonical refresh doc |
| 8 | `build.py:1514` (`cmd_refresh`) | `python3 build.py refresh permits` exits 2 with "permits_pecos11 is scoped-out" | The permits path works; you must call the two scripts directly | A documented command that refuses to run |
| 9 | `scripts/parse_rrc.py` docstring | "11-county Permian CSV" | 6-county scope since 2026-05-13 | Misleads anyone modifying the parser |
| 10 | `ARCHITECTURE.md §1` | Bundle is "single `index.html` (~18 KB)" | ~150 KB | Minor, but it signals the doc has not been revisited |
| 11 | Everywhere | No mention of the **Supabase access gate** or viewer analytics | Both are live and are the only server-side components | A whole subsystem was undocumented until this handbook |
| 12 | Everywhere | No **root `README.md`** | — | The repo's front door was blank |

Items 1, 2, 8 and 12 are the ones that actively cause errors. 11 was the most dangerous
and is now addressed.

### Healthy metrics

Not everything has drifted. `bash scripts/audit.sh` targets that currently pass:

| Metric | Target | Actual |
|---|---|---|
| `OPERATING.md` lines | ≤ 250 | **131** ✅ |
| `WIP_OPEN.md` bytes | ≤ 8192 | **7,382** ✅ |

---

## 2. Repository hygiene

| Issue | Detail | Fix |
|---|---|---|
| **20 open PRs** | 13 stale `dc-anchors-refresh-*` proposals, 7 `claude/*` drafts | [`00-MIGRATION-RUNBOOK.md §2.1`](00-MIGRATION-RUNBOOK.md#21-close-the-20-open-pull-requests) |
| **Stranded branches ≠ 0** | `audit.sh` targets 0 and `WIP_OPEN.md` records reaching 0 on 2026-05-18; it has drifted back | Close the PRs (each has `delete-branch: true`) |
| **Repo is 110 MB** | `data/fracfocus/DisclosureList_1.csv` alone is 60 MB and is not referenced by `layers.yaml` | Delete it — re-downloadable from fracfocus.org |
| **Three products in one repo** | The GIS map, the Grid Wire briefing, and OXY client deliverables | Split. PR #13 was an attempt at the Grid Wire split. |
| **Client deliverables in a public repo** | `outputs/reports/` holds OXY, GW Ranch and Stargate Abilene diligence material | Move to the team document store |
| **`ercot_queue` label is date-stamped** | Reads "(as of 2026-04-21)" — four months stale | Refresh, or make the label build-time dynamic |

---

## 3. Open sprints

### 3.1 ERCOT queue geocoding — Stage 3 · **BLOCKED**

The highest-value open item. 1,299 of 1,778 queue projects (73.1%) still sit on county
centroids against a **≥60% precise target**; only 479 (26.9%) have been upgraded.

**Blocker:** the operator-curated override CSV at `data/ercot_queue_overrides.csv` does
not exist. This is a curation task, not an engineering task — nothing else is missing.

**Spec (settled, do not re-litigate):**

- WRatio ≥ 88, `rapidfuzz` `partial_ratio` falling back to `ratio`
- Name normalisation strips `LLC`, `INC`, `LP`, `LTD`, `CORP`, `CO` and trailing
  parenthetical project codes
- Idempotent CSV read — re-running with the same CSV produces no diff
- Last-precedence pass — a manual override always beats the Stage 1+2 algorithmic match
- `coords_source = manual_override` on every row it touches
- Atomic write (temp + `os.replace`)

**Resume:** once the CSV exists, run `python3 scripts/geocode_ercot_queue.py --stage 3`,
then a full build, deploy, and verify the aggregate match rate against the Stage 2
baseline.

**Acceptance:** `manual_override` row count equals the CSV row count · aggregate
solar+wind+battery match rate logged and improved · no regression in Stage 1+2 rows.

### 3.2 `county_labels` render review · conditional

If operator-named counties still appear unlabelled at zoom 7–9, inspect MapLibre
`text-allow-overlap`, `symbol-sort-key` and `text-padding` on the `county_labels`
source-layer config in `build_template.html`. Conditional on visual confirmation that the
issue still exists — it has never been checked in a real browser.

### 3.3 RRC permits 1976–2017 backfill · in flight, unattended

Would extend permit history back 42 years. Scratch files live at
`outputs/refresh/rrc_w1_*` (gitignored).

```bash
# Per-county W-1 listing scrape, 6 counties
for c in PECOS REEVES WARD MIDLAND MARTIN REAGAN; do
  python3 scripts/scrape_rrc_w1.py "$c" 1976 2004
done

# Then the detail-page lat/lon backfill (~7 h throttled)
nohup python3 scripts/scrape_rrc_w1_detail_coords.py \
  --in  outputs/refresh/rrc_w1_permits.csv \
  --out outputs/refresh/rrc_w1_permits_with_coords.csv \
  > /tmp/rrc_w1_coords.log 2>&1 &
```

When `rrc_w1_permits_with_coords.csv` is complete:
`python3 scripts/parse_rrc.py permits` (auto-merges, deduped by `permit_no` + `api_no`)
→ `python3 build.py` → deploy.

---

## 4. Security and access control

Full posture assessment: [`06-ACCOUNTS-AND-ACCESS.md §9`](06-ACCOUNTS-AND-ACCESS.md#9-security-posture--stated-plainly).

| Gap | Severity | Fix |
|---|---|---|
| Tiles are world-readable with no auth (`Access-Control-Allow-Origin: *`) | **High if the data is sensitive** | Requires a signed-URL or authenticated tile proxy — an architecture change, not a patch |
| Single shared plaintext password, no per-user revocation | Medium | Per-viewer magic links, or Supabase Auth with an allowlist |
| Email at the gate is self-declared and unverified | Medium | Magic-link email verification would fix both this and the row above |
| Password compared with `!==`, not constant-time | Low | Real, but the shared-password design is the larger problem |
| Repo public, containing client deliverables | **High** | Make private and/or relocate `outputs/reports/` |
| Gate copy promises more than it delivers ("Confidential access… access is logged") | Medium | Either soften the copy or harden the architecture |

---

## 5. Automation improvements

| # | Improvement | Why |
|---|---|---|
| 1 | Have `dc-anchors-refresh.yml` close its prior open PR before opening a new one | 13 stale PRs is the current state; the structural fix is ~10 lines |
| 2 | Add `verify_deployed_layers.py` to `build-and-deploy.yml` | The cloud deploy path skips the gate the local path treats as mandatory |
| 3 | Correct the stale `ENVIRONMENT REALITY` block in the daily Routine | It pre-tells the routine that failure is normal, so real failures get under-investigated. [`07-AUTOMATION.md §3.3`](07-AUTOMATION.md#33-known-contract-staleness) |
| 4 | Decide what the daily Routine is *for* | It refreshes 99,808 wells rows daily into a gitignored file that never reaches the map. Either wire in `merge` + rebuild, or drop wells/permits to weekly and call it a source-availability monitor. |
| 5 | Add `rapidfuzz`, `beautifulsoup4`, `pyshp`, `shapely` to `bootstrap-claude-code.sh` | The routine installs them at runtime every single day |
| 6 | Decide between the daily Routine and the unbuilt `weekly-refresh.yml` | They occupy the same niche. Do not build both. |
| 7 | Alerting on failed runs | Currently push notifications on the Routine only; a failed GitHub Action is silent unless someone checks |

---

## 6. Data gaps

| Gap | Status |
|---|---|
| `transmission` has **no voltage attribute** | Permanent source limitation. Blocks voltage filtering and sizing. |
| `eia860_plants` null on `capacity_mw` for 476/1,367 rows | Source coverage. Sizing falls back to a static radius. |
| `substations` has **no refresh script** | Refreshed by hand into `combined_points.csv`. OSM Overpass fetch should be scripted. |
| TPIT scraper is **not in the repo** | `tpit_subs` / `tpit_lines` cannot be refreshed reproducibly |
| Tax-abatement adapters: 2 of 23 counties validated | Pecos (WordPress) and Reeves (CivicEngage) only; 21 stubs return `unverified_source` |
| **Reeves County is hard-blocked** | Akamai datacenter-egress block 403s all cloud runners regardless of UA/TLS. Unblock paths: paid residential-proxy egress · Akamai allowlisting via Reeves IT (low likelihood) · search-API result pages. |
| `date_range` filters on `eia860_*` / `wind` | Need `yyyy` → `yyyy-01-01` padding in 3 ingest scripts. Low priority — the numeric year slider works. |
| `wells_permian6`: ~9,295 in-scope wellbores have no lat/lon | Dropped rather than centroid-placed. The layer under-counts by design. |
| `permits_permian6` starts at 2018 | See [§3.3](#33-rrc-permits-19762017-backfill--in-flight-unattended) |
| `rrc_pipelines` frozen at a 2019 snapshot | Accepted per `ARCHITECTURE.md §11` |

### Permanently not feasible

- **`oxy_minerals_pecos`** — Texas mineral ownership is not public GIS geometry. Free
  public data yields a non-spatial owner roll keyed to abstract/survey legal descriptions;
  GLO publishes state-owned mineral geometry only; `parcels_pecos` is **surface**. A
  tract-precise mineral layer needs paid data plus deed-by-deed title platting, i.e.
  hand-coded coordinates — barred by hard rule 3. **Deliverable if wanted:** a sourced OXY
  mineral-*account table*, optionally shaded at abstract level.
- **`bead_fiber_planned`** — neither BEAD source file carries county or coordinates;
  geocoding requires the licensed FCC BSL Fabric. Three possible unblock paths are
  documented in `data/bead_bdo/README.md`.

---

## 7. UI/UX backlog

| Item | Detail |
|---|---|
| Cross-layer search | You must currently know which layer a facility is in before you can find it. Highest-value UX gap. |
| Mobile responsive breakpoints | The sidebar is desktop-first; peers open links on phones |
| Custom domain | Removes `netlify.app` from every share link and makes future host moves a DNS change |
| Legend on print | Implemented, but **never verified in a real browser print** |
| Measure-tool persistence | Measurements are lost on layer toggle |
| Filter input height | 40 px on mobile vs the 44 px WCAG target. Acceptable per Apple HIG (≥40 px); revisit if operator testing shows hit-rate problems. |
| Spuds Summary (PDF) export | Verified by config and arithmetic re-derivation, **not** by an in-browser render. Eyeball it once on prod. |

---

## 8. Prioritised next steps

If you can only do a handful of things, do these, in this order.

| # | Action | Effort | Why first |
|---|---|---|---|
| 1 | Execute the migration ([`00-MIGRATION-RUNBOOK.md`](00-MIGRATION-RUNBOOK.md)) | 1 day | Everything currently rests on one personal account across five vendors |
| 2 | Decide public vs private and relocate `outputs/reports/` | 2 h | Client deliverables are publicly readable today |
| 3 | Close the 20 PRs; delete stranded branches | 1 h | Cheap, and it stops the mess migrating with you |
| 4 | Fix drift items 1, 2, 8, 12 in [§1](#1-documentation-drift-found-2026-08-18) | 2 h | Wrong acceptance criteria and a command that refuses to run |
| 5 | Curate `data/ercot_queue_overrides.csv` and run Stage 3 | Curation | Unblocks the highest-value precision improvement on the map |
| 6 | Correct the daily Routine's stale environment block; decide its purpose | 1 h | It is doing 370 MB of daily work that never reaches the map |
| 7 | Add the layer-verification gate to `build-and-deploy.yml` | 30 min | Closes a real hole in the cloud deploy path |
| 8 | Attach a custom domain | 1 h | Makes every future infrastructure move a DNS change |
| 9 | Decide the access-control posture and either harden it or soften the copy | 2 h – 3 days | The gate promises confidentiality the architecture does not provide |
| 10 | Refresh `ercot_queue` and un-hardcode its date label | 2 h | The most-used layer is four months stale |
