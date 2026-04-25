# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per OPERATING.md §10: **`## Next chat`** = task spec for the immediately-next shipping chat. **`## Sprint queue`** = N+2 and beyond. Multi-step sprint detail lives in `docs/sprint-plan.md` (deleted per item when shipped).

---

## Next chat

**Chat 93 — CHAT 92 §6.12 RECONCILIATION.** No build, no deploy. Branch `refinement-chat92-field-expansion-wells` carries §1+§2+§3 commits already serving prod (deploy `69ed2cdf4039c554a1316ad2`), but Chat 92 deferred close-out per scope-creep flag — silent regression per §6.12. Reconcile branch state, resolve duplicate build.py work, merge to main, delete branch.

### Task

1. On `refinement-chat92-field-expansion-wells`: `git revert f343506 --no-edit`. Pushes a revert of the stale-format WIP_OPEN.md rewrite (was authored against pre-Audit-1 file structure). Post-revert the branch's WIP_OPEN.md matches merge-base, so the merge below carries no WIP_OPEN.md conflict. Push.
2. Same branch: `git rm docs/_chat92-field-expansion-wells_handoff.md` per §10 (handoff doc deleted before merge). Commit `Chat 93: delete chat92 handoff doc per §10`. Push.
3. Checkout main → `git pull --rebase origin main` → `git merge --no-ff origin/refinement-chat92-field-expansion-wells -m "Merge refinement-chat92-field-expansion-wells (Chat 93): Chat 92 deploy reconciliation (deploy 69ed2cdf4039c554a1316ad2)"`. **Conflict on `build.py`:** branch commit `9082542` adds local merge_csv/merge_geojson temp+rename fix; main's `b9f9553` (Audit-1b) is the canonical implementation. Accept main's version (`git checkout --ours build.py && git add build.py`). Continue merge. Push main.
4. `git push origin --delete refinement-chat92-field-expansion-wells`.
5. Update WIP_OPEN.md `## Next chat` for Chat 94 — pick top viable sprint queue item: ABATEMENT PERMIAN-CORE is blocked on Akamai egress, so next viable is POWER PLANT DATA REFRESH or DC RESEARCH. Operator may direct otherwise. Commit, push.

### Acceptance

- `git ls-remote origin refinement-chat92-field-expansion-wells` empty.
- `git log origin/main -3` includes merge commit referencing `69ed2cdf4039c554a1316ad2`.
- Prod unchanged — no curl needed (recon already verified, see Pre-flight).
- Tool-call budget: doc-only ceiling 6. Single composite bash for steps 1–4; one create_file/str_replace + one bash for step 5.

### Branch

`refinement-chat92-field-expansion-wells` — 5 commits beyond merge-base `3950736`: §1 partial refresh+CSV (`8a396c2`), handoff doc (`3f16b81`), §1 merge + duplicate build.py fix (`9082542`), §1-§3 yaml (`38f8654`), stale-format close-out WIP_OPEN.md (`f343506`).

### Pre-flight

Prior recon chat (this chat) verified prod via `curl -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/`:
- 25 distinct layer ids in prod HTML ✓
- `tceq_gas_turbines` popup_labels carries 12-field expansion (Mode, Number of CTs, Status, Received date, Issue date, Permit No.) ✓
- `tax_abatements` popup_labels carries rename (Applicant, Approved date, Project type, Capex ($M)) ✓
- `min_zoom:10` present in LAYERS payload — wells raised ✓

Chat 92 deployed but never merged. `## Prod status` below already updated to reflect reality.

**Branch divergence:** chat92 branch forked at `3950736` (pre-Audit-1). Main has had Audit-1, Audit-1b, Audit-2, Audit-3 since. Branch never touched any of the consolidated docs (Readme.md, GIS_SPEC.md, principles.md, settled.md, OPERATING.md, ARCHITECTURE.md) so three-way merge resolves all of those to main's version cleanly. Only `build.py` overlaps.

---

## Sprint queue

Ordered by operator priority. N+2 and beyond. Detailed multi-step entries live in `docs/sprint-plan.md`.

### ABATEMENT PERMIAN-CORE + PERIPHERAL

Permian-core (Andrews, Ector, Glasscock, Loving, Martin, Midland, Ward, Winkler) → peripheral (Crane, Crockett, Irion, Reagan, Schleicher, Sutton, Upton) county scrape sequence. 4–6 chats. **Hard constraint:** CivicEngage/Akamai bot-block on `reevescounty.org` extends to any county on the same CMS hosting platform — adapter fixes verifiable only after residential-proxy or whitelisted egress provisioned. Detail in `docs/sprint-plan.md`.

### POWER PLANT DATA REFRESH + POPUP REDESIGN

Re-pull EIA-860 (plants, battery) + USWTDB (wind) to fill blanks; rewrite popup templates for `eia860_plants`, `eia860_battery`, `solar`, `wind`, `ercot_queue` (drop sector; add COD/operator/capacity/fuel). Filter UI reflects same fields. Detail in `docs/sprint-plan.md`.

### COMPTROLLER LDAD SCRAPE

Supersedes prior "operator manual XLSX download" ask. There is no bulk XLSX. Canonical source: `https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`. Blocked pending operator authorization for JS-rendered scrape (Selenium / Playwright — same authorization class as CRPUB / RRC MFT). Until authorized: backstop only.

### ABATEMENT WEEKLY CRON

`.github/workflows/abatement-scrape.yml`. Cron weekly Monday 06:00 UTC. Commit diff to `data/abatements/abatement_hits_latest.csv` + rolling history. **Hard prerequisite:** `reevescounty.org` Akamai block must be resolved before cron ships, otherwise Reeves silently produces 0 hits.

### LEGEND ON PRINT / SHARE / PDF

Print CSS at `build_template.html` hides `.sidebar` on `@media print`. Sidebar IS the legend; prints ship without it. Inject print-only legend element enumerating active layers (name + color swatch + symbol) into print header or footer. Fit within 10.3"×7.1" landscape. Handle >15 active layers via multi-column or multi-page.

### DC RESEARCH → DC BUILD → DC AUTO-REFRESH

3-chat sub-sequence. Research anchors: Longfellow/Poolside (Pecos), Stargate (Abilene), Project Matador/Fermi → structured data file → layer build → GitHub Actions weekly refresh with LLM-in-the-loop parser. Detail in `docs/sprint-plan.md`.

### MOBILE-FRIENDLY MAP

Responsive breakpoints, touch-friendly controls, pinch-zoom tuning, measure tool + print-to-PDF mobile usability, popup sizing. 2–3 chats.

### ERCOT QUEUE PROJECT AGGREGATION POPUP  *(low priority)*

`ercot_queue` has 1,205 distinct project `group` keys; 394 groups have 2+ components. Build-time aggregation in `build.py`: compute `group_total_mw`, `group_count`, `group_breakdown` per group; popup template renders summary line + breakdown list. Test case Longfellow__Pecos: 6 rows, 2,153.3 MW total.

---

## Prod status

- Layer count: **25**
- Last published deploy: `69ed2cdf4039c554a1316ad2` (Chat 92, 2026-04-25). State=ready. Carries §1 tceq_gas_turbines field expansion + §2 tax_abatements popup rename + §3 wells min_zoom 6→10. **Not yet reflected in main's git history** — see `## Next chat` Chat 93 reconciliation.
- URL: `https://lrp-tx-gis.netlify.app` — requires real User-Agent on curl (`-A "Mozilla/5.0"`).

---

## Open backlog

**Data-pipeline gaps** (non-blocking):
- `eia860_plants`: 476/1367 rows null `capacity_mw` / `technology` / `fuel`
- `combined_points.csv` blank `operator` / `commissioned` on EIA point layers
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar
- BEAD `bead_fiber_planned` layer (Chat 91 §1 dropped): BDO XLSX trio archived to `data/bead_bdo/` but contains no county or coords. Three unblock paths documented in `data/bead_bdo/README.md`

**UI/UX:**
- `date_range` filter type not implemented (carryforward from Chat 92 handoff). `tax_abatements` `commissioned` filter ships as `text` multi-select over distinct ISO dates — functional with 9 rows but not a true range slider. Touches `build.py compute_filter_stats` + `build_template.html filterFieldControlHtml` + matching predicate.

**Infrastructure:**
- `NETLIFY_PAT` absent from `CREDENTIALS.md`. Netlify MCP proxy path canonical
- `GITHUB_PAT` can push branches, 403 on PR creation. Direct-merge-to-main is the protocol (OPERATING.md §9)
- **Akamai datacenter-egress block on `reevescounty.org`** — cloud-runner / GitHub-Actions traffic 403s regardless of UA / TLS fingerprint. Hard prerequisite for the abatement-weekly-cron sprint item. Unblock options: residential-proxy egress (paid), Akamai allowlisting via Reeves County IT (low likelihood), search-API result pages

**Process:**
- Chat 92 violated §6.12 (deploy + merge atomic): published deploy `69ed2cdf4039c554a1316ad2` to prod but deferred close-out merge to next chat citing scope-creep. Reconciliation queued as Chat 93. Root cause: doc-restructure work appeared on a feature branch alongside the data-layer work, blowing past §6.13 stage-fits-one-chat. Preventive structural fix: pre-commit hook could reject doc-structure changes on `refinement-*` branches; lower-effort alternative is operator-side discipline at branch-naming time.

**Outstanding credential hygiene:**
- `GITHUB_PAT` leak from Chat 87 unrotated per operator override. Token valid until 2027-04-21

**Permanently excluded:** see ARCHITECTURE.md §11

**Other (non-GIS):** Grid Wire Vol. 7. Tier 2 water availability assessments. Excel returns model.
