# Grid Wire

Intra-day capital markets and infrastructure briefing. Andrea Himmel, Land
Resource Partners. Five cuts daily: 9:30 AM, 12 PM, 3 PM, 6 PM, 9 PM ET. One
Vol number per publication day; cuts are labeled by time and are
**incremental** — each covers only what is new since the prior cut. Output per
cut: one WeasyPrint PDF + two plain-ASCII email drafts (Mel, Mark).
Counterparty emails are **draft-only** unless explicitly overridden.

Sole analytical spine: the physical-layer thesis — financed claims reprice
cheaper; land, water, gas, turbine slots, transmission cannot be financed into
existence.

## Operating rules

1. Trigger `cut <time>.` = pull main -> read WIP_OPEN.md -> web-research
   deltas since last cut -> draft -> render PDF -> make emails -> archive
   under `issues/` -> update WIP_OPEN.md + WIP_LOG.md -> commit + push ->
   hand operator the three files. No questions if unblocked.
2. Trigger `vol.` at first cut of a new day = increment vol, carry open
   falsification register forward, reset incremental baseline.
3. Banned phrases: *should I proceed*, *want me to*, recaps. Narrow ask
   whitelist: irreversible action, new spend, strategic fork, missing
   credential, operator-only facts.
4. Never `git add -A`. Explicit paths.
5. Hard-fail any cut where assert_ascii trips or WeasyPrint falls back from
   Jost (`pdffonts` post-render; expect Jost subsets only). Both checks are
   built into the scripts.
6. Research budget: incremental cuts target what changed in the window; the
   6 PM close cut is the expanded full edition. Do not restate prior-cut
   content except falsification-status updates and the tape.
7. Repo > memory. WIP_OPEN.md is the only source for current vol/cut state.

## Workflow

```bash
python3 scripts/new_cut.py <vol> <cut_slug>          # scaffold from prior cut
# write issues/vol{N}/{cut}/draft.md + email_source.txt
python3 scripts/render_pdf.py issues/vol{N}/{cut}/draft.md
python3 scripts/make_email.py issues/vol{N}/{cut}/email_source.txt
```

`main` is canonical. Work on `cut-<vol>-<time>` branches after bootstrap.
Reference gold standard: `reference/` (Vol 16, June 10 2026, 6:00 PM ET).
Full pipeline spec: `OPERATING.md`. Editorial spec (locked): `STYLE.md`.

## Credentials

`CREDENTIALS.md` is gitignored and holds `GITHUB_PAT` (fine-grained, Contents
R/W, this repo only). Ask the operator once at bootstrap if missing.
