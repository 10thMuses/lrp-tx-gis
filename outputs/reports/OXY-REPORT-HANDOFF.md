# OXY Data-Center-JV Dossier — Source & Handoff

This document explains how the **Occidental (OXY) infrastructure dossier** is
generated, so another assistant (e.g. a Claude.ai chat) can pick the work up,
edit it, and re-render it without re-deriving anything. Hand this file plus the
five scripts below to that session.

## What it produces
- `OXY-Intelligence-Report.pdf` — 20-page A4 portrait dossier.
- `OXY-Intelligence-Report.docx` — editable Word version (same content).
- Six maps (`oxy_map_*.png`) — overview, 50-mile Caramba-North proximity, and one per asset-type section.

The report is framed for a **hyperscale data-center joint venture** between the
Williams family (Caramba North, Pecos County) and OXY. It is a *subject-company*
profile of OXY only — no deal terms, no recommendations. Sources and raw
facility-database IDs live in the footnotes appendix, not the body.

## Architecture (one content source, two renderers)

```
scripts/oxy_assets_data.py   ← SINGLE SOURCE OF TRUTH: every asset (business
                               language) + geography + footnote text. EDIT HERE.
        │
        ├── scripts/oxy_maps.py        (parameterized light-theme map renderer)
        │   scripts/oxy_build_maps.py  (driver: builds the 6 PNGs + oxy_map_keys.json)
        │
        └── scripts/build_oxy_report.py (assembles cover → intro → §1–§5 → appendices → HTML)
                │
                ├── WeasyPrint  → OXY-Intelligence-Report.pdf
                └── scripts/build_oxy_docx.py (HTML→clean semantic HTML→pandoc) → .docx
```

The maps and the report read the **same** `oxy_assets_data.py`, so the picture
and the prose can never drift apart.

## Regenerate (run order, from repo root)
```bash
python3 scripts/oxy_build_maps.py            # 1. maps + oxy_map_keys.json
python3 scripts/build_oxy_report.py          # 2. HTML
python3 -c "from weasyprint import HTML; HTML('outputs/reports/oxy-intelligence-report.html').write_pdf('outputs/reports/OXY-Intelligence-Report.pdf')"   # 3. PDF
python3 scripts/build_oxy_docx.py            # 4. DOCX
```

## Dependencies
- Python: `matplotlib`, `weasyprint`, `pyshp` (maps/PDF), `python-docx` (DOCX validation only).
- `pandoc` on PATH (DOCX export).
- Fonts (Inter) load from a public CDN at render time — keep network access on, or swap the `@font-face` block in `build_oxy_report.py` for a local font.
- Geo inputs already in the repo: `combined_geoms.geojson` (counties), `data/tiger/primary_roads_wtx.geojson` (highways), `data/hifld/*.geojson` (pipelines), `combined_points.csv` (cities).

## How to edit content
Almost everything is in **`scripts/oxy_assets_data.py`**. Each asset is a dict:

```python
{
  "section": "midstream|water|power|dac",   # which section it appears in
  "type": "gas|power|netpower|dac|water",    # marker style + map filter
  "status": "existing|planned|construction|demonstration|divested",
  "name": "...", "map_label": "short label for the map key",
  "lon": -102.58, "lat": 30.61,   # OR  "county": "PECOS"  (centroid-placed)
  "on_map": True,                 # False = mention in text, don't plot (e.g. NM/CA/S-TX)
  "one": "plain-English one-liner (italic in the card)",
  "rows": [("Where","..."), ("What it does","..."), ("Scale","..."), ("Who controls it","...")],
  "jv": "why it matters for a data-center JV (blue callout)",
  "src": "footnote text — sources + raw IDs (EPA/EIA/RRC/PHMSA/TCEQ) live here",
}
```
- Add an asset → append a dict; it auto-appears in its section and on the matching map.
- Section intros (the shaded JV-angled paragraphs) and the executive summary are in `build_oxy_report.py` (`SEC_INTRO` and `INTRO`).
- Financials / Berkshire / caveats appendices are inline HTML in `build_oxy_report.py` (`APPX`).
- Bios are in `build_oxy_report.py` (`INTRO`).

## Maps API
`oxy_maps.render(assets, out_path, title, ctx, extent=None, center=None, radius_mi=None, subtitle=None)`
- `center=(lon,lat), radius_mi=50` draws the proximity ring (used for the Caramba map).
- Omit both → auto-fit to the plotted assets (used for the type maps).
- Returns the numbered key rows (written to `oxy_map_keys.json`, consumed by the report).

## Editorial rules baked in (keep these if you extend it)
1. Business reader, no jargon — translate technical facts into plain meaning; push IDs to `src`/footnotes.
2. Every section starts on a new page; each opens with a 1–3 sentence JV-angled intro.
3. Each asset-type section has its own map; the overview + 50-mile proximity maps lead §1.
4. Don't imply false nearness — the proximity map plots only assets with precise coordinates.
5. Flag anything undisclosed/changed/mis-stated in Appendix C rather than guessing.

## Known content caveats
See **Appendix C** of the report. Most load-bearing: NET Power's Odessa plant is now 80 MW
(not 300 MW Allam-cycle); no named hyperscaler is yet attached to it; OXY's WES stake is
~39.5% and possibly for sale; OXY does not own the Cortez CO₂ pipeline; DAC is barely economic.
