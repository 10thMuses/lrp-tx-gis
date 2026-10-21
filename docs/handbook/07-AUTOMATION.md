# 07 — Automation

Three scheduled jobs run against this project. Two live in the repo as GitHub Actions
workflows. The third — the most consequential — lives entirely inside a Claude scheduled
Routine in a personal account and is **captured here for the first time** so it survives
the account migration.

| Job | Where it lives | Schedule | Deploys to prod? |
|---|---|---|---|
| `build-and-deploy` | `.github/workflows/build-and-deploy.yml` | Manual only | **Yes** |
| `dc-anchors-refresh` | `.github/workflows/dc-anchors-refresh.yml` | Mondays 06:00 UTC | No — opens a PR |
| `lrp-gis-daily-refresh` | Claude Routine `trig_01JtgtPFhaDrd7TajmvN6YHi` | Daily 06:00 UTC | **Yes**, conditionally |

---

## 1. `build-and-deploy.yml`

A cloud-side build + deploy fallback for machines without tippecanoe — native Windows,
or any restricted environment.

**Trigger:** `workflow_dispatch` only. Deliberately **no** push or PR trigger, so a
routine commit can never surprise-deploy production. Optional `message` input lands in
the Netlify deploy log.

**Steps:** checkout → Python 3.11 → `apt-get install tippecanoe` →
`pip install pyyaml cairosvg pmtiles` → `python3 build.py` (tee'd to `build.log`) →
verify `dist/index.html` exists **and** the log contains `errored=0` → install Netlify
CLI → `netlify deploy --prod` → sleep 30 s → check prod returns 200.

**Secrets:** `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID`. The workflow fails with an
explicit message naming the settings URL if either is unset.

> **Gap:** this path does **not** run `scripts/verify_deployed_layers.py`. The local
> `deploy.sh` treats that check as a hard gate (exit 7) before close-out; the cloud path
> skips it entirely. After any cloud deploy, run it yourself:
>
> ```bash
> python3 scripts/verify_deployed_layers.py
> ```
>
> Adding the check as a workflow step is a 10-line fix and is on the backlog.

---

## 2. `dc-anchors-refresh.yml`

A Claude-in-the-loop weekly refresh of `data/datacenters/dc_anchors.json`.

**Schedule:** `0 6 * * 1` — Mondays 06:00 UTC (01:00 CST / 02:00 CDT), plus manual
dispatch. Permissions: `contents: write`, `pull-requests: write`.

### 2.1 What it does

1. Runs `scripts/refresh_dc_anchors.py` with `ANTHROPIC_API_KEY`.
2. The script reads `dc_anchors.json`, fetches every entry's cited source URLs (3
   attempts, 30 s timeout, 5 s backoff), and asks the Anthropic API
   (`claude-sonnet-4-5-20250929`, 2,000 max tokens) to propose factual updates to
   `status`, `capacity_mw`, `commissioned_target`, `power_source`, or `sources`.
   **It never proposes coordinate edits** — hard rule 3 applies to automation too.
3. Writes `outputs/refresh/dc_anchors_proposed.json` atomically.
4. Counts "meaningful" proposals — anything with a `diff`, `additional_sources`,
   `conflicts`, `parse_error` or `error`.
5. If any exist, opens a PR on branch `dc-anchors-refresh-<run_number>` containing only
   the proposal file, with a review checklist in the body.

### 2.2 The review checklist

The PR body carries it, and it is worth following:

- Confirm each proposed `diff` against the cited `evidence_url` and `evidence_quote`
- Confirm `additional_sources` add real signal rather than duplicates
- Investigate `conflicts` — usually a source page changed but the canonical value is
  still right
- Investigate `fetch_failures` — paywalls, dead links, layout changes
- If accepting any diffs, **manually edit** `data/datacenters/dc_anchors.json` and bump
  its `generated` date
- Delete `outputs/refresh/dc_anchors_proposed.json` after applying or rejecting

**Never merge the PR as-is.** It contains proposals, not approved updates.

Exit codes for the script: `0` clean (proposal file written, possibly empty) · `1` no API
key · `2` no input file · `3` API error after retries.

### 2.3 The stale-PR problem

The workflow is correct: it never auto-merges. But nothing closes the PRs it opens, and
**13 have accumulated since 2026-05-25** (PRs #10, 11, 12, 16, 21, 26, 28, 29, 32, 34,
35, 36, 37). Each carries `delete-branch: true`, so closing the PR cleans up its branch.

Two fixes worth making:

1. **Operationally** — review and close the open PRs weekly, or close them in bulk and
   only review the newest. A proposal from May is worthless in August.
2. **Structurally** — have the workflow close its own prior open PRs before opening a new
   one, so at most one is ever outstanding. Per `OPERATING.md §8`, prefer the structural
   fix.

---

## 3. The daily-refresh Routine

### 3.1 Configuration

| Field | Value |
|---|---|
| Name | `lrp-gis-daily-refresh` |
| Trigger ID | `trig_01JtgtPFhaDrd7TajmvN6YHi` |
| Cron | `0 6 * * *` (daily 06:00 UTC) |
| Created | 2026-05-18 |
| Environment | `env_014kr4fojXSHmvSLCusx89TU` |
| Model | `claude-sonnet-4-6` |
| Tools allowed | `Bash`, `Read`, `Write`, `Edit`, `Glob`, `Grep` |
| MCP connections | Netlify (`https://netlify-mcp.netlify.app/mcp`) — the routine deploys through MCP, **not** through a local `NETLIFY_PAT` |
| Source | `https://github.com/10thMuses/lrp-tx-gis` |
| Notifications | Push on |

Output: one report per run at `outputs/refresh/daily/<YYYY-MM-DD>.md`, merged to `main`.
**89 reports exist**, from 2026-05-18 to 2026-08-18.

> **The contract below existed nowhere in the repo.** It lives only in the trigger's
> configuration. Reproduced verbatim so it survives the migration — recreate the Routine
> from this text, changing only the repository URL and the stale paragraph flagged in
> [§3.3](#33-known-contract-staleness).

### 3.2 The contract prompt (verbatim)

```text
You are the unattended DAILY DATA-REFRESH routine for the LRP Texas Energy GIS map
(production; distributed to industry peers). Repo github.com/10thMuses/lrp-tx-gis is
checked out at branch main. NO prior context, NO local .env. Work fully autonomously;
never wait for human input. Correctness over completeness — a safe no-op beats a broken
deploy. NO HUMAN IS WATCHING: the run is observed only through git, so every outcome
MUST be committed as a run report (step 6).

Let DATE = today's UTC date YYYY-MM-DD (`date -u +%F`).

=== ENVIRONMENT REALITY (KNOWN — do NOT re-litigate, retry, or belabor) ===
This routine runs from Anthropic-cloud egress. RRC GoAnywhere MFT (mft.rrc.texas.gov)
and Census TIGER return HTTP 403 from cloud IPs. Therefore wells, permits, AND
ercot_queue are EXPECTED to fail 403 every run here. That is a known infra limitation,
NOT a per-run anomaly: record each as `blocked(403)` tersely and move on — no extra
retries, no investigation, no workarounds. abatements (county WordPress/CivicEngage
sites) is NOT cloud-blocked and is the only data step expected to succeed. A run where
wells/permits/ercot are blocked and abatements has 0 in-scope hits is a correct, healthy
NO-OP — not a failure.

=== CONTRACT (violating ANY = CONTRACT FAILURE; say so loudly in step 7) ===
- Feature branch is EXACTLY `refinement-daily-refresh-DATE`. No other name. (Run #1
  2026-05-18 wrongly used `refinement-daily-abatements-snapshot` — never do that.)
- Attempt ALL FOUR steps every run (wells, permits, ercot_queue, abatements). A
  blocked/failed source is RECORDED; you CONTINUE — never skip the rest, never narrow
  scope.
- Every run commits the step-6 report and emits the step-7 summary line. No exceptions.

=== SETUP ===
1. `bash scripts/bootstrap-claude-code.sh` (idempotent).
2. If unset: `git config user.name "Claude (LRP GIS)"`; `git config user.email
   "noreply@anthropic.com"`.
3. Read CLAUDE.md, OPERATING.md (§3 hard rules, §4 build, §8.7 deploy gate), headers of
   scripts/deploy.sh + scripts/close-out.sh.

=== HARD RULES (violate one = abort that action, record it, no workaround) ===
- NEVER `git add -A`. Stage only explicit, individually-named paths.
- NEVER deploy without the matching close-out merge in the SAME run.
- NEVER hand-edit data or coordinates.
- If `python3 build.py` reports errored>0: STOP — no deploy, no merge.

=== STEP 1 — branch ===
`git checkout main && git pull --ff-only` then `git checkout -b
refinement-daily-refresh-DATE`.

=== STEP 2 — reachability preflight ===
For each of RRC MFT (https://mft.rrc.texas.gov) and ERCOT (https://www.ercot.com):
`curl -s -o /dev/null -w "%{http_code}" --max-time 10`. Classify 2xx/3xx=`ok`,
401/403=`blocked`, 000/timeout=`unreachable`. Record verbatim in the step-6 report.
Expected: both `blocked`.

=== STEP 3 — refresh ALL FOUR (each INDEPENDENTLY GATED: nonzero exit → record
blocked/FAILED + error tail, CONTINUE). Capture exit code + one-line result each: ===
a. wells:   `python3 scripts/fetch_rrc.py wells && python3 scripts/parse_rrc.py wells`
b. permits: `python3 scripts/fetch_rrc.py permits && python3 scripts/parse_rrc.py permits`
c. ercot:   `python3 scripts/geocode_ercot_queue.py`
d. abate:   `python3 scripts/scrape_abatements.py`

=== STEP 4 — WHAT COUNTS AS A CHANGE (read carefully — this is exactly where Run #1 went
wrong) ===
- `data/wells_permian6.csv` and `data/permits_permian6.csv` are .gitignored: NEVER
  committed; they reach the map only via `combined_points.csv` after `python3 build.py`.
- `scripts/scrape_abatements.py` writes a NEW `data/abatements/abatement_hits_<ts>.csv`
  every run. This is a PROBE/diagnostic artifact, NOT a layer source (the tax_abatements
  layer is fed by a pinned snapshot via scripts/transform_abatements.py). DO NOT
  `git add` it, EVER, under any name. Its hit count goes ONLY in the step-6 report.
  (.gitignore excludes these except the pinned source; do not force-add. Run #1
  committing this file under an invented branch was THE defect — do not repeat.)
- The ONLY deployable data change is a diff in a MAP-RENDERED tracked file:
  `combined_points.csv` or `combined_geoms.geojson`.
- `git status --porcelain`. If `combined_points.csv`/`combined_geoms.geojson` did NOT
  change: this run is a NO-OP (the normal, correct outcome when RRC/ERCOT are blocked).
  NO data commit. Go to step 6 (report only). If one DID change: stage ONLY that explicit
  path, `git commit -m "daily auto-refresh DATE: <changed layers>"`, then step 5.

=== STEP 5 — build + deploy (ONLY if step 4 committed a combined_* change) ===
- `python3 build.py`. errored>0 → STOP, no deploy/merge, result=FAILURE (build errored);
  step 6 then 6b build-fail path.
- `bash scripts/deploy.sh --rebuild` (includes §8.7 verify_deployed_layers.py gate; uses
  the ATTACHED NETLIFY MCP — no local NETLIFY_PAT). Capture the single-line deployId.
  deploy.sh nonzero → STOP, no merge, result=FAILURE naming the missing/empty layers from
  the §8.7 log.

=== STEP 6 — run report (ALWAYS, every run, before close-out) ===
Write `outputs/refresh/daily/DATE.md`: step-2 preflight table; per-step status table
(step | class ok/blocked/unreachable | exit | rows-delta or "no change" | reason); deploy
result; the step-7 summary line. `git add` ONLY `outputs/refresh/daily/DATE.md` (plus
combined_* iff step 4 committed it). Commit: if a step-4 data commit exists, add
`git commit -m "daily auto-refresh DATE: report"`; else `git commit -m "daily
auto-refresh DATE: none (report only)"`. NEVER stage data/abatements/*. This report is
the ONLY way the operator sees the outcome.

=== STEP 6b — close-out / branch hygiene ===
- Success or NO-OP: `bash scripts/close-out.sh refinement-daily-refresh-DATE
  <deployId-or-none> "daily auto-refresh DATE"` — merges --no-ff into main, pushes,
  DELETES origin branch. A stranded refinement-* branch = CONTRACT FAILURE (OPERATING.md
  §7 target 0).
- close-out fails on missing GitHub write creds → state LOUDLY in step 7; leave the
  branch (the ONE acceptable stranded branch: a NAMED failure awaiting human merge).
- build-errored/deploy-failed → push the branch WITH the step-6 report on it for
  inspection; do NOT merge; step 7 states FAILURE.

=== STEP 7 — final summary line (the deliverable; also embedded in the report) ===
EXACTLY ONE line, nothing after it:
`[daily-refresh DATE] preflight=<rrc:ok|blocked|unreachable,ercot:...>
steps=<wells:ok|blocked|fail,permits:...,ercot:...,abate:ok|fail(<n>hits)>
rendered_change=<combined_points|combined_geoms|none> result=<deployId | NO-OP prod
already current | FAILURE: reason> report=outputs/refresh/daily/DATE.md`

Be precise and terse. The summary line + committed report are the deliverables.
```

### 3.3 Known contract staleness

**Fix this when you recreate the Routine.**

The `ENVIRONMENT REALITY` block asserts that RRC MFT, Census TIGER and ERCOT return
**HTTP 403 from cloud egress**, and instructs the routine to record them as
`blocked(403)` without investigation. That was true when the contract was written on
2026-05-18. It is no longer true.

The 2026-08-18 report shows:

| Step | Result |
|---|---|
| RRC MFT preflight | **302**, classified `ok` |
| ERCOT preflight | **200**, `ok` |
| wells | `ok`, exit 0, **99,808 rows**, 367.8 MB archive |
| permits | `ok`, exit 0, **28,842 rows**, 108 EOM snapshots |
| ercot_queue | `ok`, exit 0, 1,778 rows, 479 non-centroid (26.9%) |
| abatements | `ok`, exit 0, 16 hits (Pecos 23, Reeves 0) |

All four steps succeed. Leaving the stale paragraph in place tells the routine to
under-investigate real failures, because it has been pre-told that failure is normal.

**Also note:** the contract lists `rapidfuzz`, `beautifulsoup4`, `pyshp` and `shapely` as
installed at runtime because `bootstrap-claude-code.sh` does not install them. Either add
them to the bootstrap script or keep the runtime install — but say so in one place, not
two.

### 3.4 Why most runs are no-ops

This is correct behaviour, not a malfunction:

- `data/wells_permian6.csv` and `data/permits_permian6.csv` are **gitignored**. Refreshing
  them changes nothing tracked. They reach the map only through a `build.py merge` and a
  full rebuild, which the routine does not perform.
- The ERCOT geocode rewrites `combined_points.csv` **atomically and idempotently** — same
  inputs produce byte-identical output, so `git status` is clean.
- The abatements probe writes a diagnostic file that must never be committed.

So the routine only ships when `combined_points.csv` or `combined_geoms.geojson` actually
differs. In practice it commits a report and occasionally an updated ERCOT geocode log.

That said, if the routine is refreshing 99,808 wells rows daily and none of it ever
reaches the map, it is doing 370 MB of work for a liveness check. Either wire the merge +
rebuild into the routine, or drop the wells/permits steps to weekly and be explicit that
the daily job is a source-availability monitor. Choose deliberately — see
[`08-ROADMAP-AND-GAPS.md §5`](08-ROADMAP-AND-GAPS.md#5-automation-improvements).

### 3.5 Migration

Routines cannot be transferred between accounts. Recreation steps:
[`00-MIGRATION-RUNBOOK.md §7.2`](00-MIGRATION-RUNBOOK.md#72-migration-steps).

---

## 4. The unbuilt automation

`docs/refresh_automation_plan.md` (2026-05-13) specifies a `weekly-refresh.yml` workflow
that would run every refresh script in dependency order, commit deltas to a
`refinement-weekly-refresh-<date>` branch, then build and deploy behind the `errored==0`
gate. It was scoped as planning-only and **never implemented**.

The plan's recommendations, still open for sign-off:

| Decision | Recommendation |
|---|---|
| Frequency | Weekly (Mondays 06:00 UTC) — matches the RRC wellbore cadence without daily-cron overhead |
| Notification | GitHub Actions email — sufficient for a small team |
| Timing | 06:00 UTC = 01:00 CDT, so the operator wakes to a fresh deploy |
| Branch model | Auto-merge to `main` when `errored==0`; refresh deltas are data-only |
| Single-layer failure | Continue with other layers, flag in the commit message, deploy with the stale layer — stale-but-stable beats no update |

Estimated effort: 6–7 hours. Note that the daily Routine has since occupied most of this
niche, so implementing the plan as written would duplicate it. Decide which one is
canonical before building the other.

---

## 5. Automation inventory summary

| Concern | Covered by | Status |
|---|---|---|
| Daily source-availability check | `lrp-gis-daily-refresh` Routine | ✅ Running, 89 reports |
| Weekly DC anchors review | `dc-anchors-refresh.yml` | ⚠️ Running, but 13 PRs unreviewed |
| On-demand cloud build/deploy | `build-and-deploy.yml` | ✅ Working, but skips the layer-verification gate |
| Weekly full refresh + deploy | `docs/refresh_automation_plan.md` | ❌ Planned, never built |
| Data reaching the map from the daily refresh | — | ❌ Not wired — the daily job never merges or rebuilds |
| Alerting on a failed run | GitHub email / Claude push | ⚠️ Push notifications on the Routine only |
