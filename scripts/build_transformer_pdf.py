#!/usr/bin/env python3
"""Build Transformer-Opportunity-White-Paper.pdf in Grid Wire PDF format spec v2.

Spec: docs/grid-wire-master-instructions-v4.md, Part J.3 + 2026-07-08 addendum.
Layout grammar: TOP LINE banner (navy fill, gold header, red/green signal dots),
page-1 stat band + clock chips, gold section kickers, navy section header bands
with gold left accent, three-tier box grammar (navy-left/gray = Angle reads,
gold-left/cream = analytical sub-blocks, red-left/blush = falsification),
+/- signal coloring in tables. Jost instanced static weights 400/500/600/700,
navy #1c2b3a / gold #b8860b, WeasyPrint with FontConfiguration threaded to both
CSS() and write_pdf(), absolute file:// font paths, pdftotext/pdftoppm QA.

Usage: python3 scripts/build_transformer_pdf.py [--fonts-dir DIR]
"""

import argparse
import datetime as dt
import html as html_mod
import os
import re
import subprocess
import sys
import tempfile

import markdown
from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration

PROJECT = os.environ.get("LRP_PROJECT_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_MD = os.path.join(PROJECT, "outputs", "reports", "Transformer-Opportunity-White-Paper.md")
OUT_PDF = os.path.join(PROJECT, "outputs", "reports", "Transformer-Opportunity-White-Paper.pdf")

NAVY = "#1c2b3a"
GOLD = "#b8860b"
TODAY = dt.date(2026, 7, 13)

# ---------------------------------------------------------------- page-1 furniture

TOPLINE = [
    ("green", "Cycle bifurcated: distribution lead times normalized to ~30 wks by Q2 2025; power 128 wks / GSU 144 wks / EHV 3-6 yrs unimproved."),
    ("red", "“20x demand” is the field signal, not yet the print — published max is 3.7x (GSU +274%). Shipments are capacity-capped, so the print measures supply. Expect upward convergence."),
    ("green", "GOES chokepoint confirmed: 95% of domestic core steel from one mill (CLF Butler); 50-75% of cores imported; Sec 232 50% on cores + copper (Aug 2025)."),
    ("red", "CLF Weirton transformer plant cancelled per Q1 2025 8-K. Still circulating in industry decks as coming capacity. It is not."),
    ("green", "PE playbook validated twice: Sunbelt Solomon (Temple, TX) and Central Moloney. Virginia Transformer exploring sale at >$6B."),
    ("red", "Distribution overshoot window 2027-2029: announced capacity lands 2026-27 into a segment already at 30-week lead times."),
]

STATS = [
    ("+274%", "GSU demand 2019-2025", "Wood Mackenzie, verified 9-0"),
    ("144 wks", "GSU lead time, Q2 2025", "vs ~52 wks pre-2022"),
    ("+40%", "real PPI 2020-2024", "+70-86% nominal since 2019"),
    ("$47.5B", "Oncor base plan 2026-2030", "+$11.4B vs prior plan"),
    ("255 GW", "data-center queue at Oncor", "38 GW RTP-qualified"),
    ("95%", "domestic core steel, one mill", "CLF Butler Works, sole US GOES"),
]

CLOCKS = [
    (dt.date(2027, 1, 1), "Siemens Charlotte LPT production (early 2027)"),
    (dt.date(2027, 6, 30), "Distribution overshoot window opens"),
    (dt.date(2028, 1, 1), "Hitachi South Boston VA online (2028)"),
    (dt.date(2028, 12, 31), "Oncor 765-kV Longshore energization target"),
]

KICKERS = {
    "Company Map — Ranked by Asymmetry": "Most asymmetric first. On every line, the print lags the field.",
    "Executive Summary": "Five verified facts frame the trade.",
    "1. Market Fundamentals": "Four demand layers, only one of them AI. Scarcity binds at the top of the voltage stack.",
    "2. Supply Side: Capacity, Chokepoints, Tariffs": "One steel mill, one tariff wall, and a cancelled plant everyone still models.",
    "3. Public Equities": "The market prices one transformer cycle. There are two.",
    "4. Private Companies and Deal Flow": "Three successive sponsor generations have already been paid in repair/reman.",
    "5. Picks and Shovels: The Component Layer": "The least crowded layer of the chain. Mostly private, family-owned, un-securitized.",
    "6. The Texas/ERCOT Angle": "$47.5B at one utility. 255 GW of queue behind $3.5B of customer collateral.",
    "7. Risks": "Underwrite +40% real and 60-80% nominal. Do not underwrite the 4-9x tails.",
    "8. Investable Takeaways, Ranked by Asymmetry": "ERCOT repair roll-up first. Avoid commodity distribution assembly.",
    "Methodology & Sources": "105-agent adversarial verification: 23 claims confirmed, 2 refuted, gaps flagged inline.",
}

FALSIFICATION = (
    "<b>Falsification conditions.</b> The thesis is wrong if: (1) power/GSU lead times fall below "
    "80 weeks before 2028 without a demand collapse (capacity arrived early; scarcity leg dead); "
    "(2) a Section 232 carve-out for cores/GOES lands (input-cost moat dissolves; importer economics "
    "reset); (3) Oncor's RTP-qualified data-center load stalls below ~38 GW through 2027 (queue was "
    "paper); (4) utility spec-standardization collapses the 80,000-type SKU fragmentation (repair/reman "
    "moat erodes); (5) the Virginia Transformer process fails to clear anywhere near $6B (private comp "
    "deck resets down)."
)

# company-name -> website; longest names matched first so overlaps resolve correctly
COMPANY_LINKS = {
    "Powell Industries": "https://www.powellind.com",
    "GE Vernova": "https://www.gevernova.com",
    "Siemens Energy": "https://www.siemens-energy.com",
    "Hitachi Energy": "https://www.hitachienergy.com",
    "HD Hyundai Electric": "https://www.hd-hyundaielectric.com",
    "Hyosung Heavy": "https://www.hyosungheavyindustries.com",
    "Hyosung": "https://www.hyosungheavyindustries.com",
    "LS Electric": "https://www.ls-electric.com",
    "Eaton": "https://www.eaton.com",
    "Schneider": "https://www.se.com",
    "Vertiv": "https://www.vertiv.com",
    "WEG": "https://www.weg.net",
    "Mitsubishi Electric": "https://www.mitsubishielectric.com",
    "Cleveland-Cliffs": "https://www.clevelandcliffs.com",
    "ESCO Technologies": "https://escotechnologies.com",
    "Doble": "https://www.doble.com",
    "Omicron": "https://www.omicronenergy.com",
    "Megger": "https://megger.com",
    "Virginia Transformer": "https://www.vatransformer.com",
    "Sunbelt Solomon": "https://www.sunbeltsolomon.com",
    "Sunbelt Transformer": "https://www.sunbeltsolomon.com",
    "Central Moloney": "https://centralmoloneyinc.com",
    "Emerald Transformer": "https://emeraldtransformer.com",
    "ERMCO": "https://www.ermco-eci.com",
    "Prolec GE": "https://www.prolecge.com",
    "Prolec": "https://www.prolecge.com",
    "Delta Star": "https://www.deltastar.com",
    "Pennsylvania Transformer": "https://patransformer.com",
    "MGM Transformer": "https://www.mgmtransformer.com",
    "MGM/VanTran": "https://vantran.com",
    "VanTran": "https://vantran.com",
    "Maschinenfabrik Reinhausen": "https://www.reinhausen.com",
    "Reinhausen": "https://www.reinhausen.com",
    "Metglas": "https://metglas.com",
    "Proterial": "https://www.proterial.com",
    "Cargill": "https://www.cargill.com",
    "Nynas": "https://www.nynas.com",
    "Qualitrol": "https://www.qualitrolcorp.com",
    "Fortive": "https://www.fortive.com",
    "Vaisala": "https://www.vaisala.com",
    "Camlin": "https://www.camlingroup.com",
    "Heinrich Georg GmbH": "https://www.georg.com",
    "Superior Essex": "https://superioressex.com",
    "Rea Magnet Wire": "https://www.reawire.com",
    "AEM": "https://aemcores.com",
    "Wind Point Partners": "https://www.windpointpartners.com",
    "Wind Point": "https://www.windpointpartners.com",
    "Trilantic": "https://trilanticnorthamerica.com",
    "Insight Equity": "https://www.insightequity.com",
    "Oncor": "https://www.oncor.com",
}


def linkify(html_text: str) -> str:
    """Wrap company-name mentions in links, skipping text already inside anchors."""
    pattern = re.compile(
        r"(?<![\w/-])("
        + "|".join(re.escape(n) for n in sorted(COMPANY_LINKS, key=len, reverse=True))
        + r")(?![\w-])"
    )
    parts = re.split(r"(<a\b.*?</a>)", html_text, flags=re.S)
    for i, part in enumerate(parts):
        if part.startswith("<a"):
            continue
        parts[i] = pattern.sub(
            lambda m: f'<a class="co" href="{COMPANY_LINKS[m.group(1)]}">{m.group(1)}</a>', part
        )
    return "".join(parts)


# ---------------------------------------------------------------- md -> body html


def md_to_html(md_text: str) -> str:
    body = md_text.split("---", 1)[1] if "---" in md_text else md_text
    return markdown.markdown(body, extensions=["tables"])


def colorize_tds(html_text: str) -> str:
    """Signal coloring: +x%/+bps green, -x%/-bps red inside table cells."""

    def _cell(m):
        content = m.group(2)
        if re.search(r"(?<![\w.])[+↑]\s?\d[\d,.]*\s?(%|bps|x\b)", content):
            cls = ' class="sig-up"'
        elif re.search(r"(?<![\w.])[-−↓]\s?\d[\d,.]*\s?(%|bps|x\b)", content):
            cls = ' class="sig-dn"'
        else:
            return m.group(0)
        return f"<td{cls}{m.group(1)}>{content}</td>"

    return re.sub(r"<td([^>]*)>(.*?)</td>", _cell, html_text, flags=re.S)


def apply_grammar(html_text: str):
    """Kickers under section headers, anchor ids + TOC entries, italic asides -> angle boxes."""
    toc = []

    def _h2(m):
        title = html_mod.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
        sec_id = f"sec-{len(toc)}"
        toc.append((sec_id, title))
        band = f'<h2 id="{sec_id}">{m.group(1)}</h2>'
        kicker = KICKERS.get(title)
        if kicker:
            band += f'<p class="kicker">{kicker}</p>'
        return band

    html_text = re.sub(r"<h2>(.*?)</h2>", _h2, html_text, flags=re.S)
    # "Key finding:" lead paragraphs -> gold analytical sub-block
    html_text = re.sub(
        r"<p><strong>Key finding:</strong>(.*?)</p>",
        r'<div class="box-gold"><p><b>Key finding.</b>\1</p></div>',
        html_text,
        flags=re.S,
    )
    # full-italic paragraphs (inline notes/asides in the source md) -> angle boxes
    html_text = re.sub(
        r"<p><em>(.*?)</em></p>",
        r'<div class="box-angle"><p>\1</p></div>',
        html_text,
        flags=re.S,
    )
    # falsification box after the risks section (before takeaways header)
    html_text = re.sub(
        r'(<h2 id="[^"]*">8\. Investable Takeaways)',
        f'<div class="box-fals"><p>{FALSIFICATION}</p></div>\n\\1',
        html_text,
        count=1,
    )
    return html_text, toc


def build_toc(toc) -> str:
    items = "".join(
        f'<li><a href="#{sec_id}">{html_mod.escape(title)}</a></li>' for sec_id, title in toc
    )
    return (
        '<div class="toc"><div class="toc-hdr">CONTENTS</div>'
        f"<ul>{items}</ul></div>"
    )


# ---------------------------------------------------------------- page-1 html


def page_one() -> str:
    dots = "".join(
        f'<tr><td class="dot dot-{c}">●</td><td class="tl-line">{html_mod.escape(t)}</td></tr>'
        for c, t in TOPLINE
    )
    stats = "".join(
        f'<td class="stat"><div class="stat-n">{html_mod.escape(n)}</div>'
        f'<div class="stat-l">{html_mod.escape(l)}</div>'
        f'<div class="stat-d">{html_mod.escape(d)}</div></td>'
        for n, l, d in STATS
    )
    chips = "".join(
        f'<span class="chip"><b>{(d - TODAY).days}d</b> · {html_mod.escape(label)} · {d.strftime("%b %d %Y")}</span>'
        for d, label in CLOCKS
    )
    return f"""
<div class="masthead">
  <div class="mast-kicker">LAND RESOURCE PARTNERS · MARKET INTELLIGENCE · JULY 2026</div>
  <h1>The Transformer Opportunity</h1>
  <div class="mast-sub">Where the Asymmetry Actually Sits in the AI Power Buildout</div>
</div>
<div class="topline">
  <div class="topline-hdr">TOP LINE</div>
  <table class="topline-tbl">{dots}</table>
</div>
<table class="statband"><tr>{stats}</tr></table>
<div class="clocks">{chips}</div>
"""


# ---------------------------------------------------------------- css


def build_css(fonts_dir: str) -> str:
    faces = []
    for w in (400, 500, 600, 700):
        for ital, style in (("", "normal"), ("Italic", "italic")):
            p = os.path.abspath(os.path.join(fonts_dir, f"Jost-{w}{ital}.ttf"))
            faces.append(
                f"@font-face {{ font-family: Jost; font-weight: {w}; font-style: {style}; "
                f"src: url('file://{p}'); }}"
            )
    return "\n".join(faces) + f"""
@page {{
  size: letter; margin: 18mm 15mm 16mm 15mm;
  @bottom-left {{ content: "LRP · The Transformer Opportunity · July 2026";
    font-family: Jost; font-size: 8.5pt; color: {NAVY}; opacity: .65; }}
  @bottom-right {{ content: counter(page) " / " counter(pages);
    font-family: Jost; font-size: 8.5pt; color: {NAVY}; opacity: .65; }}
}}
body {{ font-family: Jost; font-weight: 400; font-size: 12pt; line-height: 1.62;
  color: #22303d; }}
a.co {{ color: {NAVY}; font-weight: 500; text-decoration: underline;
  text-decoration-color: {GOLD}; text-decoration-thickness: .8pt; }}
.toc {{ page-break-before: always; margin: 0 0 10pt 0; }}
.toc-hdr {{ background: {NAVY}; color: {GOLD}; font-weight: 700; font-size: 12.5pt;
  letter-spacing: 2pt; padding: 4pt 8pt; border-left: 4pt solid {GOLD}; }}
.toc ul {{ list-style: none; padding: 6pt 2pt 0 2pt; margin: 0; }}
.toc li {{ margin: 4.5pt 0; font-size: 12pt; font-weight: 500; }}
.toc a {{ color: {NAVY}; text-decoration: none; display: block; }}
.toc a::after {{ content: leader(". ") " " target-counter(attr(href), page);
  color: {GOLD}; font-weight: 600; }}
.masthead {{ border-bottom: 2.5pt solid {GOLD}; padding-bottom: 6pt; margin-bottom: 10pt; }}
.mast-kicker {{ font-size: 9.5pt; font-weight: 600; letter-spacing: 1.6pt; color: {GOLD}; }}
h1 {{ font-size: 28pt; font-weight: 700; color: {NAVY}; margin: 2pt 0 0 0; }}
.mast-sub {{ font-size: 14pt; font-weight: 500; color: {NAVY}; opacity: .8; }}
.topline {{ background: {NAVY}; border-radius: 3pt; padding: 8pt 10pt; margin: 6pt 0 8pt 0; }}
.topline-hdr {{ color: {GOLD}; font-weight: 700; font-size: 12.5pt; letter-spacing: 2pt;
  margin-bottom: 4pt; }}
.topline-tbl {{ border-collapse: collapse; }}
.topline-tbl td {{ border: none; padding: 1.6pt 0; vertical-align: top; }}
.topline-tbl tr:nth-child(even) td {{ background: transparent; }}
.statband tr:nth-child(even) td {{ background: #f7f8fa; }}
.dot {{ width: 15pt; font-size: 9.5pt; }}
.dot-green {{ color: #3fae6a; }} .dot-red {{ color: #e2574c; }}
.tl-line {{ color: #eef2f6; font-size: 10.8pt; line-height: 1.35; }}
.statband {{ width: 100%; border-collapse: collapse; table-layout: fixed;
  margin: 0 0 6pt 0; }}
.stat {{ border: .6pt solid #d7dde3; border-top: 2pt solid {GOLD}; background: #f7f8fa;
  padding: 5pt 4pt; text-align: center; vertical-align: top; }}
.stat-n {{ font-size: 18pt; font-weight: 700; color: {NAVY}; }}
.stat-l {{ font-size: 8.8pt; font-weight: 600; color: {NAVY}; margin-top: 1pt; }}
.stat-d {{ font-size: 8.4pt; color: {GOLD}; font-weight: 500; margin-top: 1pt; }}
.clocks {{ margin: 0 0 10pt 0; }}
.chip {{ display: inline-block; border: .8pt solid {NAVY}; border-left: 3pt solid {GOLD};
  border-radius: 2pt; padding: 1.5pt 5pt; margin: 0 3pt 3pt 0; font-size: 9.2pt;
  color: {NAVY}; }}
.chip b {{ color: {GOLD}; font-weight: 700; }}
h2 {{ background: {NAVY}; color: #ffffff; font-size: 14.5pt; font-weight: 600;
  padding: 5pt 8pt; border-left: 4pt solid {GOLD}; margin: 20pt 0 4pt 0;
  page-break-after: avoid; }}
.kicker {{ color: {GOLD}; font-weight: 600; font-size: 11.5pt; margin: 3pt 0 9pt 2pt;
  page-break-after: avoid; }}
h3 {{ color: {NAVY}; font-size: 13pt; font-weight: 600; margin: 15pt 0 5pt 0;
  border-bottom: .8pt solid {GOLD}; padding-bottom: 1.5pt; page-break-after: avoid; }}
p {{ margin: 6.5pt 0; }}
ul, ol {{ margin: 5pt 0 8pt 0; padding-left: 15pt; }}
li {{ margin: 4pt 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 9pt 0; font-size: 10.6pt; }}
th {{ background: {NAVY}; color: #fff; font-weight: 600; padding: 3pt 5pt;
  text-align: left; }}
td {{ border: .5pt solid #d7dde3; padding: 3.5pt 5.5pt; vertical-align: top; }}
tr {{ page-break-inside: avoid; }}
tr:nth-child(even) td {{ background: #f4f6f8; }}
td a, td a.co {{ color: {NAVY}; font-weight: 600; text-decoration: underline;
  text-decoration-color: {GOLD}; text-decoration-thickness: .8pt; }}
.sig-up {{ color: #1e7e45; font-weight: 600; }}
.sig-dn {{ color: #c0392b; font-weight: 600; }}
.box-angle {{ background: #eef1f4; border-left: 4pt solid {NAVY}; padding: 6pt 9pt;
  margin: 9pt 0; font-size: 11.4pt; }}
.box-angle p {{ margin: 0; }}
.box-gold {{ background: #faf5e6; border-left: 4pt solid {GOLD}; padding: 6pt 9pt;
  margin: 9pt 0 11pt 0; font-size: 11.6pt; }}
.box-gold p {{ margin: 0; }}
.box-fals {{ background: #faeceb; border-left: 4pt solid #c0392b; padding: 6pt 9pt;
  margin: 10pt 0; font-size: 11.4pt; }}
.box-fals p {{ margin: 0; }}
strong {{ font-weight: 600; color: {NAVY}; }}
hr {{ border: none; border-top: .8pt solid #d7dde3; margin: 10pt 0; }}
"""


# ---------------------------------------------------------------- build + QA


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--fonts-dir",
        default=os.path.join(PROJECT, "vendor", "fonts", "jost"),
        help="directory with Jost-{400,500,600,700}[Italic].ttf (default: vendor/fonts/jost)",
    )
    args = ap.parse_args()

    with open(SRC_MD, encoding="utf-8") as f:
        md_text = f.read()

    body, toc = apply_grammar(linkify(colorize_tds(md_to_html(md_text))))
    doc = f"<html><body>{page_one()}{build_toc(toc)}{body}</body></html>"

    font_config = FontConfiguration()
    css = CSS(string=build_css(args.fonts_dir), font_config=font_config)
    HTML(string=doc, base_url=PROJECT).write_pdf(OUT_PDF, stylesheets=[css], font_config=font_config)

    # QA: no marker leakage, text extractable, first page renders
    txt = subprocess.run(["pdftotext", OUT_PDF, "-"], capture_output=True, text=True).stdout
    for marker in ("box-angle", "box-fals", "sig-up", "sig-dn", "class="):
        assert marker not in txt, f"marker leakage: {marker}"
    squeezed = re.sub(r"\s+", "", txt)
    assert "TOPLINE" in squeezed and "TransformerOpportunity" in squeezed, "page-1 furniture missing"
    qa_dir = tempfile.mkdtemp(prefix="transformer_pdf_qa_")
    subprocess.run(
        ["pdftoppm", "-f", "1", "-l", "1", "-png", "-r", "80", OUT_PDF,
         os.path.join(qa_dir, "p1")],
        check=True,
    )
    pages = txt.count("\f")
    print(f"OK {OUT_PDF} ({pages} pp, {os.path.getsize(OUT_PDF)//1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
