# Cross-walk — Audit-1 doc consolidation

Maps every section/rule from current four governance docs to its destination in the new two-doc structure. Used to verify nothing is silently dropped before deletion.

**Legend:**
- → OPERATING.md §N  — moved to operating doc, given section
- → ARCHITECTURE.md §N — moved to architecture doc, given section
- → SCRIPT — encoded as a script check, prose rule deleted
- → ARCHIVE — moved to git history only (deleted from working tree)
- → DROP — explicit deletion (obsolete, contradictory, or never applied)

---

## Readme.md (286 lines, 18 commits)

| Current section | Disposition |
|---|---|
| §1 Source of Truth | → OPERATING.md §1 |
| §2 Andrea's time / acceptable asks / banned phrases | → OPERATING.md §2 |
| §3 Persistent structural facts | → OPERATING.md §1 (collapsed; the rule is "lock = file committed", which is implicit in the source-of-truth statement) |
| §4 Default behavior | → OPERATING.md §3 |
| §5 Classify the prompt first | → OPERATING.md §3 |
| §6 Batch execution protocol | → OPERATING.md §4 |
| §7.1 Directed prompt | → OPERATING.md §3, §4 |
| §7.2 Morning briefing | → OPERATING.md §3 |
| §7.3 Update WIP_OPEN as final action | → OPERATING.md §5, §10 |
| §7.4 Doc/meta sessions | → OPERATING.md §9 (Git Data API path) |
| §7.5 No chat labeling in responses | → OPERATING.md §10 (chat number derives from branch name only) |
| §7.6 One shipping chat at a time | → OPERATING.md §6 (implicit in stage-fits-one-chat) |
| §7.7 Progress over summary / continuous commit / minimum chat message | → OPERATING.md §10 (handoff-doc-is-authoritative) + §6 (commit-every-unit hard rule) |
| §7.8 Always ship before handoff | → OPERATING.md §10 |
| §7.9 Push-on-commit | → OPERATING.md §6 (hard rule 9) + SCRIPT (close-out.sh enforces) |
| §7.10 Stage sizing | → OPERATING.md §6 (hard rule 13) |
| §7.11 Recon-only sessions are failures | → OPERATING.md §6 (hard rule 14) + SCRIPT (close-out.sh blocks) |
| §7.12 Session-open state reconciliation | → SCRIPT (already in session-open.sh — DROP from prose) |
| §8 Working style | → OPERATING.md §2 (banned phrases section absorbs) |
| §9.1 Never pull full source file | → OPERATING.md §11 |
| §9.2 Never re-read after write | → OPERATING.md §11 |
| §9.3 Never read sidebar+repo dup | → OPERATING.md §11 |
| §9.4 Verification proportional to blast radius | → OPERATING.md §6 (verification block) |
| §9.5 One WIP pull/write per session | → OPERATING.md §11 |
| §9.6 Git Data API for doc-only | → OPERATING.md §9 |
| §9.7 Trust handoff recon | → OPERATING.md §11 |
| §10 Handoff discipline (full section) | → OPERATING.md §10 (preserved, trimmed) |
| §10 Branch-ahead rule | → SCRIPT (session-open.sh) + brief mention in OPERATING.md §10 |
| §10 Close-out discipline (4 actions) | → SCRIPT (close-out.sh) + brief mention in OPERATING.md §5 |
| §10 Never `git add -A` | → OPERATING.md §6 (hard rule 10) + SCRIPT (.gitignore + pre-commit) |
| §10 Direct merge to main | → OPERATING.md §9 |
| §10 Deploy-without-merge forbidden | → OPERATING.md §6 (hard rule 12) + SCRIPT (ship.sh atomicity) |
| §10 No history logs / no recap | → OPERATING.md §2 (banned phrases) |
| §10 Sprint-plan doc | → OPERATING.md §10 (mentioned in passing) |
| §11 Tool-call budgets | → OPERATING.md §12 |
| §12 Expected budget | → DROP (kilobyte estimates were aspirational, not a check; replaced by §15 telemetry) |
| §13 Engineering patterns | → DROP (was just pointer to other docs; obsolete with consolidation) |

---

## GIS_SPEC.md (324 lines, 2 commits)

| Current section | Disposition |
|---|---|
| §0 Trigger phrases | → OPERATING.md §7 |
| §1 Hard rules 1–12 | → OPERATING.md §6 (deduplicated; pre-flight `ls /mnt/project/` rule DROPPED — repo is canonical, /mnt/project/ is read-only and only CREDENTIALS.md is read) |
| §2 Project file layout | → ARCHITECTURE.md §2 |
| §3 Architecture (runtime + pipeline + schemas) | → ARCHITECTURE.md §1, §3, §4 |
| §4 Build cycle | → OPERATING.md §8 |
| §5 Refresh + merge cycle | → OPERATING.md §8 |
| §6 Layer catalog | → ARCHITECTURE.md §5 |
| §7 Frontend features | → ARCHITECTURE.md §7 |
| §8 Deployment | → ARCHITECTURE.md §8 |
| §9 Known fragility | → ARCHITECTURE.md §9 |
| §10 Acceptance criteria | → OPERATING.md §13 |
| §11 Critical guardrails — chat label | → DROP (contradicts Readme §7.5; chat number lives in branch name only) |
| §11 Critical guardrails — banned patterns | → OPERATING.md §11 |
| §11 Critical guardrails — read GIS_SPEC on every chat | → DROP (consolidation eliminates the multi-doc read; OPERATING.md is the single read) |
| §12–18 (already consolidated, tombstone heading lingers) | → DROP |
| Appendix A fetch utilities | → ARCHITECTURE.md §12 + scripts/ (canonicalize as importable, not pasted) |
| Appendix B adding a layer | → ARCHITECTURE.md §6 |
| Appendix C color palette | → ARCHITECTURE.md §10 |

---

## docs/principles.md (129 lines, 5 commits)

| Current section | Disposition |
|---|---|
| §1 Context discipline | → OPERATING.md §11 (deduplicated with Readme §9) |
| §2 Tool-call budgets | → OPERATING.md §12 (deduplicated with Readme §11) |
| §3 Build discipline | → OPERATING.md §8 + §13 |
| §4 Data pipeline rules | → ARCHITECTURE.md §3 + §4. "Cap-aware tier ladder" → ARCHITECTURE.md §4 footnote. "Single-feature point layers need explicit zoom args" → ARCHITECTURE.md §6. |
| §5 GitHub sync rules | → OPERATING.md §9 |
| §5 Canonical session-open script | → OPERATING.md §5 + SCRIPT (already exists) |
| §6 Credential hygiene | → OPERATING.md §9 (one-line); detailed PAT scope in CREDENTIALS.md |
| §7 Multi-chat refinement patterns | → DROP (refinement-sequence.md is historical; direct-merge-to-main is the current rule per OPERATING.md §9; the branch+PR pattern is no longer used) |
| Deferred / future cleanup | → DROP (was a placeholder, currently empty) |

---

## docs/settled.md (89 lines, 4 commits)

| Current section | Disposition |
|---|---|
| Architecture & build — Option B prebuilt PMTiles | → ARCHITECTURE.md §5 (prebuilt paragraph) |
| Architecture & build — Flat data layout | → ARCHITECTURE.md §2 |
| Architecture & build — Single layers.yaml | → ARCHITECTURE.md §6 + OPERATING.md §6 (hard rule 7) |
| Architecture & build — Full rebuild every chat | → OPERATING.md §6 (hard rule 6) |
| Architecture & build — Data files never in context | → OPERATING.md §6 (hard rule 1) |
| Deploy — PMTiles via proxy bash | → ARCHITECTURE.md §8 + OPERATING.md §8 |
| Deploy — Never deploy on errored>0 | → OPERATING.md §6 (hard rule 8) |
| GitHub sync — Clone-push bracket | → OPERATING.md §9 |
| GitHub sync — Git Data API for doc-only | → OPERATING.md §9 |
| GitHub sync — Main branch direct commit | → OPERATING.md §9 |
| GitHub sync — PAT in gitignored CREDENTIALS.md | → OPERATING.md §9 + CREDENTIALS.md |
| GitHub sync — No Git LFS | → ARCHITECTURE.md §2 (footnote) |
| Scoped-out data sources | → ARCHITECTURE.md §11 |
| Newsletter (Grid Wire) | → DROP from this repo's docs entirely. Grid Wire is a separate workstream; lives in userMemories or its own doc. |
| Operating cadence — One chat = one operation | → OPERATING.md §6 (hard rule 13) |
| Operating cadence — Trigger phrases optional | → OPERATING.md §7 |
| Data sources — EIA-860 capacity in Generator sheet | → ARCHITECTURE.md §4 (capacity paragraph) |
| Data sources — EIA-860 zip Referer header | → ARCHITECTURE.md §9 (fragility table row) |
| Data sources — EIA-860M HTML-only | → ARCHITECTURE.md §9 (fragility table row) |
| Data sources — combined_points.csv capacity fragmentation | → ARCHITECTURE.md §4 + WIP_OPEN.md backlog |
| Data sources — User-uploaded CSV equivalence audit | → DROP (one-time audit, no longer relevant) |
| Data sources — Comptroller / commissioners-court | → ARCHITECTURE.md §11 (scoped-out + leading-signal note) |
| Data sources — Ch. 313 expired / JETI excludes renewables | → ARCHITECTURE.md §11 footnote |
| Data sources — TCEQ sources closed | → ARCHITECTURE.md §11 |
| Data sources — Netlify UA 503 | → ARCHITECTURE.md §9 |

---

## docs/refinement-sequence.md (343 lines)

**Disposition: ARCHIVE.** This doc described a linear FILTER UI → BUG SWEEP → VISUAL OVERHAUL → SIZING+WATERMARK sequence that completed Chats 63–72. The branch+PR workflow it specifies is now obsolete (replaced Chat 84a by direct-merge-to-main). The "Stage specs" inside have been superseded by entries in `WIP_OPEN.md §Sprint queue`.

Move the file to `docs/archive/refinement-sequence-2026-04.md`. Keep only as historical reference.

The "DC RESEARCH → DC BUILD → DC AUTO-REFRESH" sub-sequence stays alive as a sprint-queue entry in `WIP_OPEN.md`.

---

## docs/refinement-abatement-spec.md (219 lines)

**Disposition: ARCHIVE.** This was a discovery-stage spec for the abatement layer. The layer shipped Chat 83. The spec's content survives in:
- abatement column overload → ARCHITECTURE.md §4
- 9 features live + annotation rules → ARCHITECTURE.md §7
- commissioners-court agenda as canonical leading signal → ARCHITECTURE.md §11
- Ch. 313 / JETI regulatory facts → ARCHITECTURE.md §11

Move file to `docs/archive/refinement-abatement-spec-2026-04.md`.

---

## WIP_LOG.md (757 lines, 91KB, frozen Chat 83a)

**Disposition: ARCHIVE.** Frozen but still in repo root. Move to `docs/archive/wip_log_pre_chat83.md` or remove from working tree entirely (git history retains).

This single change drops ~91KB from every clone and removes a file Claude must scan-past on `ls`.

---

## COMMANDS.md (in `/mnt/project/` only, ~280 lines)

**Disposition: KEEP as `docs/triggers.md` (committed to repo).** Designation changes from "operator command reference" (current) to "documentation of Claude's autonomous behavior" (new). Operator types whatever they want; Claude routes. The doc is reference, not authority.

Delete the sidebar copy. Single source of truth.

---

## ENVIRONMENT.md (in `/mnt/project/` only)

**Disposition: DROP.** Was deleted from repo Chat 70 per principles.md. Sidebar copy is stale and contradicts current authority (Readme §1: repo > sidebar). Remove from sidebar.

---

## CREDENTIALS.md

**Disposition: KEEP unchanged.** Already in `/mnt/project/`, gitignored from repo. The two new docs reference it for PAT lookup; structure stays as is.

---

## WIP_OPEN.md (284 lines, 24KB)

**Disposition: SHRINK in place.** Same file, dramatically reduced template per OPERATING.md §10:

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

Procedural bash blocks DELETED from `## Next chat`. The session-open and close-out scripts handle that.

`## Sprint queue`, `## Prod status`, `## Open backlog` sections preserved but trimmed:
- `## Prod status` → 3 lines max (current deploy ID, layer count, last verified UA-200). Per-chat narrative goes to git commit messages, not the WIP file.
- Per-chat narrative entries in `## Prod status` → DROP (already in commit messages and WIP_LOG)
- `## Open backlog` → keep, but enforce the "10-chat-stale = decide or drop" rule

Estimated reduction: 24KB → ~6KB. Per-chat read overhead −18KB.

---

## Net summary

| Outcome | Bytes saved per chat |
|---|---:|
| Readme.md (23.5KB) + GIS_SPEC.md (15KB) + principles.md (9.5KB) + settled.md (10KB) → OPERATING.md (~10KB) + ARCHITECTURE.md (~9KB) | ~39KB |
| WIP_LOG.md cloned per chat (91KB) → archived | ~91KB on clone, 0 on read (was 0 on read but slowed clones) |
| WIP_OPEN.md shrink (24KB → 6KB) | ~18KB |
| ENVIRONMENT.md sidebar dup → deleted | ~5KB |
| COMMANDS.md sidebar dup → reference doc only | ~8KB |
| **Total per-chat governance read** | **~70KB → ~18KB** |

Rule count: ~50 numbered items across 4 docs → ~30 in OPERATING.md.

---

## What is NOT being changed in Audit-1

This pass touches only governance docs. Untouched:
- `build.py`, `build_sprite.py`, `build_template.html`, `layers.yaml`
- `combined_points.csv`, `combined_geoms.geojson`, all data files
- `scripts/refresh_*.py`, `scripts/scrape_abatements.py`, `scripts/transform_abatements.py`
- Netlify deploy mechanism, GitHub PAT, branch model
- Live site at `https://lrp-tx-gis.netlify.app`

Audit-2 (next chat) handles: write `close-out.sh`, `deploy.sh`, `ship.sh`, `audit.sh`; resolve stranded branches; sidebar prompt cleanup. Audit-2 also touches no production code.
