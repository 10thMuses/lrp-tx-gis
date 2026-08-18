# 04 — Operations Runbook

Day-to-day procedures: set up, refresh, build, deploy, verify, close out, troubleshoot.

---

## 1. First-time setup

```bash
git clone https://github.com/<ORG>/lrp-tx-gis.git
cd lrp-tx-gis
bash scripts/bootstrap-claude-code.sh
```

`bootstrap-claude-code.sh` is idempotent and safe to re-run. It:

1. Installs **tippecanoe** (`brew` on macOS, `apt-get` on Linux)
2. Installs Python deps: `pyyaml`, `pmtiles`, `requests`
3. Copies `.env.example` → `.env` if missing
4. Sets git identity defaults if unset
5. Runs a smoke test (`import yaml, pmtiles`)

Then populate `.env`:

```bash
GITHUB_PAT=          # fine-grained PAT, Contents R/W on this repo only
NETLIFY_PAT=         # Netlify personal access token
LRP_PROJECT_DIR=.
LRP_DIST_DIR=./dist
LRP_UPLOADS_DIR=./uploads
```

Where to mint each token: [`06-ACCOUNTS-AND-ACCESS.md`](06-ACCOUNTS-AND-ACCESS.md).

**Windows:** use `scripts/bootstrap-windows.ps1`. tippecanoe does not build natively on
Windows — either work in WSL, or use the cloud-build fallback
([§5.3](#53-cloud-build-fallback)).

### 1.1 Extra dependencies not in bootstrap

Several refresh scripts need packages `bootstrap-claude-code.sh` does not install. The
daily routine installs them at runtime; install them up front if you will run refreshes:

```bash
pip install rapidfuzz beautifulsoup4 pyshp shapely openpyxl cairosvg
```

### 1.2 Optional pre-commit hook

```bash
git config core.hooksPath scripts
```

Rejects staged files over 1 MB (override with `ALLOW_LARGE=1`) and warns on staged paths
outside the canonical set. Worth enabling — it is the only automated guard against
committing a large data file by accident.

---

## 2. Starting a change

Every change gets its own branch off `main`. No exceptions except emergency hotfixes,
which require a post-hoc commit explaining why.

```bash
git checkout main && git pull --ff-only
git checkout -b refinement-<slug>          # <slug> is 2–4 words, hyphenated
```

Or use the scripted version, which additionally checks whether the branch already exists
on origin (and checks it out rather than reconstructing it), prints any handoff doc, and
runs a production sanity check:

```bash
bash scripts/session-open.sh refinement-<slug>
```

---

## 3. Refreshing data

Each layer family has its own path. Run only what you need.

### 3.1 RRC wells — weekly

```bash
python3 build.py refresh wells      # = fetch_rrc.py wells + parse_rrc.py wells
python3 build.py                    # rebuild tiles
```

Downloads `dbf900.txt.gz` (~370 MB) and parses it into `data/wells_permian6.csv`
(~99,800 rows). Both the raw archive and the parsed CSV are gitignored — **commit
nothing from this step**. The data reaches the map only through the rebuild.

### 3.2 RRC permits — monthly

```bash
python3 scripts/fetch_rrc.py permits    # all EOM monthly snapshots (~108 files)
python3 scripts/parse_rrc.py permits    # 6-county filter → data/permits_permian6.csv
python3 build.py
```

`python3 build.py refresh permits` is **not** the right entry point — it still exits with
a stale "scoped-out" message. Run the two scripts directly.

### 3.3 ERCOT queue — monthly

```bash
python3 scripts/geocode_ercot_queue.py
```

Rewrites `ercot_queue` rows in `combined_points.csv` **in place, atomically**. Idempotent —
re-running with unchanged inputs produces no git diff. Commit `combined_points.csv` only
if it actually changed.

### 3.4 EIA-860 — annual (Feb–Mar release)

```bash
python3 scripts/refresh_eia860.py --year 2024
# → outputs/refresh/eia860_plants_<date>.csv, eia860_battery_<date>.csv
python3 build.py merge eia860_plants  outputs/refresh/eia860_plants_<date>.csv
python3 build.py merge eia860_battery outputs/refresh/eia860_battery_<date>.csv
git add combined_points.csv
git commit -m "refresh: eia860 from EIA-860 2024 release <date>"
python3 build.py
```

Bump `--year` when EIA publishes the next annual release.

### 3.5 Wind — quarterly

```bash
python3 scripts/refresh_uswtdb.py
python3 build.py merge wind outputs/refresh/wind_<date>.csv
git add combined_points.csv && git commit -m "refresh: wind from USWTDB <date>"
```

### 3.6 TCEQ gas turbines — monthly

```bash
python3 scripts/refresh_tceq_gas_turbines.py
python3 build.py merge tceq_gas_turbines outputs/refresh/tceq_gas_turbines_<date>.csv
```

Append a run entry to `outputs/refresh/CHANGELOG.md` — that file is append-only and is
the audit trail for this layer's scope decisions.

### 3.7 HIFLD layers — quarterly

```bash
python3 scripts/fetch_hifld.py <slug> <featureserver_url>
# writes data/hifld/<slug>.geojson, which layers.yaml already points at
git add data/hifld/<slug>.geojson
```

FeatureServer URLs are recorded in each layer's `description` in `layers.yaml`.

### 3.8 FCC fiber coverage — biannual

```bash
python3 scripts/refresh_fcc_fiber_coverage.py
```

### 3.9 Tax abatements — weekly probe

```bash
python3 scripts/scrape_abatements.py    # diagnostic probe only
```

> **This writes `data/abatements/abatement_hits_<timestamp>.csv`, which must NEVER be
> committed.** It is a diagnostic artifact, not a layer source. The layer is fed only by
> the pinned snapshot `abatement_hits_20260424_092810.csv` via
> `scripts/transform_abatements.py`. `.gitignore` protects this, and the daily routine's
> contract calls it out explicitly, because committing this file was the single defect in
> the routine's first run.

### 3.10 Datacenter anchors — weekly, automated

Runs on GitHub Actions Mondays 06:00 UTC and opens a proposal PR. Never auto-merged.
See [`07-AUTOMATION.md §2`](07-AUTOMATION.md#2-dc-anchors-refreshyml). To run manually:

```bash
ANTHROPIC_API_KEY=<key> python3 scripts/refresh_dc_anchors.py
# → outputs/refresh/dc_anchors_proposed.json
```

Applying a proposal is a **manual edit** to `data/datacenters/dc_anchors.json` plus a
bump of its `generated` date, followed by deleting the proposal file.

---

## 4. Building

```bash
python3 build.py
```

Takes ~1–3 minutes. Target output:

```
built=39  missing=0  errored=0  tiles_total=~29594 KB
```

A clean clone reports `missing=2` until the RRC refresh has run.

Sanity check the output without opening any data file:

```bash
ls -lh dist/tiles/ | head
du -sh dist/
```

---

## 5. Deploying

### 5.1 The one command

```bash
bash scripts/deploy.sh --rebuild
```

It prints the `deployId` on **stdout** and everything else on stderr, so it composes:

```bash
DEPLOY_ID=$(bash scripts/deploy.sh --rebuild) && \
  bash scripts/close-out.sh refinement-<slug> "$DEPLOY_ID" "<what shipped>"
```

Or as one atomic call:

```bash
bash scripts/ship.sh refinement-<slug> "<what shipped>" -- --rebuild
```

### 5.2 What deploy.sh actually does

| Step | Action | Failure |
|---|---|---|
| §8.1 | Build if `--rebuild` or `dist/` missing | exit 2 on `errored>0`, missing `built=` line, or missing `dist/index.html`/`dist/tiles/` |
| — | Resolve `NETLIFY_PAT`: repo `.env` → `/mnt/project/CREDENTIALS.md` → `$NETLIFY_PAT_ENV` | exit 3 |
| §8.2 | Zip `dist/` using Python's `zipfile` (the `zip` binary is not on every runner image) | — |
| §8.3 | `POST https://api.netlify.com/api/v1/sites/<siteId>/deploys` with the zip | exit 3 if no deploy id returned |
| §8.4 | Poll prod every 5 s until `md5(prod /) == md5(dist/index.html)`, 300 s ceiling | exit 5 |
| §8.7 | `verify_deployed_layers.py` — reads every layer's PMTiles tilestats from prod via HTTP range requests | **exit 7 — do not merge** |
| — | Echo `deployId` | — |

The md5-parity poll collapses "deploy is ready" and "CDN has propagated" into a single
signal. It works because `/*__BUILD_ID__*/` guarantees every build produces a byte-unique
`index.html`. Typical convergence: 5–60 s.

**Escape hatch:** `VERIFY_LAYERS=0 bash scripts/deploy.sh` skips the layer gate. Use it
only for a known-transient verifier or network fault — never to ship a real regression.
A deploy shipped this way is **not layer-certified** and should not be closed out.

### 5.3 Cloud-build fallback

If tippecanoe is unavailable locally (native Windows, restricted machine), use the
manual GitHub Actions workflow:

`Actions → build-and-deploy → Run workflow`

It builds on an Ubuntu runner and deploys to prod via the Netlify CLI. Requires the
`NETLIFY_AUTH_TOKEN` and `NETLIFY_SITE_ID` repo secrets.

> This path **skips the `verify_deployed_layers.py` gate**. Run it manually afterwards:
> `python3 scripts/verify_deployed_layers.py`

---

## 6. Verifying

```bash
# Root responds — ALWAYS pass a UA; the default curl UA gets 503 from the edge
curl -sI -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | head -1

# Layer count on prod
curl -s -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ \
  | grep -oE '"id":"[a-z_][a-z0-9_]*"' | sort -u | wc -l

# Every layer live and non-empty
python3 scripts/verify_deployed_layers.py

# Single tile
curl -sI -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/tiles/wells_permian6.pmtiles | head -1
```

`HEAD` on the site root returns 503 even when `GET` is healthy — a bot-detection
heuristic. Use `GET` and grep for markers.

### 6.1 Verification scales to blast radius

| Blast radius | Examples | Required verification |
|---|---|---|
| **Low** | Colour tweak, label rename, doc edit | Clean local build; prod root 200 |
| **Medium** | New filter, template JS edit, build-pipeline change | Above + md5 parity + 2–3 tile spot-checks |
| **High** | Schema change, layer addition, credential rotation, destructive migration | Full acceptance ([§7](#7-acceptance-criteria)) + tile-level verification for every touched layer + **visual confirmation at the prod URL** |

---

## 7. Acceptance criteria

A change is shipped when all of these hold:

1. **Build clean** — `built=<N> missing=0 errored=0`, where `N` matches the
   `layers.yaml` entry count (currently 39)
2. **Local ↔ prod md5 parity** on `dist/index.html`
3. **Branch merged and deleted** in the same session as the deploy
4. **`bash scripts/audit.sh` clean** for any drift the change introduced

High blast radius additionally requires tile-level verification and a visual check at
the prod URL with the affected layer toggled on.

---

## 8. Hard rules

Non-negotiable. A violation requires a corrective commit.

1. **Never read source data files into context.** No `cat`/`head`/`view` of
   `combined_points.csv`, `combined_geoms.geojson`, or any layer source. Stream through
   subprocesses. Reading once is a mistake; reading repeatedly is a crisis.
2. **Never `git add -A`.** Always stage explicit paths.
3. **Never hand-code coordinates or feature values.** Every point traces to a public
   dataset cited in [`02-DATA-SOURCES.md`](02-DATA-SOURCES.md).
4. **Atomic in-place writes** — `os.replace(tmp, final)`, never `'w'` mode mid-process.
5. **Atomic deploy + merge.** A shipping unit is build → deploy → verify → merge →
   delete branch. Stale `refinement-*` branches on origin are a smell.
6. **Never deploy a build with `errored>0`.**
7. **Branch from `main` for every change.**
8. **Verification scales to blast radius** ([§6.1](#61-verification-scales-to-blast-radius)).

---

## 9. Closing out

```bash
bash scripts/close-out.sh refinement-<slug> <deployId|none> "<one-line summary>"
```

Use the literal string `none` for doc-only changes with no deploy.

Sequence: commit pending `WIP_OPEN.md` → push branch → assert ≥1 non-handoff commit
beyond `main` → remove any handoff doc → checkout `main` → `pull --rebase` → `merge
--no-ff` with the deploy id in the message → push `main` → delete the origin branch.

| Exit | Meaning |
|---|---|
| 0 | Clean |
| 3 | Bad args, wrong branch, or uncommitted tracked changes outside `WIP_OPEN.md` |
| 4 | Recon-only branch — zero non-handoff commits, refusing to merge |
| 5 | Merge conflict — resolve manually |
| 6 | Push to `main` rejected |

Merge messages must match `Merge <branch>: <title> (deploy <id>|no deploy)`. `audit.sh`
measures conformance against that pattern, so hand-rolled merges show up as drift.

---

## 10. Auditing

```bash
bash scripts/audit.sh
```

| Metric | Target |
|---|---|
| `OPERATING.md` lines | ≤ 250 |
| `WIP_OPEN.md` bytes | ≤ 8192 |
| Merge commits in last 30 | informational — each ≈ one shipping unit |
| Close-out conformance | 100% |
| Stranded `refinement-*` / `claude/*` branches on origin | **0** |
| Repo size | informational |

Any red signal is fixable in a small commit. Do not let them accumulate.

Per `OPERATING.md §8`: when a process problem recurs, prefer a **structural fix**
(script, schema, build-time check) over a prose rule. What has worked: `close-out.sh`
enforcing atomic deploy+merge; `/*__BUILD_ID__*/` making md5-parity reliable; the
`errored>0` deploy refusal. What has failed: prose rules nobody reads at the right moment.

---

## 11. Troubleshooting

Symptom-indexed.

| Symptom | Cause | Fix |
|---|---|---|
| `deploy.sh` exit **2** | `errored>0`, or the build aborted before writing its report | Read `/tmp/build.log`. Fix the layer. Never bypass. |
| `deploy.sh` exit **3** | `NETLIFY_PAT` missing/invalid, or the deploy API returned no id | Check `.env`. After a migration, the token may not have access to the new team. |
| `deploy.sh` exit **5** | md5 parity not reached in 300 s | Usually CDN lag — re-run the poll. If it never converges, check `/*__BUILD_ID__*/` still exists in `build_template.html`. |
| `deploy.sh` exit **7** | Layer verification failed — a layer is missing or zero-count on prod | **Do not merge.** The deploy artifact exists but is uncertified. Investigate the named layer and redeploy. |
| Layer builds but has **0 features** | `-zg` auto-zoom on a single-feature input | Use explicit `-Z0 -z14` in that layer's `tippecanoe:` args |
| Layer reports **MISSING** | Source file not resolvable | Expected for `wells_permian6` / `permits_permian6` on a clean clone — run the RRC refresh |
| Prod returns **503** to curl | Default curl UA is blocked by the edge | Add `-A "Mozilla/5.0"` |
| `HEAD /` returns 503 but the site works | Bot-detection heuristic | Use `GET` and grep |
| Wells plotted outside Texas | dbf900 longitude sign overpunch | The parser forces longitude negative — check `parse_rrc.py` was not modified |
| RRC fetch fails with a ViewState error | RRC changed the GoAnywhere/PrimeFaces flow | `fetch_rrc.py` raises explicitly by design. Re-derive the protocol against the live page. |
| AGOL fetch 503 "DNS cache overflow" | Cold FeatureServer | Retry — the fetchers do 5 × 10 s automatically |
| EIA download 503 | Missing `Referer` header | Send `Referer: https://www.eia.gov/electricity/data/eia860/` + a real UA |
| Reeves County scrape 403 | Akamai datacenter-egress block | **No fix from a cloud runner.** Run from a residential connection or skip. |
| tippecanoe not found | Fresh container | `bash scripts/bootstrap-claude-code.sh` |
| tippecanoe "database is locked" | `--read-parallel` on overlayfs/tmpfs | It was removed deliberately — do not add it back |
| `git push` 404s after migration | Fine-grained PAT still scoped to the old owner | Mint a new PAT with the new org as resource owner; org may need to approve it |
| Map loads but tiles never appear | `vendor/` missing from `dist/`, or CORS headers not applied | Check `dist/vendor/` exists and `_headers` shipped |
| Portal gate rejects a correct password | `oxy_config.gate_password` changed, or the Supabase project is paused | See [`06-ACCOUNTS-AND-ACCESS.md §4`](06-ACCOUNTS-AND-ACCESS.md#4-the-portal-password-gate) |
| Daily refresh report shows `blocked(403)` on everything | Cloud-egress blocking, or a genuinely stale contract | See [`07-AUTOMATION.md §3.3`](07-AUTOMATION.md#33-known-contract-staleness) |

---

## 12. Command quick reference

```bash
# Setup
bash scripts/bootstrap-claude-code.sh

# Start work
bash scripts/session-open.sh refinement-<slug>

# Refresh
python3 build.py refresh wells
python3 scripts/fetch_rrc.py permits && python3 scripts/parse_rrc.py permits
python3 scripts/geocode_ercot_queue.py
python3 scripts/refresh_eia860.py --year 2024
python3 scripts/refresh_uswtdb.py
python3 scripts/refresh_tceq_gas_turbines.py
python3 scripts/refresh_fcc_fiber_coverage.py
python3 scripts/fetch_hifld.py <slug> <url>

# Merge a refresh into a combined file
python3 build.py merge <layer_id> <refresh_file>

# Build
python3 build.py

# Ship (deploy + close-out, atomic)
bash scripts/ship.sh refinement-<slug> "<summary>" -- --rebuild

# Or in two steps
DEPLOY_ID=$(bash scripts/deploy.sh --rebuild)
bash scripts/close-out.sh refinement-<slug> "$DEPLOY_ID" "<summary>"

# Verify
python3 scripts/verify_deployed_layers.py
curl -sI -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | head -1

# Audit
bash scripts/audit.sh
```
