# WIP_OPEN.md

Active work + execution queue. Updated when something completes or a new sprint
item is added. Round/decision-log history is archived in
`docs/archive/wip_history_pre_2026-05-18.md`; layer/schema canonical detail in
`ARCHITECTURE.md`; multi-step task breakdowns in `docs/sprint-plan.md`.

---

## Last deploy

`6a04dc7a2a2db8a7d9dd7c6a` — 2026-05-13 (R26 P6). 33 layers. Build clean
`built=33 missing=0 errored=0 tiles_total=34045 KB`.

Older deploy history: `git log --merges --grep "deploy [0-9a-f]" main`.

---

## Queue (resume pointer)

The single `## Next chat` pointer convention was retired at the Round-26
restructure. The canonical queue is this section plus `## Active sprints`.
Resume trigger `resume.` = clone, read this `## Queue`, execute the top
unblocked item on a fresh `refinement-<slug>` branch per `OPERATING.md §4`.

Operator-set order (2026-05-18):

1. ~~Doc/audit hygiene — WIP_OPEN trim, sprint-plan dead-pointer removal, rrc_w1 gitignore, stranded-branch delete~~ (this branch).
2. ~~Counties outline color review~~ — shipped 2026-05-18, deploy `6a0b19d913992206825a7f2f` (`#fbbf24`→`#64748b`, Reference slate-500).
3. ~~Mobile popup audit~~ — verified clean 2026-05-18, no deploy: `60vh` cap + `overflow-y:auto` + `-webkit-overflow-scrolling:touch` + `overflow-wrap:anywhere` present at ≤768px; `ercotQueuePopupHtml`/generic `tax_abatements`/`abatementAnnotationHtml` builders use only cosmetic inline styles — none defeats the cap (this branch).
4. **Wells `filterable_fields` expansion + hide `permits_permian6`** — add filters covering every `wells_permian6` data column; hide the permits layer (wells covers the same 6-county extent). `layers.yaml` (+ `build_template.html` if filter rendering needs it). High blast radius — full §5 acceptance protocol.

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
- `date_range` filter for eia860_plants/battery/wind needs `yyyy`→`yyyy-01-01` padding in 3 ingest scripts; low priority (numeric year-slider works).
- Filter inputs 40px on mobile vs 44px WCAG; acceptable per Apple HIG (≥40px); flag if operator testing surfaces hit-rate issues.

### Audit drift (`bash scripts/audit.sh`)
`OPERATING.md` ≤250 lines · `WIP_OPEN.md` ≤8192 bytes · 0 stranded `refinement-*`/`claude/*` branches on origin · close-out conformance 100%.

---

## Process notes

- `scripts/close-out.sh` enforces atomic deploy+merge and the `refinement-*` branch lifecycle. Use it; don't hand-roll merges to `main`.
- `scripts/audit.sh` is cheap; include it in verification for medium/high blast-radius work.
- The `/*__BUILD_ID__*/` token substitution in `build.py:render_html` (UTC timestamp + nonce) makes `deploy.sh`'s md5-parity poll a reliable readiness signal. Removing the marker breaks the poll.
- Daily probe + W-1 backfill scratch (`data/abatements/abatement_hits_*.csv`, `outputs/refresh/rrc_w1_*`) are gitignored — the unattended daily-refresh routine must never commit them.
