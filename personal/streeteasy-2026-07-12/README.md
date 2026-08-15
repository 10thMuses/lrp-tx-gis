# StreetEasy Listings — shared 7/12/2026

Personal apartment-search compilation. Not part of the LRP Texas Energy GIS map or intel product — parked in this repo to reuse its tooling.

31 unique rental listings (59 shares, deduplicated) from a StreetEasy self-chat export dated 7/12/2026. All downtown Manhattan: East Village (10), West Village (8), Tribeca (5), Greenwich Village (3), West Chelsea (3), Noho (1), Soho (1). Rents $6,995–$18,000, median $10,375.

## Deliverables

| File | What it is |
|---|---|
| `streeteasy_listings_2026-07-12.xlsx` | Every data point per listing — 55 columns: link, address, rent, net-effective/concessions, beds/baths/rooms, sqft, unit type, listed/available dates, days on market, private & shared outdoor space, views, unit features, building amenities, doorman/parking/storage, building name/year/floors/units, brokerage + license, fees, security deposit, price history, unit rental history, area median comp, photo/video/floorplan counts, coordinates, full description. Plus a Summary sheet. |
| `map.html` | Interactive map — open in any browser. Markers colored by neighborhood and labeled with rent; click a marker or sidebar card for full details, photo, and a link to the listing. Filters: neighborhood chips, beds, price band, sort. Leaflet is inlined (no CDN dependency); only basemap tiles and photos need network. |
| `report.pdf` | Print-ready report: overview stats, listing index, then one detailed section per listing. |
| `data/listings.json` | The parsed dataset (source of truth for all three outputs). |
| `data/research_fill.json` | Gap-fills researched from non-StreetEasy sources, with source + confidence. |

## Data notes

- Scraped from the 31 listing pages on 7/13/2026; parsed out of StreetEasy's embedded structured data (RSC flight payload + JSON-LD), not screen text.
- Coordinates are building coordinates from StreetEasy's own geodata.
- **Sq ft:** StreetEasy publishes it for only 10 of 31 units. Web research (Zillow, RentHop, Apartments.com, CityRealty, broker sites) recovered one more: 528 E 6th St #2 ≈ 1,500 sq ft (Corcoran's own listing). The remaining 20 are published nowhere — left blank rather than estimated. One trap worth knowing: the "1,100 sq ft" cited around 450 W 17th St #542 is the private terrace, not the interior.
- **Broker fees:** none on any fee schedule (post-FARE Act). Fee columns carry application/move-in/deposit/pet/amenity fees as listed.
- 562 Hudson St year built (1900) filled from building records; flagged in `research_fill.json`.

## Rebuild

```bash
cd scripts
python3 build_xlsx.py   # needs openpyxl
python3 build_map.py    # needs data/leaflet.js + leaflet.css (fetch from unpkg leaflet@1.9.4)
python3 build_pdf.py    # needs reportlab
```

`parse_listings.py` regenerates `data/listings.json` from raw listing HTML pages (not committed — re-fetch with a `WhatsApp/2.x` user agent, which passes StreetEasy's bot wall; set `SE_WORKDIR` to the directory holding `pages/`).
