# Sprint plan

Active multi-chat plan. Referenced from `WIP_OPEN.md` §Next chat + §Sprint queue.

Covers Chat 90–91. When the last chat in this file ships, delete the file
and start a new one. Chats beyond 91 (Permian-core abatement, power-plant
refresh, DC sub-sequence, etc.) remain in `WIP_OPEN.md` §Sprint queue as
short pointers until they enter the active 5-chat window.

---

## Maintenance discipline (per `Readme.md` §10)

Each shipping chat's close-out re-reads the downstream chat briefs below.
If the just-completed work changed a downstream chat's assumptions — file
layout, dep versions, layer count baseline, discovered regression, new
backlog item, schema change, deprecated source — edit the affected brief
before committing close-out. A close-out that pushes a stale brief forward
is the same silent-regression class as Chat 85's stale-ref merge.

Promotion rule: `WIP_OPEN.md` §Next chat carries the full brief for the
immediately-next chat inline (paste-ready). `§Sprint queue` carries
one-paragraph summaries with pointers into this doc. On close-out, the
executing chat deletes its own section here, promotes the next chat's
full brief into `§Next chat`, and shortens the new §Sprint queue entry
for the chat it just removed.

---

## Chat 91 — BEAD FIBER PLANNED + REEVES ADAPTER RE-VERIFY

Conditional new layer + deferred adapter fix.

### Tasks

1. **BEAD fiber planned layer (conditional).**
   - Primary: TX Comptroller BDO BEAD map / awards list
     (https://comptroller.texas.gov/programs/broadband/).
   - Fallback 1: NTIA Middle Mile award list, Texas subset.
   - Fallback 2: NTIA National Broadband Funding Map.
   - Fields: `subgrantee`, `award_amount`, `county_list` or
     polygon, `announced_date`, `target_completion`, `technology`,
     speed commitment.
   - Render: polygon if available, else county centroid. Cyan
     family, darker shade or dashed stroke than Chat 90's layer.
   - **Ship rule:** if no downloadable source in 30 min, drop the
     layer entirely, log in §Open backlog, proceed to §2 below.

2. **Reeves CivicEngage adapter re-verify.** Chat 82 regression:
   adapter returned 0 hits on first run; Pecos Power Plant LLC
   Reeves abatement was hand-seeded from spec §8. Re-run adapter,
   confirm it reproduces the hand-seeded row. If still 0 hits,
   diagnose selector / URL pattern. If adapter works, run it
   against all Permian-core counties that share the CivicEngage
   CMS (log which).

### Acceptance

- Layer count: 25 → 26 if §1 ships, 25 if dropped.
- Reeves adapter either reproduces Pecos Power Plant row OR
  produces a diagnostic note in `§Open backlog` identifying the
  failure mode.
- `docs/sprint-plan.md` is deleted at close-out (last chat in
  sprint); a new one may be created for the next 5-chat window.

### Close-out

Deploy → merge → delete branch → update `WIP_OPEN.md` §Next chat
to whatever follows (Chat 92 = Permian-core abatement wave, per
current sprint queue) → delete `docs/sprint-plan.md` → push.
