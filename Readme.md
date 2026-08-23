# lrp-tx-gis — operating rules

Canonical entry point. `main` is canonical. Precedence: **repo > sidebar > memory.**

## Document map

| Reference name | Canonical file | Contents |
|---|---|---|
| Operating rules | `OPERATING.md` | Execution rules, hard rules, session protocol, build/deploy/close-out, verification by blast radius, tool-call budgets |
| Environment / bootstrap | `CLAUDE.md` | Operator profile, voice, runtime model, first-time setup, common workflows |
| Engineering patterns | `docs/principles.md` | Pointer -> `OPERATING.md` §6 and `ARCHITECTURE.md` |
| Settled decisions | `docs/settled.md` | Pointer -> `ARCHITECTURE.md` settled-decisions section |
| Architecture | `ARCHITECTURE.md` | Stack, schemas, layer catalog, palette, fragility table |
| Active state | `WIP_OPEN.md` | Queue, active sprints, backlog, last deploy id |
| Closed work | `WIP_LOG.md` | Pointer -> `git log --merges` |
| Refinement stage specs | `docs/refinement-sequence.md` | Pointer -> `docs/sprint-plan.md` |

## Grid Wire

| Item | File |
|---|---|
| Master instructions | `docs/grid-wire-master-instructions-v4.md` |
| Coverage taxonomy (23 domains) | `docs/grid-wire-coverage-taxonomy.md` |
| Volume log + `## Next chat` | `outputs/reports/GRIDWIRE_LOG.md` |
| Edition source + build scripts | `outputs/reports/source/` |
| Scheduled-task run prompt | `docs/grid-wire-scheduled-task-prompt.md` |

Grid Wire volume number and cut slot are read from `GRIDWIRE_LOG.md` `## Next chat` at session open. Never from memory.

## Session open

```
git clone https://github.com/10thMuses/lrp-tx-gis.git && cd lrp-tx-gis
```
Read `Readme.md`, then `OPERATING.md`, then `WIP_OPEN.md` (map work) or `outputs/reports/GRIDWIRE_LOG.md` (Grid Wire work).

Resume trigger: `resume.`
