"""Generate the OXY Partnership executive deck (HTML) and render to PDF.

Self-contained, fixed-canvas 1280x720 landscape slides. The OXY footprint
locator (slide 8) and the FracFocus chart (slide 10) are DATA-DRIVEN: the
locator projects the real coordinates from data/oxy/oxy_assets.geojson and the
Caramba North centroid; the chart uses the FracFocus county aggregation.

Run: python3 scripts/build_oxy_deck.py   (writes HTML; PDF rendered separately)
"""
import json, os, math, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_HTML = os.path.join(ROOT, "outputs", "reports", "oxy-partnership-deck.html")

CARAMBA = (-102.9747, 30.9032)  # lon, lat (report centroid)

# ---- load OXY assets ----
gj = json.load(open(os.path.join(ROOT, "data", "oxy", "oxy_assets.geojson"), encoding="utf-8"))
ASSETS = []
for ft in gj["features"]:
    lon, lat = ft["geometry"]["coordinates"][:2]
    p = ft["properties"]
    ASSETS.append({"name": p["name"], "cat": p["category"], "county": p.get("county", ""),
                   "lon": lon, "lat": lat})

# classify for the map colour/label
def kind(a):
    n = a["name"].lower()
    if "santa garcias" in n: return "solar"
    if "goldsmith" in n: return "solar"
    if "wasson" in n or "block 31" in n or "century" in n: return "plant"
    return "sub"

COL = {"plant": "#f59e0b", "solar": "#fbbf24", "sub": "#38bdf8", "caramba": "#fb7185"}

# FracFocus OXY-family completions by county (Occidental + Anadarko + CrownQuest)
FRAC = [("Loving", 1075, "abut"), ("Reeves", 1010, "abut"), ("Howard", 803, "near"),
        ("Glasscock", 422, "near"), ("Ector", 414, "near"), ("Ward", 337, "abut"),
        ("Andrews", 287, "near"), ("Crane", 18, "abut"), ("Pecos", 24, "subject")]

# ---------------- SVG footprint locator ----------------
def build_locator():
    permian = [a for a in ASSETS if kind(a) != "solar" or "goldsmith" in a["name"].lower()]
    # main frame = all except Santa Garcias (South TX outlier)
    main = [a for a in ASSETS if "santa garcias" not in a["name"].lower()]
    pts = main + [{"name": "Caramba North", "lon": CARAMBA[0], "lat": CARAMBA[1], "cat": "caramba", "county": "Pecos"}]
    lons = [p["lon"] for p in pts]; lats = [p["lat"] for p in pts]
    lon0, lon1 = min(lons), max(lons); lat0, lat1 = min(lats), max(lats)
    W, H, PAD = 560, 470, 54
    coslat = math.cos(math.radians((lat0 + lat1) / 2))
    def X(lon): return PAD + (lon - lon0) / (lon1 - lon0) * (W - 2 * PAD)
    def Y(lat): return PAD + (lat1 - lat) / (lat1 - lat0) * (H - 2 * PAD)
    svg = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}">']
    # frame + faint graticule
    svg.append(f'<rect x="8" y="8" width="{W-16}" height="{H-16}" rx="14" fill="#0b1426" stroke="rgba(148,163,184,.18)"/>')
    for gx in range(1, 4):
        x = 8 + gx * (W - 16) / 4
        svg.append(f'<line x1="{x:.0f}" y1="10" x2="{x:.0f}" y2="{H-10}" stroke="rgba(148,163,184,.06)"/>')
    for gy in range(1, 4):
        y = 8 + gy * (H - 16) / 4
        svg.append(f'<line x1="10" y1="{y:.0f}" x2="{W-10}" y2="{y:.0f}" stroke="rgba(148,163,184,.06)"/>')
    svg.append(f'<text x="20" y="30" fill="#64748b" font-size="11" letter-spacing="1.5">WEST TEXAS · PERMIAN BASIN</text>')
    # leader labels for the named assets + caramba
    named = {"Wasson CO2 Removal Plant": ("Wasson CO₂-EOR — Yoakum", "r"),
             "Block 31 Plant": ("Block 31 gas plant — Crane", "r"),
             "Century Plant Substation": ("Century gas/CO₂ — Pecos", "r"),
             "Oxy Renewable Energy - Goldsmith": ("Goldsmith solar — Ector", "r"),
             "Caramba North": ("CARAMBA NORTH", "r")}
    for p in pts:
        k = "caramba" if p.get("cat") == "caramba" else kind(p)
        x, y = X(p["lon"]), Y(p["lat"])
        if k == "caramba":
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="none" stroke="{COL["caramba"]}" stroke-width="2.2"/>')
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{COL["caramba"]}"/>')
        else:
            shape_col = COL[k]
            if k == "plant":
                svg.append(f'<path d="M{x:.1f},{y-6.5:.1f} L{x+6:.1f},{y+5:.1f} L{x-6:.1f},{y+5:.1f} Z" fill="{shape_col}" stroke="#0b1426" stroke-width="1"/>')
            else:
                svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{shape_col}" stroke="#0b1426" stroke-width="1"/>')
        if p["name"] in named:
            lab, side = named[p["name"]]
            bold = ' font-weight="800"' if p.get("cat") == "caramba" else ' font-weight="600"'
            fill = COL["caramba"] if p.get("cat") == "caramba" else "#e2e8f0"
            if side == "r":
                svg.append(f'<text x="{x+12:.1f}" y="{y+4:.1f}" fill="{fill}" font-size="13"{bold}>{html.escape(lab)}</text>')
            else:
                svg.append(f'<text x="{x-12:.1f}" y="{y+4:.1f}" fill="{fill}" font-size="13"{bold} text-anchor="end">{html.escape(lab)}</text>')
    svg.append('</svg>')
    return "\n".join(svg)

def build_bars():
    mx = max(c for _, c, _ in FRAC)
    rows = []
    for name, c, role in FRAC:
        w = max(2.0, c / mx * 100)
        hot = role == "subject"
        bar = "#fb7185" if hot else ("#f59e0b" if role == "abut" else "#475569")
        lab = f'{name}' + (" ★" if hot else "")
        tag = {"subject": "subject site", "abut": "abuts Pecos", "near": "nearby"}[role]
        rows.append(f'''<div class="barrow">
          <div class="barlab">{html.escape(lab)}<span class="bartag">{tag}</span></div>
          <div class="bartrack"><div class="barfill" style="width:{w:.1f}%;background:{bar}"></div></div>
          <div class="barval">{c:,}</div></div>''')
    return "\n".join(rows)

LOCATOR = build_locator()
BARS = build_bars()

# ---------------- CSS ----------------
CSS = """
@font-face{font-family:'Inter';font-weight:400;src:url('https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-400-normal.woff2') format('woff2');}
@font-face{font-family:'Inter';font-weight:500;src:url('https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-500-normal.woff2') format('woff2');}
@font-face{font-family:'Inter';font-weight:600;src:url('https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-600-normal.woff2') format('woff2');}
@font-face{font-family:'Inter';font-weight:700;src:url('https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-700-normal.woff2') format('woff2');}
@font-face{font-family:'Inter';font-weight:800;src:url('https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-800-normal.woff2') format('woff2');}
@font-face{font-family:'Inter';font-weight:900;src:url('https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-900-normal.woff2') format('woff2');}
@page{size:1280px 720px;margin:0;}
*{margin:0;padding:0;box-sizing:border-box;}
html{font-family:'Inter','DejaVu Sans',sans-serif;}
body{color:#e2e8f0;font-feature-settings:"tnum" 1,"cv05" 1;}
.slide{position:relative;width:1280px;height:720px;overflow:hidden;page-break-after:always;
  background:radial-gradient(1200px 700px at 78% -8%,#16243f 0%,#0c1424 46%,#080e1a 100%);}
.slide:last-child{page-break-after:auto;}
.accent{position:absolute;left:0;top:0;bottom:0;width:7px;background:linear-gradient(#fb7185,#f59e0b);}
.top{position:absolute;top:38px;left:64px;right:64px;display:flex;justify-content:space-between;align-items:center;
  font-size:12.5px;letter-spacing:2px;color:#7c8aa3;text-transform:uppercase;}
.top .lrp{font-weight:800;color:#cbd5e1;letter-spacing:3px;}
.top .lrp b{color:#fb7185;}
.foot{position:absolute;bottom:30px;left:64px;right:64px;display:flex;justify-content:space-between;align-items:center;
  font-size:11.5px;letter-spacing:.6px;color:#56657d;border-top:1px solid rgba(148,163,184,.12);padding-top:12px;}
.foot .conf{color:#7c8aa3;font-weight:600;letter-spacing:1.6px;}
.body{position:absolute;top:96px;left:64px;right:64px;bottom:70px;}
.eyebrow{font-size:14px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#fb7185;margin-bottom:14px;}
h1{font-size:50px;font-weight:900;line-height:1.04;letter-spacing:-1.2px;color:#f8fafc;}
h2{font-size:38px;font-weight:800;line-height:1.06;letter-spacing:-.8px;color:#f8fafc;margin-bottom:8px;}
.sub{font-size:18px;color:#9fb0c7;font-weight:500;margin-top:14px;line-height:1.5;}
p,li{font-size:17px;line-height:1.5;color:#cdd8e6;}
.lead{font-size:19px;color:#e2e8f0;line-height:1.5;}
ul{list-style:none;}
.bul li{position:relative;padding-left:26px;margin-bottom:13px;}
.bul li:before{content:"";position:absolute;left:2px;top:9px;width:8px;height:8px;border-radius:2px;
  background:linear-gradient(135deg,#fb7185,#f59e0b);}
.bul li b{color:#fff;font-weight:700;}
.hl{color:#fbbf24;font-weight:700;}
.rose{color:#fb7185;font-weight:700;}
.teal{color:#5eead4;font-weight:700;}
.cols{display:flex;gap:22px;margin-top:8px;}
.card{flex:1;background:linear-gradient(#101c33,#0c1626);border:1px solid rgba(148,163,184,.16);
  border-radius:16px;padding:24px 22px;position:relative;overflow:hidden;}
.card .num{font-size:13px;font-weight:800;color:#fb7185;letter-spacing:2px;}
.card h3{font-size:21px;font-weight:800;color:#f1f5f9;margin:8px 0 10px;line-height:1.12;}
.card p{font-size:15px;color:#aebbcd;line-height:1.46;}
.chip{display:inline-block;margin-top:18px;background:rgba(251,113,133,.12);border:1px solid rgba(251,113,133,.4);
  color:#fecdd3;font-size:15px;font-weight:600;padding:11px 18px;border-radius:10px;}
.strip{position:absolute;left:64px;right:64px;bottom:74px;display:flex;gap:14px;}
.stat{flex:1;background:rgba(148,163,184,.06);border:1px solid rgba(148,163,184,.14);border-radius:12px;padding:14px 16px;}
.stat .k{font-size:12px;color:#8395ad;letter-spacing:.4px;}
.stat .v{font-size:22px;font-weight:800;color:#f1f5f9;margin-top:3px;}
table{width:100%;border-collapse:collapse;margin-top:6px;}
th,td{text-align:left;padding:11px 12px;font-size:15px;border-bottom:1px solid rgba(148,163,184,.13);}
th{font-size:12px;letter-spacing:1px;text-transform:uppercase;color:#8395ad;font-weight:700;}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;}
td b{color:#fff;}
.two{display:flex;gap:30px;height:100%;}
.mapwrap{display:flex;gap:26px;align-items:flex-start;}
.legend{font-size:14px;color:#b9c5d6;}
.legend .li{display:flex;align-items:center;gap:10px;margin-bottom:12px;}
.legend .dot{width:13px;height:13px;border-radius:50%;flex:none;}
.legend .tri{width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-bottom:12px solid #f59e0b;flex:none;}
.legend .ring{width:14px;height:14px;border-radius:50%;border:2px solid #fb7185;flex:none;}
.note{background:rgba(94,234,212,.08);border-left:3px solid #5eead4;border-radius:0 10px 10px 0;padding:12px 16px;font-size:15px;color:#c8d6e5;margin-top:14px;}
.barrow{display:flex;align-items:center;gap:14px;margin-bottom:11px;}
.barlab{width:210px;font-size:15px;color:#dbe4f0;font-weight:600;display:flex;flex-direction:column;}
.bartag{font-size:11px;color:#7c8aa3;font-weight:500;letter-spacing:.3px;}
.bartrack{flex:1;height:22px;background:rgba(148,163,184,.08);border-radius:6px;overflow:hidden;}
.barfill{height:100%;border-radius:6px;}
.barval{width:54px;text-align:right;font-weight:800;font-size:16px;font-variant-numeric:tabular-nums;color:#f1f5f9;}
.kicker{font-size:15px;color:#9fb0c7;max-width:560px;line-height:1.5;}
.teamcard{flex:1;background:linear-gradient(#101c33,#0c1626);border:1px solid rgba(148,163,184,.16);border-radius:16px;padding:22px 20px;}
.teamcard .role{font-size:13.5px;color:#fbbf24;font-weight:700;margin-top:4px;line-height:1.3;}
.teamcard .nm{font-size:22px;font-weight:800;color:#f8fafc;}
.teamcard p{font-size:14px;color:#aebbcd;margin-top:12px;line-height:1.45;}
.teamcard .hook{font-size:13.5px;color:#fecdd3;margin-top:12px;font-style:italic;}
.cover-title{position:absolute;left:74px;top:250px;right:74px;}
.cover-meta{position:absolute;left:74px;bottom:96px;font-size:15px;color:#8a99b0;line-height:1.7;}
.bignum{font-size:15px;color:#8395ad;}
"""

# ---------------- slide helpers ----------------
def chrome(section, pageno, foottitle):
    return (f'<div class="accent"></div>'
            f'<div class="top"><div class="lrp">LRP<b>.</b> LAND RESOURCE PARTNERS</div><div>{html.escape(section)}</div></div>'
            f'<div class="foot"><div class="conf">CONFIDENTIAL</div><div>{html.escape(foottitle)}</div><div>{pageno} / 14</div></div>')

SLIDES = []
def slide(section, pageno, foottitle, inner, extra_class=""):
    SLIDES.append(f'<section class="slide {extra_class}">{chrome(section, pageno, foottitle)}{inner}</section>')

# 1 — cover
slide("", 1, "OXY Partnership Intelligence", f'''
  <div class="cover-title">
    <div class="eyebrow">Confidential · Partnership Intelligence</div>
    <h1>Occidental Petroleum<br><span style="color:#fb7185">×</span> Caramba North</h1>
    <div class="sub" style="max-width:760px">Portfolio, Permian &amp; Pecos footprint, data-center–adjacent capabilities, deal comps, and a counterparty briefing — for the collaboration arising from the Williams-farm mineral / surface negotiation.</div>
  </div>
  <div class="cover-meta">Prepared 19 June 2026 · Land Resource Partners · Pecos County, Texas<br>
  Sources: SEC filings &amp; earnings · 1PointFive / OXY / WES / TPL press · DOE / EPA · the LRP Texas Energy GIS map</div>''')

# 2 — situation
slide("The situation", 2, "The deal & OXY's pivot", '''
  <div class="body">
    <h2>The situation, and OXY's pivot</h2>
    <ul class="bul" style="margin-top:18px;max-width:1050px">
      <li><b>Caramba North</b> — ~1,300 ac, Pecos County — under evaluation to repurpose for a <b>hyperscale data center</b>.</li>
      <li>Site control requires the <b>shallow mineral estate (0–5,000 ft)</b> <em>and</em> the <b>working interest</b> — to remove drilling / vibration risk on the surface.</li>
      <li>On the Williams farm: <span class="rose">minerals = OXY</span> · <span class="teal">working interest = Chevron</span>.</li>
      <li>OXY declined a cheap waiver — <span class="hl">correctly</span>: a data center runs ~$40B all-in per GW, so the mineral line item is immaterial to the hyperscaler's stack — and instead proposed a <b>broader partnership</b> across CCS, produced-water desalination, power, and its basin-wide minerals / working interests / fee lands.</li>
    </ul>
    <div class="chip">"Partner up, trade market intelligence, collaborate." — OXY's counter</div>
  </div>''')

# 3 — thesis
slide("Executive thesis", 3, "Why OXY is the partner", '''
  <div class="body" style="bottom:150px">
    <h2>OXY is the most multi-dimensional partner in this geography</h2>
    <div class="cols" style="margin-top:24px">
      <div class="card"><div class="num">01 · CARBON</div><h3>A turnkey net-zero data center</h3>
        <p>1PointFive runs the world's only utility-scale DAC plant and the largest hyperscaler carbon-removal contract on record (Microsoft). Bundle: gas power + point-source CCS + DAC offtake. <b style="color:#fecdd3">Google &amp; Meta haven't signed — the opening.</b></p></div>
      <div class="card"><div class="num">02 · POWER + CCS</div><h3>Infrastructure inside Pecos</h3>
        <p>A ~$1.1B gas/CO₂ complex literally in Pecos County, a CO₂ pipeline spine (Bravo/Cortez), and a proven gas-to-power template (Project Horizon, Longfellow Ranch).</p></div>
      <div class="card"><div class="num">03 · WATER</div><h3>Cooling without the freshwater fight</h3>
        <p>Produced-water recycling at scale plus TerraLithium brine-treatment and a WES desal pilot — the path to non-potable cooling in water-scarce Pecos.</p></div>
    </div>
  </div>
  <div class="strip">
    <div class="stat"><div class="k">Capital posture</div><div class="v">Berkshire-anchored</div></div>
    <div class="stat"><div class="k">Debt</div><div class="v">~$23B → $13.3B</div></div>
    <div class="stat"><div class="k">Implication</div><div class="v">Patient · multi-decade</div></div>
  </div>''')

# 4 — at a glance
slide("Corporate & financial", 4, "OXY at a glance", '''
  <div class="body">
    <h2>OXY at a glance</h2>
    <div class="two" style="margin-top:14px">
      <div style="flex:1.25">
        <table>
          <tr><th>Metric</th><th class="n">FY2024</th><th class="n">FY2025</th><th class="n">Q1 2026</th></tr>
          <tr><td>Total revenue</td><td class="n">$26.9B</td><td class="n">$22.1B</td><td class="n">$5.7B</td></tr>
          <tr><td>Net income to common</td><td class="n">$2.4B</td><td class="n">$1.6B</td><td class="n">$3.2B*</td></tr>
          <tr><td>Operating cash flow</td><td class="n">$11.7B</td><td class="n">$10.5B</td><td class="n">~$1.4B</td></tr>
          <tr><td>Production (MBOE/d)</td><td class="n">1,327</td><td class="n"><b>1,434</b></td><td class="n">1,426</td></tr>
          <tr><td>Capex</td><td class="n">$6.8B</td><td class="n">$7.3B</td><td class="n">$1.5B</td></tr>
        </table>
        <div style="font-size:12.5px;color:#7c8aa3;margin-top:10px">*Q1'26 includes a +$3.1B gain on the OxyChem sale; continuing-ops ≈ $1.07B. OXY does not report EBITDA.</div>
      </div>
      <div style="flex:1;display:flex;flex-direction:column;gap:12px">
        <div class="stat"><div class="k">Permian standing</div><div class="v">~#4 producer · ~2.8–2.9M net ac</div></div>
        <div class="stat"><div class="k">CO₂-EOR</div><div class="v">#1 · 34 projects · ~20 Mt/yr</div></div>
        <div class="stat"><div class="k">Berkshire Hathaway</div><div class="v">~26.6% + $8.5B 8% pfd</div></div>
        <div class="note" style="margin-top:2px">OxyChem <b>sold to Berkshire ($9.7B, closed Jan 2026)</b> → OXY now reports two segments (Oil &amp; Gas; Midstream &amp; Marketing / OLCV).</div>
      </div>
    </div>
  </div>''')

# 5 — carbon / 1pointfive
slide("Capability · Carbon", 5, "1PointFive · DAC · CCS · CDR", '''
  <div class="body">
    <h2>Carbon management — the marquee asset</h2>
    <div class="two" style="margin-top:14px">
      <div style="flex:1.1">
        <ul class="bul">
          <li><b>STRATOS</b> (Ector Co.) — the <b>world's largest DAC</b>: up to 500k t CO₂/yr, ~$1.3B, BlackRock $550M JV, first-ever EPA Class VI DAC permits (Apr 2025).</li>
          <li><b>South Texas DAC hub</b> — King Ranch (Kleberg): 106k ac, ~3 Bt storage, <b>DOE up to $500M</b>, ADNOC/XRG up to $500M.</li>
          <li><b>Carbon Engineering</b> — acquired ~$1.1B (2023); the DAC IP behind both.</li>
        </ul>
        <div class="chip" style="margin-top:8px">Google &amp; Meta have <b>not</b> signed 1PointFive — LRP relationships can help close it.</div>
      </div>
      <div style="flex:1">
        <div style="font-size:12px;letter-spacing:1.4px;color:#8395ad;font-weight:700;margin-bottom:6px">CARBON-REMOVAL OFFTAKE</div>
        <table>
          <tr><th>Buyer</th><th class="n">Volume</th></tr>
          <tr><td><b>Microsoft</b> — largest-ever; AI emissions</td><td class="n">500k t</td></tr>
          <tr><td>Amazon</td><td class="n">250k t</td></tr>
          <tr><td>Airbus</td><td class="n">400k t</td></tr>
          <tr><td>AT&amp;T · TD · JPMorgan · Trafigura</td><td class="n">various</td></tr>
        </table>
        <div class="note">45Q is $85/t for saline sequestration; OXY also backs NET Power — the template for <b>CCS on gas-fired data-center power</b>.</div>
      </div>
    </div>
  </div>''')

# 6 — power + century
slide("Capability · Power", 6, "In-county power + Century", '''
  <div class="body">
    <h2>In-basin power &amp; CCS — inside the county</h2>
    <ul class="bul" style="margin-top:18px;max-width:1080px">
      <li><b>Century gas / CO₂ complex — Pecos County</b>: ~$1.1B, 800 MMcf/d treating, <b>the largest single-source industrial CO₂ capture in North America</b>, routing ~5–8 Mt/yr CO₂ to EOR. OXY infrastructure, ROW, water-handling and personnel adjacent to Caramba.</li>
      <li><b>CO₂ pipeline spine</b> — Bravo (218 mi) + Cortez (500 mi, 1.5 Bcf/d): a ready transport network for any CCS-on-power scheme.</li>
      <li><b>Gas-to-power template</b> — Project Horizon (Longfellow Ranch, Pecos): on-site turbines fed from OXY/Targa gathering. <span style="color:#9fb0c7">(CoreWeave anchor lapsed — a proven template, not a live reference.)</span></li>
      <li><b>Goldsmith solar</b> (Ector, 16–20 MW) — OXY power self-supply.</li>
    </ul>
  </div>''')

# 7 — water
slide("Capability · Water", 7, "Produced-water desalination", '''
  <div class="body">
    <h2>Produced-water treatment &amp; desalination</h2>
    <ul class="bul" style="margin-top:18px;max-width:1080px">
      <li>The Permian produced <b>&gt;20 MMbbl/d of water in 2024</b> (→ &gt;26 by 2030). OXY is a top-tier handler.</li>
      <li><b>Recycling at scale</b> — South Curtis Ranch &gt;50 MM bbl reused; Lost Tank (NM) up to 180k bbl/d.</li>
      <li><b>TerraLithium</b> direct-lithium-extraction (a brine-treatment train) + BHE JV — <b>transferable to desalinating produced water</b> into non-potable cooling makeup.</li>
      <li><b>WES Reeves-County desal pilot</b> — ~1,000 bbl/d reclaimed freshwater, a county over from Pecos.</li>
    </ul>
    <div class="note">Why it matters: treated produced water is the only scalable cooling source in Pecos that doesn't compete for Edwards-Trinity / Pecos Valley freshwater. A pilot here is a natural first joint project.</div>
  </div>''')

# 8 — footprint map
slide("The mapping data", 8, "OXY footprint — Pecos & Permian", f'''
  <div class="body">
    <h2>OXY's footprint — from the LRP map's own data</h2>
    <div class="mapwrap" style="margin-top:10px">
      <div>{LOCATOR}</div>
      <div style="flex:1;padding-top:8px">
        <div class="legend">
          <div class="li"><span class="tri"></span> Gas / CO₂ plants <span style="color:#7c8aa3">— Century · Block 31 · Wasson</span></div>
          <div class="li"><span class="dot" style="background:#fbbf24"></span> Solar <span style="color:#7c8aa3">— Goldsmith (Ector)</span></div>
          <div class="li"><span class="dot" style="background:#38bdf8"></span> OXY field substations <span style="color:#7c8aa3">— Cogdell · N. Cowden · Curtis Ranch · Welch</span></div>
          <div class="li"><span class="ring"></span> Caramba North <span style="color:#7c8aa3">— subject site</span></div>
        </div>
        <div class="note" style="margin-top:10px">Plus <b>Santa Garcias Solar, 265 MW</b> (Oxy Renewable Energy LLC) in <b>Kleberg County</b> (South Texas) — co-located with the 1PointFive King Ranch DAC hub, ~480 mi SE.</div>
        <div class="kicker" style="margin-top:14px">Every point is a live record extracted from the LRP map layers (ERCOT, EIA-860, OSM, HIFLD/EIA) — independent corroboration that OXY operates across this exact geography.</div>
      </div>
    </div>
  </div>''')

# 9 — layer evidence
slide("The mapping data", 9, "OXY in the LRP map layers", '''
  <div class="body">
    <h2>What the LRP map already shows about OXY</h2>
    <table style="margin-top:10px">
      <tr><th>Map layer</th><th>OXY record</th><th>Where</th></tr>
      <tr><td>ERCOT interconnect queue</td><td><b>Santa Garcias Solar</b>, 265 MW — Oxy Renewable Energy LLC</td><td>Kleberg</td></tr>
      <tr><td>Solar / EIA-860</td><td>Goldsmith solar farm</td><td>Ector</td></tr>
      <tr><td>Power plants (EIA-860)</td><td>Wasson CO₂ Removal — Occidental Permian Ltd</td><td>Yoakum</td></tr>
      <tr><td>Substations (OSM)</td><td><b>Century Plant Substation</b> — Occidental Petroleum, 138 kV</td><td><b>Pecos</b></td></tr>
      <tr><td>ERCOT TPIT (planned grid)</td><td>Solstice–Hayter 138 kV rebuild — beside Caramba</td><td><b>Pecos</b></td></tr>
      <tr><td>NG processing (HIFLD/EIA)</td><td><b>Block 31 plant</b> — Owner: Oxy</td><td>Crane</td></tr>
      <tr><td>Tax abatements</td><td>Ingleside OxyChem / Oxy terminal</td><td>San Patricio</td></tr>
      <tr><td>FracFocus completions</td><td>OXY-family — see footprint chart</td><td>basin-wide</td></tr>
    </table>
  </div>''')

# 10 — fracfocus chart
slide("The mapping data", 10, "Completion footprint", f'''
  <div class="body">
    <h2>OXY completion footprint — heavy around Pecos, light inside it</h2>
    <div class="two" style="margin-top:16px">
      <div style="flex:1.2">{BARS}
        <div style="font-size:12px;color:#7c8aa3;margin-top:8px">FracFocus disclosures, OXY-family (Occidental + Anadarko + CrownQuest). ★ = subject county.</div>
      </div>
      <div style="flex:.85;display:flex;align-items:center">
        <div class="note" style="border-left-color:#fb7185;background:rgba(251,113,133,.08)">
          OXY drills heavily in the abutting Delaware counties (<b>Reeves, Ward, Loving</b>) but is <b>light inside Pecos proper (24)</b>. That's the profile of a <b>royalty / fee owner</b>, not an active operator of the shallow column under the tract — which is exactly what makes a <b>shallow-rights waiver / subordination tractable</b>.</div>
      </div>
    </div>
  </div>''')

# 11 — comps
slide("Negotiation", 11, "Deal comps & framing", '''
  <div class="body">
    <h2>Deal comps &amp; negotiation framing</h2>
    <ul class="bul" style="margin-top:16px;max-width:1090px">
      <li><b>OXY already contributes surface to a Permian DC-power project.</b> Chevron's 2.5→5 GW, ~$7B AI-power campus (Pecos/Reeves; Microsoft offtaker) reportedly sits on land from <b>TPL, Oxy USA &amp; WaterBridge</b>. <span style="color:#9fb0c7">(single source — verify in county records.)</span></li>
      <li><b>Texas law</b> — the mineral estate is dominant; the accommodation doctrine is weak (<em>Lyle v. Midway Solar</em>, a Pecos case) → a <b>negotiated waiver / subordination</b> from OXY + Chevron is required.</li>
      <li><b>Benchmarks</b> — TPL: $169M = 4,106 royalty ac (~$41k/ac) + 4,120 surface ac (~$41k/ac); producing Permian minerals $2–8k+/ac.</li>
      <li><b>Framing</b> — at ~$40B/GW, a shallow-mineral buyout + waiver is a rounding error. <b>Leverage is alignment, not the doctrine.</b></li>
    </ul>
  </div>''')

# 12 — team
slide("Counterparties", 12, "The OXY team", '''
  <div class="body" style="bottom:120px">
    <h2>The OXY team — all Land / commercial</h2>
    <div class="cols" style="margin-top:20px">
      <div class="teamcard"><div class="nm">David Woest</div><div class="role">Director, Surface Land</div>
        <p>Owns surface-use agreements, ROW &amp; easements — the function that papers a Caramba surface deal.</p>
        <div class="hook">Hook: surface-rights craft — "what should we get ahead of on the ground?"</div></div>
      <div class="teamcard"><div class="nm">John Cranfill</div><div class="role">Sr. Director, Business Development — US Onshore &amp; Carbon Mgmt</div>
        <p>The commercial bridge between OXY's upstream and its CCUS strategy — the strategic node for this deal.</p>
        <div class="hook">Hook: UT Austin (pet-eng → CCUS pivot).</div></div>
      <div class="teamcard"><div class="nm">Jeff Noto</div><div class="role">Land Team Lead · ex-Sr. Negotiator, Oxy Low Carbon Ventures</div>
        <p>Has negotiated land for OXY's low-carbon projects — knows how to assemble a clean footprint.</p>
        <div class="hook">Hook: OLCV land-assembly craft. (Not the Zayo CFO.)</div></div>
    </div>
  </div>
  <div class="strip" style="bottom:64px"><div class="stat" style="flex:1"><div class="k">Sourcing note</div><div class="v" style="font-size:15px;font-weight:600;color:#aebbcd">Public-source, confidence-marked · personal details not improvised · safest rapport = Cranfill's UT Austin + craft-respect for Woest &amp; Noto</div></div></div>''')

# 13 — caveats
slide("Diligence", 13, "Caveats & verification flags", '''
  <div class="body">
    <h2>Caveats — price these in before any term sheet</h2>
    <ul class="bul" style="margin-top:18px;max-width:1090px">
      <li><b>OxyChem is divested</b> (→ Berkshire, $9.7B) — the chemicals / water-treatment-chemical angle now runs through Berkshire, not OXY.</li>
      <li><b>Western Midstream may be sold</b> — confirm OXY still controls WES before counting its water / pipeline / ROW network.</li>
      <li><b>OXY is not a TPL-style West-Texas fee empire</b> — its big land-grant estate was the Rockies (sold 2020); it's been a net seller in the TX Delaware. Your title work on the Williams tract stands — just don't extrapolate it county-wide.</li>
      <li><b>Verify</b> — the Oxy-USA / Chevron-campus land comp (single source) and the verbatim 10-K surface / sequestration risk language.</li>
    </ul>
  </div>''')

# 14 — next steps
slide("Next", 14, "Map build & recommended moves", '''
  <div class="body">
    <h2>Putting it on the map — &amp; the moves</h2>
    <div class="two" style="margin-top:14px">
      <div style="flex:1">
        <div style="font-size:13px;letter-spacing:1.4px;color:#8395ad;font-weight:700;margin-bottom:8px">LRP GIS MAP</div>
        <ul class="bul">
          <li><b style="color:#5eead4">oxy_assets</b> — built &amp; verified (9 OXY assets), staged on PR #19.</li>
          <li><b>oxy_drilling_permits</b> — RRC W-1 filtered to OXY.</li>
          <li><b>oxy_minerals_pecos</b> — StratMap parcels: OXY's actual "position in Pecos."</li>
        </ul>
        <div class="note" style="border-left-color:#5eead4">Live map · lrp-tx-gis.netlify.app</div>
      </div>
      <div style="flex:1">
        <div style="font-size:13px;letter-spacing:1.4px;color:#8395ad;font-weight:700;margin-bottom:8px">RECOMMENDED MOVES</div>
        <ul class="bul">
          <li>Press the <b>Google / Meta CDR gap</b> — bring OXY a hyperscaler it hasn't signed.</li>
          <li>Scope a <b>Pecos produced-water desal pilot</b> + a gas-to-power-with-CCS package as the first joint project.</li>
          <li><b>Quantify OXY's Pecos minerals</b> from county / RRC records (the minerals map layer).</li>
        </ul>
      </div>
    </div>
  </div>''')

DOC = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="hz:slide-selector" content=".slide">
<title>OXY Partnership Intelligence — Caramba North</title>
<style>{CSS}</style></head>
<body data-canvas-width="1280" data-canvas-height="720">
{''.join(SLIDES)}
</body></html>'''

os.makedirs(os.path.dirname(OUT_HTML), exist_ok=True)
with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(DOC)
print("wrote", OUT_HTML, "·", len(SLIDES), "slides ·", len(DOC), "bytes")
