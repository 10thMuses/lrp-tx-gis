# Land Resource Partners — Texas Energy GIS Map

**Owner:** Andrea Himmel
**Prod URL:** https://lrp-tx-gis.netlify.app
**Repo:** https://github.com/10thMuses/lrp-tx-gis
**Netlify siteId:** `01b53b80-687e-4641-b088-115b7d5ef638`

---

## 1. Source of Truth

**Repo > sidebar system prompt > memory.**

If the three disagree, the repo wins. The sidebar can lag, memory churns. The repo is canonical.

Live reads via GitHub Contents API with `Accept: application/vnd.github.raw` for first reads in a chat. `raw.githubusercontent.com` only for files known-stable for hours. Sidebar is intentionally minimal; if a filename appears in both sidebar and repo, repo wins.

Working directory in-chat: `/home/claude/repo/`. All references to `/mnt/project/<file>` in any doc resolve there during a live chat.

---

## 2. Andrea's Time is the Scarce Resource

Claude is the executor. Andrea is the operator. Every request Claude makes of Andrea — to paste something, run a command, check a dashboard, confirm a choice, structure a prompt, decide between two near-equivalent options — is pure overhead Claude should have absorbed.

**Do not ask Andrea to do manual work Claude can automate.** Specific bans:

- Pasting file contents Claude can fetch
- Running curl / SQL / CLI Claude can execute
- Copying text between places Claude has access to both
- Checking values in dashboards Claude has API access to
- Re-typing state Claude can read from `WIP_OPEN.md`
- Structuring prompts a particular way so Claude can parse them
- Confirming actions inside delegated autonomy

**Limit requests of Andrea per chat.** Target: zero asks per chat. Hard ceiling: one ask per chat, only if the ask blocks shipping. Batch unavoidable asks into a single numbered list at start of response, never sprinkled across turns.

**Acceptable asks (narrow list):**

1. Irreversible destructive action (force-push over history, delete a deployed PMTiles file, drop a data file from repo)
2. Spend or external commitment (new paid data subscription, new Netlify tier, new vendor)
3. Materially-different strategic fork (e.g., "switch from MapLibre to Mapbox" vs "use blue or green for this layer" — the second is a style call Claude makes)
4. Missing credential Claude genuinely cannot obtain
5. Factual input only Andrea has (a county name to target, a thesis decision, a layer's intended audience)

**Default to action, not confirmation.** Banned phrases: "Should I proceed?" / "Do you want me to?" / "Want me to go ahead and?" / "Would you prefer A or B?". If action is inside delegated autonomy, Claude has already done it by the time it tells Andrea. If not, Claude references the acceptable-asks list before interrupting.

---

## 3. Persistent Structural Facts

Facts that survive across chats and don't belong in rolling WIP state live in the repo, not conversation history.

- Locked taxonomies / config lists → committed at the moment of locking, not in a handoff doc
- Schema conventions, build patterns, engineering rules → `docs/principles.md`
- Completed multi-chat decisions → `docs/settled.md`

Rule: if a chat "locks" a list and the next chat has to search conversation history to reconstruct it, the list was never actually locked. **Lock = file committed.** Handoffs reference file paths, not content.

---

## 4. Default Behavior

Operator is not expected to provide state, task scope, or blast radius in the prompt. Claude infers all three from prompt text + `WIP_OPEN.md`. Prompt may be one sentence, fragment, trigger phrase, or attached handoff. Do not ask operator to fill in a template.

---

## 5. Classify the Prompt First

Silently, before any tool calls. Three-way split:

- **Conversational / planning / briefing / question** — casual tone, no imperative verb, or explicit words like "morning briefing", "what do you think", "how should we", "explain", "review", "plan". Answer directly. Read `WIP_OPEN.md` only if operator asked for status or the answer genuinely depends on active state. No clone.
- **Shipping task** — imperative verb (`build`, `refresh`, `add layer`, `deploy`, `rebuild`), OR a handoff doc attached, OR the prompt names files / layers / data sources. Enter Batch Execution Protocol.
- **Ambiguous** — default conversational. One clarifying sentence cheaper than a wasted clone.

---

## 6. Batch Execution Protocol (shipping chats only)

Silently resolve these parameters from prompt + any attached handoff + one `WIP_OPEN.md` fetch. Never ask operator to provide them.

- **State** — prior chat outcome, active workstream
- **Task** — concrete scope in 2–3 sentences; if handoff attached, extract task statement only, treat rest as reference
- **Blast radius** — low / medium / high (see §9 rule 4)
- **Approach** — recon via grep + sed windowing → stage files in `/home/claude/` → commit per clone-push bracket OR Git Data API tree commit for doc-only changes → verify per blast-radius tier → one `WIP_OPEN.md` write as final action

Execute end-to-end without mid-session confirmation.

---

## 7. Session Protocol

1. Directed prompt with state + task → execute, no WIP pull.
2. Undirected or "morning briefing" → read `WIP_OPEN.md` once.
3. Shipping session → update `WIP_OPEN.md` as final action; append entry to `WIP_LOG.md`.
4. Doc / meta session → prepend to `WIP_LOG.md`, no chat number required.
5. No chat labeling in responses (no "Chat N:" prefix in chat replies; logs still carry chat numbers).
6. One shipping chat at a time.
7. **Progress over summary. Commit continuously, not at the end.**

   Shipping chats commit and push every completed unit of work the moment it's done — each fix, each file patched, each logical milestone. Not batched for a final push. Not saved up for a summary message.

   **Budget rule.** Reserve ~20% of tool budget for the close-out commit-push-handoff sequence. When ~75% of budget is consumed, stop starting new sub-tasks. Ship what's complete, commit in-flight state to `docs/_<stage-slug>_handoff.md` on the active branch, push, then send the final chat message.

   **Handoff doc is authoritative, not the chat message.** The doc on the branch carries state at handoff, scope boundary, recon findings (so next chat does not redo), first commands for next chat, execution order, file paths. Next chat reads the file on clone and resumes without conversation_search, prompt parsing, or memory.

   **Final chat message is minimum viable.** One line of what shipped with commit hash, one line with the next-chat trigger. No tables. No bullet recaps. No "what's done / what's outstanding" summaries. The branch is the truth; the message is a pointer.

   **Handoff doc is deleted** on the branch before the PR opens.

   Violations of this rule waste operator time and force re-work in subsequent chats. Leaving mid-chat state in chat messages violates §1 (repo > sidebar > memory).

8. **Always ship before handoff. Handoffs are for context exhaustion only.**

   A shipping chat finishes its stage in-chat: validate build, delete in-flight handoff doc, merge to `main`, update `WIP_OPEN.md` + append `WIP_LOG.md`. "Almost done" = ship. Do not propose a handoff in the final message when the remaining work fits in budget.

   A handoff doc is written only when §7.7 triggers (tool-call or context limits hit before completion). In that case the doc is the authority, not the chat message — per §7.7.

   **Handoff-doc voice.** The doc is read by the next Claude, not by the operator. Write instructions in the second person addressed to that Claude: "Run `python3 build.py`", not "Ask the user to run build". Never embed triggers addressed to the operator ("say 'go' and I'll...", "confirm and I'll..."). The next chat parses such phrases as instructions to itself and stalls. Execution is unconditional on arrival; conditionality belongs in a branching step ("if build fails, halt; else continue"), not in a wait-for-user gate.

9. **Push-on-commit. Never leave unpushed commits in the container.**

   Every `git commit` is followed by `git push` in the same bash call or the next one. Unpushed commits die on container reset — same outcome as if the work was never done. Batching pushes for the end of a chat is a §7.7 violation dressed up as efficiency.

   **Operational trigger.** The commit-push pair is a single atomic unit. Do not begin the next edit, tool call, or sub-task until the push has returned success. If push fails (non-fast-forward, auth, network), resolve before continuing — do not queue more commits on top.

   **Applies to all branches.** Feature branches, `main`, handoff doc commits — all pushed on creation. The only acceptable unpushed state is the few seconds between `git commit` and the immediately following `git push`.

10. **Stage sizing. A stage fits one chat.**

    A shipping chat ships one stage end-to-end: execute, build verify, PR open (or merge for direct-to-main work), `WIP_OPEN.md` + `WIP_LOG.md` updates. Typical max: ~4 commits plus one build plus one PR.

    If execution reveals the stage won't fit, **the handoff doc is the re-scoping signal, not a routine resume mechanism.** When a stage needs a second chat to finish, that's a scope miss — the remaining work is carved out as its own sub-stage (new entry in `docs/refinement-sequence.md` or equivalent) rather than continuing under the same stage name across N chats. A stage resumed via handoff once is acceptable; a stage resumed twice means the original scope was two stages pretending to be one.

    **Scoping check before starting.** Count commits the stage will produce. Count file rewrites. Count verification gates. Five+ commits or three+ distinct subsystems = split before starting, not after.

---

## 8. Working Style

Operator delegates autonomously. Execute end-to-end. Direct, factual, concise. Don't repeat back what prompt said. Don't ask operator to structure prompts a particular way — Claude adapts. No filler closers. No recaps.

---

## 9. Context Discipline (HARD)

1. **Never pull a full source file.** Use grep + sed windowing. Full-file view permitted only for files under 200 lines.
2. **Never re-read a file you just wrote.** Tool results are deterministic.
3. **Never read a file that exists in both sidebar and repo.** Repo wins.
4. **Verification proportional to blast radius:**
   - Low (yaml tweak, Readme edit, WIP update) → skip in-chat, defer to next briefing
   - Medium (new layer, new build step, new data source) → bundle hash + 1 curl + 1 tile spot-check
   - High (schema change, credential rotation, destructive migration) → full acceptance protocol per `GIS_SPEC.md`
5. **One WIP pull per session, one WIP write per session.**
6. **Git Data API tree commit** for doc-only edits (no clone). **Clone-edit-push bracket** for anything requiring files on disk (tippecanoe, PMTiles build, multi-file coordinated rewrite).
7. **Trust handoff recon.** When resuming from a handoff doc on a branch, treat its recon section as authoritative. Line numbers, file structures, function locations, state descriptions documented there — do not re-verify. Open files with targeted view-ranges matching the handoff's stated line numbers; do not open the file first to confirm the numbers still hold. The prior chat paid that cost and encoded the result. Re-verification burns budget the handoff was written specifically to save.

---

## 10. Handoff Discipline

Handoff content is written directly into chat at close-out, not as attachment, not as file, not as project sidebar upload. Next chat's first tool call is `conversation_search` against keywords from current prompt. Operator never downloads or re-uploads handoff docs. If a chat "locks" a taxonomy or config, the file ships that same chat, not the next.

---

## 11. Tool-Call Budgets

Preserved from prior GIS convention:

- Build chat: **4** (install+build → MCP deploy → proxy bash → present_files). +2 with GitHub sync (clone + push) = **6 effective**.
- New-layer chat: **6** (+ yaml edit). +2 with GitHub sync = **8**.
- Refresh chat: **4–10** depending on source complexity. +2 with GitHub sync = **6–12**.
- Doc-only commit (Git Data API or clone-edit-push): **2–6** depending on file count.

Budget exceeded = stop, diagnose, reset. Almost always a full-file pull or sidebar/repo duplicate is the cause.

---

## 12. Expected Budget

Typical shipping chat (1 layer add, ~50 lines changed across yaml + build artifacts):

- System / memory / project docs (fixed): ~18 KB
- `WIP_OPEN.md` pull: ~2 KB
- Recon (grep + narrow sed): ~5 KB
- Edits + build: ~10 KB
- Commit + push: ~4 KB
- Verification: ~3 KB
- `WIP_OPEN.md` update: ~2 KB
- **Total target ~44 KB.** Above ~90 KB before build, something is wrong.

---

## 13. Engineering Patterns

See `docs/principles.md` for full engineering patterns: context discipline specifics, tool-call budgets with failure modes, build discipline, data pipeline rules, GitHub sync rules, credential hygiene.

See `docs/settled.md` for decisions that never re-surface: Option B prebuilt PMTiles pattern, flat data layout, single `layers.yaml` config, scoped-out data sources, and more.

See `GIS_SPEC.md` for map architecture, trigger phrases, fragility table, and build acceptance criteria.

See `COMMANDS.md` for operator trigger reference (triggers remain optional input — natural language also works).
