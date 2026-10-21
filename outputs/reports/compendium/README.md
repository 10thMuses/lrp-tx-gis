# Energy & AI Infrastructure Deal-Terms Compendium

Deal-transaction comps reference: per-unit economics across the physical power
and compute stack, each sector priced in its native unit ($/MW & $/MW-yr for
leases, $/kW for generation/nuclear/geothermal, $/hp for compression, $/MWh &
$/MW-day for power purchases/capacity, $/acre for land, $/AF→bbl/d for water).

All figures are from primary/named sources; "n/d" marks anything not disclosed
and is never estimated.

## Files
- `deals3.html` — source document (self-contained, prints to Letter).
- `charts3.py` — matplotlib chart generator → `assets/*.png` (NAVY/GOLD/TEAL palette).
- `render3.py` — Playwright Chromium → `Energy_AI_Infra_Deal_Terms_<date>.pdf`.
- `assets/` — generated chart PNGs embedded by the HTML.

## Rebuild
```bash
pip install matplotlib playwright && python3 -m playwright install --with-deps chromium
python3 charts3.py            # regenerate charts
COMPENDIUM_DATE=YYYY-MM-DD python3 render3.py   # render PDF
```

## Refresh discipline
On each update: re-run a news sweep for deal transactions dated after the
current dateline, fold qualifying deals into the right section table with a Date
entry, advance the masthead dateline, and keep "n/d" discipline (no estimates).
