# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every chat.

---

## Recent sessions

| Chat | Date | Outcome |
|---:|---|---|
| 44 | 2026-04-21 | **HANWHA SPRINT COMPLETE.** 22/22 clean, deployId `69e7a7859da0044dc5b0f714`, 17.5 MB total tiles. Display overhaul + measure + print-to-PDF + 5 basemaps + Planned Upgrade styling all live. Hanwha URL delivered. |
| 45 | 2026-04-21 | Discovery: rrc_wells_permian → path (b) bulk-CSV via `mft.rrc.texas.gov`. |
| 47 | 2026-04-21 | GitHub-backed project sync protocol installed. |
| 48 | 2026-04-21 | **GitHub sync live.** Repo `github.com/10thMuses/lrp-tx-gis`, initial push of 14 tracked files, CREDENTIALS.md gitignored. |
| 51 | 2026-04-21 | Hanwha polish patch authored in-session; container reset before close. |
| 52 | 2026-04-21 | **Hanwha polish landed.** 22/22 clean, deployId `69e82c344f3101e36a99b60e`. aquifers dropped, county_labels added. |
| 53 | 2026-04-21 | rrc_wells_permian **HALTED**; Andrea elected to exclude RRC oil/gas wells from scope. |
| 54–57 | 2026-04-21/22 | See SESSION_LOG. Chat 55 attempted EIA-860/USWTDB operator/owner field refresh — errored MCP deploy + CLI timeout blocked git push, work lost (discovered Chat 58). Chat 57 TPIT label edits never committed (container reset) — redone Chat 58. |
| 58 | 2026-04-22 | **Prod recovery + TPIT rename.** Prod 503 ("DNS cache overflow", Netlify edge platform issue) recovered via operator manual republish of Chat 44 Hanwha deploy. Fresh TPIT-rename build deployed (deployId `69e8e002c4782d80d2949109`), `ready` but `published_at=null`. Chat 55 field refresh confirmed lost and dropped from scope. |

---

## Prod status (as of Chat 58 close — 2026-04-22)

- URL: https://lrp-tx-gis.netlify.app
- **Currently published deploy**: `69e7a7859da0044dc5b0f714` (Chat 44 Hanwha), state=ready, 2026-04-21 16:37 UTC. 22 layers, 17,546 KB tiles.
- **Pending publish**: `69e8e002c4782d80d2949109` (Chat 58, TPIT-rename), state=ready, created 2026-04-22 14:49 UTC. Awaiting operator manual publish via https://app.netlify.com/projects/lrp-tx-gis/deploys/69e8e002c4782d80d2949109 → "Publish deploy" button. Once published, prod upgrades from Hanwha-22-layers to Hanwha-22-layers-with-renamed-TPIT-labels (`tpit_subs.label` → "Substation Upgrades", `tpit_lines.label` → "Transmission Upgrades"; IDs unchanged, all downstream references stable).
- **Auto-publish**: operator unlocked post-Chat-58. Future deploys auto-publish as before.
- Layer set: 22 (vs Chat 44: aquifers removed, county_labels added).
- Display features (cumulative): custom icons (solar/wind/battery/gas/wells), Planned Upgrade styling (tpit_subs + tpit_lines), measure tool (mi + ac), print-to-PDF (landscape + LRP header), 5 basemaps (Carto / Esri Streets / Esri Imagery / OpenFreeMap / NAIP), hover popups (transient, suppressed during measure), FIELD_LABELS dict, line casings (white 3.5px underlay on all line layers).
- Prebuilt PMTiles (tier-1 project, tier-3 prod): parcels_pecos (4.98 MB), rrc_pipelines (4.73 MB), tiger_highways (3.11 MB), bts_rail (2.16 MB).

---

## Hanwha data room — delivered

- URL: https://lrp-tx-gis.netlify.app (open, no password per sprint decision)
- Polish sprint complete (Chat 52).

---

## Open backlog

**Deferred sources — manual-CSV pattern:**
- ~~`rrc_wells_permian`~~ — **EXCLUDED from scope as of Chat 53.** MFT GoAnywhere/PrimeFaces AJAX-only; revisit only on explicit re-scope.
- `tceq_gas_turbines`, `tceq_nsr_pending`, `tceq_pbr` — CRPUB scrape + Census geocoder. Scope: fossil/emissions only (gas peakers + emission-permitted combustion + compressors). Queued for Chat 60.
- `tceq_pws` — HTTP 400 on original endpoint; scope-confirm needed at next touch.

**Data-pipeline gap:**
- `combined_points.csv` has blank `operator`, `commissioned`, `technology`, `fuel`, `capacity_mw` fields across `eia860_plants`, `eia860_battery`, `solar`, `wind`, `ercot_queue`. Chat 55 attempted refresh; work lost (never pushed). **Dropped from scope Chat 58** — field was illustrative; generic filter UI (Chat 59) provides the actual leverage. If a future chat decides to re-do: fetch EIA-860 XLSX + USWTDB, join by plant_code, write back to `combined_points.csv`.

**Other open items:**
- Grid Wire Vol. 7.
- Tier 2 water availability assessments (5 clusters), cluster intelligence sheets, Excel returns model (tranched water A/B/C/D).
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar (`data.json` doesn't read PMTiles metadata). Fix = tippecanoe-probe subprocess per prebuilt. Not blocking.

---

## Queue (next chats)

- **Chat 59 — Lockdown + generic filter UI.** Frontend-only build. `filterable_fields` yaml per-layer (date/category/numeric/text), sidebar filter controls rendered on layer-toggle-on, monthly-granularity range slider, popup copy-disable (`user-select:none` + `oncontextmenu`), `_headers` CORS verify on `.pmtiles`. Build + deploy to prod.
- **Chat 60 — TCEQ refresh.** `tceq_nsr` / `tceq_pbr` / `tceq_gas_turbines` via CRPUB scrape + Census geocoder. 12 Permian counties (Pecos, Reeves, Ward, Culberson, Loving, Winkler, Ector, Midland, Upton, Crane, Martin, Howard). SIC/NAICS: electric generation + compressor. Outputs to `outputs/refresh/points_tceq_{nsr,pbr,gas_turbines}.csv`. No build.
- **Chat 61 — TCEQ merge + add.** Merge into `combined_points.csv` (drop-and-append by layer_id). Add 3 layers under new "Permits" sidebar group (purple family, distinct from water). Each declares `filterable_fields`: `date_filed` (date), `permit_type` (category), `status` (category), `company` (text). Build + deploy.

**Note on user-feedback intake**: if Andrea surfaces map-refinement requests before Chat 59 starts, a dedicated intake chat may slot in as Chat 59 (triage-only, no build), shifting the above queue by one.

---

## GitHub sync — LIVE

- Repo: `github.com/10thMuses/lrp-tx-gis`, `main` = authoritative.
- Working directory in-chat: `/home/claude/repo/`.
- Session-open: `git clone` as first bash call.
- Session-close: `git add -A && git commit -m "Chat N: <title>" && git push` as last bash call, no-op if no changes.
- Push-reject fallback = pull-rebase-push once, else halt.
- Fallback if GitHub unreachable: `/mnt/project/` is read-only copy of last-uploaded state.
- Full protocol: `PROJECT_INSTRUCTIONS.md §"GitHub sync"`.
- **Sync gap to be aware of**: GitHub is authoritative for build/deploy. `/mnt/project/` is read-only and only refreshed when operator manually uploads. Project-knowledge-search can return stale content if operator hasn't re-uploaded since last repo change. For build operations this doesn't matter (repo clone is always current). For cold reads via project-knowledge-search in a new chat, operator should re-upload `/mnt/project/` after any chat where tracked files changed — OR Claude should always clone-first rather than rely on project-knowledge-search for file contents.

---

## Protocol permanence pins

- GIS_SPEC.md authoritative; sidebar system prompt aligned.
- GitHub main is the authoritative state layer after Chat 48.
- Cap check mandatory at handoff-write time (§15 Rule 3, chat-36 failure mode).
- CDN warm-up window: curl HEAD may 503 for ~45–75s post-deploy — wait and retry before escalating.
- **Polish-sprint reconstruction pattern (Chat 52):** when a prior chat claims "file already edited on disk" for `/mnt/project/` artifacts, verify via diff against the last-pushed GitHub state before trusting the claim. In-session edits to `/mnt/project/` do not persist across container resets; only GitHub does.
- **Memory-state verification pattern (Chat 58):** on session open, if memory asserts "work X is committed/persists," verify via `git log` + targeted `md5sum`/field-count check before relying on it. Memory can lag or be wrong if a prior chat's push failed silently.
- **Netlify edge 503 recovery (Chat 58):** "DNS cache overflow" on alias AND raw deploy permalink = platform-side edge issue, not deploy content. Recovery path: Netlify UI → Deploys → "Lock to stop auto publishing" (surfaces Publish button) → click prior `ready` deploy → "Publish deploy" → forces edge re-cache. MCP has no rollback/publish-deploy op, requires operator UI step. Unlock auto-publish afterward or future deploys require manual publish.
- **Netlify CLI timeout pattern (Chats 55, 58):** "Error fetching deploy status: Service Unavailable" from CLI deploy polling is unrelated to actual deploy success. Deploy completes server-side despite CLI error. Truth source = MCP `get-deploy-for-site` with the deployId returned at upload time. Do not retry CLI on timeout.
- **Parallel-session pattern (Chat 58):** when operator runs two Claude sessions simultaneously on the same project, later session must `git pull` (or just trust `git status` + fresh clone) before editing. A `git clone` at session open is always safer than assuming local state reflects origin.
