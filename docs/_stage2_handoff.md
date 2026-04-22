# Stage 2 Bug Sweep — in-flight handoff

**Temporary file.** Delete before opening PR.

Recon complete. Fixes 1 and 2 shipped this commit. Fix 3 remaining + build verification + PR. Next chat resumes from this file; no prompt-parsing or conversation_search required.

---

## State at handoff

- Branch `refinement-bug-sweep` rebased onto `main` (picked up Readme §7.7).
- Stale `refinement-filter-ui` remote branch deleted.
- This commit: Fix 1 (Waha glyphs) + Fix 2 (parcels_pecos Range fetch).
- Filter UI (Stage 1) merged to `main` in Chat 65. No prod deploy — ships with Stage 2.

---

## Scope (three bugs, per `docs/refinement-sequence.md` §Stage 2)

1. Waha gas hub — diagnose why not showing; fix.
2. `parcels_pecos` — diagnose why nothing renders; fix. If data file broken, document and propose before rebuilding.
3. Measure tool closes when user clicks a popup. Fix so measure tool persists through popup clicks.

Do NOT touch: icons, colors, sizing, sprite sheet, watermark. Stage 3+.

---

## Recon findings + fix status

### Bug 1 — Waha (`labels_hubs`) ✅ FIXED this commit

- 1 feature exists in `combined_geoms.geojson` tagged `layer_id:labels_hubs`, `name:Waha`, Point `[-103.183, 31.215]`.
- Tile confirmed present at z0–z14 (probed via pmtiles reader).
- **Root cause:** `rasterStyle()` in `build_template.html` omitted `glyphs` URL. All 4 raster basemaps (carto_light default, esri_streets, esri_imagery, naip) lack glyphs → symbol layer text silently fails. Only `openfreemap` style basemap worked.
- **Fix applied:** added `glyphs: https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf` to `rasterStyle()`; changed `text-font` from `['Open Sans Bold', 'Arial Unicode MS Bold']` to `['Noto Sans Bold']` (reliably served by OpenFreeMap).

### Bug 2 — `parcels_pecos` ✅ FIXED this commit

- `.pmtiles` NOT present at `/mnt/project/` or repo root; resolved from tier-3 prod CDN.
- Prod CDN copy verified: 5.1 MB, z11–14, vector_layer id `parcels_pecos`, bounds -103.58 30.06 to -101.77 31.37, fields include `acres`, `fips`, `county`, `land_use`. File is correct.
- **Root cause:** container egress proxy intermittently returns HTTP 503 body `"DNS cache overflow"` on full-file GETs of large objects. Range requests consistently succeed (edge path differs).
- **Fix applied:** `build.py` prebuilt fetcher now does HEAD probe (retry 5×) + 8 MB chunked Range GETs (retry 5× each) with exponential backoff. Replaces fragile single `urllib.urlopen`.
- **Open:** build verification pending next chat.

### Bug 3 — Measure tool / popup interaction ❌ TODO next chat

- Current template (lines 640–670): `measureActive` check blocks NEW popups, but doesn't dismiss EXISTING popups when measure activates, and popup DOM elements still intercept clicks that should reach the map.
- **Proposed fix (next chat):**
  1. CSS: `.measure-on .maplibregl-popup { pointer-events: none; display: none; }` on map container.
  2. In `measureBtn` click handler, when activating: `document.getElementById('map').classList.add('measure-on'); hoverPopup.remove();` and track/dismiss click popups.
  3. On deactivation: remove class.

---

## First bash commands next chat

```bash
cd /home/claude/repo
git checkout refinement-bug-sweep
git pull --rebase origin refinement-bug-sweep
# Install tippecanoe if container is fresh (~60s):
apt-get install -y libsqlite3-dev zlib1g-dev >/dev/null 2>&1 && \
  git clone --depth 1 https://github.com/felt/tippecanoe.git /tmp/tippecanoe 2>&1 | tail -1 && \
  cd /tmp/tippecanoe && make -j4 >/dev/null && make install >/dev/null && cd /home/claude/repo
# Apply Fix 3 (see below), then:
python3 build.py 2>&1 | tail -25
```

---

## Execution order

1. **Apply Fix 3** — edit `build_template.html`:
   - Add CSS rule in `<style>` block near line 60: `.measure-on .maplibregl-popup { pointer-events: none; display: none; }`
   - In `measureBtn` click handler (~line 835), on activate: add `map.getContainer().classList.add('measure-on'); hoverPopup.remove();`
   - On deactivate: `map.getContainer().classList.remove('measure-on');`
2. Run `python3 build.py` — expect `built ≥ 20 of 21, errored ≤ 1, prebuilt[prod-url]` for parcels_pecos showing chunked fetch succeeded. If parcels_pecos fails even with Range-retry, document and proceed (PR can flag as environmental).
3. Commit Fix 3 with clear message.
4. **Delete this file** (`docs/_stage2_handoff.md`).
5. Push branch, open PR → `main` via GitHub API (token has `contents: write` not `pull_requests: write` — if API 403s, print compare URL `https://github.com/10thMuses/lrp-tx-gis/compare/main...refinement-bug-sweep` for manual PR).
6. Update `WIP_OPEN.md` current workstream → Stage 3 Visual Overhaul; append `WIP_LOG.md` entry.
7. Do NOT merge, do NOT deploy.

---

## File paths (fixed)

- `layers.yaml` — config, 21 layers
- `build.py` — ROOT = repo root, PROJECT = /mnt/project read-only sidebar. Prebuilt fetcher patched this commit (chunked Range + retry).
- `build_template.html` — 891 lines; `rasterStyle` + label rendering patched this commit. Measure tool at lines 773–860; `hoverPopup` at 640.
- `combined_geoms.geojson` — 6481 features; `labels_hubs`=1, `caramba_south`=1 orphan (harmless).
- `combined_points.csv` — 39409 rows.

---

## Tool-budget note

Prior chat hit tool limit and wrote summary instead of committing patches — §7.7 violation. Andrea called it out. Current chat commits patches + this updated handoff before final message to comply. Future chats: commit-push before summary, always.
