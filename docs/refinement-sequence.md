# Refinement stage specs — pointer

Canonical breakdowns: `docs/sprint-plan.md`. Refresh mechanisms and cadence: `docs/refresh_automation_plan.md`.

Stage shape for every refinement branch:
1. `git checkout main && git pull --ff-only && git checkout -b refinement-<slug>`
2. Execute the named task. Commit each logical unit immediately and push.
3. `bash scripts/deploy.sh --rebuild` (map work only).
4. `bash scripts/close-out.sh refinement-<slug> <deploy-id-or-none> "<message>"`.
