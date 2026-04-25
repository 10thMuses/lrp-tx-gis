# ENVIRONMENT — pointer doc

Sidebar copy. Canonical content lives in the repo.

**Repo > sidebar > memory.** When this file disagrees with the repo, the repo wins.

---

## Runtime model — the one-line summary

`/mnt/project/` is read-only and used only for `CREDENTIALS.md`. State lives in `origin/main`. Working dir during a chat is `/home/claude/repo/`. In-chat edits to `/home/claude/` and `/mnt/project/` evaporate on container reset; every shipping chat ends with commit + push to `origin/main`.

See `OPERATING.md §1` (source of truth) and `§10` (handoff discipline).

## Where the rules live

- **Source of truth** (repo > sidebar > memory; clone-edit-push bracket) → `OPERATING.md §1` and `§9`
- **Acceptable asks / banned asks** (when an environment limit forces operator action) → `OPERATING.md §2`
- **Verification proportional to blast radius** → `OPERATING.md §6`
- **Build / refresh / merge cycles + Netlify MCP deploy chain** → `OPERATING.md §8`
- **Telemetry and drift signals** (`scripts/audit.sh`) → `OPERATING.md §15`

## Credentials

`CREDENTIALS.md` lives only in `/mnt/project/` (sidebar). Gitignored. Active credentials and the ask pattern for new ones are in that file's header.

## Repo

`github.com/10thMuses/lrp-tx-gis` — branch `main` is canonical. Netlify siteId `01b53b80-687e-4641-b088-115b7d5ef638`. Prod URL `https://lrp-tx-gis.netlify.app`.
