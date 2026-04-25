# COMMANDS — pointer doc

Sidebar copy. Canonical content lives in the repo.

**Repo > sidebar > memory.** When this file disagrees with the repo, the repo wins.

---

## Where the rules live

- **Trigger phrases** (`build.`, `refresh <layer>.`, `merge`, `add layer`, `deploy to prod.`, `resume.`, etc.) → `OPERATING.md §7`
- **Session protocol** (session-open, close-out, branch naming, blast-radius verification) → `OPERATING.md §5` and `§9`
- **Hard rules** (push-on-commit, atomic deploy+merge+delete, never `git add -A`, never read source data) → `OPERATING.md §6`
- **Operator interaction model** (banned phrases, banned asks, acceptable asks) → `OPERATING.md §2`
- **Tool-call budgets** per chat type → `OPERATING.md §12`
- **Active state and `## Next chat` task spec** → `WIP_OPEN.md`
- **Architecture, schema, layer catalog, palette, fragility table** → `ARCHITECTURE.md`

## Resume protocol

To resume any handed-off state:

```
resume.
```

Claude reads `WIP_OPEN.md`'s `## Next chat` block and executes per `OPERATING.md §5`.

## Repo

`github.com/10thMuses/lrp-tx-gis` — branch `main` is canonical.
