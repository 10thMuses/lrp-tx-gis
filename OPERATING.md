# Operating Protocol — LRP Texas Energy GIS Map

**Owner:** Andrea Himmel · **Repo:** github.com/10thMuses/lrp-tx-gis · **Prod:** https://lrp-tx-gis.netlify.app · **Netlify siteId:** `01b53b80-687e-4641-b088-115b7d5ef638`

This is the single operating doc. All execution rules live here. Architecture, schema, layer catalog, palette, fragility live in `ARCHITECTURE.md`.

---

## 1. Source of truth

**Repo > sidebar > memory.** Repo wins on disagreement. Sidebar lags; memory churns. Working dir in-chat is `/home/claude/repo/`; any reference to `/mnt/project/<file>` resolves there. The only `/mnt/project/` file Claude reads is `CREDENTIALS.md` for the GitHub PAT at session open.

Live reads use the GitHub Contents API on first access in a chat. `raw.githubusercontent.com` only for files known stable for hours.

---

## 2. Operator interaction model

Andrea is the operator; Claude is the executor. Every request Claude makes of Andrea is overhead Claude should have absorbed.

**Banned asks:** pasting file contents Claude can fetch, running curl/SQL/CLI Claude can execute, copying text between two places Claude has access to, checking dashboards Claude has API access to, re-typing state Claude can read from `WIP_OPEN.md`, structuring prompts a particular way, confirming actions inside delegated autonomy.

**Banned phrases** (token waste + unnecessary friction): `Should I proceed?` · `Do you want me to?` · `Want me to go ahead and?` · `Would you prefer A or B?` · `Say ship it and I'll...` · `Confirm to ship.` · any phrasing that makes action conditional on operator re-affirmation once the next move is named and unblocked. Also: `let me know if`, `ready to proceed?`, recap sections, history logs.

**Acceptable asks** (narrow list — anything outside this is execution):
1. Irreversible destructive action (force-push, delete deployed PMTiles, drop data file from repo)
2. New spend or external commitment (paid data, new tier, new vendor)
3. Materially-different strategic fork (e.g., switch mapping library — not "blue or green for this layer")
4. Missing credential Claude cannot obtain
5. Factual input only Andrea has (county to target, thesis decision, layer audience)

Target: zero asks per chat. Hard ceiling: one ask per chat, only if the ask blocks shipping. Batch unavoidable asks into a single numbered list at start of response.

**Default to action.** When the next shipping target is named and dependencies clear, ship.

---

## 3. Session classification

Silent triage of the operator's prompt before any tool call. Three buckets:

| Bucket | Signals | Behavior |
|---|---|---|
| Conversational / planning | No imperative verb; words like "morning briefing," "what do you think," "explain," "review." | Answer directly. Read `WIP_OPEN.md` only if the answer depends on active state. No clone. |
| Shipping | Imperative verb (`build`, `refresh`, `add layer`, `deploy`, `rebuild`), handoff doc attached, or prompt names files / layers / sources. | Enter Batch Execution Protocol below. |
| Ambiguous | Mixed. | Default to conversational. One clarifying sentence is cheaper than a wasted clone. |

---

## 4. Batch Execution Protocol — shipping chats only

Silently resolve from prompt + handoff (if attached) + one `WIP_OPEN.md` fetch:

- **State** — prior chat outcome, active workstream
- **Task** — concrete scope in 2–3 sentences
- **Blast radius** — low / medium / high (see §6 verification)
- **Approach** — recon via grep + sed → stage files in `/home/claude/repo/` → commit per unit of work → verify per blast radius → close-out via script

Execute end-to-end without mid-session confirmation.

---

## 5. Session-open and close-out

Both are scripts in `scripts/`. Operator's `## Next chat` block in `WIP_OPEN.md` carries task scope only. Procedural bash is not pasted into WIP_OPEN.

**Session-open** (every shipping chat):

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
cd /home/claude && rm -rf repo 2>/dev/null
git clone -q https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git repo && cd repo
bash scripts/session-open.sh <branch-name>
```

`session-open.sh` enforces three rules mechanically: branch-ahead check (fetch origin; if remote branch has commits, check out, never reconstruct); handoff-doc detection (print `docs/_<slug>_handoff.md` if present); empty-branch upstream push.

**Close-out** (every shipping chat — non-negotiable):

```bash
bash scripts/close-out.sh <branch-name> <deploy-id>
```

`close-out.sh` executes: feature branch push → checkout main → rebase → merge --no-ff with deploy-id in message → push main → delete origin branch → final WIP_OPEN.md commit.

Stop active feature work at ~65% of token budget. Reserve ~35% for close-out + blocker recovery.

---

## 6. Hard rules

**Failure-prevention checks. Violations stop the chat.**

1. **Build never reads source data into model context.** Combined files + standalone data files stream through `tippecanoe` subprocesses only. No `cat` / `head` / `view` of data files — ever. Single biggest token-burn failure mode.
2. **Never fetch during build.** Missing source = skipped layer, logged.
3. **Never hand-code coordinates or feature values.** No source, no layer.
4. **Never re-digitize from PDFs when a vector source exists.** Last resort only; mark `ACCURACY: APPROXIMATE`.
5. **One layer failure never aborts the run.** Try/except at dispatcher.
6. **One chat = one final build.** No version numbering. Output: `dist/index.html` + `dist/tiles/*.pmtiles`.
7. **Adding a layer = one yaml append + one data-file action.** Never edit `build.py` or `build_template.html` for a layer addition.
8. **Do not deploy to prod if `errored > 0`.** Stop and report.
9. **Push-on-commit.** Every `git commit` followed immediately by `git push`. Unpushed commits die on container reset.
10. **Never `git add -A`.** Always stage explicit paths. Working-directory clutter pollutes pack history forever.
11. **Commit every unit.** After every file-modifying step (script patched, data file added, single layer's yaml edited): `git add <paths>` + `git commit` + `git push` before starting the next sub-task.
12. **Deploy + merge + delete-branch is atomic.** Any chat that deploys must also merge to `main` and delete the feature branch in the same chat. Deferring creates silent regression.
13. **Stage fits one chat.** Five+ commits or three+ distinct subsystems = split before starting, not after. A stage resumed via handoff once is acceptable; twice means original scope was two stages pretending to be one.
14. **Recon-only sessions are failures.** Every shipping chat pushes ≥1 non-handoff commit to origin.
15. **Atomic in-place writes.** Any function that may write back to the same path it reads from MUST use temp-file + atomic rename (`os.replace`). Opening the destination in `'w'` mode before the source read completes truncates the source to zero bytes when the paths coincide. Surfaced by the `merge_csv` data-wipe bug; codified to prevent the same shape of bug in any future read-modify-write helper. Symmetric guards required even when one variant happens to be safe by accident (full-load-into-memory).

**Verification proportional to blast radius:**

- Low (yaml tweak, doc edit, WIP update) → skip in-chat, defer to next briefing
- Medium (new layer, new build step, new data source) → bundle hash + 1 curl + 1 tile spot-check
- High (schema change, credential rotation, destructive migration) → full acceptance protocol

---

## 7. Trigger phrases

Optional input shape. Natural-language equivalents route correctly. Operator picks whichever is faster to type.

| Phrase | Action |
|---|---|
| `build.` | Install tippecanoe if needed, run `build.py`, emit `dist/`. No deploy. |
| `build. deploy to preview.` | Build + deploy to Netlify branch preview. |
| `build. deploy to prod.` | Build + deploy to prod. |
| `deploy to prod.` | Re-deploy existing `dist/` without rebuild. |
| `refresh <layer>[, <layer>...].` | Fetch listed layers; write to `outputs/refresh/`. No build. |
| `refresh all.` | Fetch every layer with a known source. |
| `merge <layer_id> from outputs/refresh/<file>.` | Swap layer's rows in combined file; write to `outputs/`. |
| `add layer <id> from outputs/refresh.` | Append to `layers.yaml`, build, deploy to preview. |
| `password-protect with <pw>.` | Netlify access-control MCP. |
| `resume.` | Read `WIP_OPEN.md` `## Next chat`, execute. |

Ambiguity → pick most plausible interpretation, execute, note assumption at close-out. Never ask "should I proceed?".

---

## 8. Build / refresh / merge cycles

**Build cycle** (target 4 tool calls for `build. deploy to prod.`):

1. Composite bash: install tippecanoe if cold, install Python deps, run `build.py`.
2. Netlify MCP `deploy-site` returns single-use proxy URL.
3. CLI proxy: `cd /mnt/user-data/outputs/dist && npx -y @netlify/mcp@latest --site-id <siteId> --proxy-path "<URL>" --no-wait`. Returns `deployId`.
4. Poll `get-deploy-for-site` until `state=ready`. Sleep 45 for CDN warm-up. Verify with `curl -A "Mozilla/5.0"` (default UA returns 503 — bot block on Netlify edge). Grep layer-id count.
5. `present_files dist/index.html`.

**Refresh cycle:**

1. Fetch via `fetch_with_retry(url, attempts=5, sleep=10)`.
2. Validate non-empty, required columns, bounded lat/lon.
3. Simplify line/polygon; round coords; trim to registered fields.
4. Write `outputs/refresh/<canonical_filename>`.
5. One-line diff. Fetch failure = log; do not fake.

**Merge cycle:**

1. Read refreshed file.
2. Read `combined_points.csv` or `combined_geoms.geojson` (streamed; never into context).
3. Drop rows/features where `layer_id == <id>`; append refreshed.
4. Write updated combined file to `outputs/`.

---

## 9. GitHub sync

**Clone-edit-push bracket** for any session that touches files on disk. **Git Data API tree commit** for pure doc-only edits (no clone needed).

**Branch naming:** `refinement-chatN-<slug>` for shipping chats. `<slug>` is 2–4 words describing the change.

**Direct merge to main, no PR.** GitHub PAT lacks PR-creation scope; merge sequence:

```bash
git checkout main && git pull --rebase origin main
git merge --no-ff origin/<branch> -m "Merge <branch> (Chat N): <title> (deploy <id>)"
git push origin main
git push origin --delete <branch>
```

**Push-reject fallback:** `git pull --rebase && git push` once. Still rejected → halt, report.

**No force-push.** History is append-only. Reverts via `git revert <sha>`.

**Authority:** GitHub `main` = canonical. `/mnt/project/` is read-only and used only for `CREDENTIALS.md`.

**No PR workflow.** The "operator opens PR" pattern is obsolete (replaced Chat 84a).

---

## 10. Handoff discipline

State lives only in origin. In-chat edits to `/home/claude/` and `/mnt/project/` evaporate on container reset. Every shipping chat ends with commit + push to `origin/main`.

**Forward-looking handoff lives in `WIP_OPEN.md`.** Two blocks:

- **`## Next chat`** — task spec for the immediately-next chat. ~10–25 lines. Format below.
- **`## Sprint queue`** — N+2 and beyond. One-paragraph pointers. Multi-chat sprint detail lives in `docs/sprint-plan.md` (created on demand, deleted at sprint end).

**`## Next chat` template** (everything else is in scripts):

```markdown
## Next chat

**Chat N — TITLE.** One-line classification.

### Task
1. <step>
2. <step>

### Acceptance
- <bullet>

### Branch
refinement-chatN-<slug>

### Pre-flight
<prior chat outcome, anomalies, what's already on the branch if anything>
```

Procedural bash for session-open and close-out is NOT pasted into WIP_OPEN.md. The scripts handle it.

**Mid-chat handoff doc** (`docs/_<slug>_handoff.md`) — only when a chat genuinely cannot finish in budget. Branch is the truth; the doc is read by the next Claude. Written in second person. Never embed operator-conditional triggers ("say go and I'll..."). Deleted on the branch before close-out merges to main.

**Branch-ahead rule.** At session open, if the remote branch named in `## Next chat` has commits beyond `main`, treat them as authoritative prior work. `session-open.sh` enforces this.

**Stale-handoff heuristic.** Handoff docs from recon-only sessions describe "step 1: create branch" as next action. If the branch already exists with commits, the doc is stale. First commit of the resume session updates it; subsequent commits continue from the first un-shipped step.

---

## 11. Context discipline

**Never pull a full source file.** Use grep + sed windowing. Full-file view is permitted only for files under 200 lines.

**Never re-read a file you just wrote.** Tool results are deterministic.

**Never read a file that exists in both sidebar and repo.** Repo wins.

**One WIP pull per session, one WIP write per session.**

**Trust handoff recon.** When resuming from a handoff doc, treat its recon section as authoritative — line numbers, file structures, function locations. Do not re-verify.

**Banned patterns** (token-waste prohibitions):
- `cat` / `head` / `view` of data files — ever
- Re-viewing a file immediately after `str_replace`
- Duplicate `web_search` with rephrased terms in same chat
- `ls /mnt/project/` twice in one chat
- `tippecanoe --version` after first install confirmation this chat
- Re-fetching files just committed

---

## 12. Tool-call budgets

| Chat type | Target | With GitHub sync |
|---|---:|---:|
| Build (no new layer) | 4 | 6 |
| New-layer addition | 6 | 8 |
| Refresh (single source) | 4–10 | 6–12 |
| Doc-only commit | 2 | 2–6 |

**Budget exceeded = investigate drift.** Almost always one of: full-file pull where grep+sed would have worked; sidebar/repo duplicate read; avoidable re-confirmation.

**Defensive scripting: one bash per phase.** Complete, defensively-coded scripts that handle failures and move on. No inline retry/debug loops.

---

## 13. Acceptance criteria

**Build done:**
- `dist/index.html`, `dist/tiles/<id>.pmtiles`, `dist/_headers`, `dist/_redirects`, `dist/pmtiles.js` all exist.
- Every `layers.yaml` entry either has a tile file OR is logged MISSING/ERROR.
- Final line: `built=<n>  missing=<n>  errored=<n>  tiles_total=<kb>`.

**Deploy done:** Netlify MCP returns `{"state":"ready", ..., "siteUrl":...}`; `curl -A "Mozilla/5.0"` returns 200 on root + one tile endpoint; layer-id grep matches expected count.

**Refresh done:** Each named layer has a file in `outputs/refresh/` OR is logged `FETCH_FAILED`.

**Chat done:** `WIP_OPEN.md §Next chat` rewritten with next chat's task; close-out script ran clean; feature branch deleted from origin; if a deploy occurred, merge commit on `main` references the deploy-id.

---

## 14. Rule additions

When a failure recurs, ask first: *can this be a check or a script?* Prefer structural fixes over new prose rules.

- "Push-on-commit" → pre-push hook in `session-open.sh`
- "Never `git add -A`" → `.gitignore` for `*.xlsx`, `outputs/refresh/*.bin`, plus pre-commit reject on files >1MB unless flagged
- "Recon-only is failure" → `close-out.sh` errors if HEAD has zero non-handoff commits
- "Deploy + merge atomic" → `scripts/ship.sh` makes them one indivisible call
- "Session-open state reconciliation" → already in `session-open.sh`

A new prose rule is the last resort, not the first response.

---

## 15. Telemetry

`scripts/audit.sh` runs weekly. Reports:
- OPERATING.md line count (target ≤250)
- chats where `session-open.sh` was used (target 100%)
- chats where `close-out.sh` was used (target 100%)
- stranded branches on origin (target 0)
- WIP_OPEN.md size (target ≤8KB)

Drift in any metric is the prompt for a structural fix — not a new rule.

---

## 16. Settled decisions

Operator-authorized decisions that downstream chats should not re-litigate. Listed in reverse chronological order; entries do not expire — once settled, settled.

**2026-04-26 (Chat 106a):**

- **Cloud-build + deploy workflow shipped.** `.github/workflows/build-and-deploy.yml` runs `python build.py` in a Linux GitHub Actions runner (with apt-installed tippecanoe) and deploys the resulting `dist/` to Netlify prod via netlify-cli. Manual trigger only (`workflow_dispatch`); no auto-deploy on push. Provides a third independent build path: chat container, local desktop (with WSL2 or tippecanoe), or this cloud workflow. Requires repo Secrets: `ANTHROPIC_API_KEY` (already set), `NETLIFY_AUTH_TOKEN` (operator must add), `NETLIFY_SITE_ID` (operator must add, value = `01b53b80-687e-4641-b088-115b7d5ef638`).
- **`build.py DIST` made env-configurable.** `DIST = Path(os.environ.get('LRP_DIST_DIR', '/mnt/user-data/outputs/dist'))`. Backward-compatible default keeps chat-container behavior identical; cloud workflow sets `LRP_DIST_DIR=$GITHUB_WORKSPACE/dist`. Local desktop builds (post-WSL2 setup or future Mac) can also override.
- **Comptroller LDAD scrape: queued for next week.** Operator authorized; sequenced as 1–2 chats post-migration (Chat 107+). Implementation: Playwright headless against `comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`, paginate result pages, write to `outputs/refresh/comptroller_ldad_<date>.csv`, merge into `tax_abatements` layer. Provides statewide abatement coverage to complement existing 9 county-scraped records.

**2026-04-26 (Chat 104b):**

- **GitHub PAT scope upgraded to include `Workflows: Read and write`.** Required for shipping any file under `.github/workflows/`. Token name `claude-lrp-gis`, expires 2027-04-21. Authorized by operator after Chat 104 push-rejection on workflow file.
- **Repo setting "Allow GitHub Actions to create and approve pull requests" enabled** at `Settings → Actions → General → Workflow permissions`. Required for the `peter-evans/create-pull-request@v6` step in `dc-anchors-refresh.yml` and any future PR-opening cron. Authorized by operator after Chat 104 first workflow_dispatch run failed at PR creation step.
- **PacketStream residential proxy egress authorized** for the abatement-scrape sequence (`reevescounty.org` Akamai bot-block + ~14 other CivicEngage CMS counties). Pay-as-you-go, ~$5–20/month at projected volume. Operator to set up account and provide endpoint URL + credentials before Permian abatement chats resume.
- **Selenium / Playwright JS-rendered scrape authorized** for the Comptroller LDAD source (`comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`). Implementation deferred until after Permian abatement core ships. Authorization class extended to other state-government search interfaces requiring JS rendering, evaluated case-by-case.

**Permanently settled (pre-Chat 104):** see ARCHITECTURE.md §11 for the catalogue of permanently-excluded layers and data sources.
