# OXY Data-Center-JV Dossier — Source & Handoff

This document explains how the **Occidental (OXY) infrastructure dossier** is
generated, so another assistant (e.g. a Claude.ai chat) can pick the work up,
edit it, merge it with another version, and re-render it without re-deriving
anything. Hand this file plus the scripts and HTML in this zip to that session.

## What it produces
- `OXY-Intelligence-Report.pdf` — ~21-page A4 portrait dossier.
- `OXY-Intelligence-Report.docx` — editable Word version (same content).
- Six maps (`oxy_map_*.png`) — overview, 50-mile Caramba-North proximity, and one per asset-type section (midstream / water / power / carbon).

The report is framed for a **hyperscale data-center joint venture** between the
Williams family (Caramba North, Pecos County) and OXY. It is a *subject-company*
profile of OXY only — no deal terms, no recommendations. Sources and raw
facility-database IDs live in the footnotes appendix, not the body.

## Document structure (what's on the page)
```
cover
intro page ........ executive summary (shaded cards) + linked TOC w/ page numbers + bios
§1 Footprint ....... overview map + 50-mile Caramba proximity map
§2 Public databases  ERCOT-queue / generation / air-permit TABLES (the map's underlying data)
§3 Midstream ....... map + business asset cards
§4 Water ........... map + cards
§5 Power & NET Power map + cards
§6 Carbon capture .. map + cards
Appendix A ......... Financial profile
Appendix B ......... Berkshire Hathaway relationship
Appendix C ......... Caveats & confidence
Appendix D ......... Sources & notes (all footnotes — every ID/citation lands here)
```

## Architecture (one content source + map renderer + report assembler)
```
scripts/oxy_assets_data.py   ← SINGLE SOURCE OF TRUTH for the asset cards
                               (§3–§6): every asset in plain business language +
                               geography + footnote text. EDIT ASSETS HERE.
        │
        ├── scripts/oxy_maps.py        (parameterized light-theme map renderer)
        │   scripts/oxy_build_maps.py  (driver: builds the 6 PNGs + oxy_map_keys.json)
        │
        └── scripts/build_oxy_report.py (assembles cover → intro → §1–§6 →
                │                         appendices → HTML; ALSO holds the exec
                │                         summary, §1 text, the §2 database tables,
                │                         the appendices, and the bios inline)
                ├── WeasyPrint  → OXY-Intelligence-Report.pdf
                └── scripts/build_oxy_docx.py (HTML → clean semantic HTML → pandoc) → .docx
```
The maps and the §3–§6 cards read the **same** `oxy_assets_data.py`, so the
picture and the prose never drift apart.

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
- Geo inputs (in the repo, not this zip): `combined_geoms.geojson` (counties), `data/tiger/primary_roads_wtx.geojson` (highways), `data/hifld/*.geojson` (pipelines), `combined_points.csv` (cities). If you only have this zip, the six `oxy_map_*.png` are already rendered — reuse them and skip step 1.

## How to edit content
- **Asset cards (§3–§6):** edit `scripts/oxy_assets_data.py`. Each asset is a dict:
  ```python
  {
    "section": "midstream|water|power|dac",   # which section it appears in
    "type": "gas|power|netpower|dac|water",    # marker style + map filter
    "status": "existing|planned|construction|demonstration|divested",
    "name": "...", "map_label": "short label for the map key",
    "lon": -102.58, "lat": 30.61,   # OR  "county": "PECOS"  (centroid-placed)
    "on_map": True,                 # False = mention in text, don't plot (off-map)
    "one": "plain-English one-liner (italic in the card)",
    "rows": [("Where","..."), ("What it does","..."), ("Scale","..."), ("Who controls it","...")],
    "jv": "why it matters for a data-center JV (blue callout)",
    "src": "footnote text — sources + raw IDs (EPA/EIA/RRC/PHMSA/TCEQ) live here",
  }
  ```
  Add an asset → append a dict; it auto-appears in its section and on the matching map.
- **Executive summary, §1 footprint text, §2 database tables, appendices (financials / Berkshire / caveats), bios, the TOC:** all inline in `build_oxy_report.py`.
- **Section intros** (the shaded JV-angled paragraphs): `SEC_INTRO` in `build_oxy_report.py`.

## Maps API
`oxy_maps.render(assets, out_path, title, ctx, extent=None, center=None, radius_mi=None, caramba=None)`
- `caramba=(lon,lat)` plots the Caramba North reference star on the map and includes it in the extent (passed to every map).
- `center=(lon,lat), radius_mi=50` draws the 50-mile proximity ring (the Caramba map).
- Omit center/radius → auto-fit to the plotted assets (the type maps); height is capped in CSS so caption+map+key fit one page.
- Returns the numbered key rows (written to `oxy_map_keys.json`, consumed by the report).

## Editorial rules baked in (keep these if you extend it)
1. **Business reader, no jargon** — translate technical facts to plain meaning; push raw IDs to `src`/footnotes (Appendix D), not the body.
2. **Each section starts on a new page**, opens with a 1–3 sentence JV-angled intro, and its title stays on one line.
3. Each asset-type section has its **own map**; the overview + 50-mile proximity maps lead §1; §2 carries the ERCOT/generation/permit **tables**.
4. **Don't imply false nearness** — the proximity map plots only assets with precise coordinates.
5. **No editorial "conclusions"** — present facts and JV-relevance; don't draw strategic verdicts for the reader.
6. Flag anything undisclosed / recently-changed / commonly-mis-stated in **Appendix C** rather than guessing.

## Known content caveats (most load-bearing)
See **Appendix C**. Highlights: NET Power's Odessa plant is now **80 MW** (not 300 MW Allam-cycle);
the 453 MW "TRIFECTA" queue project was **withdrawn (Apr 2026)** and was never announced — do not
present it as advancing; **no named hyperscaler** is attached to NET Power's plant; OXY's WES stake is
**~39.5%** and possibly for sale; OXY does **not** own the Cortez CO₂ pipeline (it owns Bravo); DAC is
barely economic. Goldsmith solar came online **Oct 2019**; the OxyChem cogen plants (Battleground/Deer
Park) left with the **Berkshire sale (Jan 2026)**.

## Related (not part of this report)
The same OXY data also powers a live GIS web map (separate deliverable): an "OXY — Occidental
Footprint" legend group of six filterable layers (power, midstream, ERCOT-queue, permits, water,
carbon) built by `scripts/build_oxy_map_layers.py` from the same public datasets. That is the
interactive map, not this PDF/DOCX dossier.
