# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat

**Chat 103 — DOC-ONLY: PROMOTE FRESH-CONTAINER FIX TO `session-open.sh`.** Two recurring gaps confirmed across Chats 100, 101, 102: (a) `cairosvg` (pip) and `tippecanoe` (apt) not preinstalled in fresh containers; (b) `scripts/close-out.sh` fails on missing git identity. Both have been worked around three chats running. Per OPERATING.md §14, structural fix beats prose rule.

### Task

1. **Patch `scripts/session-open.sh`** to install build deps and set git identity if missing. Suggested block at top of script after the branch-checkout phase:
   - `command -v tippecanoe >/dev/null 2>&1 || apt-get install -y tippecanoe >/dev/null 2>&1`
   - `python3 -c "import cairosvg" 2>/dev/null || pip install -q cairosvg --break-system-packages`
   - `git config user.email >/dev/null 2>&1 || git config user.email "claude@anthropic.local"`
   - `git config user.name >/dev/null 2>&1 || git config user.name "Claude"`
2. **Smoke-test inside this chat** by re-running `bash scripts/session-open.sh refinement-chat103-session-open-fix` after editing — should be idempotent (deps already installed = no-op).
3. **Doc-only commit** — no build, no deploy. Per §12 budget: 2–6 tool calls.
4. WIP next-chat = Chat 104 (DC auto-refresh cron — still blocked on Anthropic API key in repo secrets; if still blocked, jump to abatement workstreams).

### Acceptance

- `scripts/session-open.sh` includes idempotent install + identity blocks.
- Re-running `session-open.sh` in same chat does not error.
- Pre-flight blocks for "known close-out script gap" and "known build dep gap" can be removed from `## Next chat` for Chat 104.
- Branch merged + deleted same chat per §6.12.
- No build / deploy.

### Branch

`refinement-chat103-session-open-fix`

### Pre-flight

- Chat 102 shipped clean. ERCOT queue project aggregation popup live on prod (deploy `69ee07134b63d09184004cf9`). Layer count 26. Build-time aggregation in `compute_ercot_group_aggregates(csv_path)` streams `combined_points.csv` once and returns `{group_key: {group_total_mw, group_count, group_breakdown}}`; `split_combined_csv()` accepts the dict and stamps the three derived fields onto each `ercot_queue` feature's props before NDGeoJSON write. PMTiles metadata schema confirms encoding: `group_total_mw: Number`, `group_count: Number`, `group_breakdown: String`. Build agg log: `1205 groups, 394 with 2+ components` — exact match to recon. Test case LONGFELLOW__PECOS recon-verified at 6 rows / 2153.3 MW.
- Popup helper `ercotQueueGroupSummaryHtml(props)` renders summary block (total MW, component count, breakdown ul) above per-row table when `group_count > 1`; empty for singletons. Wired into existing `ercotQueuePopupHtml` dispatcher (no `layers.yaml` change needed; ERCOT popup uses dedicated function not registry-iterated).
- **Deviation from prior WIP task #2 (atomic CSV rewrite):** chose build-time stamping over `combined_points.csv` rewrite. Derived fields stay in code, source CSV stays canonical, no §6.15 atomic-write needed. The user-visible outcome (each tile feature carries its group's aggregates) is identical.
- Sprint queue: session-open structural fix (this chat) → DC auto-refresh cron (still blocked on API key) → abatement workstreams.
- Tool budget for Chat 103 doc-only: 2–6 (single edit, smoke-test, commit, push, close-out).

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### DC AUTO-REFRESH CRON

`.github/workflows/dc-anchors-refresh.yml`. Cron `0 6 * * 1`. Refresh script in `scripts/refresh_dc_anchors.py` reads existing `dc_anchors.json` + watchlist URL feed; LLM-in-the-loop parser proposes diffs (status changes, capacity revisions, new entries flagged `single_source: true`); diffs surface as PR for human review (never auto-merged). **Hard prerequisite:** Anthropic API key in repo secrets — operator must add via GitHub UI; PAT lacks scope. 1 chat once unblocked.

### ABATEMENT PERMIAN-CORE + PERIPHERAL

Permian-core (Andrews, Ector, Glasscock, Loving, Martin, Midland, Ward, Winkler) → peripheral (Crane, Crockett, Irion, Reagan, Schleicher, Sutton, Upton) county scrape sequence. 4–6 chats. **Hard constraint:** CivicEngage/Akamai bot-block on `reevescounty.org` extends to any county on the same CMS hosting platform — adapter fixes verifiable only after residential-proxy or whitelisted egress provisioned. Detail in `docs/sprint-plan.md`.

### COMPTROLLER LDAD SCRAPE

Supersedes prior "operator manual XLSX download" ask. There is no bulk XLSX. Canonical source: `https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`. Blocked pending operator authorization for JS-rendered scrape (Selenium / Playwright — same authorization class as CRPUB / RRC MFT). Until authorized: backstop only.

### ABATEMENT WEEKLY CRON

`.github/workflows/abatement-scrape.yml`. Cron weekly Monday 06:00 UTC. Commit diff to `data/abatements/abatement_hits_latest.csv` + rolling history. **Hard prerequisite:** `reevescounty.org` Akamai block must be resolved before cron ships, otherwise Reeves silently produces 0 hits.

### MOBILE STAGE 3 — HOTFIX ON DEMAND

Cross-device QA + polish for the mobile-friendly map work shipped in Chats 100–101. Not scheduled. Surfaced issues become discrete patch chats. 0–1 chat per issue.

---

## Prod status

- Layer count: **26**
- Last published deploy: `69ee07134b63d09184004cf9` (Chat 102, 2026-04-26). State=ready. ERCOT queue project aggregation popup. `compute_ercot_group_aggregates(csv_path)` streams `combined_points.csv` once and returns `{group_key: {group_total_mw, group_count, group_breakdown}}` (breakdown is `\n`-joined `<name> · <mw> MW · <county>` lines, sorted by MW desc). `split_combined_csv()` stamps these fields onto every ercot_queue feature's props during NDGeoJSON write. Popup helper `ercotQueueGroupSummaryHtml(props)` renders a summary block (sage-pink card with project group label, total MW, component count, breakdown list) above the per-row table when `group_count > 1`; empty for singletons. Build clean: `built=26  missing=0  errored=0  tiles_total=18933 KB` (+68 KB from prior deploy carrying 3 new fields × 1,778 ercot_queue rows). Local↔prod md5 identical. Aggregation reach: 1,205 groups total, 394 with 2+ components.
- Previous deploy: `69edeb7d83b23c994ffd00ed` (Chat 101, 2026-04-26). Mobile stage 2: gesture rotation disabled below 768 px via matchMedia, measure-vertex radius 4→12 on mobile, `.measure-readout` close button, `#btn-print` collapses drawer on mobile.
- URL: `https://lrp-tx-gis.netlify.app` — requires real User-Agent on curl (`-A "Mozilla/5.0"`).

---

## Open backlog

**Data-pipeline gaps** (non-blocking):
- `eia860_plants`: 476/1367 rows still null `capacity_mw` (down from 529), 529/1367 null `commissioned`, 438/1367 null `technology`. EIA-860 source-side gaps; will not improve without alternate source.
- `wind`: USWTDB schema has no `operator`, `technology`, or `fuel`; structural blanks (19464/19464). `commissioned` populated for 19364/19464 (down from 0); `manu` and `model` populated. Filling operator would require joining a project-layer source (e.g. EIA-860 wind plants) — separate sprint item if pursued.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar
- BEAD `bead_fiber_planned` layer (Chat 91 §1 dropped): BDO XLSX trio archived to `data/bead_bdo/` but contains no county or coords. Three unblock paths documented in `data/bead_bdo/README.md`

**UI/UX:**
- `date_range` filter type not implemented (carryforward from Chat 92 handoff). `tax_abatements` `commissioned` filter ships as `text` multi-select over distinct ISO dates — functional with 9 rows but not a true range slider. Touches `build.py compute_filter_stats` + `build_template.html filterFieldControlHtml` + matching predicate.
- Filter inputs (`.filter-text`, `.filter-range input`) sized at 40 px on mobile (Chat 100), not strictly the 44 px WCAG bar. Acceptable per Apple HIG (≥40 px) but flag for review if operator testing surfaces hit-rate issues.

**Infrastructure:**
- `NETLIFY_PAT` absent from `CREDENTIALS.md`. Netlify MCP proxy path canonical
- `GITHUB_PAT` can push branches, 403 on PR creation. Direct-merge-to-main is the protocol (OPERATING.md §9)
- **Akamai datacenter-egress block on `reevescounty.org`** — cloud-runner / GitHub-Actions traffic 403s regardless of UA / TLS fingerprint. Hard prerequisite for the abatement-weekly-cron sprint item. Unblock options: residential-proxy egress (paid), Akamai allowlisting via Reeves County IT (low likelihood), search-API result pages
- Fresh-container build deps + git identity gaps — promoted to **active fix in Chat 103**. Currently both worked around manually (cairosvg + tippecanoe install at session start; `git config user.email/.name` before close-out.sh).

**Process:**
- Chat 92 §6.12 violation (deploy + merge atomic): published deploy `69ed2cdf4039c554a1316ad2` to prod but deferred close-out merge, citing scope-creep. Reconciled in Chat 93 (merge `3a59a73`). Root cause: doc-restructure work appeared on a feature branch alongside the data-layer work, blowing past §6.13 stage-fits-one-chat. Preventive structural fix: pre-commit hook could reject doc-structure changes on `refinement-*` branches; lower-effort alternative is operator-side discipline at branch-naming time.
- Chat 100 §6.12 deviation: deploy + merge were not atomic in the same chat. Tracked as fixed via session-open.sh structural fix scheduled for Chat 103.
- Chats 101 + 102 §6.12 compliant: deploy + merge atomic in single shipping flow.
- Chat 102 tool-budget overrun: 14 tool calls vs 6–8 estimate. Cause: heavy verification of stamped-fields encoding (tippecanoe-decode iterations + pmtiles metadata read) before deploying. Lesson: PMTiles metadata schema check via python-pmtiles is the single sufficient verification step; skip tippecanoe-decode tile-by-tile sampling.

**Outstanding credential hygiene:**
- `GITHUB_PAT` leak from Chat 87 unrotated per operator override. Token valid until 2027-04-21

**Permanently excluded:** see ARCHITECTURE.md §11

**Other (non-GIS):** Grid Wire Vol. 7. Tier 2 water availability assessments. Excel returns model.
