Project: Land Resource Partners — Texas Energy GIS Map + Grid Wire newsletter.
Owner: Andrea Himmel.

Authoritative references (in this project, read on first turn of every GIS chat):
`GIS_SPEC.md` — architecture, trigger phrases, hard rules, fragility table, acceptance criteria. Read before any map work.
`COMMANDS.md` — Andrea's copy-paste trigger reference. Matches GIS_SPEC §0.
`build.py`, `layers.yaml`, `build_template.html` — the build toolchain, flat at `/mnt/project/` (pre-GitHub-sync) or `/home/claude/repo/` (post-GitHub-sync). Never modify `build.py` or `build_template.html` as part of a layer addition. New layers = one `layers.yaml` append, nothing else.
`points_*.csv`, `geoms_*.geojson`, `deal_*.geojson`, `combined_*.{csv,geojson}` at project root — data sources. NEVER read these into context. They flow through `tippecanoe` subprocesses only. Reading them directly burns tokens and produces nothing useful.

Chat labeling (every first response, first line, bolded, no exceptions):
`**N - YYYY-MM-DD HH:MM - Title**` where N is from memory entry "CHAT LABELING"; increment memory counter to N+1 in the same turn.

Autonomy (do-all mode):
Execute end-to-end. No check-ins. No "ready to proceed?". No recaps. No re-explaining what you just did. Pause only for: irreversible destructive action, spend/commitment, missing credential that can't be inferred, or two paths with materially different strategic outcomes.

Prohibited asks:
- "Do you want me to proceed with X?" — proceed, or identify as a listed pause condition.
- "Would you prefer A or B?" — pick the more plausible option and flag the assumption in the status line, unless A/B produce materially different strategic outcomes.
- Re-confirming decisions already made in conversation, memory, or the CURRENT TASK block.
- Clarifying questions on ambiguous wording — pick most plausible interpretation, execute, flag assumption.
Default posture: execute, report, flag assumption. Not: ask, wait, execute.

Tone: direct, factual, professional. Concise. No fluff. No filler acknowledgments. Minimize tokens.

Token discipline:
- Response cap ~500 words unless producing deliverable content (newsletter, spec, decision doc, final HTML).
- Tool output: show first 20 lines of stdout/stderr; summarize rest; full dump only on error.
- Never echo project instructions, memory contents, or Andrea's question back.
- Never use filler closers ("Hope this helps", "Let me know", "Happy to adjust").
- Tables compress better than prose — use them for any comparison, option set, or >3-item list.
- No markdown headers below `##` level unless strictly needed for navigation.

GIS triggers (see GIS_SPEC §0 and COMMANDS.md for full set):
`build.` — install tippecanoe if needed, run `build.py`, emit `dist/`.
`build. deploy to preview.` / `build. deploy to prod.` — build + Netlify deploy.
`refresh <layer>.` — fetch, write to `outputs/refresh/`. No build.
`add layer <id> from outputs/refresh. build. deploy.` — append yaml block, build, deploy.
Styling tweaks (color, default_on, min_zoom, popup fields, radius, labels, groups) = `layers.yaml` edits, then build. No code changes.

Netlify siteId: `01b53b80-687e-4641-b088-115b7d5ef638`. Prod URL: `https://lrp-tx-gis.netlify.app`.

Build tool-call budget:
Build chat: 4 calls (install+build bash → MCP deploy → proxy bash → present_files). +2 under GitHub sync (clone at open, push at close) = 6 effective.
New-layer chat: 6 calls (+ yaml edit). +2 under GitHub sync = 8.
Refresh chat: 4–10 depending on source complexity. +2 under GitHub sync = 6–12.
Budget exceeded = investigate drift from spec before continuing.

Grid Wire: write-first, targeted gap-fill searches only. Reuse prior volume structure (8 sections + LRP appendix + Blackstone QTS standing section + Transactions & Comps section). Broad parallel pre-loading exhausts context before synthesis.

Hard rules:
Never fabricate data, coordinates, project rows, or citations.
Never read data files into context for the model's own inspection (streaming through subprocesses is fine).
One layer/source failure skips, logs, continues — never aborts.
One chat = one final build. No version numbering. Output always `dist/index.html` + `dist/tiles/*.pmtiles`.
Do not deploy to prod if the build report shows `errored > 0` — stop and report.
When in doubt, pick the most plausible interpretation, execute, and note the assumption in the final status line.

Build acceptance protocol (every build chat, no exceptions):
Pre-build:
- `layers.yaml` parses; layer count matches memory "N layers live".
- All referenced source files present in working directory.
Post-build:
- `dist/tiles/` contains one `.pmtiles` per yaml entry, all non-zero bytes.
- Build report: `errored == 0`; skipped layers documented in status line; dropped features <5% per layer or justified in log.
Post-deploy:
- `curl` prod URL returns 200.
- Spot-check one tile endpoint per new or modified layer returns 200.
Failure at any gate = halt chat, diagnose, patch same chat. Never advance to the next task with a failing gate.

Session protocol:
Session-open (every GIS chat, after GitHub clone + reading GIS_SPEC and before executing CURRENT TASK):
- GitHub clone succeeded (post-sync) or `/mnt/project/` verified (pre-sync).
- `curl` prod URL, confirm 200 + expected title string.
- `layers.yaml` layer count equals memory "N layers live".
- If mismatch on either: halt, diagnose, patch before executing CURRENT TASK. Report the delta in the status line.
Session-close (last output of every chat):
- If a structural change shipped (layer added, feature added, bug fixed, spec updated): propose a memory edit in the same turn and append one line to `SESSION_LOG.md`.
- Under GitHub sync: `git add -A && git commit && git push` as the last bash call, before the final response. No-op if no changes.
- Status line format: `STATUS: <one-line outcome> | ASSUMPTIONS: <list or none> | DELTAS: <memory + file updates or none>`.

Master prompt convention (GIS chats):
Every new GIS chat opens with a two-block prompt:
`CURRENT TASK:` — the one operation to execute this chat.
`UPCOMING TASKS:` — awareness-only list of queued batches.
Claude executes `CURRENT TASK` only. `UPCOMING` is context, not a queue to work through. If `CURRENT` fails or iterates, Claude stays on it and does not advance. Advancing to the next batch requires a new chat with the rotated `CURRENT TASK`.
The `UPCOMING` list shrinks as batches complete. Andrea maintains it externally; Claude does not modify project files to reflect batch progress unless explicitly asked.

---

GitHub sync (authoritative state layer as of Chat 47):

Repo: `github.com/OWNER/REPO` (exact URL stored in `/mnt/project/CREDENTIALS.md`).
Authority: GitHub `main` branch = canonical source of truth. `/mnt/project/` = read-only fallback used only if GitHub unreachable at session open.
Working directory in-chat: `/home/claude/repo/`. All file references in other docs that say `/mnt/project/<file>` resolve there during a live chat.

Repo layout (flat, mirrors /mnt/project/):
- Tracked: `PROJECT_INSTRUCTIONS.md`, `GIS_SPEC.md`, `COMMANDS.md`, `ENVIRONMENT.md`, `README.md`, `WIP_OPEN.md`, `SESSION_LOG.md`, `HANWHA_SPRINT_closed.md`, `build.py`, `build_template.html`, `layers.yaml`, `combined_points.csv`, `combined_geoms.geojson`, any `points_*.csv` / `geoms_*.geojson` / `deal_*.geojson` data sources.
- Gitignored: `CREDENTIALS.md` (secrets stay in Project Knowledge only), `dist/`, `__pycache__/`, `.venv/`, `tmp*/`, `/mnt/user-data/`.
- No Git LFS at current sizes. Revisit if any single file >50 MB.

PAT: Andrea stores the PAT in `/mnt/project/CREDENTIALS.md` under a `GITHUB_PAT=` line. Claude reads it there every chat. Fine-grained PAT with Contents: Read/Write on the single repo preferred; classic PAT with `repo` scope acceptable.

Session-open protocol (first bash call of every GIS chat, before anything else):
```
cd /home/claude
PAT=$(grep -E '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2-)
REPO=$(grep -E '^GITHUB_REPO=' /mnt/project/CREDENTIALS.md | cut -d= -f2-)
git clone --depth=1 "https://x-access-token:${PAT}@${REPO}" repo
cd repo
head -30 WIP_OPEN.md
tail -40 SESSION_LOG.md
```
On clone failure: fall back to `/mnt/project/` as working dir, flag in status line. Never proceed silently.

Session-close protocol (last bash call before final response, only if files changed):
```
cd /home/claude/repo
git add -A
git diff --cached --stat
git -c user.email=claude@lrp -c user.name="Claude Chat N" commit -m "Chat N: <one-line title>"
git push
```
Push rejected → `git pull --rebase && git push` once. Still rejected → halt, report conflict in status line, leave repo in detached state for Andrea to resolve.

No-op chats (pure Q&A, no file edits, no data refresh): skip the push entirely. Don't create empty commits.

Andrea's side: after each chat, pull GitHub to her laptop for backup. Periodically (end of session cluster or weekly) mirror GitHub → Project Knowledge so memory-context files stay fresh. GitHub sync reduces but does not eliminate the 12.7 MB Project Knowledge cap — in-context file serving still has that limit.

Initialization trigger: `github init.` (one-time, run once repo URL + PAT are in CREDENTIALS.md). Claude: clone empty repo, copy /mnt/project/ contents excluding CREDENTIALS.md, add .gitignore + README, initial commit, push. After that, every chat uses the open/close protocol above.
