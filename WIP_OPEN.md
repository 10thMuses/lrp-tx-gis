# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every chat.

---

## Recent sessions

| Chat | Date | Outcome |
|---:|---|---|
| 39 | 2026-04-21 | First build under new protocol: 17/17 clean, deployId 69e678b6...; Hanwha sprint formalized |
| 41 | 2026-04-21 | parcels_pecos pre-build + ERCOT popup + Waha label; build clean (19/19, 7.58 MB); MCP deploy errored; handoff to 42 |
| 42 | 2026-04-21 | Chat 41 artifacts deployed to prod (deployId 69e795343124ef21cb4829d3); build.py prebuilt branch hardened to 3-tier resolver |
| 43 | 2026-04-21 | 9-source refresh: 4 OK (rrc_pipelines, tiger_highways, bts_rail, water_mains_approx); 5 FETCH_FAILED; merge staged at 6.57 MB combined_geoms |
| 44 | 2026-04-21 | **HANWHA SPRINT COMPLETE.** 22/22 clean, deployId 69e7a7859da0044dc5b0f714, 17.5 MB total tiles. Display overhaul + measure + print-to-PDF + 5 basemaps + Planned Upgrade styling all live. Hanwha URL delivered. |
| 45 | 2026-04-21 | Discovery: rrc_wells_permian → path (b) bulk-CSV via `mft.rrc.texas.gov`. |
| 47 | 2026-04-21 | GitHub-backed project sync protocol installed. |
| 48 | 2026-04-21 | **GitHub sync live.** Repo `github.com/10thMuses/lrp-tx-gis`, initial push of 14 tracked files, CREDENTIALS.md gitignored. |
| 51 | 2026-04-21 | Hanwha polish patch authored in-session (FIELD_LABELS + hover popups + line casings + county_labels add, aquifers drop); build/deploy not landed — container reset before close. |
| 52 | 2026-04-21 | **Hanwha polish landed.** 22/22 clean, deployId `69e82c344f3101e36a99b60e`, patches reconstructed and applied idempotently. aquifers dropped, county_labels live at 25KB/46 features. |
| 53 | 2026-04-21 | rrc_wells_permian fetch **HALTED** pre-download — MFT endpoint is GoAnywhere AJAX-only (no direct URL); Andrea elected to exclude RRC oil/gas wells from scope for now. No build, no deploy. |

---

## Prod status (as of Chat 52 close)

- URL: https://lrp-tx-gis.netlify.app
- Deploy: `69e82c344f3101e36a99b60e`, state=ready, 2026-04-21 21:50 EDT
- Layers live: **22** (0 errored, 17,484 KB total tiles)
- Layer set change vs Chat 44: `aquifers` removed, `county_labels` added (label geom, min_zoom=6, default_off).
- Display features (cumulative): custom icons (solar/wind/battery/gas/wells), Planned Upgrade styling (tpit_subs + tpit_lines), measure tool (mi + ac), print-to-PDF (landscape + LRP header), 5 basemaps (Carto / Esri Streets / Esri Imagery / OpenFreeMap / NAIP), **hover popups** (transient, suppressed during measure), **FIELD_LABELS dict** (raw keys → display labels across all generic popups), **line casings** (white 3.5px underlay on all line layers, line-cap/join round).
- Prebuilt PMTiles (tier-1 project, tier-3 prod): parcels_pecos (4.98 MB), rrc_pipelines (4.73 MB), tiger_highways (3.11 MB), bts_rail (2.16 MB). Tier-1 missed this chat (container had no prebuilt copies) — prod-url tier-3 fallback used for all four, self-sustaining from prior deploy.

---

## Hanwha data room — delivered

- URL: https://lrp-tx-gis.netlify.app (open, no password per sprint decision)
- Polish sprint (Chat 51 authored, Chat 52 landed): complete.

---

## Open backlog

**Deferred sources — manual-CSV pattern:**
- ~~`rrc_wells_permian`~~ — **EXCLUDED from scope as of Chat 53** (Andrea decision). MFT `mft.rrc.texas.gov` path is GoAnywhere/PrimeFaces AJAX-only (no direct-URL download); reopening would require either manual browser-downloads of 12 county shapezips or a PrimeFaces session-downloader implementation. Revisit only on explicit re-scope.
- `tceq_gas_turbines` — CRPUB scrape + Census geocoder. **Scope: fossil/emissions only** (gas-fired peakers and emission-permitted combustion sources); not renewables.
- `tceq_nsr_pending` — same pattern. Scope: fossil/emissions only.
- `tceq_pbr` — same. Scope: fossil/emissions only.
- `tceq_pws` — HTTP 400 on original endpoint; alternatives = `data.texas.gov` catalog, TWDB CCN/MCS, TCEQ map viewer AGOL. Confirm scope at next touch.

**Data-pipeline gap (flagged Chat 52):**
`combined_points.csv` has blank `operator`, `commissioned`, `technology`, `fuel`, `capacity_mw` fields across `eia860_plants`, `eia860_battery`, `solar`, `wind`, `ercot_queue`. `ercot_queue` has `entity` populated (Developer slot OK). Popups degrade cleanly on blanks (empty rows dropped by `featurePopupHtml` filter), but a future refresh of EIA-860 + USWTDB must carry those fields or the Generation layers remain name-only under hover/click. Not blocking Hanwha delivery; blocking for investor-material cross-reference.

**Other open items:**
- Grid Wire Vol. 7.
- Tier 2 water availability assessments (5 clusters), cluster intelligence sheets, Excel returns model (tranched water A/B/C/D).
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar (`data.json` doesn't read PMTiles metadata). Fix = tippecanoe-probe subprocess per prebuilt. Not blocking.

---

## GitHub sync — LIVE

- Repo: `github.com/10thMuses/lrp-tx-gis`, `main` = authoritative.
- Working directory in-chat: `/home/claude/repo/`.
- Session-open: `git clone` as first bash call.
- Session-close: `git add -A && git commit -m "Chat N: <title>" && git push` as last bash call, no-op if no changes.
- Push-reject fallback = pull-rebase-push once, else halt.
- Fallback if GitHub unreachable: `/mnt/project/` is read-only copy of last-uploaded state.
- Full protocol: `PROJECT_INSTRUCTIONS.md §"GitHub sync"`.

---

## Protocol permanence pins

- GIS_SPEC.md authoritative; sidebar system prompt aligned.
- GitHub main is the authoritative state layer after Chat 48.
- Cap check mandatory at handoff-write time (§15 Rule 3, chat-36 failure mode).
- CDN warm-up window: curl HEAD may 503 for ~45–75s post-deploy — wait and retry before escalating.
- **Polish-sprint reconstruction pattern (Chat 52):** when a prior chat claims "file already edited on disk" for /mnt/project artifacts, verify via diff against the last-pushed GitHub state before trusting the claim. In-session edits to /mnt/project do not persist across container resets; only GitHub does.
