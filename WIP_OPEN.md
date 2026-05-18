# WIP_OPEN.md

Active work + execution queue. Updated when something completes or a new sprint
item is added. Round/decision-log history is archived in
`docs/archive/wip_history_pre_2026-05-18.md`; layer/schema canonical detail in
`ARCHITECTURE.md`; multi-step task breakdowns in `docs/sprint-plan.md`.

---

## Last deploy

`6a0b3037e1a99c55d1fd0a38` — 2026-05-18. 32 layers (counterparty_assets removed).
Build clean `built=32 missing=0 errored=0 tiles_total=34003 KB`.

Older deploy history: `git log --merges --grep "deploy [0-9a-f]" main`.

---

## Queue (resume pointer)

The single `## Next chat` pointer convention was retired at the Round-26
restructure. The canonical queue is this section plus `## Active sprints`.
Resume trigger `resume.` = clone, read this `## Queue`, execute the top
unblocked item on a fresh `refinement-<slug>` branch per `OPERATING.md §4`.

**2026-05-18 — two operator batches, all shipped** (deploy IDs + full detail in `git log --merges`):
- Batch 1: doc/audit hygiene · counties `#fbbf24`→`#64748b` · mobile-popup audit (clean) · wells `filterable_fields` +8 / `permits_permian6` `sidebar_omit` (+`build.py` standalone-ndjson fix).
- Batch 2: county_labels visibility · removed `counterparty_assets` (33→32) · wells own `Wells` group / −5 filters / `exclude_within` Caramba (−9 wells) · wells spud thesis XLSX+PDF export (+`write_stats_attrs` ndjson source).

No pending operator-queued items — see `## Active sprints` + `## Backlog`.

---

## Active sprints

### ERCOT queue geocoding — Stage 3

**Status:** blocked on operator-curated override CSV at `data/ercot_queue_overrides.csv`.

**Spec** (settled, do not re-litigate):
- WRatio ≥ 88 (rapidfuzz partial_ratio fallback to ratio)
- Norm-name suffix-stripping: drop `LLC`, `INC`, `LP`, `LTD`, `CORP`, `CO`, trailing parenthetical project codes
- Idempotent CSV read — re-running the geocode pass with the same CSV produces no diff
- Last-precedence pass — manual override always beats Stage 1+2 algorithmic match
- `coords_source = manual_override` for all rows touched by Stage 3
- Atomic write per `OPERATING.md §3 rule 4` — temp file + `os.replace`

**Resume:** when CSV exists, run `python3 scripts/geocode_ercot_queue.py --stage 3` (verify against Stage 2 invocation pattern). Then full build, deploy, verify aggregate match rate vs Stage 2 baseline, commit + merge.

**Acceptance:** `coords_source = manual_override` rows in built registry equal CSV row count; aggregate solar+wind+battery match rate logged and improved vs Stage 2; no regression in Stage 1+2 rows.

### county_labels render review

If operator-named counties still appear unlabeled at zoom 7–9, inspect MapLibre
`text-allow-overlap` / `symbol-sort-key` / `text-padding` on the county_labels
source-layer config in `build_template.html`. Conditional on visual
confirmation the issue still exists.

---

## Backlog

### Infrastructure
- Akamai datacenter-egress block on `reevescounty.org` 403s any cloud-runner traffic regardless of UA/TLS. Hard prerequisite for the Reeves abatement-weekly-cron item. Unblock paths: residential-proxy egress (paid), Akamai allowlisting via Reeves IT (low likelihood), search-API result pages.
- `GITHUB_PAT` can push branches + merge, 403 on PR creation. Direct-merge-to-main is the protocol per `OPERATING.md §6`.

### Data
- RRC permits 1976–2017 backfill: overnight W-1 scrape; scratch in `outputs/refresh/rrc_w1_*` (gitignored). When `rrc_w1_permits_with_coords.csv` is complete: `python3 scripts/parse_rrc.py permits` (auto-merges, deduped by permit_no+api_no) → `python3 build.py` → deploy.
- HIFLD remaining layers; ERCOT deeper geocoding (FERC EQR + PUC CCN); counterparty boundary precision upgrade. Detail in `docs/sprint-plan.md` + archive.

### UI / UX
- **`GROUP_ORDER` missing `Energy Infrastructure`** (latent, found 2026-05-18): `build_template.html` `GROUP_ORDER` gates sidebar rendering; the `hifld_*` layers declare `group: Energy Infrastructure`, absent from `GROUP_ORDER`, so they never render in the sidebar (tiles/data build fine). Fix = add `'Energy Infrastructure'` to `GROUP_ORDER` (one-line); deferred — surfaces 4 hifld layers in the sidebar, an operator-visible change to confirm first.
- No-browser-env note: county_labels (visual) + wells thesis XLSX/PDF (button click) were verified via config/bundle/math re-derivation, not in-browser render — eyeball once on prod to confirm.
- **`value_labels` not plumbed through `build.py`** (latent, found 2026-05-18): `build_template.html:905` reads `f.value_labels` but `render_html` only forwards `quick_presets`/`sort_by_count` from the yaml spec, so `plug_flag`/`active_flag` filters show raw `Y`/`N`/`A` instead of friendly labels. Cosmetic; fix = add a `value_labels` pass-through beside the `quick_presets` line in `render_html`.
- Standalone-layer filter panels now render (2026-05-18 `build.py` fix): `hifld_*` (and `permits_permian6`, though sidebar-hidden) gained their declared filter UIs — previously silently empty. Intended; noted for awareness.
- `date_range` filter for eia860_plants/battery/wind needs `yyyy`→`yyyy-01-01` padding in 3 ingest scripts; low priority (numeric year-slider works).
- Filter inputs 40px on mobile vs 44px WCAG; acceptable per Apple HIG (≥40px); flag if operator testing surfaces hit-rate issues.

### Audit drift (`bash scripts/audit.sh`)
`OPERATING.md` ≤250 lines · `WIP_OPEN.md` ≤8192 bytes · 0 stranded `refinement-*`/`claude/*` branches on origin · close-out conformance 100%.

**Stranded branches awaiting operator disposition (flagged 2026-05-18, not deleted):**
- `dc-anchors-refresh-3/4/5/6` — DC-anchors auto-refresh LLM-in-the-loop `dc_anchors_proposed.json` proposals, never reviewed/applied. 3/4/5 superseded by the 2026-05-18 run; 6 is the latest proposal. Decision: review/apply/discard, then delete.
- `refinement-chat127-drilling-permits-point` — 726 lines real unmerged work (`drilling_permits` scraper + parser + smoke test + `layers.yaml` stanza), parked on the RRC MFT-source block. Decision: revive (if MFT path now viable) or archive the work, then delete.

---

## Process notes

- `scripts/close-out.sh` enforces atomic deploy+merge and the `refinement-*` branch lifecycle. Use it; don't hand-roll merges to `main`.
- `scripts/audit.sh` is cheap; include it in verification for medium/high blast-radius work.
- The `/*__BUILD_ID__*/` token substitution in `build.py:render_html` (UTC timestamp + nonce) makes `deploy.sh`'s md5-parity poll a reliable readiness signal. Removing the marker breaks the poll.
- Daily probe + W-1 backfill scratch (`data/abatements/abatement_hits_*.csv`, `outputs/refresh/rrc_w1_*`) are gitignored — the unattended daily-refresh routine must never commit them.
