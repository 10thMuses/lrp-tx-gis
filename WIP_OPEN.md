# WIP_OPEN.md

Active state. Read at session open. Updated at close-out of every shipping chat.

Per Readme §10: **`## Next chat`** = paste-ready for next shipping chat. **`## Sprint queue`** = N+2 and beyond.

---

## Next chat

**Chat 81 — SIDEBAR COLLAPSE (RESUME, token-limit paused).** Chat 80 committed 6 of 9 edits to branch `refinement-sidebar-collapse` (commit `bdc1fb6`, pushed) then hit token limit before wiring JS behavior. Main HEAD `1320167` (Chat 79 PR was merged — WIP_OPEN's prior `dc5aa16` reference was stale). Prod live on deploy `69ea9d1b8b51ad96ce674f5d` (22 layers). Branch is NOT yet deployable — toggle button is DOM-present but inert.

**What Chat 80 shipped to the branch (`build_template.html` only):**
- CSS: `body` grid transition 220ms + `body.sb-collapsed { grid-template-columns: 0 1fr }`
- CSS: `.sidebar` gets `overflow-x: hidden` + `min-width: 0`; collapsed state removes right border
- CSS: `.sb-toggle` button (44×44, `position: absolute; top: 8px; left: 8px; z-index: 4` inside `.map-wrap`)
- CSS: `@media (max-width: 720px)` — sidebar becomes `position: absolute` overlay, `transform: translateX` on collapse, toggle button shifts to `left: calc(280px + 8px)` when expanded
- CSS: `.sb-toggle` hidden during print
- HTML: `<button id="sb-toggle" class="sb-toggle" type="button" aria-label="Toggle sidebar" aria-expanded="true" title="Toggle sidebar">«</button>` inserted inside `.map-wrap` after `#map`
- JS: `writeHash` now accepts and serializes `state.sb` as `sb=1`

**What Chat 81 must finish on `refinement-sidebar-collapse`:**

Edit A — init state (after line ~260, right after the `if (initHash.filters) { ... }` block):
```js
let sidebarCollapsed = initHash.sb === '1';
if (sidebarCollapsed) document.body.classList.add('sb-collapsed');
```
Apply BEFORE `new maplibregl.Map(...)` so the map container has correct initial width.

Edit B — `syncHash` (around line 854), add `sb` to the `writeHash` call:
```js
writeHash({ lat: c.lat, lon: c.lng, zoom: map.getZoom(), layers: activeLayerIds().join(','), base: currentBase, filters: filtersStr, sb: sidebarCollapsed ? '1' : undefined });
```

Edit C — toggle click handler (add after `btn-print` wiring, ~line 897):
```js
const sbToggle = document.getElementById('sb-toggle');
function updateSbChevron() {
  sbToggle.textContent = sidebarCollapsed ? '»' : '«';
  sbToggle.setAttribute('aria-expanded', sidebarCollapsed ? 'false' : 'true');
}
updateSbChevron();
sbToggle.addEventListener('click', () => {
  sidebarCollapsed = !sidebarCollapsed;
  document.body.classList.toggle('sb-collapsed', sidebarCollapsed);
  updateSbChevron();
  // Fire resize on transitionend; fallback timeout in case transitionend doesn't fire.
  let done = false;
  const finish = () => { if (done) return; done = true; map.resize(); syncHash(); };
  const onEnd = (e) => {
    if (e.target !== document.body) return;
    if (e.propertyName && e.propertyName.indexOf('grid-template-columns') === -1 && e.propertyName.indexOf('transform') === -1) return;
    document.body.removeEventListener('transitionend', onEnd);
    finish();
  };
  document.body.addEventListener('transitionend', onEnd);
  setTimeout(finish, 260);
});
```

Note: on mobile the transition is on `.sidebar` (transform), not on `body`. The fallback `setTimeout(260)` covers that path since the mobile listener won't fire on body. Acceptable — `map.resize()` is idempotent.

### Session open (Chat 81)

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
cd /home/claude && rm -rf repo 2>/dev/null; git clone -q https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git repo && cd repo
git config user.email "claude@lrp.local" && git config user.name "Claude (LRP GIS)"
git fetch --all
git checkout refinement-sidebar-collapse   # branch exists remotely at commit bdc1fb6
git log --oneline -3   # confirm HEAD = bdc1fb6
apt-get install -y tippecanoe libcairo2 -q
pip install shapely pmtiles pyyaml cairosvg pandas openpyxl --break-system-packages -q
```

### Verification (Chat 81, after build + deploy)

1. Load prod URL — sidebar visible, `«` button at top-left corner of map (8px inside).
2. Click `«` — sidebar slides out 220ms, map reflows full-width, button becomes `»` at left:8px of full-width map.
3. Click `»` — reverses; sidebar scroll position + filter state retained.
4. URL hash updates to include `sb=1` when collapsed.
5. Reload with `#sb=1` — sidebar loads collapsed.
6. Mobile (≤720px viewport): sidebar overlays map as 280px drawer with shadow; collapse slides it off-screen left, toggle snaps to left:8px.
7. Print — toggle hidden, sidebar hidden, map fills page.

### Build + deploy (standard pattern)

```bash
python build.py
# gate: built=22, errored=0

PAT=$(grep '^NETLIFY_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
SITE=01b53b80-687e-4641-b088-115b7d5ef638
cd /mnt/user-data/outputs/dist && zip -qr /tmp/d.zip .
RESP=$(curl -s -X POST -H "Authorization: Bearer $PAT" -H "Content-Type: application/zip" \
  --data-binary @/tmp/d.zip "https://api.netlify.com/api/v1/sites/$SITE/deploys")
DEPLOY_ID=$(echo "$RESP" | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")

i=0; while [ $i -lt 30 ]; do i=$((i+1))
  STATE=$(curl -s -H "Authorization: Bearer $PAT" \
    "https://api.netlify.com/api/v1/sites/$SITE/deploys/$DEPLOY_ID" \
    | python3 -c "import sys,json;print(json.load(sys.stdin).get('state','?'))")
  [ "$STATE" = "ready" ] && break; [ "$STATE" = "error" ] && break; sleep 6
done
sleep 90
curl -sI -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | head -3
curl -s -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | grep -oE '"id":[ ]*"[a-z0-9_]+"' | sort -u | wc -l
# expect: HTTP/2 200, 22 layers
```

### PR + close-out

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
git push "https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git" refinement-sidebar-collapse
```

Operator opens PR via GitHub UI (PAT scope still lacks PR-create). Update `WIP_OPEN.md` `## Next chat` → promote ABATEMENT BUILD (Chat 82). Append `WIP_LOG.md` entries for Chat 80 (partial, paused) and Chat 81 (resume + ship).

**Credential:** `NETLIFY_PAT=nfp_h3iY48jurPAn57KcUzaCKGNccw5gXR1z9ac5` and `GITHUB_PAT=...` supplied in `/mnt/project/CREDENTIALS.md`.

### Session open (single block)

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
cd /home/claude && rm -rf repo 2>/dev/null; git clone -q https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git repo && cd repo
git config user.email "claude@lrp.local" && git config user.name "Claude (LRP GIS)"
git fetch --all  # per Readme §10: check whether refinement-sidebar-collapse already exists remotely with prior work
git branch -a | grep refinement-sidebar-collapse || true
# if remote branch exists with commits beyond main: checkout and inspect (Readme §10)
# else: git checkout -b refinement-sidebar-collapse
apt-get install -y tippecanoe libcairo2 -q
pip install shapely pmtiles pyyaml cairosvg pandas openpyxl --break-system-packages -q
```

### SIDEBAR COLLAPSE — task execution order

Per `docs/refinement-sequence.md` §Stage: SIDEBAR COLLAPSE:

1. **Toggle control.** Add toggle button anchored to sidebar's right edge (top-right corner). Renders `«` expanded, `»` collapsed. Minimum 44×44 px hit area for mobile.
2. **Collapse behavior.** On toggle, sidebar slides out (`transform: translateX` or `width: 0`, ~200ms). Map container expands full-viewport width. `map.resize()` fires on transition end.
3. **Expand behavior.** Reverse. Map resizes back. Sidebar retains prior scroll + filter state.
4. **Mobile parity.** Same control, same chevron convention. Mobile sidebar overlays map; collapse returns full-screen map.
5. **State persistence.** Sidebar open/collapsed state in URL hash alongside viewport state. Reload or share preserves collapsed view.

Deliverables: `build_template.html` CSS + JS changes only. No `layers.yaml`, no data-pipeline, no `build.py` changes.

### Build + deploy (unchanged from Chat 79 pattern)

```bash
python build.py
# gate: built=22, errored=0

PAT=$(grep '^NETLIFY_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
SITE=01b53b80-687e-4641-b088-115b7d5ef638
cd /mnt/user-data/outputs/dist && zip -qr /tmp/d.zip .
RESP=$(curl -s -X POST -H "Authorization: Bearer $PAT" -H "Content-Type: application/zip" \
  --data-binary @/tmp/d.zip "https://api.netlify.com/api/v1/sites/$SITE/deploys")
DEPLOY_ID=$(echo "$RESP" | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")

i=0; while [ $i -lt 30 ]; do i=$((i+1))
  STATE=$(curl -s -H "Authorization: Bearer $PAT" \
    "https://api.netlify.com/api/v1/sites/$SITE/deploys/$DEPLOY_ID" \
    | python3 -c "import sys,json;print(json.load(sys.stdin).get('state','?'))")
  [ "$STATE" = "ready" ] && break; [ "$STATE" = "error" ] && break; sleep 6
done
sleep 90
curl -sI -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | head -3
curl -s -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | grep -oE '"id":[ ]*"[a-z0-9_]+"' | sort -u | wc -l
```

### PR + close-out

Per `docs/refinement-sequence.md` §universal-rules: open PR against `main` with task list + files changed in body, do not merge. Operator merges.

```bash
PAT=$(grep '^GITHUB_PAT=' /mnt/project/CREDENTIALS.md | cut -d= -f2)
git push "https://x-access-token:${PAT}@github.com/10thMuses/lrp-tx-gis.git" refinement-sidebar-collapse
```

**Known constraint (carried from Chat 79):** the `GITHUB_PAT` currently in `CREDENTIALS.md` lacks PR-creation scope — returns `403 Resource not accessible by personal access token`. Branch push works; PR must be opened by operator via GitHub UI. Revisit PAT scopes if persistent blocker.

Update `WIP_OPEN.md` `## Next chat` → promote next stage. Append `WIP_LOG.md` entry for Chat 80.

---

## Sprint queue

### Chat 81+ — Chat 79 PR merge (operator) + Tax abatement BUILD

Chat 79 PR (`refinement-ui-polish-v2` → `main`) remains open pending operator merge. No functional dependency — prod already reflects branch via deploy `69ea9d1b8b51ad96ce674f5d`. Merge is git-history cleanup only.

**Tax abatement BUILD.** Approved scope: `docs/refinement-abatement-spec.md` §12 (locked 2026-04-23). Both standalone layer + facility annotation; all 23 counties with Trans-Pecos → Permian-core → peripheral sequencing; PDFs skipped; 2025+2026 filings only; Comptroller Ch. 312 spreadsheet manual-quarterly ingest; dedup by `(county, applicant_normalized, reinvestment_zone)`; weekly GitHub Actions; alerting deferred. Stage split: DISCOVERY closed (spec committed). BUILD unblocked after SIDEBAR COLLAPSE merges. Independent track otherwise.

### Mobile-friendly map

UI/UX backlog item. Responsive breakpoints, touch-friendly controls, pinch-zoom tuning, measure tool + print-to-PDF mobile usability, popup sizing. Candidate for promotion into `docs/refinement-sequence.md` when abatement BUILD concludes.

---

## Current workstream

UI POLISH v2 shipped Chat 79 — four-task bundle (hide `parcels_pecos` from sidebar; default-ON set caramba_north/counties/county_labels/cities/waha + esri_imagery + Caramba viewport; `ercot_queue` color split by technology; searchable multi-select dropdown filters via `CATEGORICAL_CAP=2000`). Prod deploy `69ea9d1b8b51ad96ce674f5d` on branch commit `c8ff838`. PR `refinement-ui-polish-v2` → `main` pending operator merge.

Next: SIDEBAR COLLAPSE (Chat 80) on independent track. ABATEMENT BUILD deferred to Chat 81+.

---

## Recent sessions

| Chat | Date | Outcome |
|---:|---|---|
| 70 | 2026-04-22 | Token-efficiency sweep (doc-only). |
| 71 | 2026-04-22 | Stage 3 closed + Stage 4 SIZING+WATERMARK shipped. Merges `ebe5634` + `026eff2`. Prod `69e96a36`. |
| 72 | 2026-04-23 | TCEQ REFRESH recon + data pull. 6 records geocoded. `tceq_pws`/`tceq_pbr`/`tceq_nsr_pending` scoped out. |
| 73 | 2026-04-23 | TCEQ refresh branch merged to main — `ea7e39d`. |
| 74 | 2026-04-23 | TCEQ data/config + EIA-860 research committed — `4292bf2`, `3aada1c`. Build deferred. |
| 75 | 2026-04-23 | Abatement discovery spec + multi-chat refinement rules — `92d25c72`. TCEQ built locally clean. Stopped pre-deploy. |
| 75b | 2026-04-23 | **TCEQ SHIP complete.** Deploy `69ea32c7d3733641c9a1bb7c`. 21→22 layers. Readme §2 ban-ship-it rule `939ff16`. |
| 76 | 2026-04-23 | **UI polish shipped.** 10 label/layout tweaks — `a379539`. Live on prod. |
| 77 | 2026-04-23 | **EIA-860 enrichment shipped.** 891/1367 plants enriched + `capacity_mw` coalesce — commit `9d40df4`, deploy `69ea73f92acb1109e87b4ddc`. Deploy path migrated to Netlify REST API after MCP proxy 503s. |
| 78 | 2026-04-23 | **MW-driven sizing on `eia860_plants` shipped.** Single SIZING_RULES entry + `L.radius: 6` fallback — commit `f334601`, deploy `69ea83a786cf7142db291f87`. 22 layers unchanged. |
| 79 | 2026-04-23 | **UI POLISH v2 shipped.** Four-task bundle on branch `refinement-ui-polish-v2`: sidebar_omit parcels_pecos; default ON set + Caramba viewport + esri_imagery; ercot_queue color split by technology; searchable multi-select dropdown filters. Branch commit `c8ff838`, deploy `69ea9d1b8b51ad96ce674f5d`. PR pending operator merge (PAT scope blocked auto-open). |

Full per-session detail in `WIP_LOG.md`.

---

## Prod status

- URL: https://lrp-tx-gis.netlify.app — **requires real User-Agent on curl** (default `curl/x.y.z` UA returns 503; use `-A "Mozilla/5.0"`). See `docs/settled.md` §Data sources.
- Last published deploy: `69ea9d1b8b51ad96ce674f5d` on branch commit `c8ff838` (Chat 79, branch `refinement-ui-polish-v2`).
- Main HEAD: `dc5aa16` (operator scheduled SIDEBAR COLLAPSE as Chat 80; will advance once Chat 79 PR merges).
- Auto-publish: unlocked.
- **Deploy path:** Netlify REST API via `NETLIFY_PAT`. MCP proxy path deprecated for this site.
- Layer set: 22 built clean.
- Prebuilt PMTiles (4): `parcels_pecos` 4.98 MB, `rrc_pipelines` 4.73 MB, `tiger_highways` 3.11 MB, `bts_rail` 2.16 MB.
- Sprite sheet: 5 icons @ 1x + 2x at `/sprite/sprite.png` + `sprite@2x.png`.
- Data-driven sizing live: `ercot_queue`, `solar`, `eia860_plants`, `eia860_battery`, `wind` (`capacity_mw`); `substations`, `tpit_subs`, `tpit_lines` (kV).
- UI state live (Chat 79): `parcels_pecos` sidebar-hidden; default-ON = caramba_north/counties/county_labels/cities/waha; default basemap = esri_imagery; default viewport = -102.9707/30.9112 z12; `ercot_queue` per-technology color; categorical filters auto-promoted to searchable multi-select dropdowns.
- Sizing gaps (static fallback): `eia860_plants` 476/1367 null `capacity_mw` → radius 6 fallback; `transmission` no voltage in geoms.
- **CDN warmup timing:** Standard post-deploy `sleep 90` per Chat 77 observation.

---

## Open backlog

**Standing watch item:** TCEQ diesel-genset NSR permits live only in CRPUB (not in `turbine-lst.xlsx`). Gap for data-center backup-power intelligence. Revisit only if TCEQ publishes bulk feed or operator authorizes CRPUB scrape.

**Data-pipeline gaps (non-blocking):**
- `eia860_plants`: 476/1367 rows still null on `capacity_mw`/`technology`/`fuel`. Chat 78 UI fallback handles cleanly; data fix requires plants not in EIA-860 Form 2024 (small / retired / non-utility-scale).
- `combined_points.csv` blank `operator` / `commissioned` on EIA point layers — Chat 79 dropdown filters now expose this (null values appear as filter option); data fix deferred unless prioritized.
- Cosmetic: prebuilt PMTiles feature counts show 0 in sidebar. Low priority.

**Infrastructure:**
- **Netlify MCP proxy blocker:** Proxy-based deploy path returning 503 on upload. REST API is canonical path. Watch: if REST API begins failing, re-check MCP proxy, then escalate to Netlify support.
- **GitHub PAT scope (new, Chat 79):** Current `GITHUB_PAT` in `CREDENTIALS.md` can push branches but returns `403 Resource not accessible by personal access token` on PR-creation endpoint. Operator opens PRs via GitHub UI. Revisit if auto-PR becomes worth PAT re-scope effort.

**Permanently excluded / settled:**
- `rrc_wells_permian`, `tceq_pws`, `tceq_pbr`, `tceq_nsr_pending` — see `docs/settled.md` §"Scoped-out data sources" and §"Data sources".

**UI/UX backlog (unscheduled):**
- **Collapsible sidebar.** Promoted to Chat 80 SIDEBAR COLLAPSE stage (see `## Next chat`).
- **Mobile-friendly map.** Responsive breakpoints, touch-friendly controls, pinch-zoom tuning, measure tool + print-to-PDF mobile usability, popup sizing. Candidate for promotion into `docs/refinement-sequence.md` after ABATEMENT BUILD.

**Other (non-GIS):**
- Grid Wire Vol. 7.
- Tier 2 water availability assessments, cluster intelligence sheets, Excel returns model.

---

## GitHub sync — live

Repo: `github.com/10thMuses/lrp-tx-gis`. Authority: `main` = canonical. Working dir: `/home/claude/repo/`. Protocol: `Readme.md` §7 + `docs/principles.md` §5.
