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
| 45 | 2026-04-21 | Discovery chat (no build): rrc_wells_permian → path (b) bulk-CSV fallback via `mft.rrc.texas.gov`. Moves source from blocked to implementation queue under manual-CSV pattern. |
| 47 | 2026-04-21 | GitHub-backed project sync setup: repo layout, open/close protocol, PROJECT_INSTRUCTIONS.md updated, WIP/SESSION rebuilt. No data or build this chat. |

Chat 46: no log entry; likely non-GIS work or counter skip. Flagged, not reconstructed.

---

## Prod status (as of Chat 44 close — unchanged through 47)

- URL: https://lrp-tx-gis.netlify.app
- Deploy: `69e7a7859da0044dc5b0f714`, state=ready, 2026-04-21T16:37Z
- Layers live: **22** (all 0 errored, 17,546 KB total tiles)
- Prebuilt PMTiles (tier-1 project, tier-3 prod): parcels_pecos (5.10 MB), rrc_pipelines (4.85 MB), tiger_highways (3.18 MB), bts_rail (2.22 MB)
- Display features live: custom icons (solar/wind/battery/gas/wells), Planned Upgrade styling (tpit_subs + tpit_lines), measure tool (mi + ac), print-to-PDF (landscape + LRP header), 5 basemaps (Carto / Esri Streets / Esri Imagery / OpenFreeMap / NAIP)
- Hanwha URL delivered: **https://lrp-tx-gis.netlify.app** (open, no password per sprint decision)

---

## Hanwha sprint — CLOSED

Deadline Tue Apr 21 2026 6:00 PM EST → delivered ~12:38 PM EST (~5.5 hrs ahead). All P0 features live. Archive at `HANWHA_SPRINT_closed.md`.

---

## GitHub sync — ACTIVE (installed Chat 47)

- Repo: **[pending — Andrea to provide URL + PAT in `CREDENTIALS.md`]**
- Authority: GitHub `main` = canonical. `/mnt/project/` = read-only fallback at session open.
- Session-open trigger (first bash): `git clone --depth=1 https://x-access-token:$PAT@github.com/OWNER/REPO.git repo` into `/home/claude/`, then `cd repo`.
- Session-close trigger (last bash before final response, only if changes): `git add -A && git commit -m "Chat N: <title>" && git push`.
- Working directory in-chat: `/home/claude/repo/`. All references to `/mnt/project/<file>` in docs resolve there.
- Gitignored: `CREDENTIALS.md`, `dist/`, `__pycache__/`, `.venv/`, `tmp*/`.
- No Git LFS at current sizes. Revisit if any single file >50 MB.
- See PROJECT_INSTRUCTIONS.md §"GitHub sync" for full protocol.

---

## Open backlog (post-sprint)

**Deferred sources — Chat 43 FETCH_FAILED, updated through Chat 45:**
- `rrc_wells_permian` — **path resolved Chat 45**: bulk-CSV fallback via `mft.rrc.texas.gov`. Implementation queued as manual-CSV pattern (download → Permian bbox filter → emit `points_rrc_wells_permian.csv` or `geoms_rrc_wells_permian.geojson`). Next chat on this source = fetch + stage.
- `tceq_gas_turbines` — no public GIS endpoint; CRPUB scrape + Census geocoder required. Manual-CSV pattern.
- `tceq_nsr_pending` — same.
- `tceq_pbr` — same.
- `tceq_pws` — HTTP 400 on `TWSBV_Retail_Water_Service_Boundary`. Alternatives: `data.texas.gov` catalog, TWDB CCN/MCS, TCEQ map viewer AGOL.

**Other open items:**
- Aquifers layer has 5 features; sprint target was 5 aquifers — confirm completeness vs. TWDB Major + Minor catalog.
- `dc_sites` layer: requires Andrea to compile source CSV (manual-CSV pattern).
- Grid Wire Vol. 7.
- Tier 2 water availability assessments (5 clusters), cluster intelligence sheets, Excel returns model (tranched water A/B/C/D).
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar (`data.json` doesn't read PMTiles metadata). Fix = tippecanoe-probe subprocess per prebuilt. Not blocking.

---

## Next chat — no scheduled successor

GitHub sync installed Chat 47 but not yet initialized (repo empty, PAT not yet in CREDENTIALS.md). Next chat opens with either:
- **GitHub init trigger** (`github init.`) → Claude does initial push of /mnt/project/ contents to empty repo; afterward, all chats use open/close protocol.
- **Standard GIS trigger** (`refresh <layer>.`, `add layer...`, `build. deploy.`) → runs against /mnt/project/ under pre-sync convention until init happens.

Recommended order: GitHub init first (single focused chat, ~6 tool calls), then rrc_wells_permian implementation chat (bulk-CSV fetch + stage, 8–12 calls).

---

## Protocol permanence pins (unchanged from Chat 43)

- GIS_SPEC.md authoritative; sidebar system prompt aligned.
- `/mnt/project/` upload = source of truth between chats **until GitHub init**; after init, GitHub is authoritative and `/mnt/project/` is fallback.
- Cap check mandatory at handoff-write time (§15 Rule 3, chat-36 failure mode). GitHub sync reduces but does not eliminate this — PROJECT_KNOWLEDGE still caps for in-context file serving.
- CDN warm-up window: curl HEAD may 503 for ~45–75s post-deploy — wait and retry before escalating.
