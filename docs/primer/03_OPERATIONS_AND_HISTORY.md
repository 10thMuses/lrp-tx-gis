# Part 3 — Operations, Methods, Deliverables & History

Repo: `/home/user/lrp-tx-gis` (`github.com/10thMuses/lrp-tx-gis`, `main` canonical). Primer written 2026-10-21 from the repo at origin/main tip `a596741` (merge of `claude/nice-ritchie-tgzt8b`, deploy 6ad77b77) plus operator-verified facts of 2026-10-20.

Conventions in this document:

- Paths are repo-relative unless absolute. "Not documented in repo" marks an unknown.
- "verified 2026-10-20" marks facts supplied from live tooling (Netlify, Supabase, GitHub Actions, prod site). They are not derivable from code.
- "observed 2026-10-21" marks facts read in this session (git, `scripts/audit.sh`).
- No secret values appear here. Variables and secrets are named only.
- No source data file (`combined_points.csv`, `combined_geoms.geojson`, `data/**`, `outputs/refresh/*.csv`) was opened to write this. Only `.md`, `.py`, `.js`, `.sh`, `.yml`, `.html` text, git metadata, and aggregate counts already printed in repo docs were used.
- Read-and-skimmed vs read-fully: all named root and `docs/*.md` files, `outputs/reports/*.md`, every file in `scripts/` (header, constants, argument handling; not every line of the 800-1,300-line builders), `.github/workflows/*.yml`, git history (shallow, see §10).

---

## 1. Operator, audience, business context

### 1.1 Operator

- **Andrea Himmel**, Land Resource Partners (LRP; email domain abhcm.com). Works across energy infrastructure, land, and real estate: ERCOT, Texas data centers, advanced nuclear, GPU/AI infrastructure financing, grid policy (`CLAUDE.md`).
- Direct, technical, time-constrained. Voice: peer-level, concise, factual, no fluff, no recap, no "should I proceed" hedging. When the next move is named and unblocked, execute (`CLAUDE.md`, `OPERATING.md` §2).
- Public byline for Grid Wire: "Andrea Himmel of LAND · The Grid Wire". No LRP or ABH attribution on public-facing content; internal editions may carry it (`docs/grid-wire-master-instructions-v4.md` Part L; `docs/grid-wire-scheduled-task-prompt.md` §3.10).
- 2026-10-20 operator wants: (a) all data to refresh automatically ("real time"), (b) the map public.

### 1.2 Audience

Peer and deal distribution named in `CLAUDE.md`: Mel Riggs, Mark, Dory Wiley, John Lane. Used as an intelligence product (Grid Wire) and investment-analysis support.

| Audience | What they get | Source |
|---|---|---|
| Mel, Mark (Grid Wire recipients) | Two plain-ASCII email drafts per edition ("Mel" draft; "Mark" = Mel with first salutation swapped). Draft-only, never auto-sent. | `docs/grid-wire-master-instructions-v4.md` Part J.4; `docs/settled.md` |
| Dory Wiley, John Lane | Named as peers in `CLAUDE.md`. Specific distribution list Not documented in repo. | `CLAUDE.md` |
| Newmark deal team (buyer side / broker) | Caramba North OM, Appendix A, pre-NDA teaser. Operator-supplied; the repo does not name Newmark as an OM recipient. (Newmark appears only as the broker of the $2.3B JPMorgan Abilene loan in `outputs/reports/stargate-abilene-diligence-2026-06-13.md`.) | operator brief |
| Prospective buyer (data-center developer) | Drilling and vibration memo with data tool link (`outputs/reports/buyer-email.md`, `Pecos-Shallow-Drilling-Caramba-Vibration.pdf`). | `outputs/reports/buyer-email.md` |
| Landowner (Williams family) | Advisor email framing the buyer memo (`outputs/reports/owner-email.md`). LRP "advises the Clayton Williams family" (`outputs/reports/oxy-partnership-intelligence-2026-06-19.md`). | same |
| Grid Wire daily recipient | Cut PDF emailed to `andrea@abhcm.com` by the scheduled routine. | `docs/grid-wire-scheduled-task-prompt.md` Step 5 |

### 1.3 Business context

**Subject property: Caramba North.** ~1,300 contiguous acres (max), Pecos County, TX, north of I-10, ~5 mi from Fort Stockton. Tract centroid ~30.9032 N, 102.9747 W. No zoning ordinance. ERCOT Far West weather zone. Repurposing for hyperscale data-center use (`docs/redesign_content_brief.md` §2.1; `outputs/reports/pecos-shallow-drilling-caramba-vibration.md`).

**Origin of the map (spring 2026).** The map began as the visual exhibit for the Hanwha Energy USA land-sale legal-defense thesis: drilling collapsed in the "sale area" (Pecos, Reeves, Ward) while the "boom area" peers (Midland, Martin, Reagan) kept drilling. This explains the 6-county scope and `county_role` tag on wells and permits (`ARCHITECTURE.md` §5 scope note; `docs/archive/wip_history_pre_2026-05-18.md` "6-county rescope"). The map has since been repurposed to sell Caramba North.

**Thesis pillars (OM, from `docs/redesign_content_brief.md` §1-§2):**

1. **Property.** As-of-right industrial/energy land in ERCOT's fastest-growing large-load pocket.
2. **Transmission.** 15 mi from AEP/CPS Solstice Substation, western terminus of three PUCT-approved 765 kV Permian import paths (PBRP Docket 55718, approved 2025-04-24). Six local substations within 10 mi. 141 TPIT substation + 133 line upgrades tracked ERCOT-wide (planned, not committed).
3. **Regional power cluster.** Pecos operating 3,226 MW (solar 2,178; wind 542; BESS 505; gas 1); ERCOT queue 12,039 MW / 39 projects in-county; 13 projects / 3,973 MW within 20 mi; ring analysis 0.5 / 8.9 / 32.7 / 53.5 GW at 15 / 30 / 60 / 100 mi.
4. **Water.** 47,418 AF/yr (42.3 MGD) permitted on adjacent affiliated lands, about two-thirds of Middle Pecos GCD industrial rights (Edwards-Trinity). Counterparty-supplied.
5. **Gas.** 20 mi to Waha. Indicative quote: 200,000 MMBtu/d, 15-yr, Waha-index, CIAC $15-25M, 9-15 month lead. Counterparty-supplied.
6. **Regional data-center pipeline.** GW Ranch (Amazon disclosed ownership Aug 2026; Pacifico remains power developer; 7.65 GW TCEQ air permit; 15.5 mi edge-to-edge) and Longfellow / Project Horizon (19.3 mi edge-to-edge; infrastructure-first framing, no tenant narrative).
7. **Subsurface.** Pecos has the lowest genuine new-drill count of seven comparable Permian counties since 2020; none within 5 mi; no active frack ever within 2 mi (see §4).
8. **Diligence platform.** The GIS map itself ("every figure re-derivable from a cited public source").

**Product and report families (details in §6):**

| Family | What it is |
|---|---|
| Caramba North OM set | Master OM, Appendix A (technical drawing set), pre-NDA teaser; legacy decks and briefs. |
| Drilling/vibration memo | Buyer-facing memo plus buyer and owner emails. Finding set underpins the OM §9. |
| **The Grid Wire** | Twice-daily (5:00 AM / 3:00 PM ET, per 2026-08-23 cadence) energy/AI-infrastructure/capital-markets intelligence PDF. 23 coverage domains, 147 sub-domains, West Texas first. Series A (Vols 1-21, to 2026-08-07, retired); Series B (restarted at Vol 1; Vol 13 = 2026-08-19; Vol 14 = 2026-08-26 is the last logged in repo). Plus special reports (Stranded Iron, 2026-07-27; Crusoe Spark, 2026-09-22). |
| OXY intelligence report | Occidental infrastructure dossier framed for a hyperscale-DC JV between the Williams family (Caramba North) and OXY; plus partnership brief/deck and an OXY layer group on the map (7 layers). |
| Crusoe report | `outputs/reports/special/crusoe-20260922/` (Grid Wire special report, "Crusoe Spark: The Modular Pivot"; v1 modular DC + power pivot, v2 adds capitalization/project register/case studies/governance and drops the WTX section, v3 "Spark" narrows scope). |
| Stargate / GW Ranch diligence | `Stargate-Abilene-Diligence-Report.pdf` (2026-06-13; Crusoe/Blue Owl/Lancium/Oracle) and `Pacifico-GW-Ranch-Diligence-Report.pdf` (2026-06-12; Pacifico, TCEQ 396366). Counterparty diligence memos. |

---

## 2. Operating rules and conventions

Precedence: **repo > sidebar > memory** (`Readme.md`). Where docs conflict with code, code and `main` win. Where Grid Wire master instructions conflict with the repo, the repo wins.

### 2.1 Hard rules (`OPERATING.md` §3, verbatim in substance; `CLAUDE.md` restates 1-5)

Violations require a corrective commit.

1. **Never read source data files into context.** Stream through `tippecanoe` subprocesses only. No `cat`/`head`/`view` of `combined_points.csv`, `combined_geoms.geojson`, or any layer source file. "Reading once is a mistake; reading repeatedly is a crisis."
2. **Never `git add -A`.** Always stage explicit paths (prevents committing `dist/`, `__pycache__/`, scratch, `.env`).
3. **Never hand-code coordinates or feature values.** No source, no layer. Every point and polygon traces to a public dataset cited in `ARCHITECTURE.md`.
4. **Atomic in-place writes** for any read-modify-write helper: `os.replace(tmp, final)`, never `'w'` mode mid-process. Applies to merge, geocode override pass, any script rewriting a tracked file.
5. **Atomic deploy + merge.** A shipping unit is `build → deploy → verify → merge → delete branch`. Never deploy without the matching merge in the same session. Stale `refinement-*` branches on origin are a smell.
6. **Never deploy a build with `errored>0`.** `scripts/deploy.sh` checks this and exits 2.
7. **Branch from `main` for every change.** Direct commits to `main` reserved for emergency hotfixes with an immediate post-hoc explanation.
8. **Verification scales to blast radius.**

| Blast radius | Examples | Verification |
|---|---|---|
| Low | single layer color tweak, label rename, doc edit | local build clean, prod root 200 |
| Medium | new filter, template JS edit, build pipeline change | above + bundle md5 parity, 2-3 tile spot-checks |
| High | schema change, credential rotation, destructive migration, layer addition | full acceptance protocol (§2.5) |

### 2.2 Operator interaction model (`OPERATING.md` §2)

- **Banned phrases:** *should I proceed*, *do you want me to*, *want me to go ahead and*, *would you prefer A or B*, *say ship it and I'll*, *confirm to ship*, *let me know if*, *ready to proceed?*, recap sections that restate what was said, history logs of completed steps.
- **Acceptable asks (only):** (1) irreversible destructive action (force-push to main, delete deployed PMTiles, drop a data file); (2) new spend or external commitment; (3) materially different strategic fork (switch mapping library, not "blue or green"); (4) missing credential that cannot be obtained; (5) factual input only Andrea has.
- Grid Wire runs under the same ask list (Part A.5): irreversible action, missing credential, operator-only factual input.

### 2.3 Branch, commit, close-out conventions

- Branch naming: `refinement-<slug>`, slug 2-4 words (`CLAUDE.md`). Start: `git checkout main && git pull --ff-only && git checkout -b refinement-<slug>`.
- Commit each logical unit immediately and push. Push every commit (backup, triggers CI, keeps remote authoritative) (`OPERATING.md` §6).
- Close-out: `bash scripts/close-out.sh refinement-<slug> <deploy-id|none> "<message>"`. Merge message form enforced by audit regex: `Merge <branch>: <title> (deploy <hexid>)` or `(no deploy)`.
- Direct merge to `main`, no PRs (single-operator repo). `GITHUB_PAT` is Contents R/W only on this repo and cannot create PRs by design (`OPERATING.md` §6).
- Process deviations on record: this session's work landed through a PR (#50, draft as of 2026-10-20) from `claude/nice-ritchie-tgzt8b`, and deploy 6ad77b77 happened before merge. Origin/main tip observed 2026-10-21 is `a596741` "Merge claude/nice-ritchie-tgzt8b: remove access gate, operating manual (deploy 6ad77b77)". PR #50's final state is Not documented in repo.
- Archived earlier convention (`docs/archive/refinement-sequence-2026-04.md`): branch + PR workflow, "open PR, do not merge, do not deploy." Superseded by direct merge. `docs/refinement-sequence.md` is now a pointer.
- Branch cleanup state observed 2026-10-21 (`scripts/audit.sh`, `git ls-remote`): 126 remote heads: `main`, 89 `refinement-daily-refresh-*` branches (2026-05-19 to 2026-08-19, never deleted), 22 `dc-anchors-refresh-N` branches (7-28), `refinement-rig-schema-baseline`, and 13 `claude/*` session branches (one is the current branch). Audit target is 0 stranded. The 2026-08-16 daily report carries a "close-out branch-delete warning" addendum (commit 3fa53f5).

### 2.4 Audit budgets (`scripts/audit.sh`; read-only)

| Metric | Target | Observed 2026-10-21 |
|---|---|---|
| `OPERATING.md` lines | ≤250 | 131, OK |
| `WIP_OPEN.md` bytes | ≤8192 | **8,442, DRIFT** (commit `ab865f0` said it was trimmed; it is not) |
| Merge commits, last 30 | informational (each ≈ one shipping unit) | 30 |
| Close-out conformance | 100% | 25/30 |
| Stranded branches on origin | 0 | 125 non-main heads (see §2.3; the audit prints all of them) |
| Repo size | informational | 288 MB |

Drift is "fixable in a small commit. Don't let them accumulate." Prefer a structural fix (script/check) to a new prose rule (`OPERATING.md` §8: each new rule states the failure it prevents, the structural enforcement or an honest admission of none, and the recovery).

### 2.5 Acceptance criteria (`OPERATING.md` §5)

A change is shipped when: (1) build clean `built=N missing=0 errored=0` with N = layer count in `layers.yaml` (39 now); (2) local↔prod md5 parity on `dist/index.html`; (3) branch merged and deleted in the same session; (4) `audit.sh` clean for drift the change introduced. High blast radius adds: tile-level verification (curl on `/tiles/<id>.pmtiles` 200) and visual verification on prod.

Practical addition from the 2026-10-20 defects: `MISSING` layers do not block `deploy.sh` (only `errored>0` does). Do not deploy from a machine without `data/wells_permian6.csv` and `data/permits_permian6.csv` (see §3.2, §9).

### 2.6 Atomic-write and data-handling conventions

- `os.replace(tmp, final)` in every rewriter (merge, geocode, enrich_*, build_drilling_density, extend_county_labels, edit_* scripts, `refresh_dc_anchors.py`).
- Combined files are the canonical store: `combined_points.csv` (layer_id first; WGS84 6 dp) and `combined_geoms.geojson` (EPSG:4326, 2D; every feature carries `layer_id`, `source`, `source_date`). Standalone files only when size or schema demand it (`ARCHITECTURE.md` §2, §4).
- Tax-abatement column overload is locked (Chat 88): `inr`←permit_no, `funnel_stage`←status, `zone`←received_date, `project`←num_units, `poi`←agenda URL, `operator`←applicant, `commissioned`←meeting_date, `technology`←project_type.
- `coords_source` provenance values: `county_centroid`, `ldad_county_centroid`, `abatement_match`, `substation_match`, `eia860`, `uswtdb`, `tpit_poi`, `substation_poi`, `dc_anchors`, `commissioner_court`, `manual_override`.
- `/*__BUILD_ID__*/` token in `build_template.html` makes every `index.html` byte-unique. `deploy.sh`'s md5 poll depends on it. Never remove.
- `dist/_headers`, `dist/_redirects`, `dist/pmtiles.js` are generated by `build.py`. Never hand-edit.
- `-zg` silently emits a 0-feature tileset for single-feature inputs: use `-Z0 -z14` (`ARCHITECTURE.md` §6).
- Curl against prod needs `-A "Mozilla/5.0"` and GET (HEAD on root returns 503). CDN warm-up 45-90 s.

### 2.7 Settled decisions (`docs/settled.md`, `OPERATING.md` §9, `ARCHITECTURE.md` §11)

Do not re-litigate without strong reason. `docs/settled.md` list, each item:

1. MapLibre + PMTiles + tippecanoe. Not Leaflet, not Mapbox GL JS proper (license).
2. Netlify hosting; "MCP -> CLI proxy deploy path. REST API deprecated for this site." (Conflict: `scripts/deploy.sh` actually POSTs a zip to the Netlify REST API since 2026-05; the MCP helpers in it are dead code. `OPERATING.md` §4 still describes the MCP/npx path. Code wins.)
3. Single-page app, no build framework; hand-edited `build_template.html` with `/*__LAYERS__*/` and `/*__BUILD_ID__*/` substitution.
4. Combined data files with `layer_id` tag; standalone only when size or schema demands.
5. `main` canonical; `refinement-<slug>` feature branches; direct merge, no PRs.
6. Flat repo-root layout.
7. Grid Wire: light theme only, no dark background shading behind text (operator directive 2026-07-21).
8. Grid Wire: crude and natural gas never conflated; water claims district-specific; comps never averaged across entitlement stages.
9. Grid Wire: email drafts are never auto-sent.
10. ERCOT Batch Zero financial security is a $50k/MW non-refundable fee per 16 TAC §25.194, superseding the $100k + $100k stack carried in Series A Vols 19-20.

Further settled items: Netlify Team Pro, link-only access (`ARCHITECTURE.md` §1; moot since 2026-10-20 public); vendored same-origin MapLibre/pmtiles/turf since Chat 27; ERCOT Stage 3 geocode spec (WRatio ≥ 88, name suffix stripping, idempotent, last-precedence, `coords_source = manual_override`, atomic); Match rule for tax-abatement annotation is subset-only (Chat 85).

Scoped-out sources (`ARCHITECTURE.md` §11): `tceq_pws`, `tceq_pbr`, `tceq_nsr_pending`, Comptroller LDAD bulk XLSX (does not exist), per-county fetch at fetch time. `permits_permian6` was scoped out then reclassified in scope 2026-05-13 after the forensic daf420 parse.

### 2.8 Principles (`docs/principles.md`)

Pointer to `OPERATING.md` §3 and `ARCHITECTURE.md`. Restates: never read source data; no `git add -A`; atomic writes; atomic deploy + merge + branch delete; no deploy with `errored>0`; branch from main; verification by blast radius; curl with `-A "Mozilla/5.0"`, 45-90 s warm-up. Grid Wire build pattern: WeasyPrint; Jost instanced to static weights via `fontTools.varLib.instancer`; one `FontConfiguration` passed to both `CSS(font_config=fc)` and `write_pdf(font_config=fc)`; absolute `file://` font URIs; `markdown` with `extras=["extra","tables","sane_lists"]`, smartypants disabled; ASCII email check `LC_ALL=C grep -cP "[^\x00-\x7F]"` = 0.

### 2.9 Content rules for deliverables

**OM set (`docs/redesign_content_brief.md` §0, binding):**

1. No hyperbole or promotional adjectives; technical specificity.
2. Every heading carries a subheading that is a conclusion (specific, numeric where possible).
3. Longfellow / Project Horizon: infrastructure-first. Never mention CoreWeave, its exit, or any tenant-transition. Neutral line only: "phase-1 site work underway."
4. Distances are edge-to-edge: GW Ranch ≈15.5 mi, Longfellow ≈19.3 mi. Older centroid figures (17.3 / 19.7) appear only inside the §4 methodology note.
5. Cite source class for anything not in the GIS data model.
6. Density varies by format, accuracy does not.
- Pre-NDA teaser posture: Caramba North named; Amazon named (public reporting) but its site not; second campus and wind/solar/hydrogen position described without ranch or developer names; use `corridor_prenda_*` exhibits (`scripts/om2/build_teaser_prenda.py` header).
- Do not hand-edit exhibit images; build new ones by script. `exhibit_amz_gwranch.jpg`, `exhibit_longfellow.jpg`, `exhibit_power_gravity_*.png` are "do not regenerate".

**Grid Wire (`docs/grid-wire-master-instructions-v4.md` Parts I, J, L; scheduled-task prompt §3.10):** crude and gas separate; primary sources carry authority; `n/d` for undisclosed, never estimate, derived labeled `derived`; named falsification condition on every major thesis; Waha items cite negative-day count plus egress schedule; water district-specific; every financing gets a full term sheet; every section tests physical vs financed and flags West Texas builds against the LRP map; no em-dashes, no smart quotes; Munger/Burry/Sanders register; no buyback/dividend coverage; no cross-stage comp averaging; no sending the Mel/Mark drafts; never assume volume or baseline from memory.

**OXY dossier editorial rules (`outputs/reports/OXY-REPORT-HANDOFF.md`):** business reader, no jargon (IDs to Appendix D); each section on a new page with a 1-3 sentence JV-angled intro; per-section maps; do not imply false nearness (proximity map plots precise-coordinate assets only); no strategic conclusions; flag undisclosed or mis-stated items in Appendix C.

---

## 3. End-to-end workflows (exact commands)

### 3.1 Setup

```bash
git clone https://github.com/10thMuses/lrp-tx-gis.git && cd lrp-tx-gis
bash scripts/bootstrap-claude-code.sh      # idempotent
```

`bootstrap-claude-code.sh`: installs tippecanoe (brew, or `sudo apt-get install -y tippecanoe`); `pip install --upgrade pyyaml pmtiles requests`; copies `.env.example` to `.env` if missing and warns on empty `GITHUB_PAT` / `NETLIFY_PAT`; sets git identity (`claude@lrp.local`, "Claude (LRP GIS)") if unset; notes Jost font absence; smoke test `import yaml, pmtiles`. Windows: run `scripts/bootstrap-windows.ps1` first (WSL2 Ubuntu preflight).

Gaps the bootstrap does not close (from `docs/OPERATING_MANUAL.md` §5, confirmed by reading `build.py`):

```bash
pip install cairosvg Pillow                       # imported by build.py via build_sprite.py
set -a; . ./.env; set +a                          # build.py does NOT read .env
export LRP_PROJECT_DIR=. LRP_DIST_DIR=./dist LRP_UPLOADS_DIR=./uploads
git config core.hooksPath scripts                 # optional: enables scripts/pre-commit (rejects staged >1 MB unless ALLOW_LARGE=1)
```

`LRP_DIST_DIR` has no repo-root fallback; unset it and the build writes to `/mnt/user-data/outputs/dist`. No `requirements.txt`, `package.json`, or lockfile exist. `scripts/session-open.sh <branch> [handoff-slug]` is the chat-mode alternative (fetches/creates the branch, pushes an empty new branch immediately, prints `docs/_<slug>_handoff.md` if present, prod sanity check; its `apt-get install` has no `sudo`).

Required reading at session start (`CLAUDE.md`): `OPERATING.md`, `ARCHITECTURE.md`, `WIP_OPEN.md`. Grid Wire work: `Readme.md`, then `outputs/reports/GRIDWIRE_LOG.md` `## Next chat`. Resume trigger: `resume.` (clone, read `WIP_OPEN.md` `## Queue`, execute the top unblocked item on a fresh `refinement-<slug>`).

### 3.2 Build (`python3 build.py`)

Reads `layers.yaml` (39 layers), one-pass splits `combined_points.csv` and `combined_geoms.geojson` by `layer_id` into `/tmp/gis_build/split/<id>.ndjson` (hard-coded path), runs `tippecanoe -fo <out> -l <id> <flags>` per layer (serial; `--read-parallel` removed for lock errors), copies prebuilt PMTiles for `rrc_pipelines`, `tiger_highways`, `bts_rail` (tier 1 `$LRP_PROJECT_DIR/<id>.pmtiles`, tier 2 `$LRP_UPLOADS_DIR`, tier 3 live `https://lrp-tx-gis.netlify.app/tiles/<id>.pmtiles`; a first offline build marks them ERROR), writes `dist/data/<layer>.json` stats side-cars (`wells_permian6`, `permits_permian6` only), renders `dist/index.html`, `_headers`, `_redirects`, sprite, vendor files. Prints per-layer status (`OK`/`MISSING`/`ERROR`/`EMPTY`) and `built=N missing=M errored=E tiles_total=… KB`.

Layer-specific build filters (`layers.yaml` keys, implemented in `build.py`):

| Key | Layer | Effect |
|---|---|---|
| `min_spud_year: 1964` | wells_permian6 | drop earlier spuds |
| `exclude_recompletions: true` | wells_permian6 | drop rows with `completion_year < spud_year` (RULE H) |
| `reclassify_inactive_production: true` | wells_permian6 | set `well_status` = Plugged / Marginal or end-of-life / Active via `data/well_prod_status.csv` (API8 join); thresholds `gas ≤ 125 Mcf/d AND oil ≤ 25 bbl/d` (`build.py:609`) |
| `keep_technology` / `keep_county_scope` | tax_abatements | declutter |
| `exclude_within` | (none set now) | even-odd point-in-polygon exclusion (used previously to drop wells inside Caramba) |

Failure modes: missing `data/wells_permian6.csv` / `data/permits_permian6.csv` yields `MISSING` (not `errored`), so `deploy.sh` would proceed and ship a map without those layers and their `dist/data/*.json` (this is the root cause of the 2026-10-20 live defect: stats panel 0, scrubber stuck). `build.py refresh permits` exits 2 with an obsolete "scoped-out" message; use the scripts directly.

### 3.3 Deploy (`scripts/deploy.sh`)

```bash
bash scripts/deploy.sh --rebuild [--site-id <id>] [--dist <path>]    # deployId on stdout, logs on stderr
```

Internals, in order:

1. **Build gate** (if `--rebuild` or `dist/` missing): `python3 build.py > /tmp/build.log`. Refuse (exit 2) on non-zero exit, `errored>0`, absent `^built=N` summary line (guards a prior incident where a YAML error skipped the report and a stale partial `dist/` shipped), or missing `dist/index.html` / `dist/tiles/`.
2. **PAT resolution** (exit 3 if empty): `NETLIFY_PAT=` in `.env`, else `/mnt/project/CREDENTIALS.md`, else shell var `NETLIFY_PAT_ENV`.
3. **Zip + REST POST**: Python `zipfile` of `dist/`, then `POST https://api.netlify.com/api/v1/sites/<siteId>/deploys` (`Authorization: Bearer`, `Content-Type: application/zip`). `deployId` = response `id`. `MCP_URL`/`mcp_call` in the file are unused remnants.
4. **md5-parity poll**: every 5 s up to 300 s, `curl -sI -A "Mozilla/5.0"` root = 200 then GET and md5 compared with local `dist/index.html`. Parity means deploy ready and CDN propagated. Exit 5 on timeout. Relies on `/*__BUILD_ID__*/`.
5. **Layer gate** (`VERIFY_LAYERS=1` default; `0` skips): `python3 scripts/verify_deployed_layers.py --quiet`. For every `layers.yaml` id range-reads `<base>/tiles/<id>.pmtiles` header + tilestats; exit 1 on 404/unreadable/zero count; 2 on harness error. Deploy.sh exits 7 on failure ("do NOT close-out/merge"). The gate runs after publication, so it blocks the merge, not the publish.
6. Echo `deployId`.

Exit codes: 0 ok; 2 build; 3 PAT/API; 4 verify (missing local index); 5 md5 timeout; 7 layer gate.

CI alternative: `.github/workflows/build-and-deploy.yml` (manual `workflow_dispatch`; apt tippecanoe; `netlify deploy --prod` with `NETLIFY_AUTH_TOKEN` + `NETLIFY_SITE_ID`). Never run (verified 2026-10-20). Lacks the md5 and layer gates and cannot build the RRC layers (gitignored CSVs).

Alternate deploy path used 2026-10-20 (not a scripted workflow): Netlify MCP proxy from a mirrored file set; it omitted `_headers` and `_redirects`, so live tiles serve `max-age=0` without CORS and SPA fallback is absent (verified 2026-10-20). The next full `build.py` deploy restores both (`write_netlify_config`).

### 3.4 Close-out and atomic ship

```bash
bash scripts/close-out.sh refinement-<slug> <deploy-id|none> "<title>"
bash scripts/ship.sh refinement-<slug> "<title>" -- --rebuild        # deploy.sh then close-out.sh
```

`close-out.sh` sequence: require HEAD on `<branch>` (exit 3); commit pending `WIP_OPEN.md` edits ("WIP_OPEN.md: handoff to next chat"); refuse any other uncommitted tracked change (exit 3); `git push origin <branch>`; require ≥1 non-handoff commit on `origin/<branch>` beyond `origin/main` (exit 4, "recon-only chat"); remove `docs/_<slug>_handoff.md` if present; `checkout main`; `pull --rebase origin main`; `merge --no-ff origin/<branch>` with message `Merge <branch>: <title> (deploy <id>|no deploy)` (exit 5 on conflict); `push origin main` (exit 6 on rejection); `push origin --delete <branch>` (warn only on failure). Local branch is not deleted.

Doc-only work: `none` as deploy-id. `WIP_OPEN.md` "Last deploy" block is updated as the final action (budget 8,192 bytes).

### 3.5 Single-layer refresh and merge

```bash
python3 build.py merge <layer_id> <refresh_file>      # atomic swap of that layer's rows/features in the combined file
git add combined_points.csv                           # or combined_geoms.geojson
git commit -m "refresh: <layer_id> from <source> <date>"
```

The layer must already exist in `layers.yaml`; new columns are appended to the union header; CSV is forced to LF. The merge does not rebuild tiles. Rebuild and deploy are separate steps.

Adding a layer (`ARCHITECTURE.md` §6, `docs/OPERATING_MANUAL.md` §7 runbook 2): produce a documented-source refresh file, add the `layers.yaml` entry first (`id,file,geom,group,label,color,default_on,popup,min_zoom,tippecanoe`; group must be in `GROUP_ORDER`), merge or place standalone (≥10 MB: prebuilt PMTiles), build, expect `built=N+1 missing=0 errored=0`, stage explicit paths, deploy, curl `/tiles/<id>.pmtiles`, close out, update `ARCHITECTURE.md` §5 catalog.

### 3.6 RRC wells and permits refresh

```bash
python3 build.py refresh wells                 # = fetch_rrc.py wells + parse_rrc.py wells
python3 build.py                               # rebuild PMTiles

python3 scripts/fetch_rrc.py permits           # all EOM+LatLon monthly snapshots (daf420)
python3 scripts/parse_rrc.py permits           # 6-county filter -> data/permits_permian6.csv
python3 build.py
```

- `fetch_rrc.py` protocol (GoAnywhere PrimeFaces): GET `https://mft.rrc.texas.gov/link/<UUID>` landing, harvest `JSESSIONID` + `javax.faces.ViewState`, POST `/webclient/godrive/PublicGoDrive.xhtml` with `fileTable:<row>:j_id_2f`, stream to `data/rrc_raw/` via atomic temp+replace. 1.5 s throttle. Targets `wells | permits | pending | all`; flags `--force`, `--limit`. Folder UUIDs: wells `b070ce28-…` (`dbf900.txt.gz`, ~366 MB, ~1.97 GB uncompressed); permits `f5dfea9c-…`; pending `0ad92a65-…`. The most recent monthly permit snapshots are not in folder-tail order; pull by parsed date (`WIP_OPEN.md`).
- `parse_rrc.py {wells|permits|all}`: segment-aware streaming parser of `dbf900` (247-byte records; segments 01 WBROOT, 02 WBCOMPL, 13 WBNEWLOC; lon forced negative). 6-county scope by API county code: 317 Martin, 329 Midland, 371 Pecos, 383 Reagan, 389 Reeves, 475 Ward. Permits: `daf420` records `0108`/`0208`/`14`/`15` (`0109` from 2024). Auto-merges `outputs/refresh/rrc_w1_permits_with_coords.csv` (dedupe permit_no + api_no) if present. Layouts: `docs/rrc_layouts/` (`wba091_well-bore-database.pdf`, `pendingdrillingpermits.pdf`, `permit_purpose_codes.md`).
- Outputs `data/wells_permian6.csv` and `data/permits_permian6.csv` and `data/rrc_raw/` are gitignored. Last full production values: wells 99,224 (deploy 2026-06-23) vs 99,808 re-parsed 2026-08-19 (not deployed); permits 28,842.
- Oil/gas production status (feeds Marginal/EOL): `python3 scripts/fetch_pdq_dump.py` (PDQ_DSV.zip, ~3.44 GB, MFT `1f5ddb8d-…`, monthly, last Saturday) → `python3 scripts/build_lease_status.py` (`data/lease_status.csv`, trailing 6-month per lease) → `python3 scripts/build_well_prod_status.py` (`data/well_prod_status.csv` API8-keyed via `OG_WELL_COMPLETION_DATA_TABLE`; ~99.6% match). Note `build_lease_status.py` docstring still says oil < 150 bbl/d; its own gate is gas-only, the oil 25 bbl/d guard lives in `build.py`.
- OXY permits layer: `python3 scripts/fetch_rrc.py permits` then `python3 scripts/build_oxy_drilling_permits.py` → `data/oxy/oxy_drilling_permits.geojson` (OXY operator regex; dual `0108`/`0109` format reader; 294 permits 2020-2026).
- `build.py refresh permits` is wired to exit 2. Ignore.

### 3.7 Permits 1976-2004 backfill (overnight)

```bash
for c in PECOS REEVES WARD MIDLAND MARTIN REAGAN; do
  python3 scripts/scrape_rrc_w1.py "$c" 1976 2004
done
nohup python3 scripts/scrape_rrc_w1_detail_coords.py \
  --in outputs/refresh/rrc_w1_permits.csv \
  --out outputs/refresh/rrc_w1_permits_with_coords.csv \
  > /tmp/rrc_w1_coords.log 2>&1 &
# when complete:
python3 scripts/parse_rrc.py permits && python3 build.py
```

Source `https://webapps.rrc.state.tx.us/DP/initializePublicQueryAction.do` (JSP, cookie-bound session; falls back to monthly chunks above the record cap; checkpoints in `outputs/refresh/rrc_w1_checkpoint.json` and `rrc_w1_coords_checkpoint.json`; resumable). ~7 h detail scrape at 1.5 s. Scratch (`outputs/refresh/rrc_w1_*`) is gitignored so the unattended routine cannot commit it. Range inconsistency: `CLAUDE.md` says 1976-2004; `WIP_OPEN.md` and the R26 history say 1976-2017. Completion status Not documented in repo (scratch files absent). `scrape_rrc_w1.py counts` produces `rrc_w1_counts.csv` for `build_drilling_density.py`.

### 3.8 ERCOT queue geocoding

There is **no fetch script** for the ERCOT GIS Report (xlsx, monthly) or TPIT. Both are manual snapshots (queue March/April 2026; TPIT April 2026).

```bash
python3 scripts/geocode_ercot_queue.py          # Stage 1 + 2, in-place atomic rewrite of combined_points.csv, appends outputs/refresh/_geocode_ercot_log.txt
python3 scripts/enrich_ercot_coords.py          # abatement cross-reference -> coords_source=abatement_match
python3 scripts/enrich_ercot_substation_match.py # POI substation text -> OSM substations (coords_source=substation_match; 30 mi sanity gate; token filters)
```

- Stage 1: `eia860`, `uswtdb` fuzzy name+county. Stage 2: `tpit_poi`, `substation_poi` (WRatio ≥ 88, county via TIGER 2024 point-in-polygon), `dc_anchors` alias match. Later stages touch only rows still at `county_centroid`.
- Hard-coded inputs: `outputs/refresh/eia860_plants_2026-04-25.csv`, `eia860_battery_2026-04-25.csv`, `wind_2026-04-25.csv`; TIGER zip auto-fetch to `outputs/refresh/tl_2024_us_county.zip` (gitignored). From cloud egress Census returns an HTML block page stored as a zip, causing `zipfile.BadZipFile` (daily report 2026-08-19).
- **Stage 3 (manual override) is specified in `WIP_OPEN.md` but not implemented.** `scripts/geocode_ercot_queue.py` has no `--stage` flag, no override read, and no reference to `data/ercot_queue_overrides.csv` (verified by grep 2026-10-21). The override CSV is operator-curated and absent. Spec: WRatio ≥ 88; suffix stripping (LLC, INC, LP, LTD, CORP, CO, trailing project codes); idempotent; last precedence; `coords_source = manual_override`; atomic. Acceptance: override rows in registry equal CSV rows; aggregate solar+wind+battery match improved vs Stage 2; no regression in Stage 1+2. Remaining imprecise rows need FERC EQR + PUC CCN lookups (~33 per R26; 4-8 h manual).

### 3.9 Abatements scrape

```bash
python3 scripts/scrape_ldad.py                    # Comptroller open-data API -> outputs/refresh/comptroller_ldad_<date>.csv
python3 scripts/transform_ldad.py [refresh.csv]   # merges LDAD + data/abatements_court_seed.csv into combined_points.csv
python3 scripts/scrape_abatements.py [outdir]     # probe: commissioners-court agendas -> data/abatements/abatement_hits_<ts>.csv (diagnostic)
python3 scripts/transform_abatements.py           # one-off: pinned snapshot abatement_hits_20260424_092810.csv -> layer rows + layers.yaml patch (idempotent)
```

- LDAD endpoint: `https://api.comptroller.texas.gov/open-data/v1/tables/ch312-abatement?limit=10000` (single call; `offset` returns 500). Only 5 in-scope records, all Pecos County commissioners-court Ch.381; 0 Ch.312 records in the 6-county scope; no second layer created.
- `transform_ldad.py` drops only `ldad_county_centroid` rows, preserves `commissioner_court` seed rows (9 Pecos/Reeves), coerces `1900-01-01` placeholder dates to blank.
- Agenda scraper: 23 counties, filings 2025-2026, dedupe `(county, applicant_normalized, reinvestment_zone)`. Adapters validated for Pecos (WordPress, `co.pecos.tx.us`) and Reeves (CivicEngage, `reevescounty.org`); 21 counties are stubs (`unverified_source`). Reeves is blocked by Akamai from datacenter egress; Pecos works. UA `LRP-Abatement-Scraper/1.0`.
- Daily probe outputs (`data/abatements/abatement_hits_*.csv`) are gitignored except the pinned snapshot; layer is fed only by the pinned snapshot via `transform_abatements.py` plus LDAD. The weekly agenda refresh is "configured, not yet in production" (`scripts/om2/build_om_master.py` footnote b).

### 3.10 DC anchors refresh (LLM-in-the-loop)

- Workflow `.github/workflows/dc-anchors-refresh.yml`: Mondays 06:00 UTC + `workflow_dispatch`; Python 3.11; runs `python3 scripts/refresh_dc_anchors.py` with secret `ANTHROPIC_API_KEY`; counts "meaningful" proposals (`diff`, `additional_sources`, `conflicts`, `parse_error`, `error`); if any, `peter-evans/create-pull-request@v6` (token `GITHUB_TOKEN`) opens branch `dc-anchors-refresh-<run_number>` with only `outputs/refresh/dc_anchors_proposed.json`. Review checklist in PR body: "Never merge this PR as-is."
- Script: reads `data/datacenters/dc_anchors.json` (8 entries, `generated: 2026-04-25`), fetches each entry's source URLs (30 s timeout, 3 attempts, 200,000-byte read cap, 30,000 chars per page to the model), calls Anthropic Messages API (raw `urllib`, `anthropic-version: 2023-06-01`, model `claude-sonnet-4-5-20250929`, `max_tokens=2000`, 3 attempts with `5 s × attempt` backoff, 401 fails fast). System prompt forbids proposing coordinate, county, name, or developer changes; only `status`, `capacity_mw_announced`, `commissioned_target`, `power_source`, `additional_sources`; every diff must carry `evidence_url` and a ≤25-word `evidence_quote`.
- Local test: `ANTHROPIC_API_KEY=… python3 scripts/refresh_dc_anchors.py [entry-id]`. Do not commit the proposal file.
- Apply a proposal by hand-editing `data/datacenters/dc_anchors.json` and its `generated` date, rebuild, deploy. Adding a **new** anchor (Chevron WTPP, TPL+Bolt, LandBridge Alpha Digital, Longfellow cluster) is not something the script can do, and coordinates may not be hand-coded (rule 3); a sourced intake path is an open decision (§9).
- State 2026-10-20: workflow succeeds weekly; ~14 unmerged proposal PRs (22 `dc-anchors-refresh-*` branches observed).
- Other CI: none. The proposed `weekly-refresh.yml` (`docs/refresh_automation_plan.md`) was never written.

### 3.11 Other layer refreshes

| Layer | Command | Notes |
|---|---|---|
| eia860_plants, eia860_battery, solar | `python3 scripts/refresh_eia860.py [--year 2025] [--out outputs/refresh]` then `build.py merge` | Requires `Referer: https://www.eia.gov/electricity/data/eia860/` and UA. Default `--year 2024`. 2025 vintage released 2026-09-10: `--year 2025` is a one-arg change. Capacity from Generator sheet grouped by Plant Code, `Status == 'OP'`. |
| wind | `python3 scripts/refresh_uswtdb.py` | `https://eersc.usgs.gov/api/uswtdb/v1/turbines` (PostgREST, `t_state=eq.TX`, paginated by `case_id`). Upstream cert expired (verified 2026-10-20); do not disable TLS; use USWTDB V9.1 file release + `build.py merge wind`. |
| tceq_gas_turbines | `python3 scripts/refresh_tceq_gas_turbines.py` | `turbine-lst.xlsx`; 23-county scope, received ≥2020; Nominatim geocode; log in `outputs/refresh/CHANGELOG.md`. Source updated 2026-10-12. |
| fcc_fiber_coverage | `python3 scripts/refresh_fcc_fiber_coverage.py` | Not in `layers.yaml` now. |
| hifld_* (4) | `python3 scripts/fetch_hifld.py <slug> <FeatureServer URL>` | bbox `-104.0,30.0,-101.0,32.6`; output `data/hifld/<slug>.geojson`. |
| county_labels | `python3 scripts/extend_county_labels.py` | Census TIGER 2024 county zip; one-off. |
| substations | no script (OSM Overpass, in-chat) | |
| transmission | no script (HIFLD hand-merged) | ≥100 kV cutoff only. |
| oxy_* (6 + permits) | `python3 scripts/build_oxy_assets.py` then `python3 scripts/build_oxy_map_layers.py` | All coordinates extracted from sourced layers; a few county-centroid placements flagged `accuracy="approximate (county centroid)"`. |

### 3.12 Caramba North OM, teaser, deck builds

**Two lineages exist. Use lineage 2 (om2) for the current buyer set; lineage 1's data model is the only one that derives numbers at build time.**

**Lineage 1: data-derived (2026-08-19 to 08-24; superseded for distribution)**

```bash
python3 scripts/caramba_om_data.py --json /tmp/om_model.json    # inspect derived model
python3 scripts/capture_om_exhibits.py                           # needs unblocked network + Playwright; optional
python3 scripts/build_caramba_om.py                              # -> Caramba-North-OM-PostNDA.pdf (25 pp)
python3 scripts/build_caramba_om.py --no-flags                   # suppress disclosure boxes
node scripts/build_caramba_om_docx.js                            # editable Word (shells caramba_om_data.py --json)
node scripts/build_caramba_om_pptx.js                            # condensed summary deck
```

`caramba_om_data.py` derives Sections 3, 4, 7, 9 from `combined_points.csv`, `combined_geoms.geojson`, `data/wells_permian6.csv` (+ `wells_howard_loving.csv`), `data/well_prod_status.csv`, `data/fracfocus/DisclosureList_1.csv`, `data/datacenters/dc_anchors.json`. Only declared hand values (`CONFIG`): acreage 1,300, water 47,418 AF/yr, Solstice 15 mi, Waha 20 mi, gas quote terms, adjacent and peer county lists, thresholds. `build_caramba_om.py` renders HTML then headless Chromium print (candidate paths include `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`); intermediate `Caramba-North-OM-PostNDA.html` is gitignored. Rebuild notes: `outputs/reports/CARAMBA-OM-REBUILD-NOTES.md`.

**Lineage 1b: first-pass redesign (2026-08-24 `2dd2391`; design rejected, kept as legacy)**: `node scripts/build_deck_{institutional,editorial,mapled,minimalist}.js` (pptx) and `python3 scripts/build_brief_{executive,technical}.py` (docx). Inputs: `caramba_om_data.py`, `build_insight_pack.py`, raster exhibits (`build_amz_gwranch_exhibit.py`, `build_longfellow_exhibit.py`, `build_exhibit_7_1_masked.py`, `build_pipeline5_annotated_exhibit.py`, `build_minimalist_exhibit_crops.py`, `build_power_gravity_diagram.py`), icons (`node scripts/render_icon_set.js`). Facts source: `docs/redesign_content_brief.md`.

**Lineage 2: vector + type system (2026-08-24 `2bec838` onward; current)**

```bash
python3 scripts/extract_map_geometry.py --out outputs/reports/om_exhibits/map_geometry.json   # real layer geometry, clipped to a bbox around the tract
python3 scripts/build_vector_maps.py                    # SVGs -> outputs/reports/om_exhibits/vector/
python3 scripts/om2/om_charts.py                        # chart SVGs (rings, peer drilling, queue growth, maturity, power mix)
python3 scripts/om2/build_om_master.py                  # Caramba-North-OM.{html,pdf} + Caramba-North-OM-Appendix-A.{html,pdf}
python3 scripts/om2/build_teaser_prenda.py              # Caramba-North-Teaser-PreNDA.{html,pdf}
python3 scripts/om2/build_deck_{institutional,editorial,technical,minimal}.py
python3 scripts/om2/build_brief_exec.py ; python3 scripts/om2/build_brief_technical.py
```

HTML→PDF: `om_theme.render_pdf` runs `node scripts/om2/_print.mjs <html> <pdf>` (Playwright, `executablePath: '/opt/pw-browsers/chromium'`, a symlink to `chromium-1194/chrome-linux/chrome`, fonts embedded as base64 `@font-face`). Needs `scripts/om2/node_modules` (gitignored; must contain `playwright`; "symlinked in" per `.gitignore`). `build_om_master.py` imports `build_deck_institutional` and `build_deck_technical` and recomposes: Part I (institutional, renumbered, with Minimal-style statement pages) and Appendix A (technical sheets A-01..A-15; A-14 platform access, A-15 source register). Type systems in `om_theme.SYSTEMS`: institutional (Newsreader / Public Sans / IBM Plex Mono, `#FBFAF7`), editorial (Instrument Serif / IBM Plex Sans, dark `#0E141A`), technical (IBM Plex Sans, `#F4F6F7`), minimal (Archivo, white). Red `#B03A2E` reserved for the subject site and the two feature anchors. QA checklist: `docs/redesign_content_brief.md` §13 (pdfinfo page count and size; `pdftoppm -jpeg -r 100` and view every page; grep for TODO/Lorem/XXX; no CoreWeave or tenant mention; distances 15.5 / 19.3 only).

**Critical difference:** lineage 2 builders hard-code the figures (e.g. `om_charts.py` `RINGS = [(15,0.48),(30,8.9),(60,32.72),(100,53.5)]`, `QUEUE = 63/226/474`; `build_om_master.py` and `build_deck_institutional.py` carry 3,226 MW, 12,039 MW, 47,418, 1,181 as text). They are typed from `docs/redesign_content_brief.md` and do not recompute from layer data, so a data refresh does not flow into the current OM set. Rebuilding lineage 2 after a data refresh requires editing the brief and the builders by hand, or wiring `caramba_om_data.py` / `build_insight_pack.py` into them (not done; open item).

`capture_om_exhibits.py`: Playwright against the live map (`LRP_GIS_URL`, default prod), builds per-exhibit hash URLs (`layers`, `base`, `sb=1`), injects coordinate-anchored annotations via `map.project()`, writes JPGs and `manifest.json`. It still waits 8 s for `#oxy-gate-form` and fills the login with `LRP_GIS_EMAIL`/`LRP_GIS_PASSWORD`, whose **defaults are hard-coded in source (lines 26-27; values not reproduced)**. The gate no longer exists. It sets `proxy` from `HTTPS_PROXY` and launches without `executable_path`. Last real captures are 2026-07-06 (extracted from the July v4 PDF); exhibits in `om_exhibits/` were never recaptured from current layer state.

### 3.13 Drilling/vibration memo (analysis pipeline)

Scripts in `outputs/reports/` (hard-coded `/home/andreahimmel/lrp-tx-gis` paths; adjust before use): `pecos_lock.py` (locks RULE H numbers), `pecos_canon2.py` (RULE H vs RULE W comparison), `pecos_canonical.py` (W-1 "New Drill" filter; the earlier definition), `pecos_vs_peers.py`, `howard_loving_extract.py` (uses `parse_rrc.py` to pull Howard FIPS 227 + Loving 301 from `dbf900`), `v22_analysis.py` + `v22_charts.py` (recompletion ratio, spud-decade, status mix; chart PNGs in `outputs/reports/charts/`), `finding9_numbers.py` (reads `/tmp/gis_build/split/wells_permian6.ndjson`, so a build must have run), `fracfocus_caramba.py` + `fracfocus_new_drill_only.py`, `prod_reclass_numbers.py` (150 bbl/d; superseded by 25), `make_docx.py` (memo .docx), `make_emails_docx.py` (renders `buyer-email.md`, `owner-email.md` to .docx). The `.md` is the source of truth; `.docx` is generated.

### 3.14 Grid Wire volume production

Per cut (`docs/grid-wire-master-instructions-v4.md`, `docs/grid-wire-scheduled-task-prompt.md`):

1. Clone repo (PAT from `CREDENTIALS.md`); read `Readme.md`, master instructions, taxonomy (23 domains / 147 sub-domains; E = every cut, T = trigger), then `outputs/reports/GRIDWIRE_LOG.md` `## Next chat`. Volume number, slot, baseline from the log, never memory. Scheduled-prompt variant: state from the newest Google Drive `GRIDWIRE_STATE_*` file (Drive wins on numbering and ledger counts; repo log is a cross-check).
2. Preflight gates (scheduled prompt Step 0): Drive spec read, state file, Jost instances, WeasyPrint + fontTools, `pdftotext`/`pdffonts`/`pdftoppm`, Resend key, repo access.
3. Sweep primary sources first (EDGAR, EIA, RRC, TCEQ, PUCT/ERCOT, FERC, GCD agendas, courts, county records, IR), trade press as flagged data points. Six-county board every cut (Reeves, Pecos, Ward, Upton, Crane, Crockett; the scheduled prompt extends to 17 counties plus peers) with the Reeves-Pecos convergence deep dive.
4. Maintain trackers D1-D6 (litigation, deal ledger, credit register, docket tracker, physical constraints, calendar) and credit spec G1-G6.
5. Build: markdown source with markers (`TOPLINE_START/END`, `STATS:`, `CLOCKS:`, `KICKER:`, `<<<ANGLE`, `<<<GOLD`, `<<<FALSIFY`) → `markdown` → WeasyPrint (Jost 400/500/600/700; light theme; body ≥11.5 pt, tables ≥10 pt, left-aligned; gold square CSS bullets, never a glyph). Filename `Grid_Wire_Vol{N}_{YYYYMMDD}_{H}{am|pm}_ET.pdf` (repo convention) or `The-Grid-Wire-Vol{N}-{YYYY-MM-DD}-morning.pdf` (scheduled prompt). Length unconstrained.
6. QA gates: zero marker leakage, "page x of y" footer, zero em-dash/en-dash/curly quotes, Jost embedded in all four weights, page-1 and body-page render, type floor, every section has kicker + Angle + falsification condition.
7. Send (scheduled routine): POST to `https://api.resend.com/emails` from Python with a browser User-Agent (default urllib UA is Cloudflare-blocked, HTTP 403 code 1010); from `The Grid Wire <gridwire@10thmuses.com>` to `andrea@abhcm.com`; key `RESEND_API_KEY` read from Netlify env vars of a separate site (siteId in the prompt file); do not use the Resend MCP; never echo the key.
8. Emails: two plain-ASCII drafts (Mel, Mark), draft-only. NFKD → ASCII → assert; `LC_ALL=C grep -cP "[^\x00-\x7F]"` = 0.
9. Close (Part K): append entry to `GRIDWIRE_LOG.md`, rewrite `## Next chat`, commit the edition markdown source and build script to `outputs/reports/source/` in the same push (explicit paths). Write a new append-only `GRIDWIRE_STATE_{date}_morning` Drive file.
- Builders `outputs/reports/source/build_pdf14.py`, `build_pdf21.py`, `make_emails_vol14.py` and `special/crusoe-20260922/build.py` hard-code chat-mode paths (`/home/claude/...`, `/mnt/user-data/outputs/...`); they need path edits to run here.
- Series B Vol 13 (2026-08-19) source was produced in a Teams account and is not in the repo (flagged "recover or rebuild" in the log at Vols 13 and 14). Vols 15+ are Not documented in repo.

### 3.15 OXY report

```bash
python3 scripts/oxy_build_maps.py        # 6 PNGs + oxy_map_keys.json in outputs/reports/
python3 scripts/build_oxy_report.py      # outputs/reports/oxy-intelligence-report.html
python3 -c "from weasyprint import HTML; HTML('outputs/reports/oxy-intelligence-report.html').write_pdf('outputs/reports/OXY-Intelligence-Report.pdf')"
python3 scripts/build_oxy_docx.py        # pandoc -> OXY-Intelligence-Report.docx
python3 scripts/build_oxy_deck.py        # oxy-partnership-deck.html (PDF rendered separately)
```

Asset cards are edited in `scripts/oxy_assets_data.py` (single source of truth for maps and prose). Dependencies: matplotlib, weasyprint, pyshp, python-docx, pandoc on PATH; Inter font loads from a CDN at render time. Geo inputs: `combined_geoms.geojson` (counties), `data/tiger/primary_roads_wtx.geojson`, `data/hifld/*.geojson`, `combined_points.csv` (cities). Full handoff: `outputs/reports/OXY-REPORT-HANDOFF.md`; source bundle `OXY-report-source.zip`. Key caveats (Appendix C): NET Power Odessa is 80 MW (not 300); the 453 MW TRIFECTA queue project was withdrawn Apr 2026; no named hyperscaler on NET Power; OXY's WES stake ~39.5%; OXY does not own the Cortez CO2 pipeline; OxyChem cogens left with the Berkshire sale (Jan 2026).

---

## 4. Analytical methodologies

All definitions were "locked" in the May 2026 study (`outputs/reports/pecos_lock.py`) and inherited unchanged by `scripts/caramba_om_data.py` (`CONFIG` and `is_new_drill`) and the map filter (`build.py` `_filter_exclude_recompletions`).

| Rule | Definition | Where implemented |
|---|---|---|
| **RULE H, genuine new drill** | `completion_year` blank OR `completion_year >= spud_year` (and a spud year exists). A completion that precedes its spud is an old wellbore re-stamped by recompletion/re-entry. County-uniform; buyer-reproducible from the public wells file alone; also the map filter. | `outputs/reports/pecos_canon2.py`, `pecos_lock.py`; `scripts/caramba_om_data.py:333-338` `is_new_drill`; `build.py:575-605`; `layers.yaml` `exclude_recompletions: true` |
| RULE W (alternative) | Authoritative W-1 `filing_purpose = New Drill` for the API. Pecos-only (needs W-1 scrape). | `outputs/reports/pecos_canon2.py`, `pecos_canonical.py`. Superseded by RULE H as canonical. |
| Shallow | `total_depth < 3000` ft | `CONFIG["shallow_ft"]`. Note the W-1 profile field, not depth, is the authoritative vertical/horizontal marker (`pecos_w1_profile.py`: modern Pecos permits ~87% horizontal; depth is a poor orientation proxy). |
| Marginal / end-of-life (EOL) | Not plugged AND lease trailing-6-month average ≤ 125 Mcf/d gas AND ≤ 25 bbl/d oil. Join by API8 through the RRC API-to-lease crosswalk (~99.6% coverage; ~0.4% unmatched stay "Active"). Earlier 150 bbl/d cutoff judged too loose and replaced by 25 on the owner's advisor's direction. | `build.py:608-667`; `scripts/build_lease_status.py`, `build_well_prod_status.py`; `CONFIG["marginal_*"]` |
| FracFocus new-drill frack window | A disclosure matched by API10 to the wellbore record is "new-drill" iff job year is within −1 to +2 yr of EITHER the wellbore completion year OR its spud year. "Re-frac" if >2 yr after spud, or outside the completion window. Robust to RRC re-stamping because it checks both years. | `scripts/caramba_om_data.py:560-640`; `outputs/reports/fracfocus_new_drill_only.py` (older rule: completion_year ≥ spud_year AND job within ~24 months of spud) |
| Distance basis (drilling) | Straight line from the tract centroid (~30.9032 N, 102.9747 W), 69 mi per degree latitude with cos(lat) for longitude. Rings: ≤2, ≤5, ≤10, (>10; 10-20 for FracFocus). | `caramba_om_data.py` `miles()`; memo scripts |
| Distance basis (anchors) | **Edge-to-edge**: nearest point on the tract boundary to the site. GW Ranch 15.5 mi (centroid 17.3); Longfellow 19.3 mi (centroid 19.7). Do not shorten Longfellow; its own site says ">25 miles outside Fort Stockton". | `scripts/build_insight_pack.py` `boundary_distance_mi`; brief §4 |
| Peer-county comparison | New-drill wells since 2020 on the RULE H basis. Pecos vs six peers: Reagan, Howard, Reeves, Loving, Midland, Martin (OM `CONFIG["peer_counties"]`; the map's original peer set was Midland/Martin/Reagan and subject set Pecos/Reeves/Ward). Howard (FIPS 227) and Loving (301) pulled from full `dbf900` via `howard_loving_extract.py`, saved to static `data/wells_howard_loving.csv` (not refreshed with RRC). Peer average = mean of the six. | `pecos_vs_peers.py`; `caramba_om_data.py` `section9`; `docs/redesign_content_brief.md` §2.8 |
| Radius rings (power) | Cumulative operating (EIA-860, plant-level, OP) + ERCOT queue capacity region-wide (not county-bounded) at 15/30/60/100 mi from the tract centroid. 0.5 / 8.9 / 32.7 / 53.5 GW. | `scripts/build_insight_pack.py` `ring_analysis`; `om2/om_charts.py` (hard-coded) |
| Queue-by-radius | Pecos queue 12,039 MW / 39 projects is the **county** figure; the true within-20-mi figure is **13 projects / 3,973 MW**. July v4 mislabeled the county figure as within 20 miles. Adjacent six counties (Reeves, Crane, Ward, Upton, Ector, Crockett): 24,585 MW queued, 7,022 MW operating. | `CARAMBA-OM-REBUILD-NOTES.md` §5a; brief §2.3 |
| Operating basis | EIA-860 plant record for all operating-fleet figures (Pecos wind 5 plants / 542 MW), not USWTDB turbine rollup (8 projects / 653 MW). Pecos operating total 3.4 GW (v4) → 3.2 GW (rebuild). | `CARAMBA-OM-REBUILD-NOTES.md` §4 |
| Project maturity | Share of announced capacity that is under construction among local anchors: 79.3% (GW Ranch) vs 20.7% (Longfellow phase-1/planned). Depends on `dc_anchors.json` having only two entries within 60 mi. | `build_insight_pack.py`; brief §2.6 |

### 4.1 The 9.7 GW vs ~25 GW catchment issue

- OM §7 (rebuild) headline: **9.7 GW within 60 mi** (`caramba_om_data.section7`, `LOCAL_MI = 60`, sum of `capacity_mw_announced` for `dc_anchors` entries within 60 mi). July v4 said "more than 25 GW of announced data-center capacity in the immediate catchment."
- Cause: `data/datacenters/dc_anchors.json` has 8 entries, only 2 within 60 mi (GW Ranch 7.65 GW + Project Horizon 2 GW = 9.65 GW), compiled 2026-04-25. v4's table had four more regional projects with no record behind them (Chevron / Engine No. 1 West Texas Power Plant, TPL + Bolt JV, LandBridge Alpha Digital Campus, Longfellow solar/wind/BESS cluster); they also appear as labels on Exhibit 7.1 (`exhibit_7_1_datacenter-pipeline.jpg`) with no data row. They were not added because adding them by hand violates rule 3.
- How the ~15 GW gap breaks down by project: Not documented in repo (only Chevron ~$7B / 2.5 GW appears in the OXY brief; Alpha Digital "up to 2 GW" and Kilby ~2.67 GW in `GRIDWIRE_LOG.md` Vol 14). Reconcile before restating either number.
- Two incompatible "regional" numbers coexist in the current OM set: 9.7 GW (DC anchors, data-derived, lineage 1) and 32.7 GW (operating + ERCOT queue within 60 mi, power-gravity ring, lineage 2, hard-coded). They measure different things; label them as such. A smoke-test string in `scripts/om2/_smoke.py` says "9.7 GW … inside 20 miles", which is a wrong radius.
- Fix path: refresh/extend `dc_anchors.json` through a sourced process (the weekly LLM proposer cannot add entries), then rebuild lineage 1 and re-wire lineage 2.

### 4.2 RULE H boundary-case open decision

- RRC re-stamped the two 2025 Mongoose Energy "Viper" wells (6.94 and 6.95 mi from the tract) to `spud_year 2026`, `completion_year 2025`. RULE H excludes them literally. New-drill wells within 10 mi fell from 3 (July v4, nearest 6.9 mi) to **1** (nearest 9.37 mi) in the 2026-08-19 rebuild.
- Rule left unchanged ("changing a locked classification to preserve a headline is the wrong move"). The OM §9.4 carries a classification note listing the three boundary cases (6.94, 6.95, 9.23 mi) with spud/completion years. (The note says 9.23 mi for the third; the other prose says a 2020 well at 9.37 mi. Check the rendered note against `section9` before citing.)
- **Open decision (operator):** amend RULE H to treat `spud_year − completion_year <= 1` as a paperwork boundary, not a re-stamp. That would restore the count to 4 within 10 mi, is arguably more faithful to the rule's intent, but changes a locked definition and also changes the map filter (`build.py` `_filter_exclude_recompletions`, `layers.yaml` `exclude_recompletions`), `is_new_drill`, and every downstream deliverable. `CARAMBA-OM-REBUILD-NOTES.md` §3; `WIP_OPEN.md` backlog item 3.
- The buyer memo and both emails still carry the July-vintage numbers (3 within 10 mi; 117 of 1,118 events; 291 non-plugged; peer avg 1,148). August values: 115 of 1,140; 298; avg 1,181; 1 within 10 mi; FracFocus 950 disclosures, 0/9/19/452 fracks by ring, 480 within 20 mi. The memo date (2026-05-19) and its numbers are not refreshed. Re-issue or footnote before re-sending.

### 4.3 Other methodological notes

- Recompletion finding (memo Finding 2): ~10% of Pecos wellbore events since 2020 are genuine new drilling; ~90% are recompletion/workover, mostly Kinder Morgan Production reworking CO2-flood fields. An earlier draft said "~50% shallow", corrected after tracing `dbf900`.
- Production join: an earlier lease-name match covered ~31% of wells and produced a spurious "none producing within 10 mi"; replaced by the API8 crosswalk (~99.6%).
- Wells layer scope: all wells including plugged/abandoned (99,224 as of R26 P1, `plug_flag` filter exposed); `permits_permian6` is 2018-present from `daf420` (EOM + lat/lon); pre-2018 needs the W-1 detail scrape; the time scrubber keys on `spud_year` / `permit_year`.
- Hanwha thesis numbers from PDQ (R26 P5): peer/subject oil ratio 3.02x (2022), 3.34x (2024), 4.14x (2026 YTD).
- Tax abatement leading-indicator hierarchy and regulatory context (`docs/archive/refinement-abatement-spec-2026-04.md`): Ch.313 expired 2022-12-31; Ch.403/JETI (2024-01-01) excludes renewables; Ch.312 and Ch.381 are active; Tax Code §312.207(d) requires ≥30 days public notice, so commissioners-court agendas are the earliest public committed-capital signal.
- ERCOT regulation anchors used in Grid Wire: Project 58481 large-load rule (all loads ≥75 MW regardless of BTM; $50k/MW at IA execution), Project 59142 (good-cause exceptions), Batch Zero. Series B Vol 14 falsified the "BTM regulatory moat" as a categorical claim.

---

## 5. Script registry

Status key: **A** active (used by a current workflow), **L** legacy (superseded lineage or obsolete but retained), **1x** one-off edit/ingest script (historical, idempotent or already applied). "Hard-coded" notes record path or credential hazards.

### 5.1 Root

| Script | Purpose | Inputs | Outputs | External endpoints | Status |
|---|---|---|---|---|---|
| `build.py` | Full build, `merge` subcommand, `refresh wells` | `layers.yaml`, `combined_*`, standalone files, `data/**`, `build_template.html`, `vendor/`, `sprite/` | `dist/` (index.html, tiles/, data/, `_headers`, `_redirects`, sprite, vendor); `/tmp/gis_build/split/` | tier-3 prebuilt pull from prod `/tiles/` | A |
| `build_sprite.py` | Rasterize 5 icon sprites (cairosvg + Pillow) | embedded SVG | `sprite/sprite{,@2x}.{png,json}` | none | A |
| `build_template.html` | MapLibre SPA shell | token substitution | `dist/index.html` | Esri, Carto, OpenFreeMap, USGS NAIP, Google Fonts, jsDelivr (SheetJS) at runtime | A |
| `layers.yaml` | Layer registry (39 layers) | n/a | n/a | n/a | A |

### 5.2 Shell and release scripts

| Script | Purpose | Inputs | Outputs | Endpoints | Status |
|---|---|---|---|---|---|
| `scripts/deploy.sh` | Build gate, REST deploy, md5 parity, layer gate | `.env` PAT, `dist/` | deployId (stdout) | `api.netlify.com`, prod site | A |
| `scripts/close-out.sh` | Push, rebase, `--no-ff` merge, delete branch | git state | merge commit | GitHub remote | A |
| `scripts/ship.sh` | deploy.sh then close-out.sh | args | deployId + merge | same | A |
| `scripts/audit.sh` | Drift telemetry (read-only) | git remote | stdout | `git fetch`, `ls-remote` | A |
| `scripts/session-open.sh` | Chat-mode branch open, deps, handoff print | git | branch, stdout | prod site | L (chat mode) |
| `scripts/pre-commit` | >1 MB reject, non-canonical path warn (opt-in) | staged files | exit code | none | A (opt-in). Its canonical regex lists `README.md`; file is `Readme.md`. |
| `scripts/bootstrap-claude-code.sh` | One-shot env setup | host | tippecanoe, pip deps, `.env` | brew/apt/pip | A |
| `scripts/bootstrap-windows.ps1` | WSL2 preflight | host | WSL Ubuntu | Microsoft | A (Windows only) |
| `scripts/verify_deployed_layers.py` | Live tilestats gate for every layer | `layers.yaml` | exit 0/1/2, counts | `<base>/tiles/<id>.pmtiles` (Range) | A |

### 5.3 Data ingest and layer builders

| Script | Purpose | Inputs | Outputs | Endpoints | Status |
|---|---|---|---|---|---|
| `fetch_rrc.py` | RRC GoAnywhere bulk download (`wells`, `permits`, `pending`) | MFT folder UUIDs | `data/rrc_raw/*` (gitignored) | `mft.rrc.texas.gov/link/<UUID>`, `/webclient/godrive/PublicGoDrive.xhtml` | A |
| `parse_rrc.py` | `dbf900` and `daf420` parsers, 6-county filter, W-1 backfill merge | `data/rrc_raw/*`, optional `outputs/refresh/rrc_w1_permits_with_coords.csv` | `data/wells_permian6.csv`, `data/permits_permian6.csv` (gitignored) | none | A |
| `fetch_pdq_dump.py` | PDQ production bulk dump | MFT `1f5ddb8d-…` | `data/rrc_raw/PDQ_DSV.zip` (~3.44 GB) | `mft.rrc.texas.gov` | A |
| `build_lease_status.py` | Per-lease trailing 6-month production | PDQ zip | `data/lease_status.csv` (committed) | none | A |
| `build_well_prod_status.py` | API8 → lease → production crosswalk | PDQ zip, `lease_status.csv` | `data/well_prod_status.csv` (committed) | none | A |
| `build_production_deliverable.py` | Hanwha production workbook + summary PDF | PDQ zip | `data/production_permian6.xlsx`, `production_permian6_summary.pdf` | none | 1x (R26 P5) |
| `scrape_rrc_w1.py` | W-1 permit listing scrape (11 counties defined; `counts` mode) | RRC DP JSP | `outputs/refresh/rrc_w1_permits.csv`, checkpoint (gitignored) | `webapps.rrc.state.tx.us/DP/…` | A (backfill) |
| `scrape_rrc_w1_detail_coords.py` | Per-permit detail lat/lon, resumable | listing CSV | `rrc_w1_permits_with_coords.csv`, checkpoint (gitignored) | same | A (backfill) |
| `build_drilling_density.py` | Permit-density polygons per county | `rrc_w1_counts.csv`, `combined_geoms.geojson` | rewrites `combined_geoms.geojson` (11 features, layer `drilling_permit_density`; no `layers.yaml` entry) | none | 1x |
| `build_oxy_drilling_permits.py` | OXY W-1 permit points | `data/rrc_raw/daf420.dat.*`, county polygons | `data/oxy/oxy_drilling_permits.geojson` | none | A |
| `refresh_eia860.py` | EIA-860 plants, battery, solar (TX) | EIA annual zip | `outputs/refresh/eia860_{plants,battery}_<date>.csv` | `www.eia.gov/electricity/data/eia860/xls/eia860<year>.zip` (Referer + UA) | A |
| `refresh_uswtdb.py` | USWTDB wind turbines (TX) | API | `outputs/refresh/wind_<date>.csv` | `eersc.usgs.gov/api/uswtdb/v1/turbines` (cert expired upstream) | A, blocked |
| `refresh_tceq_gas_turbines.py` | TCEQ turbine permits, 23 counties | xlsx | `outputs/refresh/tceq_gas_turbines_<date>.csv`, CHANGELOG | `tceq.texas.gov/downloads/permitting/air/memos/turbine-lst.xlsx`; `nominatim.openstreetmap.org` | A |
| `refresh_fcc_fiber_coverage.py` | FCC BDC H3 hexes, clip to counties | ArcGIS layer | `fcc_fiber_coverage.geojson` (root), archive copy | `services8.arcgis.com/peDZJliSvYims39Q/…/FeatureServer/5` | A (layer not in `layers.yaml`) |
| `fetch_hifld.py` | Generic ArcGIS FeatureServer bbox fetch | slug + URL | `data/hifld/<slug>.geojson` | HIFLD/EIA ArcGIS FeatureServers | A |
| `refresh_dc_anchors.py` | LLM diff proposer for `dc_anchors.json` | `data/datacenters/dc_anchors.json` + source URLs | `outputs/refresh/dc_anchors_proposed.json` | `api.anthropic.com/v1/messages` + each entry's source URLs | A (weekly CI) |
| `geocode_ercot_queue.py` | Stage 1+2 precise geocoding of `ercot_queue` | `combined_points.csv`, dated `outputs/refresh/*_2026-04-25.csv`, `dc_anchors.json`, TIGER zip | in-place `combined_points.csv`; log | `www2.census.gov/geo/tiger/TIGER2024/COUNTY/…` (403/HTML in cloud) | A (Stage 3 unimplemented) |
| `enrich_ercot_coords.py` | Queue coords from abatement rows | `combined_points.csv` | in-place | none | A |
| `enrich_ercot_substation_match.py` | Queue coords from OSM substation names | `combined_points.csv` | in-place | none | A |
| `scrape_ldad.py` | Comptroller LDAD (Ch.312/381) fetch | API | `outputs/refresh/comptroller_ldad_<date>.csv` | `api.comptroller.texas.gov/open-data/v1/tables/ch312-abatement` | A |
| `transform_ldad.py` | Merge LDAD + court seed into `combined_points.csv` | LDAD csv, `data/abatements_court_seed.csv` | in-place | none | A |
| `scrape_abatements.py` | County agenda probe (Pecos, Reeves adapters) | county sites | `data/abatements/abatement_hits_<ts>.csv` (gitignored) | `co.pecos.tx.us`, `reevescounty.org` (Akamai-blocked) | A (diagnostic) |
| `transform_abatements.py` | Pinned snapshot → layer rows + yaml patch | `abatement_hits_20260424_092810.csv` | `combined_points.csv`, `layers.yaml` | none | 1x |
| `extend_county_labels.py` | County labels for all 254 TX counties | TIGER 2024 zip | `combined_geoms.geojson` | `www2.census.gov` | 1x |
| `edit_109b_consolidate.py` | Reposition WAHA; add Longfellow and GW Ranch polygons | `combined_geoms.geojson` | in-place | none | 1x; contains hand-placed APPROXIMATE geometry (pre-dates strict rule 3 reading) |
| `edit_110c_trans_fix.py` | Recolor/reorder `layers.yaml`; replace Longfellow polygon | `layers.yaml`, geojson | in-place | none | 1x; same caveat |
| `edit_local_devs.py` | Add Solstice, La Escalera; reposition WAHA | geojson | in-place | none | 1x; same caveat |
| `build_oxy_assets.py` | Curated OXY overlay extracted from sourced layers | `combined_points.csv`, `data/hifld/hifld_ng_processing.geojson` | `data/oxy/oxy_assets.geojson` | none | A |
| `build_oxy_map_layers.py` | Six OXY layer GeoJSONs | `combined_points.csv`, `oxy_assets.geojson`, county polygons | `data/oxy/oxy_{power,midstream,ercot,permits,water,carbon}.geojson` | none | A |

### 5.4 OXY dossier

| Script | Purpose | Inputs | Outputs | Endpoints | Status |
|---|---|---|---|---|---|
| `oxy_assets_data.py` | Single source for dossier asset cards (coords typed per `src` footnote) | n/a | importable `ASSETS`, `SUBSTATIONS`, `CARAMBA` | none | A |
| `oxy_maps.py` | Light-theme matplotlib map renderer | county/road/city data | PNGs | none | A |
| `oxy_build_maps.py` | Drives 6 maps + key JSON | `oxy_assets_data.py` | `outputs/reports/oxy_map_*.png`, `oxy_map_keys.json` | none | A |
| `build_oxy_report.py` | HTML dossier (cover, §1-§6, Appx A-D) | assets, keys | `oxy-intelligence-report.html` | Inter font CDN at render | A |
| `build_oxy_docx.py` | HTML → Word via pandoc | HTML | `OXY-Intelligence-Report.docx` | none | A |
| `build_oxy_deck.py` | Partnership deck HTML (data-driven locator, FracFocus chart) | `data/oxy/oxy_assets.geojson` | `oxy-partnership-deck.html` | none | A |

### 5.5 OM lineage 1 and 1b (legacy)

| Script | Purpose | Inputs | Outputs | Status |
|---|---|---|---|---|
| `caramba_om_data.py` | Derive all OM figures from layer data (RULE H etc.) | combined files, wells, production, FracFocus, dc_anchors | JSON model | A (only data-derived model; imported by 1/1b builders) |
| `build_insight_pack.py` | Ring analysis, project maturity, edge-to-edge distances | `caramba_om_data` | JSON | A (used by legacy decks and `build_power_gravity_diagram.py`) |
| `build_caramba_om.py` | PostNDA OM PDF (HTML → Chromium) | data model, exhibit JPGs | `Caramba-North-OM-PostNDA.pdf` (+html ignored) | L (superseded) |
| `build_caramba_om_docx.js`, `build_caramba_om_pptx.js` | Word and summary pptx of PostNDA | data model | `…PostNDA.docx/.pptx` | L |
| `build_deck_institutional.js`, `build_deck_editorial.js`, `build_deck_mapled.js`, `build_deck_minimalist.js` | First-pass pptx decks | model, exhibits, icons | `Caramba-North-Deck-{Institutional,Editorial,MapLed,Minimalist}.pptx` | L (design rejected) |
| `build_brief_executive.py`, `build_brief_technical.py` | First-pass docx briefs | brief facts, insight pack | `…Brief-{Executive,Technical}.docx` | L |
| `render_icon_set.js` | react-icons + sharp → white PNG icons | node deps (undeclared) | `outputs/reports/om_exhibits/icons/*.png` | L (support) |
| `capture_om_exhibits.py` | Playwright screenshots of live map with annotations | live site | `om_exhibits/*.jpg`, `manifest.json` | L; gate login obsolete; hard-coded credential defaults (values not reproduced) |
| `build_amz_gwranch_exhibit.py`, `build_longfellow_exhibit.py`, `build_exhibit_7_1_masked.py`, `build_pipeline5_annotated_exhibit.py`, `build_minimalist_exhibit_crops.py` | PIL edits of `exhibit_7_1` raster (pixel positions hand-located); mask CoreWeave tenant label | `om_exhibits/exhibit_7_1_datacenter-pipeline.jpg` | `exhibit_amz_gwranch.jpg`, `exhibit_longfellow.jpg`, `exhibit_7_1_masked.jpg`, `exhibit_pipeline5_mapled.jpg`, `_minimalist/` crops | L (tied to July raster; rerun if recaptured) |
| `build_power_gravity_diagram.py` | Ring diagram schematic, light and dark | insight pack | `exhibit_power_gravity_{light,dark}.png` | L (replaced by `om_charts` rings in lineage 2) |

### 5.6 OM lineage 2 (`scripts/om2/`, current)

| Script | Purpose | Outputs | Status |
|---|---|---|---|
| `extract_map_geometry.py` (in `scripts/`) | Clip real layer geometry to a bbox around the tract | `om_exhibits/map_geometry.json` | A |
| `build_vector_maps.py` (in `scripts/`) | Draw corridor SVG maps from the geometry bundle | `om_exhibits/vector/corridor_*.svg` (incl. `_prenda_*`) | A |
| `om2/om_theme.py` | Type systems, page shell, `render_pdf` (node `_print.mjs`) | n/a | A |
| `om2/om_charts.py` | Hard-coded vector charts (rings, peer drilling, queue growth, maturity, power mix, prenda variants) | `om_exhibits/vector/chart_*.svg` | A |
| `om2/_print.mjs` | Playwright HTML → PDF (`executablePath /opt/pw-browsers/chromium`) | PDF | A |
| `om2/_smoke.py` | Smoke test of theme + SVGs (writes `/tmp/smoke.html`) | none | utility; text says "20 miles" |
| `om2/build_om_master.py` | Merged OM plus Appendix A | `Caramba-North-OM.{html,pdf}`, `…-Appendix-A.{html,pdf}` | A, canonical |
| `om2/build_teaser_prenda.py` | Pre-NDA two-page teaser | `Caramba-North-Teaser-PreNDA.{html,pdf}` | A, canonical |
| `om2/build_deck_institutional.py`, `build_deck_technical.py`, `build_deck_editorial.py`, `build_deck_minimal.py` | Four decks (also imported by master) | `Caramba-North-Deck-*.html/.pdf` | A (institutional + technical feed master) |
| `om2/build_brief_exec.py`, `build_brief_technical.py` | Portrait briefs | `Caramba-North-Brief-*.html/.pdf` | A |
| `om2/fonts/*.css` | Base64 font CSS (archivo, instrumentserif, newsreader, plexmono, plexsans, publicsans) | n/a | A |

### 5.7 Report-analysis scripts (`outputs/reports/`) and Grid Wire builders

| Script | Purpose | Status |
|---|---|---|
| `pecos_shallow_analysis.py`, `pecos_v2_rings_permits.py`, `pecos_recent_rings.py`, `pecos_caramba_vicinity.py`, `pecos_permit_parse.py`, `pecos_depth_vs_profile_join.py`, `pecos_w1_profile.py`, `pecos_operators.py`, `pecos_spud_integrity.py`, `recomp_check.py`, `newdrill_detail.py` | Iterative memo analyses (May 2026) | L (history; hard-coded `/home/andreahimmel/...`) |
| `pecos_lock.py`, `pecos_canon2.py`, `pecos_canonical.py`, `pecos_vs_peers.py`, `howard_loving_extract.py`, `v22_analysis.py`, `v22_charts.py`, `finding9_numbers.py`, `fracfocus_caramba.py`, `fracfocus_new_drill_only.py`, `prod_reclass_numbers.py` | Locked rules, peers, Finding 8-10 | A for method reference; `prod_reclass_numbers.py` uses superseded 150 bbl/d |
| `make_docx.py`, `make_emails_docx.py` | Memo and email .docx | A |
| `source/build_pdf14.py`, `build_pdf21.py`, `make_emails_vol14.py`; `special/crusoe-20260922/build.py`, `charts.py`, `charts3.py`; `special/stranded-iron-20260727/expand_db.py` | Grid Wire PDF/email/chart builders; rig registry seed | A (path edits needed: `/home/claude`, `/mnt/user-data`) |

Undeclared dependencies by tier: `pyyaml pmtiles requests cairosvg Pillow` (build); `shapely pyshp pyproj rapidfuzz openpyxl beautifulsoup4` (ingest); `playwright python-docx matplotlib weasyprint fontTools markdown` and `pandoc` (reports); Node 22 with `pptxgenjs docx sharp react-icons playwright` (decks; `/opt/node22/bin/node` here).

---

## 6. Deliverables registry

"Latest commit" is the newest commit touching the path in the **shallow** history (see §10). Items dated 2026-07-21 are at the shallow boundary; their true date is earlier (embedded dates in parentheses).

### 6.1 Caramba North OM set

| File family (`outputs/reports/`) | Generator | Latest commit | Status |
|---|---|---|---|
| **`Caramba-North-OM.{html,pdf}`** (master OM, Part I) | `scripts/om2/build_om_master.py` | 2026-08-26 `38f3b13` | **CURRENT, canonical** |
| **`Caramba-North-OM-Appendix-A.{html,pdf}`** (technical drawing set A-01..A-15) | same | 2026-08-26 `38f3b13` | **CURRENT, canonical** (embeds a plaintext access password in A-14; see §9) |
| **`Caramba-North-Teaser-PreNDA.{html,pdf}`** | `scripts/om2/build_teaser_prenda.py` | 2026-08-26 `38f3b13` | **CURRENT, canonical** |
| `Caramba-North-OM-PostNDA.{pdf,docx,pptx}` | `scripts/build_caramba_om.py`, `build_caramba_om_docx.js`, `build_caramba_om_pptx.js` | 2026-08-23 `3cbdd0b` | **SUPERSEDED** by master OM + appendix. Last data-derived build (2026-08-19). |
| July 2026 v4 (`Caramba_North_OM_PostNDA_Jul2026_v4.pdf`, built 2026-07-06) | none committed | never committed | Not in repo; reconstructed in the 08-19 rebuild |
| `Caramba-North-Deck-{Institutional,Editorial,Minimal,Technical}.{html,pdf}` | `scripts/om2/build_deck_*.py` | 2026-08-26 `dab33c1` (`c83984e` for Technical) | Current-lineage alternates; not part of the canonical buyer set; distribution Not documented in repo |
| `Caramba-North-Brief-{Executive,Technical}.{html,pdf}` | `scripts/om2/build_brief_*.py` | 2026-08-26 `dab33c1` | Current-lineage alternates |
| `Caramba-North-Brief-{Executive,Technical}.docx` | `scripts/build_brief_*.py` | 2026-08-24 `2dd2391` | Superseded first pass (docx never rebuilt in lineage 2) |
| `Caramba-North-Deck-{Institutional,Editorial,MapLed,Minimalist}.pptx` | `scripts/build_deck_*.js` | 2026-08-24 `2dd2391` | Superseded first pass (design rejected) |
| `om_exhibits/` (JPG/PNG rasters, `vector/` SVGs, `map_geometry.json`, `icons/`, `_minimalist/`, `_technical/`) | capture + PIL scripts; `build_vector_maps.py`; `om_charts.py` | 2026-08-26 `38f3b13` | Rasters are July captures; vectors current |
| `CARAMBA-OM-REBUILD-NOTES.md` | hand-written | 2026-08-19 `5e75c0e` | Reference (delta v4 vs 08-19, known gaps) |

Both currents carry content that is no longer true (see §9): "access logged / credentials issued separately", "RRC weekly / ERCOT and TPIT monthly refresh", embedded July exhibits, hard-typed figures not coupled to data.

### 6.2 Drilling/vibration memo

| File | Generator | Latest commit | Status |
|---|---|---|---|
| `Pecos-Shallow-Drilling-Caramba-Vibration.{pdf,docx}`, `pecos-shallow-drilling-caramba-vibration.md`, `charts/ch_*.png` | `make_docx.py`, `v22_charts.py`; `.md` is source | ≤2026-07-21 `70cbb9a` (prepared 2026-05-19) | Current document, **stale numbers** (July vintage; pre-RULE-H-boundary change) |
| `buyer-email.{md,docx}`, `owner-email.{md,docx}`, `summary-email.md` | hand-written; `make_emails_docx.py` | ≤2026-07-21 | Drafts, not sent; same stale numbers |

### 6.3 OXY

| File | Generator | Latest commit | Status |
|---|---|---|---|
| `OXY-Intelligence-Report.{pdf,docx}`, `oxy-intelligence-report.html`, `oxy_map_*.png`, `oxy_map_keys.json` | `scripts/oxy_*`, `build_oxy_report.py`, `build_oxy_docx.py` | ≤2026-07-21 | Current (as of June 2026) |
| `OXY-Partnership-Brief.{pdf,pptx}`, `oxy-partnership-deck.html` | `build_oxy_deck.py` | ≤2026-07-21 | Current |
| `oxy-partnership-intelligence-2026-06-19.md` | hand-written source brief | ≤2026-07-21 (prepared 2026-06-19) | Source text |
| `OXY-REPORT-HANDOFF.md`, `OXY-report-source.zip` | n/a | ≤2026-07-21 | Handoff docs |
| `OXY-analytics-dashboard.html` | hand-written; calls Supabase `oxy-stats` function | ≤2026-07-21 | **Dead**: function redeployed with `verify_jwt=true`, gate removed |

### 6.4 Counterparty diligence and Grid Wire

| File | Generator | Latest commit | Status |
|---|---|---|---|
| `Pacifico-GW-Ranch-Diligence-Report.pdf`, `pacifico-gw-ranch-diligence-2026-06-12.md` | hand-written; PDF build script not in repo | ≤2026-07-21 (2026-06-12) | Current as of June; Amazon disclosed ownership Aug 2026 postdates it |
| `Stargate-Abilene-Diligence-Report.pdf`, `stargate-abilene-diligence-2026-06-13.md` | same | ≤2026-07-21 (2026-06-13) | Current as of June |
| `GW-Ranch-Email-{DESKTOP,MOBILE}.docx`, `Stargate-Abilene-Email-{DESKTOP,MOBILE}.docx` | not in repo | ≤2026-07-21 | Email drafts |
| `grid-wire-2026-06-17.md` | hand-written | ≤2026-07-21 | Pre-series issue |
| `GRIDWIRE_LOG.md` | appended per cut | 2026-08-26 `d16490e` | Vols 17-21 (Series A), Series B Vols 13-14 |
| `source/` (`grid-wire-vol14-source.md`, `grid-wire-vol21-source.md`, `build_pdf14.py`, `build_pdf21.py`, `make_emails_vol14.py`) | | 2026-08-26 `d16490e` | Only Vols 14 and 21 sources committed; Vols 13 (Series B), 15+, and Series A Vols 17-20 PDFs/sources not in repo |
| `special/stranded-iron-20260727/` (report.md, PDF, rig registry SQLite + CSVs, plan, `expand_db.py`) | | 2026-08-23 `5d0f295` | Current. Registry seeded with 17 rigs. A Supabase project `rhglbwoxuzgwoptycspc` ("lrp-tx-gis-rig", created 2026-08-24, empty) and branch `refinement-rig-schema-baseline` are related, unreferenced in repo code. |
| `special/crusoe-20260922/` (`report.md`, v2 and Spark v3 PDFs, charts) | `build.py`, `charts*.py` | 2026-09-22 `cf5f8e9` | v3 "Spark" is current; v2 PDF superseded |

### 6.5 Other generated artifacts

`data/production_permian6.xlsx` and `…_summary.pdf` (Hanwha production exhibit, R26 P5, one-off); `docs/audit-2026-10-20/*.png` (five defect screenshots: login error, wells panel zero, Carto watermark, NAIP blank, live no-login); `outputs/refresh/` dated snapshots (2026-04-23 to 04-29) and `daily/` (90 reports, 2026-05-18 to 2026-08-19).

---

## 7. External services and credentials map (names only)

| Service | Used for | Credential / config name | Where | Notes |
|---|---|---|---|---|
| **Netlify** site `lrp-tx-gis`, siteId `01b53b80-687e-4641-b088-115b7d5ef638` | Hosting, deploy | `NETLIFY_PAT` (`.env`, or `/mnt/project/CREDENTIALS.md`, or shell `NETLIFY_PAT_ENV`) | `scripts/deploy.sh` | Team Pro. REST `api.netlify.com`. Live: `https://lrp-tx-gis.netlify.app`. No `netlify.toml`, functions, or edge functions. Deploy 2026-10-20 used the Netlify MCP proxy. |
| Netlify (CI path) | `build-and-deploy.yml` | GitHub secrets `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID` | workflow | No evidence they are set. Workflow never run. |
| Netlify (separate site) | Stores `RESEND_API_KEY` env var read by Grid Wire routine | `RESEND_API_KEY` | Netlify env of a different siteId (in the prompt file) | Read through the Netlify MCP; never echo. |
| **GitHub** `10thMuses/lrp-tx-gis` | Source, CI, backup | `GITHUB_PAT` (`.env`, `CREDENTIALS.md`); `GITHUB_TOKEN` (Actions-provided) | `.env.example`; `dc-anchors-refresh.yml` | PAT is fine-grained Contents R/W only on this repo, cannot create PRs. Not read by any script (presence check only). |
| GitHub Actions secrets | | `ANTHROPIC_API_KEY` (set; used by `dc-anchors-refresh.yml`), `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID` | repo settings | |
| **Anthropic API** | DC anchors proposer | `ANTHROPIC_API_KEY` | `refresh_dc_anchors.py:238` | Model `claude-sonnet-4-5-20250929`, `anthropic-version: 2023-06-01`, `max_tokens 2000`. The only LLM call in the repo. |
| **Supabase** project `xvlpperttnedsduscgnq` ("10th-Muses") | Former access gate and tracking | edge functions `oxy-gate`, `oxy-track`, `oxy-stats` | external | Redeployed 2026-10-14 with `verify_jwt=true` (broke the gate); now unused; tables `oxy_sessions`/`oxy_events`; also hosts unrelated `promo-login-temp`, `tmp-*`. No function source or migrations in repo. |
| Supabase project `rhglbwoxuzgwoptycspc` ("lrp-tx-gis-rig") | Rig registry (planned) | none in repo | external | Created 2026-08-24, empty. |
| **Resend** | Grid Wire cut email | `RESEND_API_KEY`; sender `gridwire@10thmuses.com` | scheduled routine | Browser UA required. |
| **Google Drive** | Grid Wire spec docs and state files (`GRIDWIRE_SPEC`, `GRIDWIRE_SPEC_ADDENDUM`, `GRIDWIRE_STATE_*`) | Drive connector in Cowork task | prompt file | File IDs listed in `docs/grid-wire-scheduled-task-prompt.md`. |
| **Cowork scheduled tasks** | Grid Wire 5 AM and 3 PM ET | GitHub connector authorization (does not survive account migration), `CREDENTIALS.md` in project sidebar with `GITHUB_PAT=` line | | Whether still running after 2026-08-26: Not documented in repo. |
| External daily refresh routine | Ran wells/permits/ercot/abatement probe, build check, report | n/a | outside repo | Logged `outputs/refresh/daily/` 2026-05-18 to 2026-08-19; stopped 2026-08-19 (verified 2026-10-20). Contract: no `build.py merge`, so wells/permits (gitignored) never produced a deployable diff; result NO-OP almost every day. |
| **RRC (Texas Railroad Commission)** | Wells, permits, production, W-1 | none | `mft.rrc.texas.gov` (GoAnywhere PrimeFaces), `webapps.rrc.state.tx.us/DP/` | Throttle 1.5 s. |
| **ERCOT** | Queue, TPIT | none | manual xlsx download; no fetch script | `ercot.com` reachable in daily preflight. |
| EIA | EIA-860 | none; `Referer` + UA required | `www.eia.gov` | |
| USGS | USWTDB | none | `eersc.usgs.gov/api/uswtdb/v1/turbines` | Cert expired. |
| TCEQ | Turbine list | none | `www.tceq.texas.gov/downloads/…/turbine-lst.xlsx` | |
| Texas Comptroller | LDAD abatements | none | `api.comptroller.texas.gov` | |
| ArcGIS (HIFLD/EIA, FCC BDC, TWDB) | Layers | none (anonymous) | `services*.arcgis.com` | 503 "DNS cache overflow" retries (5 × 10 s). |
| US Census | TIGER counties | none | `www2.census.gov` | 403/HTML from cloud egress. |
| OpenStreetMap Nominatim | Geocode TCEQ turbines (1.1 s throttle) | none | `nominatim.openstreetmap.org` | Overpass for substations (in-chat; no script). |
| Basemaps and fonts | Runtime | none (keyless) | Esri, Carto (API-key watermark), OpenFreeMap (also supplies glyphs for all label layers), USGS NAIP (404), Google Fonts, jsDelivr (SheetJS) | |
| FracFocus | Disclosure registry | none | `data/fracfocus/DisclosureList_1.csv` (~60 MB, committed); `FracFocusCSV.zip` gitignored | Manual download. |
| Playwright / Chromium | PDF and capture | `HTTPS_PROXY` | local | See §10. |

`.env` variables (`.env.example`): `GITHUB_PAT`, `NETLIFY_PAT`, `LRP_PROJECT_DIR`, `LRP_DIST_DIR`, `LRP_UPLOADS_DIR`. Other read variables: `VERIFY_LAYERS`, `ALLOW_LARGE`, `LRP_GIS_URL`, `LRP_GIS_EMAIL`, `LRP_GIS_PASSWORD`, `HTTPS_PROXY`. `.env` and `CREDENTIALS.md` are gitignored.

**Credential hygiene findings (values not reproduced):**

1. `scripts/capture_om_exhibits.py` lines 26-27: default login email and password hard-coded in source.
2. `scripts/om2/build_om_master.py` (~line 528): the platform access password is hard-coded and rendered into `Caramba-North-OM-Appendix-A.html/.pdf` (A-14). The gate is gone, but the credential is in a distributed buyer file. Rotate it if it is reused anywhere. Whether items 1 and 2 are the same password: not compared.
3. Supabase project ref `xvlpperttnedsduscgnq` appears in `OXY-analytics-dashboard.html:76` (a URL, not a secret, but the function now requires a JWT).

---

## 8. Chronology

Full history is not available locally: the clone is shallow (125 commits, boundary 2026-07-21 `70cbb9a`). Entries before that rely on `docs/archive/*`, `docs/OPERATING_MANUAL.md`, and commit-message references; "Chat N" numbers are chat-mode sessions whose logs are archived.

| Date | Milestone |
|---|---|
| 2026-04-19/20 | Chats 34-37: parcels_pecos batch halted (source missing); refactor to the combined-file architecture; session-protocol install; build halted pre-flight (2 data files missing). |
| 2026-04-21 | Chat 39: first build + deploy under the new protocol, Hanwha sprint planning. Chat 44: Hanwha sprint final, 22/22 layers clean, display overhaul live. Chat 45: RRC endpoint discovery. Chat 48 (21:43): **GitHub sync initialized, `10thMuses/lrp-tx-gis` live.** Chat 52: Hanwha polish landed. Chat 53: `rrc_wells_permian` halted, excluded. |
| 2026-04-22 | Chat 58 prod recovery + TPIT relabel; 10M operating-protocol port; Filter UI stage 1 (Chats 63-65); Stage 3 visual overhaul (69-71); MW-driven sizing + watermark. |
| 2026-04-23 | TCEQ refresh and gas-turbine layer (Chats 72-75b); EIA-860 enrichment and deploy path migration (77); MW sizing (78); UI polish v2 (79). |
| 2026-04-24/25 | Sidebar collapse (80-81); abatement scraper (82; layer ship Chat 83); `dc_anchors.json` compiled (2026-04-25). Source snapshots EIA/USWTDB/TCEQ/FCC/ERCOT dated 04-23 to 04-29. Chats 83-127 (late April to mid May) are referenced in code and docs only. |
| 2026-05-13 | **Round 1**: `wells_pecos11`, RRC GoAnywhere fetch, `deploy.sh` migrated to Netlify REST (deploy `6a0490…`); 6-county rescope (`wells_permian6`); `permits_permian6` forensic parse (28,842 permits, deploy `6a0494…`). **Round 2**: 10 Hanwha-thesis features (filters, scrubber, stats panel, saved views; deploys `6a0498…` to `6a04a2…`). **Round 2.5**: layer inventory; ERCOT precision; counterparty polygons; HIFLD. **Round 26** (7 priorities): plug_flag correction (wells 71,328→99,224), Ch.312 vs LDAD reconciliation, 4 HIFLD layers, W-1 backfill launch, PDQ production deliverable, ERCOT substation match, refresh-automation plan (planning-only). 33 layers. |
| 2026-05-18 | Two operator batches shipped; doc/audit hygiene; stranded branches resolved; `Wells` group; spud-thesis XLSX/PDF export. External daily refresh routine begins (first report 2026-05-18). |
| 2026-05-19 | Pecos shallow-drilling / Caramba vibration memo prepared (Findings 1-10). |
| 2026-06-12 / 06-13 | Pacifico / GW Ranch and Stargate Abilene diligence memos. |
| 2026-06-17 / 06-19 | First free-standing Grid Wire issue; OXY partnership intelligence brief; OXY dossier. |
| 2026-06-23 | **Deploy `6a3adddefa163a0a17902c54`**: 39 layers, `built=39 missing=0 errored=0`, `oxy_drilling_permits` (294 permits), OXY precision upgrades. Last data deploy. |
| 2026-07-06 | July v4 OM PDF built (never committed). |
| 2026-07-08 | Grid Wire Series A Vols 17 (9:00 AM) and 18 (8:15 AM full). |
| 2026-07-20/21 | Vol 19; Vol 20 r1-r4; light-theme-only directive (2026-07-21); first commit visible in the shallow clone. |
| 2026-07-22 to 08-19 | Daily-refresh branches merged "(no deploy)" every day (29 merge commits visible in the shallow history; 89 daily branches exist on origin from 2026-05-19). |
| 2026-07-27 | Stranded Iron report dated (committed 08-23). |
| 2026-08-07 | Vol 21 (Series A closed; sources committed). Vol 22 never produced. |
| 2026-08-18 | `claude/gw-ranch-filings-review-596iy5` branch (3 commits ahead; not merged). Amazon ownership of GW Ranch disclosed Aug 2026. |
| 2026-08-19 | **Caramba OM generator committed** with derived figures and rebuild notes; wells re-parsed to 99,808 (not deployed). Last daily-refresh report. Series B Vol 13 produced in Teams account. |
| 2026-08-20 | OM Word + PowerPoint outputs. |
| 2026-08-23 | Readme/pointer docs restored; Grid Wire cadence (5 AM / 3 PM ET) and Series B numbering resolved; scheduled-task prompt added; Stranded Iron report + rig registry; Longfellow feature slide; Amazon exhibit crop fix. |
| 2026-08-24 | Grid Wire routine hardened (preflight, trackers, credit spec); taxonomy v2 (147 sub-domains); **full redesign** (4 decks + 2 briefs, tenant-neutral); **vector redesign** (om2 type system). Supabase "lrp-tx-gis-rig" project created. |
| 2026-08-26 | Grid Wire Series B Vol 14; **master OM** (institutional + technical merged) + pre-NDA teaser; teaser rebuilt around infrastructure, platform access added; Pre-NDA leads with the land; Appendix A split into its own file. |
| 2026-09-10 | EIA-860 2025 vintage released (repo still on 2024). |
| 2026-09-22 | Crusoe special report v1 → v2 → Spark v3 (three commits). |
| 2026-10-12 | TCEQ turbine list updated upstream (repo on April 2026). |
| 2026-10-14 | Supabase `oxy-gate` / `oxy-track` / `oxy-stats` redeployed with `verify_jwt=true`, breaking the login gate. |
| 2026-10-20 | **Gate removed; deploy `6ad77b77a79fe4d03c8ce377`** (June data, public, no access logging; deployed via Netlify MCP proxy from a mirrored file set missing `_headers`/`_redirects`). `docs/OPERATING_MANUAL.md` and `docs/audit-2026-10-20/` added. PR #50 (draft). Defects audited (§9). |
| 2026-10-21 | origin/main tip `a596741` merges `claude/nice-ritchie-tgzt8b` (deploy 6ad77b77). The working tree also shows uncommitted edits and `*_2026-10-21` refresh snapshots in `outputs/refresh/` from another session (EIA-860, USWTDB, TCEQ, FCC, LDAD); they are not part of this primer. |

---

## 9. Open backlog and known gaps (de-duplicated, ranked by impact)

Sources: `WIP_OPEN.md`, `CARAMBA-OM-REBUILD-NOTES.md`, `docs/OPERATING_MANUAL.md` §7, operator facts of 2026-10-20, this audit.

**Tier 1: wrong or misleading live/distributed content**

1. **Wells/permits stats missing on live map.** `data/wells_permian6.json` and `data/permits_permian6.json` not deployed: stats panel shows 0, scrubber min=max=2026. Cause: build without the gitignored RRC CSVs (and no tippecanoe) then mirror-deploy. Fix: on a machine with tippecanoe, run the §3.6 chain, `python3 build.py`, confirm `dist/data/*.json` and `verify_deployed_layers.py` pass, deploy. Also prevents shipping `MISSING` layers: make `deploy.sh` fail on `missing>0`, or commit the side-car JSON.
2. **Data-refresh claims are false.** OM (July) claimed "real-time" and "weekly-to-monthly" refresh. Current deliverables repeat "RRC weekly; ERCOT queue and TPIT monthly; EIA, USGS, OSM annually" and "access logged / credentials issued separately" (`om2/build_om_master.py`, `build_deck_*.py`, `build_brief_*.py`, `build_teaser_prenda.py`; also `docs/redesign_content_brief.md` §2.7). Actual: no automated data refresh in production; gate removed. Correct the text in the generators and rebuild, or re-establish the refresh.
3. **Operator goal: automatic ("real time") refresh.** Not met. Design inputs: `docs/refresh_automation_plan.md` (weekly-refresh.yml proposal, never written; decisions §7 unsigned). The external daily routine produced NO-OP nearly daily because wells/permits are gitignored and the routine never ran `build.py merge`/deploy; it stopped 2026-08-19. Needed: an in-repo workflow that fetches, builds (tippecanoe, cairosvg), gates on `errored==0` and `missing==0`, deploys with md5/layer gates, then merges. `build-and-deploy.yml` is the skeleton but cannot see the RRC CSVs.
4. **Plaintext access password and hard-coded credential defaults** in `Caramba-North-OM-Appendix-A.{html,pdf}`, `om2/build_om_master.py`, `scripts/capture_om_exhibits.py` (§7). Remove, rotate if reused.
5. **Stale July numbers in the buyer memo and emails** (§4.2). Re-issue or footnote.

**Tier 2: data currency (all behind source)**

6. **`dc_anchors.json`** 8 entries / 2 within 60 mi, compiled 2026-04-25; missing Chevron WTPP, TPL+Bolt, LandBridge Alpha Digital, Longfellow cluster. Drives the 9.7 GW vs ~25 GW discrepancy (§4.1). Highest-value fix before the OM goes to another buyer. Also triage ~14 stale proposal PRs / 22 branches.
7. **ERCOT queue** March/April 2026 snapshot, no fetcher. **TPIT** April 2026, no fetcher. Write `refresh_ercot_queue.py` / `refresh_tpit.py` emitting the combined schema and use `build.py merge`.
8. **EIA-860** still 2024 vintage; 2025 released 2026-09-10: `refresh_eia860.py --year 2025`, merge, rebuild. Solar derives from the same file.
9. **USWTDB** April 2026; V9.1 out; API cert expired: use the file release and `build.py merge wind`.
10. **TCEQ** April 2026; file updated 2026-10-12: rerun `refresh_tceq_gas_turbines.py`.
11. **RRC wells/permits in prod are 2026-06-23**; 2026-08-19 re-parse (wells 99,808) never deployed.
12. Substations (OSM) and transmission (HIFLD) have no scripts (April 2026).

**Tier 3: live UI defects**

13. NAIP basemap 404 (`build_template.html:407-411`).
14. Carto Light API-key watermark (also the initial style before `applyBasemap`).
15. Popups show source/as-of on only ~11 of 39 layers (`combined_points.csv` has no `source`/`source_date` columns; template reads only `props.source`/`props.source_date`; `popup:` lists unused).
16. Deploy `6ad77b77` shipped without `_headers`/`_redirects` (tiles `max-age=0`, no CORS). Next full deploy restores them.
17. "CONFIDENTIAL" print watermark still present on a public map.
18. `ICON_MAP` references layer `wells`, which no longer exists. Orphan data in combined files (`wells` 14,700 TWDB rows, `aquifers`, `caramba_south`, `water_mains_approx`, `drilling_permit_density`). `parcels_pecos` (14,720) and `fcc_fiber_coverage` have no `layers.yaml` entries.

**Tier 4: decisions and automation**

19. **RULE H boundary** (§4.2): operator decision on `spud_year − completion_year <= 1`.
20. **ERCOT Stage 3** override geocoding: operator CSV missing and code unimplemented (§3.8). Remaining ~33 imprecise queue rows need FERC EQR / PUC CCN research.
21. **OM lineage 2 not data-coupled** (§3.12): wire `caramba_om_data.py` / `build_insight_pack.py` into `om_charts.py` and the page builders. Exhibits in `om_exhibits/*.jpg` are July captures; `capture_om_exhibits.py` needs a rewrite (no gate; set Chromium `executable_path`) and a network-capable machine.
22. **Supabase** functions `oxy-gate/track/stats` unused: decommission; `OXY-analytics-dashboard.html` is dead. Decide the fate of `lrp-tx-gis-rig` and `refinement-rig-schema-baseline` (no code references).
23. **Branch/PR hygiene**: 89 stale `refinement-daily-refresh-*` branches, 22 `dc-anchors-refresh-*`, 13 `claude/*`; `WIP_OPEN.md` over budget (8,442 > 8,192); close-out conformance 25/30. PR #50 disposition.
24. **Reeves County abatements**: Akamai blocks datacenter egress (unblock only via residential-proxy egress (paid), Akamai allowlisting, or search-API pages). 21 county adapters are stubs; weekly agenda cron not in production. Permian-core and peripheral expansion spec: `docs/sprint-plan.md` (4-6 chats).
25. **Documentation drift**: `ARCHITECTURE.md` (32 layers) and `OPERATING.md` §5 ("26 entries"; MCP/npx deploy) stale vs 39 layers and REST deploy; `docs/settled.md` states REST deprecated (wrong); `build.py refresh permits` stale; `pre-commit` regex lists `README.md`; no dependency manifest; `build.py` ignores `.env`; `docs/sprint-plan.md` still says "stays at 25" layers; `WIP_OPEN.md` / `CLAUDE.md` W-1 range inconsistency.
26. **Grid Wire**: Series B Vol 13 edition source unrecovered ("recover or rebuild, or formally close as unrecoverable"); Vols 15+ and routine status Not documented in repo; builder scripts hard-code chat-mode paths; `docs/grid-wire-cowork-task-basic.md.bak` leftover. Carried editorial items (Middle Pecos GCD Capitan Reef export outcome; Reeves GCD Sep 1 deadline; PUCT 58481/59142; FERC EL26-67..72; NVDA 10-Q guarantee line) are in the log.
27. **Not feasible** (record to avoid repeats): `oxy_minerals_pecos` (Texas mineral ownership is not public GIS geometry; deliverable would be a non-spatial owner table); pre-2018 permit lat/lon beyond the W-1 scrape; Comptroller Ch.312 bulk (JS-gated).
28. Minor UI backlog: `county_labels` render review at zoom 7-9 (conditional); date_range filter padding for eia860/wind ingest; filter inputs 40 px vs 44 px on mobile; cross-layer search, measure persistence, custom domain, legend-on-print, responsive breakpoints (no build without explicit ask); HIFLD remaining layers; counterparty boundary precision upgrade (4 APPROXIMATE polygons: Microsoft Reeves DC, Core Scientific Pecos, Belding Farms/Cockrell, Fort Stockton Holdings/Riggs/CWEI; plus `mpgcd_zone1`, `la_escalera`, `longfellow_ranch`, `gw_ranch` digitized, labeled APPROXIMATE).

---

## 10. Environment pitfalls

- **Shallow clone.** `git rev-parse --is-shallow-repository` is `true`; 125 commits visible, boundary `70cbb9a` (2026-07-21). Anything older (Chats 34-127, Rounds 1-26 commit hashes, first commit) is not in `git log` here. `git log --merges --grep "deploy [0-9a-f]"` therefore under-reports deploy history. `git fetch --unshallow` (not run here) is the fix; `WIP_OPEN.md` points to `git log --merges` for deploy history.
- **Gitignored large files** (absent in a fresh checkout): `data/rrc_raw/` (`dbf900.txt.gz` ~366 MB, `daf420.dat.*`, `PDQ_DSV.zip` ~3.44 GB), `data/wells_permian6.csv`, `data/permits_permian6.csv`, `outputs/refresh/rrc_w1_*`, `data/abatements/abatement_hits_*.csv` (except the pinned one), `data/fracfocus/FracFocusCSV.zip`, `outputs/refresh/tl_*.zip`, `*.pmtiles`, `dist/`, `CREDENTIALS.md`, `.env`, `Caramba-North-OM-PostNDA.html`. The two RRC CSVs are the build's hidden dependency (§3.2, §9 item 1). Prebuilt layers (`rrc_pipelines`, `tiger_highways`, `bts_rail`) exist only on the live site.
- **tippecanoe absent.** In this container: no tippecanoe, no `pmtiles`, no `cairosvg` (Pillow and `yaml` present), no `.env`. Local full builds and the layer gate cannot run (`build.py:43,46`). Install: `bash scripts/bootstrap-claude-code.sh` plus `pip install cairosvg Pillow`. In chat mode it was installed cold each session (apt + felt fork, ~45 s).
- **Egress limits (sandbox proxy).** Outbound HTTPS goes through an agent proxy (`HTTPS_PROXY`, CA bundle `/root/.ccr/ca-bundle.crt`; see `/root/.ccr/README.md`, diagnose with `curl -sS "$HTTPS_PROXY/__agentproxy/status"`). Never disable TLS verification or unset the proxy; do not retry policy denials (403/407).
  - **Chromium via proxy:** the proxy accepts `curl` but the browser's TLS handshake is refused, so Playwright cannot reach the live site from this sandbox (`CARAMBA-OM-REBUILD-NOTES.md` §6c). `capture_om_exhibits.py` passes the proxy plus `--ignore-certificate-errors --disable-http2` and may still fail. Run captures on a machine with ordinary network access. Local-file PDF rendering (`om2/_print.mjs`) does not need egress.
  - **Census TIGER 403:** `www2.census.gov` returns an HTML block page that gets saved as a `.zip`, giving `zipfile.BadZipFile` in `geocode_ercot_queue.py` and `extend_county_labels.py` (daily report 2026-08-19, step 3c). Pre-seed `outputs/refresh/tl_2024_us_county.zip` from another network.
  - **Akamai on `reevescounty.org`:** datacenter egress is blocked regardless of UA/TLS; Reeves abatement adapter cannot be verified from cloud runners.
  - Other sources with known fragility: `ARCHITECTURE.md` §9 (EIA 503 without `Referer`, ArcGIS 503 "DNS cache overflow", Overpass 503, USPVDB chronic 503, TPIT 503 patterns, Netlify prod default-UA 503). Prod checks need `-A "Mozilla/5.0"` and GET.
- **`GITHUB_PAT` cannot create PRs.** Contents R/W only by design. PRs are made through the GitHub MCP or the web UI; the dc-anchors workflow opens PRs with the Actions `GITHUB_TOKEN` (requires the repo setting that allows Actions to create PRs; not documented in repo).
- **Playwright `executable_path` workaround.** Playwright's default browser lookup does not resolve to the installed Chromium (`/opt/pw-browsers` holds revision 1194 only), so a default `chromium.launch()` can fail. Pass `executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome"` (python) or `executablePath: '/opt/pw-browsers/chromium'` (node; `/opt/pw-browsers/chromium` is a symlink to that binary). `build_caramba_om.py` probes a candidate list including that path and `om2/_print.mjs` hard-codes the symlink; `capture_om_exhibits.py` sets no `executable_path` and needs the same fix. Launch args used elsewhere: `--no-sandbox --disable-dev-shm-usage`. Node 22 is at `/opt/node22/bin/node`; npm packages are undeclared and `scripts/om2/node_modules` must be provided.
- **Hard-coded paths.** `build.py` splits to `/tmp/gis_build/split/` (concurrent builds collide); `deploy.sh` writes `/tmp/build.log`; `outputs/reports/*.py` analysis scripts use `/home/andreahimmel/lrp-tx-gis`; Grid Wire builders use `/home/claude/...` and `/mnt/user-data/outputs/...`; `deploy.sh` also reads `/mnt/project/CREDENTIALS.md`. `LRP_PROJECT_DIR` falls back to repo root if the path is missing; `LRP_DIST_DIR` does not.
- **Prod verification quirks.** `curl` default UA → 503; HEAD on root → 503 even when GET is healthy; CDN warm-up 45-90 s; `_redirects` rewrites any missing path (including a missing `data/<layer>.json`) to `index.html` with 200, so panels silently fall back to empty arrays.
- **Browser-less checks.** The Spuds Summary PDF export and county label rendering were verified by config/bundle reasoning, not in-browser (`WIP_OPEN.md`).
- **Never `git add -A`.** The working tree accumulates `dist/`, `__pycache__/`, `/tmp` scratch pointers, and unignored outputs. Stage explicit paths.
- **Never read data files.** For counts use aggregate scripts or doc-recorded numbers; `build.py` and the OM data model stream data themselves.
