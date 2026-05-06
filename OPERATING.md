# OPERATING.md

Execution rules for the LRP Texas Energy GIS Map repo. Read alongside `CLAUDE.md` (environment + first-time setup), `ARCHITECTURE.md` (schema, layer catalog, palette), and `WIP_OPEN.md` (active work).

---

## 1. Source of truth

The repo is canonical. `main` branch is the deployed state.

`https://lrp-tx-gis.netlify.app` reflects whatever was last deployed from `main`. The deployed bundle and the repo's `dist/` build are byte-identical when in sync — `scripts/deploy.sh` enforces this via md5-parity check.

---

## 2. Operator interaction model

Andrea Himmel is the operator. She is direct, technical, and time-constrained. Match the register.

**Banned phrases:** *should I proceed*, *do you want me to*, *want me to go ahead and*, *would you prefer A or B*, *say ship it and I'll*, *confirm to ship*, *let me know if*, *ready to proceed?*, recap sections that just restate what was already said, history logs of completed steps. When the next move is named and unblocked, execute.

**Acceptable asks** (narrow list):
1. Irreversible destructive action (force-push to main, delete deployed PMTiles, drop a data file from the repo)
2. New spend or external commitment (paid data subscription, new vendor)
3. Materially-different strategic fork (switch mapping library — not "blue or green for this layer")
4. Missing credential that cannot be obtained
5. Factual input only Andrea has (county to target, thesis decision, layer audience)

Anything else is execution.

---

## 3. Hard rules

These are non-negotiable. Violations require a corrective commit.

1. **Never read source data files into context.** Stream through `tippecanoe` subprocesses only. No `cat` / `head` / `view` of `combined_points.csv`, `combined_geoms.geojson`, or any layer source file. Reading once is a mistake; reading repeatedly is a crisis.
2. **Never `git add -A`.** Always stage explicit paths. Prevents accidental commits of `dist/`, `__pycache__/`, scratch files, `.env`.
3. **Never hand-code coordinates or feature values.** No source, no layer. Every point and polygon traces to a public dataset cited in `ARCHITECTURE.md`.
4. **Atomic in-place writes** for any read-modify-write helper. Use `os.replace(tmp, final)`, never open in `'w'` mode mid-process. Applies to merge subcommand, geocode override pass, any script that rewrites a tracked file.
5. **Atomic deploy + merge.** A shipping unit is `build → deploy → verify → merge → delete branch`. Never deploy without the matching merge in the same session. Stale `refinement-*` branches on origin are a smell.
6. **Never deploy a build with `errored>0` in the build report.** `scripts/deploy.sh` checks this and exits 2.
7. **Branch from `main` for every change.** Direct commits to `main` are reserved for emergency hotfixes only and require an immediate post-hoc commit message explaining why.
8. **Verification scales to blast radius.**

| Blast radius | Examples | Verification |
|---|---|---|
| Low | Single layer color tweak, label rename, doc edit | Local build clean, prod root 200 |
| Medium | New filter, template JS edit, build pipeline change | Above + bundle md5 parity, 2–3 tile spot-checks |
| High | Schema change, credential rotation, destructive migration, layer addition | Full acceptance protocol per §5 |

---

## 4. Build / refresh / merge cycles

**Full build:** `python3 build.py`. Reads `layers.yaml`, splits combined files, tippecanoes per-layer, copies prebuilt PMTiles, writes `dist/index.html`. Refuses to deploy if any layer reports `errored=1`.

**Single-layer refresh:** `python3 build.py merge <layer_id> <refresh_file>`. In-place atomic-rename merge into `combined_points.csv` or `combined_geoms.geojson`. Commit the result; rebuild as a separate step.

**Deploy:** `bash scripts/deploy.sh [--rebuild]`. Reads `NETLIFY_PAT` from `.env`. Sequence:
1. Build if `--rebuild` or `dist/` missing. Exit 2 if `errored>0`.
2. Netlify MCP `deploy-site` returns single-use proxy URL.
3. `npx -y @netlify/mcp@latest --site-id <id> --proxy-path "<url>" --no-wait` uploads from `dist/`. Captures `deployId`.
4. Poll prod URL md5 against local `dist/index.html` md5. Parity == `state=ready` AND CDN propagated, in one signal. Typically 5–60s. Hard timeout 5 minutes.
5. Echo `deployId` on stdout.

The md5-parity poll relies on every build producing a byte-unique `index.html`, guaranteed by the `/*__BUILD_ID__*/` token (UTC timestamp + nonce) injected at render time in `build.py`.

**Close-out:** `bash scripts/close-out.sh <branch> <deploy-id-or-none> "<message>"`. Pushes feature branch, checks out `main`, rebases, merges `--no-ff`, pushes `main`, deletes origin branch. Atomic with the deploy step.

---

## 5. Acceptance criteria

A change is "shipped" when all of these hold:

1. **Build clean.** `built=N missing=0 errored=0` where N matches the layer count in `layers.yaml` (currently 26 entries → 24 display layers).
2. **Local↔prod md5 parity** on `dist/index.html` (deploy script enforces this, but worth confirming visually after the script returns).
3. **Branch merged + deleted** in the same session as the deploy.
4. **`audit.sh` clean** for any drift introduced by the change.

For high-blast-radius changes also require:
5. **Tile-level verification** for any layer touched (curl HEAD on `/tiles/<id>.pmtiles` returns 200, optionally pmtiles metadata read).
6. **Visual verification at prod URL** (open the map, toggle the affected layer, confirm rendering).

---

## 6. GitHub sync

`main` is canonical. Push every commit immediately — backup against local disk failure, triggers any CI, keeps the remote authoritative.

The fine-grained PAT in `.env` (`GITHUB_PAT`) has Contents R/W on `10thMuses/lrp-tx-gis` only. It can push branches and merge, but cannot create PRs (Pull Requests permission is excluded by design — the protocol is direct merge-to-main, not PR review). Most git operations (clone, fetch, push, pull) use the local credential helper, not the PAT directly.

---

## 7. Telemetry

`bash scripts/audit.sh` reports drift signals:
- `OPERATING.md` lines (target ≤250)
- `WIP_OPEN.md` bytes (target ≤8192)
- merge commits in last 30 (each ≈ one shipping unit)
- close-out conformance (target 100%)
- stranded `refinement-*` branches on origin (target 0)
- repo size

Any drift signal in red is fixable in a small commit. Don't let them accumulate.

---

## 8. Rule additions

When a process problem recurs, prefer a **structural fix** (script, schema, build-time check) over a **prose rule**. Examples that worked: `close-out.sh` enforces atomic deploy+merge; `/*__BUILD_ID__*/` injection makes md5-parity a reliable signal; `errored>0` build refuses deploy. Examples that failed: prose rules in `OPERATING.md` that nobody reads at the right moment.

When adding a rule, include:
1. The failure mode it prevents (concrete example)
2. The structural enforcement (script, build check, lint) — or honest admission that no enforcement exists
3. The recovery procedure if violated

---

## 9. Settled decisions

Architectural decisions that should not be re-litigated without a strong reason:

- **MapLibre + PMTiles + tippecanoe** stack. Not Leaflet. Not Mapbox GL JS proper (license).
- **Netlify hosting.** Not Vercel. Not Cloudflare Pages. The MCP integration and CDN behavior are calibrated.
- **Single-page app, no build framework.** No React, no Vue, no bundler. `build_template.html` is a hand-edited file with `/*__LAYERS__*/` and `/*__BUILD_ID__*/` token substitution at render. Adding a framework would lose the "edit one file, see the result" property.
- **Combined data files** (`combined_points.csv` for all points, `combined_geoms.geojson` for all polygons/lines) with `layer_id` tag column, split per-layer at build time. Standalone layer files are the exception, used only when size or schema demands it.
- **`main` is canonical**, not `master`, not `prod`. `refinement-<slug>` for feature branches. No long-lived branches.
- **Direct merge to main, no PRs.** Single-operator repo; PR review adds latency without catching anything that the build/deploy/verify cycle doesn't already catch.
