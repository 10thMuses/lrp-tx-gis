# WIP_OPEN.md

Active work. Updated when something completes or a new sprint item is added.

---

## Last deploy

`69f99009df0672911f61e588` — 2026-05-05. Mobile QA hotfix triple in `build_template.html` (topbar overflow, sb-toggle clamp at narrow viewports, tap-to-close drawer). Layer count 24. Build clean `built=26 missing=0 errored=0 tiles_total=12064 KB`.

For older deploy history, `git log --merges --grep "deploy [0-9a-f]" main`.

---

## ⚠ Next action for operator (2026-05-13)

Branch `refinement-rrc-permits-wells` has two unpushed commits (`90234c0`, `e2b8d7d`) on the WSL clone at `~/lrp-tx-gis`. **Both sides — WSL `~/lrp-tx-gis` and Windows `C:\Users\AndreaHimmel\lrp-tx-gis` — have only `.env.example`, no populated `.env` and no `CREDENTIALS.md`.** Credential-cache probing beyond those filenames was declined by the auto-mode classifier, so any locally-cached gh/Netlify CLI tokens were not consulted.

To ship Round 1:
1. On the workstation (either side), `cp .env.example .env` then fill in `GITHUB_PAT` (Contents R/W on `10thMuses/lrp-tx-gis`) and `NETLIFY_PAT`.
2. `git push -u origin refinement-rrc-permits-wells`
3. `bash scripts/deploy.sh --rebuild`
4. `bash scripts/close-out.sh refinement-rrc-permits-wells <deploy-id> "Add wells_pecos11"`

Round 2 spec is in the backlog below — **do not start until R1 is on prod AND the permits layer is unblocked**.

---

## Decision log — 2026-05-13 — RRC permits/wells sprint scope pivot

Sprint spec asked for two new layers (`permits_pecos11` + `wells_pecos11`, 1976-present, with lat/lon, 11 Permian counties). Delivered one (`wells_pecos11`) and deferred the other after source-discovery probing.

**What works:**
- `scripts/fetch_rrc.py` — RRC GoAnywhere PrimeFaces POST scrape (validated end-to-end). GET MFT folder link → harvest JSESSIONID + ViewState → POST row id to `/webclient/godrive/PublicGoDrive.xhtml`.
- `scripts/parse_rrc.py wells` — streams `dbf900.txt.gz` (29.6M segment-records, 1.2M wellbores) in 17s, filters to 11 counties → `data/wells_pecos11.csv`. Layout: `docs/rrc_layouts/wba091_well-bore-database.pdf`. Lat/lon from WBNEWLOC (seg 13) at pos 133/143, PIC S9(3)V9(7) zoned-decimal. RRC convention: longitude stored as positive magnitude — parser forces negative for Texas hemisphere.
- Layer build: 115,908 wells in scope, 101,408 with WGS84 coordinates (87.5%), 7.6 MB PMTiles, no cardinality issues.

**What's blocked — permits_pecos11:**
- RRC's "Drilling Permit Master & Trailer" file (`daf802.txt.gz`, 1.21 GB) has no published byte-position layout. The "Pending" file IS documented (pendingdrillingpermits.pdf) but its folder has been stale since 2021-02. The "EOM + Lat/Lon" `daf420.dat.MM-DD-YYYY` series has lat/lon but no public layout.
- Existing `scripts/scrape_rrc_w1.py` covers permit listing rows 1976-present but defers lat/lon to per-permit detail-page fetches (~40h throttled for the full Permian backfill).
- ARCHITECTURE.md §11 entry rewritten to reflect the actual blocker; revisit if RRC publishes the daf-series layout OR operator authorizes the long detail-page scrape.

**Deploy + push status:** local build clean (`built=27 missing=0 errored=0 tiles_total=19656 KB`), commit `90234c0` on local branch `refinement-rrc-permits-wells`. Push to origin AND deploy both blocked: this WSL clone has no `NETLIFY_PAT`, no `GITHUB_PAT`, no `.git-credentials`, no SSH key, no `gh` CLI — `git push` exits with `could not read Username for 'https://github.com'`. To ship: populate `.env` (both PATs) on the operator workstation, then `git push -u origin refinement-rrc-permits-wells && bash scripts/deploy.sh --rebuild && bash scripts/close-out.sh refinement-rrc-permits-wells <deploy-id> "Add wells_pecos11"`.

## Round 2 backlog — Hanwha thesis features (gated)

Round 2 spec received 2026-05-13. Ten items (R2-1 … R2-10) covering: wells filter to active+drilling, permits filter to production-purpose only, full historical depth (1976/1964-present), sidebar filter UX overhaul, oil/gas color + depth-scaled symbol size, time-series scrubber, live stats panel with PDF/CSV/XLSX export, Pecos-vs-active-Permian-peers comparison, pre-baked thesis bookmarks, verification + ship.

**Hard gate:** Round 2 explicitly conditions on "After the current RRC permits/wells task (Round 1) ships to prod, execute this Round 2 batch autonomously." R1 has not shipped to prod (push + deploy both blocked above).

**Soft gate — permits layer:** every R2 item that touches permits (R2-2, R2-3 perm half, R2-4 perm filters, R2-5 perm color, R2-6 perm half of scrubber, R2-7 perm stats panel, R2-8 perm comparison, R2-9 perm bookmarks) depends on `permits_pecos11` being a real layer. That layer is still scoped-out per the Round 1 decision above. R2-8 also wants Midland + Ector counties added for peer comparison — outside the 11-county scope by design.

**Foldable into R1 (deferred to keep R1 atomic per user's own protocol):** R2-1 (wells active+drilling filter at the parse layer) — would require remapping WBROOT plug_flag + active_flag codes to a true status field; R2-3 wells half (spud date) — would require adding WBDATE segment (key 03) `WB-W2-G1-DATE` to the parser; R2-5 wells color/size — pure `layers.yaml` edit. None folded; the user's instruction is "Each item is its own atomic branch." Once R1 ships, these become R2-1, R2-3, R2-5 atomic branches.

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

**Resume:** when CSV exists at `data/ercot_queue_overrides.csv`, run `python3 scripts/geocode_ercot_queue.py --stage 3` (or whatever the script expects — verify against Stage 2 invocation pattern). Then full build, deploy, verify aggregate match rate against Stage 2 baseline, commit + merge.

**Acceptance for Stage 3:**
- `coords_source = manual_override` rows in built registry equal CSV row count
- Aggregate solar+wind+battery match rate logged and improved vs Stage 2
- No regression in Stage 1+2 rows (algorithmic matches preserved)

### Counties color holistic contrast review

`#fbbf24` (amber) was chosen under time pressure as a basemap-universal hotfix. Worth a calm review: verify against `satellite`, `carto_light`, and dark basemaps; check for clash with hyperscale campus strokes (`la_escalera`, `gw_ranch`, `longfellow_ranch` lines) and tiger_highways amber. Pick a color that survives all three basemaps without competing with overlays. Pure `layers.yaml` edit + visual review.

### county_labels render review

If operator-named counties still appear unlabeled at zoom 7–9, inspect MapLibre `text-allow-overlap` / `symbol-sort-key` / `text-padding` on the county_labels source-layer config in `build_template.html`. Conditional on visual confirmation that the issue still exists.

### Mobile popup audit

Chat-mode Chat 127 fixed three mobile chrome issues. Remaining mobile risk is feature-popup density: `ercot_queue` group-aggregation popup can have many breakdown rows; `tax_abatements` popup carries long text fields. Verify `60vh` max-height + scroll behavior holds at mobile widths against the worst-offender popups. Diagnostic-first; if no issues found, no deploy needed.

---

## Backlog

### Infrastructure

- Akamai datacenter-egress block on `reevescounty.org` 403s any cloud-runner traffic regardless of UA / TLS fingerprint. Hard prerequisite for the Reeves County abatement-weekly-cron sprint item if it ever resumes. Unblock paths: residential-proxy egress (paid), Akamai allowlisting via Reeves County IT (low likelihood), search-API result pages.
- `GITHUB_PAT` can push branches and merge, returns 403 on PR creation. Direct-merge-to-main is the protocol per `OPERATING.md §6`.

### UI / UX

- Counties outline color `#fbbf24` revisit (see active sprint above).
- `date_range` filter literal extension to eia860_plants/battery/wind would require padding `yyyy` → `yyyy-01-01` in 3 ingest scripts (`refresh_eia860.py` plants/battery + `refresh_uswtdb.py` wind). Currently those layers use `numeric` year-slider — works fine, low priority.
- Filter inputs (`.filter-text`, `.filter-range input`) are 40px on mobile, not strictly the 44px WCAG bar. Acceptable per Apple HIG (≥40px) but flag for review if operator testing surfaces hit-rate issues.
- `county_labels` declutter at low zoom — 254 labels means MapLibre symbol-collision will hide overlaps below ~zoom 7. Conditional sprint item above; do not pre-empt visual review.

### Audit drift (run `bash scripts/audit.sh` to recheck)

- `OPERATING.md` line count vs ≤250 target
- `WIP_OPEN.md` byte count vs ≤8192 target
- Stranded `refinement-*` branches on origin (should be 0)

---

## Process notes

- `scripts/close-out.sh` enforces atomic deploy+merge and the `refinement-*` branch lifecycle. Use it; don't hand-roll merges to `main`.
- `scripts/audit.sh` is cheap to run after any drift-prone change. Includes it in the verification step for medium/high blast-radius work.
- The `/*__BUILD_ID__*/` token substitution in `build.py:render_html` (UTC timestamp + nonce) is what makes `deploy.sh`'s md5-parity poll a reliable readiness signal. Removing the marker would break the poll.
