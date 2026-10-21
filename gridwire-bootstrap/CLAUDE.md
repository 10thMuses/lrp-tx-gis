# CLAUDE.md

Bootstrap doc for Claude Code sessions on lrp-grid-wire. Auto-loaded.

Grid Wire: intra-day capital markets and infrastructure briefing. Operator:
Andrea Himmel, Land Resource Partners. Production triggers: `cut <time>.` and
`vol.` (new day).

## Required reading at session start

1. `Readme.md` — operating rules and triggers
2. `OPERATING.md` — cut cycle, pipeline reference, fragility table
3. `STYLE.md` — locked editorial spec (never edit without operator instruction)
4. `WIP_OPEN.md` — current vol, last cut, falsification register (the ONLY
   source for vol/cut state)

## Hard constraints

- Never `git add -A`. Explicit paths.
- Emails are draft-only. Never send.
- Hard-fail on assert_ascii trip or non-Jost fonts in the rendered PDF (both
  checks built into the scripts; do not bypass).
- Cuts are incremental: never restate prior-cut content except
  falsification-status updates and the tape.
- `main` is canonical. Branch `cut-<vol>-<time>` for production work.
