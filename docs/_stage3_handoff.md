# Stage 3 — Visual Overhaul — Handoff

Read this file on clone. Execute unconditionally — no operator gate, no confirmation.

Branch: `refinement-visual-overhaul` (cut from `main` post-Stage-2 merge).
Scope: `docs/refinement-sequence.md` §Stage: VISUAL OVERHAUL (lines 91–111).

## State at handoff

- Branch created, no commits beyond `main`.
- Recon done — findings below. Do not redo.
- Local build not yet run on this branch. Run it after edits.

## Recon findings (authoritative — do not re-investigate)

### Current color palette (source of truth: `layers.yaml`)

Five overlapping blues/grays create the ambiguity the spec flags:

| Layer | Current | Issue |
|---|---|---|
| `counties` (outline) | `#64748b` slate | same hue as `rrc_pipelines` |
| `rrc_pipelines` | `#64748b` slate | collides with `counties` |
| `transmission` (≥100 kV) | `#0ea5e9` sky | OK as "live grid" anchor |
| `substations` | `#0369a1` mid-blue | OK, distinct from transmission |
| `tpit_subs` (Substation Upgrades) | `#075985` dark blue | reads same family as substations — should signal *planned* |
| `tpit_lines` (Transmission Upgrades) | `#38bdf8` pale sky | reads same family as transmission — should signal *planned* |

### Render hook locations

- `build_template.html` line **274** — `layerPaint(L)` is the single style function for all geoms.
- `build_template.html` line **157–163** — `ICON_MAP` uses Unicode emoji rendered via `text-field` symbol layer (not a real sprite sheet).
- `build_template.html` line **359** — symbol layer conditionally added if `ICON_MAP[L.id]` exists.
- Line layers already get white casing at `${lyrId}__casing` (line 337).
- Fill layers already get outline at `${lyrId}__outline` (line 348).

### Existing styling defaults

- Points: radius 3 (overridable), stroke 0.5 px white, 0.85 opacity.
- Lines: width 1.5 px, 0.85 opacity, white casing 3.5 px.
- Fills: 0.25 opacity default.

## Execution plan

### Step 1 — Palette revision in `layers.yaml`

Apply these swaps. Rationale embedded in comments is not needed; keep yaml clean.

| Layer | New color | Reason |
|---|---|---|
| `rrc_pipelines` | `#7c2d12` (dark orange-brown) | separate fossil hydrocarbon infra from grid |
| `tpit_subs` | `#b45309` (burnt amber) | planned-upgrade amber family, dark |
| `tpit_lines` | `#f59e0b` (amber) | planned-upgrade amber family, matches existing "Planned" badge |
| `counties` | `#475569` (darker slate) | reference outline, lower visual weight |

Leave untouched: `transmission` `#0ea5e9`, `substations` `#0369a1` (these are the canonical grid blues), all Generation layers (already distinct), all Reference/Land layers except `counties`.

### Step 2 — Contrast/weight bump in `build_template.html` `layerPaint()`

- Point default radius `3 → 4`; keep `L.radius` override.
- Point stroke width `0.5 → 1.2`; keep white `#ffffff`.
- Point opacity `0.85 → 0.9`.
- Line width `1.5 → 2`; casing width `3.5 → 4.5` (keep proportional 1:2.25 ratio).
- Fill-outline opacity `0.9 → 1.0`, width `1.5 → 2`.

### Step 3 — Sprite sheet for semantic icons

Replace the emoji `ICON_MAP` approach. Generate real sprite files:

1. Create `dist/sprite/` dir.
2. Write 5 SVG icons inline in a Python generator script (don't pull external assets — keep repo self-contained):
   - `solar` — yellow sun (filled disc + 8 rays), fill `#eab308`
   - `wind` — three-bladed windmill silhouette, fill `#166534`
   - `battery` — horizontal battery outline with fill bar, stroke `#991b1b`, fill `#dc2626`
   - `plant` — factory/smokestack silhouette, fill `#9a3412`
   - `well` — teardrop/water-drop outline, fill `#7c3aed`
3. Rasterize each SVG to 48×48 PNG via `cairosvg` (available in env) or Pillow + `svglib`. Test `python3 -c "import cairosvg"` first; fall back to Pillow if unavailable.
4. Composite into single `sprite.png` (horizontal strip, 48 px tall × N×48 wide) + `sprite.json` manifest with `{name: {x, y, width, height, pixelRatio}}` entries.
5. Also emit `sprite@2x.png` at 96×96 and `sprite@2x.json` (same JSON with `pixelRatio: 2` and doubled coords).
6. In `build_template.html`:
   - Add `sprite: '/sprite/sprite'` to the `rasterStyle()` return (and same in `vectorStyle()` if present — check; if only raster, that's sufficient for current basemaps).
   - Change the `ICON_MAP[L.id]` branch (line ~359) from `text-field` symbol layer to `icon-image` symbol layer: `'icon-image': ICON_MAP[L.id]`, `'icon-size': 0.6` (so 48 px → 28 px on screen), `'icon-allow-overlap': true`.
   - Update `ICON_MAP` to string keys (sprite names), not emoji codepoints:
     ```js
     const ICON_MAP = { solar: 'solar', wind: 'wind', eia860_battery: 'battery', eia860_plants: 'plant', wells: 'well' };
     ```
   - Remove the `text-font` and `text-halo-*` paint props from that layer — they're text-layer only. For icon halo, use `icon-halo-*` if desired, but cleanest is to bake a white ring into the SVG itself.

### Step 4 — `build.py` sprite generation step

Add a function `build_sprite_sheet()` that runs at build start, writes `dist/sprite/sprite.png`, `sprite.json`, `sprite@2x.png`, `sprite@2x.json`. Call once before the per-layer loop. Idempotent (overwrite OK). Do NOT add sprite files to `.gitignore` — commit the generated artifacts so Netlify deploy from repo works without re-running the generator.

Actually: `dist/` should already be gitignored. Check `.gitignore` first. If `dist/` is gitignored, the sprite must be written to a non-ignored path OR the generator must run in Netlify build. Simplest: write sprite to `sprite/` at repo root (not under `dist/`), commit it, serve via Netlify with same path. Template reference becomes `sprite: '/sprite/sprite'` → Netlify serves from repo root.

### Step 5 — Build + verify

```
cd /home/claude/repo
python3 build.py
ls -la dist/tiles/ | wc -l       # should be 21 pmtiles + dir entries
ls -la sprite/                   # should show sprite.png, sprite.json, @2x variants
```

Open `dist/index.html` in head inspection: confirm `sprite:` key emitted, ICON_MAP updated.

### Step 6 — Commit cadence (per Readme §7.7)

Commit per step, not batched:

1. `palette: separate pipelines, TPIT upgrades, county outline` — `layers.yaml` only
2. `style: bump point/line weight + opacity` — `build_template.html` layerPaint only
3. `sprite: add generator + assets` — `build.py` + `sprite/*`
4. `sprite: wire icon-image layer, retire emoji ICON_MAP` — `build_template.html` ICON_MAP + symbol layer
5. Build verify. If clean, delete this handoff doc (`git rm docs/_stage3_handoff.md`), commit, push.

### Step 7 — PR

`gh pr create` against `main`. Title: "Stage 3 — Visual Overhaul". Body: bullet list of the 4 commits above + before/after note on the palette ambiguity resolution. Do not merge. Operator merges.

### Step 8 — WIP update on `main`

After PR opens: checkout `main`, update `WIP_OPEN.md` Current workstream block + append `WIP_LOG.md` session row. Commit + push on `main` (doc-only, Git Data API tree commit acceptable but clone-bracket is simpler if you're already cloned).

## Budget expectations

- Recon: done. Skip.
- Palette edit: 4 lines in yaml, ~1 KB.
- `layerPaint` edit: ~10 lines, ~1 KB.
- Sprite generator: ~80 lines Python, ~5 KB.
- Sprite raster output: ~20 KB for PNGs, emit once.
- Template wire: ~15 lines, ~1 KB.
- Build: typical ~10 KB tool output.
- Commits + push: 4 commits × ~2 KB each.
- **Total target ~60 KB.** Well under chat ceiling.

## Boundary flags

- If `cairosvg` and `svglib` both fail: fall back to hand-drawn 48×48 PNGs generated directly via Pillow `ImageDraw` primitives (circles, rectangles). Icons will be cruder but functional.
- If `dist/` is NOT gitignored: write sprite there, no repo-root `sprite/` needed. Check `.gitignore` Step 3.
- If build.py discovers unexpected `prebuilt: true` interaction with sprite step: sprite gen is independent of layer build; run it unconditionally before layers.
- Do NOT touch Generation layer colors — they are already semantically distinct (green wind, yellow solar, red battery, orange plants).
- Do NOT add new filter-UI interaction or bug fixes. Stage scope is visual only.
