# Grid Wire bootstrap — transfer vehicle. DO NOT MERGE into lrp-tx-gis main.

This directory is the complete `10thMuses/lrp-grid-wire` repository, parked
here because the bootstrap session's GitHub credentials are scoped to
lrp-tx-gis only and cannot create repositories (API returns 403).

`lrp-grid-wire.bundle` carries the real git history (single root commit
8e7ec0b on main). The flat tree beside it is the same content, reviewable.

## To transplant (one-time)

1. Operator: create the private repo once at github.com/new — name
   `lrp-grid-wire`, owner 10thMuses, private, NO readme/license (empty).
2. Then either say "transplant grid wire" in a Code session with access to
   the new repo, or by hand:

       git clone lrp-grid-wire.bundle lrp-grid-wire
       cd lrp-grid-wire
       git remote set-url origin https://github.com/10thMuses/lrp-grid-wire.git
       git push -u origin main

3. Delete this directory from lrp-tx-gis (close this PR unmerged) once the
   transplant is confirmed.

Bootstrap verification status is in the session report: email pipeline
byte-identical to the Vol 16 reference drafts; PDF renders 15/15 pages,
Jost-only fonts, matching pagination landmarks.
