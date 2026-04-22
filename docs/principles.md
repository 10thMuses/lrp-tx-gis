# Engineering Principles

Rules and patterns that outlive any one chat. Not a style guide. These exist because specific failures in prior chats produced them; each principle has a cost attached.

---

## 1. Context Discipline

**Data files never enter Claude's context.** `points_*.csv`, `geoms_*.geojson`, `deal_*.geojson`, `combined_*.{csv,geojson}` flow through `tippecanoe` subprocesses only. `cat`-ing or reading them for inspection burns tokens and produces nothing useful. The biggest single token-burn failure mode. Enforced in `GIS_SPEC.md` Hard Rule #1.

**Grep + sed windowing before full-file view.** Any file >200 lines gets recon via `grep -n` to find line ranges, then `sed -n 'A,Bp'` to view the window. Full-file view is a last resort.

**Never re-read a file you just wrote.** Tool results are deterministic. `create_file` returning success means the file is written; `str_replace` returning success means the edit landed. Re-viewing to confirm is wasted tokens.

**Known-stable-for-hours files may be read via CDN** (`raw.githubusercontent.com`) instead of the Contents API. Stability threshold: file hasn't been touched in the last 2 chats. First read of a chat should always go through the Contents API; subsequent reads of the same file in the same chat hit the local working directory.

**One WIP pull per session, one WIP write per session.** `WIP_OPEN.md` is read at most once per chat (only if the prompt requires state context) and written at most once (as the final action of a shipping chat).

---

## 2. Tool-Call Budgets

| Chat type | Target | With GitHub sync |
|---|---:|---:|
| Build (no new layer) | 4 | 6 |
| New-layer addition | 6 | 8 |
| Refresh (single source) | 4–10 | 6–12 |
| Doc-only commit | 2 | 2–6 |
| Discovery / planning | variable | + 2 if clone needed |

**Budget exceeded = investigate drift before continuing.** Almost always one of: a full-file pull where grep+sed would have worked; a sidebar/repo duplicate read; an avoidable re-confirmation.

**Defensive scripting: one bash per phase.** Write complete, defensively-coded scripts that handle failures and move on. No inline retry/debug loops. If a phase needs 3 attempts, that's 3 tool calls, not 1 with a Python retry wrapper — the wrapper hides the failure from the close-out log.

**One layer/source failure skips, logs, continues.** Never aborts. Try/except at the dispatcher level. Logged to the append-only log for later review.

---

## 3. Build Discipline

**Flat data layout.** All data files at repo root. No subfolders. (`docs/settled.md` covers this in full.)

**Single `layers.yaml` config.** Adding a layer = one yaml append. `build.py` and `build_template.html` are never modified for layer additions. If a layer genuinely needs new toolchain behavior (e.g., planned-upgrade popup styling), that's a separate chat scoped to the toolchain change — not a layer-addition chat.

**One chat = one final build.** No version numbering. Output is always `dist/index.html` + `dist/tiles/*.pmtiles`.

**Build acceptance gates.** Every build chat:
- Pre-build: `layers.yaml` parses; layer count matches expected; all referenced source files present
- Post-build: `dist/tiles/` has one non-zero `.pmtiles` per yaml entry; build report `errored == 0`; dropped features <5% per layer or justified
- Post-deploy: `curl` prod URL returns 200; spot-check one tile endpoint per new/modified layer

Failure at any gate halts the chat. Never advance with a failing gate.

---

## 4. Data Pipeline Rules

**Streaming tippecanoe subprocesses.** `build.py` passes source file paths as subprocess arguments; tippecanoe reads directly from disk. Claude never loads the source content.

**Option B for large GeoJSON.** Sources ≥10 MB use prebuilt PMTiles with `prebuilt: true` in `layers.yaml`. Resolved via 3-tier lookup: `/mnt/project/` → `/mnt/user-data/uploads/` → prod URL. See `docs/settled.md`.

**Cap-aware tier ladder for large-source merges.** When merging refresh outputs into `combined_geoms.geojson`, dry-measure serialized size before commit. If it exceeds project-knowledge cap (~12.7 MB), tier down geometry-simplification until it fits. Chat 43 pattern.

**Single-feature point layers require explicit tippecanoe zoom args.** `-zg` (auto-zoom) silently produces 0-feature PMTiles on single-feature inputs. Use explicit `-Z0 -z14` (or similar) instead.

**Acceptance criteria for production:**
- `errored == 0` in build report
- All layers render at expected zoom ranges
- Popup and filter UI work for every layer
- Initial load <3s on cable connection
- CDN warm-up window ~45–75s post-deploy — curl HEAD may 503 during this window, retry before escalating

---

## 5. GitHub Sync Rules

**Clone-push bracket for shipping sessions.** First bash: `git clone --depth=1` into `/home/claude/repo/`. Last bash (only if changes): `git add -A && git commit -m "Chat N: <title>" && git push`. No-op on empty diff.

**Git Data API tree commit for doc-only edits.** When the change is pure documentation with no tooling dependency, skip the clone. Commit directly via the API.

**Push-reject fallback = pull-rebase once, else halt.** `git pull --rebase && git push` exactly once. Still rejected → stop, report conflict, leave repo in detached state for Andrea.

**No force-push.** History is append-only. If a commit needs reverting, do it with `git revert <sha>`, not `git push --force`.

**Authority: GitHub `main` = canonical.** `/mnt/project/` = read-only fallback only if GitHub unreachable at session open.

**No PR workflow for routine chats.** Direct main-branch commit. PR workflow applies only when explicitly scoped (e.g., a structured refinement sequence).

---

## 6. Credential Hygiene

**PAT in gitignored `/mnt/project/CREDENTIALS.md`.** Never in userMemories. Never in repo history. Fine-grained PAT with `contents: read/write` on the single repo preferred. Classic PAT with `repo` scope acceptable as fallback.

**Secrets never in sidebar system prompt.** The sidebar is trimmed but still visible in logs and context dumps. Secrets go in `CREDENTIALS.md` only.

**Rotation is a high-blast-radius operation.** Triggers full acceptance protocol per §9 rule 4 of `Readme.md` (full stack verification). Not part of any routine chat.

---

## Deferred / future cleanup

- `ENVIRONMENT.md` contains stale language about `/mnt/project/` being the single sync touchpoint; post-GitHub-sync, the clone-push bracket is the actual mechanism. Refresh out of scope for this protocol port; revisit opportunistically.
- `GIS_SPEC.md` §12–§18 session protocol overlaps with `Readme.md` §7. Not resolved in this port (blast radius too high for a scope expansion). Single source of truth is `Readme.md`; `GIS_SPEC.md` sections remain as historical context.
