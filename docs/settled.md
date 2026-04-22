# Settled Decisions

Never re-ask. Never re-litigate. If a decision lives here, it's final. Revisit only if the ground shifts materially (new data source appears, platform constraint lifts, thesis pivots).

Append only. Do not rewrite history. If a decision is overturned, strike it through, add the reversal below with date and reason.

---

## Architecture & build

**Option B: prebuilt PMTiles for large GeoJSON.** Layers whose source GeoJSON exceeds ~10 MB bypass project-knowledge ingestion entirely. Pre-built `.pmtiles` files are checked in as binary to the repo, or resolved at build time from one of three tiers: (1) `/mnt/project/<id>.pmtiles`, (2) `/mnt/user-data/uploads/<id>.pmtiles`, (3) `https://lrp-tx-gis.netlify.app/tiles/<id>.pmtiles`. `layers.yaml` flags these with `prebuilt: true`. `build.py` skips tippecanoe for these layers and copies the PMTiles through. First applied to `parcels_pecos` (Chat 41–42).

**Flat data layout at repo root.** All `points_*.csv`, `geoms_*.geojson`, `deal_*.geojson`, `combined_*.{csv,geojson}` files live flat at the repo root. No nested `data/` folder. Rationale: every existing `build.py` and doc path would break with subfolders, and the flat layout already works. Revisit only if file count exceeds ~50.

**Single `layers.yaml` config.** Adding a layer = one yaml append. `build.py` and `build_template.html` are never modified as part of a layer addition. Styling tweaks (color, default_on, min_zoom, popup fields, radius, labels, groups) are yaml edits only.

**Full rebuild every chat.** Container resets between chats; there is no incremental-build state to preserve. The full rebuild is the accepted cost of the isolation model. Each shipping chat emits `dist/index.html` + `dist/tiles/*.pmtiles`.

**Data files never read into Claude's context.** CSVs and GeoJSONs stream through tippecanoe subprocesses only. Reading them into context for model inspection burns tokens and produces nothing useful. Enforced in `GIS_SPEC.md` Hard Rule #1.

---

## Deploy

**PMTiles deploys via proxy bash, not MCP.** Netlify MCP `deploy-site` returns a one-time-token proxy URL; actual deploy runs locally via `npx @netlify/mcp`. File sizes exceed MCP inline limits. Pattern: MCP call → CLI proxy command → retry on 503 with ~45–75s CDN warm-up window.

**Never deploy to prod if build report shows `errored > 0`.** Stop and report. No exceptions.

---

## GitHub sync

**Clone-push bracket for shipping sessions** (established Chat 48). First bash call: `git clone --depth=1` into `/home/claude/repo/`. Last bash call before final response: `git add -A && git commit && git push`. No-op if no changes. Push-reject fallback = `git pull --rebase && git push` once; still rejected → halt, report, leave repo in detached state.

**Git Data API tree commit for doc-only edits** that don't need tooling. No clone required. Reduces tool-call budget for small doc changes.

**Main branch direct commit.** No PR workflow for routine GIS chats. Branch + PR workflow applies only when explicitly scoped (e.g., structured refinement sequences).

**PAT in gitignored `/mnt/project/CREDENTIALS.md`.** Never in userMemories. Never in repo history. Fine-grained single-repo scope, `contents: read/write` only. Classic PAT with `repo` scope acceptable.

**No Git LFS.** Revisit if any single file >50 MB. Current max: `combined_points.csv` at ~4.5 MB.

---

## Scoped-out data sources

**`rrc_wells_permian` excluded** (Chat 53 decision). RRC MFT portal (`mft.rrc.texas.gov`) is GoAnywhere PrimeFaces AJAX — no direct-URL path for bulk downloads. Re-scope would require either manual browser-downloads of 12 Permian-county shapezips or implementing an AJAX downloader. Neither is worth the cost given the per-county fetching overhead.

**Per-county / per-chunk fetching is a data-source-shape problem.** There is no workflow fix. Sources that require per-county iteration at fetch time (e.g., RRC MFT) are scoped out by default unless a bulk endpoint is discovered.

---

## Newsletter (Grid Wire)

**Structure locked:** 8 sections + LRP appendix + Blackstone QTS standing section + Transactions & Comps section. Volume-numbered, dated. Weekly cadence.

**Write-first approach.** Targeted gap-fill searches only. Broad parallel pre-loading exhausts context before synthesis.

**Voice:** Munger / Sanders / Burry register — dry, declarative, contrarianism implicit, short sentences, minimal adjectives. ≤3 hashtags per LinkedIn post.

---

## Operating cadence

**One chat = one operation.** Build, refresh, add-layer, doc update — each is a separate chat. Sequential operation is architecturally correct for this workload.

**Trigger phrases optional.** `build.`, `refresh X.`, `add layer...` remain valid shipping-classifier inputs. Natural-language shipping prompts also route correctly. Operator picks whichever is faster to type.
