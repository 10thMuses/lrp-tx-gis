#!/usr/bin/env python3
import re, os, markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

SRC = "/home/claude/gw21/vol21.md"
OUT = "/mnt/user-data/outputs/Grid_Wire_Vol21_20260807_815am_ET.pdf"
FONTDIR = "/home/claude/gw21/fonts"
NAVY = "#1c2b3a"; GOLD = "#b8860b"; RED = "#b0322b"; GREEN = "#1f7a3f"

raw = open(SRC).read()

m = re.search(r"TOPLINE_START\n(.*?)TOPLINE_END\n", raw, re.S)
topline_items = [tuple(l.split("|",1)) for l in m.group(1).strip().splitlines()]
raw = raw.replace(m.group(0), "@@TOPLINE@@\n")

stats = [tuple(s.strip() for s in sm.group(1).split("|")) for sm in re.finditer(r"^STATS:(.*)$", raw, re.M)]
raw = re.sub(r"^STATS:.*$\n?", "", raw, flags=re.M)
raw = raw.replace("@@TOPLINE@@\n\n", "@@TOPLINE@@\n@@STATS@@\n", 1)

clocks = [tuple(s.strip() for s in cm.group(1).split("|")) for cm in re.finditer(r"^CLOCKS:(.*)$", raw, re.M)]
raw = re.sub(r"^CLOCKS:.*$\n?", "", raw, flags=re.M)
raw = raw.replace("@@STATS@@\n", "@@STATS@@\n@@CLOCKS@@\n", 1)

raw = re.sub(r"^KICKER:\s*(.*)$", r'<div class="kicker">\1</div>', raw, flags=re.M)
raw = re.sub(r"<<<(ANGLE|GOLD|FALSIFY)\n(.*?)\n>>>",
             lambda m: f'<div class="{m.group(1).lower()}" markdown="1">\n{m.group(2).strip()}\n</div>',
             raw, flags=re.S)

body = markdown.markdown(raw, extensions=["extra","tables","sane_lists"])

tl = ['<div class="topline"><div class="tl-head">TOP LINE</div>']
for sig, txt in topline_items:
    tl.append(f'<div class="tl-item"><span class="dot dot-{ "red" if sig.strip()=="RED" else "green" }"></span><span>{txt.strip()}</span></div>')
tl.append("</div>")
st = ['<div class="statband">'] + [f'<div class="stat"><div class="stat-label">{a}</div><div class="stat-big">{b}</div><div class="stat-delta">{c}</div></div>' for a,b,c in stats] + ["</div>"]
ck = ['<div class="clockrow">'] + [f'<span class="chip"><b>{c}</b> · {a} · {b}</span>' for a,b,c in clocks] + ["</div>"]
for k,v in [("@@TOPLINE@@","".join(tl)),("@@STATS@@","".join(st)),("@@CLOCKS@@","".join(ck))]:
    body = body.replace(f"<p>{k}</p>", v).replace(k, v)

def color_td(mm):
    cell, inner = mm.group(0), mm.group(1)
    if re.search(r"(^|[\s(>])\+\s?[\$\d]", inner) or re.search(r"\+\d+(\.\d+)?\s?(%|bps|pts?|GW)", inner):
        return cell.replace(inner, f'<span class="pos">{inner}</span>')
    if re.search(r"(^|[\s(>])-\s?[\$\d]", inner) or re.search(r"-\d+(\.\d+)?\s?(%|bps|pts?)", inner):
        return cell.replace(inner, f'<span class="neg">{inner}</span>')
    return cell
body = re.sub(r"<td>(.*?)</td>", color_td, body)

css = f"""
@page {{ size: letter; margin: 15mm;
  @bottom-left {{ content: "THE GRID WIRE · Vol. 21 · 2026-08-07 08:15 ET"; font-family: Jost; font-size: 8pt; color: #5a6675; }}
  @bottom-right {{ content: "Page " counter(page) " of " counter(pages); font-family: Jost; font-size: 8pt; color: #5a6675; }} }}
@font-face {{ font-family: Jost; font-weight: 400; src: url("file://{FONTDIR}/Jost-Regular.ttf"); }}
@font-face {{ font-family: Jost; font-weight: 500; src: url("file://{FONTDIR}/Jost-Medium.ttf"); }}
@font-face {{ font-family: Jost; font-weight: 600; src: url("file://{FONTDIR}/Jost-SemiBold.ttf"); }}
@font-face {{ font-family: Jost; font-weight: 700; src: url("file://{FONTDIR}/Jost-Bold.ttf"); }}
body {{ font-family: Jost; font-size: 11.5pt; line-height: 1.58; color: #1b2430; }}
h1:first-of-type {{ font-size: 30pt; font-weight: 700; color: {NAVY}; letter-spacing: 2px; margin: 0 0 1mm; border-bottom: 1.2mm solid {GOLD}; padding-bottom: 2mm; }}
h2:first-of-type {{ font-size: 13.5pt; font-weight: 600; color: {GOLD}; margin: 1.5mm 0 4mm; }}
h1 {{ font-size: 16pt; font-weight: 700; color: {NAVY}; border-bottom: 0.9mm solid {GOLD}; padding-bottom: 1.2mm; margin: 9mm 0 3mm; page-break-after: avoid; letter-spacing: 0.3px; }}
h2 {{ font-size: 13pt; font-weight: 600; color: {NAVY}; margin: 5mm 0 2mm; page-break-after: avoid; }}
p {{ margin: 0 0 3mm; text-align: left; }}
strong {{ font-weight: 600; color: {NAVY}; }}
.kicker {{ font-weight: 500; font-size: 11.5pt; color: {GOLD}; margin: 0 0 3mm; page-break-after: avoid; }}
.topline {{ background: #faf6ec; color: #1b2430; padding: 4mm 4.5mm; margin: 3.5mm 0 3mm; border-left: 1.6mm solid {GOLD}; border-radius: 1mm; }}
.tl-head {{ color: {NAVY}; font-weight: 700; letter-spacing: 3px; font-size: 12.5pt; margin-bottom: 2.4mm; }}
.tl-item {{ display: flex; gap: 2.6mm; margin-bottom: 2.2mm; font-size: 11pt; line-height: 1.45; }}
.dot {{ flex: none; width: 3mm; height: 3mm; border-radius: 50%; margin-top: 1.6mm; }}
.dot-red {{ background: {RED}; }} .dot-green {{ background: {GREEN}; }}
.statband {{ display: flex; gap: 2mm; margin: 0 0 3mm; }}
.stat {{ flex: 1; background: #ffffff; border: 0.4pt solid #d7dde4; border-top: 1.4mm solid {GOLD}; padding: 2.4mm 2mm; }}
.stat-label {{ font-size: 8.6pt; font-weight: 600; letter-spacing: 0.6px; color: #5a6675; }}
.stat-big {{ font-size: 16pt; font-weight: 700; color: {NAVY}; margin: 0.6mm 0; }}
.stat-delta {{ font-size: 8.4pt; color: #7a6420; font-weight: 500; line-height: 1.3; }}
.clockrow {{ margin: 0 0 3mm; }}
.chip {{ display: inline-block; background: #ffffff; border: 0.5pt solid {GOLD}; color: #1b2430; font-size: 9.4pt; padding: 1.1mm 2.4mm; margin: 0 1.2mm 1.4mm 0; border-radius: 3.5mm; }}
.chip b {{ color: #8a6a10; }}
.angle {{ background: #f4f6f8; border-left: 1.6mm solid {NAVY}; padding: 3mm 3.5mm; margin: 3mm 0 4mm; page-break-inside: avoid; }}
.gold {{ background: #faf6ec; border-left: 1.6mm solid {GOLD}; padding: 3mm 3.5mm; margin: 3mm 0 4mm; page-break-inside: avoid; }}
.falsify {{ background: #faf1ef; border-left: 1.6mm solid {RED}; padding: 3mm 3.5mm; margin: 3mm 0 4mm; page-break-inside: avoid; }}
.angle p, .gold p, .falsify p {{ margin-bottom: 2mm; font-size: 11pt; }}
table {{ width: 100%; border-collapse: collapse; margin: 2.5mm 0 4.5mm; font-size: 10.2pt; }}
th {{ background: #eef1f4; color: {NAVY}; font-weight: 600; text-align: left; padding: 1.8mm 2.2mm; border-bottom: 0.8mm solid {GOLD}; }}
td {{ border-bottom: 0.4pt solid #d7dde4; padding: 1.7mm 2.2mm; vertical-align: top; line-height: 1.45; }}
tr:nth-child(even) td {{ background: #f8fafb; }}
.pos {{ color: {GREEN}; font-weight: 600; }} .neg {{ color: {RED}; font-weight: 600; }}
hr {{ border: none; border-top: 0.6pt solid #d9c58a; margin: 5mm 0; }}
ol, ul {{ margin: 0 0 3mm 5.5mm; }} li {{ margin-bottom: 1.4mm; }}
em {{ color: #3a4656; }}
"""

fc = FontConfiguration()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
HTML(string=f"<html><body>{body}</body></html>").write_pdf(OUT, stylesheets=[CSS(string=css, font_config=fc)], font_config=fc)
print("written", OUT)
