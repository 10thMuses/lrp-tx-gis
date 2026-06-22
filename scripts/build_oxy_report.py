# -*- coding: utf-8 -*-
"""Build the OXY data-center-JV intelligence dossier (portrait A4) as HTML.

Clean single-file generator (replaces the old v2 + v3 post-processor chain).
Reads the shared asset list from oxy_assets_data.py and the map keys written by
oxy_build_maps.py, then assembles:

  cover → intro page (summary + linked contents + personnel bios)
       → §1 Footprint & proximity to Caramba North (overview + 50-mi maps)
       → §2 Midstream / gas / CO₂   (intro + map + business cards)
       → §3 Water
       → §4 Power & NET Power
       → §5 Carbon capture
       → Appendix A Financial profile
       → Appendix B Berkshire relationship
       → Appendix C Caveats & confidence
       → Appendix D Sources & notes (all footnotes)

Every section starts on a new page; spacing is tuned so a section that can fit
on one page does. Sources and raw facility-database IDs live only in the
footnotes appendix. Render to PDF/DOCX as separate steps.

Run: python3 scripts/build_oxy_report.py
"""
import os, json
from oxy_assets_data import ASSETS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RPT = os.path.join(ROOT, "outputs", "reports")
OUT = os.path.join(RPT, "oxy-intelligence-report.html")
KEYS = json.load(open(os.path.join(RPT, "oxy_map_keys.json"), encoding="utf-8"))

# ---- footnote registry (everything sourced lands here) ----
FN = []
def fn(text):
    FN.append(text)
    return len(FN)

CHIP = {"existing": ("ex", "Existing"), "planned": ("pl", "Planned"),
        "construction": ("con", "Under construction"),
        "demonstration": ("demo", "Pilot / demo"), "divested": ("dv", "Divested")}

TYPE_LABEL = {"gas": "Gas / CO₂", "power": "Power / solar", "netpower": "NET Power",
              "dac": "Carbon capture", "water": "Water"}

# section id -> (number label, title, accent, accent-bg, map key, map file, caption)
SECTIONS = [
    ("midstream", "Section 2", "Midstream, pipelines &amp; gas processing", "#b91c1c", "#fef2f2",
     "midstream", "oxy_map_midstream.png", "OXY-owned CO₂ / gas-processing assets and WES processing plants."),
    ("water", "Section 3", "Water infrastructure", "#0369a1", "#eff6ff",
     "water", "oxy_map_water.png", "OXY and Western Midstream produced-water recycling and desalination assets."),
    ("power", "Section 4", "Power generation &amp; NET Power", "#c2410c", "#fff7ed",
     "power", "oxy_map_power.png", "Solar OXY uses to power its operations, plus the NET Power gas-to-power site near Odessa."),
    ("dac", "Section 5", "Carbon capture", "#15803d", "#f0fdf4",
     "dac", "oxy_map_dac.png", "The Odessa low-carbon cluster: STRATOS direct-air-capture with co-located solar and NET Power."),
]

SEC_INTRO = {
    "midstream": "A behind-the-meter data center makes its own electricity from natural gas, so it needs a dependable way to gather, treat and move that gas — and, increasingly, to manage the carbon that comes with burning it. This section profiles OXY's gas and CO₂ network: what it owns, what it has sold, and which pieces could supply fuel and carbon handling to a jointly-developed campus.",
    "water": "Large data centers use significant water for cooling, and West Texas is water-short — making water access a permitting and community flashpoint. OXY and its affiliate Western Midstream run one of the larger produced-water and recycling networks in private hands, infrastructure that (paired with emerging desalination) could supply non-potable cooling water without drawing down scarce freshwater.",
    "power": "Power is the gating constraint for AI data centers, and the multi-year wait to connect to the ERCOT grid is the single biggest schedule risk. OXY's most strategically relevant asset to a data-center JV is its power platform — above all NET Power, purpose-built to deliver firm, around-the-clock, low-emission gas power behind the meter and skip the grid queue. Each generation asset is profiled through that lens.",
    "dac": "Carbon management is becoming a precondition for hyperscalers' clean-energy commitments. OXY's capture and storage assets offer a partner a credible path to carbon-neutral claims for a gas-powered campus — though today's economics depend on subsidies and premium buyers, so this section is deliberately right-sized as the least-mature part of the platform.",
}

def chip(status):
    c, lab = CHIP.get(status, ("dv", status))
    return f'<span class="chip {c}">{lab}</span>'

def asset_card(a):
    n = fn(a["src"])
    rows = "".join(
        f'<div class="arow"><span class="al">{l}</span><span class="av">{v}</span></div>'
        for l, v in a["rows"])
    return (
        f'<div class="asset">'
        f'<div class="ah"><span class="an">{a["name"]}<sup class="fnref">{n}</sup></span>{chip(a["status"])}</div>'
        f'<div class="ab"><div class="one">{a["one"]}</div>{rows}'
        f'<div class="jv"><span class="jvl">Why it matters for a data-center JV</span>{a["jv"]}</div>'
        f'</div></div>')

def keytable(mapkey):
    rows = KEYS.get(mapkey, [])
    out = []
    for r in rows:
        out.append(
            f'<div class="kr"><span class="kn">{r["n"]}</span>'
            f'<span class="kt">{r["label"]}<span class="kk"> · {TYPE_LABEL.get(r["type"], r["type"])}</span></span></div>')
    return "".join(out)

# ===================== CSS =====================
CSS = """
@font-face{font-family:'Inter';font-weight:400;src:url('https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-400-normal.woff2') format('woff2');}
@font-face{font-family:'Inter';font-weight:500;src:url('https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-500-normal.woff2') format('woff2');}
@font-face{font-family:'Inter';font-weight:600;src:url('https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-600-normal.woff2') format('woff2');}
@font-face{font-family:'Inter';font-weight:700;src:url('https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-700-normal.woff2') format('woff2');}
@font-face{font-family:'Inter';font-weight:800;src:url('https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-800-normal.woff2') format('woff2');}
@font-face{font-family:'Inter';font-weight:900;src:url('https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-900-normal.woff2') format('woff2');}
:root{--ink:#15202b;--mut:#5b6b7a;--faint:#8a98a6;--red:#b91c1c;--rule:#e2e8ef;--tint:#f6f8fb;--acc:#0f766e;--accbg:#f0fdfa;}
@page{size:A4;margin:15mm 13mm 13mm 13mm;
  @top-left{content:"OCCIDENTAL PETROLEUM (NYSE: OXY) — DATA-CENTER JV INTELLIGENCE";font-family:'Inter';font-size:6.5pt;font-weight:700;color:#9aa7b4;letter-spacing:.5pt;}
  @top-right{content:"CONFIDENTIAL";font-family:'Inter';font-size:6.5pt;font-weight:700;color:#b91c1c;letter-spacing:1.2pt;}
  @bottom-left{content:"Prepared June 2026 · subject-company profile · sources in Appendix D";font-family:'Inter';font-size:6.2pt;color:#9aa7b4;}
  @bottom-right{content:counter(page) " / " counter(pages);font-family:'Inter';font-size:7.2pt;font-weight:600;color:#7e8c9a;}}
@page cover{margin:0;@top-left{content:none}@top-right{content:none}@bottom-left{content:none}@bottom-right{content:none}}
*{margin:0;padding:0;box-sizing:border-box;}
html{font-family:'Inter','DejaVu Sans',sans-serif;color:var(--ink);font-size:9pt;line-height:1.36;font-feature-settings:"tnum" 1;}
p{margin:0 0 5pt;}
b,strong{font-weight:700;color:#0d1620;}
.mut{color:var(--mut);} .faint{color:var(--faint);}
sup.fnref{font-size:5.6pt;font-weight:800;color:#2563eb;vertical-align:super;margin-left:1pt;}

/* cover */
.cover{page:cover;height:297mm;position:relative;background:linear-gradient(160deg,#0c1726 0%,#13243b 52%,#0a1320 100%);color:#eaf0f7;padding:30mm 22mm;}
.cover .bar{width:54pt;height:5pt;background:linear-gradient(90deg,#b91c1c,#f59e0b);margin-bottom:20pt;}
.cover .ey{font-size:9pt;font-weight:700;letter-spacing:3pt;color:#fca5a5;text-transform:uppercase;}
.cover h1{font-size:31pt;font-weight:900;line-height:1.06;letter-spacing:-.6pt;margin:14pt 0 0;}
.cover h1 span{color:#f8b4b4;}
.cover .sub{font-size:11.5pt;color:#aebccd;margin-top:14pt;max-width:150mm;line-height:1.5;}
.cover .meta{position:absolute;left:22mm;bottom:24mm;font-size:8.5pt;color:#8ea0b3;line-height:1.7;}

/* section frame */
.section{break-before:page;}
.snum{font-size:7.3pt;font-weight:800;letter-spacing:2pt;color:var(--acc);display:block;margin-bottom:2pt;}
h2{font-size:15.5pt;font-weight:800;letter-spacing:-.2pt;color:#0f172a;margin:0 0 2pt;border-top:2.4pt solid var(--acc);padding-top:5pt;display:inline-block;}
h3{font-size:11pt;font-weight:800;color:#0f172a;margin:9pt 0 3pt;}
h4{font-size:9.2pt;font-weight:800;color:var(--acc);margin:7pt 0 2pt;letter-spacing:.2pt;}
.lead{background:var(--accbg);border-left:3pt solid var(--acc);padding:7pt 11pt;border-radius:0 5pt 5pt 0;margin:5pt 0 8pt;font-size:9.6pt;line-height:1.45;color:#1f2933;}
.lead b{color:#0d1620;}

/* asset cards */
.asset{border:.8pt solid var(--rule);border-left:3pt solid var(--acc);border-radius:6pt;margin:6pt 0;break-inside:avoid;}
.asset .ah{display:flex;justify-content:space-between;align-items:center;gap:8pt;background:#f4f6f9;padding:4.5pt 9pt;border-bottom:.8pt solid var(--rule);border-radius:5pt 5pt 0 0;}
.asset .an{font-size:10.4pt;font-weight:800;color:#0f172a;line-height:1.2;}
.asset .ab{padding:5pt 9pt 6pt;}
.asset .one{font-size:8.9pt;font-style:italic;color:#33414e;margin-bottom:4pt;line-height:1.35;}
.arow{display:flex;gap:8pt;padding:2.6pt 0;}
.arow+.arow{border-top:.5pt solid #eef2f6;}
.al{flex:none;width:72pt;font-size:6.5pt;font-weight:800;text-transform:uppercase;letter-spacing:.4pt;color:#64748b;padding-top:1.5pt;}
.av{font-size:8.6pt;color:#1f2933;line-height:1.36;}
.jv{margin-top:5pt;background:#eef5ff;border-left:2.4pt solid #2563eb;padding:4pt 8pt;border-radius:0 3pt 3pt 0;}
.jvl{font-size:6.3pt;font-weight:800;letter-spacing:.8pt;text-transform:uppercase;color:#2563eb;display:block;margin-bottom:1pt;}
.jv{font-size:8.4pt;color:#17314f;line-height:1.38;}

/* status chips */
.chip{flex:none;display:inline-block;font-size:6.1pt;font-weight:800;letter-spacing:.4pt;padding:1.5pt 4.5pt;border-radius:3pt;text-transform:uppercase;}
.chip.ex{background:#dcfce7;color:#166534;} .chip.pl{background:#fef9c3;color:#854d0e;}
.chip.con{background:#ffedd5;color:#9a3412;} .chip.demo{background:#dbeafe;color:#1e40af;}
.chip.dv{background:#eef1f5;color:#64748b;}

/* maps */
.mapfig{margin:6pt 0 4pt;break-inside:avoid;}
.mapfig img{width:100%;border:.8pt solid var(--rule);border-radius:5pt;display:block;}
.mapcap{font-size:7pt;color:#94a3b8;margin-top:2.5pt;line-height:1.3;}
.maprow{display:flex;gap:10pt;align-items:flex-start;}
.maprow .mapfig{flex:none;width:112mm;}
.keytab{flex:1;font-size:7.3pt;padding-top:2pt;}
.keyh{font-size:6.6pt;font-weight:800;letter-spacing:1pt;color:#6b7a89;text-transform:uppercase;margin-bottom:4pt;}
.kr{display:flex;gap:5pt;margin-bottom:2.6pt;align-items:baseline;}
.kn{flex:none;width:12pt;height:12pt;border-radius:50%;background:var(--ink);color:#fff;font-size:6.2pt;font-weight:800;text-align:center;line-height:12pt;}
.kt{color:#27323d;font-weight:600;line-height:1.22;} .kk{color:var(--faint);font-weight:500;}

/* intro page */
.exec{font-size:9.8pt;line-height:1.5;color:#1f2933;margin:5pt 0 9pt;}
.exec b{color:#0d1620;}
.toc{font-size:9pt;margin:2pt 0 9pt;}
.toc a{display:flex;justify-content:space-between;text-decoration:none;color:#1f2933;border-bottom:.6pt dotted #cbd5e1;padding:3.2pt 0;}
.toc a .tt{font-weight:600;} .toc a .tn{color:var(--faint);font-weight:700;}
.bio{border-left:2.4pt solid #94a3b8;padding:2pt 0 2pt 9pt;margin:6pt 0;}
.bio .bn{font-size:9.6pt;font-weight:800;color:#0f172a;}
.bio .br{font-size:7.6pt;font-weight:700;color:var(--mut);text-transform:uppercase;letter-spacing:.3pt;}
.bio p{font-size:8.5pt;margin:2pt 0 0;line-height:1.4;}

/* tables (appendix) */
table{width:100%;border-collapse:collapse;margin:5pt 0 4pt;font-size:8pt;}
th{text-align:left;font-size:6.6pt;font-weight:800;text-transform:uppercase;letter-spacing:.5pt;color:#6b7a89;border-bottom:1.2pt solid #cbd5e1;padding:3.4pt 4pt;}
td{padding:3.4pt 4pt;border-bottom:.6pt solid var(--rule);vertical-align:top;line-height:1.3;}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;}
tr:nth-child(even) td{background:var(--tint);}
.two{display:flex;gap:12pt;} .two>*{flex:1;}
.kbox{border:.8pt solid var(--rule);border-radius:5pt;padding:7pt 9pt;background:var(--tint);margin:6pt 0;break-inside:avoid;}
.kbox .h{font-size:6.8pt;font-weight:800;letter-spacing:1.2pt;color:#6b7a89;text-transform:uppercase;margin-bottom:4pt;}
ul{margin:2pt 0 6pt 0;list-style:none;}
li{position:relative;padding-left:11pt;margin-bottom:3.2pt;font-size:8.7pt;line-height:1.4;}
li:before{content:"";position:absolute;left:0;top:4.5pt;width:4pt;height:4pt;border-radius:1pt;background:var(--acc);}
.quote{border-left:2.4pt solid #cbd5e1;padding:2pt 0 2pt 9pt;margin:5pt 0;font-style:italic;color:#33414e;font-size:8.6pt;}
.src{font-size:7.2pt;color:var(--faint);line-height:1.4;}
.fnlist{font-size:7.5pt;line-height:1.4;color:#3a4654;}
.fnlist li{padding-left:16pt;margin-bottom:3.4pt;}
.fnlist li:before{content:none;}
.fnlist li .fnn{position:absolute;left:0;font-weight:800;color:#2563eb;}
h2,h3,h4{break-after:avoid;} .lead{break-after:avoid;}
"""

def section_open(sid, snum, title, acc, accbg):
    return (f'<div class="section" id="{sid}" style="--acc:{acc};--accbg:{accbg};">'
            f'<span class="snum">{snum}</span><h2>{title}</h2>')

# ===================== BUILD BODY (sections) =====================
parts = []

# --- §1 Footprint & proximity (two maps) ---
parts.append(section_open("s-footprint", "Section 1",
             "OXY's footprint &amp; proximity to Caramba North", "#0f766e", "#f0fdfa"))
parts.append('<div class="lead">For a hyperscale data center, what sits nearby in energy infrastructure decides how fast and how cheaply it can be powered, cooled and connected. This section maps OXY\'s physical footprint across West Texas and shows what lies within reach of the Williams family\'s Caramba North tract in Pecos County — the starting point for judging whether OXY\'s assets are close enough to be additive to a jointly-developed campus.</div>')
parts.append(
    '<div class="maprow"><div class="mapfig"><img src="oxy_map_overview.png" alt="OXY overview map">'
    '<div class="mapcap">All OXY-owned and affiliated (Western Midstream) assets across the Permian. Substations (blue) shown for orientation.</div></div>'
    f'<div class="keytab"><div class="keyh">Map key</div>{keytable("overview")}</div></div>')
parts.append('<h3>What is actually near the Williams land</h3>')
parts.append(
    '<div class="mapfig"><img src="oxy_map_caramba.png" alt="50-mile proximity map">'
    '<div class="mapcap">OXY assets with a precise location, within 50 miles of Caramba North. County-level assets are excluded here to avoid implying false nearness.</div></div>')
PROX = """<div class="kbox"><div class="h">The proximity read</div><p style="font-size:8.7pt">OXY's two nearest major assets to Caramba North are the <b>Century gas &amp; CO&#8322; plant (~31 miles)</b> and the <b>Block 31 CO&#8322;-flood complex (~48 miles)</b>. The rest of OXY's footprint &mdash; its largest CO&#8322; field (Wasson), its gas-processing plants, and its power and carbon-capture projects around Odessa &mdash; sits 90&ndash;130 miles north in the Midland Basin and the Gaines/Yoakum CO&#8322; corridor. The practical conclusion: physical adjacency to the Williams tract is limited to OXY's CO&#8322; system, while the assets most relevant to a data center (power and water) are a basin away. The strategic fit, developed in the following sections, is therefore about OXY's <b>capabilities and contracts</b>, not its pipe within sight of the property.</p></div>"""
parts.append(PROX)
parts.append('</div>')

# --- §2-§5 asset-type sections ---
by_sec = {}
for a in ASSETS:
    by_sec.setdefault(a["section"], []).append(a)

for sid_key, snum, title, acc, accbg, mapkey, mapfile, cap in SECTIONS:
    parts.append(section_open("s-" + sid_key, snum, title, acc, accbg))
    parts.append(f'<div class="lead">{SEC_INTRO[sid_key]}</div>')
    nkey = KEYS.get(mapkey, [])
    if nkey:
        parts.append(
            f'<div class="maprow"><div class="mapfig"><img src="{mapfile}" alt="{title} map">'
            f'<div class="mapcap">{cap}</div></div>'
            f'<div class="keytab"><div class="keyh">Map key</div>{keytable(mapkey)}</div></div>')
    else:
        parts.append(f'<div class="mapfig"><img src="{mapfile}" alt="{title} map"><div class="mapcap">{cap}</div></div>')
    for a in by_sec.get(sid_key, []):
        parts.append(asset_card(a))
    parts.append('</div>')

BODY = "".join(parts)

# ===================== APPENDICES (financials, Berkshire, caveats) =====================
fn_fin = fn("Financial sources: OXY Q1-2026 earnings call &amp; slides (5 May 2026); OXY Q4/FY2025 release (18 Feb 2026); FY2024/FY2025 8-Ks; GAAP rendered via stockanalysis.com tying to the 10-K/10-Q (SEC EDGAR returned HTTP 403 to automated fetch). *Principal debt as of 5 May 2026, down from ~$20.8B at Q3-2025. **FCF before working capital. ***Q1-2026 net income includes a ~$3.1B gain on the OxyChem sale; continuing-ops adjusted income ≈ $1.07B. OXY does not report EBITDA.")
fn_bk = fn("Berkshire sources: OXY Q3-2023 release; OXY Q1-2026 call &amp; transcript (6 May 2026); Berkshire 10-Qs (via Morningstar); berkshirehathaway.com shareholder letters 2022–2025; FERC order EC22-87-000 (19 Aug 2022); SEC 13D/A.")

APPX = f"""
<div class="section" id="appx-fin" style="--acc:#334155;--accbg:#f1f5f9;">
  <span class="snum">Appendix A</span><h2>Financial profile<sup class="fnref">{fn_fin}</sup></h2>
  <div class="lead">Post-OxyChem (sold to Berkshire Hathaway, closed 2 Jan 2026), Occidental reports three businesses — Oil &amp; Gas, Midstream &amp; Marketing, and Low-Carbon Ventures (1PointFive). The headline of the last two years is debt reduction: <b>net debt roughly halved</b> and principal debt fell toward a $10B target, restoring an investment-grade rating. A data-center partner reads this as a counterparty that is de-risking and disciplined on capital — but also one that prefers contracts and asset sales over new owned construction.</div>
  <table>
    <tr><th>Metric ($M unless noted)</th><th class="n">FY2024</th><th class="n">FY2025</th><th class="n">Q1 2026</th><th class="n">FY2026 guidance</th></tr>
    <tr><td><b>Net debt</b> (total debt − cash)</td><td class="n">23,992</td><td class="n">20,428</td><td class="n"><b>11,860</b></td><td class="n">—</td></tr>
    <tr><td>Principal debt (headline)</td><td class="n">~24.9B</td><td class="n">~15.0B</td><td class="n">13.3B*</td><td class="n">target $10B</td></tr>
    <tr><td>Operating cash flow</td><td class="n">11,439</td><td class="n">10,532</td><td class="n">~2,000</td><td class="n">n/d</td></tr>
    <tr><td>Free cash flow</td><td class="n">5,176</td><td class="n">4,105</td><td class="n">1,700**</td><td class="n">&gt;$1.2B incr.</td></tr>
    <tr><td>Capital expenditure</td><td class="n">6,263</td><td class="n">6,427</td><td class="n">~1,450</td><td class="n"><b>5,500–5,900</b></td></tr>
    <tr><td>Net income to common</td><td class="n">2,377</td><td class="n">1,647</td><td class="n">3,175***</td><td class="n">—</td></tr>
    <tr><td>Total production (Mboe/d)</td><td class="n">—</td><td class="n">1,460 (Q4)</td><td class="n">1,426</td><td class="n">1,410–1,460</td></tr>
    <tr><td>Permian production (Mboe/d)</td><td class="n">—</td><td class="n">~800 (Q4)</td><td class="n">787 (55%)</td><td class="n">783–803 (Q2)</td></tr>
  </table>
  <div class="two">
    <div class="kbox"><div class="h">Capital spending (2026)</div><ul>
      <li>FY2026 capex guided <b>$5.5–5.9B</b>, cut ~8% from the initial frame; ~70% to US onshore.</li>
      <li>Low-Carbon Ventures / 1PointFive capex only <b>~$100M in 2026</b> as STRATOS spend rolls off.</li>
      <li>FY2027 guidance and full per-segment capex split: not disclosed.</li></ul></div>
    <div class="kbox"><div class="h">Ratings &amp; priorities</div><ul>
      <li><b>Fitch upgraded OXY to BBB</b> (investment grade), 26 Feb 2026.</li>
      <li>Capital priorities: debt to $10B, then a growing dividend (raised ~8% to $0.26/qtr), then cash ahead of the 2029 preferred redemption. Buybacks de-emphasized.</li></ul></div>
  </div>
  <h4>Asset sales that funded the debt paydown</h4>
  <table>
    <tr><th>Asset → buyer</th><th>Proceeds</th><th>Closed</th></tr>
    <tr><td><b>OxyChem → Berkshire Hathaway</b></td><td>$9.7B cash</td><td>2 Jan 2026</td></tr>
    <tr><td>Delaware upstream → Permian Resources; DJ minerals → Elk Range</td><td>~$1.2B</td><td>Q1 2025</td></tr>
    <tr><td>Midland-Basin gas gathering → Enterprise Products</td><td>$580M</td><td>22 Aug 2025</td></tr>
  </table>
</div>

<div class="section" id="appx-bk" style="--acc:#6d28d9;--accbg:#f5f3ff;">
  <span class="snum">Appendix B</span><h2>The Berkshire Hathaway relationship<sup class="fnref">{fn_bk}</sup></h2>
  <div class="lead">Berkshire is OXY's most important financial partner, with four layers of exposure: an <b>$8.5B preferred stock</b> paying 8%, ~83.9M warrants, a ~27% common stake, and the OxyChem business it bought outright in January 2026. For a JV, the relevance is that Warren Buffett's company is comfortable underwriting OXY at scale and praises its carbon-capture leadership — a useful signal of institutional confidence.</div>
  <h4>The 2019 preferred stock — the structural anchor</h4>
  <ul>
    <li>Berkshire holds <b>$10B face of perpetual preferred at an 8% dividend</b> (~$680M/yr at the ~$8.5B remaining), originally to fund OXY's 2019 Anadarko purchase.</li>
    <li>OXY must redeem pieces at a <b>10% premium</b> whenever its dividends + buybacks exceed <b>$4.00/share</b>; it can redeem the whole balance at <b>105% from August 2029</b>.</li>
    <li>Only <b>~$1.5B has been redeemed</b> (all in 2023); buyback cuts since then paused further redemptions. OxyChem proceeds are going to <b>debt, not the preferred</b>.</li>
  </ul>
  <div class="two">
    <div class="kbox"><div class="h">Warrants</div><ul>
      <li><b>~83.9M warrants</b> at <b>$59.62</b>, unexercised; expire one year after the preferred is fully redeemed.</li></ul></div>
    <div class="kbox"><div class="h">Common stake</div><ul>
      <li><b>~265M shares (~27%)</b>, flat since Feb 2025. FERC has authorized Berkshire to go up to 50%.</li></ul></div>
  </div>
  <div class="quote">"Berkshire has no interest in purchasing or managing Occidental. We particularly like its vast oil and gas holdings… as well as its leadership in carbon-capture initiatives, though the economic feasibility of this technique has yet to be proven." <span class="mut">— Warren Buffett, Berkshire 2023 letter</span></div>
</div>

<div class="section" id="appx-cav" style="--acc:#9a3412;--accbg:#fef6f3;">
  <span class="snum">Appendix C</span><h2>Caveats &amp; confidence</h2>
  <div class="lead">Each item below is flagged because it is <b>not publicly disclosed</b>, <b>recently changed</b>, or <b>commonly mis-stated</b> — and material enough that relying on a wrong version would mislead a partner.</div>
  <ul>
    <li><b>NET Power's Odessa plant is no longer 300 MW.</b> It was re-scoped in March 2026 to an 80 MW design using conventional turbines plus bolt-on capture; older “300 MW Allam-cycle” figures are superseded.</li>
    <li><b>No named hyperscaler is attached to NET Power's plant yet.</b> The data-center fit is a strong category thesis, not a signed contract — present it as such.</li>
    <li><b>OXY's Western Midstream stake is ~39.5%, not “49%,”</b> and OXY has explored selling it entirely (~$20B). Don't treat WES as a fixed half-owned asset.</li>
    <li><b>OXY does not own the Cortez CO₂ pipeline</b> (Kinder Morgan / ExxonMobil do); OXY is only a shipper. It does own the Bravo system in New Mexico.</li>
    <li><b>Carbon capture is barely economic today</b> — roughly $400–600+/tonne cost against a ~$180/tonne federal credit; it depends on subsidy-stacking and premium buyers.</li>
    <li><b>TerraLithium (lithium-from-brine) is California-only;</b> there is no announced Texas produced-water project.</li>
    <li><b>Several figures are genuinely undisclosed:</b> OXY-only produced-water volumes, South Curtis Ranch daily capacity, STRATOS per-tonne cost, FY2027 guidance, and the reported 2022 Century plant sale. Marked “not disclosed” rather than estimated.</li>
  </ul>
</div>
"""

# ===================== INTRO PAGE (exec summary + TOC + bios) =====================
fn_woest = fn("David Woest — Texas Legislature SB 421 witness lists (2019); TheOrg; Wiza. A possible Anadarko tenure and his credentials could not be verified (behind blocked LinkedIn).")
fn_cran = fn("John Cranfill — TheOrg; Wiza; 1PointFive / EnLink releases. Career timeline confidence medium; education (UT Austin Petroleum Engineering; U. Houston CCUS certificate) high.")
fn_noto = fn("Jeffrey Noto — ZoomInfo & LinkedIn headline snippets; Hart Energy; 1PointFive Louisiana CCS release. The Greater-Houston OXY land professional (not the Zayo Group CFO). Education/credentials not found.")

TOC = [
    ("§1 · OXY's footprint &amp; proximity to Caramba North", "#s-footprint"),
    ("§2 · Midstream, pipelines &amp; gas processing", "#s-midstream"),
    ("§3 · Water infrastructure", "#s-water"),
    ("§4 · Power generation &amp; NET Power", "#s-power"),
    ("§5 · Carbon capture", "#s-dac"),
    ("Appendix A · Financial profile", "#appx-fin"),
    ("Appendix B · The Berkshire Hathaway relationship", "#appx-bk"),
    ("Appendix C · Caveats &amp; confidence", "#appx-cav"),
    ("Appendix D · Sources &amp; notes", "#appx-fn"),
]
toc_html = "".join(f'<a href="{href}"><span class="tt">{t}</span><span class="tn">→</span></a>' for t, href in TOC)

INTRO = f"""
<div class="section" id="intro" style="--acc:#0f766e;--accbg:#f0fdfa;break-before:auto;">
  <span class="snum">Executive summary</span><h2>Occidental as a data-center JV partner</h2>
  <div class="exec">Occidental Petroleum is the Permian Basin's largest carbon-dioxide and enhanced-oil-recovery operator, and over the last five years it has quietly assembled the three ingredients a hyperscale data center needs most: <b>dispatchable power, large-scale water handling, and carbon management.</b> Its NET Power venture is building one of the first natural-gas power plants designed to capture nearly all of its own CO₂ — the single most relevant asset to a behind-the-meter campus that must avoid the multi-year ERCOT grid queue. Its produced-water and recycling network across West Texas is among the largest in private hands, a potential source of cooling water that doesn't draw on scarce freshwater. And its STRATOS plant near Odessa is the world's largest direct-air-capture facility, offering a turnkey route to credible carbon-neutral claims. For the Williams family's Caramba North site in Pecos County, OXY's <b>nearest</b> major infrastructure is the Century CO₂ plant (~31 miles) and the Block 31 complex (~48 miles); the <b>deeper</b> fit is OXY's power-and-carbon platform, which maps directly onto the needs of a co-developed AI campus — capabilities and contracts more than pipe within sight of the property.</div>

  <h3>Contents</h3>
  <div class="toc">{toc_html}</div>

  <h3>Key personnel</h3>
  <div class="bio"><span class="bn">David Woest<sup class="fnref">{fn_woest}</sup></span> &nbsp;<span class="br">Director, Surface Land — OXY</span>
    <p>Leads OXY's surface-land function (surface-use agreements, rights-of-way, easements, landowner relations) out of Katy, Texas. Independently confirmed in 2019 Texas Legislature records testifying for OXY on eminent-domain / right-of-way reform — squarely the surface-land remit a landowner negotiation would touch.</p></div>
  <div class="bio"><span class="bn">John Cranfill<sup class="fnref">{fn_cran}</sup></span> &nbsp;<span class="br">Sr. Director, Business Development — US Onshore &amp; Carbon Management, OXY</span>
    <p>Houston-based; ~16 years' experience. His mandate is securing CO₂ supply/off-take agreements and optimizing OXY's upstream portfolio — the commercial bridge between conventional oil &amp; gas and the carbon-management business. Petroleum-engineering background (UT Austin) with a CCUS certificate (U. Houston).</p></div>
  <div class="bio"><span class="bn">Jeffrey “Jeff” Noto<sup class="fnref">{fn_noto}</sup></span> &nbsp;<span class="br">Land Team Lead — OXY</span>
    <p>Leads negotiation and administration of OXY's oil-, gas- and carbon-storage property rights — leasing, surface/subsurface agreements, title and regulatory coordination. Previously a senior land negotiator at OXY's Low-Carbon Ventures, tied to its CO₂-storage land assembly. (The Greater-Houston OXY professional — not the telecom CFO of the same name.)</p></div>
</div>
"""

# ===================== ASSEMBLE =====================
FN_HTML = "".join(f'<li><span class="fnn">{i+1}.</span>{t}</li>' for i, t in enumerate(FN))
APPX_FN = (f'<div class="section" id="appx-fn" style="--acc:#475569;--accbg:#f1f5f9;">'
           f'<span class="snum">Appendix D</span><h2>Sources &amp; notes</h2>'
           f'<div class="lead">Every source citation and raw facility-database identifier (EPA, EIA, RRC, PHMSA, TCEQ, DOE) referenced in this report is collected here, numbered to the markers in the text.</div>'
           f'<ol class="fnlist">{FN_HTML}</ol></div>')

HTML = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Occidental Petroleum — Data-Center JV Intelligence</title>
<style>{CSS}</style></head><body>
<section class="cover">
  <div class="bar"></div>
  <div class="ey">Confidential · Subject-Company Intelligence</div>
  <h1>Occidental Petroleum<br><span>OXY</span> — infrastructure for a<br>hyperscale data-center JV</h1>
  <div class="sub">An assessment of Occidental's power, water, gas/CO₂ and carbon-capture infrastructure across West Texas and the Permian Basin — framed for a potential joint venture with the Williams family to co-develop a hyperscale data-center campus near Caramba North, Pecos County.</div>
  <div class="meta">Prepared June 2026<br>Subject company: Occidental Petroleum Corp. (NYSE: OXY)<br>Audience: data-center JV evaluation<br>Sources: SEC filings &amp; earnings calls · OXY / WES / 1PointFive / NET Power releases · DOE / EPA / EIA / RRC / TCEQ · trade press — see Appendix D</div>
</section>
{INTRO}
{BODY}
{APPX}
{APPX_FN}
</body></html>"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)
print("wrote", OUT, "·", len(HTML), "bytes ·", len(ASSETS), "assets ·", len(FN), "footnotes")
