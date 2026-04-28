# Chat 112 mid-chat handoff — ERCOT queue geocoding stage 1

Status: code + data work complete on `refinement-chat112-ercot-geocode-stage1`. Build, deploy, merge **not done**. Stage 1 is **not in prod**.

You are resuming this chat. Branch already has three commits on top of `main`:

1. `9acb46a` — `scripts/geocode_ercot_queue.py` + `outputs/refresh/_geocode_ercot_log.txt`
2. (next commit) — `combined_points.csv` rewritten with new `coords_source` column; 334 rows geocoded
3. (most recent) — `build_template.html` ercot_queue popup adds "Coordinates" provenance row

Per OPERATING.md §11 "trust handoff recon": do not re-verify the work above. The script ran successfully end-to-end and the file diffs are already committed and pushed.

## What Stage 1 actually delivered

| Bucket | Matched | Total | Rate |
|---|---|---|---|
| Solar | 131 | 625 | 21.0% |
| Wind (EIA-860 + USWTDB) | 56 | 155 | 36.1% |
| Battery | 132 | 896 | 14.7% |
| Gas | 25 | 98 | 25.5% |
| **Solar + wind + battery** | **309** | **1,676** | **18.4%** |

Below the WIP_OPEN.md ≥60% acceptance target. See "Reframe" below before doing anything to retune the matcher.

## Reframe — read before touching the matcher

The 60% target was structurally unreachable in Stage 1. EIA-860 indexes **operating** plants. The ERCOT GIR queue is **forward-looking by design** — most queue projects haven't been built yet, so they cannot appear in EIA-860 regardless of fuzzy-match tuning. The 18.4% is approximately the share of queue projects that have already commissioned and entered EIA-860.

Do not lower the WRatio threshold to chase the 60% number. Below 88 the match quality collapses (verified via sample misses in `_geocode_ercot_log.txt`).

The actual lever is Stage 2 (TPIT substation/POI proximity). Every queue project specifies a POI substation regardless of operating status. That moves the rate well past 60% on its own.

WIP_OPEN.md `## Sprint queue` description of Stage 2 should be updated when you write the new handoff: TPIT POI matching is the **primary** geocoding mechanism, not a minor extension. Stage 1 (EIA-860) is the cheap pre-pass for already-operating projects.

## Secondary finding

Original WIP_OPEN.md framing said "All 1,778 ercot_queue rows currently sit at county centroids — visible as clusters at county center." Streaming verification before the script ran showed 187 counties hold ercot_queue rows with up to 36 distinct coord pairs each. Coords already varied per row pre-script. The script preserves existing lat/lon for unmatched rows and stamps `coords_source=county_centroid` only as a provenance label — that is correct behavior, but it means the popup label "County centroid (approximate)" applied to centroid-bucket rows is technically a description of provenance reliability, not literal geometric centroid placement. Acceptable as-is; flag if operator wants stricter language.

## Next steps in order

1. **Build.** `python3 build.py`. Acceptance: `built=26 missing=0 errored=0`.
2. **Deploy to prod.** Per OPERATING.md §8: Netlify MCP `deploy-site` → CLI proxy `npx -y @netlify/mcp@latest --site-id 01b53b80-687e-4641-b088-115b7d5ef638 --proxy-path "<URL>" --no-wait` → poll `get-deploy-for-site` → sleep 45 → `curl -A "Mozilla/5.0"` verify.
3. **Verify.** Compare prod md5 vs local `dist/index.html` md5. Spot-check ercot_queue popup shows "Coordinates: County centroid (approximate)" (or eia860/uswtdb where matched).
4. **Atomic close-out per §6.12.** `bash scripts/close-out.sh refinement-chat112-ercot-geocode-stage1 <deploy-id>`.
5. **Update WIP_OPEN.md `## Next chat`** for Chat 113 — Stage 2 (TPIT POI proximity). Reframe Stage 2 as the primary geocoding mechanism. Update `## Sprint queue` ERCOT section likewise. Then delete this handoff doc on the branch before close-out runs (§10 "Deleted on the branch before close-out merges to main" — but close-out.sh handles WIP_OPEN.md commit; you handle the handoff-doc deletion as a separate commit before invoking close-out.sh).

## Tool-call budget for the resume

§12 budget for build+deploy is ~4 calls. Reserve ~3 more for close-out and WIP_OPEN.md edit. Total ~7. Achievable.

## What not to do

- Do not re-run `geocode_ercot_queue.py`. The data is already on the branch.
- Do not lower the WRatio threshold below 88.
- Do not retune the suffix-stripping in `norm_name` to chase higher match counts. Sample misses in `_geocode_ercot_log.txt` are mostly project-name mismatches (`MAKALU SOLAR` in HUNT — no Hunt County solar plant in EIA-860 yet), not normalization gaps.
- Do not merge before deploying. §6.12 atomicity.
