# OXY — Pecos County appraisal accounts (2025 certified roll)
**Pulled:** 2026-06-24 · **Source:** Pecos County Appraisal District, *2025 Certified Real & Personal Appraisal Roll* (Excel/CSV export), `www.pecoscad.org/Forms/ExcelDownload` → file `1753382930_2025...Real-Personal...20250718_082826.csv` (certified 2025-07-18). Owner filter: `Name` contains OXY / OCCIDENTAL / ALTURA. 32,139-row roll → 45 matching accounts.
## ⚠️ Read this first — surface, not minerals
These 45 accounts are **fee-surface land** (state category **D1** = qualified ag/open-space land, **E** = rural land + improvements). **They are not the oil-&-gas mineral interests.**
The downloadable certified roll contains **zero category-G (oil & gas mineral) accounts** — confirmed across all 32,139 rows. Pecos CAD's minerals are appraised by **Pritchard & Abbott, Inc.** on a *separate* mineral roll that the district does **not** publish as a downloadable file. The only public access to OXY's mineral (royalty/working-interest) accounts is the `esearch.pecoscad.org` / `propaccess.pecoscad.org` search portal — which **refuses all datacenter/cloud egress** (TLS connection reset / `SSL_ERROR_SYSCALL`; server-side fetch returns HTTP 503). Same datacenter-egress block class already logged for `reevescounty.org`. The mineral table is therefore **not pullable from this environment** — see unblock paths at the bottom.
What *is* below is genuinely useful: OXY's **fee-surface footprint** in Pecos — the surface-ownership inventory the OXY partnership memo (2026-06-19) flagged as a needed data-acquisition step.
## Summary
- **45 accounts**, 3 OXY entities · **17,503 surface acres** · market **$1,748,860** · net taxable **$599,600**
- **OCCIDENTAL WEST TEXAS OVERTHRUST INC** — 27 accounts · 14,273 ac · market $1,199,710
- **OCCIDENTAL PERMIAN LTD** — 15 accounts · 2,460 ac · market $191,600
- **OXY USA INC** — 3 accounts · 770 ac · market $357,550

_Note: low taxable vs. market reflects D1 ag-use (productivity) valuation. Legal descriptions are abstract/survey/section level (e.g. `SEC 92, BLK 3 CCSD&RGNG NRR`), not tract-precise polygons._

## All 45 accounts (by market value)
| Account | Owner | Cat | Acres | Market $ | Taxable $ | Legal |
|---|---|---|--:|--:|--:|---|
| 00707-01018-00100-000000 | OXY USA Inc | D1 | 480 | 257,580 | 202,100 | 5064  C-3 PSL   SEC 18 |
| 00707-01007-00103-000000 | OXY USA Inc | D1 | 131 | 89,250 | 81,280 | 5063  C-3 PSL   SEC 7 NE PT |
| 00003-04092-00100-000000 | OXY W TX Overthrust | D1 | 640 | 60,690 | 6,340 | 6943  3 CCSD & RGNG SEC 92 |
| 00003-04023-00100-000000 | OXY W TX Overthrust | D1 | 640 | 59,040 | 6,310 | 2362  3 CCSD & RGNG SEC 23 |
| 00003-04037-00100-000000 | OXY W TX Overthrust | D1 | 640 | 58,760 | 6,470 | 2398  3 CCSD & RGNG SEC 37 |
| 00003-04050-00100-000000 | OXY W TX Overthrust | D1 | 640 | 58,760 | 6,470 | 7286  3 CCSD & RGNG SEC 50 |
| 00003-04036-00100-000000 | OXY W TX Overthrust | D1 | 640 | 57,630 | 6,140 | 7281  3 CCSD & RGNG SEC 36 |
| 00003-04022-00100-000000 | OXY W TX Overthrust | D1 | 640 | 55,760 | 6,060 | 7523  3 CCSD & RGNG SEC 22 |
| 00003-04051-00100-000000 | OXY W TX Overthrust | D1 | 640 | 55,760 | 6,060 | 2405  3 CCSD & RGNG SEC 51 |
| 00003-04121-00100-000000 | OXY W TX Overthrust | D1 | 642 | 55,580 | 5,610 | 2513  3 CCSD & RGNG SEC 121 |
| 00003-04079-00100-000000 | OXY W TX Overthrust | D1 | 640 | 54,830 | 5,290 | 2423  3 CCSD & RGNG SEC 79 |
| 00003-04064-00100-000000 | OXY W TX Overthrust | D1 | 640 | 54,560 | 5,780 | 7522  3 CCSD & RGNG SEC 64 |
| 00003-04078-00100-000000 | OXY W TX Overthrust | D1 | 640 | 52,200 | 4,950 | 5664  3 CCSD & RGNG SEC 78 |
| 00003-04120-00100-000000 | OXY W TX Overthrust | D1 | 642 | 51,480 | 5,310 | 6261  3 CCSD & RGNG SEC 120 |
| 00003-04009-00200-000000 | OXY W TX Overthrust | D1 | 623 | 51,250 | 5,270 | 2345  3 CCSD & RGNG SEC 9 |
| 00003-04106-00100-000000 | OXY W TX Overthrust | D1 | 640 | 51,070 | 5,240 | 5669  3 CCSD & RGNG SEC 106 |
| 00003-04065-00100-000000 | OXY W TX Overthrust | D1 | 640 | 50,360 | 5,100 | 2352  3 CCSD & RGNG SEC 65 |
| 00003-04008-00200-000000 | OXY W TX Overthrust | D1 | 615 | 49,720 | 5,130 | 6900  3 CCSD &RGNG SEC 8 |
| 00003-04093-00100-000000 | OXY W TX Overthrust | D1 | 640 | 49,710 | 4,950 | 2418  3 CCSD & RGNG SEC 93 |
| 00003-04107-00100-000000 | OXY W TX Overthrust | D1 | 640 | 49,640 | 4,790 | 2517  3 CCSD & RGNG SEC 107 |
| 00143-00006-00100-000000 | OXY Permian Ltd | E | 523 | 42,160 | 42,160 | 8680  143 T&STL SEC 6 UND INT |
| 00143-00008-00100-000000 | OXY Permian Ltd | E | 491 | 41,300 | 41,300 | 8678  143 T&STL SEC 8 UND INT |
| 00143-00010-00100-000000 | OXY Permian Ltd | E | 553 | 38,590 | 38,590 | 8679  143 T&STL SEC 10 UND INT |
| 00003-04038-00100-000000 | OXY W TX Overthrust | D1 | 321 | 26,940 | 2,910 | 7526  3 CCSD & RGNG SEC 38 E/2 |
| 00003-04049-00100-000000 | OXY W TX Overthrust | D1 | 321 | 26,590 | 2,830 | 2404  3 CCSD & RGNG SEC 49 E/2 |
| 00003-04077-00300-000000 | OXY W TX Overthrust | D1 | 321 | 26,510 | 2,550 | 2424  3 CCSD & RGNG SEC 77      E/2 |
| 00003-04105-00200-000000 | OXY W TX Overthrust | D1 | 321 | 25,890 | 2,620 | 2518  3 CCSD & RGNG SEC 105 E/2 |
| 00003-04122-00100-000000 | OXY W TX Overthrust | D1 | 321 | 25,800 | 2,620 | 5668  3 CCSD & RGNG SEC 122 E/2 |
| 00003-04094-00100-000000 | OXY W TX Overthrust | D1 | 321 | 25,240 | 2,550 | 7284  3 CCSD & RGNG SEC 94 E/2 |
| 00003-04021-00100-000000 | OXY W TX Overthrust | D1 | 321 | 24,390 | 2,380 | 2361  3 CCSD & RGNG SEC 21 |
| 00003-04066-00100-000000 | OXY W TX Overthrust | D1 | 321 | 24,210 | 2,340 | 5663  3 CCSD & RGNG SEC 66 E/2 |
| 00011-02026-00100-000000 | OXY Permian Ltd | E | 308 | 21,650 | 21,650 | 8118  11 H&GN SEC 26 UND INT |
| 00003-04010-00200-000000 | OXY W TX Overthrust | D1 | 224 | 17,340 | 1,670 | 6901  3 CCSD & RGNG SEC 10 NE PT |
| 00713-00082-00500-000000 | OXY USA Inc | D1 | 160 | 10,720 | 880 | 9475  OW CCSD&RGNG SEC 82 SE/4 |
| 00010-02096-00501-000000 | OXY Permian Ltd | E | 65 | 6,380 | 6,380 | 7095  10 H&GN  SEC 96 UND 65/640 INT |
| 00010-02098-00900-000000 | OXY Permian Ltd | E | 65 | 6,380 | 6,380 | 7097  10  H&GN   SEC 98 UND 65/640 INT |
| 00011-02032-00600-000000 | OXY Permian Ltd | E | 80 | 6,340 | 6,340 | 8698  11 H&GN SEC 32 |
| 00010-02100-00203-000000 | OXY Permian Ltd | E | 60 | 6,230 | 6,230 | 8419  10 H&GN  SEC 100 UND 6/64 INT |
| 00010-02110-00101-000000 | OXY Permian Ltd | E | 60 | 5,200 | 5,200 | 8422  10 H&GN  SEC 110 UND 6/64 INT |
| 00010-02102-00201-000000 | OXY Permian Ltd | E | 65 | 4,360 | 4,360 | 7651  10 H&GN SEC 102 UND 65/640 INT |
| 00010-02106-00203-000000 | OXY Permian Ltd | E | 60 | 4,020 | 4,020 | 8420  10 H&GN   SEC 106 UND 6/64 INT |
| 00178-00035-01301-000000 | OXY Permian Ltd | E | 40 | 3,360 | 3,360 | 4342  178 TC SEC 35 SW/4 SW/4 |
| 00713-00012-01101-000000 | OXY Permian Ltd | E | 40 | 2,410 | 2,410 | 9302  OW J DONOVAN TR 4-7       SEC 12 |
| 00010-02108-00101-000000 | OXY Permian Ltd | E | 30 | 2,010 | 2,010 | 8421  10 H&GN   SEC 108 UND 3/64 INT |
| 00713-00012-00201-000000 | OXY Permian Ltd | E | 20 | 1,210 | 1,210 | 9304  OW J DONOVAN TR 8-11      SEC 12 |

## Getting the actual mineral (category-G) accounts — unblock paths
1. **You pull `esearch` from a browser (~5 min, free).** esearch.pecoscad.org → Advanced/Owner search → run `OXY`, `OCCIDENTAL`, `ALTURA` → filter to category **G1/G2/G3** → export/print → send me the file; I'll structure it into the same table format (owner · account · lease/operator/RRC · interest · legal · market value).
2. **Open-records request** to Pecos CAD (or directly to Pritchard & Abbott) for the certified **mineral roll** export. Districts typically email a CSV within 1–10 business days; I parse it on arrival.
3. **Paid aggregator with credentials** — TexasFile, MineralHolders.com, or CADdata. If you have/open an account, several expose exports or an API I can run with your login.
4. **Residential-proxy egress (paid)** — the same unblock noted for the Reeves item. With non-datacenter egress I can scrape `esearch` directly and build the full mineral table end-to-end.
